import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QProgressBar, QTextEdit, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
import logging
import json
import os

from JarJsonProcessor import jsonJarManager

class Worker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, jar_path, output_path, api_key):
        super().__init__()
        self.jar_path = jar_path
        self.output_path = output_path
        self.api_key = api_key

    def run(self):
        # 로거 설정 (GUI로 출력)
        class GuiHandler(logging.Handler):
            def emit(self, record):
                self.parent.progress.emit(self.format(record))

        logger = logging.getLogger('mod-translator')
        logger.setLevel(logging.INFO)
        handler = GuiHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        logger.addHandler(handler)
        handler.parent = self  # 부모 설정

        try:
            jsonJarManager(self.jar_path, output_path=self.output_path, api_key=self.api_key, logger=logger)
            self.progress.emit("번역 완료!")
        except Exception as e:
            self.progress.emit(f"오류: {str(e)}")
        finally:
            self.finished.emit()

class MinecraftTranslatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.config_file = 'config.json'
        self.load_config()
        self.initUI()

    def load_config(self):
        """Load API key from config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.saved_api_key = config.get('api_key', '')
            except:
                self.saved_api_key = ''
        else:
            self.saved_api_key = ''

    def save_config(self):
        """Save API key to config file."""
        config = {'api_key': self.api_input.text().strip()}
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            self.log_text.append(f"설정 저장 오류: {str(e)}")

    def initUI(self):
        self.setWindowTitle('Minecraft Mod Translator (Gemini)')
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout()

        # API 키 입력 및 저장
        api_layout = QHBoxLayout()
        api_label = QLabel('Gemini API Key:')
        self.api_input = QLineEdit()
        self.api_input.setText(self.saved_api_key)
        self.api_input.setPlaceholderText('API 키 입력')
        self.save_api_button = QPushButton('저장')
        self.save_api_button.clicked.connect(self.save_config)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        api_layout.addWidget(self.save_api_button)
        layout.addLayout(api_layout)

        # 입력 폴더 선택
        input_layout = QHBoxLayout()
        self.input_label = QLabel('번역할 JAR 파일이 있는 폴더를 선택하세요.')
        self.select_input_button = QPushButton('입력 폴더 선택')
        self.select_input_button.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.select_input_button)
        layout.addLayout(input_layout)

        # 출력 폴더 선택
        output_layout = QHBoxLayout()
        self.output_label = QLabel('번역된 파일을 저장할 폴더를 선택하세요.')
        self.select_output_button = QPushButton('출력 폴더 선택')
        self.select_output_button.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.select_output_button)
        layout.addLayout(output_layout)

        self.start_button = QPushButton('번역 시작')
        self.start_button.clicked.connect(self.start_translation)
        self.start_button.setEnabled(False)
        layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

        self.jar_path = None
        self.output_path = './translated'  # 기본 출력 폴더

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'JAR 파일 폴더 선택')
        if folder:
            self.jar_path = folder
            self.input_label.setText(f'입력 폴더: {folder}')
            self.check_start_enabled()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '출력 폴더 선택')
        if folder:
            self.output_path = folder
            self.output_label.setText(f'출력 폴더: {folder}')
            self.check_start_enabled()

    def check_start_enabled(self):
        if self.jar_path and self.output_path:
            self.start_button.setEnabled(True)

    def start_translation(self):
        api_key = self.api_input.text().strip()
        if not api_key:
            self.log_text.append("API 키를 입력하세요.")
            return
        if not self.jar_path:
            self.log_text.append("입력 폴더를 선택하세요.")
            return
        if not self.output_path:
            self.log_text.append("출력 폴더를 선택하세요.")
            return

        self.start_button.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # 불확정 진행 바

        self.worker = Worker(self.jar_path, self.output_path, api_key)
        self.worker.progress.connect(self.update_log)
        self.worker.finished.connect(self.translation_finished)
        self.worker.start()

    def update_log(self, message):
        self.log_text.append(message)

    def translation_finished(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.start_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MinecraftTranslatorGUI()
    gui.show()
    sys.exit(app.exec_())