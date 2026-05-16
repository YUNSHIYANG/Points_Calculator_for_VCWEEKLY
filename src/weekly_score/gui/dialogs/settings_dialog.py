"""
设置对话框模块

提供应用设置的配置界面。
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QPushButton, QLabel, QGroupBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import Dict, Any
import logging

try:
    from ...utils.config import Config
except ImportError:
    from weekly_score.utils.config import Config

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """设置对话框类"""
    
    def __init__(self, config: Config, parent=None):
        """
        初始化设置对话框
        
        Args:
            config: 配置管理器
            parent: 父窗口
        """
        super().__init__(parent)
        self.config = config
        self.original_config = config._config.copy()
        
        self.setup_ui()
        self.load_settings()
        
        logger.info("设置对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_general_tab()
        self.create_api_tab()
        self.create_excel_tab()
        self.create_gui_tab()
        self.create_logging_tab()
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # 重置按钮
        self.reset_btn = QPushButton("重置为默认")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        # 添加弹性空间
        button_layout.addStretch()
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        # 确定按钮
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """创建通用设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        # 应用信息组
        app_group = QGroupBox("应用信息")
        app_layout = QFormLayout(app_group)
        
        # 应用名称
        self.app_name_edit = QLineEdit()
        app_layout.addRow("应用名称:", self.app_name_edit)
        
        # 版本
        self.version_edit = QLineEdit()
        self.version_edit.setReadOnly(True)
        app_layout.addRow("版本:", self.version_edit)
        
        # 作者
        self.author_edit = QLineEdit()
        app_layout.addRow("作者:", self.author_edit)
        
        layout.addWidget(app_group)
        
        # 缓存设置组
        cache_group = QGroupBox("缓存设置")
        cache_layout = QFormLayout(cache_group)
        
        # 启用缓存
        self.cache_enabled_check = QCheckBox("启用缓存")
        cache_layout.addRow(self.cache_enabled_check)
        
        # 缓存目录
        cache_dir_layout = QHBoxLayout()
        self.cache_dir_edit = QLineEdit()
        cache_dir_layout.addWidget(self.cache_dir_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_cache_dir)
        cache_dir_layout.addWidget(browse_btn)
        
        cache_layout.addRow("缓存目录:", cache_dir_layout)
        
        # 最大缓存大小
        self.cache_max_size_spin = QSpinBox()
        self.cache_max_size_spin.setRange(10, 10000)
        self.cache_max_size_spin.setSuffix(" MB")
        cache_layout.addRow("最大缓存大小:", self.cache_max_size_spin)
        
        layout.addWidget(cache_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "通用")
    
    def create_api_tab(self):
        """创建API设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        # API设置组
        api_group = QGroupBox("API设置")
        api_layout = QFormLayout(api_group)
        
        # 基础URL
        self.api_base_url_edit = QLineEdit()
        api_layout.addRow("基础URL:", self.api_base_url_edit)
        
        # 超时时间
        self.api_timeout_spin = QSpinBox()
        self.api_timeout_spin.setRange(1, 60)
        self.api_timeout_spin.setSuffix(" 秒")
        api_layout.addRow("请求超时:", self.api_timeout_spin)
        
        # 重试次数
        self.api_retry_spin = QSpinBox()
        self.api_retry_spin.setRange(0, 10)
        api_layout.addRow("重试次数:", self.api_retry_spin)
        
        # 缓存TTL
        self.api_cache_ttl_spin = QSpinBox()
        self.api_cache_ttl_spin.setRange(0, 3600)
        self.api_cache_ttl_spin.setSuffix(" 秒")
        api_layout.addRow("缓存有效期:", self.api_cache_ttl_spin)
        
        layout.addWidget(api_group)
        
        # 验证设置组
        validation_group = QGroupBox("输入验证")
        validation_layout = QFormLayout(validation_group)
        
        # BV号正则表达式
        self.bvid_pattern_edit = QLineEdit()
        validation_layout.addRow("BV号正则:", self.bvid_pattern_edit)
        
        # 最大输入长度
        self.max_input_length_spin = QSpinBox()
        self.max_input_length_spin.setRange(1, 100)
        validation_layout.addRow("最大输入长度:", self.max_input_length_spin)
        
        layout.addWidget(validation_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "API")
    
    def create_excel_tab(self):
        """创建Excel设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        # Excel设置组
        excel_group = QGroupBox("Excel设置")
        excel_layout = QFormLayout(excel_group)
        
        # 默认工作表
        self.excel_sheet_edit = QLineEdit()
        excel_layout.addRow("默认工作表:", self.excel_sheet_edit)
        
        # 数据行
        self.excel_data_row_spin = QSpinBox()
        self.excel_data_row_spin.setRange(1, 1000)
        excel_layout.addRow("数据行:", self.excel_data_row_spin)
        
        # 基数行
        self.excel_base_row_spin = QSpinBox()
        self.excel_base_row_spin.setRange(1, 1000)
        excel_layout.addRow("基数行:", self.excel_base_row_spin)
        
        # 列范围
        self.excel_column_range_edit = QLineEdit()
        excel_layout.addRow("列范围:", self.excel_column_range_edit)
        
        # 自动保存
        self.excel_auto_save_check = QCheckBox("自动保存")
        excel_layout.addRow(self.excel_auto_save_check)
        
        layout.addWidget(excel_group)
        
        # 模板设置组
        template_group = QGroupBox("模板设置")
        template_layout = QFormLayout(template_group)
        
        # 模板目录
        template_dir_layout = QHBoxLayout()
        self.template_dir_edit = QLineEdit()
        template_dir_layout.addWidget(self.template_dir_edit)
        
        template_browse_btn = QPushButton("浏览...")
        template_browse_btn.clicked.connect(self.browse_template_dir)
        template_dir_layout.addWidget(template_browse_btn)
        
        template_layout.addRow("模板目录:", template_dir_layout)
        
        layout.addWidget(template_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Excel")
    
    def create_gui_tab(self):
        """创建GUI设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        # 外观设置组
        appearance_group = QGroupBox("外观设置")
        appearance_layout = QFormLayout(appearance_group)
        
        # 主题
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色"])
        appearance_layout.addRow("主题:", self.theme_combo)
        
        # 语言
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        appearance_layout.addRow("语言:", self.language_combo)
        
        layout.addWidget(appearance_group)
        
        # 窗口设置组
        window_group = QGroupBox("窗口设置")
        window_layout = QFormLayout(window_group)
        
        # 窗口宽度
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 2560)
        self.window_width_spin.setSuffix(" px")
        window_layout.addRow("窗口宽度:", self.window_width_spin)
        
        # 窗口高度
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 1440)
        self.window_height_spin.setSuffix(" px")
        window_layout.addRow("窗口高度:", self.window_height_spin)
        
        # 最小宽度
        self.min_width_spin = QSpinBox()
        self.min_width_spin.setRange(600, 1920)
        self.min_width_spin.setSuffix(" px")
        window_layout.addRow("最小宽度:", self.min_width_spin)
        
        # 最小高度
        self.min_height_spin = QSpinBox()
        self.min_height_spin.setRange(400, 1080)
        self.min_height_spin.setSuffix(" px")
        window_layout.addRow("最小高度:", self.min_height_spin)
        
        layout.addWidget(window_group)
        
        # 效果设置组
        effects_group = QGroupBox("效果设置")
        effects_layout = QFormLayout(effects_group)
        
        # 亚克力效果
        self.acrylic_check = QCheckBox("启用亚克力效果")
        effects_layout.addRow(self.acrylic_check)
        
        # 动画效果
        self.animation_check = QCheckBox("启用动画效果")
        effects_layout.addRow(self.animation_check)
        
        layout.addWidget(effects_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "界面")
    
    def create_logging_tab(self):
        """创建日志设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        # 日志设置组
        logging_group = QGroupBox("日志设置")
        logging_layout = QFormLayout(logging_group)
        
        # 日志级别
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addRow("日志级别:", self.log_level_combo)
        
        # 日志文件
        log_file_layout = QHBoxLayout()
        self.log_file_edit = QLineEdit()
        log_file_layout.addWidget(self.log_file_edit)
        
        log_browse_btn = QPushButton("浏览...")
        log_browse_btn.clicked.connect(self.browse_log_file)
        log_file_layout.addWidget(log_browse_btn)
        
        logging_layout.addRow("日志文件:", log_file_layout)
        
        # 最大大小
        self.log_max_size_spin = QSpinBox()
        self.log_max_size_spin.setRange(1, 100)
        self.log_max_size_spin.setSuffix(" MB")
        logging_layout.addRow("最大文件大小:", self.log_max_size_spin)
        
        # 备份数量
        self.log_backup_count_spin = QSpinBox()
        self.log_backup_count_spin.setRange(0, 20)
        logging_layout.addRow("备份数量:", self.log_backup_count_spin)
        
        # 控制台输出
        self.log_console_check = QCheckBox("输出到控制台")
        logging_layout.addRow(self.log_console_check)
        
        layout.addWidget(logging_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "日志")
    
    def load_settings(self):
        """加载设置到界面"""
        # 通用设置
        self.app_name_edit.setText(self.config.get("app.name", ""))
        self.version_edit.setText(self.config.get("app.version", ""))
        self.author_edit.setText(self.config.get("app.author", ""))
        
        # 缓存设置
        self.cache_enabled_check.setChecked(self.config.get("cache.enabled", True))
        self.cache_dir_edit.setText(self.config.get("cache.directory", "cache"))
        self.cache_max_size_spin.setValue(self.config.get("cache.max_size", 100))
        
        # API设置
        self.api_base_url_edit.setText(self.config.get("api.base_url", ""))
        self.api_timeout_spin.setValue(self.config.get("api.timeout", 10))
        self.api_retry_spin.setValue(self.config.get("api.retry_count", 3))
        self.api_cache_ttl_spin.setValue(self.config.get("api.cache_ttl", 300))
        
        # 验证设置
        self.bvid_pattern_edit.setText(self.config.get("validation.bvid_pattern", ""))
        self.max_input_length_spin.setValue(self.config.get("validation.max_input_length", 20))
        
        # Excel设置
        self.excel_sheet_edit.setText(self.config.get("excel.default_sheet", "Sheet1"))
        self.excel_data_row_spin.setValue(self.config.get("excel.data_row", 4))
        self.excel_base_row_spin.setValue(self.config.get("excel.base_row", 5))
        self.excel_column_range_edit.setText(self.config.get("excel.column_range", "B:G"))
        self.excel_auto_save_check.setChecked(self.config.get("excel.auto_save", True))
        self.template_dir_edit.setText(self.config.get("resources.templates", "resources/templates"))
        
        # GUI设置
        theme = self.config.get("gui.theme", "light")
        self.theme_combo.setCurrentIndex(0 if theme == "light" else 1)
        
        language = self.config.get("gui.language", "zh_CN")
        self.language_combo.setCurrentIndex(0 if language == "zh_CN" else 1)
        
        self.window_width_spin.setValue(self.config.get("gui.window_width", 1200))
        self.window_height_spin.setValue(self.config.get("gui.window_height", 800))
        self.min_width_spin.setValue(self.config.get("gui.min_width", 1000))
        self.min_height_spin.setValue(self.config.get("gui.min_height", 600))
        
        self.acrylic_check.setChecked(self.config.get("gui.acrylic_enabled", True))
        self.animation_check.setChecked(self.config.get("gui.animation_enabled", True))
        
        # 日志设置
        self.log_level_combo.setCurrentText(self.config.get("logging.level", "INFO"))
        self.log_file_edit.setText(self.config.get("logging.file", "logs/app.log"))
        self.log_max_size_spin.setValue(self.config.get("logging.max_size", 10))
        self.log_backup_count_spin.setValue(self.config.get("logging.backup_count", 5))
        self.log_console_check.setChecked(self.config.get("logging.console_output", True))
    
    def save_settings(self):
        """保存设置到配置"""
        # 通用设置
        self.config.set("app.name", self.app_name_edit.text())
        self.config.set("app.author", self.author_edit.text())
        
        # 缓存设置
        self.config.set("cache.enabled", self.cache_enabled_check.isChecked())
        self.config.set("cache.directory", self.cache_dir_edit.text())
        self.config.set("cache.max_size", self.cache_max_size_spin.value())
        
        # API设置
        self.config.set("api.base_url", self.api_base_url_edit.text())
        self.config.set("api.timeout", self.api_timeout_spin.value())
        self.config.set("api.retry_count", self.api_retry_spin.value())
        self.config.set("api.cache_ttl", self.api_cache_ttl_spin.value())
        
        # 验证设置
        self.config.set("validation.bvid_pattern", self.bvid_pattern_edit.text())
        self.config.set("validation.max_input_length", self.max_input_length_spin.value())
        
        # Excel设置
        self.config.set("excel.default_sheet", self.excel_sheet_edit.text())
        self.config.set("excel.data_row", self.excel_data_row_spin.value())
        self.config.set("excel.base_row", self.excel_base_row_spin.value())
        self.config.set("excel.column_range", self.excel_column_range_edit.text())
        self.config.set("excel.auto_save", self.excel_auto_save_check.isChecked())
        self.config.set("resources.templates", self.template_dir_edit.text())
        
        # GUI设置
        theme = "light" if self.theme_combo.currentIndex() == 0 else "dark"
        self.config.set("gui.theme", theme)
        
        language = "zh_CN" if self.language_combo.currentIndex() == 0 else "en"
        self.config.set("gui.language", language)
        
        self.config.set("gui.window_width", self.window_width_spin.value())
        self.config.set("gui.window_height", self.window_height_spin.value())
        self.config.set("gui.min_width", self.min_width_spin.value())
        self.config.set("gui.min_height", self.min_height_spin.value())
        
        self.config.set("gui.acrylic_enabled", self.acrylic_check.isChecked())
        self.config.set("gui.animation_enabled", self.animation_check.isChecked())
        
        # 日志设置
        self.config.set("logging.level", self.log_level_combo.currentText())
        self.config.set("logging.file", self.log_file_edit.text())
        self.config.set("logging.max_size", self.log_max_size_spin.value())
        self.config.set("logging.backup_count", self.log_backup_count_spin.value())
        self.config.set("logging.console_output", self.log_console_check.isChecked())
        
        logger.info("设置已保存")
    
    def accept_settings(self):
        """接受设置"""
        # 验证设置
        if not self.validate_settings():
            return
        
        # 保存设置
        self.save_settings()
        
        # 保存到文件
        self.config.save_config()
        
        # 接受对话框
        self.accept()
    
    def validate_settings(self) -> bool:
        """
        验证设置
        
        Returns:
            bool: 验证是否通过
        """
        # 验证API超时时间
        if self.api_timeout_spin.value() <= 0:
            QMessageBox.warning(self, "验证错误", "API超时时间必须大于0")
            return False
        
        # 验证重试次数
        if self.api_retry_spin.value() < 0:
            QMessageBox.warning(self, "验证错误", "重试次数不能为负数")
            return False
        
        # 验证窗口尺寸
        if self.window_width_spin.value() < self.min_width_spin.value():
            QMessageBox.warning(self, "验证错误", "窗口宽度不能小于最小宽度")
            return False
        
        if self.window_height_spin.value() < self.min_height_spin.value():
            QMessageBox.warning(self, "验证错误", "窗口高度不能小于最小高度")
            return False
        
        # 验证Excel行号
        if self.excel_data_row_spin.value() <= 0 or self.excel_base_row_spin.value() <= 0:
            QMessageBox.warning(self, "验证错误", "Excel行号必须大于0")
            return False
        
        return True
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        reply = QMessageBox.question(
            self,
            "确认重置",
            "确定要将所有设置重置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 恢复原始配置
            self.config._config = self.original_config.copy()
            self.load_settings()
            logger.info("设置已重置为默认值")
    
    def browse_cache_dir(self):
        """浏览缓存目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择缓存目录")
        if directory:
            self.cache_dir_edit.setText(directory)
    
    def browse_template_dir(self):
        """浏览模板目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择模板目录")
        if directory:
            self.template_dir_edit.setText(directory)
    
    def browse_log_file(self):
        """浏览日志文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择日志文件",
            "",
            "日志文件 (*.log);;所有文件 (*)"
        )
        if file_path:
            self.log_file_edit.setText(file_path)
    
    def closeEvent(self, event):
        """关闭事件"""
        # 检查是否有未保存的更改
        if self.config._config != self.original_config:
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "有未保存的更改，确定要关闭吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        event.accept()