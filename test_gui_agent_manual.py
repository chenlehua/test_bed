#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI-Agent 命令行测试 - 手动实现每一步
演示：启动虚拟机 → 截图 → 调用模型 → 解析动作 → 控制虚拟机
"""

import os
import sys
import time
import base64
import json
import re
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageGrab
from datetime import datetime


class ManualGUIAgentTest:
    """手动实现 GUI-Agent 的每一步，用于测试和演示"""
    
    def __init__(self, use_docker=True, model="gpt-4o"):
        self.use_docker = use_docker
        self.model = model
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        
        # 创建截图保存目录
        self.screenshot_dir = Path('data/gui_agent_test/screenshots')
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔧 初始化测试环境")
        print(f"   使用 Docker: {use_docker}")
        print(f"   模型: {model}")
        print(f"   截图目录: {self.screenshot_dir}")
        print()
    
    def step1_start_vm(self):
        """步骤1: 启动虚拟机（Docker 或本地）"""
        print("=" * 60)
        print("📦 步骤1: 启动虚拟机")
        print("=" * 60)
        
        if self.use_docker:
            print("🐳 使用 Docker 容器作为虚拟机...")
            print()
            print("Docker 命令示例（基于 OSWorld）：")
            print("  docker run -d \\")
            print("    --name gui-agent-vm \\")
            print("    -e DISPLAY=:0 \\")
            print("    -v /tmp/.X11-unix:/tmp/.X11-unix \\")
            print("    ubuntu:22.04")
            print()
            print("💡 注意：OSWorld 使用特殊的 Docker 镜像，包含桌面环境")
            print("   参考：https://github.com/xlang-ai/OSWorld#docker")
            print()
            
            # 检查 Docker 是否安装
            import subprocess
            try:
                result = subprocess.run(['docker', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ Docker 已安装: {result.stdout.strip()}")
                else:
                    print("⚠️  Docker 未安装或无法访问")
            except Exception as e:
                print(f"⚠️  Docker 检查失败: {e}")
        else:
            print("🖥️  使用本地环境（不推荐用于生产）")
            print("   本地模式会直接控制当前系统")
        
        print()
        input("按 Enter 继续到下一步...")
        return True
    
    def step2_capture_screenshot(self):
        """步骤2: 截取屏幕"""
        print()
        print("=" * 60)
        print("📸 步骤2: 截取屏幕")
        print("=" * 60)
        
        try:
            print("正在截图...")
            
            # 使用 PIL 截图（本地）
            screenshot = ImageGrab.grab()
            
            # 保存截图
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.screenshot_dir / f'test_{timestamp}.png'
            screenshot.save(screenshot_path)
            
            # 转换为 bytes
            buffer = BytesIO()
            screenshot.save(buffer, format='PNG')
            screenshot_bytes = buffer.getvalue()
            
            print(f"✅ 截图成功:")
            print(f"   尺寸: {screenshot.size}")
            print(f"   大小: {len(screenshot_bytes) / 1024:.2f} KB")
            print(f"   保存: {screenshot_path}")
            print()
            
            if self.use_docker:
                print("💡 Docker 环境截图方法:")
                print("   1. docker exec gui-agent-vm import -window root screenshot.png")
                print("   2. docker cp gui-agent-vm:/screenshot.png ./")
                print("   3. 或使用 VNC/X11 转发捕获")
            
            print()
            input("按 Enter 继续到下一步...")
            
            return screenshot_bytes, screenshot_path
            
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return None, None
    
    def step3_call_vl_model(self, screenshot_bytes, instruction):
        """步骤3: 调用视觉语言模型"""
        print()
        print("=" * 60)
        print("🤖 步骤3: 调用视觉语言模型")
        print("=" * 60)
        
        if not self.api_key:
            print("⚠️  未设置 OPENAI_API_KEY，跳过实际调用")
            print()
            print("模拟响应示例：")
            mock_response = """
我看到了屏幕截图。为了完成任务「打开终端」，我需要执行以下操作：

1. 点击屏幕左下角的应用菜单
2. 在搜索框中输入 "terminal"
3. 点击终端应用

```python
pyautogui.click(x=50, y=950)
pyautogui.typewrite('terminal')
pyautogui.press('enter')
```
"""
            print(mock_response)
            print()
            input("按 Enter 继续到下一步...")
            return mock_response
        
        try:
            print(f"任务指令: {instruction}")
            print(f"模型: {self.model}")
            print()
            
            # 编码截图为 base64
            print("编码截图为 base64...")
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            print(f"✅ Base64 长度: {len(screenshot_b64)} 字符")
            print()
            
            # 构造 prompt
            system_prompt = """你是一个桌面自动化代理，能够通过 PyAutoGUI 控制计算机完成任务。

你需要：
1. 观察当前屏幕截图
2. 理解用户任务
3. 规划下一步动作
4. 输出 PyAutoGUI 代码

可用的动作：
- pyautogui.moveTo(x, y)  # 移动鼠标
- pyautogui.click()  # 点击
- pyautogui.click(x=x, y=y)  # 在指定位置点击
- pyautogui.doubleClick()  # 双击
- pyautogui.rightClick()  # 右键
- pyautogui.typewrite('text')  # 输入文本（仅英文）
- pyautogui.press('enter')  # 按键
- pyautogui.hotkey('ctrl', 'c')  # 组合键
- DONE  # 任务完成
- FAIL  # 任务失败
- WAIT  # 等待

请按以下格式输出：
1. 首先描述你的观察和思考
2. 然后在代码块中输出 PyAutoGUI 命令（每行一个命令）

示例：
我看到屏幕上有一个按钮在坐标(100, 200)，我需要点击它。
```python
pyautogui.click(x=100, y=200)
```"""

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"任务: {instruction}\n\n请分析当前屏幕截图并规划下一步动作。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_b64}"
                            }
                        }
                    ]
                }
            ]
            
            print("发送请求到 OpenAI API...")
            print(f"API 端点: {self.base_url}")
            
            # 调用 OpenAI API
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            print("✅ 模型响应:")
            print("-" * 60)
            print(response_text)
            print("-" * 60)
            print()
            
            # 显示使用情况
            if hasattr(response, 'usage'):
                print(f"Token 使用:")
                print(f"  Prompt: {response.usage.prompt_tokens}")
                print(f"  Completion: {response.usage.completion_tokens}")
                print(f"  Total: {response.usage.total_tokens}")
            
            print()
            input("按 Enter 继续到下一步...")
            
            return response_text
            
        except Exception as e:
            print(f"❌ API 调用失败: {e}")
            print()
            print("使用模拟响应继续...")
            mock_response = """
我需要执行任务。以下是动作：

```python
pyautogui.click(x=100, y=100)
WAIT
```
"""
            return mock_response
    
    def step4_parse_actions(self, response_text):
        """步骤4: 解析动作"""
        print()
        print("=" * 60)
        print("🔍 步骤4: 解析动作")
        print("=" * 60)
        
        actions = []
        
        # 提取代码块
        code_blocks = re.findall(r'```python\n(.*?)```', response_text, re.DOTALL)
        
        print(f"找到 {len(code_blocks)} 个代码块")
        print()
        
        if code_blocks:
            for i, block in enumerate(code_blocks):
                print(f"代码块 {i+1}:")
                print(block.strip())
                print()
                
                lines = block.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    # 只接受 pyautogui 命令或控制符
                    if line.startswith('pyautogui.') or line in ['DONE', 'FAIL', 'WAIT']:
                        actions.append(line)
        
        # 如果没有找到代码块，尝试直接提取
        if not actions:
            print("未找到代码块，尝试直接提取...")
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('pyautogui.') or line in ['DONE', 'FAIL', 'WAIT']:
                    actions.append(line)
        
        print(f"✅ 解析出 {len(actions)} 个动作:")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action}")
        
        print()
        
        # 安全检查
        print("安全检查:")
        safe_actions = []
        for action in actions:
            # 检查是否为安全的命令
            if action in ['DONE', 'FAIL', 'WAIT']:
                safe_actions.append(action)
                print(f"  ✅ {action} - 控制符")
            elif action.startswith('pyautogui.'):
                # 简单验证语法
                try:
                    # 检查是否包含危险操作
                    if any(dangerous in action for dangerous in ['os.', 'subprocess.', 'eval', 'exec']):
                        print(f"  ⚠️  {action} - 包含危险操作，跳过")
                    else:
                        safe_actions.append(action)
                        print(f"  ✅ {action}")
                except:
                    print(f"  ⚠️  {action} - 语法错误，跳过")
            else:
                print(f"  ⚠️  {action} - 未知命令，跳过")
        
        print()
        print(f"安全动作数: {len(safe_actions)}/{len(actions)}")
        print()
        input("按 Enter 继续到下一步...")
        
        return safe_actions
    
    def step5_execute_actions(self, actions):
        """步骤5: 执行动作"""
        print()
        print("=" * 60)
        print("⚡ 步骤5: 执行动作")
        print("=" * 60)
        
        if not actions:
            print("⚠️  没有可执行的动作")
            return
        
        # 检查是否真的要执行
        print("⚠️  警告：即将在系统中执行以下动作：")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action}")
        print()
        
        if self.use_docker:
            print("💡 Docker 环境中执行动作的方法:")
            print("   1. 通过 VNC 连接到容器桌面")
            print("   2. 使用 docker exec 在容器内运行 PyAutoGUI")
            print("   3. 或使用 X11 转发")
            print()
            print("示例命令:")
            print("   docker exec gui-agent-vm python3 -c \"import pyautogui; pyautogui.click(100, 100)\"")
            print()
        
        response = input("是否真的执行？(yes/no): ")
        if response.lower() != 'yes':
            print("❌ 取消执行")
            return
        
        print()
        print("开始执行...")
        
        try:
            import pyautogui
            
            for i, action in enumerate(actions, 1):
                print(f"\n执行动作 {i}/{len(actions)}: {action}")
                
                # 处理控制符
                if action == 'DONE':
                    print("✅ 任务完成")
                    break
                elif action == 'FAIL':
                    print("❌ 任务失败")
                    break
                elif action == 'WAIT':
                    print("⏸️  等待...")
                    time.sleep(1)
                    continue
                
                # 执行 PyAutoGUI 命令
                try:
                    # 在安全的命名空间中执行
                    namespace = {'pyautogui': pyautogui}
                    exec(action, namespace)
                    print(f"  ✅ 执行成功")
                    
                    # 等待界面响应
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  ❌ 执行失败: {e}")
            
            print()
            print("✅ 所有动作执行完成")
            
        except ImportError:
            print("❌ PyAutoGUI 未安装")
            print("   pip install pyautogui")
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    def run_full_test(self, instruction="打开终端并输入 echo Hello"):
        """运行完整测试流程"""
        print()
        print("=" * 60)
        print("🚀 GUI-Agent 完整流程测试")
        print("=" * 60)
        print(f"任务: {instruction}")
        print()
        
        # 步骤1: 启动虚拟机
        if not self.step1_start_vm():
            return
        
        # 步骤2: 截图
        screenshot_bytes, screenshot_path = self.step2_capture_screenshot()
        if not screenshot_bytes:
            return
        
        # 步骤3: 调用模型
        response_text = self.step3_call_vl_model(screenshot_bytes, instruction)
        if not response_text:
            return
        
        # 步骤4: 解析动作
        actions = self.step4_parse_actions(response_text)
        if not actions:
            return
        
        # 步骤5: 执行动作
        self.step5_execute_actions(actions)
        
        print()
        print("=" * 60)
        print("🎉 测试完成！")
        print("=" * 60)
        print()
        print(f"截图保存在: {screenshot_path}")
        print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GUI-Agent 手动测试')
    parser.add_argument('--no-docker', action='store_true', help='不使用 Docker（直接在本地执行）')
    parser.add_argument('--model', default='gpt-4o', help='使用的模型（默认: gpt-4o）')
    parser.add_argument('--task', default='打开终端', help='任务指令')
    
    args = parser.parse_args()
    
    # 创建测试实例
    tester = ManualGUIAgentTest(
        use_docker=not args.no_docker,
        model=args.model
    )
    
    # 运行完整测试
    tester.run_full_test(instruction=args.task)


if __name__ == '__main__':
    main()

