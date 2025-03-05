import os
import zipfile
import json
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, QLabel, QHBoxLayout, QLineEdit,
    QProgressBar
)


class IDExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_previous_dirs()

    def initUI(self):
        layout = QVBoxLayout()

        vanilla_layout = QHBoxLayout()
        self.btn_vanilla = QPushButton("Select Vanilla .JAR  ")
        self.btn_vanilla.clicked.connect(self.select_vanilla)
        vanilla_layout.addWidget(self.btn_vanilla)
        self.label_vanilla = QLineEdit()
        self.label_vanilla.setReadOnly(True)
        vanilla_layout.addWidget(self.label_vanilla)
        layout.addLayout(vanilla_layout)

        mods_layout = QHBoxLayout()
        self.btn_mods = QPushButton("Select Mods Folder")
        self.btn_mods.clicked.connect(self.select_mods)
        mods_layout.addWidget(self.btn_mods)
        self.label_mods = QLineEdit()
        self.label_mods.setReadOnly(True)
        mods_layout.addWidget(self.label_mods)
        layout.addLayout(mods_layout)

        self.btn_extract = QPushButton("Extract IDs")
        self.btn_extract.clicked.connect(self.extract_ids)
        layout.addWidget(self.btn_extract)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        layout.addWidget(self.text_output)

        self.btn_save = QPushButton("Save to File")
        self.btn_save.clicked.connect(self.save_to_file)
        layout.addWidget(self.btn_save)

        self.setLayout(layout)
        self.setWindowTitle("Minecraft IDs Extractor")
        self.setGeometry(100, 100, 600, 400)

        self.vanilla_jar = None
        self.mods_folder = None
        self.saved_file = None

    def load_previous_dirs(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                data = json.load(f)
                self.vanilla_jar = data.get("vanilla_jar")
                self.mods_folder = data.get("mods_folder")
                if self.vanilla_jar:
                    self.label_vanilla.setText(self.vanilla_jar)
                if self.mods_folder:
                    self.label_mods.setText(self.mods_folder)

    def save_dirs(self):
        data = {"vanilla_jar": self.vanilla_jar, "mods_folder": self.mods_folder}
        with open("last_dirs.json", "w") as f:
            json.dump(data, f)

    def select_vanilla(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Vanilla JAR", "", "JAR Files (*.jar)")
        if file:
            self.vanilla_jar = file
            self.label_vanilla.setText(file)
            self.save_dirs()

    def select_mods(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mods Folder")
        if folder:
            self.mods_folder = folder
            self.label_mods.setText(folder)
            self.save_dirs()

    def extract_ids(self):
        ids = set()
        total_files = 1
        processed_files = 0

        if self.vanilla_jar:
            total_files += 1

        if self.mods_folder:
            total_files += len([f for f in os.listdir(self.mods_folder) if f.endswith(".jar")])

        if self.vanilla_jar:
            ids.update(self.extract_from_jar(self.vanilla_jar, "minecraft"))
            processed_files += 1
            self.progress_bar.setValue(int((processed_files / total_files) * 100))

        if self.mods_folder:
            for filename in os.listdir(self.mods_folder):
                if filename.endswith(".jar"):
                    modid = filename.split("-")[0]
                    mod_jar_path = os.path.join(self.mods_folder, filename)
                    ids.update(self.extract_from_jar(mod_jar_path, modid))
                    processed_files += 1
                    self.progress_bar.setValue(int((processed_files / total_files) * 100))

        self.text_output.setText("\n".join(sorted(ids)))
        self.progress_bar.setValue(100)

    def extract_from_jar(self, jar_path, default_modid):
        ids = set()
        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                for file in jar.namelist():
                    if file.startswith("assets/") and file.endswith(".json"):
                        parts = file.split("/")
                        if "models" in parts and "item" in parts:
                            item_name = parts[-1].replace(".json", "")
                            if not re.search(r'\d', item_name):
                                formatted_name = f"{default_modid}:{item_name}"
                                ids.add(formatted_name)
        except Exception as e:
            print(f"Error reading {jar_path}: {e}")
        return ids

    def save_to_file(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save Item IDs", "", "Text Files (*.txt)")
        if file:
            with open(file, "w") as f:
                f.write(self.text_output.toPlainText())
            self.saved_file = file


if __name__ == "__main__":
    app = QApplication([])
    window = IDExtractor()
    window.show()
    app.exec()
