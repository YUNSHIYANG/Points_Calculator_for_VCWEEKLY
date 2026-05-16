"""
周刊得点计算模块

实现基于Bilibili视频数据的周刊得点计算逻辑。
"""

from typing import Dict, Union
import logging

try:
    from .models import VideoStats, ScoreResult, DeltaStats
    from ..utils.config import CALCULATOR_CONSTANTS
except ImportError:
    from weekly_score.core.models import VideoStats, ScoreResult, DeltaStats
    from weekly_score.utils.config import CALCULATOR_CONSTANTS

logger = logging.getLogger(__name__)


class WeeklyScoreCalculator:
    """周刊得点计算器"""
    
    def __init__(self):
        """初始化计算器"""
        # 加载常量
        self.PLAY_THRESHOLD = CALCULATOR_CONSTANTS["PLAY_THRESHOLD"]
        self.PLAY_BONUS = CALCULATOR_CONSTANTS["PLAY_BONUS"]
        self.PLAY_DECAY_RATE = CALCULATOR_CONSTANTS["PLAY_DECAY_RATE"]
        self.INTERACTION_WEIGHT = CALCULATOR_CONSTANTS["INTERACTION_WEIGHT"]
        self.INTERACTION_DAMPING = CALCULATOR_CONSTANTS["INTERACTION_DAMPING"]
        self.FAVORITE_COIN_RATIO = CALCULATOR_CONSTANTS["FAVORITE_COIN_RATIO"]
        self.MODIFIER_B_MAX = CALCULATOR_CONSTANTS["MODIFIER_B_MAX"]
        self.MODIFIER_C_MAX = CALCULATOR_CONSTANTS["MODIFIER_C_MAX"]
        self.MODIFIER_D_MAX = CALCULATOR_CONSTANTS["MODIFIER_D_MAX"]
        self.MODIFIER_B_FACTOR = CALCULATOR_CONSTANTS["MODIFIER_B_FACTOR"]
        self.MODIFIER_C_FACTOR = CALCULATOR_CONSTANTS["MODIFIER_C_FACTOR"]
        self.MODIFIER_D_FACTOR = CALCULATOR_CONSTANTS["MODIFIER_D_FACTOR"]
        self.MODIFIER_B_HIGH_FACTOR = CALCULATOR_CONSTANTS["MODIFIER_B_HIGH_FACTOR"]
        self.LIKE_COIN_MULTIPLIER = CALCULATOR_CONSTANTS["LIKE_COIN_MULTIPLIER"]
    
    def calculate_score(self, stats: Union[VideoStats, DeltaStats, Dict[str, float]]) -> ScoreResult:
        """
        计算周刊得点
        
        Args:
            stats: 视频统计数据，可以是VideoStats、DeltaStats或字典
            
        Returns:
            ScoreResult: 计算结果
        """
        # 转换为浮点数
        if isinstance(stats, (VideoStats, DeltaStats)):
            data = stats.to_dict()
        else:
            data = stats
        
        views = float(data.get('view', 0))
        likes = float(data.get('like', 0))
        danmaku = float(data.get('danmaku', 0))
        replies = float(data.get('reply', 0))
        coins = float(data.get('coin', 0))
        favorites = float(data.get('favorite', 0))
        
        # 计算基础播点
        adjusted_views = self._calculate_adjusted_views(views)
        
        # 计算互动量
        interaction_count = replies + danmaku
        
        # 计算修正系数
        interaction_modifier = self._calculate_interaction_modifier(adjusted_views, favorites, interaction_count)
        favorite_modifier = self._calculate_favorite_modifier(views, favorites, coins)
        coin_modifier = self._calculate_coin_modifier(views, favorites, coins)
        play_modifier = self._calculate_play_modifier(views, favorites, coins)
        
        # 计算各项得分
        play_points = adjusted_views * play_modifier
        interaction_points = interaction_count * interaction_modifier * self.INTERACTION_WEIGHT
        favorite_points = favorites * favorite_modifier
        coin_points = coins * coin_modifier
        like_points = min(likes, coins * self.LIKE_COIN_MULTIPLIER)
        
        # 计算总分
        total_points = play_points + interaction_points + favorite_points + coin_points + like_points
        
        logger.debug(f"计算完成: 播放得点={play_points:.2f}, 互动得点={interaction_points:.2f}, "
                    f"收藏得点={favorite_points:.2f}, 硬币得点={coin_points:.2f}, "
                    f"点赞得点={like_points:.2f}, 总分={total_points:.2f}")
        
        return ScoreResult(
            play_points=play_points,
            interaction_points=interaction_points,
            favorite_points=favorite_points,
            coin_points=coin_points,
            like_points=like_points,
            total_points=total_points
        )
    
    def _calculate_adjusted_views(self, views: float) -> float:
        """
        计算调整后的播放量
        
        Args:
            views: 原始播放量
            
        Returns:
            调整后的播放量
        """
        if views > self.PLAY_THRESHOLD:
            return views * self.PLAY_DECAY_RATE + self.PLAY_BONUS
        return views
    
    def _calculate_interaction_modifier(self, adjusted_views: float, favorites: float, interaction_count: float) -> float:
        """
        计算互动修正系数
        
        Args:
            adjusted_views: 调整后的播放量
            favorites: 收藏数
            interaction_count: 互动量
            
        Returns:
            互动修正系数
        """
        denominator = adjusted_views + favorites + interaction_count * self.INTERACTION_DAMPING
        if denominator == 0:
            return 0.0
        return ((adjusted_views + favorites) / denominator) ** 2
    
    def _calculate_favorite_modifier(self, views: float, favorites: float, coins: float) -> float:
        """
        计算收藏修正系数
        
        Args:
            views: 播放量
            favorites: 收藏数
            coins: 硬币数
            
        Returns:
            收藏修正系数
        """
        if views == 0:
            return 0.0
        
        if favorites > coins * self.FAVORITE_COIN_RATIO:
            # 收藏远多于硬币的情况
            if views * favorites == 0:
                return 0.0
            temp = (coins ** 2 / (views * favorites)) * self.MODIFIER_B_HIGH_FACTOR
        else:
            # 正常情况
            temp = (favorites / views) * self.MODIFIER_B_FACTOR
        
        return min(temp, self.MODIFIER_B_MAX)
    
    def _calculate_coin_modifier(self, views: float, favorites: float, coins: float) -> float:
        """
        计算硬币修正系数
        
        Args:
            views: 播放量
            favorites: 收藏数
            coins: 硬币数
            
        Returns:
            硬币修正系数
        """
        if views == 0:
            return 0.0
        
        if coins > favorites:
            # 硬币多于收藏的情况
            if views * coins == 0:
                return 0.0
            temp = (favorites ** 2 / (views * coins)) * self.MODIFIER_C_FACTOR
        else:
            # 正常情况
            temp = (coins / views) * self.MODIFIER_C_FACTOR
        
        return min(temp, self.MODIFIER_C_MAX)
    
    def _calculate_play_modifier(self, views: float, favorites: float, coins: float) -> float:
        """
        计算播放修正系数
        
        Args:
            views: 播放量
            favorites: 收藏数
            coins: 硬币数
            
        Returns:
            播放修正系数
        """
        if views == 0:
            return 0.0
        
        if favorites > coins:
            # 收藏多于硬币的情况
            temp = (coins / views) * self.MODIFIER_D_FACTOR
        else:
            # 正常情况
            temp = (favorites / views) * self.MODIFIER_D_FACTOR
        
        return min(temp, self.MODIFIER_D_MAX)
    
    def calculate_delta(self, total: VideoStats, base: VideoStats) -> DeltaStats:
        """
        计算增量数据
        
        Args:
            total: 当前总数
            base: 基数
            
        Returns:
            DeltaStats: 增量数据
        """
        return DeltaStats(
            view=max(0, total.view - base.view),
            like=max(0, total.like - base.like),
            danmaku=max(0, total.danmaku - base.danmaku),
            reply=max(0, total.reply - base.reply),
            coin=max(0, total.coin - base.coin),
            favorite=max(0, total.favorite - base.favorite)
        )