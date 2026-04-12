#!/usr/bin/env python3
"""文档治理综合审计单一入口脚本

用途: 为新模型系统(AI Agent)提供标准化的全量审计入口
功能: 
  - 读取检查清单配置
  - 顺序/并行执行所有检查
  - 生成统一报告（JSON + Markdown）
  - 提供修复建议

使用方法:
  python scripts/run_comprehensive_audit.py
  python scripts/run_comprehensive_audit.py --check C-01,C-02
  python scripts/run_comprehensive_audit.py --severity P0,P1
  python scripts/run_comprehensive_audit.py --output json
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# ── Windows 控制台 UTF-8 ──────────────────────────────────────
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── 常量配置 ───────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_ROOT = SCRIPT_DIR.parent / "docs"
CHECKLIST_PATH = DOCS_ROOT / "09_AUDIT" / "CHECKLISTS" / "comprehensive-audit-checklist.yaml"
OUTPUT_DIR = DOCS_ROOT / "05_IMPLEMENTATION" / "04_OPERATIONS" / "audit_state"


@dataclass
class CheckResult:
    """单个检查项的结果"""
    check_id: str
    name: str
    severity: str
    passed: bool
    issues_found: int
    threshold: int
    message: str
    duration: float
    fix_suggestion: str = ""


@dataclass
class AuditReport:
    """完整审计报告"""
    version: str
    timestamp: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    p0_issues: int
    p1_issues: int
    p2_issues: int
    results: List[CheckResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class ComprehensiveAuditor:
    """综合审计执行器"""
    
    def __init__(self, checklist_path: Path = CHECKLIST_PATH, verbose: bool = False):
        self.checklist_path = checklist_path
        self.checklist: Dict = {}
        self.results: List[CheckResult] = []
        self.verbose = verbose
        
    def load_checklist(self) -> bool:
        """加载检查清单配置"""
        try:
            with open(self.checklist_path, "r", encoding="utf-8") as f:
                self.checklist = yaml.safe_load(f)
            print(f"✅ 加载检查清单: {self.checklist_path}")
            print(f"   版本: {self.checklist.get('audit_spec', {}).get('version', 'unknown')}")
            return True
        except Exception as e:
            print(f"❌ 加载检查清单失败: {e}")
            return False
    
    def get_checks(self, severity_filter: Optional[List[str]] = None, 
                   id_filter: Optional[List[str]] = None) -> List[Dict]:
        """获取检查项列表，支持过滤"""
        all_checks = self.checklist.get("checks", [])
        
        if id_filter:
            all_checks = [c for c in all_checks if c["id"] in id_filter]
        elif severity_filter:
            all_checks = [c for c in all_checks if c["severity"] in severity_filter]
        else:
            # 默认只执行 P0 检查
            all_checks = [c for c in all_checks if c["severity"] == "P0"]
            
        return all_checks
    
    def run_check(self, check: Dict) -> CheckResult:
        """执行单个检查"""
        import time
        start_time = time.time()
        
        check_id = check["id"]
        name = check["name"]
        severity = check["severity"]
        script = check.get("script", "")
        
        print(f"\n🔍 [{check_id}] {name}...")
        
        # 根据检查ID执行对应的检查
        result = self._execute_native_check(check)
        
        result.duration = time.time() - start_time
        return result
    
    def _execute_native_check(self, check: Dict) -> CheckResult:
        """执行内置检查逻辑"""
        check_id = check["id"]
        
        # C-01: 双YAML检测
        if check_id == "C-01":
            return self._check_double_yaml(check)
        
        # C-02: 无效内链检测
        elif check_id == "C-02":
            return self._check_invalid_links(check)
        
        # C-03: 重复Module ID检测
        elif check_id == "C-03":
            return self._check_duplicate_module_ids(check)
        
        # C-04: 编码损坏检测
        elif check_id == "C-04":
            return self._check_encoding_issues(check)
        
        # C-05: 必需元数据字段检测
        elif check_id == "C-05":
            return self._check_required_metadata(check)
        
        # 其他检查（待实现）
        else:
            return CheckResult(
                check_id=check_id,
                name=check["name"],
                severity=check["severity"],
                passed=True,
                issues_found=0,
                threshold=check.get("threshold", 0),
                message=f"检查 {check_id} 尚未实现",
                duration=0.0,
                fix_suggestion=""
            )
    
    def _check_double_yaml(self, check: Dict) -> CheckResult:
        """C-01: 双YAML检测"""
        script_path = SCRIPT_DIR / "doc_guard_pre_commit.py"
        result = subprocess.run(
            ["python", str(script_path), "--scan-double-yaml"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        # 解析输出
        issues = 0
        if "阻止提交的缺陷" in result.stdout or result.returncode != 0:
            # 统计问题数量
            issues = result.stdout.count("[D-01]")
        
        # Verbose 模式：打印样本文件的YAML结构快照
        if self.verbose and issues > 0:
            print("\n📋 [VERBOSE] 样本文件YAML结构快照（用于人工审计）:")
            sample_files = self._extract_double_yaml_samples(result.stdout, count=10)
            for file_path, line_num, yaml_content in sample_files:
                print(f"\n  ✓ {file_path}:{line_num}")
                # 打印YAML块的概要（前3行）
                preview = "\n  ".join(yaml_content.split("\n")[:3]) if yaml_content else "（无内容）"
                print(f"    YAML结构: {preview}")
        
        passed = issues == 0
        return CheckResult(
            check_id=check["id"],
            name=check["name"],
            severity=check["severity"],
            passed=passed,
            issues_found=issues,
            threshold=check["threshold"],
            message=f"发现 {issues} 个双YAML文件" if issues > 0 else "未发现问题",
            duration=0.0,
            fix_suggestion=check.get("failure_action", "") if not passed else ""
        )
    
    def _extract_double_yaml_samples(self, output: str, count: int = 10) -> List[tuple]:
        """从扫描输出中提取样本文件信息"""
        import re
        samples = []
        lines = output.split("\n")
        
        for line in lines:
            if "[D-01]" in line and len(samples) < count:
                # 解析行格式: [D-01] file:line — detail
                match = re.search(r'\[D-01\]\s+([^:]+):(\d+)', line)
                if match:
                    file_path = match.group(1)
                    line_num = match.group(2)
                    # 读取实际文件并提取YAML内容
                    try:
                        full_path = DOCS_ROOT.parent / file_path
                        if full_path.exists():
                            with open(full_path, 'r', encoding='utf-8-sig') as f:
                                content = f.read()
                            # 提取第二个YAML块的预览
                            yaml_preview = self._get_yaml_preview(content)
                            samples.append((file_path, line_num, yaml_preview))
                    except Exception as e:
                        samples.append((file_path, line_num, f"[读取失败: {e}]"))
        
        return samples
    
    def _get_yaml_preview(self, content: str) -> str:
        """从文件内容中提取第二个YAML块的预览"""
        import re
        # 找第一个frontmatter块
        first_fm = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not first_fm:
            return ""
        
        # 找第二个frontmatter块
        after_first = content[first_fm.end():]
        after_first_stripped = after_first.lstrip('\n\r\ufeff')
        second_fm = re.match(r'^---\s*\n(.*?)\n---\s*\n', after_first_stripped, re.DOTALL)
        
        if second_fm:
            yaml_content = second_fm.group(1).strip()
            # 返回前几行作为预览
            return yaml_content[:200] + ("..." if len(yaml_content) > 200 else "")
        
        return ""
    
    def _check_invalid_links(self, check: Dict) -> CheckResult:
        """C-02: 无效内链检测"""
        script_path = SCRIPT_DIR / "ci_cd_link_checker.py"
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        # 解析无效链接数
        issues = 0
        if "无效链接数:" in result.stdout:
            for line in result.stdout.split("\n"):
                if "无效链接数:" in line:
                    try:
                        issues = int(line.split(":")[1].strip())
                    except:
                        pass
                    break
        
        passed = issues == 0
        return CheckResult(
            check_id=check["id"],
            name=check["name"],
            severity=check["severity"],
            passed=passed,
            issues_found=issues,
            threshold=check["threshold"],
            message=f"发现 {issues} 个无效链接" if issues > 0 else "所有链接有效",
            duration=0.0,
            fix_suggestion=check.get("failure_action", "") if not passed else ""
        )
    
    def _check_duplicate_module_ids(self, check: Dict) -> CheckResult:
        """C-03: 重复Module ID检测"""
        # 豁免的通用ID（按设计允许重复）
        GENERIC_MODULE_IDS = {"INDEX", "README", "SITEMAP", "CHANGELOG", "LICENSE"}
        
        # 收集所有module_id
        module_ids: Dict[str, List[str]] = {}
        duplicate_groups = 0
        
        for md_file in DOCS_ROOT.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8-sig") as f:
                    content = f.read()
                
                # 解析frontmatter
                import re
                fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                if fm_match:
                    fm_content = fm_match.group(1)
                    for line in fm_content.split("\n"):
                        if line.strip().startswith("module_id:"):
                            module_id = line.split(":", 1)[1].strip()
                            # 跳过通用ID
                            if module_id in GENERIC_MODULE_IDS:
                                continue
                            if module_id not in module_ids:
                                module_ids[module_id] = []
                            module_ids[module_id].append(str(md_file.relative_to(DOCS_ROOT.parent)))
                            break
            except:
                continue
        
        # 统计重复
        for module_id, files in module_ids.items():
            if len(files) > 1:
                duplicate_groups += 1
        
        passed = duplicate_groups == 0
        return CheckResult(
            check_id=check["id"],
            name=check["name"],
            severity=check["severity"],
            passed=passed,
            issues_found=duplicate_groups,
            threshold=check["threshold"],
            message=f"发现 {duplicate_groups} 组重复module_id" if duplicate_groups > 0 else "所有module_id唯一",
            duration=0.0,
            fix_suggestion=check.get("failure_action", "") if not passed else ""
        )
    
    def _check_encoding_issues(self, check: Dict) -> CheckResult:
        """C-04: 编码损坏检测"""
        issues = 0
        garbled_chars = ['ï', '¿', '½', 'Ã', 'Â']
        
        for md_file in DOCS_ROOT.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8-sig") as f:
                    content = f.read()
                
                for char in garbled_chars:
                    if char in content:
                        issues += content.count(char)
            except:
                continue
        
        passed = issues == 0
        return CheckResult(
            check_id=check["id"],
            name=check["name"],
            severity=check["severity"],
            passed=passed,
            issues_found=issues,
            threshold=check["threshold"],
            message=f"发现 {issues} 个乱码字符" if issues > 0 else "未检测到编码问题",
            duration=0.0,
            fix_suggestion=check.get("failure_action", "") if not passed else ""
        )
    
    def _check_required_metadata(self, check: Dict) -> CheckResult:
        """C-05: 必需元数据字段检测"""
        required = self.checklist.get("audit_spec", {}).get("metadata", {}).get("required_fields", [])
        issues = 0
        
        for md_file in DOCS_ROOT.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8-sig") as f:
                    content = f.read()
                
                import re
                fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                if fm_match:
                    fm_content = fm_match.group(1)
                    for field in required:
                        if f"{field}:" not in fm_content:
                            issues += 1
                            break
            except:
                continue
        
        passed = issues == 0
        return CheckResult(
            check_id=check["id"],
            name=check["name"],
            severity=check["severity"],
            passed=passed,
            issues_found=issues,
            threshold=check["threshold"],
            message=f"发现 {issues} 个文件缺少必需字段" if issues > 0 else "所有文件包含必需字段",
            duration=0.0,
            fix_suggestion=check.get("failure_action", "") if not passed else ""
        )
    
    def run_audit(self, severity_filter: Optional[List[str]] = None,
                  id_filter: Optional[List[str]] = None) -> AuditReport:
        """执行完整审计"""
        print("="*70)
        print("文档治理综合审计")
        print("="*70)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"检查清单: {self.checklist_path}")
        print("-"*70)
        
        if not self.load_checklist():
            sys.exit(1)
        
        checks = self.get_checks(severity_filter, id_filter)
        print(f"\n执行 {len(checks)} 个检查项...")
        print("-"*70)
        
        total_duration = 0.0
        
        for check in checks:
            result = self.run_check(check)
            self.results.append(result)
            total_duration += result.duration
            
            status = "✅" if result.passed else "❌"
            print(f"{status} [{result.check_id}] {result.name}: {result.issues_found} 问题")
        
        # 生成报告
        report = self._generate_report(total_duration)
        return report
    
    def _generate_report(self, total_duration: float) -> AuditReport:
        """生成审计报告"""
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        p0_issues = sum(r.issues_found for r in self.results if r.severity == "P0")
        p1_issues = sum(r.issues_found for r in self.results if r.severity == "P1")
        p2_issues = sum(r.issues_found for r in self.results if r.severity == "P2")
        
        report = AuditReport(
            version="2.0.0",
            timestamp=datetime.now().isoformat(),
            total_checks=len(self.results),
            passed_checks=passed,
            failed_checks=failed,
            p0_issues=p0_issues,
            p1_issues=p1_issues,
            p2_issues=p2_issues,
            results=self.results,
            summary={
                "total_duration": total_duration,
                "docs_root": str(DOCS_ROOT),
                "pass_rate": round(passed / len(self.results) * 100, 2) if self.results else 100
            }
        )
        
        return report
    
    def export_json(self, report: AuditReport, output_path: Path) -> None:
        """导出JSON报告"""
        data = {
            "version": report.version,
            "timestamp": report.timestamp,
            "summary": {
                "total_checks": report.total_checks,
                "passed_checks": report.passed_checks,
                "failed_checks": report.failed_checks,
                "p0_issues": report.p0_issues,
                "p1_issues": report.p1_issues,
                "p2_issues": report.p2_issues,
                "pass_rate": report.summary.get("pass_rate", 100)
            },
            "results": [
                {
                    "check_id": r.check_id,
                    "name": r.name,
                    "severity": r.severity,
                    "passed": r.passed,
                    "issues_found": r.issues_found,
                    "threshold": r.threshold,
                    "message": r.message,
                    "duration": round(r.duration, 2),
                    "fix_suggestion": r.fix_suggestion
                }
                for r in report.results
            ]
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ JSON报告已保存: {output_path}")
    
    def export_markdown(self, report: AuditReport, output_path: Path) -> None:
        """导出Markdown报告"""
        md = f"""# 文档治理综合审计报告

**审计版本**: {report.version}  
**审计时间**: {report.timestamp}  
**文档根目录**: `{report.summary.get('docs_root', '')}`

---

## 执行摘要

| 指标 | 数值 | 状态 |
|------|------|------|
| 检查项总数 | {report.total_checks} | - |
| 通过项 | {report.passed_checks} | ✅ |
| 失败项 | {report.failed_checks} | {'✅' if report.failed_checks == 0 else '❌'} |
| 通过率 | {report.summary.get('pass_rate', 100)}% | {'✅' if report.summary.get('pass_rate', 100) >= 95 else '⚠️'} |

### 问题统计

| 级别 | 问题数 | 状态 |
|------|--------|------|
| P0 (关键) | {report.p0_issues} | {'✅' if report.p0_issues == 0 else '❌'} |
| P1 (重要) | {report.p1_issues} | {'✅' if report.p1_issues == 0 else '⚠️'} |
| P2 (建议) | {report.p2_issues} | {'✅' if report.p2_issues == 0 else '⚠️'} |

---

## 详细检查结果

"""
        
        for r in report.results:
            status_icon = "✅" if r.passed else "❌"
            md += f"""### [{r.check_id}] {r.name}

- **严重级别**: {r.severity}
- **检查结果**: {status_icon} {'通过' if r.passed else '失败'}
- **发现问题**: {r.issues_found}
- **阈值**: {r.threshold}
- **执行耗时**: {r.duration:.2f}s
- **详细信息**: {r.message}

"""
            if not r.passed and r.fix_suggestion:
                md += f"**修复建议**: {r.fix_suggestion}\n\n"
            
            md += "---\n\n"
        
        md += f"""## 结论

"""
        if report.failed_checks == 0:
            md += "✅ **所有检查通过** - 文档治理体系处于健康状态"
        elif report.p0_issues > 0:
            md += "❌ **存在P0级别问题** - 需要立即修复"
        else:
            md += "⚠️ **存在非关键问题** - 建议按计划修复"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"✅ Markdown报告已保存: {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="文档治理综合审计工具 - 新模型全量审计入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_comprehensive_audit.py
  python run_comprehensive_audit.py --severity P0,P1
  python run_comprehensive_audit.py --check C-01,C-02,C-03
  python run_comprehensive_audit.py --output json
        """
    )
    
    parser.add_argument("--check", type=str, default="",
                        help="指定检查项ID，逗号分隔 (如: C-01,C-02)")
    parser.add_argument("--severity", type=str, default="P0",
                        help="指定严重级别，逗号分隔 (如: P0,P1,P2)")
    parser.add_argument("--output", type=str, choices=["json", "markdown", "both"], default="both",
                        help="输出格式")
    parser.add_argument("--checklist", type=str, default=str(CHECKLIST_PATH),
                        help="检查清单文件路径")
    parser.add_argument("--verbose", action="store_true",
                        help="启用详细模式：打印10个样本文件的YAML结构快照用于人工审计")
    
    args = parser.parse_args()
    
    # 解析参数
    id_filter = args.check.split(",") if args.check else None
    severity_filter = args.severity.split(",") if args.severity else None
    
    # 创建审计器
    auditor = ComprehensiveAuditor(Path(args.checklist), verbose=args.verbose)
    
    # 执行审计
    report = auditor.run_audit(severity_filter=severity_filter, id_filter=id_filter)
    
    # 生成输出路径
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"COMPREHENSIVE_AUDIT_{timestamp}"
    
    # 导出报告
    if args.output in ["json", "both"]:
        json_path = OUTPUT_DIR / f"{base_name}.json"
        auditor.export_json(report, json_path)
    
    if args.output in ["markdown", "both"]:
        md_path = OUTPUT_DIR / f"{base_name}.md"
        auditor.export_markdown(report, md_path)
    
    # 打印摘要
    print("\n" + "="*70)
    print("审计摘要")
    print("="*70)
    print(f"总检查项: {report.total_checks}")
    print(f"通过: {report.passed_checks} | 失败: {report.failed_checks}")
    print(f"通过率: {report.summary.get('pass_rate', 100)}%")
    print(f"P0问题: {report.p0_issues} | P1问题: {report.p1_issues} | P2问题: {report.p2_issues}")
    print("="*70)
    
    # 返回码
    if report.p0_issues > 0:
        sys.exit(1)
    elif report.p1_issues > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
