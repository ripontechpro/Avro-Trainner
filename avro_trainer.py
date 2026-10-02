"""Bangla Typing Tutor (Avro Phonetic)
   - Practice mode : timed session (default 60 min) per level, endless auto-generated lines
   - Test mode     : timed test (1/2/3/5 min), keys hidden, Backspace allowed, pass/fail result
Run:    python avro_trainer.py
Check:  python avro_trainer.py --check     (validates every lesson item against the converter)
"""
import tkinter as tk, tkinter.font as tkf, json, os, sys, time, random

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

CONJ = P("""ক্ষ=kkh জ্ঞ=jNG ক্ক=kk ত্ত=tt ন্ত=nt ন্দ=nd স্ত=st স্থ=sth ম্ব=mb ল্ল=ll ম্প=mp ন্ন=nn দ্দ=dd ঞ্চ=NGc ণ্ড=ND ন্ধ=ndh শ্চ=shc ষ্ট=ShT
 ক্ত=kt ক্র=kr গ্র=gr ত্র=tr দ্র=dr প্র=pr ব্র=br শ্র=shr স্র=sr ক্ল=kl গ্ল=gl প্ল=pl ব্ল=bl স্ক=sk স্ট=sT স্প=sp স্ম=sm স্ব=sb
 ম্ম=mm ম্ভ=mbh ন্ম=nm ন্স=ns ল্প=lp ল্ব=lb ল্ম=lm ষ্ক=Shk ষ্ণ=ShN ণ্ঠ=NTh ঙ্ক=Ngk ঙ্গ=Ngg ক্য=kz ত্য=tz দ্য=dz ন্য=nz
 ম্য=mz ব্য=bz স্য=sz র্ক=rk র্ম=rm র্ব=rb র্থ=rth র্গ=rg র্ত=rt র্দ=rd র্ণ=rN""")

WORDS = P("""
 মা=ma বাবা=baba ভাই=bhai বোন=bOn দাদা=dada দাদি=dadi নানা=nana নানি=nani চাচা=caca মামা=mama খালা=khala ফুফু=phuphu
 বন্ধু=bondhu শিক্ষক=shikkhok ছাত্র=chatro ছাত্রী=chatrI ডাক্তার=Daktar মানুষ=manuSh ছেলে=chele মেয়ে=meye শিশু=shishu রাজা=raja কৃষক=krriShok
 আকাশ=akash নদী=nodI ফুল=phul পাখি=pakhi গাছ=gach পাতা=pata মাঠ=maTh পাহাড়=pahaR সাগর=sagor সূর্য=sUrzo চাঁদ=ca^d তারা=tara
 মেঘ=megh বৃষ্টি=brriShTi বাতাস=batas রোদ=rOd মাটি=maTi পানি=pani আগুন=agun আলো=alO ফল=phol বন=bon ঝড়=jhoR ঢেউ=Dheu
 গরু=goru বিড়াল=biRal হাতি=hati ঘোড়া=ghORa বাঘ=bagh মাছ=mach কাক=kak হাঁস=ha^s মুরগি=murogi কুকুর=kukur সিংহ=singho
 ভালুক=bhaluk বানর=banor হরিণ=horiN ইঁদুর=i^dur টিয়া=Tiya
 ভাত=bhat রুটি=ruTi ডাল=Dal মাংস=mangs দুধ=dudh ডিম=Dim চা=ca আম=am কলা=kola আপেল=apel লেবু=lebu চিনি=cini লবণ=loboN
 মিষ্টি=miShTi সবজি=soboji তেল=tel পিঠা=piTha খিচুড়ি=khicuRi
 বই=boi খাতা=khata কলম=kolom স্কুল=skul ঘর=ghor দরজা=doroja জানালা=janala টেবিল=Tebil চেয়ার=ceyar গান=gan খেলা=khela
 রাস্তা=rasta গ্রাম=gram শহর=shohor দেশ=desh বাজার=bajar হাসপাতাল=hasopatal বিদ্যা=bidza পরীক্ষা=porIkkha ক্লাস=klas
 বিদ্যালয়=bidzaloy কম্পিউটার=kompiuTar ঘড়ি=ghoRi ছবি=chobi গাড়ি=gaRi নৌকা=nOUka
 ভালো=bhalO বড়=boR ছোট=chOT নতুন=notun পুরোনো=purOnO সুন্দর=sundor লাল=lal নীল=nIl সবুজ=sobuj হলুদ=holud কালো=kalO সাদা=sada
 ঠান্ডা=ThanDa গরম=gorom লম্বা=lomba দ্রুত=drut ধীরে=dhIre সহজ=sohoj কঠিন=koThin সত্য=sotzo
 যাই=zai খাই=khai পড়ি=poRi লিখি=likhi দেখি=dekhi করি=kori বলি=boli হাসি=hasi কাঁদি=ka^di গাই=gai নাচি=naci শুনি=shuni
 দৌড়াই=dOURai ঘুমাই=ghumai খেলি=kheli ভাবি=bhabi বুঝি=bujhi শিখি=shikhi চলি=coli থামি=thami আসি=asi ডাকি=Daki
 দিন=din রাত=rat সকাল=sokal সন্ধ্যা=sondhza সময়=somoy বছর=bochor মাস=mas সপ্তাহ=soptah আজ=aj কাল=kal এখন=ekhon তখন=tokhon
 বিকাল=bikal দুপুর=dupur সোমবার=sOmobar
 শিক্ষা=shikkha বিজ্ঞান=bijNGan ধন্যবাদ=dhonzobad স্বাধীন=sbadhIn স্বপ্ন=sbopno রাষ্ট্র=raShTro পত্র=potro মন্ত্রী=montrI যন্ত্র=zontro
 বিশ্ব=bishbo সম্পর্ক=sompork প্রশ্ন=proshno উত্তর=uttor সুস্থ=susth মুক্তি=mukti শক্তি=shokti ব্যবহার=bzobohar ব্যস্ত=bzosto
 চিত্র=citro মিত্র=mitro
""")

SENTENCES = P("""
 আমি_বাংলায়_গান_গাই=ami_banglay_gan_gai আমি_ভাত_খাই=ami_bhat_khai আকাশ_নীল=akash_nIl পাখি_গান_গায়=pakhi_gan_gay
 সে_স্কুলে_যায়=se_skule_zay আমি_বাংলা_ভালোবাসি=ami_bangla_bhalObasi আমার_নাম_রহিম=amar_nam_rohim আমি_স্কুলে_যাই=ami_skule_zai
 মা_ভাত_রান্না_করে=ma_bhat_ranna_kore বাবা_অফিসে_যান=baba_ophise_zan আমরা_সবাই_বাংলা_বলি=amora_sobai_bangla_boli
 নদীর_পানি_ঠান্ডা=nodIr_pani_ThanDa গাছে_পাখি_বসে_আছে=gache_pakhi_bose_ache তুমি_কেমন_আছ=tumi_kemon_ach
 আমি_ভালো_আছি=ami_bhalO_achi আজ_আকাশ_মেঘলা=aj_akash_meghola আমি_রোজ_বই_পড়ি=ami_rOj_boi_poRi
 সূর্য_পূর্ব_দিকে_ওঠে=sUrzo_pUrb_dike_OThe ফুল_দেখতে_সুন্দর=phul_dekhote_sundor আমার_দেশ_বাংলাদেশ=amar_desh_bangladesh
 আমি_প্রতিদিন_স্কুলে_যাই=ami_protidin_skule_zai শিক্ষক_আমাদের_পড়ান=shikkhok_amader_poRan বৃষ্টি_পড়ছে=brriShTi_poRoche
 আমি_চা_খাই=ami_ca_khai সে_ভালো_গান_গায়=se_bhalO_gan_gay ছেলেরা_মাঠে_খেলে=chelera_maThe_khele মেয়েরা_গান_গায়=meyera_gan_gay
 রাতে_আকাশে_তারা_ওঠে=rate_akashe_tara_OThe আমরা_একসাথে_খেলি=amora_ekosathe_kheli বাংলা_আমার_মাতৃভাষা=bangla_amar_matrribhaSha
 স্বাধীনতা_আমাদের_গর্ব=sbadhInota_amader_gorb সত্য_কথা_বলো=sotzo_kotha_bolO সময়_খুব_মূল্যবান=somoy_khub_mUlzoban
 ভোরে_পাখি_ডাকে=bhOre_pakhi_Dake সকালে_সূর্য_ওঠে=sokale_sUrzo_OThe তুমি_কোথায়_যাও=tumi_kOthay_zaO
 আমি_একটি_বই_পড়ছি=ami_ekoTi_boi_poRochi আজ_খুব_গরম=aj_khub_gorom মাছ_পানিতে_থাকে=mach_panite_thake গরু_ঘাস_খায়=goru_ghas_khay
 হাতি_অনেক_বড়=hati_onek_boR আমার_মা_খুব_ভালো=amar_ma_khub_bhalO নতুন_বছর_শুভ_হোক=notun_bochor_shubh_hOk
 পরিশ্রম_সফলতার_চাবিকাঠি=porishrom_sopholotar_cabikaThi দেশকে_ভালোবাসো=deshoke_bhalObasO
""", True)

LESSONS = {
 "১. স্বরবর্ণ": VOWELS,
 "২. ব্যঞ্জনবর্ণ": CONSONANTS,
 "৩. কার": KARS,
 "৪. যুক্তাক্ষর": CONJ,
 "৫. শব্দ": WORDS,
 "৬. বাক্য": SENTENCES,
 "৭. মিশ্র": [],          # generated from levels 3-6
}
POOLS = [VOWELS, CONSONANTS, KARS, CONJ, WORDS, SENTENCES]
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
ACC, GOOD, BAD, SOFT = "#5b5bf0", "#22b573", "#ef4444", "#e8eafc"
SAVE = os.path.join(os.path.expanduser("~"), ".bangla_typing_progress.json")

def lerp(a, b, t):
    A = [int(a[i:i+2], 16) for i in (1, 3, 5)]; B = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(A, B))

def fmt(sec):
    sec = int(max(0, sec)); h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Avro Typing Tutor"); self.attributes("-fullscreen", True); self.update_idletasks()
        self.W, self.H = self.winfo_screenwidth(), self.winfo_screenheight()
        self.s = min(self.W / 1180, self.H / 760)
        self.ox, self.oy = (self.W - 1180 * self.s) / 2, (self.H - 760 * self.s) / 2
        self.bind("<Escape>", self.closetool); self.bind("<F11>", self.toggle_fs); self.bind("<F2>", lambda e: self.toggle_pause())
        fams = set(tkf.families())
        bn = next((f for f in ("Nirmala UI", "Kalpurush", "Noto Sans Bengali", "Vrinda") if f in fams), "TkDefaultFont")
        F = lambda z, w="normal": tkf.Font(family=bn, size=max(6, int(z * self.s)), weight=w)
        self.fb = {"xl": F(60, "bold"), "l": F(40, "bold"), "m": F(24, "bold"), "s": F(13), "sb": F(13, "bold")}
        self.fk = tkf.Font(family="Consolas", size=max(8, int(17 * self.s)), weight="bold")
        self.fu = tkf.Font(family="Segoe UI", size=max(7, int(10 * self.s)))
        self.fv = tkf.Font(family="Segoe UI", size=max(10, int(20 * self.s)), weight="bold")
        try: self.prog = json.load(open(SAVE))
        except Exception: self.prog = {}
        self.mode, self.dur_idx, self.name, self.tc = "practice", {"practice": len(PRACTICE_MIN) - 1, "test": 1}, None, 0
        self.c = tk.Canvas(self, width=self.W, height=self.H, bg=BG, highlightthickness=0); self.c.pack(fill="both", expand=True)
        self.build(); self.bind("<Key>", self.on_key); self.select(0); self.tick()

    def closetool(self, event=None):
        self.commit()
        os._exit(0)

    def toggle_fs(self, e=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def tx(self, x, y, **kw):
        return self.c.create_text(self.ox + x * self.s, self.oy + y * self.s, **kw)

    def rr(self, x1, y1, x2, y2, r=16, **kw):
        sc = self.s; x1, x2, y1, y2, r = self.ox + x1*sc, self.ox + x2*sc, self.oy + y1*sc, self.oy + y2*sc, r*sc
        p = [x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,x2,y2,x2-r,y2,x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1]
        return self.c.create_polygon(p, smooth=True, **kw)

    def btn(self, x1, y1, x2, y2, text, fill, fg, tag, cmd):
        r = self.rr(x1, y1, x2, y2, 12, fill=fill, outline="", tags=tag)
        t = self.tx((x1 + x2) / 2, (y1 + y2) / 2, text=text, font=self.fu, fill=fg, tags=tag)
        self.c.tag_bind(tag, "<Button-1>", lambda e: cmd())
        return r, t

    def build(self):
        c = self.c
        self.rr(20, 20, 300, 740, fill=CARD, outline="")
        self.tx(160, 62, text="অভ্র টাইপিং", font=self.fb["m"], fill=ACC)
        self.tx(160, 96, text="Ripon Avro Phonetic Tutor", font=self.fu, fill=MUTED)
        self.lbtn = []
        for i, name in enumerate(LESSONS):
            y = 118 + i * 44; tg = f"les{i}"
            r = self.rr(36, y, 284, y + 38, 12, fill=CARD, outline="", tags=tg)
            t = self.tx(56, y + 19, text=name, font=self.fb["s"], fill=INK, anchor="w", tags=tg)
            c.tag_bind(tg, "<Button-1>", lambda e, i=i: self.select(i)); self.lbtn.append((r, t))
        self.best = self.tx(160, 456, text="", font=self.fu, fill=MUTED, justify="center")
        self.mbtn = {}
        for m, x1, x2, lab in (("practice", 36, 156, "Practice"), ("test", 164, 284, "Test")):
            tg = "m_" + m
            r = self.rr(x1, 492, x2, 530, 12, fill=SOFT, outline="", tags=tg)
            t = self.tx((x1 + x2) / 2, 511, text=lab, font=self.fu, fill=INK, tags=tg)
            c.tag_bind(tg, "<Button-1>", lambda e, m=m: self.set_mode(m)); self.mbtn[m] = (r, t)
        self.dur_b = self.btn(36, 538, 284, 576, "", SOFT, INK, "dur", self.cycle_dur)
        self.pause_b = self.btn(36, 584, 284, 622, "⏸  Pause  (F2)", SOFT, INK, "pause", self.toggle_pause)
        self.btn(36, 630, 284, 668, "↻  Restart", ACC, "white", "rs", lambda: self.select(self.cur))
        self.btn(36, 678, 284, 716, "Close  (Esc)", "#ff0303", "white", "hello", self.closetool)

        self.stat = {}
        for i, (k, lab) in enumerate([("wpm", "WPM"), ("acc", "ACCURACY"), ("time", "TIME LEFT"), ("err", "ERRORS")]):
            x = 320 + i * 214
            self.rr(x, 20, x + 200, 90, 14, fill=CARD, outline="")
            self.tx(x + 16, 38, text=lab, font=self.fu, fill=MUTED, anchor="w")
            self.stat[k] = self.tx(x + 16, 66, text="0", font=self.fv, fill=INK, anchor="w")
        self.rr(320, 110, 1160, 450, 20, fill=CARD, outline="")
        self.rr(350, 128, 1130, 134, 3, fill=SOFT, outline="")
        self.bar = self.rr(350, 128, 356, 134, 3, fill=ACC, outline="")
        self.stage_lbl = self.tx(350, 148, text="", font=self.fu, fill=MUTED, anchor="w")
        self.mode_lbl = self.tx(1130, 148, text="", font=self.fu, fill=MUTED, anchor="e")
        self.item_txt = self.tx(740, 196, text="", font=self.fb["xl"], fill=INK, tags="shk")
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
                self.kb[ch] = (self.rr(x, y, x + K, y + K, 9, fill=base, outline=""), self.tx(x + K/2, y + K/2, text=ch.upper(), font=self.fu, fill=INK), base)
        y = 484 + 3 * P_
        for nm, x1, x2 in (("shift", 386, 481), (" ", 531, 861)):
            yy = y if nm == "shift" else y + P_
            self.kb[nm] = (self.rr(x1, yy, x2, yy + K, 9, fill="#e9ecef", outline=""), self.tx((x1+x2)/2, yy + K/2, text=nm.upper() if nm != " " else "SPACE", font=self.fu, fill=INK), "#e9ecef")

    # ---- animation helpers ----
    def fade(self, item, prop, a, b, steps=9, ms=28, i=0):
        try: self.c.itemconfig(item, **{prop: lerp(a, b, i / steps)})
        except tk.TclError: return
        if i < steps: self.after(ms, self.fade, item, prop, a, b, steps, ms, i + 1)

    def shake(self, seq=(9, -18, 18, -18, 9)):
        if seq:
            self.c.move("shk", seq[0] * self.s, 0); self.after(28, self.shake, seq[1:])

    # ---- progress / timing ----
    def save(self):
        try:
            with open(SAVE, "w") as f: json.dump(self.prog, f)
        except Exception: pass

    def elapsed(self):
        return self.accum + (time.time() - self.t0 if self.t0 else 0)

    def commit(self):
        """Add practice seconds of this session to the saved total for the level."""
        if self.name and self.mode == "practice":
            el = self.elapsed(); d = el - self.committed
            if d > 0:
                k = self.name + "|secs"; self.prog[k] = self.prog.get(k, 0) + d; self.committed = el; self.save()

    def refresh_best(self):
        f = lambda d: f"{d['wpm']:.0f} WPM · {d['acc']:.0f}%" if isinstance(d, dict) else "—"
        secs = int(self.prog.get(self.name + "|secs", 0))
        self.c.itemconfig(self.best, text=f"Practice best  {f(self.prog.get(self.name))}\n"
                          f"Test best  {f(self.prog.get(self.name + '|test'))}\n"
                          f"Total practice  {secs // 3600}h {secs % 3600 // 60:02d}m")

    def set_mode(self, m):
        self.mode = m; self.select(self.cur)

    def cycle_dur(self):
        self.dur_idx[self.mode] = (self.dur_idx[self.mode] + 1) % len(DUR[self.mode]); self.select(self.cur)

    def toggle_pause(self):
        if self.done or not self.began: return
        if self.paused:
            self.paused = False; self.t0 = time.time(); self.c.itemconfig(self.badge, text="", fill=MUTED)
            self.c.itemconfig(self.pause_b[1], text="⏸  Pause  (F2)")
        else:
            self.accum = self.elapsed(); self.t0 = None; self.paused = True; self.commit()
            self.c.itemconfig(self.badge, text="⏸ Paused - press F2 to resume", fill="#ff922b")
            self.c.itemconfig(self.pause_b[1], text="▶  Resume  (F2)")

    # ---- logic ----
    def select(self, i):
        if self.name: self.commit()
        self.cur, self.name = i, list(LESSONS)[i]
        self.gen = stream(i) if self.mode == "practice" else test_stream(i)
        self.limit = DUR[self.mode][self.dur_idx[self.mode]] * 60
        self.ok = self.err = self.good = self.bad = self.line_no = 0
        self.accum, self.t0, self.began, self.paused, self.done, self.committed = 0.0, None, False, False, False, 0.0
        for j, (r, t) in enumerate(self.lbtn):
            self.c.itemconfig(r, fill=ACC if j == i else CARD); self.c.itemconfig(t, fill="white" if j == i else INK)
        for m, (r, t) in self.mbtn.items():
            on = m == self.mode
            self.c.itemconfig(r, fill=ACC if on else SOFT); self.c.itemconfig(t, fill="white" if on else INK)
        self.c.itemconfig(self.dur_b[1], text=f"⏱  {self.limit // 60} min   (click to change)")
        self.c.itemconfig(self.pause_b[1], text="⏸  Pause  (F2)")
        self.c.itemconfig(self.mode_lbl, text=f"{self.mode.upper()} · {self.limit // 60} min")
        self.refresh_best()
        self.c.itemconfig(self.out, text="", fill=INK); self.c.itemconfig(self.badge, text="", fill=MUTED)
        self.c.delete("chip"); self.set_bar(8); self.barw = 0
        self.show_item()

    def show_item(self):
        (bn, keys), self.stage = next(self.gen)
        self.line_no += 1
        self.target, self.keys, self.pos, self.typed = bn, keys, 0, ""
        self.c.itemconfig(self.item_txt, text=bn, fill=INK, font=self.fb["xl"] if len(bn) < 6 else self.fb["l"] if len(bn) < 14 else self.fb["m"])
        self.info(); self.chips(); self.highlight()

    def info(self):
        if self.mode == "practice": t = f"Stage: {self.stage}  ·  Line {self.line_no}"
        else: t = f"Line {self.line_no}  ·  ✓ {self.good}   ✗ {self.bad}   ·  keys hidden, Backspace allowed"
        self.c.itemconfig(self.stage_lbl, text=t)

    def set_bar(self, w):
        self.c.delete(self.bar); self.bar = self.rr(350, 128, 350 + max(w, 8), 134, 3, fill=ACC, outline="")

    def chips(self, done_anim=False):
        self.c.delete("chip")
        test, n, pos = self.mode == "test", len(self.keys), self.pos
        VIS, cw, gap = 16, 40, 6                                  # long lines scroll in a 16-key window
        a = max(0, min(pos - 7, n - VIS)); b = min(n, a + VIS); m = b - a
        x0 = 740 - (m * (cw + gap) - gap) / 2
        for j, i in enumerate(range(a, b)):
            x = x0 + j * (cw + gap); y = 262; ch = self.keys[i]
            if test:
                if i < pos:
                    t = self.typed[i]; okc = t == ch
                    fill, fg, txt = ("#e6f9f0", GOOD, t) if okc else ("#fee2e2", BAD, t)
                else:
                    fill, fg, txt = (ACC, "white", "") if i == pos else ("#eef0fb", INK, "")
            else:
                fill, fg = ("#e6f9f0", GOOD) if i < pos else (ACC, "white") if i == pos else ("#eef0fb", INK)
                txt = ch
            r = self.rr(x, y, x + cw, y + 44, 10, fill=fill, outline="", tags=("chip", "shk"))
            self.tx(x + cw/2, y + 22, text="␣" if txt == " " else txt, font=self.fk, fill=fg, tags=("chip", "shk"))
            if not test:
                if done_anim and i == pos - 1: self.fade(r, "fill", "#86efac", "#e6f9f0")
                if i == pos: self.fade(r, "fill", "#8b8bff", ACC)
        if a > 0: self.tx(x0 - 16, 284, text="‹", font=self.fk, fill=MUTED, tags="chip")
        if b < n: self.tx(x0 + m * (cw + gap) + 10, 284, text="›", font=self.fk, fill=MUTED, tags="chip")

    def highlight(self):
        for r, t, base in self.kb.values(): self.c.itemconfig(r, fill=base)
        if self.mode == "test": return                           # no keyboard hints in test mode
        if self.pos < len(self.keys):
            k, sh = base_key(self.keys[self.pos])
            if k in self.kb: self.c.itemconfig(self.kb[k][0], fill=ACC)
            if sh: self.c.itemconfig(self.kb["shift"][0], fill="#ff922b")

    def flash_key(self, ch, col):
        k, _ = base_key(ch)
        if k in self.kb and k != base_key(self.keys[self.pos] if self.pos < len(self.keys) else " ")[0]:
            self.fade(self.kb[k][0], "fill", col, self.kb[k][2])

    def begin(self):
        if not self.began: self.began, self.t0 = True, time.time()

    def on_key(self, e):
        if self.done or self.paused: return
        if e.keysym == "BackSpace": return self.back()
        if not e.char or e.char in "\r\t\x1b\x08" or not e.char.isprintable(): return
        self.begin()
        (self.key_test if self.mode == "test" else self.key_practice)(e.char)

    # -- practice: must type the right key to advance
    def key_practice(self, ch):
        if ch == self.keys[self.pos]:
            self.ok += 1; self.pos += 1; self.typed += ch
            self.c.itemconfig(self.out, text=convert(self.typed)); self.fade(self.out, "fill", ACC, INK)
            self.c.itemconfig(self.badge, text="typing…", fill=MUTED)
            if self.pos == len(self.keys): return self.complete()
            self.chips(True); self.highlight(); self.flash_key(ch, "#86efac")
        else:
            self.err += 1; self.shake(); self.flash_key(ch, "#fca5a5")
            self.c.itemconfig(self.item_txt, fill=BAD); self.after(220, lambda: self.c.itemconfig(self.item_txt, fill=INK))

    def complete(self):
        got = convert(self.typed); good = got == self.target
        self.c.itemconfig(self.out, text=got)
        self.fade(self.out, "fill", GOOD if good else BAD, GOOD if good else BAD)
        self.fade(self.item_txt, "fill", GOOD, INK, 14, 30)
        self.show_item()
        self.c.itemconfig(self.badge, text="✓ Perfect match" if good else "✗ mismatch", fill=GOOD if good else BAD)

    # -- test: free typing, errors are counted but you may fix with Backspace
    def key_test(self, ch):
        if ch == self.keys[self.pos]: self.ok += 1
        else: self.err += 1
        self.typed += ch; self.pos += 1
        self.c.itemconfig(self.out, text=convert(self.typed), fill=INK)
        if self.pos == len(self.keys): return self.submit()
        self.chips()

    def back(self):
        if self.mode == "test" and self.pos > 0:
            self.pos -= 1; self.typed = self.typed[:-1]
            self.c.itemconfig(self.out, text=convert(self.typed), fill=INK); self.chips()

    def submit(self):
        got = convert(self.typed); good = got == self.target
        if good: self.good += 1
        else: self.bad += 1
        self.c.itemconfig(self.out, text=got)
        self.fade(self.out, "fill", GOOD if good else BAD, GOOD if good else BAD)
        self.show_item()
        self.c.itemconfig(self.badge, text="previous line ✓" if good else "previous line ✗", fill=GOOD if good else BAD)

    def stats(self):
        el = self.elapsed()
        wpm = (self.ok / 5) / (el / 60) if el > 1 else 0
        tot = self.ok + self.err
        return el, wpm, 100 * self.ok / tot if tot else 100

    def tick(self):
        el, wpm, acc = self.stats()
        for k, v in (("wpm", f"{wpm:.0f}"), ("acc", f"{acc:.0f}%"), ("time", fmt(self.limit - el)), ("err", str(self.err))):
            self.c.itemconfig(self.stat[k], text=v)
        w = int(780 * min(1, el / self.limit))
        if abs(w - self.barw) >= 2 and not self.done: self.barw = w; self.set_bar(w)
        self.tc += 1
        if self.tc % 150 == 0: self.commit()                     # autosave practice time every 30 s
        if self.began and not self.paused and not self.done and el >= self.limit: self.finish()
        self.after(200, self.tick)

    def finish(self):
        self.done = True
        self.commit()
        el, wpm, acc = self.stats()
        test = self.mode == "test"; passed = acc >= PASS_ACC
        k = self.name + ("|test" if test else "")
        old = self.prog.get(k); old = old["wpm"] if isinstance(old, dict) else -1
        if (passed or not test) and wpm > old:
            self.prog[k] = {"wpm": wpm, "acc": acc}; self.save()
        self.refresh_best()
        title = ("পাস! 🎉" if passed else "আবার চেষ্টা করুন") if test else "শাবাশ! 🎉"
        self.c.itemconfig(self.item_txt, text=title, fill=GOOD if (passed or not test) else BAD, font=self.fb["xl"]); self.set_bar(780)
        self.c.delete("chip")
        self.tx(740, 270, text=f"{wpm:.0f} WPM  ·  {acc:.0f}% accuracy  ·  {self.err} errors", font=self.fb["sb"], fill=MUTED, tags="chip")
        if test:
            msg = f"Lines correct: {self.good} / {self.good + self.bad}   ·   " + ("PASSED" if passed else f"need ≥ {PASS_ACC}% accuracy to pass")
        else:
            secs = int(self.prog.get(self.name + "|secs", 0))
            msg = f"{self.line_no - 1} lines practised   ·   total on this level: {secs // 3600}h {secs % 3600 // 60:02d}m"
        self.tx(740, 302, text=msg, font=self.fb["sb"], fill=MUTED, tags="chip")
        self.c.itemconfig(self.stage_lbl, text="Session finished - press Restart or choose another level")
        self.highlight()

if __name__ == "__main__":
    if "--check" in sys.argv: sys.exit(1 if check() else 0)
    App().mainloop()