from PyQt5.Qsci import QsciScintilla, QsciLexerCPP
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QProcess
import os
import re

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
        
        # Margin 0: Percentages (Text Margin) - ON THE LEFT
        self.setMarginType(0, QsciScintilla.TextMargin)
        self.setMarginWidth(0, 0) # Hidden by default until requested
        
        # Margin 1: Line numbers - ON THE RIGHT
        self.setMarginType(1, QsciScintilla.NumberMargin)
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, "0000 ")
        
        self.setMarginsBackgroundColor(QColor("#1e1e1e"))
        self.setMarginsForegroundColor(QColor("#858585"))
        
        self.setup_margin_styles()
        
        # No border
        self.setFrameShape(QsciScintilla.NoFrame)

    def setup_margin_styles(self):
        # 6 shades for percentages: 0-2%, 2-6%, 6-10%, 10-15%, 15-20%, 20%+
        self.pct_colors = [
            (2.0, QColor("#28a745")),     # Green (0-2%)
            (6.0, QColor("#85c83b")),     # Lime (2-6%)
            (10.0, QColor("#e5c07b")),    # Yellow (6-10%)
            (15.0, QColor("#d19a66")),    # Orange (10-15%)
            (20.0, QColor("#be5046")),    # Dark Orange/Red (15-20%)
            (float('inf'), QColor("#e06c75")) # Red (20%+)
        ]
        
        for i, (_, color) in enumerate(self.pct_colors):
            style = 50 + i
            bgr = (color.blue() << 16) | (color.green() << 8) | color.red()
            self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, style, bgr)
            # Background same as margin background
            self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, style, 0x1e1e1e)
            # Explicitly set font to ensure visibility
            self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, style, b"Fira Code")
            self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, style, 10)
            
        # Style for instruction count (Style 60)
        self.inst_style = 60
        self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, self.inst_style, 0x858585)
        self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, self.inst_style, 0x1e1e1e)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, self.inst_style, b"Fira Code")
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, self.inst_style, 10)

        # Remove annotations
        self.setMarginWidth(0, 0)
        for i in range(self.lines()):
            self.SendScintilla(QsciScintilla.SCI_MARGINSETTEXT, i, b"")

class EditorTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def open_file(self, file_path):
        # Check if file is already open
        for i in range(self.count()):
            editor = self.widget(i)
            if hasattr(editor, 'file_path') and editor.file_path == file_path:
                self.setCurrentIndex(i)
                return
                
        # Open new file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_editor = CppEditor()
            new_editor.setText(content)
            new_editor.file_path = file_path
            
            file_name = os.path.basename(file_path)
            tab_index = self.addTab(new_editor, file_name)
            self.setCurrentIndex(tab_index)
            self.setTabToolTip(tab_index, file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")

    def close_tab(self, index):
        widget = self.widget(index)
        self.removeTab(index)
        if widget:
            widget.deleteLater()

    def save_file(self):
        current_tab_index = self.currentIndex()
        if current_tab_index != -1:
            editor = self.widget(current_tab_index)
            if hasattr(editor, 'file_path'):
                try:
                    with open(editor.file_path, 'w', encoding='utf-8') as f:
                        f.write(editor.text())
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")

    def get_current_file_path(self):
        current_tab_index = self.currentIndex()
        if current_tab_index != -1:
            editor = self.widget(current_tab_index)
            if hasattr(editor, 'file_path'):
                return editor.file_path
        return None

class MetricsPanel(QsciScintilla):
    def __init__(self, editor_tabs: EditorTabWidget, parent=None):
        super().__init__(parent)
        self.editor_tabs = editor_tabs
        
        # Hide all margins
        self.setMarginWidth(0, 0)
        self.setMarginWidth(1, 0)
        
        self.setReadOnly(True)
        self.setFrameShape(QsciScintilla.NoFrame)
        self.setPaper(QColor("#1e1e1e"))
        self.setColor(QColor("#858585"))
        
        font = QFont("Fira Code", 10)
        self.setFont(font)
        
        # Setup styles
        self.pct_colors = [
            (2.0, QColor("#28a745")),     # Green (0-2%)
            (6.0, QColor("#85c83b")),     # Lime (2-6%)
            (10.0, QColor("#e5c07b")),    # Yellow (6-10%)
            (15.0, QColor("#d19a66")),    # Orange (10-15%)
            (20.0, QColor("#be5046")),    # Dark Orange/Red (15-20%)
            (float('inf'), QColor("#e06c75")) # Red (20%+)
        ]
        
        for i, (_, color) in enumerate(self.pct_colors):
            style = 50 + i
            bgr = (color.blue() << 16) | (color.green() << 8) | color.red()
            self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, style, bgr)
            self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, style, 0x1e1e1e)
            self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, style, b"Fira Code")
            self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, style, 10)
            
        self.inst_style = 60
        self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, self.inst_style, 0x67A5E5) # Peach/Orange (BGR format)
        self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, self.inst_style, 0x1e1e1e)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, self.inst_style, b"Fira Code")
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, self.inst_style, 10)
        
        self.header_style = 70
        self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, self.header_style, 0xD6C85E) # Cyan (BGR format)
        self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, self.header_style, 0x1e1e1e)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, self.header_style, b"Fira Code")
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, self.header_style, 10)
        self.SendScintilla(QsciScintilla.SCI_STYLESETBOLD, self.header_style, True)
        
        # Disable vertical scrollbar, keep horizontal
        self.SendScintilla(QsciScintilla.SCI_SETVSCROLLBAR, 0)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 1)
        
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)
        self.current_data = None
        self.hide()
        
    def on_tab_changed(self, index):
        if hasattr(self, 'current_editor') and self.current_editor:
            try:
                self.current_editor.verticalScrollBar().valueChanged.disconnect(self.sync_scroll)
            except TypeError:
                pass
                
        if index == -1:
            self.hide()
            return
            
        editor = self.editor_tabs.widget(index)
        self.current_editor = editor
        
        editor.verticalScrollBar().valueChanged.connect(self.sync_scroll)
        self.sync_scroll(editor.verticalScrollBar().value())
        
        # If we have data for this file, show it
        if hasattr(editor, 'metrics_data') and editor.metrics_data:
            self.update_annotations(editor.metrics_data, editor.lines())
            self.show()
        else:
            self.hide()
            
    def sync_scroll(self, value):
        self.verticalScrollBar().setValue(value)
        
    def update_annotations(self, data, total_lines):
        all_metrics = set()
        for item in data:
            for k in item.keys():
                if k not in ("line", "percentage"):
                    all_metrics.add(k)
        
        preferred_order = ["raw_instructions", "branches_executed", "branch_misses", "l1_cache_misses", "llc_cache_misses", "Dr", "Dw", "D1mw", "DLmw", "I1mr", "ILmr"]
        sorted_keys = [k for k in preferred_order if k in all_metrics]
        sorted_keys += sorted(list(all_metrics - set(preferred_order)))
        
        col_widths = {}
        for k in sorted_keys:
            max_val = 0
            for item in data:
                v = item.get(k, 0)
                if isinstance(v, (int, float)) and v > max_val:
                    max_val = v
            col_widths[k] = max(len(k), len(f"{max_val:,}"))
            
        header1 = f" {'%':>6} "
        for k in sorted_keys:
            header1 += f"  {k:>{col_widths[k]}}"
            
        # We offset the data by 2 lines so it visually aligns with the code editor 
        # (which is pushed down by the tab bar)
        lines_text = [""] * (total_lines + 2)
        lines_text[0] = ""
        lines_text[1] = header1
        
        line_styles = {}
        line_styles[1] = (self.header_style, len(header1), 0, 0)
            
        for item in data:
            ln = item.get("line")
            if not ln or ln < 1 or ln > total_lines:
                continue
                
            pct = item.get("percentage", 0.0)
            
            style = 50
            for i, (threshold, _) in enumerate(self.pct_colors):
                if pct <= threshold:
                    style = 50 + i
                    break
            else:
                style = 50 + len(self.pct_colors) - 1
                
            pct_text = f" {pct:5.2f}%"
            
            metrics_text = ""
            for k in sorted_keys:
                val = item.get(k, 0)
                w = col_widths[k]
                val_str = f"{val:,}" if isinstance(val, int) else str(val)
                metrics_text += f"  {val_str:>{w}}"
            
            # Assign to line index (ln - 1 + 2 offset = ln + 1)
            lines_text[ln + 1] = pct_text + metrics_text
            line_styles[ln + 1] = (style, len(pct_text), self.inst_style, len(metrics_text))
            
        self.setReadOnly(False)
        self.setText("\n".join(lines_text))
        self.setReadOnly(True)
        
        # Apply styles per line
        for i in range(total_lines + 2):
            if i in line_styles:
                pos = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, i)
                s1, l1, s2, l2 = line_styles[i]
                
                self.SendScintilla(QsciScintilla.SCI_STARTSTYLING, pos, 0xFF)
                self.SendScintilla(QsciScintilla.SCI_SETSTYLING, l1, s1)
                if l2 > 0:
                    self.SendScintilla(QsciScintilla.SCI_SETSTYLING, l2, s2)



