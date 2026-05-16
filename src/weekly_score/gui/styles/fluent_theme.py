"""
Fluent Design主题系统

实现Windows Fluent Design视觉风格。
"""

from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QEvent, QObject
from PyQt6.QtGui import QColor, QPainter, QBrush, QLinearGradient
from typing import Dict, Any
import sys
import logging

logger = logging.getLogger(__name__)


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
    
    def _hex_to_rgba(self, hex_color: str, alpha: int = 255) -> str:
        """将十六进制颜色转为 rgba 字符串"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    
    def get_stylesheet(self, acrylic_enabled: bool = False) -> str:
        """
        获取全局样式表
        
        Args:
            acrylic_enabled: 是否启用亚克力效果（影响背景透明度）
        
        Returns:
            CSS样式字符串
        """
        # 根据亚克力开关决定背景颜色
        if acrylic_enabled:
            main_bg = self._hex_to_rgba(self.colors['background'], 230)  # ~90% 不透明
            surface_bg = self._hex_to_rgba(self.colors['surface'], 220)   # ~86% 不透明
        else:
            main_bg = self.colors['background']
            surface_bg = self.colors['surface']
        
        return f"""
        /* 全局样式 */
        QWidget {{
            font-family: {self.FONTS['family']};
            font-size: {self.FONTS['body']['size']}px;
            color: {self.colors['on_surface']};
            background-color: {main_bg};
        }}
        
        /* 主窗口样式 */
        QMainWindow {{
            background-color: {main_bg};
        }}
        
        /* 标签样式 */
        QLabel {{
            color: {self.colors['on_surface']};
            background-color: transparent;
        }}
        
        /* 输入框样式 */
        QLineEdit {{
            background-color: {surface_bg};
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
            background-color: {surface_bg};
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
            background-color: {surface_bg};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            color: {self.colors['on_surface']};
        }}
        
        /* 滚动条样式 */
        QScrollBar:vertical {{
            background-color: {main_bg};
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
            background-color: {surface_bg};
            border-top: 1px solid {self.colors['outline']};
            color: {self.colors['on_surface_variant']};
        }}
        
        /* 菜单栏样式 */
        QMenuBar {{
            background-color: {surface_bg};
            border-bottom: 1px solid {self.colors['outline']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.colors['surface_variant']};
        }}
        
        QMenu {{
            background-color: {surface_bg};
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
        
        /* 复选框样式 */
        QCheckBox {{
            spacing: 8px;
            color: {self.colors['on_surface']};
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {self.colors['outline']};
            background-color: {surface_bg};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {self.colors['primary']};
            border-color: {self.colors['primary']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {self.colors['primary']};
        }}
        
        /* 组合框样式 */
        QComboBox {{
            background-color: {surface_bg};
            border: 1px solid {self.colors['outline']};
            border-radius: {self.BORDER_RADIUS['small']}px;
            padding: 6px 12px;
            color: {self.colors['on_surface']};
        }}
        
        QComboBox:hover {{
            border-color: {self.colors['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        
        /* 旋转框样式 */
        QSpinBox {{
            background-color: {surface_bg};
            border: 1px solid {self.colors['outline']};
            border-radius: {self.BORDER_RADIUS['small']}px;
            padding: 6px 12px;
            color: {self.colors['on_surface']};
        }}
        
        QSpinBox:hover {{
            border-color: {self.colors['primary']};
        }}
        
        /* 选项卡样式 */
        QTabWidget::pane {{
            border: 1px solid {self.colors['outline']};
            border-radius: {self.BORDER_RADIUS['small']}px;
            background-color: {surface_bg};
        }}
        
        QTabBar::tab {{
            background-color: {self.colors['surface_variant']};
            border: 1px solid {self.colors['outline']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: {self.BORDER_RADIUS['small']}px;
            border-top-right-radius: {self.BORDER_RADIUS['small']}px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {surface_bg};
            border-bottom-color: {surface_bg};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {self.colors['primary_light']};
        }}
        """
    
    def apply_acrylic_effect(self, widget: QWidget):
        """
        应用Windows亚克力模糊效果
        
        使用Windows DWM API实现真正的亚克力背景模糊。
        非Windows平台或API不可用时降级为半透明背景。
        
        Args:
            widget: 目标窗口（通常是QMainWindow）
        """
        if sys.platform != 'win32':
            logger.debug("非Windows平台，跳过亚克力效果")
            return
        
        try:
            import ctypes
            from ctypes import wintypes, Structure, POINTER, c_int, c_uint, c_size_t
            
            hwnd = int(widget.winId())
            
            class ACCENT_POLICY(Structure):
                _fields_ = [
                    ("AccentState", c_int),
                    ("AccentFlags", c_int),
                    ("GradientColor", c_uint),
                    ("AnimationId", c_int),
                ]
            
            class WINDOWCOMPOSITIONATTRIBDATA(Structure):
                _fields_ = [
                    ("Attribute", c_int),
                    ("Data", POINTER(ACCENT_POLICY)),
                    ("SizeOfData", c_size_t),
                ]
            
            # ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
            accent = ACCENT_POLICY()
            accent.AccentState = 4
            accent.AccentFlags = 2  # ACCENT_FLAG_DRAW_ALL
            # GradientColor: AABBGGRR 格式，alpha ~0xCC (80%)
            bg_color = QColor(self.colors['background'])
            accent.GradientColor = (0xCC << 24) | (bg_color.blue() << 16) | (bg_color.green() << 8) | bg_color.red()
            accent.AnimationId = 0
            
            data = WINDOWCOMPOSITIONATTRIBDATA()
            data.Attribute = 19  # WCA_ACCENT_POLICY
            data.Data = ctypes.pointer(accent)
            data.SizeOfData = ctypes.sizeof(accent)
            
            result = ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
            if result:
                logger.info("Windows亚克力效果已启用")
            else:
                logger.warning("SetWindowCompositionAttribute调用失败，降级为半透明背景")
                widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        except Exception as e:
            logger.warning(f"应用亚克力效果失败: {e}，降级为半透明背景")
            widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    
    def remove_acrylic_effect(self, widget: QWidget):
        """
        移除Windows亚克力模糊效果，恢复不透明背景
        
        Args:
            widget: 目标窗口
        """
        if sys.platform != 'win32':
            return
        
        # 先移除半透明属性
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        try:
            import ctypes
            from ctypes import Structure, POINTER, c_int, c_uint, c_size_t
            
            hwnd = int(widget.winId())
            
            class ACCENT_POLICY(Structure):
                _fields_ = [
                    ("AccentState", c_int),
                    ("AccentFlags", c_int),
                    ("GradientColor", c_uint),
                    ("AnimationId", c_int),
                ]
            
            class WINDOWCOMPOSITIONATTRIBDATA(Structure):
                _fields_ = [
                    ("Attribute", c_int),
                    ("Data", POINTER(ACCENT_POLICY)),
                    ("SizeOfData", c_size_t),
                ]
            
            # ACCENT_DISABLED = 0
            accent = ACCENT_POLICY()
            accent.AccentState = 0
            accent.AccentFlags = 0
            accent.GradientColor = 0
            accent.AnimationId = 0
            
            data = WINDOWCOMPOSITIONATTRIBDATA()
            data.Attribute = 19
            data.Data = ctypes.pointer(accent)
            data.SizeOfData = ctypes.sizeof(accent)
            
            ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
            logger.info("Windows亚克力效果已禁用")
        except Exception as e:
            logger.debug(f"移除亚克力效果时出错（可忽略）: {e}")
    
    def add_animation(self, widget: QWidget, property_name: str, start_value: Any, end_value: Any, duration: int = 200):
        """
        添加属性动画
        
        Args:
            widget: 目标控件
            property_name: 属性名称
            start_value: 起始值
            end_value: 结束值
            duration: 动画时长（毫秒）
        """
        animation = QPropertyAnimation(widget, property_name.encode())
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        
        # 保持动画引用
        if not hasattr(widget, '_animations'):
            widget._animations = []
        widget._animations.append(animation)
    
    def apply_button_hover_animation(self, button):
        """
        为按钮添加悬停透明度动画效果
        
        Args:
            button: 目标按钮
        """
        animator = HoverAnimator(button, self.colors, button)
        button.installEventFilter(animator)
        button._hover_animator = animator
    
    def remove_button_hover_animation(self, button):
        """
        移除按钮的悬停动画效果
        
        Args:
            button: 目标按钮
        """
        if hasattr(button, '_hover_animator'):
            button.removeEventFilter(button._hover_animator)
            del button._hover_animator
    
    def animate_widget_show(self, widget: QWidget, duration: int = 200):
        """
        控件显示动画（淡入）
        
        Args:
            widget: 目标控件
            duration: 动画时长（毫秒）
        """
        if not widget.graphicsEffect() or not isinstance(widget.graphicsEffect(), QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        
        effect = widget.graphicsEffect()
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        
        # 保持引用
        if not hasattr(widget, '_show_animations'):
            widget._show_animations = []
        widget._show_animations.append(anim)
        
        widget.show()
    
    def animate_widget_hide(self, widget: QWidget, duration: int = 200):
        """
        控件隐藏动画（淡出）
        
        Args:
            widget: 目标控件
            duration: 动画时长（毫秒）
        """
        if not widget.graphicsEffect() or not isinstance(widget.graphicsEffect(), QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        
        effect = widget.graphicsEffect()
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(widget.hide)
        anim.start()
        
        # 保持引用
        if not hasattr(widget, '_hide_animations'):
            widget._hide_animations = []
        widget._hide_animations.append(anim)
    
    def apply_shadow(self, widget: QWidget, shadow_type: str = "medium"):
        """
        应用阴影效果
        
        Args:
            widget: 目标控件
            shadow_type: 阴影类型
        """
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        widget.setGraphicsEffect(shadow)


class HoverAnimator(QObject):
    """按钮悬停动画管理器 - 使用透明度过渡替代几何形变"""
    
    def __init__(self, button, theme_colors, parent=None):
        super().__init__(parent)
        self.button = button
        self.theme_colors = theme_colors
        self._anim = None
        self._original_style = None
    
    def eventFilter(self, obj, event):
        if obj != self.button:
            return False
        
        if event.type() == QEvent.Type.Enter:
            self._apply_hover_effect(True)
        elif event.type() == QEvent.Type.Leave:
            self._apply_hover_effect(False)
        elif event.type() == QEvent.Type.MouseButtonPress:
            self._apply_press_effect()
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self._apply_hover_effect(True)
        
        return False
    
    def _apply_hover_effect(self, entering):
        """应用悬停效果：通过透明度动画"""
        if not self.button.graphicsEffect() or not isinstance(self.button.graphicsEffect(), QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(self.button)
            self.button.setGraphicsEffect(effect)
        
        effect = self.button.graphicsEffect()
        
        if self._anim is not None:
            self._anim.stop()
        
        self._anim = QPropertyAnimation(effect, b"opacity")
        self._anim.setDuration(100)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        if entering:
            self._anim.setStartValue(effect.opacity())
            self._anim.setEndValue(1.0)
        else:
            self._anim.setStartValue(effect.opacity())
            self._anim.setEndValue(0.85)
        
        self._anim.start()
    
    def _apply_press_effect(self):
        """应用按下效果"""
        if not self.button.graphicsEffect() or not isinstance(self.button.graphicsEffect(), QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(self.button)
            self.button.setGraphicsEffect(effect)
        
        effect = self.button.graphicsEffect()
        
        if self._anim is not None:
            self._anim.stop()
        
        self._anim = QPropertyAnimation(effect, b"opacity")
        self._anim.setDuration(80)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setStartValue(effect.opacity())
        self._anim.setEndValue(0.7)
        self._anim.start()
