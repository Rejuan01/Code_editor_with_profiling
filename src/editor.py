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
        self.setMarginType(0, QsciScintilla.TextMarginRightJustified)
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
        # 5 shades for percentages: 0-4%, 5-10%, 10-25%, 25-50%, 50-100%
        self.pct_colors = [
            (4.999, QColor("#28a745")), # Green (0-4%)
            (9.999, QColor("#85c83b")), # Lime (5-10%)
            (24.999, QColor("#e5c07b")), # Yellow (10-25%)
            (49.999, QColor("#d19a66")), # Orange (25-50%)
            (float('inf'), QColor("#e06c75")) # Red (50-100%)
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

    def show_percentages(self, pct_dict):
        # Set margin width to accommodate 100.00%
        self.setMarginWidth(0, " 100.00% ")
        self.clearMarginText()
        
        for ln, pct in pct_dict.items():
            # Determine color style based on threshold
            style = 50
            for i, (threshold, _) in enumerate(self.pct_colors):
                if pct <= threshold:
                    style = 50 + i
                    break
            else:
                style = 54
                
            self.setMarginText(ln - 1, f" {pct:.2f}% ", style)

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

class AnnotationPanel(QWidget):
    def __init__(self, editor_tabs: EditorTabWidget, parent=None):
        super().__init__(parent)
        self.editor_tabs = editor_tabs
        self.setup_ui()
        self.annot_process = None

    def setup_ui(self):
        self.setObjectName("SummaryContainer")
        summary_layout = QVBoxLayout(self)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(0)
        
        self.summary_header = QWidget()
        self.summary_header.setObjectName("SummaryHeader")
        self.summary_header.setFixedHeight(30)
        sum_header_layout = QHBoxLayout(self.summary_header)
        sum_header_layout.setContentsMargins(15, 0, 10, 0)
        
        sum_title = QLabel("SUMMARY")
        sum_title.setStyleSheet("color: #bbbbbb; font-size: 11px; font-weight: normal;")
        
        close_sum_btn = QPushButton("✕")
        close_sum_btn.setObjectName("CloseSummaryBtn")
        close_sum_btn.setFixedSize(20, 20)
        close_sum_btn.setCursor(Qt.PointingHandCursor)
        close_sum_btn.setToolTip("Close Summary")
        close_sum_btn.clicked.connect(self.hide)
        
        sum_header_layout.addWidget(sum_title)
        sum_header_layout.addStretch()
        sum_header_layout.addWidget(close_sum_btn)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("background-color: #0d1117; color: #abb2bf; border: none; padding: 10px; font-family: 'Courier New';")
        
        summary_layout.addWidget(self.summary_header)
        summary_layout.addWidget(self.summary_text)
        self.hide()

    def format_summary_text(self, text):
        html = "<div style='font-family: \"Fira Code\", \"Courier New\", monospace; font-size: 13px; line-height: 1.5; color: #abb2bf; padding: 5px;'>"
        color_key = "#61afef"    
        color_num = "#d19a66"    
        color_pct = "#e06c75"    
        color_paren = "#5c6370"  
        
        for line in text.splitlines():
            if not line.strip():
                html += "<br>"
                continue
                
            if ':' in line:
                key, rest = line.split(':', 1)
                formatted_line = f"<span style='color: {color_key}; font-weight: bold;'>{key}:</span>"
                paren_split = rest.split('(', 1)
                val_part = paren_split[0]
                paren_part = f"({paren_split[1]}" if len(paren_split) > 1 else ""
                
                def colorize_numbers(s):
                    chunks = s.split('&nbsp;')
                    for i, chunk in enumerate(chunks):
                        if not any(c.isdigit() for c in chunk):
                            continue
                        m = re.match(r'^(\(?)?([\d,.]+)(%?)(\)?\s*\w*)?$', chunk)
                        if m:
                            pre, num, pct, post = m.groups()
                            color = color_pct if pct else color_num
                            chunks[i] = f"{pre or ''}<span style='color: {color};'>{num}{pct}</span>{post or ''}"
                    return '&nbsp;'.join(chunks)
                
                val_part = val_part.replace(' ', '&nbsp;')
                val_part = colorize_numbers(val_part)
                
                if paren_part:
                    paren_part = paren_part.replace(' ', '&nbsp;')
                    paren_part = colorize_numbers(paren_part)
                    formatted_line += f"{val_part}<span style='color: {color_paren};'>{paren_part}</span>"
                else:
                    formatted_line += val_part
                    
                html += f"<div>{formatted_line}</div>\n"
            else:
                html += f"<div>{line.replace(' ', '&nbsp;')}</div>\n"
                
        html += "</div>"
        return html

    def run_annotation(self):
        file_path = self.editor_tabs.get_current_file_path()
        if not file_path:
            QMessageBox.warning(self, "Warning", "No file is currently open.")
            return

        self.summary_text.setHtml("<div style='color: #abb2bf; padding: 10px;'>Running annotation scripts, please wait...</div>")
        self.show()
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if self.annot_process is not None:
            self.annot_process.kill()
            
        self.annot_process = QProcess(self)
        self.annot_process.setWorkingDirectory(os.path.join(project_root, "src"))
        
        command = f'python3 annotate/main_script.py "{file_path}" && python3 annotate/reconstruction.py'
        self.annot_process.start("bash", ["-c", command])
        
        self.annot_process.finished.connect(self.on_annotation_finished)

    def on_annotation_finished(self, exitCode, exitStatus):
        if exitCode != 0:
            err = self.annot_process.readAllStandardError().data().decode()
            if err:
                QMessageBox.critical(self, "Error", f"Annotation script failed:\n{err}")

        # Parse standard output for percentages
        output = self.annot_process.readAllStandardOutput().data().decode()
        pct_dict = {}
        for line in output.splitlines():
            line = line.strip()
            if " -> " in line and line.endswith("%"):
                try:
                    parts = line.split(" -> ")
                    ln = int(parts[0])
                    pct = float(parts[1].rstrip("%"))
                    pct_dict[ln] = pct
                except ValueError:
                    pass
                    
        # Apply percentages to the active editor
        current_tab_index = self.editor_tabs.currentIndex()
        if current_tab_index != -1:
            editor = self.editor_tabs.widget(current_tab_index)
            if hasattr(editor, 'show_percentages'):
                editor.show_percentages(pct_dict)

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        summary_path = os.path.join(project_root, "src", "annotate", "summary.txt")
        
        if os.path.exists(summary_path):
            try:
                with open(summary_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                html_content = self.format_summary_text(content)
                self.summary_text.setHtml(html_content)
            except Exception as e:
                self.summary_text.setText(f"Error reading summary.txt:\n{str(e)}")
        else:
            self.summary_text.setText("summary.txt not found.")
            
        self.show()
