"""English (Typing-Master style) trainer page."""
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout, QWidget

import english_data as E
from engines import EnglishEngine
from widgets import (ACCENTS, INK, MUTED, BarsWidget, EnglishCanvas, PageHeader, accent_qss, card, make_btn)


def _page():
    w = QWidget()
    w.setObjectName("page")
    w.setAttribute(Qt.WA_StyledBackground, True)
    return w


class EnglishPage(QWidget):
    go_home = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("page")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(accent_qss(ACCENTS["english"]))
        self.eng = EnglishEngine()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        outer.addWidget(self.stack)
        self.menu, self.practice = _page(), _page()
        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.practice)
        self.build_practice()
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.on_tick)
        self.build_menu()

    # ------------------------------------------------------------ menu
    def build_menu(self):
        old = self.menu.layout()
        if old:
            QWidget().setLayout(old)       # drop previous layout (and its children) cleanly
        lay = QVBoxLayout(self.menu)
        lay.setContentsMargins(26, 22, 26, 22)
        lay.setSpacing(16)
        lay.addWidget(PageHeader("English Typing Tutor",
                                 "Touch typing step by step - home row → full sentences", ACCENTS["english"]))
        levels = E.LEVELS
        if not levels:
            msg = QLabel("Wordlist pawa jay ni.\n\nwordlist/english_*.txt file gulo khali ba nai.\n"
                         "'Wordlist Editor' theke file gulo fill korun.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet(f"color:{MUTED}; font-size:16px;")
            lay.addWidget(msg, 1)
            return
        row = QHBoxLayout()
        row.setSpacing(14)
        for lv in levels:
            cv = QVBoxLayout()
            cf = QFrame()
            cf.setObjectName("modeCard")
            cf.setLayout(cv)
            cv.setContentsMargins(0, 0, 0, 14)
            cv.setSpacing(6)
            h = QLabel(lv["name"])
            h.setAlignment(Qt.AlignCenter)
            h.setStyleSheet(f"background:{lv['color']}; color:white; font-size:18px; font-weight:700;"
                            f"border-top-left-radius:15px; border-top-right-radius:15px; padding:12px;")
            cv.addWidget(h)
            tt = QLabel(lv["title"])
            tt.setAlignment(Qt.AlignCenter)
            tt.setStyleSheet("font-size:16px; font-weight:700; padding-top:6px;")
            kk = QLabel(lv["keys"])
            kk.setAlignment(Qt.AlignCenter)
            kk.setWordWrap(True)
            kk.setStyleSheet(f"color:{MUTED}; font-size:12px; padding:0 8px 6px 8px;")
            cv.addWidget(tt)
            cv.addWidget(kk)
            for ls in lv["lessons"]:
                mins = sum(s["mins"] for s in ls["stages"])
                txt = f"{ls['id']}   {ls['title']}\n{mins} min"
                best = self.eng.progress.get(ls["id"])
                if best:
                    txt += f"   ✓ {best['wpm']} wpm"
                b = make_btn(txt, "soft", lambda l=ls: self.start(l))
                b.setStyleSheet("QPushButton{text-align:left; margin:0 12px; padding:10px 12px; background:#f1f5f9; border:none;}"
                                "QPushButton:hover{background:#e2e8f0;}")
                cv.addWidget(b)
            cv.addStretch(1)
            row.addWidget(cf, 1)
        lay.addLayout(row)
        lay.addStretch(1)
        foot = QLabel("Every stage is a timed drill. Type the highlighted key - a wrong key will not move forward.   "
                      "Aim for 90% accuracy first, speed comes later.   ·   Esc = back")
        foot.setAlignment(Qt.AlignCenter)
        foot.setStyleSheet(f"color:{MUTED}; font-size:12px;")
        lay.addWidget(foot)

    # ------------------------------------------------------------ practice
    def build_practice(self):
        lay = QVBoxLayout(self.practice)
        lay.setContentsMargins(26, 22, 26, 22)
        lay.setSpacing(16)
        self.head = PageHeader("", "", ACCENTS["english"])
        self.head.add(make_btn("☰  Lessons", "soft", self.show_menu))
        lay.addWidget(self.head)
        body = QHBoxLayout()
        body.setSpacing(16)
        lay.addLayout(body, 1)
        self.canvas = EnglishCanvas(self.eng)
        cf = QVBoxLayout()
        cf.addWidget(self.canvas)
        body.addWidget(card(cf, (10, 10, 10, 10)), 1)
        rv = QVBoxLayout()
        rf = card(rv, (18, 16, 18, 16), 8)
        rf.setFixedWidth(270)
        h = QLabel("YOUR PROGRESS")
        h.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:700; letter-spacing:2px;")
        rv.addWidget(h)
        self.bars = BarsWidget()
        rv.addWidget(self.bars)
        tm = QHBoxLayout()
        tl = QLabel("TIME")
        tl.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:700; letter-spacing:2px;")
        tm.addWidget(tl)
        tm.addStretch(1)
        self.pause_btn = make_btn("Pause", "soft", self.pause)
        tm.addWidget(self.pause_btn)
        rv.addLayout(tm)
        self.time_lbl = QLabel("00:00")
        self.time_lbl.setStyleSheet(f"font-family:Consolas; font-size:38px; font-weight:700; color:{INK};")
        rv.addWidget(self.time_lbl)
        self.wpm_lbl, self.acc_lbl, self.err_lbl = QLabel(), QLabel(), QLabel()
        for w in (self.wpm_lbl, self.acc_lbl, self.err_lbl):
            w.setStyleSheet("font-size:16px;")
            rv.addWidget(w)
        rv.addStretch(1)
        self.next_btn = make_btn("Next  →", "primary", self.next)
        rv.addWidget(self.next_btn)
        rv.addWidget(make_btn("↻   Repeat stage", "soft", self.repeat))
        body.addWidget(rf)

    def on_show(self):
        self.timer.start()
        self.build_menu()
        self.stack.setCurrentIndex(0)
        self.setFocus()

    def reload_wordlist(self):
        E.reload()
        self.build_menu()
        self.stack.setCurrentIndex(0)

    def leave(self):
        self.timer.stop()
        if self.eng.state == "run":
            self.eng.pause_toggle()

    def summary_text(self):
        total = sum(len(lv["lessons"]) for lv in E.LEVELS)
        done = sum(1 for lv in E.LEVELS for ls in lv["lessons"] if ls["id"] in self.eng.progress)
        return f"{done} / {total} lessons completed"

    def show_menu(self):
        if self.eng.state == "run":
            self.eng.pause_toggle()
        self.stack.setCurrentIndex(0)
        self.build_menu()
        self.setFocus()

    def start(self, lesson):
        self.eng.start(lesson)
        self.stack.setCurrentIndex(1)
        self.next_btn.setText("Next  →")
        self.refresh()
        self.setFocus()

    def next(self):
        if self.stack.currentIndex() != 1:
            return
        if self.eng.next():
            self.show_menu()
            return
        self.next_btn.setText("Finish" if self.eng.is_last() else "Next  →")
        self.refresh()

    def repeat(self):
        if self.stack.currentIndex() == 1:
            self.eng.repeat()
            self.refresh()
            self.setFocus()

    def pause(self):
        self.eng.pause_toggle()
        self.refresh()
        self.setFocus()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            if self.stack.currentIndex() == 1:
                self.show_menu()
            else:
                self.go_home.emit()
            return
        if self.stack.currentIndex() != 1:
            return
        txt = e.text()
        if len(txt) != 1 or (e.modifiers() & Qt.ControlModifier):
            return
        res = self.eng.on_char(txt)
        if res == "bad":
            QTimer.singleShot(180, self.unflash)
        if res:
            self.refresh()

    def unflash(self):
        self.eng.flash = False
        self.canvas.update()

    def on_tick(self):
        if self.stack.currentIndex() != 1:
            return
        if self.eng.tick():
            self.next_btn.setText("Finish" if self.eng.is_last() else "Next  →")
        self.refresh()

    def refresh(self):
        e = self.eng
        if not e.lesson:
            return
        self.head.title.setText(f"Lesson {e.lesson['id']} · {e.lesson['title']}")
        self.head.sub.setText(f"Stage {e.si + 1}/{len(e.lesson['stages'])}:  {e.stage['name']}")
        wpm, acc = e.stats()
        left = e.time_left()
        self.time_lbl.setText(f"{left // 60:02d}:{left % 60:02d}")
        self.wpm_lbl.setText(f"Speed:  {wpm:.0f} WPM")
        self.acc_lbl.setText(f"Accuracy:  {acc:.0f}%")
        self.err_lbl.setText(f"Errors:  {e.errors}")
        self.bars.set_frac(min(1, e.elapsed() / e.total_sec) if e.total_sec else 1)
        self.pause_btn.setText("Resume" if e.state == "paused" else "Pause")
        self.canvas.update()
