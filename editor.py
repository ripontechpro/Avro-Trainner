"""Wordlist Editor - edit every wordlist/*.txt file inside the app."""
import os
import time

from PySide6.QtCore import QRect, QSize, Qt, QUrl, Signal
from PySide6.QtGui import (QColor, QDesktopServices, QKeySequence, QPainter, QShortcut, QSyntaxHighlighter,
                           QTextCharFormat, QTextCursor)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
                               QPlainTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

import avro_data as A
import bijoy_data as B
import wordlists as WL
from widgets import ACCENTS, MUTED, PageHeader, accent_qss, card, font, make_btn

HELP = {
    "paragraph": "Ek line = ek ta paragraph.",
    "pairs": "Format:  বাংলা = avro key     (ek line = ek item).  Validate diye key check korun.",
    "lines": "Ek line = ek ta item.",
}
COMMENT_HELP = "Line er shurute  '# '  (hash + space) dile seta comment, ignore hoy."


# ---------------------------------------------------------------- code edit with line numbers
class _Gutter(QWidget):
    def __init__(self, ed):
        super().__init__(ed)
        self.ed = ed

    def sizeHint(self):
        return QSize(self.ed.gutter_width(), 0)

    def paintEvent(self, e):
        self.ed.paint_gutter(e)


class CodeEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.gutter = _Gutter(self)
        self.blockCountChanged.connect(self.update_margin)
        self.updateRequest.connect(self.update_gutter)
        self.update_margin()

    def gutter_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 18 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_margin(self, *_):
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)

    def update_gutter(self, rect, dy):
        if dy:
            self.gutter.scroll(0, dy)
        else:
            self.gutter.update(0, rect.y(), self.gutter.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_margin()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cr = self.contentsRect()
        self.gutter.setGeometry(QRect(cr.left(), cr.top(), self.gutter_width(), cr.height()))

    def paint_gutter(self, event):
        p = QPainter(self.gutter)
        p.fillRect(event.rect(), QColor("#f1f5f9"))
        block = self.firstVisibleBlock()
        n = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        p.setPen(QColor("#94a3b8"))
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                p.drawText(0, top, self.gutter.width() - 8, self.fontMetrics().height(), Qt.AlignRight, str(n + 1))
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            n += 1

    def goto_line(self, line):
        blk = self.document().findBlockByNumber(max(0, line - 1))
        if blk.isValid():
            cur = QTextCursor(blk)
            cur.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            self.setTextCursor(cur)
            self.centerCursor()
            self.setFocus()


class Highlighter(QSyntaxHighlighter):
    def __init__(self, doc, kind):
        super().__init__(doc)
        self.kind = kind
        self.f_comment = QTextCharFormat()
        self.f_comment.setForeground(QColor("#94a3b8"))
        self.f_comment.setFontItalic(True)
        self.f_eq = QTextCharFormat()
        self.f_eq.setForeground(QColor("#7c3aed"))
        self.f_eq.setFontWeight(700)
        self.f_key = QTextCharFormat()
        self.f_key.setForeground(QColor("#0d9488"))

    def highlightBlock(self, text):
        s = text.strip()
        if WL.is_comment(s):
            self.setFormat(0, len(text), self.f_comment)
        elif self.kind == "pairs" and "=" in text:
            i = text.index("=")
            self.setFormat(i, 1, self.f_eq)
            self.setFormat(i + 1, len(text) - i - 1, self.f_key)


# ---------------------------------------------------------------- validation
def validate(kind, check, text):
    """-> list of (line_no, 'error'|'warn', message)"""
    out, seen = [], {}
    conv_old, conv_new = B.make_convert(True), B.make_convert(False)
    for no, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if not s or WL.is_comment(s):
            continue
        if kind == "paragraph" and len(s.split()) < 3:
            out.append((no, "warn", "khub chhoto paragraph (3 word er kom)"))
        if "\t" in raw:
            out.append((no, "warn", "Tab ache - space dilei bhalo"))
        if check == "avro":
            if "=" not in s:
                out.append((no, "error", "'=' nai.  Format:  বাংলা = key"))
                continue
            a, b = (x.strip() for x in s.split("=", 1))
            if not a or not b:
                out.append((no, "error", "'=' er duidike-i lekha thakte hobe"))
                continue
            if any(ord(c) > 127 for c in b):
                out.append((no, "error", "key te non-English character ache"))
                continue
            got = A.convert(b)
            if got != a:
                out.append((no, "error", f"'{b}' type korle '{got}' hoy, '{a}' noy"))
            if a in seen:
                out.append((no, "warn", f"'{a}' agei line {seen[a]} e ache (duplicate)"))
            seen.setdefault(a, no)
        elif check == "bijoy":
            for old, conv in ((True, conv_old), (False, conv_new)):
                back = conv(B.encode(s, old))
                if B.nfd(back) != B.nfd(s):
                    out.append((no, "error", f"'{s}' Bijoy key diye thik moto toiri hoy na (pelam '{back}')"))
                    break
            if s in seen:
                out.append((no, "warn", f"'{s}' agei line {seen[s]} e ache (duplicate)"))
            seen.setdefault(s, no)
        elif check == "token":
            if any(c.isspace() for c in s):
                out.append((no, "error", "ek line e ek ta word - space thakbe na"))
            if any(ord(c) > 127 or not c.isprintable() for c in s):
                out.append((no, "error", "non-English character - keyboard e type kora jabe na"))
            if s in seen:
                out.append((no, "warn", f"'{s}' agei line {seen[s]} e ache (duplicate)"))
            seen.setdefault(s, no)
        elif check == "ascii":
            if any(ord(c) > 127 or not c.isprintable() for c in s):
                out.append((no, "error", "non-English character - keyboard e type kora jabe na"))
    return out


def count_items(kind, text):
    return len(WL.parse_pairs(text)) if kind == "pairs" else len(WL.parse_lines(text))


# ---------------------------------------------------------------- page
class WordlistEditor(QWidget):
    saved = Signal(str)
    go_home = Signal()

    def __init__(self, fam):
        super().__init__()
        self.setObjectName("page")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(accent_qss(ACCENTS["editor"]))
        self.fam = fam
        self.cur = None            # registry entry of the open file
        self._loading = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 22, 26, 22)
        lay.setSpacing(16)
        hd = PageHeader("Wordlist Editor", "Shob paragraph, word ar sentence list - wordlist/ folder er text file", ACCENTS["editor"])
        hd.add(make_btn("📂  Open folder", "soft", self.open_folder))
        lay.addWidget(hd)
        body = QHBoxLayout()
        body.setSpacing(16)
        lay.addLayout(body, 1)

        # ---- file tree
        lv = QVBoxLayout()
        lf = card(lv, (10, 12, 10, 12))
        lf.setFixedWidth(330)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(2)
        self.tree.setIndentation(14)
        self.tree.setStyleSheet("QTreeWidget{border:none; background:transparent;}")
        self.tree.currentItemChanged.connect(self.on_tree_select)
        lv.addWidget(self.tree)
        body.addWidget(lf)

        # ---- editor side
        rv = QVBoxLayout()
        rf = card(rv, (18, 14, 18, 14), 8)
        top = QHBoxLayout()
        tv = QVBoxLayout()
        tv.setSpacing(0)
        self.f_title = QLabel("")
        self.f_title.setStyleSheet("font-size:18px; font-weight:700;")
        self.f_path = QLabel("")
        self.f_path.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        tv.addWidget(self.f_title)
        tv.addWidget(self.f_path)
        top.addLayout(tv, 1)
        self.save_btn = make_btn("💾  Save   Ctrl+S", "primary", self.save)
        self.revert_btn = make_btn("↶  Revert", "soft", self.revert)
        self.valid_btn = make_btn("✔  Validate", "soft", self.run_validate)
        for b in (self.valid_btn, self.revert_btn, self.save_btn):
            top.addWidget(b)
        rv.addLayout(top)
        self.help = QLabel("")
        self.help.setStyleSheet(f"color:{MUTED}; font-size:12px; background:#f8fafc; border-radius:8px; padding:6px 10px;")
        self.help.setWordWrap(True)
        rv.addWidget(self.help)

        find = QHBoxLayout()
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Find...  (Enter = next)")
        self.find_edit.returnPressed.connect(self.find_next)
        find.addWidget(self.find_edit, 1)
        find.addWidget(make_btn("Find next", "soft", self.find_next))
        rv.addLayout(find)

        self.edit = CodeEdit()
        self.edit.document().modificationChanged.connect(self.on_modified)
        self.edit.textChanged.connect(self.update_status)
        rv.addWidget(self.edit, 1)

        self.problems = QListWidget()
        self.problems.setMaximumHeight(150)
        self.problems.setVisible(False)
        self.problems.itemClicked.connect(self.jump_problem)
        rv.addWidget(self.problems)
        self.status = QLabel("")
        self.status.setStyleSheet(f"color:{MUTED}; font-size:12px;")
        rv.addWidget(self.status)
        body.addWidget(rf, 1)

        sc = QShortcut(QKeySequence("Ctrl+S"), self, activated=self.save)
        sc.setContext(Qt.WidgetWithChildrenShortcut)
        self.build_tree()
        self.set_enabled(False)

    # ---- tree
    def build_tree(self, keep=None):
        self.tree.blockSignals(True)
        self.tree.clear()
        groups = {}
        for ent in WL.FILES:
            g = groups.get(ent["group"])
            if g is None:
                g = QTreeWidgetItem([ent["group"], ""])
                g.setFlags(Qt.ItemIsEnabled)
                f = g.font(0)
                f.setBold(True)
                g.setFont(0, f)
                self.tree.addTopLevelItem(g)
                g.setExpanded(True)
                groups[ent["group"]] = g
            text = WL.read_text(ent["name"])
            cnt = "missing" if text is None else str(count_items(ent["kind"], text))
            it = QTreeWidgetItem([ent["title"], cnt])
            it.setData(0, Qt.UserRole, ent["name"])
            it.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            if text is None or cnt == "0":
                it.setForeground(1, QColor("#dc2626"))
            else:
                it.setForeground(1, QColor(MUTED))
            g.addChild(it)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, self.tree.header().ResizeMode.Stretch)
        self.tree.setColumnWidth(1, 70)
        self.tree.blockSignals(False)
        if keep:
            self.select_in_tree(keep)

    def select_in_tree(self, name):
        for gi in range(self.tree.topLevelItemCount()):
            g = self.tree.topLevelItem(gi)
            for ci in range(g.childCount()):
                it = g.child(ci)
                if it.data(0, Qt.UserRole) == name:
                    self.tree.blockSignals(True)
                    self.tree.setCurrentItem(it)
                    self.tree.blockSignals(False)
                    return

    def on_tree_select(self, cur, prev):
        if not cur or not cur.data(0, Qt.UserRole):
            return
        name = cur.data(0, Qt.UserRole)
        if self.cur and name == self.cur["name"]:
            return
        if not self.confirm_discard():
            self.select_in_tree(self.cur["name"] if self.cur else "")
            return
        self.load(name)

    # ---- file ops
    def set_enabled(self, on):
        for w in (self.edit, self.save_btn, self.revert_btn, self.valid_btn, self.find_edit):
            w.setEnabled(on)

    def open_file(self, name):
        if self.cur and self.cur["name"] == name:
            return
        if not self.confirm_discard():
            return
        self.select_in_tree(name)
        self.load(name)

    def load(self, name):
        ent = next((e for e in WL.FILES if e["name"] == name), None)
        if not ent:
            return
        self.cur = ent
        text = WL.read_text(name)
        self._loading = True
        self.edit.setFont(font(self.fam[ent["font"]], 28 if ent["font"] == "bijoy" else 17))
        self.edit.setLineWrapMode(CodeEdit.WidgetWidth if ent["kind"] == "paragraph" else CodeEdit.NoWrap)
        self.hl = Highlighter(self.edit.document(), ent["kind"])
        self.edit.setPlainText(text if text is not None else "")
        self.edit.document().setModified(False)
        self._loading = False
        self.f_title.setText(f"{ent['group']}  ›  {ent['title']}")
        path = WL.find(name)
        self.f_path.setText(path if path else f"{os.path.join(WL.user_dir(), name)}   (file nai - Save korle toiri hobe)")
        self.help.setText(HELP[ent["kind"]] + "   " + COMMENT_HELP)
        self.valid_btn.setVisible(bool(ent["check"]) or ent["kind"] == "paragraph")
        self.problems.setVisible(False)
        self.set_enabled(True)
        self.on_modified(False)
        self.update_status()

    def current_text(self):
        return self.edit.toPlainText()

    def revert(self):
        if self.cur and (not self.edit.document().isModified()
                         or QMessageBox.question(self, "Revert", "Save na kora poriborton bad dite chan?") == QMessageBox.Yes):
            self.load(self.cur["name"])

    def save(self):
        if not self.cur:
            return False
        errs = [p for p in validate(self.cur["kind"], self.cur["check"], self.current_text()) if p[1] == "error"]
        if errs:
            r = QMessageBox.question(self, "Problem ache",
                                     f"{len(errs)} ta line e problem ache (jemon line {errs[0][0]}: {errs[0][2]}).\n"
                                     "Tobuo save korben?")
            if r != QMessageBox.Yes:
                self.run_validate()
                return False
        ok, msg = WL.write_text(self.cur["name"], self.current_text())
        if not ok:
            QMessageBox.critical(self, "Save hoy ni", msg)
            return False
        self.edit.document().setModified(False)
        self.f_path.setText(msg)
        self.status.setText(f"Saved ✓  {time.strftime('%H:%M:%S')}   ·   " + self.status.text())
        self.build_tree(keep=self.cur["name"])
        self.saved.emit(self.cur["name"])
        return True

    def confirm_discard(self):
        """True if it is OK to leave the open file."""
        if not (self.cur and self.edit.document().isModified()):
            return True
        box = QMessageBox(self)
        box.setWindowTitle("Save na kora poriborton")
        box.setText(f"'{self.cur['title']}' e save na kora poriborton ache.")
        sv = box.addButton("Save", QMessageBox.AcceptRole)
        ds = box.addButton("Discard", QMessageBox.DestructiveRole)
        box.addButton("Cancel", QMessageBox.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked == sv:
            return self.save()
        return clicked == ds

    def leave(self):
        pass

    def can_leave(self):
        return self.confirm_discard()

    def on_show(self):
        self.build_tree(keep=self.cur["name"] if self.cur else None)

    def open_folder(self):
        os.makedirs(WL.user_dir(), exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(WL.user_dir()))

    # ---- validate / find / status
    def run_validate(self):
        if not self.cur:
            return
        res = validate(self.cur["kind"], self.cur["check"], self.current_text())
        self.problems.clear()
        for no, level, msg in res:
            it = QListWidgetItem(f"{'✖' if level == 'error' else '⚠'}  Line {no}:  {msg}")
            it.setData(Qt.UserRole, no)
            it.setForeground(QColor("#dc2626" if level == "error" else "#b45309"))
            self.problems.addItem(it)
        if not res:
            it = QListWidgetItem("✔  Kono problem pawa jay ni")
            it.setForeground(QColor("#16a34a"))
            it.setData(Qt.UserRole, 0)
            self.problems.addItem(it)
        self.problems.setVisible(True)

    def jump_problem(self, item):
        n = item.data(Qt.UserRole)
        if n:
            self.edit.goto_line(n)

    def find_next(self):
        t = self.find_edit.text()
        if not t:
            return
        if not self.edit.find(t):
            self.edit.moveCursor(QTextCursor.Start)
            self.edit.find(t)

    def on_modified(self, mod):
        self.save_btn.setEnabled(bool(self.cur) and mod)
        self.revert_btn.setEnabled(bool(self.cur) and mod)
        if self.cur:
            self.f_title.setText(f"{self.cur['group']}  ›  {self.cur['title']}" + ("   ●" if mod else ""))

    def update_status(self):
        if not self.cur or self._loading:
            return
        t = self.current_text()
        self.status.setText(f"{count_items(self.cur['kind'], t)} items   ·   {t.count(chr(10)) + 1 if t else 0} lines   ·   UTF-8")
