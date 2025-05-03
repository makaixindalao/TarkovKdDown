#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块

该模块提供了加载和访问配置文件的功能。
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    "timeouts": {
        "main_menu": 120,
        "pmc_select": 30,
        "next_step": 30,
        "factory_map": 30,
        "ready": 30,
        "game_start": 600,
        "character_death": 600,
        "return_to_main": 30,
        "confirm_dialog": 30
    },
    "thresholds": {
        "default": 0.7,
        "main_menu": 0.7,
        "pmc_select": 0.7,
        "next_step": 0.7,
        "factory_map": 0.7,
        "ready": 0.7,
        "game_start": 0.7,
        "character_death": 0.7,
        "return_to_main": 0.7,
        "confirm_dialog": 0.7
    },
    "intervals": {
        "check_interval": 1.0
    },
    "game": {
        "process_name": "EscapeFromTarkov.exe",
        "path": "C:\\Battlestate Games\\EFT\\EscapeFromTarkov.exe",
        "restart_wait_time": 30
    }
}

# 配置文件路径
CONFIG_FILE_PATH = "config.json"

# 全局配置对象
_config = None

def load_config() -> Dict[str, Any]:
    """
    加载配置文件
    
    如果配置文件不存在，则创建默认配置文件
    
    Returns:
        Dict[str, Any]: 配置字典
    """
    global _config
    
    if _config is not None:
        return _config
    
    try:
        # 检查配置文件是否存在
        if not os.path.exists(CONFIG_FILE_PATH):
            # 创建默认配置文件
            with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            logger.info(f"已创建默认配置文件: {CONFIG_FILE_PATH}")
            _config = DEFAULT_CONFIG
        else:
            # 加载配置文件
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                _config = json.load(f)
            logger.info(f"已加载配置文件: {CONFIG_FILE_PATH}")
        
        return _config
    except Exception as e:
        logger.exception(f"加载配置文件时发生异常: {str(e)}")
        logger.warning("使用默认配置")
        _config = DEFAULT_CONFIG
        return _config

def get_timeout(key: str) -> int:
    """
    获取超时时间
    
    Args:
        key: 超时时间的键名
        
    Returns:
        int: 超时时间（秒）
    """
    config = load_config()
    return config.get("timeouts", {}).get(key, DEFAULT_CONFIG["timeouts"].get(key, 30))

def get_threshold(key: str) -> float:
    """
    获取匹配阈值
    
    Args:
        key: 匹配阈值的键名
        
    Returns:
        float: 匹配阈值
    """
    config = load_config()
    return config.get("thresholds", {}).get(key, config.get("thresholds", {}).get("default", 0.7))

def get_check_interval() -> float:
    """
    获取检查间隔
    
    Returns:
        float: 检查间隔（秒）
    """
    config = load_config()
    return config.get("intervals", {}).get("check_interval", 1.0)

def get_game_process_name() -> str:
    """
    获取游戏进程名称
    
    Returns:
        str: 游戏进程名称
    """
    config = load_config()
    return config.get("game", {}).get("process_name", "EscapeFromTarkov.exe")

def get_game_path() -> str:
    """
    获取游戏路径
    
    Returns:
        str: 游戏路径
    """
    config = load_config()
    return config.get("game", {}).get("path", "C:\\Battlestate Games\\EFT\\EscapeFromTarkov.exe")

def get_restart_wait_time() -> int:
    """
    获取重启等待时间
    
    Returns:
        int: 重启等待时间（秒）
    """
    config = load_config()
    return config.get("game", {}).get("restart_wait_time", 30)

def save_config(config: Dict[str, Any]) -> bool:
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        
    Returns:
        bool: 是否成功保存
    """
    global _config
    
    try:
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        _config = config
        logger.info(f"已保存配置到文件: {CONFIG_FILE_PATH}")
        return True
    except Exception as e:
        logger.exception(f"保存配置文件时发生异常: {str(e)}")
        return False
