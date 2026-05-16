# B站周刊得点计算器 v3.0

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey)

基于 Bilibili 视频数据的周刊得点计算工具，采用现代化 Fluent Design 界面设计。

## 功能介绍

- **一键查询**：输入 BV 号即可获取视频统计数据并计算周刊得点
- **双模式支持**：简单模式（直接查询）/ 高级模式（增量计算，需配合 Excel 模板）
- **Fluent Design 界面**：现代化卡片式布局，支持浅色/深色主题切换
- **亚克力效果**：半透明背景材质（可在设置中开关）
- **动画效果**：按钮悬停动画（可在设置中开关）

## 下载安装

### 方式一：直接运行 EXE（推荐）

1. 从 [Releases](https://github.com/your-username/Points_Calculator_for_VCWEEKLY/releases) 页面下载最新版本
2. 解压后双击 `weekly_score.exe` 即可运行

### 方式二：从源码运行

1. 安装 [Python 3.10+](https://www.python.org/downloads/)
2. 下载本项目代码
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 运行程序：
   ```bash
   python run.py
   ```

## 使用说明

### 简单模式

1. 启动程序后，在顶部输入框输入 BV 号（如 `BV1GJ411x7h7`）
2. 点击「查询」按钮或按回车键
3. 程序将显示该视频的总数据和周刊得点

### 高级模式

1. 菜单栏 → 视图 → 模式 → 高级模式
2. 在 `resources/templates/` 目录下准备对应的 Excel 模板文件
3. 输入 BV 号查询，程序会自动读取历史基数并计算增量数据

### 设置说明

菜单栏 → 文件 → 设置，可配置：

| 设置项 | 说明 |
|--------|------|
| 主题 | 浅色 / 深色 |
| 亚克力效果 | 开启/关闭半透明背景 |
| 动画效果 | 开启/关闭按钮悬停动画 |
| API 超时 | 网络请求超时时间（默认 10 秒） |
| 缓存设置 | 是否启用缓存及缓存大小 |

## 常见问题

### Q: 运行时提示"找不到 python313.dll"？
A: 请使用 Python 3.13 或更新版本重新打包，或直接使用 `python run.py` 运行。

### Q: 亚克力效果不生效？
A: 亚克力效果仅在 Windows 10/11 上生效，请在设置中确认已启用。

### Q: 如何切换深色主题？
A: 菜单栏 → 视图 → 主题 → 深色主题，或在设置中修改。

### Q: 查询时提示"网络请求失败"？
A: 请检查网络连接，或在设置中增加 API 超时时间。

### Q: 高级模式的 Excel 模板在哪里？
A: 模板文件位于 `resources/templates/` 目录，文件名需与 BV 号对应。

## 计算公式说明

计算公式来源于 B 站中 V 周刊组，主要包含：

- **播放得点**：基于调整后的播放量和播放修正系数
- **互动得点**：基于评论 + 弹幕量和互动修正系数
- **收藏得点**：基于收藏数和收藏修正系数
- **硬币得点**：基于硬币数和硬币修正系数
- **点赞得点**：基于点赞数（上限为硬币数的 2 倍）

## 版权声明

本计算器初始版权由：
- **计算公式**：中 V 周刊组（B站 UID: 156489）
- **代码实现**：云师阳（B站 UID: 1866643210）

所享有。

## 二创说明

本作品采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 协议。您必须：
- **署名**：注明原作出处
- **非商业**：不得用于商业用途
- **相同方式共享**：衍生作品必须使用相同许可证

### 简单而言
1. 您可以使用本仓库所提供的代码进行二次修改以适用自身使用需求
2. 您需要在您二次创作发布时在明显地方列出原始作品的 staff
3. 本内容完全免费公开，禁止商用及售卖
4. 您在二次创作时也需要保持同上授权

---

## 开发者指南

### 项目结构

```
Points_Calculator_for_VCWEEKLY/
├── src/weekly_score/        # 源代码
│   ├── app.py               # QApplication 初始化
│   ├── __main__.py          # 模块入口
│   ├── core/                # 核心业务逻辑
│   │   ├── api.py           # Bilibili API 调用（同步/异步）
│   │   ├── calculator.py    # 得分计算逻辑
│   │   ├── excel_io.py      # Excel 读写操作
│   │   └── models.py        # 数据模型定义
│   ├── gui/                 # GUI 界面
│   │   ├── main_window.py   # 主窗口
│   │   ├── widgets/         # 自定义组件
│   │   ├── dialogs/         # 对话框
│   │   └── styles/          # Fluent Design 主题
│   └── utils/               # 工具函数（配置、日志、验证）
├── tests/                   # 测试代码（66 个测试用例）
├── resources/templates/     # Excel 模板
├── config/                  # 配置文件
├── run.py                   # 应用入口
├── build.py                 # 打包脚本
├── weekly_score.spec        # PyInstaller 配置
└── pyproject.toml           # 项目配置
```

### 技术栈

| 类别 | 技术 |
|------|------|
| GUI 框架 | PyQt6 |
| HTTP 请求 | requests（同步）/ aiohttp（异步） |
| Excel 处理 | openpyxl |
| 配置管理 | tomllib / tomli_w |
| 日志系统 | logging + RotatingFileHandler |
| 测试框架 | pytest + pytest-qt + pytest-asyncio |
| 打包工具 | PyInstaller |

### 环境搭建

```bash
# 克隆仓库
git clone https://github.com/your-username/Points_Calculator_for_VCWEEKLY.git
cd Points_Calculator_for_VCWEEKLY

# 安装依赖（包含开发工具）
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块
pytest tests/test_calculator.py -v
pytest tests/test_api.py -v
pytest tests/test_excel_io.py -v
```

### 打包为 EXE

```bash
python build.py
# 输出：dist/weekly_score.exe
```

### 公式常量

计算公式常量定义在 `src/weekly_score/utils/config.py` 的 `CALCULATOR_CONSTANTS` 中，可通过修改该字典调整计算行为。

---

## 版本历史

### v3.0.0（当前版本）
- 全面重构为现代化 Fluent Design 界面
- 支持浅色/深色主题切换
- 支持亚克力效果和动画效果开关
- 添加设置对话框
- 支持打包为单个 exe 文件
- 66 个单元测试覆盖核心模块

### v2.1
- 增加 Excel 读写功能
- 支持读取历史基数、计算增量数据

### v1.1
- 基础 API 查询和得点计算功能

## 联系方式

- **B站**：[@云师阳](https://space.bilibili.com/1866643210)

## 许可证

本项目采用 [CC BY-NC-SA 4.0](LICENSE) 许可协议。
