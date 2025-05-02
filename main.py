import os
import time
import logging
import enum
from image_recognition import find_and_get_center
from mouse_control import left_click
from keyboard_control import key_press
from image_manager import get_image_path, ensure_image_dir, image_exists

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

def wait_for_image(image_name, timeout=30, check_interval=1.0, threshold=0.7, region=None):
    """
    等待并寻找指定图片，直到找到或超时
    
    参数:
        image_name: 图片名称
        timeout: 超时时间（秒）
        check_interval: 检查间隔（秒）
        threshold: 匹配阈值
        region: 搜索区域
        
    返回:
        如果找到: ((center_x, center_y), confidence)
        如果超时: (None, 0)
    """
    template_path = get_image_path(image_name)

    # 检查模板图像是否存在
    if not image_exists(image_name):
        logger.warning(f"警告: 模板图像 {image_name} 不存在。")
        return (None, 0)
    
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 查找图像并获取中心点
        (center_point, confidence) = find_and_get_center(template_path, threshold=threshold, region=region)
        
        if center_point:
            center_x, center_y = center_point
            return (center_point, confidence)
        
        # 等待一段时间再次检查
        time.sleep(check_interval)
    
    logger.warning(f"等待图像 {image_name} 超时")
    return (None, 0)

class WorkflowStateMachine:
    """工作流状态机"""
    
    def __init__(self):
        self.state = WorkflowState.INIT
        self.data = {}  # 存储流程中的数据
        self.start_time = time.time()
        logger.info(f"状态机初始化，初始状态: {self.state.value}")
        self.success_count = 0  # 成功执行次数
    
    def transition_to(self, new_state):
        """转换到新状态"""
        old_state = self.state
        self.state = new_state
        duration = time.time() - self.start_time
        logger.info(f"状态转换: {old_state.value} -> {new_state.value} (耗时: {duration:.2f}秒)")
        self.start_time = time.time()  # 重置计时器
    
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
                return False
                
            # 继续执行下一个状态
            return self.execute()
            
        except Exception as e:
            logger.exception(f"执行状态 {self.state.value} 时发生异常: {str(e)}")
            self.transition_to(WorkflowState.ERROR)
            return False

def execute_workflow():
    """
    执行自动化工作流程
    """
    logger.info("开始执行自动化工作流程...")
    
    # 等待用户准备
    logger.info("请在3秒内切换到目标窗口...")
    time.sleep(3)

    workflow = WorkflowStateMachine()
    success = workflow.execute()
    
    if success:
        logger.info("工作流程执行成功!")
    else:
        logger.warning("工作流程执行失败，请检查日志了解详情。")
    
    return success


def main():
    """
    主函数
    """
    logger.info("=" * 50)
    logger.info("开始运行自动化程序...")
    logger.info("=" * 50)
    
    # 执行工作流程
    success = execute_workflow()
    
    logger.info("=" * 50)
    if success:
        logger.info("程序执行成功!")
    else:
        logger.warning("程序执行失败，请检查日志了解详情。")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()


