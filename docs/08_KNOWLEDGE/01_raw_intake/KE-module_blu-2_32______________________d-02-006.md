---
module_id: KE-module_blu-2_32______________________d-02-006
title: 2.32 密码学防篡改审计追踪 + 取证就绪（决策 D-022-22）
category: module_blueprint
---

# 2.32 密码学防篡改审计追踪 + 取证就绪（决策 D-022-22）

2.32 密码学防篡改审计追踪 + 取证就绪（决策 D-022-22）

> **决策 D-022-22**：审计日志不是普通的"记录"，而是证据链。引入Merkle Tree + 哈希链 + 外部锚定的三级密码学防篡改机制。审计写入进程与Agent进程物理分离（Supervisor/Child模式）。取证就绪——任何时候都可以一键生成包含完整证据链+签名+验证路径的取证包。
> **对标**：nono Supervisor/Child双进程（agent无法访问审计tree）+ Regure Merkle Tree审计 + in-toto供应链取证 + DSSE签名信封 + "Hunting for Nothing"数字取证方法。

```yaml
cryptographic_audit_integrity:
  
  hash_chain:
    principle: "每条审计记录 = {data, prev_hash, timestamp, signature}——修改任一条→后续所有hash断裂"
    structure:
      leaf_hash: "SHA-256(record_id || timestamp || actor || action || result || metadata)"
      chain_hash: "SHA-256(leaf_hash || prev_chain_hash)"
      merkle_root: "从所有leaf_hash构建Merkle Tree→单个root hash"
    verification: "任何时间点可重新计算整个链→与存储的root对比→不一致=篡改告警"

  merkle_tree_batching:
    principle: "每N条记录(默认100)构建一个Merkle block→root锚定到外部→形成不可逆证据链"
    block_structure:
      - block_id: "递增序号"
      - leaves: "该block内所有审计记录的leaf_hash"
      - merkle_root: "该block的Merkle Tree root"
      - prev_block_root: "上一block的root(链式连接block间)"
      - timestamp: "block创建时间(多时钟源交叉验证)"
    proof_generation: "对任一记录→生成Merkle inclusion proof→证明'此记录在此block中且未被修改'"

  external_anchoring:
    methods:
      primary:
        mechanism: "定期(每10分钟/每1000条)将merkle_root发布到独立存储"
        storage: "本地独立WORM分区 + GitHub Gist(公开不可变) + 可选: 去中心化存储(IPFS/Arweave)"
      secondary:
        mechanism: "每24h将累积root hash发布到多个外部独立系统"
        storage: "独立VPS上的只追加日志 + Email归档(第三方时间戳证明)"
    purpose: "即使攻击者获得系统完整控制权→已发布的历史root无法修改→篡改必然被检测"

  process_separation:
    architecture: |
      审计写入进程(Audit Supervisor)──独立进程/独立用户──仅此进程可写审计
            ▲ kernel-enforced boundary
            │
      升级引擎进程(Agent/Worker)──只能通过IPC提交审计事件──不能直接写审计文件
    enforcement: "OS级——独立Linux用户+独立文件权限+seccomp限制系统调用"
    reference: "nono Supervisor/Child——child cannot open audit file, cannot ptrace supervisor"

  forensic_readiness:
    evidence_package:
      trigger: "手动触发 / P0安全事件自动触发"
      contents:
        - "完整审计链(所有记录+所有hash+所有Merkle block)"
        - "系统状态快照(进程列表+网络连接+打开文件+内存 footprint)"
        - "签名密钥(本次使用的签名公钥)"
        - "Merkle inclusion proofs(每条记录的验证路径)"
        - "外部锚定记录(已发布的root hash+发布时间戳)"
        - "时间线重建(所有事件按因果顺序排列)"
      format: "in-toto layout + DSSE签名信封 + JSON证据索引"
      verification: "第三方可用独立工具验证整个证据包完整性——无需信任生成系统"
    
    causal_graph:
      principle: "每条审计记录维护因果依赖——operation_A导致了escalation_B触发了notification_C"
      structure: "有向无环图(DAG)——节点=审计记录, 边=因果关系(触发/导致/依赖)"
      purpose: "取证时重建完整事件链——不是离散记录,而是连续叙事"

    dead_man_switch_logging:
      principle: "升级引擎必须定期(每5s)输出心跳审计记录→心跳缺失本身=最严重的安全事件"
      detection: "心跳gap>15s→触发独立watchdog→日志'NO_HEARTBEAT_DETECTED'→升级P0-FATAL"
      forensic_value: "gap模式=攻击者活跃时间窗口签名"

  last_resort_watchdog:
    design: |
      独立守护进程(非Python,编译型语言Rust/Go,~100行代码):
        - 唯一职责: 监控升级引擎进程是否存活
        - 心跳超时>30s→强制系统进入ALL_STOP
        - 运行在独立用户,独立进程空间,最小依赖
        - 启动方式: systemd service(自动重启)
    rationale: "当所有Python层/LLM层安全全部失效时,还有一个物理级的最后开关"

  recovery_priority:
    all_crash_recover
