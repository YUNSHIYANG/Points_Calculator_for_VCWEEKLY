"""
应用启动入口

PyInstaller打包入口点，处理模块导入兼容性。
"""

import sys
import os

# 将 src 目录添加到 Python 路径
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后运行
    base_path = sys._MEIPASS
else:
    # 开发环境运行
    base_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(base_path, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

from weekly_score.app import WeeklyScoreApp

if __name__ == "__main__":
    app = WeeklyScoreApp()
    sys.exit(app.run())
