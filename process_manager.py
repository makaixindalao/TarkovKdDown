import os
import time
import logging
import subprocess
import psutil

# 配置日志
logger = logging.getLogger(__name__)

# 游戏进程名称和启动路径
GAME_PROCESS_NAME = "EscapeFromTarkov.exe"
GAME_PATH = r"C:\Battlestate Games\EFT\EscapeFromTarkov.exe"  # 默认安装路径，可能需要根据实际情况调整

def is_game_running():
    """
    检查EscapeFromTarkov游戏进程是否正在运行
    
    返回:
        True: 游戏进程正在运行
        False: 游戏进程未运行
    """
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if GAME_PROCESS_NAME.lower() in proc.info['name'].lower():
                logger.info(f"检测到游戏进程: {proc.info['name']} (PID: {proc.info['pid']})")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    logger.warning(f"未检测到游戏进程: {GAME_PROCESS_NAME}")
    return False

def start_game():
    """
    启动EscapeFromTarkov游戏
    
    返回:
        True: 成功启动游戏
        False: 启动游戏失败
    """
    if is_game_running():
        logger.info("游戏已经在运行中，无需重新启动")
        return True
    
    try:
        if not os.path.exists(GAME_PATH):
            logger.error(f"游戏路径不存在: {GAME_PATH}")
            return False
        
        logger.info(f"正在启动游戏: {GAME_PATH}")
        subprocess.Popen(GAME_PATH)
        
        # 等待游戏启动
        for _ in range(30):  # 最多等待30秒
            time.sleep(1)
            if is_game_running():
                logger.info("游戏已成功启动")
                return True
        
        logger.error("游戏启动超时")
        return False
    except Exception as e:
        logger.exception(f"启动游戏时发生异常: {str(e)}")
        return False
