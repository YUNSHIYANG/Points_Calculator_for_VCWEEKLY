"""
输入框组件

实现现代化的输入框组件。
"""

from PyQt6.QtWidgets import QLineEdit, QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPen, QFontMetrics
from typing import Optional, Callable


class InputField(QWidget):
    """输入框组件"""
    
    def __init__(self, placeholder: str = "", label: str = "", parent: Optional[QWidget] = None):
        """
        初始化输入框
        
        Args:
            placeholder: 占位符文本
            label: 标签文本
            parent: 父控件
        """
        super().__init__(parent)
        self.placeholder = placeholder
        self.label = label
        self._focus = False
        self._error = False
        self._error_message = ""
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 标签
        if self.label:
            self.label_widget = QLabel(self.label)
            self.label_widget.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    font-weight: 500;
                    color: #1A1A1A;
                    background-color: transparent;
                }
            """)
            layout.addWidget(self.label_widget)
        
        # 输入框容器
        self.container = QWidget()
        self.container.setObjectName("inputContainer")
        self.container.setFixedHeight(40)
        
        # 输入框
        self.input = QLineEdit()
        self.input.setPlaceholderText(self.placeholder)
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                color: #1A1A1A;
            }
            QLineEdit:focus {
                border: 2px solid #0078D4;
            }
            QLineEdit:disabled {
                background-color: #F3F3F3;
                color: #616161;
            }
        """)
        
        # 连接信号
        self.input.textChanged.connect(self.on_text_changed)
        self.input.returnPressed.connect(self.on_return_pressed)
        
        # 创建容器布局
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.input)
        
        layout.addWidget(self.container)
        
        # 错误消息
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #D83B01;
                background-color: transparent;
            }
        """)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # 设置最小尺寸
        self.setMinimumWidth(200)
    
    def setup_animations(self):
        """设置动画"""
        self.border_animation = QPropertyAnimation(self.container, b"borderColor")
        self.border_animation.setDuration(200)
        self.border_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def on_text_changed(self, text: str):
        """文本改变事件"""
        # 清除错误状态
        if self._error:
            self.clear_error()
    
    def on_return_pressed(self):
        """回车键按下事件"""
        # 可以在这里添加回车键处理逻辑
        pass
    
    def text(self) -> str:
        """获取输入文本"""
        return self.input.text()
    
    def setText(self, text: str):
        """设置输入文本"""
        self.input.setText(text)
    
    def setPlaceholderText(self, text: str):
        """设置占位符文本"""
        self.placeholder = text
        self.input.setPlaceholderText(text)
    
    def setError(self, message: str):
        """
        设置错误状态
        
        Args:
            message: 错误消息
        """
        self._error = True
        self._error_message = message
        
        # 更新样式
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #D83B01;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                color: #1A1A1A;
            }
            QLineEdit:focus {
                border: 2px solid #D83B01;
            }
        """)
        
        # 显示错误消息
        self.error_label.setText(message)
        self.error_label.show()
    
    def clear_error(self):
        """清除错误状态"""
        self._error = False
        self._error_message = ""
        
        # 恢复默认样式
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                color: #1A1A1A;
            }
            QLineEdit:focus {
                border: 2px solid #0078D4;
            }
        """)
        
        # 隐藏错误消息
        self.error_label.hide()
    
    def setEnabled(self, enabled: bool):
        """设置启用状态"""
        self.input.setEnabled(enabled)
        super().setEnabled(enabled)
    
    def focusInEvent(self, event):
        """获得焦点事件"""
        self._focus = True
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        """失去焦点事件"""
        self._focus = False
        super().focusOutEvent(event)