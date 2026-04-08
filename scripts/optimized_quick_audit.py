#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版快速审计工具
实现并行扫描和缓存机制
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

DOCS_DIR = Path("D:/ZephyrAlpha/docs")
CACHE_DIR = Path("D:/ZephyrAlpha/.audit_cache")
REPORTS_DIR = DOCS_DIR / "09_AUDIT/REPORTS"
STATE_DIR = DOCS_DIR / "09_AUDIT/STATE"

class OptimizedQuickAuditor:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.cache_file = CACHE_DIR / "quick_audit_cache.json"
        self.report_file = REPORTS_DIR / f"OPTIMIZED_QUICK_AUDIT_REPORT_{self.timestamp}.md"
        self.state_file = STATE_DIR / f"optimized_quick_audit_state_{self.timestamp}.json"
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'audit_type': 'optimized_quick',
            'total_files': 0,
            'total_issues': 0,
            'compliance_rate': 0.0,
            'audit_time': 0,
            'issues': {
                'P0': [],
                'P1': [],
                'P2': [],
                'P3': []
            }
        }
        
        self.file_hashes = {}
        self.cache_data = {}
        
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_cache(self):
        """加载缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache_data = json.load(f)
                print(f"✅ 加载缓存: {len(self.cache_data)} 条记录")
            except Exception as e:
                print(f"⚠️ 缓存加载失败: {e}")
                self.cache_data = {}
    
    def save_cache(self):
        """保存缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 保存缓存: {len(self.cache_data)} 条记录")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")
    
    def calculate_file_hash(self, file_path):
        """计算文件哈希"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            return None
    
    def check_file_with_cache(self, file_path):
        """使用缓存检查文件"""
        file_hash = self.calculate_file_hash(file_path)
        if not file_hash:
            return None
        
        self.file_hashes[str(file_path)] = file_hash
        
        if str(file_path) in self.cache_data:
            cached_hash = self.cache_data[str(file_path)].get('hash')
            if cached_hash == file_hash:
                return self.cache_data[str(file_path)].get('result', {})
        
        return None
    
    def check_critical_docs_parallel(self):
        """并行检查关键文档"""
        print("\n[1/3] 并行检查关键文档...")
        
        critical_docs = [
            "System_Manifest.md",
            "INDEX.md",
            "SITEMAP.md"
        ]
        
        def check_doc(doc):
            doc_path = DOCS_DIR / doc
            if not doc_path.exists():
                return {
                    'doc': doc,
                    'status': 'missing',
                    'issue': {
                        'type': 'missing_critical_doc',
                        'file': doc,
                        'message': f'关键文档缺失: {doc}'
                    }
                }
            return {
                'doc': doc,
                'status': 'exists',
                'issue': None
            }
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(check_doc, doc): doc for doc in critical_docs}
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        for result in results:
            if result['status'] == 'missing':
                self.results['issues']['P1'].append(result['issue'])
                print(f"  ❌ {result['doc']} - 缺失")
            else:
                print(f"  ✅ {result['doc']} - 存在")
    
    def check_index_completeness_parallel(self):
        """并行检查索引完整性"""
        print("\n[2/3] 并行检查索引完整性...")
        
        dirs = [d for d in DOCS_DIR.rglob("*") if d.is_dir() 
                and 'archive' not in str(d).lower() 
                and '_archive' not in str(d).lower()
                and '.git' not in str(d)]
        
        def check_dir_index(dir_path):
            index_file = dir_path / "INDEX.md"
            return {
                'dir': str(dir_path.relative_to(DOCS_DIR)),
                'has_index': index_file.exists()
            }
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(check_dir_index, d): d for d in dirs}
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        total_dirs = len(results)
        dirs_with_index = sum(1 for r in results if r['has_index'])
        index_coverage = dirs_with_index / total_dirs * 100 if total_dirs > 0 else 0
        
        print(f"  索引覆盖率: {index_coverage:.2f}%")
        
        if index_coverage < 95:
            self.results['issues']['P2'].append({
                'type': 'low_index_coverage',
                'coverage': index_coverage,
                'message': f'索引覆盖率过低: {index_coverage:.2f}%'
            })
    
    def check_recent_files_parallel(self):
        """并行检查最近修改的文件"""
        print("\n[3/3] 并行检查最近修改的文件...")
        
        cutoff_time = datetime.now() - timedelta(days=1)
        md_files = list(DOCS_DIR.rglob("*.md"))
        
        recent_files = []
        for md_file in md_files:
            if md_file.stat().st_mtime > cutoff_time.timestamp():
                recent_files.append(md_file)
        
        print(f"  最近24小时修改的文档: {len(recent_files)}个")
        
        def check_file(file_path):
            cached_result = self.check_file_with_cache(file_path)
            if cached_result:
                return cached_result
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues = []
                
                if not re.search(r'module_id:', content):
                    issues.append({
                        'type': 'missing_module_id',
                        'file': str(file_path.relative_to(DOCS_DIR)),
                        'message': f'缺少module_id: {file_path.name}'
                    })
                
                result = {
                    'file': str(file_path.relative_to(DOCS_DIR)),
                    'issues': issues
                }
                
                self.cache_data[str(file_path)] = {
                    'hash': self.file_hashes.get(str(file_path)),
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                
                return result
            except Exception as e:
                return {
                    'file': str(file_path.relative_to(DOCS_DIR)),
                    'issues': []
                }
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(check_file, f): f for f in recent_files[:20]}
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        for result in results:
            for issue in result.get('issues', []):
                self.results['issues']['P2'].append(issue)
    
    def run_audit(self):
        """执行优化版快速审计"""
        start_time = datetime.now()
        
        print("=" * 80)
        print("优化版快速审计 - 并行处理 + 缓存机制")
        print("=" * 80)
        
        self.load_cache()
        
        self.check_critical_docs_parallel()
        self.check_index_completeness_parallel()
        self.check_recent_files_parallel()
        
        self.results['total_files'] = len(list(DOCS_DIR.rglob("*.md")))
        self.results['total_issues'] = sum(len(v) for v in self.results['issues'].values())
        self.results['compliance_rate'] = (self.results['total_files'] - self.results['total_issues']) / self.results['total_files'] * 100
        
        end_time = datetime.now()
        self.results['audit_time'] = (end_time - start_time).total_seconds()
        
        print(f"\n合规率: {self.results['compliance_rate']:.2f}%")
        print(f"审计时间: {self.results['audit_time']:.2f}秒")
        
        self.save_cache()
        self.generate_report()
        self.save_state()
        
        print(f"\n优化版快速审计完成！")
    
    def generate_report(self):
        """生成审计报告"""
        report = f"""# 优化版快速审计报告

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**审计类型**: 优化版快速审计（并行 + 缓存）
**审计时间**: {self.results['audit_time']:.2f}秒

---

## 📊 审计结果

| 指标 | 数值 |
|------|------|
| **总文件数** | {self.results['total_files']} |
| **总问题数** | {self.results['total_issues']} |
| **合规率** | {self.results['compliance_rate']:.2f}% |
| **审计时间** | {self.results['audit_time']:.2f}秒 |

---

## 🔍 问题分布

| 优先级 | 数量 |
|--------|------|
| **P0（严重）** | {len(self.results['issues']['P0'])} |
| **P1（重要）** | {len(self.results['issues']['P1'])} |
| **P2（次要）** | {len(self.results['issues']['P2'])} |
| **P3（建议）** | {len(self.results['issues']['P3'])} |

---

## ✅ 审计结论

- **合规率**: {self.results['compliance_rate']:.2f}%
- **审计状态**: {'✅ 通过' if self.results['compliance_rate'] >= 99.5 else '⚠️ 需要改进'}
- **性能提升**: 使用并行处理和缓存机制

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n审计报告已保存至: {self.report_file}")
    
    def save_state(self):
        """保存审计状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"审计状态已保存至: {self.state_file}")

if __name__ == "__main__":
    auditor = OptimizedQuickAuditor()
    auditor.run_audit()
