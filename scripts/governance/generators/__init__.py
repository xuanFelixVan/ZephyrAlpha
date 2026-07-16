# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/__init__.py | §
# [TTL] permanent
# generators/ — 静态清单自动生成器
# 对标 §6.16 静态清单自动生成铁律
# 所有脚本从此目录批量生成静态清单文件
__all__ = [
    "fix_module_manifest_layout",
    "generate_gate_registry",
    "generate_registry_master_index",
    "generate_script_manifest",
    "inject_manifests",
    "refresh_master_entries",
    "sync_audit_protocol_numbers",
]
