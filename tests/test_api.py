"""
API模块测试

测试Bilibili API调用功能。
"""

import pytest
import aiohttp
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any
import json
import time

from weekly_score.core.api import BilibiliAPI, APIError, NetworkError, APIResponseError
from weekly_score.core.models import VideoStats


class TestBilibiliAPI:
    """BilibiliAPI测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.api = BilibiliAPI(timeout=5, retry_count=2, cache_ttl=60)
    
    def teardown_method(self):
        """测试后清理"""
        self.api.close()
    
    def test_initialization(self):
        """测试API客户端初始化"""
        assert self.api.timeout == 5
        assert self.api.retry_count == 2
        assert self.api.cache_ttl == 60
        assert self.api.session is not None
        assert self.api._cache == {}
        assert self.api._cache_timestamps == {}
    
    def test_clear_cache_specific_bvid(self):
        """测试清除特定BV号缓存"""
        # 添加缓存
        self.api._cache["BV1234567890"] = {"view": 1000}
        self.api._cache_timestamps["BV1234567890"] = time.time()
        
        # 清除缓存
        self.api.clear_cache("BV1234567890")
        
        assert "BV1234567890" not in self.api._cache
        assert "BV1234567890" not in self.api._cache_timestamps
    
    def test_clear_cache_all(self):
        """测试清除所有缓存"""
        # 添加缓存
        self.api._cache["BV1234567890"] = {"view": 1000}
        self.api._cache_timestamps["BV1234567890"] = time.time()
        self.api._cache["BV0987654321"] = {"view": 2000}
        self.api._cache_timestamps["BV0987654321"] = time.time()
        
        # 清除所有缓存
        self.api.clear_cache()
        
        assert self.api._cache == {}
        assert self.api._cache_timestamps == {}
    
    def test_parse_server_time_valid(self):
        """测试解析有效服务器时间"""
        # 有效的HTTP日期格式
        server_time_str = "Wed, 21 Oct 2015 07:28:00 GMT"
        result = self.api.parse_server_time(server_time_str)
        
        assert result is not None
        assert result.year == 2015
        assert result.month == 10
        assert result.day == 21
    
    def test_parse_server_time_none(self):
        """测试解析None服务器时间"""
        result = self.api.parse_server_time(None)
        assert result is None
    
    def test_parse_server_time_empty_string(self):
        """测试解析空字符串服务器时间"""
        result = self.api.parse_server_time("")
        assert result is None
    
    def test_parse_server_time_invalid(self):
        """测试解析无效服务器时间"""
        result = self.api.parse_server_time("invalid time")
        assert result is None
    
    @patch('weekly_score.core.api.requests.Session.get')
    def test_get_video_stats_success(self, mock_get):
        """测试成功获取视频数据"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "message": "success",
            "data": {
                "stat": {
                    "view": 100000,
                    "like": 5000,
                    "danmaku": 1000,
                    "reply": 500,
                    "coin": 2000,
                    "favorite": 3000
                }
            }
        }
        mock_response.headers = {"Date": "Wed, 21 Oct 2015 07:28:00 GMT"}
        mock_response.raise_for_status = MagicMock()
        
        mock_get.return_value = mock_response
        
        result = self.api.get_video_stats("BV1234567890")
        
        assert isinstance(result, VideoStats)
        assert result.view == 100000
        assert result.like == 5000
        assert result.danmaku == 1000
        assert result.reply == 500
        assert result.coin == 2000
        assert result.favorite == 3000
        assert result.server_time == "Wed, 21 Oct 2015 07:28:00 GMT"
        
        # 验证缓存
        assert "BV1234567890" in self.api._cache
        assert "BV1234567890" in self.api._cache_timestamps
    
    @patch('weekly_score.core.api.requests.Session.get')
    def test_get_video_stats_with_cache(self, mock_get):
        """测试使用缓存获取视频数据"""
        # 预先设置缓存
        cached_data = {
            "view": 100000,
            "like": 5000,
            "danmaku": 1000,
            "reply": 500,
            "coin": 2000,
            "favorite": 3000,
            "server_time": "Wed, 21 Oct 2015 07:28:00 GMT"
        }
        self.api._cache["BV1234567890"] = cached_data
        self.api._cache_timestamps["BV1234567890"] = time.time()
        
        result = self.api.get_video_stats("BV1234567890", use_cache=True)
        
        assert isinstance(result, VideoStats)
        assert result.view == 100000
        
        # 验证没有发起网络请求
        mock_get.assert_not_called()
    
    @patch('weekly_score.core.api.requests.Session.get')
    def test_get_video_stats_cache_disabled(self, mock_get):
        """测试禁用缓存获取视频数据"""
        # 预先设置缓存
        cached_data = {
            "view": 100000,
            "like": 5000,
            "danmaku": 1000,
            "reply": 500,
            "coin": 2000,
            "favorite": 3000,
            "server_time": "Wed, 21 Oct 2015 07:28:00 GMT"
        }
        self.api._cache["BV1234567890"] = cached_data
        self.api._cache_timestamps["BV1234567890"] = time.time()
        
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "message": "success",
            "data": {
                "stat": {
                    "view": 200000,
                    "like": 10000,
                    "danmaku": 2000,
                    "reply": 1000,
                    "coin": 4000,
                    "favorite": 6000
                }
            }
        }
        mock_response.headers = {"Date": "Wed, 21 Oct 2015 08:28:00 GMT"}
        mock_response.raise_for_status = MagicMock()
        
        mock_get.return_value = mock_response
        
        result = self.api.get_video_stats("BV1234567890", use_cache=False)
        
        assert isinstance(result, VideoStats)
        assert result.view == 200000
        
        # 验证发起了网络请求
        mock_get.assert_called_once()
    
    @patch('weekly_score.core.api.requests.Session.get')
    def test_get_video_stats_api_error(self, mock_get):
        """测试API返回错误"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": -400,
            "message": "请求错误",
            "data": None
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_get.return_value = mock_response
        
        with pytest.raises(APIResponseError) as exc_info:
            self.api.get_video_stats("BV1234567890")
        
        assert "请求错误" in str(exc_info.value)
    
    @patch('weekly_score.core.api.requests.Session.get')
    def test_get_video_stats_network_error(self, mock_get):
        """测试网络错误"""
        # 模拟网络异常
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("网络连接失败")
        
        with pytest.raises(NetworkError):
            self.api.get_video_stats("BV1234567890")
    
    @patch('weekly_score.core.api.requests.Session.get')
    def test_get_video_stats_retry(self, mock_get):
        """测试重试机制"""
        # 第一次失败，第二次成功
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 200
        mock_response_fail.json.return_value = {
            "code": -400,
            "message": "请求错误",
            "data": None
        }
        mock_response_fail.raise_for_status = MagicMock()
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "code": 0,
            "message": "success",
            "data": {
                "stat": {
                    "view": 100000,
                    "like": 5000,
                    "danmaku": 1000,
                    "reply": 500,
                    "coin": 2000,
                    "favorite": 3000
                }
            }
        }
        mock_response_success.headers = {"Date": "Wed, 21 Oct 2015 07:28:00 GMT"}
        mock_response_success.raise_for_status = MagicMock()
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        # 由于第一次返回API错误，应该抛出异常，不会重试
        with pytest.raises(APIResponseError):
            self.api.get_video_stats("BV1234567890")
    
    @patch('weekly_score.core.api.requests.Session.get')
    def test_get_video_stats_invalid_json(self, mock_get):
        """测试无效JSON响应"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("无效JSON")
        mock_response.raise_for_status = MagicMock()
        
        mock_get.return_value = mock_response
        
        with pytest.raises(APIResponseError):
            self.api.get_video_stats("BV1234567890")
    
    @patch('weekly_score.core.api.requests.Session.get')
    def test_get_video_stats_missing_stat(self, mock_get):
        """测试缺少统计数据"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "message": "success",
            "data": {
                "stat": None
            }
        }
        mock_response.headers = {"Date": "Wed, 21 Oct 2015 07:28:00 GMT"}
        mock_response.raise_for_status = MagicMock()
        
        mock_get.return_value = mock_response
        
        with pytest.raises((APIResponseError, TypeError)):
            self.api.get_video_stats("BV1234567890")
    
    @patch('weekly_score.core.api.requests.Session.get')
    def test_get_video_stats_partial_data(self, mock_get):
        """测试部分数据缺失"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "message": "success",
            "data": {
                "stat": {
                    "view": 100000,
                    "like": 5000,
                    # 缺少其他字段
                }
            }
        }
        mock_response.headers = {"Date": "Wed, 21 Oct 2015 07:28:00 GMT"}
        mock_response.raise_for_status = MagicMock()
        
        mock_get.return_value = mock_response
        
        with pytest.raises((KeyError, APIResponseError)):
            self.api.get_video_stats("BV1234567890")
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with BilibiliAPI() as api:
            assert api is not None
            assert api.session is not None
        
        # 验证会话已关闭
        # 注意：requests.Session.close() 不会抛出异常，所以这里只验证上下文管理器工作正常


class MockAsyncContextManager:
    """模拟异步上下文管理器"""
    def __init__(self, return_value=None, side_effect=None):
        self._return_value = return_value
        self._side_effect = side_effect
    
    async def __aenter__(self):
        if self._side_effect:
            raise self._side_effect
        return self._return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False


class TestBilibiliAPIAsync:
    """BilibiliAPI异步方法测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.api = BilibiliAPI(timeout=5, retry_count=2, cache_ttl=60)
    
    def teardown_method(self):
        """测试后清理"""
        self.api.close()
    
    @pytest.mark.asyncio
    async def test_get_video_stats_async_success(self):
        """测试异步成功获取视频数据"""
        # 模拟aiohttp响应
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "code": 0,
            "message": "success",
            "data": {
                "stat": {
                    "view": 100000,
                    "like": 5000,
                    "danmaku": 1000,
                    "reply": 500,
                    "coin": 2000,
                    "favorite": 3000
                }
            }
        })
        mock_response.headers = {"Date": "Wed, 21 Oct 2015 07:28:00 GMT"}
        mock_response.raise_for_status = MagicMock()
        
        # 模拟aiohttp会话 - session.get返回一个异步上下文管理器
        mock_session = MagicMock()
        mock_session.get.return_value = MockAsyncContextManager(return_value=mock_response)
        
        with patch('weekly_score.core.api.aiohttp.ClientSession') as mock_cls:
            mock_cls.return_value = MockAsyncContextManager(return_value=mock_session)
            result = await self.api.get_video_stats_async("BV1234567890")
        
        assert isinstance(result, VideoStats)
        assert result.view == 100000
        assert result.like == 5000
        assert result.danmaku == 1000
        assert result.reply == 500
        assert result.coin == 2000
        assert result.favorite == 3000
        
        # 验证缓存
        assert "BV1234567890" in self.api._cache
        assert "BV1234567890" in self.api._cache_timestamps
    
    @pytest.mark.asyncio
    async def test_get_video_stats_async_with_cache(self):
        """测试异步使用缓存获取视频数据"""
        # 预先设置缓存
        cached_data = {
            "view": 100000,
            "like": 5000,
            "danmaku": 1000,
            "reply": 500,
            "coin": 2000,
            "favorite": 3000,
            "server_time": "Wed, 21 Oct 2015 07:28:00 GMT"
        }
        self.api._cache["BV1234567890"] = cached_data
        self.api._cache_timestamps["BV1234567890"] = time.time()
        
        result = await self.api.get_video_stats_async("BV1234567890", use_cache=True)
        
        assert isinstance(result, VideoStats)
        assert result.view == 100000
    
    @pytest.mark.asyncio
    async def test_get_video_stats_async_api_error(self):
        """测试异步API返回错误"""
        # 模拟aiohttp响应
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "code": -400,
            "message": "请求错误",
            "data": None
        })
        mock_response.raise_for_status = MagicMock()
        
        # 模拟aiohttp会话
        mock_session = MagicMock()
        mock_session.get.return_value = MockAsyncContextManager(return_value=mock_response)
        
        with patch('weekly_score.core.api.aiohttp.ClientSession') as mock_cls:
            mock_cls.return_value = MockAsyncContextManager(return_value=mock_session)
            with pytest.raises(APIResponseError) as exc_info:
                await self.api.get_video_stats_async("BV1234567890")
            
            assert "请求错误" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_video_stats_async_network_error(self):
        """测试异步网络错误"""
        # 模拟aiohttp会话
        mock_session = MagicMock()
        mock_session.get.return_value = MockAsyncContextManager(
            side_effect=aiohttp.ClientError("网络连接失败")
        )
        
        with patch('weekly_score.core.api.aiohttp.ClientSession') as mock_cls:
            mock_cls.return_value = MockAsyncContextManager(return_value=mock_session)
            with pytest.raises(NetworkError):
                await self.api.get_video_stats_async("BV1234567890")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])