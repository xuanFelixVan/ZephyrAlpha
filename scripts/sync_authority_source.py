#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权威源同步脚本 (sync_authority_source.py)

功能: 验证权威源与衍生文档的一致性，并自动同步关键字段
使用: python sync_authority_source.py --layer 11 --check
"""

import os
import sys
import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class AuthoritySourceSync:
    """权威源同步管理器"""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.docs_root = self.workspace_root / "docs"
        
    def parse_yaml_frontmatter(self, file_path: Path) -> Tuple[Dict, str]:
        """
        解析 markdown 文件的 YAML frontmatter
        返回: (frontmatter_dict, content)
        """
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return {}, content
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content
        
        try:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2]
            return frontmatter or {}, body
        except yaml.YAMLError as e:
            print(f"!! YAML 解析错误 {file_path}: {e}")
            return {}, content
    
    def write_yaml_frontmatter(self, file_path: Path, frontmatter: Dict, content: str):
        """写入 YAML frontmatter 和内容"""
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"---\n{yaml_str}---\n{content}")
    
    def check_layer_11_sync(self) -> Dict:
        """检查 Layer 11 权威源与衍生文档的同步状态"""
        
        # 权威源文档
        authority_doc = self.docs_root / "11_STRATEGIC_DECISION" / "complete-blueprint-overview.md"
        
        # 衍生文档
        # 已归档文件列表（跳过同步检查）
        archived_docs = {
            "blueprint-progress-report-20260407.md",
        }
        
        derived_docs = [
            self.docs_root / "11_STRATEGIC_DECISION" / "blueprint-index.md",
            self.docs_root / "11_STRATEGIC_DECISION" / "responsibility-boundary-matrix.md",
        ]
        
        if not authority_doc.exists():
            return {"status": "error", "message": f"权威源文档不存在: {authority_doc}"}
        
        # 解析权威源
        authority_fm, _ = self.parse_yaml_frontmatter(authority_doc)
        authority_data = {
            "blueprint_count": authority_fm.get("blueprint_count"),
            "existing_count": authority_fm.get("existing_count"),
            "missing_count": authority_fm.get("missing_count"),
            "version": authority_fm.get("version"),
        }
        
        print(f"\n== 权威源数据 ({authority_doc.name}):")
        print(f"   - 蓝图总数: {authority_data['blueprint_count']}")
        print(f"   - 已存在: {authority_data['existing_count']}")
        print(f"   - 缺失: {authority_data['missing_count']}")
        print(f"   - 版本: {authority_data['version']}")
        
        # 检查衍生文档
        results = {
            "authority_source": authority_doc.name,
            "authority_data": authority_data,
            "derived_docs": {},
            "inconsistencies": [],
        }
        
        for derived_doc in derived_docs:
            if not derived_doc.exists():
                results["inconsistencies"].append(f"衍生文档不存在: {derived_doc}")
                continue
            
            derived_fm, _ = self.parse_yaml_frontmatter(derived_doc)
            derived_data = {
                "blueprint_count": derived_fm.get("blueprint_count"),
                "existing_count": derived_fm.get("existing_count"),
                "missing_count": derived_fm.get("missing_count"),
                "version": derived_fm.get("version"),
            }
            
            results["derived_docs"][derived_doc.name] = derived_data
            
            # 检查一致性
            if derived_data["blueprint_count"] != authority_data["blueprint_count"]:
                results["inconsistencies"].append(
                    f"{derived_doc.name}: 蓝图总数不一致 "
                    f"({derived_data['blueprint_count']} vs {authority_data['blueprint_count']})"
                )
            
            if derived_data["missing_count"] != authority_data["missing_count"]:
                results["inconsistencies"].append(
                    f"{derived_doc.name}: 缺失数不一致 "
                    f"({derived_data['missing_count']} vs {authority_data['missing_count']})"
                )
            
            if derived_data["version"] != authority_data["version"]:
                results["inconsistencies"].append(
                    f"{derived_doc.name}: 版本不一致 "
                    f"({derived_data['version']} vs {authority_data['version']})"
                )
        
        return results
    
    def sync_layer_11(self, force: bool = False) -> Dict:
        """同步 Layer 11 衍生文档"""
        
        check_result = self.check_layer_11_sync()
        
        if check_result.get("status") == "error":
            return check_result
        
        if not check_result["inconsistencies"] and not force:
            print("\n++ 所有文档已同步，无需更新")
            return {"status": "ok", "message": "已同步"}
        
        if check_result["inconsistencies"]:
            print(f"\n!! 发现 {len(check_result['inconsistencies'])} 个不一致:")
            for inconsistency in check_result["inconsistencies"]:
                print(f"   - {inconsistency}")
        
        if not force:
            response = input("\n是否继续同步? (y/n): ")
            if response.lower() != 'y':
                return {"status": "cancelled", "message": "用户取消"}
        
        # 执行同步
        authority_doc = self.docs_root / "11_STRATEGIC_DECISION" / "complete-blueprint-overview.md"
        authority_fm, _ = self.parse_yaml_frontmatter(authority_doc)
        
        derived_docs = [
            self.docs_root / "11_STRATEGIC_DECISION" / "blueprint-index.md",
            self.docs_root / "11_STRATEGIC_DECISION" / "responsibility-boundary-matrix.md",
        ]
        
        sync_count = 0
        for derived_doc in derived_docs:
            if not derived_doc.exists():
                continue
            
            derived_fm, content = self.parse_yaml_frontmatter(derived_doc)
            
            # 同步关键字段
            derived_fm["blueprint_count"] = authority_fm.get("blueprint_count")
            derived_fm["existing_count"] = authority_fm.get("existing_count")
            derived_fm["missing_count"] = authority_fm.get("missing_count")
            derived_fm["version"] = authority_fm.get("version")
            derived_fm["last_synced_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            derived_fm["synced_from"] = authority_doc.name
            
            self.write_yaml_frontmatter(derived_doc, derived_fm, content)
            print(f"++ 已同步: {derived_doc.name}")
            sync_count += 1
        
        return {
            "status": "success",
            "message": f"已同步 {sync_count} 个文档",
            "synced_count": sync_count,
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="权威源同步脚本")
    parser.add_argument("--layer", type=int, default=11, help="Layer 编号 (默认: 11)")
    parser.add_argument("--check", action="store_true", help="仅检查，不同步")
    parser.add_argument("--force", action="store_true", help="强制同步")
    parser.add_argument("--workspace", default=".", help="工作区根目录")
    
    args = parser.parse_args()
    
    sync = AuthoritySourceSync(args.workspace)
    
    if args.layer == 11:
        if args.check:
            result = sync.check_layer_11_sync()
            print(f"\n== 检查结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            result = sync.sync_layer_11(force=args.force)
            print(f"\n== 同步结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"!! 暂不支持 Layer {args.layer}")
        sys.exit(1)


if __name__ == "__main__":
    main()
