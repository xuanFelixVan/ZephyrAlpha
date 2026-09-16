# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §bdpan-tick-watch
# [MODULE] scripts.data.bdpan_tick_watch
# [DOMAIN] D_DATA
# [A_module] module_id=scripts-data-bdpan-tick-watch | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""bdpan tick 缺口看门狗（2026-09-16）：每日检查网盘按月归档，缺口日 zip 上传即自动下载+导入。

7 天缺口（20260703/0607/0608/0609/0609?/20260805/20260806）：上游 bdpan 分享按月归档
（分笔成交_按月归档_沪深/京市）尚未上传这些日期的 zip；本看门狗每日检查，zip 一出现：
  1. BaiduPCS-Go 下载到 E:\\数据下载\\tick 8 天缺口\\<月>\\
  2. 调 import_bdpan_tick_zip.py --zip-dir 导入（幂等：已有 bdpan 行自动跳过）
  3. Alerter 记录结果

用法：
  python scripts/data/bdpan_tick_watch.py            # 单次检查
  （计划任务 ZephyrAlpha_BdpanTickWatch 每日 08:00 触发）

配置：环境变量 BDPAN_TICK_GAP_DAYS（逗号分隔，默认 7 天缺口清单）。
退出码：0=无新增或全部导入成功；2=部分下载/导入失败；3=BaiduPCS 未登录。
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

BPCS = (
    r"C:\Users\fanzi\AppData\Local\Microsoft\WinGet\Packages"
    r"\qjfoidnh.BaiduPCS-Go_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\BaiduPCS-Go-v4.0.1-windows-x64\BaiduPCS-Go.exe"
)
BDPAN_BASE = "/apps/bdpan/量化交易数据/A股数据_分笔数据/分笔成交_按月归档"
DEST_ROOT = r"E:\数据下载\tick 8 天缺口"
DEFAULT_GAP_DAYS = "20260703,20260706,20260707,20260708,20260709,20260805,20260806"
_MONTH_OF = {"2026-07": ("20260703", "20260706", "20260707", "20260708", "20260709"), "2026-08": ("20260805", "20260806")}


def _bpsc(*args: str, timeout: int = 300) -> str:
    r = subprocess.run([BPCS, *args], capture_output=True, timeout=timeout)
    return (r.stdout + r.stderr).decode("utf-8", errors="replace")


def _check_remote(month: str, days: tuple) -> dict[str, int]:
    """返回 {yyyymmdd: 远端字节数}——仅统计该月归档下命中缺口日的 zip。"""
    out = _bpsc("cd", f"{BDPAN_BASE}/{month}", timeout=120)
    if "改变工作目录" not in out:
        return {}
    out = _bpsc("ls", timeout=120)
    found: dict[str, int] = {}
    for ln in out.splitlines():
        for d in days:
            if d in ln:
                # 提取大小（如 83.11MB）
                try:
                    size_part = ln.split()[1]
                    mult = {"KB": 1e3, "MB": 1e6, "GB": 1e9, "B": 1}.get(size_part[-2:], 1)
                    found[d] = int(float(size_part[:-2]) * mult)
                except Exception:  # noqa: BLE001 — 解析失败按 0 字节计
                    found[d] = 0
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="bdpan tick 缺口看门狗")
    ap.add_argument("--gap-days", default=os.environ.get("BDPAN_TICK_GAP_DAYS", DEFAULT_GAP_DAYS))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    days = tuple(args.gap_days.split(","))

    from zephyr.data.alerter import Alerter

    alerter = Alerter()
    who = _bpsc("who", timeout=60)
    if "uid" not in who:
        alerter.notify("bdpan_tick_watch", "BaiduPCS-Go 未登录，无法检查缺口 zip", level="ERROR")
        return 3

    pending: dict[str, int] = {}
    for month, month_days in _MONTH_OF.items():
        found = _check_remote(month, month_days)
        for d, size in found.items():
            if size > 1024:  # 0B 占位文件忽略
                pending[f"{month}/{d}.zip"] = size

    if not pending:
        print("上游尚未上传缺口日 zip，今日无动作")
        return 0

    print(f"发现 {len(pending)} 个缺口日 zip：{pending}")
    if args.dry_run:
        return 0

    results: dict[str, str] = {}
    for rel, _size in sorted(pending.items()):
        month, fname = rel.split("/")
        day = fname.replace(".zip", "")
        dest_dir = Path(DEST_ROOT) / month
        dest_dir.mkdir(parents=True, exist_ok=True)
        dl = _bpsc("download", f"{BDPAN_BASE}/{month}/{fname}", "--saveto", str(dest_dir / fname), timeout=3600)
        ok_dl = "下载成功" in dl or "已保存到" in dl or (dest_dir / fname).exists()
        if not ok_dl:
            results[day] = "下载失败"
            continue
        r = subprocess.run(
            [sys.executable, str(_REPO_ROOT / "scripts" / "data" / "import_bdpan_tick_zip.py"),
             "--zip-dir", str(dest_dir), "--days", day],
            cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=7200,
        )
        results[day] = f"导入 rc={r.returncode}"
        alerter.notify("bdpan_tick_watch", f"{day} tick 缺口 zip 已下载并导入（rc={r.returncode}）", level="INFO")

    failed = [d for d, s in results.items() if "失败" in s]
    if failed:
        alerter.notify("bdpan_tick_watch", f"部分缺口日失败: {failed}", level="ERROR")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
