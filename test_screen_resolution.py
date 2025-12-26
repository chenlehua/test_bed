#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试屏幕分辨率问题
"""

import sys
import platform

print(f"操作系统: {platform.system()}")
print(f"Python 版本: {sys.version}")
print()

# 测试 PyAutoGUI
try:
    import pyautogui
    
    # 获取逻辑屏幕尺寸（PyAutoGUI 使用的坐标系统）
    logical_size = pyautogui.size()
    print(f"✅ PyAutoGUI 逻辑屏幕尺寸: {logical_size}")
    print(f"   - 坐标范围: x ∈ [0, {logical_size[0]-1}], y ∈ [0, {logical_size[1]-1}]")
    
    # 获取截图实际分辨率（物理像素）
    screenshot = pyautogui.screenshot()
    physical_size = screenshot.size
    print(f"✅ 截图物理分辨率: {physical_size}")
    print(f"   - 像素范围: width={physical_size[0]}, height={physical_size[1]}")
    
    # 计算缩放比例
    scale_x = physical_size[0] / logical_size[0]
    scale_y = physical_size[1] / logical_size[1]
    print(f"\n⚠️  分辨率不匹配检测:")
    print(f"   - X 轴缩放比例: {scale_x:.2f}x")
    print(f"   - Y 轴缩放比例: {scale_y:.2f}x")
    
    if scale_x != 1.0 or scale_y != 1.0:
        print(f"\n❌ 发现问题：截图分辨率与 PyAutoGUI 坐标系统不一致！")
        print(f"   这会导致模型预测的坐标与实际点击位置不匹配。")
        print(f"\n💡 解决方案：")
        print(f"   1. 传给模型的分辨率应该使用 pyautogui.size()，而不是从截图中提取")
        print(f"   2. 或者将截图缩放到逻辑分辨率: {logical_size}")
    else:
        print(f"\n✅ 分辨率一致，没有问题")
        
except ImportError as e:
    print(f"❌ PyAutoGUI 未安装: {e}")
    print(f"   请运行: pip install pyautogui")

print()

# 测试 PIL ImageGrab
try:
    from PIL import ImageGrab
    screenshot = ImageGrab.grab()
    print(f"✅ PIL ImageGrab 截图分辨率: {screenshot.size}")
except ImportError:
    print(f"❌ PIL 未安装")
except Exception as e:
    print(f"⚠️  PIL ImageGrab 失败: {e}")

