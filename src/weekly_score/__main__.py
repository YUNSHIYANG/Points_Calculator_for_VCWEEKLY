"""
应用入口点

允许使用 python -m weekly_score 运行应用。
"""

import sys

try:
    from .app import WeeklyScoreApp
except ImportError:
    from weekly_score.app import WeeklyScoreApp


def main():
    """主函数"""
    app = WeeklyScoreApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()