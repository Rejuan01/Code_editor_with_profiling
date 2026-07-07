import os
import re
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtGui import QColor, QTextCursor, QFont

class TerminalWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                font-family: 'Courier New';
                font-size: 11pt;
                border: none;
                border-top: 1px solid #454545;
            }
        """)
        
        self.cwd = os.path.expanduser("~")
        self.is_running = False
        self.input_start_pos = 0
        
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.on_process_finished)
        
        self.print_prompt()
        
    def print_prompt(self):
        # Move to end
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        
        # Print colored path and prompt
        path = self.cwd
        home = os.path.expanduser("~")
        if path.startswith(home):
            path = "~" + path[len(home):]
            
        prompt = f"<br><span style='color: #8be9fd;'>{path}</span> <span style='color: #50fa7b;'>$</span> "
        if self.document().isEmpty():
            prompt = prompt.replace('<br>', '') # No newline if very first prompt
            
        self.insertHtml(prompt)
        
        # Insert a space to reset format
        self.insertPlainText(" ")
        
        # Update input start position
        self.input_start_pos = self.textCursor().position()
        self.ensureCursorVisible()

    def keyPressEvent(self, event):
        if self.is_running:
            return # Ignore input while command is running
            
        cursor = self.textCursor()
        
        # Prevent editing before input_start_pos
        if event.key() in (Qt.Key_Backspace, Qt.Key_Left):
            if cursor.position() <= self.input_start_pos:
                return
                
        # If selection goes into read-only area, cancel it
        if cursor.hasSelection():
            if cursor.selectionStart() < self.input_start_pos:
                cursor.clearSelection()
                self.setTextCursor(cursor)
                
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Move cursor to end to get full command
            cursor.movePosition(QTextCursor.End)
            cursor.setPosition(self.input_start_pos, QTextCursor.KeepAnchor)
            cmd = cursor.selectedText().strip()
            
            # Reset selection and move to end
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.insertPlainText("\n")
            
            self.execute_command(cmd)
            return
            
        # Ensure cursor is at or after input_start_pos when typing
        if cursor.position() < self.input_start_pos:
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)
            
        super().keyPressEvent(event)
        
    def set_directory(self, new_dir):
        if os.path.exists(new_dir) and os.path.isdir(new_dir):
            self.cwd = os.path.normpath(new_dir)
            if not self.is_running:
                self.insertPlainText("\n")
                self.print_prompt()

    def execute_command(self, cmd):
        if not cmd:
            self.print_prompt()
            return
            
        if cmd == 'clear':
            self.clear()
            self.print_prompt()
            return
            
        if cmd.startswith('cd '):
            new_dir = cmd[3:].strip()
            new_dir = os.path.expanduser(new_dir)
            if os.path.isabs(new_dir):
                target = new_dir
            else:
                target = os.path.join(self.cwd, new_dir)
                
            if os.path.exists(target) and os.path.isdir(target):
                self.cwd = os.path.normpath(target)
            else:
                self.append_output(f"cd: {new_dir}: No such file or directory\n", "#ff5555")
            
            self.print_prompt()
            return
            
        self.is_running = True
        self.process.setWorkingDirectory(self.cwd)
        self.process.start('bash', ['-c', cmd])
        
    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self.append_output(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.append_output(data, color="#ff5555")
        
    def on_process_finished(self):
        self.is_running = False
        self.print_prompt()
        
    def append_output(self, text, color="#cccccc"):
        # Move cursor to end
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        
        # Strip basic ANSI escape sequences
        text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
        
        text = text.replace('\n', '<br>')
        text = text.replace(' ', '&nbsp;')
        
        if text.replace('<br>', '').replace('&nbsp;', '').strip() != "":
            self.insertHtml(f"<span style='color:{color};'>{text}</span>")
            
        self.ensureCursorVisible()
        
    def closeEvent(self, event):
        self.process.kill()
        super().closeEvent(event)
