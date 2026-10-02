pyinstaller --onefile --windowed --name AvroTrainer avro_trainer.py
pyinstaller --onefile --windowed --name BijoyTrainer bijoy_trainer.py
pyinstaller --onefile --windowed --name EnglishTrainer english_trainer.py
pyinstaller --onefile --windowed --name TypingPractice --add-binary "dist/AvroTrainer.exe;." --add-binary "dist/BijoyTrainer.exe;." --add-binary "dist/EnglishTrainer.exe;." typing_practice.py