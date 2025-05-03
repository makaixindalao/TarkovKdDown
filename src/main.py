#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
塔科夫自动送死掉KD工具主程序

该程序通过图像识别和键鼠模拟，实现全自动化操作，无需人工干预。
"""

import time
import logging

# 导入自定义模块
from image.image_manager import ensure_image_dir
from workflow.state_machine import WorkflowStateMachine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("logs/automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 确保图片目录存在
ensure_image_dir()

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
