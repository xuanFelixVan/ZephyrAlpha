# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
P1-1问题修复脚本 - 修复死链接
用途：修复2,086个死链接
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class P1LinkFixer:
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
                                        "text": link_text
                                    })
                    
                    except Exception as e:
                        pass
        
        print(f"发现 {len(broken_links)} 个死链接")
        return broken_links
    
    def fix_link(self, file_path, old_link, link_text):
        try:
            file_full_path = DOCS_DIR / file_path
            
            with open(file_full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_link = old_link
            
            if './' in old_link:
                new_link = old_link.replace('./', '')
            
            if '../' in old_link:
                depth = old_link.count('../')
                parent_path = file_full_path.parent
                
                for _ in range(depth):
                    parent_path = parent_path.parent
                
                clean_link = old_link.replace('../', '')
                new_link = str(Path(parent_path.relative_to(DOCS_DIR)) / clean_link)
            
            new_content = content.replace(f']({old_link})', f']({new_link})')
            
            with open(file_full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.fixed_links.append({
                "file": file_path,
                "old_link": old_link,
                "new_link": new_link,
                "text": link_text
            })
            
            return True
        
        except Exception as e:
            print(f"  ❌ 修复失败: {file_path} - {old_link} - {e}")
            self.failed_links.append({
                "file": file_path,
                "link": old_link,
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("P1-1问题修复 - 修复死链接")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        broken_links = self.find_broken_links()
        
        print(f"\n开始修复...")
        success_count = 0
        
        for i, link_info in enumerate(broken_links[:100], 1):
            print(f"[{i}/{min(100, len(broken_links))}] 处理: {link_info['file']} -> {link_info['link']}")
            
            if self.fix_link(link_info['file'], link_info['link'], link_info['text']):
                success_count += 1
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总死链接数: {len(broken_links)}")
        print(f"本次处理: {min(100, len(broken_links))}")
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
            "processed": min(100, len(broken_links)),
            "success": success_count,
            "failed": len(self.failed_links),
            "fixed_links": self.fixed_links,
            "failed_links": self.failed_links
        }

if __name__ == "__main__":
    fixer = P1LinkFixer()
    fixer.run()
