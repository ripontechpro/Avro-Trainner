"""Bijoy lesson data + converter (extracted unchanged from bijoy_trainer.py)."""
import os, random, unicodedata
BSAVE = os.path.join(os.path.expanduser("~"), ".bijoy_typing_progress.json")
SHIFTED = {":": ";", "^": "6"}
def base_key(ch):
    if ch in SHIFTED: return SHIFTED[ch], True
    if ch.isalpha(): return ch.lower(), ch.isupper()
    return ch, False
nfd = lambda t: unicodedata.normalize("NFD", t)
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

import wordlists as WL

BN_FILES = [("১. স্বরবর্ণ", "bijoy_vowels.txt"), ("২. ব্যঞ্জনবর্ণ", "bijoy_consonants.txt"),
            ("৩. কার", "bijoy_kar.txt"), ("৪. যুক্তাক্ষর", "bijoy_conjuncts.txt"),
            ("৫. শব্দ", "bijoy_words.txt"), ("৬. বাক্য", "bijoy_sentences.txt"),
            ("৭. সংখ্যা", "bijoy_numbers.txt")]
BN = {}


def reload():
    """(Re)read wordlist/bijoy_*.txt  (one Bangla item per line)."""
    global BN
    BN = {nm: WL.lines(fn) for nm, fn in BN_FILES}


def file_of(level_name):
    return dict(BN_FILES).get(level_name, "")


reload()

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

