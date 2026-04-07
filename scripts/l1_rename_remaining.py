"""
L1-3问题修复脚本 - 修复剩余旧架构命名
用途：修复15个剩余的旧架构命名文件
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class L1RenameFixer:
    def __init__(self):
        self.renamed_files = []
        self.failed_files = []
        
    def find_old_architecture_files(self):
        print("扫描剩余旧架构文件...")
        old_files = []
        
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith('.md'):
                    if re.search(r'layer\s*[0-8]', file, re.IGNORECASE):
                        file_path = Path(root) / file
                        old_files.append(file_path)
        
        print(f"发现 {len(old_files)} 个旧架构文件")
        return old_files
    
    def generate_new_name(self, old_name):
        new_name = old_name
        
        patterns = [
            (r'layer11_', ''),
            (r'layer10_', ''),
            (r'layer9_', ''),
            (r'layer8_', ''),
            (r'layer7_', ''),
            (r'layer6_', ''),
            (r'layer5_', ''),
            (r'layer4_', ''),
            (r'layer3_', ''),
            (r'layer2_', ''),
            (r'layer1_', ''),
            (r'layer0_', ''),
            (r'Layer11_', ''),
            (r'Layer10_', ''),
            (r'Layer9_', ''),
            (r'Layer8_', ''),
            (r'Layer7_', ''),
            (r'Layer6_', ''),
            (r'Layer5_', ''),
            (r'Layer4_', ''),
            (r'Layer3_', ''),
            (r'Layer2_', ''),
            (r'Layer1_', ''),
            (r'Layer0_', ''),
        ]
        
        for pattern, replacement in patterns:
            new_name = re.sub(pattern, replacement, new_name, flags=re.IGNORECASE)
        
        return new_name
    
    def rename_file(self, file_path):
        try:
            old_name = file_path.name
            new_name = self.generate_new_name(old_name)
            
            if old_name == new_name:
                return False
            
            new_path = file_path.parent / new_name
            
            if new_path.exists():
                print(f"  ⚠️ 目标文件已存在: {new_path.name}")
                self.failed_files.append({
                    "path": str(file_path.relative_to(DOCS_DIR)),
                    "error": "目标文件已存在"
                })
                return False
            
            os.rename(file_path, new_path)
            
            self.renamed_files.append({
                "old_path": str(file_path.relative_to(DOCS_DIR)),
                "new_path": str(new_path.relative_to(DOCS_DIR)),
                "old_name": old_name,
                "new_name": new_name
            })
            
            return True
        
        except Exception as e:
            print(f"  ❌ 重命名失败: {file_path} - {e}")
            self.failed_files.append({
                "path": str(file_path.relative_to(DOCS_DIR)),
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("L1-3问题修复 - 修复剩余旧架构命名")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        old_files = self.find_old_architecture_files()
        
        print(f"\n开始重命名...")
        success_count = 0
        
        for i, file_path in enumerate(old_files, 1):
            print(f"[{i}/{len(old_files)}] 处理: {file_path.name}")
            
            if self.rename_file(file_path):
                success_count += 1
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总文件数: {len(old_files)}")
        print(f"成功重命名: {success_count}")
        print(f"失败: {len(self.failed_files)}")
        
        if self.renamed_files:
            print("\n成功重命名:")
            for item in self.renamed_files:
                print(f"  ✅ {item['old_name']}")
                print(f"     -> {item['new_name']}")
        
        if self.failed_files:
            print("\n失败文件:")
            for item in self.failed_files:
                print(f"  ❌ {item['path']}: {item['error']}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "total": len(old_files),
            "success": success_count,
            "failed": len(self.failed_files)
        }

if __name__ == "__main__":
    fixer = L1RenameFixer()
    fixer.run()
