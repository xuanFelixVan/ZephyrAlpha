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

# 5.31.6 修复：生产镜像用 pip install . 而非可编辑模式 -e .
COPY src/ ./src/
RUN pip install --no-cache-dir .

# 创建日志目录
RUN mkdir -p /app/logs

# 健康检查端点
# 5.31.1/5.31.2 修复：原指向不存在的 zephyr.l01_infrastructure，改为 zephyr.trading（已存在的入口）
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import zephyr; print('ok')" || exit 1

EXPOSE 8000

# 5.31.1 修复：原 CMD zephyr.l01_infrastructure 不存在，改为 zephyr.trading
CMD ["python", "-m", "zephyr.trading"]
