# [BLUEPRINT] MOD-GOV_CHECK_GEN_NO_REALTIME
# [MODULE] scripts.governance.d11_compliance.check_generator_no_realtime_time
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] .pre-commit-config.yaml (gate-generator-no-realtime-time hook)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_CHECK_GEN_NO_REALTIME | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  pre-commit hook脚本按需调用,非cron/daemon常驻服务
"""

门禁：生成器禁止使用实时时间源（datetime.now / time.time / datetime.today）。

治本：#ARCH-REGEN-NONIDEMPOTENT-001
真源：AGENTS.md §11.1.1 时间戳约定
二元判定：staged scripts/governance/d5_architecture/generators/*.py 文件中
         出现 datetime.now() / time.time() / datetime.today() 且无
         # noqa: arch-regen-nonidempotent 豁免标注（需人工评估确认无风险）
         → hard block exit 1

正典替代：from _common import idempotent_timestamp, idempotent_date
         （返回脚本最近 git commit 时间，相同 commit → 相同输出）

豁免场景（需 # noqa: arch-regen-nonidempotent 标注且经人工评估确认）：
- 日粒度时间源（datetime.now(UTC).strftime("%Y-%m-%d")），24 小时内幂等
- 已人工评估并确认无 reconciler 非收敛风险的场景

[MODULE] scripts.governance.d11_compliance.check_generator_no_realtime_time
[INVARIANTS] 只读 staged 文件；不修改工作树；fail-closed (exit 1 on violation)
[CONSUMERS] .pre-commit-config.yaml (gate-generator-no-realtime-time hook)
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 无 staged 生成器文件 → exit 0 (skip)；违规 → exit 1
[TESTS] tests/governance/d11_compliance/test_check_generator_no_realtime_time.py
[DOMAIN] D_GOVERNANCE

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: staged 生成器文件列表
#   fields: git diff --cached --name-only 过滤 scripts/governance/d5_architecture/generators/*.py
#   code: get_staged_generator_files (check_generator_no_realtime_time.py L69-83)
# - id: I2
#   name: 禁止时间源正则 FORBIDDEN_PATTERN
#   fields: datetime.now() / datetime.today() / time.time() 精确函数调用匹配
#   code: FORBIDDEN_PATTERN (check_generator_no_realtime_time.py L58)
# - id: I3
#   name: 豁免标注模式组
#   fields: # noqa: arch-regen-nonidempotent 豁免标注（需人工评估）+ 日粒度strftime("%Y-%m-%d")配 # noqa: m46-time 组合豁免标注（需人工评估）
#   code: EXEMPTION/DAILY_GRANULARITY/M46_EXEMPTION_PATTERN (check_generator_no_realtime_time.py L61-66)
# 层: 算法
# - id: A1
#   name_zh: ① staged 生成器文件枚举
#   name_en: get_staged_generator_files
#   intro: git diff --cached取暂存的生成器py文件，只读暂存区不改工作树
#   desc: subprocess跑git diff --cached --name-only -- GEN_GLOB，非0返回→空列表；滤存在的.py文件转绝对路径（L69-83）
#   inputs: I1
#   outputs: list[Path]
#   invariant: 只读staged文件；不修改工作树
# - id: A2
#   name_zh: ② 单文件违规扫描
#   name_en: check_file
#   intro: 逐行正则找禁止的实时时间源调用，跳过注释行和带豁免标注的行
#   desc: #开头行跳过；命中FORBIDDEN且无arch-regen-nonidempotent标注→记违规；日粒度+m46-time双标注豁免；违规格式rel_path:行号: 内容（L86-117）
#   inputs: I2 I3
#   outputs: 违规行列表 violations
# - id: A3
#   name_zh: ③ 门禁判定入口
#   name_en: main
#   intro: 汇总所有文件违规，有违规打印报告exit 1阻断提交，无staged生成器文件直接exit 0
#   desc: 无文件→0(skip)；有违规→打印GATE-GEN-NO-REALTIME-TIME报告+正典替代提示→1（L120-140）
#   inputs: A1 A2
#   outputs: exit code 0/1
#   invariant: fail-closed（违规exit 1）
# 层: 输出
# - id: O1
#   name_zh: 门禁退出码与违规报告
#   name_en: exit code + violations report
#   intro: 违规时打印每条违规位置与正典替代（_common.idempotent_timestamp），exit 1阻断pre-commit
#   invariant: 只读不写；无违规exit 0
#   downstream: .pre-commit-config.yaml（gate-generator-no-realtime-time hook）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A3
# I2 --> A2
# I3 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 门禁：生成器禁止使用实时时间源（datetime.now / time.time / datetime.today）。
dimensions:
- D11
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re
import subprocess
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

GEN_GLOB = "scripts/governance/d5_architecture/generators/*.py"

# 禁止的实时时间源调用（精确匹配函数调用，避免误报注释/字符串）
# datetime.now() / datetime.today() / time.time()
FORBIDDEN_PATTERN = re.compile(r"\b(datetime\.now\(\)|datetime\.today\(\)|time\.time\(\))")

# 豁免标注（行尾或同行）
EXEMPTION_PATTERN = re.compile(r"#\s*noqa:\s*arch-regen-nonidempotent")

# 额外豁免：日粒度 datetime.now(UTC).strftime("%Y-%m-%d") 模式
# 24 小时内幂等，且有 # noqa: m46-time 标注的视为已人工评估
DAILY_GRANULARITY_PATTERN = re.compile(r'datetime\.now\([^)]*\)\.strftime\(["\']%Y-%m-%d["\']\)')
M46_EXEMPTION_PATTERN = re.compile(r"#\s*noqa:\s*m46-time")


def get_staged_generator_files() -> list[Path]:
    """获取 staged 的生成器文件列表。"""
    r = subprocess.run(  # noqa: bare-subprocess  pre-commit门禁脚本读staged文件,process_pool在此场景不适用
        ["git", "diff", "--cached", "--name-only", "--", GEN_GLOB],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if r.returncode != 0:
        return []
    return [
        REPO_ROOT / f.strip()
        for f in r.stdout.splitlines()
        if f.strip().endswith(".py") and (REPO_ROOT / f.strip()).exists()
    ]


def check_file(path: Path) -> list[str]:
    """检查单个文件，返回违规行列表（格式：rel_path:line: content）。"""
    rel = path.relative_to(REPO_ROOT).as_posix()
    violations: list[str] = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return violations

    for i, line in enumerate(content.splitlines(), 1):
        # 跳过注释行（以 # 开头）和 docstring 行（含 """ 或 '''）
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue

        matches = FORBIDDEN_PATTERN.findall(line)
        if not matches:
            continue

        # 检查豁免标注
        if EXEMPTION_PATTERN.search(line):
            continue

        # 检查日粒度豁免（datetime.now(UTC).strftime("%Y-%m-%d") + # noqa: m46-time 标注经人工评估才生效）
        if DAILY_GRANULARITY_PATTERN.search(line) and M46_EXEMPTION_PATTERN.search(line):
            continue

        # 报告违规
        for m in matches:
            violations.append(f"{rel}:{i}: {m} — {line.strip()}")

    return violations


def main() -> int:
    """门禁入口：扫描 staged 生成器文件，发现违规 → exit 1。"""
    files = get_staged_generator_files()
    if not files:
        # 无 staged 生成器文件，跳过
        return 0

    all_violations: list[str] = []
    for f in files:
        all_violations.extend(check_file(f))

    if not all_violations:
        return 0

    print("GATE-GEN-NO-REALTIME-TIME: 生成器禁止使用实时时间源 (治本 #ARCH-REGEN-NONIDEMPOTENT-001)")
    print("  真源：AGENTS.md §11.1.1。请改用 _common.idempotent_timestamp() / idempotent_date()")
    print("  豁免：行尾加 # noqa: arch-regen-nonidempotent 并附人工评估理由（≥10字符）")
    print()
    for v in all_violations:
        print(f"  {v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
