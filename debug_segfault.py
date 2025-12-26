#!/usr/bin/env python3
"""调试 segmentation fault 的测试脚本"""

import sys
print("✅ Python 启动成功")

try:
    import numpy as np
    print(f"✅ NumPy {np.__version__} 导入成功")
except Exception as e:
    print(f"❌ NumPy 导入失败: {e}")
    sys.exit(1)

try:
    import sklearn
    print(f"✅ Scikit-learn {sklearn.__version__} 导入成功")
except Exception as e:
    print(f"❌ Scikit-learn 导入失败: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print(f"✅ Pandas {pd.__version__} 导入成功")
except Exception as e:
    print(f"❌ Pandas 导入失败: {e}")
    sys.exit(1)

try:
    import tensorflow as tf
    print(f"✅ TensorFlow {tf.__version__} 导入成功")
except Exception as e:
    print(f"❌ TensorFlow 导入失败: {e}")
    # TensorFlow 失败不退出，继续测试

try:
    import threading
    print("✅ Threading 模块导入成功")
    
    def test_thread():
        import numpy as np
        arr = np.array([1, 2, 3])
        print(f"  线程内 NumPy 测试: {arr.sum()}")
    
    t = threading.Thread(target=test_thread)
    t.start()
    t.join()
    print("✅ Threading + NumPy 测试通过")
except Exception as e:
    print(f"❌ Threading 测试失败: {e}")
    sys.exit(1)

try:
    from sklearn.linear_model import LogisticRegression
    print("✅ Scikit-learn LogisticRegression 导入成功")
    
    # 简单训练测试
    X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    y = np.array([0, 0, 1, 1])
    model = LogisticRegression()
    model.fit(X, y)
    print("✅ LogisticRegression 训练测试通过")
except Exception as e:
    print(f"❌ Scikit-learn 训练测试失败: {e}")
    sys.exit(1)

try:
    import gradio as gr
    print(f"✅ Gradio 导入成功")
except Exception as e:
    print(f"❌ Gradio 导入失败: {e}")

print("\n" + "="*50)
print("🎉 所有基础测试通过！")
print("="*50)

