# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
L2职责描述批量优化脚本V2
用途：继续优化职责描述（500个）
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class L2ResponsibilityBatchFixerV2:
    def __init__(self):
        self.fixed_files = []
        self.failed_files = []
        
    def get_responsibility_from_path(self, file_path):
        relative_path = file_path.relative_to(DOCS_DIR)
        path_parts = relative_path.parts
        
        responsibility_map = {
            '00_OVERVIEW': '系统概览、架构总览、文档索引',
            '00_RESOURCES': '资源管理、平台文档、外部资源',
            '01_FRAMEWORK': '系统框架、架构设计、核心模块',
            '02_FACTOR_LIBRARY': '因子库、因子开发、因子管理',
            '03_TRADING_TACTICS': '交易策略、战术设计、策略实现',
            '04_DATA_PIPELINE': '数据管道、数据流、数据处理',
            '04_EXECUTION': '执行引擎、订单执行、交易执行',
            '05_IMPLEMENTATION': '实施指南、部署文档、操作手册',
            '06_ARCHIVE': '归档文档、历史版本、备份文件',
            '07_BACKTESTING': '回测系统、回测框架、回测报告',
            '08_PRODUCTION': '生产环境、系统运维、监控告警',
            '09_AUDIT': '审计报告、合规检查、质量评估',
            '09_RESEARCH_INNOVATION': '研究创新、新技术、实验性功能',
            '10_AI_WORKFLOW': 'AI工作流、智能辅助、自动化流程',
        }
        
        for part in path_parts:
            if part in responsibility_map:
                return responsibility_map[part]
        
        if 'BLUEPRINT' in str(file_path).upper():
            return '蓝图设计、架构规划、技术方案'
        elif 'SPECIFICATION' in str(file_path).upper():
            return '技术规范、实现标准、接口定义'
        elif 'MANUAL' in str(file_path).upper():
            return '操作手册、使用指南、流程文档'
        elif 'REPORT' in str(file_path).upper():
            return '分析报告、评估结果、审计发现'
        elif 'ARCHITECTURE' in str(file_path).upper():
            return '架构设计、系统结构、模块关系'
        else:
            return '扩展功能、辅助模块、支撑文档'
    
    def find_unclear_responsibility_files(self):
        print("扫描职责不清文件...")
        unclear_files = []
        
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                        
                        if yaml_match:
                            yaml_content = yaml_match.group(1)
                            
                            resp_match = re.search(r'responsibility:\s*\n?\s*-\s*(.+?)(?:\n|$)', yaml_content)
                            
                            if resp_match:
                                responsibility = resp_match.group(1).strip()
                                
                                if responsibility in ['扩展功能、辅助模块', '核心功能、主模块', '扩展功能、辅助模块、支撑文档']:
                                    relative_path = file_path.relative_to(DOCS_DIR)
                                    unclear_files.append({
                                        "path": str(relative_path),
                                        "file_path": file_path,
                                        "current_resp": responsibility
                                    })
                    
                    except Exception as e:
                        pass
        
        print(f"发现 {len(unclear_files)} 个职责不清文件")
        return unclear_files
    
    def fix_responsibility(self, file_info):
        try:
            file_path = file_info["file_path"]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_responsibility = self.get_responsibility_from_path(file_path)
            
            content = re.sub(
                r'(responsibility:\s*\n?\s*-\s*)(.+?)(\n)',
                f'\\1{new_responsibility}\\3',
                content
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixed_files.append({
                "path": file_info["path"],
                "old_resp": file_info["current_resp"],
                "new_resp": new_responsibility
            })
            
            return True
        
        except Exception as e:
            self.failed_files.append({
                "path": file_info["path"],
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("L2职责描述批量优化V2")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        unclear_files = self.find_unclear_responsibility_files()
        
        print(f"\n开始优化（处理前500个）...")
        success_count = 0
        
        for i, file_info in enumerate(unclear_files[:500], 1):
            if i % 100 == 0:
                print(f"[{i}/500] 已处理 {i} 个文件...")
            
            if self.fix_responsibility(file_info):
                success_count += 1
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总职责不清文件: {len(unclear_files)}")
        print(f"本次处理: {min(500, len(unclear_files))}个")
        print(f"成功优化: {success_count}")
        print(f"失败: {len(self.failed_files)}")
        
        if self.fixed_files:
            print("\n成功优化示例:")
            for item in self.fixed_files[:10]:
                print(f"  ✅ {item['path']}")
                print(f"     {item['old_resp']} -> {item['new_resp']}")
        
        if self.failed_files:
            print("\n失败文件:")
            for item in self.failed_files[:10]:
                print(f"  ❌ {item['path']}: {item['error']}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "total": len(unclear_files),
            "processed": min(500, len(unclear_files)),
            "success": success_count,
            "failed": len(self.failed_files)
        }

if __name__ == "__main__":
    fixer = L2ResponsibilityBatchFixerV2()
    fixer.run()
