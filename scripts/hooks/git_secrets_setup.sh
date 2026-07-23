#!/usr/bin/env bash
# git_secrets_setup.sh — 部署 git-secrets pre_commit hook
#
# 对标 06-security_architecture.md §6.3 Secret 三道防线 L2-Pre-commit
#      architecture_principles.md §2bis R1 门禁
#
# 功能：
#   1. 检查 git-secrets 是否已安装
#   2. 在当前仓库安装 git-secrets hook
#   3. 添加 ZEPHYR_SECRET_* 自定义 pattern
#   4. 验证 hook 已正确安装
#
# 用法: bash scripts/hooks/git_secrets_setup.sh [--check]
#   --check: 仅检查安装状态，不执行安装

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHECK_MODE=false

if [[ "${1:-}" == "--check" ]]; then
    CHECK_MODE=true
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

check_git_secrets_installed() {
    if command -v git-secrets &>/dev/null; then
        return 0
    fi
    return 1
}

check_hook_installed() {
    local hook_file="$REPO_ROOT/.git/hooks/pre_commit"
    if [[ -f "$hook_file" ]] && grep -q "git-secrets" "$hook_file" 2>/dev/null; then
        return 0
    fi
    return 1
}

check_patterns_registered() {
    local patterns
    patterns=$(cd "$REPO_ROOT" && git secrets --list 2>/dev/null || true)
    if echo "$patterns" | grep -q "ZEPHYR_SECRET"; then
        return 0
    fi
    return 1
}

do_check() {
    local rc=0

    echo "=== git-secrets 安装状态检查 ==="
    echo ""

    if check_git_secrets_installed; then
        info "git-secrets 已安装: $(command -v git-secrets)"
    else
        error "git-secrets 未安装"
        echo "  安装方式: brew install git-secrets (macOS) 或 pip install git-secrets"
        rc=1
    fi

    if check_hook_installed; then
        info "pre_commit hook 已安装"
    else
        error "pre_commit hook 未安装"
        rc=1
    fi

    if check_patterns_registered; then
        info "ZEPHYR_SECRET_* pattern 已注册"
    else
        error "ZEPHYR_SECRET_* pattern 未注册"
        rc=1
    fi

    echo ""
    if [[ $rc -eq 0 ]]; then
        info "所有检查通过"
    else
        error "部分检查未通过 — 运行此脚本（不带 --check）执行安装"
    fi

    return $rc
}

do_install() {
    echo "=== git-secrets 安装与配置 ==="
    echo ""

    if ! check_git_secrets_installed; then
        error "git-secrets 未安装，请先安装："
        echo "  macOS:  brew install git-secrets"
        echo "  Linux:  pip install git-secrets"
        echo "  Manual: git clone https://github.com/awslabs/git-secrets && cd git-secrets && make install"
        return 1
    fi
    info "git-secrets 已安装"

    cd "$REPO_ROOT"

    git secrets --install 2>/dev/null || true
    info "git-secrets hook 已安装到 .git/hooks/"

    git secrets --register-aws 2>/dev/null || true
    info "AWS pattern 已注册"

    git secrets --add 'ZEPHYR_SECRET_[A-Z_]+\s*[:=]\s*["\x27][^"\x27]{4,}["\x27]'
    git secrets --add 'ZEPHYR_API_KEY\s*[:=]\s*["\x27][^"\x27]{8,}["\x27]'
    git secrets --add 'ZEPHYR_TOKEN\s*[:=]\s*["\x27][^"\x27]{8,}["\x27]'
    git secrets --add 'ZEPHYR_PRIVATE_KEY\s*[:=]\s*["\x27][^"\x27]{16,}["\x27]'
    info "ZEPHYR_SECRET_* 自定义 pattern 已注册"

    echo ""
    echo "--- 验证 ---"
    if check_hook_installed && check_patterns_registered; then
        info "安装验证通过"
        echo ""
        echo "已注册 pattern 列表:"
        git secrets --list
        return 0
    else
        error "安装验证失败"
        return 1
    fi
}

if $CHECK_MODE; then
    do_check
else
    do_install
fi
