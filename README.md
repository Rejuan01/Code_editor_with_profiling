# C++ IDE with Performance Profiling

A lightweight, feature-rich Integrated Development Environment (IDE) for C++ development, built with Python, PyQt5, and QScintilla. The editor is designed with a modern dark aesthetic (inspired by VS Code and One Dark) and features a unique, built-in performance profiling pipeline.

## Key Features

- **Modern Editor Interface**: 
  - Multi-tab support for seamless switching between files.
  - Full C++ syntax highlighting and customizable themes.
  - Monospace font styling (`Fira Code`) for a clean coding experience.
- **Integrated File Explorer**: Navigate your project directory via a built-in file tree structure on the left panel.
- **Integrated Terminal**: A functional bottom-panel terminal that tracks the application's working directory, allowing you to run shell commands without leaving the IDE.
- **One-Click Build & Run**: Easily compile (`g++`) and execute your active C++ code with dedicated action buttons.
- **Advanced Performance Profiling (Annotation)**:
  - Leverages Valgrind (`Callgrind`/`Cachegrind`) to deeply analyze your C++ code.
  - **Summary Panel**: Opens a beautifully formatted, classic terminal-styled side panel displaying cache misses, branch mispredicts, instruction references, and data references.
  - **In-Editor Bottleneck Margins**: Automatically injects line-by-line performance metrics into the editor's left margin. The percentages are color-coded in a 5-shade gradient (from green to red) so you can instantly spot critical bottlenecks.

## Requirements

Ensure you have the following installed on your system:

- Python 3.x
- `PyQt5`
- `QScintilla` (for PyQt5)
- `g++` (GCC Compiler)
- `valgrind` (Specifically tools like `callgrind` and `cachegrind`)

## Project Structure

- `src/main.py`: The main entry point and controller of the IDE (handles the layout, toolbar, and integrates all components).
- `src/editor.py`: Contains the `CppEditor` (the Scintilla-based code editor widget), the `EditorTabWidget` for tab management, and the `AnnotationPanel` for the profiler summary view.
- `src/terminal.py`: Implements the interactive bottom terminal.
- `src/annotate/`: Directory containing the profiling scripts (`main_script.py`, `reconstruction.py`) that interface with Valgrind to parse execution data.

## Getting Started

1. Set up a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install the necessary Python packages:
   ```bash
   pip install PyQt5 PyQt5-Qsci
   ```

3. Run the application:
   ```bash
   python3 src/main.py
   ```
