#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
清风量化系统 - 实施复杂度计算工具

功能: 计算技术方案的实施复杂度，包括架构复杂度、集成复杂度、维护复杂度、测试复杂度等
版本: v1.0
创建日期: 2026-04-02
维护者: 审批智能体 (Spec-Approver)

使用方法:
    python scripts/implementation_complexity_calculator.py [--verbose] [--report] [--input PATH] [--score-only]

参数:
    --verbose    : 显示详细计算过程
    --report     : 生成详细的复杂度分析报告
    --input PATH : 指定输入文件（蓝图或技术规格书）
    --score-only : 只输出综合复杂度评分（0-100分）
    --help       : 显示帮助信息

复杂度维度:
1. 架构复杂度 (权重: 30%)
   - 系统组件数量
   - 组件间依赖关系复杂度
   - 架构模式复杂度
   - 部署拓扑复杂度
2. 集成复杂度 (权重: 25%)
   - 外部系统集成数量
   - 集成接口复杂度
   - 数据格式转换复杂度
   - 集成测试复杂度
3. 维护复杂度 (权重: 25%)
   - 代码复杂度
   - 配置管理复杂度
   - 监控运维复杂度
   - 故障排查复杂度
4. 测试复杂度 (权重: 20%)
   - 测试用例数量
   - 测试环境复杂度
   - 自动化测试复杂度
   - 性能测试复杂度

复杂度等级:
- 低复杂度 (0-30分): 简单系统，易于实施和维护
- 中等复杂度 (31-60分): 中等规模系统，需要一定专业知识和经验
- 高复杂度 (61-80分): 复杂系统，需要专业团队和详细规划
- 极高复杂度 (81-100分): 极其复杂系统，实施风险高，需要专家团队
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import yaml

@dataclass
class ArchitectureComplexity:
    """架构复杂度"""
    component_count: int = 0
    dependency_complexity: float = 0.0  # 0-10分
    pattern_complexity: float = 0.0     # 0-10分
    deployment_complexity: float = 0.0  # 0-10分
    
    def calculate_score(self) -> float:
        """计算架构复杂度总分 (0-30分)"""
        # 组件数量评分 (0-10分)
        component_score = min(10.0, self.component_count / 5.0)
        
        total = (component_score + 
                self.dependency_complexity + 
                self.pattern_complexity + 
                self.deployment_complexity)
        
        return min(30.0, total)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_count": self.component_count,
            "dependency_complexity": self.dependency_complexity,
            "pattern_complexity": self.pattern_complexity,
            "deployment_complexity": self.deployment_complexity,
            "total_score": self.calculate_score()
        }


@dataclass
class IntegrationComplexity:
    """集成复杂度"""
    external_system_count: int = 0
    interface_complexity: float = 0.0    # 0-10分
    data_format_complexity: float = 0.0  # 0-10分
    testing_complexity: float = 0.0      # 0-10分
    
    def calculate_score(self) -> float:
        """计算集成复杂度总分 (0-25分)"""
        # 外部系统数量评分 (0-10分)
        system_score = min(10.0, self.external_system_count * 2.0)
        
        total = (system_score + 
                self.interface_complexity + 
                self.data_format_complexity + 
                self.testing_complexity)
        
        return min(25.0, total)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "external_system_count": self.external_system_count,
            "interface_complexity": self.interface_complexity,
            "data_format_complexity": self.data_format_complexity,
            "testing_complexity": self.testing_complexity,
            "total_score": self.calculate_score()
        }


@dataclass
class MaintenanceComplexity:
    """维护复杂度"""
    code_complexity: float = 0.0        # 0-10分
    config_complexity: float = 0.0      # 0-10分
    monitoring_complexity: float = 0.0  # 0-10分
    troubleshooting_complexity: float = 0.0  # 0-10分
    
    def calculate_score(self) -> float:
        """计算维护复杂度总分 (0-25分)"""
        total = (self.code_complexity + 
                self.config_complexity + 
                self.monitoring_complexity + 
                self.troubleshooting_complexity)
        
        return min(25.0, total)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code_complexity": self.code_complexity,
            "config_complexity": self.config_complexity,
            "monitoring_complexity": self.monitoring_complexity,
            "troubleshooting_complexity": self.troubleshooting_complexity,
            "total_score": self.calculate_score()
        }


@dataclass
class TestingComplexity:
    """测试复杂度"""
    test_case_count: int = 0
    environment_complexity: float = 0.0  # 0-10分
    automation_complexity: float = 0.0   # 0-10分
    performance_complexity: float = 0.0  # 0-10分
    
    def calculate_score(self) -> float:
        """计算测试复杂度总分 (0-20分)"""
        # 测试用例数量评分 (0-10分)
        case_score = min(10.0, self.test_case_count / 10.0)
        
        total = (case_score + 
                self.environment_complexity + 
                self.automation_complexity + 
                self.performance_complexity)
        
        return min(20.0, total)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_case_count": self.test_case_count,
            "environment_complexity": self.environment_complexity,
            "automation_complexity": self.automation_complexity,
            "performance_complexity": self.performance_complexity,
            "total_score": self.calculate_score()
        }


@dataclass
class ImplementationComplexityResult:
    """实施复杂度计算结果"""
    file_path: str
    architecture: ArchitectureComplexity
    integration: IntegrationComplexity
    maintenance: MaintenanceComplexity
    testing: TestingComplexity
    analysis_timestamp: str = ""
    
    def __post_init__(self):
        if not self.analysis_timestamp:
            self.analysis_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def calculate_overall_score(self) -> float:
        """计算总体实施复杂度评分 (0-100分)"""
        total = (self.architecture.calculate_score() + 
                self.integration.calculate_score() + 
                self.maintenance.calculate_score() + 
                self.testing.calculate_score())
        
        return min(100.0, total)
    
    def get_complexity_level(self) -> str:
        """根据评分确定复杂度等级"""
        score = self.calculate_overall_score()
        if score <= 30:
            return "低复杂度"
        elif score <= 60:
            return "中等复杂度"
        elif score <= 80:
            return "高复杂度"
        else:
            return "极高复杂度"
    
    def get_implementation_effort(self) -> Tuple[str, int]:
        """估算实施工作量（人天）"""
        score = self.calculate_overall_score()
        
        if score <= 30:
            return "小型项目", 10  # 10人天
        elif score <= 50:
            return "中型项目", 30  # 30人天
        elif score <= 70:
            return "大型项目", 60  # 60人天
        elif score <= 85:
            return "超大型项目", 120  # 120人天
        else:
            return "特大型项目", 200  # 200人天
    
    def get_recommendation(self) -> str:
        """根据复杂度给出实施建议"""
        score = self.calculate_overall_score()
        
        if score <= 30:
            return "[OK] 实施复杂度低，可以由小型团队快速完成"
        elif score <= 60:
            return "[WARNING] 实施复杂度中等，需要专业团队和经验丰富的开发者"
        elif score <= 80:
            return "[WARNING] 实施复杂度高，需要专业团队、详细规划和严格的项目管理"
        else:
            return "[FAIL] 实施复杂度极高，建议分阶段实施或重新评估方案可行性"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        effort_level, effort_days = self.get_implementation_effort()
        
        return {
            "file_path": self.file_path,
            "overall_score": self.calculate_overall_score(),
            "complexity_level": self.get_complexity_level(),
            "implementation_effort_level": effort_level,
            "implementation_effort_days": effort_days,
            "recommendation": self.get_recommendation(),
            "architecture": self.architecture.to_dict(),
            "integration": self.integration.to_dict(),
            "maintenance": self.maintenance.to_dict(),
            "testing": self.testing.to_dict(),
            "analysis_timestamp": self.analysis_timestamp
        }


class ImplementationComplexityCalculator:
    """实施复杂度计算器"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []
        
    def analyze_file(self, file_path: str) -> ImplementationComplexityResult:
        """分析蓝图或技术规格书文件的实施复杂度"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if self.verbose:
            print(f"开始分析实施复杂度: {file_path}")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分析各个复杂度维度
        architecture = self._analyze_architecture_complexity(content)
        integration = self._analyze_integration_complexity(content)
        maintenance = self._analyze_maintenance_complexity(content)
        testing = self._analyze_testing_complexity(content)
        
        # 创建结果对象
        result = ImplementationComplexityResult(
            file_path=file_path,
            architecture=architecture,
            integration=integration,
            maintenance=maintenance,
            testing=testing
        )
        
        self.results.append(result)
        
        if self.verbose:
            print(f"实施复杂度分析完成:")
            print(f"  总体评分: {result.calculate_overall_score():.1f}/100")
            print(f"  复杂度等级: {result.get_complexity_level()}")
            print(f"  实施工作量: {result.get_implementation_effort()[1]}人天")
        
        return result
    
    def _analyze_architecture_complexity(self, content: str) -> ArchitectureComplexity:
        """分析架构复杂度"""
        architecture = ArchitectureComplexity()
        
        # 分析组件数量（通过关键词匹配）
        component_keywords = ["模块", "组件", "服务", "微服务", "函数", "类", "接口"]
        component_count = 0
        
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            for keyword in component_keywords:
                if keyword in line_lower:
                    # 简单计数：每行最多算一个组件
                    component_count += 1
                    break
        
        architecture.component_count = min(50, component_count)  # 限制最大数量
        
        # 分析依赖关系复杂度
        dependency_keywords = ["依赖", "调用", "引用", "导入", "require", "import", "from"]
        dependency_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in dependency_keywords:
                if keyword in line_lower:
                    dependency_count += 1
                    break
        
        architecture.dependency_complexity = min(10.0, dependency_count / 5.0)
        
        # 分析架构模式复杂度
        pattern_keywords = ["微服务", "分布式", "事件驱动", "CQRS", "事件溯源", "六边形", "整洁架构", "洋葱架构"]
        pattern_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in pattern_keywords:
                if keyword in line_lower:
                    pattern_count += 1
                    break
        
        architecture.pattern_complexity = min(10.0, pattern_count * 2.0)
        
        # 分析部署拓扑复杂度
        deployment_keywords = ["集群", "负载均衡", "高可用", "容错", "灾备", "多区域", "多可用区", "云原生"]
        deployment_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in deployment_keywords:
                if keyword in line_lower:
                    deployment_count += 1
                    break
        
        architecture.deployment_complexity = min(10.0, deployment_count * 2.0)
        
        if self.verbose:
            print(f"  架构复杂度: 组件={architecture.component_count}, "
                  f"依赖={architecture.dependency_complexity:.1f}, "
                  f"模式={architecture.pattern_complexity:.1f}, "
                  f"部署={architecture.deployment_complexity:.1f}")
        
        return architecture
    
    def _analyze_integration_complexity(self, content: str) -> IntegrationComplexity:
        """分析集成复杂度"""
        integration = IntegrationComplexity()
        
        # 分析外部系统数量
        external_keywords = ["API", "接口", "SDK", "第三方", "外部系统", "集成", "连接", "对接"]
        external_count = 0
        
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            for keyword in external_keywords:
                if keyword in line_lower:
                    external_count += 1
                    break
        
        integration.external_system_count = min(20, external_count)  # 限制最大数量
        
        # 分析接口复杂度
        interface_keywords = ["REST", "GraphQL", "gRPC", "WebSocket", "消息队列", "Kafka", "RabbitMQ", "协议"]
        interface_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in interface_keywords:
                if keyword in line_lower:
                    interface_count += 1
                    break
        
        integration.interface_complexity = min(10.0, interface_count * 2.0)
        
        # 分析数据格式复杂度
        data_format_keywords = ["JSON", "XML", "Protobuf", "Avro", "Thrift", "序列化", "反序列化", "格式转换"]
        data_format_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in data_format_keywords:
                if keyword in line_lower:
                    data_format_count += 1
                    break
        
        integration.data_format_complexity = min(10.0, data_format_count * 2.0)
        
        # 分析集成测试复杂度
        integration_test_keywords = ["集成测试", "端到端测试", "接口测试", "联调", "联测", "对接测试"]
        integration_test_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in integration_test_keywords:
                if keyword in line_lower:
                    integration_test_count += 1
                    break
        
        integration.testing_complexity = min(10.0, integration_test_count * 2.0)
        
        if self.verbose:
            print(f"  集成复杂度: 外部系统={integration.external_system_count}, "
                  f"接口={integration.interface_complexity:.1f}, "
                  f"数据格式={integration.data_format_complexity:.1f}, "
                  f"测试={integration.testing_complexity:.1f}")
        
        return integration
    
    def _analyze_maintenance_complexity(self, content: str) -> MaintenanceComplexity:
        """分析维护复杂度"""
        maintenance = MaintenanceComplexity()
        
        # 分析代码复杂度
        code_keywords = ["复杂度", "圈复杂度", "代码质量", "重构", "技术债务", "遗留代码", "代码审查"]
        code_count = 0
        
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            for keyword in code_keywords:
                if keyword in line_lower:
                    code_count += 1
                    break
        
        maintenance.code_complexity = min(10.0, code_count * 2.0)
        
        # 分析配置管理复杂度
        config_keywords = ["配置", "环境变量", "配置文件", "密钥管理", "配置中心", "动态配置", "配置更新"]
        config_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in config_keywords:
                if keyword in line_lower:
                    config_count += 1
                    break
        
        maintenance.config_complexity = min(10.0, config_count * 2.0)
        
        # 分析监控运维复杂度
        monitoring_keywords = ["监控", "告警", "日志", "指标", "仪表盘", "性能监控", "可用性", "SLA"]
        monitoring_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in monitoring_keywords:
                if keyword in line_lower:
                    monitoring_count += 1
                    break
        
        maintenance.monitoring_complexity = min(10.0, monitoring_count * 2.0)
        
        # 分析故障排查复杂度
        troubleshooting_keywords = ["故障", "排查", "诊断", "调试", "问题定位", "根因分析", "故障恢复"]
        troubleshooting_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in troubleshooting_keywords:
                if keyword in line_lower:
                    troubleshooting_count += 1
                    break
        
        maintenance.troubleshooting_complexity = min(10.0, troubleshooting_count * 2.0)
        
        if self.verbose:
            print(f"  维护复杂度: 代码={maintenance.code_complexity:.1f}, "
                  f"配置={maintenance.config_complexity:.1f}, "
                  f"监控={maintenance.monitoring_complexity:.1f}, "
                  f"故障排查={maintenance.troubleshooting_complexity:.1f}")
        
        return maintenance
    
    def _analyze_testing_complexity(self, content: str) -> TestingComplexity:
        """分析测试复杂度"""
        testing = TestingComplexity()
        
        # 分析测试用例数量
        test_case_keywords = ["测试用例", "测试场景", "测试数据", "测试步骤", "预期结果", "断言"]
        test_case_count = 0
        
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            for keyword in test_case_keywords:
                if keyword in line_lower:
                    test_case_count += 1
                    break
        
        testing.test_case_count = min(100, test_case_count * 5)  # 估算
        
        # 分析测试环境复杂度
        environment_keywords = ["测试环境", "预生产", "沙箱", "隔离环境", "环境配置", "环境部署"]
        environment_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in environment_keywords:
                if keyword in line_lower:
                    environment_count += 1
                    break
        
        testing.environment_complexity = min(10.0, environment_count * 2.0)
        
        # 分析自动化测试复杂度
        automation_keywords = ["自动化测试", "CI/CD", "持续集成", "持续部署", "测试自动化", "自动化脚本"]
        automation_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in automation_keywords:
                if keyword in line_lower:
                    automation_count += 1
                    break
        
        testing.automation_complexity = min(10.0, automation_count * 2.0)
        
        # 分析性能测试复杂度
        performance_keywords = ["性能测试", "压力测试", "负载测试", "并发测试", "响应时间", "吞吐量", "性能基准"]
        performance_count = 0
        
        for line in lines:
            line_lower = line.lower()
            for keyword in performance_keywords:
                if keyword in line_lower:
                    performance_count += 1
                    break
        
        testing.performance_complexity = min(10.0, performance_count * 2.0)
        
        if self.verbose:
            print(f"  测试复杂度: 测试用例={testing.test_case_count}, "
                  f"环境={testing.environment_complexity:.1f}, "
                  f"自动化={testing.automation_complexity:.1f}, "
                  f"性能={testing.performance_complexity:.1f}")
        
        return testing
    
    def generate_report(self, result: ImplementationComplexityResult) -> str:
        """生成实施复杂度分析报告"""
        report = []
        report.append("=" * 80)
        report.append("实施复杂度分析报告")
        report.append("=" * 80)
        report.append(f"分析文件: {result.file_path}")
        report.append(f"分析时间: {result.analysis_timestamp}")
        report.append("")
        
        report.append("1. 总体评估结果")
        report.append("-" * 40)
        report.append(f"综合复杂度评分: {result.calculate_overall_score():.1f}/100")
        report.append(f"复杂度等级: {result.get_complexity_level()}")
        effort_level, effort_days = result.get_implementation_effort()
        report.append(f"估算实施工作量: {effort_level} ({effort_days}人天)")
        report.append(f"实施建议: {result.get_recommendation()}")
        report.append("")
        
        report.append("2. 详细复杂度分析")
        report.append("-" * 40)
        
        # 架构复杂度
        arch = result.architecture
        report.append("2.1 架构复杂度分析 (权重: 30%)")
        report.append(f"  • 系统组件数量: {arch.component_count}个")
        report.append(f"  • 组件间依赖关系复杂度: {arch.dependency_complexity:.1f}/10")
        report.append(f"  • 架构模式复杂度: {arch.pattern_complexity:.1f}/10")
        report.append(f"  • 部署拓扑复杂度: {arch.deployment_complexity:.1f}/10")
        report.append(f"  • 小计: {arch.calculate_score():.1f}/30")
        report.append("")
        
        # 集成复杂度
        integ = result.integration
        report.append("2.2 集成复杂度分析 (权重: 25%)")
        report.append(f"  • 外部系统集成数量: {integ.external_system_count}个")
        report.append(f"  • 集成接口复杂度: {integ.interface_complexity:.1f}/10")
        report.append(f"  • 数据格式转换复杂度: {integ.data_format_complexity:.1f}/10")
        report.append(f"  • 集成测试复杂度: {integ.testing_complexity:.1f}/10")
        report.append(f"  • 小计: {integ.calculate_score():.1f}/25")
        report.append("")
        
        # 维护复杂度
        maint = result.maintenance
        report.append("2.3 维护复杂度分析 (权重: 25%)")
        report.append(f"  • 代码复杂度: {maint.code_complexity:.1f}/10")
        report.append(f"  • 配置管理复杂度: {maint.config_complexity:.1f}/10")
        report.append(f"  • 监控运维复杂度: {maint.monitoring_complexity:.1f}/10")
        report.append(f"  • 故障排查复杂度: {maint.troubleshooting_complexity:.1f}/10")
        report.append(f"  • 小计: {maint.calculate_score():.1f}/25")
        report.append("")
        
        # 测试复杂度
        test = result.testing
        report.append("2.4 测试复杂度分析 (权重: 20%)")
        report.append(f"  • 测试用例数量: {test.test_case_count}个 (估算)")
        report.append(f"  • 测试环境复杂度: {test.environment_complexity:.1f}/10")
        report.append(f"  • 自动化测试复杂度: {test.automation_complexity:.1f}/10")
        report.append(f"  • 性能测试复杂度: {test.performance_complexity:.1f}/10")
        report.append(f"  • 小计: {test.calculate_score():.1f}/20")
        report.append("")
        
        report.append("3. 复杂度热点分析")
        report.append("-" * 40)
        
        # 识别复杂度热点
        hotspots = []
        
        if arch.calculate_score() > 20:
            hotspots.append("架构复杂度较高 - 考虑简化架构设计")
        if integ.calculate_score() > 15:
            hotspots.append("集成复杂度较高 - 减少外部依赖或使用标准化接口")
        if maint.calculate_score() > 15:
            hotspots.append("维护复杂度较高 - 加强代码质量和运维自动化")
        if test.calculate_score() > 12:
            hotspots.append("测试复杂度较高 - 优化测试策略和自动化")
        
        if hotspots:
            report.append("发现以下复杂度热点:")
            for hotspot in hotspots:
                report.append(f"  • {hotspot}")
        else:
            report.append("未发现明显的复杂度热点，复杂度分布较为均衡")
        
        report.append("")
        
        report.append("4. 优化建议")
        report.append("-" * 40)
        
        score = result.calculate_overall_score()
        
        if score <= 30:
            report.append("[OK] 优化建议:")
            report.append("  • 保持当前设计，按计划实施")
            report.append("  • 关注实施细节，确保质量")
            report.append("  • 建立简单的监控和运维机制")
        elif score <= 60:
            report.append("[WARNING] 优化建议:")
            report.append("  • 简化复杂模块的设计")
            report.append("  • 优先实施核心功能，分阶段推进")
            report.append("  • 加强团队技术培训和知识分享")
            report.append("  • 建立完善的项目管理机制")
        elif score <= 80:
            report.append("[WARNING] 优化建议:")
            report.append("  • 重新评估技术方案可行性")
            report.append("  • 考虑分拆为多个独立子系统")
            report.append("  • 引入专业架构师进行设计评审")
            report.append("  • 制定详细的项目计划和风险管理")
            report.append("  • 建立专业的运维团队和流程")
        else:
            report.append("[FAIL] 优化建议:")
            report.append("  • 强烈建议重新设计技术方案")
            report.append("  • 考虑采用更成熟稳定的技术栈")
            report.append("  • 分阶段实施，先验证核心功能")
            report.append("  • 引入外部专家进行技术咨询")
            report.append("  • 制定详细的风险应对计划")
        
        report.append("")
        report.append("5. 实施策略建议")
        report.append("-" * 40)
        
        if score <= 40:
            report.append("推荐实施策略: 敏捷开发")
            report.append("  • 采用短周期迭代开发")
            report.append("  • 快速交付可用版本")
            report.append("  • 持续收集用户反馈")
            report.append("  • 灵活调整开发计划")
        elif score <= 70:
            report.append("推荐实施策略: 混合模式")
            report.append("  • 核心模块采用瀑布式开发")
            report.append("  • 非核心模块采用敏捷开发")
            report.append("  • 制定详细的里程碑计划")
            report.append("  • 加强项目管理和质量控制")
        else:
            report.append("推荐实施策略: 瀑布模型")
            report.append("  • 详细的需求分析和设计")
            report.append("  • 严格的阶段评审和质量门禁")
            report.append("  • 完善的测试和验收流程")
            report.append("  • 专业化的团队分工协作")
        
        report.append("")
        report.append("=" * 80)
        report.append("报告生成完毕")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_to_json(self, result: ImplementationComplexityResult, output_path: str = None) -> str:
        """导出复杂度分析结果为JSON格式"""
        if output_path is None:
            output_path = f"implementation_complexity_{Path(result.file_path).stem}.json"
        
        data = result.to_dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="实施复杂度计算工具")
    parser.add_argument("--verbose", action="store_true", help="显示详细计算过程")
    parser.add_argument("--report", action="store_true", help="生成详细的复杂度分析报告")
    parser.add_argument("--input", type=str, help="指定输入文件（蓝图或技术规格书）")
    parser.add_argument("--score-only", action="store_true", help="只输出综合复杂度评分（0-100分）")
    parser.add_argument("--export-json", type=str, help="导出JSON结果到指定文件")
    
    args = parser.parse_args()
    
    # 如果没有指定输入文件，尝试使用默认测试文件
    if args.input is None:
        # 检查是否存在测试蓝图文件
        default_files = [
            "docs/02_FACTOR_LIBRARY/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md",
            "docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/TECHNICAL_SPECIFICATION_TEMPLATE.md"
        ]
        
        for file in default_files:
            if os.path.exists(file):
                args.input = file
                break
        
        if args.input is None:
            print("错误: 请使用 --input 参数指定要分析的文件")
            print("或确保以下文件之一存在:")
            for file in default_files:
                print(f"  - {file}")
            sys.exit(1)
    
    try:
        # 创建计算器
        calculator = ImplementationComplexityCalculator(verbose=args.verbose)
        
        # 分析文件
        result = calculator.analyze_file(args.input)
        
        # 输出结果
        if args.score_only:
            print(f"{result.calculate_overall_score():.1f}")
        elif args.report:
            report = calculator.generate_report(result)
            print(report)
        else:
            print(f"实施复杂度分析完成:")
            print(f"  文件: {result.file_path}")
            print(f"  综合复杂度评分: {result.calculate_overall_score():.1f}/100")
            print(f"  复杂度等级: {result.get_complexity_level()}")
            effort_level, effort_days = result.get_implementation_effort()
            print(f"  估算实施工作量: {effort_level} ({effort_days}人天)")
            print(f"  建议: {result.get_recommendation()}")
            print("")
            print("详细维度评分:")
            print(f"  架构复杂度: {result.architecture.calculate_score():.1f}/30")
            print(f"  集成复杂度: {result.integration.calculate_score():.1f}/25")
            print(f"  维护复杂度: {result.maintenance.calculate_score():.1f}/25")
            print(f"  测试复杂度: {result.testing.calculate_score():.1f}/20")
        
        # 导出JSON结果
        if args.export_json:
            output_file = calculator.export_to_json(result, args.export_json)
            print(f"JSON结果已导出到: {output_file}")
        elif args.report and not args.score_only:
            # 自动生成JSON文件
            output_file = calculator.export_to_json(result)
            print(f"JSON结果已导出到: {output_file}")
            
    except Exception as e:
        print(f"复杂度分析过程中发生错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()