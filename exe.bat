@echo off
rem One single EXE.  Needs:  pip install PySide6 pyinstaller
rem The wordlist folder is bundled inside the EXE AND is read/edited from the "wordlist" folder
rem placed next to the EXE (copy the wordlist folder next to RiponTypingTutor.exe to customise it).
pyinstaller --onefile --windowed --name RiponTypingTutor --icon logo.ico ^
  --add-data "logo.png;." --add-data "logo.ico;." --add-data "wordlist;wordlist" ^
  ripon_typing_tutor.py
