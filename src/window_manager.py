#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
窗口管理模块

该模块提供了窗口操作的功能，包括查找窗口、前置窗口等。
"""

import win32gui
import win32con
import logging
from typing import Optional, Tuple, List

# 配置日志
logger = logging.getLogger(__name__)

# 游戏窗口标题（部分匹配即可）
GAME_WINDOW_TITLE = "EscapeFromTarkov"

def find_window_by_title(title_part: str) -> Optional[int]:
    """
    根据窗口标题（部分匹配）查找窗口句柄
    
    Args:
        title_part: 窗口标题的部分内容
        
    Returns:
        Optional[int]: 窗口句柄，如果未找到则返回None
    """
    result = []
    
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title_part.lower() in window_title.lower():
                result.append(hwnd)
    
    win32gui.EnumWindows(callback, None)
    
    if result:
        logger.debug(f"找到窗口: {win32gui.GetWindowText(result[0])}, 句柄: {result[0]}")
        return result[0]
    
    logger.warning(f"未找到包含 '{title_part}' 的窗口")
    return None

def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """
    获取窗口的位置和大小
    
    Args:
        hwnd: 窗口句柄
        
    Returns:
        Tuple[int, int, int, int]: 窗口的位置和大小 (left, top, right, bottom)
    """
    return win32gui.GetWindowRect(hwnd)

def set_foreground_window(hwnd: int) -> bool:
    """
    将指定窗口设置为前台窗口（前置窗口）
    
    Args:
        hwnd: 窗口句柄
        
    Returns:
        bool: 是否成功将窗口设置为前台窗口
    """
    try:
        # 如果窗口被最小化，先恢复它
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # 将窗口设置为前台窗口
        win32gui.SetForegroundWindow(hwnd)
        
        # 获取窗口标题用于日志记录
        window_title = win32gui.GetWindowText(hwnd)
        logger.debug(f"已将窗口 '{window_title}' 设置为前台窗口")
        
        return True
    except Exception as e:
        logger.exception(f"设置前台窗口时发生异常: {str(e)}")
        return False

def ensure_game_window_foreground() -> bool:
    """
    确保游戏窗口处于前台
    
    Returns:
        bool: 是否成功将游戏窗口设置为前台窗口
    """
    # 查找游戏窗口
    hwnd = find_window_by_title(GAME_WINDOW_TITLE)
    
    if hwnd:
        # 将游戏窗口设置为前台窗口
        return set_foreground_window(hwnd)
    
    logger.warning(f"未找到游戏窗口，无法设置为前台窗口")
    return False

def list_all_windows() -> List[Tuple[int, str]]:
    """
    列出所有可见窗口
    
    Returns:
        List[Tuple[int, str]]: 窗口句柄和标题的列表
    """
    result = []
    
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if window_title:  # 只包含有标题的窗口
                result.append((hwnd, window_title))
    
    win32gui.EnumWindows(callback, None)
    return result
