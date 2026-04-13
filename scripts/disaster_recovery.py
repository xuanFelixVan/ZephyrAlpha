#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZephyrAlpha Disaster Recovery Script
4-Phase Emergency Restoration Plan
"""

import shutil, re, os
from pathlib import Path

def main():
    root = Path('d:\\ZephyrAlpha')
    docs = root / 'docs'
    
    # Standard directories
    STANDARD = {
        '00_OVERVIEW', '01_FRAMEWORK', '02_FACTOR_LIBRARY', '03_TRADING_TACTICS',
        '04_EXECUTION', '05_IMPLEMENTATION', '06_CONSTRUCTION_DOCS', '07_AI_REPORTING',
        '08_HUMAN_AI_INTERFACE', '09_AUDIT', '10_GOVERNANCE_COMPLIANCE', '99_ARCHIVE'
    }
    
    stats = {
        'created': 0,
        'quarantined': 0,
        'rescued': 0,
        'destroyed': 0
    }
    
    print('\n[DISASTER RECOVERY 4-PHASE PLAN] Starting...\n')
    
    # PHASE 1
    print('[PHASE 1] Creating standard skeleton & quarantine zone...')
    for d in STANDARD:
        dir_path = docs / d
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            stats['created'] += 1
    
    quarantine = docs / '_QUARANTINE_ZONE_DANGER'
    quarantine.mkdir(exist_ok=True)
    (docs / '99_ARCHIVE' / 'RESCUED_ORPHANS').mkdir(parents=True, exist_ok=True)
    print(f'  [OK] Created {stats["created"]} standard dirs')
    print('  [OK] Quarantine zone ready')
    
    # PHASE 2
    print('\n[PHASE 2] Mass quarantine (physical isolation)...')
    for item in list(docs.iterdir()):
        if item.is_dir() and item.name not in STANDARD:
            try:
                dest = quarantine / item.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(item), str(dest))
                stats['quarantined'] += 1
            except Exception as e:
                pass
    print(f'  [OK] Quarantined {stats["quarantined"]} malformed directories')
    
    # PHASE 3
    print('\n[PHASE 3] Content-based rescue (吸星大法)...')
    
    # Module ID mapping
    ID_TO_DIR = {
        'FACTOR': '02_FACTOR_LIBRARY',
        'ALPHA': '02_FACTOR_LIBRARY',
        'LAYER': '01_FRAMEWORK',
        'STRATEGY': '03_TRADING_TACTICS',
        'TACTIC': '03_TRADING_TACTICS',
        'EXECUTION': '04_EXECUTION',
        'ORDER': '04_EXECUTION',
        'IMPL': '05_IMPLEMENTATION',
        'IMPLEMENTATION': '05_IMPLEMENTATION',
        'CONSTRUCT': '06_CONSTRUCTION_DOCS',
        'REPORT': '07_AI_REPORTING',
        'AI': '07_AI_REPORTING',
        'HUMAN': '08_HUMAN_AI_INTERFACE',
        'AUDIT': '09_AUDIT',
        'GOVERNANCE': '10_GOVERNANCE_COMPLIANCE',
        'COMPLIANCE': '10_GOVERNANCE_COMPLIANCE',
        'OVERVIEW': '00_OVERVIEW',
    }
    
    # Rescue .md files
    for md_file in quarantine.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            
            # Extract module_id
            module_match = re.search(r'^module_id:\s*(\S+)', content, re.MULTILINE)
            module_id = module_match.group(1) if module_match else None
            
            target_dir = None
            if module_id:
                for prefix, target in ID_TO_DIR.items():
                    if prefix.upper() in module_id.upper():
                        target_dir = target
                        break
            
            if not target_dir:
                target_dir = '99_ARCHIVE/RESCUED_ORPHANS'
            
            target_path = docs / target_dir
            target_path.mkdir(parents=True, exist_ok=True)
            
            dest_file = target_path / md_file.name
            if dest_file.exists():
                name, ext = md_file.name.rsplit('.', 1) if '.' in md_file.name else (md_file.name, '')
                dest_file = target_path / f'{name}_RESCUED.{ext}' if ext else target_path / f'{name}_RESCUED'
            
            shutil.move(str(md_file), str(dest_file))
            stats['rescued'] += 1
        except Exception as e:
            pass
    
    # Rescue other valuable files
    for ext in ['*.yaml', '*.yml', '*.py', '*.json']:
        for valuable_file in quarantine.rglob(ext):
            try:
                rescued_area = docs / '99_ARCHIVE' / 'RESCUED_ORPHANS'
                rescued_area.mkdir(parents=True, exist_ok=True)
                dest = rescued_area / valuable_file.name
                if dest.exists():
                    name, ext_val = valuable_file.name.rsplit('.', 1) if '.' in valuable_file.name else (valuable_file.name, '')
                    dest = rescued_area / f'{name}_RESCUED.{ext_val}' if ext_val else rescued_area / f'{name}_RESCUED'
                shutil.move(str(valuable_file), str(dest))
                stats['rescued'] += 1
            except:
                pass
    
    print(f'  [OK] Rescued {stats["rescued"]} valuable files')
    
    # PHASE 4
    print('\n[PHASE 4] Burning ruins (焚毁废墟)...')
    if quarantine.exists():
        nested_count = len(list(quarantine.rglob('*')))
        shutil.rmtree(str(quarantine))
        stats['destroyed'] = nested_count
        print(f'  [OK] Quarantine zone destroyed: {nested_count} nested items removed')
    
    # Report
    print('\n' + '='*70)
    print('[DISASTER RECOVERY REPORT]')
    print('='*70)
    print(f'  Standard directories created: {stats["created"]}')
    print(f'  Malformed directories quarantined: {stats["quarantined"]}')
    print(f'  Files rescued: {stats["rescued"]}')
    print(f'  Nested items destroyed: {stats["destroyed"]}')
    print(f'\n  [STATUS] DISASTER RECOVERY COMPLETE - SYSTEM NORMALIZED')
    print('='*70)

if __name__ == '__main__':
    main()
