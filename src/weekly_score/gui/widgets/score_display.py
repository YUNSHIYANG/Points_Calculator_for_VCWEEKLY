"""
得分展示组件

实现得分的动态展示效果。
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QPalette
from typing import Optional, Union


class ScoreDisplay(QWidget):
    """得分展示组件"""
    
    def __init__(self, label: str = "", value: float = 0.0, parent: Optional[QWidget] = None):
        """
        初始化得分展示组件
        
        Args:
            label: 标签文本
            value: 初始值
            parent: 父控件
        """
        super().__init__(parent)
        self.label = label
        self._value = value
        self._display_value = 0.0
        self._animation_duration = 500
        self._decimal_places = 2
        
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # 标签
        self.label_widget = QLabel(self.label)
        self.label_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.label_widget.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #616161;
                background-color: transparent;
            }
        """)
        layout.addWidget(self.label_widget)
        
        # 数值显示
        self.value_widget = QLabel(self.format_value(self._value))
        self.value_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value_widget.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 600;
                color: #1A1A1A;
                background-color: transparent;
            }
        """)
        layout.addWidget(self.value_widget)
        
        # 设置最小尺寸
        self.setMinimumSize(120, 80)
    
    def setup_animation(self):
        """设置动画"""
        self.animation = QPropertyAnimation(self, b"displayValue")
        self.animation.setDuration(self._animation_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def format_value(self, value: float) -> str:
        """
        格式化数值显示
        
        Args:
            value: 数值
            
        Returns:
            格式化后的字符串
        """
        if self._decimal_places == 0:
            return f"{int(value):,}"
        else:
            return f"{value:,.{self._decimal_places}f}"
    
    def setValue(self, value: float, animate: bool = True):
        """
        设置数值
        
        Args:
            value: 新数值
            animate: 是否使用动画
        """
        if animate and self._value != value:
            # 使用动画过渡
            self.animation.setStartValue(self._value)
            self.animation.setEndValue(value)
            self.animation.start()
        else:
            # 直接设置
            self._value = value
            self._display_value = value
            self.value_widget.setText(self.format_value(value))
        
        # 根据数值设置颜色
        self.update_color(value)
    
    def update_color(self, value: float):
        """
        根据数值更新颜色
        
        Args:
            value: 数值
        """
        if value > 0:
            color = "#107C10"  # 绿色
        elif value < 0:
            color = "#D83B01"  # 红色
        else:
            color = "#1A1A1A"  # 默认颜色
        
        self.value_widget.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: 600;
                color: {color};
                background-color: transparent;
            }}
        """)
    
    @pyqtProperty(float)
    def displayValue(self):
        """获取显示值"""
        return self._display_value
    
    @displayValue.setter
    def displayValue(self, value: float):
        """设置显示值"""
        self._display_value = value
        self.value_widget.setText(self.format_value(value))
    
    def setLabel(self, label: str):
        """
        设置标签文本
        
        Args:
            label: 标签文本
        """
        self.label = label
        self.label_widget.setText(label)
    
    def setDecimalPlaces(self, places: int):
        """
        设置小数位数
        
        Args:
            places: 小数位数
        """
        self._decimal_places = places
        self.value_widget.setText(self.format_value(self._display_value))
    
    def setAnimationDuration(self, duration: int):
        """
        设置动画时长
        
        Args:
            duration: 动画时长（毫秒）
        """
        self._animation_duration = duration
        self.animation.setDuration(duration)