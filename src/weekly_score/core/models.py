"""
数据模型定义

定义视频统计数据和计算结果的数据结构。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class VideoStats:
    """视频统计数据模型"""
    view: int
    like: int
    danmaku: int
    reply: int
    coin: int
    favorite: int
    server_time: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'view': self.view,
            'like': self.like,
            'danmaku': self.danmaku,
            'reply': self.reply,
            'coin': self.coin,
            'favorite': self.favorite,
            'server_time': self.server_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VideoStats':
        """从字典创建实例"""
        return cls(
            view=data.get('view', 0),
            like=data.get('like', 0),
            danmaku=data.get('danmaku', 0),
            reply=data.get('reply', 0),
            coin=data.get('coin', 0),
            favorite=data.get('favorite', 0),
            server_time=data.get('server_time')
        )


@dataclass
class ScoreResult:
    """得分计算结果模型"""
    play_points: float
    interaction_points: float
    favorite_points: float
    coin_points: float
    like_points: float
    total_points: float
    
    def to_dict(self) -> dict:
        """转换为字典格式（中文键名）"""
        return {
            "播放得点": self.play_points,
            "互动得点": self.interaction_points,
            "收藏得点": self.favorite_points,
            "硬币得点": self.coin_points,
            "点赞得点": self.like_points,
            "最终得点": self.total_points
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScoreResult':
        """从字典创建实例"""
        return cls(
            play_points=data.get("播放得点", 0.0),
            interaction_points=data.get("互动得点", 0.0),
            favorite_points=data.get("收藏得点", 0.0),
            coin_points=data.get("硬币得点", 0.0),
            like_points=data.get("点赞得点", 0.0),
            total_points=data.get("最终得点", 0.0)
        )


@dataclass
class DeltaStats:
    """增量统计数据模型"""
    view: int
    like: int
    danmaku: int
    reply: int
    coin: int
    favorite: int
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'view': self.view,
            'like': self.like,
            'danmaku': self.danmaku,
            'reply': self.reply,
            'coin': self.coin,
            'favorite': self.favorite
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DeltaStats':
        """从字典创建实例"""
        return cls(
            view=data.get('view', 0),
            like=data.get('like', 0),
            danmaku=data.get('danmaku', 0),
            reply=data.get('reply', 0),
            coin=data.get('coin', 0),
            favorite=data.get('favorite', 0)
        )