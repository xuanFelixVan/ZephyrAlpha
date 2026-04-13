# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
P0-2问题修复脚本 - 修复职责描述
用途：修复1,418个职责描述不清的文档
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class P0ResponsibilityFixer:
    def __init__(self):
        self.fixed_files = []
        self.failed_files = []
        
    def generate_responsibility_from_path(self, file_path):
        relative_path = file_path.relative_to(DOCS_DIR)
        parts = relative_path.parts
        
        if len(parts) == 0:
            return "系统核心文档"
        
        first_dir = parts[0] if len(parts) > 0 else ""
        second_dir = parts[1] if len(parts) > 1 else ""
        
        dir_mapping = {
            "00_OVERVIEW": "系统概览、架构总览",
            "00_RESOURCES": "资源管理、平台文档",
            "01_FRAMEWORK": "系统框架、架构设计",
            "02_FACTOR_LIBRARY": "因子计算、因子库管理",
            "03_TRADING_TACTICS": "交易策略、战术执行",
            "04_DATA_SOURCES": "数据源管理、数据接入",
            "05_IMPLEMENTATION": "实施指南、部署文档",
            "06_ARCHIVE": "归档文档、历史版本",
            "07_TESTS": "测试文档、质量保证",
            "08_API": "API文档、接口规范",
            "09_AUDIT": "审计报告、合规检查",
            "09_RESEARCH_INNOVATION": "研究创新、技术探索"
        }
        
        if first_dir in dir_mapping:
            base_resp = dir_mapping[first_dir]
            
            if "audit_state" in str(relative_path):
                return f"{base_resp}、审计状态追踪"
            elif "technical_reviews" in str(relative_path):
                return f"{base_resp}、技术评审"
            elif "blueprints" in str(relative_path):
                return f"{base_resp}、蓝图设计"
            elif "standards" in str(relative_path):
                return f"{base_resp}、标准规范"
            
            return base_resp
        
        file_name = file_path.stem
        
        if "BLUEPRINT" in file_name.upper():
            return "蓝图设计、架构规划"
        elif "AUDIT" in file_name.upper():
            return "审计报告、合规检查"
        elif "REPORT" in file_name.upper():
            return "报告文档、状态追踪"
        elif "GUIDE" in file_name.upper():
            return "实施指南、操作手册"
        elif "API" in file_name.upper():
            return "API文档、接口规范"
        elif "TEST" in file_name.upper():
            return "测试文档、质量保证"
        elif "README" in file_name.upper():
            return "说明文档、快速入门"
        elif "INDEX" in file_name.upper():
            return "索引文档、导航目录"
        
        return "扩展功能、辅助模块"
    
    def fix_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            
            if not yaml_match:
                new_responsibility = self.generate_responsibility_from_path(file_path)
                
                yaml_header = f"""---
responsibility:
  - {new_responsibility}
module_id: AUTO_GENERATED_{datetime.now().strftime('%Y%m%d%H%M%S')}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 个人开发者
standard_type: 专业量化机构文档
---

"""
                
                new_content = yaml_header + content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.fixed_files.append({
                    "path": str(file_path.relative_to(DOCS_DIR)),
                    "action": "添加YAML头部",
                    "responsibility": new_responsibility
                })
                
                return True
            
            yaml_content = yaml_match.group(1)
            
            resp_match = re.search(r'responsibility:\s*\n?\s*-\s*(.+?)(?:\n|$)', yaml_content, re.MULTILINE)
            
            if resp_match:
                current_responsibility = resp_match.group(1).strip()
                
                if len(current_responsibility) < 10 or current_responsibility in ['扩展功能、辅助模块', '核心功能、主模块']:
                    new_responsibility = self.generate_responsibility_from_path(file_path)
                    
                    new_yaml_content = re.sub(
                        r'responsibility:\s*\n?\s*-\s*.+?(?:\n|$)',
                        f'responsibility:\n  - {new_responsibility}\n',
                        yaml_content,
                        flags=re.MULTILINE
                    )
                    
                    new_content = content.replace(yaml_content, new_yaml_content)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.fixed_files.append({
                        "path": str(file_path.relative_to(DOCS_DIR)),
                        "action": "更新职责描述",
                        "old_responsibility": current_responsibility,
                        "new_responsibility": new_responsibility
                    })
                    
                    return True
            
            return False
        
        except Exception as e:
            print(f"  ❌ 修复失败: {file_path} - {e}")
            self.failed_files.append({
                "path": str(file_path.relative_to(DOCS_DIR)),
                "error": str(e)
            })
            return False
    
    def scan_and_fix(self):
        print("扫描需要修复职责描述的文件...")
        
        unclear_files = []
        
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                        
                        if not yaml_match:
                            unclear_files.append(file_path)
                            continue
                        
                        yaml_content = yaml_match.group(1)
                        resp_match = re.search(r'responsibility:\s*\n?\s*-\s*(.+?)(?:\n|$)', yaml_content, re.MULTILINE)
                        
                        if resp_match:
                            current_responsibility = resp_match.group(1).strip()
                            
                            if len(current_responsibility) < 10 or current_responsibility in ['扩展功能、辅助模块', '核心功能、主模块']:
                                unclear_files.append(file_path)
                    
                    except Exception as e:
                        pass
        
        print(f"发现 {len(unclear_files)} 个需要修复的文件")
        
        return unclear_files
    
    def run(self):
        print("=" * 80)
        print("P0-2问题修复 - 修复职责描述")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        unclear_files = self.scan_and_fix()
        
        print(f"\n开始修复...")
        success_count = 0
        
        for i, file_path in enumerate(unclear_files, 1):
            print(f"[{i}/{len(unclear_files)}] 处理: {file_path.name}")
            
            if self.fix_file(file_path):
                success_count += 1
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总文件数: {len(unclear_files)}")
        print(f"成功修复: {success_count}")
        print(f"失败: {len(self.failed_files)}")
        
        if self.fixed_files:
            print("\n成功修复示例:")
            for item in self.fixed_files[:10]:
                print(f"  ✅ {item['path']}")
                if 'old_responsibility' in item:
                    print(f"     旧职责: {item['old_responsibility']}")
                print(f"     新职责: {item['new_responsibility']}")
        
        if self.failed_files:
            print("\n失败文件:")
            for item in self.failed_files[:10]:
                print(f"  ❌ {item['path']}: {item['error']}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "total": len(unclear_files),
            "success": success_count,
            "failed": len(self.failed_files),
            "fixed_files": self.fixed_files,
            "failed_files": self.failed_files
        }

if __name__ == "__main__":
    fixer = P0ResponsibilityFixer()
    fixer.run()
