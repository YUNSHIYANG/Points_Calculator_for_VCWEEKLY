"""
主窗口模块

实现应用主窗口界面。
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QStatusBar, QMenuBar, QMenu,
    QGroupBox, QGridLayout, QFrame, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QFont, QColor
import logging
from pathlib import Path
from typing import Optional, Dict

try:
    from ..utils.config import Config
    from ..utils.validators import validate_bvid
    from ..core.api import BilibiliAPI, APIError, NetworkError, APIResponseError
    from ..core.calculator import WeeklyScoreCalculator
    from ..core.excel_io import ExcelManager, ExcelError
    from ..core.models import VideoStats, ScoreResult, DeltaStats
    from .styles.fluent_theme import FluentTheme
    from .widgets import FluentCard, ScoreDisplay, InputField
    from .dialogs.settings_dialog import SettingsDialog
except ImportError:
    from weekly_score.utils.config import Config
    from weekly_score.utils.validators import validate_bvid
    from weekly_score.core.api import BilibiliAPI, APIError, NetworkError, APIResponseError
    from weekly_score.core.calculator import WeeklyScoreCalculator
    from weekly_score.core.excel_io import ExcelManager, ExcelError
    from weekly_score.core.models import VideoStats, ScoreResult, DeltaStats
    from weekly_score.gui.styles.fluent_theme import FluentTheme
    from weekly_score.gui.widgets import FluentCard, ScoreDisplay, InputField
    from weekly_score.gui.dialogs.settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 定义信号
    data_updated = pyqtSignal(dict)
    
    def __init__(self, config: Config):
        """
        初始化主窗口
        
        Args:
            config: 配置管理器
        """
        super().__init__()
        self.config = config
        self.theme = FluentTheme(config.get("gui.theme", "light"))
        self.api = BilibiliAPI(
            timeout=config.get("api.timeout", 10),
            retry_count=config.get("api.retry_count", 3),
            cache_ttl=config.get("api.cache_ttl", 300)
        )
        self.calculator = WeeklyScoreCalculator()
        
        # 应用模式：simple 或 advanced
        self.mode = "simple"
        
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
        
        logger.info("主窗口初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        # 设置窗口标题
        self.setWindowTitle("B站周刊得点计算器")
        
        # 设置窗口大小
        width = self.config.get("gui.window_width", 1200)
        height = self.config.get("gui.window_height", 800)
        self.resize(width, height)
        
        # 设置最小大小
        min_width = self.config.get("gui.min_width", 1000)
        min_height = self.config.get("gui.min_height", 600)
        self.setMinimumSize(min_width, min_height)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建顶部区域
        self.create_top_area(main_layout)
        
        # 创建数据展示区域
        self.create_data_area(main_layout)
        
        # 创建底部状态栏
        self.create_status_bar()
        
        # 初始模式下隐藏增量卡片
        self.delta_card.hide()
        
        # 设置窗口居中
        self.center_window()
        
        logger.debug("主窗口UI初始化完成")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 设置动作
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        # 模式切换
        mode_menu = view_menu.addMenu("模式")
        
        mode_group = QActionGroup(self)
        mode_group.setExclusive(True)
        
        simple_mode = QAction("简单模式", self)
        simple_mode.setCheckable(True)
        simple_mode.setChecked(True)
        simple_mode.triggered.connect(lambda: self.switch_mode("simple"))
        mode_group.addAction(simple_mode)
        mode_menu.addAction(simple_mode)
        
        advanced_mode = QAction("高级模式", self)
        advanced_mode.setCheckable(True)
        advanced_mode.triggered.connect(lambda: self.switch_mode("advanced"))
        mode_group.addAction(advanced_mode)
        mode_menu.addAction(advanced_mode)
        
        # 主题切换
        theme_menu = view_menu.addMenu("主题")
        
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        
        light_theme = QAction("浅色主题", self)
        light_theme.setCheckable(True)
        light_theme.setChecked(True)
        light_theme.triggered.connect(lambda: self.switch_theme("light"))
        theme_group.addAction(light_theme)
        theme_menu.addAction(light_theme)
        
        dark_theme = QAction("深色主题", self)
        dark_theme.setCheckable(True)
        dark_theme.triggered.connect(lambda: self.switch_theme("dark"))
        theme_group.addAction(dark_theme)
        theme_menu.addAction(dark_theme)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_top_area(self, parent_layout: QVBoxLayout):
        """创建顶部区域"""
        # 顶部容器
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(16)
        
        # 应用标题
        title_label = QLabel("B站周刊得点计算器")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 600;
                color: #0078D4;
                background-color: transparent;
            }
        """)
        top_layout.addWidget(title_label)
        
        # 添加弹性空间
        top_layout.addStretch()
        
        # 输入区域
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)
        
        # BV号输入框
        self.bvid_input = InputField(
            placeholder="请输入BV号，如：BV1GJ411x7h7",
            label="BV号"
        )
        self.bvid_input.setFixedWidth(300)
        input_layout.addWidget(self.bvid_input)
        
        # 查询按钮
        self.query_btn = QPushButton("查询")
        self.query_btn.setFixedSize(80, 40)
        self.query_btn.clicked.connect(self.query_data)
        input_layout.addWidget(self.query_btn)
        
        # 北京时间显示
        self.time_label = QLabel("北京时间：--")
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #616161;
                background-color: transparent;
            }
        """)
        input_layout.addWidget(self.time_label)
        
        top_layout.addWidget(input_widget)
        
        parent_layout.addWidget(top_widget)
    
    def create_data_area(self, parent_layout: QVBoxLayout):
        """创建数据展示区域"""
        # 数据容器
        data_widget = QWidget()
        data_layout = QHBoxLayout(data_widget)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(16)
        
        # 第一列：总原始数据
        self.total_card = FluentCard("总原始数据")
        self.setup_total_card()
        data_layout.addWidget(self.total_card)
        
        # 第二列：增量数据
        self.delta_card = FluentCard("本期增量数据")
        self.setup_delta_card()
        data_layout.addWidget(self.delta_card)
        
        # 第三列：得分结果
        self.score_card = FluentCard("本期周刊得点")
        self.setup_score_card()
        data_layout.addWidget(self.score_card)
        
        parent_layout.addWidget(data_widget)
    
    def setup_total_card(self):
        """设置总数据卡片"""
        # 创建网格布局
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        
        # 数据字段
        fields = [
            ("播放量", "view"), ("点赞量", "like"), ("弹幕量", "danmaku"),
            ("评论量", "reply"), ("硬币量", "coin"), ("收藏量", "favorite")
        ]
        
        self.total_displays = {}
        for i, (label, key) in enumerate(fields):
            # 标签
            label_widget = QLabel(label)
            label_widget.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #616161;
                    background-color: transparent;
                }
            """)
            grid_layout.addWidget(label_widget, i, 0)
            
            # 数值显示
            display = ScoreDisplay(value=0.0)
            display.setDecimalPlaces(0)
            grid_layout.addWidget(display, i, 1)
            
            self.total_displays[key] = display
        
        self.total_card.addLayout(grid_layout)
    
    def setup_delta_card(self):
        """设置增量数据卡片"""
        # 创建网格布局
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        
        # 数据字段
        fields = [
            ("播放量", "view"), ("点赞量", "like"), ("弹幕量", "danmaku"),
            ("评论量", "reply"), ("硬币量", "coin"), ("收藏量", "favorite")
        ]
        
        self.delta_displays = {}
        for i, (label, key) in enumerate(fields):
            # 标签
            label_widget = QLabel(label)
            label_widget.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #616161;
                    background-color: transparent;
                }
            """)
            grid_layout.addWidget(label_widget, i, 0)
            
            # 数值显示
            display = ScoreDisplay(value=0.0)
            display.setDecimalPlaces(0)
            grid_layout.addWidget(display, i, 1)
            
            self.delta_displays[key] = display
        
        self.delta_card.addLayout(grid_layout)
    
    def setup_score_card(self):
        """设置得分卡片"""
        # 创建网格布局
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        
        # 得分字段
        fields = [
            ("播放得点", "play"), ("互动得点", "interaction"),
            ("收藏得点", "favorite_points"), ("硬币得点", "coin_points"),
            ("点赞得点", "like_points"), ("最终得点", "total")
        ]
        
        self.score_displays = {}
        for i, (label, key) in enumerate(fields):
            # 标签
            label_widget = QLabel(label)
            label_widget.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #616161;
                    background-color: transparent;
                }
            """)
            grid_layout.addWidget(label_widget, i, 0)
            
            # 数值显示
            display = ScoreDisplay(value=0.0)
            display.setDecimalPlaces(2)
            grid_layout.addWidget(display, i, 1)
            
            self.score_displays[key] = display
        
        self.score_card.addLayout(grid_layout)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 版本信息
        version_label = QLabel("版本 3.0.0")
        self.status_bar.addWidget(version_label)
        
        # 版权信息
        copyright_label = QLabel("相关计算公式来源于B站中V周刊组，本计算器由云师阳(1866643210)制作")
        self.status_bar.addPermanentWidget(copyright_label)
    
    def setup_connections(self):
        """设置信号连接"""
        # 输入框回车键连接
        self.bvid_input.input.returnPressed.connect(self.query_data)
    
    def apply_theme(self):
        """应用主题"""
        # 重建主题对象（支持主题切换）
        theme_name = self.config.get("gui.theme", "light")
        self.theme = FluentTheme(theme_name)
        
        stylesheet = self.theme.get_stylesheet()
        self.setStyleSheet(stylesheet)
        
        # 应用或移除亚克力效果
        if self.config.get("gui.acrylic_enabled", True):
            self.theme.get_acrylic_effect(self, 0.95)
        else:
            self.theme.remove_acrylic_effect(self)
        
        # 应用或移除动画效果
        if self.config.get("gui.animation_enabled", True):
            self._apply_animations()
        else:
            self._remove_animations()
    
    def _apply_animations(self):
        """为交互控件添加动画效果"""
        if not hasattr(self, '_animations_applied') or not self._animations_applied:
            # 为按钮添加悬停动画
            for btn in self.findChildren(QPushButton):
                self.theme.apply_button_hover_animation(btn)
            self._animations_applied = True
    
    def _remove_animations(self):
        """移除所有动画效果"""
        if hasattr(self, '_animations_applied') and self._animations_applied:
            # 移除按钮的悬停动画事件过滤器
            for btn in self.findChildren(QPushButton):
                if hasattr(btn, '_hover_animator'):
                    btn.removeEventFilter(btn._hover_animator)
                    del btn._hover_animator
            self._animations_applied = False
    
    def center_window(self):
        """将窗口居中显示"""
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
    
    def switch_mode(self, mode: str):
        """
        切换应用模式
        
        Args:
            mode: 模式类型，"simple" 或 "advanced"
        """
        self.mode = mode
        logger.info(f"切换到{mode}模式")
        
        # 更新界面
        if mode == "simple":
            # 简单模式：只显示总数据和得分
            self.delta_card.hide()
        else:
            # 高级模式：显示所有三列
            self.delta_card.show()
    
    def switch_theme(self, theme: str):
        """
        切换主题
        
        Args:
            theme: 主题类型，"light" 或 "dark"
        """
        self.theme = FluentTheme(theme)
        self.apply_theme()
        self.config.set("gui.theme", theme)
        logger.info(f"切换到{theme}主题")
    
    def query_data(self):
        """查询数据"""
        # 获取BV号
        bvid = self.bvid_input.text().strip()
        
        # 验证BV号
        is_valid, error_message = validate_bvid(bvid)
        if not is_valid:
            self.bvid_input.setError(error_message)
            return
        
        # 清除错误状态
        self.bvid_input.clear_error()
        
        # 禁用查询按钮
        self.query_btn.setEnabled(False)
        self.query_btn.setText("查询中...")
        
        try:
            # 获取视频数据
            total_stats = self.api.get_video_stats(bvid)
            
            # 解析服务器时间
            server_time = self.api.parse_server_time(total_stats.server_time)
            if server_time:
                self.time_label.setText(f"北京时间：{server_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 更新总数据
            self.update_total_display(total_stats)
            
            # 如果是高级模式，读取基数并计算增量
            if self.mode == "advanced":
                self.process_advanced_mode(bvid, total_stats)
            else:
                # 简单模式：直接计算得分
                score_result = self.calculator.calculate_score(total_stats)
                self.update_score_display(score_result)
            
            logger.info(f"数据查询成功: {bvid}")
            
        except NetworkError as e:
            QMessageBox.critical(self, "网络错误", f"网络请求失败: {e}")
            logger.error(f"网络错误: {e}")
        except APIResponseError as e:
            QMessageBox.critical(self, "API错误", f"API返回错误: {e}")
            logger.error(f"API错误: {e}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生未知错误: {e}")
            logger.error(f"未知错误: {e}")
        finally:
            # 恢复查询按钮
            self.query_btn.setEnabled(True)
            self.query_btn.setText("查询")
    
    def process_advanced_mode(self, bvid: str, total_stats: VideoStats):
        """
        处理高级模式
        
        Args:
            bvid: BV号
            total_stats: 总统计数据
        """
        try:
            # 构建Excel文件路径
            template_dir = self.config.get("resources.templates", "resources/templates")
            excel_path = Path(template_dir) / f"{bvid}.xlsx"
            sheet_name = self.config.get("excel.default_sheet", "Sheet1")
            
            # 读取基数
            with ExcelManager(excel_path, sheet_name) as excel_manager:
                base_stats = excel_manager.read_base_stats()
                
                # 计算增量
                delta_stats = self.calculator.calculate_delta(total_stats, base_stats)
                
                # 更新增量显示
                self.update_delta_display(delta_stats)
                
                # 计算得分
                score_result = self.calculator.calculate_score(delta_stats)
                self.update_score_display(score_result)
                
                # 写入数据到Excel
                beijing_time = self.api.parse_server_time(total_stats.server_time)
                if beijing_time:
                    beijing_time_str = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
                    excel_manager.write_stats(total_stats, beijing_time_str)
                
                logger.info(f"高级模式处理完成: {bvid}")
                
        except ExcelError as e:
            QMessageBox.warning(self, "Excel错误", f"Excel操作失败: {e}")
            logger.error(f"Excel错误: {e}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"处理失败: {e}")
            logger.error(f"处理错误: {e}")
    
    def update_total_display(self, stats: VideoStats):
        """更新总数据展示"""
        self.total_displays["view"].setValue(float(stats.view))
        self.total_displays["like"].setValue(float(stats.like))
        self.total_displays["danmaku"].setValue(float(stats.danmaku))
        self.total_displays["reply"].setValue(float(stats.reply))
        self.total_displays["coin"].setValue(float(stats.coin))
        self.total_displays["favorite"].setValue(float(stats.favorite))
    
    def update_delta_display(self, stats: DeltaStats):
        """更新增量数据展示"""
        self.delta_displays["view"].setValue(float(stats.view))
        self.delta_displays["like"].setValue(float(stats.like))
        self.delta_displays["danmaku"].setValue(float(stats.danmaku))
        self.delta_displays["reply"].setValue(float(stats.reply))
        self.delta_displays["coin"].setValue(float(stats.coin))
        self.delta_displays["favorite"].setValue(float(stats.favorite))
    
    def update_score_display(self, score: ScoreResult):
        """更新得分展示"""
        self.score_displays["play"].setValue(score.play_points)
        self.score_displays["interaction"].setValue(score.interaction_points)
        self.score_displays["favorite_points"].setValue(score.favorite_points)
        self.score_displays["coin_points"].setValue(score.coin_points)
        self.score_displays["like_points"].setValue(score.like_points)
        self.score_displays["total"].setValue(score.total_points)
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            # 设置已更新，重新应用主题
            self.apply_theme()
            logger.info("设置已更新")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "B站周刊得点计算器 v3.0.0\n\n"
            "基于Bilibili视频数据的周刊得点计算工具。\n\n"
            "计算公式来源于B站中V周刊组。\n"
            "代码实现：云师阳 (B站UID: 1866643210)\n\n"
            "本作品采用 CC BY-NC-SA 4.0 协议。"
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        # 保存配置
        self.config.save_config()
        
        # 关闭API会话
        self.api.close()
        
        logger.info("主窗口关闭")
        event.accept()