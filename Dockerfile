# ZephyrAlpha 2.0 — 核心应用容器镜像
# Phase B: 开发/测试环境

FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖声明
COPY pyproject.toml requirements.txt requirements-dev.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# 以可编辑模式安装项目
COPY src/ ./src/
RUN pip install -e .

# 创建日志目录
RUN mkdir -p /app/logs

# 健康检查端点
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -m zephyr.l01_infrastructure.health || exit 1

EXPOSE 8000

CMD ["python", "-m", "zephyr.l01_infrastructure"]
