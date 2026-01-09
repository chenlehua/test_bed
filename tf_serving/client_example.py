#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TensorFlow Serving 客户端示例
演示如何调用部署在 TensorFlow Serving 上的 Wide & Deep CTR 模型
"""

import json
import requests
import numpy as np
from typing import Dict, Any, List, Optional


class WideDeepServingClient:
    """Wide & Deep 模型 TensorFlow Serving 客户端"""
    
    def __init__(self, host: str = "localhost", port: int = 8501, model_name: str = "wide_deep_ctr"):
        """
        初始化客户端
        
        Args:
            host: TensorFlow Serving 主机地址
            port: REST API 端口 (默认 8501)
            model_name: 模型名称
        """
        self.base_url = f"http://{host}:{port}"
        self.model_name = model_name
        self.predict_url = f"{self.base_url}/v1/models/{model_name}:predict"
        self.model_url = f"{self.base_url}/v1/models/{model_name}"
    
    def check_model_status(self) -> Dict[str, Any]:
        """
        检查模型状态
        
        Returns:
            模型状态信息
        """
        try:
            response = requests.get(self.model_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_model_metadata(self) -> Dict[str, Any]:
        """
        获取模型元数据
        
        Returns:
            模型元数据信息
        """
        try:
            response = requests.get(f"{self.model_url}/metadata")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def predict(
        self,
        wide_features: List[float],
        deep_features: List[float],
        query_hash: int,
        doc_hash: int,
        position_group: int,
        model_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        单样本预测
        
        Args:
            wide_features: Wide 特征向量 (6维)
            deep_features: Deep 特征向量 (8维)
            query_hash: 查询哈希值 (0-999)
            doc_hash: 文档哈希值 (0-999)
            position_group: 位置分组 (0-2)
            model_version: 模型版本号 (可选)
        
        Returns:
            预测结果
        """
        # 构建请求数据
        request_data = {
            "instances": [
                {
                    "wide": wide_features,
                    "deep": deep_features,
                    "query_hash": query_hash,
                    "doc_hash": doc_hash,
                    "position_group": position_group
                }
            ]
        }
        
        # 构建 URL
        url = self.predict_url
        if model_version:
            url = f"{self.base_url}/v1/models/{self.model_name}/versions/{model_version}:predict"
        
        try:
            response = requests.post(url, json=request_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def batch_predict(
        self,
        samples: List[Dict[str, Any]],
        model_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        批量预测
        
        Args:
            samples: 样本列表，每个样本包含:
                - wide: Wide 特征向量
                - deep: Deep 特征向量
                - query_hash: 查询哈希值
                - doc_hash: 文档哈希值
                - position_group: 位置分组
            model_version: 模型版本号 (可选)
        
        Returns:
            批量预测结果
        """
        # 构建请求数据
        request_data = {
            "instances": samples
        }
        
        # 构建 URL
        url = self.predict_url
        if model_version:
            url = f"{self.base_url}/v1/models/{self.model_name}/versions/{model_version}:predict"
        
        try:
            response = requests.post(url, json=request_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


def generate_sample_features() -> Dict[str, Any]:
    """生成示例特征用于测试"""
    return {
        "wide": [1.0, 0.5, 0.8, 0.3, 0.1, 0.2],  # 6维 Wide 特征
        "deep": [10.0, 5.0, 20.0, 3.0, 8.0, 0.5, 0.6, 0.1],  # 8维 Deep 特征
        "query_hash": np.random.randint(0, 1000),  # 查询哈希
        "doc_hash": np.random.randint(0, 1000),  # 文档哈希
        "position_group": np.random.randint(0, 3)  # 位置分组
    }


def main():
    """主函数 - 演示客户端使用"""
    print("=" * 60)
    print("🚀 TensorFlow Serving Wide & Deep 客户端示例")
    print("=" * 60)
    
    # 创建客户端
    client = WideDeepServingClient(
        host="localhost",
        port=8501,
        model_name="wide_deep_ctr"
    )
    
    # 1. 检查模型状态
    print("\n📊 检查模型状态...")
    status = client.check_model_status()
    print(json.dumps(status, indent=2))
    
    if "error" in status:
        print("\n❌ 无法连接到 TensorFlow Serving，请确保服务已启动")
        print("   启动命令: docker run -p 8501:8501 -p 8500:8500 wide-deep-serving")
        return
    
    # 2. 获取模型元数据
    print("\n📋 获取模型元数据...")
    metadata = client.get_model_metadata()
    print(json.dumps(metadata, indent=2))
    
    # 3. 单样本预测
    print("\n🔮 单样本预测...")
    sample = generate_sample_features()
    print(f"   输入特征: {sample}")
    
    result = client.predict(
        wide_features=sample["wide"],
        deep_features=sample["deep"],
        query_hash=int(sample["query_hash"]),
        doc_hash=int(sample["doc_hash"]),
        position_group=int(sample["position_group"])
    )
    print(f"   预测结果: {result}")
    
    # 4. 批量预测
    print("\n📦 批量预测 (3个样本)...")
    batch_samples = []
    for i in range(3):
        s = generate_sample_features()
        batch_samples.append({
            "wide": s["wide"],
            "deep": s["deep"],
            "query_hash": int(s["query_hash"]),
            "doc_hash": int(s["doc_hash"]),
            "position_group": int(s["position_group"])
        })
    
    batch_result = client.batch_predict(batch_samples)
    print(f"   批量预测结果: {batch_result}")
    
    # 5. 性能测试
    print("\n⏱️  性能测试 (100次预测)...")
    import time
    start_time = time.time()
    
    for _ in range(100):
        s = generate_sample_features()
        client.predict(
            wide_features=s["wide"],
            deep_features=s["deep"],
            query_hash=int(s["query_hash"]),
            doc_hash=int(s["doc_hash"]),
            position_group=int(s["position_group"])
        )
    
    elapsed_time = time.time() - start_time
    print(f"   总耗时: {elapsed_time:.2f}秒")
    print(f"   平均延迟: {elapsed_time/100*1000:.2f}ms")
    print(f"   QPS: {100/elapsed_time:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ 客户端示例运行完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
