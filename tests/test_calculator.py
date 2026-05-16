"""
计算器模块测试

测试周刊得点计算逻辑。
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from weekly_score.core.calculator import WeeklyScoreCalculator
from weekly_score.core.models import VideoStats, ScoreResult, DeltaStats
from weekly_score.utils.config import CALCULATOR_CONSTANTS


class TestWeeklyScoreCalculator:
    """WeeklyScoreCalculator测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.calculator = WeeklyScoreCalculator()
    
    def test_calculator_initialization(self):
        """测试计算器初始化"""
        assert self.calculator.PLAY_THRESHOLD == CALCULATOR_CONSTANTS["PLAY_THRESHOLD"]
        assert self.calculator.PLAY_BONUS == CALCULATOR_CONSTANTS["PLAY_BONUS"]
        assert self.calculator.PLAY_DECAY_RATE == CALCULATOR_CONSTANTS["PLAY_DECAY_RATE"]
        assert self.calculator.INTERACTION_WEIGHT == CALCULATOR_CONSTANTS["INTERACTION_WEIGHT"]
        assert self.calculator.INTERACTION_DAMPING == CALCULATOR_CONSTANTS["INTERACTION_DAMPING"]
        assert self.calculator.FAVORITE_COIN_RATIO == CALCULATOR_CONSTANTS["FAVORITE_COIN_RATIO"]
        assert self.calculator.MODIFIER_B_MAX == CALCULATOR_CONSTANTS["MODIFIER_B_MAX"]
        assert self.calculator.MODIFIER_C_MAX == CALCULATOR_CONSTANTS["MODIFIER_C_MAX"]
        assert self.calculator.MODIFIER_D_MAX == CALCULATOR_CONSTANTS["MODIFIER_D_MAX"]
        assert self.calculator.MODIFIER_B_FACTOR == CALCULATOR_CONSTANTS["MODIFIER_B_FACTOR"]
        assert self.calculator.MODIFIER_C_FACTOR == CALCULATOR_CONSTANTS["MODIFIER_C_FACTOR"]
        assert self.calculator.MODIFIER_D_FACTOR == CALCULATOR_CONSTANTS["MODIFIER_D_FACTOR"]
        assert self.calculator.MODIFIER_B_HIGH_FACTOR == CALCULATOR_CONSTANTS["MODIFIER_B_HIGH_FACTOR"]
        assert self.calculator.LIKE_COIN_MULTIPLIER == CALCULATOR_CONSTANTS["LIKE_COIN_MULTIPLIER"]
    
    def test_calculate_score_with_video_stats(self):
        """测试使用VideoStats计算得分"""
        stats = VideoStats(
            view=100000,
            like=5000,
            danmaku=1000,
            reply=500,
            coin=2000,
            favorite=3000
        )
        
        result = self.calculator.calculate_score(stats)
        
        assert isinstance(result, ScoreResult)
        assert result.play_points >= 0
        assert result.interaction_points >= 0
        assert result.favorite_points >= 0
        assert result.coin_points >= 0
        assert result.like_points >= 0
        assert result.total_points >= 0
        assert result.total_points == (
            result.play_points + result.interaction_points + 
            result.favorite_points + result.coin_points + result.like_points
        )
    
    def test_calculate_score_with_delta_stats(self):
        """测试使用DeltaStats计算得分"""
        stats = DeltaStats(
            view=10000,
            like=500,
            danmaku=100,
            reply=50,
            coin=200,
            favorite=300
        )
        
        result = self.calculator.calculate_score(stats)
        
        assert isinstance(result, ScoreResult)
        assert result.total_points >= 0
    
    def test_calculate_score_with_dict(self):
        """测试使用字典计算得分"""
        stats = {
            'view': 100000,
            'like': 5000,
            'danmaku': 1000,
            'reply': 500,
            'coin': 2000,
            'favorite': 3000
        }
        
        result = self.calculator.calculate_score(stats)
        
        assert isinstance(result, ScoreResult)
        assert result.total_points >= 0
    
    def test_calculate_score_zero_stats(self):
        """测试零数据计算得分"""
        stats = VideoStats(
            view=0,
            like=0,
            danmaku=0,
            reply=0,
            coin=0,
            favorite=0
        )
        
        result = self.calculator.calculate_score(stats)
        
        assert isinstance(result, ScoreResult)
        assert result.play_points == 0.0
        assert result.interaction_points == 0.0
        assert result.favorite_points == 0.0
        assert result.coin_points == 0.0
        assert result.like_points == 0.0
        assert result.total_points == 0.0
    
    def test_calculate_score_missing_keys(self):
        """测试缺少键的字典"""
        stats = {
            'view': 100000,
            'like': 5000
            # 缺少其他键
        }
        
        result = self.calculator.calculate_score(stats)
        
        assert isinstance(result, ScoreResult)
        assert result.total_points >= 0
    
    def test_calculate_adjusted_views_below_threshold(self):
        """测试播放量低于阈值时的调整"""
        views = 5000
        adjusted = self.calculator._calculate_adjusted_views(views)
        assert adjusted == views
    
    def test_calculate_adjusted_views_above_threshold(self):
        """测试播放量高于阈值时的调整"""
        views = 20000
        expected = views * self.calculator.PLAY_DECAY_RATE + self.calculator.PLAY_BONUS
        adjusted = self.calculator._calculate_adjusted_views(views)
        assert adjusted == expected
    
    def test_calculate_adjusted_views_at_threshold(self):
        """测试播放量等于阈值时的调整"""
        views = self.calculator.PLAY_THRESHOLD
        adjusted = self.calculator._calculate_adjusted_views(views)
        assert adjusted == views
    
    def test_calculate_interaction_modifier_zero_denominator(self):
        """测试互动修正系数分母为零的情况"""
        modifier = self.calculator._calculate_interaction_modifier(0, 0, 0)
        assert modifier == 0.0
    
    def test_calculate_interaction_modifier_normal(self):
        """测试正常互动修正系数计算"""
        adjusted_views = 10000
        favorites = 1000
        interaction_count = 500
        
        modifier = self.calculator._calculate_interaction_modifier(
            adjusted_views, favorites, interaction_count
        )
        
        assert 0 <= modifier <= 1
    
    def test_calculate_favorite_modifier_zero_views(self):
        """测试播放量为零时的收藏修正系数"""
        modifier = self.calculator._calculate_favorite_modifier(0, 1000, 500)
        assert modifier == 0.0
    
    def test_calculate_favorite_modifier_normal(self):
        """测试正常收藏修正系数计算"""
        views = 100000
        favorites = 1000
        coins = 500
        
        modifier = self.calculator._calculate_favorite_modifier(views, favorites, coins)
        
        assert 0 <= modifier <= self.calculator.MODIFIER_B_MAX
    
    def test_calculate_favorite_modifier_high_favorite(self):
        """测试高收藏低硬币的收藏修正系数"""
        views = 100000
        favorites = 10000
        coins = 100  # 远低于收藏
        
        modifier = self.calculator._calculate_favorite_modifier(views, favorites, coins)
        
        assert 0 <= modifier <= self.calculator.MODIFIER_B_MAX
    
    def test_calculate_coin_modifier_zero_views(self):
        """测试播放量为零时的硬币修正系数"""
        modifier = self.calculator._calculate_coin_modifier(0, 1000, 500)
        assert modifier == 0.0
    
    def test_calculate_coin_modifier_normal(self):
        """测试正常硬币修正系数计算"""
        views = 100000
        favorites = 1000
        coins = 500
        
        modifier = self.calculator._calculate_coin_modifier(views, favorites, coins)
        
        assert 0 <= modifier <= self.calculator.MODIFIER_C_MAX
    
    def test_calculate_coin_modifier_high_coin(self):
        """测试高硬币低收藏的硬币修正系数"""
        views = 100000
        favorites = 100
        coins = 1000  # 远高于收藏
        
        modifier = self.calculator._calculate_coin_modifier(views, favorites, coins)
        
        assert 0 <= modifier <= self.calculator.MODIFIER_C_MAX
    
    def test_calculate_play_modifier_zero_views(self):
        """测试播放量为零时的播放修正系数"""
        modifier = self.calculator._calculate_play_modifier(0, 1000, 500)
        assert modifier == 0.0
    
    def test_calculate_play_modifier_normal(self):
        """测试正常播放修正系数计算"""
        views = 100000
        favorites = 1000
        coins = 500
        
        modifier = self.calculator._calculate_play_modifier(views, favorites, coins)
        
        assert 0 <= modifier <= self.calculator.MODIFIER_D_MAX
    
    def test_calculate_delta(self):
        """测试增量计算"""
        total = VideoStats(
            view=100000,
            like=5000,
            danmaku=1000,
            reply=500,
            coin=2000,
            favorite=3000
        )
        
        base = VideoStats(
            view=90000,
            like=4500,
            danmaku=900,
            reply=450,
            coin=1800,
            favorite=2700
        )
        
        delta = self.calculator.calculate_delta(total, base)
        
        assert isinstance(delta, DeltaStats)
        assert delta.view == 10000
        assert delta.like == 500
        assert delta.danmaku == 100
        assert delta.reply == 50
        assert delta.coin == 200
        assert delta.favorite == 300
    
    def test_calculate_delta_negative_values(self):
        """测试增量计算中的负值处理"""
        total = VideoStats(
            view=90000,
            like=4500,
            danmaku=900,
            reply=450,
            coin=1800,
            favorite=2700
        )
        
        base = VideoStats(
            view=100000,
            like=5000,
            danmaku=1000,
            reply=500,
            coin=2000,
            favorite=3000
        )
        
        delta = self.calculator.calculate_delta(total, base)
        
        # 所有增量应该为0，因为基础值大于总值
        assert delta.view == 0
        assert delta.like == 0
        assert delta.danmaku == 0
        assert delta.reply == 0
        assert delta.coin == 0
        assert delta.favorite == 0
    
    def test_calculate_score_with_large_numbers(self):
        """测试大数值计算"""
        stats = VideoStats(
            view=10000000,
            like=500000,
            danmaku=100000,
            reply=50000,
            coin=200000,
            favorite=300000
        )
        
        result = self.calculator.calculate_score(stats)
        
        assert isinstance(result, ScoreResult)
        assert result.total_points > 0
    
    def test_calculate_score_with_small_numbers(self):
        """测试小数值计算"""
        stats = VideoStats(
            view=100,
            like=5,
            danmaku=1,
            reply=1,
            coin=2,
            favorite=3
        )
        
        result = self.calculator.calculate_score(stats)
        
        assert isinstance(result, ScoreResult)
        assert result.total_points >= 0
    
    def test_calculate_score_like_points_capped(self):
        """测试点赞得点上限"""
        # 点赞数远高于硬币数的2倍
        stats = VideoStats(
            view=100000,
            like=10000,
            danmaku=1000,
            reply=500,
            coin=100,
            favorite=3000
        )
        
        result = self.calculator.calculate_score(stats)
        
        # 点赞得点应该被限制在硬币数的2倍
        assert result.like_points <= stats.coin * self.calculator.LIKE_COIN_MULTIPLIER
    
    def test_calculate_score_all_zero(self):
        """测试全零数据"""
        stats = VideoStats(
            view=0,
            like=0,
            danmaku=0,
            reply=0,
            coin=0,
            favorite=0
        )
        
        result = self.calculator.calculate_score(stats)
        
        assert result.play_points == 0.0
        assert result.interaction_points == 0.0
        assert result.favorite_points == 0.0
        assert result.coin_points == 0.0
        assert result.like_points == 0.0
        assert result.total_points == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])