"""
应用主模块

提供应用初始化和主窗口管理。
"""

import sys
from PyQt6.QtWidgets import QApplication
from pathlib import Path
import logging

# 支持直接运行、模块导入和 PyInstaller 打包三种方式
try:
    from .gui.main_window import MainWindow
    from .utils.config import Config
    from .utils.logger import setup_logger
except ImportError:
    from weekly_score.gui.main_window import MainWindow
    from weekly_score.utils.config import Config
    from weekly_score.utils.logger import setup_logger

logger = logging.getLogger(__name__)


class WeeklyScoreApp:
    """周刊得点计算器应用"""
    
    def __init__(self):
        """初始化应用"""
        # PyQt6 默认支持高 DPI，无需手动设置
        
        # 创建应用实例
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("周刊得点计算器")
        self.app.setApplicationVersion("3.0.0")
        self.app.setOrganizationName("VCWEEKLY Calculator")
        
        # 加载配置
        config_path = Path("config/settings.toml")
        self.config = Config(config_path)
        
        # 设置日志
        log_file = Path(self.config.get("logging.file", "logs/app.log"))
        log_level = logging.DEBUG if self.config.get("logging.level") == "DEBUG" else logging.INFO
        setup_logger(
            name="weekly_score",
            log_file=log_file,
            level=log_level,
            max_size=self.config.get("logging.max_size", 10) * 1024 * 1024,
            backup_count=self.config.get("logging.backup_count", 5),
            console_output=self.config.get("logging.console_output", True)
        )
        
        logger.info("应用初始化完成")
        
        # 创建主窗口
        self.window = MainWindow(self.config)
    
    def run(self):
        """运行应用"""
        logger.info("应用启动")
        self.window.show()
        return self.app.exec()
    
    def cleanup(self):
        """清理资源"""
        logger.info("应用关闭")
        # 保存配置
        self.config.save_config()


if __name__ == "__main__":
    # 直接运行此文件时启动应用
    app = WeeklyScoreApp()
    sys.exit(app.run())