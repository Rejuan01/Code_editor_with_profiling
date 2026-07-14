import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QAction, QSplitter, QTreeView, QFileSystemModel, 
                             QFileDialog, QMessageBox, QPushButton, QStackedWidget, QLabel, QTabWidget, QTextEdit, QToolBar)
from PyQt5.QtCore import Qt, QDir, QProcess, QSize
from PyQt5.QtGui import QFontDatabase, QFont, QIcon
from editor import CppEditor, EditorTabWidget, MetricsPanel
from terminal import TerminalWidget

class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Code Editor")
        self.resize(1024, 768)
        self.annot_process = None
        
        self.setup_ui()
        self.setup_menu()
        self.apply_dark_theme()

    def setup_ui(self):
        # Toolbar
        self.toolbar = self.addToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("background-color: #333333; border-bottom: 1px solid #252526;")
        
        self.annotate_btn = QPushButton("Annotate")
        self.annotate_btn.setCursor(Qt.PointingHandCursor)
        self.annotate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c; 
                color: white; 
                padding: 4px 12px; 
                border: none;
                border-radius: 2px;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        self.toolbar.addWidget(self.annotate_btn)

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
        self.explorer_btn = QPushButton("")
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'asset', 'explorer.png')
        self.explorer_btn.setIcon(QIcon(icon_path))
        self.explorer_btn.setIconSize(QSize(28, 28))
        self.explorer_btn.setObjectName("ExplorerBtn")
        self.explorer_btn.setFixedSize(40, 40)
        self.explorer_btn.setToolTip("Explorer")
        self.explorer_btn.setCursor(Qt.PointingHandCursor)
        self.explorer_btn.clicked.connect(self.toggle_explorer)
        activity_layout.addWidget(self.explorer_btn)
        
        main_layout.addWidget(self.activity_bar)
        
        # Splitter for sidebar and editor
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)
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
        
        # Explorer Container
        self.explorer_container = QWidget()
        self.explorer_container.setObjectName("ExplorerContainer")
        explorer_layout = QVBoxLayout(self.explorer_container)
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        explorer_layout.setSpacing(0)
        
        # Explorer Title
        self.explorer_title = QLabel("EXPLORER")
        self.explorer_title.setObjectName("ExplorerTitle")
        explorer_layout.addWidget(self.explorer_title)
        
        # Folder Header
        self.folder_header = QPushButton("NO FOLDER OPENED")
        self.folder_header.setObjectName("FolderHeader")
        self.folder_header.setCursor(Qt.PointingHandCursor)
        self.folder_header.clicked.connect(self.open_folder)
        explorer_layout.addWidget(self.folder_header)
        
        # Sidebar Stack for tree or empty state
        self.sidebar_stack = QStackedWidget()
        
        # Empty State
        self.empty_state = QWidget()
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignTop)
        empty_layout.setContentsMargins(20, 10, 20, 20)
        
        no_folder_label = QLabel("You have not yet opened a folder.")
        no_folder_label.setWordWrap(True)
        no_folder_label.setStyleSheet("color: #cccccc;")
        
        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.setObjectName("OpenFolderBtn")
        open_folder_btn.setCursor(Qt.PointingHandCursor)
        open_folder_btn.clicked.connect(self.open_folder)
        
        empty_layout.addWidget(no_folder_label)
        empty_layout.addWidget(open_folder_btn)
        
        self.sidebar_stack.addWidget(self.empty_state)
        self.sidebar_stack.addWidget(self.tree_view)
        
        explorer_layout.addWidget(self.sidebar_stack)
        
        self.explorer_container.hide()
        
        # Editor part (Tabs)
        self.tabs = EditorTabWidget()
        
        # Metrics panel (Left of code editor)
        self.metrics_panel = MetricsPanel(self.tabs)
        
        self.editor_splitter = QSplitter(Qt.Horizontal)
        self.editor_splitter.setHandleWidth(1)
        self.editor_splitter.addWidget(self.metrics_panel)
        self.editor_splitter.addWidget(self.tabs)
        self.editor_splitter.setSizes([300, 700])
        
        # Connect Annotate button
        self.annotate_btn.clicked.connect(self.run_annotation)
        
        # Right Side Layout Splitter (Editor on top, Terminal on bottom)
        self.right_splitter = QSplitter(Qt.Vertical)
        self.right_splitter.setHandleWidth(1)
        
        # Terminal Container
        self.terminal_container = QWidget()
        self.terminal_container.setObjectName("TerminalContainer")
        self.terminal_container.setMinimumHeight(100) # Prevents terminal from being squeezed too small
        term_layout = QVBoxLayout(self.terminal_container)
        term_layout.setContentsMargins(0, 0, 0, 0)
        term_layout.setSpacing(0)
        
        # Terminal Header
        self.terminal_header = QWidget()
        self.terminal_header.setObjectName("TerminalHeader")
        self.terminal_header.setFixedHeight(30)
        term_header_layout = QHBoxLayout(self.terminal_header)
        term_header_layout.setContentsMargins(15, 0, 10, 0)
        
        term_title = QLabel("TERMINAL")
        term_title.setStyleSheet("color: #bbbbbb; font-size: 11px; font-weight: normal;")
        
        close_term_btn = QPushButton("✕")
        close_term_btn.setObjectName("CloseTerminalBtn")
        close_term_btn.setFixedSize(20, 20)
        close_term_btn.setCursor(Qt.PointingHandCursor)
        close_term_btn.setToolTip("Close Terminal")
        close_term_btn.clicked.connect(self.hide_terminal)
        
        term_header_layout.addWidget(term_title)
        term_header_layout.addStretch()
        term_header_layout.addWidget(close_term_btn)
        
        # Terminal Widget
        self.terminal = TerminalWidget()
        
        term_layout.addWidget(self.terminal_header)
        term_layout.addWidget(self.terminal)
        
        self.right_splitter.addWidget(self.editor_splitter)
        self.right_splitter.addWidget(self.terminal_container)
        self.right_splitter.setSizes([600, 168])
        self.terminal_container.hide()
        
        # Add to splitter
        self.splitter.addWidget(self.explorer_container)
        self.splitter.addWidget(self.right_splitter)
        self.splitter.setSizes([250, 774]) # Default sizes

    def setup_menu(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        
        open_action = QAction("Open Folder...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_folder)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(lambda: self.tabs.save_file())
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Run Menu
        run_menu = menubar.addMenu("Run")
        
        build_action = QAction("Build", self)
        build_action.setShortcut("Ctrl+B")
        build_action.triggered.connect(self.build_code)
        
        run_action = QAction("Run Code", self)
        run_action.setShortcut("Ctrl+R")
        run_action.triggered.connect(self.run_code)
        
        run_menu.addAction(build_action)
        run_menu.addAction(run_action)
        
        # Terminal Menu
        terminal_menu = menubar.addMenu("Terminal")
        new_terminal_action = QAction("Toggle Terminal", self)
        new_terminal_action.setShortcut("Ctrl+`")
        new_terminal_action.triggered.connect(self.toggle_terminal)
        
        terminal_menu.addAction(new_terminal_action)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            folder_name = os.path.basename(os.path.normpath(folder_path))
            self.folder_header.setText(f"⌄ {folder_name.upper()}")
            self.model.setRootPath(folder_path)
            self.tree_view.setRootIndex(self.model.index(folder_path))
            self.sidebar_stack.setCurrentWidget(self.tree_view)
            self.explorer_container.show()
            self.terminal.set_directory(folder_path)

    def toggle_explorer(self):
        if self.explorer_container.isHidden():
            self.explorer_container.show()
        else:
            self.explorer_container.hide()

    def on_tree_double_clicked(self, index):
        file_path = self.model.filePath(index)
        if not self.model.isDir(index):
            self.tabs.open_file(file_path)

    def build_code(self):
        # Save before building
        self.tabs.save_file()
        
        file_path = self.tabs.get_current_file_path()
        if not file_path:
            QMessageBox.warning(self, "Warning", "No file is currently open to annotate.")
            return
            
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        file_name_no_ext, ext = os.path.splitext(file_name)
        
        if ext not in ['.cpp', '.c', '.cxx', '.cc']:
            QMessageBox.warning(self, "Warning", "Current file is not a C/C++ source file.")
            return
            
        out_file = os.path.join(file_dir, file_name_no_ext)
        cmd = f'g++ "{file_path}" -o "{out_file}"'
        
        if self.terminal_container.isHidden():
            self.terminal_container.show()
            self.terminal.setFocus()
        self.terminal.set_directory(file_dir)
        self.terminal.execute_command(cmd)

    def run_code(self):
        file_path = self.tabs.get_current_file_path()
        if not file_path:
            QMessageBox.warning(self, "Warning", "No file is currently open to run.")
            return
            
        file_dir = os.path.dirname(file_path)
        file_name_no_ext = os.path.splitext(os.path.basename(file_path))[0]
        out_file = os.path.join(file_dir, file_name_no_ext)
        
        if not os.path.exists(out_file):
            QMessageBox.warning(self, "Warning", "Executable not found. Please build the code first.")
            return
            
        cmd = f'./"{os.path.basename(out_file)}"'
        
        if self.terminal_container.isHidden():
            self.terminal_container.show()
            self.terminal.setFocus()
        self.terminal.set_directory(file_dir)
        self.terminal.execute_command(cmd)

    def hide_terminal(self):
        self.terminal_container.hide()

    def toggle_terminal(self):
        if self.terminal_container.isHidden():
            self.terminal_container.show()
            self.terminal.setFocus()
        else:
            self.terminal_container.hide()

    def run_annotation(self):
        file_path = self.tabs.get_current_file_path()
        if not file_path:
            QMessageBox.warning(self, "Warning", "No file is currently open.")
            return

        self.statusBar().showMessage("Running annotation scripts, please wait...")
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if self.annot_process is not None:
            self.annot_process.kill()
            
        self.annot_process = QProcess(self)
        self.annot_process.setWorkingDirectory(os.path.join(project_root, "src"))
        
        file_basename = os.path.basename(file_path)
        command = f'python3 annotate/run_script.py "{file_path}" && python3 annotate/backend.py "annotation.txt" "{file_basename}"'
        self.annot_process.start("bash", ["-c", command])
        
        self.annot_process.finished.connect(self.on_annotation_finished)

    def on_annotation_finished(self, exitCode, exitStatus):
        self.statusBar().clearMessage()
        if exitCode != 0:
            err = self.annot_process.readAllStandardError().data().decode()
            if err:
                QMessageBox.critical(self, "Error", f"Annotation script failed:\n{err}")

        output = self.annot_process.readAllStandardOutput().data().decode()
        
        if "=== FINAL PARSED JSON OUTPUT ===" in output:
            try:
                json_str = output.split("=== FINAL PARSED JSON OUTPUT ===")[1].strip()
                data = json.loads(json_str)
                
                current_tab_index = self.tabs.currentIndex()
                if current_tab_index != -1:
                    editor = self.tabs.widget(current_tab_index)
                    editor.metrics_data = data
                    self.metrics_panel.on_tab_changed(current_tab_index)
                        
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error parsing JSON output:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "Did not receive expected JSON from backend.")

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
            QTreeView::item {
                padding: 4px;
            }
            QTreeView::item:hover {
                background-color: #2a2d2e;
            }
            QTreeView::item:selected {
                background-color: #37373d;
                color: #ffffff;
            }
            #ExplorerContainer {
                background-color: #252526;
            }
            #ExplorerTitle {
                color: #bbbbbb;
                font-size: 11px;
                padding: 10px 20px;
                background-color: #252526;
            }
            #FolderHeader {
                text-align: left;
                padding: 5px 20px;
                border: none;
                font-weight: bold;
                font-size: 11px;
                color: #cccccc;
                background-color: #252526;
            }
            #FolderHeader:hover {
                background-color: #2a2d2e;
            }
            #OpenFolderBtn {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                padding: 6px 12px;
                border-radius: 2px;
                margin-top: 10px;
            }
            #OpenFolderBtn:hover {
                background-color: #1177bb;
            }
            #TerminalHeader {
                background-color: #252526;
                border-top: 1px solid #454545;
            }
            #CloseTerminalBtn {
                background-color: transparent;
                color: #cccccc;
                border: none;
                font-size: 14px;
            }
            #CloseTerminalBtn:hover {
                background-color: #505050;
                border-radius: 2px;
            }
            #SummaryContainer {
                background-color: #252526;
            }
            #SummaryHeader {
                background-color: #252526;
                border-bottom: 1px solid #454545;
            }
            #CloseSummaryBtn {
                background-color: transparent;
                color: #cccccc;
                border: none;
                font-size: 14px;
            }
            #CloseSummaryBtn:hover {
                background-color: #505050;
                border-radius: 2px;
            }
            QSplitter::handle {
                background-color: #252526;
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
            QScrollBar:horizontal {
                background: #1e1e1e;
                height: 14px;
            }
            QScrollBar::handle:horizontal {
                background: #424242;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 14px;
            }
            QScrollBar::handle:vertical {
                background: #424242;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QTabWidget::pane {
                border: 0;
                background-color: #1e1e1e;
            }
            QTabBar {
                qproperty-drawBase: 0;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #858585;
                padding: 8px 16px;
                border: none;
                border-right: 1px solid #252526;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
                border-top: 2px solid #007acc;
            }
            QTabBar::tab:hover:!selected {
                color: #cccccc;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load Fira Code Font
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_path = os.path.join(project_root, "fonts", "FiraCode-Regular.ttf")
    QFontDatabase.addApplicationFont(font_path)
    
    # Set app style to Fusion for better dark theme compatibility across OS
    app.setStyle("Fusion")
    window = CodeEditor()
    window.show()
    sys.exit(app.exec_())
