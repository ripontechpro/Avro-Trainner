"""
Typing Tutor - 5 levels, Typing-Master style (Python + tkinter, nothing to install)
Run:  python typing_tutor.py

Level 1  Home row   a s d f g h j k l ;     (1 hour)
Level 2  Top row    q w e r t y u i o p
Level 3  Bottom row z x c v b n m , .
Level 4  Symbols & numbers  ? / ' " ! @ # $ % ( ) ...
Level 5  Full keyboard test with sentences
Lesson "1" = letters drill, lesson "1.1" = words (same for 2/2.1, 3/3.1, 4/4.1).
Every letter/symbol stage starts with the keys IN ORDER (asdf jkl; / qwerty uiop ...),
then continues with random mixed drills.

Keys:  F11 = full screen on/off,  Esc = back to menu,  top-right button = Close
"""
import json
import math
import random
import time
import tkinter as tk
from pathlib import Path

MINUTE_SCALE = 1.0   # 1.0 = real minutes.  Set to 0.1 to test quickly.
SAVE_FILE = Path.home() / ".typing_tutor_progress.json"
FONT = "Segoe UI"
BG, PURPLE, GL, GR = "#a9b4ff", "#6a5acd", "#eaffd3", "#d1f58c"
PSC = MSC = 1.0     # practice-screen / menu-screen scale (set from screen size)


def F(n):   # practice font size
    return max(7, round(n * PSC))


def P(n):   # practice pixel size
    return int(n * PSC)


def W(n):   # line width
    return max(1, round(n * PSC))


def FM(n):  # menu font size
    return max(8, round(n * MSC))


def M(n):   # menu pixel size
    return int(n * MSC)


# ------------------------------------------------------------------ keyboard
ROWS = [list("`1234567890-="), list("qwertyuiop[]\\"), list("asdfghjkl;'"), list("zxcvbnm,./")]
ROW_X = [0, 62, 74, 98]
KU, KH, KX, KY = 44, 40, 33, 172

FINGERS = {
    "Left pinky": "`1qaz", "Left ring": "2wsx", "Left middle": "3edc", "Left index": "45rtfgvb",
    "Right index": "67yuhjnm", "Right middle": "8ik,", "Right ring": "9ol.",
    "Right pinky": "0-=p[]\\;'/", "Thumb": " ",
}
COLORS = {
    "Left pinky": "#c9d1ff", "Left ring": "#ffd2d2", "Left middle": "#d6f5ba", "Left index": "#e6ccff",
    "Right index": "#e6ccff", "Right middle": "#d6f5ba", "Right ring": "#ffd2d2",
    "Right pinky": "#c9d1ff", "Thumb": "#dcdccb",
}
MOD = "#dfe3ff"
KEY_FINGER = {k: f for f, keys in FINGERS.items() for k in keys}
SHIFTED = dict(zip('~!@#$%^&*()_+{}|:"<>?', "`1234567890-=[]\\;',./"))
SHIFT_UP = {v: k for k, v in SHIFTED.items()}


def base_key(ch):
    return ch.lower() if ch.isalpha() else SHIFTED.get(ch, ch)


def needs_shift(ch):
    return ch.isupper() or ch in SHIFTED


def cap(c):
    return c.upper() if c.isalpha() else SHIFT_UP.get(c, c)


def up(s):
    return "".join(cap(c) for c in s)


# ------------------------------------------------------------------ texts
WORDS = """a ask asks add adds all alas dad dads fad fads fall falls flag flags flask flash gag gas gal gall had
hag hall halls half hash jag lad lads lag lags lash sad sag sash shall slag slash salad saga dash gash glad flak
flaks skald alfalfa shad gals sags the be to of and in that have it for not on with he as you do at this but his
by from they we say her she or an will my one all would there their what so up out if about who get which go me
when make can like time no just him know take people into year your good some could them see other than then now
look only come its over think also back after use two how our work first well way even new want because any these
give day most us quiet power write type ruler paper pretty ready hello world upper please tree trade tired right
three whole those flower follow powder quality outside tooth sleep wheel true rest tell shut show high took lead
load glass girl hold full zero zone size quick exam name women brown black music voice number never between many
much next move box mix vase zebra maze quiz jazz fox excuse complex cabin combine camera basket bottle mountain
machine monkey chance clean candle bridge button cream danger evening family garden happy island jungle kitchen
letter market notice orange police question river simple table under valley window yellow""".split()

PUNCT_TOKENS = ["don't", "can't", "it's", "(yes)", "[ok]", "{x}", "who?", "why?", "wow!", "hi!", '"quote"',
                "'single'", "a/b", "x+y", "a=b", "#tag", "@home", "50%", "$25", "&more", "a-b", "one_two",
                "C:\\dir", "~/home", "10*5", "5<7", "7>5", "a|b", "^up", "`tick`", "yes;", "no:", "Mr.", "e.g.,"]
NUM_TOKENS = ["2024", "7:30", "$19.99", "50%", "3.14", "100/200", "(555)", "12-34", "#7", "@45", "1,000",
              "8*9=72", "4+5=9", "100%", "25th", "$5", "99.9", "12:45", "3x4", "1/2", "40-60", "5>3", "(2+3)*4"]
SHORT = ["The quick brown fox jumps over the lazy dog.", "Practice makes perfect.",
         "Keep your fingers on the home row.", "Typing is a useful skill.", "Slow and steady wins the race.",
         "Look at the screen, not at the keys.", "Accuracy comes before speed.",
         "Every expert was once a beginner.", "Sit straight and relax your hands.",
         "A smooth rhythm beats a fast burst."]
LONG = ["Learning to type without looking at the keyboard saves a lot of time every single day.",
        "Good typists keep their wrists relaxed and let each finger return to the home row.",
        "Short daily practice sessions work better than one very long session each week.",
        "Computers have changed the way we write, learn, work and talk to one another.",
        "Speed will come by itself once your fingers know where every key is hiding.",
        "Take a short break every half hour so your hands and eyes can rest."]
MIXED = ["Hello, my name is Sam; I am 25 years old.", "Can you send me the file by 5:30 p.m.?",
         "\"Well done!\" she said. \"Keep going.\"", "The total cost is $49.99 (tax included).",
         "Visit www.example.com or email sam@mail.com today.", "Wow! That was 100% better than yesterday's try.",
         "Step 1: open the file; step 2: save it.", "It's 9 o'clock - time for a break, isn't it?",
         "Pack: 3 shirts, 2 pairs of jeans & 1 jacket.", "Is it true that 7 + 8 = 15? Yes, it is!"]
ALL_SYMBOLS = ",.;:'\"/?!-_()[]{}+=*<>@#$%^&\\|~`0123456789"


def words_for(letters, must=""):
    s, m = set(letters), set(must)
    return [w for w in WORDS if set(w) <= s and (not m or set(w) & m)]


def words_with(letters):
    return [w for w in WORDS if set(w) & set(letters)]


# ------------------------------------------------------------------ lesson data
def S(name, chars="", focus="", case="lower", mins=4, kind="drill", pool=None, punct=False, small=False,
      groups=None):
    return dict(locals())


def SYM(name, chars, groups, mins=4):
    return S(name, chars, case="none", mins=mins, groups=groups)


TOP, HOME, BOT = "qwertyuiop", "asdfghjkl;", "zxcvbnm,."
ALPHA = "abcdefghijklmnopqrstuvwxyz"
HW = words_for("asdfghjkl")
TW = words_for(TOP + "asdfghjkl", TOP)
BW = words_with("zxcvbnm")
G_HOME = ["asdf", "gh", "jkl;"]      # ordered groups used for the "in order" part of each stage
G_TOP = ["qwerty", "uiop"]
G_BOT = ["zxcvb", "nm,."]


def word_stages(pool, mins, punct=False):
    return [S("Words - small letters", kind="words", pool=pool, mins=mins[0], punct=punct),
            S("Words - Capital letters", kind="words", pool=pool, case="cap", mins=mins[1], punct=punct),
            S("Words - mixed", kind="words", pool=pool, case="mixed", mins=mins[2], punct=punct)]


LEVELS = [
    dict(name="Level 1", title="Home Row", keys="a s d f g h j k l ;", color="#6c7bff", lessons=[
        dict(id="1", title="Letters", stages=[
            S("Left hand:  a s d f", "asdf", groups=["asdf"], mins=4),
            S("Right hand:  j k l ;", "jkl;", groups=["jkl;"], mins=4),
            S("Both hands:  asdf jkl;", "asdfjkl;", groups=["asdf", "jkl;"], mins=5),
            S("New keys:  g  h", HOME, focus="gh", groups=G_HOME, mins=5),
            S("Full home row", HOME, groups=["asdfg", "hjkl;"], mins=5),
            S("Capital letters (hold Shift)", HOME, case="upper", groups=G_HOME, mins=6),
            S("Capital + small mixed", HOME, case="mixed", groups=["asdfg", "hjkl;"], mins=6),
            S("Home row speed round", HOME, case="mixed", groups=G_HOME, mins=5)]),
        dict(id="1.1", title="Words", stages=word_stages(HW, (7, 6, 7)))]),
    dict(name="Level 2", title="Top Row", keys="q w e r t y u i o p", color="#2fb98f", lessons=[
        dict(id="2", title="Letters", stages=[
            S("Top row:  q w e r t", "qwert", groups=["qwert"], mins=4),
            S("Top row:  y u i o p", "yuiop", groups=["yuiop"], mins=4),
            S("Full top row:  qwerty uiop", TOP, groups=G_TOP, mins=4),
            S("Top row + home row", TOP + HOME, focus=TOP, groups=[G_TOP, G_HOME], mins=4),
            S("Capital letters - top row", TOP, case="upper", groups=G_TOP, mins=4),
            S("Mixed: top + home row", TOP + HOME, focus=TOP, case="mixed", groups=[G_TOP, G_HOME], mins=4)]),
        dict(id="2.1", title="Words", stages=word_stages(TW, (5, 5, 6)))]),
    dict(name="Level 3", title="Bottom Row", keys="z x c v b n m , .", color="#f29b2d", lessons=[
        dict(id="3", title="Letters", stages=[
            S("Bottom row:  z x c v b", "zxcvb", groups=["zxcvb"], mins=4),
            S("Bottom row:  n m , .", "nm,.", groups=["nm,."], mins=4),
            S("Full bottom row", BOT, groups=G_BOT, mins=4),
            S("Bottom row + home row", BOT + HOME, focus=BOT, groups=[G_BOT, G_HOME], mins=4),
            S("Capital letters - bottom row", BOT, case="upper", groups=G_BOT, mins=4),
            S("Mixed: all three rows", ALPHA + ",.;", focus=BOT, case="mixed",
              groups=[G_TOP, G_HOME, G_BOT], mins=4)]),
        dict(id="3.1", title="Words", stages=word_stages(BW, (5, 5, 6), punct=True))]),
    dict(name="Level 4", title="Symbols & Numbers", keys="? / ' \" ! @ # $ % ( ) 0-9", color="#ef5d7a", lessons=[
        dict(id="4", title="Symbols", stages=[
            SYM("Punctuation:  , . ; ' \"", ",.;'\"", [",.;", "'\""]),
            SYM("Question & slash:  / ? ! - _", "/?!-_", ["/?!", "-_"]),
            SYM("Numbers:  1 2 3 4 5", "12345", ["12345"]),
            SYM("Numbers:  6 7 8 9 0", "67890", ["67890"]),
            SYM("Brackets:  ( ) [ ] { }", "()[]{}", ["()", "[]", "{}"]),
            SYM("Math:  + = * < > / -", "+=*<>/-", ["+=*", "<>/-"]),
            SYM("Special:  @ # $ % ^ & \\ | ~ `", "@#$%^&\\|~`", ["@#$", "%^&", "\\|~`"]),
            SYM("All symbols mixed", ALL_SYMBOLS, [",.;'\"", "/?!-_"], 5)]),
        dict(id="4.1", title="Words & Numbers", stages=[
            S("Words with punctuation", kind="words", pool=PUNCT_TOKENS, case="none", mins=6),
            S("Numbers & symbols in text", kind="words", pool=NUM_TOKENS, case="none", mins=6)])]),
    dict(name="Level 5", title="Full Keyboard Test", keys="Sentences & paragraphs", color="#8a63d2", lessons=[
        dict(id="5", title="Sentences", stages=[
            S("Short sentences", kind="sent", pool=SHORT, small=True, mins=5),
            S("Long sentences", kind="sent", pool=LONG, small=True, mins=5),
            S("Numbers & punctuation", kind="sent", pool=MIXED, small=True, mins=5),
            S("Final test - everything", kind="sent", pool=SHORT + LONG + MIXED, small=True, mins=5)]),
        dict(id="5.1", title="Paragraph Test", stages=[
            S("Paragraph test", kind="para", pool=SHORT + LONG + MIXED, small=True, mins=8)])]),
]


# ------------------------------------------------------------------ text generators
def tw(small):
    return (21, 21) if small else (38, 74)      # letter advance, space advance


def line_limit(small):
    return 650 if small else 620


def build_seq(st):
    """Ordered lines like 'asdf asdf ', 'asdf jkl; ', 'fdsa ;lkj' shown before the random mix."""
    g = st.get("groups")
    if not g:
        return []
    out = []
    for gs in (g if isinstance(g[0], list) else [g]):
        out += [f"{x} {x} " for x in gs]
        if len(gs) > 1:
            out += [" ".join(gs) + " "] * 2
            out.append(" ".join(x[::-1] for x in reversed(gs)) + " ")
        else:
            out += [f"{gs[0]} {gs[0]} ", f"{gs[0][::-1]} {gs[0][::-1]} "]
    return [up(l) for l in out] if st["case"] == "upper" else out


def case_group(g, case):
    if case == "upper":
        return up(g)
    if case == "mixed":
        r = random.random()
        return g if r < .34 else up(g) if r < .67 else up(g[0]) + g[1:]
    return g


def case_word(w, case):
    if case == "cap":
        return w.capitalize()
    if case == "upper":
        return up(w)
    if case == "mixed":
        r = random.random()
        return w if r < .4 else w.capitalize() if r < .9 else up(w)
    return w


def gen_drill(st):
    seq = st.get("_seq")
    if seq and st.get("_n", 0) < len(seq):          # first: keys in order
        st["_n"] += 1
        return [seq[st["_n"] - 1]]
    chars, focus = st["chars"], st["focus"]         # then: random mix ("ulot palot")

    def mk(n):
        g = "".join(random.choice(focus if focus and random.random() < .6 else chars) for _ in range(n))
        return case_group(g, st["case"])

    n = random.choice([2, 3, 4, 4])
    g = mk(n)
    if n == 2 and random.random() < .5:
        g2 = mk(2)
        return [f"{g} {g} {g2} {g2} "]
    return [(g + " ") * (3 if n == 2 else 2)]


def gen_words(st):
    cw, sw = tw(st["small"])
    lim, out, width = line_limit(st["small"]), [], 0
    while True:
        w = case_word(random.choice(st["pool"]), st["case"])
        if st["punct"] and random.random() < .25:
            w += random.choice(",.")
        need = len(w) * cw + sw
        if out and width + need > lim:
            break
        out.append(w)
        width += need
    return [" ".join(out) + " "]


def wrap(text, small):
    cw, sw = tw(small)
    lim, lines, cur, width = line_limit(small), [], [], 0
    for w in text.split():
        need = len(w) * cw + sw
        if cur and width + need > lim:
            lines.append(" ".join(cur) + " ")
            cur, width = [], 0
        cur.append(w)
        width += need
    if cur:
        lines.append(" ".join(cur) + " ")
    return lines


def gen_sent(st):
    if st["kind"] == "para":
        return wrap(" ".join(random.sample(st["pool"], 3)), st["small"])
    return wrap(random.choice(st["pool"]), st["small"])


GEN = {"drill": gen_drill, "words": gen_words, "sent": gen_sent, "para": gen_sent}


# ------------------------------------------------------------------ app
class App:
    def __init__(self, root):
        global PSC, MSC
        self.root = root
        root.title("Typing Tutor")
        root.configure(bg=BG)
        root.attributes("-fullscreen", True)
        root.update_idletasks()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        PSC = max(.8, min(2.4, (sw - 60) / 942, (sh - 90) / 552))
        MSC = max(.9, min(2.2, sw / 1040, sh / 720))
        try:
            self.progress = json.loads(SAVE_FILE.read_text())
        except Exception:
            self.progress = {}
        self.full = True
        self.menu = tk.Frame(root, bg=BG)
        self.practice = tk.Frame(root, bg=BG)
        self.mode, self.state, self.tick_job = "menu", "ready", None
        self.build_practice()
        self.close_btn = tk.Button(root, text="✕  Close", command=root.destroy, bg="#ff5d5d", fg="white",
                                   activebackground="#d93a3a", activeforeground="white", relief="flat",
                                   font=(FONT, FM(11), "bold"), cursor="hand2", padx=M(12), pady=M(4))
        self.close_btn.place(relx=1.0, x=-M(14), y=M(12), anchor="ne")
        root.bind("<Key>", self.on_key)
        root.bind("<F11>", self.toggle_full)
        root.bind("<Escape>", lambda e: self.show_menu() if self.mode == "practice" else None)
        self.show_menu()

    def toggle_full(self, _e=None):
        self.full = not self.full
        self.root.attributes("-fullscreen", self.full)
        if not self.full:
            try:
                self.root.state("zoomed")
            except tk.TclError:
                pass

    # ---------------------------------------------------------- menu
    def show_menu(self):
        self.mode = "menu"
        self.cancel_tick()
        self.practice.pack_forget()
        for w in self.menu.winfo_children():
            w.destroy()
        tk.Label(self.menu, text="Typing Tutor", font=(FONT, FM(32), "bold"), bg=BG, fg="white").pack(
            pady=(M(40), M(2)))
        tk.Label(self.menu, text="Learn touch typing step by step - from the home row to full sentences",
                 font=(FONT, FM(12)), bg=BG, fg="#2b2f6e").pack()
        row = tk.Frame(self.menu, bg=BG)
        row.pack(pady=M(28))
        for lv in LEVELS:
            card = tk.Frame(row, bg="white", highlightbackground=lv["color"], highlightthickness=3)
            card.pack(side="left", padx=M(7), anchor="n")
            tk.Label(card, text=lv["name"], bg=lv["color"], fg="white", font=(FONT, FM(15), "bold"),
                     width=15, pady=M(6)).pack(fill="x")
            tk.Label(card, text=lv["title"], bg="white", fg="#222", font=(FONT, FM(11), "bold"),
                     pady=M(6)).pack()
            tk.Label(card, text=lv["keys"], bg="white", fg="#666", font=(FONT, FM(10)),
                     wraplength=M(150), pady=M(4)).pack()
            for ls in lv["lessons"]:
                mins = sum(s["mins"] for s in ls["stages"])
                txt = f"{ls['id']}   {ls['title']}\n{mins} min"
                best = self.progress.get(ls["id"])
                if best:
                    txt += f"   ✓ {best['wpm']} wpm"
                tk.Button(card, text=txt, command=lambda l=ls: self.start(l), bg="#eef0ff",
                          activebackground="#d6dbff", relief="flat", font=(FONT, FM(10), "bold"),
                          justify="left", anchor="w", padx=M(8), pady=M(4),
                          cursor="hand2").pack(fill="x", padx=M(10), pady=M(5))
            tk.Frame(card, bg="white", height=M(10)).pack()
        tk.Label(self.menu, font=(FONT, FM(11)), bg=BG, fg="#2b2f6e", justify="center",
                 text="Every stage is a timed drill. Type the highlighted key - a wrong key will not move forward.\n"
                      "Aim for 90% accuracy first, speed comes later.      "
                      "F11 = full screen on/off      Esc = back to menu").pack(pady=M(6))
        self.menu.pack(fill="both", expand=True)
        self.close_btn.lift()

    # ---------------------------------------------------------- practice screen
    def build_practice(self):
        outer = tk.Frame(self.practice, bg=PURPLE, padx=P(6), pady=P(6))
        outer.pack(expand=True)
        self.canvas = c = tk.Canvas(outer, width=P(700), height=P(540), bg=GL, highlightthickness=0)
        c.pack(side="left")
        right = tk.Frame(outer, bg=GR, width=P(230), height=P(540))
        right.pack(side="left", fill="y")
        right.pack_propagate(False)
        px = P(16)

        tk.Label(right, text="Your Progress", bg=GR, font=(FONT, F(12), "bold")).pack(
            anchor="w", padx=px, pady=(P(18), P(4)))
        self.bars = tk.Canvas(right, width=P(196), height=P(122), bg=GR, highlightthickness=0)
        self.bars.pack()
        tm = tk.Frame(right, bg=GR)
        tm.pack(fill="x", padx=px, pady=(P(14), 0))
        tk.Label(tm, text="Time", bg=GR, font=(FONT, F(11), "bold")).pack(side="left")
        tk.Button(tm, text="Pause", command=self.pause, bg=GR, fg="#1a3fd0", bd=0, relief="flat",
                  activebackground=GR, font=(FONT, F(10), "underline"), cursor="hand2").pack(side="right")
        self.time_lbl = tk.Label(right, text="00:00", bg=GR, font=("Consolas", F(24), "bold"))
        self.time_lbl.pack(anchor="w", padx=px)
        self.wpm_lbl = tk.Label(right, text="Speed:  0 WPM", bg=GR, font=(FONT, F(12)))
        self.wpm_lbl.pack(anchor="w", padx=px, pady=(P(14), 0))
        self.acc_lbl = tk.Label(right, text="Accuracy:  100%", bg=GR, font=(FONT, F(12)))
        self.acc_lbl.pack(anchor="w", padx=px)
        self.err_lbl = tk.Label(right, text="Errors:  0", bg=GR, font=(FONT, F(12)))
        self.err_lbl.pack(anchor="w", padx=px)

        def btn(text, cmd):
            b = tk.Button(right, text=text, command=cmd, bg="white", activebackground="#e6e9ff",
                          relief="solid", bd=1, font=(FONT, F(11)), cursor="hand2", pady=P(4))
            b.pack(side="bottom", fill="x", padx=px, pady=P(4))
            return b
        btn("Cancel", self.show_menu)
        btn("Repeat", self.repeat)
        self.next_btn = btn("Next", self.next)

        # static drawing in logical 700x540 coordinates (scaled once at the end)
        self.head = c.create_text(34, 20, anchor="w", text="", font=(FONT, F(12), "bold"), fill="#3b3f99")
        self.hint = c.create_text(350, 404, text="", font=(FONT, F(11), "bold"), fill="#7a5c00")
        self.rects, self.pos = {}, {}

        def key(name, x, y, w, label, color, fs=11):
            x, y = x + KX, y + KY
            r = c.create_rectangle(x, y, x + w, y + KH, fill=color, outline="#9aa0c8", width=W(2))
            c.create_text(x + w / 2, y + KH / 2, text=label, font=(FONT, F(fs), "bold"), fill="#5a5f8a")
            self.rects[name] = (r, color)
            self.pos[name] = (x + w / 2, y)

        for r, row in enumerate(ROWS):
            for i, k in enumerate(row):
                label = k.upper() if k.isalpha() else f"{SHIFT_UP[k]}\n{k}"
                key(k, ROW_X[r] + i * KU, r * KU, KH, label, COLORS[KEY_FINGER[k]], 11 if k.isalpha() else 9)
        key("<Back>", 572, 0, 62, "Back", MOD, 9)
        key("<Tab>", 0, KU, 58, "Tab", MOD, 9)
        key("<Caps>", 0, 2 * KU, 70, "Caps", MOD, 9)
        key("<Enter>", 558, 2 * KU, 76, "Enter", MOD, 9)
        key("LSHIFT", 0, 3 * KU, 94, "Shift", MOD, 10)
        key("RSHIFT", 538, 3 * KU, 96, "Shift", MOD, 10)
        key(" ", 170, 4 * KU, 300, "Space", COLORS["Thumb"], 10)

        self.skin = "#f3c9a6"
        edge, fx = "#d9a37c", (lambda k: self.pos[k][0])
        c.create_oval(fx("a") - 26, 490, fx("f") + 60, 640, fill=self.skin, outline=edge)
        c.create_oval(fx("j") - 60, 490, fx(";") + 26, 640, fill=self.skin, outline=edge)
        self.fitems = {}
        hands = [("Left pinky", "a", 455), ("Left ring", "s", 432), ("Left middle", "d", 422),
                 ("Left index", "f", 432), ("Right index", "j", 432), ("Right middle", "k", 422),
                 ("Right ring", "l", 432), ("Right pinky", ";", 455)]
        for name, k, top in hands:
            x = fx(k)
            self.fitems.setdefault(name, []).append(
                c.create_oval(x - 17, top, x + 17, top + 95, fill=self.skin, outline=edge, width=W(2)))
        for x in (fx("f") + 52, fx("j") - 52):
            self.fitems.setdefault("Thumb", []).append(
                c.create_oval(x - 15, 468, x + 15, 540, fill=self.skin, outline=edge, width=W(2)))
        c.scale("all", 0, 0, PSC, PSC)

    # ---------------------------------------------------------- flow
    def start(self, lesson):
        self.lesson, self.si, self.results = lesson, 0, []
        self.menu.pack_forget()
        self.practice.pack(fill="both", expand=True)
        self.mode = "practice"
        self.close_btn.lift()
        self.load_stage()

    def load_stage(self):
        self.cancel_tick()
        st = self.stage = self.lesson["stages"][self.si]
        st["_seq"], st["_n"] = build_seq(st), 0
        self.total_sec = st["mins"] * 60 * MINUTE_SCALE
        self.lines, self.ci = [], 0
        self.correct = self.total = self.errors = 0
        self.active, self.state, self.flash = 0, "ready", False
        self.canvas.delete("overlay")
        self.fill_lines()
        n = len(self.lesson["stages"])
        self.canvas.itemconfig(
            self.head, text=f"Lesson {self.lesson['id']}  {self.lesson['title']}    |    "
                            f"Stage {self.si + 1}/{n}:  {st['name']}")
        self.next_btn.config(text="Next")
        self.render()
        self.highlight()
        self.update_labels()

    def fill_lines(self):
        want = 4 if self.stage["small"] else 3
        while len(self.lines) < want:
            self.lines += GEN[self.stage["kind"]](self.stage)

    def next(self):
        if self.mode != "practice":
            return
        self.si += 1
        if self.si >= len(self.lesson["stages"]):
            self.finish_lesson()
        else:
            self.load_stage()

    def repeat(self):
        if self.mode == "practice":
            if self.state == "done" and self.results:
                self.results.pop()
            self.load_stage()

    def finish_lesson(self):
        if self.results:
            wpm = sum(r[0] for r in self.results) / len(self.results)
            acc = sum(r[1] for r in self.results) / len(self.results)
            old = self.progress.get(self.lesson["id"], {})
            self.progress[self.lesson["id"]] = {"wpm": max(old.get("wpm", 0), round(wpm)), "acc": round(acc)}
            try:
                SAVE_FILE.write_text(json.dumps(self.progress, indent=2))
            except Exception:
                pass
        self.show_menu()

    # ---------------------------------------------------------- typing
    def cur_char(self):
        return self.lines[0][self.ci] if self.lines else None

    def on_key(self, e):
        if self.mode != "practice" or self.state not in ("ready", "run"):
            return
        ch = e.char
        if not ch or ord(ch) < 32:
            return
        if self.state == "ready":
            self.state, self.t_start = "run", time.time()
            self.tick()
        self.total += 1
        if ch == self.cur_char():
            self.correct += 1
            self.ci += 1
            if self.ci >= len(self.lines[0]):
                self.lines.pop(0)
                self.ci = 0
                self.fill_lines()
        else:
            self.errors += 1
            self.flash = True
            self.root.after(180, self.unflash)
        self.render()
        self.highlight()
        self.update_labels()

    def unflash(self):
        self.flash = False
        if self.mode == "practice" and self.state != "done":
            self.render()

    def elapsed(self):
        return self.active + (time.time() - self.t_start if self.state == "run" else 0)

    def stats(self):
        if not self.total:
            return 0, 100
        wpm = (self.correct / 5) / (max(self.elapsed(), 5) / 60)
        return wpm, 100 * self.correct / self.total

    def cancel_tick(self):
        if self.tick_job:
            self.root.after_cancel(self.tick_job)
            self.tick_job = None

    def tick(self):
        if self.state != "run":
            return
        self.update_labels()
        if self.elapsed() >= self.total_sec:
            self.end_stage()
            return
        self.tick_job = self.root.after(200, self.tick)

    def pause(self):
        c = self.canvas
        if self.mode != "practice":
            return
        if self.state == "run":
            self.cancel_tick()
            self.active += time.time() - self.t_start
            self.state = "paused"
            c.create_rectangle(120, 170, 580, 290, fill="white", outline=PURPLE, width=W(4), tags="overlay")
            c.create_text(350, 230, text="Paused", font=(FONT, F(28), "bold"), fill=PURPLE, tags="overlay")
            c.scale("overlay", 0, 0, PSC, PSC)
        elif self.state == "paused":
            c.delete("overlay")
            self.state, self.t_start = "run", time.time()
            self.cancel_tick()
            self.tick()

    def end_stage(self):
        if self.state == "done":
            return
        self.cancel_tick()
        self.active = self.total_sec
        self.state = "done"
        wpm, acc = self.stats()
        self.results.append((wpm, acc))
        self.update_labels()
        last = self.si == len(self.lesson["stages"]) - 1
        verdict = ("Excellent accuracy!" if acc >= 95 else "Good job - keep it up." if acc >= 90
                   else "Accuracy is below 90%.  Press Repeat and go a little slower.")
        c = self.canvas
        c.create_rectangle(70, 60, 630, 340, fill="white", outline=PURPLE, width=W(4), tags="overlay")
        c.create_text(350, 110, text="Lesson complete!" if last else "Stage complete!",
                      font=(FONT, F(24), "bold"), fill=PURPLE, tags="overlay")
        c.create_text(350, 190, text=f"Speed:  {wpm:.0f} WPM        Accuracy:  {acc:.0f}%        Errors:  {self.errors}",
                      font=(FONT, F(14), "bold"), fill="#222", tags="overlay")
        c.create_text(350, 245, text=verdict, font=(FONT, F(12)), fill="#444", tags="overlay")
        c.create_text(350, 295, text="Press Next to continue" if not last else "Press Next to finish and save",
                      font=(FONT, F(11)), fill="#888", tags="overlay")
        c.scale("overlay", 0, 0, PSC, PSC)
        if last:
            self.next_btn.config(text="Finish")

    # ---------------------------------------------------------- drawing
    def update_labels(self):
        wpm, acc = self.stats()
        left = max(0, math.ceil(self.total_sec - self.elapsed()))
        self.time_lbl.config(text=f"{left // 60:02d}:{left % 60:02d}")
        self.wpm_lbl.config(text=f"Speed:  {wpm:.0f} WPM")
        self.acc_lbl.config(text=f"Accuracy:  {acc:.0f}%")
        self.err_lbl.config(text=f"Errors:  {self.errors}")
        frac = min(1, self.elapsed() / self.total_sec) if self.total_sec else 1
        filled = math.ceil(frac * 10 - 1e-9) if frac > 0 else 0
        b = self.bars
        b.delete("all")
        for i in range(10):
            h, x = 22 + i * 10, 6 + i * 18
            b.create_rectangle(x, 118 - h, x + 13, 118, outline="#222", fill="#7bd13b" if i < filled else "#eaffc4")
        b.scale("all", 0, 0, PSC, PSC)

    def render(self):
        c = self.canvas
        c.delete("tile")
        small = self.stage["small"]
        cw, sw = tw(small)
        th, gap, rows = (26, 34, 4) if small else (38, 56, 2)
        for r in range(min(rows, len(self.lines))):
            x, y = 34, 42 + r * gap
            for j, ch in enumerate(self.lines[r]):
                sp = ch == " "
                done, cur = r == 0 and j < self.ci, r == 0 and j == self.ci
                w = 20 if small else (52 if sp else 34)
                if done:
                    fill, line, txt, lw = "#d8f5a2", "#58b000", "#2f7d00", 2
                elif cur:
                    fill, line, txt, lw = ("#fecaca", "#dc2626", "#7f1d1d", 3) if self.flash \
                        else ("white", "#f77f00", "#3b3f99", 3)
                elif r == 0:
                    fill, line, txt, lw = "#f4ffe6", "#7ccf1d", "#9aa6f5", 2
                else:
                    fill, line, txt, lw = "#f4ffe6", "#c9e8a2", "#c6cdf7", 2
                c.create_rectangle(x, y, x + w, y + th, fill=fill, outline=line, width=W(lw), tags="tile")
                label = ("·" if small else "Space") if sp else ch
                fs = 12 if small else (8 if sp else 16)
                c.create_text(x + w / 2, y + th / 2, text=label, fill=txt, font=(FONT, F(fs), "bold"), tags="tile")
                if sp and done and not small:
                    c.create_text(x + w + 12, y + th / 2, text="✓", fill="#43a500",
                                  font=(FONT, F(16), "bold"), tags="tile")
                x += sw if sp else cw
        c.scale("tile", 0, 0, PSC, PSC)

    def highlight(self):
        c = self.canvas
        for r, col in self.rects.values():
            c.itemconfig(r, fill=col, outline="#9aa0c8", width=W(2))
        for ids in self.fitems.values():
            for i in ids:
                c.itemconfig(i, fill=self.skin)
        ch = self.cur_char()
        if ch is None or self.state == "done":
            c.itemconfig(self.hint, text="")
            return
        k = base_key(ch)
        f = KEY_FINGER.get(k)
        if k not in self.rects or not f:
            return

        def mark(name):
            c.itemconfig(self.rects[name][0], fill="#ffd166", outline="#f77f00", width=W(3))

        def finger(name):
            for i in self.fitems[name]:
                c.itemconfig(i, fill="#ffb347")

        mark(k)
        finger(f)
        text = "Space bar  -  thumb" if f == "Thumb" else f"{f} finger"
        if needs_shift(ch):
            right_hand = f.startswith("Left")          # use opposite Shift
            mark("RSHIFT" if right_hand else "LSHIFT")
            finger("Right pinky" if right_hand else "Left pinky")
            text += f"   +   hold {'Right' if right_hand else 'Left'} Shift"
        if self.state == "ready":
            text = "Put your fingers on the home row and start typing.     " + text
        c.itemconfig(self.hint, text=text)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()