#!/usr/bin/env bash
# contract_fingerprint_hook.sh — pre_commit hook: 契约文件变更时自动更新 ocp-manifest.json
#
# L2 修复：消除"改契约文件但忘更新 manifest"的漂移根因。
# 当 src/zephyr/shared/contracts/*.py 或 cross_layer_contracts.yaml 变更时，
# 自动调用 build_ocp_manifest.py 重新生成指纹，并 git add 到当前 commit。
#
# 安装方式：
#   1. 在 .git/hooks/pre_commit 中添加：
#      bash scripts/hooks/contract_fingerprint_hook.sh
#   2. 或运行 scripts/hooks/git_secrets_setup.sh 时自动集成

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTRACT_DIR="src/zephyr/shared/contracts"
CONTRACTS_YAML="architecture_model/contracts/cross_layer_contracts.yaml"
BUILD_SCRIPT="scripts/arch_guard/_tools/build_ocp_manifest.py"
MANIFEST_PATH="src/zephyr/shared/contracts/_frozen_signatures/ocp-manifest.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[CONTRACT-HOOK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[CONTRACT-HOOK]${NC} $*"; }
error() { echo -e "${RED}[CONTRACT-HOOK]${NC} $*"; }

contract_files_changed() {
    git diff --cached --name-only --diff-filter=ACMR 2>/dev/null | grep -E \
        "^${CONTRACT_DIR}/.*\.py$|^${CONTRACTS_YAML}$" || true
}

if [ -z "$(contract_files_changed)" ]; then
    exit 0
fi

info "检测到契约文件变更，重新生成 ocp-manifest.json ..."

CHANGED="$(contract_files_changed | tr '\n' ' ')"
info "变更文件: ${CHANGED}"

if [ ! -f "${REPO_ROOT}/${BUILD_SCRIPT}" ]; then
    error "${BUILD_SCRIPT} 不存在 — 跳过指纹更新"
    exit 0
fi

python "${REPO_ROOT}/${BUILD_SCRIPT}"
if [ $? -ne 0 ]; then
    error "build_ocp_manifest.py 执行失败 — 请手动修复后再提交"
    exit 1
fi

if [ -f "${REPO_ROOT}/${MANIFEST_PATH}" ]; then
    git add "${MANIFEST_PATH}"
    info "已暂存 ${MANIFEST_PATH}"
fi

info "契约指纹已更新并暂存"
exit 0
