#!/usr/bin/env python
"""
download_models.py — ARCH-MODEL-LIFECYCLE-001 Phase 3
=====================================================
模型文件下载脚本——从 HuggingFace 下载嵌入模型到 data/models/local_model/

治本背景 (ARCH-MODEL-LIFECYCLE-001):
  Phase 1: git filter-repo 从历史中移除大模型文件（bge-m3 2.2GB）
  Phase 2: .gitignore 排除 data/models/，.gitattributes 移除死 LFS 规则
  Phase 3: 本脚本提供模型获取途径（永不入库，按需下载）

模型来源 (SSoT: config/embedding_model_registry.yaml):
  - BAAI/bge-m3                          → data/models/local_model/bge-m3/                          (2.2GB, HOT collections)
  - BAAI/bge-small-zh-v1.5               → data/models/local_model/bge-small-zh-v1.5/               (92MB,  轻量中文)
  - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
                                          → data/models/local_model/paraphrase-multilingual-MiniLM-L12-v2/ (465MB, DEFAULT)

用法:
  python scripts/ops/download_models.py              # 下载所有缺失模型
  python scripts/ops/download_models.py --force       # 强制重新下载所有模型
  python scripts/ops/download_models.py --model bge-m3 # 只下载指定模型
  python scripts/ops/download_models.py --list        # 列出模型状态
  python scripts/ops/download_models.py --verify      # 验证已下载模型完整性
  python scripts/ops/download_models.py --dry-run     # 预览将下载什么（不实际下载）

依赖:
  huggingface_hub (sentence-transformers>=3.0.0 的传递依赖，已在 requirements.txt)
  如缺失: pip install huggingface_hub
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Model Registry — MUST stay in sync with config/embedding_model_registry.yaml
# Only models with `local_path` in the YAML need downloading here.
# Models without local_path (all-MiniLM-L6-v2, text2vec-base-chinese) are
# auto-downloaded by sentence-transformers on first use — no manual action needed.
# ---------------------------------------------------------------------------
MODELS: list[dict] = [
    {
        "name": "bge-m3",
        "hf_repo_id": "BAAI/bge-m3",
        "local_path": "data/models/local_model/bge-m3",
        "size_mb": 2182,
        "description": "BGE M3 multilingual (dense/sparse/colbert), HOT collections",
        "required_files": ["model.safetensors", "config.json", "tokenizer.json"],
    },
    {
        "name": "bge-small-zh-v1.5",
        "hf_repo_id": "BAAI/bge-small-zh-v1.5",
        "local_path": "data/models/local_model/bge-small-zh-v1.5",
        "size_mb": 92,
        "description": "BGE small Chinese model, lightweight retrieval",
        "required_files": ["model.safetensors", "config.json", "tokenizer.json"],
    },
    {
        "name": "paraphrase-multilingual-MiniLM-L12-v2",
        "hf_repo_id": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "local_path": "data/models/local_model/paraphrase-multilingual-MiniLM-L12-v2",
        "size_mb": 465,
        "description": "Multilingual 50+ language model, COLD collections (DEFAULT)",
        "required_files": ["model.safetensors", "config.json", "tokenizer.json"],
    },
]

# Repo root = 3 levels up from scripts/ops/download_models.py
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _model_local_path(model: dict) -> Path:
    """Get absolute Path for a model's local directory."""
    return REPO_ROOT / model["local_path"]


def is_model_downloaded(model: dict) -> bool:
    """Check if model is already downloaded (all required files present)."""
    local_path = _model_local_path(model)
    if not local_path.is_dir():
        return False
    return all((local_path / f).is_file() for f in model["required_files"])


def get_model_size_mb(model: dict) -> float:
    """Get actual size of downloaded model directory in MB (0 if not present)."""
    local_path = _model_local_path(model)
    if not local_path.is_dir():
        return 0.0
    total = sum(f.stat().st_size for f in local_path.rglob("*") if f.is_file())
    return total / (1024 * 1024)


def check_disk_space(required_mb: float) -> bool:
    """Check if sufficient disk space is available at REPO_ROOT."""
    usage = shutil.disk_usage(REPO_ROOT)
    free_mb = usage.free / (1024 * 1024)
    if free_mb < required_mb:
        print(f"  ✗ Insufficient disk space: {free_mb:.0f} MB free, ~{required_mb:.0f} MB required")
        return False
    return True


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def download_model(model: dict, force: bool = False) -> bool:
    """Download a single model from HuggingFace Hub.

    Returns True if model is available after this call (downloaded or already present).
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("  ✗ huggingface_hub not installed.")
        print("    Install with: pip install huggingface_hub")
        print("    (Or: pip install -r requirements.txt — it's a transitive dep of sentence-transformers)")
        return False

    local_path = _model_local_path(model)

    # Skip if already downloaded and not forced
