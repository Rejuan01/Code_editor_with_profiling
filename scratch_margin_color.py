import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.Qsci import QsciScintilla
from PyQt5.QtGui import QColor

app = QApplication(sys.argv)
ed = QsciScintilla()

# Margin 0: Text (percentages)
ed.setMarginType(0, QsciScintilla.TextMarginRightJustified)
ed.setMarginWidth(0, " 100.00% ")

# Margin 1: Line numbers
ed.setMarginType(1, QsciScintilla.NumberMargin)
ed.setMarginLineNumbers(1, True)
ed.setMarginWidth(1, "0000 ")

# Define colors for styles 50 and 51
def set_style_color(style, hex_color):
    # hex_color like "#ff0000"
    c = QColor(hex_color)
    # Scintilla expects BGR for SCI_STYLESETFORE
    # Wait, QsciScintilla might intercept it if we use QColor?
    # No, SendScintilla with integer needs BGR, but let's see if there's a better way
    # Let's try SCI_STYLESETFORE with BGR
    bgr = (c.blue() << 16) | (c.green() << 8) | c.red()
    ed.SendScintilla(QsciScintilla.SCI_STYLESETFORE, style, bgr)
    ed.SendScintilla(QsciScintilla.SCI_STYLESETBACK, style, 0x1e1e1e) # dark back

set_style_color(50, "#00ff00") # Green
set_style_color(51, "#ff0000") # Red

ed.setText("Line 1\nLine 2\nLine 3")
ed.setMarginText(0, " 5.00% ", 50)
ed.setMarginText(1, " 99.00% ", 51)
ed.setMarginText(2, " 0.00% ", 50)
ed.show()

# Write to file instead of GUI loop for automation check
print("Script parsed successfully")
