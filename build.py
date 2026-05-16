"""
打包构建脚本

用于构建周刊得点计算器的可执行文件。
"""

import subprocess
import sys
from pathlib import Path


def build():
    """执行打包构建"""
    project_root = Path(__file__).parent
    
    print("=" * 60)
    print("周刊得点计算器 - 打包构建")
    print("=" * 60)
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("错误: PyInstaller未安装，请运行: pip install pyinstaller")
        sys.exit(1)
    
    # 检查spec文件是否存在
    spec_file = project_root / "weekly_score.spec"
    if not spec_file.exists():
        print(f"错误: 找不到spec文件: {spec_file}")
        sys.exit(1)
    
    # 执行打包
    print("\n开始打包...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n打包成功！")
        print(f"输出目录: {project_root / 'dist' / '周刊得点计算器'}")
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败: {e}")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build()