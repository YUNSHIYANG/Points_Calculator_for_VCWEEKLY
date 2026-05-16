"""
GUI界面模块

基于PyQt6的Fluent Design界面实现。
"""

try:
    from .main_window import MainWindow
except ImportError:
    from weekly_score.gui.main_window import MainWindow

__all__ = ["MainWindow"]