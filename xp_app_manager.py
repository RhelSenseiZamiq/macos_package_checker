#!/usr/bin/env python3
"""
H4CK3R App Manager — macOS application/package manager with cyberpunk hacker GUI.
Scans /Applications, ~/Applications, Homebrew formulae & casks, system packages,
pip packages, and running processes.  Lets you uninstall or kill them.
"""

import sys
import os
import subprocess
import json
import plistlib
import platform
import shutil
import time
import random
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QComboBox, QFrame, QProgressBar,
    QAbstractItemView, QCheckBox, QDialog, QTextEdit, QTabWidget,
    QGroupBox, QGridLayout, QSizePolicy,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QPoint, QRect, pyqtProperty,
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QPen, QBrush,
    QLinearGradient, QIcon, QTextCursor, QAction,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HACKER COLOUR PALETTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BG_DARKEST      = "#0a0a0a"
BG_DARK         = "#0d1117"
BG_PANEL        = "#111820"
BG_INPUT        = "#0b1016"
BG_TABLE        = "#080c10"
BG_HEADER       = "#0f1923"

NEON_GREEN      = "#00ff41"
NEON_GREEN_DIM  = "#00cc33"
NEON_GREEN_DARK = "#004d00"
NEON_CYAN       = "#00e5ff"
NEON_RED        = "#ff1744"
NEON_RED_DIM    = "#cc0033"
NEON_ORANGE     = "#ff9100"
NEON_PURPLE     = "#d500f9"
NEON_YELLOW     = "#ffea00"

BORDER_GREEN    = "#003300"
BORDER_BRIGHT   = "#00ff41"
TEXT_DIM        = "#4a6a4a"
TEXT_MID        = "#00aa2a"
TEXT_BRIGHT     = "#00ff41"

# Row type colours (dark variants)
ROW_APP         = "#0a1a0a"
ROW_BREW_FORM   = "#1a1a00"
ROW_BREW_CASK   = "#001a1a"
ROW_SYSTEM      = "#1a0a0a"
ROW_PIP         = "#0a0a1a"
ROW_PROCESS     = "#1a0a1a"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HACKER ICON
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def make_hacker_icon(size=64):
    px = QPixmap(size, size)
    px.fill(QColor(0, 0, 0, 0))
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)  # pixelated
    s = size // 16

    # Black background with green border
    p.setPen(QPen(QColor(NEON_GREEN), 2))
    p.setBrush(QColor(BG_DARKEST))
    p.drawRect(1, 1, size-2, size-2)

    # Skull pixels (simple 8-bit skull)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(NEON_GREEN))
    skull = [
        (5,2),(6,2),(7,2),(8,2),(9,2),(10,2),
        (4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),
        (4,4),(5,4),(7,4),(8,4),(10,4),(11,4),
        (4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),
        (5,6),(6,6),(7,6),(8,6),(9,6),(10,6),
        (6,7),(7,7),(8,7),(9,7),
        (5,8),(6,8),(7,8),(8,8),(9,8),(10,8),
        (6,9),(8,9),(10,9),
    ]
    for (px_x, px_y) in skull:
        p.drawRect(px_x * s, px_y * s, s, s)

    # Terminal cursor blink
    p.setBrush(QColor(NEON_GREEN))
    p.drawRect(3*s, 12*s, 3*s, s)
    p.drawRect(7*s, 12*s, s, s)
    p.drawRect(9*s, 12*s, 2*s, s)
    p.drawRect(12*s, 12*s, s, s)

    p.end()
    return QIcon(px)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GLOBAL HACKER STYLESHEET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HACKER_CSS = f"""
* {{
    font-family: "Menlo", "Monaco", "Courier New", monospace;
}}

QMainWindow {{
    background-color: {BG_DARKEST};
}}

/* ── Buttons ── */
QPushButton {{
    background-color: {BG_PANEL};
    color: {NEON_GREEN};
    border: 1px solid {NEON_GREEN_DARK};
    padding: 6px 16px;
    font-size: 13px;
    font-weight: bold;
    font-family: "Menlo", monospace;
    min-height: 26px;
}}
QPushButton:hover {{
    background-color: {NEON_GREEN_DARK};
    border: 1px solid {NEON_GREEN};
    color: #ffffff;
}}
QPushButton:pressed {{
    background-color: {NEON_GREEN};
    color: {BG_DARKEST};
}}
QPushButton:disabled {{
    color: #333333;
    border-color: #1a1a1a;
    background-color: #0a0a0a;
}}

QPushButton#scanBtn {{
    background-color: #001a00;
    border: 2px solid {NEON_GREEN};
    color: {NEON_GREEN};
    font-size: 14px;
    padding: 6px 22px;
}}
QPushButton#scanBtn:hover {{
    background-color: {NEON_GREEN};
    color: {BG_DARKEST};
}}

QPushButton#deleteBtn {{
    background-color: #1a0000;
    border: 2px solid {NEON_RED};
    color: {NEON_RED};
    font-size: 13px;
}}
QPushButton#deleteBtn:hover {{
    background-color: {NEON_RED};
    color: #ffffff;
}}
QPushButton#deleteBtn:disabled {{
    color: #331111;
    border-color: #1a0000;
    background-color: #0a0000;
}}

QPushButton#killBtn {{
    background-color: #1a0a00;
    border: 2px solid {NEON_ORANGE};
    color: {NEON_ORANGE};
}}
QPushButton#killBtn:hover {{
    background-color: {NEON_ORANGE};
    color: {BG_DARKEST};
}}

QPushButton#infoBtn {{
    background-color: #000a1a;
    border: 1px solid {NEON_CYAN};
    color: {NEON_CYAN};
}}
QPushButton#infoBtn:hover {{
    background-color: {NEON_CYAN};
    color: {BG_DARKEST};
}}

QPushButton#exportBtn {{
    background-color: #0a001a;
    border: 1px solid {NEON_PURPLE};
    color: {NEON_PURPLE};
}}
QPushButton#exportBtn:hover {{
    background-color: {NEON_PURPLE};
    color: #ffffff;
}}

/* ── Line edit ── */
QLineEdit {{
    background: {BG_INPUT};
    color: {NEON_GREEN};
    border: 1px solid {NEON_GREEN_DARK};
    padding: 5px 8px;
    font-family: "Menlo", monospace;
    font-size: 13px;
    selection-background-color: {NEON_GREEN_DARK};
    selection-color: #ffffff;
}}
QLineEdit:focus {{
    border: 1px solid {NEON_GREEN};
}}

/* ── Combo box ── */
QComboBox {{
    background: {BG_INPUT};
    color: {NEON_GREEN};
    border: 1px solid {NEON_GREEN_DARK};
    padding: 4px 8px;
    font-family: "Menlo", monospace;
    font-size: 13px;
    min-width: 160px;
}}
QComboBox::drop-down {{
    border-left: 1px solid {NEON_GREEN_DARK};
    width: 24px;
    background: {BG_PANEL};
}}
QComboBox::down-arrow {{
    image: none;
    border: none;
}}
QComboBox QAbstractItemView {{
    background: {BG_DARK};
    color: {NEON_GREEN};
    border: 1px solid {NEON_GREEN_DARK};
    selection-background-color: {NEON_GREEN_DARK};
    selection-color: #ffffff;
    font-family: "Menlo", monospace;
}}

/* ── Tab widget ── */
QTabWidget::pane {{
    border: 1px solid {NEON_GREEN_DARK};
    background: {BG_DARK};
}}
QTabBar::tab {{
    background: {BG_PANEL};
    color: {TEXT_DIM};
    border: 1px solid {NEON_GREEN_DARK};
    padding: 8px 20px;
    font-family: "Menlo", monospace;
    font-size: 12px;
    font-weight: bold;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {BG_DARK};
    color: {NEON_GREEN};
    border-bottom: 2px solid {NEON_GREEN};
}}
QTabBar::tab:hover {{
    color: {NEON_GREEN};
    background: #0a1a0a;
}}

/* ── Table ── */
QTableWidget {{
    background-color: {BG_TABLE};
    color: {NEON_GREEN};
    border: 1px solid {NEON_GREEN_DARK};
    gridline-color: #0a1a0a;
    font-family: "Menlo", monospace;
    font-size: 12px;
    selection-background-color: {NEON_GREEN_DARK};
    selection-color: #ffffff;
    alternate-background-color: #0c1018;
}}
QTableWidget::item {{
    padding: 3px 6px;
    border-bottom: 1px solid #0a1a0a;
}}
QHeaderView::section {{
    background: {BG_HEADER};
    color: {NEON_GREEN};
    border: 1px solid #0a1a0a;
    border-bottom: 2px solid {NEON_GREEN_DARK};
    padding: 6px 4px;
    font-family: "Menlo", monospace;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
}}

/* ── Progress bar ── */
QProgressBar {{
    border: 1px solid {NEON_GREEN_DARK};
    background: {BG_DARKEST};
    color: {NEON_GREEN};
    text-align: center;
    font-size: 12px;
    font-family: "Menlo", monospace;
    height: 22px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {NEON_GREEN_DARK}, stop:0.5 {NEON_GREEN}, stop:1 {NEON_GREEN_DARK});
}}

/* ── Labels ── */
QLabel {{
    color: {NEON_GREEN};
    font-family: "Menlo", monospace;
    font-size: 12px;
}}
QLabel#titleLabel {{
    color: {NEON_GREEN};
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QLabel#statusLabel {{
    color: {TEXT_MID};
    font-size: 11px;
    padding: 2px 6px;
}}
QLabel#headerAscii {{
    color: {NEON_GREEN};
    font-size: 10px;
    font-family: "Menlo", monospace;
}}
QLabel#sysInfoLabel {{
    color: {NEON_CYAN};
    font-size: 11px;
}}
QLabel#dimLabel {{
    color: {TEXT_DIM};
    font-size: 11px;
}}

/* ── Frames ── */
QFrame#titleBar {{
    background: {BG_DARKEST};
    border-bottom: 1px solid {NEON_GREEN_DARK};
    min-height: 60px;
}}
QFrame#toolBar {{
    background: {BG_PANEL};
    border: 1px solid #0a1a0a;
    padding: 4px;
}}
QFrame#statusBar {{
    background: {BG_DARKEST};
    border-top: 1px solid {NEON_GREEN_DARK};
    padding: 2px;
}}
QFrame#statsBox {{
    background: {BG_PANEL};
    border: 1px solid {NEON_GREEN_DARK};
    padding: 8px;
}}

/* ── Text edit (terminal) ── */
QTextEdit {{
    background: {BG_DARKEST};
    color: {NEON_GREEN};
    border: 1px solid {NEON_GREEN_DARK};
    font-family: "Menlo", monospace;
    font-size: 12px;
    selection-background-color: {NEON_GREEN_DARK};
}}

/* ── CheckBox ── */
QCheckBox {{
    color: {NEON_GREEN};
    font-family: "Menlo", monospace;
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {NEON_GREEN_DARK};
    background: {BG_DARKEST};
}}
QCheckBox::indicator:checked {{
    background: {NEON_GREEN};
    border-color: {NEON_GREEN};
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: {BG_DARKEST};
    width: 12px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {NEON_GREEN_DARK};
    min-height: 30px;
    border: none;
}}
QScrollBar::handle:vertical:hover {{
    background: {NEON_GREEN_DIM};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {BG_DARKEST};
    height: 12px;
}}
QScrollBar::handle:horizontal {{
    background: {NEON_GREEN_DARK};
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {NEON_GREEN_DIM};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── Group box ── */
QGroupBox {{
    color: {NEON_GREEN};
    border: 1px solid {NEON_GREEN_DARK};
    margin-top: 12px;
    padding-top: 14px;
    font-family: "Menlo", monospace;
    font-size: 12px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    padding: 0 8px;
}}

/* ── Message box ── */
QMessageBox {{
    background: {BG_DARK};
    color: {NEON_GREEN};
}}
QMessageBox QLabel {{
    color: {NEON_GREEN};
    font-size: 13px;
}}
QMessageBox QPushButton {{
    min-width: 80px;
}}

/* ── Dialog ── */
QDialog {{
    background: {BG_DARK};
    color: {NEON_GREEN};
}}
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MATRIX RAIN WIDGET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class MatrixRain(QWidget):
    """A small Matrix-style digital rain background strip."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = 80
        self.drops = [random.randint(-20, 0) for _ in range(self.columns)]
        self.chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
        self.grid = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(60)
        self.setFixedHeight(50)

    def _tick(self):
        for i in range(self.columns):
            self.drops[i] += 1
            y = self.drops[i]
            self.grid[(i, y)] = random.choice(self.chars)
            if y > 8 and random.random() > 0.95:
                self.drops[i] = random.randint(-10, 0)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(BG_DARKEST))
        cell_w = max(self.width() // self.columns, 1)
        cell_h = 6
        for (cx, cy), ch in list(self.grid.items()):
            age = self.drops[cx % self.columns] - cy
            if age > 10:
                del self.grid[(cx, cy)]
                continue
            if age == 0:
                p.setPen(QColor("#ffffff"))
            elif age < 3:
                p.setPen(QColor(NEON_GREEN))
            elif age < 6:
                p.setPen(QColor(NEON_GREEN_DIM))
            else:
                p.setPen(QColor(NEON_GREEN_DARK))
            py = (cy % 8) * cell_h
            p.setFont(QFont("Menlo", 5))
            p.drawText(cx * cell_w, py, cell_w, cell_h,
                       Qt.AlignmentFlag.AlignCenter, ch)
        p.end()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SCAN WORKER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ScanWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)

    def run(self):
        results = []
        self.progress.emit(0, "[SCAN] /Applications ...")
        results += self._scan_applications("/Applications", "Application")
        self.progress.emit(15, "[SCAN] ~/Applications ...")
        results += self._scan_applications(
            str(Path.home() / "Applications"), "User App"
        )
        self.progress.emit(30, "[SCAN] Homebrew formulae ...")
        results += self._scan_brew_formulae()
        self.progress.emit(45, "[SCAN] Homebrew casks ...")
        results += self._scan_brew_casks()
        self.progress.emit(60, "[SCAN] pip3 packages ...")
        results += self._scan_pip()
        self.progress.emit(75, "[SCAN] System packages (pkgutil) ...")
        results += self._scan_pkgutil()
        self.progress.emit(100, f"[DONE] {len(results)} targets acquired")
        self.finished.emit(results)

    @staticmethod
    def _get_app_version(app_path):
        plist = os.path.join(app_path, "Contents", "Info.plist")
        try:
            with open(plist, "rb") as f:
                data = plistlib.load(f)
            return data.get("CFBundleShortVersionString",
                            data.get("CFBundleVersion", "-"))
        except Exception:
            return "-"

    @staticmethod
    def _dir_size_mb(path):
        total = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                    except OSError:
                        pass
        except Exception:
            pass
        return round(total / (1024 * 1024), 1)

    def _scan_applications(self, folder, kind):
        items = []
        if not os.path.isdir(folder):
            return items
        for name in sorted(os.listdir(folder)):
            full = os.path.join(folder, name)
            if name.endswith(".app") and os.path.isdir(full):
                ver = self._get_app_version(full)
                size = self._dir_size_mb(full)
                items.append({
                    "name": name.replace(".app", ""),
                    "version": ver,
                    "size_mb": size,
                    "kind": kind,
                    "path": full,
                    "uninstall_cmd": f'rm -rf "{full}"',
                })
        return items

    def _scan_brew_formulae(self):
        items = []
        try:
            raw = subprocess.check_output(
                ["brew", "list", "--formula", "--versions"],
                text=True, timeout=30, stderr=subprocess.DEVNULL,
            )
            cellar = subprocess.check_output(
                ["brew", "--cellar"], text=True, timeout=5
            ).strip()
            for line in raw.strip().splitlines():
                parts = line.split()
                if not parts:
                    continue
                name = parts[0]
                ver = parts[1] if len(parts) > 1 else "-"
                pkg_path = os.path.join(cellar, name)
                size = self._dir_size_mb(pkg_path) if os.path.isdir(pkg_path) else 0
                items.append({
                    "name": name,
                    "version": ver,
                    "size_mb": size,
                    "kind": "Brew Formula",
                    "path": pkg_path,
                    "uninstall_cmd": f"brew uninstall --formula {name}",
                })
        except Exception:
            pass
        return items

    def _scan_brew_casks(self):
        items = []
        try:
            raw = subprocess.check_output(
                ["brew", "list", "--cask", "--versions"],
                text=True, timeout=30, stderr=subprocess.DEVNULL,
            )
            for line in raw.strip().splitlines():
                parts = line.split()
                if not parts:
                    continue
                name = parts[0]
                ver = parts[1] if len(parts) > 1 else "-"
                items.append({
                    "name": name,
                    "version": ver,
                    "size_mb": 0,
                    "kind": "Brew Cask",
                    "path": "",
                    "uninstall_cmd": f"brew uninstall --cask {name}",
                })
        except Exception:
            pass
        return items

    def _scan_pip(self):
        items = []
        try:
            raw = subprocess.check_output(
                ["pip3", "list", "--format=json"],
                text=True, timeout=15, stderr=subprocess.DEVNULL,
            )
            pkgs = json.loads(raw)
            for pkg in pkgs:
                items.append({
                    "name": pkg["name"],
                    "version": pkg.get("version", "-"),
                    "size_mb": 0,
                    "kind": "pip Package",
                    "path": "",
                    "uninstall_cmd": f"pip3 uninstall -y --break-system-packages {pkg['name']}",
                })
        except Exception:
            pass
        return items

    def _scan_pkgutil(self):
        items = []
        try:
            raw = subprocess.check_output(
                ["pkgutil", "--pkgs"], text=True, timeout=15
            )
            for pkg in sorted(raw.strip().splitlines()):
                if not pkg:
                    continue
                ver = "-"
                try:
                    info = subprocess.check_output(
                        ["pkgutil", "--pkg-info", pkg],
                        text=True, timeout=5, stderr=subprocess.DEVNULL,
                    )
                    for ln in info.splitlines():
                        if ln.startswith("version:"):
                            ver = ln.split(":", 1)[1].strip()
                            break
                except Exception:
                    pass
                items.append({
                    "name": pkg,
                    "version": ver,
                    "size_mb": 0,
                    "kind": "System Pkg",
                    "path": "",
                    "uninstall_cmd": f"pkgutil --forget {pkg}",
                })
        except Exception:
            pass
        return items


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PROCESS SCANNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ProcessWorker(QThread):
    finished = pyqtSignal(list)

    def run(self):
        procs = []
        try:
            raw = subprocess.check_output(
                ["ps", "aux"], text=True, timeout=10,
            )
            for line in raw.strip().splitlines()[1:]:
                parts = line.split(None, 10)
                if len(parts) < 11:
                    continue
                procs.append({
                    "user": parts[0],
                    "pid": parts[1],
                    "cpu": parts[2],
                    "mem": parts[3],
                    "command": parts[10][:120],
                })
        except Exception:
            pass
        self.finished.emit(procs)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DISK USAGE WORKER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class DiskWorker(QThread):
    finished = pyqtSignal(dict)

    def run(self):
        info = {}
        try:
            usage = shutil.disk_usage("/")
            info["total_gb"] = round(usage.total / (1024**3), 1)
            info["used_gb"] = round(usage.used / (1024**3), 1)
            info["free_gb"] = round(usage.free / (1024**3), 1)
            info["percent"] = round(usage.used / usage.total * 100, 1)
        except Exception:
            info = {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0}
        self.finished.emit(info)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  UNINSTALL WORKER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class UninstallWorker(QThread):
    log = pyqtSignal(str)
    done = pyqtSignal(int, int)

    def __init__(self, items, password):
        super().__init__()
        self.items = items
        self.password = password

    def run(self):
        ok = fail = 0
        for item in self.items:
            cmd = item["uninstall_cmd"]
            self.log.emit(f"  $ {cmd}")
            try:
                needs_sudo = cmd.startswith("rm -rf") or cmd.startswith("pkgutil")
                if needs_sudo:
                    full_cmd = f"echo '{self.password}' | sudo -S {cmd}"
                else:
                    full_cmd = cmd
                r = subprocess.run(
                    full_cmd, shell=True, capture_output=True,
                    text=True, timeout=120,
                )
                if r.returncode == 0:
                    self.log.emit(f"  [OK] {item['name']} removed")
                    ok += 1
                else:
                    err = r.stderr.strip().split('\n')[-1] if r.stderr.strip() else "unknown error"
                    self.log.emit(f"  [FAIL] {err}")
                    fail += 1
            except Exception as e:
                self.log.emit(f"  [ERR] {e}")
                fail += 1
        self.done.emit(ok, fail)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONFIRM DIALOG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class HackerConfirmDialog(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("[!] CONFIRM UNINSTALL")
        self.setFixedSize(540, 380)
        self.result_action = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        warn = QLabel(f"[WARNING] You are about to DESTROY {len(items)} target(s).\n"
                      f"This requires root privileges. No undo.")
        warn.setStyleSheet(f"color: {NEON_RED}; font-size: 14px; font-weight: bold;")
        layout.addWidget(warn)
        layout.addSpacing(8)

        txt = QTextEdit()
        txt.setReadOnly(True)
        for it in items:
            txt.append(f"  > {it['name']}  [{it['kind']}]")
        layout.addWidget(txt, 1)
        layout.addSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        yes_btn = QPushButton("  [EXECUTE]  ")
        yes_btn.setObjectName("deleteBtn")
        yes_btn.clicked.connect(self._accept)
        no_btn = QPushButton("  [ABORT]  ")
        no_btn.clicked.connect(self.reject)
        btn_row.addWidget(yes_btn)
        btn_row.addWidget(no_btn)
        layout.addLayout(btn_row)

    def _accept(self):
        self.result_action = True
        self.accept()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PASSWORD DIALOG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class HackerPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("[AUTH] sudo password")
        self.setFixedSize(420, 180)
        self.password = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        lbl = QLabel("[root@localhost] ~ # Enter password for sudo:")
        lbl.setStyleSheet(f"color: {NEON_RED}; font-weight: bold;")
        layout.addWidget(lbl)
        layout.addSpacing(6)
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_input.setPlaceholderText("••••••••")
        layout.addWidget(self.pw_input)
        layout.addSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton("  [AUTHENTICATE]  ")
        ok_btn.setObjectName("scanBtn")
        ok_btn.clicked.connect(self._ok)
        cancel_btn = QPushButton("  [CANCEL]  ")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self.pw_input.returnPressed.connect(self._ok)

    def _ok(self):
        self.password = self.pw_input.text()
        if self.password:
            self.accept()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN WINDOW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ASCII_BANNER = r"""
  ██╗  ██╗██╗  ██╗ ██████╗██╗  ██╗██████╗ ██████╗
  ██║  ██║██║  ██║██╔════╝██║ ██╔╝╚════██╗██╔══██╗
  ███████║███████║██║     █████╔╝  █████╔╝██████╔╝
  ██╔══██║╚════██║██║     ██╔═██╗  ╚═══██╗██╔══██╗
  ██║  ██║     ██║╚██████╗██║  ██╗██████╔╝██║  ██║
  ╚═╝  ╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝
"""


class HackerAppManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.all_items = []
        self.filtered_items = []
        self.processes = []

        self.setWindowTitle("H4CK3R App Manager")
        self.setMinimumSize(1100, 720)
        self.setWindowIcon(make_hacker_icon(64))

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Matrix rain header ──
        self.matrix = MatrixRain()
        root.addWidget(self.matrix)

        # ── Title bar ──
        title_bar = QFrame()
        title_bar.setObjectName("titleBar")
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(16, 8, 16, 8)

        ascii_lbl = QLabel(ASCII_BANNER)
        ascii_lbl.setObjectName("headerAscii")
        ascii_lbl.setFont(QFont("Menlo", 7))
        tb_layout.addWidget(ascii_lbl)

        tb_layout.addStretch()

        # System info panel
        info_frame = QFrame()
        info_frame.setObjectName("statsBox")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 6, 10, 6)
        info_layout.setSpacing(2)

        self.sys_info_labels = []
        mac_ver = platform.mac_ver()[0]
        cpu_brand = platform.processor() or "Apple Silicon"
        infos = [
            f"OS: macOS {mac_ver}",
            f"CPU: {cpu_brand}",
            f"Host: {platform.node()}",
            f"User: {os.getenv('USER', 'root')}",
            f"Time: {datetime.now().strftime('%H:%M:%S')}",
        ]
        for txt in infos:
            lbl = QLabel(txt)
            lbl.setObjectName("sysInfoLabel")
            info_layout.addWidget(lbl)
            self.sys_info_labels.append(lbl)

        self.disk_label = QLabel("Disk: scanning...")
        self.disk_label.setObjectName("sysInfoLabel")
        info_layout.addWidget(self.disk_label)
        self.sys_info_labels.append(self.disk_label)

        tb_layout.addWidget(info_frame)
        root.addWidget(title_bar)

        # ── Tab widget ──
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        # ═══ TAB 1: Applications & Packages ═══
        tab_apps = QWidget()
        tab_apps_layout = QVBoxLayout(tab_apps)
        tab_apps_layout.setContentsMargins(8, 8, 8, 8)
        tab_apps_layout.setSpacing(6)

        # Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("toolBar")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(8, 6, 8, 6)

        self.scan_btn = QPushButton("  [SCAN ALL]  ")
        self.scan_btn.setObjectName("scanBtn")
        self.scan_btn.clicked.connect(self.start_scan)
        tb.addWidget(self.scan_btn)

        tb.addSpacing(10)
        lbl = QLabel("TYPE:")
        lbl.setObjectName("dimLabel")
        tb.addWidget(lbl)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All", "Application", "User App",
            "Brew Formula", "Brew Cask", "pip Package", "System Pkg"
        ])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        tb.addWidget(self.filter_combo)

        tb.addSpacing(6)
        lbl2 = QLabel("FIND:")
        lbl2.setObjectName("dimLabel")
        tb.addWidget(lbl2)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("grep -i ...")
        self.search_input.textChanged.connect(self.apply_filter)
        tb.addWidget(self.search_input, 1)

        tb.addSpacing(10)
        self.select_all_btn = QPushButton("  [ALL]  ")
        self.select_all_btn.setObjectName("infoBtn")
        self.select_all_btn.clicked.connect(self.select_all)
        tb.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton("  [NONE]  ")
        self.select_none_btn.clicked.connect(self.select_none)
        tb.addWidget(self.select_none_btn)

        tb.addSpacing(10)
        self.export_btn = QPushButton("  [EXPORT]  ")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.clicked.connect(self.export_list)
        self.export_btn.setEnabled(False)
        tb.addWidget(self.export_btn)

        self.delete_btn = QPushButton("  [UNINSTALL]  ")
        self.delete_btn.setObjectName("deleteBtn")
        self.delete_btn.clicked.connect(self.uninstall_selected)
        self.delete_btn.setEnabled(False)
        tb.addWidget(self.delete_btn)

        tab_apps_layout.addWidget(toolbar)

        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("[ IDLE ] Run scan to enumerate targets")
        tab_apps_layout.addWidget(self.progress)

        # Stats row
        stats_row = QHBoxLayout()
        self.stats_labels = {}
        for key in ["Applications", "Brew Formula", "Brew Cask", "pip", "System Pkg", "Total Size"]:
            box = QFrame()
            box.setObjectName("statsBox")
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(8, 4, 8, 4)
            val_lbl = QLabel("--")
            val_lbl.setStyleSheet(f"color: {NEON_CYAN}; font-size: 16px; font-weight: bold;")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            key_lbl = QLabel(key)
            key_lbl.setObjectName("dimLabel")
            key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box_layout.addWidget(val_lbl)
            box_layout.addWidget(key_lbl)
            self.stats_labels[key] = val_lbl
            stats_row.addWidget(box)
        tab_apps_layout.addLayout(stats_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            " SEL", " NAME", " VER", " SIZE", " TYPE", " PATH"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 42)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 120)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        tab_apps_layout.addWidget(self.table, 1)

        self.tabs.addTab(tab_apps, "  [PACKAGES]  ")

        # ═══ TAB 2: Process Manager ═══
        tab_proc = QWidget()
        tab_proc_layout = QVBoxLayout(tab_proc)
        tab_proc_layout.setContentsMargins(8, 8, 8, 8)
        tab_proc_layout.setSpacing(6)

        proc_toolbar = QFrame()
        proc_toolbar.setObjectName("toolBar")
        ptb = QHBoxLayout(proc_toolbar)
        ptb.setContentsMargins(8, 6, 8, 6)

        self.proc_scan_btn = QPushButton("  [SCAN PROCESSES]  ")
        self.proc_scan_btn.setObjectName("scanBtn")
        self.proc_scan_btn.clicked.connect(self.scan_processes)
        ptb.addWidget(self.proc_scan_btn)

        ptb.addSpacing(10)
        lbl3 = QLabel("FILTER:")
        lbl3.setObjectName("dimLabel")
        ptb.addWidget(lbl3)
        self.proc_search = QLineEdit()
        self.proc_search.setPlaceholderText("search process ...")
        self.proc_search.textChanged.connect(self.filter_processes)
        ptb.addWidget(self.proc_search, 1)

        ptb.addSpacing(10)
        self.kill_btn = QPushButton("  [KILL -9]  ")
        self.kill_btn.setObjectName("killBtn")
        self.kill_btn.clicked.connect(self.kill_process)
        ptb.addWidget(self.kill_btn)

        tab_proc_layout.addWidget(proc_toolbar)

        self.proc_table = QTableWidget()
        self.proc_table.setColumnCount(5)
        self.proc_table.setHorizontalHeaderLabels([
            " USER", " PID", " %CPU", " %MEM", " COMMAND"
        ])
        self.proc_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch)
        self.proc_table.setColumnWidth(0, 100)
        self.proc_table.setColumnWidth(1, 80)
        self.proc_table.setColumnWidth(2, 80)
        self.proc_table.setColumnWidth(3, 80)
        self.proc_table.verticalHeader().setVisible(False)
        self.proc_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.proc_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.proc_table.setSortingEnabled(True)
        self.proc_table.setAlternatingRowColors(True)
        tab_proc_layout.addWidget(self.proc_table, 1)

        self.tabs.addTab(tab_proc, "  [PROCESSES]  ")

        # ═══ TAB 3: Terminal / Log ═══
        tab_log = QWidget()
        tab_log_layout = QVBoxLayout(tab_log)
        tab_log_layout.setContentsMargins(8, 8, 8, 8)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Menlo", 12))
        self._log_boot_sequence()
        tab_log_layout.addWidget(self.log_area)

        self.tabs.addTab(tab_log, "  [TERMINAL]  ")

        # ── Status bar ──
        status_bar = QFrame()
        status_bar.setObjectName("statusBar")
        sb = QHBoxLayout(status_bar)
        sb.setContentsMargins(10, 4, 10, 4)
        self.status_label = QLabel("[READY]")
        self.status_label.setObjectName("statusLabel")
        sb.addWidget(self.status_label, 1)
        self.count_label = QLabel("0 targets")
        self.count_label.setObjectName("statusLabel")
        self.count_label.setStyleSheet(f"color: {NEON_CYAN};")
        sb.addWidget(self.count_label)
        root.addWidget(status_bar)

        # ── Clock timer ──
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

        # ── Boot disk scan ──
        self._scan_disk()

    # ── log boot sequence ──
    def _log_boot_sequence(self):
        lines = [
            "┌──────────────────────────────────────────────────────┐",
            "│  H4CK3R App Manager v2.0                            │",
            "│  macOS System Exploitation & Package Control         │",
            "│  ─────────────────────────────────────────────       │",
            f"│  Boot time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                       │",
            f"│  User: {os.getenv('USER', 'root'):<20s}                         │",
            "│  Status: OPERATIONAL                                 │",
            "└──────────────────────────────────────────────────────┘",
            "",
            "root@h4ck3r:~# Initializing subsystems...",
            "  [OK] GUI engine loaded",
            "  [OK] Package scanner ready",
            "  [OK] Process monitor ready",
            "  [OK] Disk analyzer ready",
            "",
            "root@h4ck3r:~# Awaiting commands...",
            "",
        ]
        for line in lines:
            self.log_area.append(line)

    def _log(self, msg):
        self.log_area.append(msg)
        self.log_area.moveCursor(QTextCursor.MoveOperation.End)

    # ── clock ──
    def _update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        if self.sys_info_labels:
            self.sys_info_labels[4].setText(f"Time: {now}")

    # ── disk scan ──
    def _scan_disk(self):
        self.disk_worker = DiskWorker()
        self.disk_worker.finished.connect(self._on_disk_done)
        self.disk_worker.start()

    def _on_disk_done(self, info):
        self.disk_label.setText(
            f"Disk: {info['used_gb']}G / {info['total_gb']}G  ({info['percent']}%)"
        )
        pct = info["percent"]
        color = NEON_GREEN if pct < 70 else NEON_ORANGE if pct < 90 else NEON_RED
        self.disk_label.setStyleSheet(f"color: {color}; font-size: 11px;")

    # ── app scanning ──
    def start_scan(self):
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("  [SCANNING...]  ")
        self.table.setRowCount(0)
        self.all_items.clear()
        self.progress.setFormat("[SCANNING] Enumerating all targets...")
        self._log("root@h4ck3r:~# Initiating full system scan...")

        self.worker = ScanWorker()
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_scan_done)
        self.worker.start()

    def _on_progress(self, pct, msg):
        self.progress.setValue(pct)
        self.progress.setFormat(msg)
        self.status_label.setText(msg)
        self._log(f"  {msg}")

    def _on_scan_done(self, items):
        self.all_items = items
        self.apply_filter()
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("  [SCAN ALL]  ")
        self.delete_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.count_label.setText(f"{len(items)} targets")
        self._log(f"  [DONE] {len(items)} targets acquired\n")
        self._update_stats()

    def _update_stats(self):
        counts = {}
        total_size = 0
        for it in self.all_items:
            k = it["kind"]
            counts[k] = counts.get(k, 0) + 1
            total_size += it.get("size_mb", 0)

        mapping = {
            "Applications": counts.get("Application", 0) + counts.get("User App", 0),
            "Brew Formula": counts.get("Brew Formula", 0),
            "Brew Cask": counts.get("Brew Cask", 0),
            "pip": counts.get("pip Package", 0),
            "System Pkg": counts.get("System Pkg", 0),
            "Total Size": f"{total_size:.0f}MB",
        }
        for key, val in mapping.items():
            if key in self.stats_labels:
                self.stats_labels[key].setText(str(val))

    # ── filtering ──
    def apply_filter(self):
        kind = self.filter_combo.currentText()
        query = self.search_input.text().lower()
        self.filtered_items = [
            it for it in self.all_items
            if (kind == "All" or it["kind"] == kind)
            and (not query or query in it["name"].lower())
        ]
        self._populate_table()

    def _populate_table(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.filtered_items))
        KIND_COLORS = {
            "Application":   QColor(ROW_APP),
            "User App":      QColor(ROW_APP),
            "Brew Formula":  QColor(ROW_BREW_FORM),
            "Brew Cask":     QColor(ROW_BREW_CASK),
            "System Pkg":    QColor(ROW_SYSTEM),
            "pip Package":   QColor(ROW_PIP),
        }
        KIND_TEXT = {
            "Application":   QColor(NEON_GREEN),
            "User App":      QColor(NEON_GREEN),
            "Brew Formula":  QColor(NEON_YELLOW),
            "Brew Cask":     QColor(NEON_CYAN),
            "System Pkg":    QColor(NEON_RED),
            "pip Package":   QColor(NEON_PURPLE),
        }
        for row, item in enumerate(self.filtered_items):
            chk = QCheckBox()
            chk.setStyleSheet(f"""
                QCheckBox::indicator {{
                    width: 14px; height: 14px;
                    border: 1px solid {NEON_GREEN_DARK};
                    background: {BG_DARKEST};
                }}
                QCheckBox::indicator:checked {{
                    background: {NEON_GREEN};
                }}
            """)
            chk_widget = QWidget()
            chk_widget.setStyleSheet(f"background: transparent;")
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, chk_widget)

            bg = KIND_COLORS.get(item["kind"], QColor(BG_TABLE))
            fg = KIND_TEXT.get(item["kind"], QColor(NEON_GREEN))

            for col, val in enumerate([
                "", item["name"], item["version"],
                f"{item['size_mb']}M" if item["size_mb"] else "-",
                item["kind"],
                item.get("path") or item["name"],
            ]):
                if col == 0:
                    continue
                cell = QTableWidgetItem(val)
                cell.setBackground(bg)
                cell.setForeground(fg)
                self.table.setItem(row, col, cell)

        self.table.setSortingEnabled(True)
        self.count_label.setText(
            f"{len(self.filtered_items)}/{len(self.all_items)} targets"
        )

    # ── select all / none ──
    def select_all(self):
        for row in range(self.table.rowCount()):
            w = self.table.cellWidget(row, 0)
            if w:
                chk = w.findChild(QCheckBox)
                if chk:
                    chk.setChecked(True)

    def select_none(self):
        for row in range(self.table.rowCount()):
            w = self.table.cellWidget(row, 0)
            if w:
                chk = w.findChild(QCheckBox)
                if chk:
                    chk.setChecked(False)

    # ── export ──
    def export_list(self):
        if not self.all_items:
            return
        out_path = os.path.expanduser("~/Desktop/h4ck3r_export.txt")
        with open(out_path, "w") as f:
            f.write(f"# H4CK3R App Manager — Export\n")
            f.write(f"# Date: {datetime.now().isoformat()}\n")
            f.write(f"# Total: {len(self.all_items)} items\n")
            f.write(f"{'='*80}\n\n")
            for it in self.all_items:
                f.write(f"[{it['kind']:<14}]  {it['name']:<40}  v{it['version']:<12}  "
                        f"{it['size_mb']}MB\n")
        self._log(f"root@h4ck3r:~# Exported to {out_path}")
        self.status_label.setText(f"[EXPORT] Saved to {out_path}")

    # ── uninstall ──
    def _get_checked_items(self):
        checked = []
        for row in range(self.table.rowCount()):
            w = self.table.cellWidget(row, 0)
            if w:
                chk = w.findChild(QCheckBox)
                if chk and chk.isChecked():
                    checked.append(self.filtered_items[row])
        return checked

    def uninstall_selected(self):
        items = self._get_checked_items()
        if not items:
            QMessageBox.warning(
                self, "[!] No Selection",
                "Select targets before executing uninstall."
            )
            return

        dlg = HackerConfirmDialog(items, self)
        if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.result_action:
            return

        pw_dlg = HackerPasswordDialog(self)
        if pw_dlg.exec() != QDialog.DialogCode.Accepted:
            return

        self.delete_btn.setEnabled(False)
        self.tabs.setCurrentIndex(2)  # Switch to terminal
        self._log("root@h4ck3r:~# ═══ UNINSTALL SEQUENCE INITIATED ═══")

        self.uninst_worker = UninstallWorker(items, pw_dlg.password)
        self.uninst_worker.log.connect(self._log)
        self.uninst_worker.done.connect(self._on_uninst_done)
        self.uninst_worker.start()

    def _on_uninst_done(self, ok, fail):
        self._log(f"\nroot@h4ck3r:~# ═══ COMPLETE: {ok} removed, {fail} failed ═══\n")
        self.delete_btn.setEnabled(True)
        self.status_label.setText(f"[DONE] {ok} removed, {fail} failed")
        QTimer.singleShot(1000, self.start_scan)

    # ── process management ──
    def scan_processes(self):
        self.proc_scan_btn.setEnabled(False)
        self.proc_scan_btn.setText("  [SCANNING...]  ")
        self._log("root@h4ck3r:~# ps aux ...")
        self.proc_worker = ProcessWorker()
        self.proc_worker.finished.connect(self._on_proc_done)
        self.proc_worker.start()

    def _on_proc_done(self, procs):
        self.processes = procs
        self.filter_processes()
        self.proc_scan_btn.setEnabled(True)
        self.proc_scan_btn.setText("  [SCAN PROCESSES]  ")
        self._log(f"  [DONE] {len(procs)} processes found\n")

    def filter_processes(self):
        query = self.proc_search.text().lower()
        filtered = [p for p in self.processes
                    if not query or query in p["command"].lower()
                    or query in p["user"].lower()]

        self.proc_table.setSortingEnabled(False)
        self.proc_table.setRowCount(len(filtered))
        for row, proc in enumerate(filtered):
            cpu_val = float(proc["cpu"])
            mem_val = float(proc["mem"])

            for col, val in enumerate([
                proc["user"], proc["pid"], proc["cpu"],
                proc["mem"], proc["command"]
            ]):
                cell = QTableWidgetItem(val)
                cell.setForeground(QColor(NEON_GREEN))
                # Highlight heavy processes
                if col == 2 and cpu_val > 50:
                    cell.setForeground(QColor(NEON_RED))
                elif col == 2 and cpu_val > 10:
                    cell.setForeground(QColor(NEON_ORANGE))
                if col == 3 and mem_val > 10:
                    cell.setForeground(QColor(NEON_RED))
                elif col == 3 and mem_val > 3:
                    cell.setForeground(QColor(NEON_ORANGE))
                # Sort numerically for CPU/MEM/PID
                if col in (1, 2, 3):
                    try:
                        cell.setData(Qt.ItemDataRole.UserRole, float(val))
                    except ValueError:
                        pass
                self.proc_table.setItem(row, col, cell)

        self.proc_table.setSortingEnabled(True)

    def kill_process(self):
        row = self.proc_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "[!]", "Select a process to kill.")
            return
        pid_item = self.proc_table.item(row, 1)
        cmd_item = self.proc_table.item(row, 4)
        if not pid_item:
            return
        pid = pid_item.text()
        cmd = cmd_item.text() if cmd_item else ""

        reply = QMessageBox.question(
            self, "[KILL]",
            f"Send SIGKILL to PID {pid}?\n\n{cmd[:80]}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                subprocess.run(["kill", "-9", pid], timeout=5)
                self._log(f"root@h4ck3r:~# kill -9 {pid}  [OK]")
                self.status_label.setText(f"[KILLED] PID {pid}")
                QTimer.singleShot(500, self.scan_processes)
            except Exception as e:
                self._log(f"  [FAIL] {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Force dark palette as base
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG_DARKEST))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(NEON_GREEN))
    palette.setColor(QPalette.ColorRole.Base, QColor(BG_DARK))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(BG_PANEL))
    palette.setColor(QPalette.ColorRole.Text, QColor(NEON_GREEN))
    palette.setColor(QPalette.ColorRole.Button, QColor(BG_PANEL))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(NEON_GREEN))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(NEON_GREEN_DARK))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(BG_DARK))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(NEON_GREEN))
    app.setPalette(palette)

    app.setStyleSheet(HACKER_CSS)
    app.setFont(QFont("Menlo", 12))

    window = HackerAppManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
