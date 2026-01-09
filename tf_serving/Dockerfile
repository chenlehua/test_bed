# Wide & Deep CTR 模型 TensorFlow Serving 部署
# 
# 使用说明:
#   1. 构建镜像: docker build -t wide-deep-serving .
#   2. 运行容器: docker run -p 8501:8501 -p 8500:8500 wide-deep-serving
#
# 端口说明:
#   - 8500: gRPC 接口
#   - 8501: REST API 接口

FROM tensorflow/serving:2.14.0

# 设置工作目录
WORKDIR /models

# 复制模型文件
COPY exported_models/wide_deep_ctr /models/wide_deep_ctr

# 复制模型配置文件
COPY models.config /models/models.config

# 设置环境变量
ENV MODEL_NAME=wide_deep_ctr
ENV MODEL_BASE_PATH=/models/wide_deep_ctr

# 暴露端口
# 8500: gRPC
# 8501: REST API
EXPOSE 8500 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/v1/models/wide_deep_ctr || exit 1

# 启动 TensorFlow Serving
# 使用模型配置文件支持多模型和版本管理
ENTRYPOINT ["tensorflow_model_server"]
CMD ["--port=8500", \
     "--rest_api_port=8501", \
     "--model_config_file=/models/models.config", \
     "--allow_version_labels_for_unavailable_models=true"]
