import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'hmon.py',
    '--onefile',         # Собрать в один EXE
    '--noconsole',       # Не открывать консоль
    '--name=HMonOverlay', # Имя файла
    '--clean'
])
