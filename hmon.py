import sys
import json
import os
import psutil
import cpuinfo
import wmi
import pynvml
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QMenu, QCheckBox, QComboBox, QPushButton, QFormLayout, QGroupBox)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QFont

CONFIG_FILE = "hmon_config.json"

# Localization dictionary
TRANSLATIONS = {
    'EN': {
        'settings': 'HMon Settings',
        'display_info': 'Display Information',
        'appearance': 'Appearance',
        'language': 'Language',
        'skin': 'Skin',
        'cpu': 'Processor (CPU)',
        'ram': 'Memory (RAM)',
        'gpu_f': 'GPU Clock',
        'gpu_v': 'Video Memory (VRAM)',
        'close': 'Close',
        'exit': 'Exit',
        'setup': 'Settings',
        'loading': 'Loading...',
        'no_gpu': 'No NVIDIA GPU'
    },
    'RU': {
        'settings': 'Настройки HMon',
        'display_info': 'Отображаемая информация',
        'appearance': 'Внешний вид',
        'language': 'Язык',
        'skin': 'Скин',
        'cpu': 'Процессор (CPU)',
        'ram': 'Память (RAM)',
        'gpu_f': 'Частота GPU',
        'gpu_v': 'Видеопамять (VRAM)',
        'close': 'Закрыть',
        'exit': 'Выход',
        'setup': 'Настройки',
        'loading': 'Загрузка...',
        'no_gpu': 'Нет NVIDIA GPU'
    }
}

class HardwareMonitor:
    """Hardware data retrieval logic."""
    def __init__(self):
        self.cpu_name = "Unknown CPU"
        self.ram_freq = "N/A"
        try:
            info = cpuinfo.get_cpu_info()
            self.cpu_name = info.get('brand_raw', "Unknown CPU")
        except: pass
        
        try:
            pynvml.nvmlInit()
            self.nvml_available = True
        except: self.nvml_available = False

        try:
            w = wmi.WMI()
            speeds = [str(ram.Speed) for ram in w.Win32_PhysicalMemory()]
            if speeds: self.ram_freq = f"{speeds[0]} MHz"
        except: pass

    def get_data(self, lang_code='EN'):
        t = TRANSLATIONS[lang_code]
        data = {}
        try:
            freq = psutil.cpu_freq()
            data['cpu'] = f"CPU: {self.cpu_name}\nFreq: {freq.current:.0f} MHz" if freq else f"CPU: {self.cpu_name}\nFreq: N/A"
        except: data['cpu'] = "CPU Error"

        try:
            mem = psutil.virtual_memory()
            data['ram'] = f"RAM: {mem.total / (1024**3):.1f} GB @ {self.ram_freq}"
        except: data['ram'] = "RAM Error"

        if self.nvml_available:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes): name = name.decode('utf-8')
                clk = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
                v_clk = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
                v_mem = pynvml.nvmlDeviceGetMemoryInfo(handle).total / (1024**2)
                data['gpu_freq'] = f"GPU: {name}\nClock: {clk} MHz"
                data['gpu_vram'] = f"VRAM: {v_mem:.0f} MB @ {v_clk} MHz"
            except:
                data['gpu_freq'] = "GPU Error"
                data['gpu_vram'] = "N/A"
        else:
            data['gpu_freq'] = t['no_gpu']
            data['gpu_vram'] = "N/A"
        return data

class SettingsWindow(QWidget):
    """Settings interface with localization support."""
    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setFixedSize(320, 420)
        self.main_layout = QVBoxLayout()
        
        # Data group
        self.group_data = QGroupBox()
        data_layout = QVBoxLayout()
        self.chk_cpu = QCheckBox()
        self.chk_ram = QCheckBox()
        self.chk_gpu_f = QCheckBox()
        self.chk_gpu_v = QCheckBox()
        for chk in [self.chk_cpu, self.chk_ram, self.chk_gpu_f, self.chk_gpu_v]:
            data_layout.addWidget(chk)
            chk.stateChanged.connect(self.save_and_apply)
        self.group_data.setLayout(data_layout)
        self.main_layout.addWidget(self.group_data)

        # Appearance group
        self.group_app = QGroupBox()
        app_layout = QFormLayout()
        
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["EN", "RU"])
        self.combo_lang.currentTextChanged.connect(self.save_and_apply)
        
        self.combo_skin = QComboBox()
        self.combo_skin.addItems(["Dark", "Light", "Cyberpunk", "Minimalist"])
        self.combo_skin.currentTextChanged.connect(self.save_and_apply)
        
        self.lbl_lang = QLabel()
        self.lbl_skin = QLabel()
        
        app_layout.addRow(self.lbl_lang, self.combo_lang)
        app_layout.addRow(self.lbl_skin, self.combo_skin)
        self.group_app.setLayout(app_layout)
        self.main_layout.addWidget(self.group_app)

        self.btn_close = QPushButton()
        self.btn_close.clicked.connect(self.hide)
        self.main_layout.addWidget(self.btn_close)
        
        self.setLayout(self.main_layout)

    def update_texts(self, lang_code):
        t = TRANSLATIONS[lang_code]
        self.setWindowTitle(t['settings'])
        self.group_data.setTitle(t['display_info'])
        self.group_app.setTitle(t['appearance'])
        self.chk_cpu.setText(t['cpu'])
        self.chk_ram.setText(t['ram'])
        self.chk_gpu_f.setText(t['gpu_f'])
        self.chk_gpu_v.setText(t['gpu_v'])
        self.lbl_lang.setText(t['language'] + ":")
        self.lbl_skin.setText(t['skin'] + ":")
        self.btn_close.setText(t['close'])

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    s = json.load(f)
                    self.chk_cpu.setChecked(s.get('show_cpu', True))
                    self.chk_ram.setChecked(s.get('show_ram', True))
                    self.chk_gpu_f.setChecked(s.get('show_gpu_f', True))
                    self.chk_gpu_v.setChecked(s.get('show_gpu_v', True))
                    self.combo_lang.setCurrentText(s.get('lang', 'EN'))
                    self.combo_skin.setCurrentText(s.get('skin', 'Dark'))
            except: self._set_defaults()
        else: self._set_defaults()
        self.save_and_apply()

    def _set_defaults(self):
        for chk in [self.chk_cpu, self.chk_ram, self.chk_gpu_f, self.chk_gpu_v]:
            chk.setChecked(True)
        self.combo_lang.setCurrentText("EN")
        self.combo_skin.setCurrentText("Dark")

    def save_and_apply(self):
        lang = self.combo_lang.currentText()
        settings = {
            'show_cpu': self.chk_cpu.isChecked(),
            'show_ram': self.chk_ram.isChecked(),
            'show_gpu_f': self.chk_gpu_f.isChecked(),
            'show_gpu_v': self.chk_gpu_v.isChecked(),
            'lang': lang,
            'skin': self.combo_skin.currentText()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f)
        self.update_texts(lang)
        self.overlay.apply_settings(settings)

class OverlayWindow(QWidget):
    """Transparent overlay window."""
    SKINS = {
        "Dark": "color: white; background-color: rgba(0, 0, 0, 160); border: 1px solid #444; border-radius: 5px;",
        "Light": "color: #222; background-color: rgba(255, 255, 255, 180); border: 1px solid #ccc; border-radius: 5px;",
        "Cyberpunk": "color: #0ff; background-color: rgba(10, 10, 10, 200); border: 2px solid #0ff; border-radius: 0px;",
        "Minimalist": "color: white; background-color: transparent; border: none;"
    }

    def __init__(self):
        super().__init__()
        self.monitor = HardwareMonitor()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.labels = {k: QLabel() for k in ['cpu', 'ram', 'gpu_freq', 'gpu_vram']}
        for lbl in self.labels.values():
            lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.layout.addWidget(lbl)

        self.current_lang = 'EN'
        self.settings_win = SettingsWindow(self)
        self.old_pos = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)
        self.update_info()

    def apply_settings(self, s):
        self.current_lang = s.get('lang', 'EN')
        self.labels['cpu'].setVisible(s.get('show_cpu', True))
        self.labels['ram'].setVisible(s.get('show_ram', True))
        self.labels['gpu_freq'].setVisible(s.get('show_gpu_f', True))
        self.labels['gpu_vram'].setVisible(s.get('show_gpu_v', True))
        
        style = self.SKINS.get(s.get('skin', 'Dark'), self.SKINS["Dark"])
        for lbl in self.labels.values():
            lbl.setStyleSheet(style + "padding: 8px;")
        self.adjustSize()

    def update_info(self):
        data = self.monitor.get_data(self.current_lang)
        for k, v in data.items():
            if k in self.labels: self.labels[k].setText(v)
        self.adjustSize()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.RightButton:
            t = TRANSLATIONS[self.current_lang]
            menu = QMenu(self)
            menu.addAction(t['setup']).triggered.connect(self.settings_win.show)
            menu.addSeparator()
            menu.addAction(t['exit']).triggered.connect(QApplication.quit)
            menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event): self.old_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = OverlayWindow()
    window.show()
    sys.exit(app.exec())
