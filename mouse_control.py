import ctypes
from ctypes import wintypes
import time
import logging

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

# 获取屏幕分辨率
def get_screen_size():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def set_cursor_pos(x, y):
    """设置鼠标位置"""
    logger.debug(f"设置鼠标位置: ({x}, {y})")
    user32.SetCursorPos(int(x), int(y))

def mouse_event(flags, x=0, y=0, data=0):
    """执行鼠标事件"""
    logger.debug(f"执行鼠标事件: flags={flags}, x={x}, y={y}")
    user32.mouse_event(flags, x, y, data, 0)

def move_to(x, y):
    """移动鼠标到指定位置"""
    logger.debug(f"移动鼠标到: ({x}, {y})")
    set_cursor_pos(x, y)

def left_click(x=None, y=None):
    """在指定位置执行左键点击"""
    if x is not None and y is not None:
        logger.debug(f"左键点击位置: ({x}, {y})")
        move_to(x, y)
        time.sleep(0.1)
    else:
        logger.debug("左键点击当前位置")
    
    mouse_event(MOUSEEVENTF_LEFTDOWN)
    time.sleep(0.05)
    mouse_event(MOUSEEVENTF_LEFTUP)

def right_click(x=None, y=None):
    """在指定位置执行右键点击"""
    if x is not None and y is not None:
        logger.debug(f"右键点击位置: ({x}, {y})")
        move_to(x, y)
        time.sleep(0.1)
    else:
        logger.debug("右键点击当前位置")
    
    mouse_event(MOUSEEVENTF_RIGHTDOWN)
    time.sleep(0.05)
    mouse_event(MOUSEEVENTF_RIGHTUP)

def double_click(x=None, y=None):
    """在指定位置执行双击"""
    logger.debug(f"双击位置: ({x}, {y})")
    left_click(x, y)
    time.sleep(0.1)
    left_click()

