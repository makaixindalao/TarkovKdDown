import os
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

# 定义图片存储目录
IMAGE_DIR = "images"

def ensure_image_dir():
    """确保图片目录存在"""
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
        logger.info(f"创建图片存储目录: {IMAGE_DIR}")
    return IMAGE_DIR

def get_image_path(image_name):
    """
    获取图片的完整路径
    
    参数:
        image_name: 图片名称，如果不包含扩展名，将自动添加.png
    
    返回:
        图片的完整路径
    """

    # 确保图片目录存在
    ensure_image_dir()
    
    # 如果没有扩展名，添加.png
    if not os.path.splitext(image_name)[1]:
        logger.debug(f"没有扩展名，添加.png")
        image_name = f"{image_name}.png"

    path = os.path.join(IMAGE_DIR, image_name)
    
    return path

def list_images():
    """
    列出所有可用的图片
    
    返回:
        图片名称列表
    """
    ensure_image_dir()
    
    image_files = []
    for file in os.listdir(IMAGE_DIR):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            image_files.append(file)
    
    return image_files

def add_image(source_path, image_name=None):
    """
    添加图片到图片目录
    
    参数:
        source_path: 源图片路径
        image_name: 保存的图片名称，如果为None则使用源文件名
    
    返回:
        保存后的图片路径
    """
    ensure_image_dir()
    
    # 如果没有指定名称，使用源文件名
    if image_name is None:
        image_name = os.path.basename(source_path)
    
    # 如果没有扩展名，添加.png
    if not os.path.splitext(image_name)[1]:
        image_name = f"{image_name}.png"
    
    # 目标路径
    target_path = os.path.join(IMAGE_DIR, image_name)
    
    # 复制文件
    shutil.copy2(source_path, target_path)
    logger.info(f"添加图片: {source_path} -> {target_path}")
    
    return target_path

def remove_image(image_name):
    """
    从图片目录中删除图片
    
    参数:
        image_name: 图片名称
    
    返回:
        是否成功删除
    """
    # 获取完整路径
    image_path = get_image_path(image_name)
    
    # 检查文件是否存在
    if os.path.exists(image_path):
        os.remove(image_path)
        logger.info(f"删除图片: {image_path}")
        return True
    else:
        logger.warning(f"图片不存在，无法删除: {image_path}")
        return False

def image_exists(image_name):
    """
    检查图片是否存在
    
    参数:
        image_name: 图片名称
    
    返回:
        图片是否存在
    """
    return os.path.exists(get_image_path(image_name))