"""
配置管理模块

管理应用配置和常量。
"""

import sys
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import tomli_w
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    "app": {
        "name": "周刊得点计算器",
        "version": "3.0.0",
        "author": "云师阳"
    },
    "api": {
        "base_url": "https://api.bilibili.com/x/web-interface/view",
        "timeout": 10,
        "retry_count": 3,
        "cache_ttl": 300
    },
    "excel": {
        "default_sheet": "Sheet1",
        "data_row": 4,
        "base_row": 5,
        "column_range": "B:G",
        "auto_save": True
    },
    "gui": {
        "theme": "light",
        "language": "zh_CN",
        "window_width": 1200,
        "window_height": 800,
        "min_width": 1000,
        "min_height": 600,
        "acrylic_enabled": True,
        "animation_enabled": True
    },
    "logging": {
        "level": "INFO",
        "file": "logs/app.log",
        "max_size": 10,
        "backup_count": 5,
        "console_output": True
    },
    "cache": {
        "enabled": True,
        "directory": "cache",
        "max_size": 100
    },
    "validation": {
        "bvid_pattern": "^BV[a-zA-Z0-9]{10}$",
        "max_input_length": 20
    }
}

# 计算公式常量
CALCULATOR_CONSTANTS = {
    "PLAY_THRESHOLD": 10000,  # 播放量阈值
    "PLAY_BONUS": 5000,  # 播放量加成
    "PLAY_DECAY_RATE": 0.5,  # 播放量衰减率
    "INTERACTION_WEIGHT": 15,  # 互动权重
    "INTERACTION_DAMPING": 20,  # 互动阻尼系数
    "FAVORITE_COIN_RATIO": 2,  # 收藏硬币比例阈值
    "MODIFIER_B_MAX": 50,  # 修正B最大值
    "MODIFIER_C_MAX": 50,  # 修正C最大值
    "MODIFIER_D_MAX": 1,  # 修正D最大值
    "MODIFIER_B_FACTOR": 250,  # 修正B因子
    "MODIFIER_C_FACTOR": 250,  # 修正C因子
    "MODIFIER_D_FACTOR": 25,  # 修正D因子
    "MODIFIER_B_HIGH_FACTOR": 1000,  # 修正B高因子
    "LIKE_COIN_MULTIPLIER": 2  # 点赞硬币乘数
}


class Config:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.config_path = config_path
        self._config = DEFAULT_CONFIG.copy()
        
        if config_path and config_path.exists():
            self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'rb') as f:
                user_config = tomllib.load(f)
            self._merge_config(self._config, user_config)
            logger.info(f"配置已加载: {self.config_path}")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        if not self.config_path:
            logger.warning("配置文件路径未设置，跳过保存")
            return
        
        try:
            # 确保配置目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'wb') as f:
                tomli_w.dump(self._config, f)
            logger.info(f"配置已保存: {self.config_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def _merge_config(self, base: Dict, update: Dict):
        """递归合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键名，使用点分隔（如 "api.timeout"）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键名，使用点分隔
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    @property
    def calculator_constants(self) -> Dict[str, Any]:
        """获取计算器常量"""
        return CALCULATOR_CONSTANTS.copy()