#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
统一审计工具集成框架
功能：
1. 统一工具接口
2. 工具链集成
3. 自动化审计流程
4. 统一报告生成
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

@dataclass
class AuditResult:
    tool_name: str
    status: str
    score: float
    issues: List[Dict]
    metrics: Dict
    execution_time: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class AuditTool(ABC):
    @abstractmethod
    def execute(self, docs_dir: Path) -> AuditResult:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass

class UnifiedAuditFramework:
    def __init__(self, docs_dir: Path):
        self.docs_dir = Path(docs_dir)
        self.tools: List[AuditTool] = []
        self.results: List[AuditResult] = []
        self.report_dir = self.docs_dir.parent / "docs/09_AUDIT/REPORTS"
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def register_tool(self, tool: AuditTool):
        self.tools.append(tool)
        print(f"✅ 注册工具: {tool.get_name()}")
    
    def execute_all(self) -> List[AuditResult]:
        print("\n=== 统一审计工具执行 ===\n")
        print(f"文档目录: {self.docs_dir}")
        print(f"注册工具数: {len(self.tools)}")
        
        start_time = time.time()
        
        for i, tool in enumerate(self.tools, 1):
            print(f"\n[{i}/{len(self.tools)}] 执行工具: {tool.get_name()}")
            print(f"  描述: {tool.get_description()}")
            
            tool_start = time.time()
            try:
                result = tool.execute(self.docs_dir)
                result.execution_time = time.time() - tool_start
                self.results.append(result)
                
                print(f"  ✅ 执行成功")
                print(f"  状态: {result.status}")
                print(f"  得分: {result.score:.2f}")
                print(f"  问题数: {len(result.issues)}")
                print(f"  耗时: {result.execution_time:.2f}秒")
            except Exception as e:
                print(f"  ❌ 执行失败: {e}")
                self.results.append(AuditResult(
                    tool_name=tool.get_name(),
                    status='error',
                    score=0.0,
                    issues=[{'type': 'execution_error', 'message': str(e)}],
                    metrics={},
                    execution_time=time.time() - tool_start
                ))
        
        total_time = time.time() - start_time
        print(f"\n=== 审计完成 ===")
        print(f"总耗时: {total_time:.2f}秒")
        
        return self.results
    
    def generate_unified_report(self) -> Path:
        report = {
            'summary': self._generate_summary(),
            'tool_results': [self._result_to_dict(r) for r in self.results],
            'recommendations': self._generate_recommendations(),
            'execution_info': {
                'total_time': sum(r.execution_time for r in self.results),
                'tool_count': len(self.tools),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        report_file = self.report_dir / f"unified_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已生成: {report_file}")
        return report_file
    
    def _generate_summary(self) -> Dict:
        if not self.results:
            return {}
        
        total_score = sum(r.score for r in self.results)
        avg_score = total_score / len(self.results)
        
        total_issues = sum(len(r.issues) for r in self.results)
        
        status_counts = {}
        for r in self.results:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1
        
        return {
            'average_score': round(avg_score, 2),
            'total_issues': total_issues,
            'status_distribution': status_counts,
            'overall_status': 'pass' if avg_score >= 80 else 'warning' if avg_score >= 60 else 'fail'
        }
    
    def _generate_recommendations(self) -> List[Dict]:
        recommendations = []
        
        for result in self.results:
            if result.score < 80:
                recommendations.append({
                    'tool': result.tool_name,
                    'priority': 'high' if result.score < 60 else 'medium',
                    'issue': f'{result.tool_name}得分较低({result.score:.2f})',
                    'action': f'建议优化{result.tool_name}相关问题'
                })
        
        return recommendations
    
    def _result_to_dict(self, result: AuditResult) -> Dict:
        return {
            'tool_name': result.tool_name,
            'status': result.status,
            'score': result.score,
            'issues': result.issues,
            'metrics': result.metrics,
            'execution_time': result.execution_time,
            'timestamp': result.timestamp
        }

class QuickAuditTool(AuditTool):
    def get_name(self) -> str:
        return "快速审计工具"
    
    def get_description(self) -> str:
        return "检查关键文档和索引完整性"
    
    def execute(self, docs_dir: Path) -> AuditResult:
        start_time = time.time()
        
        critical_docs = ['System_Manifest.md', 'INDEX.md', 'SITEMAP.md']
        issues = []
        score = 100.0
        
        for doc in critical_docs:
            if not (docs_dir / doc).exists():
                issues.append({
                    'type': 'missing_critical_doc',
                    'file': doc,
                    'message': f'关键文档缺失: {doc}'
                })
                score -= 20
        
        return AuditResult(
            tool_name=self.get_name(),
            status='pass' if score >= 80 else 'warning',
            score=score,
            issues=issues,
            metrics={'critical_docs': len(critical_docs), 'missing_docs': len(issues)},
            execution_time=time.time() - start_time
        )

class DeadLinkAuditTool(AuditTool):
    def get_name(self) -> str:
        return "死链接检测工具"
    
    def get_description(self) -> str:
        return "检测文档中的无效链接"
    
    def execute(self, docs_dir: Path) -> AuditResult:
        start_time = time.time()
        
        import re
        issues = []
        total_links = 0
        dead_links = 0
        
        for md_file in docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            for link_text, link_path in links:
                if link_path.startswith(('http://', 'https://', '#', 'mailto:')):
                    continue
                
                total_links += 1
                target_file = (md_file.parent / link_path).resolve()
                
                if not target_file.exists():
                    dead_links += 1
                    issues.append({
                        'type': 'dead_link',
                        'source': str(md_file.relative_to(docs_dir)),
                        'target': link_path,
                        'message': f'死链接: {link_path}'
                    })
        
        score = 100.0 if total_links == 0 else max(0, 100 - (dead_links / total_links * 100))
        
        return AuditResult(
            tool_name=self.get_name(),
            status='pass' if score >= 95 else 'warning',
            score=score,
            issues=issues[:20],
            metrics={'total_links': total_links, 'dead_links': dead_links},
            execution_time=time.time() - start_time
        )

class ResponsibilityAuditTool(AuditTool):
    def get_name(self) -> str:
        return "职责检测工具"
    
    def get_description(self) -> str:
        return "检测文档职责是否清晰"
    
    def execute(self, docs_dir: Path) -> AuditResult:
        start_time = time.time()
        
        issues = []
        total_docs = 0
        docs_with_responsibility = 0
        
        for md_file in docs_dir.rglob("*.md"):
            total_docs += 1
            content = md_file.read_text(encoding='utf-8')
            
            if '职责' in content or '功能' in content or '目标' in content:
                docs_with_responsibility += 1
            else:
                issues.append({
                    'type': 'missing_responsibility',
                    'file': str(md_file.relative_to(docs_dir)),
                    'message': f'文档缺少职责说明: {md_file.name}'
                })
        
        score = (docs_with_responsibility / total_docs * 100) if total_docs > 0 else 0
        
        return AuditResult(
            tool_name=self.get_name(),
            status='pass' if score >= 80 else 'warning',
            score=score,
            issues=issues[:20],
            metrics={'total_docs': total_docs, 'docs_with_responsibility': docs_with_responsibility},
            execution_time=time.time() - start_time
        )

def main():
    docs_dir = Path("D:/ZephyrAlpha/docs")
    
    framework = UnifiedAuditFramework(docs_dir)
    
    framework.register_tool(QuickAuditTool())
    framework.register_tool(DeadLinkAuditTool())
    framework.register_tool(ResponsibilityAuditTool())
    
    results = framework.execute_all()
    
    report_file = framework.generate_unified_report()
    
    print("\n=== 审计结果汇总 ===")
    for result in results:
        print(f"\n{result.tool_name}:")
        print(f"  状态: {result.status}")
        print(f"  得分: {result.score:.2f}")
        print(f"  问题数: {len(result.issues)}")
        print(f"  耗时: {result.execution_time:.2f}秒")

if __name__ == "__main__":
    main()
