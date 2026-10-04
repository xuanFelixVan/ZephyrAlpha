# [BLUEPRINT] MOD-GOV-REGISTER-ASSET | scripts/governance/register_asset.py | §裁定480-C2 上户口合一
# [MODULE] scripts.governance.register_asset
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（argparse/pathlib/re/subprocess/sys）；子进程依序调既有四工具（零重写）：d3_metadata/batch_creation_tokens.py、d3_metadata/add_module_translation.py、apply_depgraph.py、generate_project_depgraph.py；字段头判据真源=trae_047_engineering_file_header.yaml（动态读，fail-closed）
# [CONSUMERS] AI 会话新建资产时的一条命令上户口通道（裁定#480 C-2）；替代会话手工串接五道手续
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯编排零重写（五道手续全部委托既有工具，本件只做顺序/回显/逃生留痕）；
#   全部子进程调用 subprocess.run(list, capture_output)（禁 shell=True）；
#   任一步失败=非零退出+已办步骤回显（半程状态可见，绝不静默续跑）；
#   --skip 逃生必须留痕输出（[SKIP] step=... reason=--skip）；
#   模块头字段判据从 trae_047 真源动态读取（required 列表），禁手写第二真源
#   （裁定#480 原理性红线：说明书/判据机生禁手写第二真源）；真源读失败=fail-closed 报错
# [MODIFY-GUARD] scripts/governance/register_asset.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=五步全成（或全 skip）；exit 1=参数/判据真源读取失败；exit 2=任一子步骤失败（stderr 含失败步+已办回显）
# [TESTS] tests/governance/test_register_asset_cli.py
# [A_module] module_id=MOD-GOV-REGISTER-ASSET | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的 CLI 编排件（manual 触发，非 cron/非 daemon）
"""register_asset —— 新资产上户口合一命令（裁定#480 C-2，车道C 手术1）。

病根：新资产五道手续（creation_token / 大白话简介 / design node 登记 / 依赖图
重建 / 模块头校验）此前靠会话手工逐条串接——漏一步=CREATE-GUARD /
TRANSLATION-COVERAGE / DEPGRAPH gate 轮番阻断，重来一遍又要排大队。

处方：一条命令按序调既有四工具（零重写——本件是编排器不是新真源）::

    python scripts/governance/register_asset.py \\
        --path src/zephyr/governance/reuse_scan.py \\
        --session st-xxx-20261003 \\
        --plain "大白话：做什么/解决什么/怎么做" \\
        [--capability surgery_c] [--name-zh 中文名] [--domain D_GOVERNANCE] \\
        [--merge-eval "<裁定#375 合并评估一句话>"] [--skip token,depgraph,...]

五步依序（任一步失败=exit 2+已办步骤回显；--skip 逃生留痕）：
  ① token      batch_creation_tokens.py --prefix <path>（CREATE-GUARD 批量通道）
  ② translation add_module_translation.py --path/--domain/--name-zh/--plain-zh
                （domain 缺省从目标 .py 头 [DOMAIN] 行读；name-zh 缺省取 stem）
  ③ depgraph   apply_depgraph.py --add-design-node <path> <bp> <domain>
                （blueprint_id 缺省从头 [BLUEPRINT] 行第一段读）
  ④ generate   generate_project_depgraph.py --force（依赖图重建）
  ⑤ header     模块头字段校验（.py）——字段列表=trae_047 field_specs a_full.required
                真源动态读（15 字段含 TTL），缺字段打印整模板退出非零
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
# 注：模块头字段真源（trae_047）路径不在本文件出现——GATE-VOCAB 禁 SSoT 路径
# 硬编码；装载走 generate_project_depgraph.HEADER_FIELDS（既有唯一装载点）。

STEP_TOKEN = "token"
STEP_TRANSLATION = "translation"
STEP_DEPGRAPH = "depgraph"
STEP_GENERATE = "generate"
STEP_HEADER = "header"
STEP_ORDER: tuple[str, ...] = (STEP_TOKEN, STEP_TRANSLATION, STEP_DEPGRAPH, STEP_GENERATE, STEP_HEADER)

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_STEP_FAILED = 2


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """子进程统一入口：run_subprocess_hidden（trae_067 铁律2 CREATE_NO_WINDOW 强制）。

    Returns:
        (returncode, 合并输出)——stdout 优先，空则 stderr（供回显定位）。
    """
    from zephyr.shared.infra.process_pool import (
        run_subprocess_hidden,  # noqa: PLC0415 — 惰性装载（BARE-SUBPROCESS 统一入口）
    )

    try:
        r = run_subprocess_hidden(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(cwd or _REPO),
        )
        rc, out = r.returncode, (r.stdout or "").strip() or (r.stderr or "").strip()
    except (OSError, subprocess.SubprocessError) as exc:  # noqa: BLE001 — 子进程起不来=步骤失败非崩溃
        return 1, f"subprocess error: {type(exc).__name__}: {exc}"
    return rc, out


def header_required_fields() -> list[str]:
    """模块头字段判据真源读取（trae_047 field_specs a_full.required）。

    真源装载点唯一：复用 generate_project_depgraph.HEADER_FIELDS（同目录既有
    装载器，fail-closed 在其侧）——本文件禁再写 SSoT 路径（GATE-VOCAB：
    VOCAB-CHAIN 新增 .py 禁硬编码 SSoT 路径，应经既有装载点发现）。
    """
    import sys as _sys

    gov_dir = str(Path(__file__).resolve().parent)
    if gov_dir not in _sys.path:
        _sys.path.insert(0, gov_dir)
    try:
        from generate_project_depgraph import HEADER_FIELDS  # noqa: PLC0415 — 既有真源装载点

        return [str(f) for f in HEADER_FIELDS]
    except Exception as exc:  # noqa: BLE001 — 结构缺失/文件不可达都走 fail-closed
        raise RuntimeError(
            "模块头字段规范真源装载失败（经 generate_project_depgraph.HEADER_FIELDS）: "
            f"{exc}. 禁回退硬编码清单（判据禁手写第二真源）——先修真源装载点"
        ) from exc


def parse_header_tags(text: str) -> dict[str, str]:
    """解析文件头 ``# [TAG] rest`` 标签行（仅头部注释区，遇 docstring/代码即止）。"""
    tags: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^#\s*\[([A-Za-z_-]+)\]\s*(.*)$", line)
        if m:
            tags[m.group(1)] = m.group(2).strip()
    return tags


def check_module_header(path: Path) -> tuple[list[str], list[str]]:
    """⑤ 模块头校验：对照真源 required 字段清单查缺失。

    Returns:
        (缺失字段清单, 全字段模板行)——缺失为空=通过；模板按真源字段动态生成
        （说明书机生，禁手写字段表）。
    """
    fields = header_required_fields()
    template = [f"# [{f}] <...>" for f in fields]
    if path.suffix != ".py":
        return [], template  # 非 .py 无 14 字段头契约，直接通过（模板备用）
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    tags = parse_header_tags(text)
    return [f for f in fields if f not in tags], template


def _step_token(path: str, session: str, capability: str, merge_eval: str) -> tuple[int, str]:
    cmd = [
        sys.executable,
        "scripts/governance/d3_metadata/batch_creation_tokens.py",
        "--prefix",
        path,
        "--created-by",
        session,
        "--capability",
        capability,
    ]
    if merge_eval:
        cmd += ["--merge-evaluation", merge_eval]
    return _run(cmd)


def _step_translation(path: str, domain: str, name_zh: str, plain: str) -> tuple[int, str]:
    cmd = [
        sys.executable,
        "scripts/governance/d3_metadata/add_module_translation.py",
        "--path",
        path,
        "--domain",
        domain,
        "--name-zh",
        name_zh,
        "--plain-zh",
        plain,
    ]
    return _run(cmd)


def _step_depgraph(path: str, blueprint_id: str, domain: str) -> tuple[int, str]:
    # 粒度判定：带扩展名的单文件=--granularity file；目录=directory 且补尾斜杠
    # （apply_depgraph 缺省 directory 要求路径以 / 结尾，单文件不带该旗必被拒）
    if Path(path).suffix:
        granularity, norm_path = "file", path
    else:
        granularity, norm_path = "directory", path if path.endswith("/") else path + "/"
    return _run(
        [
            sys.executable,
            "scripts/governance/apply_depgraph.py",
            "--granularity",
            granularity,
            "--add-design-node",
            norm_path,
            blueprint_id,
            domain,
        ]
    )


def _step_generate() -> tuple[int, str]:
    return _run([sys.executable, "scripts/governance/generate_project_depgraph.py", "--force"])


def _step_header(path: Path) -> tuple[int, str]:
    missing, template = check_module_header(path)
    if not missing:
        return EXIT_OK, f"header OK（{len(header_required_fields())} 字段齐）"
    lines = [f"模块头缺 {len(missing)} 字段: {', '.join(missing)}"]
    lines.append("模板（按 trae_047 真源机生，逐行补齐后重跑）:")
    lines.extend(template)
    return EXIT_STEP_FAILED, "\n".join(lines)


def register_asset(
    path: str,
    session: str,
    plain: str,
    *,
    capability: str = "governance",
    name_zh: str = "",
    domain: str = "",
    merge_eval: str = "",
    skips: tuple[str, ...] = (),
) -> int:
    """主流程：五步依序编排，任一步失败=回显已办步骤+exit 2。"""
    target = Path(path)
    done: list[str] = []
    header_text = target.read_text(encoding="utf-8", errors="replace") if target.exists() else ""
    tags = parse_header_tags(header_text)
    eff_domain = domain or tags.get("DOMAIN", "")
    eff_name_zh = name_zh or target.stem
    bp_match = re.match(r"^([A-Za-z0-9_-]+)", tags.get("BLUEPRINT", ""))
    eff_blueprint = bp_match.group(1) if bp_match else ""

    print(f"register_asset: path={path} session={session} skips={list(skips) or '无'}")

    for step in STEP_ORDER:
        if step in skips:
            print(f"[SKIP] step={step} reason=--skip（逃生留痕）")
            continue
        if step == STEP_TOKEN:
            rc, out = _step_token(path, session, capability, merge_eval)
        elif step == STEP_TRANSLATION:
            if not eff_domain:
                print("FAIL step=translation: 无 domain（--domain 缺省且头 [DOMAIN] 行缺失/文件不存在）")
                print(f"已办步骤: {done or '无'}")
                return EXIT_STEP_FAILED
            rc, out = _step_translation(path, eff_domain, eff_name_zh, plain)
        elif step == STEP_DEPGRAPH:
            if not (eff_blueprint and eff_domain):
                print(
                    f"FAIL step=depgraph: blueprint_id/domain 不齐"
                    f"（blueprint={eff_blueprint!r}, domain={eff_domain!r}；从头 [BLUEPRINT]/[DOMAIN] 读或显式传参）"
                )
                print(f"已办步骤: {done or '无'}")
                return EXIT_STEP_FAILED
            rc, out = _step_depgraph(path, eff_blueprint, eff_domain)
        elif step == STEP_GENERATE:
            rc, out = _step_generate()
        else:
            rc, out = _step_header(target)
        mark = "OK" if rc == EXIT_OK else "FAIL"
        print(f"[{mark}] step={step} rc={rc}")
        if out:
            for ln in out.splitlines()[:12]:
                print(f"    {ln}")
        if rc != EXIT_OK:
            print(f"已办步骤: {done or '无'}（step={step} 失败中止，后续步骤未跑）")
            return EXIT_STEP_FAILED
        done.append(step)

    print(f"OK: 五道手续完成（已办: {', '.join(done) or '全 skip'}）")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(
        prog="register_asset.py",
        description="新资产上户口合一命令（裁定#480 C-2）：一条命令依序办五道手续"
        "——token/大白话/design node/依赖图重建/模块头校验，全部委托既有工具（零重写）。",
    )
    ap.add_argument("--path", required=True, help="新资产路径（相对仓库根）")
    ap.add_argument("--session", required=True, help="登记会话名（created_by）")
    ap.add_argument("--plain", required=True, help="大白话简介（做什么/解决什么/怎么做，CJK≥8）")
    ap.add_argument("--capability", default="governance", help="token 能力名前缀（缺省 governance）")
    ap.add_argument("--name-zh", default="", help="模块中文名（缺省取文件 stem）")
    ap.add_argument("--domain", default="", help="域 ID（缺省从目标 .py 头 [DOMAIN] 行读）")
    ap.add_argument("--merge-eval", default="", help="裁定#375 合并评估一句话（写入 token merge_evaluation）")
    ap.add_argument(
        "--skip",
        default="",
        help="逃生口：逗号分隔步骤名（token,translation,depgraph,generate,header）——跳过留痕输出",
    )
    args = ap.parse_args(argv)

    skips = tuple(s.strip() for s in args.skip.split(",") if s.strip())
    bad = [s for s in skips if s not in STEP_ORDER]
    if bad:
        print(f"FAIL: --skip 未知步骤名 {bad}（合法: {','.join(STEP_ORDER)}）", file=sys.stderr)
        return EXIT_USAGE
    if not args.plain.strip():
        print("FAIL: --plain 为空（大白话是必填手续）", file=sys.stderr)
        return EXIT_USAGE

    return register_asset(
        args.path,
        args.session,
        args.plain,
        capability=args.capability,
        name_zh=args.name_zh,
        domain=args.domain,
        merge_eval=args.merge_eval,
        skips=skips,
    )


if __name__ == "__main__":
    sys.exit(main())
