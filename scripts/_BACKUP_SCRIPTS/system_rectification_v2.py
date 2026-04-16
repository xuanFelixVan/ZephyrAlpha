#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Rectification v2.0
七维审计报告精准打击：消除23项致命风险和326项逻辑缺陷

修复范围：
1. 物理层：重命名13个非法目录（中文、[]、-）
2. 元数据层：解决50+个module_id冲突和74个双YAML炸弹
3. 逻辑层：标记208处L5硬编码参数，建立全局常量占位
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class SystemRectificationEngine:
    def __init__(self, root_path: str = "d:\\ZephyrAlpha"):
        self.root = Path(root_path)
        self.docs = self.root / "docs"
        self.stats = {
            "dir_renamed": 0,
            "yaml_fixed": 0,
            "params_marked": 0,
            "errors": []
        }
        self.audit_log = []

    # ═══════════════════════════════════════════════════════════════════════
    # Task 1: 物理层修复 - 重命名非法目录
    # ═══════════════════════════════════════════════════════════════════════

    def get_illegal_dirs(self) -> List[str]:
        """扫描含有中文、方括号或短横线的目录"""
        illegal = []
        for item in self.docs.iterdir():
            if item.is_dir():
                name = item.name
                # 检测非法字符：中文、方括号、开头短横线
                if (any('\u4e00' <= c <= '\u9fff' for c in name) or
                    '[' in name or ']' in name or
                    name.startswith('-')):
                    illegal.append(name)
        return illegal

    def sanitize_dirname(self, dirname: str) -> str:
        """将目录名转换为合法的英文格式"""
        # 移除中文
        sanitized = re.sub(r'[\u4e00-\u9fff]+', '', dirname)
        # 替换非法字符
        sanitized = sanitized.replace('[', '').replace(']', '')
        sanitized = sanitized.lstrip('-')
        # 首字母大写
        sanitized = sanitized.strip()
        if not sanitized:
            sanitized = "ARCHIVED"
        return sanitized

    def rename_illegal_dirs(self) -> int:
        """重命名所有非法目录"""
        illegal_dirs = self.get_illegal_dirs()
        renamed_count = 0

        for old_name in illegal_dirs:
            old_path = self.docs / old_name
            new_name = self.sanitize_dirname(old_name)
            new_path = self.docs / new_name

            # 避免覆盖
            if new_path.exists():
                new_name = f"{new_name}_BACKUP_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                new_path = self.docs / new_name

            try:
                shutil.move(str(old_path), str(new_path))
                self.audit_log.append(f"✅ 重命名: {old_name} → {new_name}")
                renamed_count += 1
            except Exception as e:
                msg = f"❌ 重命名失败 {old_name}: {str(e)}"
                self.audit_log.append(msg)
                self.stats["errors"].append(msg)

        self.stats["dir_renamed"] = renamed_count
        return renamed_count

    # ═══════════════════════════════════════════════════════════════════════
    # Task 2: 元数据修复 - 解决module_id冲突和双YAML炸弹
    # ═══════════════════════════════════════════════════════════════════════

    def fix_module_ids(self) -> int:
        """修复module_id冲突和双YAML炸弹"""
        fixed_count = 0
        readme_count = 0

        for md_file in self.docs.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content

                # 检测是否需要修复
                if content.startswith("---"):
                    # 提取YAML头部
                    yaml_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
                    if yaml_match:
                        yaml_block = yaml_match.group(1)
                        body = content[yaml_match.end():]

                        # 检测module_id为README的情况
                        if 'module_id: README' in yaml_block:
                            readme_count += 1
                            # 生成唯一ID
                            rel_path = md_file.relative_to(self.docs)
                            layer_name = rel_path.parts[0] if rel_path.parts else "UNKNOWN"
                            new_module_id = f"README_{layer_name}_{hash(str(md_file)) % 10000:04d}"
                            yaml_block = yaml_block.replace('module_id: README', f'module_id: {new_module_id}')
                            content = f"---\n{yaml_block}\n---\n{body}"

                        # 检测双YAML炸弹：正文中的module_id: 如果不在代码块内，包裹它
                        # 查找正文中的module_id:行（在YAML块之外）
                        body_lines = body.split('\n')
                        fixed_body = []
                        in_code_block = False
                        for line in body_lines:
                            if line.startswith('```'):
                                in_code_block = not in_code_block
                            if not in_code_block and 'module_id:' in line and not line.startswith('```'):
                                # 找到未被包裹的module_id，将其所在段落包裹为代码块
                                fixed_body.append('```')
                                fixed_body.append(line)
                                fixed_body.append('```')
                            else:
                                fixed_body.append(line)

                        content = f"---\n{yaml_block}\n---\n" + '\n'.join(fixed_body)

                # 如果内容改变，保存
                if content != original_content:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_count += 1
                    self.audit_log.append(f"✅ 修复YAML: {md_file.relative_to(self.docs)}")

            except Exception as e:
                msg = f"❌ 修复YAML失败 {md_file}: {str(e)}"
                self.audit_log.append(msg)
                self.stats["errors"].append(msg)

        self.stats["yaml_fixed"] = fixed_count
        self.audit_log.insert(0, f"【YAML修复统计】README重复: {readme_count} | 已修复: {fixed_count}")
        return fixed_count

    # ═══════════════════════════════════════════════════════════════════════
    # Task 3: 逻辑层修复 - 标记L5硬编码参数
    # ═══════════════════════════════════════════════════════════════════════

    def mark_hardcoded_params(self) -> int:
        """扫描和标记L5层硬编码的业务参数"""
        marked_count = 0

        # L5的常见位置
        l5_patterns = [
            r'layer:\s*layer_05',
            r'layer_05/',
            r'05_IMPLEMENTATION'
        ]

        # 参数模式（风控、配置等）
        param_patterns = [
            r'max_position_size\s*[:=]',
            r'min_order_amount\s*[:=]',
            r'risk_limit\s*[:=]',
            r'stop_loss\s*[:=]',
            r'take_profit\s*[:=]',
            r'leverage\s*[:=]',
            r'slippage\s*[:=]'
        ]

        for md_file in self.docs.rglob("*.md"):
            try:
                # 检测是否是L5文件
                is_l5 = False
                for l5_pat in l5_patterns:
                    if re.search(l5_pat, str(md_file)):
                        is_l5 = True
                        break

                if not is_l5:
                    continue

                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检测是否含有参数
                has_params = any(re.search(pat, content) for pat in param_patterns)

                if has_params:
                    # 添加标签到YAML头部
                    if content.startswith("---"):
                        yaml_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
                        if yaml_match:
                            yaml_block = yaml_match.group(1)
                            body = content[yaml_match.end():]

                            # 添加标签（如果还没有）
                            if 'audit_status:' not in yaml_block:
                                yaml_block += "\naudit_status: EXTRACT_TO_L0_REQUIRED"
                                content = f"---\n{yaml_block}\n---\n{body}"

                                with open(md_file, 'w', encoding='utf-8') as f:
                                    f.write(content)

                                marked_count += 1
                                self.audit_log.append(f"✅ 标记L5参数: {md_file.relative_to(self.docs)}")

            except Exception as e:
                msg = f"❌ 标记失败 {md_file}: {str(e)}"
                self.audit_log.append(msg)
                self.stats["errors"].append(msg)

        self.stats["params_marked"] = marked_count
        return marked_count

    # ═══════════════════════════════════════════════════════════════════════
    # 全局常量占位文件
    # ═══════════════════════════════════════════════════════════════════════

    def create_global_constants(self) -> bool:
        """创建全局常量占位文件"""
        try:
            constants_dir = self.docs / "00_MANAGEMENT"
            constants_dir.mkdir(parents=True, exist_ok=True)

            constants_file = constants_dir / "GLOBAL_CONSTANTS.json"

            constants = {
                "metadata": {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "purpose": "全局系统常量真源中心",
                    "status": "PLACEHOLDER_FOR_FUTURE_IMPLEMENTATION"
                },
                "risk_parameters": {
                    "max_position_size": "TBD",
                    "min_order_amount": "TBD",
                    "risk_limit": "TBD",
                    "stop_loss": "TBD",
                    "take_profit": "TBD",
                    "leverage": "TBD",
                    "slippage": "TBD"
                },
                "notes": [
                    "此文件为L0层真源中心占位符",
                    "所有L5层硬编码参数应在此处定义",
                    "当前所有参数值为 TBD（待定），需后续补充"
                ]
            }

            with open(constants_file, 'w', encoding='utf-8') as f:
                json.dump(constants, f, ensure_ascii=False, indent=2)

            self.audit_log.append(f"✅ 创建全局常量占位: {constants_file.relative_to(self.docs)}")
            return True
        except Exception as e:
            msg = f"❌ 创建全局常量失败: {str(e)}"
            self.audit_log.append(msg)
            self.stats["errors"].append(msg)
            return False

    # ═══════════════════════════════════════════════════════════════════════
    # 执行与报告
    # ═══════════════════════════════════════════════════════════════════════

    def execute(self):
        """执行所有修复任务"""
        print("\n" + "="*70)
        print("【系统修复工程 v2.0】七维审计精准打击")
        print("="*70 + "\n")

        # Task 1: 重命名
        print("📋 Task 1: 物理层修复 - 重命名非法目录")
        illegal = self.get_illegal_dirs()
        print(f"   检测到 {len(illegal)} 个非法目录: {illegal}")
        renamed = self.rename_illegal_dirs()
        print(f"   ✅ 重命名完成: {renamed} 个\n")

        # Task 2: 元数据修复
        print("📋 Task 2: 元数据层修复 - module_id 和双YAML")
        fixed = self.fix_module_ids()
        print(f"   ✅ YAML修复完成: {fixed} 个\n")

        # Task 3: 逻辑层标记
        print("📋 Task 3: 逻辑层修复 - L5参数标记")
        marked = self.mark_hardcoded_params()
        print(f"   ✅ 参数标记完成: {marked} 个\n")

        # 创建全局常量占位
        print("📋 Task 4: 创建全局常量占位文件")
        self.create_global_constants()
        print()

        # 生成报告
        self.generate_report()

    def generate_report(self):
        """生成修复报告"""
        print("\n" + "="*70)
        print("【执行结果表格】")
        print("="*70)
        print(f"\n├─ 目录重命名数:  {self.stats['dir_renamed']}")
        print(f"├─ YAML 修复数:   {self.stats['yaml_fixed']}")
        print(f"├─ 参数标记数:    {self.stats['params_marked']}")
        print(f"└─ 错误统计:      {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\n【错误详情】")
            for err in self.stats['errors']:
                print(f"  {err}")

        # 保存审计日志
        log_file = self.root / "docs" / "09_AUDIT" / "STATE" / f"system_rectification_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("SYSTEM RECTIFICATION v2.0 - AUDIT LOG\n")
            f.write("="*70 + "\n\n")
            for line in self.audit_log:
                f.write(line + "\n")
            f.write(f"\n执行时间: {datetime.now().isoformat()}\n")

        print(f"\n✅ 审计日志已保存: {log_file}")

        print("\n" + "="*70)
        print("【修复工程完成】下一步请运行: pre-commit run --all-files")
        print("="*70 + "\n")

if __name__ == "__main__":
    engine = SystemRectificationEngine()
    engine.execute()
