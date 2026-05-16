"""
Bilibili API调用模块

提供视频统计数据的获取功能。
"""

import requests
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import email.utils
import logging
import time
from functools import lru_cache

try:
    from .models import VideoStats
except ImportError:
    from weekly_score.core.models import VideoStats

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API调用异常基类"""
    pass


class NetworkError(APIError):
    """网络连接异常"""
    pass


class APIResponseError(APIError):
    """API响应异常"""
    pass


class BilibiliAPI:
    """Bilibili API客户端"""
    
    BASE_URL = "https://api.bilibili.com/x/web-interface/view"
    
    def __init__(self, timeout: int = 10, retry_count: int = 3, cache_ttl: int = 300):
        """
        初始化API客户端
        
        Args:
            timeout: 请求超时时间（秒）
            retry_count: 重试次数
            cache_ttl: 缓存有效期（秒）
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self.cache_ttl = cache_ttl
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # 缓存机制
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
    
    def get_video_stats(self, bvid: str, use_cache: bool = True) -> VideoStats:
        """
        获取视频统计数据
        
        Args:
            bvid: 视频BV号
            use_cache: 是否使用缓存
            
        Returns:
            VideoStats: 视频统计数据
            
        Raises:
            NetworkError: 网络连接异常
            APIResponseError: API响应异常
        """
        # 检查缓存
        if use_cache and bvid in self._cache:
            cache_time = self._cache_timestamps.get(bvid, 0)
            if time.time() - cache_time < self.cache_ttl:
                logger.debug(f"从缓存获取数据: {bvid}")
                return VideoStats.from_dict(self._cache[bvid])
        
        url = f"{self.BASE_URL}?bvid={bvid}"
        
        last_exception = None
        for attempt in range(self.retry_count):
            try:
                logger.debug(f"尝试获取视频数据 (尝试 {attempt + 1}/{self.retry_count}): {bvid}")
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                
                data = resp.json()
                if data['code'] != 0:
                    raise APIResponseError(f"API返回错误: {data['message']}")
                
                stat = data['data']['stat']
                server_time = resp.headers.get('Date')
                
                video_stats = VideoStats(
                    view=stat['view'],
                    like=stat['like'],
                    danmaku=stat['danmaku'],
                    reply=stat['reply'],
                    coin=stat['coin'],
                    favorite=stat['favorite'],
                    server_time=server_time
                )
                
                # 更新缓存
                self._cache[bvid] = video_stats.to_dict()
                self._cache_timestamps[bvid] = time.time()
                
                logger.info(f"成功获取视频数据: {bvid}")
                return video_stats
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"网络请求失败 (尝试 {attempt + 1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    continue
                raise NetworkError(f"网络请求失败: {e}")
            except (KeyError, ValueError) as e:
                raise APIResponseError(f"API响应格式错误: {e}")
        
        raise NetworkError(f"网络请求失败: {last_exception}")
    
    def clear_cache(self, bvid: Optional[str] = None):
        """
        清除缓存
        
        Args:
            bvid: 指定BV号，如果为None则清除所有缓存
        """
        if bvid:
            self._cache.pop(bvid, None)
            self._cache_timestamps.pop(bvid, None)
            logger.debug(f"已清除缓存: {bvid}")
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
            logger.debug("已清除所有缓存")
    
    def parse_server_time(self, server_time_str: Optional[str]) -> Optional[datetime]:
        """
        解析服务器时间字符串
        
        Args:
            server_time_str: 服务器时间字符串
            
        Returns:
            Optional[datetime]: 解析后的时间（北京时间），解析失败返回None
        """
        if not server_time_str:
            return None
        
        try:
            gmt_time = email.utils.parsedate_to_datetime(server_time_str)
            beijing_time = gmt_time.astimezone(timezone(timedelta(hours=8)))
            return beijing_time
        except Exception as e:
            logger.warning(f"时间解析失败: {e}")
            return None
    
    async def get_video_stats_async(self, bvid: str, use_cache: bool = True) -> VideoStats:
        """
        异步获取视频统计数据
        
        Args:
            bvid: 视频BV号
            use_cache: 是否使用缓存
            
        Returns:
            VideoStats: 视频统计数据
            
        Raises:
            NetworkError: 网络连接异常
            APIResponseError: API响应异常
        """
        # 检查缓存
        if use_cache and bvid in self._cache:
            cache_time = self._cache_timestamps.get(bvid, 0)
            if time.time() - cache_time < self.cache_ttl:
                logger.debug(f"从缓存获取数据: {bvid}")
                return VideoStats.from_dict(self._cache[bvid])
        
        url = f"{self.BASE_URL}?bvid={bvid}"
        
        last_exception = None
        for attempt in range(self.retry_count):
            try:
                logger.debug(f"异步尝试获取视频数据 (尝试 {attempt + 1}/{self.retry_count}): {bvid}")
                
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout), headers=headers) as resp:
                        resp.raise_for_status()
                        
                        data = await resp.json()
                        if data['code'] != 0:
                            raise APIResponseError(f"API返回错误: {data['message']}")
                        
                        stat = data['data']['stat']
                        server_time = resp.headers.get('Date')
                        
                        video_stats = VideoStats(
                            view=stat['view'],
                            like=stat['like'],
                            danmaku=stat['danmaku'],
                            reply=stat['reply'],
                            coin=stat['coin'],
                            favorite=stat['favorite'],
                            server_time=server_time
                        )
                        
                        # 更新缓存
                        self._cache[bvid] = video_stats.to_dict()
                        self._cache_timestamps[bvid] = time.time()
                        
                        logger.info(f"异步成功获取视频数据: {bvid}")
                        return video_stats
                        
            except aiohttp.ClientError as e:
                last_exception = e
                logger.warning(f"异步网络请求失败 (尝试 {attempt + 1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    continue
                raise NetworkError(f"异步网络请求失败: {e}")
            except (KeyError, ValueError) as e:
                raise APIResponseError(f"API响应格式错误: {e}")
        
        raise NetworkError(f"异步网络请求失败: {last_exception}")
    
    def close(self):
        """关闭会话"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()