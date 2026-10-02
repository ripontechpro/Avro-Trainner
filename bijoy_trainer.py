"""Bijoy Bangla Typing Tutor (single file). Run: python bijoy_typing_tutor.py\nAlways fullscreen. Close button = bottom-left (or Ctrl+Q). F2 = kar order (age/pore)"""
import tkinter as tk, tkinter.font as tkf, json, os, time, unicodedata

BSAVE = os.path.join(os.path.expanduser("~"), ".bijoy_typing_progress.json")

# ---------------- Keyboard ----------------
ROWS = ["`1234567890-=", "qwertyuiop[]", "asdfghjkl;'", "zxcvbnm,./"]
ROWOFF = [0, 22, 30, 44]
FING = ["`1qaz", "2wsx", "3edc", "4rfv5tgb", "6yhn7ujm", "8ik,", "9ol.", "0p;/-[]'="]
FCOL = ["#fde2e4", "#ffe8cc", "#fff3bf", "#d3f9d8", "#d0ebff", "#e5dbff", "#fcc2d7", "#e9ecef"]
FMAP = {ch: FCOL[i] for i, g in enumerate(FING) for ch in g}
SHIFTED = {":": ";", "^": "6"}

def base_key(ch):
    if ch in SHIFTED: return SHIFTED[ch], True
    if ch.isalpha(): return ch.lower(), ch.isupper()
    return ch, False

# ---------------- Theme ----------------
BG, CARD, INK, MUTED = "#f3f4fb", "#ffffff", "#1f2340", "#8a8fb0"
ACC, GOOD, BAD = "#5b5bf0", "#22b573", "#ef4444"
SAVE = os.path.join(os.path.expanduser("~"), ".bangla_typing_progress.json")
nfd = lambda t: unicodedata.normalize("NFD", t)

def lerp(a, b, t):
    A = [int(a[i:i+2], 16) for i in (1, 3, 5)]; B = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(A, B))

class App(tk.Tk):
    def __init__(self, layout):
        super().__init__()
        self.L = layout
        self.title("Bangla Typing Tutor"); self.attributes("-fullscreen", True); self.update_idletasks()
        self.W, self.H = self.winfo_screenwidth(), self.winfo_screenheight()
        self.s = min(self.W / 1180, self.H / 760)
        self.ox, self.oy = (self.W - 1180 * self.s) / 2, (self.H - 760 * self.s) / 2
        self.protocol("WM_DELETE_WINDOW", self.destroy); self.bind("<Control-q>", lambda e: self.destroy()); self.bind("<F2>", self.toggle_opt)
        fams = set(tkf.families())
        bn = next((f for f in ("Nirmala UI", "Kalpurush", "Noto Sans Bengali", "Vrinda") if f in fams), "TkDefaultFont")
        F = lambda z, w="normal": tkf.Font(family=bn, size=max(6, int(z * self.s)), weight=w)
        self.fb = {"xs": F(9), "xl": F(60, "bold"), "l": F(40, "bold"), "m": F(24, "bold"), "s": F(13), "sb": F(13, "bold")}
        self.fk = tkf.Font(family="Consolas", size=max(8, int(17 * self.s)), weight="bold")
        self.fu = tkf.Font(family="Segoe UI", size=max(7, int(10 * self.s)))
        self.fv = tkf.Font(family="Segoe UI", size=max(10, int(20 * self.s)), weight="bold")
        try: self.prog = json.load(open(self.L["save"]))
        except Exception: self.prog = {}
        self.c = tk.Canvas(self, width=self.W, height=self.H, bg=BG, highlightthickness=0); self.c.pack(fill="both", expand=True)
        self.build(); self.bind("<Key>", self.on_key); self.select(0); self.tick()

    def pk(self):
        return self.name + self.L.get("tag", "")

    def toggle_opt(self, e=None):
        if self.L.get("toggle"):
            self.L = self.L["toggle"](); self.c.itemconfig(self.modet, text=self.L["mode"]); self.select(self.cur)

    def keylabel(self, ch, x, y, K):
        lab = self.L["labels"]
        if lab and ch in lab:
            n, sh = lab[ch]
            if sh: self.tx(x + K * 0.72, y + K * 0.24, text=sh, font=self.fb["xs"], fill=MUTED)
            return self.tx(x + K * 0.4, y + K * 0.62, text=n, font=self.fb["s"], fill=INK)
        return self.tx(x + K/2, y + K/2, text=ch.upper(), font=self.fu, fill=INK)

    def toggle_fs(self, e=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def tx(self, x, y, **kw):
        return self.c.create_text(self.ox + x * self.s, self.oy + y * self.s, **kw)

    def rr(self, x1, y1, x2, y2, r=16, **kw):
        sc = self.s; x1, x2, y1, y2, r = self.ox + x1*sc, self.ox + x2*sc, self.oy + y1*sc, self.oy + y2*sc, r*sc
        p = [x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,x2,y2,x2-r,y2,x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1]
        return self.c.create_polygon(p, smooth=True, **kw)
    def closetool(self, event=None):
        exit(0)
    def build(self):
        c = self.c
        self.rr(20, 20, 300, 740, fill=CARD, outline="")
        self.tx(160, 62, text="বাংলা টাইপিং", font=self.fb["m"], fill=ACC)
        self.tx(160, 96, text=self.L["title"], font=self.fu, fill=MUTED)
        self.lbtn = []
        for i, name in enumerate(self.L["lessons"]):
            y = 130 + i * 56; tg = f"les{i}"
            r = self.rr(36, y, 284, y + 46, 12, fill=CARD, outline="", tags=tg)
            t = self.tx(56, y + 23, text=name, font=self.fb["s"], fill=INK, anchor="w", tags=tg)
            c.tag_bind(tg, "<Button-1>", lambda e, i=i: self.select(i)); self.lbtn.append((r, t))
        self.best = self.tx(160, 556, text="", font=self.fu, fill=MUTED, justify="center")
        self.modet = self.tx(160, 610, text=self.L["mode"], font=self.fu, fill=ACC, justify="center")
        self.rr(36, 680, 154, 722, 14, fill=ACC, outline="", tags="rs")
        self.tx(95, 701, text="↻  Restart", font=self.fu, fill="white", tags="rs")
        cb = self.rr(166, 680, 284, 722, 14, fill=BAD, outline="", tags="cl")
        self.tx(225, 701, text="✕  Close", font=self.fu, fill="white", tags="cl")
        c.tag_bind("cl", "<Button-1>", lambda e: self.closetool())
        c.tag_bind("cl", "<Enter>", lambda e: c.itemconfig(cb, fill="#c62828"))
        c.tag_bind("cl", "<Leave>", lambda e: c.itemconfig(cb, fill=BAD))
        c.tag_bind("rs", "<Button-1>", lambda e: self.select(self.cur))
        self.stat = {}
        for i, (k, lab) in enumerate([("wpm", "WPM"), ("acc", "ACCURACY"), ("time", "TIME"), ("err", "ERRORS")]):
            x = 320 + i * 214
            self.rr(x, 20, x + 200, 90, 14, fill=CARD, outline="")
            self.tx(x + 16, 38, text=lab, font=self.fu, fill=MUTED, anchor="w")
            self.stat[k] = self.tx(x + 16, 66, text="0", font=self.fv, fill=INK, anchor="w")
        self.rr(320, 110, 1160, 450, 20, fill=CARD, outline="")
        self.rr(350, 128, 1130, 134, 3, fill="#e8eafc", outline="")
        self.bar = self.rr(350, 128, 356, 134, 3, fill=ACC, outline="")
        self.item_txt = self.tx(740, 190, text="", font=self.fb["xl"], fill=INK, tags="shk")
        self.rr(350, 340, 1130, 432, 16, fill="#f6f7ff", outline="#e3e6fb")
        self.tx(370, 358, text="YOUR OUTPUT", font=self.fu, fill=MUTED, anchor="w")
        self.badge = self.tx(1110, 358, text="", font=self.fu, fill=MUTED, anchor="e")
        self.out = self.tx(740, 396, text="", font=self.fb["m"], fill=INK)
        self.rr(320, 466, 1160, 740, 20, fill=CARD, outline="")
        self.kb = {}
        K, P_ = 42, 46
        for r, row in enumerate(ROWS):
            for i, ch in enumerate(row):
                x, y = 441 + ROWOFF[r] + i * P_, 484 + r * P_
                base = FMAP.get(ch, "#e9ecef")
                self.kb[ch] = (self.rr(x, y, x + K, y + K, 9, fill=base, outline=""), self.keylabel(ch, x, y, K), base)
        y = 484 + 3 * P_
        for nm, x1, x2 in (("shift", 386, 481), (" ", 531, 861)):
            yy = y if nm == "shift" else y + P_
            self.kb[nm] = (self.rr(x1, yy, x2, yy + K, 9, fill="#e9ecef", outline=""), self.tx((x1+x2)/2, yy + K/2, text=nm.upper() if nm != " " else "SPACE", font=self.fu, fill=INK), "#e9ecef")

    # ---- animation helper ----
    def fade(self, item, prop, a, b, steps=9, ms=28, i=0):
        try: self.c.itemconfig(item, **{prop: lerp(a, b, i / steps)})
        except tk.TclError: return
        if i < steps: self.after(ms, self.fade, item, prop, a, b, steps, ms, i + 1)

    def shake(self, seq=(9, -18, 18, -18, 9)):
        if seq:
            self.c.move("shk", seq[0] * self.s, 0); self.after(28, self.shake, seq[1:])

    # ---- logic ----
    def select(self, i):
        LS = self.L["lessons"]; self.cur, self.items = i, LS[list(LS)[i]]; self.name = list(LS)[i]
        self.idx = self.pos = self.ok = self.err = 0; self.start = None; self.done = False
        for j, (r, t) in enumerate(self.lbtn):
            self.c.itemconfig(r, fill=ACC if j == i else CARD); self.c.itemconfig(t, fill="white" if j == i else INK)
        b = self.prog.get(self.pk())
        self.c.itemconfig(self.best, text=f"Best\n{b['wpm']:.0f} WPM · {b['acc']:.0f}%" if b else "Best\n—")
        self.c.itemconfig(self.out, text="", fill=INK); self.c.itemconfig(self.badge, text="")
        self.show_item()

    def show_item(self):
        bn, keys = self.items[self.idx]
        self.target, self.keys, self.pos, self.typed = bn, keys, 0, ""
        self.c.itemconfig(self.item_txt, text=bn, font=self.fb["xl"] if len(bn) < 6 else self.fb["l"] if len(bn) < 14 else self.fb["m"])
        w = max(6, int(780 * (self.idx / len(self.items))))
        self.set_bar(w)
        self.chips(); self.highlight()

    def set_bar(self, w):
        self.c.delete(self.bar); self.bar = self.rr(350, 128, 350 + max(w, 8), 134, 3, fill=ACC, outline="")

    def chips(self, done_anim=False):
        self.c.delete("chip")
        n = len(self.keys); cw, gap = 40, 6
        x0 = 740 - (n * (cw + gap) - gap) / 2
        for i, ch in enumerate(self.keys):
            x = x0 + i * (cw + gap); y = 262
            fill, fg = ("#e6f9f0", GOOD) if i < self.pos else (ACC, "white") if i == self.pos else ("#eef0fb", INK)
            r = self.rr(x, y, x + cw, y + 44, 10, fill=fill, outline="", tags=("chip", "shk"))
            t = self.tx(x + cw/2, y + 22, text="␣" if ch == " " else ch, font=self.fk, fill=fg, tags=("chip", "shk"))
            if done_anim and i == self.pos - 1: self.fade(r, "fill", "#86efac", "#e6f9f0")
            if i == self.pos: self.fade(r, "fill", "#8b8bff", ACC)

    def highlight(self):
        for r, t, base in self.kb.values(): self.c.itemconfig(r, fill=base)
        if self.pos < len(self.keys):
            k, sh = self.L["base_key"](self.keys[self.pos])
            if k in self.kb: self.c.itemconfig(self.kb[k][0], fill=ACC)
            if sh: self.c.itemconfig(self.kb["shift"][0], fill="#ff922b")

    def flash_key(self, ch, col):
        k, _ = self.L["base_key"](ch)
        if k in self.kb and k != self.L["base_key"](self.keys[self.pos] if self.pos < len(self.keys) else " ")[0]:
            self.fade(self.kb[k][0], "fill", col, self.kb[k][2])

    def on_key(self, e):
        if self.done or not e.char or e.char in "\r\t\x1b\x08" or not e.char.isprintable(): return
        if self.start is None: self.start = time.time()
        if e.char == self.keys[self.pos]:
            self.ok += 1; self.pos += 1; self.typed += e.char
            self.c.itemconfig(self.out, text=self.L["convert"](self.typed)); self.fade(self.out, "fill", ACC, INK)
            self.c.itemconfig(self.badge, text="typing…", fill=MUTED)
            if self.pos == len(self.keys): return self.complete(e.char)
            self.chips(True); self.highlight(); self.flash_key(e.char, "#86efac")
        else:
            self.err += 1; self.shake(); self.flash_key(e.char, "#fca5a5")
            self.c.itemconfig(self.item_txt, fill=BAD); self.after(220, lambda: self.c.itemconfig(self.item_txt, fill=INK))

    def complete(self, last):
        got = self.L["convert"](self.typed)
        good = nfd(got) == nfd(self.target)
        if not good: self.err += 1
        self.c.itemconfig(self.out, text=got)
        self.fade(self.out, "fill", GOOD if good else BAD, GOOD if good else BAD)
        self.c.itemconfig(self.badge, text="✓ Perfect match" if good else f"✗ expected {self.target}", fill=GOOD if good else BAD)
        self.fade(self.item_txt, "fill", GOOD, INK, 14, 30)
        self.idx += 1
        if self.idx >= len(self.items): return self.finish()
        self.show_item()
        self.c.itemconfig(self.badge, text="✓ Perfect match" if good else f"✗ expected", fill=GOOD if good else BAD)

    def stats(self):
        el = time.time() - self.start if self.start else 0
        wpm = (self.ok / 5) / (el / 60) if el > 1 else 0
        tot = self.ok + self.err
        return el, wpm, 100 * self.ok / tot if tot else 100

    def tick(self):
        el, wpm, acc = self.stats()
        for k, v in (("wpm", f"{wpm:.0f}"), ("acc", f"{acc:.0f}%"), ("time", f"{int(el//60):02d}:{int(el%60):02d}"), ("err", str(self.err))):
            self.c.itemconfig(self.stat[k], text=v)
        self.after(200, self.tick)

    def finish(self):
        self.done = True
        el, wpm, acc = self.stats()
        if wpm > self.prog.get(self.pk(), {"wpm": -1})["wpm"]:
            self.prog[self.pk()] = {"wpm": wpm, "acc": acc}
            try: json.dump(self.prog, open(SAVE, "w"))
            except Exception: pass
        b = self.prog[self.pk()]
        self.c.itemconfig(self.best, text=f"Best\n{b['wpm']:.0f} WPM · {b['acc']:.0f}%")
        self.c.itemconfig(self.item_txt, text="শাবাশ! 🎉", font=self.fb["xl"]); self.set_bar(780)
        self.c.delete("chip"); self.tx(740, 284, text=f"{wpm:.0f} WPM  ·  {acc:.0f}% accuracy  ·  {self.err} errors", font=self.fb["sb"], fill=MUTED, tags="chip")
        self.highlight()


# physical key -> Bengali (Bijoy layout)
K2B = {'q':'ঙ','w':'য','e':'ড','r':'প','t':'ট','y':'চ','u':'জ','i':'হ','o':'গ','p':'\u09dc',
 'a':'ৃ','s':'ু','d':'ি','f':'া','g':'্','h':'ব','j':'ক','k':'ত','l':'দ','z':'্র','x':'ও','c':'ে','v':'র','b':'ন','n':'স','m':'ম',
 'Q':'ং','W':'\u09df','E':'ঢ','R':'ফ','T':'ঠ','Y':'ছ','U':'ঝ','I':'ঞ','O':'ঘ','P':'\u09dd',
 'S':'ূ','D':'ী','F':'অ','G':'।','H':'ভ','J':'খ','K':'থ','L':'ধ','Z':'্য','X':'\u09d7','V':'ল','B':'ণ','N':'ষ','M':'শ','C':'ৈ','&':'ঁ'}
for d, b in zip("1234567890", "১২৩৪৫৬৭৮৯০"): K2B[d] = b
CONS_KEYS = set("qwertyuiophjklvbnmWERTYUIOPHJKLVBNM")
CB = {K2B[k]: k for k in CONS_KEYS}
PRE_K = {"ি": "d", "ে": "c", "ৈ": "C"}
POST_K = {"া": "f", "ু": "s", "ূ": "S", "ৃ": "a", "ী": "D"}
PRE = {"d": "ি", "c": "ে", "C": "ৈ"}
INDEP_K = {"অ": "F", "আ": "gf", "ই": "gd", "ঈ": "gD", "উ": "gs", "ঊ": "gS", "ঋ": "ga", "এ": "gc", "ঐ": "gC", "ও": "x", "ঔ": "gX", "ং": "Q", "ঁ": "&"}
INDEP = {"f": "আ", "d": "ই", "D": "ঈ", "s": "উ", "S": "ঊ", "a": "ঋ", "c": "এ", "C": "ঐ", "X": "ঔ"}
for d, b in zip("1234567890", "১২৩৪৫৬৭৮৯০"): INDEP_K[b] = d

def fix(t):
    return t.replace("য\u09bc", "\u09df").replace("ড\u09bc", "\u09dc").replace("ঢ\u09bc", "\u09dd")

def encode(t, old):
    t = fix(t); out, i, n = "", 0, len(t)
    while i < n:
        ch = t[i]
        if ch in CB:
            cl = CB[ch]; i += 1
            while i + 1 < n and t[i] == "্":
                if t[i+1] == "র": cl += "z"
                elif t[i+1] == "য": cl += "Z"
                elif t[i+1] in CB: cl += "g" + CB[t[i+1]]
                else: break
                i += 2
            pre = post = inl = ""
            while i < n and (t[i] in PRE_K or t[i] in POST_K or t[i] in "োৌ"):
                s = t[i]; i += 1
                if s in PRE_K: pre += PRE_K[s]; inl += PRE_K[s]
                elif s in "োৌ": pre += "c"; post += "fX"["োৌ".index(s)]; inl += "c" + "fX"["োৌ".index(s)]
                else: post += POST_K[s]; inl += POST_K[s]
            out += pre + cl + post if old else cl + inl
        else:
            out += INDEP_K.get(ch, ch); i += 1
    return out

def make_convert(old):
    def cluster(s, i):
        out = K2B[s[i]]; i += 1
        while i < len(s):
            if s[i] == "g" and i + 1 < len(s) and s[i+1] in CONS_KEYS: out += "্" + K2B[s[i+1]]; i += 2
            elif s[i] in "zZ": out += K2B[s[i]]; i += 1
            else: break
        return out, i
    def convert(s):
        out, i, n = "", 0, len(s)
        while i < n:
            k = s[i]
            if old and k in PRE and i + 1 < n and s[i+1] in CONS_KEYS:
                cl, j = cluster(s, i + 1); kar = PRE[k]
                if k == "c" and j < n and s[j] in "fX": kar = "ো" if s[j] == "f" else "ৌ"; j += 1
                out += cl + kar; i = j
            elif k in CONS_KEYS:
                cl, i = cluster(s, i); out += cl
            elif k == "g" and i + 1 < n and s[i+1] in INDEP:
                out += INDEP[s[i+1]]; i += 2
            else:
                out += K2B.get(k, k); i += 1
        return out.replace("ে" + "া", "ো").replace("ে" + "\u09d7", "ৌ")
    return convert

BN = {
 "১. স্বরবর্ণ": "অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ".split(),
 "২. ব্যঞ্জনবর্ণ": "ক খ গ ঘ ঙ চ ছ জ ঝ ঞ ট ঠ ড ঢ ণ ত থ দ ধ ন প ফ ব ভ ম য র ল শ ষ স হ ড় ঢ় য় ং ঁ".split(),
 "৩. কার": "কা কি কী কু কূ কৃ কে কৈ কো কৌ বা মি নী তু রূ দে সৈ পো মৌ".split(),
 "৪. যুক্তাক্ষর": "ক্ষ জ্ঞ ক্ক ত্ত ন্ত ন্দ স্ত স্থ ম্ব ল্ল ম্প ন্ন দ্দ ঞ্চ ণ্ড ন্ধ শ্চ ষ্ট প্র ক্র ত্র ব্য স্ক্র".split(),
 "৫. শব্দ": "আমি তুমি আমার বাংলা মা বাবা ভাই বোন ভাত পানি বই দেশ ফুল নদী আকাশ স্কুল সোনার পাখি".split(),
 "৬. বাক্য": ["আমি বাংলায় গান গাই", "আমি ভাত খাই", "আকাশ নীল", "পাখি গান গায়", "সে স্কুলে যায়", "আমি বাংলা ভালোবাসি"],
 "৭. সংখ্যা": list("১২৩৪৫৬৭৮৯০") + ["১২৩", "৪৫৬", "৭৮৯০"],
}

def lessons(old):
    L = {name: [(t, encode(t, old)) for t in items] for name, items in BN.items()}
    return L

def disp(s):
    return ("◌" + s) if s and unicodedata.category(s[0]) in ("Mn", "Mc") else s

LAB = {}
for k in "qwertyuiopasdfghjklzxcvbnm1234567890":
    LAB[k] = (disp(K2B.get(k, "")), disp(K2B.get(k.upper(), "")) if k.isalpha() else "")
LAB["a"] = (disp("ৃ"), "র্"); LAB["x"] = ("ও", disp("ৌ")); LAB["7"] = ("৭", "ঁ")

def layout(old=True):
    return dict(title="Bijoy Typing Tutor", lessons=lessons(old), convert=make_convert(old),
                base_key=lambda c: ("7", True) if c == "&" else base_key(c), labels=LAB, save=BSAVE,
                tag="|old" if old else "|new", toggle=lambda: layout(not old),
                mode=("Kar age (Bijoy style: ি ে ৈ)" if old else "Kar pore (logical order)") + "\nF2 chepe bodlao")

if __name__ == "__main__":
    App(layout()).mainloop()