"""
Typing Practice — বাংলা (অভ্র) | English | বিজয়
--------------------------------------------------
একটি আধুনিক ডেস্কটপ অ্যাপ (Tkinter দিয়ে তৈরি) — তিন ধরনের টাইপিং প্র্যাকটিসের জন্য:
  1) বাংলা (অভ্র ফোনেটিক, ইউনিকোড)
  2) English (QWERTY)
  3) বিজয় কীবোর্ড (ANSI ফন্ট, যেমন SutonnyMJ)

চালানোর নিয়ম (Run):
    python typing_practice.py

EXE বানানোর নিয়ম:
    pip install pyinstaller
    pyinstaller --onefile --windowed --name TypingPractice typing_practice.py

কীবোর্ড শর্টকাট:
    F11     - পূর্ণ স্ক্রিন (edge-to-edge) চালু/বন্ধ
    Escape  - পূর্ণ স্ক্রিন থেকে বের হওয়া
"""

import json
import os
import sys
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import avro
from bijoy_converter import unicode_to_bijoy
def get_base_dir():
    """
    ডেটা ফাইল (paragraphs*.json) কোন ফোল্ডারে থাকবে তা ঠিক করে।

    - সাধারণ .py স্ক্রিপ্ট হিসেবে চালালে: স্ক্রিপ্টের ফোল্ডার।
    - PyInstaller দিয়ে বানানো --onefile EXE হিসেবে চালালে: __file__ আসলে
      একটা টেম্পোরারি এক্সট্র্যাকশন ফোল্ডারে (_MEIPASS) পয়েন্ট করে, যেটা
      প্রোগ্রাম বন্ধ হলেই মুছে যায়। তাই সেক্ষেত্রে EXE ফাইলটা যেখানে
      আছে (sys.executable) সেই ফোল্ডার ব্যবহার করা হয়, যাতে ডেটা স্থায়ী থাকে।
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
LOGO_CANDIDATES = ["image.png", "logo.png", "ripon.png", "image.jpg", "logo.jpg"]
LOGO_SIZE = 110  # গোল লোগোর ব্যাস (পিক্সেল)


def find_logo_path():
    """BASE_DIR এ উপরের নামগুলোর মধ্যে যেটা প্রথমে পাওয়া যায় সেই ফাইলের পাথ রিটার্ন করে।"""
    for name in LOGO_CANDIDATES:
        p = os.path.join(BASE_DIR, name)
        if os.path.exists(p):
            return p
    return None


def _log_logo_issue(msg):
    """
    লোগো লোড না হলে exe (--windowed) বা ডাবল-ক্লিকে চালানো অবস্থায় print()
    কোথাও দেখা যায় না (কনসোল থাকে না) — তাই কারণটা একটা লগ ফাইলে লিখে রাখা
    হয়, যাতে পরে খুলে দেখা যায় ঠিক কী সমস্যা হয়েছিল।
    """
    print(msg)
    try:
        log_path = os.path.join(BASE_DIR, "logo_debug.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def load_circular_logo(path, size=LOGO_SIZE):
    """
    যদি path না দেওয়া থাকে (None), বা ফাইল না পাওয়া যায়, বা Pillow ইনস্টল না
    থাকে — তাহলে None রিটার্ন করে, সেক্ষেত্রে অ্যাপ লোগো ছাড়াই স্বাভাবিকভাবে চলবে।
    সমস্যার কারণ logo_debug.log ফাইলে লেখা থাকবে।
    """
    try:
        from PIL import Image, ImageDraw, ImageOps, ImageTk
    except ImportError as e:
        _log_logo_issue(f"[লোগো] Pillow ইমপোর্ট করা যায়নি — 'pip install pillow' করুন। ({e})")
        return None

    if not path or not os.path.exists(path):
        _log_logo_issue(f"[লোগো] ছবির ফাইল খুঁজে পাওয়া যায়নি। BASE_DIR = {BASE_DIR}, "
                         f"খোঁজা হয়েছে: {LOGO_CANDIDATES}")
        return None

    # Pillow 9.1+ এ Image.LANCZOS এর বদলে Image.Resampling.LANCZOS সুপারিশ করা
    # হয়, আর কিছু Pillow ভার্সনে পুরনো নামটা কাজ নাও করতে পারে — তাই দুই
    # রকমই চেষ্টা করা হচ্ছে, যেন Pillow-এর ভার্সন যাই হোক না কেন কাজ করে।
    resample = getattr(Image, "Resampling", Image).LANCZOS

    try:
        img = Image.open(path).convert("RGBA")
        # ছবিটিকে size x size বর্গক্ষেত্রে ঠিকমতো fit/crop করে নেয়
        img = ImageOps.fit(img, (size, size), resample)

        # গোলাকার মাস্ক তৈরি (অ্যান্টি-অ্যালিয়াসিং সহ মসৃণ কিনারার জন্য
        # ৪ গুণ বড় সাইজে বৃত্ত এঁকে পরে ছোট করে আনা হচ্ছে)
        scale = 4
        mask = Image.new("L", (size * scale, size * scale), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size * scale, size * scale), fill=255)
        mask = mask.resize((size, size), resample)

        img.putalpha(mask)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        _log_logo_issue(f"[লোগো] ছবি প্রসেস করতে সমস্যা হয়েছে (path={path}): {e}")
        return None

# ----------------------------------------------------------------------------
# থিম / রঙ
# ----------------------------------------------------------------------------
BG = "#F4F6FB"
SIDEBAR_BG = "#FFFFFF"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E7EAF3"
PRIMARY = "#6C5CE7"
PRIMARY_DARK = "#5A4BD1"
PRIMARY_LIGHT = "#EEEBFF"
SECONDARY = "#00B894"
SECONDARY_DARK = "#00997A"
DANGER = "#E74C3C"
DANGER_DARK = "#C0392B"
MUTED = "#8B93A7"
TEXT_DARK = "#22262F"
CURRENT_BG = "#FFE9A8"
INCORRECT_BG = "#FFE0E0"
INCORRECT_FG = "#E74C3C"
CORRECT_FG = "#00B894"
PENDING_FG = "#A6ACBE"

UI_FONT = ("Segoe UI", 11)
UI_FONT_BOLD = ("Segoe UI", 11, "bold")

BN_FONT = ("Nirmala UI", 17)
BN_FONT_BOLD = ("Nirmala UI", 17, "bold")

EN_FONT = ("Consolas", 17)
EN_FONT_BOLD = ("Consolas", 17, "bold")

BIJOY_FONT = ("SutonnyMJ", 19)
BIJOY_FONT_BOLD = ("SutonnyMJ", 19, "bold")

DEFAULT_PARAGRAPHS_BANGLA = [
    "আমাদের দেশ বাংলাদেশ অনেক সুন্দর। এখানে ছয়টি ঋতু পালাক্রমে আসে। "
    "নদীমাতৃক এই দেশে মাঠভরা সবুজ ফসল আর নীল আকাশ মিলেমিশে থাকে। "
    "গ্রামের মানুষ সহজ সরল জীবনযাপন করে। শহরের জীবন কর্মব্যস্ত এবং দ্রুতগতির। "
    "সবার মাঝে ভালোবাসা আর সম্মান থাকলে সমাজ সুন্দর হয়। "
    "অভ্র কীবোর্ড দিয়ে বাংলা টাইপ করা এখন অনেক সহজ ও আনন্দদায়ক।",

    "প্রযুক্তির উন্নতির সাথে সাথে মানুষের জীবনযাত্রা অনেক বদলে গেছে। "
    "এখন ঘরে বসেই পৃথিবীর যেকোনো প্রান্তের খবর জানা যায়। "
    "কম্পিউটার আর মোবাইল ফোন আমাদের নিত্যদিনের সঙ্গী হয়ে উঠেছে। "
    "নিয়মিত অনুশীলন করলে যেকোনো দক্ষতা আয়ত্ত করা সম্ভব। "
    "টাইপিং অনুশীলনও ঠিক তেমনই, ধৈর্য ধরে চর্চা করলে গতি ও নির্ভুলতা দুটোই বাড়ে।",
]

DEFAULT_PARAGRAPHS_ENGLISH = [
    "The quick brown fox jumps over the lazy dog. Typing practice helps you build "
    "both speed and accuracy over time. The more consistently you practice, the "
    "more natural it becomes to find each key without looking down.",

    "Good typing habits start with proper posture and finger placement. Keep your "
    "wrists relaxed, your eyes on the screen, and your fingers resting lightly on "
    "the home row. Small, steady improvements each day add up to real progress.",

    "Technology has changed the way we communicate, work, and learn. A skilled "
    "typist can turn thoughts into text almost as fast as they can think, which "
    "makes practice a genuinely useful investment of your time.",
]

DEFAULT_PARAGRAPHS_BIJOY = []

MODES = {
    "bangla": {
        "key": "bangla",
        "label": "বাংলা",
        "sublabel": "অভ্র ফোনেটিক · ইউনিকোড",
        "icon": "🇧🇩",
        "font": BN_FONT,
        "font_bold": BN_FONT_BOLD,
        "data_file": os.path.join(BASE_DIR, "paragraphs.json"),
        "defaults": DEFAULT_PARAGRAPHS_BANGLA,
        "hint": "",
    },
    "english": {
        "key": "english",
        "label": "English",
        "sublabel": "Standard QWERTY layout",
        "icon": "🔤",
        "font": EN_FONT,
        "font_bold": EN_FONT_BOLD,
        "data_file": os.path.join(BASE_DIR, "paragraphs_english.json"),
        "defaults": DEFAULT_PARAGRAPHS_ENGLISH,
        "hint": "",
    },
    "bijoy": {
        "key": "bijoy",
        "label": "বিজয় কীবোর্ড",
        "sublabel": "ANSI ফন্ট (SutonnyMJ)",
        "icon": "⌨️",
        "font": BIJOY_FONT,
        "font_bold": BIJOY_FONT_BOLD,
        "data_file": os.path.join(BASE_DIR, "paragraphs_bijoy.json"),
        "defaults": DEFAULT_PARAGRAPHS_BIJOY,
        "hint": "⚠ বিজয় কীবোর্ড লেআউট সক্রিয় করে টাইপ করুন। এই মোডে প্যারাগ্রাফ দেখতে "
                "SutonnyMJ ফন্ট ইনস্টল থাকা প্রয়োজন। 'ডেটা ম্যানেজ' থেকে নিজের "
                "বিজয়-এ লেখা প্যারাগ্রাফ যোগ করুন।",
    },
}
MODE_ORDER = ["bangla", "english", "bijoy"]

# ----------------------------------------------------------------------------
# অভ্র ফোনেটিক হিন্ট (আনুমানিক) — বাংলা ইউনিকোড অক্ষর থেকে সম্ভাব্য ইংরেজি
# কী-স্ট্রোক অনুমান করার জন্য। এটা omicronlab-এর Avro Phonetic নিয়মের একটা
# সরলীকৃত সংস্করণ, তাই সবসময় ১০০% হুবহু মিলবে না — শুধু শেখার সহায়ক হিন্ট।
# ----------------------------------------------------------------------------
AVRO_MAP = {
    "অ": "o", "আ": "a", "ই": "i", "ঈ": "I", "উ": "u", "ঊ": "U",
    "ঋ": "rri", "এ": "e", "ঐ": "OI", "ও": "O", "ঔ": "OU",
    "ক": "k", "খ": "kh", "গ": "g", "ঘ": "gh", "ঙ": "Ng",
    "চ": "c", "ছ": "Ch", "জ": "j", "ঝ": "jh", "ঞ": "NG",
    "ট": "T", "ঠ": "Th", "ড": "D", "ঢ": "Dh", "ণ": "N",
    "ত": "t", "থ": "th", "দ": "d", "ধ": "dh", "ন": "n",
    "প": "p", "ফ": "ph", "ব": "b", "ভ": "bh", "ম": "m",
    "য": "z", "র": "r", "ল": "l", "শ": "sh", "ষ": "Sh", "স": "s", "হ": "h",
    "ড়": "r", "ঢ়": "rh", "য়": "y", "ৎ": "t",
    "ং": "ng", "ঃ": ":", "ঁ": "^",
    "া": "a", "ি": "i", "ী": "I", "ু": "u", "ূ": "U", "ৃ": "rri",
    "ে": "e", "ৈ": "OI", "ো": "O", "ৌ": "OU",
    "্": "",
    "০": "0", "১": "1", "২": "2", "৩": "3", "৪": "4",
    "৫": "5", "৬": "6", "৭": "7", "৮": "8", "৯": "9",
    "।": ".",
}


def bangla_word_to_avro_hint(word):
    """
    একটি বাংলা শব্দকে আনুমানিক অভ্র-ফোনেটিক (ইংরেজি) হিন্টে রূপান্তর করে।

    সাধারণ char-by-char ম্যাপিং যথেষ্ট না, কারণ বাংলা ব্যঞ্জনবর্ণের নিজস্ব
    (অন্তর্নিহিত) 'অ' স্বরধ্বনি থাকে যখন তার পরে কোনো কার (vowel sign) বা
    হসন্ত থাকে না — যেমন "পরিবর্তন" ঠিকভাবে লিখতে হলে প-র-ি-ব-র-্-ত-ন এর
    মাঝে সেই লুকানো 'o' যোগ করতে হয় (poriborton), নাহলে ভুল হিন্ট (pribrtn)
    তৈরি হয়। শব্দের একদম শেষ ব্যঞ্জনবর্ণে এই 'o' সাধারণত উচ্চারণে বাদ পড়ে
    (schwa deletion) — যেমন "কলম" → kolom, "poriborton" এর শেষ 'ন' → n,
    তাই সেটা আলাদাভাবে বাদ রাখা হয়েছে।
    """
    vowel_signs = set("ািীুূৃেৈোৌ")
    consonants = set("কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎ")
    hasant = "্"

    out = []
    i = 0
    n = len(word)
    while i < n:
        ch = word[i]
        if ch in consonants:
            out.append(AVRO_MAP.get(ch, ch))
            nxt = word[i + 1] if i + 1 < n else ""
            if nxt == hasant:
                i += 2  # হসন্ত নিজে কিছু যোগ করে না, শুধু পরের ব্যঞ্জনের সাথে যুক্ত হয়
                continue
            if nxt in vowel_signs:
                i += 1  # পরের কার নিজেই স্বরধ্বনি বহন করবে, তাই inherent 'o' লাগবে না
                continue
            is_word_final = (i == n - 1)
            if not is_word_final:
                out.append("o")
            i += 1
        else:
            out.append(AVRO_MAP.get(ch, ch))
            i += 1
    return "".join(out)




def load_paragraphs(mode_key):
    path = MODES[mode_key]["data_file"]
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
        except Exception:
            pass
    return list(MODES[mode_key]["defaults"])


def save_paragraphs(mode_key, paragraphs):
    path = MODES[mode_key]["data_file"]
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(paragraphs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("সংরক্ষণ ব্যর্থ", f"ডেটা সংরক্ষণ করা যায়নি: {e}")


# ----------------------------------------------------------------------------
# রিইউজেবল উইজেট
# ----------------------------------------------------------------------------
class HoverButton(tk.Button):
    """একটা সাধারণ Button, hover এ রঙ বদলায়।"""

    def __init__(self, master, bg, hover_bg, fg="white", **kwargs):
        super().__init__(master, bg=bg, fg=fg, activebackground=hover_bg,
                          activeforeground=fg, bd=0, relief="flat",
                          cursor="hand2", font=UI_FONT_BOLD,
                          highlightthickness=0, padx=16, pady=10, **kwargs)
        self._bg = bg
        self._hover_bg = hover_bg
        self.bind("<Enter>", lambda e: self.config(bg=self._hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))


class Card(tk.Frame):
    """হালকা বর্ডারসহ একটা সাদা কার্ড, hover এ সামান্য হাইলাইট হয়।"""

    def __init__(self, master, **kwargs):
        outer = kwargs.pop("outer_bg", BG)
        super().__init__(master, bg=CARD_BORDER, padx=1, pady=1, **kwargs)
        self.inner = tk.Frame(self, bg=CARD_BG)
        self.inner.pack(fill="both", expand=True)
        self._outer = outer

    def set_hover(self, enable):
        self.config(bg=PRIMARY if enable else CARD_BORDER)


# ----------------------------------------------------------------------------
# মূল অ্যাপ
# ----------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Typing Practice — বাংলা | English | বিজয়")
        self.configure(bg=BG)
        self.minsize(760, 560)

        # --- পূর্ণ স্ক্রিন (maximized) দিয়ে শুরু, ক্রস-প্ল্যাটফর্ম-সেফ ---
        self.fullscreen = False
        try:
            self.state("zoomed")
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)
            except tk.TclError:
                self.attributes("-fullscreen", True)
                self.fullscreen = True

        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.end_fullscreen)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Accent.Horizontal.TProgressbar",
                         troughcolor="#EDEFF7", background=PRIMARY,
                         bordercolor="#EDEFF7", lightcolor=PRIMARY, darkcolor=PRIMARY,
                         thickness=10)

        self.current_mode = "bangla"
        self.paragraphs = {key: load_paragraphs(key) for key in MODES}

        # --- circle logo (image.png থেকে) ---
        # self.logo_image রেফারেন্স ধরে না রাখলে Tkinter এটাকে গার্বেজ
        # কালেক্ট করে ফেলবে আর লোগো অদৃশ্য হয়ে যাবে — তাই controller-এই রাখা হলো
        self.logo_image = load_circular_logo(find_logo_path(), LOGO_SIZE)
        if self.logo_image is not None:
            try:
                self.iconphoto(True, self.logo_image)
            except tk.TclError:
                pass

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (HomePage, ManagePage, TypingPage):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("HomePage")

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def end_fullscreen(self, event=None):
        if self.fullscreen:
            self.fullscreen = False
            self.attributes("-fullscreen", False)
            try:
                self.state("zoomed")
            except tk.TclError:
                pass

    def show_frame(self, name, mode=None):
        if mode is not None:
            self.current_mode = mode
        frame = self.frames[name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()


# ----------------------------------------------------------------------------
# হোম পেজ
# ----------------------------------------------------------------------------
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(40, 8))

        if controller.logo_image is not None:
            tk.Label(
                header,
                image=controller.logo_image,
                bg=BG
            ).pack(pady=(0, 10))

            # Image-এর নিচে Notice
            notice_label = tk.Label(
                header,
                text="📢 নোটিশ: সফটওয়্যার টি রিপন অনেক পরিশ্রম করে তৈরি করেছে। অতএব এর নাম এবং ছবি মডিফাই এর মাধ্যমে পরিবর্তন করে নিচু মানুষিকতার পরিচয় দিবেন না। এটা সম্পুর্ন বিনামুল্যের সফটওয়্যার!",
                font=("Noto Sans Bengali", 11, "bold"),
                fg="#8B5E00",
                bg="#FFF3CD",
                padx=12,
                pady=8,
                wraplength=800,
                justify="center"
            )
            notice_label.pack(fill="x", padx=20, pady=(0, 10))

            title_text = "Typing Practice"

        else:
            title_text = "⌨️  Typing Practice"

        tk.Label(
            header,
            text=title_text,
            font=("Segoe UI", 30, "bold"),
            bg=BG,
            fg=TEXT_DARK
        ).pack()

        tk.Label(
            header,
            text="একটি মোড বেছে নিন এবং অনুশীলন শুরু করুন",
            font=("Segoe UI", 13),
            bg=BG,
            fg=MUTED
        ).pack(pady=(6, 0))     
        cards_wrap = tk.Frame(self, bg=BG)
        cards_wrap.pack(expand=True, pady=20)

        self.cards_wrap = cards_wrap
        for i, key in enumerate(MODE_ORDER):
            self.build_card(cards_wrap, key).grid(row=0, column=i, padx=16, pady=10, sticky="n")

        tk.Label(self, text="F11 = ফুলস্ক্রিন টগল   •   Esc = ফুলস্ক্রিন থেকে বের হন",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(side="bottom", pady=16)

    def build_card(self, parent, key):
        m = MODES[key]
        card = Card(parent, width=250, height=270)
        card.grid_propagate(False)
        card.pack_propagate(False)

        inner = card.inner
        tk.Label(inner, text=m["icon"], font=("Segoe UI Emoji", 40),
                 bg=CARD_BG).pack(pady=(28, 6))
        tk.Label(inner, text=m["label"], font=("Segoe UI", 16, "bold"),
                 bg=CARD_BG, fg=TEXT_DARK).pack()
        tk.Label(inner, text=m["sublabel"], font=("Segoe UI", 10),
                 bg=CARD_BG, fg=MUTED, wraplength=200, justify="center").pack(pady=(2, 18))

        HoverButton(inner, bg=PRIMARY, hover_bg=PRIMARY_DARK, text="শুরু করুন  ▶",
                    command=lambda k=key: self.controller.show_frame("TypingPage", mode=k)
                    ).pack(pady=(0, 8), padx=24, fill="x")

        manage_btn = tk.Button(
            inner, text="ডেটা ম্যানেজ করুন", font=("Segoe UI", 9, "underline"),
            bg=CARD_BG, fg=MUTED, bd=0, cursor="hand2", activebackground=CARD_BG,
            activeforeground=PRIMARY,
            command=lambda k=key: self.controller.show_frame("ManagePage", mode=k))
        manage_btn.pack()

        for widget in (card, inner):
            widget.bind("<Enter>", lambda e, c=card: c.set_hover(True))
            widget.bind("<Leave>", lambda e, c=card: c.set_hover(False))

        return card


# ----------------------------------------------------------------------------
# ম্যানেজ পেজ (তিনটা মোডের জন্যই একটাই পেজ, ট্যাব দিয়ে সুইচ হয়)
# ----------------------------------------------------------------------------
class ManagePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.mode = "bangla"

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=28, pady=(24, 10))
        HoverButton(top, bg="#E7EAF3", hover_bg="#D7DBEA", fg=TEXT_DARK,
                    text="←  হোম", command=lambda: controller.show_frame("HomePage")
                    ).pack(side="left")
        tk.Label(top, text="ডেটা ম্যানেজ করুন", font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TEXT_DARK).pack(side="left", padx=18)

        # --- মোড ট্যাব ---
        self.tabs_frame = tk.Frame(self, bg=BG)
        self.tabs_frame.pack(fill="x", padx=28, pady=(0, 14))
        self.tab_buttons = {}
        for key in MODE_ORDER:
            b = tk.Button(self.tabs_frame, text=f"{MODES[key]['icon']}  {MODES[key]['label']}",
                          font=UI_FONT_BOLD, bd=0, cursor="hand2", padx=18, pady=9,
                          command=lambda k=key: self.switch_mode(k))
            b.pack(side="left", padx=(0, 8))
            self.tab_buttons[key] = b

        body = Card(self, outer_bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 16))
        inner = body.inner
        inner.configure(padx=20, pady=20)

        row = tk.Frame(inner, bg=CARD_BG)
        row.pack(fill="both", expand=True)

        list_frame = tk.Frame(row, bg=CARD_BG)
        list_frame.pack(fill="both", expand=True, side="left", padx=(0, 14))
        tk.Label(list_frame, text="বিদ্যমান প্যারাগ্রাফ", font=UI_FONT_BOLD,
                 bg=CARD_BG, fg=TEXT_DARK).pack(anchor="w", pady=(0, 6))

        list_body = tk.Frame(list_frame, bg=CARD_BG)
        list_body.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(list_body)
        scrollbar.pack(side="right", fill="y")
        self.listbox = tk.Listbox(list_body, font=UI_FONT, yscrollcommand=scrollbar.set,
                                   selectbackground=PRIMARY_LIGHT, selectforeground=TEXT_DARK,
                                   bd=1, relief="solid", highlightthickness=0,
                                   activestyle="none")
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        HoverButton(list_frame, bg=DANGER, hover_bg=DANGER_DARK, text="মুছে ফেলুন",
                    command=self.delete_selected).pack(anchor="w", pady=(10, 0))

        add_frame = tk.Frame(row, bg=CARD_BG)
        add_frame.pack(fill="both", expand=True, side="left")
        tk.Label(add_frame, text="নতুন প্যারাগ্রাফ যোগ করুন", font=UI_FONT_BOLD,
                 bg=CARD_BG, fg=TEXT_DARK).pack(anchor="w", pady=(0, 6))
        self.hint_label = tk.Label(add_frame, text="", font=("Segoe UI", 9), bg=CARD_BG,
                                    fg=DANGER, wraplength=320, justify="left")
        self.hint_label.pack(anchor="w", pady=(0, 6))
        self.text_box = tk.Text(add_frame, height=7, wrap="word", bd=1, relief="solid",
                                 padx=8, pady=8)
        self.text_box.pack(fill="both", expand=True, pady=(0, 8))
        HoverButton(add_frame, bg=SECONDARY, hover_bg=SECONDARY_DARK, text="+ যোগ করুন",
                    command=self.add_paragraph).pack(anchor="e")

        self.switch_mode("bangla")

    def switch_mode(self, key):
        self.mode = key
        m = MODES[key]
        for k, b in self.tab_buttons.items():
            active = k == key
            b.config(bg=PRIMARY if active else "#E7EAF3",
                     fg="white" if active else TEXT_DARK,
                     activebackground=PRIMARY_DARK if active else "#D7DBEA",
                     activeforeground="white" if active else TEXT_DARK)
        self.listbox.config(font=m["font"])
        self.text_box.config(font=m["font"])
        self.hint_label.config(text=m["hint"])
        self.refresh_list()

    def on_show(self):
        self.switch_mode(self.controller.current_mode)

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for p in self.controller.paragraphs[self.mode]:
            preview = p.replace("\n", " ")[:60] + ("..." if len(p) > 60 else "")
            self.listbox.insert(tk.END, preview)

    def add_paragraph(self):
        text = self.text_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("খালি", "প্যারাগ্রাফ খালি রাখা যাবে না।")
            return
        self.controller.paragraphs[self.mode].append(text)
        save_paragraphs(self.mode, self.controller.paragraphs[self.mode])
        self.text_box.delete("1.0", tk.END)
        self.refresh_list()

    def delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("নির্বাচন করুন", "প্রথমে একটি প্যারাগ্রাফ নির্বাচন করুন।")
            return
        idx = sel[0]
        if messagebox.askyesno("নিশ্চিত করুন", "এই প্যারাগ্রাফটি মুছে ফেলতে চান?"):
            del self.controller.paragraphs[self.mode][idx]
            save_paragraphs(self.mode, self.controller.paragraphs[self.mode])
            self.refresh_list()


# ----------------------------------------------------------------------------
# টাইপিং পেজ
# ----------------------------------------------------------------------------
class TypingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.mode = "bangla"
        self.words = []
        self.start_time = None
        self.finished = False
        self.avro_raw = ""

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=28, pady=(22, 6))
        HoverButton(top, bg="#E7EAF3", hover_bg="#D7DBEA", fg=TEXT_DARK,
                    text="←  হোম", command=lambda: controller.show_frame("HomePage")
                    ).pack(side="left")
        self.title_label = tk.Label(top, text="", font=("Segoe UI", 18, "bold"),
                                     bg=BG, fg=TEXT_DARK)
        self.title_label.pack(side="left", padx=18)
        HoverButton(top, bg="#FDCB6E",
                    hover_bg="#F0B94D", fg=TEXT_DARK, text="⟳  নতুন প্যারাগ্রাফ",
                    command=self.new_paragraph).pack(side="right")

        self.hint_label = tk.Label(self, text="", font=("Segoe UI", 10), bg=BG,
                                    fg=DANGER, wraplength=900, justify="left")
        self.hint_label.pack(fill="x", padx=28)

        # --- প্যারাগ্রাফ কার্ড ---
        para_card = Card(self, outer_bg=BG)
        para_card.pack(fill="both", padx=28, pady=(12, 12))
        self.para_box = tk.Text(para_card.inner, height=8, wrap="word",
                                 bg=CARD_BG, relief="flat", padx=18, pady=18,
                                 state="disabled", bd=0, highlightthickness=0)
        self.para_box.pack(fill="both", expand=True)
        self.para_box.tag_configure("correct", foreground=CORRECT_FG)
        self.para_box.tag_configure("incorrect", foreground=INCORRECT_FG,
                                     background=INCORRECT_BG)
        self.para_box.tag_configure("current", background=CURRENT_BG)
        self.para_box.tag_configure("pending", foreground=PENDING_FG)

        tk.Label(self, text="এখানে টাইপ করুন:", font=UI_FONT_BOLD, bg=BG,
                 fg=TEXT_DARK).pack(anchor="w", padx=28)

        entry_card = Card(self, outer_bg=BG)
        entry_card.pack(fill="x", padx=28, pady=(6, 14))
        self.entry = tk.Text(entry_card.inner, height=4, wrap="word",
                              bg=CARD_BG, relief="flat", bd=0, padx=18, pady=14,
                              highlightthickness=0)
        self.entry.pack(fill="both", expand=True)
        self.entry.bind("<KeyPress>", self.on_key_press)

        # --- পরবর্তী শব্দের ইংরেজি টাইপিং হিন্ট (অভ্র/বিজয় মোডে) ---
        self.hint_bar = tk.Frame(self, bg=CARD_BORDER, padx=1, pady=1)
        hint_inner = tk.Frame(self.hint_bar, bg=CARD_BG)
        hint_inner.pack(fill="both", expand=True)

        hint_strip = tk.Frame(hint_inner, bg=PRIMARY, width=5)
        hint_strip.pack(side="left", fill="y")
        self.hint_strip = hint_strip

        hint_content = tk.Frame(hint_inner, bg=CARD_BG)
        hint_content.pack(side="left", fill="both", expand=True, padx=(14, 16), pady=10)

        self.hint_caption_label = tk.Label(hint_content, text="", font=("Segoe UI", 9),
                                            bg=CARD_BG, fg=MUTED, anchor="w")
        self.hint_caption_label.pack(anchor="w")
        self.hint_text_label = tk.Label(hint_content, text="", font=("Consolas", 15, "bold"),
                                         bg=CARD_BG, fg=PRIMARY_DARK, anchor="w",
                                         justify="left", wraplength=900)
        self.hint_text_label.pack(anchor="w", pady=(2, 0))

        # --- স্ট্যাটস ---
        self.stats_card = Card(self, outer_bg=BG)
        stats_card = self.stats_card
        stats_card.pack(fill="x", padx=28, pady=(0, 22))
        stats_inner = stats_card.inner
        stats_inner.configure(padx=20, pady=16)

        self.progress = ttk.Progressbar(stats_inner, style="Accent.Horizontal.TProgressbar",
                                         orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(0, 12))

        stats_row = tk.Frame(stats_inner, bg=CARD_BG)
        stats_row.pack(fill="x")
        self.stat_words = self._make_stat(stats_row, "📝", "শব্দ", "0 / 0")
        self.stat_correct = self._make_stat(stats_row, "✅", "সঠিক", "0")
        self.stat_acc = self._make_stat(stats_row, "🎯", "নির্ভুলতা", "100%")
        self.stat_wpm = self._make_stat(stats_row, "⚡", "গতি", "0 WPM")

    def _make_stat(self, parent, icon, label, value):
        box = tk.Frame(parent, bg=CARD_BG)
        box.pack(side="left", expand=True, fill="x")
        tk.Label(box, text=f"{icon}  {label}", font=("Segoe UI", 10), bg=CARD_BG,
                 fg=MUTED).pack(anchor="center")
        val_lbl = tk.Label(box, text=value, font=("Segoe UI", 15, "bold"), bg=CARD_BG,
                            fg=TEXT_DARK)
        val_lbl.pack(anchor="center")
        return val_lbl

    def on_show(self):
        self.mode = self.controller.current_mode
        m = MODES[self.mode]
        self.title_label.config(text=f"{m['icon']}  {m['label']} — টাইপিং প্র্যাকটিস")
        self.hint_label.config(text=m["hint"])
        self.para_box.config(font=m["font"])
        self.entry.config(font=m["font"])

        # অভ্র/বিজয় মোডে ইংরেজি-টাইপিং হিন্ট বার দেখানো হবে, English মোডে দরকার নেই
        if self.mode == "english":
            self.hint_bar.pack_forget()
        else:
            self.hint_bar.pack(fill="x", padx=28, pady=(0, 14), before=self.stats_card)

        self.new_paragraph()

    def new_paragraph(self):
        paragraphs = self.controller.paragraphs[self.mode]
        if not paragraphs:
            messagebox.showinfo("কোনো ডেটা নেই",
                                 "প্রথমে ডেটা ম্যানেজ থেকে কিছু প্যারাগ্রাফ যোগ করুন।")
            self.controller.show_frame("ManagePage", mode=self.mode)
            return
        text = random.choice(paragraphs)
        self.words = text.split()
        self.start_time = None
        self.finished = False
        self.entry.delete("1.0", tk.END)
        self.avro_raw = ""
        self.render_paragraph()
        self.progress.config(value=0)
        self.stat_words.config(text=f"0 / {len(self.words)}")
        self.stat_correct.config(text="0")
        self.stat_acc.config(text="100%")
        self.stat_wpm.config(text="0 WPM")
        self.update_hint([])
        self.entry.focus_set()

    def update_hint(self, typed_words):
        """বর্তমানে হাইলাইট করা (পরবর্তী) শব্দের ইংরেজি-টাইপিং হিন্ট আপডেট করে।"""
        if self.mode == "english" or not self.words:
            return
        idx = len(typed_words)

        if idx >= len(self.words):
            self.hint_strip.config(bg=SECONDARY)
            self.hint_caption_label.config(text="✓ সম্পন্ন")
            self.hint_text_label.config(text="পরবর্তী প্যারাগ্রাফে যান",
                                         font=("Segoe UI", 13, "bold"), fg=SECONDARY_DARK)
            return

        if self.mode == "bangla":
            hint = bangla_word_to_avro_hint(self.words[idx])
            self.hint_strip.config(bg=PRIMARY)
            self.hint_caption_label.config(text="🔤  পরবর্তী শব্দ — ইংরেজি হিন্ট (আনুমানিক)")
            self.hint_text_label.config(text=hint, font=("Consolas", 15, "bold"), fg=PRIMARY_DARK)
        elif self.mode == "bijoy":
            hint = "Hint অপশন বিজয়ের জন্য এখনো বানানো হয়নি; পরবর্তী আপডেটে যোগ হবে ইনশা-আল্লাহ।"
            self.hint_strip.config(bg=PRIMARY)
            self.hint_caption_label.config(text="🔤  পরবর্তী শব্দ — ইংরেজি হিন্ট (আনুমানিক)")
            self.hint_text_label.config(text=hint, font=("Consolas", 15, "bold"), fg=PRIMARY_DARK)
    def render_paragraph(self, typed_words=None, current_prefix=""):
        typed_words = typed_words or []
        self.para_box.config(state="normal")
        self.para_box.delete("1.0", tk.END)
        for i, w in enumerate(self.words):
            if i < len(typed_words):
                tag = "correct" if typed_words[i] == w else "incorrect"
            elif i == len(typed_words):
                if current_prefix and not w.startswith(current_prefix):
                    tag = "incorrect"
                else:
                    tag = "current"
            else:
                tag = "pending"
            self.para_box.insert(tk.END, w + " ", tag)
        self.para_box.config(state="disabled")
    def on_type(self, event=None):
        """English/Bijoy mode-এর typing validation এবং statistics update করে।"""

        raw = self.entry.get("1.0", "end-1c")

        if self.start_time is None and raw:
            self.start_time = time.time()

        # Space দিয়ে আলাদা হওয়া শব্দ
        ends_with_space = raw.endswith(" ")
        parts = raw.split()

        if ends_with_space:
            typed_words = parts
            current_prefix = ""
        else:
            typed_words = parts[:-1] if parts else []
            current_prefix = parts[-1] if parts else ""

        # Paragraph render
        self.render_paragraph(
            typed_words,
            current_prefix
        )

        self.update_hint(typed_words)

        # Correct word count
        correct = sum(
            1
            for i, word in enumerate(typed_words)
            if i < len(self.words) and word == self.words[i]
        )

        total_typed = len(typed_words)

        # Accuracy
        accuracy = (
            (correct / total_typed) * 100
            if total_typed > 0
            else 100
        )

        # WPM
        if self.start_time is not None:
            elapsed = max(time.time() - self.start_time, 0.01)
        else:
            elapsed = 0.01

        wpm = (total_typed / elapsed) * 60

        # Statistics update
        self.stat_words.config(
            text=f"{total_typed} / {len(self.words)}"
        )

        self.stat_correct.config(
            text=str(correct)
        )

        self.stat_acc.config(
            text=f"{accuracy:.0f}%"
        )

        self.stat_wpm.config(
            text=f"{wpm:.0f} WPM"
        )

        # Progress
        pct = (
            min(100, (total_typed / len(self.words)) * 100)
            if self.words
            else 0
        )

        self.progress.config(value=pct)

        # Finished
        if (
            not self.finished
            and total_typed >= len(self.words)
        ):
            self.finished = True

            final_correct = sum(
                1
                for i, word in enumerate(
                    typed_words[:len(self.words)]
                )
                if word == self.words[i]
            )

            final_acc = (
                final_correct / len(self.words) * 100
                if self.words
                else 100
            )

            self.after(
                150,
                lambda: messagebox.showinfo(
                    "সম্পন্ন হয়েছে!",
                    f"প্যারাগ্রাফ শেষ হয়েছে।\n"
                    f"নির্ভুলতা: {final_acc:.0f}%\n"
                    f"গতি: {wpm:.0f} WPM\n\n"
                    "'নতুন প্যারাগ্রাফ' চাপুন পরেরটির জন্য।"
                )
            )
    def on_key_press(self, event=None):
        # English / Bijoy mode
        if self.mode != "bangla":
            self.after_idle(self.on_type)
            return

        if event is None:
            return "break"

        key = event.keysym

        # Backspace
        if key == "BackSpace":
            if self.avro_raw:
                self.avro_raw = self.avro_raw[:-1]

        elif key == "Delete":
            return "break"

        elif key == "Return":
            self.avro_raw += "\n"

        elif key == "space":
            self.avro_raw += " "

        elif len(event.char) == 1 and event.char.isprintable():
            self.avro_raw += event.char

        else:
            return "break"

        try:
            converted = avro.parse(self.avro_raw)
        except Exception:
            converted = self.avro_raw

        self.entry.delete("1.0", tk.END)
        self.entry.insert("1.0", converted)
        self.entry.mark_set(tk.INSERT, tk.END)

        self.update_typing_stats(converted)

        return "break"
    def update_typing_stats(self, raw):
        if self.start_time is None and raw:
            self.start_time = time.time()

        ends_with_space = raw.endswith(" ")
        parts = raw.split()

        if ends_with_space:
            typed_words = parts
            current_prefix = ""
        else:
            typed_words = parts[:-1] if parts else []
            current_prefix = parts[-1] if parts else ""

        self.render_paragraph(typed_words, current_prefix)
        self.update_hint(typed_words)

        correct = sum(
            1 for i, w in enumerate(typed_words)
            if i < len(self.words) and w == self.words[i]
        )

        total_typed = len(typed_words)

        accuracy = (
            correct / total_typed * 100
            if total_typed else 100
        )

        if self.start_time is not None:
            elapsed = max(time.time() - self.start_time, 0.01)
        else:
            elapsed = 0.01

        wpm = (total_typed / elapsed) * 60

        self.stat_words.config(
            text=f"{total_typed} / {len(self.words)}"
        )

        self.stat_correct.config(
            text=str(correct)
        )

        self.stat_acc.config(
            text=f"{accuracy:.0f}%"
        )

        self.stat_wpm.config(
            text=f"{wpm:.0f} WPM"
        )

        pct = (
            min(100, (total_typed / len(self.words)) * 100)
            if self.words else 0
        )

        self.progress.config(value=pct)

        if not self.finished and total_typed >= len(self.words):
            self.finished = True

            final_correct = sum(
                1
                for i, w in enumerate(
                    typed_words[:len(self.words)]
                )
                if w == self.words[i]
            )

            final_acc = (
                final_correct / len(self.words) * 100
            )

            self.after(
                150,
                lambda: messagebox.showinfo(
                    "সম্পন্ন হয়েছে!",
                    f"প্যারাগ্রাফ শেষ হয়েছে।\n"
                    f"নির্ভুলতা: {final_acc:.0f}%\n"
                    f"গতি: {wpm:.0f} WPM\n\n"
                    "'নতুন প্যারাগ্রাফ' চাপুন পরেরটির জন্য।"
                )
            )
if __name__ == "__main__":
    app = App()
    app.mainloop()