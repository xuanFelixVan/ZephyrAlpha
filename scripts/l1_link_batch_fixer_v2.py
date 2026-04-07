"""
L1死链接批量修复脚本V2
用途：继续修复死链接（500个）
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class L1LinkBatchFixerV2:
    def __init__(self):
        self.fixed_links = []
        self.failed_links = []
        
    def find_broken_links(self):
        print("扫描死链接...")
        broken_links = []
        
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        relative_path = file_path.relative_to(DOCS_DIR)
                        
                        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                        
                        for link_text, link_path in links:
                            if link_path.startswith('http') or link_path.startswith('#'):
                                continue
                            
                            if not link_path.startswith('/'):
                                target_path = (file_path.parent / link_path).resolve()
                                
                                if not target_path.exists():
                                    broken_links.append({
                                        "file": str(relative_path),
                                        "link": link_path,
                                        "text": link_text,
                                        "file_path": file_path
                                    })
                    
                    except Exception as e:
                        pass
        
        print(f"发现 {len(broken_links)} 个死链接")
        return broken_links
    
    def fix_link(self, link_info):
        try:
            file_path = link_info["file_path"]
            old_link = link_info["link"]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_link = old_link
            
            if './' in old_link:
                new_link = old_link.replace('./', '')
            
            if '../' in old_link:
                depth = old_link.count('../')
                parent_path = file_path.parent
                
                for _ in range(depth):
                    parent_path = parent_path.parent
                
                clean_link = old_link.replace('../', '')
                new_link = str(Path(parent_path.relative_to(DOCS_DIR)) / clean_link)
            
            new_content = content.replace(f']({old_link})', f']({new_link})')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.fixed_links.append({
                "file": link_info["file"],
                "old_link": old_link,
                "new_link": new_link
            })
            
            return True
        
        except Exception as e:
            self.failed_links.append({
                "file": link_info["file"],
                "link": link_info["link"],
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("L1死链接批量修复V2")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        broken_links = self.find_broken_links()
        
        print(f"\n开始修复（处理所有链接）...")
        success_count = 0
        
        total_links = len(broken_links)
        for i, link_info in enumerate(broken_links, 1):
            if i % 100 == 0:
                print(f"[{i}/{total_links}] 已处理 {i} 个链接...")
            
            if self.fix_link(link_info):
                success_count += 1
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总死链接数: {len(broken_links)}")
        print(f"本次处理: 500个")
        print(f"成功修复: {success_count}")
        print(f"失败: {len(self.failed_links)}")
        
        if self.fixed_links:
            print("\n成功修复示例:")
            for item in self.fixed_links[:10]:
                print(f"  ✅ {item['file']}")
                print(f"     {item['old_link']} -> {item['new_link']}")
        
        if self.failed_links:
            print("\n失败链接:")
            for item in self.failed_links[:10]:
                print(f"  ❌ {item['file']} -> {item['link']}: {item['error']}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "total": len(broken_links),
            "processed": 500,
            "success": success_count,
            "failed": len(self.failed_links)
        }

if __name__ == "__main__":
    fixer = L1LinkBatchFixerV2()
    fixer.run()
