#!/usr/bin/env python
# [BLUEPRINT] MOD-INF-045 | docs/03_modules/_domain_infrastructure_operations/model_downloader/blueprint.md | §
# [MODULE] scripts.ops.download_models
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] config/embedding_model_registry.yaml; huggingface_hub; PyYAML
# [CONSUMERS] manual; CI setup; onboarding
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 模型文件永不入库(.gitignore排除); MODELS从embedding_model_registry.yaml动态加载(SSoT,零硬编码)
# [MODIFY-GUARD] ARCH-MODEL-LIFECYCLE-001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAML缺失→exit 2; huggingface_hub未安装→exit 1; 下载失败→exit 1
# [TESTS] manual: --list/--verify/--dry-run
# [A_module] module_id=MOD-INF-045 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-MODEL-LIFECYCLE-001
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

真源说明 (P2 治本 2026-08-03):
  模型清单（name/hf_repo_id/local_path/file_size_mb/required_files）的唯一真源是
  config/embedding_model_registry.yaml。本脚本启动时从该 YAML 动态加载，零硬编码——
  新增/移除模型只需改 YAML，无需同步脚本，消除多真源漂移风险。
  仅 local_path + hf_repo_id 均存在的模型需要手动下载；其余（all-MiniLM-L6-v2、
  text2vec-base-chinese）由 sentence-transformers 首次使用时自动下载。

用法:
  python scripts/ops/download_models.py              # 下载所有缺失模型
  python scripts/ops/download_models.py --force       # 强制重新下载所有模型
  python scripts/ops/download_models.py --model bge-m3 # 只下载指定模型
  python scripts/ops/download_models.py --list        # 列出模型状态
  python scripts/ops/download_models.py --verify      # 验证已下载模型完整性
  python scripts/ops/download_models.py --dry-run     # 预览将下载什么（不实际下载）

依赖:
  huggingface_hub (sentence-transformers>=3.0.0 的传递依赖，已在 requirements.txt)
  PyYAML (项目通用依赖)
  如缺失: pip install huggingface_hub pyyaml
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover — PyYAML 是项目通用依赖
    yaml = None

# Repo root = 3 levels up from scripts/ops/download_models.py
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# SSoT: 模型注册表 YAML（唯一真源，禁止在本脚本硬编码模型清单）
REGISTRY_PATH = REPO_ROOT / "config" / "embedding_model_registry.yaml"

# 下载验证默认必需文件（YAML 未声明 required_files 时兜底）
DEFAULT_REQUIRED_FILES = ["model.safetensors", "config.json", "tokenizer.json"]


# ---------------------------------------------------------------------------
# Model Registry Loader — 从 YAML 动态加载（SSoT，消除多真源）
# ---------------------------------------------------------------------------


def _load_models_from_registry() -> list[dict]:
    """从 config/embedding_model_registry.yaml 加载需手动下载的模型清单。

    仅返回 local_path AND hf_repo_id 均存在的模型——这些需要通过本脚本下载。
    无 local_path 的模型（all-MiniLM-L6-v2、text2vec-base-chinese）由
    sentence-transformers 首次使用时自动下载，不在此处理。
    """
    if yaml is None:
        print(f"ERROR: PyYAML not installed — cannot load {REGISTRY_PATH}")
        print("  Install with: pip install pyyaml")
        sys.exit(2)

    if not REGISTRY_PATH.is_file():
        print(f"ERROR: Model registry not found: {REGISTRY_PATH}")
        print("  This file is the SSoT for model download info. Cannot proceed.")
        sys.exit(2)

    with open(REGISTRY_PATH, encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    models: list[dict] = []
    for entry in registry.get("models", []):
        local_path = entry.get("local_path")
        hf_repo_id = entry.get("hf_repo_id")
        if not local_path or not hf_repo_id:
            continue  # 自动下载模型，跳过
        models.append(
            {
                "name": entry["name"],
                "hf_repo_id": hf_repo_id,
                "local_path": local_path,
                "size_mb": entry.get("file_size_mb") or 0,
                "description": entry.get("description", ""),
                "required_files": entry.get("required_files", DEFAULT_REQUIRED_FILES),
            }
        )
    return models


# 启动时从 SSoT YAML 加载（零硬编码）
MODELS: list[dict] = _load_models_from_registry()


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
    if is_model_downloaded(model) and not force:
        size = get_model_size_mb(model)
        print(f"  ✓ Already downloaded ({size:.1f} MB) — use --force to re-download")
        return True

    # Clean existing directory if force-download
    if force and local_path.exists():
        print(f"  Removing existing {local_path} ...")
        shutil.rmtree(local_path)

    print(f"  Source:   {model['hf_repo_id']}")
    print(f"  Target:   {local_path}")
    print(f"  Expected: ~{model['size_mb']} MB")

    try:
        snapshot_download(
            repo_id=model["hf_repo_id"],
            local_dir=str(local_path),
        )
    except Exception as exc:  # noqa: BLE001
        print(f"  ✗ Download failed: {exc}")
        print("    Troubleshooting:")
        print("    - Check network connectivity")
        print("    - If behind proxy: set HTTPS_PROXY env var")
        print("    - If private model: set HF_TOKEN env var")
        return False

    # Verify after download
    if not is_model_downloaded(model):
        missing = [f for f in model["required_files"] if not (local_path / f).is_file()]
        print(f"  ✗ Download incomplete — missing files: {missing}")
        return False

    actual_size = get_model_size_mb(model)
    print(f"  ✓ Downloaded successfully ({actual_size:.1f} MB)")
    return True


def verify_model(model: dict) -> bool:
    """Verify a model's integrity (required files present, size reasonable)."""
    local_path = _model_local_path(model)

    if not local_path.is_dir():
        print(f"  ✗ NOT DOWNLOADED — run: python scripts/ops/download_models.py --model {model['name']}")
        return False

    missing = [f for f in model["required_files"] if not (local_path / f).is_file()]
    if missing:
        print(f"  ✗ MISSING files: {missing} — re-download with --force")
        return False

    actual_mb = get_model_size_mb(model)
    expected_mb = model["size_mb"]
    # Warn if size is less than 50% of expected (possible truncated download)
    if actual_mb < expected_mb * 0.5:
        print(f"  ⚠ Size mismatch: expected ~{expected_mb} MB, got {actual_mb:.1f} MB — re-download with --force")
        return False

    print(f"  ✓ OK ({actual_mb:.1f} MB)")
    return True


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------


def cmd_list() -> None:
    """List all models and their download status."""
    print("=" * 78)
    print("Embedding Model Registry — config/embedding_model_registry.yaml")
    print("=" * 78)
    for m in MODELS:
        downloaded = is_model_downloaded(m)
        status = "✓ DOWNLOADED" if downloaded else "✗ MISSING"
        size = f"{get_model_size_mb(m):.1f} MB" if downloaded else f"~{m['size_mb']} MB (not downloaded)"
        print(f"\n  {m['name']}")
        print(f"    Status:    {status}")
        print(f"    Size:      {size}")
        print(f"    Desc:      {m['description']}")
        print(f"    HF Source: {m['hf_repo_id']}")
        print(f"    Local:     {m['local_path']}")
    print()


def cmd_verify(models: list[dict]) -> int:
    """Verify downloaded models."""
    print("=" * 78)
    print("Model Verification")
    print("=" * 78)
    all_ok = True
    for m in models:
        print(f"\n  {m['name']}:")
        if not verify_model(m):
            all_ok = False
    print()
    if all_ok:
        print("✓ All models verified successfully.")
        return 0
    print("✗ Some models failed verification. Run download to fix.")
    return 1


def cmd_download(models: list[dict], force: bool, dry_run: bool) -> int:
    """Download models."""
    print("=" * 78)
    print("Model Download — ARCH-MODEL-LIFECYCLE-001 Phase 3")
    print("=" * 78)

    # Determine which models need downloading
    to_download = []
    for m in models:
        if force or not is_model_downloaded(m):
            to_download.append(m)

    if not to_download:
        print("\n  All requested models are already downloaded. Use --force to re-download.")
        return 0

    total_mb = sum(m["size_mb"] for m in to_download)
    print(f"\n  Models to download: {len(to_download)}")
    print(f"  Estimated total:    ~{total_mb} MB ({total_mb / 1024:.1f} GB)")
    for m in to_download:
        print(f"    • {m['name']:50s} ~{m['size_mb']} MB")

    if dry_run:
        print("\n  DRY RUN — no files will be downloaded.\n")
        return 0

    # Disk space check
    print()
    if not check_disk_space(total_mb):
        return 1

    # Download each model
    print()
    success = 0
    for i, m in enumerate(to_download, 1):
        print(f"\n[{i}/{len(to_download)}] {m['name']}")
        if download_model(m, force=force):
            success += 1

    # Summary
    print("\n" + "=" * 78)
    print(f"Download complete: {success}/{len(to_download)} models successful")

    if success < len(to_download):
        print("✗ Some models failed. Check errors above.")
        return 1

    # Verify all
    print("\nVerifying downloads ...")
    all_ok = True
    for m in to_download:
        print(f"  {m['name']}:", end=" ")
        if not verify_model(m):
            all_ok = False

    if all_ok:
        print("\n✓ All models verified. Ready for use.")
        return 0
    print("\n✗ Some models failed verification. Try --force to re-download.")
    return 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download embedding models from HuggingFace (ARCH-MODEL-LIFECYCLE-001 Phase 3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Models are stored in data/models/local_model/ (git-ignored, never committed).\n"
            "Registry SSoT: config/embedding_model_registry.yaml\n"
            "\n"
            "Examples:\n"
            "  python scripts/ops/download_models.py              # Download all missing\n"
            "  python scripts/ops/download_models.py --model bge-m3\n"
            "  python scripts/ops/download_models.py --list\n"
            "  python scripts/ops/download_models.py --verify\n"
        ),
    )
    parser.add_argument("--force", action="store_true", help="Force re-download even if already present")
    parser.add_argument("--model", type=str, metavar="NAME", help="Download/verify specific model by name")
    parser.add_argument("--list", action="store_true", help="List all models and their download status")
    parser.add_argument("--verify", action="store_true", help="Verify downloaded model integrity")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be downloaded without downloading")
    args = parser.parse_args()

    # Filter models if --model specified
    models = MODELS
    if args.model:
        models = [m for m in MODELS if m["name"] == args.model]
        if not models:
            available = ", ".join(m["name"] for m in MODELS)
            print(f"ERROR: Unknown model '{args.model}'. Available: {available}")
            sys.exit(2)

    if args.list:
        cmd_list()
        return

    if args.verify:
        sys.exit(cmd_verify(models))

    sys.exit(cmd_download(models, force=args.force, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
