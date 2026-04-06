"""
Layer 8 人机交互层深度审计脚本 v3
三层审计：L1文件系统层、L2文档内容层、L3专业标准层
重点检查：职责重叠、重复文档、目录结构
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

LAYER8_DIR = Path("docs/08_human_ai_interface")
OUTPUT_DIR = Path("docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")


class Layer8DeepAuditorV3:
    """Layer 8 深度审计器 v3"""
    
    def __init__(self):
        self.issues = {
            "L1_文件系统层": [],
            "L2_文档内容层": [],
            "L3_专业标准层": []
        }
        self.stats = {
            "total_files": 0,
            "total_dirs": 0,
            "md_files": 0,
            "blueprint_files": 0,
            "index_files": 0
        }
        self.documents = {}
        self.responsibilities = defaultdict(list)
        self.module_ids = defaultdict(list)
        
    def read_document(self, filepath: Path) -> str:
        """读取文档内容"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except:
                continue
        return ""
    
    def extract_yaml(self, content: str) -> dict:
        """提取YAML头部"""
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            yaml_dict = {}
            current_key = None
            current_value = []
            
            for line in yaml_content.split('\n'):
                if ':' in line and not line.startswith(' '):
                    # 保存之前的键值对
                    if current_key:
                        yaml_dict[current_key] = '\n'.join(current_value).strip()
                    # 开始新的键值对
                    key, value = line.split(':', 1)
                    current_key = key.strip()
                    current_value = [value.strip()] if value.strip() else []
                elif line.startswith(' ') and current_key:
                    # 多行值的续行
                    current_value.append(line)
            
            # 保存最后一个键值对
            if current_key:
                yaml_dict[current_key] = '\n'.join(current_value).strip()
            
            return yaml_dict
        return {}
    
    def audit_L1_filesystem(self):
        """L1 文件系统层审计"""
        print("\n" + "="*60)
        print("L1 文件系统层审计")
        print("="*60)
        
        # 1.1 目录结构检查
        print("\n1.1 目录结构检查...")
        
        dirs = [d for d in LAYER8_DIR.iterdir() if d.is_dir()]
        self.stats['total_dirs'] = len(dirs)
        
        expected_dirs = [
            "01_MONITORING", "02_ALERTING", "03_AUTH", "04_API_DOCS",
            "05_BACKTEST_UI", "06_REPORTING", "07_AUDIT_LOG", "08_MOBILE_PUSH",
            "09_TRADING_JOURNAL", "10_CONFIG_MANAGEMENT", "11_USER_PREFERENCES",
            "12_SYSTEM_STATUS", "13_DATA_MANAGEMENT", "14_STRATEGY_MANAGEMENT",
            "15_PERMISSION_MANAGEMENT", "16_API_RATE_LIMITING", "17_DOCUMENTATION_CENTER",
            "18_KNOWLEDGE_BASE", "19_CI_CD_INTEGRATION", "20_DATA_BACKUP",
            "21_ONLINE_RESEARCH_ENVIRONMENT", "22_PARAMETER_OPTIMIZATION", "23_LIVE_TRADING_INTERFACE"
        ]
        
        for d in dirs:
            if d.name not in expected_dirs and d.name != '.git':
                self.issues["L1_文件系统层"].append({
                    "type": "目录漂移",
                    "severity": "P1",
                    "location": str(d.relative_to(LAYER8_DIR)),
                    "description": f"非标准目录: {d.name}",
                    "suggestion": f"整合到标准目录或归档"
                })
            
            # 检查稀疏目录
            files_in_dir = list(d.glob("*.md"))
            if len(files_in_dir) < 2:
                self.issues["L1_文件系统层"].append({
                    "type": "目录稀疏",
                    "severity": "P2",
                    "location": str(d.relative_to(LAYER8_DIR)),
                    "description": f"目录文件数过少: {len(files_in_dir)}个",
                    "suggestion": "整合到相关目录或补充文档"
                })
        
        # 检查缺失的标准目录
        existing_dir_names = [d.name for d in dirs]
        for expected in expected_dirs:
            if expected not in existing_dir_names:
                self.issues["L1_文件系统层"].append({
                    "type": "目录缺失",
                    "severity": "P2",
                    "location": expected,
                    "description": f"缺少标准目录: {expected}",
                    "suggestion": "创建目录并添加蓝图文档"
                })
        
        # 1.2 文件命名检查
        print("1.2 文件命名检查...")
        
        md_files = list(LAYER8_DIR.glob("**/*.md"))
        self.stats['md_files'] = len(md_files)
        
        for filepath in md_files:
            filename = filepath.name
            
            # 检查命名规范
            if not re.match(r'^[A-Z_0-9]+\.md$', filename) and filename.upper() != 'INDEX.MD':
                self.issues["L1_文件系统层"].append({
                    "type": "命名不规范",
                    "severity": "P2",
                    "location": str(filepath.relative_to(LAYER8_DIR)),
                    "description": f"文件名不符合规范: {filename}",
                    "suggestion": "使用大写字母和下划线命名"
                })
            
            # 检查蓝图文件
            if filename.endswith('_BLUEPRINT.md'):
                self.stats['blueprint_files'] += 1
            
            # 检查索引文件
            if filename.upper() == 'INDEX.MD':
                self.stats['index_files'] += 1
        
        self.stats['total_files'] = len(md_files)
        
        # 1.3 路径引用检查
        print("1.3 路径引用检查...")
        
        for filepath in md_files:
            content = self.read_document(filepath)
            if not content:
                continue
            
            # 检查死链接
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for link_text, link_path in links:
                if link_path.startswith('http') or link_path.startswith('#'):
                    continue
                
                # 解析相对路径
                target_path = filepath.parent / link_path
                target_path = target_path.resolve()
                
                if not target_path.exists():
                    self.issues["L1_文件系统层"].append({
                        "type": "死链接",
                        "severity": "P2",
                        "location": str(filepath.relative_to(LAYER8_DIR)),
                        "description": f"死链接: [{link_text}]({link_path})",
                        "suggestion": "修复或删除链接"
                    })
    
    def audit_L2_content(self):
        """L2 文档内容层审计"""
        print("\n" + "="*60)
        print("L2 文档内容层审计")
        print("="*60)
        
        md_files = list(LAYER8_DIR.glob("**/*.md"))
        
        # 2.1 职责驱动原则检查
        print("\n2.1 职责驱动原则检查...")
        
        for filepath in md_files:
            if filepath.name.upper() == 'INDEX.MD':
                continue
            
            content = self.read_document(filepath)
            if not content:
                continue
            
            yaml_data = self.extract_yaml(content)
            
            # 存储文档信息
            self.documents[filepath.name] = {
                "path": str(filepath.relative_to(LAYER8_DIR)),
                "yaml": yaml_data,
                "content": content[:2000]  # 前2000字符用于分析
            }
            
            # 检查职责字段
            responsibility = yaml_data.get('responsibility', '')
            if responsibility:
                self.responsibilities[responsibility].append(filepath.name)
            
            # 检查module_id
            module_id = yaml_data.get('module_id', '')
            if module_id:
                self.module_ids[module_id].append(filepath.name)
            
            # 检查职责描述是否清晰
            if not responsibility or len(responsibility) < 20:
                self.issues["L2_文档内容层"].append({
                    "type": "职责不清",
                    "severity": "P1",
                    "location": str(filepath.relative_to(LAYER8_DIR)),
                    "description": f"职责描述不清晰或缺失",
                    "suggestion": "添加明确的职责描述，说明负责和不负责的内容"
                })
            
            # 检查Layer定位
            layer = yaml_data.get('layer', '')
            if 'Layer 8' not in layer and '人机交互' not in layer:
                self.issues["L2_文档内容层"].append({
                    "type": "Layer定位错误",
                    "severity": "P2",
                    "location": str(filepath.relative_to(LAYER8_DIR)),
                    "description": f"Layer定位不正确: {layer}",
                    "suggestion": "更新为 Layer 8 (人机交互层)"
                })
        
        # 检查职责重叠
        print("检查职责重叠...")
        for resp, files in self.responsibilities.items():
            if len(files) > 1:
                self.issues["L2_文档内容层"].append({
                    "type": "职责重叠",
                    "severity": "P1",
                    "location": ", ".join(files),
                    "description": f"多个文档职责相同: {resp[:50]}...",
                    "suggestion": "明确各文档职责边界"
                })
        
        # 检查module_id重复
        print("检查module_id重复...")
        for mid, files in self.module_ids.items():
            if len(files) > 1:
                self.issues["L2_文档内容层"].append({
                    "type": "module_id重复",
                    "severity": "P1",
                    "location": ", ".join(files),
                    "description": f"重复的module_id: {mid}",
                    "suggestion": "为每个文档分配唯一的module_id"
                })
        
        # 2.2 索引完备性检查
        print("\n2.2 索引完备性检查...")
        
        # 检查根目录INDEX.md
        root_index = LAYER8_DIR / "index.md"
        if not root_index.exists():
            self.issues["L2_文档内容层"].append({
                "type": "缺少主索引",
                "severity": "P1",
                "location": "docs/08_human_ai_interface/",
                "description": "缺少根目录INDEX.md",
                "suggestion": "创建主索引文件"
            })
        
        # 检查子目录INDEX.md
        dirs = [d for d in LAYER8_DIR.iterdir() if d.is_dir()]
        for d in dirs:
            index_file = d / "INDEX.md"
            if not index_file.exists():
                index_file = d / "index.md"
            
            if not index_file.exists():
                self.issues["L2_文档内容层"].append({
                    "type": "缺少子目录索引",
                    "severity": "P2",
                    "location": str(d.relative_to(LAYER8_DIR)),
                    "description": f"缺少INDEX.md",
                    "suggestion": "创建子目录索引文件"
                })
        
        # 2.3 版本隔离检查
        print("\n2.3 版本隔离检查...")
        
        # 检查重复文档（基于文件名相似性）
        filenames = [f.name for f in md_files if f.name.upper() != 'INDEX.MD']
        seen = set()
        for name in filenames:
            # 提取核心名称
            core_name = re.sub(r'_v\d+.*\.md$', '.md', name, flags=re.IGNORECASE)
            core_name = re.sub(r'_\d{8}.*\.md$', '.md', core_name)
            
            if core_name in seen:
                self.issues["L2_文档内容层"].append({
                    "type": "可能重复",
                    "severity": "P2",
                    "location": name,
                    "description": f"可能存在重复文档",
                    "suggestion": "检查并归档旧版本"
                })
            seen.add(core_name)
        
        # 2.4 文档代码对应检查
        print("\n2.4 文档代码对应检查...")
        
        for filepath in md_files:
            if filepath.name.upper() == 'INDEX.MD':
                continue
            
            content = self.read_document(filepath)
            if not content:
                continue
            
            # 检查是否有实质内容
            text_content = re.sub(r'[#*\-\n\s]', '', content)
            if len(text_content) < 100:
                self.issues["L2_文档内容层"].append({
                    "type": "内容不完整",
                    "severity": "P2",
                    "location": str(filepath.relative_to(LAYER8_DIR)),
                    "description": f"文档内容过少: {len(text_content)}字符",
                    "suggestion": "补充文档内容"
                })
    
    def audit_L3_professional(self):
        """L3 专业标准层审计"""
        print("\n" + "="*60)
        print("L3 专业标准层审计")
        print("="*60)
        
        md_files = list(LAYER8_DIR.glob("**/*.md"))
        
        # 3.1 五大原则符合性检查
        print("\n3.1 五大原则符合性检查...")
        
        for filepath in md_files:
            if filepath.name.upper() == 'INDEX.MD':
                continue
            
            content = self.read_document(filepath)
            if not content:
                continue
            
            yaml_data = self.extract_yaml(content)
            
            # 检查YAML字段完整性
            required_fields = ['module_id', 'version', 'status', 'owner', 'responsibility', 'layer']
            missing_fields = [f for f in required_fields if f not in yaml_data]
            
            if missing_fields:
                self.issues["L3_专业标准层"].append({
                    "type": "YAML字段缺失",
                    "severity": "P2",
                    "location": str(filepath.relative_to(LAYER8_DIR)),
                    "description": f"缺少字段: {', '.join(missing_fields)}",
                    "suggestion": "补充缺失的YAML字段"
                })
            
            # 检查双YAML头部（只检查文档开头前30行）
            # YAML头部应该只在文档开头，前30行内只应该有2个---
            lines = content.split('\n')[:30]
            yaml_sep_lines = [i for i, line in enumerate(lines) if line.strip() == '---']
            
            # 如果前30行有超过2个---，检查是否是双YAML头部
            if len(yaml_sep_lines) > 2:
                # 检查第1和第2个---之间是否有内容（第一个YAML）
                # 检查第3和第4个---之间是否有内容（第二个YAML）
                if len(yaml_sep_lines) >= 4:
                    # 检查是否是双YAML模式
                    first_yaml_end = yaml_sep_lines[1]
                    second_yaml_start = yaml_sep_lines[2]
                    # 如果两个YAML之间只有空行，说明是双YAML头部
                    between = lines[first_yaml_end+1:second_yaml_start]
                    if all(line.strip() == '' or line.strip().startswith('\ufeff') for line in between):
                        self.issues["L3_专业标准层"].append({
                            "type": "双YAML头部",
                            "severity": "P1",
                            "location": str(filepath.relative_to(LAYER8_DIR)),
                            "description": f"检测到双YAML头部结构",
                            "suggestion": "合并为单一YAML头部"
                        })
        
        # 3.2 文档分类检查
        print("\n3.2 文档分类检查...")
        
        # 检查蓝图文件是否在正确目录
        for filepath in md_files:
            if filepath.name.endswith('_BLUEPRINT.md'):
                parent_name = filepath.parent.name
                # 蓝图文件应该在编号目录下
                if not re.match(r'^\d{2}_', parent_name):
                    self.issues["L3_专业标准层"].append({
                        "type": "分类错误",
                        "severity": "P2",
                        "location": str(filepath.relative_to(LAYER8_DIR)),
                        "description": f"蓝图文件不在标准编号目录下",
                        "suggestion": "移动到正确的编号目录"
                    })
        
        # 3.3 编号体系检查
        print("\n3.3 编号体系检查...")
        
        for filepath in md_files:
            if filepath.name.upper() == 'INDEX.MD':
                continue
            
            content = self.read_document(filepath)
            yaml_data = self.extract_yaml(content)
            
            module_id = yaml_data.get('module_id', '')
            
            # 检查module_id格式
            if module_id and not re.match(r'^[A-Z_0-9]+_\d{3}$', module_id):
                self.issues["L3_专业标准层"].append({
                    "type": "编号不规范",
                    "severity": "P2",
                    "location": str(filepath.relative_to(LAYER8_DIR)),
                    "description": f"module_id格式不规范: {module_id}",
                    "suggestion": "使用大写字母、下划线和三位数字编号"
                })
        
        # 3.4 文档质量检查
        print("\n3.4 文档质量检查...")
        
        for filepath in md_files:
            if filepath.name.upper() == 'INDEX.MD':
                continue
            
            content = self.read_document(filepath)
            if not content:
                continue
            
            # 检查标准章节结构
            required_sections = ['概述', '核心功能', '技术实现']
            missing_sections = []
            
            for section in required_sections:
                if section not in content and section.upper() not in content:
                    missing_sections.append(section)
            
            if len(missing_sections) == len(required_sections):
                self.issues["L3_专业标准层"].append({
                    "type": "结构不完整",
                    "severity": "P2",
                    "location": str(filepath.relative_to(LAYER8_DIR)),
                    "description": "缺少标准章节结构",
                    "suggestion": "添加概述、核心功能、技术实现等章节"
                })
    
    def run_audit(self):
        """执行完整审计"""
        print("="*60)
        print("Layer 8 人机交互层深度审计 v3")
        print("="*60)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: {LAYER8_DIR}")
        print("="*60)
        
        # 执行三层审计
        self.audit_L1_filesystem()
        self.audit_L2_content()
        self.audit_L3_professional()
        
        # 统计问题
        total_issues = sum(len(issues) for issues in self.issues.values())
        p1_issues = sum(1 for issues in self.issues.values() for i in issues if i['severity'] == 'P1')
        p2_issues = sum(1 for issues in self.issues.values() for i in issues if i['severity'] == 'P2')
        
        print("\n" + "="*60)
        print("审计完成")
        print("="*60)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"蓝图文件: {self.stats['blueprint_files']}")
        print(f"索引文件: {self.stats['index_files']}")
        print(f"总问题数: {total_issues}")
        print(f"  - P1级问题: {p1_issues}")
        print(f"  - P2级问题: {p2_issues}")
        
        return {
            "stats": self.stats,
            "issues": self.issues,
            "total_issues": total_issues,
            "p1_issues": p1_issues,
            "p2_issues": p2_issues
        }


def generate_report(result: dict):
    """生成审计报告"""
    report_path = OUTPUT_DIR / f"LAYER8_DEEP_AUDIT_REPORT_V3_{datetime.now().strftime('%Y%m%d')}.md"
    
    # 按类型统计问题
    issue_stats = defaultdict(lambda: defaultdict(int))
    for level, issues in result['issues'].items():
        for issue in issues:
            issue_stats[level][issue['type']] += 1
    
    report = f"""---
module_id: LAYER8DEEPAUDITV3_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 审计团队
responsibility:
  - 人机交互层审计
  - 文档治理
  - 质量保证
standard_type: 专业量化机构审计报告
applicable_scope: Layer 8 人机交互层
compliance_level: 专业标准
---

# Layer 8 人机交互层深度审计报告 V3

**审计日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: docs/08_human_ai_interface  
**审计方法**: 三层审计框架 (L1-L3)  
**Git备份分支**: backup/layer8-optimization-20260407

---

## 审计统计

| 指标 | 数量 |
|------|------|
| 总文件数 | {result['stats']['total_files']} |
| 蓝图文件 | {result['stats']['blueprint_files']} |
| 索引文件 | {result['stats']['index_files']} |
| 总问题数 | {result['total_issues']} |
| P1级问题 | {result['p1_issues']} |
| P2级问题 | {result['p2_issues']} |

---

## L1 文件系统层问题 ({len(result['issues']['L1_文件系统层'])}个)

"""
    
    for issue in result['issues']['L1_文件系统层']:
        report += f"""### {issue['type']} [{issue['severity']}]

- **位置**: {issue['location']}
- **描述**: {issue['description']}
- **建议**: {issue['suggestion']}

"""
    
    report += f"""---

## L2 文档内容层问题 ({len(result['issues']['L2_文档内容层'])}个)

"""
    
    for issue in result['issues']['L2_文档内容层']:
        report += f"""### {issue['type']} [{issue['severity']}]

- **位置**: {issue['location']}
- **描述**: {issue['description']}
- **建议**: {issue['suggestion']}

"""
    
    report += f"""---

## L3 专业标准层问题 ({len(result['issues']['L3_专业标准层'])}个)

"""
    
    for issue in result['issues']['L3_专业标准层']:
        report += f"""### {issue['type']} [{issue['severity']}]

- **位置**: {issue['location']}
- **描述**: {issue['description']}
- **建议**: {issue['suggestion']}

"""
    
    report += f"""---

## 问题分布统计

| 层级 | 问题数 | P1级 | P2级 |
|------|--------|------|------|
| L1 文件系统层 | {len(result['issues']['L1_文件系统层'])} | {sum(1 for i in result['issues']['L1_文件系统层'] if i['severity']=='P1')} | {sum(1 for i in result['issues']['L1_文件系统层'] if i['severity']=='P2')} |
| L2 文档内容层 | {len(result['issues']['L2_文档内容层'])} | {sum(1 for i in result['issues']['L2_文档内容层'] if i['severity']=='P1')} | {sum(1 for i in result['issues']['L2_文档内容层'] if i['severity']=='P2')} |
| L3 专业标准层 | {len(result['issues']['L3_专业标准层'])} | {sum(1 for i in result['issues']['L3_专业标准层'] if i['severity']=='P1')} | {sum(1 for i in result['issues']['L3_专业标准层'] if i['severity']=='P2')} |

---

## 优先修复建议

### P1级问题（立即修复）

"""
    
    p1_issues = [i for issues in result['issues'].values() for i in issues if i['severity'] == 'P1']
    if p1_issues:
        for i, issue in enumerate(p1_issues[:10], 1):
            report += f"{i}. **{issue['type']}**: {issue['location']}\n"
    else:
        report += "无P1级问题\n"
    
    report += f"""
### P2级问题（短期改进）

"""
    
    p2_issues = [i for issues in result['issues'].values() for i in issues if i['severity'] == 'P2']
    if p2_issues:
        for i, issue in enumerate(p2_issues[:10], 1):
            report += f"{i}. **{issue['type']}**: {issue['location']}\n"
    else:
        report += "无P2级问题\n"
    
    report += f"""
---

## 审计质量声明

**审计执行**: Audit Sentinel  
**审计标准**: 专业量化机构五大原则  
**审计方法**: 三层审计框架 (L1-L3)  
**审计时间**: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8-sig') as f:
        f.write(report)
    
    print(f"\n报告已生成: {report_path}")
    
    # 保存JSON结果
    json_path = OUTPUT_DIR / f"layer8_deep_audit_v3_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"JSON结果已保存: {json_path}")


def main():
    auditor = Layer8DeepAuditorV3()
    result = auditor.run_audit()
    generate_report(result)


if __name__ == "__main__":
    main()
