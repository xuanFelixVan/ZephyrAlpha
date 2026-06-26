---
module_id: KE-2709---------001
status: active
title: _detector-registry.yaml — 声明式检测器注册表（机器 SSoT）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# _detector-registry.yaml — 声明式检测器注册表（机器 SSoT）

_detector-registry.yaml — 声明式检测器注册表（机器 SSoT）
detectors:
  existing:
    - id: "blueprint_code_sync"
      script: "validate_blueprint_code_sync.py"
      drift_dimension: "D5_blueprint_code_sync"
      check_dims: ["D5", "D8"]
      severity: HIGH
      category: architecture

    - id: "code_yaml_alignment"
      script: "validate_code_yaml_alignment.py"
      drift_dimension: "D5_yaml_disk_sync"
      check_dims: ["D5"]
      severity: MEDIUM
      category: consistency

    - id: "static_manifest_drift"
      script: "validate_static_manifest_drift.py"
      drift_dimension: "D5_static_manifest"
      check_dims: ["D5"]
      severity: HIGH
      category: generators

    - id: "md_yaml_number_drift"
      script: "validate_md_yaml_number_drift.py"
      drift_dimension: "D3_D5_number_drift"
      check_dims: ["D3", "D5"]
      severity: HIGH
      category: consistency

    - id: "blueprint_implementation_docs"
      script: "validate_blueprint_implementation_docs.py"
      drift_dimension: "D5_implementation_docs"
      check_dims: ["D5"]
      severity: HIGH
      category: documentation

    - id: "three_way_consistency"
      script: "validate_three_way_consistency.py"
      drift_dimension: "D5_three_way"
      check_dims: ["D5"]
      severity: HIGH
      category: consistency

    - id: "ssot"
      script: "validate_ssot.py"
      drift_dimension: "D5_ssot"
      check_dims: ["D5"]
      severity: HIGH
      category: authority

    - id: "module_lifecycle"
      script: "validate_module_lifecycle.py"
      drift_dimension: "D5_lifecycle"
      check_dims: ["D5"]
      severity: MEDIUM
      category: lifecycle

    - id: "layer_deps"
      script: "validate_layer_deps.py"
      drift_dimension: "D4_layer_deps"
      check_dims: ["D4"]
      severity: HIGH
      category: architecture

    - id: "cross_references"
      script: "validate_cross_references.py"
      drift_dimension: "D5_cross_refs"
      check_dims: ["D5"]
      severity: MEDIUM
      category: consistency

    - id: "depends_on_format"
      script: "validate_depends_on_format.py"
      drift_dimension: "D5_depends_on"
      check_dims: ["D5"]
      severity: MEDIUM
      category: consistency

    - id: "interface_contracts"
      script: "validate_interface_contracts.py"
      drift_dimension: "D5_contracts"
      check_dims: ["D5"]
      severity: HIGH
      category: contracts

    - id: "directory_structure"
      script: "validate_directory_structure.py"
      drift_dimension: "D5_directory"
      check_dims: ["D5"]
      severity: MEDIUM
      category: structure

    - id: "deprecated_dependents"
      script: "validate_deprecated_dependents.py"
      drift_dimension: "D5_deprecated"
      check_dims: ["D5"]
      severity: HIGH
      category: lifecycle

    - id: "gate_yaml"
      script: "validate_gate_yaml.py"
      drift_dimension: "D5_gate_yaml"
      check_dims: ["D5"]
      severity: HIGH
      category: gates

    - id: "p0_module_contracts"
      scri
