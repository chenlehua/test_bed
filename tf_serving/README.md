# Wide & Deep CTR 模型 TensorFlow Serving 部署

本目录包含将 Wide & Deep CTR 模型部署到 TensorFlow Serving 的所有必要文件。

## 📁 文件结构

```
tf_serving/
├── README.md              # 本文档
├── Dockerfile             # Docker 镜像构建文件
├── docker-compose.yml     # Docker Compose 配置
├── models.config          # TensorFlow Serving 模型配置
├── export_model.py        # 模型导出脚本
├── client_example.py      # Python 客户端示例
├── build_and_run.sh       # 一键构建运行脚本
└── exported_models/       # 导出的模型目录
    └── wide_deep_ctr/
        └── 1/             # 模型版本 1
            ├── saved_model.pb
            └── variables/
```

## 🚀 快速开始

### 方式一：一键部署（推荐）

```bash
cd tf_serving
chmod +x build_and_run.sh
./build_and_run.sh
```

### 方式二：手动部署

#### 1. 导出模型

如果你已经训练了 Wide & Deep 模型：

```bash
# 导出已训练的模型
python export_model.py --input models/wide_deep_ctr_model.h5

# 或创建示例模型用于测试
python export_model.py --create-sample
```

#### 2. 构建 Docker 镜像

```bash
docker build -t wide-deep-serving .
```

#### 3. 运行容器

```bash
docker run -d \
  --name wide-deep-ctr-serving \
  -p 8500:8500 \
  -p 8501:8501 \
  wide-deep-serving
```

#### 4. 验证服务

```bash
# 检查模型状态
curl http://localhost:8501/v1/models/wide_deep_ctr

# 查看模型元数据
curl http://localhost:8501/v1/models/wide_deep_ctr/metadata
```

## 📡 API 接口

### REST API (端口 8501)

#### 模型状态

```bash
GET http://localhost:8501/v1/models/wide_deep_ctr
```

响应示例：
```json
{
  "model_version_status": [
    {
      "version": "1",
      "state": "AVAILABLE",
      "status": {
        "error_code": "OK",
        "error_message": ""
      }
    }
  ]
}
```

#### 单样本预测

```bash
POST http://localhost:8501/v1/models/wide_deep_ctr:predict
Content-Type: application/json

{
  "instances": [{
    "wide": [1.0, 0.5, 0.8, 0.3, 0.1, 0.2],
    "deep": [10.0, 5.0, 20.0, 3.0, 8.0, 0.5, 0.6, 0.1],
    "query_hash": 123,
    "doc_hash": 456,
    "position_group": 0
  }]
}
```

响应示例：
```json
{
  "predictions": [[0.7523456]]
}
```

#### 批量预测

```bash
POST http://localhost:8501/v1/models/wide_deep_ctr:predict
Content-Type: application/json

{
  "instances": [
    {
      "wide": [1.0, 0.5, 0.8, 0.3, 0.1, 0.2],
      "deep": [10.0, 5.0, 20.0, 3.0, 8.0, 0.5, 0.6, 0.1],
      "query_hash": 123,
      "doc_hash": 456,
      "position_group": 0
    },
    {
      "wide": [2.0, 0.3, 0.6, 0.5, 0.2, 0.1],
      "deep": [15.0, 8.0, 25.0, 5.0, 10.0, 0.7, 0.4, 0.2],
      "query_hash": 789,
      "doc_hash": 101,
      "position_group": 1
    }
  ]
}
```

#### 指定版本预测

```bash
POST http://localhost:8501/v1/models/wide_deep_ctr/versions/1:predict
```

### gRPC API (端口 8500)

gRPC 提供更高性能的调用方式，适合高并发场景。

```python
import grpc
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

# 创建 gRPC channel
channel = grpc.insecure_channel('localhost:8500')
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

# 构建请求
request = predict_pb2.PredictRequest()
request.model_spec.name = 'wide_deep_ctr'
request.model_spec.signature_name = 'serving_default'
# ... 设置输入张量 ...

# 发送请求
response = stub.Predict(request)
```

## 📊 输入特征说明

| 特征名 | 类型 | 维度 | 说明 |
|-------|------|------|------|
| `wide` | float32 | [6] | Wide 线性特征（位置、分数、匹配度等） |
| `deep` | float32 | [8] | Deep 非线性特征（长度、词数、时间等） |
| `query_hash` | int32 | [] | 查询哈希值 (0-999) |
| `doc_hash` | int32 | [] | 文档哈希值 (0-999) |
| `position_group` | int32 | [] | 位置分组 (0=头部, 1=中部, 2=尾部) |

### Wide 特征详情 (6维)

1. 位置 (position)
2. 位置衰减 (1/(position+1))
3. 原始相似度分数 (score)
4. 查询匹配度 (query-summary overlap)
5. 查询历史CTR
6. 文档历史CTR

### Deep 特征详情 (8维)

1. 文档长度 (doc_length)
2. 查询长度 (query_length)
3. 摘要长度 (summary_length)
4. 查询词数 (query_word_count)
5. 摘要词数 (summary_word_count)
6. 时间特征 (time_feature)
7. 位置×分数交叉特征
8. 查询长度×匹配度交叉特征

## 🔧 模型版本管理

### 部署新版本

1. 导出新模型到新版本目录：
```bash
python export_model.py --version 2
```

2. TensorFlow Serving 会自动检测并加载新版本

### 回滚到旧版本

修改 `models.config`，指定加载特定版本：

```protobuf
model_version_policy {
  specific {
    versions: 1
  }
}
```

### A/B 测试

使用版本标签进行流量分配：

```protobuf
version_labels {
  key: "stable"
  value: 1
}
version_labels {
  key: "canary"
  value: 2
}
```

## 🛠️ 运维命令

```bash
# 查看容器状态
docker ps | grep wide-deep

# 查看实时日志
docker logs -f wide-deep-ctr-serving

# 进入容器
docker exec -it wide-deep-ctr-serving /bin/bash

# 重启服务
docker restart wide-deep-ctr-serving

# 停止服务
docker stop wide-deep-ctr-serving

# 删除容器
docker rm -f wide-deep-ctr-serving
```

## 📈 性能优化

### 1. 启用批处理

编辑 Dockerfile，添加批处理参数：

```dockerfile
CMD ["--port=8500", \
     "--rest_api_port=8501", \
     "--model_config_file=/models/models.config", \
     "--enable_batching=true", \
     "--batching_parameters_file=/models/batching.config"]
```

创建 `batching.config`：

```protobuf
max_batch_size { value: 32 }
batch_timeout_micros { value: 5000 }
num_batch_threads { value: 4 }
```

### 2. GPU 加速

使用 GPU 版本的 TensorFlow Serving：

```dockerfile
FROM tensorflow/serving:2.14.0-gpu
```

运行时挂载 GPU：

```bash
docker run --gpus all -p 8501:8501 wide-deep-serving
```

### 3. 多实例负载均衡

使用 Docker Compose 或 Kubernetes 部署多个实例，配合 Nginx 或 Envoy 进行负载均衡。

## 🔍 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker logs wide-deep-ctr-serving

# 常见问题：
# 1. 端口被占用 -> 修改端口映射
# 2. 模型文件不存在 -> 检查 exported_models 目录
# 3. 模型格式错误 -> 重新导出模型
```

### 预测返回错误

```bash
# 检查模型状态
curl http://localhost:8501/v1/models/wide_deep_ctr

# 查看模型签名
curl http://localhost:8501/v1/models/wide_deep_ctr/metadata

# 常见问题：
# 1. 输入维度不匹配 -> 检查 wide/deep 特征维度
# 2. 数据类型错误 -> 确保 query_hash 等为整数
```

## 📚 参考资料

- [TensorFlow Serving 官方文档](https://www.tensorflow.org/tfx/guide/serving)
- [TensorFlow Serving REST API](https://www.tensorflow.org/tfx/serving/api_rest)
- [TensorFlow Serving 配置](https://www.tensorflow.org/tfx/serving/serving_config)
- [Wide & Deep 论文](https://arxiv.org/abs/1606.07792)
