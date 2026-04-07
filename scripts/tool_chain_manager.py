#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审计工具链管理脚本
功能：
1. 工具链配置管理
2. 工具依赖管理
3. 工具执行调度
4. 工具结果聚合
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import subprocess
import sys

@dataclass
class ToolChainConfig:
    name: str
    description: str
    tools: List[str]
    execution_order: List[int]
    dependencies: Dict[str, List[str]]
    parallel_execution: bool
    timeout: int

class ToolChainManager:
    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "tool_chain_config.yaml"
        self.tools_dir = self.config_dir.parent.parent / "scripts"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        if not self.config_file.exists():
            return self._create_default_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_default_config(self) -> Dict:
        default_config = {
            'tool_chains': {
                'quick_audit': {
                    'name': '快速审计链',
                    'description': '执行快速审计，检查关键文档和索引',
                    'tools': ['optimized_quick_audit.py'],
                    'execution_order': [1],
                    'dependencies': {},
                    'parallel_execution': False,
                    'timeout': 300
                },
                'standard_audit': {
                    'name': '标准审计链',
                    'description': '执行标准审计，包括死链接检测和职责检测',
                    'tools': [
                        'optimized_quick_audit.py',
                        'enhanced_dead_link_detector.py',
                        'responsibility_detector.py'
                    ],
                    'execution_order': [1, 2, 3],
                    'dependencies': {
                        'enhanced_dead_link_detector.py': ['optimized_quick_audit.py'],
                        'responsibility_detector.py': ['optimized_quick_audit.py']
                    },
                    'parallel_execution': True,
                    'timeout': 600
                },
                'deep_audit': {
                    'name': '深度审计链',
                    'description': '执行深度审计，包括所有审计工具',
                    'tools': [
                        'optimized_quick_audit.py',
                        'enhanced_dead_link_detector.py',
                        'responsibility_detector.py',
                        'unified_audit_framework.py'
                    ],
                    'execution_order': [1, 2, 3, 4],
                    'dependencies': {
                        'unified_audit_framework.py': [
                            'optimized_quick_audit.py',
                            'enhanced_dead_link_detector.py',
                            'responsibility_detector.py'
                        ]
                    },
                    'parallel_execution': False,
                    'timeout': 900
                }
            },
            'global_settings': {
                'docs_dir': 'D:/ZephyrAlpha/docs',
                'report_dir': 'D:/ZephyrAlpha/docs/09_AUDIT/REPORTS',
                'log_level': 'INFO',
                'cache_enabled': True,
                'cache_dir': 'D:/ZephyrAlpha/.audit_cache'
            }
        }
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
        
        return default_config
    
    def list_tool_chains(self) -> List[str]:
        return list(self.config.get('tool_chains', {}).keys())
    
    def get_tool_chain_config(self, chain_name: str) -> ToolChainConfig:
        chain_config = self.config['tool_chains'].get(chain_name)
        if not chain_config:
            raise ValueError(f"工具链不存在: {chain_name}")
        
        return ToolChainConfig(
            name=chain_config['name'],
            description=chain_config['description'],
            tools=chain_config['tools'],
            execution_order=chain_config['execution_order'],
            dependencies=chain_config['dependencies'],
            parallel_execution=chain_config['parallel_execution'],
            timeout=chain_config['timeout']
        )
    
    def execute_tool_chain(self, chain_name: str) -> Dict:
        print(f"\n=== 执行工具链: {chain_name} ===\n")
        
        chain_config = self.get_tool_chain_config(chain_name)
        print(f"工具链名称: {chain_config.name}")
        print(f"工具链描述: {chain_config.description}")
        print(f"工具数量: {len(chain_config.tools)}")
        print(f"并行执行: {'是' if chain_config.parallel_execution else '否'}")
        
        results = {
            'chain_name': chain_name,
            'start_time': datetime.now().isoformat(),
            'tool_results': [],
            'status': 'success'
        }
        
        for i, tool in enumerate(chain_config.tools, 1):
            print(f"\n[{i}/{len(chain_config.tools)}] 执行工具: {tool}")
            
            tool_path = self.tools_dir / tool
            if not tool_path.exists():
                print(f"  ❌ 工具不存在: {tool}")
                results['tool_results'].append({
                    'tool': tool,
                    'status': 'error',
                    'message': '工具不存在'
                })
                continue
            
            try:
                start_time = datetime.now()
                result = subprocess.run(
                    [sys.executable, str(tool_path)],
                    capture_output=True,
                    text=True,
                    timeout=chain_config.timeout
                )
                end_time = datetime.now()
                
                if result.returncode == 0:
                    print(f"  ✅ 执行成功")
                    results['tool_results'].append({
                        'tool': tool,
                        'status': 'success',
                        'execution_time': (end_time - start_time).total_seconds(),
                        'output': result.stdout[:500]
                    })
                else:
                    print(f"  ❌ 执行失败: {result.stderr[:200]}")
                    results['tool_results'].append({
                        'tool': tool,
                        'status': 'error',
                        'message': result.stderr[:200]
                    })
            except subprocess.TimeoutExpired:
                print(f"  ❌ 执行超时")
                results['tool_results'].append({
                    'tool': tool,
                    'status': 'timeout',
                    'message': f'执行超时({chain_config.timeout}秒)'
                })
            except Exception as e:
                print(f"  ❌ 执行异常: {e}")
                results['tool_results'].append({
                    'tool': tool,
                    'status': 'error',
                    'message': str(e)
                })
        
        results['end_time'] = datetime.now().isoformat()
        
        failed_tools = [r for r in results['tool_results'] if r['status'] != 'success']
        if failed_tools:
            results['status'] = 'partial_success' if len(failed_tools) < len(chain_config.tools) else 'failed'
        
        return results
    
    def create_custom_chain(self, chain_name: str, tools: List[str], description: str = "") -> bool:
        if chain_name in self.config['tool_chains']:
            print(f"工具链已存在: {chain_name}")
            return False
        
        new_chain = {
            'name': chain_name,
            'description': description or f"自定义工具链: {chain_name}",
            'tools': tools,
            'execution_order': list(range(1, len(tools) + 1)),
            'dependencies': {},
            'parallel_execution': False,
            'timeout': 600
        }
        
        self.config['tool_chains'][chain_name] = new_chain
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"✅ 创建工具链成功: {chain_name}")
        return True
    
    def delete_chain(self, chain_name: str) -> bool:
        if chain_name not in self.config['tool_chains']:
            print(f"工具链不存在: {chain_name}")
            return False
        
        del self.config['tool_chains'][chain_name]
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"✅ 删除工具链成功: {chain_name}")
        return True

def main():
    config_dir = Path("D:/ZephyrAlpha/docs/09_AUDIT/CONFIG")
    manager = ToolChainManager(config_dir)
    
    print("\n=== 审计工具链管理 ===\n")
    print("可用工具链:")
    for chain_name in manager.list_tool_chains():
        config = manager.get_tool_chain_config(chain_name)
        print(f"  - {chain_name}: {config.name} ({len(config.tools)}个工具)")
    
    print("\n执行快速审计链...")
    results = manager.execute_tool_chain('quick_audit')
    print(f"\n执行结果: {results['status']}")

if __name__ == "__main__":
    main()
