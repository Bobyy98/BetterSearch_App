import sys
import os
import subprocess
import datetime
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget,
    QTableWidgetItem, QComboBox, QHeaderView, QMainWindow,
    QMenuBar, QMenu, QWidgetAction
)
from PyQt6.QtGui import QFont, QDesktopServices, QCursor, QAction
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal

# This function will help you get the correct path for dependencies after the app is packaged.
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores the path to the app
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Example usage:
chevron_svg = resource_path("assets/chevron-down.svg")
mft_path = resource_path("dependencies/mft.exe")


class SizeTableWidgetItem(QTableWidgetItem):
    def __init__(self, size_str):
        super().__init__(size_str)
        self.size_str = size_str
        self.size_value = self.convert_to_bytes(size_str)

    def convert_to_bytes(self, size_str):
        try:
            number, unit = size_str.split()
            number = float(number)
            unit = unit.upper()
            units = ["B", "KB", "MB", "GB", "TB", "PB"]
            if unit in units:
                return number * (1024 ** units.index(unit))
        except:
            return 0
        return 0

    def __lt__(self, other):
        if isinstance(other, SizeTableWidgetItem):
            return self.size_value < other.size_value
        return super().__lt__(other)


class SearchWorker(QThread):
    results_ready = pyqtSignal(list)

    def __init__(self, query, selected_filter, match_whole_word=False):
        super().__init__()
        self.query = query
        self.selected_filter = selected_filter
        self.match_whole_word = match_whole_word

    def run(self):
        if self.match_whole_word:
            pattern = rf'^.*\b{re.escape(self.query)}\b.*$'
            command = [mft_path, "-regex", pattern, "-size", "-dm"]
        else:
            command = [mft_path, self.query, "-size", "-dm"]

        result = subprocess.run(command, capture_output=True, text=True)
        parsed_results = self.parse_es_output(result.stdout)
        filtered = self.filter_files(parsed_results, self.selected_filter)
        grouped_results = self.group_and_sort_files(filtered)
        self.results_ready.emit(grouped_results)

    def parse_es_output(self, output):
        files = []
        lines = output.strip().split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("<DIR>"):
                match = re.match(r"<DIR>\s+(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\s+(.*)", line)
                if match:
                    date_modified = self.format_date(match.group(1))
                    path = match.group(2).strip()
                    files.append({
                        "name": os.path.basename(path),
                        "size": "-",
                        "date_modified": date_modified,
                        "path": path,
                        "is_folder": True
                    })
            else:
                match = re.match(r"([\d,]+)\s+(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\s+(.*)", line)
                if match:
                    size_raw = match.group(1).replace(",", "")
                    date_modified = self.format_date(match.group(2))
                    path = match.group(3).strip()
                    files.append({
                        "name": os.path.basename(path),
                        "size": self.format_size(size_raw),
                        "date_modified": date_modified,
                        "path": path,
                        "is_folder": False
                    })

        return files

    def format_size(self, bytes_str):
        try:
            size = int(bytes_str)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
            return f"{size:.2f} PB"
        except:
            return "-"

    def format_date(self, date_str):
        try:
            return datetime.datetime.strptime(date_str, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M")
        except:
            return date_str

    def filter_files(self, all_files, selected_filter):
        filtered_files = []
        ext_map = {
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
            "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "Documents": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".xlsx", ".xls", ".csv", ".pptx", ".ppt"],
            "Executables": [".exe", ".bat", ".msi", ".sh", ".app"],
            "Picture": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
            "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".mpeg", ".webm"]
        }

        for file_data in all_files:
            file_ext = os.path.splitext(file_data["name"])[1].lower()
            if selected_filter == "All":
                filtered_files.append(file_data)
            elif selected_filter == "Folder" and file_data["is_folder"]:
                filtered_files.append(file_data)
            elif file_ext in ext_map.get(selected_filter, []):
                filtered_files.append(file_data)

        return filtered_files

    def group_and_sort_files(self, files):
        folders = [file for file in files if file["is_folder"]]
        grouped_files = { "Popular": [], "Audio": [], "Documents": [], "Executables": [], "Video": [], "Others": [] }

        popular_extensions = [".exe", ".pdf", ".mp3", ".docx", ".jpg", ".mp4"]
        for file in files:
            if file["is_folder"]:
                continue
            ext = os.path.splitext(file["name"])[1].lower()
            if ext in popular_extensions:
                grouped_files["Popular"].append(file)
            elif ext in [".mp3", ".wav", ".flac"]:
                grouped_files["Audio"].append(file)
            elif ext in [".docx", ".txt", ".pdf"]:
                grouped_files["Documents"].append(file)
            elif ext in [".exe", ".bat"]:
                grouped_files["Executables"].append(file)
            elif ext in [".mp4", ".avi"]:
                grouped_files["Video"].append(file)
            else:
                grouped_files["Others"].append(file)

        for group in grouped_files.values():
            group.sort(key=lambda x: x["name"])

        result = sorted(folders, key=lambda x: x["name"])
        for group in ["Popular", "Audio", "Documents", "Executables", "Video", "Others"]:
            result.extend(grouped_files[group])

        return result


class BetterSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Better Search")
        self.setGeometry(100, 100, 900, 500)
        
        # Set window opacity to % (you can adjust the value between 0.0 and 1.0)
        self.setWindowOpacity(0.97)

        # Optional: For more control over translucency, you can set the background as transparent
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        self.selected_filter = "All"
        self.match_whole_word = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        menu_bar = self.menuBar()

        # File Menu
        self.file_menu = QMenu("File", self)
        self.file_menu.aboutToShow.connect(self.update_file_menu)
        menu_bar.addMenu(self.file_menu)

        # Other Menus
        for name in ["Edit", "View", "Settings", "Help"]:
            menu_bar.addMenu(name)

        # Search Menu
        self.search_menu = QMenu("Search", self)
        self.whole_word_action = QAction("Match Whole Word", self)
        self.whole_word_action.setCheckable(True)
        self.whole_word_action.triggered.connect(self.toggle_whole_word)
        self.search_menu.addAction(self.whole_word_action)
        menu_bar.addMenu(self.search_menu)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Type a filename to search...")
        self.search_entry.setFont(QFont("Arial", 12))

        self.search_entry.setStyleSheet("background-color: #FFFFFF; color: black; padding: 8px; border-radius: 5px;")

        self.search_entry.returnPressed.connect(self.search_files)

        search_btn = QPushButton("Search")
        search_btn.setFixedWidth(150)
        search_btn.setFixedHeight(37)
        search_btn.setStyleSheet("""
            background-color: #004fe1;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
        """)
        search_btn.clicked.connect(self.search_files)

        search_layout.addWidget(self.search_entry)
        search_layout.addWidget(search_btn)

        # Filter
        filter_layout = QHBoxLayout()
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems([
            "All", "Audio", "Compressed", "Documents",
            "Executables", "Folder", "Picture", "Video"
        ])
        self.filter_dropdown.setFixedWidth(150)
        self.filter_dropdown.setFixedHeight(30)
        self.filter_dropdown.currentIndexChanged.connect(self.update_filter)
        self.filter_dropdown.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 150);  # White with transparency
                color: black;
                border-radius: 8px;
                padding: 2px 10px;
                font-size: 13px;
            }
        
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid white;
            }
            
            QComboBox::down-arrow {
                image: url({svg_path.replace("\\", "/")});
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                border-radius: 6px;
                selection-background-color: #004fe1;
                selection-color: white;
                padding: 4px;
            }
        """)
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_dropdown)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Size", "Date Modified", "Path"])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 400)

        self.table.setStyleSheet("""
            background-color: rgba(41, 41, 41, 150);  # Dark gray with alpha
            color: white;
            border-radius: 10px;
            selection-background-color: #004fe1;
            selection-color: white;
        """)

        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.open_file)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        self.status = self.statusBar()
        self.status.setStyleSheet("background-color: #2B2B2B; color: #AAAAAA; padding: 4px;")
        self.status.showMessage("Ready.")

        main_layout.addLayout(search_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table)

    def toggle_whole_word(self):
        self.match_whole_word = self.whole_word_action.isChecked()
        self.search_files()

    def update_file_menu(self):
        self.file_menu.clear()
        index = self.table.currentRow()
        if index >= 0:
            file_path = self.table.item(index, 3).text()
            for name, func in [
                ("Open", lambda: self.open_file(index, 0)),
                ("Open Path", lambda: self.open_file_path(file_path)),
                ("Copy Path", lambda: self.copy_to_clipboard(file_path))
            ]:
                action = QWidgetAction(self)
                btn = QPushButton(name)
                btn.setFixedSize(200, 35)
                btn.setStyleSheet(self.menu_button_style())
                btn.clicked.connect(func)
                action.setDefaultWidget(btn)
                self.file_menu.addAction(action)

        exit_action = QWidgetAction(self)
        exit_btn = QPushButton("Exit")
        exit_btn.setFixedSize(200, 35)
        exit_btn.setStyleSheet(self.menu_button_style())
        exit_btn.clicked.connect(self.close)
        exit_action.setDefaultWidget(exit_btn)
        self.file_menu.addAction(exit_action)

    def menu_button_style(self):
        return """
        QPushButton {
            background-color: #1E1E1E;
            color: white;
            border: none;
            padding: 10px;
            font-size: 12px;
            text-align: left;
        }
        QPushButton:hover {
            background-color: black;
        }
        """

    def show_context_menu(self, pos):
        index = self.table.indexAt(pos).row()
        if index >= 0:
            path = self.table.item(index, 3).text()
            menu = QMenu(self)
            for name, func in [
                ("Open", lambda: self.open_file(index, 0)),
                ("Open Path", lambda: self.open_file_path(path)),
                ("Copy Path", lambda: self.copy_to_clipboard(path))
            ]:
                action = QAction(name, self)
                action.triggered.connect(func)
                menu.addAction(action)
            menu.exec(QCursor.pos())

    def open_file(self, row, column):
        path = self.table.item(row, 3).text()
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def open_file_path(self, path):
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))

    def copy_to_clipboard(self, path):
        QApplication.clipboard().setText(path)

    def update_filter(self):
        self.selected_filter = self.filter_dropdown.currentText()
        self.search_files()

    def search_files(self):
        query = self.search_entry.text().strip()
        if not query:
            return
        self.status.showMessage("Searching...")
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(0)
        self.worker = SearchWorker(query, self.selected_filter, self.match_whole_word)
        self.worker.results_ready.connect(self.update_results)
        self.worker.start()

    def update_results(self, results):
        self.table.setRowCount(len(results))
        for row, file in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(file["name"]))
            self.table.setItem(row, 1, SizeTableWidgetItem(file["size"]))
            self.table.setItem(row, 2, QTableWidgetItem(file["date_modified"]))
            self.table.setItem(row, 3, QTableWidgetItem(file["path"]))
        self.table.setSortingEnabled(True)
        self.status.showMessage(f"Found {len(results)} item(s).")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BetterSearchApp()
    window.show()
    sys.exit(app.exec())
