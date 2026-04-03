"""
监管合规检查模块
基于2026年4月7日量化监管新政的合规检查实现

技术层次: Layer 5 - 策略执行层 | 业务架构: 三级时间框架融合架构
监管依据:
    1. 证监会《关于短线交易监管的若干规定》(2026-04-07施行)
    2. 沪深北交易所《程序化交易管理实施细则》(2025-07-07施行)

核心功能:
    1. 高频交易认定检查
    2. 撤单限制检查
    3. 异常交易行为监控
    4. 短线交易合规检查
    5. 程序化交易报告管理
"""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """合规级别"""
    COMPLIANT = "compliant"              # 完全合规
    WARNING = "warning"                  # 警告（接近限制）
    VIOLATION = "violation"              # 违规
    CRITICAL_VIOLATION = "critical"      # 严重违规


class TradingBehaviorType(Enum):
    """交易行为类型"""
    NORMAL = "normal"                    # 正常交易
    HIGH_FREQUENCY = "high_frequency"    # 高频交易
    ABNORMAL = "abnormal"                # 异常交易


@dataclass
class OrderRecord:
    """订单记录"""
    order_id: str
    symbol: str
    direction: str                       # 'buy' or 'sell'
    quantity: int
    price: float
    order_type: str                      # 'limit', 'market', etc.
    timestamp: datetime
    status: str                          # 'submitted', 'filled', 'cancelled', 'rejected'
    cancel_time: Optional[datetime] = None
    fill_time: Optional[datetime] = None
    duration_microseconds: Optional[int] = None


@dataclass
class ComplianceCheckResult:
    """合规检查结果"""
    is_compliant: bool
    compliance_level: ComplianceLevel
    behavior_type: TradingBehaviorType
    triggered_rules: List[str]
    warnings: List[str]
    violations: List[str]
    details: Dict
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'is_compliant': self.is_compliant,
            'compliance_level': self.compliance_level.value,
            'behavior_type': self.behavior_type.value,
            'triggered_rules': self.triggered_rules,
            'warnings': self.warnings,
            'violations': self.violations,
            'details': self.details,
            'recommendations': self.recommendations
        }


class RegulatoryConfig:
    """监管配置
    
    基于2026年4月7日量化监管新政的监管参数
    """
    
    def __init__(self):
        self.high_frequency_criteria = {
            'per_second_threshold': 300,        # 每秒申报+撤单≥300笔
            'per_day_threshold': 20000,         # 单日申报+撤单≥20000笔
            'stricter_standard': {
                'per_second': 15,                # 更严格标准：每秒15笔
                'cancel_rate_per_day': 0.15      # 单日撤单率≤15%
            }
        }
        
        self.cancel_order_limits = {
            'max_cancel_per_second': 15,         # 每秒撤单≤15笔
            'max_cancel_rate_per_day': 0.15,     # 单日撤单率≤15%
            'min_order_duration_microseconds': 50,  # 订单停留≥50微秒
        }
        
        self.abnormal_trading_thresholds = {
            'instant_order_rate': {
                'per_second': 300,                # 瞬时申报速率异常阈值
            },
            'frequent_instant_cancel': {
                'cancel_rate': 0.15,              # 频繁瞬时撤单阈值
                'instant_cancel_count': 10        # 瞬时撤单次数
            },
            'frequent_lift_suppress': {
                'price_change_pct': 0.02,         # 价格变动阈值2%
                'occurrence_count': 5             # 发生次数
            },
            'short_time_large_volume': {
                'time_window_minutes': 30,        # 时间窗口30分钟
                'volume_multiplier': 5            # 成交量倍数
            }
        }
        
        self.short_term_trading_rules = {
            'lock_period_months': 6,              # 6个月锁仓期
            'major_shareholder_threshold': 0.05,  # 5%大股东认定
            'penetration_enabled': True           # 穿透监管启用
        }
        
        self.reporting_requirements = {
            'account_basic_info': True,
            'account_fund_info': True,
            'account_trading_info': True,
            'trading_software_info': True,
            'contact_info': True
        }


class OrderTracker:
    """订单跟踪器
    
    跟踪订单流，统计申报、撤单等数据
    """
    
    def __init__(self):
        self.orders: Dict[str, OrderRecord] = {}
        self.second_window: Dict[int, List[OrderRecord]] = defaultdict(list)
        self.daily_stats = {
            'total_orders': 0,
            'total_cancels': 0,
            'total_fills': 0,
            'order_count_per_second': defaultdict(int),
            'cancel_count_per_second': defaultdict(int),
        }
        
    def add_order(self, order: OrderRecord):
        """添加订单"""
        self.orders[order.order_id] = order
        second_timestamp = int(order.timestamp.timestamp())
        self.second_window[second_timestamp].append(order)
        self.daily_stats['total_orders'] += 1
        self.daily_stats['order_count_per_second'][second_timestamp] += 1
        
    def record_cancel(self, order_id: str, cancel_time: datetime):
        """记录撤单"""
        if order_id in self.orders:
            order = self.orders[order_id]
            order.status = 'cancelled'
            order.cancel_time = cancel_time
            order.duration_microseconds = int(
                (cancel_time - order.timestamp).total_seconds() * 1_000_000
            )
            
            second_timestamp = int(cancel_time.timestamp())
            self.daily_stats['total_cancels'] += 1
            self.daily_stats['cancel_count_per_second'][second_timestamp] += 1
            
    def get_second_stats(self, second_timestamp: int) -> Dict:
        """获取某一秒的统计数据"""
        orders_in_second = self.second_window.get(second_timestamp, [])
        order_count = self.daily_stats['order_count_per_second'].get(second_timestamp, 0)
        cancel_count = self.daily_stats['cancel_count_per_second'].get(second_timestamp, 0)
        
        return {
            'order_count': order_count,
            'cancel_count': cancel_count,
            'total_count': order_count + cancel_count,
            'orders': orders_in_second
        }
    
    def get_daily_stats(self) -> Dict:
        """获取当日统计数据"""
        cancel_rate = (
            self.daily_stats['total_cancels'] / self.daily_stats['total_orders']
            if self.daily_stats['total_orders'] > 0 else 0
        )
        
        max_orders_per_second = max(
            self.daily_stats['order_count_per_second'].values()
        ) if self.daily_stats['order_count_per_second'] else 0
        
        max_cancels_per_second = max(
            self.daily_stats['cancel_count_per_second'].values()
        ) if self.daily_stats['cancel_count_per_second'] else 0
        
        max_total_per_second = max_orders_per_second + max_cancels_per_second
        
        return {
            'total_orders': self.daily_stats['total_orders'],
            'total_cancels': self.daily_stats['total_cancels'],
            'total_fills': self.daily_stats['total_fills'],
            'cancel_rate': cancel_rate,
            'max_orders_per_second': max_orders_per_second,
            'max_cancels_per_second': max_cancels_per_second,
            'max_total_per_second': max_total_per_second,
        }
    
    def reset_daily(self):
        """重置每日统计"""
        self.orders.clear()
        self.second_window.clear()
        self.daily_stats = {
            'total_orders': 0,
            'total_cancels': 0,
            'total_fills': 0,
            'order_count_per_second': defaultdict(int),
            'cancel_count_per_second': defaultdict(int),
        }


class ComplianceChecker:
    """监管合规检查器
    
    核心合规检查功能实现
    """
    
    def __init__(self, config: Optional[RegulatoryConfig] = None):
        self.config = config or RegulatoryConfig()
        self.order_tracker = OrderTracker()
        self.compliance_history: List[ComplianceCheckResult] = []
        
    def check_high_frequency_trading(self) -> ComplianceCheckResult:
        """检查是否触发高频交易认定
        
        Returns:
            ComplianceCheckResult: 合规检查结果
        """
        daily_stats = self.order_tracker.get_daily_stats()
        
        triggered_rules = []
        warnings = []
        violations = []
        details = {
            'daily_stats': daily_stats,
            'thresholds': self.config.high_frequency_criteria
        }
        
        is_high_freq = False
        compliance_level = ComplianceLevel.COMPLIANT
        
        per_second_total = daily_stats['max_total_per_second']
        per_day_total = daily_stats['total_orders'] + daily_stats['total_cancels']
        
        if per_second_total >= self.config.high_frequency_criteria['per_second_threshold']:
            is_high_freq = True
            violations.append(
                f"触发高频交易认定：每秒申报+撤单{per_second_total}笔，"
                f"超过阈值{self.config.high_frequency_criteria['per_second_threshold']}笔"
            )
            triggered_rules.append('high_frequency_per_second')
            compliance_level = ComplianceLevel.VIOLATION
            
        if per_day_total >= self.config.high_frequency_criteria['per_day_threshold']:
            is_high_freq = True
            violations.append(
                f"触发高频交易认定：单日申报+撤单{per_day_total}笔，"
                f"超过阈值{self.config.high_frequency_criteria['per_day_threshold']}笔"
            )
            triggered_rules.append('high_frequency_per_day')
            compliance_level = ComplianceLevel.VIOLATION
        
        stricter_second = self.config.high_frequency_criteria['stricter_standard']['per_second']
        if per_second_total >= stricter_second:
            warnings.append(
                f"警告：每秒申报+撤单{per_second_total}笔，"
                f"接近更严格标准{stricter_second}笔"
            )
            if compliance_level == ComplianceLevel.COMPLIANT:
                compliance_level = ComplianceLevel.WARNING
        
        behavior_type = (
            TradingBehaviorType.HIGH_FREQUENCY 
            if is_high_freq else TradingBehaviorType.NORMAL
        )
        
        recommendations = []
        if is_high_freq:
            recommendations.extend([
                "降低交易频率，避免高频交易认定",
                "优化策略，减少不必要的申报和撤单",
                "考虑使用智能执行算法（VWAP/TWAP）降低交易速率"
            ])
        
        return ComplianceCheckResult(
            is_compliant=not is_high_freq,
            compliance_level=compliance_level,
            behavior_type=behavior_type,
            triggered_rules=triggered_rules,
            warnings=warnings,
            violations=violations,
            details=details,
            recommendations=recommendations
        )
    
    def check_cancel_limits(self) -> ComplianceCheckResult:
        """检查撤单限制
        
        Returns:
            ComplianceCheckResult: 合规检查结果
        """
        daily_stats = self.order_tracker.get_daily_stats()
        
        triggered_rules = []
        warnings = []
        violations = []
        details = {
            'daily_stats': daily_stats,
            'limits': self.config.cancel_order_limits
        }
        
        is_compliant = True
        compliance_level = ComplianceLevel.COMPLIANT
        
        max_cancels_per_second = daily_stats['max_cancels_per_second']
        cancel_rate = daily_stats['cancel_rate']
        
        if max_cancels_per_second > self.config.cancel_order_limits['max_cancel_per_second']:
            is_compliant = False
            violations.append(
                f"违规：每秒撤单{max_cancels_per_second}笔，"
                f"超过限制{self.config.cancel_order_limits['max_cancel_per_second']}笔"
            )
            triggered_rules.append('cancel_per_second_limit')
            compliance_level = ComplianceLevel.VIOLATION
        
        if cancel_rate > self.config.cancel_order_limits['max_cancel_rate_per_day']:
            is_compliant = False
            violations.append(
                f"违规：单日撤单率{cancel_rate:.2%}，"
                f"超过限制{self.config.cancel_order_limits['max_cancel_rate_per_day']:.2%}"
            )
            triggered_rules.append('cancel_rate_limit')
            compliance_level = ComplianceLevel.VIOLATION
        
        if cancel_rate > self.config.cancel_order_limits['max_cancel_rate_per_day'] * 0.8:
            warnings.append(
                f"警告：单日撤单率{cancel_rate:.2%}，"
                f"接近限制{self.config.cancel_order_limits['max_cancel_rate_per_day']:.2%}"
            )
            if compliance_level == ComplianceLevel.COMPLIANT:
                compliance_level = ComplianceLevel.WARNING
        
        recommendations = []
        if not is_compliant:
            recommendations.extend([
                "减少不必要的撤单操作",
                "优化订单价格，提高成交率",
                "使用限价单而非市价单，减少撤单需求"
            ])
        
        return ComplianceCheckResult(
            is_compliant=is_compliant,
            compliance_level=compliance_level,
            behavior_type=TradingBehaviorType.NORMAL,
            triggered_rules=triggered_rules,
            warnings=warnings,
            violations=violations,
            details=details,
            recommendations=recommendations
        )
    
    def check_order_duration(self, order: OrderRecord) -> ComplianceCheckResult:
        """检查订单停留时间
        
        Args:
            order: 订单记录
            
        Returns:
            ComplianceCheckResult: 合规检查结果
        """
        if order.duration_microseconds is None:
            return ComplianceCheckResult(
                is_compliant=True,
                compliance_level=ComplianceLevel.COMPLIANT,
                behavior_type=TradingBehaviorType.NORMAL,
                triggered_rules=[],
                warnings=[],
                violations=[],
                details={'message': '订单未撤单，无需检查停留时间'}
            )
        
        min_duration = self.config.cancel_order_limits['min_order_duration_microseconds']
        is_compliant = order.duration_microseconds >= min_duration
        
        violations = []
        warnings = []
        triggered_rules = []
        
        if not is_compliant:
            violations.append(
                f"违规：订单停留时间{order.duration_microseconds}微秒，"
                f"低于最小要求{min_duration}微秒"
            )
            triggered_rules.append('min_order_duration')
        
        return ComplianceCheckResult(
            is_compliant=is_compliant,
            compliance_level=(
                ComplianceLevel.VIOLATION if not is_compliant 
                else ComplianceLevel.COMPLIANT
            ),
            behavior_type=TradingBehaviorType.NORMAL,
            triggered_rules=triggered_rules,
            warnings=warnings,
            violations=violations,
            details={
                'order_id': order.order_id,
                'duration_microseconds': order.duration_microseconds,
                'min_duration': min_duration
            },
            recommendations=['延长订单停留时间，避免秒挂秒撤'] if not is_compliant else []
        )
    
    def check_short_term_trading(
        self, 
        symbol: str, 
        position_pct: float,
        is_buy: bool,
        last_trade_date: Optional[datetime] = None
    ) -> ComplianceCheckResult:
        """检查短线交易合规性
        
        Args:
            symbol: 股票代码
            position_pct: 持仓比例
            is_buy: 是否为买入
            last_trade_date: 上次交易日期
            
        Returns:
            ComplianceCheckResult: 合规检查结果
        """
        triggered_rules = []
        warnings = []
        violations = []
        details = {
            'symbol': symbol,
            'position_pct': position_pct,
            'is_buy': is_buy,
            'last_trade_date': last_trade_date
        }
        
        is_compliant = True
        compliance_level = ComplianceLevel.COMPLIANT
        
        if position_pct >= self.config.short_term_trading_rules['major_shareholder_threshold']:
            if last_trade_date:
                lock_period_months = self.config.short_term_trading_rules['lock_period_months']
                lock_period_end = last_trade_date + timedelta(days=lock_period_months * 30)
                
                if datetime.now() < lock_period_end:
                    is_compliant = False
                    violations.append(
                        f"违规：作为大股东（持股{position_pct:.2%}），"
                        f"在{lock_period_end.strftime('%Y-%m-%d')}前不得进行反向交易"
                    )
                    triggered_rules.append('short_term_trading_lock')
                    compliance_level = ComplianceLevel.CRITICAL_VIOLATION
                else:
                    warnings.append(
                        f"注意：作为大股东（持股{position_pct:.2%}），"
                        f"需遵守6个月锁仓期规定"
                    )
                    compliance_level = ComplianceLevel.WARNING
            else:
                warnings.append(
                    f"注意：作为大股东（持股{position_pct:.2%}），"
                    f"需遵守6个月锁仓期规定"
                )
                compliance_level = ComplianceLevel.WARNING
        
        recommendations = []
        if not is_compliant:
            recommendations.extend([
                "等待6个月锁仓期结束后再进行反向交易",
                "如需交易，请咨询合规部门",
                "考虑调整持仓比例至5%以下"
            ])
        
        return ComplianceCheckResult(
            is_compliant=is_compliant,
            compliance_level=compliance_level,
            behavior_type=TradingBehaviorType.NORMAL,
            triggered_rules=triggered_rules,
            warnings=warnings,
            violations=violations,
            details=details,
            recommendations=recommendations
        )
    
    def check_abnormal_trading(self) -> ComplianceCheckResult:
        """检查异常交易行为
        
        Returns:
            ComplianceCheckResult: 合规检查结果
        """
        triggered_rules = []
        warnings = []
        violations = []
        details = {}
        
        is_compliant = True
        compliance_level = ComplianceLevel.COMPLIANT
        behavior_type = TradingBehaviorType.NORMAL
        
        hf_result = self.check_high_frequency_trading()
        if not hf_result.is_compliant:
            is_compliant = False
            triggered_rules.extend(hf_result.triggered_rules)
            violations.extend(hf_result.violations)
            compliance_level = hf_result.compliance_level
            behavior_type = TradingBehaviorType.HIGH_FREQUENCY
        
        cancel_result = self.check_cancel_limits()
        if not cancel_result.is_compliant:
            is_compliant = False
            triggered_rules.extend(cancel_result.triggered_rules)
            violations.extend(cancel_result.violations)
            if compliance_level != ComplianceLevel.CRITICAL_VIOLATION:
                compliance_level = cancel_result.compliance_level
        
        warnings.extend(hf_result.warnings)
        warnings.extend(cancel_result.warnings)
        
        details['high_frequency_check'] = hf_result.to_dict()
        details['cancel_limit_check'] = cancel_result.to_dict()
        
        if not is_compliant:
            behavior_type = TradingBehaviorType.ABNORMAL
        
        return ComplianceCheckResult(
            is_compliant=is_compliant,
            compliance_level=compliance_level,
            behavior_type=behavior_type,
            triggered_rules=triggered_rules,
            warnings=warnings,
            violations=violations,
            details=details,
            recommendations=list(set(
                hf_result.recommendations + cancel_result.recommendations
            ))
        )
    
    def check_order_before_submission(
        self, 
        order: OrderRecord,
        position_pct: float = 0.0,
        last_trade_date: Optional[datetime] = None
    ) -> ComplianceCheckResult:
        """订单提交前合规检查
        
        Args:
            order: 订单记录
            position_pct: 持仓比例
            last_trade_date: 上次交易日期
            
        Returns:
            ComplianceCheckResult: 合规检查结果
        """
        self.order_tracker.add_order(order)
        
        results = []
        
        hf_check = self.check_high_frequency_trading()
        results.append(hf_check)
        
        cancel_check = self.check_cancel_limits()
        results.append(cancel_check)
        
        stt_check = self.check_short_term_trading(
            order.symbol, 
            position_pct, 
            order.direction == 'buy',
            last_trade_date
        )
        results.append(stt_check)
        
        is_compliant = all(r.is_compliant for r in results)
        compliance_level = max((r.compliance_level for r in results), key=lambda x: x.value)
        triggered_rules = [rule for r in results for rule in r.triggered_rules]
        warnings = [w for r in results for w in r.warnings]
        violations = [v for r in results for v in r.violations]
        details = {
            'order_id': order.order_id,
            'checks': {f'check_{i}': r.to_dict() for i, r in enumerate(results)}
        }
        recommendations = list(set(rec for r in results for rec in r.recommendations))
        
        result = ComplianceCheckResult(
            is_compliant=is_compliant,
            compliance_level=compliance_level,
            behavior_type=TradingBehaviorType.NORMAL,
            triggered_rules=triggered_rules,
            warnings=warnings,
            violations=violations,
            details=details,
            recommendations=recommendations
        )
        
        self.compliance_history.append(result)
        
        return result
    
    def generate_compliance_report(self) -> Dict:
        """生成合规报告
        
        Returns:
            Dict: 合规报告
        """
        daily_stats = self.order_tracker.get_daily_stats()
        abnormal_check = self.check_abnormal_trading()
        
        total_checks = len(self.compliance_history)
        compliant_checks = sum(1 for r in self.compliance_history if r.is_compliant)
        warning_checks = sum(
            1 for r in self.compliance_history 
            if r.compliance_level == ComplianceLevel.WARNING
        )
        violation_checks = sum(
            1 for r in self.compliance_history 
            if r.compliance_level in [ComplianceLevel.VIOLATION, ComplianceLevel.CRITICAL_VIOLATION]
        )
        
        return {
            'report_time': datetime.now().isoformat(),
            'daily_statistics': daily_stats,
            'compliance_summary': {
                'total_checks': total_checks,
                'compliant_checks': compliant_checks,
                'warning_checks': warning_checks,
                'violation_checks': violation_checks,
                'compliance_rate': compliant_checks / total_checks if total_checks > 0 else 1.0
            },
            'current_status': abnormal_check.to_dict(),
            'recommendations': abnormal_check.recommendations
        }
    
    def reset_daily(self):
        """重置每日数据"""
        self.order_tracker.reset_daily()
        self.compliance_history.clear()
        logger.info("合规检查器每日数据已重置")


def create_compliance_checker(config: Optional[Dict] = None) -> ComplianceChecker:
    """创建合规检查器
    
    Args:
        config: 配置字典（可选）
        
    Returns:
        ComplianceChecker: 合规检查器实例
    """
    regulatory_config = RegulatoryConfig()
    if config:
        if 'high_frequency_criteria' in config:
            regulatory_config.high_frequency_criteria.update(config['high_frequency_criteria'])
        if 'cancel_order_limits' in config:
            regulatory_config.cancel_order_limits.update(config['cancel_order_limits'])
        if 'short_term_trading_rules' in config:
            regulatory_config.short_term_trading_rules.update(config['short_term_trading_rules'])
    
    return ComplianceChecker(regulatory_config)
