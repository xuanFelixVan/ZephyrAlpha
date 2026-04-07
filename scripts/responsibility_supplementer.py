#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
战略决策层职责描述补充脚本
目标：为缺少职责描述的文档补充标准职责描述
"""

import os
import re
from pathlib import Path
from datetime import datetime

class ResponsibilitySupplementer:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root)
        self.strategic_dir = self.docs_root / "11_STRATEGIC_DECISION"
        self.documents = []
        self.supplemented_count = 0
        
    def run_supplement(self):
        """执行职责补充"""
        print("=" * 80)
        print("战略决策层职责描述补充")
        print("=" * 80)
        print(f"补充目录: {self.strategic_dir}")
        print()
        
        # 1. 扫描所有文档
        print("1. 扫描所有文档...")
        self.scan_documents()
        
        # 2. 补充职责描述
        print("\n2. 补充职责描述...")
        self.supplement_responsibilities()
        
        # 3. 生成补充报告
        print("\n3. 生成补充报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print(f"补充完成: {self.supplemented_count} 个文档")
        print("=" * 80)
        
    def scan_documents(self):
        """扫描所有文档"""
        md_files = list(self.strategic_dir.rglob("*.md"))
        
        for md_file in md_files:
            if 'archive' in str(md_file).lower() or md_file.name == 'INDEX.md':
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否有职责描述
                has_responsibility = bool(re.search(r'核心职责[：:]', content))
                
                # 提取标题
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else md_file.stem
                
                doc_info = {
                    'path': str(md_file),
                    'filename': md_file.name,
                    'title': title,
                    'has_responsibility': has_responsibility,
                    'content': content
                }
                
                self.documents.append(doc_info)
                
            except Exception as e:
                print(f"  ⚠️ 读取文件失败: {md_file.name} - {str(e)}")
        
        print(f"  ✅ 扫描完成: {len(self.documents)} 个文档")
        print(f"  - 有职责描述: {len([d for d in self.documents if d['has_responsibility']])} 个")
        print(f"  - 缺职责描述: {len([d for d in self.documents if not d['has_responsibility']])} 个")
        
    def supplement_responsibilities(self):
        """补充职责描述"""
        for doc in self.documents:
            if doc['has_responsibility']:
                continue
            
            # 根据文件名推断职责
            responsibility = self.infer_responsibility(doc['filename'], doc['title'])
            
            if responsibility:
                # 在文档开头添加职责描述
                self.add_responsibility_to_doc(doc, responsibility)
                self.supplemented_count += 1
                print(f"  ✅ 补充: {doc['filename']} - {responsibility}")
        
    def infer_responsibility(self, filename, title):
        """根据文件名推断职责"""
        # 蓝图文档的职责推断
        if 'BLUEPRINT' in filename:
            if 'BENCHMARK' in filename:
                return '基准管理系统蓝图设计'
            elif 'CAPITAL_ALLOCATION' in filename:
                return '资本配置系统蓝图设计'
            elif 'DECISION_AUDIT' in filename:
                return '投资决策审计系统蓝图设计'
            elif 'ESG' in filename:
                return 'ESG投资系统蓝图设计'
            elif 'INVESTMENT_CONSTRAINT' in filename:
                return '投资限制管理系统蓝图设计'
            elif 'IPS' in filename:
                return '投资政策声明(IPS)管理系统蓝图设计'
            elif 'LEVERAGE' in filename:
                return '融资融券管理系统蓝图设计'
            elif 'LIQUIDITY' in filename:
                return '流动性管理系统蓝图设计'
            elif 'MACRO_FACTOR' in filename:
                return '宏观因子系统蓝图设计'
            elif 'MARKET_REGIME' in filename:
                return '市场状态识别系统蓝图设计'
            elif 'MULTI_STRATEGY' in filename:
                return '多策略协调系统蓝图设计'
            elif 'OPEN_SOURCE' in filename:
                return '开源项目集成蓝图设计'
            elif 'PERFORMANCE_ATTRIBUTION' in filename:
                return '业绩归因系统蓝图设计'
            elif 'PORTFOLIO_INSURANCE' in filename:
                return '投资组合保险系统蓝图设计'
            elif 'REBALANCING' in filename:
                return '再平衡决策系统蓝图设计'
            elif 'SCENARIO_ANALYSIS' in filename:
                return '情景分析系统蓝图设计'
            elif 'TAX' in filename:
                return '税务管理系统蓝图设计'
            elif 'TCA' in filename:
                return '交易成本分析系统蓝图设计'
            elif filename == 'BLUEPRINT.md':
                return '战略决策层总览蓝图设计'
            else:
                return '蓝图设计和规划'
        
        # 子目录文档的职责推断
        if 'ASSET_ALLOCATION' in filename or 'ALLOCATION' in filename:
            if 'MODEL' in filename:
                return '资产配置模型设计'
            elif 'METHOD' in filename:
                return '配置优化方法设计'
            elif 'CLASS' in filename:
                return '资产类别定义设计'
            else:
                return '资产配置相关设计'
        
        if 'RISK_BUDGETING' in filename or 'RISK_ADJUSTMENT' in filename:
            if 'FRAMEWORK' in filename:
                return '风险预算框架设计'
            elif 'METHOD' in filename:
                return '风险预算方法设计'
            elif 'ADJUSTMENT' in filename:
                return '风险调整机制设计'
            else:
                return '风险预算相关设计'
        
        if 'STRATEGY_SELECTION' in filename or 'STRATEGY_EVALUATION' in filename or 'STRATEGY_PORTFOLIO' in filename:
            if 'FRAMEWORK' in filename:
                return '策略选择框架设计'
            elif 'CRITERIA' in filename:
                return '策略评估标准设计'
            elif 'OPTIMIZATION' in filename:
                return '策略组合优化设计'
            else:
                return '策略选择相关设计'
        
        if 'ADJUSTMENT' in filename or 'MARKET_ENVIRONMENT' in filename or 'STRATEGIC_ADJUSTMENT' in filename:
            if 'TRIGGER' in filename:
                return '调整触发条件设计'
            elif 'ENVIRONMENT' in filename:
                return '市场环境评估设计'
            elif 'MECHANISM' in filename:
                return '战略调整机制设计'
            else:
                return '战略调整相关设计'
        
        # 其他文档
        if 'PROGRESS_REPORT' in filename:
            return '进度报告和状态跟踪'
        elif 'IMPLEMENTATION_PLAN' in filename:
            return '实施计划制定'
        elif 'RESPONSIBILITY_BOUNDARY' in filename:
            return '职责边界矩阵定义'
        elif 'TECHNOLOGY_SELECTION' in filename:
            return '技术选型决策'
        elif 'BLUEPRINT_INDEX' in filename:
            return '蓝图索引和导航'
        elif 'COMPLETE_BLUEPRINT_OVERVIEW' in filename:
            return '完整蓝图总览'
        
        return None
        
    def add_responsibility_to_doc(self, doc, responsibility):
        """在文档中添加职责描述"""
        content = doc['content']
        
        # 查找第一个标题
        title_match = re.search(r'^#\s+.+$', content, re.MULTILINE)
        
        if title_match:
            # 在标题后添加职责描述
            insert_pos = title_match.end()
            responsibility_block = f"\n> **核心职责**: {responsibility}\n> **职责边界**: \n> - ✅ 本文档负责：{responsibility}相关内容\n> - ❌ 本文档不负责：其他模块内容\n"
            
            new_content = content[:insert_pos] + responsibility_block + content[insert_pos:]
            
            # 写入文件
            with open(doc['path'], 'w', encoding='utf-8') as f:
                f.write(new_content)
        
    def generate_report(self):
        """生成补充报告"""
        report_path = self.docs_root / "05_IMPLEMENTATION" / "07_OPERATIONS" / "audit_state" / "STRATEGIC_DECISION_RESPONSIBILITY_SUPPLEMENT_REPORT_20260407.md"
        
        report = f"""# 战略决策层职责描述补充报告

> **补充时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> **补充范围**: 11_STRATEGIC_DECISION（战略决策层）
> **补充方法**: 基于文件名和标题推断职责

---

## 📊 补充统计

| 统计项 | 数量 |
|--------|------|
| **文档总数** | {len(self.documents)} |
| **原有职责描述** | {len([d for d in self.documents if d['has_responsibility']])} |
| **补充职责描述** | {self.supplemented_count} |
| **补充后职责清晰度** | {len([d for d in self.documents if d['has_responsibility']]) + self.supplemented_count} / {len(self.documents)} |

---

## 📋 补充详情

### 已补充文档

"""
        
        supplemented_docs = [d for d in self.documents if not d['has_responsibility']]
        for doc in supplemented_docs:
            responsibility = self.infer_responsibility(doc['filename'], doc['title'])
            if responsibility:
                report += f"- **{doc['filename']}**: {responsibility}\n"
        
        report += f"""
---

## 🎯 质量改进

| 指标 | 补充前 | 补充后 | 改进 |
|------|--------|--------|------|
| **职责清晰度** | {len([d for d in self.documents if d['has_responsibility']]) / len(self.documents) * 100:.1f}% | {(len([d for d in self.documents if d['has_responsibility']]) + self.supplemented_count) / len(self.documents) * 100:.1f}% | +{self.supplemented_count / len(self.documents) * 100:.1f}% |

---

## 📝 补充说明

**补充原则**:
- 基于文件名和标题推断职责
- 保持职责描述简洁明确
- 符合专业量化机构标准

**后续建议**:
1. 人工复核补充的职责描述
2. 根据实际内容调整职责描述
3. 建立职责描述标准模板

---

**补充完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**补充报告路径**: {report_path.relative_to(self.docs_root)}
"""
        
        # 保存报告
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  ✅ 报告已生成: {report_path.relative_to(self.docs_root)}")

if __name__ == "__main__":
    supplementer = ResponsibilitySupplementer("docs")
    supplementer.run_supplement()
