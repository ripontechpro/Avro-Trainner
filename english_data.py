"""English (Typing-Master style) lessons + generators (extracted unchanged from english_trainer.py)."""
import random
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
import wordlists as WL

WORDS, PUNCT_TOKENS, NUM_TOKENS, SHORT, LONG, MIXED = [], [], [], [], [], []
LEVELS = []

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
G_HOME = ["asdf", "gh", "jkl;"]      # ordered groups used for the "in order" part of each stage
G_TOP = ["qwerty", "uiop"]
G_BOT = ["zxcvb", "nm,."]


def word_stages(pool, mins, punct=False):
    return [S("Words - small letters", kind="words", pool=pool, mins=mins[0], punct=punct),
            S("Words - Capital letters", kind="words", pool=pool, case="cap", mins=mins[1], punct=punct),
            S("Words - mixed", kind="words", pool=pool, case="mixed", mins=mins[2], punct=punct)]


def build_levels():
    HW = words_for("asdfghjkl")
    TW = words_for(TOP + "asdfghjkl", TOP)
    BW = words_with("zxcvbnm")
    levels = [
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
    # drop stages/lessons/levels whose wordlist is empty (never crash on an edited/missing file)
    for lv in levels:
        for ls in lv["lessons"]:
            ls["stages"] = [st for st in ls["stages"]
                            if st["kind"] == "drill" or len(st["pool"] or []) >= (3 if st["kind"] == "para" else 1)]
        lv["lessons"] = [ls for ls in lv["lessons"] if ls["stages"]]
    return [lv for lv in levels if lv["lessons"]]


def reload():
    """(Re)read wordlist/english_*.txt and rebuild all levels."""
    global WORDS, PUNCT_TOKENS, NUM_TOKENS, SHORT, LONG, MIXED, LEVELS
    WORDS = WL.lines("english_words.txt")
    PUNCT_TOKENS = WL.lines("english_punct.txt")
    NUM_TOKENS = WL.lines("english_numbers.txt")
    SHORT = WL.lines("english_short.txt")
    LONG = WL.lines("english_long.txt")
    MIXED = WL.lines("english_mixed.txt")
    LEVELS = build_levels()


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


reload()
