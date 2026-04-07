"""
L1删除重复Layer命名文件脚本
用途：删除5个重复的Layer命名文件
创建时间：2026-04-07
"""

import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class L1DeleteDuplicateFiles:
    def __init__(self):
        self.deleted_files = []
        self.failed_files = []
        
        self.target_files = [
            "05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER8_DEEP_AUDIT_REPORT_20260407_20260407_125123.md",
            "05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/LAYER1_ARCHITECTURE_GAP_ANALYSIS_BLUEPRINT.md",
            "06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/LAYER5_BLUEPRINT_GAP_ANALYSIS_20260407_125123.md",
            "06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/LAYER6_BLUEPRINT_COMPREHENSIVE_ASSESSMENT_20260407_125123.md",
            "06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/LAYER6_GAP_ANALYSIS_REPORT_20260407_125123.md",
        ]
    
    def delete_file(self, file_path):
        try:
            if file_path.exists():
                os.remove(file_path)
                self.deleted_files.append(str(file_path.relative_to(DOCS_DIR)))
                print(f"  ✅ 删除: {file_path.name}")
                return True
            else:
                print(f"  ⚠️ 文件不存在: {file_path.name}")
                return False
        except Exception as e:
            print(f"  ❌ 删除失败: {file_path} - {e}")
            self.failed_files.append({
                "path": str(file_path.relative_to(DOCS_DIR)),
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("L1删除重复Layer命名文件")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        print(f"\n开始删除...")
        success_count = 0
        
        for i, file_rel_path in enumerate(self.target_files, 1):
            file_path = DOCS_DIR / file_rel_path
            print(f"[{i}/{len(self.target_files)}] 处理: {Path(file_rel_path).name}")
            
            if self.delete_file(file_path):
                success_count += 1
        
        print("\n" + "=" * 80)
        print("删除统计")
        print("=" * 80)
        print(f"总文件数: {len(self.target_files)}")
        print(f"成功删除: {success_count}")
        print(f"失败: {len(self.failed_files)}")
        
        if self.deleted_files:
            print("\n成功删除:")
            for path in self.deleted_files:
                print(f"  ✅ {path}")
        
        if self.failed_files:
            print("\n失败文件:")
            for item in self.failed_files:
                print(f"  ❌ {item['path']}: {item['error']}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "total": len(self.target_files),
            "success": success_count,
            "failed": len(self.failed_files)
        }

if __name__ == "__main__":
    deleter = L1DeleteDuplicateFiles()
    deleter.run()
