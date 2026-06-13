from __future__ import annotations

import json
import logging
import threading
import shutil
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

from modules.config import read_config, write_config
from modules.find_json import find_json
from modules.i18n import DEFAULT_UI_LANG, SUPPORTED_UI_LANGS, normalize_ui_lang, tr
from modules.unzip_jar import unzip_jar
from modules.zip_jar import zip_jar

PROJECT_ROOT = Path(__file__).resolve().parent
WORK_ROOT = PROJECT_ROOT / "work"
DEFAULT_INPUT_LANG = "en_us"
DEFAULT_OUTPUT_LANG = "ko_kr"
SUPPORTED_LANGS = [
    "en_us",
    "ko_kr",
    "ja_jp",
    "zh_cn",
    "ru_ru",
    "de_de",
    "fr_fr",
    "es_es",
]


class GUILogHandler(logging.Handler):
    def __init__(self, log_window: "LogWindow") -> None:
        super().__init__()
        self._log_window = log_window

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._log_window.append(msg, record.levelname)
        except Exception:
            self.handleError(record)


class LogWindow(ctk.CTkToplevel):
    _TAG_COLORS = {
        "INFO": "#a8d8a8",
        "WARNING": "#f6d365",
        "ERROR": "#ff7979",
    }

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)
        self._ui_lang = getattr(master, "_ui_lang", DEFAULT_UI_LANG)
        self.title(tr("log_window_title", self._ui_lang))
        self.geometry("600x400")
        self.protocol("WM_DELETE_WINDOW", self.hide)
        self._build_ui()
        self.withdraw()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._textbox = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self._textbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=(8, 4))

        inner: tk.Text = self._textbox._textbox
        for level, color in self._TAG_COLORS.items():
            inner.tag_config(level, foreground=color)

        self._btn_save = ctk.CTkButton(self, text=tr("log_save_button", self._ui_lang), command=self.save_log)
        self._btn_save.grid(
            row=1, column=0, sticky="ew", padx=8, pady=(0, 8)
        )
        self._btn_clear = ctk.CTkButton(self, text=tr("log_clear_button", self._ui_lang), fg_color="gray40", command=self.clear)
        self._btn_clear.grid(
            row=1, column=1, sticky="ew", padx=(0, 8), pady=(0, 8)
        )

    def set_language(self, ui_lang: str) -> None:
        self._ui_lang = ui_lang
        self.title(tr("log_window_title", self._ui_lang))
        self._btn_save.configure(text=tr("log_save_button", self._ui_lang))
        self._btn_clear.configure(text=tr("log_clear_button", self._ui_lang))

    def show(self) -> None:
        self.deiconify()
        self.lift()

    def hide(self) -> None:
        self.withdraw()

    def append(self, message: str, level: str = "INFO") -> None:
        def _update() -> None:
            self._textbox.configure(state="normal")
            inner: tk.Text = self._textbox._textbox
            tag = level if level in self._TAG_COLORS else "INFO"
            inner.insert("end", message + "\n", tag)
            self._textbox.configure(state="disabled")
            self._textbox.see("end")

        self.after(0, _update)

    def save_log(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")],
            title="로그 저장",
        )
        if not path:
            return
        content = self._textbox._textbox.get("1.0", "end")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def clear(self) -> None:
        self._textbox.configure(state="normal")
        self._textbox._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")


class ProgressPanel(ctk.CTkFrame):
    def __init__(self, master, ui_lang: str = DEFAULT_UI_LANG, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._ui_lang = normalize_ui_lang(ui_lang)
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self._lbl_jar = ctk.CTkLabel(self, text=tr("waiting", self._ui_lang), anchor="w")
        self._lbl_jar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))

        self._lbl_total = ctk.CTkLabel(self, text=f"{tr('total_progress', self._ui_lang)}  0%", anchor="w")
        self._lbl_total.grid(row=1, column=0, sticky="ew", padx=8, pady=(6, 0))
        self._bar_total = ctk.CTkProgressBar(self)
        self._bar_total.set(0)
        self._bar_total.grid(row=2, column=0, sticky="ew", padx=8, pady=(2, 0))

        self._lbl_current = ctk.CTkLabel(self, text=f"{tr('current_progress', self._ui_lang)}  0%", anchor="w")
        self._lbl_current.grid(row=3, column=0, sticky="ew", padx=8, pady=(6, 0))
        self._bar_current = ctk.CTkProgressBar(self)
        self._bar_current.set(0)
        self._bar_current.grid(row=4, column=0, sticky="ew", padx=8, pady=(2, 8))

    def set_jar_name(self, name: str) -> None:
        self._lbl_jar.configure(text=name)

    def set_total(self, value: float) -> None:
        self._bar_total.set(value)
        self._lbl_total.configure(text=f"{tr('total_progress', self._ui_lang)}  {int(value * 100)}%")

    def set_current(self, value: float) -> None:
        self._bar_current.set(value)
        self._lbl_current.configure(text=f"{tr('current_progress', self._ui_lang)}  {int(value * 100)}%")

    def reset(self) -> None:
        self.set_jar_name(tr("waiting", self._ui_lang))
        self.set_total(0)
        self.set_current(0)

    def set_language(self, ui_lang: str) -> None:
        self._ui_lang = normalize_ui_lang(ui_lang)
        self._lbl_jar.configure(text=tr("waiting", self._ui_lang))
        self._lbl_total.configure(text=f"{tr('total_progress', self._ui_lang)}  0%")
        self._lbl_current.configure(text=f"{tr('current_progress', self._ui_lang)}  0%")
        self._bar_total.set(0)
        self._bar_current.set(0)

    def refresh_texts(self) -> None:
        self._lbl_jar.configure(text=tr("waiting", self._ui_lang))
        self._lbl_total.configure(text=f"{tr('total_progress', self._ui_lang)}  {int(self._bar_total.get() * 100)}%")
        self._lbl_current.configure(text=f"{tr('current_progress', self._ui_lang)}  {int(self._bar_current.get() * 100)}%")


class ModListPanel(ctk.CTkFrame):
    _STATE_COLORS = {
        "idle": ("gray60", "gray30"),
        "running": ("#3a7ebf", "#1f538d"),
        "done": ("#2d936c", "#1a6b4a"),
        "failed": ("#c0392b", "#922b21"),
    }
    _STATE_PREFIX = {"idle": "", "running": "", "done": "✓ ", "failed": ""}

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._items: dict[str, ctk.CTkLabel] = {}
        self._states: dict[str, str] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._title_label = ctk.CTkLabel(self, text=tr("mod_list", getattr(self.master, "_ui_lang", DEFAULT_UI_LANG)), anchor="w")
        self._title_label.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 2))
        self._scroll = ctk.CTkScrollableFrame(self, label_text="")
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._scroll.grid_columnconfigure(0, weight=1)

    def set_files(self, filenames: list[str]) -> None:
        for widget in self._scroll.winfo_children():
            widget.destroy()
        self._items.clear()
        self._states.clear()
        for name in sorted(filenames):
            label = ctk.CTkLabel(self._scroll, text=name, anchor="w")
            label.grid(sticky="ew", padx=4, pady=1)
            self._items[name] = label
            self._states[name] = "idle"
            self._apply_color(name)

    def set_state(self, filename: str, state: str) -> None:
        if filename not in self._items:
            return
        self._states[filename] = state
        self._apply_color(filename)

    def _apply_color(self, filename: str) -> None:
        state = self._states.get(filename, "idle")
        colors = self._STATE_COLORS[state]
        prefix = self._STATE_PREFIX[state]
        self._items[filename].configure(text=f"{prefix}{filename}", text_color=colors)

    def set_title(self, text: str) -> None:
        self._title_label.configure(text=text)


class ResultDialog(ctk.CTkToplevel):
    def __init__(self, master, success: int, failures: list[tuple[str, str]]) -> None:
        super().__init__(master)
        self._ui_lang = getattr(master, "_ui_lang", DEFAULT_UI_LANG)
        self.title(tr("result_title", self._ui_lang))
        self.resizable(False, False)
        self.grab_set()
        self._build_ui(success, failures)
        self._center(master)

    def _build_ui(self, success: int, failures: list[tuple[str, str]]) -> None:
        pad = {"padx": 24, "pady": 8}
        ctk.CTkLabel(self, text=tr("result_done", self._ui_lang), font=("", 16, "bold")).pack(**pad)
        ctk.CTkLabel(self, text=f"{tr('result_success', self._ui_lang)}: {success}").pack(**pad)
        ctk.CTkLabel(self, text=f"{tr('result_failed', self._ui_lang)}: {len(failures)}").pack(padx=24, pady=(0, 8))
        if failures:
            box = ctk.CTkScrollableFrame(self, width=320, height=120)
            box.pack(padx=16, pady=(0, 8), fill="both", expand=True)
            for fname, reason in failures:
                ctk.CTkLabel(box, text=f"{fname}\n  → {reason}", anchor="w", justify="left").pack(
                    anchor="w", pady=2
                )
        ctk.CTkButton(self, text=tr("result_ok", self._ui_lang), command=self.destroy).pack(pady=(0, 16))

    def _center(self, master) -> None:
        self.update_idletasks()
        mx = master.winfo_rootx() + master.winfo_width() // 2
        my = master.winfo_rooty() + master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{mx - w // 2}+{my - h // 2}")


class MainWindow(ctk.CTk):
    def __init__(
        self,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        load_window_size: Optional[Callable] = None,
        save_window_size: Optional[Callable] = None,
        on_settings_change: Optional[Callable[[dict], None]] = None,
        ui_language: str = DEFAULT_UI_LANG,
    ) -> None:
        super().__init__()
        self._on_start = on_start or (lambda *_: None)
        self._on_stop = on_stop or (lambda: None)
        self._load_window_size = load_window_size or (lambda: (300, 600))
        self._save_window_size = save_window_size or (lambda w, h: None)
        self._on_settings_change = on_settings_change or (lambda settings: None)
        self._ui_lang = normalize_ui_lang(ui_language)
        self._jar_paths: list[str] = []
        self._output_dir: Optional[str] = None
        self._detected_languages: list[str] = []
        self._setup_window()
        self._build_ui()
        self._setup_logging()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_window(self) -> None:
        self.title(tr("app_title", self._ui_lang))
        w, h = self._load_window_size()
        self.geometry(f"{w}x{h}")
        self.minsize(400, 600)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._part1 = ctk.CTkFrame(self)
        self._part1.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=8)
        self._part1.grid_columnconfigure(0, weight=1)
        self._part1.grid_rowconfigure(9, weight=1)

        self._part2 = ctk.CTkFrame(self)
        self._part2.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=8)
        self._part2.grid_columnconfigure(0, weight=1)
        self._part2.grid_rowconfigure(0, weight=1)

        self._build_part1()
        self._build_part2()

    def _t(self, key: str, **kwargs) -> str:
        return tr(key, self._ui_lang, **kwargs)

    def _build_part1(self) -> None:
        self._ui_lang_var = ctk.StringVar(value=self._ui_lang)
        self._jar_frame = ctk.CTkFrame(self._part1)
        self._jar_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        self._jar_frame.grid_columnconfigure(0, weight=1)
        self._lbl_ui_language = ctk.CTkLabel(self._jar_frame, text=self._t("ui_language"), anchor="w")
        self._lbl_ui_language.grid(
            row=0, column=0, sticky="ew", padx=8, pady=(6, 0)
        )
        self._ui_lang_menu = ctk.CTkOptionMenu(
            self._jar_frame,
            values=list(SUPPORTED_UI_LANGS),
            variable=self._ui_lang_var,
            command=self._on_ui_language_change,
            width=96,
        )
        self._ui_lang_menu.grid(row=0, column=1, sticky="e", padx=8, pady=(6, 0))
        self._lbl_input_files = ctk.CTkLabel(self._jar_frame, text=self._t("input_files"), anchor="w")
        self._lbl_input_files.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(6, 0)
        )
        self._lbl_jars = ctk.CTkLabel(
            self._jar_frame, text=self._t("selected_none_files"), anchor="w", wraplength=160, justify="left"
        )
        self._lbl_jars.grid(row=2, column=0, sticky="ew", padx=8, pady=(2, 0))
        self._input_btn_frame = ctk.CTkFrame(self._jar_frame, fg_color="transparent")
        self._input_btn_frame.grid(row=2, column=1, padx=8, pady=4, sticky="ew")
        self._input_btn_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(self._input_btn_frame, text=self._t("select_files"), width=72, command=self._select_jars).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ctk.CTkButton(self._input_btn_frame, text=self._t("select_folder"), width=72, command=self._select_jar_folder).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )

        self._out_frame = ctk.CTkFrame(self._part1)
        self._out_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        self._out_frame.grid_columnconfigure(0, weight=1)
        self._lbl_output_folder = ctk.CTkLabel(self._out_frame, text=self._t("output_folder"), anchor="w")
        self._lbl_output_folder.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(6, 0)
        )
        self._lbl_output = ctk.CTkLabel(
            self._out_frame, text=self._t("selected_none_folder"), anchor="w", wraplength=160, justify="left"
        )
        self._lbl_output.grid(row=1, column=0, sticky="ew", padx=8, pady=(2, 0))
        ctk.CTkButton(self._out_frame, text=self._t("select_folder"), width=72, command=self._select_output).grid(
            row=1, column=1, padx=8, pady=4
        )

        self._scan_frame = ctk.CTkFrame(self._part1)
        self._scan_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        self._scan_frame.grid_columnconfigure(0, weight=1)
        self._lbl_scan_title = ctk.CTkLabel(self._scan_frame, text=self._t("scan_title"), anchor="w")
        self._lbl_scan_title.grid(
            row=0, column=0, sticky="ew", padx=8, pady=(6, 0)
        )
        ctk.CTkButton(self._scan_frame, text=self._t("scan_button"), command=self._handle_scan).grid(
            row=1, column=0, sticky="ew", padx=8, pady=(4, 8)
        )

        self._lang_frame = ctk.CTkFrame(self._part1)
        self._lang_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=4)
        self._lang_frame.grid_columnconfigure((0, 1), weight=1)

        self._input_lang_panel = ctk.CTkFrame(self._lang_frame)
        self._input_lang_panel.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=8)
        self._input_lang_panel.grid_columnconfigure(0, weight=1)
        self._input_lang_label = ctk.CTkLabel(self._input_lang_panel, text=self._t("input_lang_label"), anchor="w")
        self._input_lang_label.grid(
            row=0, column=0, sticky="ew", padx=8, pady=(6, 0)
        )
        self._input_lang_var = ctk.StringVar(value=DEFAULT_INPUT_LANG)
        self._input_lang_menu = ctk.CTkOptionMenu(
            self._input_lang_panel,
            values=[DEFAULT_INPUT_LANG],
            variable=self._input_lang_var,
            command=self._on_input_lang_change,
        )
        self._input_lang_menu.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 8))

        self._output_lang_panel = ctk.CTkFrame(self._lang_frame)
        self._output_lang_panel.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=8)
        self._output_lang_panel.grid_columnconfigure(0, weight=1)
        self._output_lang_label = ctk.CTkLabel(self._output_lang_panel, text=self._t("output_lang_label"), anchor="w")
        self._output_lang_label.grid(
            row=0, column=0, sticky="ew", padx=8, pady=(6, 0)
        )
        self._output_lang_var = ctk.StringVar(value=DEFAULT_OUTPUT_LANG)
        self._output_lang_menu = ctk.CTkOptionMenu(
            self._output_lang_panel,
            values=SUPPORTED_LANGS,
            variable=self._output_lang_var,
        )
        self._output_lang_menu.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 8))

        self._action_frame = ctk.CTkFrame(self._part1)
        self._action_frame.grid(row=4, column=0, sticky="ew", padx=8, pady=(4, 8))
        self._action_frame.grid_columnconfigure((0, 1), weight=1)
        self._btn_start = ctk.CTkButton(self._action_frame, text=self._t("start"), command=self._handle_start)
        self._btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._btn_stop = ctk.CTkButton(
            self._action_frame, text=self._t("stop"), command=self._handle_stop, fg_color="gray40", state="disabled"
        )
        self._btn_stop.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        self._progress = ProgressPanel(self._part1, ui_lang=self._ui_lang)
        self._progress.grid(row=5, column=0, sticky="ew", padx=8, pady=4)

        self._log_window = LogWindow(self)
        self._btn_log = ctk.CTkButton(self._part1, text=self._t("log_view"), fg_color="gray30", command=self._toggle_log)
        self._btn_log.grid(row=6, column=0, sticky="ew", padx=8, pady=(4, 8))

    def _build_part2(self) -> None:
        self._mod_list = ModListPanel(self._part2)
        self._mod_list.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    def _setup_logging(self) -> None:
        handler = GUILogHandler(self._log_window)
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        root = logging.getLogger()
        root.addHandler(handler)
        root.setLevel(logging.INFO)

    def _select_jars(self) -> None:
        paths = filedialog.askopenfilenames(
            title="JAR 파일 선택",
            filetypes=[("JAR files", "*.jar"), ("All files", "*.*")],
        )
        if not paths:
            return
        self._jar_paths = list(paths)
        names = [Path(p).name for p in paths]
        self._lbl_jars.configure(text="\n".join(names))
        self._mod_list.set_files(names)
        self._refresh_language_options()

    def _select_jar_folder(self) -> None:
        folder = filedialog.askdirectory(title="JAR 폴더 선택")
        if not folder:
            return
        root = Path(folder)
        paths = sorted(root.rglob("*.jar"))
        if not paths:
            self._log_window.show()
            logging.warning(self._t("no_jar_in_folder"))
            return
        self._jar_paths = [str(path) for path in paths]
        names = [path.name for path in paths]
        self._lbl_jars.configure(text=f"{root.name}\n" + "\n".join(names))
        self._mod_list.set_files(names)
        self._refresh_language_options()

    def _select_output(self) -> None:
        path = filedialog.askdirectory(title="출력 폴더 선택")
        if not path:
            return
        self._output_dir = path
        self._lbl_output.configure(text=path)

    def _handle_scan(self) -> None:
        if not self._jar_paths:
            self._log_window.show()
            logging.warning(self._t("no_input_files"))
            return
        logging.getLogger(__name__).info("%s: %s", self._t("scan_start"), ", ".join(self._jar_paths))
        self._detected_languages = self._scan_language_codes()
        self._refresh_language_options()
        logging.info("%s: %s", self._t("scan_complete"), ", ".join(self._detected_languages))

    def _scan_language_codes(self) -> list[str]:
        detected: list[str] = []
        for jar_path in self._jar_paths:
            logging.getLogger(__name__).info("압축 해제 시작(스캔): %s", jar_path)
            extract_dir = unzip_jar(Path(jar_path), WORK_ROOT)
            try:
                lang_files = find_json(extract_dir)
                logging.getLogger(__name__).info(
                    "감지된 언어 파일: %s",
                    ", ".join(Path(path).name for path in lang_files),
                )
                for json_path in lang_files:
                    code = Path(json_path).stem
                    if code not in detected:
                        detected.append(code)
            finally:
                logging.getLogger(__name__).info("압축 해제 폴더 삭제(스캔): %s", extract_dir)
                shutil.rmtree(extract_dir, ignore_errors=True)
        if DEFAULT_INPUT_LANG not in detected:
            detected.insert(0, DEFAULT_INPUT_LANG)
        return detected

    def _refresh_language_options(self) -> None:
        input_values = self._detected_languages or [DEFAULT_INPUT_LANG]
        if DEFAULT_INPUT_LANG not in input_values:
            input_values = [DEFAULT_INPUT_LANG, *input_values]
        self._input_lang_menu.configure(values=input_values)
        if self._input_lang_var.get() not in input_values:
            self._input_lang_var.set(input_values[0])
        self._input_lang_menu.set(self._input_lang_var.get())

        output_values = [DEFAULT_OUTPUT_LANG]
        for code in SUPPORTED_LANGS:
            if code not in output_values:
                output_values.append(code)
        self._output_lang_menu.configure(values=output_values)
        if self._output_lang_var.get() not in output_values:
            self._output_lang_var.set(DEFAULT_OUTPUT_LANG)
        self._output_lang_menu.set(self._output_lang_var.get())
        self._update_input_lang_label()
        logging.getLogger(__name__).info(
            "언어 옵션 갱신: input=%s output=%s / UI=%s",
            self._input_lang_var.get(),
            self._output_lang_var.get(),
            self._ui_lang,
        )

    def _on_input_lang_change(self, value: str) -> None:
        self._input_lang_var.set(value)
        self._update_input_lang_label()

    def _update_input_lang_label(self) -> None:
        self._input_lang_label.configure(text=f"{self._t('input_lang_label')} ({self._input_lang_var.get()})")

    def _on_ui_language_change(self, value: str) -> None:
        self._ui_lang = normalize_ui_lang(value)
        self._ui_lang_var.set(self._ui_lang)
        self.title(self._t("app_title"))
        self._on_settings_change({"ui_language": self._ui_lang, "restart": True})

    def _apply_ui_language(self) -> None:
        self._log_window.set_language(self._ui_lang)
        self._progress.set_language(self._ui_lang)
        self._progress.refresh_texts()
        self._lbl_ui_language.configure(text=self._t("ui_language"))
        self._lbl_input_files.configure(text=self._t("input_files"))
        self._lbl_output_folder.configure(text=self._t("output_folder"))
        self._lbl_scan_title.configure(text=self._t("scan_title"))
        self._output_lang_label.configure(text=self._t("output_lang_label"))
        self._mod_list.set_title(self._t("mod_list"))
        self._btn_log.configure(text=self._t("log_view"))
        self._btn_start.configure(text=self._t("start"))
        self._btn_stop.configure(text=self._t("stop"))
        self._input_lang_label.configure(text=f"{self._t('input_lang_label')} ({self._input_lang_var.get()})")

    def _handle_start(self) -> None:
        if not self._jar_paths:
            self._log_window.show()
            logging.warning(self._t("no_input_files"))
            return
        if not self._output_dir:
            self._log_window.show()
            logging.warning(self._t("no_output_folder"))
            return
        logging.getLogger(__name__).info(
            "%s: jars=%s, output=%s, input=%s, output_lang=%s",
            self._t("translation_start_request"),
            ", ".join(self._jar_paths),
            self._output_dir,
            self._input_lang_var.get(),
            self._output_lang_var.get(),
        )
        self._btn_start.configure(state="disabled")
        self._btn_stop.configure(state="normal")
        self._progress.reset()
        threading.Thread(
            target=self._on_start,
            args=(list(self._jar_paths), self._output_dir),
            daemon=True,
        ).start()

    def _handle_stop(self) -> None:
        self._on_stop()
        self._set_idle_state()

    def _toggle_log(self) -> None:
        if self._log_window.winfo_viewable():
            self._log_window.hide()
        else:
            self._log_window.show()

    def _on_close(self) -> None:
        w, h = self.winfo_width(), self.winfo_height()
        self._save_window_size(w, h)
        self.destroy()

    def update_total_progress(self, value: float) -> None:
        self.after(0, lambda: self._progress.set_total(value))

    def update_current_progress(self, value: float) -> None:
        self.after(0, lambda: self._progress.set_current(value))

    def update_jar_name(self, name: str) -> None:
        self.after(0, lambda: self._progress.set_jar_name(name))

    def update_mod_state(self, filename: str, state: str) -> None:
        self.after(0, lambda: self._mod_list.set_state(filename, state))

    def show_result(self, success: int, failures: list[tuple[str, str]]) -> None:
        def _show() -> None:
            self._set_idle_state()
            ResultDialog(self, success, failures)

        self.after(0, _show)

    def _set_idle_state(self) -> None:
        self._btn_start.configure(state="normal")
        self._btn_stop.configure(state="disabled")


class AppController:
    def __init__(self) -> None:
        self._settings = self._load_settings()
        self._stop_event = threading.Event()
        self._app: Optional[MainWindow] = None
        self._restart_requested = False

    def _load_settings(self) -> dict:
        config = read_config(PROJECT_ROOT)
        return {
            "window_width": int(config.get("window_width", 400)),
            "window_height": int(config.get("window_height", 600)),
            "ui_language": normalize_ui_lang(config.get("ui_language", DEFAULT_UI_LANG)),
        }

    def _save_settings(self) -> None:
        try:
            config = read_config(PROJECT_ROOT)
            config.update(self._settings)
            write_config(PROJECT_ROOT, config)
        except OSError as exc:
            logging.error("설정 저장 실패: %s", exc)

    def load_window_size(self) -> tuple[int, int]:
        return (
            int(self._settings.get("window_width", 400)),
            int(self._settings.get("window_height", 600)),
        )

    def save_window_size(self, w: int, h: int) -> None:
        self._settings["window_width"] = w
        self._settings["window_height"] = h
        self._save_settings()

    def on_stop(self) -> None:
        self._stop_event.set()
        logging.getLogger(__name__).info(self._app._t("translation_stopped") if self._app else "stopped")

    def _find_selected_language_file(self, extract_dir: Path, input_lang: str) -> Path:
        candidates = sorted(extract_dir.rglob(f"{input_lang}.json"))
        logging.getLogger(__name__).info(
            "입력 언어 탐색: %s / candidates=%s",
            input_lang,
            ", ".join(str(candidate) for candidate in candidates) or "(none)",
        )
        for candidate in candidates:
            if candidate.is_file() and candidate.parent.name.lower() == "lang":
                return candidate
        raise FileNotFoundError(
            f"선택한 입력 언어 파일을 찾지 못했습니다: {input_lang}.json"
        )

    def on_start(self, jar_paths: list[str], output_dir: str) -> None:
        self._stop_event.clear()
        logger = logging.getLogger(__name__)

        config = read_config(PROJECT_ROOT)
        api_key = config.get("gemini_api_key", "").strip()
        if not api_key:
            logger.error("번역 시작 불가: config.json의 gemini_api_key가 비어 있습니다.")
            self._app.show_result(0, [(Path(p).name, self._app._t("config_api_missing")) for p in jar_paths])
            return

        names = [Path(p).name for p in jar_paths]
        total = len(jar_paths)
        successes = 0
        failures: list[tuple[str, str]] = []
        input_lang = self._app._input_lang_var.get().strip() or DEFAULT_INPUT_LANG
        output_lang = self._app._output_lang_var.get().strip() or DEFAULT_OUTPUT_LANG

        for index, (path, name) in enumerate(zip(jar_paths, names)):
            if self._stop_event.is_set():
                logger.info(self._app._t("translation_stopped"))
                break

            self._app.update_jar_name(name)
            self._app.update_mod_state(name, "running")
            self._app.update_current_progress(0)
            logger.info("%s: %s", self._app._t("translation_start"), name)

            try:
                self._translate_one(Path(path), Path(output_dir), api_key, input_lang, output_lang)
                self._app.update_mod_state(name, "done")
                successes += 1
                logger.info("%s: %s", self._app._t("translation_complete"), name)
            except Exception as exc:
                reason = str(exc)
                self._app.update_mod_state(name, "failed")
                user_reason = self._format_user_error(exc)
                failures.append((name, user_reason))
                logger.error("%s: %s - %s", self._app._t("translation_failed"), name, reason)
                logger.exception("번역 상세 예외")
                self._app._log_window.show()

            self._app.update_total_progress((index + 1) / total)
            self._app.update_current_progress(0)

        self._app.show_result(successes, failures)

    def _translate_one(
        self,
        jar_path: Path,
        output_dir: Path,
        api_key: str,
        input_lang: str,
        output_lang: str,
    ) -> None:
        from modules.gemini_translator import translate_json

        extract_dir = unzip_jar(jar_path, WORK_ROOT)
        try:
            logging.getLogger(__name__).info("압축 해제 완료(번역): %s -> %s", jar_path, extract_dir)
            lang_file = self._find_selected_language_file(extract_dir, input_lang)
            logging.getLogger(__name__).info("%s: %s", self._app._t("selected_language_file"), lang_file)
            if self._stop_event.is_set():
                raise InterruptedError("작업이 중단되었습니다.")
            self._app.update_current_progress(0)
            logging.getLogger(__name__).info(
                "번역 중: %s (%s -> %s)",
                lang_file.name,
                input_lang,
                output_lang,
            )
            translate_json(
                api_key=api_key,
                json_path=lang_file,
                input_lang=input_lang,
                output_lang=output_lang,
                logger=logging.getLogger(__name__),
            )
            self._app.update_current_progress(1)

            output_dir.mkdir(parents=True, exist_ok=True)
            logging.getLogger(__name__).info("%s: %s -> %s", self._app._t("repack_start"), extract_dir, output_dir / jar_path.name)
            zip_jar(extract_dir, output_dir / jar_path.name)
            logging.getLogger(__name__).info("%s: %s", self._app._t("repack_done"), output_dir / jar_path.name)
        finally:
            logging.getLogger(__name__).info("%s: %s", self._app._t("extract_delete"), extract_dir)
            shutil.rmtree(extract_dir, ignore_errors=True)
            self._prune_work_dirs(extract_dir)

    def _prune_work_dirs(self, extract_dir: Path) -> None:
        current = extract_dir.parent
        while current != WORK_ROOT.parent:
            try:
                current.rmdir()
                logging.getLogger(__name__).info("%s: %s", self._app._t("work_delete"), current)
            except OSError:
                break
            current = current.parent

    def run(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        while True:
            self._restart_requested = False
            self._app = MainWindow(
                on_start=self.on_start,
                on_stop=self.on_stop,
                load_window_size=self.load_window_size,
                save_window_size=self.save_window_size,
                on_settings_change=self.update_settings,
                ui_language=self._settings.get("ui_language", DEFAULT_UI_LANG),
            )
            self._app.mainloop()
            if not self._restart_requested:
                break

    def update_settings(self, patch: dict) -> None:
        restart = bool(patch.pop("restart", False))
        self._settings.update(patch)
        self._save_settings()
        if restart and self._app is not None:
            self._restart_requested = True
            self._app.after(0, self._app.destroy)

    def _format_user_error(self, exc: Exception) -> str:
        try:
            from modules.gemini_translator import user_friendly_error_message
        except Exception:
            return "오류가 발생했습니다."
        return user_friendly_error_message(exc)


def main() -> int:
    AppController().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
