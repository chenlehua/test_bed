#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wide & Deep 模型导出脚本
将训练好的 Wide & Deep 模型导出为 TensorFlow Serving 可用的 SavedModel 格式
"""

import os
import sys
import argparse
import shutil
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import tensorflow as tf
    from tensorflow import keras
except ImportError:
    print("❌ TensorFlow 未安装，请运行: pip install tensorflow")
    sys.exit(1)


def export_wide_deep_model(
    input_model_path: str = "models/wide_deep_ctr_model.h5",
    output_dir: str = "tf_serving/exported_models/wide_deep_ctr",
    version: int = None
):
    """
    导出 Wide & Deep 模型为 TensorFlow Serving SavedModel 格式
    
    Args:
        input_model_path: 输入模型路径 (.h5 格式)
        output_dir: 输出目录
        version: 模型版本号（默认使用时间戳）
    """
    print("=" * 60)
    print("🚀 Wide & Deep 模型导出工具")
    print("=" * 60)
    
    # 检查输入模型是否存在
    if not os.path.exists(input_model_path):
        print(f"❌ 模型文件不存在: {input_model_path}")
        print("\n💡 提示：请先训练 Wide & Deep 模型，或指定正确的模型路径")
        print("   训练命令: 在系统 UI 中使用 Training 标签页训练模型")
        return False
    
    print(f"📂 输入模型: {input_model_path}")
    
    try:
        # 加载模型
        print("📥 加载模型...")
        model = keras.models.load_model(input_model_path)
        print(f"✅ 模型加载成功")
        
        # 打印模型信息
        print(f"\n📋 模型信息:")
        print(f"   输入层: {[layer.name for layer in model.inputs]}")
        print(f"   输出层: {[layer.name for layer in model.outputs]}")
        
        # 生成版本号
        if version is None:
            version = int(datetime.now().strftime("%Y%m%d%H%M%S"))
        
        # 创建输出目录
        version_dir = os.path.join(output_dir, str(version))
        os.makedirs(version_dir, exist_ok=True)
        
        print(f"\n📤 导出模型到: {version_dir}")
        
        # 导出为 SavedModel 格式
        model.save(version_dir, save_format='tf')
        
        print(f"✅ 模型导出成功!")
        print(f"\n📊 导出信息:")
        print(f"   模型路径: {version_dir}")
        print(f"   模型版本: {version}")
        print(f"   格式: TensorFlow SavedModel")
        
        # 验证导出的模型
        print(f"\n🔍 验证导出的模型...")
        loaded_model = tf.saved_model.load(version_dir)
        print(f"✅ 模型验证成功")
        
        # 打印签名信息
        if hasattr(loaded_model, 'signatures'):
            print(f"\n📝 模型签名:")
            for sig_name in loaded_model.signatures.keys():
                print(f"   - {sig_name}")
        
        print("\n" + "=" * 60)
        print("🎉 导出完成! 可以使用 TensorFlow Serving 部署此模型")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_sample_model_for_testing(output_dir: str = "tf_serving/exported_models/wide_deep_ctr"):
    """
    创建一个示例模型用于测试（当没有训练好的模型时）
    """
    print("=" * 60)
    print("🔧 创建示例 Wide & Deep 模型用于测试")
    print("=" * 60)
    
    try:
        # 模型参数
        wide_dim = 6  # Wide 特征维度
        deep_dim = 8  # Deep 特征维度
        vocab_sizes = {
            'query_hash': 1000,
            'doc_hash': 1000,
            'position_group': 3
        }
        
        # Wide部分输入
        wide_input = keras.Input(shape=(wide_dim,), name='wide')
        
        # Deep部分输入
        deep_input = keras.Input(shape=(deep_dim,), name='deep')
        
        # 分类特征输入
        query_input = keras.Input(shape=(), name='query_hash', dtype='int32')
        doc_input = keras.Input(shape=(), name='doc_hash', dtype='int32')
        position_input = keras.Input(shape=(), name='position_group', dtype='int32')
        
        # 嵌入层
        query_embedding = keras.layers.Embedding(vocab_sizes['query_hash'], 8)(query_input)
        doc_embedding = keras.layers.Embedding(vocab_sizes['doc_hash'], 8)(doc_input)
        position_embedding = keras.layers.Embedding(vocab_sizes['position_group'], 4)(position_input)
        
        # 展平
        query_flat = keras.layers.Flatten()(query_embedding)
        doc_flat = keras.layers.Flatten()(doc_embedding)
        position_flat = keras.layers.Flatten()(position_embedding)
        
        # Deep部分
        deep_concat = keras.layers.Concatenate()([deep_input, query_flat, doc_flat, position_flat])
        deep_hidden1 = keras.layers.Dense(128, activation='relu')(deep_concat)
        deep_hidden2 = keras.layers.Dense(64, activation='relu')(deep_hidden1)
        deep_hidden3 = keras.layers.Dense(32, activation='relu')(deep_hidden2)
        
        # Wide & Deep 合并
        wide_deep_concat = keras.layers.Concatenate()([wide_input, deep_hidden3])
        
        # 输出层
        output = keras.layers.Dense(1, activation='sigmoid', name='output')(wide_deep_concat)
        
        # 创建模型
        model = keras.Model(
            inputs=[wide_input, deep_input, query_input, doc_input, position_input],
            outputs=output,
            name='wide_and_deep_ctr'
        )
        
        # 编译模型
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # 生成版本号
        version = 1
        version_dir = os.path.join(output_dir, str(version))
        
        # 清理已存在的目录
        if os.path.exists(version_dir):
            shutil.rmtree(version_dir)
        
        os.makedirs(version_dir, exist_ok=True)
        
        # 导出模型
        print(f"📤 导出示例模型到: {version_dir}")
        model.save(version_dir, save_format='tf')
        
        print(f"✅ 示例模型创建成功!")
        print(f"\n📋 模型信息:")
        print(f"   Wide 特征维度: {wide_dim}")
        print(f"   Deep 特征维度: {deep_dim}")
        print(f"   Query Hash 桶数: {vocab_sizes['query_hash']}")
        print(f"   Doc Hash 桶数: {vocab_sizes['doc_hash']}")
        print(f"   Position 分组数: {vocab_sizes['position_group']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建示例模型失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Wide & Deep 模型导出工具')
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='models/wide_deep_ctr_model.h5',
        help='输入模型路径 (.h5 格式)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='tf_serving/exported_models/wide_deep_ctr',
        help='输出目录'
    )
    parser.add_argument(
        '--version', '-v',
        type=int,
        default=None,
        help='模型版本号 (默认使用时间戳)'
    )
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='创建示例模型用于测试'
    )
    
    args = parser.parse_args()
    
    if args.create_sample:
        success = create_sample_model_for_testing(args.output)
    else:
        success = export_wide_deep_model(args.input, args.output, args.version)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
