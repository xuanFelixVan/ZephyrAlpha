#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZephyrAlpha 10-Dimension Deep Audit System
Full-dimensional logical penetration audit for ZephyrAlpha system
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# Fix encoding for Windows
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# ============== Configuration ==============
BASE_DIR = Path("d:/ZephyrAlpha")
EXCLUDE_DIRS = {'.git', '.venv', '.venv-1', '__pycache__', '.cursor', '.trae', '.audit_fix_backup', '.github'}

# ============== Audit Results Container ==============
class AuditReport:
    def __init__(self):
        self.dimension1_paths = []  # Physical path compliance
        self.dimension2_duplicates = defaultdict(list)  # module_id duplicates
        self.dimension3_yaml_issues = []  # YAML metadata issues
        self.dimension4_dead_links = []  # Dead links
        self.dimension4_orphans = []  # Orphan files
        self.dimension5_bypass_risks = []  # Protection bypass risks
        self.dimension6_yaml_bombs = []  # YAML logic bombs
        self.dimension7_layer_violations = []  # Layer violations
        self.dimension8_script_issues = []  # Script security issues
        self.dimension9_missing_dod = []  # Missing Definition of Done
        self.dimension10_governance_trend = {}  # Governance trend

report = AuditReport()

# Simple YAML frontmatter parser
def parse_yaml_frontmatter(content):
    """Parse YAML frontmatter from markdown content"""
    if not content.startswith('---'):
        return None, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content

    yaml_text = parts[1].strip()
    body = parts[2]

    # Simple key-value parsing
    metadata = {}
    for line in yaml_text.split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith('#'):
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"\'')
            metadata[key] = value

    return metadata, body

# ============== Dimension 1: Physical Path Compliance ==============
def audit_dimension1_paths():
    """Scan for non-ASCII, spaces, brackets, special symbols"""
    print("[D1] Scanning physical path compliance...")

    issues = []
    # Pattern for non-ASCII, spaces, brackets, Chinese characters
    pattern = re.compile(r'[^\x00-\x7F]|\s|[\[\]<>{}]|[\u4e00-\u9fff]')

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        rel_root = Path(root).relative_to(BASE_DIR)

        # Check directory names
        for d in dirs:
            if pattern.search(d):
                issues.append({
                    'type': 'DIR',
                    'path': str(rel_root / d),
                    'issue': 'Non-ASCII/Space/Special char'
                })

        # Check filenames
        for f in files:
            if pattern.search(f):
                issues.append({
                    'type': 'FILE',
                    'path': str(rel_root / f),
                    'issue': 'Non-ASCII/Space/Special char'
                })

    report.dimension1_paths = issues
    print(f"     Found {len(issues)} path compliance issues")
    return issues

# ============== Dimension 2: Source Uniqueness Conflict ==============
def audit_dimension2_module_ids():
    """Global search for module_id, detect duplicates"""
    print("[D2] Checking module_id uniqueness...")

    module_ids = defaultdict(list)

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for f in files:
            if f.endswith('.md'):
                filepath = Path(root) / f
                rel_path = filepath.relative_to(BASE_DIR)

                try:
                    content = filepath.read_text(encoding='utf-8', errors='ignore')
                    # Find module_id
                    matches = re.findall(r'^module_id:\s*(\S+)', content, re.MULTILINE)
                    for mid in matches:
                        module_ids[mid].append(str(rel_path))
                except Exception:
                    pass

    # Filter duplicates
    duplicates = {k: v for k, v in module_ids.items() if len(v) > 1}
    report.dimension2_duplicates = duplicates
    print(f"     Found {len(duplicates)} duplicate module_ids")
    return duplicates

# ============== Dimension 3: Metadata Lineage Integrity ==============
def audit_dimension3_yaml_frontmatter():
    """Check YAML Frontmatter for all .md files"""
    print("[D3] Checking YAML frontmatter integrity...")

    issues = []
    required_fields = {'owner', 'version', 'status'}

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for f in files:
            if f.endswith('.md'):
                filepath = Path(root) / f
                rel_path = filepath.relative_to(BASE_DIR)

                try:
                    content = filepath.read_text(encoding='utf-8', errors='ignore')
                    metadata, body = parse_yaml_frontmatter(content)

                    if metadata is None:
                        issues.append({
                            'path': str(rel_path),
                            'type': 'MISSING_YAML',
                            'missing': list(required_fields)
                        })
                    else:
                        missing = required_fields - set(metadata.keys())
                        if missing:
                            issues.append({
                                'path': str(rel_path),
                                'type': 'MISSING_FIELDS',
                                'missing': list(missing)
                            })

                except Exception as e:
                    issues.append({
                        'path': str(rel_path),
                        'type': 'READ_ERROR',
                        'error': str(e)
                    })

    report.dimension3_yaml_issues = issues
    print(f"     Found {len(issues)} YAML metadata issues")
    return issues

# ============== Dimension 4: Index System Link Breakage ==============
def audit_dimension4_index_links():
    """Cross-check INDEX.md links with physical files"""
    print("[D4] Checking index system link integrity...")

    dead_links = []
    indexed_files = set()

    # Find all INDEX.md files
    index_files = list(BASE_DIR.rglob('INDEX.md'))

    for index_file in index_files:
        rel_index = index_file.relative_to(BASE_DIR)
        try:
            content = index_file.read_text(encoding='utf-8', errors='ignore')

            # Extract Markdown links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

            for text, link in links:
                if link.endswith('.md') and not link.startswith('http'):
                    # Resolve relative path
                    if link.startswith('/'):
                        target = BASE_DIR / link.lstrip('/')
                    else:
                        target = index_file.parent / link

                    try:
                        target_resolved = target.resolve()
                        if not target_resolved.exists():
                            dead_links.append({
                                'index': str(rel_index),
                                'link': link,
                                'text': text
                            })
                        else:
                            indexed_files.add(str(target_resolved.relative_to(BASE_DIR)))
                    except Exception:
                        dead_links.append({
                            'index': str(rel_index),
                            'link': link,
                            'text': text
                        })

        except Exception:
            pass

    # Find orphan files (all .md files)
    all_md_files = set()
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith('.md'):
                all_md_files.add(str(Path(root).relative_to(BASE_DIR) / f))

    orphans = all_md_files - indexed_files - {'INDEX.md'}

    report.dimension4_dead_links = dead_links
    report.dimension4_orphans = list(orphans)
    print(f"     Found {len(dead_links)} dead links, {len(orphans)} orphan files")
    return dead_links, list(orphans)

# ============== Dimension 5: Protection Bypass Risk ==============
def audit_dimension5_protection_bypass():
    """Evaluate pre-commit and index_compiler logic"""
    print("[D5] Evaluating protection bypass risks...")

    issues = []

    # Check pre-commit config
    precommit_file = BASE_DIR / '.pre-commit-config.yaml'
    if precommit_file.exists():
        content = precommit_file.read_text(encoding='utf-8', errors='ignore')

        # Check if index_compiler is integrated
        if 'index_compiler' not in content.lower():
            issues.append({
                'file': '.pre-commit-config.yaml',
                'risk': 'Missing index_compiler integration',
                'vector': 'git commit may bypass index checks'
            })

    # Check scripts directory
    scripts_dir = BASE_DIR / 'scripts'
    if scripts_dir.exists():
        for script in scripts_dir.glob('*.py'):
            content = script.read_text(encoding='utf-8', errors='ignore')

            # Check path escaping
            if 'glob' in content and 'recursive' in content:
                if 'escape' not in content.lower() and 'sanitize' not in content.lower():
                    issues.append({
                        'file': str(script.relative_to(BASE_DIR)),
                        'risk': 'Path not sanitized',
                        'vector': 'Special char paths may cause issues'
                    })

    report.dimension5_bypass_risks = issues
    print(f"     Found {len(issues)} bypass risks")
    return issues

# ============== Dimension 6: Dual YAML Logic Bomb ==============
def audit_dimension6_yaml_bombs():
    """Scan for YAML markers misidentified in body"""
    print("[D6] Scanning for YAML logic bombs...")

    issues = []

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for f in files:
            if f.endswith('.md'):
                filepath = Path(root) / f
                rel_path = filepath.relative_to(BASE_DIR)

                try:
                    content = filepath.read_text(encoding='utf-8', errors='ignore')
                    lines = content.split('\n')

                    # Skip frontmatter
                    in_frontmatter = False
                    frontmatter_ended = False

                    for i, line in enumerate(lines):
                        if i == 0 and line.strip() == '---':
                            in_frontmatter = True
                            continue

                        if in_frontmatter and line.strip() == '---':
                            in_frontmatter = False
                            frontmatter_ended = True
                            continue

                        if frontmatter_ended and not in_frontmatter:
                            # Check for problematic patterns in body
                            if line.strip() == '---':
                                issues.append({
                                    'path': str(rel_path),
                                    'line': i + 1,
                                    'issue': 'Isolated --- in body',
                                    'risk': 'May be misidentified as YAML block'
                                })

                            # Check module_id in body
                            if re.match(r'^module_id:\s*\S+', line.strip()):
                                issues.append({
                                    'path': str(rel_path),
                                    'line': i + 1,
                                    'issue': 'module_id declaration in body',
                                    'risk': 'May override metadata'
                                })

                except Exception:
                    pass

    report.dimension6_yaml_bombs = issues
    print(f"     Found {len(issues)} YAML logic bombs")
    return issues

# ============== Dimension 7: Layer Violation ==============
def audit_dimension7_layer_violations():
    """Check L5 implementation for hardcoded global params"""
    print("[D7] Checking for layer violations...")

    issues = []

    # Check L5 directories
    impl_dirs = [
        BASE_DIR / 'docs' / '05_IMPLEMENTATION',
        BASE_DIR / 'src' / 'modules'
    ]

    global_patterns = [
        r'(?i)risk_threshold\s*=\s*[\d.]+',
        r'(?i)fee_rate\s*=\s*[\d.]+',
        r'(?i)max_leverage\s*=\s*[\d.]+',
        r'(?i)DEFAULT_.+\s*=\s*[\d.]+',
        r'(?i)HARD_CODED',
    ]

    for impl_dir in impl_dirs:
        if not impl_dir.exists():
            continue

        for root, dirs, files in os.walk(impl_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for f in files:
                if f.endswith(('.py', '.md', '.yaml', '.yml')):
                    filepath = Path(root) / f
                    rel_path = filepath.relative_to(BASE_DIR)

                    try:
                        content = filepath.read_text(encoding='utf-8', errors='ignore')

                        for pattern in global_patterns:
                            matches = re.finditer(pattern, content)
                            for match in matches:
                                issues.append({
                                    'path': str(rel_path),
                                    'line': content[:match.start()].count('\n') + 1,
                                    'violation': match.group()[:50],
                                    'type': 'L5 hardcoded global param'
                                })

                    except Exception:
                        pass

    report.dimension7_layer_violations = issues
    print(f"     Found {len(issues)} layer violations")
    return issues

# ============== Dimension 8: Script Security ==============
def audit_dimension8_script_security():
    """Audit core production scripts for robustness"""
    print("[D8] Auditing script security...")

    issues = []
    scripts_dir = BASE_DIR / 'scripts'

    if not scripts_dir.exists():
        return issues

    # Dangerous patterns
    dangerous_patterns = [
        (r'os\.system\s*\(', 'Uses os.system(), command injection risk'),
        (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'subprocess with shell=True'),
        (r'eval\s*\(', 'Uses eval()'),
        (r'exec\s*\(', 'Uses exec()'),
    ]

    # Windows specific issues
    windows_issues = [
        (r'["\'].*\\\\.*["\']', 'Windows double backslash escape'),
        (r'\.replace\s*\(\s*["\']\\\\["\']', 'Manual path separator handling'),
    ]

    for script in scripts_dir.rglob('*.py'):
        if 'archive' in str(script):
            continue

        rel_path = script.relative_to(BASE_DIR)

        try:
            content = script.read_text(encoding='utf-8', errors='ignore')

            # Check dangerous patterns
            for pattern, desc in dangerous_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        'script': str(rel_path),
                        'line': content[:match.start()].count('\n') + 1,
                        'issue': desc,
                        'severity': 'High'
                    })

            # Check Windows path issues
            for pattern, desc in windows_issues:
                matches = re.finditer(pattern, content)
                for match in matches:
                    issues.append({
                        'script': str(rel_path),
                        'line': content[:match.start()].count('\n') + 1,
                        'issue': desc,
                        'severity': 'Medium'
                    })

        except Exception:
            pass

    report.dimension8_script_issues = issues
    print(f"     Found {len(issues)} script security issues")
    return issues

# ============== Dimension 9: SOP Closure Effectiveness ==============
def audit_dimension9_sop_completeness():
    """Identify docs with steps but missing Definition of Done"""
    print("[D9] Checking SOP completeness...")

    issues = []
    dod_patterns = [
        r'(?i)definition of done',
        r'(?i)done criteria',
        r'(?i)##\s*done',
    ]

    step_patterns = [
        r'(?i)^##?\s*step',
        r'(?i)^##?\s*procedure',
    ]

    for root, dirs, files in os.walk(BASE_DIR / 'docs'):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for f in files:
            if f.endswith('.md'):
                filepath = Path(root) / f
                rel_path = filepath.relative_to(BASE_DIR)

                try:
                    content = filepath.read_text(encoding='utf-8', errors='ignore')

                    # Check for steps
                    has_steps = any(re.search(p, content, re.MULTILINE) for p in step_patterns)

                    # Check for DoD
                    has_dod = any(re.search(p, content, re.MULTILINE) for p in dod_patterns)

                    if has_steps and not has_dod:
                        issues.append({
                            'path': str(rel_path),
                            'issue': 'Has steps but missing Definition of Done',
                            'type': 'SOP_GAP'
                        })

                except Exception:
                    pass

    report.dimension9_missing_dod = issues
    print(f"     Found {len(issues)} docs missing DoD")
    return issues

# ============== Dimension 10: Automation Orphan Trend ==============
def audit_dimension10_governance_trend():
    """Compare with historical reports for governance rebound"""
    print("[D10] Analyzing governance trend...")

    reports_dir = BASE_DIR / 'reports'

    if not reports_dir.exists():
        return {'status': 'N/A', 'reason': 'reports dir missing'}

    # Find migration reports
    migration_reports = sorted(reports_dir.glob('migration_*.md'))

    if len(migration_reports) < 1:
        return {'status': 'N/A', 'reason': 'No migration reports'}

    # Read latest report
    latest = migration_reports[-1]
    try:
        content = latest.read_text(encoding='utf-8', errors='ignore')

        # Extract stats
        stats = {}
        orphan_match = re.search(r'(?:orphan|孤儿).*?(\d+)', content, re.IGNORECASE)
        if orphan_match:
            stats['orphan_count'] = int(orphan_match.group(1))

        governance_match = re.search(r'(?:governance|治理率).*?(\d+\.?\d*)%', content, re.IGNORECASE)
        if governance_match:
            stats['governance_rate'] = float(governance_match.group(1))

        current_orphans = len(report.dimension4_orphans)
        historical = stats.get('orphan_count', current_orphans)

        trend_analysis = {
            'status': 'OK',
            'latest_report': str(latest.name),
            'historical_orphans': historical,
            'current_orphans': current_orphans,
            'governance_rate': stats.get('governance_rate', 'N/A'),
            'trend': 'stable' if historical == current_orphans else
                    'rebound' if historical < current_orphans else 'improving'
        }

    except Exception as e:
        trend_analysis = {'status': 'error', 'error': str(e)}

    report.dimension10_governance_trend = trend_analysis
    print(f"     Trend: {trend_analysis.get('trend', 'unknown')}")
    return trend_analysis

# ============== Generate Report ==============
def generate_report():
    """Generate standardized Digital System Health White Paper"""

    # Execute all audits
    d1 = audit_dimension1_paths()
    d2 = audit_dimension2_module_ids()
    d3 = audit_dimension3_yaml_frontmatter()
    d4_dead, d4_orphan = audit_dimension4_index_links()
    d5 = audit_dimension5_protection_bypass()
    d6 = audit_dimension6_yaml_bombs()
    d7 = audit_dimension7_layer_violations()
    d8 = audit_dimension8_script_security()
    d9 = audit_dimension9_sop_completeness()
    d10 = audit_dimension10_governance_trend()

    output = []
    output.append("# ZephyrAlpha System Health White Paper")
    output.append("## 10-Dimension Deep Audit Report")
    output.append("")
    output.append(f"**Audit Time**: 2026-04-13T04:32:59+08:00")
    output.append(f"**Audit Scope**: d:/ZephyrAlpha")
    output.append("")
    output.append("---")
    output.append("")

    # Risk Classification Table
    output.append("## Risk Classification Summary")
    output.append("")

    critical = []
    high = []
    medium = []
    low = []

    # Classification logic
    for item in d1:
        if 'DIR' in item['type']:
            high.append(('D1-Path', item['path'], item['issue']))
        else:
            medium.append(('D1-Path', item['path'], item['issue']))

    for mid, paths in d2.items():
        if len(paths) > 2:
            critical.append(('D2-ID', f"module_id: {mid}", f"Duplicated {len(paths)} times"))
        else:
            high.append(('D2-ID', f"module_id: {mid}", f"Duplicated: {', '.join(paths)}"))

    for item in d3:
        if item['type'] == 'MISSING_YAML':
            high.append(('D3-YAML', item['path'], f"Missing: {', '.join(item['missing'])}"))
        elif item['type'] == 'MISSING_FIELDS':
            medium.append(('D3-YAML', item['path'], f"Missing: {', '.join(item['missing'])}"))

    for item in d4_dead:
        high.append(('D4-Link', item['index'], f"Dead: {item['link']} ({item['text']})"))

    for item in d4_orphan[:50]:
        low.append(('D4-Orphan', item, 'Not indexed'))

    for item in d5:
        high.append(('D5-Bypass', item['file'], item['risk']))

    for item in d6:
        medium.append(('D6-YAML', item['path'], f"L{item['line']}: {item['issue']}"))

    for item in d7[:30]:
        medium.append(('D7-Layer', item['path'], f"L{item['line']}: {item['violation']}..."))

    for item in d8:
        if item['severity'] == 'High':
            critical.append(('D8-Script', item['script'], f"L{item['line']}: {item['issue']}"))
        else:
            medium.append(('D8-Script', item['script'], f"L{item['line']}: {item['issue']}"))

    for item in d9[:30]:
        low.append(('D9-SOP', item['path'], item['issue']))

    # Output tables
    output.append("### Critical Level")
    output.append("| Dimension | Location | Issue |")
    output.append("|-----------|----------|-------|")
    for dim, loc, desc in critical:
        output.append(f"| {dim} | `{loc}` | {desc} |")
    if not critical:
        output.append("| - | - | No Critical issues found |")
    output.append("")

    output.append("### High Level")
    output.append("| Dimension | Location | Issue |")
    output.append("|-----------|----------|-------|")
    for dim, loc, desc in high[:30]:
        output.append(f"| {dim} | `{loc}` | {desc} |")
    if len(high) > 30:
        output.append(f"| ... | ... | Plus {len(high)-30} more High issues |")
    output.append("")

    output.append("### Medium Level")
    output.append("| Dimension | Location | Issue |")
    output.append("|-----------|----------|-------|")
    for dim, loc, desc in medium[:30]:
        output.append(f"| {dim} | `{loc}` | {desc} |")
    if len(medium) > 30:
        output.append(f"| ... | ... | Plus {len(medium)-30} more Medium issues |")
    output.append("")

    output.append("### Low Level")
    output.append("| Dimension | Location | Issue |")
    output.append("|-----------|----------|-------|")
    for dim, loc, desc in low[:20]:
        output.append(f"| {dim} | `{loc}` | {desc} |")
    if len(low) > 20:
        output.append(f"| ... | ... | Plus {len(low)-20} more Low issues |")
    output.append("")

    # Detailed Findings
    output.append("---")
    output.append("## Detailed Audit Findings")
    output.append("")

    # D1 Details
    output.append("### D1: Physical Path Compliance")
    output.append(f"**Issues Found**: {len(d1)}")
    for item in d1[:30]:
        output.append(f"- [{item['type']}] `{item['path']}` - {item['issue']}")
    if len(d1) > 30:
        output.append(f"- ... Plus {len(d1)-30} more issues")
    output.append("")

    # D2 Details
    output.append("### D2: Source Uniqueness Conflict")
    output.append(f"**Duplicate module_ids**: {len(d2)}")
    for mid, paths in list(d2.items())[:15]:
        output.append(f"- **{mid}**: Found in {len(paths)} files")
        for p in paths:
            output.append(f"  - `{p}`")
    output.append("")

    # D3 Details
    output.append("### D3: Metadata Lineage Integrity")
    output.append(f"**Problem Files**: {len(d3)}")
    for item in d3[:20]:
        output.append(f"- `{item['path']}`: {item['type']}")
    output.append("")

    # D4 Details
    output.append("### D4: Index System Link Breakage")
    output.append(f"**Dead Links**: {len(d4_dead)} | **Orphan Files**: {len(d4_orphan)}")
    output.append("")
    output.append("#### Sample Orphan Files:")
    for item in d4_orphan[:20]:
        output.append(f"- `{item}`")
    output.append("")

    # D5 Details
    output.append("### D5: Protection Bypass Risk")
    output.append(f"**Risks Found**: {len(d5)}")
    for item in d5:
        output.append(f"- `{item['file']}`: {item['risk']}")
    output.append("")

    # D6 Details
    output.append("### D6: Dual YAML Logic Bomb")
    output.append(f"**Issues Found**: {len(d6)}")
    for item in d6[:15]:
        output.append(f"- `{item['path']}` L{item['line']}: {item['issue']}")
    output.append("")

    # D7 Details
    output.append("### D7: Layer Violation")
    output.append(f"**Violations**: {len(d7)}")
    for item in d7[:20]:
        output.append(f"- `{item['path']}` L{item['line']}: {item['violation']}")
    output.append("")

    # D8 Details
    output.append("### D8: Script Security")
    output.append(f"**Issues Found**: {len(d8)}")
    for item in d8[:15]:
        output.append(f"- `{item['script']}` L{item['line']}: [{item['severity']}] {item['issue']}")
    output.append("")

    # D9 Details
    output.append("### D9: SOP Closure Effectiveness")
    output.append(f"**Missing DoD**: {len(d9)}")
    for item in d9[:15]:
        output.append(f"- `{item['path']}`")
    output.append("")

    # D10 Details
    output.append("### D10: Automation Orphan Trend")
    output.append(f"**Trend**: {d10.get('trend', 'unknown')}")
    output.append(f"- Historical Orphans: {d10.get('historical_orphans', 'N/A')}")
    output.append(f"- Current Orphans: {d10.get('current_orphans', 'N/A')}")
    output.append(f"- Governance Rate: {d10.get('governance_rate', 'N/A')}%")
    output.append("")

    # Physical Fix Checklist
    output.append("---")
    output.append("## Physical Fix Checklist")
    output.append("")

    output.append("### Paths to Rename")
    for item in d1[:20]:
        output.append(f"- [ ] `{item['path']}` -> Remove special chars/spaces")
    output.append("")

    output.append("### YAML Fields to Fix")
    yaml_fix_files = [item['path'] for item in d3 if item['type'] in ['MISSING_FIELDS', 'MISSING_YAML']]
    for f in yaml_fix_files[:25]:
        output.append(f"- [ ] `{f}` -> Add owner, version, status")
    output.append("")

    output.append("### Scripts to Review")
    for item in d8[:10]:
        output.append(f"- [ ] `{item['script']}` L{item['line']} -> Fix {item['issue']}")
    output.append("")

    # Statistics Summary
    output.append("---")
    output.append("## Audit Statistics")
    output.append("")
    output.append(f"| Dimension | Issues | Risk Level |")
    output.append(f"|-----------|--------|------------|")
    output.append(f"| D1 Path Compliance | {len(d1)} | High |")
    output.append(f"| D2 ID Uniqueness | {len(d2)} | Critical/High |")
    output.append(f"| D3 YAML Integrity | {len(d3)} | High/Medium |")
    output.append(f"| D4 Link Breakage | {len(d4_dead)} dead, {len(d4_orphan)} orphan | High/Low |")
    output.append(f"| D5 Bypass Risk | {len(d5)} | High |")
    output.append(f"| D6 YAML Bombs | {len(d6)} | Medium |")
    output.append(f"| D7 Layer Violation | {len(d7)} | Medium |")
    output.append(f"| D8 Script Security | {len(d8)} | Critical/Medium |")
    output.append(f"| D9 SOP Gap | {len(d9)} | Low |")
    output.append(f"| D10 Governance | {d10.get('trend', 'unknown')} | N/A |")
    output.append("")

    return '\n'.join(output)

# ============== Main ==============
if __name__ == '__main__':
    print("="*60)
    print(" ZephyrAlpha 10-Dimension Deep Audit System v1.0")
    print("="*60)
    print()

    report_content = generate_report()

    # Save report
    output_file = BASE_DIR / 'AUDIT_10_DIMENSIONS_REPORT.md'
    output_file.write_text(report_content, encoding='utf-8')

    print()
    print("="*60)
    print(f"Audit complete. Report saved to: {output_file}")
    print("="*60)
