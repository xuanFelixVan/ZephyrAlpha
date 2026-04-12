#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
P0-2: 修复职责不清问题
为所有文档添加清晰的职责描述
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class UnclearResponsibilityFixer:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.audit_report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / "layer4_deep_audit_v2_20260407_031623.json"
        self.fix_log = {
            "fix_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fixed_count": 0,
            "skipped_count": 0,
            "error_count": 0,
            "details": []
        }
        
        self.audit_data = None
        self.load_audit_data()
        
    def load_audit_data(self):
        """加载审计数据"""
        try:
            with open(self.audit_report_path, 'r', encoding='utf-8') as f:
                self.audit_data = json.load(f)
            print(f"✅ 已加载审计数据: {self.audit_report_path}")
        except Exception as e:
            print(f"❌ 加载审计数据失败: {e}")
            self.audit_data = None
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """读取文件内容"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except:
                continue
        return None
    
    def write_file_content(self, file_path: Path, content: str):
        """写入文件内容"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def extract_yaml_header(self, content: str) -> Tuple[Optional[str], str]:
        """提取YAML头部"""
        if not content.startswith('---'):
            return None, content
        
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), '---' + '---'.join(parts[2:])
        return None, content
    
    def infer_responsibility(self, file_path: Path, content: str) -> str:
        """根据文件路径和内容推断职责"""
        file_name = file_path.stem.lower()
        parent_dir = file_path.parent.name.lower()
        
        responsibility_map = {
            'factor': '因子计算、因子分析、因子管理',
            'backtest': '回测验证、策略测试、性能评估',
            'data': '数据管理、数据清洗、数据质量',
            'strategy': '策略开发、策略优化、策略执行',
            'risk': '风险管理、风险控制、风险评估',
            'portfolio': '组合管理、组合优化、组合构建',
            'execution': '交易执行、订单管理、执行优化',
            'monitor': '监控告警、性能监控、系统监控',
            'report': '报告生成、数据分析、结果展示',
            'blueprint': '架构设计、模块规划、技术方案',
            'index': '文档索引、导航导航、快速查找',
            'readme': '模块说明、快速入门、使用指南',
            'audit': '审计检查、质量评估、合规验证',
            'ml': '机器学习、模型训练、特征工程',
            'model': '模型管理、模型版本、模型部署',
            'feature': '特征工程、特征提取、特征选择',
            'train': '模型训练、参数优化、超参调优',
            'predict': '预测推理、结果输出、模型应用',
            'experiment': '实验管理、实验跟踪、实验记录',
            'sentiment': '舆情分析、情感识别、文本处理',
            'ai': 'AI决策、智能分析、自动化流程',
            'workflow': '工作流管理、流程编排、任务调度',
            'governance': '治理合规、规范管理、制度建设',
            'compliance': '合规检查、规则验证、标准执行',
            'strategic': '战略决策、投资规划、资产配置',
            'decision': '决策支持、方案评估、选择优化',
            'benchmark': '基准管理、业绩比较、标准设定',
            'allocation': '资产配置、权重分配、组合构建',
            'optimization': '优化算法、参数调优、性能提升',
            'trading': '交易策略、交易执行、交易管理',
            'tactics': '交易战术、策略执行、风险控制',
            'archive': '文档归档、历史记录、版本管理',
            'template': '模板文档、标准格式、规范参考',
            'standard': '标准文档、规范定义、质量要求',
            'process': '流程文档、操作指南、执行步骤',
            'knowledge': '知识库、经验总结、最佳实践',
            'research': '研究创新、策略研发、技术探索',
            'innovation': '创新研究、新技术、新方法',
        }
        
        for key, resp in responsibility_map.items():
            if key in file_name or key in parent_dir:
                return resp
        
        if 'layer' in file_name.lower():
            layer_match = re.search(r'layer[_\s]*(\d+)', file_name, re.IGNORECASE)
            if layer_match:
                layer_num = int(layer_match.group(1))
                layer_resp = {
                    0: '数据源管理、数据接入、数据质量',
                    1: '数据质量、数据清洗、数据标准化',
                    2: '因子计算、因子分析、因子管理',
                    3: '策略开发、策略优化、策略回测',
                    4: '机器学习、模型训练、特征工程',
                    5: '组合优化、权重分配、组合构建',
                    6: '交易执行、订单管理、执行优化',
                    7: '风险管理、风险控制、风险评估',
                    8: '人机交互、界面展示、用户操作',
                    9: '研究创新、策略研发、技术探索',
                    10: '治理合规、规范管理、制度建设',
                    11: '战略决策、投资规划、资产配置',
                }
                return layer_resp.get(layer_num, '系统功能模块')
        
        return '系统功能模块'
    
    def fix_unclear_responsibility(self):
        """修复职责不清问题"""
        print("\n" + "=" * 80)
        print("P0-2: 修复职责不清问题")
        print("=" * 80)
        
        if not self.audit_data:
            print("❌ 无审计数据，跳过")
            return
        
        unclear_docs = self.audit_data['deep_check']['unclear_responsibility']
        print(f"发现 {len(unclear_docs)} 个职责不清的文档")
        
        for doc_info in unclear_docs[:200]:
            doc_path = self.project_root / doc_info['doc']
            
            if not doc_path.exists():
                self.fix_log['skipped_count'] += 1
                continue
            
            content = self.read_file_content(doc_path)
            if not content:
                self.fix_log['error_count'] += 1
                continue
            
            yaml_header, body = self.extract_yaml_header(content)
            
            issues = doc_info['issues']
            fixed = False
            
            if '缺少YAML头部' in issues:
                responsibility = self.infer_responsibility(doc_path, content)
                new_yaml = f"---\nmodule_id: {doc_path.stem.upper()}_001\n"
                new_yaml += f"version: 1.0.0\n"
                new_yaml += f"status: Active\n"
                new_yaml += f"created_date: {datetime.now().strftime('%Y-%m-%d')}\n"
                new_yaml += f"last_updated: {datetime.now().strftime('%Y-%m-%d')}\n"
                new_yaml += f"owner: 个人开发者\n"
                new_yaml += f"responsibility:\n  - {responsibility}\n"
                new_yaml += f"---\n\n"
                
                new_content = new_yaml + body.lstrip('---')
                self.write_file_content(doc_path, new_content)
                fixed = True
            
            elif '缺少responsibility字段' in issues:
                responsibility = self.infer_responsibility(doc_path, content)
                if yaml_header:
                    if 'responsibility:' not in yaml_header:
                        yaml_header += f"\nresponsibility:\n  - {responsibility}"
                        new_content = f"---\n{yaml_header}\n---\n{body}"
                        self.write_file_content(doc_path, new_content)
                        fixed = True
            
            elif any('职责描述过短' in issue for issue in issues):
                responsibility = self.infer_responsibility(doc_path, content)
                if yaml_header:
                    lines = yaml_header.split('\n')
                    new_lines = []
                    for line in lines:
                        if line.startswith('responsibility:'):
                            new_lines.append(f"responsibility:")
                            new_lines.append(f"  - {responsibility}")
                        elif line.startswith('  -') and 'responsibility' in '\n'.join(new_lines[-2:]):
                            continue
                        else:
                            new_lines.append(line)
                    
                    new_yaml = '\n'.join(new_lines)
                    new_content = f"---\n{new_yaml}\n---\n{body}"
                    self.write_file_content(doc_path, new_content)
                    fixed = True
            
            if fixed:
                self.fix_log['fixed_count'] += 1
                self.fix_log['details'].append({
                    "doc": doc_info['doc'],
                    "issues": issues,
                    "fixed": True
                })
                
                if self.fix_log['fixed_count'] % 20 == 0:
                    print(f"已修复 {self.fix_log['fixed_count']} 个文档...")
            else:
                self.fix_log['skipped_count'] += 1
        
        print(f"\n✅ 职责不清修复完成:")
        print(f"  - 修复: {self.fix_log['fixed_count']} 个文档")
        print(f"  - 跳过: {self.fix_log['skipped_count']} 个文档")
        print(f"  - 错误: {self.fix_log['error_count']} 个文档")
    
    def save_fix_log(self):
        """保存修复日志"""
        log_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"p0_fix_unclear_resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.fix_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 修复日志已保存: {log_path}")
    
    def run(self):
        """执行修复"""
        print("=" * 80)
        print("P0-2: 修复职责不清问题")
        print("=" * 80)
        print(f"修复时间: {self.fix_log['fix_time']}")
        print("-" * 80)
        
        self.fix_unclear_responsibility()
        self.save_fix_log()
        
        print("\n" + "=" * 80)
        print("P0-2修复完成")
        print("=" * 80)

if __name__ == "__main__":
    fixer = UnclearResponsibilityFixer()
    fixer.run()
