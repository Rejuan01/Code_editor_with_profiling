import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.Qsci import QsciScintilla
app = QApplication(sys.argv)
ed = QsciScintilla()
ed.setMarginLineNumbers(0, True)
ed.setMarginWidth(0, "0000")
ed.setMarginType(1, QsciScintilla.TextMarginRightJustified)
ed.setMarginWidth(1, " 100.00% ")
ed.setText("Line 1\nLine 2\nLine 3")
ed.setMarginText(0, " 5.00% ", 0)
ed.setMarginText(1, " 12.00% ", 0)
ed.show()
sys.exit(0) # Just quit immediately, we just want to see if it crashes
