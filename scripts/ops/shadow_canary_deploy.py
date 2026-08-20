# [BLUEPRINT] MOD-CD-001 | docs/03_modules/_cross_layer/cd_pipeline/blueprint.md
# [MODULE] zephyr.ops.shadow_canary_deploy
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.can_i_deploy; zephyr.security.access_control.canary_rollout_manager; zephyr.autonomy_core.context.shadow_canary; zephyr.governance.adapters.simulation_broker; zephyr.shared.infra.process_pool
# [CONSUMERS] .github/workflows/deploy.yml (shadow-canary job); 人工/CI 按需调用（簇C EX-021 门禁基建）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 预检失败立即退出不进入 shadow(exit 2); 影子进程强制 --broker simulation 走 simulation_broker 不下真单(shadow-cmd 含 simulation token,缺失则 warn); 分歧率 < threshold 才 promote(exit 0) 否则 rollback(exit 1); 状态机经 CanaryRolloutManager DRAFT→SAMPLING→ROLLOUT/ROLLED_BACK; report.json 落 logs/shadow_canary/<run_id>/; 影子输出路径经 ZEPHYR_SHADOW_OUTPUT_PATH 环境变量传给子进程; 比对按 (symbol,timestamp) 对齐,分歧=不匹配/已对齐(已对齐=0 且有单侧差异→1.0 fail-safe)
# [MODIFY-GUARD] docs/03_modules/_cross_layer/cd_pipeline/blueprint.md; .github/workflows/deploy.yml
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=promote(预检通过+分歧<threshold); exit 1=rollback(预检通过+分歧>=threshold); exit 2=预检失败(CanIDeploy blocker 或异常); 子进程异常降级 fail-closed exit 2; 比对/读文件异常不抛,记入 report 后按分歧语义裁决
# [TESTS] tests/ops/test_shadow_canary_deploy.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  合法 manual CI/CD 灰度发布运行器（簇C EX-021 门禁基建）：GitHub Actions workflow_dispatch / 人工按需调用，非常驻服务/cron/daemon，对齐 apply_depgraph.py 的 manual permanent CLI 写入模式
"""

shadow_canary_deploy.py — Shadow Canary 部署运行器（簇C CI/CD 灰度发布基建）

把 4 个已有原语编排成一条命令，满足 EX-021 门禁的「CI/CD 灰度发布基础设施」半：

  CanIDeploy (预检)  →  WindowsProcessDeployer (新版本影子进程)  →
  compare_decisions (输出比对)  →  CanaryRolloutManager (状态机)  →  report.json + 退出码

设计依据：
  - GATE-CDC-1 / CT-CDC-001：master blueprint §16（4 项预部署检查）
  - CT-CANARY-001：master blueprint §23.2（金丝雀阶段化 + 回滚触发条件）
  - Shadow Canary 模式：新版本并行跑、吸相同输入、**不下真单**（走
    ``simulation_broker``），比对输出一致性后再切——契合单机+实盘安全。

为什么 shadow 必须在生产机本地跑（而非 GitHub Actions 托管 runner）：
要比对真实生产输出，必须在生产机（Windows 单机）上启动新版本影子进程、
吸入与生产相同的行情数据输入。CI 部分（门禁+构建）在 Actions 托管 runner；
shadow/promote 部分通过本脚本在生产机本地执行（手动或 self-hosted runner 触发）。

退出码契约：
  0 = promote（预检通过 + 分歧率 < threshold）
  1 = rollback（预检通过 + 分歧率 >= threshold）
  2 = 预检失败（CanIDeploy 任一 blocker，或运行异常 fail-closed）

阶段感知（策略模式）：
  - ``WindowsProcessDeployer``（当前激活）：spawn 新版本子进程，强制
    ``--broker simulation``，输出写 ``logs/shadow_canary/<run_id>/new_decisions.jsonl``。
  - ``ContainerDeployer``（post-activation stub）：``raise NotImplementedError``，
    容器化在 #ARCH-065 激活。

预检命令可经环境变量覆盖（12-factor 风格，便于 smoke 测试注入轻量命令）：
  ZEPHYR_PRECHECK_CONSUMER_CMD   consumer_expectations 检查（默认 pytest tests/contracts/）
  ZEPHYR_PRECHECK_SCHEMA_CMD     schema_version 检查（默认 validate_static_manifest_drift.py --check）
  ZEPHYR_PRECHECK_CONTRACT_CMD   contract_consistency 检查（默认 validate_ssot.py --ci）
  ZEPHYR_PRECHECK_HEALTH_CMD     health 检查（默认 ``python -c "import zephyr"`` 存活检查）

用法示例::

  # 生产灰度（deploy.yml 调用）
  python scripts/ops/shadow_canary_deploy.py       --baseline-ref v1.2.3 --duration 600 --divergence-threshold 0.05

  # smoke 测试（预检跳过 + 自定义影子命令 + 测试数据）
  python scripts/ops/shadow_canary_deploy.py       --precheck-mode skip --duration 5 --divergence-threshold 0.05       --shadow-cmd "python -c 'import json,os;       p=os.environ["ZEPHYR_SHADOW_OUTPUT_PATH"];       open(p,"w").write(json.dumps({"symbol":"000001","timestamp":"t1","side":"BUY","quantity":100,"price":10.0})+chr(10))'"       --production-log tests/ops/fixtures/prod_decisions.jsonl

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: CLI 命令行参数 7项
#   fields: baseline_ref / duration / divergence_threshold / adapter / shadow_cmd / production_log / precheck_mode
#   code: _build_argparser L626
# - id: I2
#   name: 生产侧决策日志 jsonl 文件
#   fields: 每行一条 symbol/timestamp/side/quantity/price
#   code: logs/production_decisions.jsonl L107
# - id: I3
#   name: 影子进程输出决策 jsonl 文件
#   fields: 每行一条 symbol/timestamp/side/quantity/price（新版本影子决策）
#   code: logs/shadow_canary/<run_id>/new_decisions.jsonl（ZEPHYR_SHADOW_OUTPUT_PATH 传给子进程）
# - id: I4
#   name: 预检命令 4条 GATE-CDC-1
#   fields: consumer_expectations / schema_version / contract_consistency / health（环境变量 ZEPHYR_PRECHECK_*_CMD 可覆盖）
#   code: _PRECHECK_DEFAULTS L111
# 层: 算法
# - id: A1
#   name_zh: ① GATE-CDC-1 四项预检
#   name_en: run_precheck
#   intro: 发布前先跑4条治理检查命令，任一失败就不进入影子阶段
#   desc: 4条子命令 returncode==0 视为通过 + simulation_broker 可导入检查；skip 模式 vacuous-pass；异常 fail-closed 视为 blocker
#   inputs: I1 I4
#   outputs: CanIDeployResult（allowed/checks/blockers）
#   invariant: 预检失败 exit 2 不进入 shadow
# - id: A2
#   name_zh: ② 影子进程部署
#   name_en: WindowsProcessDeployer
#   intro: 启动新版本影子子进程吸相同输入，但走模拟券商不下真单
#   desc: spawn_python_hidden 启动 → wait_or_timeout 按 duration 等待 → stop 终止 → read_output 读输出；container 适配器为 NotImplementedError stub（#ARCH-065 激活）
#   inputs: I1
#   outputs: 影子决策 jsonl（经 I3 落盘）
#   invariant: shadow-cmd 须含 simulation token（缺失仅 warn 不阻断）
# - id: A3
#   name_zh: ③ 决策对齐比对
#   name_en: compare_decisions
#   intro: 按(symbol,timestamp)对齐生产与影子决策，算分歧率
#   desc: 分歧率=mismatches/aligned；不匹配=side不同 或 qty差>1e-9 或 price差超阈值；aligned=0且单侧有差异→1.0 fail-safe，双方皆空→0.0
#   inputs: I2 I3
#   outputs: ComparisonResult（divergence_rate/aligned/mismatches/new_only/prod_only/deltas）
# - id: A4
#   name_zh: ④ 金丝雀状态机裁决
#   name_en: CanaryRolloutManager
#   intro: 分歧率低于阈值就放行 ROLLOUT，否则回滚 ROLLED_BACK
#   desc: DRAFT→SAMPLING→ROLLOUT/ROLLED_BACK；promote = divergence_rate < threshold
#   inputs: A3
#   outputs: CanaryState + 退出码（0=promote / 1=rollback）
#   invariant: 分歧率 < threshold 才 promote
# - id: A5
#   name_zh: ⑤ 运行报告写入
#   name_en: _write_report
#   intro: 把预检/比对/状态机/退出码汇总落盘 report.json
#   desc: 汇总 run_id/precheck/comparison/shadow_canary/canary_state/exit_code/outcome 写 json；写失败不改变退出码
#   inputs: A1 A3 A4
#   outputs: report.json
# 层: 输出
# - id: O1
#   name_zh: report.json 灰度运行报告
#   name_en: report.json
#   intro: 本次灰度发布的完整裁决依据落盘文件
#   downstream: 人工审查/CI 归档 logs/shadow_canary/<run_id>/
# - id: O2
#   name_zh: 进程退出码 0/1/2
#   name_en: exit_code
#   intro: 0=promote放行 1=rollback回滚 2=预检失败或异常
#   invariant: 预检失败恒为2；分歧率>=阈值恒为1
#   downstream: .github/workflows/deploy.yml shadow-canary job 门禁（MOD-CD-001 消费方）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I4 --> A1
# I1 --> A2
# A1 --> A2
# A2 --> A3
# I2 --> A3
# I3 --> A3
# A3 --> A4
# A1 --> A5
# A3 --> A5
# A4 --> A5
# A5 --> O1
# A4 --> O2
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shlex
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

# 确保项目根在 sys.path（对标 ch_health_probe.py 范式）
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.autonomy_core.context.shadow_canary import (  # noqa: E402
    CanaryResult,
    ShadowCanary,
)
from zephyr.gov_enforcement.rule_enforcement.can_i_deploy import (  # noqa: E402
    CanIDeploy,
    CanIDeployResult,
)
from zephyr.security.access_control.canary_rollout_manager import (  # noqa: E402
    CanaryRolloutManager,
    CanaryState,
)
from zephyr.shared.infra.process_pool import (  # noqa: E402
    run_subprocess_hidden,
    spawn_python_hidden,
)

log = logging.getLogger("shadow_canary_deploy")

# ============================================================================
# 常量
# ============================================================================
SHADOW_OUTPUT_ENV = "ZEPHYR_SHADOW_OUTPUT_PATH"
DEFAULT_PRODUCTION_LOG = "logs/production_decisions.jsonl"
SHADOW_LOG_DIR = _REPO_ROOT / "logs" / "shadow_canary"

# 预检默认命令（生产灰度用；smoke 测试经环境变量覆盖为轻量命令）
_PRECHECK_DEFAULTS: dict[str, list[str]] = {
    "consumer_expectations": [sys.executable, "-m", "pytest", "tests/contracts/", "-q"],
    "schema_version": [
        sys.executable,
        "scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py",
        "--check",
    ],
    "contract_consistency": [
        sys.executable,
        "scripts/governance/d5_architecture/validators/validate_ssot.py",
        "--ci",
    ],
    "health": [sys.executable, "-c", "import zephyr"],
}
_PRECHECK_ENV_OVERRIDE = {
    "consumer_expectations": "ZEPHYR_PRECHECK_CONSUMER_CMD",
    "schema_version": "ZEPHYR_PRECHECK_SCHEMA_CMD",
    "contract_consistency": "ZEPHYR_PRECHECK_CONTRACT_CMD",
    "health": "ZEPHYR_PRECHECK_HEALTH_CMD",
}

EXIT_PROMOTE = 0
EXIT_ROLLBACK = 1
EXIT_PRECHECK_FAIL = 2


# ============================================================================
# 数据类
# ============================================================================
@dataclass
class ComparisonResult:
    """影子比对结果。"""

    divergence_rate: float
    aligned: int
    mismatches: int
    new_only: int  # shadow 有、生产无（新版本多出的决策）
    prod_only: int  # 生产有、shadow 无（新版本漏掉的决策）
    deltas: list[dict] = field(default_factory=list)

    @property
    def promote(self) -> bool:
        """分歧率 < 阈值 → promote（CT-CANARY-001 回滚触发条件的反面）。"""
        return self.divergence_rate < _ThresholdHolder.threshold


class _ThresholdHolder:
    """比较时使用的全局阈值占位（main 启动时设置，避免 promote 属性需传参）。

    用类属性而非实例——``run_deploy`` 启动时设置 ``_ThresholdHolder.threshold``，
    ``ComparisonResult.promote`` 读取它，免去把阈值逐层传进 dataclass。
    """

    threshold: float = 0.05


# ============================================================================
# 部署适配器（策略模式）
# ============================================================================
class WindowsProcessDeployer:
    """Windows 单机部署适配器——spawn 新版本子进程作为影子。

    影子进程经 ``ZEPHYR_SHADOW_OUTPUT_PATH`` 环境变量知道决策输出文件路径，
    自行把决策写入该 jsonl 文件。本适配器只负责启动/等待/停止/读输出，
    不关心影子进程内部如何消费行情（解耦 runner 与交易系统 I/O 细节）。
    """

    def __init__(
        self,
        command: list[str],
        output_path: Path,
        duration: int,
        cwd: Path | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> None:
        self._command = command
        self._output_path = output_path
        self._duration = duration
        self._cwd = str(cwd) if cwd else str(_REPO_ROOT)
        self._extra_env = extra_env or {}
        self._proc = None
        self._pid: int | None = None

    def start(self) -> int:
        env = dict(os.environ)
        env[SHADOW_OUTPUT_ENV] = str(self._output_path)
        env.update(self._extra_env)
        self._proc = spawn_python_hidden(
            self._command,
            cwd=self._cwd,
            env=env,
            stdout_to_devnull=False,  # 允许影子进程 stdout 继承（便于调试）
            stderr_to_devnull=False,
        )
        self._pid = self._proc.pid
        log.info("影子进程已启动: pid=%s, cmd=%s, output=%s", self._pid, self._command, self._output_path)
        return self._pid

    def wait_or_timeout(self) -> str:
        """等待影子进程结束或超时。

        Returns:
            "exited"（进程自行退出）或 "timeout"（到达 duration 超时）。
        """
        deadline = time.time() + max(0, self._duration)
        while True:
            if self._proc is None:
                return "exited"
            rc = self._proc.poll()
            if rc is not None:
                log.info("影子进程已退出: pid=%s rc=%s", self._pid, rc)
                return "exited"
            if time.time() >= deadline:
                log.info("影子进程到达 duration 超时: pid=%s", self._pid)
                return "timeout"
            time.sleep(1)

    def stop(self) -> None:
        if self._proc is None:
            return
        if self._proc.poll() is None:
            try:
                self._proc.terminate()
                try:
                    self._proc.wait(timeout=5)
                except Exception:  # noqa: BLE001 — terminate 后 wait 超时强制 kill
                    self._proc.kill()
            except Exception as e:  # noqa: BLE001 — stop 失败不阻断报告产出
                log.warning("停止影子进程失败 pid=%s: %s", self._pid, e)

    def read_output(self) -> list[dict]:
        return load_decisions(self._output_path)


class ContainerDeployer:
    """容器部署适配器（post-activation stub）。

    容器化部署在 #ARCH-065 激活（接入真实资金后），当前所有方法 raise
    NotImplementedError，结构上预留扩展点。
    """

    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError(
            "容器化部署在 post-activation 激活，见 #ARCH-065。"
            " 当前阶段使用 --adapter windows（WindowsProcessDeployer）。"
        )


def make_deployer(adapter: str, command: list[str], output_path: Path, duration: int, **kwargs):
    """工厂：按 adapter 名构造部署适配器。"""
    if adapter == "windows":
        return WindowsProcessDeployer(command, output_path, duration, **kwargs)
    if adapter == "container":
        return ContainerDeployer(command, output_path, duration, **kwargs)
    raise ValueError(f"未知 adapter: {adapter}（支持: windows | container）")


# ============================================================================
# 预检（GATE-CDC-1 / CT-CDC-001）
# ============================================================================
def _resolve_precheck_command(check_name: str) -> list[str]:
    """解析单条预检命令：env 覆盖 > 默认。env 值为 shell 字符串（shlex.split）。"""
    env_var = _PRECHECK_ENV_OVERRIDE[check_name]
    env_val = os.environ.get(env_var, "").strip()
    if env_val:
        return shlex.split(env_val)
    return list(_PRECHECK_DEFAULTS[check_name])


def _run_check_command(cmd: list[str]) -> bool:
    """运行一条预检命令，returncode==0 视为通过。fail-closed：异常视为失败。"""
    try:
        result = run_subprocess_hidden(cmd, cwd=str(_REPO_ROOT), timeout=600)
        ok = result.returncode == 0
        if not ok:
            stderr = (result.stderr or "").strip()
            log.warning("预检命令失败: cmd=%s rc=%s stderr=%s", cmd, result.returncode, stderr[:300])
        return ok
    except Exception as e:  # noqa: BLE001 — fail-closed：预检异常视为 blocker
        log.warning("预检命令异常: cmd=%s err=%s", cmd, e)
        return False


def _verify_simulation_broker_available() -> bool:
    """验证 simulation_broker 依赖可加载（shadow 进程将走它不下真单）。

    fail-closed：不可导入视为 health blocker——影子进程无模拟券商则可能下真单。
    """
    try:
        from zephyr.governance.adapters.simulation_broker import SimulationBroker  # noqa: F401

        return True
    except Exception as e:  # noqa: BLE001
        log.warning("simulation_broker 不可加载: %s（影子进程可能无法走模拟券商）", e)
        return False


def run_precheck(mode: str) -> CanIDeployResult:
    """执行 GATE-CDC-1 四项预检，返回 CanIDeployResult。

    Args:
        mode: "full" 运行真实预检命令；"skip" 全部 vacuous-pass（smoke/重跑用）。
    """
    if mode == "skip":
        log.info("预检模式=skip，全部 vacuous-pass（smoke/重跑，不运行治理套件）")
        return CanIDeploy().check(
            consumer_expectations_ok=True,
            schema_version_ok=True,
            contract_consistency_ok=True,
            health_ok=True,
        )
    log.info("预检模式=full，运行 GATE-CDC-1 四项检查...")
    # checks dict 键名对齐 CanIDeployResult.checks（无 _ok 后缀，供报告输出）；
    # CanIDeploy.check() 形参带 _ok 后缀，下方显式映射。
    raw_checks = {
        "consumer_expectations": _run_check_command(_resolve_precheck_command("consumer_expectations")),
        "schema_version": _run_check_command(_resolve_precheck_command("schema_version")),
        "contract_consistency": _run_check_command(_resolve_precheck_command("contract_consistency")),
        "health": _run_check_command(_resolve_precheck_command("health")) and _verify_simulation_broker_available(),
    }
    result = CanIDeploy().check(
        consumer_expectations_ok=raw_checks["consumer_expectations"],
        schema_version_ok=raw_checks["schema_version"],
        contract_consistency_ok=raw_checks["contract_consistency"],
        health_ok=raw_checks["health"],
    )
    log.info("预检结果: allowed=%s checks=%s blockers=%s", result.allowed, result.checks, result.blockers)
    return result


# ============================================================================
# 影子比对（CT-CANARY-001 输出一致性）
# ============================================================================
def load_decisions(path: Path | str) -> list[dict]:
    """读取 jsonl 决策文件，每行一条 JSON。文件缺失/空 → 空列表。"""
    p = Path(path)
    if not p.exists():
        log.warning("决策文件不存在: %s（视为空）", p)
        return []
    decisions: list[dict] = []
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                decisions.append(json.loads(line))
            except json.JSONDecodeError as e:
                log.warning("决策行 JSON 解析失败 %s: %s（跳过）", line[:80], e)
    except Exception as e:  # noqa: BLE001 — 读文件异常不阻断，返回已读部分
        log.warning("读取决策文件异常 %s: %s", p, e)
    return decisions


def _to_float(v) -> float:
    """容错转 float（None/字符串/Decimal 等）。"""
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def compare_decisions(
    prod: list[dict],
    shadow: list[dict],
    *,
    qty_epsilon: float = 1e-9,
    price_epsilon: float = 1e-9,
) -> ComparisonResult:
    """按 (symbol, timestamp) 对齐生产与影子决策，计算分歧率。

    分歧率 = 不匹配数 / 已对齐数。
    已对齐数=0 时：双方皆空 → 0.0（无可比对，vacuous promote）；
    单侧有差异 → 1.0（fail-safe，无法比对视为全分歧）。
    不匹配 = side 不同，或 quantity 差异 > qty_epsilon，或 price 差异 > price_epsilon。
    """
    prod_map = {(d.get("symbol"), d.get("timestamp")): d for d in prod}
    shadow_map = {(d.get("symbol"), d.get("timestamp")): d for d in shadow}
    keys = set(prod_map) | set(shadow_map)

    aligned = 0
    mismatches = 0
    new_only = 0
    prod_only = 0
    deltas: list[dict] = []

    for k in keys:
        p = prod_map.get(k)
        s = shadow_map.get(k)
        if p is not None and s is not None:
            aligned += 1
            reasons: list[str] = []
            if str(p.get("side", "")).upper() != str(s.get("side", "")).upper():
                reasons.append(f"side {p.get('side')}->{s.get('side')}")
            if abs(_to_float(p.get("quantity")) - _to_float(s.get("quantity"))) > qty_epsilon:
                reasons.append(f"qty {p.get('quantity')}->{s.get('quantity')}")
            if (
                abs(_to_float(p.get("price")) - _to_float(s.get("price"))) > _to_float(s.get("price")) * 1e-6
                and abs(_to_float(p.get("price")) - _to_float(s.get("price"))) > price_epsilon
            ):
                reasons.append(f"price {p.get('price')}->{s.get('price')}")
            if reasons:
                mismatches += 1
                deltas.append({"key": list(k), "reasons": reasons})
        elif s is not None and p is None:
            new_only += 1
            deltas.append({"key": list(k), "reasons": ["shadow_only"]})
        elif p is not None and s is None:
            prod_only += 1
            deltas.append({"key": list(k), "reasons": ["prod_only"]})

    if aligned > 0:
        divergence = mismatches / aligned
    elif prod_only or new_only:
        divergence = 1.0  # fail-safe：无可对齐但有单侧差异
    else:
        divergence = 0.0  # 双方皆空

    return ComparisonResult(
        divergence_rate=divergence,
        aligned=aligned,
        mismatches=mismatches,
        new_only=new_only,
        prod_only=prod_only,
        deltas=deltas,
    )


# ============================================================================
# 主流程
# ============================================================================
def _build_default_shadow_command() -> list[str]:
    """默认影子命令：python -m zephyr.trading --broker simulation --shadow。

    注意：zephyr.trading 对 --broker/--shadow 的支持是 post-activation，
    当前阶段 smoke 测试应经 --shadow-cmd 覆盖为轻量命令。
    """
    return [sys.executable, "-m", "zephyr.trading", "--broker", "simulation", "--shadow"]


def _parse_shadow_cmd(raw: str | None) -> list[str]:
    """解析 --shadow-cmd（shell 字符串）或返回默认命令。

    用 POSIX shlex 规则切分（支持引号包裹的 -c 代码块）。Windows 路径须用
    正斜杠或双反斜杠——POSIX shlex 会把单反斜杠当转义符吃掉（如
    ``D:\\path`` → ``D:path``）。正斜杠在 Python 下跨平台可用，推荐。
    """
    if raw:
        return shlex.split(raw, posix=True)
    return _build_default_shadow_command()


def _assert_simulation_in_command(command: list[str]) -> None:
    """INVARIANTS: 影子命令须含 simulation token（走 simulation_broker 不下真单）。

    缺失则 warn（不阻断——命令形式多变，token 检查是启发式）。
    """
    joined = " ".join(command)
    if "simulation" not in joined:
        log.warning(
            "影子命令未含 'simulation' token: %s —— 确保影子进程走 simulation_broker"
            " 不下真单（INVARIANTS）。若命令使用其他形式指定模拟券商，可忽略本警告。",
            joined,
        )


def run_deploy(
    *,
    baseline_ref: str,
    duration: int,
    divergence_threshold: float,
    adapter: str,
    shadow_cmd: str | None,
    production_log: str,
    precheck_mode: str,
) -> int:
    """主流程：预检 → 影子部署 → 比对 → 状态机 → 报告。返回退出码。"""
    _ThresholdHolder.threshold = divergence_threshold
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = SHADOW_LOG_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    shadow_output = run_dir / "new_decisions.jsonl"
    report_path = run_dir / "report.json"
    started_at = datetime.now().isoformat(timespec="seconds")

    log.info("=== Shadow Canary Run %s ===", run_id)
    log.info(
        "baseline=%s duration=%ss threshold=%s adapter=%s precheck=%s",
        baseline_ref,
        duration,
        divergence_threshold,
        adapter,
        precheck_mode,
    )

    # 1. 预检（GATE-CDC-1）
    precheck = run_precheck(precheck_mode)
    if not precheck.allowed:
        log.error("预检失败 blockers=%s —— 不进入 shadow", precheck.blockers)
        _write_report(
            report_path,
            run_id,
            started_at,
            baseline_ref,
            duration,
            divergence_threshold,
            precheck,
            None,
            None,
            CanaryState.DRAFT,
            EXIT_PRECHECK_FAIL,
            "precheck_failed",
        )
        return EXIT_PRECHECK_FAIL

    # 2. 影子部署（CT-CANARY-001 shadow 阶段）
    command = _parse_shadow_cmd(shadow_cmd)
    _assert_simulation_in_command(command)
    shadow_canary = ShadowCanary()
    canary_result: CanaryResult | None = None
    comparison: ComparisonResult | None = None
    state = CanaryState.DRAFT
    exit_code = EXIT_PRECHECK_FAIL
    outcome = "unknown"

    try:
        deployer = make_deployer(adapter, command, shadow_output, duration)
        # 状态机：DRAFT → SAMPLING
        manager = CanaryRolloutManager()
        canary_name = f"shadow-{run_id}"
        manager.register(canary_name, rules=["no_real_orders", "output_comparison"])
        manager.start_sampling(canary_name)
        state = CanaryState.SAMPLING
        log.info("状态机: DRAFT -> SAMPLING (canary=%s)", canary_name)

        deployer.start()
        wait_result = deployer.wait_or_timeout()
        deployer.stop()

        # 3. 影子比对
        shadow_decisions = deployer.read_output()
        prod_decisions = load_decisions(production_log)
        log.info(
            "比对: shadow=%d 条, production=%d 条 (源=%s)", len(shadow_decisions), len(prod_decisions), production_log
        )
        comparison = compare_decisions(prod_decisions, shadow_decisions)
        log.info(
            "比对结果: divergence=%.4f aligned=%d mismatches=%d new_only=%d prod_only=%d",
            comparison.divergence_rate,
            comparison.aligned,
            comparison.mismatches,
            comparison.new_only,
            comparison.prod_only,
        )

        # ShadowCanary 语义复用：记录 shadow_generated，promote 由分歧率裁决
        canary_result = shadow_canary.shadow(
            strategy=baseline_ref,
            context=f"divergence={comparison.divergence_rate:.4f}",
        )
        canary_result.performance_delta = -comparison.divergence_rate  # 负分歧=好

        # 4. 状态机：SAMPLING → ROLLOUT / ROLLED_BACK
        if comparison.promote:
            state = CanaryState.ROLLOUT
            exit_code = EXIT_PROMOTE
            outcome = "promote"
            log.info(
                "promote=True (分歧 %.4f < 阈值 %s) → ROLLOUT, exit 0", comparison.divergence_rate, divergence_threshold
            )
        else:
            state = CanaryState.ROLLED_BACK
            exit_code = EXIT_ROLLBACK
            outcome = "rollback"
            log.warning(
                "promote=False (分歧 %.4f >= 阈值 %s) → ROLLED_BACK, exit 1",
                comparison.divergence_rate,
                divergence_threshold,
            )
    except NotImplementedError as e:
        log.error("部署适配器未实现: %s", e)
        state = CanaryState.ROLLED_BACK
        exit_code = EXIT_PRECHECK_FAIL
        outcome = f"adapter_error: {e}"
    except Exception as e:  # noqa: BLE001 — fail-closed：运行异常 exit 2
        log.exception("Shadow Canary 运行异常: %s", e)
        state = CanaryState.ROLLED_BACK
        exit_code = EXIT_PRECHECK_FAIL
        outcome = f"exception: {type(e).__name__}: {e}"

    _write_report(
        report_path,
        run_id,
        started_at,
        baseline_ref,
        duration,
        divergence_threshold,
        precheck,
        comparison,
        canary_result,
        state,
        exit_code,
        outcome,
    )
    log.info("报告已写入: %s (outcome=%s, exit=%s)", report_path, outcome, exit_code)
    return exit_code


def _write_report(
    report_path: Path,
    run_id: str,
    started_at: str,
    baseline_ref: str,
    duration: int,
    divergence_threshold: float,
    precheck: CanIDeployResult,
    comparison: ComparisonResult | None,
    canary_result: CanaryResult | None,
    state: str,
    exit_code: int,
    outcome: str,
) -> None:
    """写 report.json（运行记录 + 裁决依据）。"""
    report = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "baseline_ref": baseline_ref,
        "duration_seconds": duration,
        "divergence_threshold": divergence_threshold,
        "precheck": {
            "allowed": precheck.allowed,
            "checks": precheck.checks,
            "blockers": precheck.blockers,
        },
        "comparison": asdict(comparison) if comparison else None,
        "shadow_canary": {
            "strategy_name": canary_result.strategy_name if canary_result else None,
            "shadow_generated": canary_result.shadow_generated if canary_result else None,
            "performance_delta": canary_result.performance_delta if canary_result else None,
        }
        if canary_result
        else None,
        "canary_state": state,
        "exit_code": exit_code,
        "outcome": outcome,
    }
    try:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:  # noqa: BLE001 — 报告写入失败不改变退出码
        log.error("写 report.json 失败: %s", e)


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="shadow_canary_deploy.py",
        description="Shadow Canary 部署运行器（簇C CI/CD 灰度发布基建，MOD-CD-001）。"
        "预检 → 影子部署 → 比对 → 状态机 → 报告。"
        "退出码: 0=promote, 1=rollback, 2=预检失败。",
    )
    p.add_argument("--baseline-ref", default="HEAD", help="基线版本（默认当前生产 HEAD）")
    p.add_argument("--duration", type=int, default=600, help="影子运行秒数（默认 600）")
    p.add_argument(
        "--divergence-threshold",
        type=float,
        default=0.05,
        help="输出分歧率阈值，<阈值 promote、>=阈值 rollback（默认 0.05）",
    )
    p.add_argument(
        "--adapter",
        choices=["windows", "container"],
        default="windows",
        help="部署适配器（默认 windows；container 为 post-activation stub）",
    )
    p.add_argument(
        "--shadow-cmd",
        default=None,
        help="影子进程命令（shell 字符串，shlex 解析）。"
        "默认 'python -m zephyr.trading --broker simulation --shadow'。"
        "smoke 测试应覆盖为轻量命令。子进程经 ZEPHYR_SHADOW_OUTPUT_PATH"
        " 环境变量获取决策输出文件路径。",
    )
    p.add_argument(
        "--production-log",
        default=DEFAULT_PRODUCTION_LOG,
        help=f"生产侧决策 jsonl 路径（默认 {DEFAULT_PRODUCTION_LOG}）",
    )
    p.add_argument(
        "--precheck-mode",
        choices=["full", "skip"],
        default="full",
        help="预检模式: full=运行 GATE-CDC-1 四项检查; skip=vacuous-pass（smoke/重跑用）",
    )
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    return run_deploy(
        baseline_ref=args.baseline_ref,
        duration=args.duration,
        divergence_threshold=args.divergence_threshold,
        adapter=args.adapter,
        shadow_cmd=args.shadow_cmd,
        production_log=args.production_log,
        precheck_mode=args.precheck_mode,
    )


if __name__ == "__main__":
    sys.exit(main())
