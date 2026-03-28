# T.08.AI002.ICIR监控

> 信息系数与信息比率实时监控
>
> **策略编号**：T.08.AI002
> **所属模块**：ai-optimization
> **文档类型**：AI监控
> **优先级**：P2
>
> **配套文档**：
> - [T.08.AI001.因子衰减检测.md](./T.08.AI001.因子衰减检测.md) - 因子衰减检测
> - [self-optimization.md](./self-optimization.md) - AI自我优化框架

---

## 1. IC/IR监控理论基础

```python
class ICIRMonitor:
    """
    IC/IR监控器

    核心理论：
    - IC (Information Coefficient): 因子与收益的相关性
    - IR (Information Ratio): IC的稳定性（IC均值/IC标准差）
    - IC decay: 因子预测能力随时间的衰减
    """

    IC_THRESHOLDS = {
        'excellent': 0.08,
        'good': 0.05,
        'acceptable': 0.03,
        'poor': 0.01
    }

    IR_THRESHOLDS = {
        'excellent': 1.0,
        'good': 0.5,
        'acceptable': 0.3,
        'poor': 0.2
    }
```

---

## 2. IC计算与监控

```python
class ICAnalyzer:
    """
    IC分析器
    """

    def __init__(self):
        self.ic_history = []
        self.ic_decay_window = 20

    def calculate_ic(self, factor_values: pd.Series,
                    returns: pd.Series,
                    method: str = 'spearman') -> float:
        """
        计算IC值

        参数:
            factor_values: 因子值
            returns: 收益率
            method: 'spearman' 或 'pearson'

        返回:
            ic_value: IC值
        """
        if method == 'spearman':
            return factor_values.corr(returns, method='spearman')
        else:
            return factor_values.corr(returns, method='pearson')

    def calculate_ic_series(self, factor_data: pd.DataFrame,
                           return_data: pd.Series,
                           window: int = 20,
                           method: str = 'spearman') -> pd.Series:
        """
        计算滚动IC序列

        参数:
            factor_data: 因子数据（多因子DataFrame）
            return_data: 收益率序列
            window: 滚动窗口
            method: 相关系数计算方法

        返回:
            ic_series: IC序列
        """
        ic_series_dict = {}

        for col in factor_data.columns:
            ic_values = []
            for i in range(window, len(factor_data)):
                factor_window = factor_data[col].iloc[i-window:i]
                return_window = return_data.iloc[i-window:i]

                ic = self.calculate_ic(factor_window, return_window, method)
                ic_values.append(ic)

            ic_series_dict[col] = pd.Series(ic_values, index=factor_data.index[window:])

        return pd.DataFrame(ic_series_dict)

    def calculate_ic_decay(self, ic_series: pd.Series) -> pd.Series:
        """
        计算IC衰减

        参数:
            ic_series: IC序列

        返回:
            ic_decay: IC衰减序列
        """
        ic_cumsum = ic_series.cumsum()
        n = len(ic_series)

        ic_decay = pd.Series(index=ic_series.index)

        for i in range(1, n + 1):
            ic_decay.iloc[i-1] = ic_cumsum.iloc[i-1] / i

        return ic_decay

    def evaluate_ic_quality(self, ic_series: pd.Series) -> dict:
        """
        评估IC质量

        参数:
            ic_series: IC序列

        返回:
            quality_report: 质量报告
        """
        ic_mean = ic_series.mean()
        ic_std = ic_series.std()
        ic_ir = ic_mean / ic_std if ic_std > 0 else 0

        ic_positive_rate = (ic_series > 0).mean()

        ic_cumulative = ic_series.cumsum()
        rolling_ic = ic_series.rolling(20).mean()

        recent_ic = ic_series.iloc[-20:].mean()
        early_ic = ic_series.iloc[:20].mean()

        decay_rate = (early_ic - recent_ic) / early_ic if early_ic != 0 else 0

        return {
            'ic_mean': round(ic_mean, 4),
            'ic_std': round(ic_std, 4),
            'ir': round(ic_ir, 4),
            'positive_rate': round(ic_positive_rate, 4),
            'recent_ic': round(recent_ic, 4),
            'early_ic': round(early_ic, 4),
            'decay_rate': round(decay_rate, 4),
            'quality_grade': self.get_quality_grade(ic_ir, ic_positive_rate, decay_rate)
        }

    def get_quality_grade(self, ir: float, positive_rate: float,
                         decay_rate: float) -> str:
        """
        质量评级
        """
        score = 0

        if ir >= 0.5:
            score += 3
        elif ir >= 0.3:
            score += 2
        elif ir >= 0.1:
            score += 1

        if positive_rate >= 0.6:
            score += 2
        elif positive_rate >= 0.5:
            score += 1

        if decay_rate < 0.2:
            score += 2
        elif decay_rate < 0.4:
            score += 1

        if score >= 6:
            return 'A (优秀)'
        elif score >= 4:
            return 'B (良好)'
        elif score >= 2:
            return 'C (一般)'
        else:
            return 'D (较差)'
```

---

## 3. IR计算与监控

```python
class IRAnalyzer:
    """
    IR分析器
    """

    def __init__(self):
        self.ir_history = []

    def calculate_ir(self, ic_series: pd.Series,
                    lookback: int = 60) -> float:
        """
        计算IR（信息比率）

        IR = IC均值 / IC标准差

        参数:
            ic_series: IC序列
            lookback: 回溯期

        返回:
            ir: IR值
        """
        ic_window = ic_series.iloc[-lookback:]
        ic_mean = ic_window.mean()
        ic_std = ic_window.std()

        return ic_mean / ic_std if ic_std > 0 else 0

    def calculate_rolling_ir(self, ic_series: pd.Series,
                           window: int = 60) -> pd.Series:
        """
        计算滚动IR序列

        参数:
            ic_series: IC序列
            window: 滚动窗口

        返回:
            rolling_ir: 滚动IR序列
        """
        rolling_mean = ic_series.rolling(window).mean()
        rolling_std = ic_series.rolling(window).std()

        rolling_ir = rolling_mean / rolling_std
        rolling_ir = rolling_ir.replace([np.inf, -np.inf], np.nan)

        return rolling_ir

    def detect_ir_breakdown(self, ir_series: pd.Series,
                          threshold: float = 0.3) -> list:
        """
        检测IR失效

        参数:
            ir_series: IR序列
            threshold: 失效阈值

        返回:
            breakdowns: 失效点列表
        """
        breakdowns = []

        for i in range(20, len(ir_series)):
            if ir_series.iloc[i] < threshold:
                if i == 0 or ir_series.iloc[i-1] >= threshold:
                    breakdowns.append({
                        'date': ir_series.index[i] if hasattr(ir_series, 'index') else i,
                        'ir_value': round(ir_series.iloc[i], 4),
                        'severity': '严重' if ir_series.iloc[i] < 0.1 else '轻微'
                    })

        return breakdowns

    def evaluate_ir_trend(self, ir_series: pd.Series) -> dict:
        """
        评估IR趋势

        参数:
            ir_series: IR序列

        返回:
            trend_report: 趋势报告
        """
        recent_ir = ir_series.iloc[-20:].mean()
        earlier_ir = ir_series.iloc[-60:-20].mean() if len(ir_series) >= 60 else recent_ir

        ir_trend = '稳定' if abs(recent_ir - earlier_ir) < 0.1 else \
                   '上升' if recent_ir > earlier_ir else '下降'

        ir_volatility = ir_series.iloc[-20:].std()

        return {
            'recent_ir': round(recent_ir, 4),
            'earlier_ir': round(earlier_ir, 4),
            'trend': ir_trend,
            'volatility': round(ir_volatility, 4),
            'interpretation': self.interpret_ir(recent_ir)
        }

    def interpret_ir(self, ir: float) -> str:
        """
        解读IR值
        """
        if ir >= 1.0:
            return '极高稳定性，优秀'
        elif ir >= 0.5:
            return '较高稳定性，良好'
        elif ir >= 0.3:
            return '一般稳定性，可接受'
        elif ir >= 0.1:
            return '低稳定性，需关注'
        else:
            return '极低稳定性，建议替换'
```

---

## 4. IC/IR综合监控

```python
class ICIRComprehensiveMonitor:
    """
    IC/IR综合监控器
    """

    def __init__(self):
        self.ic_analyzer = ICAnalyzer()
        self.ir_analyzer = IRAnalyzer()
        self.alert_thresholds = {
            'ic_warning': 0.03,
            'ic_critical': 0.01,
            'ir_warning': 0.3,
            'ir_critical': 0.1
        }

    def generate_monitoring_report(self, factor_name: str,
                                 factor_data: pd.Series,
                                 return_data: pd.Series) -> dict:
        """
        生成综合监控报告

        参数:
            factor_name: 因子名称
            factor_data: 因子数据
            return_data: 收益率数据

        返回:
            monitoring_report: 监控报告
        """
        ic_series = self.ic_analyzer.calculate_ic_series(
            factor_data.to_frame(),
            return_data,
            window=20
        )[factor_name]

        ir_series = self.ir_analyzer.calculate_rolling_ir(ic_series)

        ic_quality = self.ic_analyzer.evaluate_ic_quality(ic_series)

        ir_trend = self.ir_analyzer.evaluate_ir_trend(ir_series)

        alerts = self.generate_alerts(ic_series, ir_series)

        recommendations = self.get_recommendations(
            ic_quality, ir_trend, alerts
        )

        return {
            'factor_name': factor_name,
            'ic_analysis': {
                'mean_ic': ic_quality['ic_mean'],
                'ic_std': ic_quality['ic_std'],
                'ir': ic_quality['ir'],
                'positive_rate': ic_quality['positive_rate'],
                'quality_grade': ic_quality['quality_grade']
            },
            'ir_analysis': {
                'recent_ir': ir_trend['recent_ir'],
                'trend': ir_trend['trend'],
                'volatility': ir_trend['volatility'],
                'interpretation': ir_trend['interpretation']
            },
            'alerts': alerts,
            'recommendations': recommendations,
            'report_timestamp': pd.Timestamp.now()
        }

    def generate_alerts(self, ic_series: pd.Series,
                      ir_series: pd.Series) -> list:
        """
        生成预警

        参数:
            ic_series: IC序列
            ir_series: IR序列

        返回:
            alerts: 预警列表
        """
        alerts = []

        recent_ic = ic_series.iloc[-20:].mean()
        if recent_ic < self.alert_thresholds['ic_critical']:
            alerts.append({
                'level': 'critical',
                'type': 'IC失效',
                'message': f'IC均值{recent_ic:.4f}低于临界值{self.alert_thresholds["ic_critical"]}',
                'action': '立即替换因子'
            })
        elif recent_ic < self.alert_thresholds['ic_warning']:
            alerts.append({
                'level': 'warning',
                'type': 'IC偏低',
                'message': f'IC均值{recent_ic:.4f}低于警戒线{self.alert_thresholds["ic_warning"]}',
                'action': '密切关注，准备替换'
            })

        recent_ir = ir_series.iloc[-20:].mean()
        if recent_ir < self.alert_thresholds['ir_critical']:
            alerts.append({
                'level': 'critical',
                'type': 'IR失效',
                'message': f'IR{recent_ir:.4f}低于临界值{self.alert_thresholds["ir_critical"]}',
                'action': '因子稳定性丧失，建议替换'
            })
        elif recent_ir < self.alert_thresholds['ir_warning']:
            alerts.append({
                'level': 'warning',
                'type': 'IR下降',
                'message': f'IR{recent_ir:.4f}低于警戒线{self.alert_thresholds["ir_warning"]}',
                'action': '关注衰减趋势'
            })

        ic_negative_rate = (ic_series.iloc[-20:] < 0).mean()
        if ic_negative_rate > 0.4:
            alerts.append({
                'level': 'warning',
                'type': 'IC负值率偏高',
                'message': f'近20日IC负值率{ic_negative_rate:.1%}',
                'action': '检查因子逻辑'
            })

        return alerts

    def get_recommendations(self, ic_quality: dict,
                           ir_trend: dict,
                           alerts: list) -> list:
        """
        获取建议
        """
        recommendations = []

        if ic_quality['quality_grade'] in ['A (优秀)', 'B (良好)']:
            recommendations.append('因子质量良好，可继续使用')

        if ic_quality['decay_rate'] > 0.3:
            recommendations.append('因子存在明显衰减，建议降低权重')

        if ir_trend['trend'] == '下降':
            recommendations.append('IR呈下降趋势，需密切关注')

        if any(alert['level'] == 'critical' for alert in alerts):
            recommendations.append('存在严重预警，建议立即替换因子')

        if not recommendations:
            recommendations.append('继续监控，维持当前配置')

        return recommendations

    def plot_icir_dashboard(self, ic_series: pd.Series,
                          ir_series: pd.Series) -> dict:
        """
        生成IC/IR监控看板数据

        返回:
            dashboard_data: 看扳数据
        """
        return {
            'ic_series': ic_series.to_dict(),
            'ir_series': ir_series.to_dict(),
            'ic_ma5': ic_series.rolling(5).mean().to_dict(),
            'ic_ma20': ic_series.rolling(20).mean().to_dict(),
            'ir_ma20': ir_series.rolling(20).mean().to_dict()
        }
```

---

## 5. 实时IC监控脚本

```python
class RealTimeICIRMonitor:
    """
    实时IC/IR监控脚本
    """

    def __init__(self, data_source, alert_callback=None):
        self.data_source = data_source
        self.alert_callback = alert_callback
        self.comprehensive_monitor = ICIRComprehensiveMonitor()
        self.factors_to_monitor = []
        self.monitoring_interval = 60

    def add_factor(self, factor_name: str, factor_data: pd.Series):
        """
        添加监控因子
        """
        self.factors_to_monitor.append({
            'name': factor_name,
            'data': factor_data
        })

    def run_monitoring_cycle(self):
        """
        运行一个监控周期
        """
        results = []

        return_data = self.data_source.get_latest_returns()

        for factor_info in self.factors_to_monitor:
            factor_name = factor_info['name']
            factor_data = factor_info['data']

            latest_factor = self.data_source.get_latest_factor(factor_name)

            factor_data = pd.concat([factor_data, latest_factor])

            report = self.comprehensive_monitor.generate_monitoring_report(
                factor_name,
                factor_data,
                return_data
            )

            results.append(report)

            if report['alerts']:
                self.handle_alerts(report)

        return results

    def handle_alerts(self, report: dict):
        """
        处理预警
        """
        if self.alert_callback:
            for alert in report['alerts']:
                self.alert_callback(report['factor_name'], alert)

    def start_monitoring(self):
        """
        启动监控
        """
        while True:
            try:
                self.run_monitoring_cycle()
                time.sleep(self.monitoring_interval)
            except KeyboardInterrupt:
                print("监控已停止")
                break
            except Exception as e:
                print(f"监控异常: {e}")
                time.sleep(60)
```

---

## 6. 使用示例

```python
def example_icir_monitoring():
    """
    IC/IR监控示例
    """
    monitor = ICIRComprehensiveMonitor()

    factor_data = pd.read_csv('factor_data.csv', index_col=0)
    return_data = pd.read_csv('returns.csv', index_col=0)['return']

    for factor_name in factor_data.columns:
        report = monitor.generate_monitoring_report(
            factor_name,
            factor_data[factor_name],
            return_data
        )

        print(f"\n因子: {factor_name}")
        print(f"IC均值: {report['ic_analysis']['mean_ic']:.4f}")
        print(f"IR: {report['ic_analysis']['ir']:.4f}")
        print(f"质量评级: {report['ic_analysis']['quality_grade']}")

        if report['alerts']:
            print("\n预警:")
            for alert in report['alerts']:
                print(f"  [{alert['level']}] {alert['message']}")

        print(f"建议: {report['recommendations']}")
```

---

## 7. IC/IR阈值速查表

| IC范围 | 评级 | IR范围 | 评级 | 操作建议 |
|--------|------|--------|------|----------|
| ≥0.08 | 优秀 | ≥1.0 | 极高 | 重点使用 |
| 0.05-0.08 | 良好 | 0.5-1.0 | 较高 | 正常使用 |
| 0.03-0.05 | 一般 | 0.3-0.5 | 一般 | 辅助使用 |
| 0.01-0.03 | 较差 | 0.1-0.3 | 低 | 降低权重 |
| <0.01 | 失效 | <0.1 | 极低 | 立即替换 |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 新建ICIR监控文档 |
