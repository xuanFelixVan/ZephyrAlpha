"""
P1-3问题修复脚本 - 修复Module ID重复
用途：修复18个Module ID重复的文件
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class P1ModuleIdFixer:
    def __init__(self):
        self.fixed_ids = []
        self.failed_ids = []
        self.module_ids = {}
        
    def find_duplicate_module_ids(self):
        print("扫描Module ID重复...")
        duplicate_ids = []
        
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
                            
                            module_match = re.search(r'module_id:\s*(.+?)(?:\n|$)', yaml_content, re.MULTILINE)
                            if module_match:
                                module_id = module_match.group(1).strip()
                                
                                if module_id in self.module_ids:
                                    duplicate_ids.append({
                                        "module_id": module_id,
                                        "file1": self.module_ids[module_id],
                                        "file2": str(file_path.relative_to(DOCS_DIR)),
                                        "file2_path": file_path
                                    })
                                else:
                                    self.module_ids[module_id] = str(file_path.relative_to(DOCS_DIR))
                    
                    except Exception as e:
                        pass
        
        print(f"发现 {len(duplicate_ids)} 个重复的Module ID")
        return duplicate_ids
    
    def generate_unique_module_id(self, file_path):
        relative_path = file_path.relative_to(DOCS_DIR)
        
        path_parts = relative_path.parts
        
        if len(path_parts) > 0:
            first_dir = path_parts[0].upper()
            file_name = file_path.stem.upper()
            
            file_name = re.sub(r'[^A-Z0-9_]', '_', file_name)
            
            module_id = f"{first_dir}_{file_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return module_id
        
        return f"AUTO_GENERATED_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def fix_module_id(self, file_path, old_module_id):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_module_id = self.generate_unique_module_id(file_path)
            
            new_content = re.sub(
                r'module_id:\s*' + re.escape(old_module_id),
                f'module_id: {new_module_id}',
                content
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.fixed_ids.append({
                "file": str(file_path.relative_to(DOCS_DIR)),
                "old_module_id": old_module_id,
                "new_module_id": new_module_id
            })
            
            return True
        
        except Exception as e:
            print(f"  ❌ 修复失败: {file_path} - {e}")
            self.failed_ids.append({
                "file": str(file_path.relative_to(DOCS_DIR)),
                "module_id": old_module_id,
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("P1-3问题修复 - 修复Module ID重复")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        duplicate_ids = self.find_duplicate_module_ids()
        
        print(f"\n开始修复...")
        success_count = 0
        
        for i, dup_info in enumerate(duplicate_ids, 1):
            print(f"[{i}/{len(duplicate_ids)}] 处理: {dup_info['file2']}")
            print(f"  Module ID: {dup_info['module_id']}")
            
            if self.fix_module_id(dup_info['file2_path'], dup_info['module_id']):
                success_count += 1
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总重复数: {len(duplicate_ids)}")
        print(f"成功修复: {success_count}")
        print(f"失败: {len(self.failed_ids)}")
        
        if self.fixed_ids:
            print("\n成功修复示例:")
            for item in self.fixed_ids[:10]:
                print(f"  ✅ {item['file']}")
                print(f"     {item['old_module_id']} -> {item['new_module_id']}")
        
        if self.failed_ids:
            print("\n失败文件:")
            for item in self.failed_ids[:10]:
                print(f"  ❌ {item['file']}: {item['error']}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "total": len(duplicate_ids),
            "success": success_count,
            "failed": len(self.failed_ids),
            "fixed_ids": self.fixed_ids,
            "failed_ids": self.failed_ids
        }

if __name__ == "__main__":
    fixer = P1ModuleIdFixer()
    fixer.run()
