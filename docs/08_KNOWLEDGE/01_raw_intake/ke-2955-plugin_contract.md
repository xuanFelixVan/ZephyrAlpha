---
module_id: KE-2855
status: active
title: Plugin Contract v1.0 — 所有治理脚本必须满足的接口约定
category: module_blueprint
ttl: permanent
---

# Plugin Contract v1.0 — 所有治理脚本必须满足的接口约定

Plugin Contract v1.0 — 所有治理脚本必须满足的接口约定

contract:
  name: "governance-script-plugin"
  version: "1.0.0"

  # 一、命令行接口
  cli:
    required_args:
      - name: "--warn-only"
        type: flag
        description: "退出码 ≤ 1，不因 ERROR 阻断"
    optional_args:
      - name: "--output"
        type: path
        description: "输出文件路径（默认 stdout）"
      - name: "--verbose"
        type: flag
        description: "输出详细信息"

  # 二、退出码约定
  exit_codes:
    0: "全通过，零Finding"
    1: "仅有 WARNING/INFO"
    2: "存在 ERROR——阻断"
    3: "脚本自身崩溃——阻断"

  # 三、输出格式
  output:
    format: "JSONL"
    schema: "Finding Schema"
    encoding: "UTF-8"

  # 四、manifest 注册
  manifest:
    file: "scripts/governance/script-manifest.yaml"
    required_fields:
      - dimensions
      - priority
      - timeout
      - args
      - description
```


---
