"""
Qt-free logic for all three trainers (Avro / Bijoy / English).

Keeping the logic away from the GUI is deliberate: the screen only *draws* the
engine state, so there is no canvas rebuilding, no per-key widget churn and the
logic can be tested without a window.  Behaviour is ported 1:1 from the old
tkinter trainers (same levels, same save files, same rules).
"""
import json
import math
import os
import random
import time

import avro_data as A
import bijoy_data as B
import english_data as E

HOME = os.path.expanduser("~")
AVRO_SAVE = os.path.join(HOME, ".bangla_typing_progress.json")
ENGLISH_SAVE = os.path.join(HOME, ".typing_tutor_progress.json")


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except Exception:
        return default


def save_json(path, data):
    """Atomic write - a crash or power-cut while saving can never corrupt progress."""
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, path)
        return True
    except Exception:
        return False


def mmss(sec):
    sec = int(max(0, sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


def fmt_hms(sec):
    sec = int(max(0, sec))
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# --------------------------------------------------------------------------
# keyboard helpers shared by Avro / Bijoy
# --------------------------------------------------------------------------
SHIFTED_BN = {":": ";", "^": "6"}


def bn_base_key(ch):
    if ch in SHIFTED_BN:
        return SHIFTED_BN[ch], True
    if ch.isalpha():
        return ch.lower(), ch.isupper()
    return ch, False


# ==========================================================================
# AVRO
# ==========================================================================
class AvroEngine:
    """Practice (timed, endless lines) and Test (timed, keys hidden, backspace allowed)."""

    def __init__(self):
        self.prog = load_json(AVRO_SAVE, {})
        self.mode = "practice"
        self.dur_idx = {"practice": len(A.PRACTICE_MIN) - 1, "test": 1}
        self.names = list(A.LESSONS)
        self.cur = 0
        self.name = None
        self.select(0)

    # -- persistence
    def save(self):
        save_json(AVRO_SAVE, self.prog)

    def commit(self):
        """Add the practice seconds of this session to the saved total of the level."""
        if self.name and self.mode == "practice":
            el = self.elapsed()
            d = el - self.committed
            if d > 0:
                k = self.name + "|secs"
                self.prog[k] = self.prog.get(k, 0) + d
                self.committed = el
                self.save()

    def best_text(self):
        f = lambda d: f"{d['wpm']:.0f} WPM · {d['acc']:.0f}%" if isinstance(d, dict) else "—"
        secs = int(self.prog.get(self.name + "|secs", 0))
        return (f"Practice best  {f(self.prog.get(self.name))}\n"
                f"Test best  {f(self.prog.get(self.name + '|test'))}\n"
                f"Total practice  {secs // 3600}h {secs % 3600 // 60:02d}m")

    # -- session control
    @property
    def limit_min(self):
        return A.DUR[self.mode][self.dur_idx[self.mode]]

    def set_mode(self, m):
        self.mode = m
        self.select(self.cur)

    def cycle_dur(self):
        self.dur_idx[self.mode] = (self.dur_idx[self.mode] + 1) % len(A.DUR[self.mode])
        self.select(self.cur)

    def select(self, i):
        if self.name:
            self.commit()
        self.cur, self.name = i, self.names[i]
        self.gen = A.stream(i) if self.mode == "practice" else A.test_stream(i)
        self.limit = self.limit_min * 60
        self.ok = self.err = self.good = self.bad = self.line_no = 0
        self.accum, self.t0 = 0.0, None
        self.began = self.paused = self.done = False
        self.committed = 0.0
        self.out, self.out_kind = "", "ink"
        self.badge, self.badge_kind = "", "muted"
        self.summary = None
        self._autosave = 0
        self.target, self.keys, self.pos, self.typed, self.stage = "", "", 0, "", ""
        prob = A.level_problem(i)
        if prob:                       # wordlist file empty / missing -> clear message, no crash
            self.done = True
            self.summary = dict(title="Wordlist pawa jay ni", good=False, line1=prob,
                                line2="Wordlist Editor theke file ta fill korun", footer="")
            return
        self.show_item()

    def reload(self):
        A.reload()
        self.select(self.cur)

    def show_item(self):
        (bn, keys), self.stage = next(self.gen)
        self.line_no += 1
        self.target, self.keys, self.pos, self.typed = bn, keys, 0, ""

    def elapsed(self):
        return self.accum + (time.time() - self.t0 if self.t0 else 0)

    def toggle_pause(self):
        if self.done or not self.began:
            return
        if self.paused:
            self.paused = False
            self.t0 = time.time()
            self.badge, self.badge_kind = "", "muted"
        else:
            self.accum = self.elapsed()
            self.t0 = None
            self.paused = True
            self.commit()
            self.badge, self.badge_kind = "⏸ Paused - press F2 to resume", "warn"

    # -- typing
    def on_char(self, ch):
        """Returns 'ok' | 'bad' | 'line' | None (ignored)."""
        if self.done or self.paused or not ch or not ch.isprintable():
            return None
        if not self.began:
            self.began, self.t0 = True, time.time()
        return self._key_test(ch) if self.mode == "test" else self._key_practice(ch)

    def _key_practice(self, ch):
        if ch == self.keys[self.pos]:
            self.ok += 1
            self.pos += 1
            self.typed += ch
            self.out, self.out_kind = A.convert(self.typed), "ink"
            self.badge, self.badge_kind = "typing…", "muted"
            if self.pos == len(self.keys):
                got = A.convert(self.typed)
                good = got == self.target
                self.out, self.out_kind = got, "good" if good else "bad"
                self.show_item()
                self.badge = "✓ Perfect match" if good else "✗ mismatch"
                self.badge_kind = "good" if good else "bad"
                return "line"
            return "ok"
        self.err += 1
        return "bad"

    def _key_test(self, ch):
        if ch == self.keys[self.pos]:
            self.ok += 1
            res = "ok"
        else:
            self.err += 1
            res = "bad"
        self.typed += ch
        self.pos += 1
        self.out, self.out_kind = A.convert(self.typed), "ink"
        if self.pos == len(self.keys):
            got = A.convert(self.typed)
            good = got == self.target
            self.good += good
            self.bad += not good
            self.out, self.out_kind = got, "good" if good else "bad"
            self.show_item()
            self.badge = "previous line ✓" if good else "previous line ✗"
            self.badge_kind = "good" if good else "bad"
            return "line"
        return res

    def backspace(self):
        if self.done or self.paused:
            return False
        if self.mode == "test" and self.pos > 0:
            self.pos -= 1
            self.typed = self.typed[:-1]
            self.out, self.out_kind = A.convert(self.typed), "ink"
            return True
        return False

    # -- stats / clock
    def stats(self):
        el = self.elapsed()
        wpm = (self.ok / 5) / (el / 60) if el > 1 else 0
        tot = self.ok + self.err
        return el, wpm, 100 * self.ok / tot if tot else 100

    def tick(self):
        """Call ~5x per second.  Returns True on the tick the session finishes."""
        self._autosave += 1
        if self._autosave % 150 == 0:
            self.commit()
        el = self.elapsed()
        if self.began and not self.paused and not self.done and el >= self.limit:
            self.finish()
            return True
        return False

    def finish(self):
        self.done = True
        self.commit()
        el, wpm, acc = self.stats()
        test = self.mode == "test"
        passed = acc >= A.PASS_ACC
        k = self.name + ("|test" if test else "")
        old = self.prog.get(k)
        old = old["wpm"] if isinstance(old, dict) else -1
        if (passed or not test) and wpm > old:
            self.prog[k] = {"wpm": wpm, "acc": acc}
            self.save()
        title = ("পাস! 🎉" if passed else "আবার চেষ্টা করুন") if test else "শাবাশ! 🎉"
        ok_title = passed or not test
        l1 = f"{wpm:.0f} WPM  ·  {acc:.0f}% accuracy  ·  {self.err} errors"
        if test:
            l2 = (f"Lines correct: {self.good} / {self.good + self.bad}   ·   "
                  + ("PASSED" if passed else f"need ≥ {A.PASS_ACC}% accuracy to pass"))
        else:
            secs = int(self.prog.get(self.name + "|secs", 0))
            l2 = (f"{self.line_no - 1} lines practised   ·   total on this level: "
                  f"{secs // 3600}h {secs % 3600 // 60:02d}m")
        self.summary = dict(title=title, good=ok_title, line1=l1, line2=l2,
                            footer="Session finished - press Restart or choose another level")


# ==========================================================================
# BIJOY
# ==========================================================================
TRAIN_SECS = 3600     # training time per level (1 hour)
IDLE_SECS = 10        # no key for this long -> the training clock pauses
TEST_HINTS = False    # True = show key hints in test mode too


class BijoyEngine:
    """Training: 1 hour per level (clock runs only while you type).  Test: one random pass."""

    def __init__(self):
        self.L = B.layout(True)
        self.mode = "train"
        self.prog = load_json(self.L["save"], {})
        if not isinstance(self.prog.get("_train"), dict):
            self.prog["_train"] = {}
        now = time.monotonic()
        self.dirty, self.last_save, self.last_tick, self.last_key = False, now, now, 0.0
        self.cur = 0
        self.select(0)

    # -- helpers
    def pk(self):
        return self.name + self.L.get("tag", "")

    def trained(self, name=None):
        return self.prog["_train"].get(name or self.name, 0)

    def save(self):
        if save_json(self.L["save"], self.prog):
            self.dirty = False
            self.last_save = time.monotonic()

    def toggle_kar(self):
        self.L = self.L["toggle"]()
        self.select(self.cur)

    def set_mode(self, m):
        if m != self.mode:
            self.mode = m
            self.select(self.cur)

    def toggle_mode(self):
        self.set_mode("test" if self.mode == "train" else "train")

    def reset_hour(self):
        self.prog["_train"].pop(self.name, None)
        self.dirty = True
        self.select(self.cur)

    def next_level(self):
        if self.cur + 1 < len(self.L["lessons"]):
            self.select(self.cur + 1)

    @property
    def names(self):
        return list(self.L["lessons"])

    def best_text(self):
        b = self.prog.get(self.pk())
        best = f"Test best\n{b['wpm']:.0f} WPM · {b['acc']:.0f}%" if b else "Test best\n—"
        return f"{best}\nTrained {mmss(min(self.trained(), TRAIN_SECS))} / {mmss(TRAIN_SECS)}"

    def level_done(self, nm):
        return self.trained(nm) >= TRAIN_SECS

    # -- session
    def select(self, i):
        if self.dirty:
            self.save()
        LS = self.L["lessons"]
        self.cur, self.name = i, list(LS)[i]
        self.items = LS[self.name]
        self.target, self.keys, self.typed = "", "", ""
        self.pos = self.ok = self.err = self.miss = self.idx = 0
        self.start = self.end = None
        self.done = False
        self.active = 0.0
        self.rounds = 1
        self.order = list(range(len(self.items)))
        if self.mode == "test":
            random.shuffle(self.order)
        self.was_done = self.trained() >= TRAIN_SECS
        self.out, self.out_kind = "", "ink"
        self.badge, self.badge_kind = "", "muted"
        self.summary = None
        self.last_tick = time.monotonic()
        if not self.items:             # wordlist file empty / missing -> clear message, no crash
            self.order, self.done = [], True
            self.summary = dict(title="Wordlist pawa jay ni", good=False,
                                line1="wordlist/" + B.file_of(self.name) + " - khali ba file nai",
                                line2="Wordlist Editor theke file ta fill korun")
            return
        self.show_item()

    def reload(self):
        B.reload()
        self.L = B.layout(self.L["tag"] == "|old")
        self.select(self.cur)

    def hints(self):
        return self.mode == "train" or TEST_HINTS or self.miss >= 3

    def show_item(self):
        bn, keys = self.items[self.order[self.idx]]
        self.target, self.keys, self.pos, self.typed, self.miss = bn, keys, 0, "", 0

    def progress_frac(self):
        if self.mode == "train":
            return min(self.trained(), TRAIN_SECS) / TRAIN_SECS
        return self.idx / len(self.order) if self.order else 0

    def on_char(self, ch):
        """Returns 'ok' | 'bad' | 'line' | 'next' | None."""
        if self.done:
            return None
        if not ch or not ch.isprintable():
            return None
        now = time.monotonic()
        self.last_key = now
        if self.start is None:
            self.start = now
        if ch == self.keys[self.pos]:
            self.ok += 1
            self.pos += 1
            self.typed += ch
            self.miss = 0
            self.out, self.out_kind = self.L["convert"](self.typed), "ink"
            self.badge, self.badge_kind = "typing…", "muted"
            if self.pos == len(self.keys):
                self._complete()
                return "line"
            return "ok"
        self.err += 1
        self.miss += 1
        return "bad"

    def _complete(self):
        got = self.L["convert"](self.typed)
        prev = self.target
        good = B.nfd(got) == B.nfd(prev)
        if not good:
            self.err += 1
        self.out, self.out_kind = got, "good" if good else "bad"
        self.badge = "✓ Perfect match" if good else f"✗ expected {prev}"
        self.badge_kind = "good" if good else "bad"
        self.idx += 1
        if self.idx >= len(self.order):
            if self.mode == "test":
                return self._finish_test()
            n, last_i = len(self.order), self.order[-1]
            self.rounds += 1
            self.idx = 0
            self.order = random.sample(range(n), n)
            if n > 1 and self.order[0] == last_i:
                self.order.append(self.order.pop(0))
        self.show_item()

    def stats(self):
        now = time.monotonic()
        if self.mode == "train":
            el = self.active
        else:
            el = (self.end or now) - self.start if self.start is not None else 0
        wpm = (self.ok / 5) / (el / 60) if el > 1 else 0
        tot = self.ok + self.err
        return el, wpm, 100 * self.ok / tot if tot else 100

    def time_text(self):
        if self.mode == "train":
            left = TRAIN_SECS - self.trained()
            return mmss(left) if left > 0 else "✓ Done"
        return mmss(self.stats()[0])

    def tick(self):
        now = time.monotonic()
        dt = min(now - self.last_tick, 1.0)
        self.last_tick = now
        if (self.mode == "train" and self.start is not None and not self.done
                and now - self.last_key <= IDLE_SECS):
            self.active += dt
            tr = self.prog["_train"]
            tr[self.name] = tr.get(self.name, 0) + dt
            self.dirty = True
            if tr[self.name] >= TRAIN_SECS and not self.was_done:
                self._finish_training()
        if self.dirty and now - self.last_save > 15:
            self.save()

    def _finish_training(self):
        self.done = self.was_done = True
        el, wpm, acc = self.stats()
        self.save()
        self.summary = dict(
            title="শাবাশ! 🎉", good=True,
            line1=f"1 hour done  ·  this session: {wpm:.0f} WPM  ·  {acc:.0f}% accuracy",
            line2="Enter = next level   ·   Restart = keep practising   ·   F3 = take the Test")

    def _finish_test(self):
        self.done = True
        self.end = time.monotonic()
        el, wpm, acc = self.stats()
        old = self.prog.get(self.pk())
        new_best = not old or wpm > old["wpm"]
        if new_best:
            self.prog[self.pk()] = {"wpm": wpm, "acc": acc}
            self.save()
        self.summary = dict(
            title="শাবাশ! 🎉", good=True,
            line1=f"{wpm:.0f} WPM  ·  {acc:.0f}% accuracy  ·  {self.err} errors"
                  + ("  ·  New best!" if new_best else ""),
            line2="Enter = next level   ·   Restart = try again")


# ==========================================================================
# ENGLISH (Typing-Master style)
# ==========================================================================
MINUTE_SCALE = 1.0   # 0.1 = quick testing


class EnglishEngine:
    def __init__(self):
        self.progress = load_json(ENGLISH_SAVE, {})
        self.state = "ready"
        self.flash = False
        self.lesson = None

    def start(self, lesson):
        self.lesson, self.si, self.results = lesson, 0, []
        self.load_stage()

    def load_stage(self):
        st = self.stage = self.lesson["stages"][self.si]
        st["_seq"], st["_n"] = E.build_seq(st), 0
        self.total_sec = st["mins"] * 60 * MINUTE_SCALE
        self.lines, self.ci = [], 0
        self.correct = self.total = self.errors = 0
        self.active, self.state, self.flash = 0.0, "ready", False
        self.t_start = 0.0
        self.fill_lines()

    def fill_lines(self):
        want = 4 if self.stage["small"] else 3
        while len(self.lines) < want:
            self.lines += E.GEN[self.stage["kind"]](self.stage)

    def head_text(self):
        n = len(self.lesson["stages"])
        return (f"Lesson {self.lesson['id']}  {self.lesson['title']}    |    "
                f"Stage {self.si + 1}/{n}:  {self.stage['name']}")

    def is_last(self):
        return self.si == len(self.lesson["stages"]) - 1

    def next(self):
        """Returns True when the whole lesson is finished."""
        self.si += 1
        if self.si >= len(self.lesson["stages"]):
            self.finish_lesson()
            return True
        self.load_stage()
        return False

    def repeat(self):
        if self.state == "done" and self.results:
            self.results.pop()
        self.load_stage()

    def finish_lesson(self):
        if self.results:
            wpm = sum(r[0] for r in self.results) / len(self.results)
            acc = sum(r[1] for r in self.results) / len(self.results)
            old = self.progress.get(self.lesson["id"], {})
            self.progress[self.lesson["id"]] = {"wpm": max(old.get("wpm", 0), round(wpm)),
                                                "acc": round(acc)}
            save_json(ENGLISH_SAVE, self.progress)

    def cur_char(self):
        return self.lines[0][self.ci] if self.lines else None

    def on_char(self, ch):
        """Returns 'ok' | 'bad' | None."""
        if self.state not in ("ready", "run") or not ch or ord(ch) < 32:
            return None
        if self.state == "ready":
            self.state, self.t_start = "run", time.time()
        self.total += 1
        if ch == self.cur_char():
            self.correct += 1
            self.ci += 1
            if self.ci >= len(self.lines[0]):
                self.lines.pop(0)
                self.ci = 0
                self.fill_lines()
            return "ok"
        self.errors += 1
        self.flash = True
        return "bad"

    def elapsed(self):
        return self.active + (time.time() - self.t_start if self.state == "run" else 0)

    def stats(self):
        if not self.total:
            return 0, 100
        wpm = (self.correct / 5) / (max(self.elapsed(), 5) / 60)
        return wpm, 100 * self.correct / self.total

    def time_left(self):
        return max(0, math.ceil(self.total_sec - self.elapsed()))

    def pause_toggle(self):
        if self.state == "run":
            self.active += time.time() - self.t_start
            self.state = "paused"
        elif self.state == "paused":
            self.state, self.t_start = "run", time.time()

    def tick(self):
        """Returns True on the tick the stage ends."""
        if self.state == "run" and self.elapsed() >= self.total_sec:
            self.end_stage()
            return True
        return False

    def end_stage(self):
        if self.state == "done":
            return
        self.active = self.total_sec
        self.state = "done"
        self.results.append(self.stats())
        wpm, acc = self.stats()
        self.verdict = ("Excellent accuracy!" if acc >= 95 else "Good job - keep it up." if acc >= 90
                        else "Accuracy is below 90%.  Press Repeat and go a little slower.")

    def hint_text(self):
        ch = self.cur_char()
        if ch is None or self.state == "done":
            return ""
        k = E.base_key(ch)
        f = E.KEY_FINGER.get(k)
        if not f:
            return ""
        text = "Space bar  -  thumb" if f == "Thumb" else f"{f} finger"
        if E.needs_shift(ch):
            right = f.startswith("Left")
            text += f"   +   hold {'Right' if right else 'Left'} Shift"
        if self.state == "ready":
            text = "Put your fingers on the home row and start typing.     " + text
        return text

    def target_keys(self):
        """-> (key_names_to_mark, fingers_to_mark)"""
        ch = self.cur_char()
        if ch is None or self.state == "done":
            return [], []
        k = E.base_key(ch)
        f = E.KEY_FINGER.get(k)
        if not f:
            return [], []
        keys, fingers = [k], [f]
        if E.needs_shift(ch):
            right = f.startswith("Left")
            keys.append("RSHIFT" if right else "LSHIFT")
            fingers.append("Right pinky" if right else "Left pinky")
        return keys, fingers
