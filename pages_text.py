"""Paragraph practice page (Bangla / English / Bijoy). Paragraphs come from wordlist/paragraphs_*.txt."""
import random
import time
from html import escape

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QMessageBox, QPlainTextEdit, QProgressBar,
                               QTextEdit, QVBoxLayout, QWidget)

import wordlists as WL
from widgets import (ACCENTS, INK, MUTED, PageHeader, Segmented, StatCard, accent_qss, card, font, make_btn)

PARA_MODES = {
    "bangla": dict(label="বাংলা", file="paragraphs_bangla.txt", fam="bn",
                   hint="Bangla Unicode - system Avro keyboard on kore likhun"),
    "english": dict(label="English", file="paragraphs_english.txt", fam="mono", hint="Standard QWERTY"),
    "bijoy": dict(label="বিজয়", file="paragraphs_bijoy.txt", fam="bijoy",
                  hint="ANSI font (SutonnyMJ) - Bijoy keyboard on kore likhun"),
}
PARA_ORDER = ["bangla", "english", "bijoy"]


class TypingInput(QPlainTextEdit):
    """Input box. Optional built-in Avro conversion (pyavrophonetic). Paste is disabled."""
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.builtin = False
        self.raw = ""
        self.converter = None
        self._silent = False
        self.textChanged.connect(self._on_changed)

    def _on_changed(self):
        if not self._silent:
            self.changed.emit()

    def reset(self):
        self.raw = ""
        self._silent = True
        self.clear()
        self._silent = False

    def insertFromMimeData(self, source):      # no pasting - it is a typing test
        pass

    def keyPressEvent(self, e):
        if not (self.builtin and self.converter):
            super().keyPressEvent(e)
            return
        k, txt = e.key(), e.text()
        if k == Qt.Key_Backspace:
            self.raw = self.raw[:-1]
        elif k in (Qt.Key_Return, Qt.Key_Enter):
            self.raw += "\n"
        elif txt and txt.isprintable() and not (e.modifiers() & Qt.ControlModifier):
            self.raw += txt
        else:
            return
        try:
            shown = self.converter(self.raw)
        except Exception:
            shown = self.raw
        self._silent = True
        self.setPlainText(shown)
        c = self.textCursor()
        c.movePosition(c.MoveOperation.End)
        self.setTextCursor(c)
        self._silent = False
        self.changed.emit()


class ParagraphPage(QWidget):
    go_home = Signal()
    edit_requested = Signal(str)          # wordlist file name

    COLORS = dict(correct="#16a34a", wrong="#dc2626", wrong_bg="#fee2e2", cur_bg="#fef08a", pending="#94a3b8")

    def __init__(self, fam):
        super().__init__()
        self.setObjectName("page")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(accent_qss(ACCENTS["para"]))
        self.fam = fam
        self.mode = "bangla"
        self.words, self.start_time, self.finished = [], None, False
        self.data = {}
        self.load_data()
        try:
            from pyavrophonetic import avro
            self.avro_parse = avro.parse
        except Exception:
            self.avro_parse = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 22, 26, 22)
        lay.setSpacing(14)
        self.header = PageHeader("Paragraph Practice", "", ACCENTS["para"])
        self.seg = Segmented([(k, PARA_MODES[k]["label"]) for k in PARA_ORDER], self.set_mode)
        self.header.add(self.seg)
        self.header.add(make_btn("✎  Edit wordlist", "soft", self.edit_current))
        self.header.add(make_btn("⟳  New paragraph", "primary", self.new_paragraph))
        lay.addWidget(self.header)

        pv = QVBoxLayout()
        pf = card(pv, (8, 8, 8, 8))
        self.para = QTextEdit()
        self.para.setReadOnly(True)
        self.para.setFocusPolicy(Qt.NoFocus)
        self.para.setStyleSheet("QTextEdit{border:none; background:transparent; padding:14px;}")
        pv.addWidget(self.para)
        lay.addWidget(pf, 3)

        row = QHBoxLayout()
        cap = QLabel("TYPE HERE")
        cap.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:700; letter-spacing:2px;")
        row.addWidget(cap)
        row.addStretch(1)
        self.builtin_cb = QCheckBox("Built-in Avro phonetic (pyavrophonetic)")
        self.builtin_cb.setFocusPolicy(Qt.NoFocus)
        self.builtin_cb.setVisible(self.avro_parse is not None)
        self.builtin_cb.toggled.connect(lambda _: self.on_show())
        row.addWidget(self.builtin_cb)
        lay.addLayout(row)
        self.inp = TypingInput()
        self.inp.changed.connect(self.on_type)
        lay.addWidget(self.inp, 2)

        sv = QVBoxLayout()
        sf = card(sv, (16, 12, 16, 12), 10)
        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setTextVisible(False)
        sv.addWidget(self.bar)
        sr = QHBoxLayout()
        sr.setSpacing(14)
        a = ACCENTS["para"]
        self.stats = {k: StatCard(lab, ac) for k, lab, ac in (
            ("words", "WORDS", a), ("correct", "CORRECT", "#16a34a"),
            ("acc", "ACCURACY", "#f59e0b"), ("wpm", "SPEED", "#dc2626"))}
        for w in self.stats.values():
            sr.addWidget(w)
        sv.addLayout(sr)
        lay.addWidget(sf)

    # ---- data
    def load_data(self):
        self.data = {k: WL.lines(PARA_MODES[k]["file"]) for k in PARA_MODES}

    def reload_wordlist(self):
        self.load_data()
        if self.isVisible():
            self.on_show()

    def edit_current(self):
        self.edit_requested.emit(PARA_MODES[self.mode]["file"])

    def family(self):
        return self.fam[PARA_MODES[self.mode]["fam"]]

    def set_mode(self, k):
        self.mode = k
        self.on_show()

    def on_show(self):
        m = PARA_MODES[self.mode]
        self.header.sub.setText(m["hint"])
        self.seg.set_active(self.mode)
        use_builtin = self.builtin_cb.isChecked() and self.mode == "bangla"
        self.builtin_cb.setEnabled(self.mode == "bangla")
        self.inp.builtin = use_builtin
        self.inp.converter = self.avro_parse
        f = font(self.family(), 28 if self.mode == "bijoy" else 24)
        self.para.setFont(f)
        self.inp.setFont(f)
        self.new_paragraph()

    def leave(self):
        pass

    def new_paragraph(self):
        items = self.data[self.mode]
        self.start_time, self.finished = None, False
        self.inp.reset()
        for k, v in (("words", "0 / 0"), ("correct", "0"), ("acc", "100%"), ("wpm", "0 WPM")):
            self.stats[k].set(v)
        self.bar.setValue(0)
        if not items:
            self.words = []
            self.inp.setEnabled(False)
            self.para.setHtml(f'<div style="color:{MUTED}; font-size:18px; text-align:center; padding-top:30px;">'
                              f'<b>Wordlist pawa jay ni</b><br>wordlist/{PARA_MODES[self.mode]["file"]} khali ba nai.<br>'
                              f'"Edit wordlist" diye paragraph add korun.</div>')
            return
        self.inp.setEnabled(True)
        self.words = random.choice(items).split()
        self.stats["words"].set(f"0 / {len(self.words)}")
        self.render()
        self.inp.setFocus()

    def render(self, typed=None, prefix=""):
        typed = typed or []
        c = self.COLORS
        out = []
        for i, w in enumerate(self.words):
            if i < len(typed):
                ok = typed[i] == w
                st = f"color:{c['correct']};" if ok else f"color:{c['wrong']}; background-color:{c['wrong_bg']};"
            elif i == len(typed):
                bad = prefix and not w.startswith(prefix)
                st = (f"color:{c['wrong']}; background-color:{c['wrong_bg']};" if bad
                      else f"background-color:{c['cur_bg']}; color:{INK};")
            else:
                st = f"color:{c['pending']};"
            out.append(f'<span style="{st}">{escape(w)}</span>')
        self.para.setHtml(f'<div style="line-height:155%;">{" ".join(out)}</div>')

    def on_type(self):
        if self.finished or not self.words:
            return
        raw = self.inp.toPlainText()
        if self.start_time is None and raw:
            self.start_time = time.time()
        parts = raw.split()
        if raw.endswith((" ", "\n")):
            typed, prefix = parts, ""
        else:
            typed, prefix = parts[:-1], (parts[-1] if parts else "")
        self.render(typed, prefix)
        correct = sum(1 for i, w in enumerate(typed) if i < len(self.words) and w == self.words[i])
        n = len(typed)
        acc = correct / n * 100 if n else 100
        el = max(time.time() - self.start_time, 0.01) if self.start_time else 0.01
        wpm = n / el * 60
        for k, v in (("words", f"{n} / {len(self.words)}"), ("correct", str(correct)),
                     ("acc", f"{acc:.0f}%"), ("wpm", f"{wpm:.0f} WPM")):
            self.stats[k].set(v)
        self.bar.setValue(int(1000 * min(1, n / len(self.words))))
        if n >= len(self.words):
            self.finished = True
            fc = sum(1 for i, w in enumerate(typed[:len(self.words)]) if w == self.words[i])
            QTimer.singleShot(150, lambda: self.done_dialog(fc / len(self.words) * 100, wpm))

    def done_dialog(self, acc, wpm):
        QMessageBox.information(self, "সম্পন্ন হয়েছে!",
                                f"প্যারাগ্রাফ শেষ হয়েছে।\nনির্ভুলতা: {acc:.0f}%\nগতি: {wpm:.0f} WPM\n\n"
                                "'New paragraph' chapun porerti-r jonno.")
        self.inp.setFocus()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.go_home.emit()
            return
        super().keyPressEvent(e)
