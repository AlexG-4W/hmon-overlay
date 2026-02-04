# HMon - Hardware Monitoring Overlay

A lightweight, customizable, and transparent system resource monitor for Windows. It stays on top of all windows and provides real-time updates for your CPU, RAM, and GPU.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)

## Features

- **Real-time Monitoring**: Tracks CPU frequency, RAM usage/speed, and GPU clock/VRAM.
- **Always on Top**: Transparent overlay that doesn't interfere with your workflow.
- **Customizable**:
  - **Skins**: Choose between Dark, Light, Cyberpunk, and Minimalist themes.
  - **Localization**: Supports English (EN) and Russian (RU).
  - **Selective Display**: Toggle visibility for each hardware component.
- **Draggable**: Easily move the overlay anywhere on your screen.
- **Lightweight**: Low resource consumption.

## Installation

### Prerequisites

Ensure you have Python 3.8+ installed. Install the required dependencies using pip:

```bash
pip install psutil py-cpuinfo pynvml PySide6 WMI
```

### Running the App

1. **Standard Run**: 
   ```bash
   python hmon.py
   ```
2. **Silent Run (No Console)**: 
   Double-click `hmon.pyw` or run `pythonw hmon.py`.

## Configuration

Right-click on the overlay to access the **Settings** menu. You can:
- Change the display language.
- Select a visual skin.
- Choose which hardware metrics to show.

## Build EXE

To create a standalone executable, use PyInstaller:

```bash
pip install pyinstaller
python build_exe.py
```
The executable will be located in the `dist/` folder.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
