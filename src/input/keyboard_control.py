#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
键盘控制模块

该模块提供了键盘操作的功能，包括按下、释放和模拟按键等。
"""

import ctypes
from ctypes import wintypes
import time
import logging

# 配置日志
logger = logging.getLogger(__name__)

user32 = ctypes.WinDLL('user32', use_last_error=True)

# Windows键盘事件常量
INPUT_KEYBOARD = 1
KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002

# 定义输入结构
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT_union(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("padding", ctypes.c_ubyte * 24)  # 确保足够大小
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_union)
    ]

def press_key(key_code: int) -> None:
    """
    按下指定键位
    
    Args:
        key_code: 键位的虚拟键码
    """
    logger.debug(f"按下键位: 0x{key_code:02X}")
    inputs = INPUT(type=INPUT_KEYBOARD, 
                  union=INPUT_union(ki=KEYBDINPUT(wVk=key_code, 
                                                 wScan=0, 
                                                 dwFlags=KEYEVENTF_KEYDOWN, 
                                                 time=0, 
                                                 dwExtraInfo=None)))
    user32.SendInput(1, ctypes.byref(inputs), ctypes.sizeof(inputs))

def release_key(key_code: int) -> None:
    """
    释放指定键位
    
    Args:
        key_code: 键位的虚拟键码
    """
    logger.debug(f"释放键位: 0x{key_code:02X}")
    inputs = INPUT(type=INPUT_KEYBOARD, 
                  union=INPUT_union(ki=KEYBDINPUT(wVk=key_code, 
                                                 wScan=0, 
                                                 dwFlags=KEYEVENTF_KEYUP, 
                                                 time=0, 
                                                 dwExtraInfo=None)))
    user32.SendInput(1, ctypes.byref(inputs), ctypes.sizeof(inputs))

def key_press(key_code: int, duration: float = 0.1) -> None:
    """
    按下并释放键位
    
    Args:
        key_code: 键位的虚拟键码
        duration: 按键持续时间（秒）
    """
    logger.debug(f"按下并释放键位: 0x{key_code:02X}, 持续时间: {duration}秒")
    press_key(key_code)
    time.sleep(duration)
    release_key(key_code)
