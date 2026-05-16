import tkinter as tk
from tkinter import messagebox
import requests
import math
from datetime import datetime, timezone, timedelta
import email.utils

# Windows 字体 DPI 优化
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# ====================== 核心计算函数 ======================
def get_video_stats(bvid):
    """通过 BV 号获取视频统计数据"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data['code'] != 0:
            raise Exception(f"API返回错误: {data['message']}")
        stat = data['data']['stat']
        server_time = resp.headers.get('Date')
        return {
            'view': stat['view'],
            'like': stat['like'],
            'danmaku': stat['danmaku'],
            'reply': stat['reply'],
            'coin': stat['coin'],
            'favorite': stat['favorite'],
            'server_time': server_time
        }
    except Exception as e:
        messagebox.showerror("获取失败", str(e))
        return None

def compute_weekly_score(stats):
    """根据公式计算周刊得点"""
    A3 = float(stats['view'])
    B3 = float(stats['like'])
    C3 = float(stats['danmaku'])
    D3 = float(stats['reply'])
    E3 = float(stats['coin'])
    F3 = float(stats['favorite'])

    # 基础播点
    A6 = A3 * 0.5 + 5000 if A3 > 10000 else A3

    # 互动量
    B6 = D3 + C3

    # 修正A
    denominator = A6 + F3 + B6 * 20
    C6 = 0 if denominator == 0 else ((A6 + F3) / denominator) ** 2

    # 修正B
    if F3 > E3 * 2:
        temp = (E3 ** 2 / (A3 * F3)) * 1000 if A3 * F3 != 0 else 0
    else:
        temp = (F3 / A3) * 250 if A3 != 0 else 0
    D6 = 50 if temp > 50 else temp

    # 修正C
    if E3 > F3:
        temp = (F3 ** 2 / (A3 * E3)) * 250 if A3 * E3 != 0 else 0
    else:
        temp = (E3 / A3) * 250 if A3 != 0 else 0
    E6 = 50 if temp > 50 else temp

    # 修正D
    if F3 > E3:
        temp = (E3 / A3) * 25 if A3 != 0 else 0
    else:
        temp = (F3 / A3) * 25 if A3 != 0 else 0
    F6 = 1 if temp > 1 else temp

    play_points = A6 * F6
    interaction_points = B6 * C6 * 15
    favorite_points = F3 * D6
    coin_points = E3 * E6
    like_points = min(B3, E3 * 2)

    total_points = play_points + interaction_points + favorite_points + coin_points + like_points

    return {
        "播放得点": play_points,
        "互动得点": interaction_points,
        "收藏得点": favorite_points,
        "硬币得点": coin_points,
        "点赞得点": like_points,
        "最终得点": total_points
    }

# ====================== GUI 程序 ======================
class WeeklyScoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("B站周刊得点计算器")
        self.root.geometry("700x450")   # 加宽窗口，确保两列完整显示
        self.root.minsize(700, 450)     # 允许用户调整大小，设置最小尺寸

        font_label = ("楷体", 11)
        font_data = ("微软雅黑", 10)

        # ----- 顶部：输入框、查询按钮和北京时间（同一行） -----
        top_frame = tk.Frame(root)
        top_frame.pack(pady=15, fill=tk.X)

        # 左侧区域：BV号标签、输入框、查询按钮
        left_part = tk.Frame(top_frame)
        left_part.pack(side=tk.LEFT)
        tk.Label(left_part, text=" BV号：", font=font_label).pack(side=tk.LEFT, padx=5)
        self.bvid_entry = tk.Entry(left_part, width=15, font=("等线", 11))
        self.bvid_entry.pack(side=tk.LEFT, padx=5)
        self.query_btn = tk.Button(left_part, text="查询", font=("楷体", 10), width=8, command=self.query_data)
        self.query_btn.pack(side=tk.LEFT, padx=10)

        # 右侧显示北京时间
        self.time_label = tk.Label(top_frame, text="北京时间：--", font=("仿宋", 9))
        self.time_label.pack(side=tk.LEFT, padx=10)

        # ----- 主体：左右两列，使用 grid 布局（在 main_frame 中）-----
        main_frame = tk.Frame(root)
        main_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # 配置 main_frame 的列权重，使左右两列平分空间
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 左列：原始数据
        left_frame = tk.LabelFrame(main_frame, text="▍原始数据(总)", font=("黑体", 12, "bold"), padx=12, pady=10)
        left_frame.grid(row=0, column=0, padx=12, sticky="nsew")

        # 右列：得点结果
        right_frame = tk.LabelFrame(main_frame, text="▍周刊得点", font=("黑体", 12, "bold"), padx=12, pady=10)
        right_frame.grid(row=0, column=1, padx=12, sticky="nsew")

        # 存储动态变量的字典
        self.raw_vars = {}
        self.result_vars = {}

        # 左列内容
        raw_fields = [
            ("播放量", "view"), ("点赞量", "like"), ("弹幕量", "danmaku"),
            ("评论量", "reply"), ("硬币量", "coin"), ("收藏量", "favorite")
        ]
        for i, (ch_name, en_name) in enumerate(raw_fields):
            label = tk.Label(left_frame, text=ch_name, font=font_label, anchor="e", width=10)
            label.grid(row=i, column=0, padx=5, pady=8, sticky="e")
            var = tk.StringVar(value="--")
            display = tk.Label(left_frame, textvariable=var, font=font_data, width=12, anchor="w", relief="sunken", bd=1, bg="white")
            display.grid(row=i, column=1, padx=5, pady=8, sticky="w")
            self.raw_vars[en_name] = var

        # 右列内容
        result_fields = [
            ("播放得点", "play"), ("互动得点", "interaction"),
            ("收藏得点", "favorite_points"), ("硬币得点", "coin_points"),
            ("点赞得点", "like_points"), ("最终得点", "total")
        ]
        for i, (ch_name, en_name) in enumerate(result_fields):
            label = tk.Label(right_frame, text=ch_name, font=font_label, anchor="e", width=10)
            label.grid(row=i, column=0, padx=5, pady=8, sticky="e")
            var = tk.StringVar(value="--")
            display = tk.Label(right_frame, textvariable=var, font=font_data, width=12, anchor="w", relief="sunken", bd=1, bg="white")
            display.grid(row=i, column=1, padx=5, pady=8, sticky="w")
            self.result_vars[en_name] = var

        # 底部留一点空白

        tk.Label(root, text="相关计算公式来源于B站中V周刊组，本计算器由云师阳(1866643210)制作", font=("仿宋", 9), fg="gray").pack(pady=2)
        tk.Label(root, text="", font=("仿宋", 9), fg="gray").pack(pady=2)
        tk.Label(root, text="").pack()
        
    def query_data(self):
        bvid = self.bvid_entry.get().strip()
        if not bvid:
            messagebox.showwarning("警告", "请输入 BV 号")
            return

        self.query_btn.config(state=tk.DISABLED)
        self.root.update()

        try:
            stats = get_video_stats(bvid)
            if stats is None:
                return

            # 显示北京时间
            server_time_str = stats.get('server_time')
            if server_time_str:
                try:
                    gmt_time = email.utils.parsedate_to_datetime(server_time_str)
                    beijing_time = gmt_time.astimezone(timezone(timedelta(hours=8)))
                    self.time_label.config(text=f"北京时间：{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    self.time_label.config(text=f"北京时间：解析失败 ({server_time_str})")
            else:
                self.time_label.config(text="北京时间：未获取到服务器时间")

            # 更新原始数据
            self.raw_vars['view'].set(f"{stats['view']:,}")
            self.raw_vars['like'].set(f"{stats['like']:,}")
            self.raw_vars['danmaku'].set(f"{stats['danmaku']:,}")
            self.raw_vars['reply'].set(f"{stats['reply']:,}")
            self.raw_vars['coin'].set(f"{stats['coin']:,}")
            self.raw_vars['favorite'].set(f"{stats['favorite']:,}")

            # 计算得分
            scores = compute_weekly_score(stats)

            # 更新结果
            self.result_vars['play'].set(f"{scores['播放得点']:.2f}")
            self.result_vars['interaction'].set(f"{scores['互动得点']:.2f}")
            self.result_vars['favorite_points'].set(f"{scores['收藏得点']:.2f}")
            self.result_vars['coin_points'].set(f"{scores['硬币得点']:.2f}")
            self.result_vars['like_points'].set(f"{scores['点赞得点']:.2f}")
            self.result_vars['total'].set(f"{scores['最终得点']:.2f}")

        except Exception as e:
            messagebox.showerror("错误", f"发生异常: {str(e)}")
        finally:
            self.query_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeeklyScoreApp(root)
    root.mainloop()
