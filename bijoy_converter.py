# bijoy_converter.py
# Unicode Bangla word  ->  Bijoy keyboard key sequence (hint er jonno)
#
#   আমি   -> Ffmd   (যেমন)
#   ক্র   -> jz
#
# VERIFY চিহ্নিত key গুলো আপনার trainer-এর Bijoy chart-এর সাথে মিলিয়ে নিন।
# ভুল হলে শুধু নিচের table-এ ওই একটা লাইন বদলালেই হবে।

HASANT = "\u09CD"   # ্
NUKTA = "\u09BC"    # ়

# ---------------- ব্যঞ্জনবর্ণ ----------------
CONSONANT = {
    "ক": "j", "খ": "J", "গ": "o", "ঘ": "O", "ঙ": "q",
    "চ": "y", "ছ": "Y", "জ": "u", "ঝ": "U", "ঞ": "I",
    "ট": "t", "ঠ": "T", "ড": "e", "ঢ": "E", "ণ": "B",
    "ত": "k", "থ": "K", "দ": "l", "ধ": "L", "ন": "b",
    "প": "r", "ফ": "R", "ব": "h", "ভ": "H", "ম": "m",
    "য": "w", "র": "v", "ল": "V", "শ": "M", "ষ": "N",
    "স": "n", "হ": "i",
    "ড়": "p", "ঢ়": "P", "য়": "W",      # একক code point হিসেবে এলে
    "ৎ": "/",                            # VERIFY
}

# nukta দিয়ে তৈরি: ড + ় ইত্যাদি
NUKTA_MAP = {"ড": "p", "ঢ": "P", "য": "W"}

# ---------------- কার চিহ্ন (ব্যঞ্জনের পরে) ----------------
KAR = {
    "া": "f", "ি": "d", "ী": "D", "ু": "s", "ূ": "S", "ৃ": "a",
    "ে": "c", "ৈ": "C",
    "ো": "cf",      # ে + া   VERIFY
    "ৌ": "cX",      # ে + ৗ   VERIFY
    "ৗ": "X",       # VERIFY
}

# ---------------- স্বরবর্ণ (শব্দের শুরুতে/আলাদা) ----------------
VOWEL = {
    "অ": "F",       # VERIFY
    "আ": "Ff",      # VERIFY
    "ই": "d", "ঈ": "D", "উ": "s", "ঊ": "S",
    "ঋ": "A",       # VERIFY
    "এ": "c", "ঐ": "C", "ও": "x",
    "ঔ": "X",       # VERIFY
}

# ---------------- অন্যান্য ----------------
OTHER = {
    "ং": "Q",
    "ঃ": ":",       # VERIFY
    "ঁ": "&",       # VERIFY
    "।": "G",
    "০": "0", "১": "1", "২": "2", "৩": "3", "৪": "4",
    "৫": "5", "৬": "6", "৭": "7", "৮": "8", "৯": "9",
}

HASANT_KEY = "g"
RA_PHALA_KEY = "z"   # ্র
YA_PHALA_KEY = "Z"   # ্য

IGNORE = {"\u200c", "\u200d"}  # ZWNJ, ZWJ


def convert_bijoy_keys(text):
    """Unicode Bangla text -> Bijoy key sequence (string)."""
    return "".join(key for _, key in convert_with_parts(text))


def convert_with_parts(text):
    """[(bangla_part, keys), ...] ফেরত দেয় - ধাপে ধাপে hint দেখানোর জন্য।"""
    out = []
    i, n = 0, len(text or "")
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if ch in IGNORE:
            i += 1
        elif ch in NUKTA_MAP and nxt == NUKTA:
            out.append((ch + NUKTA, NUKTA_MAP[ch]))
            i += 2
        elif ch == HASANT:
            after = text[i + 2] if i + 2 < n else ""
            if nxt == "র" and after != HASANT:
                out.append((HASANT + "র", RA_PHALA_KEY))
                i += 2
            elif nxt == "য":
                out.append((HASANT + "য", YA_PHALA_KEY))
                i += 2
            else:
                out.append((HASANT, HASANT_KEY))
                i += 1
        elif ch in CONSONANT:
            out.append((ch, CONSONANT[ch]))
            i += 1
        elif ch in KAR:
            out.append((ch, KAR[ch]))
            i += 1
        elif ch in VOWEL:
            out.append((ch, VOWEL[ch]))
            i += 1
        elif ch in OTHER:
            out.append((ch, OTHER[ch]))
            i += 1
        else:                       # space, English, punctuation ইত্যাদি
            out.append((ch, ch))
            i += 1
    return out


def hint(text):
    """যেমন: 'আমি' -> 'আ(Ff) ম(m) ি(d)'"""
    return " ".join(f"{b}({k})" for b, k in convert_with_parts(text) if b.strip())


convert = convert_bijoy_keys


if __name__ == "__main__":
    for w in ["আমি", "কর্ম", "ক্রম", "বিদ্যা", "কোন", "বাংলাদেশ", "ড়", "পড়া"]:
        print(f"{w:10} -> {convert_bijoy_keys(w):12} | {hint(w)}")