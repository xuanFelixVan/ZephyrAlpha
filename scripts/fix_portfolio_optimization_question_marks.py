#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 PORTFOLIO_OPTIMIZATION_BLUEPRINT.md 中残留的 '?' 断字（一次性替换表）。"""

from __future__ import annotations

import pathlib

FP = pathlib.Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_OPTIMIZATION_BLUEPRINT.md")

PAIRS: list[tuple[str, str]] = [
    ("## 三、核心组件详细设?", "## 三、核心组件详细设计"),
    ("### 3.1 组合优化控制器（PortfolioOptimizationController?", "### 3.1 组合优化控制器（PortfolioOptimizationController）"),
    ("    组合优化控制?- 负责调度不同的优化算法，管理优化流程", "    组合优化控制器 — 负责调度不同的优化算法，管理优化流程"),
    (
        "        Args:\n含策略列表、绩效数据、约束条件等\n            \n        Returns:",
        "        Args:\n            optimization_request: 含策略列表、绩效数据、约束条件等\n\n        Returns:",
    ),
    ("        # 1. 数据准备与验?", "        # 1. 数据准备与验证"),
    ("        # 4. 应用交易成本与流动性约?", "        # 4. 应用交易成本与流动性约束"),
    ("            # 从批量评估结果中获取策略的历史收益序?", "            # 从批量评估结果中获取策略的历史收益序列"),
    ("    使用PyPortfolioOpt库实?", "    使用 PyPortfolioOpt 库实现"),
    ("            cov_matrix: 协方差矩?", "            cov_matrix: 协方差矩阵"),
    ("            pd.Series: 最优权重分?", "            pd.Series: 最优权重分布"),
    ("        # 使用PyPortfolioOpt?", "        # 使用 PyPortfolioOpt 求解"),
    ("        # ¸", "        # 清理数值噪声权重"),
    ("        绘制有效前沿?", "        绘制有效前沿图"),
    ("            ax.scatter(vol, ret, marker='*', s=200, c='r', label='最优组?)", "            ax.scatter(vol, ret, marker='*', s=200, c='r', label='最优组合')"),
    ("### 3.3 风险平价优化器（RiskParityOptimizer?", "### 3.3 风险平价优化器（RiskParityOptimizer）"),
    ("    使用Riskfolio-Lib库实?", "    使用 Riskfolio-Lib 库实现"),
    ("        self.risk_measure = risk_measure  # CVaR, VaR, CDaR, EDaR?", "        self.risk_measure = risk_measure  # CVaR, VaR, CDaR, EDaR 等"),
    ("            returns: 策略收益数据?", "            returns: 策略收益数据框"),
    ("            rf=0,  # 无风险利?", "            rf=0,  # 无风险利率"),
    ("        计算各策略的风险贡献?", "        计算各策略的风险贡献度"),
    ("        # 权重分布?", "        # 权重分布图"),
    ("        ax2.set_title('风险贡献度分?)", "        ax2.set_title('风险贡献度分布')"),
    ("        ax2.set_ylabel('风险贡献?)", "        ax2.set_ylabel('风险贡献度')"),
    ("### 3.4 约束处理器（ConstraintProcessor?", "### 3.4 约束处理器（ConstraintProcessor）"),
    ("    约束处理?- 处理各种实盘约束条件", "    约束处理器 — 处理各种实盘约束条件"),
    ("            'liquidity_constraint', # 流动性约?", "            'liquidity_constraint', # 流动性约束"),
    ("            'turnover_limit',      # 换手率限?", "            'turnover_limit',      # 换手率限制"),
    ("        处理单策略仓位限?", "        处理单策略仓位限制"),
    ("        max_position = limit_config.get('max_position', 0.3)  # 默认单策略最大仓?0%", "        max_position = limit_config.get('max_position', 0.3)  # 默认单策略最大仓位 30%"),
    ("        min_position = limit_config.get('min_position', 0.01) # 默认最小仓?%", "        min_position = limit_config.get('min_position', 0.01) # 默认最小仓位 1%"),
    ("        # 应用上下?", "        # 应用上下界"),
    ("        处理流动性约?", "        处理流动性约束"),
    (
        "        portfolio_value = liquidity_config.get('portfolio_value', 1e6)  # 默认组合规模100?",
        "        portfolio_value = liquidity_config.get('portfolio_value', 1e6)  # 默认组合规模（示例）",
    ),
    ("过日成交量的5%?", "超过日成交量的 5%（示例）"),
    ("                if position_value > max_daily_trade * 3:  # ?天建?", "                if position_value > max_daily_trade * 3:  # 多日建仓约束（示例）"),
    ("### 3.5 强化学习调仓器（RLRebalancer?", "### 3.5 强化学习调仓器（RLRebalancer）"),
    ("    强化学习调仓?- 使用强化学习优化动态调仓决?", "    强化学习调仓器 — 使用强化学习优化动态调仓决策"),
    ("        # 使用Stable-Baselines3?", "        # 使用 Stable-Baselines3"),
    ("            historical_data: 历史市场数据和策略表现数?", "            historical_data: 历史市场数据和策略表现数据"),
    ("        # 使用PPO算法（Proximal Policy Optimization?", "        # 使用 PPO 算法（Proximal Policy Optimization）"),
    ("            current_state: 当前状态（市场状态、策略表现、风险指标等?", "            current_state: 当前状态（市场状态、策略表现、风险指标等）"),
    ("        # 市场状态特?", "        # 市场状态特征"),
    ("        # 组合成观察向?", "        # 组合成观察向量"),
    ("            strategy_features[:min(len(strategy_features), 8)],  # 最?个策略特?", "            strategy_features[:min(len(strategy_features), 8)],  # 最多 8 个策略特征"),
    ("## 四、开源模块集成方?", "## 四、开源模块集成方案"),
    ("      description: \"给定风险水平下的最优收?", '      description: "给定风险水平下的最优收益"'),
    ("      description: \"给定收益水平下的最小风?", '      description: "给定收益水平下的最小风险"'),
    ("    weight_bounds: [0.01, 0.3]  # 单策略权重范?%-30%", "    weight_bounds: [0.01, 0.3]  # 单策略权重范围 1%-30%"),
    ("    covariance_estimator: \"sample_cov\"  # 样本协方?", '    covariance_estimator: "sample_cov"  # 样本协方差'),
    ("      description: \"熵在险价?", '      description: "熵在险价值（示例）"'),
    ("        Omega: null  # 观点不确定性矩?", "        Omega: null  # 观点不确定性矩阵"),
    ("### 4.3 CVXPY集成（自定义优化问题?", "### 4.3 CVXPY 集成（自定义优化问题）"),
    ("    最小化回撤优化?- 使用CVXPY求解自定义优化问?", "    最小化回撤优化 — 使用 CVXPY 求解自定义优化问题"),
    ("        # 决策变量：权?", "        # 决策变量：权重向量"),
    ("        # 计算累积收益和回?", "        # 计算累积收益和回撤"),
    ("        # 目标函数：最小化最大回?", "        # 目标函数：最小化最大回撤"),
    ("            w <= 0.3,  # 单资产最大权?0%", "            w <= 0.3,  # 单资产最大权重 30%"),
    ("            cp.norm(w, 0) <= max_positions  # 最多持有max_positions个策?", "            cp.norm(w, 0) <= max_positions  # 最多持有 max_positions 个策略"),
    ("    完整的组合优化流程示?", "    完整的组合优化流程示例"),
    ("    # 1. 从策略选择系统获取已选择的策?", "    # 1. 从策略选择系统获取已选择的策略"),
    ("    # 2. 从批量评估系统获取策略绩效数?", "    # 2. 从批量评估系统获取策略绩效数据"),
    ("        lookback_period=252  # 一年数?", "        lookback_period=252  # 一年交易日（示例）"),
    ("        max_strategy_risk: 0.25  # 单策略最大风险贡献?5%", "        max_strategy_risk: 0.25  # 单策略最大风险贡献 25%（示例）"),
    ("    print(f\"  预期最大回? {result.risk_metrics['max_drawdown']:.2%}\")", "    print(f\"  预期最大回撤 {result.risk_metrics['max_drawdown']:.2%}\")"),
    ("    print(f\"\\n风险贡献?\")", "    print(f\"\\n风险贡献度\")"),
    ("    # 7. 生成可视化报?", "    # 7. 生成可视化报告"),
    ("### 5.2 命令行接口示?", "### 5.2 命令行接口示例"),
    ("# 查看可用的优化方?", "# 查看可用的优化方法"),
]


def main() -> int:
    t = FP.read_text(encoding="utf-8-sig")
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    for a, b in PAIRS:
        t = t.replace(a, b)
    # 孤立行仅含 ? 的常见残留
    lines = []
    for line in t.split("\n"):
        stripped = line.strip()
        if stripped == "?":
            continue
        lines.append(line)
    t = "\n".join(lines)
    if not t.endswith("\n"):
        t += "\n"
    FP.write_bytes(t.encode("utf-8-sig"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
