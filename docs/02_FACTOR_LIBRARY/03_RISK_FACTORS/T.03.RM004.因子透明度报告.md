# T.03.RM004.因子透明度报告

> 因子暴露透明度报告生成器
>
> **来源**：量化策略专业分层方案_v3.0 附录AJ
>
> **配套文档**：
> - Barra风格因子：[1_Barra风格因子.md](./1_Barra风格因子.md)
> - Barra优化器：[T.03.RM003.Barra优化器.md](./T.03.RM003.Barra优化器.md)

---

## 1. 因子暴露度报告

### 1.1 报告生成器

```python
class FactorExposureReport:
    """
    因子暴露度报告
    生成组合的因子暴露透明度报告，用于合规和风控
    """

    def __init__(self, portfolio_name: str = "默认组合"):
        self.portfolio_name = portfolio_name

    def generate_report(self, portfolio_weights: pd.Series,
                      factor_exposures: pd.DataFrame) -> dict:
        """
        生成因子暴露报告

        Parameters:
            portfolio_weights: 持仓权重，index为股票代码
            factor_exposures: 因子暴露度，columns为因子名

        Returns:
            dict: 报告内容
        """
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'portfolio_name': self.portfolio_name,
            'total_positions': len(portfolio_weights),
            'factor_exposure_summary': self.calc_summary(factor_exposures, portfolio_weights),
            'top_exposures': self.get_top_exposures(factor_exposures, portfolio_weights),
            'risk_contribution': self.calc_risk_contribution(factor_exposures, portfolio_weights),
            'compliance_check': self.check_constraints(factor_exposures, portfolio_weights),
        }

        return report

    def calc_summary(self, factor_exposures: pd.DataFrame,
                   weights: pd.Series) -> dict:
        """
        计算因子暴露汇总
        """
        summary = {}
        for factor in factor_exposures.columns:
            exposure = (factor_exposures[factor] * weights).sum()
            abs_exposure = (factor_exposures[factor].abs() * weights).sum()

            summary[factor] = {
                'net_exposure': float(exposure),
                'abs_exposure': float(abs_exposure),
                'active': abs(exposure) > 0.1
            }

        return summary

    def get_top_exposures(self, factor_exposures: pd.DataFrame,
                         weights: pd.Series, top_n: int = 5) -> list:
        """
        获取最大暴露的股票
        """
        top_stocks = []
        for factor in factor_exposures.columns:
            exposure_with_weight = factor_exposures[factor] * weights.abs()
            top_indices = exposure_with_weight.nlargest(top_n).index.tolist()

            for stock in top_indices:
                top_stocks.append({
                    'factor': factor,
                    'stock': stock,
                    'exposure': float(factor_exposures.loc[stock, factor]),
                    'weight': float(weights[stock])
                })

        return sorted(top_stocks, key=lambda x: abs(x['exposure']), reverse=True)[:top_n]

    def calc_risk_contribution(self, factor_exposures: pd.DataFrame,
                             weights: pd.Series) -> dict:
        """
        计算因子风险贡献
        """
        factor_vol = {
            'SIZE': 0.15,
            'VALUE': 0.12,
            'MOM': 0.18,
            'QUAL': 0.10,
            'VOL': 0.14,
            'GROW': 0.16,
            'EARN': 0.13,
            'LEVER': 0.08,
            'LIQUID': 0.11,
            'YIELD': 0.09
        }

        risk_contrib = {}
        for factor in factor_exposures.columns:
            exposure = (factor_exposures[factor] * weights).sum()
            vol = factor_vol.get(factor, 0.15)
            risk_contrib[factor] = float(exposure * vol)

        return risk_contrib

    def check_constraints(self, factor_exposures: pd.DataFrame,
                         weights: pd.Series) -> dict:
        """
        检查约束合规性
        """
        constraints = {
            'SIZE': {'max': 0.3, 'type': 'max'},
            'MOM': {'max': 0.5, 'type': 'max'},
            'VALUE': {'min': 0.1, 'type': 'min'},
            'LIQUID': {'min': 0.05, 'type': 'min'},
        }

        violations = []
        for factor, limit in constraints.items():
            if factor not in factor_exposures.columns:
                continue

            exposure = (factor_exposures[factor] * weights).sum()

            if limit['type'] == 'max':
                if abs(exposure) > limit['max']:
                    violations.append({
                        'factor': factor,
                        'exposure': float(exposure),
                        'limit': limit['max'],
                        'status': 'violation'
                    })
            elif limit['type'] == 'min':
                if abs(exposure) < limit['min']:
                    violations.append({
                        'factor': factor,
                        'exposure': float(exposure),
                        'limit': limit['min'],
                        'status': 'violation'
                    })

        return {
            'violations': violations,
            'is_compliant': len(violations) == 0
        }
```

### 1.2 报告输出格式化

```python
def generate_transparency_report(portfolio_weights: pd.Series,
                                 factor_exposures: pd.DataFrame,
                                 portfolio_name: str = "默认组合") -> str:
    """
    生成透明度报告

    Parameters:
        portfolio_weights: 持仓权重
        factor_exposures: 因子暴露度
        portfolio_name: 组合名称

    Returns:
        str: 格式化的报告文本
    """
    report = FactorExposureReport(portfolio_name).generate_report(
        portfolio_weights, factor_exposures
    )

    output = f"""
========================================
因子暴露透明度报告
========================================
报告日期: {report['report_date']}
组合名称: {report['portfolio_name']}
持仓数量: {report['total_positions']}

----------------------------------------
因子暴露汇总
----------------------------------------
因子       | 净暴露    | 绝对暴露  | 状态
----------------------------------------
"""

    for factor, data in report['factor_exposure_summary'].items():
        status = '⚠️显著' if data['active'] else '✅正常'
        output += f"{factor:10} | {data['net_exposure']:+.2%}  | {data['abs_exposure']:.2%}   | {status}\n"

    output += """
----------------------------------------
因子风险贡献
----------------------------------------
"""
    for factor, risk in sorted(report['risk_contribution'].items(),
                              key=lambda x: -abs(x[1])):
        output += f"{factor:10} : {risk:.2%}\n"

    compliance = report['compliance_check']
    if not compliance['is_compliant']:
        output += "\n⚠️违规项:\n"
        for v in compliance['violations']:
            output += f"  - {v['factor']}: {v['exposure']:.2%} (限{v['limit']:.2%})\n"
    else:
        output += "\n✅ 所有约束合规\n"

    return output
```

---

## 2. 组合透明度JSON输出

```python
def generate_json_report(portfolio_weights: pd.Series,
                        factor_exposures: pd.DataFrame,
                        portfolio_name: str = "默认组合") -> dict:
    """
    生成JSON格式的报告

    Returns:
        dict: 结构化报告
    """
    report_gen = FactorExposureReport(portfolio_name)
    report = report_gen.generate_report(portfolio_weights, factor_exposures)

    return {
        'metadata': {
            'report_date': report['report_date'],
            'portfolio_name': report['portfolio_name'],
            'total_positions': report['total_positions']
        },
        'factor_exposures': report['factor_exposure_summary'],
        'top_exposures': report['top_exposures'],
        'risk_contribution': report['risk_contribution'],
        'compliance': {
            'is_compliant': report['compliance_check']['is_compliant'],
            'violations': report['compliance_check']['violations']
        }
    }
```

---

## 3. 使用示例

```python
import pandas as pd
import numpy as np

# 示例持仓
stocks = ['000001', '000002', '000333', '600519', '600036']
weights = pd.Series([0.2, 0.15, 0.25, 0.3, 0.1], index=stocks)

# 示例因子暴露
factors = ['SIZE', 'VALUE', 'MOM', 'QUAL', 'VOL']
exposures = pd.DataFrame(
    np.random.randn(5, 5) * 0.3,
    index=stocks,
    columns=factors
)

# 生成报告
report = generate_transparency_report(weights, exposures, "测试组合")
print(report)

# JSON格式
json_report = generate_json_report(weights, exposures, "测试组合")
print(json_report)
```

---

## 4. 因子暴露约束

### 4.1 默认约束规则

| 因子 | 约束类型 | 限制值 | 说明 |
|------|----------|--------|------|
| SIZE | max | 0.30 | 规模因子暴露不超过30% |
| MOM | max | 0.50 | 动量因子暴露不超过50% |
| VALUE | min | 0.10 | 价值因子暴露至少10% |
| LIQUID | min | 0.05 | 流动性因子暴露至少5% |
| LEVER | max | 0.20 | 杠杆因子暴露不超过20% |

### 4.2 自定义约束

```python
class ConstraintManager:
    """
    约束管理器
    """

    DEFAULT_CONSTRAINTS = {
        'SIZE': {'max': 0.3, 'type': 'max'},
        'VALUE': {'min': 0.1, 'type': 'min'},
        'MOM': {'max': 0.5, 'type': 'max'},
        'QUAL': {'min': 0.05, 'type': 'min'},
        'VOL': {'max': 0.4, 'type': 'max'},
        'GROW': {'min': 0.0, 'type': 'min'},
        'EARN': {'min': 0.0, 'type': 'min'},
        'LEVER': {'max': 0.2, 'type': 'max'},
        'LIQUID': {'min': 0.05, 'type': 'min'},
        'YIELD': {'min': 0.0, 'type': 'min'},
    }

    def __init__(self, custom_constraints: dict = None):
        self.constraints = self.DEFAULT_CONSTRAINTS.copy()
        if custom_constraints:
            self.constraints.update(custom_constraints)

    def check(self, factor_exposures: pd.DataFrame,
              weights: pd.Series) -> list:
        """
        检查所有约束
        """
        violations = []
        for factor, limit in self.constraints.items():
            if factor not in factor_exposures.columns:
                continue

            exposure = (factor_exposures[factor] * weights).sum()

            if limit['type'] == 'max':
                if abs(exposure) > limit['max']:
                    violations.append({
                        'factor': factor,
                        'exposure': float(exposure),
                        'limit': limit['max'],
                        'type': 'max'
                    })
            elif limit['type'] == 'min':
                if abs(exposure) < limit['min']:
                    violations.append({
                        'factor': factor,
                        'exposure': float(exposure),
                        'limit': limit['min'],
                        'type': 'min'
                    })

        return violations
```

---

## 5. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合附录AJ因子暴露透明度报告 |
