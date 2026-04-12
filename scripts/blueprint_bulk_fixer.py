#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
蓝图终稿大规模修复工具
处理元数据补齐、编码修复、职责补全
"""

import os
import re
from pathlib import Path
from datetime import datetime

class BlueprintBulkFixer:
    def __init__(self, root_path="d:\\ZephyrAlpha"):
        self.root = Path(root_path)
        self.docs_path = self.root / "docs"
        self.fixed_count = 0
        self.failed_count = 0
        
    def get_layer_from_path(self, file_path):
        """从文件路径推断layer"""
        path_parts = file_path.parts
        for part in path_parts:
            if part.startswith(('00_', '01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_')):
                # 提取数字部分
                layer_num = part.split('_')[0]
                return f"layer_{layer_num}"
        return "layer_00"
    
    def get_default_module_id(self, file_path):
        """从文件名推断module_id"""
        file_stem = file_path.stem
        # 使用文件名作为module_id
        return file_stem.upper()
    
    def fix_encoding_corruption(self):
        """修复编码问题"""
        print("\n【修复第1步】修复编码corruption")
        
        for md_file in self.docs_path.rglob("*.md"):
            try:
                # 尝试读取文件
                with open(md_file, 'rb') as f:
                    raw_bytes = f.read()
                
                # 尝试UTF-8-SIG解码
                try:
                    content = raw_bytes.decode('utf-8-sig')
                except:
                    # 尝试其他编码
                    try:
                        content = raw_bytes.decode('utf-8')
                    except:
                        try:
                            content = raw_bytes.decode('gbk')
                        except:
                            print(f"  ✗ 无法解码: {md_file.relative_to(self.docs_path)}")
                            self.failed_count += 1
                            continue
                
                # 检查是否包含乱码替换字符
                if '\ufffd' in content:
                    # 尝试清理
                    clean_content = content.replace('\ufffd', '')
                    
                    # 重新保存为UTF-8-SIG
                    with open(md_file, 'w', encoding='utf-8-sig') as f:
                        f.write(clean_content)
                    
                    print(f"  ✓ 修复: {md_file.relative_to(self.docs_path)}")
                    self.fixed_count += 1
                else:
                    # 确保使用UTF-8-SIG编码保存
                    with open(md_file, 'w', encoding='utf-8-sig') as f:
                        f.write(content)
                        
            except Exception as e:
                print(f"  ✗ 错误: {md_file.relative_to(self.docs_path)}: {str(e)[:50]}")
                self.failed_count += 1
    
    def fix_missing_metadata(self):
        """补齐缺失的元数据"""
        print("\n【修复第2步】补齐缺失的元数据")
        
        count = 0
        for md_file in self.docs_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查是否有YAML首部
                if not content.startswith('---'):
                    # 需要添加YAML首部
                    layer = self.get_layer_from_path(md_file)
                    module_id = self.get_default_module_id(md_file)
                    
                    yaml_header = f"""---
module_id: {module_id}
layer: {layer}
version: 1.0.0
responsibility: "待补充"
---

"""
                    new_content = yaml_header + content
                    
                    with open(md_file, 'w', encoding='utf-8-sig') as f:
                        f.write(new_content)
                    
                    count += 1
                    if count <= 10:
                        print(f"  ✓ 添加首部: {md_file.relative_to(self.docs_path)}")
                    elif count % 100 == 0:
                        print(f"  ... 已处理 {count} 个文件")
                        
                else:
                    # 检查YAML首部的完整性
                    yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if yaml_match:
                        yaml_content = yaml_match.group(1)
                        needs_update = False
                        
                        # 检查缺失的字段
                        if 'module_id:' not in yaml_content:
                            yaml_content += f"\nmodule_id: {self.get_default_module_id(md_file)}"
                            needs_update = True
                        
                        if 'layer:' not in yaml_content:
                            yaml_content += f"\nlayer: {self.get_layer_from_path(md_file)}"
                            needs_update = True
                        
                        if 'version:' not in yaml_content:
                            yaml_content += "\nversion: 1.0.0"
                            needs_update = True
                        
                        if 'responsibility:' not in yaml_content:
                            yaml_content += '\nresponsibility: "待补充"'
                            needs_update = True
                        
                        if needs_update:
                            new_content = f'---\n{yaml_content}\n---\n{content[len(yaml_match.group(0)):]}'
                            with open(md_file, 'w', encoding='utf-8-sig') as f:
                                f.write(new_content)
                            
                            count += 1
                            if count <= 10:
                                print(f"  ✓ 更新首部: {md_file.relative_to(self.docs_path)}")
                            elif count % 100 == 0:
                                print(f"  ... 已处理 {count} 个文件")
                                
            except Exception as e:
                self.failed_count += 1
        
        print(f"  完成: 修复/添加 {count} 个文件的元数据")
    
    def ensure_responsibility_descriptions(self):
        """确保所有responsibility字段有有效的值"""
        print("\n【修复第3步】补齐职责描述")
        
        count = 0
        for md_file in self.docs_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    
                    # 检查responsibility字段
                    if 'responsibility:' in yaml_content:
                        # 检查是否为空或只有默认值
                        resp_match = re.search(r'responsibility:\s*["\']?([^"\']*)["\']?$', yaml_content, re.MULTILINE)
                        if resp_match:
                            resp_value = resp_match.group(1).strip()
                            if not resp_value or resp_value == "待补充" or resp_value == "[]":
                                # 从文件名推断职责
                                file_name = md_file.stem
                                inferred_responsibility = f"处理{file_name}相关业务"
                                
                                new_yaml = re.sub(
                                    r'responsibility:.*$',
                                    f'responsibility: "{inferred_responsibility}"',
                                    yaml_content,
                                    flags=re.MULTILINE
                                )
                                
                                new_content = f'---\n{new_yaml}\n---\n{content[len(yaml_match.group(0)):]}'
                                with open(md_file, 'w', encoding='utf-8-sig') as f:
                                    f.write(new_content)
                                
                                count += 1
                                
            except Exception as e:
                self.failed_count += 1
        
        print(f"  完成: 补齐 {count} 个文件的职责描述")
    
    def run_all_fixes(self):
        """执行所有修复"""
        print("=" * 80)
        print("蓝图终稿大规模修复系统")
        print("=" * 80)
        print(f"工作目录: {self.docs_path}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 执行修复
        self.fix_encoding_corruption()
        self.fix_missing_metadata()
        self.ensure_responsibility_descriptions()
        
        # 总结
        print("\n" + "=" * 80)
        print("修复总结")
        print("=" * 80)
        print(f"成功修复: {self.fixed_count}")
        print(f"失败: {self.failed_count}")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

if __name__ == '__main__':
    fixer = BlueprintBulkFixer()
    fixer.run_all_fixes()
