"""Avro and Bijoy trainer pages (they share one screen; the engines hold the rules)."""
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

import avro_data as A
import engines
from engines import AvroEngine, BijoyEngine, bn_base_key, fmt_hms
from widgets import (ACCENTS, BAD, GOOD, INK, KIND_COLOR, MUTED, ChipsWidget, ItemView, KeyboardWidget,
                     PageHeader, Segmented, StatCard, accent_qss, card, font, make_btn, set_prop)
import bijoy_data as B


class TrainerBase(QWidget):
    go_home = Signal()

    def __init__(self, engine, title, subtitle, accent, bn_family, labels=None):
        super().__init__()
        self.setObjectName("page")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(accent_qss(accent))
        self.eng, self.bn, self.accent = engine, bn_family, accent

        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 22)
        root.setSpacing(16)
        self.header = PageHeader(title, subtitle, accent)
        self.header_controls(self.header)
        root.addWidget(self.header)

        body = QHBoxLayout()
        body.setSpacing(16)
        root.addLayout(body, 1)

        # ---------- left: levels
        lv = QVBoxLayout()
        lf = card(lv, (12, 14, 12, 12), 4)
        lf.setFixedWidth(258)
        cap = QLabel("LEVELS")
        cap.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:700; letter-spacing:2px; padding-left:6px;")
        lv.addWidget(cap)
        self.level_btns = []
        for i, nm in enumerate(self.level_names()):
            b = make_btn(nm, "level", lambda i=i: self.pick_level(i))
            b.setFont(font(bn_family, 17))
            lv.addWidget(b)
            self.level_btns.append(b)
        lv.addStretch(1)
        self.best = QLabel("")
        self.best.setStyleSheet(f"color:{MUTED}; font-size:12px; background:#f8fafc; border-radius:10px; padding:10px;")
        lv.addWidget(self.best)
        lv.addWidget(make_btn("↻   Restart level", "soft", lambda: self.engine_select()))
        body.addWidget(lf)

        # ---------- right
        col = QVBoxLayout()
        col.setSpacing(14)
        stats = QHBoxLayout()
        stats.setSpacing(14)
        self.stat = {k: StatCard(lab, ac) for k, lab, ac in (
            ("wpm", "SPEED · WPM", accent), ("acc", "ACCURACY", "#16a34a"),
            ("time", "TIME", "#f59e0b"), ("err", "ERRORS", "#dc2626"))}
        for w in self.stat.values():
            stats.addWidget(w)
        col.addLayout(stats)

        mid = QVBoxLayout()
        mf = card(mid, (26, 16, 26, 14), 6)
        top = QHBoxLayout()
        self.info = QLabel("")
        self.info.setStyleSheet(f"color:{MUTED}; font-size:12px; font-weight:600;")
        self.badge = QLabel("")
        self.badge.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top.addWidget(self.info, 1)
        top.addWidget(self.badge)
        mid.addLayout(top)
        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setTextVisible(False)
        mid.addWidget(self.bar)
        self.item = ItemView(bn_family)
        mid.addWidget(self.item, 3)
        self.chips = ChipsWidget()
        self.chips.accent = accent
        mid.addWidget(self.chips, 2)
        ob = QVBoxLayout()
        of = QFrame()
        of.setObjectName("outBox")
        of.setLayout(ob)
        ob.setContentsMargins(18, 8, 18, 8)
        ob.setSpacing(0)
        capo = QLabel("YOUR OUTPUT")
        capo.setStyleSheet(f"color:{MUTED}; font-size:10px; font-weight:700; letter-spacing:2px;")
        ob.addWidget(capo)
        self.out = QLabel("")
        self.out.setAlignment(Qt.AlignCenter)
        self.out.setFont(font(bn_family, 28, True))
        self.out.setMinimumHeight(46)
        ob.addWidget(self.out)
        mid.addWidget(of)
        col.addWidget(mf, 5)

        self.kb = KeyboardWidget(bn_family, labels)
        self.kb.accent = accent
        kv = QVBoxLayout()
        kv.addWidget(self.kb)
        col.addWidget(card(kv, (14, 10, 14, 10)), 4)
        body.addLayout(col, 1)

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.on_tick)

    # ---- hooks
    def header_controls(self, header): pass
    def level_names(self): raise NotImplementedError
    def engine_select(self): self.eng.select(self.eng.cur); self.refresh()
    def info_text(self): return ""
    def chip_mode(self): return "show"
    def hint_key(self): return None
    def progress_frac(self): return 0.0
    def stat_values(self): raise NotImplementedError
    def on_result(self, res, ch): pass
    def special_key(self, e): return False
    def refresh_side(self): pass

    def reload_wordlist(self):
        self.eng.reload()
        if self.isVisible():
            self.refresh()

    def on_show(self):
        self.timer.start()
        self.refresh()
        self.setFocus()

    def leave(self):
        self.timer.stop()

    def pick_level(self, i):
        self.eng.select(i)
        self.refresh()

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key_Escape:
            self.go_home.emit()
            return
        if self.special_key(e):
            self.refresh()
            return
        if k == Qt.Key_Backspace:
            if self.eng.backspace():
                self.refresh()
            return
        txt = e.text()
        if len(txt) != 1 or not txt.isprintable() or (e.modifiers() & Qt.ControlModifier):
            return
        if ord(txt) > 127:       # a Bangla/other keyboard layout is active -> ignore, warn
            self.badge.setText("⚠ Keyboard language English (US) korun")
            self.badge.setStyleSheet(f"color:{KIND_COLOR['warn']}; font-size:12px; font-weight:600;")
            return
        res = self.eng.on_char(txt)
        if res:
            self.on_result(res, txt)
        self.refresh()

    def on_tick(self):
        self.tick_engine()
        self.update_stats()

    def tick_engine(self):
        if self.eng.tick():
            self.refresh()

    def update_stats(self):
        for k, v in self.stat_values().items():
            self.stat[k].set(v)
        self.bar.setValue(int(1000 * min(1.0, self.progress_frac())))

    def refresh(self):
        e = self.eng
        for i, b in enumerate(self.level_btns):
            want = "true" if i == e.cur else "false"
            if b.property("active") != want:
                set_prop(b, "active", want)
        self.refresh_side()
        self.best.setText(e.best_text())
        self.info.setText(self.info_text())
        if e.summary:
            sm = e.summary
            self.item.set_item(sm["title"], GOOD if sm["good"] else BAD)
            self.chips.set_summary(sm["line1"], sm["line2"])
            self.kb.set_target(None)
        else:
            self.item.set_item(e.target, INK)
            self.chips.set_state(e.keys, e.pos, e.typed, self.chip_mode())
            hk = self.hint_key()
            self.kb.set_target(*(hk if hk else (None, False)))
        self.out.setText(e.out)
        self.out.setStyleSheet(f"color:{KIND_COLOR[e.out_kind]};")
        self.badge.setText(e.badge)
        self.badge.setStyleSheet(f"color:{KIND_COLOR[e.badge_kind]}; font-size:12px; font-weight:600;")
        self.update_stats()


# ======================================================================== Avro
class AvroPage(TrainerBase):
    def __init__(self, family):
        super().__init__(AvroEngine(), "অভ্র ফোনেটিক ট্রেনার", "Level 1-7 · Practice (timed) & Test (pass at 90%)",
                         ACCENTS["avro"], family)

    def header_controls(self, h):
        self.seg = Segmented((("practice", "Practice"), ("test", "Test")), self.set_mode)
        self.dur_btn = make_btn("", "soft", self.cycle_dur, "Click to change duration")
        self.pause_btn = make_btn("⏸  Pause  (F2)", "soft", self.toggle_pause)
        for w in (self.seg, self.dur_btn, self.pause_btn):
            h.add(w)

    def level_names(self):
        return list(A.LESSONS)

    def set_mode(self, m):
        self.eng.set_mode(m)
        self.refresh()

    def cycle_dur(self):
        self.eng.cycle_dur()
        self.refresh()

    def toggle_pause(self):
        self.eng.toggle_pause()
        self.refresh()

    def special_key(self, e):
        if e.key() == Qt.Key_F2:
            self.eng.toggle_pause()
            return True
        return False

    def leave(self):
        super().leave()
        if self.eng.began and not self.eng.paused and not self.eng.done:
            self.eng.toggle_pause()        # stop the clock + save time while away
        self.eng.commit()

    def refresh_side(self):
        e = self.eng
        self.seg.set_active(e.mode)
        self.dur_btn.setText(f"⏱  {e.limit_min} min")
        self.pause_btn.setText("▶  Resume  (F2)" if e.paused else "⏸  Pause  (F2)")
        self.stat["time"].title.setText("TIME LEFT")

    def info_text(self):
        e = self.eng
        if e.mode == "practice":
            return f"PRACTICE · {e.limit_min} min   ·   Stage: {e.stage}   ·   Line {e.line_no}"
        return f"TEST · {e.limit_min} min   ·   Line {e.line_no}   ·   ✓ {e.good}  ✗ {e.bad}   ·   keys hidden, Backspace allowed"

    def chip_mode(self):
        return "typed" if self.eng.mode == "test" else "show"

    def hint_key(self):
        e = self.eng
        if e.mode == "test" or e.pos >= len(e.keys):
            return None
        return bn_base_key(e.keys[e.pos])

    def progress_frac(self):
        return self.eng.elapsed() / self.eng.limit if self.eng.limit else 0

    def stat_values(self):
        el, wpm, acc = self.eng.stats()
        return {"wpm": f"{wpm:.0f}", "acc": f"{acc:.0f}%", "time": fmt_hms(self.eng.limit - el),
                "err": str(self.eng.err)}

    def on_result(self, res, ch):
        e = self.eng
        if res == "ok":
            k, _ = bn_base_key(ch)
            hk = self.hint_key()
            if e.mode == "practice" and (not hk or hk[0] != k):
                self.kb.flash(k, "#86efac")
        elif res == "bad":
            self.kb.flash(bn_base_key(ch)[0], "#fca5a5")
            if e.mode == "practice":
                self.item.shake()
                self.item.flash_color(BAD)

    def summary_text(self):
        secs = sum(v for k, v in self.eng.prog.items() if k.endswith("|secs") and isinstance(v, (int, float)))
        return f"{int(secs) // 3600}h {int(secs) % 3600 // 60:02d}m practised"


# ======================================================================== Bijoy
class BijoyPage(TrainerBase):
    def __init__(self, family):
        super().__init__(BijoyEngine(), "বিজয় ট্রেনার", "1 ঘণ্টা training প্রতি level · Test mode · F2 kar order",
                         ACCENTS["bijoy"], family, labels=B.LAB)

    def header_controls(self, h):
        self.seg = Segmented((("train", "Training"), ("test", "Test")), self.set_mode)
        self.kar_btn = make_btn("", "soft", self.toggle_kar, "F2")
        for w in (self.seg, self.kar_btn):
            h.add(w)

    def level_names(self):
        return self.eng.names

    def set_mode(self, m):
        self.eng.set_mode(m)
        self.refresh()

    def toggle_kar(self):
        self.eng.toggle_kar()
        self.refresh()

    def special_key(self, e):
        k, mods = e.key(), e.modifiers()
        if k == Qt.Key_F2:
            self.eng.toggle_kar()
        elif k == Qt.Key_F3:
            self.eng.toggle_mode()
        elif k == Qt.Key_R and mods & Qt.ControlModifier:
            self.eng.reset_hour()
        elif k in (Qt.Key_Return, Qt.Key_Enter) and self.eng.done:
            self.eng.next_level()
        else:
            return False
        return True

    def leave(self):
        super().leave()
        self.eng.save()

    def refresh_side(self):
        e = self.eng
        self.seg.set_active(e.mode)
        self.kar_btn.setText("⇄  " + e.L["mode"].split("\n")[0] + "  (F2)")
        for nm, b in zip(e.names, self.level_btns):
            b.setText(nm + ("     ✓" if e.level_done(nm) else ""))
        self.stat["time"].title.setText("TIME LEFT" if e.mode == "train" else "TIME")

    def info_text(self):
        e = self.eng
        if not e.order:
            return ""
        if e.mode == "train":
            return f"TRAINING · round {e.rounds} · item {e.idx + 1}/{len(e.order)}   ·   clock runs only while you type"
        return f"TEST · item {e.idx + 1}/{len(e.order)}   ·   random order, one pass   ·   F3 = Training"

    def chip_mode(self):
        return "hidden" if (self.eng.mode == "test" and not engines.TEST_HINTS) else "show"

    def hint_key(self):
        e = self.eng
        if e.pos < len(e.keys) and e.hints():
            return e.L["base_key"](e.keys[e.pos])
        return None

    def progress_frac(self):
        return self.eng.progress_frac()

    def stat_values(self):
        el, wpm, acc = self.eng.stats()
        return {"wpm": f"{wpm:.0f}", "acc": f"{acc:.0f}%", "time": self.eng.time_text(),
                "err": str(self.eng.err)}

    def tick_engine(self):
        self.eng.tick()
        if self.eng.summary and self.chips.summary is None:
            self.refresh()

    def on_result(self, res, ch):
        base = self.eng.L["base_key"]
        if res == "ok":
            hk = self.hint_key()
            if not hk or hk[0] != base(ch)[0]:
                self.kb.flash(base(ch)[0], "#86efac")
        elif res == "bad":
            self.kb.flash(base(ch)[0], "#fca5a5")
            self.item.shake()
            self.item.flash_color(BAD)

    def summary_text(self):
        done = sum(1 for nm in self.eng.names if self.eng.level_done(nm))
        return f"{done} / {len(self.eng.names)} levels completed"
