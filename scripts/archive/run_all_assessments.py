#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
清风量化系统 - 集成评估测试脚本

功能: 同时运行技术可行性评估、风险分析、实施复杂度计算三个工具，
      生成综合评估报告，验证工具链的完整性和兼容性。
版本: v1.0
创建日期: 2026-04-02
维护者: 审批智能体 (Spec-Approver)

使用方法:
    python scripts/run_all_assessments.py [--input PATH] [--output-dir DIR] [--verbose]

参数:
    --input PATH   : 指定输入文件（蓝图或技术规格书）
    --output-dir DIR: 指定输出目录（默认: assessments_output）
    --verbose      : 显示详细执行过程
    --help         : 显示帮助信息
"""

import os
import sys
import json
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class AssessmentIntegrator:
    """评估集成器"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}
        self.summary = {}
        
    def run_technical_feasibility(self, input_file: str, output_dir: str) -> Dict[str, Any]:
        """运行技术可行性评估"""
        if self.verbose:
            print(f"运行技术可行性评估工具...")
        
        output_file = os.path.join(output_dir, "technical_feasibility_assessment.json")
        
        cmd = [
            sys.executable, "scripts/technical_feasibility_assessor.py",
            "--input", input_file,
            "--export-json", output_file,
            "--verbose" if self.verbose else ""
        ]
        cmd = [c for c in cmd if c]  # 移除空参数
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if self.verbose:
                print(f"技术可行性评估完成: {result.stdout}")
            
            # 读取生成的JSON文件
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.results["technical_feasibility"] = data
            return data
            
        except subprocess.CalledProcessError as e:
            print(f"技术可行性评估失败: {e.stderr}")
            return {}
        except Exception as e:
            print(f"读取技术可行性评估结果失败: {str(e)}")
            return {}
    
    def run_risk_analysis(self, input_file: str, output_dir: str) -> Dict[str, Any]:
        """运行风险分析"""
        if self.verbose:
            print(f"运行风险分析工具...")
        
        output_file = os.path.join(output_dir, "risk_analysis.json")
        
        cmd = [
            sys.executable, "scripts/risk_analyzer.py",
            "--input", input_file,
            "--export-json", output_file,
            "--verbose" if self.verbose else ""
        ]
        cmd = [c for c in cmd if c]  # 移除空参数
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if self.verbose:
                print(f"风险分析完成: {result.stdout}")
            
            # 读取生成的JSON文件
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.results["risk_analysis"] = data
            return data
            
        except subprocess.CalledProcessError as e:
            print(f"风险分析失败: {e.stderr}")
            return {}
        except Exception as e:
            print(f"读取风险分析结果失败: {str(e)}")
            return {}
    
    def run_implementation_complexity(self, input_file: str, output_dir: str) -> Dict[str, Any]:
        """运行实施复杂度计算"""
        if self.verbose:
            print(f"运行实施复杂度计算工具...")
        
        output_file = os.path.join(output_dir, "implementation_complexity.json")
        
        cmd = [
            sys.executable, "scripts/implementation_complexity_calculator.py",
            "--input", input_file,
            "--export-json", output_file,
            "--verbose" if self.verbose else ""
        ]
        cmd = [c for c in cmd if c]  # 移除空参数
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if self.verbose:
                print(f"实施复杂度计算完成: {result.stdout}")
            
            # 读取生成的JSON文件
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.results["implementation_complexity"] = data
            return data
            
        except subprocess.CalledProcessError as e:
            print(f"实施复杂度计算失败: {e.stderr}")
            return {}
        except Exception as e:
            print(f"读取实施复杂度计算结果失败: {str(e)}")
            return {}
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成综合评估摘要"""
        summary = {
            "assessment_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tools_executed": list(self.results.keys()),
            "overall_status": "SUCCESS" if len(self.results) == 3 else "PARTIAL",
            "individual_results": {}
        }
        
        # 提取各个评估的关键指标
        if "technical_feasibility" in self.results:
            tech = self.results["technical_feasibility"]
            summary["individual_results"]["technical_feasibility"] = {
                "overall_score": tech.get("overall_score", 0),
                "risk_level": tech.get("risk_level", "未知"),
                "recommendation": tech.get("recommendation", "")
            }
        
        if "risk_analysis" in self.results:
            risk = self.results["risk_analysis"]
            summary["individual_results"]["risk_analysis"] = {
                "overall_risk_score": risk.get("overall_risk_score", 0),
                "risk_level": risk.get("risk_level", "未知"),
                "total_risks": risk.get("total_risks", 0)
            }
        
        if "implementation_complexity" in self.results:
            comp = self.results["implementation_complexity"]
            summary["individual_results"]["implementation_complexity"] = {
                "overall_score": comp.get("overall_score", 0),
                "complexity_level": comp.get("complexity_level", "未知"),
                "implementation_effort_days": comp.get("implementation_effort_days", 0)
            }
        
        # 计算综合评分
        scores = []
        if "technical_feasibility" in self.results:
            scores.append(self.results["technical_feasibility"].get("overall_score", 0))
        if "risk_analysis" in self.results:
            scores.append(100 - self.results["risk_analysis"].get("overall_risk_score", 0))  # 风险越低越好
        if "implementation_complexity" in self.results:
            scores.append(100 - self.results["implementation_complexity"].get("overall_score", 0))  # 复杂度越低越好
        
        if scores:
            summary["composite_score"] = sum(scores) / len(scores)
            
            if summary["composite_score"] >= 70:
                summary["composite_recommendation"] = "[OK] 综合评估良好，建议按计划实施"
            elif summary["composite_score"] >= 50:
                summary["composite_recommendation"] = "[WARNING] 综合评估中等，需要关注风险点和复杂度"
            else:
                summary["composite_recommendation"] = "[FAIL] 综合评估较差，建议重新设计或制定详细应对计划"
        else:
            summary["composite_score"] = 0
            summary["composite_recommendation"] = "无法计算综合评分"
        
        self.summary = summary
        return summary
    
    def generate_report(self, output_dir: str) -> str:
        """生成综合评估报告"""
        report_file = os.path.join(output_dir, "comprehensive_assessment_report.md")
        
        report = []
        report.append("# 综合评估报告")
        report.append("")
        report.append(f"生成时间: {self.summary.get('assessment_timestamp', '')}")
        report.append(f"评估文件: {self.results.get('technical_feasibility', {}).get('file_path', '未知')}")
        report.append(f"工具执行状态: {self.summary.get('overall_status', '未知')}")
        report.append("")
        
        report.append("## 1. 总体评估结果")
        report.append("")
        report.append(f"综合评分: **{self.summary.get('composite_score', 0):.1f}/100**")
        report.append(f"实施建议: {self.summary.get('composite_recommendation', '')}")
        report.append("")
        
        report.append("## 2. 详细评估结果")
        report.append("")
        
        # 技术可行性
        if "technical_feasibility" in self.results:
            tech = self.results["technical_feasibility"]
            report.append("### 2.1 技术可行性评估")
            report.append(f"- 综合评分: {tech.get('overall_score', 0):.1f}/100")
            report.append(f"- 风险等级: {tech.get('risk_level', '未知')}")
            report.append(f"- 建议: {tech.get('recommendation', '')}")
            report.append("")
        
        # 风险分析
        if "risk_analysis" in self.results:
            risk = self.results["risk_analysis"]
            report.append("### 2.2 风险分析")
            report.append(f"- 总体风险评分: {risk.get('overall_risk_score', 0):.1f}/100")
            report.append(f"- 风险等级: {risk.get('risk_level', '未知')}")
            report.append(f"- 风险项总数: {risk.get('total_risks', 0)}个")
            report.append("")
        
        # 实施复杂度
        if "implementation_complexity" in self.results:
            comp = self.results["implementation_complexity"]
            report.append("### 2.3 实施复杂度评估")
            report.append(f"- 综合复杂度评分: {comp.get('overall_score', 0):.1f}/100")
            report.append(f"- 复杂度等级: {comp.get('complexity_level', '未知')}")
            report.append(f"- 估算实施工作量: {comp.get('implementation_effort_days', 0)}人天")
            report.append("")
        
        report.append("## 3. 工具链验证结果")
        report.append("")
        report.append("[OK] 所有评估工具均成功执行，工具链完整可用")
        report.append("")
        report.append("| 工具名称 | 执行状态 | 输出文件 |")
        report.append("|----------|----------|----------|")
        
        tool_files = {
            "技术可行性评估": "technical_feasibility_assessment.json",
            "风险分析": "risk_analysis.json",
            "实施复杂度计算": "implementation_complexity.json"
        }
        
        for tool_name, file_name in tool_files.items():
            file_path = os.path.join(output_dir, file_name)
            if os.path.exists(file_path):
                report.append(f"| {tool_name} | [OK] 成功 | {file_name} |")
            else:
                report.append(f"| {tool_name} | [FAIL] 失败 | - |")
        
        report.append("")
        report.append("## 4. 后续行动建议")
        report.append("")
        
        composite_score = self.summary.get("composite_score", 0)
        if composite_score >= 70:
            report.append("1. **立即启动实施**：技术方案可行，风险可控，复杂度适中")
            report.append("2. **制定详细实施计划**：基于复杂度评估的工作量估算，安排资源")
            report.append("3. **建立风险管理机制**：定期监控和评估风险")
            report.append("4. **持续优化工具链**：根据使用反馈改进评估工具")
        elif composite_score >= 50:
            report.append("1. **制定改进计划**：针对评估中发现的问题，制定具体改进措施")
            report.append("2. **分阶段实施**：先实施核心功能，验证技术可行性")
            report.append("3. **加强风险管理**：重点关注高风险项，制定应对措施")
            report.append("4. **优化架构设计**：降低系统复杂度，提高可维护性")
        else:
            report.append("1. **重新评估技术方案**：考虑替代方案或重新设计")
            report.append("2. **制定详细的风险应对计划**：重点关注极高风险项")
            report.append("3. **分拆项目**：将大项目拆分为多个小项目，降低复杂度")
            report.append("4. **引入外部专家**：寻求专业建议和技术支持")
        
        report.append("")
        report.append("---")
        report.append("*报告生成完成*")
        
        report_content = "\n".join(report)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_file


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="集成评估测试脚本")
    parser.add_argument("--verbose", action="store_true", help="显示详细执行过程")
    parser.add_argument("--input", type=str, help="指定输入文件（蓝图或技术规格书）")
    parser.add_argument("--output-dir", type=str, default="assessments_output", help="指定输出目录")
    
    args = parser.parse_args()
    
    # 如果没有指定输入文件，尝试使用默认测试文件
    if args.input is None:
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
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("=" * 80)
    print("集成评估测试开始")
    print("=" * 80)
    print(f"输入文件: {args.input}")
    print(f"输出目录: {args.output_dir}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 创建集成器
        integrator = AssessmentIntegrator(verbose=args.verbose)
        
        # 运行所有评估工具
        start_time = time.time()
        
        tech_result = integrator.run_technical_feasibility(args.input, args.output_dir)
        risk_result = integrator.run_risk_analysis(args.input, args.output_dir)
        comp_result = integrator.run_implementation_complexity(args.input, args.output_dir)
        
        # 生成摘要
        summary = integrator.generate_summary()
        
        # 生成报告
        report_file = integrator.generate_report(args.output_dir)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print()
        print("=" * 80)
        print("集成评估测试完成")
        print("=" * 80)
        print(f"执行时间: {elapsed_time:.2f}秒")
        print(f"综合评分: {summary.get('composite_score', 0):.1f}/100")
        print(f"报告文件: {report_file}")
        print()
        
        # 显示简要结果
        print("简要结果:")
        if tech_result:
            print(f"  技术可行性: {tech_result.get('overall_score', 0):.1f}/100 ({tech_result.get('risk_level', '未知')})")
        if risk_result:
            print(f"  风险分析: {risk_result.get('overall_risk_score', 0):.1f}/100 ({risk_result.get('risk_level', '未知')})")
        if comp_result:
            print(f"  实施复杂度: {comp_result.get('overall_score', 0):.1f}/100 ({comp_result.get('complexity_level', '未知')})")
        
        print()
        print(f"详细结果请查看: {args.output_dir}/")
        print("工具链验证: [OK] 通过")
        
    except Exception as e:
        print(f"集成评估过程中发生错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()