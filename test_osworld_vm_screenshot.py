#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试：下载 OSWorld 虚拟机镜像，启动 Docker 容器，在虚拟机内截图
"""

import os
import sys
import time
import requests
import zipfile
import docker
from pathlib import Path
from tqdm import tqdm


# 虚拟机镜像 URL
UBUNTU_VM_URL = "https://huggingface.co/datasets/xlangai/ubuntu_osworld/resolve/main/Ubuntu.qcow2.zip"
VM_DIR = Path("data/osworld_vm")
UBUNTU_QCOW2 = VM_DIR / "Ubuntu.qcow2"


def download_vm_image():
    """下载虚拟机镜像"""
    print("=" * 60)
    print("📥 下载 OSWorld Ubuntu 虚拟机镜像")
    print("=" * 60)
    print()
    
    VM_DIR.mkdir(parents=True, exist_ok=True)
    
    # 检查是否已下载
    if UBUNTU_QCOW2.exists():
        file_size = UBUNTU_QCOW2.stat().st_size / (1024**3)
        print(f"✅ 镜像已存在: {UBUNTU_QCOW2}")
        print(f"   大小: {file_size:.2f} GB")
        return True
    
    zip_file = VM_DIR / "Ubuntu.qcow2.zip"
    
    # 检查 zip 文件
    if zip_file.exists():
        print(f"⚠️  发现 zip 文件，正在解压...")
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(VM_DIR)
            print(f"✅ 解压完成")
            zip_file.unlink()  # 删除 zip 文件节省空间
            return True
        except Exception as e:
            print(f"❌ 解压失败: {e}")
            zip_file.unlink()
    
    print(f"📦 镜像 URL: {UBUNTU_VM_URL}")
    print(f"⚠️  警告: 这个文件很大（约 10-20 GB），下载可能需要较长时间")
    print()
    print("⏭️  自动开始下载...")
    print()
    print("开始下载...")
    
    try:
        # 支持断点续传
        downloaded_size = 0
        if zip_file.exists():
            downloaded_size = zip_file.stat().st_size
        
        headers = {}
        if downloaded_size > 0:
            headers["Range"] = f"bytes={downloaded_size}-"
            print(f"继续下载（已下载: {downloaded_size / (1024**2):.2f} MB）...")
        
        response = requests.get(UBUNTU_VM_URL, headers=headers, stream=True, timeout=30)
        total_size = int(response.headers.get('content-length', 0)) + downloaded_size
        
        mode = 'ab' if downloaded_size > 0 else 'wb'
        with open(zip_file, mode) as f, tqdm(
            desc="下载进度",
            initial=downloaded_size,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
        
        print()
        print("✅ 下载完成")
        print()
        
        # 解压
        print("正在解压...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(VM_DIR)
        
        print("✅ 解压完成")
        zip_file.unlink()  # 删除 zip 文件
        
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False


def start_docker_with_vm():
    """启动 Docker 容器并挂载虚拟机镜像"""
    print()
    print("=" * 60)
    print("🐳 启动 Docker 容器（挂载虚拟机镜像）")
    print("=" * 60)
    print()
    
    try:
        client = docker.from_env()
        print("✅ Docker 客户端连接成功")
    except Exception as e:
        print(f"❌ Docker 连接失败: {e}")
        return None
    
    container_name = "osworld-vm-test"
    
    # 清理旧容器
    try:
        old_container = client.containers.get(container_name)
        print(f"清理已存在的容器...")
        old_container.stop()
        old_container.remove()
        time.sleep(2)
    except docker.errors.NotFound:
        pass
    
    # 启动容器
    print()
    print("启动容器...")
    
    # 端口配置
    vnc_port = 58006
    server_port = 55000
    chrome_port = 59222
    vlc_port = 58080
    
    # 环境变量
    environment = {
        "DISK_SIZE": "8G",
        "RAM_SIZE": "2G",
        "CPU_CORES": "2",
        "KVM": "N"  # macOS 不支持 KVM
    }
    
    print(f"  虚拟机镜像: {UBUNTU_QCOW2.absolute()}")
    print(f"  API 端口: {server_port}")
    print(f"  VNC 端口: {vnc_port}")
    print(f"  配置: {environment}")
    print()
    
    try:
        container = client.containers.run(
            "happysixd/osworld-docker",
            name=container_name,
            environment=environment,
            cap_add=["NET_ADMIN"],
            volumes={
                str(UBUNTU_QCOW2.absolute()): {
                    "bind": "/System.qcow2",
                    "mode": "ro"
                }
            },
            ports={
                8006: vnc_port,
                5000: server_port,
                9222: chrome_port,
                8080: vlc_port
            },
            detach=True
        )
        
        print(f"✅ 容器已启动: {container.short_id}")
        print()
        
        return {
            'container': container,
            'server_port': server_port,
            'vnc_port': vnc_port
        }
        
    except Exception as e:
        print(f"❌ 容器启动失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def wait_for_vm_ready(server_port, timeout=300):
    """等待虚拟机启动完成"""
    print("⏳ 等待虚拟机启动...")
    print(f"   这可能需要 2-5 分钟，请耐心等待...")
    print()
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(
                f"http://localhost:{server_port}/screenshot",
                timeout=10
            )
            if response.status_code == 200:
                print("✅ 虚拟机已就绪！")
                return True
        except:
            pass
        
        elapsed = int(time.time() - start_time)
        print(f"\r   等待中... {elapsed}s / {timeout}s", end='', flush=True)
        time.sleep(5)
    
    print()
    print(f"❌ 虚拟机启动超时（{timeout}秒）")
    return False


def capture_vm_screenshot(server_port):
    """从虚拟机中截图"""
    print()
    print("=" * 60)
    print("📸 在虚拟机内截图")
    print("=" * 60)
    print()
    
    try:
        print(f"调用 API: http://localhost:{server_port}/screenshot")
        response = requests.get(
            f"http://localhost:{server_port}/screenshot",
            timeout=30
        )
        
        if response.status_code == 200:
            # 保存截图
            screenshot_dir = Path("data/osworld_screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            screenshot_path = screenshot_dir / f"vm_screenshot_{int(time.time())}.png"
            screenshot_path.write_bytes(response.content)
            
            print(f"✅ 截图成功！")
            print(f"   保存位置: {screenshot_path}")
            print(f"   大小: {len(response.content) / 1024:.2f} KB")
            
            return screenshot_path
        else:
            print(f"❌ 截图失败: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        return None


def main():
    """主流程"""
    print()
    print("=" * 60)
    print("🚀 OSWorld Docker 虚拟机完整测试")
    print("=" * 60)
    print()
    
    # 步骤1: 下载虚拟机镜像
    if not download_vm_image():
        print("❌ 虚拟机镜像准备失败")
        return 1
    
    # 步骤2: 启动 Docker 容器
    container_info = start_docker_with_vm()
    if not container_info:
        print("❌ Docker 容器启动失败")
        return 1
    
    try:
        # 步骤3: 等待虚拟机就绪
        if not wait_for_vm_ready(container_info['server_port']):
            print("❌ 虚拟机启动失败")
            return 1
        
        # 步骤4: 截图
        screenshot_path = capture_vm_screenshot(container_info['server_port'])
        
        if screenshot_path:
            print()
            print("=" * 60)
            print("🎉 测试成功！")
            print("=" * 60)
            print()
            print(f"📸 虚拟机截图: {screenshot_path}")
            print(f"🌐 VNC 访问: http://localhost:{container_info['vnc_port']}")
            print()
            print("💡 提示:")
            print("   - 容器将继续运行，可以通过 VNC 查看桌面")
            print("   - 停止容器: docker stop osworld-vm-test && docker rm osworld-vm-test")
            print()
            return 0
        else:
            print("❌ 截图失败")
            return 1
            
    finally:
        # 容器保持运行以便查看结果
        print("\n💡 容器将继续运行")
        print(f"   查看日志: docker logs osworld-vm-test")
        print(f"   停止容器: docker stop osworld-vm-test && docker rm osworld-vm-test")


if __name__ == '__main__':
    sys.exit(main())

