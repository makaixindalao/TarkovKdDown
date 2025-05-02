#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
鼠标控制模块

该模块提供了鼠标操作的功能，包括移动鼠标、点击和双击等。
"""

import ctypes
from ctypes import wintypes
import time
import logging
from typing import Tuple, Optional

# 配置日志
logger = logging.getLogger(__name__)

user32 = ctypes.WinDLL('user32', use_last_error=True)

# 鼠标事件常量
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_ABSOLUTE = 0x8000

def get_screen_size() -> Tuple[int, int]:
    """
    获取屏幕分辨率
    
    Returns:
        Tuple[int, int]: 屏幕宽度和高度
    """
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def set_cursor_pos(x: int, y: int) -> None:
    """
    设置鼠标位置
    
    Args:
        x: 横坐标
        y: 纵坐标
    """
    logger.debug(f"设置鼠标位置: ({x}, {y})")
    user32.SetCursorPos(int(x), int(y))

def mouse_event(flags: int, x: int = 0, y: int = 0, data: int = 0) -> None:
    """
    执行鼠标事件
    
    Args:
        flags: 鼠标事件标志
        x: 横坐标
        y: 纵坐标
        data: 附加数据
    """
    logger.debug(f"执行鼠标事件: flags={flags}, x={x}, y={y}")
    user32.mouse_event(flags, x, y, data, 0)

def move_to(x: int, y: int) -> None:
    """
    移动鼠标到指定位置
    
    Args:
        x: 横坐标
        y: 纵坐标
    """
    logger.debug(f"移动鼠标到: ({x}, {y})")
    set_cursor_pos(x, y)

def left_click(x: Optional[int] = None, y: Optional[int] = None) -> None:
    """
    在指定位置执行左键点击
    
    Args:
        x: 横坐标，如果为None则在当前位置点击
        y: 纵坐标，如果为None则在当前位置点击
    """
    if x is not None and y is not None:
        logger.debug(f"左键点击位置: ({x}, {y})")
        move_to(x, y)
        time.sleep(0.1)
    else:
        logger.debug("左键点击当前位置")
    
    mouse_event(MOUSEEVENTF_LEFTDOWN)
    time.sleep(0.05)
    mouse_event(MOUSEEVENTF_LEFTUP)

def right_click(x: Optional[int] = None, y: Optional[int] = None) -> None:
    """
    在指定位置执行右键点击
    
    Args:
        x: 横坐标，如果为None则在当前位置点击
        y: 纵坐标，如果为None则在当前位置点击
    """
    if x is not None and y is not None:
        logger.debug(f"右键点击位置: ({x}, {y})")
        move_to(x, y)
        time.sleep(0.1)
    else:
        logger.debug("右键点击当前位置")
    
    mouse_event(MOUSEEVENTF_RIGHTDOWN)
    time.sleep(0.05)
    mouse_event(MOUSEEVENTF_RIGHTUP)

def double_click(x: Optional[int] = None, y: Optional[int] = None) -> None:
    """
    在指定位置执行双击
    
    Args:
        x: 横坐标，如果为None则在当前位置双击
        y: 纵坐标，如果为None则在当前位置双击
    """
    logger.debug(f"双击位置: ({x}, {y})")
    left_click(x, y)
    time.sleep(0.1)
    left_click()
