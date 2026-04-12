#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
清风量化系统 - 技术可行性评估工具

功能: 评估技术方案的技术可行性，包括技术成熟度评分、团队技能匹配度分析、实施复杂度评估
版本: v1.0
创建日期: 2026-04-02
维护者: 审批智能体 (Spec-Approver)

使用方法:
    python scripts/technical_feasibility_assessor.py [--verbose] [--report] [--input PATH] [--score-only]

参数:
    --verbose    : 显示详细评估过程
    --report     : 生成详细的评估报告
    --input PATH : 指定输入文件（蓝图或技术规格书）
    --score-only : 只输出综合评分（0-100分）
    --help       : 显示帮助信息

评估维度:
1. 技术成熟度 (30%权重)
   - 技术栈稳定性 (0-10分)
   - 社区活跃度 (0-10分) 
   - 文档完整性 (0-10分)
2. 团队技能匹配度 (30%权重)
   - 现有技能覆盖 (0-10分)
   - 学习曲线坡度 (0-10分)
   - 培训资源可用性 (0-10分)
3. 实施复杂度 (40%权重)
   - 架构复杂度 (0-10分)
   - 集成复杂度 (0-10分)
   - 维护复杂度 (0-10分)
   - 测试复杂度 (0-10分)
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
import yaml
import math

@dataclass
class TechnicalMaturityAssessment:
    """技术成熟度评估"""
    technology_stack_stability: float = 0.0  # 0-10分
    community_activity: float = 0.0         # 0-10分
    documentation_completeness: float = 0.0 # 0-10分
    
    def calculate_score(self) -> float:
        """计算技术成熟度总分 (0-30分)"""
        return (self.technology_stack_stability + 
                self.community_activity + 
                self.documentation_completeness)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "technology_stack_stability": self.technology_stack_stability,
            "community_activity": self.community_activity,
            "documentation_completeness": self.documentation_completeness,
            "total_score": self.calculate_score()
        }

@dataclass
class TeamSkillAssessment:
    """团队技能匹配度评估"""
    existing_skill_coverage: float = 0.0    # 0-10分
    learning_curve_steepness: float = 0.0   # 0-10分（越低越好，转换为分数）
    training_resource_availability: float = 0.0  # 0-10分
    
    def calculate_score(self) -> float:
        """计算团队技能匹配度总分 (0-30分)"""
        # 学习曲线坡度转换为正向分数（坡度越小，分数越高）
        learning_curve_score = 10.0 - self.learning_curve_steepness
        if learning_curve_score < 0:
            learning_curve_score = 0.0
            
        return (self.existing_skill_coverage + 
                learning_curve_score + 
                self.training_resource_availability)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "existing_skill_coverage": self.existing_skill_coverage,
            "learning_curve_steepness": self.learning_curve_steepness,
            "training_resource_availability": self.training_resource_availability,
            "total_score": self.calculate_score()
        }

@dataclass
class ImplementationComplexityAssessment:
    """实施复杂度评估"""
    architecture_complexity: float = 0.0    # 0-10分（越低越好）
    integration_complexity: float = 0.0     # 0-10分（越低越好）
    maintenance_complexity: float = 0.0     # 0-10分（越低越好）
    testing_complexity: float = 0.0         # 0-10分（越低越好）
    
    def calculate_score(self) -> float:
        """计算实施复杂度总分 (0-40分，越低越好)"""
        total_complexity = (self.architecture_complexity + 
                           self.integration_complexity + 
                           self.maintenance_complexity + 
                           self.testing_complexity)
        # 转换为正向分数（复杂度越低，得分越高）
        return 40.0 - total_complexity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "architecture_complexity": self.architecture_complexity,
            "integration_complexity": self.integration_complexity,
            "maintenance_complexity": self.maintenance_complexity,
            "testing_complexity": self.testing_complexity,
            "total_score": self.calculate_score()
        }

@dataclass
class TechnicalFeasibilityResult:
    """技术可行性评估结果"""
    technical_maturity: TechnicalMaturityAssessment
    team_skill_match: TeamSkillAssessment
    implementation_complexity: ImplementationComplexityAssessment
    file_path: str = ""
    
    def calculate_overall_score(self) -> float:
        """计算总体可行性评分 (0-100分)"""
        # 权重分配：技术成熟度30%，团队技能30%，实施复杂度40%
        total_score = (self.technical_maturity.calculate_score() * 0.3 +
                      self.team_skill_match.calculate_score() * 0.3 +
                      self.implementation_complexity.calculate_score() * 0.4)
        
        # 转换为0-100分
        return (total_score / 100.0) * 100.0
    
    def get_risk_level(self) -> str:
        """根据评分确定风险等级"""
        score = self.calculate_overall_score()
        if score >= 80:
            return "低风险 (P3)"
        elif score >= 60:
            return "中风险 (P2)"
        elif score >= 40:
            return "高风险 (P1)"
        else:
            return "极高风险 (P0)"
    
    def get_recommendation(self) -> str:
        """根据评分给出建议"""
        score = self.calculate_overall_score()
        if score >= 80:
            return "[OK] 技术方案可行，建议立即实施"
        elif score >= 60:
            return "[WARNING] 技术方案基本可行，但需要关注风险点，建议优化后实施"
        elif score >= 40:
            return "[WARNING] 技术方案存在较大风险，需要详细评估和准备应对措施"
        else:
            return "[FAIL] 技术方案不可行，建议重新设计或选择替代方案"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "file_path": self.file_path,
            "overall_score": self.calculate_overall_score(),
            "risk_level": self.get_risk_level(),
            "recommendation": self.get_recommendation(),
            "technical_maturity": self.technical_maturity.to_dict(),
            "team_skill_match": self.team_skill_match.to_dict(),
            "implementation_complexity": self.implementation_complexity.to_dict(),
            "assessment_timestamp": "2026-04-02"
        }


class TechnicalFeasibilityAssessor:
    """技术可行性评估器"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []
        
    def analyze_file(self, file_path: str) -> TechnicalFeasibilityResult:
        """分析蓝图或技术规格书文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if self.verbose:
            print(f"开始分析文件: {file_path}")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单的内容分析（实际中可以使用更复杂的NLP技术）
        # 这里使用简单的关键词匹配来评估
        
        # 1. 技术成熟度评估
        tech_maturity = self._assess_technical_maturity(content)
        
        # 2. 团队技能匹配度评估
        team_skill = self._assess_team_skill(content)
        
        # 3. 实施复杂度评估
        impl_complexity = self._assess_implementation_complexity(content)
        
        # 创建结果
        result = TechnicalFeasibilityResult(
            technical_maturity=tech_maturity,
            team_skill_match=team_skill,
            implementation_complexity=impl_complexity,
            file_path=file_path
        )
        
        self.results.append(result)
        return result
    
    def _assess_technical_maturity(self, content: str) -> TechnicalMaturityAssessment:
        """评估技术成熟度"""
        assessment = TechnicalMaturityAssessment()
        
        # 分析技术栈关键词
        tech_keywords = ["python", "pandas", "numpy", "scikit-learn", "pytorch", "tensorflow",
                        "backtrader", "qlib", "feast", "postgresql", "mysql", "redis", "docker"]
        
        # 检查技术栈的提及频率
        tech_mentions = 0
        for keyword in tech_keywords:
            if keyword in content.lower():
                tech_mentions += 1
        
        # 技术栈稳定性评分（基于成熟技术的提及）
        stable_techs = ["python", "pandas", "numpy", "postgresql", "mysql"]
        stable_mentions = 0
        for tech in stable_techs:
            if tech in content.lower():
                stable_mentions += 1
        
        assessment.technology_stack_stability = min(10.0, (stable_mentions / len(stable_techs)) * 10.0)
        
        # 社区活跃度评分（基于开源框架的提及）
        community_techs = ["backtrader", "qlib", "feast", "scikit-learn", "pytorch", "tensorflow"]
        community_mentions = 0
        for tech in community_techs:
            if tech in content.lower():
                community_mentions += 1
        
        assessment.community_activity = min(10.0, (community_mentions / len(community_techs)) * 10.0)
        
        # 文档完整性评分（基于文档相关关键词）
        doc_keywords = ["文档", "说明", "注释", "readme", "api文档", "接口文档", "示例", "example"]
        doc_mentions = 0
        for keyword in doc_keywords:
            if keyword in content.lower():
                doc_mentions += 1
        
        assessment.documentation_completeness = min(10.0, (doc_mentions / len(doc_keywords)) * 10.0)
        
        if self.verbose:
            print(f"  技术成熟度评估: 稳定性={assessment.technology_stack_stability:.1f}, "
                  f"社区活跃度={assessment.community_activity:.1f}, "
                  f"文档完整性={assessment.documentation_completeness:.1f}")
        
        return assessment
    
    def _assess_team_skill(self, content: str) -> TeamSkillAssessment:
        """评估团队技能匹配度"""
        assessment = TeamSkillAssessment()
        
        # 现有技能覆盖评分（基于技术栈与团队技能的匹配）
        # 这里假设团队已有Python、Pandas、NumPy等基础技能
        team_skills = ["python", "pandas", "numpy", "sql", "git", "docker"]
        skill_mentions = 0
        for skill in team_skills:
            if skill in content.lower():
                skill_mentions += 1
        
        assessment.existing_skill_coverage = min(10.0, (skill_mentions / len(team_skills)) * 10.0)
        
        # 学习曲线坡度评估（基于新技术和复杂框架的提及）
        complex_techs = ["pytorch", "tensorflow", "分布式", "并发", "微服务", "云原生"]
        complex_mentions = 0
        for tech in complex_techs:
            if tech in content.lower():
                complex_mentions += 1
        
        # 学习曲线坡度（0-10分，越高越陡峭）
        assessment.learning_curve_steepness = min(10.0, (complex_mentions / len(complex_techs)) * 10.0)
        
        # 培训资源可用性评估（基于文档和示例的提及）
        training_keywords = ["教程", "培训", "学习资源", "示例", "demo", "案例", "最佳实践"]
        training_mentions = 0
        for keyword in training_keywords:
            if keyword in content.lower():
                training_mentions += 1
        
        assessment.training_resource_availability = min(10.0, (training_mentions / len(training_keywords)) * 10.0)
        
        if self.verbose:
            print(f"  团队技能评估: 技能覆盖={assessment.existing_skill_coverage:.1f}, "
                  f"学习曲线坡度={assessment.learning_curve_steepness:.1f}, "
                  f"培训资源={assessment.training_resource_availability:.1f}")
        
        return assessment
    
    def _assess_implementation_complexity(self, content: str) -> ImplementationComplexityAssessment:
        """评估实施复杂度"""
        assessment = ImplementationComplexityAssessment()
        
        # 架构复杂度评估（基于架构关键词）
        arch_keywords = ["微服务", "分布式", "消息队列", "缓存", "负载均衡", "服务发现", "api网关"]
        arch_mentions = 0
        for keyword in arch_keywords:
            if keyword in content.lower():
                arch_mentions += 1
        
        assessment.architecture_complexity = min(10.0, (arch_mentions / len(arch_keywords)) * 10.0)
        
        # 集成复杂度评估（基于集成和依赖关键词）
        integration_keywords = ["集成", "接口", "api", "sdk", "第三方", "外部系统", "依赖", "兼容性"]
        integration_mentions = 0
        for keyword in integration_keywords:
            if keyword in content.lower():
                integration_mentions += 1
        
        assessment.integration_complexity = min(10.0, (integration_mentions / len(integration_keywords)) * 10.0)
        
        # 维护复杂度评估（基于监控和运维关键词）
        maintenance_keywords = ["监控", "日志", "告警", "运维", "部署", "升级", "备份", "恢复"]
        maintenance_mentions = 0
        for keyword in maintenance_keywords:
            if keyword in content.lower():
                maintenance_mentions += 1
        
        assessment.maintenance_complexity = min(10.0, (maintenance_mentions / len(maintenance_keywords)) * 10.0)
        
        # 测试复杂度评估（基于测试相关关键词）
        testing_keywords = ["测试", "单元测试", "集成测试", "压力测试", "性能测试", "自动化测试", "测试用例"]
        testing_mentions = 0
        for keyword in testing_keywords:
            if keyword in content.lower():
                testing_mentions += 1
        
        assessment.testing_complexity = min(10.0, (testing_mentions / len(testing_keywords)) * 10.0)
        
        if self.verbose:
            print(f"  实施复杂度评估: 架构={assessment.architecture_complexity:.1f}, "
                  f"集成={assessment.integration_complexity:.1f}, "
                  f"维护={assessment.maintenance_complexity:.1f}, "
                  f"测试={assessment.testing_complexity:.1f}")
        
        return assessment
    
    def generate_report(self, result: TechnicalFeasibilityResult) -> str:
        """生成评估报告"""
        report = []
        report.append("=" * 80)
        report.append("技术可行性评估报告")
        report.append("=" * 80)
        report.append(f"评估文件: {result.file_path}")
        report.append(f"评估时间: 2026-04-02")
        report.append("")
        
        report.append("1. 总体评估结果")
        report.append("-" * 40)
        report.append(f"综合评分: {result.calculate_overall_score():.1f}/100")
        report.append(f"风险等级: {result.get_risk_level()}")
        report.append(f"实施建议: {result.get_recommendation()}")
        report.append("")
        
        report.append("2. 详细评估维度")
        report.append("-" * 40)
        
        # 技术成熟度
        tech = result.technical_maturity
        report.append("2.1 技术成熟度评估 (权重: 30%)")
        report.append(f"  • 技术栈稳定性: {tech.technology_stack_stability:.1f}/10")
        report.append(f"  • 社区活跃度: {tech.community_activity:.1f}/10")
        report.append(f"  • 文档完整性: {tech.documentation_completeness:.1f}/10")
        report.append(f"  • 小计: {tech.calculate_score():.1f}/30")
        report.append("")
        
        # 团队技能匹配度
        team = result.team_skill_match
        report.append("2.2 团队技能匹配度评估 (权重: 30%)")
        report.append(f"  • 现有技能覆盖: {team.existing_skill_coverage:.1f}/10")
        report.append(f"  • 学习曲线坡度: {team.learning_curve_steepness:.1f}/10 (越低越好)")
        report.append(f"  • 培训资源可用性: {team.training_resource_availability:.1f}/10")
        report.append(f"  • 小计: {team.calculate_score():.1f}/30")
        report.append("")
        
        # 实施复杂度
        impl = result.implementation_complexity
        report.append("2.3 实施复杂度评估 (权重: 40%)")
        report.append(f"  • 架构复杂度: {impl.architecture_complexity:.1f}/10 (越低越好)")
        report.append(f"  • 集成复杂度: {impl.integration_complexity:.1f}/10 (越低越好)")
        report.append(f"  • 维护复杂度: {impl.maintenance_complexity:.1f}/10 (越低越好)")
        report.append(f"  • 测试复杂度: {impl.testing_complexity:.1f}/10 (越低越好)")
        report.append(f"  • 小计: {impl.calculate_score():.1f}/40")
        report.append("")
        
        report.append("3. 风险评估与建议")
        report.append("-" * 40)
        
        score = result.calculate_overall_score()
        if score >= 80:
            report.append("[OK] 低风险区域:")
            report.append("  • 技术方案成熟稳定，实施风险较低")
            report.append("  • 建议: 按计划推进实施，关注实施细节")
        elif score >= 60:
            report.append("[WARNING] 中风险区域:")
            report.append("  • 存在一些技术风险点，需要关注")
            report.append("  • 建议: 制定风险应对计划，加强技术验证")
        elif score >= 40:
            report.append("[WARNING] 高风险区域:")
            report.append("  • 存在重大技术风险，需要详细评估")
            report.append("  • 建议: 重新评估技术选型，准备备选方案")
        else:
            report.append("[FAIL] 极高风险区域:")
            report.append("  • 技术方案存在严重问题，不建议实施")
            report.append("  • 建议: 重新设计技术方案或选择替代方案")
        
        report.append("")
        report.append("4. 改进建议")
        report.append("-" * 40)
        
        # 根据薄弱环节给出改进建议
        if tech.calculate_score() < 20:
            report.append("• 技术成熟度不足:")
            report.append("  - 考虑使用更成熟稳定的技术栈")
            report.append("  - 优先选择有活跃社区支持的开源项目")
            report.append("  - 完善技术文档和示例代码")
        
        if team.calculate_score() < 20:
            report.append("• 团队技能匹配度不足:")
            report.append("  - 安排相关技术培训")
            report.append("  - 引入有相关经验的技术顾问")
            report.append("  - 考虑外包复杂模块给专业团队")
        
        if impl.calculate_score() < 25:
            report.append("• 实施复杂度较高:")
            report.append("  - 简化系统架构设计")
            report.append("  - 减少外部系统依赖")
            report.append("  - 制定详细的测试和运维计划")
        
        report.append("")
        report.append("=" * 80)
        report.append("报告生成完毕")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_to_json(self, result: TechnicalFeasibilityResult, output_path: str = None) -> str:
        """导出评估结果为JSON格式"""
        if output_path is None:
            output_path = f"technical_feasibility_assessment_{Path(result.file_path).stem}.json"
        
        data = result.to_dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="技术可行性评估工具")
    parser.add_argument("--verbose", action="store_true", help="显示详细评估过程")
    parser.add_argument("--report", action="store_true", help="生成详细的评估报告")
    parser.add_argument("--input", type=str, help="指定输入文件（蓝图或技术规格书）")
    parser.add_argument("--score-only", action="store_true", help="只输出综合评分（0-100分）")
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
            print("错误: 请使用 --input 参数指定要评估的文件")
            print("或确保以下文件之一存在:")
            for file in default_files:
                print(f"  - {file}")
            sys.exit(1)
    
    try:
        # 创建评估器
        assessor = TechnicalFeasibilityAssessor(verbose=args.verbose)
        
        # 分析文件
        result = assessor.analyze_file(args.input)
        
        # 输出结果
        if args.score_only:
            print(f"{result.calculate_overall_score():.1f}")
        elif args.report:
            report = assessor.generate_report(result)
            print(report)
        else:
            print(f"技术可行性评估完成:")
            print(f"  文件: {result.file_path}")
            print(f"  综合评分: {result.calculate_overall_score():.1f}/100")
            print(f"  风险等级: {result.get_risk_level()}")
            print(f"  建议: {result.get_recommendation()}")
            print("")
            print("详细维度评分:")
            print(f"  技术成熟度: {result.technical_maturity.calculate_score():.1f}/30")
            print(f"  团队技能匹配度: {result.team_skill_match.calculate_score():.1f}/30")
            print(f"  实施复杂度: {result.implementation_complexity.calculate_score():.1f}/40")
        
        # 导出JSON结果
        if args.export_json:
            output_file = assessor.export_to_json(result, args.export_json)
            print(f"JSON结果已导出到: {output_file}")
        elif args.report and not args.score_only:
            # 自动生成JSON文件
            output_file = assessor.export_to_json(result)
            print(f"JSON结果已导出到: {output_file}")
            
    except Exception as e:
        print(f"评估过程中发生错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()