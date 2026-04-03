#!/usr/bin/env python3
"""
清风量化系统 - 文件系统健康度扫描脚本
版本: 1.0
用途: 自动化扫描文件系统健康度，辅助人工审查
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

class FileSystemAuditor:
    """文件系统审计器"""
    
    def __init__(self, root_path="."):
        self.root_path = Path(root_path).resolve()
        self.findings = []
        self.statistics = {
            "total_files": 0,
            "total_dirs": 0,
            "audit_time": datetime.now().isoformat(),
            "health_score": 0
        }
    
    def audit_directory_structure(self):
        """审计目录结构"""
        print("🔍 审计目录结构...")
        
        required_dirs = ['src', 'tests', 'docs', 'config', 'scripts', 'data']
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = self.root_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.findings.append({
                    "type": "directory_check",
                    "status": "✅",
                    "message": f"目录存在: {dir_name}/",
                    "severity": "info"
                })
            else:
                missing_dirs.append(dir_name)
                self.findings.append({
                    "type": "directory_check",
                    "status": "❌",
                    "message": f"目录缺失: {dir_name}/",
                    "severity": "warning"
                })
        
        if missing_dirs:
            self.findings.append({
                "type": "summary",
                "status": "⚠️",
                "message": f"缺失目录: {', '.join(missing_dirs)}",
                "severity": "medium"
            })
        
        return len(missing_dirs) == 0
    
    def audit_file_naming(self):
        """审计文件命名规范"""
        print("🔍 审计文件命名规范...")
        
        # 检查Python文件命名
        python_files = list(self.root_path.rglob("*.py"))
        non_standard_names = []
        
        for py_file in python_files:
            filename = py_file.name
            if not filename.islower() and "_" not in filename:
                non_standard_names.append(str(py_file.relative_to(self.root_path)))
        
        if non_standard_names:
            self.findings.append({
                "type": "naming_check",
                "status": "⚠️",
                "message": f"发现 {len(non_standard_names)} 个非标准命名的Python文件",
                "severity": "low",
                "details": non_standard_names[:10]  # 只显示前10个
            })
        
        return len(non_standard_names)
    
    def find_orphan_documents(self, manifest_path="docs/System_Manifest.md"):
        """查找孤儿文档（不在System_Manifest.md中记录的文档）"""
        print("🔍 查找孤儿文档...")
        
        manifest_file = self.root_path / manifest_path
        if not manifest_file.exists():
            self.findings.append({
                "type": "orphan_check",
                "status": "❌",
                "message": f"System_Manifest.md 文件不存在: {manifest_path}",
                "severity": "high"
            })
            return []
        
        # 读取System_Manifest.md内容（简化版本）
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
        except:
            manifest_content = ""
        
        # 查找所有.md文件
        md_files = list(self.root_path.rglob("*.md"))
        orphan_files = []
        
        for md_file in md_files:
            # 相对路径
            rel_path = str(md_file.relative_to(self.root_path))
            
            # 检查是否在System_Manifest.md中被引用
            if rel_path not in manifest_content:
                # 排除归档目录中的文件
                if "06_ARCHIVE" not in rel_path and "99_ARCHIVE" not in rel_path:
                    orphan_files.append(rel_path)
        
        if orphan_files:
            self.findings.append({
                "type": "orphan_check",
                "status": "⚠️",
                "message": f"发现 {len(orphan_files)} 个孤儿文档（未在System_Manifest.md中记录）",
                "severity": "medium",
                "details": orphan_files[:20]  # 只显示前20个
            })
        
        return orphan_files
    
    def check_file_drift(self):
        """检查文件漂移"""
        print("🔍 检查文件漂移...")
        
        drift_findings = []
        
        # 检查src/中是否有文档文件
        src_docs = list((self.root_path / "src").rglob("*.md")) if (self.root_path / "src").exists() else []
        for doc in src_docs:
            drift_findings.append({
                "file": str(doc.relative_to(self.root_path)),
                "issue": "文档文件在源代码目录中",
                "recommendation": "移动到 docs/ 目录"
            })
        
        # 检查docs/中是否有Python文件
        docs_py = list((self.root_path / "docs").rglob("*.py")) if (self.root_path / "docs").exists() else []
        for py_file in docs_py:
            drift_findings.append({
                "file": str(py_file.relative_to(self.root_path)),
                "issue": "Python文件在文档目录中",
                "recommendation": "移动到 src/ 目录"
            })
        
        if drift_findings:
            self.findings.append({
                "type": "drift_check",
                "status": "⚠️",
                "message": f"发现 {len(drift_findings)} 个文件漂移问题",
                "severity": "medium",
                "details": drift_findings
            })
        
        return drift_findings
    
    def collect_statistics(self):
        """收集统计信息"""
        print("📊 收集统计信息...")
        
        total_files = 0
        total_dirs = 0
        
        for root, dirs, files in os.walk(self.root_path):
            # 排除.git目录
            if ".git" in root:
                continue
                
            total_dirs += len(dirs)
            total_files += len(files)
        
        self.statistics["total_files"] = total_files
        self.statistics["total_dirs"] = total_dirs
        
        # 计算健康度评分（简化版本）
        health_score = 100
        
        # 目录完整性扣分
        required_dirs = ['src', 'tests', 'docs', 'config', 'scripts', 'data']
        missing_count = sum(1 for d in required_dirs if not (self.root_path / d).exists())
        health_score -= missing_count * 10
        
        # 孤儿文档扣分
        orphan_docs = self.find_orphan_documents()
        if orphan_docs:
            health_score -= min(len(orphan_docs) * 2, 30)
        
        self.statistics["health_score"] = max(health_score, 0)
        
        return self.statistics
    
    def generate_report(self, output_file="audit_report.json"):
        """生成审计报告"""
        report = {
            "metadata": {
                "system_name": "清风量化系统",
                "audit_date": self.statistics["audit_time"],
                "audit_version": "1.0"
            },
            "statistics": self.statistics,
            "findings": self.findings,
            "summary": {
                "total_findings": len(self.findings),
                "critical_findings": sum(1 for f in self.findings if f.get("severity") == "high"),
                "health_score": self.statistics["health_score"]
            }
        }
        
        output_path = self.root_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 审计报告已生成: {output_path}")
        return output_path
    
    def print_summary(self):
        """打印审计摘要"""
        print("\n" + "="*60)
        print("📋 文件系统审计摘要")
        print("="*60)
        
        print(f"📊 统计信息:")
        print(f"  总文件数: {self.statistics['total_files']}")
        print(f"  总目录数: {self.statistics['total_dirs']}")
        print(f"  健康度评分: {self.statistics['health_score']}/100")
        
        print(f"\n🔍 审计发现 ({len(self.findings)} 项):")
        
        # 按严重性分组
        severity_groups = {"high": [], "medium": [], "low": [], "info": []}
        for finding in self.findings:
            sev = finding.get("severity", "info")
            severity_groups[sev].append(finding)
        
        for severity in ["high", "medium", "low", "info"]:
            findings = severity_groups[severity]
            if findings:
                severity_label = {"high": "🔴 高危", "medium": "🟠 中危", "low": "🟡 低危", "info": "🔵 信息"}[severity]
                print(f"\n  {severity_label} ({len(findings)} 项):")
                for i, finding in enumerate(findings[:3], 1):  # 只显示前3项
                    print(f"    {i}. {finding['status']} {finding['message']}")
                if len(findings) > 3:
                    print(f"    ... 还有 {len(findings)-3} 项")
        
        print("\n" + "="*60)
        
        # 给出建议
        if self.statistics["health_score"] >= 80:
            print("🎉 系统健康度良好，继续保持！")
        elif self.statistics["health_score"] >= 60:
            print("⚠️  系统健康度一般，建议进行优化。")
        else:
            print("❌ 系统健康度较差，建议立即进行深度审查和修复。")
        
        print("="*60)

def main():
    """主函数"""
    print("🚀 启动文件系统健康度审计...")
    
    # 解析命令行参数
    root_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = sys.argv[2] if len(sys.argv) > 2 else "audit_report.json"
    
    auditor = FileSystemAuditor(root_path)
    
    try:
        # 执行各项审计
        auditor.audit_directory_structure()
        auditor.audit_file_naming()
        auditor.find_orphan_documents()
        auditor.check_file_drift()
        auditor.collect_statistics()
        
        # 生成报告
        report_path = auditor.generate_report(output_file)
        
        # 打印摘要
        auditor.print_summary()
        
        print(f"\n✅ 审计完成！详细报告请查看: {report_path}")
        
        # 根据健康度评分返回退出码
        if auditor.statistics["health_score"] >= 70:
            return 0
        elif auditor.statistics["health_score"] >= 50:
            return 1
        else:
            return 2
            
    except Exception as e:
        print(f"❌ 审计过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
