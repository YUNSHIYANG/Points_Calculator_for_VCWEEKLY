"""
Fluent Design主题系统

实现Windows Fluent Design视觉风格。
"""

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPainter, QBrush, QLinearGradient
from typing import Dict, Any
import sys


class FluentTheme:
    """Fluent Design主题管理器"""
    
    # 主题颜色
    COLORS = {
        "light": {
            "primary": "#0078D4",
            "primary_dark": "#005A9E",
            "primary_light": "#60CDFF",
            "background": "#F3F3F3",
            "surface": "#FFFFFF",
            "surface_variant": "#F9F9F9",
            "on_surface": "#1A1A1A",
            "on_surface_variant": "#616161",
            "outline": "#E0E0E0",
            "error": "#D83B01",
            "success": "#107C10",
            "warning": "#A4262C",
            "info": "#0078D4"
        },
        "dark": {
            "primary": "#60CDFF",
            "primary_dark": "#0078D4",
            "primary_light": "#98DFFF",
            "background": "#202020",
            "surface": "#2D2D2D",
            "surface_variant": "#383838",
            "on_surface": "#FFFFFF",
            "on_surface_variant": "#B3B3B3",
            "outline": "#404040",
            "error": "#FF993B",
            "success": "#6CCB5F",
            "warning": "#FCE100",
            "info": "#60CDFF"
        }
    }
    
    # 字体设置
    FONTS = {
        "family": "Microsoft YaHei UI",
        "heading": {
            "size": 18,
            "weight": 600
        },
        "subheading": {
            "size": 14,
            "weight": 500
        },
        "body": {
            "size": 13,
            "weight": 400
        },
        "caption": {
            "size": 11,
            "weight": 400
        }
    }
    
    # 圆角设置
    BORDER_RADIUS = {
        "small": 4,
        "medium": 8,
        "large": 12,
        "extra_large": 16
    }
    
    # 阴影设置
    SHADOWS = {
        "small": "0px 2px 4px rgba(0, 0, 0, 0.1)",
        "medium": "0px 4px 8px rgba(0, 0, 0, 0.12)",
        "large": "0px 8px 16px rgba(0, 0, 0, 0.14)"
    }
    
    def __init__(self, theme: str = "light"):
        """
        初始化主题管理器
        
        Args:
            theme: 主题类型，"light" 或 "dark"
        """
        self.theme = theme
        self.colors = self.COLORS[theme]
    
    def get_stylesheet(self) -> str:
        """
        获取全局样式表
        
        Returns:
            CSS样式字符串
        """
        return f"""
        /* 全局样式 */
        QWidget {{
            font-family: {self.FONTS['family']};
            font-size: {self.FONTS['body']['size']}px;
            color: {self.colors['on_surface']};
            background-color: {self.colors['background']};
        }}
        
        /* 主窗口样式 */
        QMainWindow {{
            background-color: {self.colors['background']};
        }}
        
        /* 标签样式 */
        QLabel {{
            color: {self.colors['on_surface']};
            background-color: transparent;
        }}
        
        /* 输入框样式 */
        QLineEdit {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['outline']};
            border-radius: {self.BORDER_RADIUS['small']}px;
            padding: 8px 12px;
            color: {self.colors['on_surface']};
            selection-background-color: {self.colors['primary']};
        }}
        
        QLineEdit:focus {{
            border: 2px solid {self.colors['primary']};
        }}
        
        /* 按钮样式 */
        QPushButton {{
            background-color: {self.colors['primary']};
            color: white;
            border: none;
            border-radius: {self.BORDER_RADIUS['small']}px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {self.colors['primary_dark']};
        }}
        
        QPushButton:pressed {{
            background-color: {self.colors['primary_dark']};
        }}
        
        QPushButton:disabled {{
            background-color: {self.colors['outline']};
            color: {self.colors['on_surface_variant']};
        }}
        
        /* 卡片样式 */
        .FluentCard {{
            background-color: {self.colors['surface']};
            border-radius: {self.BORDER_RADIUS['medium']}px;
            border: 1px solid {self.colors['outline']};
            padding: 16px;
        }}
        
        .FluentCard:hover {{
            border: 1px solid {self.colors['primary']};
            {self.SHADOWS['medium']}
        }}
        
        /* 分组框样式 */
        QGroupBox {{
            font-weight: 600;
            border: 1px solid {self.colors['outline']};
            border-radius: {self.BORDER_RADIUS['medium']}px;
            margin-top: 12px;
            padding-top: 16px;
            background-color: {self.colors['surface']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            color: {self.colors['on_surface']};
        }}
        
        /* 滚动条样式 */
        QScrollBar:vertical {{
            background-color: {self.colors['background']};
            width: 8px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.colors['outline']};
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.colors['on_surface_variant']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* 状态栏样式 */
        QStatusBar {{
            background-color: {self.colors['surface']};
            border-top: 1px solid {self.colors['outline']};
            color: {self.colors['on_surface_variant']};
        }}
        
        /* 菜单栏样式 */
        QMenuBar {{
            background-color: {self.colors['surface']};
            border-bottom: 1px solid {self.colors['outline']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.colors['surface_variant']};
        }}
        
        QMenu {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['outline']};
            border-radius: {self.BORDER_RADIUS['small']}px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 24px;
            border-radius: {self.BORDER_RADIUS['small']}px;
        }}
        
        QMenu::item:selected {{
            background-color: {self.colors['surface_variant']};
        }}
        """
    
    def get_acrylic_effect(self, widget: QWidget, opacity: float = 0.8):
        """
        应用亚克力效果
        
        Args:
            widget: 目标控件
            opacity: 透明度
        """
        # 设置半透明背景
        palette = widget.palette()
        background_color = QColor(self.colors['background'])
        background_color.setAlphaF(opacity)
        palette.setColor(widget.backgroundRole(), background_color)
        widget.setPalette(palette)
        
        # 设置自动填充背景
        widget.setAutoFillBackground(True)
    
    def remove_acrylic_effect(self, widget: QWidget):
        """
        移除亚克力效果，恢复不透明背景
        
        Args:
            widget: 目标控件
        """
        palette = widget.palette()
        background_color = QColor(self.colors['background'])
        background_color.setAlpha(255)
        palette.setColor(widget.backgroundRole(), background_color)
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)
    
    def add_animation(self, widget: QWidget, property: str, start_value: Any, end_value: Any, duration: int = 200):
        """
        添加属性动画
        
        Args:
            widget: 目标控件
            property: 属性名称
            start_value: 起始值
            end_value: 结束值
            duration: 动画时长（毫秒）
        """
        animation = QPropertyAnimation(widget, property.encode())
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        
        # 保持动画引用
        if not hasattr(widget, '_animations'):
            widget._animations = []
        widget._animations.append(animation)
    
    def apply_button_hover_animation(self, button: 'QPushButton'):
        """
        为按钮添加悬停动画效果
        
        Args:
            button: 目标按钮
        """
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtCore import QEvent, QObject
        
        class HoverAnimator(QObject):
            """按钮悬停动画管理器"""
            def __init__(self, button, theme_colors, parent=None):
                super().__init__(parent)
                self.button = button
                self.theme_colors = theme_colors
                self._enter_anim = None
                self._leave_anim = None
            
            def eventFilter(self, obj, event):
                if obj != self.button:
                    return False
                if event.type() == QEvent.Type.Enter:
                    self._start_hover_animation(True)
                elif event.type() == QEvent.Type.Leave:
                    self._start_hover_animation(False)
                return False
            
            def _start_hover_animation(self, entering):
                from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
                anim = QPropertyAnimation(self.button, b"geometry")
                anim.setDuration(150)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                
                geo = self.button.geometry()
                if entering:
                    anim.setStartValue(geo)
                    expanded = geo.adjusted(-2, -1, 2, 1)
                    anim.setEndValue(expanded)
                else:
                    anim.setStartValue(geo)
                    shrunk = geo.adjusted(2, 1, -2, -1)
                    anim.setEndValue(shrunk)
                
                anim.start()
                # Keep reference to prevent garbage collection
                if entering:
                    self._enter_anim = anim
                else:
                    self._leave_anim = anim
        
        # Install event filter
        animator = HoverAnimator(button, self.colors, button)
        button.installEventFilter(animator)
        # Keep reference on the button to prevent garbage collection
        if not hasattr(button, '_hover_animator'):
            button._hover_animator = animator
    
    def apply_shadow(self, widget: QWidget, shadow_type: str = "medium"):
        """
        应用阴影效果
        
        Args:
            widget: 目标控件
            shadow_type: 阴影类型
        """
        # 注意：PyQt6中需要使用QGraphicsDropShadowEffect
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        widget.setGraphicsEffect(shadow)