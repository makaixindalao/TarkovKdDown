#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
塔科夫自动送死掉KD工具启动脚本

该脚本用于启动塔科夫自动送死掉KD工具。
"""

import os
import sys

# 将src目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 导入主程序
from main import main

if __name__ == "__main__":
    # 启动主程序
    main()
