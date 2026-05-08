"""LSG Red Team 攻击载荷库。

收录供自动 Red Team 模拟使用的攻击载荷：
- 注入载荷（Prompt Injection Payloads）
- 越狱载荷（Jailbreak Payloads）
- 编码逃逸载荷（Encoding Escapes）
- 多模态注入载荷（Multimodal Injections）
- 供应链攻击载荷（Supply Chain Attacks）
"""

import yaml
from pathlib import Path


def load_injection_payloads():
    """加载注入载荷数据"""
    payloads_file = Path(__file__).parent / "injection_payloads.yaml"
    with open(payloads_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_tool_call_payloads():
    """加载工具调用载荷数据"""
    payloads_file = Path(__file__).parent / "tool_call_payloads.yaml"
    with open(payloads_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_leak_probe_phrases():
    """加载泄露探测短语数据"""
    payloads_file = Path(__file__).parent / "leak_probe_phrases.yaml"
    with open(payloads_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_red_team_payloads():
    """加载 Red Team 攻击载荷数据"""
    payloads_file = Path(__file__).parent / "red_team_payloads.yaml"
    with open(payloads_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_all_payloads():
    """加载所有载荷数据"""
    return {
        "injection": load_injection_payloads(),
        "tool_call": load_tool_call_payloads(),
        "leak_probe": load_leak_probe_phrases(),
        "red_team": load_red_team_payloads()
    }


__all__ = [
    "load_injection_payloads",
    "load_tool_call_payloads", 
    "load_leak_probe_phrases",
    "load_red_team_payloads",
    "load_all_payloads"
]