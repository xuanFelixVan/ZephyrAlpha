# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os, re, csv, json
from datetime import datetime

REPO = r'D:\ZephyrAlpha'
LEDGER = os.path.join(REPO, r'docs\09_AUDIT\STATE\OPENCLAW_INVENTORY_AUDIT_LEDGER.csv')
STATE_JSON = os.path.join(REPO, r'docs\09_AUDIT\STATE\OPENCLAW_AUDIT_RUNNER_STATE.json')
CHUNK_LOG = os.path.join(REPO, r'docs\09_AUDIT\REPORTS\OPENCLAW_CHUNK_LOG.md')
REPORTS_DIR = os.path.join(REPO, r'docs\09_AUDIT\REPORTS')

def read_file_head(rel_path, max_lines=200):
    abs_path = os.path.join(REPO, rel_path.replace('/', os.sep))
    if not os.path.isfile(abs_path):
        return None, 'file_not_found'
    try:
        with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line)
        return ''.join(lines), None
    except Exception as e:
        return None, str(e)

def extract_yaml_blocks(content):
    blocks = []
    if not content:
        return blocks
    parts = content.split('---')
    for i in range(1, len(parts), 2):
        block = parts[i].strip()
        if block and any(k in block for k in ['module_id', 'version', 'status', 'owner', 'responsibility']):
            blocks.append(block)
    return blocks

def extract_title(content):
    if not content:
        return None
    for line in content.split('\n'):
        m = re.match(r'^#\s+(.+)', line.strip())
        if m:
            return m.group(1).strip()
    return None

def analyze_file(rel_path):
    content, err = read_file_head(rel_path)
    if err:
        return {
            'path': rel_path,
            'status': 'skipped_unreadable' if err == 'file_not_found' else 'skipped_unreadable',
            'note': err,
            'title': None,
            'yaml_count': 0,
            'module_id': None,
            'has_mojibake': False,
            'severity': 'P0' if err == 'file_not_found' else 'P1'
        }
    
    yaml_blocks = extract_yaml_blocks(content)
    title = extract_title(content)
    
    module_id = None
    for block in yaml_blocks:
        m = re.search(r'module_id:\s*(.+)', block)
        if m:
            module_id = m.group(1).strip().strip("'\"")
    
    has_mojibake = bool(re.search(r'[\ufffd\u00c0-\u00ff]{3,}', content))
    has_double_yaml = len(yaml_blocks) > 1
    
    severity = 'P2'
    notes = []
    if has_mojibake:
        severity = 'P0'
        notes.append('mojibake编码损坏')
    if has_double_yaml:
        if severity < 'P1':
            severity = 'P1'
        notes.append(f'双YAML头({len(yaml_blocks)}块)')
    if not module_id:
        notes.append('缺module_id')
    if not title:
        notes.append('缺标题')
    
    return {
        'path': rel_path,
        'status': 'done',
        'note': '; '.join(notes) if notes else '',
        'title': title,
        'yaml_count': len(yaml_blocks),
        'module_id': module_id,
        'has_mojibake': has_mojibake,
        'has_double_yaml': has_double_yaml,
        'severity': severity
    }

def load_ledger():
    rows = []
    with open(LEDGER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def save_ledger(rows):
    with open(LEDGER, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['relative_path','phase2_status','phase2_note','reviewed_at_batch'])
        w.writeheader()
        w.writerows(rows)

def load_state():
    with open(STATE_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_JSON, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_pending_dirs():
    with open(os.path.join(REPO, r'docs\09_AUDIT\STATE\MD_FILES_BY_SUBDIRECTORY_20260408.md'), 'r', encoding='utf-8') as f:
        content = f.read()
    
    dirs = []
    current_dir = None
    current_files = []
    
    for line in content.split('\n'):
        m = re.match(r'^## `(.+?)`（(\d+) 个文件）', line)
        if m:
            if current_dir and current_files:
                dirs.append((current_dir, current_files))
            current_dir = m.group(1).replace('\\', '/')
            current_files = []
        elif line.strip().startswith('- `') and current_dir:
            fm = re.match(r'^- `(.+?)`', line.strip())
            if fm:
                current_files.append(fm.group(1))
    
    if current_dir and current_files:
        dirs.append((current_dir, current_files))
    
    return dirs

def process_batch(dir_name, files, batch_id):
    results = []
    for f in files:
        r = analyze_file(f)
        results.append(r)
    
    safe_name = dir_name.replace('/', '_').replace('\\', '_')
    if len(safe_name) > 60:
        import hashlib
        safe_name = safe_name[:40] + '_' + hashlib.md5(safe_name.encode()).hexdigest()[:8]
    
    report_path = os.path.join(REPORTS_DIR, f'OPENCLAW_L2_{safe_name}_{batch_id}.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f'# OpenClaw L2 深度审计 — 批次: {dir_name}\n\n')
        f.write(f'> **批次ID**: {batch_id}\n')
        f.write(f'> **目录**: `{dir_name}`\n')
        f.write(f'> **文件数**: {len(results)}\n')
        f.write(f'> **审计时间**: {datetime.now().strftime("%Y-%m-%dT%H:%M")}\n\n---\n\n')
        
        f.write('## 审计汇总表\n\n')
        f.write('| 文件 | 标题 | module_id | 问题 | 严重度 |\n')
        f.write('|------|------|-----------|------|--------|\n')
        for r in results:
            fname = os.path.basename(r['path'])
            f.write(f'| `{fname}` | {r["title"] or "—"} | {r["module_id"] or "—"} | {r["note"] or "无"} | {r["severity"]} |\n')
        
        p0 = [r for r in results if r['severity'] == 'P0']
        p1 = [r for r in results if r['severity'] == 'P1']
        p2 = [r for r in results if r['severity'] == 'P2']
        
        f.write(f'\n## 统计\n\n')
        f.write(f'- P0: {len(p0)} 篇\n- P1: {len(p1)} 篇\n- P2: {len(p2)} 篇\n\n')
        
        if p0:
            f.write('## P0 问题明细\n\n')
            for r in p0:
                f.write(f'- `{r["path"]}`: {r["note"]}\n')
            f.write('\n')
        
        f.write('## 目录级结论\n\n')
        mojibake_count = sum(1 for r in results if r.get('has_mojibake'))
        double_yaml_count = sum(1 for r in results if r.get('has_double_yaml'))
        missing_mid = sum(1 for r in results if not r.get('module_id'))
        
        if mojibake_count:
            f.write(f'- **编码损坏**: {mojibake_count} 篇\n')
        if double_yaml_count:
            f.write(f'- **双YAML头**: {double_yaml_count} 篇\n')
        if missing_mid:
            f.write(f'- **缺module_id**: {missing_mid} 篇\n')
    
    return results, report_path

def main():
    state = load_state()
    ledger_rows = load_ledger()
    all_dirs = get_pending_dirs()
    
    done_paths = set(r['relative_path'] for r in ledger_rows if r['phase2_status'] == 'done')
    
    last_completed = state.get('last_completed_directory_batch')
    start_idx = 0
    if last_completed:
        for i, (d, _) in enumerate(all_dirs):
            if d == last_completed:
                start_idx = i + 1
                break
    
    batch_count = 0
    max_batches = 50
    
    for i in range(start_idx, len(all_dirs)):
        if batch_count >= max_batches:
            break
        
        dir_name, files = all_dirs[i]
        
        pending_files = [f for f in files if f not in done_paths]
        if not pending_files:
            continue
        
        batch_id = f'{i+1:03d}'
        results, report_path = process_batch(dir_name, pending_files, batch_id)
        batch_count += 1
        
        for r in results:
            for lr in ledger_rows:
                if lr['relative_path'] == r['path']:
                    lr['phase2_status'] = r['status']
                    lr['phase2_note'] = r.get('note', '')[:200]
                    lr['reviewed_at_batch'] = batch_id
                    break
        
        done_count = sum(1 for r in ledger_rows if r['phase2_status'] in ('done', 'skipped_unreadable', 'deferred_oversize'))
        state['last_completed_directory_batch'] = dir_name
        state['total_md_reviewed'] = done_count
        state['last_heartbeat_at'] = datetime.now().isoformat()
        state['current_phase'] = 'phase2_l2_batch'
        if 'report_files_written' not in state:
            state['report_files_written'] = []
        state['report_files_written'].append(os.path.basename(report_path))
        
        save_ledger(ledger_rows)
        save_state(state)
        
        print(f'Batch {batch_id}: {dir_name} ({len(pending_files)} files) -> {os.path.basename(report_path)} [total reviewed: {done_count}/{state["total_md_expected"]}]')
    
    print(f'\nDone. Processed {batch_count} batches. Total reviewed: {done_count}/{state["total_md_expected"]}')

if __name__ == '__main__':
    main()
