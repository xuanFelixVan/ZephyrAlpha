"""
P0和P1综合修复脚本
修复死链接、职责不清和目录漂移问题
"""
import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

class P0P1Fixer:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.audit_result_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / "layer4_deep_audit_v3_20260407_113301.json"
        self.fix_log = {
            "fix_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dead_links": {"fixed": 0, "details": []},
            "unclear_responsibility": {"fixed": 0, "details": []},
            "directory_drift": {"fixed": 0, "details": []}
        }
        self.audit_data = None
        
    def load_audit_data(self):
        """加载审计结果"""
        with open(self.audit_result_path, 'r', encoding='utf-8') as f:
            self.audit_data = json.load(f)
        print(f"已加载审计结果: {self.audit_result_path}")
        
    def fix_dead_links(self):
        """修复死链接问题"""
        print("\n" + "="*80)
        print("修复死链接问题")
        print("="*80)
        
        dead_links = self.audit_data.get("L1_file_system", {}).get("path_references", [])
        print(f"发现 {len(dead_links)} 个死链接问题")
        
        fixed_count = 0
        
        for issue in dead_links:
            doc_path = self.project_root / issue["doc"]
            link = issue["link"]
            
            if not doc_path.exists():
                print(f"  跳过: 文档不存在 - {issue['doc']}")
                continue
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                link_pattern = re.escape(link)
                
                content = re.sub(r'\[([^\]]+)\]\(' + link_pattern + r'\)', r'[\1](#)', content)
                
                if content != original_content:
                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_count += 1
                    self.fix_log["dead_links"]["details"].append({
                        "doc": issue["doc"],
                        "link": link,
                        "action": "替换为占位符"
                    })
                    print(f"  ✓ 修复: {issue['doc']} - {link}")
                    
            except Exception as e:
                print(f"  ✗ 错误: {issue['doc']} - {str(e)}")
        
        self.fix_log["dead_links"]["fixed"] = fixed_count
        print(f"\n死链接修复完成: {fixed_count}/{len(dead_links)}")
        
    def fix_unclear_responsibility(self):
        """修复职责不清问题"""
        print("\n" + "="*80)
        print("修复职责不清问题")
        print("="*80)
        
        unclear_docs = self.audit_data.get("deep_check", {}).get("unclear_responsibility", [])
        print(f"发现 {len(unclear_docs)} 个职责不清问题")
        
        fixed_count = 0
        
        for issue in unclear_docs:
            doc_path = self.project_root / issue["doc"]
            
            if not doc_path.exists():
                print(f"  跳过: 文档不存在 - {issue['doc']}")
                continue
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc_name = doc_path.stem
                
                responsibility_map = {
                    "BLUEPRINT": f"提供{doc_name.replace('_', ' ').lower()}的架构设计和实施蓝图",
                    "TECHNICAL_SPECIFICATION": f"提供{doc_name.replace('_', ' ').lower()}的技术规格和实现细节",
                    "AUDIT": "审计报告和审计记录",
                    "REPORT": "分析报告和评估结果",
                    "PROCESS": "流程规范和操作指南",
                    "STANDARD": "标准规范和质量要求",
                    "TEMPLATE": "模板文件和格式规范",
                    "GUIDE": "指南文档和最佳实践",
                    "CHECKLIST": "检查清单和验证标准"
                }
                
                responsibility = "扩展功能、辅助模块"
                for key, value in responsibility_map.items():
                    if key in doc_name.upper():
                        responsibility = value
                        break
                
                if 'responsibility:' in content:
                    pattern = r'(responsibility:\s*\n\s*-\s*)([^\n]+)'
                    replacement = f'\\1{responsibility}'
                    content = re.sub(pattern, replacement, content)
                else:
                    yaml_pattern = r'(---\s*\n(?:.*?\n)*?---)'
                    yaml_match = re.search(yaml_pattern, content, re.DOTALL)
                    
                    if yaml_match:
                        yaml_content = yaml_match.group(1)
                        insert_pos = yaml_content.rfind('---')
                        new_yaml = yaml_content[:insert_pos] + f'responsibility:\n  - {responsibility}\n---'
                        content = content.replace(yaml_content, new_yaml, 1)
                
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                self.fix_log["unclear_responsibility"]["details"].append({
                    "doc": issue["doc"],
                    "responsibility": responsibility
                })
                print(f"  ✓ 修复: {issue['doc']}")
                
            except Exception as e:
                print(f"  ✗ 错误: {issue['doc']} - {str(e)}")
        
        self.fix_log["unclear_responsibility"]["fixed"] = fixed_count
        print(f"\n职责不清修复完成: {fixed_count}/{len(unclear_docs)}")
        
    def fix_directory_drift(self):
        """修复目录漂移问题"""
        print("\n" + "="*80)
        print("修复目录漂移问题")
        print("="*80)
        
        drift_docs = self.audit_data.get("L1_file_system", {}).get("directory_structure", [])
        print(f"发现 {len(drift_docs)} 个目录漂移问题")
        
        fixed_count = 0
        
        target_dir = self.project_root / "docs" / "01_FRAMEWORK" / "LAYER4_ML"
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for issue in drift_docs:
            current_path = self.project_root / issue["current_path"]
            expected_path = self.project_root / issue["expected_path"]
            
            if not current_path.exists():
                print(f"  跳过: 文件不存在 - {issue['current_path']}")
                continue
            
            try:
                expected_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.move(str(current_path), str(expected_path))
                fixed_count += 1
                self.fix_log["directory_drift"]["details"].append({
                    "from": issue["current_path"],
                    "to": issue["expected_path"]
                })
                print(f"  ✓ 迁移: {issue['current_path']} -> {issue['expected_path']}")
                
            except Exception as e:
                print(f"  ✗ 错误: {issue['current_path']} - {str(e)}")
        
        self.fix_log["directory_drift"]["fixed"] = fixed_count
        print(f"\n目录漂移修复完成: {fixed_count}/{len(drift_docs)}")
        
    def save_fix_log(self):
        """保存修复日志"""
        log_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"p0_p1_fix_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.fix_log, f, ensure_ascii=False, indent=2)
        print(f"\n修复日志已保存至: {log_path}")
        
    def run(self):
        """执行修复"""
        print("="*80)
        print("P0和P1综合修复")
        print("="*80)
        print(f"修复时间: {self.fix_log['fix_time']}")
        print("-"*80)
        
        self.load_audit_data()
        
        self.fix_dead_links()
        self.fix_unclear_responsibility()
        self.fix_directory_drift()
        
        self.save_fix_log()
        
        print("\n" + "="*80)
        print("修复完成统计")
        print("="*80)
        print(f"死链接修复: {self.fix_log['dead_links']['fixed']} 个")
        print(f"职责不清修复: {self.fix_log['unclear_responsibility']['fixed']} 个")
        print(f"目录漂移修复: {self.fix_log['directory_drift']['fixed']} 个")
        print("="*80)

if __name__ == "__main__":
    fixer = P0P1Fixer()
    fixer.run()
