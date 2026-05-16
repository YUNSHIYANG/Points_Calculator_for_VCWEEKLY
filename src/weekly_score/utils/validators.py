"""
输入验证模块

提供输入验证功能。
"""

import re
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# BV号正则表达式
BVID_PATTERN = re.compile(r'^BV[a-zA-Z0-9]{10}$')


def validate_bvid(bvid: str) -> Tuple[bool, Optional[str]]:
    """
    验证BV号格式
    
    Args:
        bvid: BV号字符串
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not bvid:
        return False, "BV号不能为空"
    
    if len(bvid) > 20:
        return False, "BV号长度超过限制"
    
    if not BVID_PATTERN.match(bvid):
        return False, "BV号格式不正确，应为BV开头后跟10位字母数字"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除路径分隔符和特殊字符
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # 移除控制字符
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    return filename.strip()


def validate_file_path(file_path: str, allowed_extensions: list = None) -> Tuple[bool, Optional[str]]:
    """
    验证文件路径
    
    Args:
        file_path: 文件路径
        allowed_extensions: 允许的文件扩展名列表
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not file_path:
        return False, "文件路径不能为空"
    
    # 检查路径遍历攻击
    if '..' in file_path or '~' in file_path:
        return False, "文件路径包含不安全字符"
    
    # 检查文件扩展名
    if allowed_extensions:
        import os
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in allowed_extensions:
            return False, f"不支持的文件类型: {ext}"
    
    return True, None