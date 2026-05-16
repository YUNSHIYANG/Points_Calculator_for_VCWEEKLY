"""
样式定义模块

包含Fluent Design主题和样式定义。
"""

try:
    from .fluent_theme import FluentTheme
except ImportError:
    from weekly_score.gui.styles.fluent_theme import FluentTheme

__all__ = ["FluentTheme"]