"""Reusable, self-painted widgets + the application theme (colors, QSS).
Everything dynamic is drawn with QPainter and only repainted when state changes."""
from PySide6.QtCore import Qt, QRectF, QTimer, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

import english_data as E

# ---------------------------------------------------------------- theme
BG, CARD, INK, MUTED = "#f4f6fb", "#ffffff", "#0f172a", "#64748b"
LINE = "#e3e8f0"
ACC, ACC_DARK, GOOD, BAD, SOFT = "#4f46e5", "#4338ca", "#16a34a", "#dc2626", "#eef1f8"
WARN = "#f59e0b"
KIND_COLOR = {"ink": INK, "muted": MUTED, "good": GOOD, "bad": BAD, "warn": WARN}
ACCENTS = {"avro": "#0d9488", "bijoy": "#ea580c", "english": "#2563eb",
           "para": "#7c3aed", "editor": "#0891b2", "home": ACC}

QSS = f"""
* {{ outline: 0; }}
QWidget#root, QWidget#page {{ background: {BG}; }}
QLabel {{ color: {INK}; background: transparent; }}
QToolTip {{ color: {INK}; background: white; border: 1px solid {LINE}; padding: 4px 6px; }}

/* ---------- buttons */
QPushButton {{ border: 1px solid {LINE}; border-radius: 10px; padding: 8px 16px; background: {CARD};
              color: {INK}; font-size: 13px; }}
QPushButton:hover {{ background: #f1f4fb; border-color: #cfd6e6; }}
QPushButton:pressed {{ background: #e6eaf5; }}
QPushButton:disabled {{ color: #a3adc0; background: #f4f6fb; }}
QPushButton[kind="primary"] {{ background: {ACC}; color: white; border: none; font-weight: 600; }}
QPushButton[kind="primary"]:hover {{ background: {ACC_DARK}; }}
QPushButton[kind="danger"] {{ background: #fee2e2; color: #b91c1c; border: none; font-weight: 600; }}
QPushButton[kind="danger"]:hover {{ background: #fecaca; }}
QPushButton[kind="green"] {{ background: {GOOD}; color: white; border: none; font-weight: 600; }}
QPushButton[kind="green"]:hover {{ background: #15803d; }}
QPushButton[kind="ghost"] {{ background: transparent; border: none; color: {MUTED}; }}
QPushButton[kind="ghost"]:hover {{ background: {SOFT}; color: {INK}; }}
QPushButton[kind="level"] {{ background: transparent; border: none; text-align: left; padding: 10px 14px;
              border-radius: 10px; color: {INK}; }}
QPushButton[kind="level"]:hover {{ background: {SOFT}; }}
QPushButton[kind="level"][active="true"] {{ background: {ACC}; color: white; font-weight: 600; }}
QPushButton[kind="seg"] {{ background: transparent; border: none; border-radius: 8px; padding: 7px 16px;
              color: {MUTED}; font-weight: 600; }}
QPushButton[kind="seg"]:hover {{ color: {INK}; }}
QPushButton[kind="seg"][active="true"] {{ background: {CARD}; color: {INK}; border: 1px solid {LINE}; }}
QPushButton[kind="nav"] {{ background: transparent; border: none; border-left: 3px solid transparent;
              border-radius: 0; text-align: left; padding: 11px 18px; color: #cbd5e1; font-size: 14px; }}
QPushButton[kind="nav"]:hover {{ background: rgba(255,255,255,0.07); color: white; }}
QPushButton[kind="nav"][active="true"] {{ background: rgba(255,255,255,0.13); color: white;
              border-left: 3px solid #a5b4fc; font-weight: 600; }}
QPushButton[kind="navfoot"] {{ background: transparent; border: 1px solid rgba(255,255,255,0.18);
              color: #cbd5e1; padding: 7px 10px; font-size: 12px; }}
QPushButton[kind="navfoot"]:hover {{ background: rgba(255,255,255,0.1); color: white; }}

/* ---------- surfaces */
QFrame[card="true"] {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 16px; }}
QFrame#seg {{ background: {SOFT}; border: none; border-radius: 11px; }}
QFrame#rail {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #0f172a, stop:1 #1e1b4b); }}
QFrame#hero {{ border: none; border-radius: 20px;
              background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #4f46e5, stop:1 #7c3aed); }}
QFrame#modeCard {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 16px; }}
QFrame#modeCard:hover {{ border: 1px solid {ACC}; }}
QFrame#outBox {{ background: #f8fafc; border: 1px solid {LINE}; border-radius: 12px; }}
QProgressBar {{ background: {SOFT}; border: none; border-radius: 3px; min-height: 6px; max-height: 6px; }}
QProgressBar::chunk {{ background: {ACC}; border-radius: 3px; }}

/* ---------- inputs */
QPlainTextEdit, QTextEdit, QListWidget, QTreeWidget, QLineEdit {{ background: {CARD}; border: 1px solid {LINE};
              border-radius: 12px; padding: 8px; color: {INK}; selection-background-color: #c7d2fe;
              selection-color: {INK}; }}
QPlainTextEdit:focus, QLineEdit:focus {{ border: 1px solid {ACC}; }}
QTreeWidget, QListWidget {{ padding: 4px; }}
QTreeWidget::item, QListWidget::item {{ padding: 6px 8px; border-radius: 8px; }}
QTreeWidget::item:selected, QListWidget::item:selected {{ background: #e0e7ff; color: {INK}; }}
QTreeWidget::item:hover, QListWidget::item:hover {{ background: {SOFT}; }}
QCheckBox {{ color: {INK}; spacing: 8px; }}

/* ---------- slim scrollbars */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #cbd5e1; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #94a3b8; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: #cbd5e1; border-radius: 4px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
"""


def set_prop(w, name, value):
    """Change a dynamic property and make Qt re-apply the stylesheet."""
    w.setProperty(name, value)
    w.style().unpolish(w)
    w.style().polish(w)


def make_btn(text, kind="soft", cb=None, tip=None):
    b = QPushButton(text)
    b.setFocusPolicy(Qt.NoFocus)          # buttons must never steal the typing focus
    b.setCursor(Qt.PointingHandCursor)
    b.setProperty("kind", kind)
    if cb:
        b.clicked.connect(lambda _=False: cb())
    if tip:
        b.setToolTip(tip)
    return b


def card(layout=None, margins=(18, 16, 18, 16), spacing=8):
    f = QFrame()
    f.setProperty("card", "true")
    if layout is not None:
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)
        f.setLayout(layout)
    return f


def font(family, px, bold=False):
    f = QFont(family)
    f.setPixelSize(max(6, int(px)))
    f.setBold(bold)
    return f


def accent_qss(accent):
    """Per-page accent: level list, progress bar, primary buttons."""
    return (f"QPushButton[kind='level'][active='true'] {{ background: {accent}; color: white; }}"
            f"QProgressBar::chunk {{ background: {accent}; }}"
            f"QPushButton[kind='primary'] {{ background: {accent}; }}"
            f"QPushButton[kind='primary']:hover {{ background: {accent}; }}"
            f"QPlainTextEdit:focus, QLineEdit:focus {{ border: 1px solid {accent}; }}")


# ---------------------------------------------------------------- header / segmented / stat card
class PageHeader(QWidget):
    """Title + subtitle on the left, free slot (controls) on the right."""

    def __init__(self, title, subtitle, accent=ACC):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        bar = QFrame()
        bar.setFixedSize(5, 40)
        bar.setStyleSheet(f"background:{accent}; border-radius:2px; border:none;")
        lay.addWidget(bar)
        tv = QVBoxLayout()
        tv.setSpacing(0)
        self.title = QLabel(title)
        self.title.setStyleSheet(f"font-size:24px; font-weight:700; color:{INK};")
        self.sub = QLabel(subtitle)
        self.sub.setStyleSheet(f"font-size:13px; color:{MUTED};")
        tv.addWidget(self.title)
        tv.addWidget(self.sub)
        lay.addLayout(tv)
        lay.addStretch(1)
        self.right = QHBoxLayout()
        self.right.setSpacing(10)
        lay.addLayout(self.right)

    def add(self, w):
        self.right.addWidget(w)


class Segmented(QFrame):
    """Pill-style toggle:  [ Practice | Test ]"""

    def __init__(self, items, on_change):
        super().__init__()
        self.setObjectName("seg")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(2)
        self.btns = {}
        for key, label in items:
            b = make_btn(label, "seg", lambda k=key: on_change(k))
            self.btns[key] = b
            lay.addWidget(b)

    def set_active(self, key):
        for k, b in self.btns.items():
            want = "true" if k == key else "false"
            if b.property("active") != want:
                set_prop(b, "active", want)


class StatCard(QFrame):
    def __init__(self, title, accent=ACC):
        super().__init__()
        self.setProperty("card", "true")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 16, 10)
        lay.setSpacing(12)
        bar = QFrame()
        bar.setFixedWidth(4)
        bar.setStyleSheet(f"background:{accent}; border-radius:2px; border:none;")
        lay.addWidget(bar)
        v = QVBoxLayout()
        v.setSpacing(0)
        self.title = QLabel(title)
        self.title.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:600; letter-spacing:1px;")
        self.value = QLabel("0")
        self.value.setStyleSheet(f"color:{INK}; font-size:24px; font-weight:700;")
        v.addWidget(self.title)
        v.addWidget(self.value)
        lay.addLayout(v)
        lay.addStretch(1)

    def set(self, text):
        if self.value.text() != text:
            self.value.setText(text)


# ---------------------------------------------------------------- big item
class ItemView(QWidget):
    """The big Bangla item to type. Auto-shrinks to fit, shakes on a wrong key."""

    def __init__(self, family):
        super().__init__()
        self.family, self._text, self._color, self._dx = family, "", QColor(INK), 0.0
        self.setMinimumHeight(110)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(240)
        for t, v in ((0, 0), (.2, 10), (.4, -10), (.6, 8), (.8, -6), (1, 0)):
            self._anim.setKeyValueAt(t, float(v))
        self._anim.valueChanged.connect(self._set_dx)
        self._token = 0

    def _set_dx(self, v):
        self._dx = float(v)
        self.update()

    def set_item(self, text, color=INK):
        self._text, self._color = text, QColor(color)
        self.update()

    def shake(self):
        self._anim.stop()
        self._anim.start()

    def flash_color(self, color, ms=220):
        self._token += 1
        tok, old = self._token, self._color
        self._color = QColor(color)
        self.update()

        def back():
            if tok == self._token:
                self._color = QColor(INK)
                self.update()
        QTimer.singleShot(ms, back)

    def paintEvent(self, _e):
        if not self._text:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        px = min(self.height() * 0.62, 84)
        f = font(self.family, px, True)
        p.setFont(f)
        while px > 18 and p.fontMetrics().horizontalAdvance(self._text) > self.width() - 40:
            px -= 3
            f.setPixelSize(int(px))
            p.setFont(f)
        p.setPen(self._color)
        p.drawText(QRectF(self._dx, 0, self.width(), self.height()), Qt.AlignCenter, self._text)


# ---------------------------------------------------------------- key chips
class ChipsWidget(QWidget):
    """Row of key chips (scrolls in a 16-key window for long lines)."""
    VIS = 16

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(70)
        self.keys, self.pos, self.typed, self.mode = "", 0, "", "show"   # show | typed | hidden
        self.summary = None
        self.accent = ACC
        self.mono = font("Consolas", 22, True)
        self.fam = "Segoe UI"

    def set_state(self, keys, pos, typed, mode):
        self.keys, self.pos, self.typed, self.mode, self.summary = keys, pos, typed, mode, None
        self.update()

    def set_summary(self, l1, l2):
        self.summary = (l1, l2)
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self.summary:
            p.setPen(QColor(MUTED))
            p.setFont(font(self.fam, 17, True))
            p.drawText(QRectF(0, 0, self.width(), self.height() / 2), Qt.AlignCenter, self.summary[0])
            p.setFont(font(self.fam, 14))
            p.drawText(QRectF(0, self.height() / 2, self.width(), self.height() / 2), Qt.AlignCenter,
                       self.summary[1])
            return
        if self.mode == "hidden" or not self.keys:
            return
        n, pos = len(self.keys), self.pos
        a = max(0, min(pos - 7, n - self.VIS))
        b = min(n, a + self.VIS)
        m = b - a
        sc = max(.55, min(1.3, self.width() / 860, self.height() / 62))
        cw, gap, ch = 40 * sc, 6 * sc, 44 * sc
        x0 = (self.width() - (m * (cw + gap) - gap)) / 2
        y = (self.height() - ch) / 2
        f = QFont(self.mono)
        f.setPixelSize(int(22 * sc))
        p.setFont(f)
        for j, i in enumerate(range(a, b)):
            x, key = x0 + j * (cw + gap), self.keys[i]
            txt = key
            if self.mode == "typed":
                if i < pos:
                    t = self.typed[i]
                    ok = t == key
                    fill, fg, txt = ("#dcfce7", GOOD, t) if ok else ("#fee2e2", BAD, t)
                else:
                    fill, fg, txt = (self.accent, "white", "") if i == pos else ("#eef1f8", INK, "")
            else:
                fill, fg = (("#dcfce7", GOOD) if i < pos else (self.accent, "white") if i == pos
                            else ("#eef1f8", INK))
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(fill))
            r = QRectF(x, y, cw, ch)
            p.drawRoundedRect(r, 10 * sc, 10 * sc)
            p.setPen(QColor(fg))
            p.drawText(r, Qt.AlignCenter, "␣" if txt == " " else txt)
        p.setPen(QColor(MUTED))
        if a > 0:
            p.drawText(QRectF(x0 - 30 * sc, y, 24 * sc, ch), Qt.AlignCenter, "‹")
        if b < n:
            p.drawText(QRectF(x0 + m * (cw + gap) + 4 * sc, y, 24 * sc, ch), Qt.AlignCenter, "›")


# ---------------------------------------------------------------- keyboard
ROWS = ["`1234567890-=", "qwertyuiop[]", "asdfghjkl;'", "zxcvbnm,./"]
ROWOFF = [0, 22, 30, 44]
FING = ["`1qaz", "2wsx", "3edc", "4rfv5tgb", "6yhn7ujm", "8ik,", "9ol.", "0p;/-[]'="]
FCOL = ["#fde2e4", "#ffe8cc", "#fff3bf", "#d3f9d8", "#d0ebff", "#e5dbff", "#fcc2d7", "#e9ecef"]
FMAP = {ch: FCOL[i] for i, g in enumerate(FING) for ch in g}


class KeyboardWidget(QWidget):
    LW, LH = 700, 240

    def __init__(self, bn_family, labels=None):
        super().__init__()
        self.setMinimumHeight(150)
        self.bn, self.labels = bn_family, labels
        self.accent = ACC
        self.target, self.shift, self.flashes = None, False, {}
        self.rects = {}
        K, P_, x0, y0 = 42, 46, 60, 8
        for r, row in enumerate(ROWS):
            for i, ch in enumerate(row):
                self.rects[ch] = (QRectF(x0 + ROWOFF[r] + i * P_, y0 + r * P_, K, K), FMAP.get(ch, "#e9ecef"))
        self.rects["shift"] = (QRectF(x0 - 55, y0 + 3 * P_, 95, K), "#e9ecef")
        self.rects[" "] = (QRectF(x0 + 90, y0 + 4 * P_, 330, K), "#e9ecef")

    def set_labels(self, labels):
        self.labels = labels
        self.update()

    def set_target(self, key, shift=False):
        if (key, shift) != (self.target, self.shift):
            self.target, self.shift = key, shift
            self.update()

    def flash(self, key, color):
        if key in self.rects:
            self.flashes[key] = color
            self.update()
            QTimer.singleShot(260, lambda: self._unflash(key, color))

    def _unflash(self, key, color):
        if self.flashes.get(key) == color:
            del self.flashes[key]
            self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = min(self.width() / self.LW, self.height() / self.LH)
        p.translate((self.width() - self.LW * s) / 2, (self.height() - self.LH * s) / 2)
        p.scale(s, s)
        for name, (rect, base) in self.rects.items():
            is_t = name == self.target
            col = self.flashes.get(name) or (self.accent if is_t else WARN if (name == "shift" and self.shift) else base)
            p.setPen(QPen(QColor("#00000014"), 1))
            p.setBrush(QColor(col))
            p.drawRoundedRect(rect, 8, 8)
            p.setPen(QColor("white" if (is_t or (name == "shift" and self.shift)) else INK))
            if name == " ":
                p.setFont(font("Segoe UI", 14))
                p.drawText(rect, Qt.AlignCenter, "SPACE")
            elif name == "shift":
                p.setFont(font("Segoe UI", 14))
                p.drawText(rect, Qt.AlignCenter, "SHIFT")
            elif self.labels and name in self.labels:
                n, sh = self.labels[name]
                p.setFont(font(self.bn, 17))
                p.drawText(QRectF(rect.x(), rect.y() + 8, rect.width() * .7, rect.height() - 8), Qt.AlignCenter, n)
                if sh:
                    p.setFont(font(self.bn, 12))
                    p.drawText(QRectF(rect.x() + rect.width() * .55, rect.y() + 1, rect.width() * .45,
                                      rect.height() * .45), Qt.AlignCenter, sh)
            else:
                p.setFont(font("Segoe UI", 15, True))
                p.drawText(rect, Qt.AlignCenter, name.upper())


# ---------------------------------------------------------------- english practice canvas
class EnglishCanvas(QWidget):
    """Typing-Master style practice area (tiles + keyboard + hands), drawn from engine state."""
    LW, LH = 700, 540
    KU, KH, KX, KY = E.KU, E.KH, E.KX, E.KY

    def __init__(self, engine):
        super().__init__()
        self.eng = engine
        self.setMinimumSize(560, 430)
        self.keyrects = {}
        KU, KH, KX, KY = self.KU, self.KH, self.KX, self.KY

        def add(name, x, y, w, label, color, fs=11):
            self.keyrects[name] = (QRectF(x + KX, y + KY, w, KH), label, color, fs)

        for r, row in enumerate(E.ROWS):
            for i, k in enumerate(row):
                label = k.upper() if k.isalpha() else f"{E.SHIFT_UP[k]}\n{k}"
                add(k, E.ROW_X[r] + i * KU, r * KU, KH, label, E.COLORS[E.KEY_FINGER[k]], 11 if k.isalpha() else 9)
        add("<Back>", 572, 0, 62, "Back", E.MOD, 9)
        add("<Tab>", 0, KU, 58, "Tab", E.MOD, 9)
        add("<Caps>", 0, 2 * KU, 70, "Caps", E.MOD, 9)
        add("<Enter>", 558, 2 * KU, 76, "Enter", E.MOD, 9)
        add("LSHIFT", 0, 3 * KU, 94, "Shift", E.MOD, 10)
        add("RSHIFT", 538, 3 * KU, 96, "Shift", E.MOD, 10)
        add(" ", 170, 4 * KU, 300, "Space", E.COLORS["Thumb"], 10)
        fx = lambda k: self.keyrects[k][0].center().x()
        self.fx = fx
        hands = [("Left pinky", "a", 455), ("Left ring", "s", 432), ("Left middle", "d", 422),
                 ("Left index", "f", 432), ("Right index", "j", 432), ("Right middle", "k", 422),
                 ("Right ring", "l", 432), ("Right pinky", ";", 455)]
        self.fingers = {}
        for name, k, top in hands:
            x = fx(k)
            self.fingers.setdefault(name, []).append(QRectF(x - 17, top, 34, 95))
        for x in (fx("f") + 52, fx("j") - 52):
            self.fingers.setdefault("Thumb", []).append(QRectF(x - 15, 468, 30, 72))
        self.palms = [QRectF(fx("a") - 26, 490, fx("f") + 60 - (fx("a") - 26), 150),
                      QRectF(fx("j") - 60, 490, fx(";") + 26 - (fx("j") - 60), 150)]

    def paintEvent(self, _e):
        eng = self.eng
        if not eng.lesson:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = min(self.width() / self.LW, self.height() / self.LH)
        p.translate((self.width() - self.LW * s) / 2, (self.height() - self.LH * s) / 2)
        p.scale(s, s)
        p.setClipRect(QRectF(0, 0, self.LW, self.LH))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#ffffff"))
        p.drawRoundedRect(QRectF(0, 0, self.LW, self.LH), 18, 18)

        self._tiles(p)
        self._keyboard(p)
        if eng.state == "paused":
            self._box(p, QRectF(120, 170, 460, 120), "Paused", None, None)
        elif eng.state == "done":
            wpm, acc = eng.stats()
            self._box(p, QRectF(70, 60, 560, 280),
                      "Lesson complete!" if eng.is_last() else "Stage complete!",
                      f"Speed:  {wpm:.0f} WPM        Accuracy:  {acc:.0f}%        Errors:  {eng.errors}",
                      (eng.verdict, "Press Next to finish and save" if eng.is_last() else "Press Next to continue"))

    def _tiles(self, p):
        eng = self.eng
        small = eng.stage["small"]
        cw, sw = E.tw(small)
        th, gap, rows = (26, 34, 4) if small else (38, 56, 2)
        for r in range(min(rows, len(eng.lines))):
            x, y = 34, 46 + r * gap
            for j, ch in enumerate(eng.lines[r]):
                sp = ch == " "
                done, cur = r == 0 and j < eng.ci, r == 0 and j == eng.ci
                w = 20 if small else (52 if sp else 34)
                if done:
                    fill, line, txt, lw = "#dcfce7", "#4ade80", "#15803d", 2
                elif cur:
                    fill, line, txt, lw = (("#fee2e2", "#dc2626", "#7f1d1d", 3) if eng.flash
                                           else ("white", "#2563eb", "#1e3a8a", 3))
                elif r == 0:
                    fill, line, txt, lw = "#f1f5f9", "#cbd5e1", "#64748b", 2
                else:
                    fill, line, txt, lw = "#f8fafc", "#e2e8f0", "#94a3b8", 2
                p.setPen(QPen(QColor(line), lw))
                p.setBrush(QColor(fill))
                rect = QRectF(x, y, w, th)
                p.drawRect(rect)
                p.setPen(QColor(txt))
                label = ("·" if small else "Space") if sp else ch
                p.setFont(font("Segoe UI", 16 if small else (11 if sp else 22), True))
                p.drawText(rect, Qt.AlignCenter, label)
                x += sw if sp else cw

    def _keyboard(self, p):
        eng = self.eng
        keys, fingers = eng.target_keys()
        for name, (rect, label, color, fs) in self.keyrects.items():
            hot = name in keys
            p.setPen(QPen(QColor("#f59e0b" if hot else "#cbd5e1"), 3 if hot else 2))
            p.setBrush(QColor("#fde68a" if hot else color))
            p.drawRect(rect)
            p.setPen(QColor("#475569"))
            p.setFont(font("Segoe UI", fs * 1.35, True))
            p.drawText(rect, Qt.AlignCenter, label)
        skin, edge = QColor("#f3c9a6"), QColor("#d9a37c")
        p.setPen(QPen(edge, 1))
        p.setBrush(skin)
        for pr in self.palms:
            p.drawEllipse(pr)
        for name, rects in self.fingers.items():
            p.setPen(QPen(edge, 2))
            p.setBrush(QColor("#ffb347") if name in fingers else skin)
            for r in rects:
                p.drawEllipse(r)
        p.setPen(QColor("#7a5c00"))
        p.setFont(font("Segoe UI", 15, True))
        p.drawText(QRectF(0, 392, self.LW, 28), Qt.AlignCenter, eng.hint_text())

    def _box(self, p, rect, title, l1, extra):
        p.setPen(QPen(QColor("#2563eb"), 3))
        p.setBrush(QColor("white"))
        p.drawRoundedRect(rect, 10, 10)
        p.setPen(QColor("#2563eb"))
        p.setFont(font("Segoe UI", 34, True))
        p.drawText(QRectF(rect.x(), rect.y() + 8, rect.width(), 60 if l1 else rect.height() - 16), Qt.AlignCenter, title)
        if l1:
            p.setPen(QColor("#222"))
            p.setFont(font("Segoe UI", 19, True))
            p.drawText(QRectF(rect.x(), rect.y() + 90, rect.width(), 40), Qt.AlignCenter, l1)
            p.setPen(QColor("#444"))
            p.setFont(font("Segoe UI", 16))
            p.drawText(QRectF(rect.x(), rect.y() + 150, rect.width(), 36), Qt.AlignCenter, extra[0])
            p.setPen(QColor("#888"))
            p.setFont(font("Segoe UI", 14))
            p.drawText(QRectF(rect.x(), rect.y() + 215, rect.width(), 32), Qt.AlignCenter, extra[1])


class BarsWidget(QWidget):
    """The 10 rising progress bars of the English trainer."""

    def __init__(self):
        super().__init__()
        self.frac = 0.0
        self.setMinimumSize(190, 120)

    def set_frac(self, f):
        if f != self.frac:
            self.frac = f
            self.update()

    def paintEvent(self, _e):
        import math
        p = QPainter(self)
        s = min(self.width() / 196, self.height() / 122)
        p.scale(s, s)
        filled = math.ceil(self.frac * 10 - 1e-9) if self.frac > 0 else 0
        p.setPen(QColor("#222"))
        for i in range(10):
            h, x = 22 + i * 10, 6 + i * 18
            p.setBrush(QColor("#7bd13b" if i < filled else "#eaffc4"))
            p.drawRect(QRectF(x, 118 - h, 13, h))
