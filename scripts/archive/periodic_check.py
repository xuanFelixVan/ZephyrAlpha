#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
定期检查脚本
整合所有检查功能
"""

import subprocess
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')
SCRIPTS_DIR = Path(r'D:\ZephyrAlpha\scripts')

def run_check(script_name, check_name):
    """运行检查脚本"""
    print(f"\n{'=' * 80}")
    print(f"执行: {check_name}")
    print('=' * 80)
    
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        print(f"脚本不存在: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            ['python', str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"错误: {result.stderr}")
            return False
        
        return True
    
    except Exception as e:
        print(f"执行失败: {e}")
        return False

def generate_summary_report(results):
    """生成总结报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'PERIODIC_CHECK_SUMMARY_{timestamp}.md'
    
    report_content = f"""---
module_id: PERIODIC_CHECK_SUMMARY_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 检查报告
applicable_scope: 定期检查总结
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 定期检查总结报告

> **核心职责**: 记录定期检查的执行情况和结果
> **职责边界**: 
> - [OK] 本文档负责：检查总结、效果评估、后续建议
> - [NO] 本文档不负责：具体检查执行、问题修复

---

## 检查概要

**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**检查范围**: 全系统文档  
**检查方法**: 自动化检查  
**检查结论**: {'成功' if all(results.values()) else '部分失败'}

---

## 检查统计

| 检查项 | 状态 | 结果 |
|--------|------|------|
"""
    
    for check_name, success in results.items():
        status = '✅ 成功' if success else '❌ 失败'
        report_content += f"| **{check_name}** | {status} | {'完成' if success else '失败'} |\n"
    
    report_content += f"""
---

## 后续建议

### 立即行动

1. [ ] 查看详细检查报告
2. [ ] 处理发现的问题
3. [ ] 验证修复效果

### 持续改进

1. [ ] 定期执行检查
2. [ ] 持续优化文档质量
3. [ ] 建立质量监控体系

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，定期检查总结报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n总结报告已生成: {report_path}")
    return report_path

def main():
    """主函数"""
    print("=" * 80)
    print("定期检查")
    print("=" * 80)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 定义检查项
    checks = [
        ('check_metadata_completeness.py', '元数据完整性检查'),
        ('quality_metrics_monitoring.py', '质量指标监控'),
    ]
    
    # 执行检查
    results = {}
    for script_name, check_name in checks:
        results[check_name] = run_check(script_name, check_name)
    
    # 生成总结报告
    report_path = generate_summary_report(results)
    
    print("\n" + "=" * 80)
    print("定期检查完成")
    print("=" * 80)
    print(f"检查项数: {len(results)}")
    print(f"成功项数: {sum(results.values())}")
    print(f"失败项数: {len(results) - sum(results.values())}")
    print(f"总结报告: {report_path}")

if __name__ == '__main__':
    main()
