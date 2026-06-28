#!/usr/bin/env python
# [A_full] module_id=CFG-check-vms-ssot | layer=config | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
#
# GATE-VMS-SSOT: VMS 单一真源门禁（三重检测：governance/vector_memory 漂移副本 + snapshot 方法重建 + faiss dead code 重建）
#
# 真源：AGENTS.md §11.2 遗留项-3 VMS SSoT 声明 + 遗留项-4 snapshot 整体删除治本
#       "integration/vector_memory/ 是 VMS 唯一真源，governance/vector_memory/ 已删除（2026-06-28）"
#       "snapshot 备份功能整体删除——R4 被 ChromaDB SQLite ACID+WAL 覆盖，30GB 递归灾难根因"
#       "faiss_collection_manager.write_with_provenance 死代码已删除（零调用方）"
#
# 原理：
#   1) governance/vector_memory/ 曾是 integration/vector_memory/ 的漂移副本，
#      两者并存导致维度方向双向漂移（integration 512d 领先 / governance 384d 落后）。
#      2026-06-28 阶段3 删除 governance 副本治本（commit 306dbb2f76 + 0137750451），
#      本门禁防止 AI 重建已删除的漂移副本。
#   2) snapshot_backup/cleanup_snapshots/_cleanup_old_snapshots 三方法已删除治本
#      （commit dddd1813，30GB 递归自复制 + 零消费方），本门禁防止 AI 重建方法名。
#      AST 检测 FunctionDef/AsyncFunctionDef 名字——无论方法体是否实现均阻断
#      （防止"保留方法名但内部空桩"或"重建为伪装方法"绕过）。
#   3) faiss_collection_manager.write_with_provenance 死代码已删除（零调用方，
#      AGENTS.md §11.2 遗留项-3），FAISS 启用时按 CollectionManager 真源签名重新实现。
#      本门禁防止 AI 在 FAISS 未启用时提前补全此死代码。
#
# 历史教训：
#   - governance/vector_memory 26 文件漂移副本与 integration/vector_memory 并存，
#     导致 SSoT 双向漂移；AI"不搜索就新生成"是副本复发的根因
#   - snapshot_backup 目标路径在源路径内 → copytree 递归自复制 → 30GB 膨胀；
#     R4 被高估（ChromaDB SQLite ACID+WAL 已应对断电）；snapshot 零消费方（只写不读）
#
# 模式：--ci 硬阻断（违规 exit 1 拒绝提交）/ --warn-only 只警告
# 触发：pre-commit（事件驱动，staged 文件检测，自动运行自动关闭）
# 消费者：.pre-commit-config.yaml gate-vms-ssot
"""GATE-VMS-SSOT: VMS 单一真源门禁——三重检测。

检测1（路径前缀）：防止 AI 重建已删除的 governance/vector_memory/ 漂移副本目录。
检测2（AST 方法名·snapshot）：防止 AI 在 VMS 真源目录重建已删除的 snapshot 方法。
检测3（AST 方法名·faiss dead code）：防止 AI 重建 faiss_collection_manager.write_with_provenance 死代码。

真源为 integration/vector_memory/（MOD-INF-011 蓝图）。

与 GATE-SRC-NO-DATA 的区别：
    - GATE-SRC-NO-DATA 禁止 src/data/（数据真源唯一 data/），真源 trae_047
    - 本脚本禁止 governance/vector_memory/ 重建 + snapshot/faiss dead code 方法重建，
      真源 AGENTS.md §11.2 遗留项-3/4

Exit codes:
    0 = PASS（无违规或无 staged 文件）
    1 = VIOLATION（检测到违规，--ci 模式）
"""

import argparse
import ast
import subprocess
import sys

# 检测1：禁止路径前缀（小写，大小写不敏感比较——Windows 文件系统大小写不敏感）
# 规则真源见 AGENTS.md §11.2 遗留项-3 VMS SSoT 声明，此处为校验执行逻辑非第二真源
FORBIDDEN_PREFIX = "src/zephyr/governance/vector_memory/"

# 检测2/3：已删除方法名清单（AST 检测，防重建）
# 方法名 → 删除原因（用于违规提示），规则真源见 AGENTS.md §11.2 遗留项-3/4
DEAD_METHOD_NAMES = {
    # 遗留项-4：snapshot 整体删除治本（30GB 递归自复制 + 零消费方 + R4 被 ChromaDB ACID+WAL 覆盖）
    "snapshot_backup": "snapshot 整体删除治本（遗留项-4，30GB 递归自复制）",
    "cleanup_snapshots": "snapshot 整体删除治本（遗留项-4）",
    "_cleanup_old_snapshots": "snapshot 整体删除治本（遗留项-4）",
    # 遗留项-3：faiss write_with_provenance 死代码删除（零调用方，FAISS 启用时按 CollectionManager 真源签名重新实现）
    "write_with_provenance": "faiss dead code 删除（遗留项-3，零调用方）",
}

# 检测2/3：AST 扫描范围——仅 VMS 真源目录的 .py 文件（治本范围限定，不误报其他模块）
DEAD_METHOD_CHECK_PREFIX = "src/zephyr/integration/vector_memory/"


def get_staged_files():
    """获取 staged 文件列表（相对路径，仅新增/修改/重命名）"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_vms_ssot(files):
    """检测1：是否有 governance/vector_memory 路径的 staged 文件（大小写不敏感）"""
    violations = []
    for f in files:
        if f.lower().startswith(FORBIDDEN_PREFIX):
            violations.append(f)
    return violations


def check_dead_method_rebuild(files):
    """检测2/3：VMS 真源目录 .py 文件是否重建已删除的方法（AST 检测）

    扫描 src/zephyr/integration/vector_memory/ 下 staged 的 .py 文件，
    用 ast.walk 检测 FunctionDef/AsyncFunctionDef 节点名字是否命中 DEAD_METHOD_NAMES。
    无论方法体是否实现，命中方法名即阻断（防空桩绕过 / 伪装重建）。

    涵盖两类已删除方法：
      - snapshot 三方法（遗留项-4，30GB 递归自复制灾难根因）
      - faiss write_with_provenance（遗留项-3，零调用方死代码）
    """
    violations = []
    for f in files:
        if not f.lower().startswith(DEAD_METHOD_CHECK_PREFIX):
            continue
        if not f.lower().endswith(".py"):
            continue
        try:
            with open(f, encoding="utf-8") as fp:
                source = fp.read()
            tree = ast.parse(source, filename=f)
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in DEAD_METHOD_NAMES:
                    violations.append((f, node.name, node.lineno, DEAD_METHOD_NAMES[node.name]))
    return violations


def main():
    parser = argparse.ArgumentParser(
        description="GATE-VMS-SSOT: VMS 单一真源门禁（governance/vector_memory 漂移副本 + snapshot/faiss dead code 方法重建 防复发）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--ci", action="store_true", help="硬阻断模式（违规 exit 1）")
    mode.add_argument("--warn-only", action="store_true", help="只警告不阻断")
    args = parser.parse_args()

    files = get_staged_files()
    if not files:
        return 0

    violations_ssot = check_vms_ssot(files)
    violations_dead_method = check_dead_method_rebuild(files)

    if not violations_ssot and not violations_dead_method:
        return 0

    print("[GATE-VMS-SSOT] 违规：VMS 单一真源 / dead code 治本约束被破坏", file=sys.stderr)

    if violations_ssot:
        print(
            f"  [检测1·漂移副本] governance/vector_memory/ 是已删除的漂移副本目录\n"
            f"    违规文件：{violations_ssot}\n"
            f"    真源：AGENTS.md §11.2 遗留项-3 VMS SSoT 声明\n"
            f"    原因：integration/vector_memory/ 是 VMS 唯一真源，"
            f"governance/vector_memory/ 已于 2026-06-28 删除\n"
            f"    历史教训：26 文件漂移副本与真源并存导致维度方向双向漂移"
            f"（commit 306dbb2f76 + 0137750451 治本）\n"
            f"    修复：删除 governance/vector_memory/ 下的文件，改用 integration/vector_memory/",
            file=sys.stderr,
        )

    if violations_dead_method:
        for f, method_name, lineno, reason in violations_dead_method:
            print(
                f"  [检测2/3·dead method 重建] VMS 真源目录下检测到已删除的方法被重建\n"
                f"    违规文件：{f}#{lineno} 方法名：{method_name}\n"
                f"    删除原因：{reason}\n"
                f"    真源：AGENTS.md §11.2 遗留项-3/4\n"
                f"    修复：删除重建的方法。",
                file=sys.stderr,
            )

    if args.ci:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
