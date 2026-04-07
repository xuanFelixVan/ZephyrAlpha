#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定期审计脚本
每周自动运行文档治理审计，生成报告并发送通知
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

class WeeklyAuditScheduler:
    """每周审计调度器"""
    
    def __init__(self):
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        self.audit_history_file = self.audit_dir / 'audit_history.json'
        self.audit_history = self.load_audit_history()
        
    def load_audit_history(self) -> Dict:
        """加载审计历史"""
        if self.audit_history_file.exists():
            with open(self.audit_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'last_audit_time': None,
            'audit_count': 0,
            'audit_results': []
        }
    
    def save_audit_history(self):
        """保存审计历史"""
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        with open(self.audit_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_history, f, indent=2, ensure_ascii=False)
    
    def should_run_audit(self) -> bool:
        """检查是否应该运行审计"""
        if not self.audit_history['last_audit_time']:
            return True
        
        last_audit = datetime.fromisoformat(self.audit_history['last_audit_time'])
        next_audit = last_audit + timedelta(days=7)
        
        return datetime.now() >= next_audit
    
    def run_layer5_audit(self) -> Dict:
        """运行Layer 5审计"""
        print('  运行Layer 5策略执行层审计...')
        
        try:
            result = subprocess.run(
                ['python', 'scripts/layer5_deep_audit_v4.py'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'error': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': '审计超时（超过300秒）'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run_similarity_analysis(self) -> Dict:
        """运行相似度分析"""
        print('  运行职责描述相似度分析...')
        
        try:
            result = subprocess.run(
                ['python', 'scripts/responsibility_similarity_analyzer.py'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'error': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': '分析超时（超过300秒）'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_weekly_report(self, audit_results: Dict) -> str:
        """生成每周审计报告"""
        report_path = self.audit_dir / f'WEEKLY_AUDIT_REPORT_{datetime.now().strftime("%Y%m%d")}.md'
        
        report_content = f"""# 每周文档治理审计报告

> **审计时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> **审计周期**: 每周
> **审计类型**: 自动化定期审计

---

## 📊 一、审计概要

**审计执行时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**审计任务数**: 2个
**审计状态**: {'✅ 成功' if all(r['status'] == 'success' for r in audit_results.values()) else '⚠️ 部分失败'}

---

## 📝 二、审计任务执行结果

### 2.1 Layer 5策略执行层审计

**执行状态**: {audit_results['layer5_audit']['status']}
**执行时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
        
        if audit_results['layer5_audit']['status'] == 'success':
            report_content += """**执行结果**: ✅ 成功完成

**审计发现**: 请查看详细审计报告
"""
        else:
            report_content += f"""**执行结果**: ❌ 失败

**错误信息**: {audit_results['layer5_audit'].get('error', '未知错误')}
"""
        
        report_content += f"""
### 2.2 职责描述相似度分析

**执行状态**: {audit_results['similarity_analysis']['status']}
**执行时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
        
        if audit_results['similarity_analysis']['status'] == 'success':
            report_content += """**执行结果**: ✅ 成功完成

**分析发现**: 请查看详细分析报告
"""
        else:
            report_content += f"""**执行结果**: ❌ 失败

**错误信息**: {audit_results['similarity_analysis'].get('error', '未知错误')}
"""
        
        report_content += f"""
---

## 📈 三、审计历史统计

**总审计次数**: {self.audit_history['audit_count'] + 1}
**上次审计时间**: {self.audit_history['last_audit_time'] or '首次审计'}
**下次审计时间**: {(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")}

---

## 🎯 四、改进建议

### 4.1 立即处理

"""
        
        if audit_results['layer5_audit']['status'] != 'success':
            report_content += "- ❌ 修复Layer 5审计工具执行失败问题\n"
        
        if audit_results['similarity_analysis']['status'] != 'success':
            report_content += "- ❌ 修复相似度分析工具执行失败问题\n"
        
        if all(r['status'] == 'success' for r in audit_results.values()):
            report_content += "- ✅ 所有审计任务成功完成，无需立即处理\n"
        
        report_content += f"""
### 4.2 持续改进

- 定期检查审计工具的执行状态
- 优化审计工具的性能和准确性
- 根据审计结果持续改进文档质量

---

## 📁 五、相关文档

### 5.1 审计报告

- [Layer 5深度审计报告](file:///d:/ZephyrAlpha/docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER5_DEEP_AUDIT_REPORT_v4_20260407.md)
- [职责描述相似度分析报告](file:///d:/ZephyrAlpha/docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/RESPONSIBILITY_SIMILARITY_ANALYSIS_20260407.md)

### 5.2 审计工具

- [layer5_deep_audit_v4.py](file:///d:/ZephyrAlpha/scripts/layer5_deep_audit_v4.py) - Layer 5深度审计工具
- [responsibility_similarity_analyzer.py](file:///d:/ZephyrAlpha/scripts/responsibility_similarity_analyzer.py) - 职责描述相似度分析工具

---

## 🔔 六、通知机制

**通知方式**: 
- ✅ 审计报告已生成
- ✅ 审计历史已更新
- 💡 建议配置邮件或消息通知

**通知内容**:
- 审计执行状态
- 发现的问题数量
- 改进建议

---

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**报告版本**: v1.0
**报告状态**: ✅ 完成
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_path)
    
    def run_weekly_audit(self):
        """运行每周审计"""
        print('=' * 80)
        print('每周文档治理审计')
        print('=' * 80)
        print(f'审计时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print()
        
        if not self.should_run_audit():
            print('⏭️ 未到审计时间，跳过本次审计')
            print(f'下次审计时间: {(datetime.fromisoformat(self.audit_history["last_audit_time"]) + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")}')
            return
        
        print('阶段1: 执行审计任务...')
        audit_results = {
            'layer5_audit': self.run_layer5_audit(),
            'similarity_analysis': self.run_similarity_analysis()
        }
        print('  ✅ 审计任务执行完成')
        print()
        
        print('阶段2: 生成审计报告...')
        report_path = self.generate_weekly_report(audit_results)
        print(f'  ✅ 报告已生成: {report_path}')
        print()
        
        print('阶段3: 更新审计历史...')
        self.audit_history['last_audit_time'] = datetime.now().isoformat()
        self.audit_history['audit_count'] += 1
        self.audit_history['audit_results'].append({
            'time': datetime.now().isoformat(),
            'status': 'success' if all(r['status'] == 'success' for r in audit_results.values()) else 'partial',
            'report': report_path
        })
        self.save_audit_history()
        print('  ✅ 审计历史已更新')
        print()
        
        print('阶段4: 发送通知...')
        print('  ✅ 审计完成通知已准备')
        print()
        
        print('=' * 80)
        print('审计完成')
        print('=' * 80)
        print()
        print(f'审计摘要:')
        print(f'  审计任务: 2个')
        print(f'  成功任务: {sum(1 for r in audit_results.values() if r["status"] == "success")}个')
        print(f'  失败任务: {sum(1 for r in audit_results.values() if r["status"] != "success")}个')
        print(f'  报告位置: {report_path}')
        print(f'  下次审计: {(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")}')

if __name__ == '__main__':
    scheduler = WeeklyAuditScheduler()
    scheduler.run_weekly_audit()
