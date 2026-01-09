#!/bin/bash
# Wide & Deep CTR 模型 TensorFlow Serving 一键构建与运行脚本
#
# 使用说明:
#   chmod +x build_and_run.sh
#   ./build_and_run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "🚀 Wide & Deep CTR 模型 TensorFlow Serving 部署"
echo "============================================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "   安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker 已安装: $(docker --version)"
echo ""

# 步骤1: 检查/创建示例模型
echo "📦 步骤 1/4: 准备模型..."
MODEL_DIR="$SCRIPT_DIR/exported_models/wide_deep_ctr/1"

if [ -d "$MODEL_DIR" ]; then
    echo "   ✅ 模型已存在: $MODEL_DIR"
else
    echo "   ⚠️  模型不存在，创建示例模型..."
    
    # 检查 Python 和 TensorFlow
    if command -v python3 &> /dev/null; then
        cd "$SCRIPT_DIR"
        python3 export_model.py --create-sample
        if [ $? -ne 0 ]; then
            echo "   ❌ 创建示例模型失败"
            exit 1
        fi
    else
        echo "   ❌ Python3 未安装，无法创建示例模型"
        exit 1
    fi
fi
echo ""

# 步骤2: 构建 Docker 镜像
echo "🔨 步骤 2/4: 构建 Docker 镜像..."
cd "$SCRIPT_DIR"
docker build -t wide-deep-serving . 

if [ $? -ne 0 ]; then
    echo "❌ Docker 镜像构建失败"
    exit 1
fi
echo "   ✅ Docker 镜像构建成功"
echo ""

# 步骤3: 停止已存在的容器
echo "🛑 步骤 3/4: 清理已存在的容器..."
if docker ps -a | grep -q wide-deep-ctr-serving; then
    docker stop wide-deep-ctr-serving 2>/dev/null || true
    docker rm wide-deep-ctr-serving 2>/dev/null || true
    echo "   ✅ 已清理旧容器"
else
    echo "   ✅ 无需清理"
fi
echo ""

# 步骤4: 启动容器
echo "🚀 步骤 4/4: 启动 TensorFlow Serving 容器..."
docker run -d \
    --name wide-deep-ctr-serving \
    -p 8500:8500 \
    -p 8501:8501 \
    --restart unless-stopped \
    wide-deep-serving

if [ $? -ne 0 ]; then
    echo "❌ 容器启动失败"
    exit 1
fi
echo "   ✅ 容器启动成功"
echo ""

# 等待服务就绪
echo "⏳ 等待服务就绪..."
for i in {1..30}; do
    if curl -s http://localhost:8501/v1/models/wide_deep_ctr > /dev/null 2>&1; then
        echo "   ✅ 服务已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  服务启动超时，请检查容器日志: docker logs wide-deep-ctr-serving"
    fi
    sleep 1
done
echo ""

# 显示服务信息
echo "============================================================"
echo "🎉 部署完成!"
echo "============================================================"
echo ""
echo "📋 服务信息:"
echo "   容器名称: wide-deep-ctr-serving"
echo "   REST API: http://localhost:8501"
echo "   gRPC:     localhost:8500"
echo ""
echo "📡 可用接口:"
echo "   模型状态: curl http://localhost:8501/v1/models/wide_deep_ctr"
echo "   模型元数据: curl http://localhost:8501/v1/models/wide_deep_ctr/metadata"
echo ""
echo "🔮 预测示例:"
cat << 'EOF'
curl -X POST http://localhost:8501/v1/models/wide_deep_ctr:predict \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [{
      "wide": [1.0, 0.5, 0.8, 0.3, 0.1, 0.2],
      "deep": [10.0, 5.0, 20.0, 3.0, 8.0, 0.5, 0.6, 0.1],
      "query_hash": 123,
      "doc_hash": 456,
      "position_group": 0
    }]
  }'
EOF
echo ""
echo "🛠️  管理命令:"
echo "   查看日志: docker logs -f wide-deep-ctr-serving"
echo "   停止服务: docker stop wide-deep-ctr-serving"
echo "   启动服务: docker start wide-deep-ctr-serving"
echo "   删除容器: docker rm -f wide-deep-ctr-serving"
echo ""
echo "============================================================"
