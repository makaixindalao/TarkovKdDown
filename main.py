#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
塔科夫自动送死掉KD工具主程序

该程序通过图像识别和键鼠模拟，实现全自动化操作，无需人工干预。
"""

import os
import time
import logging
import enum
from typing import Tuple, Optional, Dict, Any

# 导入自定义模块
from image_recognition import find_and_get_center
from mouse_control import left_click
from keyboard_control import key_press
from image_manager import get_image_path, ensure_image_dir, image_exists
from process_manager import is_game_running, start_game

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 确保图片目录存在
ensure_image_dir()

# 定义工作流状态
class WorkflowState(enum.Enum):
    INIT = "初始化"
    WAIT_MAIN_MEAN = "等待主界面加载"
    CHOOSE_PMC = "选择PMC"
    NEXT_STEP = "下一步"
    CHOOSE_FACTORY = "选择工厂"
    READY = "准备"
    WAIT_GAME_START = "等待游戏开始"
    WAIT_DEAY = "等待角色死亡"
    RETURN_TO_MAIN = "返回主菜单"
    CLICK_YES = "点击是"
    ERROR = "错误"


def wait_for_image(
    image_name: str,
    timeout: int = 30,
    check_interval: float = 1.0,
    threshold: float = 0.7,
    region: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[Optional[Tuple[int, int]], float]:
    """
    等待并寻找指定图片，直到找到或超时

    Args:
        image_name: 图片名称
        timeout: 超时时间（秒）
        check_interval: 检查间隔（秒）
        threshold: 匹配阈值
        region: 搜索区域，格式为(x, y, width, height)

    Returns:
        Tuple[Optional[Tuple[int, int]], float]:
            - 如果找到: ((center_x, center_y), confidence)
            - 如果超时: (None, 0)
    """
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

class WorkflowStateMachine:
    """
    工作流状态机

    负责管理和执行自动化工作流程的状态转换和操作。
    """

    def __init__(self):
        """初始化工作流状态机"""
        self.state = WorkflowState.INIT
        self.data: Dict[str, Any] = {}  # 存储流程中的数据
        self.start_time = time.time()
        self.success_count = 0  # 成功执行次数

        logger.info(f"状态机初始化，初始状态: {self.state.value}")

    def transition_to(self, new_state: WorkflowState) -> None:
        """
        转换到新状态

        Args:
            new_state: 新的工作流状态
        """
        old_state = self.state
        self.state = new_state

        # 计算当前状态执行时间
        duration = time.time() - self.start_time

        # 记录状态转换日志
        logger.info(f"状态转换: {old_state.value} -> {new_state.value} (耗时: {duration:.2f}秒)")

        # 重置计时器，用于下一个状态的执行时间计算
        self.start_time = time.time()

    def execute(self):
        """执行当前状态的操作"""
        try:
            if self.state == WorkflowState.INIT:
                logger.info("开始执行自动化工作流程...")
                logger.info("请在3秒内切换到目标窗口...")
                time.sleep(3)
                self.transition_to(WorkflowState.WAIT_MAIN_MEAN)

            # 等待主界面加载
            elif self.state == WorkflowState.WAIT_MAIN_MEAN:
                logger.info(f"等待主界面加载, 当前执行成功次数: {self.success_count}")
                image_name = "escape"
                (center_point1, confidence1) = wait_for_image(image_name, timeout=120)
                if center_point1:
                    left_click(center_point1[0], center_point1[1])
                    self.transition_to(WorkflowState.CHOOSE_PMC)
                else:
                    logger.error(f"{self.state}失败，流程终止")
                    self.transition_to(WorkflowState.ERROR)

            # 选择PMC
            elif self.state == WorkflowState.CHOOSE_PMC:
                image_name = "pmc_select"
                (center_point1, confidence1) = wait_for_image(image_name, timeout=30)
                if center_point1:
                    self.transition_to(WorkflowState.NEXT_STEP)
                else:
                    image_name = "pmc"
                    (center_point1, confidence1) = wait_for_image(image_name, timeout=30)
                    if center_point1:
                        self.transition_to(WorkflowState.NEXT_STEP)
                    else:
                        logger.error(f"{self.state}失败，流程终止")
                        self.transition_to(WorkflowState.ERROR)

            # 下一步
            elif self.state == WorkflowState.NEXT_STEP:
                image_name = "nextstep"
                (center_point1, confidence1) = wait_for_image(image_name, timeout=30)
                if center_point1:
                    left_click(center_point1[0], center_point1[1])
                    self.transition_to(WorkflowState.CHOOSE_FACTORY)
                else:
                    logger.error(f"{self.state}失败，流程终止")
                    self.transition_to(WorkflowState.ERROR)

            # 选择工厂
            elif self.state == WorkflowState.CHOOSE_FACTORY:
                image_name = "factory"
                (center_point1, confidence1) = wait_for_image(image_name, timeout=30)
                if center_point1:
                    left_click(center_point1[0], center_point1[1])
                    self.transition_to(WorkflowState.READY)
                else:
                    image_name = "factory_select"
                    (center_point1, confidence1) = wait_for_image(image_name, timeout=30)
                    if center_point1:
                        left_click(center_point1[0], center_point1[1])
                        self.transition_to(WorkflowState.READY)
                    else:
                        logger.error(f"{self.state}失败，流程终止")
                        self.transition_to(WorkflowState.ERROR)

            # 准备
            elif self.state == WorkflowState.READY:
                image_name = "ready"
                (center_point1, confidence1) = wait_for_image(image_name, timeout=30)
                if center_point1:
                    left_click(center_point1[0], center_point1[1])
                    self.transition_to(WorkflowState.WAIT_GAME_START)
                else:
                    logger.error(f"{self.state}失败，流程终止")
                    self.transition_to(WorkflowState.ERROR)

            # 等待游戏开始
            elif self.state == WorkflowState.WAIT_GAME_START:
                image_name = "in_game"
                (center_point1, confidence1) = wait_for_image(image_name, timeout=600)
                if center_point1:
                    self.transition_to(WorkflowState.WAIT_DEAY)
                else:
                    logger.error(f"{self.state}失败，流程终止")
                    self.transition_to(WorkflowState.ERROR)

            # 等待角色死亡
            elif self.state == WorkflowState.WAIT_DEAY:
                image_name = "nextstep"
                (center_point1, confidence1) = wait_for_image(image_name, timeout=600)
                if center_point1:
                    self.transition_to(WorkflowState.RETURN_TO_MAIN)
                else:
                    logger.error(f"{self.state}失败，流程终止")
                    self.transition_to(WorkflowState.ERROR)

            # 返回主菜单
            elif self.state == WorkflowState.RETURN_TO_MAIN:
                image_name = "main_menu"
                (center_point1, confidence1) = wait_for_image(image_name, timeout=30)
                if center_point1:
                    left_click(center_point1[0], center_point1[1])
                    self.transition_to(WorkflowState.CLICK_YES)
                else:
                    logger.error(f"{self.state}失败，流程终止")
                    self.transition_to(WorkflowState.ERROR)

            # 点击是
            elif self.state == WorkflowState.CLICK_YES:
                image_name = "yes"
                (center_point1, confidence1) = wait_for_image(image_name, timeout=30)
                if center_point1:
                    left_click(center_point1[0], center_point1[1])
                    self.success_count += 1
                    logger.info("=========================")
                    logger.info(f"成功执行次数: {self.success_count}")
                    logger.info("=========================")
                    self.transition_to(WorkflowState.WAIT_MAIN_MEAN)
                else:
                    logger.error(f"{self.state}失败，流程终止")
                    self.transition_to(WorkflowState.ERROR)
            elif self.state == WorkflowState.ERROR:
                logger.error("工作流程执行失败!")

                # 检查游戏进程是否存在
                if not is_game_running():
                    logger.error("检测到EscapeFromTarkov游戏进程不存在!")

                    # 尝试重新启动游戏
                    logger.info("正在尝试重新启动游戏...")
                    if start_game():
                        logger.info("游戏已重新启动，等待30秒让游戏完全加载...")
                        time.sleep(30)  # 等待游戏完全加载
                        self.transition_to(WorkflowState.WAIT_MAIN_MEAN)
                        return self.execute()  # 重新开始执行工作流
                    else:
                        logger.error("重新启动游戏失败，请手动启动游戏后重试。")

                return False

            # 继续执行下一个状态
            return self.execute()

        except Exception as e:
            logger.exception(f"执行状态 {self.state.value} 时发生异常: {str(e)}")

            # 检查是否是因为游戏进程不存在导致的异常
            if not is_game_running():
                logger.error("异常可能是由于游戏进程不存在导致的")

            self.transition_to(WorkflowState.ERROR)
            return False

def execute_workflow() -> bool:
    """
    执行自动化工作流程

    创建并执行工作流状态机，处理整个自动化流程。

    Returns:
        bool: 工作流程是否成功执行
            - True: 工作流程成功执行
            - False: 工作流程执行失败
    """
    logger.info("开始执行自动化工作流程...")

    # 等待用户准备
    logger.info("请在3秒内切换到目标窗口...")
    time.sleep(3)

    # 创建并执行工作流状态机
    workflow = WorkflowStateMachine()
    success = workflow.execute()

    # 记录执行结果
    if success:
        logger.info("工作流程执行成功!")
    else:
        logger.warning("工作流程执行失败，请检查日志了解详情。")

    return success


def main() -> None:
    """
    主函数

    程序入口点，负责初始化和启动自动化工作流程。
    """
    # 打印分隔线和启动信息
    separator = "=" * 50
    logger.info(separator)
    logger.info("塔科夫自动送死掉KD工具 - 启动中...")
    logger.info(separator)

    try:
        # 执行工作流程
        success = execute_workflow()

        # 打印结束信息
        logger.info(separator)
        if success:
            logger.info("程序执行成功!")
        else:
            logger.warning("程序执行失败，请检查日志了解详情。")
    except Exception as e:
        # 捕获并记录未预期的异常
        logger.exception(f"程序执行过程中发生未预期的异常: {str(e)}")
        logger.error("程序异常终止")
    finally:
        # 确保始终打印结束分隔线
        logger.info(separator)

if __name__ == "__main__":
    main()


