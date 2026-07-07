from PyQt5.Qsci import QsciScintilla, QsciLexerCPP
from PyQt5.QtGui import QColor, QFont

class CppEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Basic font configuration
        font = QFont("Fira Code", 10)
        self.setFont(font)
        
        # Editor Dark Theme Settings
        self.setPaper(QColor("#1e1e1e"))
        self.setColor(QColor("#d4d4d4"))
        self.setCaretForegroundColor(QColor("#ffffff"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#2d2d30"))
        self.setFoldMarginColors(QColor("#1e1e1e"), QColor("#1e1e1e"))
        
        # Syntax highlighting
        self.lexer = QsciLexerCPP()
        self.lexer.setDefaultFont(font)
        self.lexer.setDefaultPaper(QColor("#1e1e1e"))
        self.lexer.setDefaultColor(QColor("#d4d4d4"))
        
        # Setup specific colors for syntax and ensure font is applied
        styles = {
            QsciLexerCPP.Keyword: QColor("#569cd6"),
            QsciLexerCPP.KeywordSet2: QColor("#569cd6"),
            QsciLexerCPP.SingleQuotedString: QColor("#ce9178"),
            QsciLexerCPP.DoubleQuotedString: QColor("#ce9178"),
            QsciLexerCPP.RawString: QColor("#ce9178"),
            QsciLexerCPP.Comment: QColor("#6a9955"),
            QsciLexerCPP.CommentLine: QColor("#6a9955"),
            QsciLexerCPP.CommentDoc: QColor("#6a9955"),
            QsciLexerCPP.Number: QColor("#b5cea8"),
            QsciLexerCPP.PreProcessor: QColor("#c586c0"),
            QsciLexerCPP.Identifier: QColor("#9cdcfe"),
            QsciLexerCPP.Operator: QColor("#d4d4d4"),
        }
        
        for style, color in styles.items():
            self.lexer.setColor(color, style)
            self.lexer.setFont(font, style)
            
        self.setLexer(self.lexer)
        
        # Line numbers
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, "0000")
        self.setMarginsBackgroundColor(QColor("#1e1e1e"))
        self.setMarginsForegroundColor(QColor("#858585"))
        
        # No border
        self.setFrameShape(QsciScintilla.NoFrame)
