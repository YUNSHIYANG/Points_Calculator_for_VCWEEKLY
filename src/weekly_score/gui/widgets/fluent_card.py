"""
Fluent Design卡片组件

实现现代化的卡片式布局。
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QBrush, QLinearGradient, QPen
from typing import Optional


class FluentCard(QFrame):
    """Fluent Design卡片组件"""
    
    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        """
        初始化卡片
        
        Args:
            title: 卡片标题
            parent: 父控件
        """
        super().__init__(parent)
        self.title = title
        self._hovered = False
        self._border_color = QColor("#E0E0E0")
        self._background_color = QColor("#FFFFFF")
        self._shadow_opacity = 0.1
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """设置用户界面"""
        # 设置卡片样式
        self.setObjectName("FluentCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrameShadow(QFrame.Shadow.Plain)
        
        # 设置最小尺寸
        self.setMinimumSize(200, 150)
        
        # 创建布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)
        
        # 添加标题
        if self.title:
            self.title_label = QLabel(self.title)
            self.title_label.setObjectName("cardTitle")
            self.title_label.setStyleSheet("""
                QLabel#cardTitle {
                    font-size: 16px;
                    font-weight: 600;
                    color: #1A1A1A;
                    background-color: transparent;
                }
            """)
            self.main_layout.addWidget(self.title_label)
        
        # 内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.main_layout.addWidget(self.content_widget)
        
        # 设置默认样式
        self.update_style()
    
    def setup_animations(self):
        """设置动画"""
        # 边框颜色动画
        self.border_animation = QPropertyAnimation(self, b"borderColor")
        self.border_animation.setDuration(200)
        self.border_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 背景颜色动画
        self.background_animation = QPropertyAnimation(self, b"backgroundColor")
        self.background_animation.setDuration(200)
        self.background_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def update_style(self):
        """更新样式"""
        style = f"""
        #FluentCard {{
            background-color: {self._background_color.name()};
            border: 1px solid {self._border_color.name()};
            border-radius: 8px;
        }}
        """
        self.setStyleSheet(style)
    
    def addWidget(self, widget: QWidget):
        """添加控件到内容区域"""
        self.content_layout.addWidget(widget)
    
    def addLayout(self, layout):
        """添加布局到内容区域"""
        self.content_layout.addLayout(layout)
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self._hovered = True
        self.animate_hover(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._hovered = False
        self.animate_hover(False)
        super().leaveEvent(event)
    
    def animate_hover(self, hover: bool):
        """
        执行悬停动画
        
        Args:
            hover: 是否悬停
        """
        if hover:
            # 悬停时边框变为主题色
            self.border_animation.setStartValue(self._border_color)
            self.border_animation.setEndValue(QColor("#0078D4"))
            self.border_animation.start()
            
            # 添加阴影效果
            self.setGraphicsEffect(self.create_shadow_effect())
        else:
            # 恢复默认边框
            self.border_animation.setStartValue(self._border_color)
            self.border_animation.setEndValue(QColor("#E0E0E0"))
            self.border_animation.start()
            
            # 移除阴影效果
            self.setGraphicsEffect(None)
    
    def create_shadow_effect(self):
        """创建阴影效果"""
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        return shadow
    
    @pyqtProperty(QColor)
    def borderColor(self):
        """获取边框颜色"""
        return self._border_color
    
    @borderColor.setter
    def borderColor(self, color: QColor):
        """设置边框颜色"""
        self._border_color = color
        self.update_style()
    
    @pyqtProperty(QColor)
    def backgroundColor(self):
        """获取背景颜色"""
        return self._background_color
    
    @backgroundColor.setter
    def backgroundColor(self, color: QColor):
        """设置背景颜色"""
        self._background_color = color
        self.update_style()