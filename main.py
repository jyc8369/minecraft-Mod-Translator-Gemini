import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QProgressBar, QTextEdit, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
import logging
import json
import os
import zipfile
import shutil
import commentjson
import google.generativeai as genai

# Translator functions
def do_translate_gemini(target_json, api_key, logger=None):
    """
    Translates JSON data using Google Gemini AI.

    Args:
        target_json (str): JSON data as a string to be translated.
        api_key (str): Google Gemini API key.
        logger (logging.Logger): Optional logger for logging translation status.

    Returns:
        dict: Translated JSON data.
    """
    if logger:
        logger.info("Starting translation using Gemini AI.")

    # Configure Gemini API
    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        prompt = (
            "당신은 게임전문 번역가입니다. 번역하고자 하는 게임은 마인크래프트의 모드입니다.\n"
            "딕셔너리 형태의 데이터를 넘겨드릴겁니다. Key값은 그대로두고 Value값만 번역해야합니다.\n"
            "영어를 한글로 번역하는 작업이며, 답변은 Json 형태로만 주시면 됩니다.\n\n"
            f"{target_json}"
        )
        response = model.generate_content(prompt)
        
        if logger:
            logger.info("Translation request successfully sent to Gemini AI.")

        # Extract translated JSON string
        translated_json_str = response.text.strip()

        if logger:
            logger.debug(f"Raw translated response: {translated_json_str}")

        # Safely parse JSON result (assuming response is wrapped in ```json ... ```)
        # Gemini might return JSON directly, but check for code blocks
        if translated_json_str.startswith("```json"):
            translated_json_str = translated_json_str[7:-3].strip()
        elif translated_json_str.startswith("```"):
            translated_json_str = translated_json_str[3:-3].strip()

        translated_data = commentjson.loads(translated_json_str)
        if logger:
            logger.info("Translation successfully parsed into JSON format.")

        return translated_data

    except Exception as e:
        if logger:
            logger.error(f"An error occurred during translation: {e}")
        raise

# JarJsonProcessor functions
def jsonJarManager(jar_path: str, output_path: str = './translated', api_key: str = None, logger=None):
    """
    Processes JAR files in a directory, extracts and translates en_us.json to ko_kr.json.

    Args:
        jar_path (str): Path to the directory containing JAR files.
        output_path (str): Path to the directory where translated JAR files will be saved.
        api_key (str): Google Gemini API key.
        logger (logging.Logger): Optional logger for recording the process.

    Returns:
        None
    """
    temp_dir = Path('./temp')
    translated_dir = Path(output_path)

    # Ensure necessary directories exist
    temp_dir.mkdir(exist_ok=True)
    translated_dir.mkdir(exist_ok=True)

    mod_path = Path(jar_path)
    mod_list = mod_path.glob('*.jar')

    for mod_file in mod_list:
        if logger:
            logger.info(f"Processing {mod_file.name}...")

        mod_temp_dir = temp_dir / mod_file.stem
        try:
            # Extract JAR file contents
            with zipfile.ZipFile(mod_file, 'r') as jar:
                jar.extractall(mod_temp_dir)
                if logger:
                    logger.info(f"Extracted {mod_file.name} to {mod_temp_dir}")

            # Locate en_us.json file
            target_json_path = next(mod_temp_dir.rglob('en_us.json'), None)
            if not target_json_path:
                if logger:
                    logger.warning(f"en_us.json not found in {mod_file.name}")
                continue

            # Translate JSON content
            translated_data = None
            with target_json_path.open('r', encoding='utf-8') as json_file:
                original_data = commentjson.load(json_file)
                json_str = commentjson.dumps(original_data, ensure_ascii=False, indent=4)
                translated_data = do_translate_gemini(target_json=json_str, api_key=api_key, logger=logger)

            # Save translated data to ko_kr.json
            ko_kr_path = target_json_path.parent / 'ko_kr.json'
            with ko_kr_path.open('w', encoding='utf-8') as json_file:
                commentjson.dump(translated_data, json_file, ensure_ascii=False, indent=4)
            if logger:
                logger.info(f"Translated JSON saved to {ko_kr_path}")

            # Recompress JAR with translated JSON
            new_jar_file = translated_dir / f"{mod_file.stem}_modified.jar"
            shutil.make_archive(new_jar_file.with_suffix(''), 'zip', mod_temp_dir)
            final_jar_file = new_jar_file.with_suffix('.jar')
            shutil.move(f"{new_jar_file.with_suffix('.zip')}", final_jar_file)

            if logger:
                logger.info(f"Translated JAR created: {final_jar_file}")

        except Exception as e:
            if logger:
                logger.error(f"An error occurred while processing {mod_file.name}: {e}")
        finally:
            # Clean up temporary files
            shutil.rmtree(mod_temp_dir, ignore_errors=True)
            if logger:
                logger.info(f"Cleaned up temporary directory: {mod_temp_dir}")

# GUI Classes
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
            self.log_text.append("API 키가 저장되었습니다.")
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