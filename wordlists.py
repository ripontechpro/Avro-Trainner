"""
wordlist/ folder access.  EVERY word, sentence and paragraph list lives in
wordlist/*.txt - nothing is stored inside the program.

Search order for a file:   <program folder>/wordlist/NAME   ->   bundled copy (PyInstaller)
Saving always writes to:   <program folder>/wordlist/NAME   (so edits survive restarts)

Line rules (all files):  UTF-8, one item per line, blank lines ignored,
                         a line starting with "# " (hash + space) or just "#" is a comment.
"""
import os
import sys

DIR_NAME = "wordlist"


def base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def user_dir():
    return os.path.join(base_dir(), DIR_NAME)


def bundled_dir():
    m = getattr(sys, "_MEIPASS", None)
    return os.path.join(m, DIR_NAME) if m else None


def find(name):
    for d in (user_dir(), bundled_dir()):
        if d and os.path.isfile(os.path.join(d, name)):
            return os.path.join(d, name)
    return None


def read_text(name):
    """Whole file text, or None when the file does not exist / cannot be read."""
    p = find(name)
    if not p:
        return None
    try:
        with open(p, encoding="utf-8-sig") as f:
            return f.read()
    except Exception:
        return None


def is_comment(line):
    return line == "#" or line.startswith("# ")


def parse_lines(text):
    out = []
    for raw in (text or "").splitlines():
        s = raw.strip()
        if s and not is_comment(s):
            out.append(s)
    return out


def parse_pairs(text):
    """'left = right' lines -> [(left, right)]; malformed lines are skipped."""
    out = []
    for s in parse_lines(text):
        if "=" in s:
            a, b = s.split("=", 1)
            a, b = a.strip(), b.strip()
            if a and b:
                out.append((a, b))
    return out


def lines(name):
    return parse_lines(read_text(name))


def pairs(name):
    return parse_pairs(read_text(name))


def write_text(name, text):
    """Atomic save into wordlist/. Returns (ok, message)."""
    try:
        os.makedirs(user_dir(), exist_ok=True)
        p = os.path.join(user_dir(), name)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(text if text.endswith("\n") or not text else text + "\n")
        os.replace(tmp, p)
        return True, p
    except Exception as e:
        return False, str(e)


# ---- registry used by the editor ------------------------------------------------
# kind: paragraph | lines | pairs      check: avro | bijoy | None
FILES = [
    dict(name="paragraphs_bangla.txt",  group="Paragraph practice", title="বাংলা paragraph",   kind="paragraph", check=None, font="bn"),
    dict(name="paragraphs_english.txt", group="Paragraph practice", title="English paragraph", kind="paragraph", check=None, font="mono"),
    dict(name="paragraphs_bijoy.txt",   group="Paragraph practice", title="বিজয় paragraph (ANSI)", kind="paragraph", check=None, font="bijoy"),
    dict(name="avro_conjuncts.txt",  group="Avro trainer", title="৪. যুক্তাক্ষর", kind="pairs", check="avro", font="bn"),
    dict(name="avro_words.txt",      group="Avro trainer", title="৫. শব্দ",       kind="pairs", check="avro", font="bn"),
    dict(name="avro_sentences.txt",  group="Avro trainer", title="৬. বাক্য",      kind="pairs", check="avro", font="bn"),
    dict(name="bijoy_vowels.txt",     group="Bijoy trainer", title="১. স্বরবর্ণ",     kind="lines", check="bijoy", font="bn"),
    dict(name="bijoy_consonants.txt", group="Bijoy trainer", title="২. ব্যঞ্জনবর্ণ", kind="lines", check="bijoy", font="bn"),
    dict(name="bijoy_kar.txt",        group="Bijoy trainer", title="৩. কার",         kind="lines", check="bijoy", font="bn"),
    dict(name="bijoy_conjuncts.txt",  group="Bijoy trainer", title="৪. যুক্তাক্ষর", kind="lines", check="bijoy", font="bn"),
    dict(name="bijoy_words.txt",      group="Bijoy trainer", title="৫. শব্দ",         kind="lines", check="bijoy", font="bn"),
    dict(name="bijoy_sentences.txt",  group="Bijoy trainer", title="৬. বাক্য",        kind="lines", check="bijoy", font="bn"),
    dict(name="bijoy_numbers.txt",    group="Bijoy trainer", title="৭. সংখ্যা",       kind="lines", check="bijoy", font="bn"),
    dict(name="english_words.txt",   group="English trainer", title="Word pool (L1.1-3.1)", kind="lines", check="token", font="mono"),
    dict(name="english_punct.txt",   group="English trainer", title="Words + punctuation (L4.1)", kind="lines", check="token", font="mono"),
    dict(name="english_numbers.txt", group="English trainer", title="Numbers & symbols (L4.1)", kind="lines", check="token", font="mono"),
    dict(name="english_short.txt",   group="English trainer", title="Short sentences (L5)", kind="lines", check="ascii", font="mono"),
    dict(name="english_long.txt",    group="English trainer", title="Long sentences (L5)", kind="lines", check="ascii", font="mono"),
    dict(name="english_mixed.txt",   group="English trainer", title="Numbers & punctuation sentences (L5)", kind="lines", check="ascii", font="mono"),
]
