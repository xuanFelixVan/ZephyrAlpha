---
module_id: KE-module_blu-2_33__________________d-022-23-005
title: 2.33 系统代码与依赖完整性验证链（决策 D-022-23）
category: module_blueprint
---

# 2.33 系统代码与依赖完整性验证链（决策 D-022-23）

2.33 系统代码与依赖完整性验证链（决策 D-022-23）

> **决策 D-022-23**：升级协议的安全不是从规则文件开始的——而是从BIOS启动→OS加载→Python运行时→依赖包→升级代码的完整信任链。引入SBOM + 代码签名 + 可重复构建 + 启动完整性验证。
> **对标**：Microsoft Authenticode + Python REPRODUCIBLE_BUILD + 腾讯"幽灵依赖"研究 + ClawHavoc 1200+Skill攻击 + SLSA框架 + Sigstore。

```yaml
system_integrity_chain:

  boot_integrity:
    chain: "Secure Boot(BIOS/UEFI) → OS kernel签名校验 → init system → Python runtime → escalation code"
    each_stage: "加载前校验签名/→失败=停止启动+告警"
    implementation: "Windows: Authenticode签名 + Driver Signature Enforcement; Linux: IMA/EVM + dm-verity"

  code_integrity:
    escalation_source:
      files: ["escalation_engine.py", "delegation_manager.py", "所有§3文件组成中的.py"]
      protection: "启动时SHA-256 hash对比baseline(存储在独立于源码的baseline文件)"
      baseline_update: "仅Owner可更新——通过§2.5 change_process"
      mismatch_action: "拒绝启动+记录CRITICAL事件+P0通知Owner"
    
    compiled_bytecode:
      threat: "攻击者修改.pyc而不改.py→源码hash通过但运行时逻辑被篡改"
      solution: "每次启动强制从源码重新编译.pyc(不信任磁盘上的.pyc)+对比编译产物hash"

  reproducible_build:
    goal: "从相同源码→产生bit-identical二进制→任何人可独立验证"
    implementation:
      - "固定Python版本+固定pip依赖版本(锁定requirements.txt hash)"
      - "固定构建环境(Docker容器,指定base image SHA256)"
      - "消除时间戳/路径等非确定性因素(PYTHONHASHSEED=0,SOURCE_DATE_EPOCH固定)"
    verification: "reproducible_build.sh→SHA256(构建产物) == SHA256(发布二进制)"

  sbom_and_dependencies:
    sbom_generation:
      format: "SPDX 2.3 + CycloneDX 1.5 (双格式)"
      trigger: "每次依赖变更自动生成"
      contents: "所有直接+传递依赖的名称/版本/hash/license/来源URL"
    
    dependency_signing:
      principle: "不仅检查依赖版本,检查依赖的密码学签名"
      tool: "pip install --require-hashes(锁定每个包的SHA256)"
      enforcement: "任何依赖hash不匹配→拒绝安装+阻止系统启动"
    
    ghost_dependency_defense:
      threat: "腾讯玄武实验室发现——LLM倾向引入旧版/捏造组件"
      defense:
        - "Pre-execution hook: pip install前→拦截→SBOM比对→未知/异常包→blocked"
        - "版本白名单: 只允许经过审计的包版本(锁定requirements.txt with hashes)"
        - "幻觉包预注册: 分析本系统LLM的幻觉模式→在PyPI注册可能的幻觉包名(占坑防御)"
    
    pre_execution_scan:
      tool: "Sigil / Atuin(腾讯) ——分析install hooks/obfuscation/网络调用"
      trigger: "pip install / npm install执行前"
      behavior: "检测到恶意行为→阻止安装+P1升级+通知Owner"
    
    supply_chain_monitor:
      principle: "持续监控——已安装依赖是否出现新CVE/新恶意版本"
      check: "每日扫描所有依赖的CVE数据库+PyPI安全公告"
      response: "发现高危CVE→自动P1升级+建议升级/替换方案"

  runtime_integrity:
    python_runtime:
      check: "启动时SHA-256(python.dll/python binary) vs baseline"
      mismatch: "可能被rootkit篡改→拒绝启动+P0-FATAL"
    loaded_modules:
      check: "定期(每5min)扫描Python sys.modules→对比预期模块白名单"
      anomaly: "未知/未签名模块被加载→P0升级+隔离Agent"

  ghost_process_detection:
    principle: "rootkit可隐藏恶意进程使其不出现在ps/tasklist中"
    cross_verification:
      method: "对比内核级进程列表(driver/enumerate) vs 用户空间进程列表(ps/tasklist)"
      mismatch: "内核看到但用户空间看不到的进程=隐藏进程→P0-FATAL直接ALL_STOP"
    external_verification:
      method: "外部watchdog(独立硬件/VM)定期SSH/API查询进程列表→对比已知-good列表"
```

---
