"""
Ripon Typing Tutor  (PySide6 / Qt 6)
====================================
Avro (Bangla phonetic) | Bijoy | English trainers + paragraph practice + wordlist editor.

Run:      python ripon_typing_tutor.py          (pip install PySide6)
Keys:     F11 fullscreen | Esc back to dashboard | Ctrl+Q quit | Ctrl+S save (editor)
Avro:     F2 pause        Bijoy: F2 kar order, F3 training/test, Ctrl+R reset hour, Enter next level

ALL word lists / sentences / paragraphs live in the  wordlist/  folder (plain UTF-8 .txt files).
"""
import os
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QKeySequence, QPainter, QPainterPath, QPixmap, QShortcut
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow,
                               QMessageBox, QStackedWidget, QVBoxLayout, QWidget)

import wordlists as WL
from editor import WordlistEditor
from pages_english import EnglishPage
from pages_text import ParagraphPage
from pages_trainer import AvroPage, BijoyPage
from widgets import ACCENTS, INK, MUTED, QSS, font, make_btn, set_prop

APP_NAME = "Ripon Typing Tutor"
VERSION = "2.0"
BASE_DIR = WL.base_dir()


def res_path(name):
    """Find a bundled/side-by-side file: beside the program first, then PyInstaller's bundle."""
    for d in (BASE_DIR, getattr(sys, "_MEIPASS", None)):
        if d and os.path.isfile(os.path.join(d, name)):
            return os.path.join(d, name)
    return None


def pick_family(cands, default):
    have = set(QFontDatabase.families())
    return next((f for f in cands if f in have), default)


def circular_pixmap(path, size):
    pm = QPixmap(path)
    if pm.isNull():
        return None
    pm = pm.scaled(size * 2, size * 2, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    out = QPixmap(size * 2, size * 2)
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.Antialiasing)
    pp = QPainterPath()
    pp.addEllipse(0, 0, size * 2, size * 2)
    p.setClipPath(pp)
    p.drawPixmap((size * 2 - pm.width()) // 2, (size * 2 - pm.height()) // 2, pm)
    p.end()
    out.setDevicePixelRatio(2)
    return out


# ======================================================================== dashboard
class FeatureCard(QFrame):
    clicked = Signal()

    def __init__(self, glyph, color, title, desc, glyph_font):
        super().__init__()
        self.setObjectName("modeCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(170)
        v = QVBoxLayout(self)
        v.setContentsMargins(20, 18, 20, 16)
        v.setSpacing(4)
        top = QHBoxLayout()
        g = QLabel(glyph)
        g.setFixedSize(52, 52)
        g.setAlignment(Qt.AlignCenter)
        g.setFont(font(glyph_font, 26, True))
        g.setStyleSheet(f"background:{color}; color:white; border-radius:14px;")
        top.addWidget(g)
        top.addStretch(1)
        arrow = QLabel("→")
        arrow.setStyleSheet(f"color:{MUTED}; font-size:20px;")
        top.addWidget(arrow)
        v.addLayout(top)
        v.addSpacing(6)
        t = QLabel(title)
        t.setStyleSheet("font-size:18px; font-weight:700;")
        d = QLabel(desc)
        d.setWordWrap(True)
        d.setStyleSheet(f"color:{MUTED}; font-size:12px;")
        v.addWidget(t)
        v.addWidget(d)
        v.addStretch(1)
        self.summary = QLabel("")
        self.summary.setStyleSheet(f"color:{color}; font-size:12px; font-weight:700;")
        v.addWidget(self.summary)
        for w in self.findChildren(QLabel):
            w.setAttribute(Qt.WA_TransparentForMouseEvents)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()


class HomePage(QWidget):
    open_page = Signal(str)

    def __init__(self, fam):
        super().__init__()
        self.setObjectName("page")
        self.setAttribute(Qt.WA_StyledBackground, True)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 26, 30, 20)
        lay.setSpacing(18)

        hero = QFrame()
        hero.setObjectName("hero")
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(34, 26, 34, 26)
        hv = QVBoxLayout()
        hv.setSpacing(4)
        kick = QLabel("WELCOME")
        kick.setStyleSheet("color:rgba(255,255,255,0.7); font-size:12px; font-weight:700; letter-spacing:3px;")
        t = QLabel(APP_NAME)
        t.setStyleSheet("color:white; font-size:38px; font-weight:800;")
        s = QLabel("অভ্র · বিজয় · English  —  সব টাইপিং প্র্যাকটিস এক জায়গায়")
        s.setStyleSheet("color:rgba(255,255,255,0.88); font-size:16px;")
        hv.addWidget(kick)
        hv.addWidget(t)
        hv.addWidget(s)
        hv.addStretch(1)
        hl.addLayout(hv, 1)
        lp = res_path("logo.png")
        pm = circular_pixmap(lp, 112) if lp else None
        if pm:
            lg = QLabel()
            lg.setPixmap(pm)
            lg.setStyleSheet("background:transparent;")
            hl.addWidget(lg)
        lay.addWidget(hero)

        grid = QGridLayout()
        grid.setSpacing(16)
        defs = [
            ("avro", "অ", ACCENTS["avro"], "অভ্র ট্রেনার", "Avro phonetic · ৭ লেভেল · Practice ও Test mode", fam["bn"]),
            ("bijoy", "ক", ACCENTS["bijoy"], "বিজয় ট্রেনার", "Bijoy keyboard · প্রতি লেভেলে ১ ঘণ্টা training · Test", fam["bn"]),
            ("english", "A", ACCENTS["english"], "English Trainer", "Home row থেকে full keyboard · ৫ লেভেল", "Segoe UI"),
            ("para", "¶", ACCENTS["para"], "Paragraph Practice", "বাংলা · English · বিজয় paragraph typing test", "Segoe UI"),
            ("editor", "✎", ACCENTS["editor"], "Wordlist Editor", "wordlist/ folder er shob text file edit, validate ও save", "Segoe UI"),
        ]
        self.cards = {}
        for i, (key, glyph, color, title, desc, gf) in enumerate(defs):
            c = FeatureCard(glyph, color, title, desc, gf)
            c.clicked.connect(lambda k=key: self.open_page.emit(k))
            self.cards[key] = c
            grid.addWidget(c, i // 3, i % 3)
        # progress card
        pf = QFrame()
        pf.setProperty("card", "true")
        pv = QVBoxLayout(pf)
        pv.setContentsMargins(20, 18, 20, 16)
        pt = QLabel("YOUR PROGRESS")
        pt.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:700; letter-spacing:2px;")
        pv.addWidget(pt)
        self.prog_lbl = QLabel("")
        self.prog_lbl.setStyleSheet("font-size:13px; line-height:160%;")
        pv.addWidget(self.prog_lbl)
        pv.addStretch(1)
        grid.addWidget(pf, 1, 2)
        for c in range(3):
            grid.setColumnStretch(c, 1)
        lay.addLayout(grid, 1)

        notice = QLabel("📢 নোটিশ: সফটওয়্যার টি রিপন অনেক পরিশ্রম করে তৈরি করেছে। অতএব এর নাম এবং ছবি মডিফাই এর মাধ্যমে "
                        "পরিবর্তন করে নিচু মানুষিকতার পরিচয় দিবেন না। এটা সম্পুর্ন বিনামুল্যের সফটওয়্যার!")
        notice.setWordWrap(True)
        notice.setStyleSheet("background:#fffbeb; color:#92400e; border:1px solid #fde68a; border-radius:12px;"
                             "padding:10px 16px; font-size:12px; font-weight:600;")
        lay.addWidget(notice)

    def refresh(self, summaries):
        for k, txt in summaries.items():
            if k in self.cards:
                self.cards[k].summary.setText(txt)
        names = {"avro": "অভ্র", "bijoy": "বিজয়", "english": "English"}
        self.prog_lbl.setText("<br>".join(f"<b>{names[k]}</b> — {summaries.get(k, '')}" for k in names)
                              + f"<br><b>Wordlist</b> — {len(WL.FILES)} files")


# ======================================================================== main window
NAV = [("home", "⌂", "Dashboard"), ("avro", "অ", "অভ্র ট্রেনার"), ("bijoy", "ক", "বিজয় ট্রেনার"),
       ("english", "A", "English Trainer"), ("para", "¶", "Paragraph Practice"), ("editor", "✎", "Wordlist Editor")]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — অভ্র | বিজয় | English")
        ico = res_path("logo.ico") or res_path("logo.png")
        if ico:
            self.setWindowIcon(QIcon(ico))
        self.setMinimumSize(1120, 700)
        fam = dict(bn=pick_family(["Nirmala UI", "Kalpurush", "Noto Sans Bengali", "Vrinda", "SolaimanLipi"],
                                  QApplication.font().family()),
                   bijoy="SutonnyMJ",
                   mono=pick_family(["Consolas", "Cascadia Mono", "DejaVu Sans Mono", "Courier New"], "monospace"))
        self.fam = fam

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        hl = QHBoxLayout(root)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)
        hl.addWidget(self.build_rail())
        self.stack = QStackedWidget()
        hl.addWidget(self.stack, 1)

        self.pages = {
            "home": HomePage(fam),
            "avro": AvroPage(fam["bn"]),
            "bijoy": BijoyPage(fam["bn"]),
            "english": EnglishPage(),
            "para": ParagraphPage(fam),
            "editor": WordlistEditor(fam),
        }
        for p in self.pages.values():
            self.stack.addWidget(p)
        self.pages["home"].open_page.connect(self.go)
        for k in ("avro", "bijoy", "english", "para"):
            self.pages[k].go_home.connect(lambda: self.go("home"))
        self.pages["para"].edit_requested.connect(self.edit_wordlist)
        self.pages["editor"].saved.connect(self.on_wordlist_saved)

        QShortcut(QKeySequence("F11"), self, activated=self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Q"), self, activated=self.close)
        self.current = "home"
        self.go("home", force=True)

    # ---- rail
    def build_rail(self):
        rail = QFrame()
        rail.setObjectName("rail")
        rail.setFixedWidth(236)
        v = QVBoxLayout(rail)
        v.setContentsMargins(0, 22, 0, 16)
        v.setSpacing(2)
        lp = res_path("logo.png")
        pm = circular_pixmap(lp, 76) if lp else None
        if pm:
            lg = QLabel()
            lg.setPixmap(pm)
            lg.setAlignment(Qt.AlignCenter)
            lg.setStyleSheet("background:transparent;")
            v.addWidget(lg)
        t = QLabel(APP_NAME)
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("color:white; font-size:17px; font-weight:700; background:transparent; padding-top:8px;")
        s = QLabel("Professional typing practice")
        s.setAlignment(Qt.AlignCenter)
        s.setStyleSheet("color:#94a3b8; font-size:11px; background:transparent; padding-bottom:18px;")
        v.addWidget(t)
        v.addWidget(s)
        self.nav = {}
        for key, glyph, label in NAV:
            b = make_btn(f"{glyph}      {label}", "nav", lambda k=key: self.go(k))
            self.nav[key] = b
            v.addWidget(b)
        v.addStretch(1)
        fr = QHBoxLayout()
        fr.setContentsMargins(14, 0, 14, 0)
        fr.addWidget(make_btn("⛶  F11", "navfoot", self.toggle_fullscreen, "Fullscreen"))
        fr.addWidget(make_btn("⏻  Quit", "navfoot", self.close, "Ctrl+Q"))
        v.addLayout(fr)
        c = QLabel(f"v{VERSION}  ·  Free software by Ripon")
        c.setAlignment(Qt.AlignCenter)
        c.setStyleSheet("color:#64748b; font-size:11px; background:transparent; padding-top:10px;")
        v.addWidget(c)
        return rail

    # ---- navigation
    def go(self, name, force=False):
        if not force and name == self.current:
            return
        prev = self.pages[self.current]
        if self.current == "editor" and not prev.can_leave():
            return
        if hasattr(prev, "leave"):
            prev.leave()
        self.current = name
        page = self.pages[name]
        self.stack.setCurrentWidget(page)
        for k, b in self.nav.items():
            want = "true" if k == name else "false"
            if b.property("active") != want:
                set_prop(b, "active", want)
        if name == "home":
            page.refresh({k: self.pages[k].summary_text() for k in ("avro", "bijoy", "english")})
        if hasattr(page, "on_show"):
            page.on_show()
        if name not in ("para", "editor"):
            page.setFocus()

    def edit_wordlist(self, filename):
        self.go("editor")
        if self.current == "editor":
            self.pages["editor"].open_file(filename)

    def on_wordlist_saved(self, name):
        """A wordlist file was saved -> every page re-reads its lists immediately."""
        for k in ("avro", "bijoy", "english", "para"):
            self.pages[k].reload_wordlist()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def closeEvent(self, e):
        if not self.pages["editor"].can_leave():
            e.ignore()
            return
        for p in self.pages.values():
            if hasattr(p, "leave"):
                try:
                    p.leave()
                except Exception:
                    pass
        super().closeEvent(e)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")                 # same look on every Windows version - no native-style glitches
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(QSS)
    w = MainWindow()
    w.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
