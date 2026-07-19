# ZephyrAlpha 2.0 — 核心应用容器镜像
# Phase B: 开发/测试环境
# 5.31.5 修复：多阶段构建——gcc 只在 builder 阶段，最终镜像不含编译工具链

# ── Stage 1: builder（gcc 仅存在于本阶段，不进入最终镜像）──
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装编译工具链（编译含 C 扩展的依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖声明（README.md/LICENSE 是 pyproject.toml readme/license 元数据引用的文件，
# pip install . 构建元数据时必须存在）
COPY pyproject.toml README.md LICENSE requirements.txt requirements-dev.txt ./

# 生产依赖 → /install（会被复制到 runtime 阶段）
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
# 5.30 治本：开发依赖装到独立前缀 /install-dev，仅供 builder 阶段使用
# （如 docker build --target builder 跑测试），不复制进 runtime 镜像——
# 修复 ruff/mypy/pytest/pre-commit 等 dev 工具链进入生产镜像的问题
RUN pip install --no-cache-dir --prefix=/install-dev -r requirements-dev.txt

# 5.31.6 修复：生产镜像用 pip install . 而非可编辑模式 -e .
COPY src/ ./src/
RUN pip install --no-cache-dir --prefix=/install .

# ── Stage 2: runtime（无 gcc，仅运行产物）──
FROM python:3.12-slim

WORKDIR /app

# 从 builder 复制安装产物（site-packages + console scripts）
COPY --from=builder /install /usr/local

# 创建日志目录
RUN mkdir -p /app/logs

# 健康检查端点
# 5.31.1/5.31.2 修复：原指向不存在的 zephyr.l01_infrastructure，改为 zephyr.trading（已存在的入口）
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import zephyr; print('ok')" || exit 1

EXPOSE 8000

# 5.31.1 修复：原 CMD zephyr.l01_infrastructure 不存在，改为 zephyr.trading
CMD ["python", "-m", "zephyr.trading"]
