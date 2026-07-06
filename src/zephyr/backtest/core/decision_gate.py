# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.decision_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.implementations.event_driven_engine
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] IS→WFA→OOS不可跳级;参数锁定;Sharpe>0.5准入
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DecisionGateError
# [TESTS]
# [TTL] permanent
# [A_module] module_id=MOD-BT-001-decision-gate | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
"""3阶段决策门控模块(IS→WFA→OOS)

职责:
  - IS(In-Sample)阶段:样本内Sharpe准入(>0.5)+参数稳定性门控(避悬崖型参数)
  - WFA(Walk-Forward Analysis)阶段:滚动Walk-Forward多数通过(>50%)+灾难否决(回撤>50%)
  - OOS(Out-of-Sample)阶段:参数锁定+样本外Sharpe>=70%样本内Sharpe+人工审批上线
  - 参数稳定性区域:识别稳定高原(±10%范围Sharpe变化<20%)+避悬崖型参数(微调导致Sharpe下降>50%)
  - 回测-实盘偏差监控:偏差>30%告警,偏差>50%退役

约束:
  - IS→WFA→OOS不可跳级:IS未通过不进入WFA;WFA未通过不进入OOS
  - 进入OOS后参数锁定,不可调整
  - 正式上线需人工审批(can_deploy仅表示技术门控通过)

SSoT: docs/03_modules/_domain_backtest/blueprint.md §3.3 P0-14
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class DecisionGateError(Exception):
    """决策门控错误"""

    error_code = "ZA-BT-0009"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


@dataclass(frozen=True)
class DecisionGateConfig:
    """决策门控配置

    Attributes:
        is_sharpe_threshold: IS阶段Sharpe准入门槛(默认0.5)
        wfa_sharpe_threshold: WFA阶段单窗口Sharpe通过门槛(默认0.0,
            区别于IS门槛; WFA关注Walk-Forward各fold的相对稳定性而非绝对准入);
            0.0=要求fold为正Sharpe即可
        oos_sharpe_ratio_threshold: OOS Sharpe/IS Sharpe 比率门槛(默认0.7)
        wfa_majority_pct: WFA多数通过比例(默认0.5,即>50%)
        disaster_max_drawdown: 灾难否决最大回撤(默认0.5,即50%)
        stability_plateau_tolerance: 稳定高原Sharpe变化容忍度(默认0.20)
        cliff_sharpe_drop: 悬崖型参数Sharpe下降阈值(默认0.50)
        backtest_live_deviation_warn: 回测-实盘偏差告警阈值(默认0.30)
        backtest_live_deviation_retire: 回测-实盘偏差退役阈值(默认0.50)
    """

    is_sharpe_threshold: float = 0.5
    wfa_sharpe_threshold: float = 0.0
    oos_sharpe_ratio_threshold: float = 0.7
    wfa_majority_pct: float = 0.5
    disaster_max_drawdown: float = 0.5
    stability_plateau_tolerance: float = 0.20
    cliff_sharpe_drop: float = 0.50
    backtest_live_deviation_warn: float = 0.30
    backtest_live_deviation_retire: float = 0.50


@dataclass(frozen=True)
class ISStageResult:
    """IS(In-Sample)阶段结果

    Attributes:
        passed: 是否通过本阶段
        sharpe: 样本内Sharpe比率
        optimal_params: 最优参数字典
        is_plateau_stable: 参数是否处于稳定高原(非悬崖型)
        reasons: 判定原因列表
    """

    passed: bool
    sharpe: float
    optimal_params: dict[str, Any]
    is_plateau_stable: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class WFAStageResult:
    """WFA(Walk-Forward Analysis)阶段结果

    Attributes:
        passed: 是否通过本阶段
        windows_total: Walk-Forward窗口总数
        windows_passed: 通过的窗口数
        has_disaster: 是否出现灾难性回撤
        reasons: 判定原因列表
    """

    passed: bool
    windows_total: int
    windows_passed: int
    has_disaster: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class OOSStageResult:
    """OOS(Out-of-Sample)阶段结果

    Attributes:
        passed: 是否通过本阶段
        oos_sharpe: 样本外Sharpe比率
        is_sharpe: 样本内Sharpe比率
        oos_is_ratio: 样本外/样本内Sharpe比率
        params_locked: 参数是否已锁定
        reasons: 判定原因列表
    """

    passed: bool
    oos_sharpe: float
    is_sharpe: float
    oos_is_ratio: float
    params_locked: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DecisionGateResult:
    """3阶段决策门控综合结果

    Attributes:
        is_stage: IS阶段结果
        wfa_stage: WFA阶段结果
        oos_stage: OOS阶段结果
        overall_passed: 三阶段是否全部通过
        can_deploy: 是否可上线(技术门控通过,仍需人工审批)
        reasons: 综合判定原因列表
    """

    is_stage: ISStageResult
    wfa_stage: WFAStageResult
    oos_stage: OOSStageResult
    overall_passed: bool
    can_deploy: bool
    reasons: list[str] = field(default_factory=list)


class DecisionGate:
    """3阶段决策门控(IS→WFA→OOS)

    按蓝图§3.3 P0-14编排三阶段决策:
      1. IS阶段:样本内Sharpe准入+参数稳定性门控
      2. WFA阶段:Walk-Forward多数通过+灾难否决
      3. OOS阶段:参数锁定+样本外Sharpe比率门控

    阶段不可跳级:IS未通过不进入WFA;WFA未通过不进入OOS。
    """

    def __init__(self, config: DecisionGateConfig | None = None) -> None:
        """初始化决策门控

        Args:
            config: 决策门控配置,为None时使用默认配置
        """
        self.config: DecisionGateConfig = (
            config if config is not None else DecisionGateConfig()
        )

    def check_is_stage(
        self,
        sharpe: float,
        params: dict[str, Any],
        param_sensitivity: dict[str, list[tuple[Any, float]]] | None = None,
    ) -> ISStageResult:
        """IS(In-Sample)阶段门控检查

        检查项:
          - Sharpe准入门控:Sharpe > is_sharpe_threshold(默认0.5)
          - 参数稳定性门控:参数处于稳定高原且非悬崖型(避悬崖型参数)

        Args:
            sharpe: 样本内Sharpe比率
            params: 最优参数字典
            param_sensitivity: 参数敏感性扫描结果,键为参数名,值为(参数值,Sharpe)列表;
                为None时跳过稳定性门控

        Returns:
            ISStageResult: IS阶段判定结果

        Raises:
            DecisionGateError: sharpe非数值或params非字典
        """
        # 输入校验
        try:
            sharpe_f = float(sharpe)
        except (TypeError, ValueError) as exc:
            raise DecisionGateError(f"sharpe必须是数值: {sharpe!r}") from exc
        if not isinstance(params, dict):
            raise DecisionGateError(
                f"params必须是字典: {type(params).__name__}"
            )

        reasons: list[str] = []
        # 复制参数,避免外部突变
        optimal_params = dict(params)

        # Sharpe准入门控
        sharpe_passed = sharpe_f > self.config.is_sharpe_threshold
        if sharpe_passed:
            reasons.append(
                f"Sharpe准入通过: {sharpe_f:.4f} > {self.config.is_sharpe_threshold}"
            )
        else:
            reasons.append(
                f"Sharpe准入未通过: {sharpe_f:.4f} <= {self.config.is_sharpe_threshold}"
            )

        # 参数稳定性门控
        is_plateau_stable = True
        if param_sensitivity is None:
            reasons.append("未提供参数敏感性数据,跳过稳定性门控")
        else:
            if not isinstance(param_sensitivity, dict):
                raise DecisionGateError(
                    f"param_sensitivity必须是字典: {type(param_sensitivity).__name__}"
                )
            unstable_params: list[str] = []
            for param_name, scan_points in param_sensitivity.items():
                if not scan_points:
                    # 扫描点为空,视为数据不足,标记不稳定
                    is_plateau_stable = False
                    unstable_params.append(f"{param_name}(扫描点为空)")
                    continue
                plateau_info = self.check_stability_plateau(param_name, scan_points)
                if not plateau_info["is_plateau"] or plateau_info["is_cliff"]:
                    is_plateau_stable = False
                    unstable_params.append(
                        f"{param_name}({plateau_info['reason']})"
                    )
            if is_plateau_stable:
                reasons.append("参数稳定性门控通过:所有参数处于稳定高原且非悬崖型")
            else:
                reasons.append(
                    "参数稳定性门控未通过:存在不稳定参数 -> "
                    + "; ".join(unstable_params)
                )

        passed = sharpe_passed and is_plateau_stable
        return ISStageResult(
            passed=passed,
            sharpe=sharpe_f,
            optimal_params=optimal_params,
            is_plateau_stable=is_plateau_stable,
            reasons=reasons,
        )

    def check_wfa_stage(self, walk_forward_results: list[dict]) -> WFAStageResult:
        """WFA(Walk-Forward Analysis)阶段门控检查

        检查项:
          - 多数通过:通过窗口数/总窗口数 > wfa_majority_pct(默认0.5)
          - 灾难否决:任一窗口最大回撤 > disaster_max_drawdown(默认0.5)则直接否决

        每个窗口字典可包含:
          - "passed"(bool):窗口是否通过;未提供时按"sharpe"是否>准入门槛判定
          - "sharpe"(float):窗口Sharpe比率
          - "max_drawdown"(float):窗口最大回撤(正值,如0.5表示50%)

        Args:
            walk_forward_results: Walk-Forward窗口结果列表

        Returns:
            WFAStageResult: WFA阶段判定结果

        Raises:
            DecisionGateError: walk_forward_results非列表或窗口结构非法
        """
        if not isinstance(walk_forward_results, list):
            raise DecisionGateError(
                f"walk_forward_results必须是列表: {type(walk_forward_results).__name__}"
            )

        reasons: list[str] = []
        windows_total = len(walk_forward_results)

        if windows_total == 0:
            reasons.append("无Walk-Forward窗口数据,WFA阶段未通过")
            return WFAStageResult(
                passed=False,
                windows_total=0,
                windows_passed=0,
                has_disaster=False,
                reasons=reasons,
            )

        windows_passed = 0
        has_disaster = False
        disaster_windows: list[int] = []

        for idx, window in enumerate(walk_forward_results):
            if not isinstance(window, dict):
                raise DecisionGateError(
                    f"Walk-Forward窗口{idx}必须是字典: {type(window).__name__}"
                )
            # 窗口通过判定:优先使用passed字段,否则按sharpe判定
            # P2-2 修正: WFA使用独立的wfa_sharpe_threshold(非IS门槛),
            # 因为WFA关注的是Walk-Forward各fold的相对稳定性, 而非IS绝对准入
            if "passed" in window:
                w_passed = bool(window["passed"])
            elif "sharpe" in window:
                try:
                    w_passed = float(window["sharpe"]) > self.config.wfa_sharpe_threshold
                except (TypeError, ValueError) as exc:
                    raise DecisionGateError(
                        f"窗口{idx}的sharpe非数值: {window['sharpe']!r}"
                    ) from exc
            else:
                w_passed = False
                reasons.append(f"窗口{idx}缺少passed/sharpe字段,按未通过处理")
            if w_passed:
                windows_passed += 1

            # 灾难否决判定:max_drawdown取绝对值(兼容正负号表达)
            md_raw = window.get("max_drawdown", 0.0)
            try:
                md_abs = abs(float(md_raw))
            except (TypeError, ValueError) as exc:
                raise DecisionGateError(
                    f"窗口{idx}的max_drawdown非数值: {md_raw!r}"
                ) from exc
            if md_abs > self.config.disaster_max_drawdown:
                has_disaster = True
                disaster_windows.append(idx)

        pass_ratio = windows_passed / windows_total
        majority_passed = pass_ratio > self.config.wfa_majority_pct

        reasons.append(
            f"Walk-Forward通过率: {windows_passed}/{windows_total} = {pass_ratio:.4f} "
            f"(门槛> {self.config.wfa_majority_pct})"
        )
        if has_disaster:
            reasons.append(
                f"灾难否决触发:窗口{disaster_windows}最大回撤超过"
                f"{self.config.disaster_max_drawdown}"
            )

        passed = majority_passed and not has_disaster
        if passed:
            reasons.append("WFA阶段通过:多数窗口通过且无灾难性回撤")
        else:
            reasons.append("WFA阶段未通过")
        return WFAStageResult(
            passed=passed,
            windows_total=windows_total,
            windows_passed=windows_passed,
            has_disaster=has_disaster,
            reasons=reasons,
        )

    def check_oos_stage(
        self,
        is_sharpe: float,
        oos_sharpe: float,
        params_locked: bool = True,
    ) -> OOSStageResult:
        """OOS(Out-of-Sample)阶段门控检查

        检查项:
          - 参数锁定:进入OOS后参数不可调整(params_locked必须为True)
          - 样本外Sharpe比率:oos_sharpe/is_sharpe >= oos_sharpe_ratio_threshold(默认0.7)

        Args:
            is_sharpe: 样本内Sharpe比率
            oos_sharpe: 样本外Sharpe比率
            params_locked: 参数是否已锁定

        Returns:
            OOSStageResult: OOS阶段判定结果

        Raises:
            DecisionGateError: is_sharpe或oos_sharpe非数值
        """
        try:
            is_f = float(is_sharpe)
            oos_f = float(oos_sharpe)
        except (TypeError, ValueError) as exc:
            raise DecisionGateError(
                f"is_sharpe/oos_sharpe必须是数值: {is_sharpe!r}, {oos_sharpe!r}"
            ) from exc

        reasons: list[str] = []

        # 参数锁定检查
        if params_locked:
            reasons.append("参数已锁定(OOS阶段参数不可调整)")
        else:
            reasons.append("参数未锁定,OOS阶段要求参数锁定")

        # 样本外Sharpe比率检查
        if is_f <= 0:
            oos_is_ratio = 0.0
            reasons.append(
                f"样本内Sharpe={is_f:.4f}<=0,无法满足OOS/IS比率门槛"
            )
            ratio_passed = False
        else:
            oos_is_ratio = oos_f / is_f
            ratio_passed = oos_is_ratio >= self.config.oos_sharpe_ratio_threshold
            if ratio_passed:
                reasons.append(
                    f"OOS/IS Sharpe比率通过: {oos_is_ratio:.4f} >= "
                    f"{self.config.oos_sharpe_ratio_threshold}"
                )
            else:
                reasons.append(
                    f"OOS/IS Sharpe比率未通过: {oos_is_ratio:.4f} < "
                    f"{self.config.oos_sharpe_ratio_threshold}"
                )

        passed = bool(params_locked) and ratio_passed
        if passed:
            reasons.append("OOS阶段通过(正式上线仍需人工审批)")
        else:
            reasons.append("OOS阶段未通过")
        return OOSStageResult(
            passed=passed,
            oos_sharpe=oos_f,
            is_sharpe=is_f,
            oos_is_ratio=oos_is_ratio,
            params_locked=bool(params_locked),
            reasons=reasons,
        )

    def evaluate(
        self,
        is_sharpe: float,
        params: dict,
        param_sensitivity: dict | None,
        walk_forward_results: list[dict],
        oos_sharpe: float,
        params_locked: bool = True,
    ) -> DecisionGateResult:
        """编排3阶段决策门控(IS→WFA→OOS)

        阶段不可跳级:
          - IS未通过 → 不进入WFA(WFA/OOS标记为跳过)
          - WFA未通过 → 不进入OOS(OOS标记为跳过)

        Args:
            is_sharpe: 样本内Sharpe比率
            params: 最优参数字典
            param_sensitivity: 参数敏感性扫描结果(可为None)
            walk_forward_results: Walk-Forward窗口结果列表
            oos_sharpe: 样本外Sharpe比率
            params_locked: 参数是否已锁定

        Returns:
            DecisionGateResult: 三阶段综合判定结果
        """
        # 阶段1: IS
        is_result = self.check_is_stage(is_sharpe, params, param_sensitivity)
        aggregate_reasons: list[str] = list(is_result.reasons)

        if not is_result.passed:
            # IS未通过,不进入WFA和OOS(不可跳级)
            wfa_result = WFAStageResult(
                passed=False,
                windows_total=0,
                windows_passed=0,
                has_disaster=False,
                reasons=["跳过:IS阶段未通过,不进入WFA阶段"],
            )
            oos_result = OOSStageResult(
                passed=False,
                oos_sharpe=0.0,
                is_sharpe=is_result.sharpe,
                oos_is_ratio=0.0,
                params_locked=params_locked,
                reasons=["跳过:IS阶段未通过,不进入OOS阶段"],
            )
            aggregate_reasons.append("IS阶段未通过,后续阶段跳过")
            return DecisionGateResult(
                is_stage=is_result,
                wfa_stage=wfa_result,
                oos_stage=oos_result,
                overall_passed=False,
                can_deploy=False,
                reasons=aggregate_reasons,
            )

        # 阶段2: WFA
        wfa_result = self.check_wfa_stage(walk_forward_results)
        aggregate_reasons.extend(wfa_result.reasons)

        if not wfa_result.passed:
            # WFA未通过,不进入OOS(不可跳级)
            oos_result = OOSStageResult(
                passed=False,
                oos_sharpe=0.0,
                is_sharpe=is_result.sharpe,
                oos_is_ratio=0.0,
                params_locked=params_locked,
                reasons=["跳过:WFA阶段未通过,不进入OOS阶段"],
            )
            aggregate_reasons.append("WFA阶段未通过,后续阶段跳过")
            return DecisionGateResult(
                is_stage=is_result,
                wfa_stage=wfa_result,
                oos_stage=oos_result,
                overall_passed=False,
                can_deploy=False,
                reasons=aggregate_reasons,
            )

        # 阶段3: OOS
        oos_result = self.check_oos_stage(is_result.sharpe, oos_sharpe, params_locked)
        aggregate_reasons.extend(oos_result.reasons)

        overall_passed = oos_result.passed
        # 技术门控通过即可上线标志为True,正式上线仍需人工审批
        can_deploy = overall_passed
        if overall_passed:
            aggregate_reasons.append("三阶段全部通过,可上线(需人工审批)")
        else:
            aggregate_reasons.append("OOS阶段未通过,不可上线")
        return DecisionGateResult(
            is_stage=is_result,
            wfa_stage=wfa_result,
            oos_stage=oos_result,
            overall_passed=overall_passed,
            can_deploy=can_deploy,
            reasons=aggregate_reasons,
        )

    def check_stability_plateau(
        self,
        param_name: str,
        param_values: list[tuple[Any, float]],
    ) -> dict:
        """检查参数稳定性区域(稳定高原/悬崖型参数)

        算法:
          - 以Sharpe最大的参数值为高原中心(center_value)
          - 稳定高原:center附近±10%范围内Sharpe相对变化<容忍度(默认20%)
          - 悬崖型参数:center相邻参数的Sharpe下降>阈值(默认50%)
          - ±10%窗口内扫描点不足时,回退到center的相邻扫描点进行判定

        Args:
            param_name: 参数名(仅用于提示)
            param_values: 参数扫描结果,元素为(参数值, Sharpe)

        Returns:
            dict: {
                "is_plateau": bool, 是否处于稳定高原,
                "is_cliff": bool, 是否为悬崖型参数,
                "center_value": Any, 高原中心参数值,
                "reason": str, 判定原因,
            }

        Raises:
            DecisionGateError: param_values非列表或元素结构非法
        """
        if not isinstance(param_values, list):
            raise DecisionGateError(
                f"参数{param_name}的param_values必须是列表: "
                f"{type(param_values).__name__}"
            )
        if len(param_values) == 0:
            return {
                "is_plateau": False,
                "is_cliff": False,
                "center_value": None,
                "reason": f"参数{param_name}扫描数据为空",
            }

        # 校验元素结构并转为(value, float(sharpe))
        points: list[tuple[Any, float]] = []
        for item in param_values:
            if not (isinstance(item, tuple) and len(item) == 2):
                raise DecisionGateError(
                    f"参数{param_name}的扫描点必须是(value, sharpe)二元组: {item!r}"
                )
            try:
                points.append((item[0], float(item[1])))
            except (TypeError, ValueError) as exc:
                raise DecisionGateError(
                    f"参数{param_name}的sharpe非数值: {item[1]!r}"
                ) from exc

        # 找高原中心(Sharpe最大的点)
        center_idx = max(range(len(points)), key=lambda i: points[i][1])
        center_value, center_sharpe = points[center_idx]

        if len(points) < 2:
            return {
                "is_plateau": False,
                "is_cliff": False,
                "center_value": center_value,
                "reason": f"参数{param_name}扫描点不足(仅1点),无法判定高原",
            }

        # 按参数值排序(数值型可排序;非数值型保持原序)
        try:
            sorted_points = sorted(points, key=lambda x: x[0])
        except TypeError:
            sorted_points = list(points)
        # 重新定位center在排序后的位置
        center_sorted_idx = max(
            range(len(sorted_points)), key=lambda i: sorted_points[i][1]
        )

        # 收集±10%窗口内的点(仅数值型center)
        window_points: list[tuple[Any, float]] = []
        if isinstance(center_value, (int, float)) and not isinstance(center_value, bool):
            lo = center_value * 0.9
            hi = center_value * 1.1
            for v, s in sorted_points:
                if (
                    isinstance(v, (int, float))
                    and not isinstance(v, bool)
                    and lo <= v <= hi
                ):
                    window_points.append((v, s))

        # 窗口内点不足时,回退到center的相邻扫描点
        if len(window_points) < 2:
            window_points = [(center_value, center_sharpe)]
            if center_sorted_idx > 0:
                window_points.append(sorted_points[center_sorted_idx - 1])
            if center_sorted_idx < len(sorted_points) - 1:
                window_points.append(sorted_points[center_sorted_idx + 1])

        # 稳定高原判定:窗口内Sharpe相对变化
        if len(window_points) < 2:
            return {
                "is_plateau": False,
                "is_cliff": False,
                "center_value": center_value,
                "reason": f"参数{param_name}相邻扫描点不足,无法判定高原",
            }

        sharpes = [s for _, s in window_points]
        max_s = max(sharpes)
        min_s = min(sharpes)
        if max_s <= 0:
            is_plateau = False
            plateau_detail = "窗口内Sharpe均<=0"
        else:
            rel_change = (max_s - min_s) / max_s
            is_plateau = rel_change < self.config.stability_plateau_tolerance
            plateau_detail = (
                f"窗口内Sharpe相对变化={rel_change:.4f} "
                f"(容忍度{self.config.stability_plateau_tolerance})"
            )

        # 悬崖型参数判定:center相邻点的Sharpe下降是否超阈值
        is_cliff = False
        cliff_detail = ""
        if center_sharpe > 0:
            for neighbor_idx in (
                center_sorted_idx - 1,
                center_sorted_idx + 1,
            ):
                if 0 <= neighbor_idx < len(sorted_points):
                    neighbor_sharpe = sorted_points[neighbor_idx][1]
                    drop = (center_sharpe - neighbor_sharpe) / center_sharpe
                    if drop > self.config.cliff_sharpe_drop:
                        is_cliff = True
                        cliff_detail = (
                            f"相邻参数Sharpe下降{drop:.2%}超过悬崖阈值"
                            f"{self.config.cliff_sharpe_drop:.0%}"
                        )
                        break

        # 综合原因
        if is_cliff:
            reason = f"参数{param_name}为悬崖型参数: {cliff_detail}"
        elif is_plateau:
            reason = f"参数{param_name}处于稳定高原: {plateau_detail}"
        else:
            reason = f"参数{param_name}非稳定高原: {plateau_detail}"

        return {
            "is_plateau": is_plateau,
            "is_cliff": is_cliff,
            "center_value": center_value,
            "reason": reason,
        }

    def monitor_backtest_live_deviation(
        self,
        backtest_sharpe: float,
        live_sharpe: float,
    ) -> dict:
        """监控回测-实盘Sharpe偏差

        偏差 = |backtest_sharpe - live_sharpe| / |backtest_sharpe|
          - 偏差 > backtest_live_deviation_warn(默认30%) → 告警
          - 偏差 > backtest_live_deviation_retire(默认50%) → 退役

        Args:
            backtest_sharpe: 回测Sharpe比率
            live_sharpe: 实盘Sharpe比率

        Returns:
            dict: {"deviation": float, "action": "ok"|"warn"|"retire"}

        Raises:
            DecisionGateError: backtest_sharpe非数值或为0(无法计算相对偏差)
        """
        try:
            bt = float(backtest_sharpe)
            lv = float(live_sharpe)
        except (TypeError, ValueError) as exc:
            raise DecisionGateError(
                f"backtest_sharpe/live_sharpe必须是数值: "
                f"{backtest_sharpe!r}, {live_sharpe!r}"
            ) from exc
        if bt == 0:
            raise DecisionGateError("backtest_sharpe为0,无法计算相对偏差")

        deviation = abs(bt - lv) / abs(bt)
        # 先判高阈值(退役),再判低阈值(告警)
        if deviation > self.config.backtest_live_deviation_retire:
            action = "retire"
        elif deviation > self.config.backtest_live_deviation_warn:
            action = "warn"
        else:
            action = "ok"
        return {"deviation": deviation, "action": action}


__all__ = [
    "DecisionGate",
    "DecisionGateConfig",
    "DecisionGateError",
    "DecisionGateResult",
    "ISStageResult",
    "OOSStageResult",
    "WFAStageResult",
]
