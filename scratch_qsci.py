from PyQt5.Qsci import QsciScintilla
for attr in dir(QsciScintilla):
    if 'Margin' in attr:
        print(attr)
