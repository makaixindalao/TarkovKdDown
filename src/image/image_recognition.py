#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图像识别模块

该模块提供了屏幕截图和图像识别的功能，用于在屏幕上查找特定的图像模板。
"""

import cv2
import numpy as np
from PIL import ImageGrab
import os
import logging
from typing import List, Tuple, Optional, Any

# 配置日志
logger = logging.getLogger(__name__)

def take_screenshot(region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
    """
    捕获屏幕截图
    
    Args:
        region: 截图区域，格式为(left, top, right, bottom)
        
    Returns:
        np.ndarray: 屏幕截图的numpy数组
    """
    if region:
        screenshot = ImageGrab.grab(bbox=region)
    else:
        screenshot = ImageGrab.grab()
    
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot

def find_image(
    template_path: str, 
    screenshot: Optional[np.ndarray] = None, 
    threshold: float = 0.8, 
    region: Optional[Tuple[int, int, int, int]] = None
) -> List[Tuple[int, int, int, int, float]]:
    """
    在屏幕上查找模板图像，返回匹配结果列表
    
    Args:
        template_path: 模板图像路径
        screenshot: 可选的屏幕截图
        threshold: 匹配阈值
        region: 搜索区域，格式为(left, top, right, bottom)
        
    Returns:
        List[Tuple[int, int, int, int, float]]: 匹配结果列表，每个结果为(x, y, w, h, confidence)
    """
    # 加载模板图像
    template = cv2.imread(template_path)
    if template is None:
        logger.error(f"无法加载模板图像: {template_path}")
        raise FileNotFoundError(f"无法加载模板图像: {template_path}")
    
    # 获取模板尺寸
    h, w = template.shape[:2]
    
    # 如果没有提供截图，则捕获屏幕
    if screenshot is None:
        screenshot = take_screenshot(region)
    
    # 执行模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    
    # 查找匹配位置
    locations = np.where(result >= threshold)
    matches = []
    
    # 转换匹配结果为坐标列表
    for pt in zip(*locations[::-1]):
        x, y = pt
        if region:
            x += region[0]
            y += region[1]
        
        confidence = result[pt[1], pt[0]]
        matches.append((x, y, w, h, confidence))
    
    # 非极大值抑制，移除重叠的匹配
    if matches:
        matches = non_max_suppression(matches, 0.3)
        logger.debug(f"找到 {len(matches)} 个匹配结果")
    else:
        logger.debug("未找到匹配结果")
    
    return matches

def find_best_match(
    template_path: str, 
    screenshot: Optional[np.ndarray] = None, 
    threshold: float = 0.7, 
    region: Optional[Tuple[int, int, int, int]] = None
) -> Optional[Tuple[int, int, int, int, float]]:
    """
    查找最佳匹配的图像，并返回匹配结果
    
    Args:
        template_path: 模板图像路径
        screenshot: 可选的屏幕截图
        threshold: 匹配阈值
        region: 搜索区域，格式为(left, top, right, bottom)
        
    Returns:
        Optional[Tuple[int, int, int, int, float]]: 
            - 如果找到匹配: (x, y, w, h, confidence) 元组
            - 如果未找到: None
    """
    matches = find_image(template_path, screenshot, threshold, region)
    if matches:
        logger.debug(f"最佳匹配置信度: {matches[0][4]:.4f}")
        return matches[0]  # 返回最佳匹配（已按置信度排序）
    return None

def non_max_suppression(
    matches: List[Tuple[int, int, int, int, float]], 
    overlap_thresh: float
) -> List[Tuple[int, int, int, int, float]]:
    """
    非极大值抑制，移除重叠的匹配
    
    Args:
        matches: 匹配结果列表，每个结果为(x, y, w, h, confidence)
        overlap_thresh: 重叠阈值
        
    Returns:
        List[Tuple[int, int, int, int, float]]: 经过非极大值抑制后的匹配结果列表
    """
    if not matches:
        return []
    
    # 提取坐标和置信度
    boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h, _) in matches])
    confidences = np.array([conf for (_, _, _, _, conf) in matches])
    
    # 按置信度排序
    idxs = np.argsort(confidences)[::-1]
    
    pick = []
    while len(idxs) > 0:
        current = idxs[0]
        pick.append(current)
        
        xx1 = np.maximum(boxes[current, 0], boxes[idxs[1:], 0])
        yy1 = np.maximum(boxes[current, 1], boxes[idxs[1:], 1])
        xx2 = np.minimum(boxes[current, 2], boxes[idxs[1:], 2])
        yy2 = np.minimum(boxes[current, 3], boxes[idxs[1:], 3])
        
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        
        overlap = (w * h) / ((boxes[idxs[1:], 2] - boxes[idxs[1:], 0] + 1) * 
                             (boxes[idxs[1:], 3] - boxes[idxs[1:], 1] + 1))
        
        idxs = np.delete(idxs, np.concatenate(([0], np.where(overlap > overlap_thresh)[0] + 1)))
    
    logger.debug(f"非极大值抑制后保留 {len(pick)} 个匹配")
    return [matches[i] for i in pick]

def get_center_point(match: Tuple[int, int, int, int, float]) -> Tuple[int, int]:
    """
    获取匹配区域的中心点
    
    Args:
        match: 匹配结果，格式为(x, y, w, h, confidence)
        
    Returns:
        Tuple[int, int]: 中心点坐标(center_x, center_y)
    """
    x, y, w, h, _ = match
    return (x + w // 2, y + h // 2)

def find_and_get_center(
    template_path: str, 
    threshold: float = 0.7, 
    region: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[Optional[Tuple[int, int]], float]:
    """
    查找图像并返回中心点坐标和置信度
    
    Args:
        template_path: 模板图像路径
        threshold: 匹配阈值
        region: 搜索区域，格式为(left, top, right, bottom)
        
    Returns:
        Tuple[Optional[Tuple[int, int]], float]: 
            - 如果找到匹配: ((center_x, center_y), confidence)
            - 如果未找到: (None, 0)
    """
    match = find_best_match(template_path, threshold=threshold, region=region)
    if match:
        center = get_center_point(match)
        confidence = match[4]
        logger.debug(f"找到中心点: {center}, 置信度: {confidence:.4f}")
        return (center, confidence)
    logger.debug("未找到匹配，无法获取中心点")
    return (None, 0)
