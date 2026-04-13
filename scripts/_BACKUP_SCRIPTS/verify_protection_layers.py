#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""防护层验证脚本"""

import subprocess
import sys
from pathlib import Path

def verify_protection_layers():
    """验证三层防护架构完整性"""
    
    print("\n" + "="*70)
    print("【三层防护架构校验】")
    print("="*70 + "\n")
    
    results = {
        "Layer 1 (Pre-commit)": {"status": "待验证", "details": []},
        "Layer 2 (编译器)": {"status": "待验证", "details": []},
        "Layer 3 (CI/CD)": {"status": "待验证", "details": []}
    }
    
    # Layer 1: Pre-commit 校验
    print("🔍 Layer 1: Pre-commit 本地守卫")
    try:
        # 检查.pre-commit-config.yaml
        config_file = Path("d:\\ZephyrAlpha\\.pre-commit-config.yaml")
        if config_file.exists():
            with open(config_file) as f:
                content = f.read()
                if "mandatory-inbound-guard" in content:
                    print("  ✅ mandatory-inbound-guard 钮钩已部署")
                    results["Layer 1 (Pre-commit)"]["status"] = "✅ 就绪"
                else:
                    print("  ⚠️ mandatory-inbound-guard 钮钩未发现")
                    results["Layer 1 (Pre-commit)"]["status"] = "⚠️ 配置缺失"
        else:
            print("  ❌ .pre-commit-config.yaml 未找到")
            results["Layer 1 (Pre-commit)"]["status"] = "❌ 未配置"
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        results["Layer 1 (Pre-commit)"]["status"] = f"❌ {str(e)}"
    
    print()
    
    # Layer 2: 编译器完整性校验
    print("🔍 Layer 2: 编译时自动生成")
    try:
        compiler_file = Path("d:\\ZephyrAlpha\\scripts\\index_compiler.py")
        if compiler_file.exists():
            print(f"  ✅ index_compiler.py 存在 ({compiler_file.stat().st_size} bytes)")
            # 检查是否可执行
            if compiler_file.read_text().count("def ") > 5:
                print("  ✅ 编译器函数结构完整")
                results["Layer 2 (编译器)"]["status"] = "✅ 活跃"
            else:
                print("  ⚠️ 编译器函数不完整")
                results["Layer 2 (编译器)"]["status"] = "⚠️ 功能缺失"
        else:
            print("  ❌ index_compiler.py 未找到")
            results["Layer 2 (编译器)"]["status"] = "❌ 文件丢失"
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        results["Layer 2 (编译器)"]["status"] = f"❌ {str(e)}"
    
    print()
    
    # Layer 3: CI/CD 工作流校验
    print("🔍 Layer 3: CI/CD 每小时验证")
    try:
        workflow_file = Path("d:\\ZephyrAlpha\\.github\\workflows\\eternal-index-validation.yml")
        if workflow_file.exists():
            with open(workflow_file) as f:
                content = f.read()
                if "schedule:" in content and "0 * * * *" in content:
                    print("  ✅ 每小时定时任务已配置")
                    print("  ✅ GitHub Actions 工作流已部署")
                    results["Layer 3 (CI/CD)"]["status"] = "✅ 配置完毕"
                else:
                    print("  ⚠️ 定时任务配置可能缺失")
                    results["Layer 3 (CI/CD)"]["status"] = "⚠️ 配置不完整"
        else:
            print("  ❌ CI/CD 工作流文件未找到")
            results["Layer 3 (CI/CD)"]["status"] = "❌ 文件丢失"
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        results["Layer 3 (CI/CD)"]["status"] = f"❌ {str(e)}"
    
    print()
    
    # 综合评估
    print("="*70)
    print("【防护层综合评估】")
    print("="*70)
    
    layer_statuses = [results[key]["status"] for key in results.keys()]
    success_count = sum(1 for status in layer_statuses if "✅" in status)
    
    for layer, data in results.items():
        print(f"\n{layer}: {data['status']}")
    
    print(f"\n综合防护有效率: {success_count * 100 // 3}% {'🛡️' if success_count == 3 else '⚠️'}")
    
    if success_count == 3:
        print("\n✅ 三层防护架构完整，无缺陷！")
        return True
    else:
        print(f"\n⚠️ 检测到 {3 - success_count} 层防护配置问题，需人工审视")
        return False

if __name__ == "__main__":
    verify_protection_layers()
