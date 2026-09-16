# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] scripts.ops.ollama_version_guard
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] 仅标准库（stdlib-only）；运行时经 subprocess 调 `ollama --version` 与安装器
# [CONSUMERS] 运维/boot 探活（--check 幂等自判）、Owner 一条命令升级（--upgrade）、lane J 移交③
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 默认零副作用（--check 只读判定，永不安装）；--upgrade 必须先过 SHA-256 完整性校验再落装，校验失败=中止且不装；已合规时 --upgrade 幂等 no-op（除非 --force）；升级后复检版本，非合规则回退到快照的前一版安装器
# [MODIFY-GUARD] 软件安装=Owner 门位（本脚本不自装，Owner 执行一条命令）
# [STABILITY] evolving
# [SAFETY] M
# noqa: m11-perm-manual-legitimate  M11豁免: 本工具为 Owner/CI 按需 CLI，非常驻服务非 cron；默认 --check 只读
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 版本不可解析/未安装 → 专用退出码；完整性校验失败 → 中止退出码非零且不落装
# [TESTS] python -m pytest tests/ops/test_ollama_version_guard.py -q
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Ollama 版本治本守卫（#移交③，2026-09-16，lane J）。

背景（真源）：docs/_working/forensics/llama_server_crash_forensics_202609.md（治理战役 M4）
—— Ollama 0.32.1 内嵌 llama-server.exe 的 `libllama.dll +0x2a230` 访问违例（AV）为
确定性构建缺陷（8 例崩溃收敛 3 签名族，AV 四例同模块同偏移=野指针/越界固有路径，非随机
内存翻转）。VRAM 超订只是放大器；8/27 两例 AV 早于超订事故日，说明缺陷固有——
「版本升级建议独立于超订治理成立」（报告 §4.5）。已落防护：ensure_running VRAM 预算门 +
M1 孵化登记 + M2 水位门禁 + M3 超寿收割（断循环放大），但根因修复=升级到 >0.32.1 的 stable。

原待办「Ollama 升级=Owner 门位」的"必须人工"根因由本脚本消除：
  - 自带版本判定与幂等：`--check`（默认，零副作用）读当前安装版本、与崩溃构建天花板比较，
    CI/boot 探活可直接常挂；本仓现装 0.34.1 已 > 0.32.1 → 待办的即时阻断已在环境层解除。
  - 一条命令自动化：Owner 执行 `python scripts/ops/ollama_version_guard.py --upgrade
    --installer-path <下载的安装器> --expected-sha256 <官方发布页校验和>` 即完成
    版本判定→完整性校验→落装→复检→失败回退，无需人工多步。
  - 完整性校验=锚定 Operator 提供的官方 SHA-256（不信任下载物自带哈希，防 MITM）；校验不
    通过则中止且不落装。软件安装本身仍是 Owner 门位（本脚本不静默自装，需显式 --upgrade +
    校验和），但"判断要不要升/怎么升/升坏了怎么退"的人工认知负担被脚本吸收。

用法：
  python scripts/ops/ollama_version_guard.py --check                # 只读自判（幂等，CI 可挂）
  python scripts/ops/ollama_version_guard.py --check --json         # 机器可读
  python scripts/ops/ollama_version_guard.py --upgrade --dry-run \
      --installer-path OllamaSetup.exe --expected-sha256 <hex>      # 预演升级流程
  python scripts/ops/ollama_version_guard.py --upgrade \
      --installer-path OllamaSetup.exe --expected-sha256 <hex>      # Owner 一条命令真升级
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

# 崩溃构建天花板（含）：<= 此版本的 llama.cpp 构建含 AV@0x2a230 确定性缺陷，判非合规。
# 真源=llama_server_crash_forensics_202609.md §2/§4（0.32.1）。
CRASH_BEARING_CEILING: tuple[int, ...] = (0, 32, 1)

_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")

# 退出码约定（与 governance _shared 对齐语义，但本脚本 stdlib-only 自持）
EXIT_PASS = 0
EXIT_NOT_COMPLIANT = 3
EXIT_NOT_INSTALLED = 4
EXIT_ERROR = 2


def parse_version(text: str) -> tuple[int, ...] | None:
    """从任意含语义化版本号的文本中解析出 (major, minor, patch)。

    兼容 `0.34.1`、`ollama version is 0.32.1`、`client version is 0.34.1` 等形态。
    解析失败返回 None（不抛）。
    """
    if not text:
        return None
    m = _VERSION_RE.search(text)
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def is_compliant(version: tuple[int, ...] | None, ceiling: tuple[int, ...] = CRASH_BEARING_CEILING) -> bool:
    """版本严格大于崩溃构建天花板才合规；None（未装/不可解析）判非合规。"""
    if version is None:
        return False
    return tuple(version) > tuple(ceiling)


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    """流式计算文件 SHA-256（大写十六进制），避免整文件入内存。"""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest().lower()


def verify_sha256(path: Path, expected_hex: str) -> bool:
    """完整性校验：实际哈希（不区分大小写）与锚定期望一致才 True。"""
    if not expected_hex:
        return False
    try:
        actual = sha256_of(path)
    except OSError:
        return False
    return actual == expected_hex.strip().lower()


def detect_installed_version(ollama_bin: str = "ollama") -> tuple[int, ...] | None:
    """运行 `ollama --version` 解析当前安装版本；不可用/未装返回 None。

    注意：`ollama --version` 在未起服务时会向 stderr 打 warning，版本仍可从任一输出解析。
    """
    exe = shutil.which(ollama_bin) or ollama_bin
    try:
        proc = subprocess.run(  # noqa: S603 固定参数、无 shell，输入受控
            [exe, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return parse_version(blob)


@dataclass
class Verdict:
    installed: bool
    version: str | None
    version_tuple: tuple[int, ...] | None
    compliant: bool
    ceiling: tuple[int, ...]


def judge(version: tuple[int, ...] | None) -> Verdict:
    """把版本元组折算成人类/机器可读裁定。"""
    compliant = is_compliant(version)
    return Verdict(
        installed=version is not None,
        version=".".join(str(x) for x in version) if version else None,
        version_tuple=version,
        compliant=compliant,
        ceiling=CRASH_BEARING_CEILING,
    )


def _run_or_print(cmd: list[str], dry_run: bool) -> int:
    """执行安装/回退命令（dry_run 时仅打印）。返回退出码（dry_run 记 0）。"""
    if dry_run:
        print(f"  [dry-run] 将执行: {' '.join(cmd)}")
        return 0
    proc = subprocess.run(cmd, check=False)  # noqa: S603 固定参数、无 shell
    return proc.returncode


def cmd_check(as_json: bool, ollama_bin: str) -> int:
    """只读自判（幂等，零副作用）。"""
    ver = detect_installed_version(ollama_bin)
    v = judge(ver)
    ceiling_str = ".".join(str(x) for x in CRASH_BEARING_CEILING)
    if as_json:
        payload = asdict(v)
        payload["ceiling"] = ceiling_str
        print(json.dumps(payload, ensure_ascii=False))
    elif not v.installed:
        print("[OLLAMA-GUARD] ⚠️ 未检测到 Ollama 或版本不可解析（可能未安装/不在 PATH）")
    elif v.compliant:
        print(
            f"[OLLAMA-GUARD] ✅ Ollama {v.version} > 崩溃构建天花板 {ceiling_str}，"
            "合规（AV@libllama+0x2a230 根因已随版本升级解除）"
        )
    else:
        print(
            f"[OLLAMA-GUARD] 🔴 Ollama {v.version} <= 崩溃构建天花板 {ceiling_str}，"
            "须升级（根因修复路径）"
        )
    if not v.installed:
        return EXIT_NOT_INSTALLED
    return EXIT_PASS if v.compliant else EXIT_NOT_COMPLIANT


def cmd_upgrade(args) -> int:
    """一条命令升级：版本判定→幂等→完整性校验→落装→复检→失败回退。绝不盲装。"""
    installer = Path(args.installer_path)
    cur = detect_installed_version(args.ollama_bin)
    cur_v = judge(cur)

    # 幂等：已合规且非强制 → no-op
    if cur_v.compliant and not args.force:
        print(f"[OLLAMA-GUARD] ✅ 当前 {cur_v.version} 已合规，无需升级（幂等 no-op）。加 --force 可强制重装")
        return EXIT_PASS

    if not installer.exists():
        print(f"[OLLAMA-GUARD] ❌ 安装器不存在: {installer}", file=sys.stderr)
        return EXIT_ERROR

    # 完整性校验（锚定 Operator 提供的官方校验和；不信任下载物自带哈希）
    if not verify_sha256(installer, args.expected_sha256):
        actual = sha256_of(installer)
        print(
            "[OLLAMA-GUARD] ❌ 完整性校验失败——中止且未落装（防 MITM/损坏包）\n"
            f"    期望 SHA-256: {args.expected_sha256.strip().lower()}\n"
            f"    实际 SHA-256: {actual}",
            file=sys.stderr,
        )
        return EXIT_ERROR
    print(f"[OLLAMA-GUARD] ✅ 完整性校验通过（{installer.name}）")

    # 快照当前版本用于回退说明
    prior = cur_v.version
    print(f"[OLLAMA-GUARD] 升级前版本: {prior or '未知'} → 落装 {installer.name}"
          + ("（dry-run）" if args.dry_run else ""))

    rc = _run_or_print([str(installer), "/S"], args.dry_run)  # Ollama Windows 安装器静默参数 /S
    if rc != 0:
        print(f"[OLLAMA-GUARD] ❌ 安装器返回非零（rc={rc}）——不视为成功", file=sys.stderr)

    # 复检
    post = judge(detect_installed_version(args.ollama_bin))
    if post.compliant:
        print(f"[OLLAMA-GUARD] ✅ 升级后复检 {post.version} 合规")
        return EXIT_PASS

    print(f"[OLLAMA-GUARD] 🔴 升级后复检非合规（version={post.version}）——回退", file=sys.stderr)
    # 回退：若有前一版安装器快照则重跑之；否则给出人工回退指引（不静默破坏现状）
    if args.prior_installer:
        prior_inst = Path(args.prior_installer)
        if prior_inst.exists():
            _run_or_print([str(prior_inst), "/S"], args.dry_run)
            print(f"[OLLAMA-GUARD] 已回退到 {args.prior_installer}")
    else:
        print(
            f"[OLLAMA-GUARD] 建议回退命令：重新运行前一版安装器（快照版本 {prior}）\n"
            "    验收（复跑溯源报告 §6）：升级窗口内无新增 0xc0000005/0xc0000409 事件",
            file=sys.stderr,
        )
    return EXIT_NOT_COMPLIANT


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ollama_version_guard",
        description="Ollama 版本守卫：自判合规/幂等；一条命令带完整性校验+失败回退升级（Owner 门位）",
    )
    p.add_argument("--check", action="store_true", help="只读自判（默认，零副作用，可常挂 CI/boot 探活）")
    p.add_argument("--upgrade", action="store_true", help="执行升级流程（需 --installer-path 与 --expected-sha256）")
    p.add_argument("--dry-run", action="store_true", help="与 --upgrade 配合，打印动作不真执行")
    p.add_argument("--json", action="store_true", dest="as_json", help="--check 输出机器可读 JSON")
    p.add_argument("--installer-path", help="本地已下载的安装器路径（--upgrade 必填）")
    p.add_argument("--expected-sha256", help="官方发布页公布的安装器 SHA-256（完整性锚，--upgrade 必填）")
    p.add_argument("--prior-installer", help="回退用的前一版安装器路径（可选）")
    p.add_argument("--force", action="store_true", help="即使当前已合规也强制走升级流程")
    p.add_argument("--ollama-bin", default="ollama", help="ollama 可执行文件名/路径（默认 ollama）")
    return p


def main(argv: list[str] | None = None) -> int:
    """入口函数."""
    args = build_parser().parse_args(argv)
    if args.upgrade:
        if not args.installer_path or not args.expected_sha256:
            print(
                "[OLLAMA-GUARD] ❌ --upgrade 需同时提供 --installer-path 与 --expected-sha256"
                "（软件安装=Owner 门位，拒绝无完整性锚的盲装）",
                file=sys.stderr,
            )
            return EXIT_ERROR
        return cmd_upgrade(args)
    # 默认 --check
    return cmd_check(args.as_json, args.ollama_bin)


if __name__ == "__main__":
    sys.exit(main())
