import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QAction, QSplitter, QTreeView, QFileSystemModel, 
                             QFileDialog, QMessageBox, QPushButton, QStackedWidget, QLabel)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QDir
from PyQt5.Qsci import QsciScintilla
from terminal import TerminalWidget
class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Code Editor")
        self.resize(1024, 768)
        
        self.setup_ui()
        self.setup_menu()
        self.apply_dark_theme()

    def setup_ui(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Activity Bar (Leftmost narrow bar)
        self.activity_bar = QWidget()
        self.activity_bar.setFixedWidth(50)
        self.activity_bar.setObjectName("ActivityBar")
        activity_layout = QVBoxLayout(self.activity_bar)
        activity_layout.setContentsMargins(0, 10, 0, 0)
        activity_layout.setAlignment(Qt.AlignTop)
        
        # Explorer toggle button
        self.explorer_btn = QPushButton("📁") # Using emoji for icon
        self.explorer_btn.setObjectName("ExplorerBtn")
        self.explorer_btn.setFixedSize(40, 40)
        self.explorer_btn.setToolTip("Explorer")
        self.explorer_btn.setCursor(Qt.PointingHandCursor)
        self.explorer_btn.clicked.connect(self.toggle_explorer)
        activity_layout.addWidget(self.explorer_btn)
        
        main_layout.addWidget(self.activity_bar)
        
        # Splitter for sidebar and editor
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # File System Model
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        
        # Tree View for sidebar
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setAnimated(False)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        # Hide size, type, date modified columns
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)
        self.tree_view.setHeaderHidden(True)
        
        # Double click to open file
        self.tree_view.doubleClicked.connect(self.on_tree_double_clicked)
        
        # Sidebar Stack
        self.sidebar_stack = QStackedWidget()
        
        self.no_folder_label = QLabel("No folder is selected")
        self.no_folder_label.setAlignment(Qt.AlignCenter)
        self.no_folder_label.setStyleSheet("color: #858585;")
        
        self.sidebar_stack.addWidget(self.no_folder_label)
        self.sidebar_stack.addWidget(self.tree_view)
        
        self.sidebar_stack.hide()
        
        # QScintilla editor
        self.editor = QsciScintilla()
        
        # Right Side Layout Splitter (Editor on top, Terminal on bottom)
        self.right_splitter = QSplitter(Qt.Vertical)
        
        # Terminal Widget
        self.terminal = TerminalWidget()
        
        self.right_splitter.addWidget(self.editor)
        self.right_splitter.addWidget(self.terminal)
        self.right_splitter.setSizes([600, 168])
        self.terminal.hide()
        
        # Add to splitter
        self.splitter.addWidget(self.sidebar_stack)
        self.splitter.addWidget(self.right_splitter)
        self.splitter.setSizes([250, 774]) # Default sizes
        
        # Basic font configuration
        font = self.editor.font()
        font.setFamily("Courier New")
        font.setPointSize(12)
        self.editor.setFont(font)
        
        # Editor Dark Theme Settings
        self.editor.setPaper(QColor("#1e1e1e"))
        self.editor.setColor(QColor("#d4d4d4"))
        self.editor.setCaretForegroundColor(QColor("#ffffff"))
        self.editor.setCaretLineVisible(True)
        self.editor.setCaretLineBackgroundColor(QColor("#2d2d30"))
        self.editor.setFoldMarginColors(QColor("#1e1e1e"), QColor("#1e1e1e"))
        
        # Line numbers
        self.editor.setMarginLineNumbers(0, True)
        self.editor.setMarginWidth(0, "0000")
        self.editor.setMarginsBackgroundColor(QColor("#1e1e1e"))
        self.editor.setMarginsForegroundColor(QColor("#858585"))
        
        # No border
        self.editor.setFrameShape(QsciScintilla.NoFrame)

    def setup_menu(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        open_action = QAction("Open Folder...", self)
        open_action.triggered.connect(self.open_folder)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Run Menu
        run_menu = menubar.addMenu("Run")
        run_action = QAction("Run Code", self)
        build_action = QAction("Build", self)
        
        run_menu.addAction(run_action)
        run_menu.addAction(build_action)
        
        # Terminal Menu
        terminal_menu = menubar.addMenu("Terminal")
        new_terminal_action = QAction("New Terminal", self)
        new_terminal_action.triggered.connect(self.toggle_terminal)
        
        terminal_menu.addAction(new_terminal_action)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            self.model.setRootPath(folder_path)
            self.tree_view.setRootIndex(self.model.index(folder_path))
            self.sidebar_stack.setCurrentWidget(self.tree_view)
            self.sidebar_stack.show()
            self.terminal.set_directory(folder_path)

    def toggle_explorer(self):
        if self.sidebar_stack.isHidden():
            self.sidebar_stack.show()
        else:
            self.sidebar_stack.hide()

    def on_tree_double_clicked(self, index):
        file_path = self.model.filePath(index)
        if not self.model.isDir(index):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.setText(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")

    def toggle_terminal(self):
        if self.terminal.isHidden():
            self.terminal.show()
            self.terminal.setFocus()
        else:
            self.terminal.hide()

    def apply_dark_theme(self):
        # App-wide dark theme stylesheet (VS Code inspired)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QMenuBar {
                background-color: #333333;
                color: #cccccc;
                font-size: 13px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #505050;
                color: #ffffff;
            }
            QMenu {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #454545;
            }
            QMenu::item {
                padding: 6px 30px 6px 20px;
            }
            QMenu::item:selected {
                background-color: #094771;
                color: #ffffff;
            }
            QTreeView {
                background-color: #252526;
                color: #cccccc;
                border: none;
            }
            QTreeView::item:selected {
                background-color: #37373d;
            }
            QSplitter::handle {
                background-color: #333333;
            }
            #ActivityBar {
                background-color: #333333;
                border-right: 1px solid #252526;
            }
            #ExplorerBtn {
                background-color: transparent;
                color: #cccccc;
                border: none;
                font-size: 20px;
            }
            #ExplorerBtn:hover {
                background-color: #505050;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Set app style to Fusion for better dark theme compatibility across OS
    app.setStyle("Fusion")
    window = CodeEditor()
    window.show()
    sys.exit(app.exec_())
