#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工作流状态机模块

该模块提供了工作流状态机的实现，用于管理和执行自动化工作流程的状态转换和操作。
"""

import time
import logging
import enum
from typing import Dict, Any, Optional, Tuple

from input.mouse_control import left_click
from process.process_manager import is_game_running, start_game
from config_manager import get_restart_wait_time
from game.game_actions import (
    wait_for_main_menu,
    select_pmc,
    proceed_to_next,
    select_factory_map,
    prepare_deployment,
    wait_for_game_start,
    wait_for_character_death,
    return_to_main_menu,
    confirm_dialog
)

# 配置日志
logger = logging.getLogger(__name__)


class WorkflowState(enum.Enum):
    """
    工作流状态枚举
    
    定义了工作流程中的各个状态。
    """
    INITIALIZATION = "初始化"
    WAITING_FOR_MAIN_MENU = "等待主界面加载"
    SELECTING_PMC = "选择PMC角色"
    PROCEEDING_TO_NEXT = "进行下一步"
    SELECTING_FACTORY_MAP = "选择工厂地图"
    PREPARING_DEPLOYMENT = "准备部署角色"
    WAITING_FOR_GAME_START = "等待游戏开始"
    WAITING_FOR_CHARACTER_DEATH = "等待角色死亡"
    RETURNING_TO_MAIN_MENU = "返回主菜单"
    CONFIRMING_DIALOG = "确认对话框选项"
    ERROR_STATE = "错误状态"


class WorkflowStateMachine:
    """
    工作流状态机
    
    负责管理和执行自动化工作流程的状态转换和操作。
    """

    def __init__(self):
        """初始化工作流状态机"""
        self.state = WorkflowState.INITIALIZATION
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

    def handle_initialization(self) -> bool:
        """
        处理初始化状态
        
        Returns:
            bool: 是否成功处理
        """
        logger.info("开始执行自动化工作流程...")
        logger.info("请在3秒内切换到目标窗口...")
        time.sleep(3)
        self.transition_to(WorkflowState.WAITING_FOR_MAIN_MENU)
        return True

    def handle_waiting_for_main_menu(self) -> bool:
        """
        处理等待主界面加载状态
        
        Returns:
            bool: 是否成功处理
        """
        logger.info(f"等待主界面加载, 当前执行成功次数: {self.success_count}")
        success, center_point = wait_for_main_menu()
        
        if success and center_point:
            left_click(center_point[0], center_point[1])
            self.transition_to(WorkflowState.SELECTING_PMC)
            return True
        else:
            logger.error(f"状态 {self.state.value} 执行失败，流程终止")
            self.transition_to(WorkflowState.ERROR_STATE)
            return False

    def handle_selecting_pmc(self) -> bool:
        """
        处理选择PMC角色状态
        
        Returns:
            bool: 是否成功处理
        """
        success, _ = select_pmc()
        
        if success:
            self.transition_to(WorkflowState.PROCEEDING_TO_NEXT)
            return True
        else:
            logger.error(f"状态 {self.state.value} 执行失败，流程终止")
            self.transition_to(WorkflowState.ERROR_STATE)
            return False

    def handle_proceeding_to_next(self) -> bool:
        """
        处理进行下一步状态
        
        Returns:
            bool: 是否成功处理
        """
        success, center_point = proceed_to_next()
        
        if success and center_point:
            left_click(center_point[0], center_point[1])
            self.transition_to(WorkflowState.SELECTING_FACTORY_MAP)
            return True
        else:
            logger.error(f"状态 {self.state.value} 执行失败，流程终止")
            self.transition_to(WorkflowState.ERROR_STATE)
            return False

    def handle_selecting_factory_map(self) -> bool:
        """
        处理选择工厂地图状态
        
        Returns:
            bool: 是否成功处理
        """
        success, center_point = select_factory_map()
        
        if success and center_point:
            left_click(center_point[0], center_point[1])
            self.transition_to(WorkflowState.PREPARING_DEPLOYMENT)
            return True
        else:
            logger.error(f"状态 {self.state.value} 执行失败，流程终止")
            self.transition_to(WorkflowState.ERROR_STATE)
            return False

    def handle_preparing_deployment(self) -> bool:
        """
        处理准备部署角色状态
        
        Returns:
            bool: 是否成功处理
        """
        success, center_point = prepare_deployment()
        
        if success and center_point:
            left_click(center_point[0], center_point[1])
            self.transition_to(WorkflowState.WAITING_FOR_GAME_START)
            return True
        else:
            logger.error(f"状态 {self.state.value} 执行失败，流程终止")
            self.transition_to(WorkflowState.ERROR_STATE)
            return False

    def handle_waiting_for_game_start(self) -> bool:
        """
        处理等待游戏开始状态
        
        Returns:
            bool: 是否成功处理
        """
        success, _ = wait_for_game_start()
        
        if success:
            self.transition_to(WorkflowState.WAITING_FOR_CHARACTER_DEATH)
            return True
        else:
            logger.error(f"状态 {self.state.value} 执行失败，流程终止")
            self.transition_to(WorkflowState.ERROR_STATE)
            return False

    def handle_waiting_for_character_death(self) -> bool:
        """
        处理等待角色死亡状态
        
        Returns:
            bool: 是否成功处理
        """
        success, _ = wait_for_character_death()
        
        if success:
            self.transition_to(WorkflowState.RETURNING_TO_MAIN_MENU)
            return True
        else:
            logger.error(f"状态 {self.state.value} 执行失败，流程终止")
            self.transition_to(WorkflowState.ERROR_STATE)
            return False

    def handle_returning_to_main_menu(self) -> bool:
        """
        处理返回主菜单状态
        
        Returns:
            bool: 是否成功处理
        """
        success, center_point = return_to_main_menu()
        
        if success and center_point:
            left_click(center_point[0], center_point[1])
            self.transition_to(WorkflowState.CONFIRMING_DIALOG)
            return True
        else:
            logger.error(f"状态 {self.state.value} 执行失败，流程终止")
            self.transition_to(WorkflowState.ERROR_STATE)
            return False

    def handle_confirming_dialog(self) -> bool:
        """
        处理确认对话框状态
        
        Returns:
            bool: 是否成功处理
        """
        success, center_point = confirm_dialog()
        
        if success and center_point:
            left_click(center_point[0], center_point[1])
            self.success_count += 1
            logger.info("=" * 30)
            logger.info(f"成功执行次数: {self.success_count}")
            logger.info("=" * 30)
            self.transition_to(WorkflowState.WAITING_FOR_MAIN_MENU)
            return True
        else:
            logger.error(f"状态 {self.state.value} 执行失败，流程终止")
            self.transition_to(WorkflowState.ERROR_STATE)
            return False

    def handle_error_state(self) -> bool:
        """
        处理错误状态
        
        Returns:
            bool: 是否成功处理
        """
        logger.error("工作流程执行失败!")

        # 检查游戏进程是否存在
        if not is_game_running():
            logger.error("检测到EscapeFromTarkov游戏进程不存在!")

            # 尝试重新启动游戏
            logger.info("正在尝试重新启动游戏...")
            if start_game():
                restart_wait_time = get_restart_wait_time()
                logger.info(f"游戏已重新启动，等待{restart_wait_time}秒让游戏完全加载...")
                time.sleep(restart_wait_time)  # 等待游戏完全加载
                self.transition_to(WorkflowState.WAITING_FOR_MAIN_MENU)
                return self.execute()  # 重新开始执行工作流
            else:
                logger.error("重新启动游戏失败，请手动启动游戏后重试。")

        return False

    def execute(self) -> bool:
        """
        执行当前状态的操作
        
        根据当前状态执行相应的操作，并根据操作结果转换到下一个状态。
        
        Returns:
            bool: 工作流是否成功执行
                - True: 工作流成功执行
                - False: 工作流执行失败
        """
        try:
            # 根据当前状态执行相应的处理函数
            if self.state == WorkflowState.INITIALIZATION:
                return self.handle_initialization() and self.execute()
                
            elif self.state == WorkflowState.WAITING_FOR_MAIN_MENU:
                return self.handle_waiting_for_main_menu() and self.execute()
                
            elif self.state == WorkflowState.SELECTING_PMC:
                return self.handle_selecting_pmc() and self.execute()
                
            elif self.state == WorkflowState.PROCEEDING_TO_NEXT:
                return self.handle_proceeding_to_next() and self.execute()
                
            elif self.state == WorkflowState.SELECTING_FACTORY_MAP:
                return self.handle_selecting_factory_map() and self.execute()
                
            elif self.state == WorkflowState.PREPARING_DEPLOYMENT:
                return self.handle_preparing_deployment() and self.execute()
                
            elif self.state == WorkflowState.WAITING_FOR_GAME_START:
                return self.handle_waiting_for_game_start() and self.execute()
                
            elif self.state == WorkflowState.WAITING_FOR_CHARACTER_DEATH:
                return self.handle_waiting_for_character_death() and self.execute()
                
            elif self.state == WorkflowState.RETURNING_TO_MAIN_MENU:
                return self.handle_returning_to_main_menu() and self.execute()
                
            elif self.state == WorkflowState.CONFIRMING_DIALOG:
                return self.handle_confirming_dialog() and self.execute()
                
            elif self.state == WorkflowState.ERROR_STATE:
                return self.handle_error_state()
                
            else:
                logger.error(f"未知状态: {self.state}")
                return False

        except Exception as e:
            logger.exception(f"执行状态 {self.state.value} 时发生异常: {str(e)}")

            # 检查是否是因为游戏进程不存在导致的异常
            if not is_game_running():
                logger.error("异常可能是由于游戏进程不存在导致的")

            self.transition_to(WorkflowState.ERROR_STATE)
            return False
