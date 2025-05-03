#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
游戏操作模块

该模块提供了与游戏交互的各种操作函数，如等待界面、点击按钮等。
"""

import time
import logging
from typing import Tuple, Optional, Dict, Any

from image.image_recognition import find_and_get_center
from input.mouse_control import left_click
from image.image_manager import get_image_path, image_exists
from config_manager import get_timeout, get_threshold, get_check_interval

# 配置日志
logger = logging.getLogger(__name__)


def wait_for_image(
    image_name: str,
    timeout: Optional[int] = None,
    check_interval: Optional[float] = None,
    threshold: Optional[float] = None,
    region: Optional[Tuple[int, int, int, int]] = None,
    config_key: Optional[str] = None
) -> Tuple[Optional[Tuple[int, int]], float]:
    """
    等待并寻找指定图片，直到找到或超时

    Args:
        image_name: 图片名称
        timeout: 超时时间（秒），如果为None则使用配置文件中的值
        check_interval: 检查间隔（秒），如果为None则使用配置文件中的值
        threshold: 匹配阈值，如果为None则使用配置文件中的值
        region: 搜索区域，格式为(x, y, width, height)
        config_key: 配置键名，用于从配置文件中获取超时时间和匹配阈值

    Returns:
        Tuple[Optional[Tuple[int, int]], float]:
            - 如果找到: ((center_x, center_y), confidence)
            - 如果超时: (None, 0)
    """
    # 如果提供了配置键名，则从配置文件中获取超时时间和匹配阈值
    if config_key:
        if timeout is None:
            timeout = get_timeout(config_key)
        if threshold is None:
            threshold = get_threshold(config_key)
    
    # 如果仍未指定，则使用默认值
    if timeout is None:
        timeout = 30
    if threshold is None:
        threshold = 0.7
    
    # 如果未指定检查间隔，则使用配置文件中的值
    if check_interval is None:
        check_interval = get_check_interval()
    
    template_path = get_image_path(image_name)

    # 检查模板图像是否存在
    if not image_exists(image_name):
        logger.warning(f"警告: 模板图像 {image_name} 不存在。")
        return (None, 0)

    start_time = time.time()
    while time.time() - start_time < timeout:
        # 查找图像并获取中心点
        center_point, confidence = find_and_get_center(
            template_path,
            threshold=threshold,
            region=region
        )

        if center_point:
            center_x, center_y = center_point
            logger.debug(f"找到图像 {image_name}，位置: {center_point}，置信度: {confidence:.4f}")
            return (center_point, confidence)

        # 等待一段时间再次检查
        time.sleep(check_interval)

    logger.warning(f"等待图像 {image_name} 超时（{timeout}秒）")
    return (None, 0)


def wait_for_main_menu() -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    等待主界面加载
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]:
            - 是否成功找到主界面
            - 如果找到，返回主界面中心点坐标，否则返回None
    """
    logger.info("等待主界面加载...")
    image_name = "escape"
    center_point, _ = wait_for_image(image_name, config_key="main_menu")
    
    if center_point:
        logger.info("找到主界面")
        return True, center_point
    else:
        logger.error("未找到主界面")
        return False, None


def select_pmc() -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    选择PMC角色
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]:
            - 是否成功选择PMC角色
            - 如果成功，返回PMC角色中心点坐标，否则返回None
    """
    logger.info("选择PMC角色...")
    
    # 尝试找到已选择的PMC
    image_name = "pmc_select"
    center_point, _ = wait_for_image(image_name, config_key="pmc_select")
    
    if center_point:
        logger.info("找到已选择的PMC")
        return True, center_point
    
    # 如果未找到已选择的PMC，尝试找到未选择的PMC
    image_name = "pmc"
    center_point, _ = wait_for_image(image_name, config_key="pmc_select")
    
    if center_point:
        logger.info("找到未选择的PMC")
        return True, center_point
    
    logger.error("未找到PMC角色")
    return False, None


def proceed_to_next() -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    进行下一步操作
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]:
            - 是否成功找到下一步按钮
            - 如果找到，返回下一步按钮中心点坐标，否则返回None
    """
    logger.info("进行下一步操作...")
    image_name = "nextstep"
    center_point, _ = wait_for_image(image_name, config_key="next_step")
    
    if center_point:
        logger.info("找到下一步按钮")
        return True, center_point
    else:
        logger.error("未找到下一步按钮")
        return False, None


def select_factory_map() -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    选择工厂地图
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]:
            - 是否成功选择工厂地图
            - 如果成功，返回工厂地图中心点坐标，否则返回None
    """
    logger.info("选择工厂地图...")
    
    # 尝试找到工厂地图
    image_name = "factory"
    center_point, _ = wait_for_image(image_name, config_key="factory_map")
    
    if center_point:
        logger.info("找到工厂地图")
        return True, center_point
    
    # 如果未找到工厂地图，尝试找到已选择的工厂地图
    image_name = "factory_select"
    center_point, _ = wait_for_image(image_name, config_key="factory_map")
    
    if center_point:
        logger.info("找到已选择的工厂地图")
        return True, center_point
    
    logger.error("未找到工厂地图")
    return False, None


def prepare_deployment() -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    准备部署角色
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]:
            - 是否成功找到准备按钮
            - 如果找到，返回准备按钮中心点坐标，否则返回None
    """
    logger.info("准备部署角色...")
    image_name = "ready"
    center_point, _ = wait_for_image(image_name, config_key="ready")
    
    if center_point:
        logger.info("找到准备按钮")
        return True, center_point
    else:
        logger.error("未找到准备按钮")
        return False, None


def wait_for_game_start() -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    等待游戏开始
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]:
            - 是否成功进入游戏
            - 如果成功，返回游戏中界面标识中心点坐标，否则返回None
    """
    logger.info("等待游戏开始...")
    image_name = "in_game"
    center_point, _ = wait_for_image(image_name, config_key="game_start")
    
    if center_point:
        logger.info("游戏已开始")
        return True, center_point
    else:
        logger.error("游戏未开始")
        return False, None


def wait_for_character_death() -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    等待角色死亡
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]:
            - 是否成功检测到角色死亡
            - 如果成功，返回下一步按钮中心点坐标，否则返回None
    """
    logger.info("等待角色死亡...")
    image_name = "nextstep"
    center_point, _ = wait_for_image(image_name, config_key="character_death")
    
    if center_point:
        logger.info("角色已死亡")
        return True, center_point
    else:
        logger.error("未检测到角色死亡")
        return False, None


def return_to_main_menu() -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    返回主菜单
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]:
            - 是否成功找到返回主菜单按钮
            - 如果找到，返回返回主菜单按钮中心点坐标，否则返回None
    """
    logger.info("返回主菜单...")
    image_name = "main_menu"
    center_point, _ = wait_for_image(image_name, config_key="return_to_main")
    
    if center_point:
        logger.info("找到返回主菜单按钮")
        return True, center_point
    else:
        logger.error("未找到返回主菜单按钮")
        return False, None


def confirm_dialog() -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    确认对话框
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]:
            - 是否成功找到确认按钮
            - 如果找到，返回确认按钮中心点坐标，否则返回None
    """
    logger.info("确认对话框...")
    image_name = "yes"
    center_point, _ = wait_for_image(image_name, config_key="confirm_dialog")
    
    if center_point:
        logger.info("找到确认按钮")
        return True, center_point
    else:
        logger.error("未找到确认按钮")
        return False, None
