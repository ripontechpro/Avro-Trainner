"""Avro phonetic lesson data + converter (extracted unchanged from avro_trainer.py)."""
import random, sys
# ---------------- Avro-style converter (for the live output box) ----------------
CONS = {"kkh":"ক্ষ","jNG":"জ্ঞ","kh":"খ","gh":"ঘ","ch":"ছ","jh":"ঝ","Th":"ঠ","Dh":"ঢ","th":"থ","dh":"ধ","ph":"ফ","bh":"ভ",
 "sh":"শ","Sh":"ষ","Rh":"ঢ়","NG":"ঞ","Ng":"ঙ","t``":"ৎ","k":"ক","g":"গ","c":"চ","j":"জ","T":"ট","D":"ড","N":"ণ","t":"ত",
 "d":"দ","n":"ন","p":"প","b":"ব","m":"ম","z":"য","r":"র","l":"ল","s":"স","h":"হ","R":"ড়","y":"য়"}
VOW = {"rri":("ঋ","ৃ"),"OU":("ঔ","ৌ"),"OI":("ঐ","ৈ"),"a":("আ","া"),"i":("ই","ি"),"I":("ঈ","ী"),"u":("উ","ু"),
 "U":("ঊ","ূ"),"e":("এ","ে"),"O":("ও","ো"),"o":("অ","")}
MARK = {"ng":"ং",":":"ঃ","^":"ঁ"}

def convert(s):
    out, prev, i = [], None, 0
    while i < len(s):
        for n in (3, 2, 1):
            t = s[i:i+n]
            if t in CONS or t in VOW or t in MARK:
                break
        else:
            out.append(s[i]); prev = None; i += 1; continue
        if t in MARK:
            out.append(MARK[t]); prev = "m"
        elif t in CONS:
            c = CONS[t]
            out.append(("্য" if t == "y" else "্" + c) if prev == "c" else c); prev = "c"
        else:
            ind, kar = VOW[t]
            if t == "o" and prev == "v": ind = "ও"
            out.append(kar if prev == "c" else ind); prev = "v"
        i += len(t)
    return "".join(out)

# ---------------- Lesson data ----------------
def P(s, sp=False):
    r = [tuple(p.split("=")) for p in s.split()]
    return [(b.replace("_", " "), a.replace("_", " ")) for b, a in r] if sp else r

VOWELS = P("অ=o আ=a ই=i ঈ=I উ=u ঊ=U ঋ=rri এ=e ঐ=OI ও=O ঔ=OU")

CONSONANTS = P("ক=k খ=kh গ=g ঘ=gh ঙ=Ng চ=c ছ=ch জ=j ঝ=jh ঞ=NG ট=T ঠ=Th ড=D ঢ=Dh ণ=N ত=t থ=th দ=d ধ=dh ন=n প=p ফ=ph ব=b ভ=bh ম=m য=z র=r ল=l শ=sh ষ=Sh স=s হ=h ড়=R ঢ়=Rh য়=y ৎ=t`` ং=ng ঃ=: ঁ=^")

_C = "k=ক kh=খ g=গ gh=ঘ c=চ ch=ছ j=জ T=ট D=ড t=ত th=থ d=দ dh=ধ n=ন p=প ph=ফ b=ব bh=ভ m=ম r=র l=ল s=স sh=শ h=হ"
_K = "a=া i=ি I=ী u=ু U=ূ rri=ৃ e=ে OI=ৈ O=ো OU=ৌ"
def _kar():   # every consonant x every kar  (kar-major order: কা খা গা ... কি খি গি ...)
    cs = [tuple(x.split("=")) for x in _C.split()]
    ks = [tuple(x.split("=")) for x in _K.split()]
    return [(b + kb, ck + kk) for kk, kb in ks for ck, b in cs]
KARS = _kar()

# ---------------- Word lists: loaded from wordlist/*.txt (nothing is stored in code) ----------------
import wordlists as WL

CONJ, WORDS, SENTENCES = [], [], []
LESSONS, POOLS = {}, []
LEVEL_FILES = {3: "avro_conjuncts.txt", 4: "avro_words.txt", 5: "avro_sentences.txt"}


def reload():
    """(Re)read wordlist/avro_*.txt. Missing/empty file => that level shows a clear message."""
    global CONJ, WORDS, SENTENCES, LESSONS, POOLS
    CONJ = WL.pairs("avro_conjuncts.txt")
    WORDS = WL.pairs("avro_words.txt")
    SENTENCES = WL.pairs("avro_sentences.txt")
    LESSONS = {
        "১. স্বরবর্ণ": VOWELS, "২. ব্যঞ্জনবর্ণ": CONSONANTS, "৩. কার": KARS,
        "৪. যুক্তাক্ষর": CONJ, "৫. শব্দ": WORDS, "৬. বাক্য": SENTENCES, "৭. মিশ্র": [],
    }
    POOLS = [VOWELS, CONSONANTS, KARS, CONJ, WORDS, SENTENCES]


def level_problem(idx):
    """None if the level can run, else a human readable reason (which wordlist file is empty)."""
    need = [idx] if idx < 6 else [3, 4, 5]
    bad = [LEVEL_FILES[i] for i in need if i in LEVEL_FILES and not POOLS[i]]
    return None if not bad else "wordlist/" + ", wordlist/".join(bad) + " - khali ba file nai"


reload()

KINDS = ["short", "short", "short", "short", "word", "sent"]
PER = {"short": 5, "word": 3, "sent": 1}                       # items per practice line
MIXPOOLS = {0: [0], 1: [0, 1, 1], 2: [1, 2, 2], 3: [2, 3, 3], 4: [3, 4, 4], 5: [4, 5, 5], 6: [2, 3, 4, 5]}

PRACTICE_MIN = [10, 20, 30, 45, 60]     # click the duration button to cycle
TEST_MIN = [1, 2, 3, 5]
DUR = {"practice": PRACTICE_MIN, "test": TEST_MIN}
PASS_ACC = 90                            # test passes at >= 90 % accuracy

def join(items):
    return " ".join(b for b, _ in items), " ".join(k for _, k in items)

def rand_line(pi, last=None):
    pool, per = POOLS[pi], PER[KINDS[pi]]
    for _ in range(6):
        line = join(random.sample(pool, min(per, len(pool))))
        if line != last: break
    return line

def mix_line(idx, last=None):
    return rand_line(random.choice(MIXPOOLS[idx]), last)

def stream(idx):
    """Endless practice lines for a level: Learn -> Repeat -> (Drill, Mix) forever."""
    last = None
    if idx < 6:
        pool, per = POOLS[idx], PER[KINDS[idx]]
        if len(pool) <= 15:                                      # tiny pool: repeat each item
            for it in pool:
                for _ in range(2): yield join([it] * 3), "Learn"
        else:
            for p in range(2):
                seq = pool[:] if p == 0 else random.sample(pool, len(pool))
                for i in range(0, len(seq), per): yield join(seq[i:i + per]), "Learn" if p == 0 else "Repeat"
    while True:
        for _ in range(25):
            last = rand_line(idx, last) if idx < 6 else mix_line(idx, last)
            yield last, "Drill" if idx < 6 else "Mixed"
        for _ in range(25):
            last = mix_line(idx, last)
            yield last, "Mix" if idx < 6 else "Mixed"

def test_stream(idx):
    last = None
    while True:
        last = mix_line(idx, last) if idx >= 1 else rand_line(0, last)
        yield last, "Test"

def check():
    bad = 0
    for name, pool in LESSONS.items():
        for bn, keys in pool:
            if convert(keys) != bn:
                bad += 1; print("MISMATCH", name, bn, keys, "->", convert(keys))
    print("All lesson items OK" if not bad else f"{bad} mismatches")
    return bad
