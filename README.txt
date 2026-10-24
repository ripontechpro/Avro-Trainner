Ripon Typing Tutor v2.0  (PySide6)

Run      : pip install PySide6   ->   run.bat   (or: python ripon_typing_tutor.py)
EXE      : pip install pyinstaller  ->  exe.bat
Keys     : F11 fullscreen | Esc dashboard | Ctrl+Q quit | Ctrl+S save (editor)

WORDLIST (everything is a text file in wordlist/ - nothing is stored in the program)
  paragraphs_bangla.txt / paragraphs_english.txt / paragraphs_bijoy.txt   one paragraph per line
  avro_conjuncts.txt / avro_words.txt / avro_sentences.txt                 "বাংলা = avro key" per line
  bijoy_*.txt                                                              one Bangla item per line
  english_*.txt                                                            one item per line
Lines starting with "# " (hash + space) are comments.
Edit them with any editor, or inside the app:  Wordlist Editor (line numbers, find, validate, save).
After Save every trainer re-reads its lists immediately.
