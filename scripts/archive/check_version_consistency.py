#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本一致性检查脚本 (check_version_consistency.py)

功能: 检查同一 Layer 的所有相关文档版本号是否一致
使用: python check_version_consistency.py --layer 11
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple

class VersionConsistencyChecker:
    """版本一致性检查器"""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.docs_root = self.workspace_root / "docs"
        
    def parse_yaml_frontmatter(self, file_path: Path) -> Dict:
        """解析 markdown 文件的 YAML frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.startswith('---'):
                return {}
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}
            
            frontmatter = yaml.safe_load(parts[1])
            return frontmatter or {}
        except Exception as e:
            print(f"!! 解析错误 {file_path}: {e}")
            return {}
    
    def get_version(self, file_path: Path) -> str:
        """获取文件版本号"""
        fm = self.parse_yaml_frontmatter(file_path)
        return fm.get("version", "unknown")
    
    def check_layer_11_versions(self) -> Dict:
        """检查 Layer 11 所有文档的版本一致性"""
        
        # Layer 11 相关文档
        layer_11_docs = [
            self.docs_root / "01_FRAMEWORK" / "ARCHITECTURE.md",
            self.docs_root / "11_STRATEGIC_DECISION" / "complete-blueprint-overview.md",
            self.docs_root / "11_STRATEGIC_DECISION" / "blueprint-index.md",
            self.docs_root / "11_STRATEGIC_DECISION" / "blueprint-progress-report-20260407.md",
            self.docs_root / "11_STRATEGIC_DECISION" / "responsibility-boundary-matrix.md",
            self.docs_root / "11_STRATEGIC_DECISION" / "ARCHITECTURE_REVIEW_HANDOVER_20260412.md",
            self.docs_root / "11_STRATEGIC_DECISION" / "FOLDER_STRUCTURE_PROFESSIONAL_ASSESSMENT_AND_PREVENTION_PLAN_20260412.md",
        ]
        
        results = {
            "layer": 11,
            "documents": {},
            "inconsistencies": [],
            "status": "ok",
        }
        
        # 获取所有文档的版本
        versions = {}
        for doc in layer_11_docs:
            if doc.exists():
                version = self.get_version(doc)
                results["documents"][doc.name] = version
                if version not in versions:
                    versions[version] = []
                versions[version].append(doc.name)
            else:
                results["documents"][doc.name] = "NOT_FOUND"
        
        # 检查一致性
        if len(versions) > 1:
            results["status"] = "inconsistent"
            for version, docs in versions.items():
                if version != "unknown":
                    results["inconsistencies"].append({
                        "version": version,
                        "documents": docs,
                        "count": len(docs),
                    })
        
        return results
    
    def check_all_layers(self) -> Dict:
        """检查所有 Layer 的版本一致性"""
        
        all_results = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "layers": {},
            "summary": {
                "total_layers": 0,
                "consistent_layers": 0,
                "inconsistent_layers": 0,
            }
        }
        
        # 检查 Layer 0-11
        for layer_num in range(12):
            layer_docs = self._find_docs_by_layer(layer_num)
            
            if not layer_docs:
                continue
            
            all_results["summary"]["total_layers"] += 1
            
            versions = {}
            doc_versions = {}
            
            for doc in layer_docs:
                version = self.get_version(doc)
                doc_versions[doc.name] = version
                if version not in versions:
                    versions[version] = []
                versions[version].append(doc.name)
            
            layer_result = {
                "documents": doc_versions,
                "status": "consistent" if len(versions) <= 1 else "inconsistent",
            }
            
            if len(versions) > 1:
                all_results["summary"]["inconsistent_layers"] += 1
                layer_result["inconsistencies"] = [
                    {"version": v, "documents": docs}
                    for v, docs in versions.items()
                ]
            else:
                all_results["summary"]["consistent_layers"] += 1
            
            all_results["layers"][f"layer_{layer_num:02d}"] = layer_result
        
        return all_results
    
    def _find_docs_by_layer(self, layer_num: int) -> List[Path]:
        """查找指定 Layer 的所有文档"""
        
        layer_mapping = {
            0: ["01_FRAMEWORK"],
            1: ["01_FRAMEWORK"],
            2: ["02_FACTOR_LIBRARY"],
            3: ["03_TRADING_TACTICS"],
            4: ["04_EXECUTION"],
            5: ["05_IMPLEMENTATION"],
            6: ["05_IMPLEMENTATION"],
            7: ["05_IMPLEMENTATION"],
            8: ["08_AI_GOVERNANCE"],
            9: ["09_AUDIT"],
            10: ["08_AI_GOVERNANCE", "09_AUDIT"],
            11: ["11_STRATEGIC_DECISION", "01_FRAMEWORK"],
        }
        
        docs = []
        for dir_name in layer_mapping.get(layer_num, []):
            dir_path = self.docs_root / dir_name
            if dir_path.exists():
                for md_file in dir_path.glob("*.md"):
                    fm = self.parse_yaml_frontmatter(md_file)
                    if fm.get("layer") == f"layer_{layer_num:02d}":
                        docs.append(md_file)
        
        return docs


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="版本一致性检查脚本")
    parser.add_argument("--layer", type=int, help="检查指定 Layer (0-11)")
    parser.add_argument("--all", action="store_true", help="检查所有 Layer")
    parser.add_argument("--workspace", default=".", help="工作区根目录")
    parser.add_argument("--output", help="输出结果到文件 (JSON 格式)")
    
    args = parser.parse_args()
    
    checker = VersionConsistencyChecker(args.workspace)
    
    if args.all:
        result = checker.check_all_layers()
    elif args.layer is not None:
        if args.layer == 11:
            result = checker.check_layer_11_versions()
        else:
            print(f"!! 暂不支持 Layer {args.layer} 的详细检查")
            sys.exit(1)
    else:
        result = checker.check_layer_11_versions()
    
    # 输出结果
    print("\n== 版本一致性检查结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 保存到文件
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n++ 结果已保存到: {args.output}")
    
    # 返回状态码
    if result.get("status") == "inconsistent" or result.get("summary", {}).get("inconsistent_layers", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
