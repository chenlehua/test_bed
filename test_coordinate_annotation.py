#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试坐标标注功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 70)
print("GUI Agent 坐标标注功能测试")
print("=" * 70)
print()

try:
    import pyautogui
    from PIL import Image
    from io import BytesIO
    from search_engine.gui_agent_service import annotate_screenshot_with_coordinates
    
    # 1. 获取屏幕信息
    print("📋 步骤 1: 获取屏幕信息")
    print("-" * 70)
    
    logical_size = pyautogui.size()
    print(f"✅ 逻辑屏幕尺寸: {logical_size.width}x{logical_size.height}")
    
    # 2. 截取屏幕
    print()
    print("📋 步骤 2: 截取屏幕")
    print("-" * 70)
    
    screenshot = pyautogui.screenshot()
    print(f"✅ 截图分辨率: {screenshot.size[0]}x{screenshot.size[1]}")
    
    # 转换为 bytes
    buffer = BytesIO()
    screenshot.save(buffer, format='PNG')
    screenshot_bytes = buffer.getvalue()
    print(f"✅ 截图大小: {len(screenshot_bytes) / 1024:.1f} KB")
    
    # 3. 标注截图
    print()
    print("📋 步骤 3: 标注坐标基准点")
    print("-" * 70)
    
    annotated_bytes = annotate_screenshot_with_coordinates(
        screenshot_bytes,
        logical_size.width,
        logical_size.height
    )
    
    print(f"✅ 标注完成")
    print(f"   标注后大小: {len(annotated_bytes) / 1024:.1f} KB")
    
    # 4. 保存标注后的截图
    print()
    print("📋 步骤 4: 保存标注截图")
    print("-" * 70)
    
    annotated_img = Image.open(BytesIO(annotated_bytes))
    
    # 创建输出目录
    output_dir = Path("data/gui_screenshots")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"annotated_test_{timestamp}.png"
    annotated_img.save(output_path)
    
    print(f"✅ 已保存到: {output_path.absolute()}")
    print(f"   分辨率: {annotated_img.size[0]}x{annotated_img.size[1]}")
    
    # 5. 验证标注内容
    print()
    print("📋 步骤 5: 验证标注内容")
    print("-" * 70)
    
    print("标注的基准点：")
    print(f"  1. 左上角: (0, 0)")
    print(f"  2. 右上角: ({logical_size.width-1}, 0)")
    print(f"  3. 左下角: (0, {logical_size.height-1})")
    print(f"  4. 右下角: ({logical_size.width-1}, {logical_size.height-1})")
    print(f"  5. 中心点: ({logical_size.width//2}, {logical_size.height//2})")
    print()
    print(f"顶部显示: Screen: {logical_size.width}×{logical_size.height}")
    
    # 6. 效果说明
    print()
    print("=" * 70)
    print("📊 标注效果说明")
    print("=" * 70)
    print()
    print("✅ 标注成功！")
    print()
    print("标注内容：")
    print("  🔴 红色圆点：标记 5 个关键坐标位置")
    print("  ⬛ 黑色背景：坐标标签的半透明背景")
    print("  ⬜ 白色文字：坐标数值（逻辑像素）")
    print("  🟢 绿色文字：顶部的分辨率信息")
    print()
    print("这些标注将帮助 VLM：")
    print("  1. 清楚地看到坐标系统的边界")
    print("  2. 通过中心点了解屏幕的中央位置")
    print("  3. 参考基准点来准确推算目标元素的坐标")
    print()
    print(f"请打开以下文件查看效果：")
    print(f"  {output_path.absolute()}")
    print()
    print("=" * 70)
    
except Exception as e:
    import traceback
    print(f"❌ 测试失败: {e}")
    print()
    print(traceback.format_exc())
    sys.exit(1)


