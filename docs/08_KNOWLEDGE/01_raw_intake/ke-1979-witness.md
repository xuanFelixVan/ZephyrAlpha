---
module_id: KE-1888-------------witness-------004
status: active
title: 2.34 时钟完整性纵深防御 + Witness分离 + 静默窗口检测（决策 D-022-24）
category: module_blueprint
---

# 2.34 时钟完整性纵深防御 + Witness分离 + 静默窗口检测（决策 D-022-24）

2.34 时钟完整性纵深防御 + Witness分离 + 静默窗口检测（决策 D-022-24）

> **决策 D-022-24**：时间是一切TTL/SLO/TIMEOUT/审计排序的基础。时间被操纵→所有时间相关安全控制失效。引入多时钟源交叉验证+NTS加密+NTP异常检测。Witness分离——监控运行在独立于Agent的信任域。静默窗口检测——日志缺失本身是最高等级的告警。
> **对标**：NSA 818天攻授时中心防御经验(北斗+GPS+GLONASS四源Kalman滤波) + chrony maxchange + NTS(RFC 8915) + LimaCharlie silent sensor + Apple fsevents gap analysis + "Hunting for Nothing"方法论。

```yaml
clock_integrity_defense:

  multi_source_clock:
    sources:
      - id: "ntp_pool"
        servers: ["0.pool.ntp.org", "1.pool.ntp.org", "2.pool.ntp.org", "3.pool.ntp.org"]
        protocol: "NTS(NTPv4 with RFC 8915 authentication+encryption)"
        min_sources: 3  # chrony minsources=3

      - id: "rtc_hardware"
        description: "硬件实时时钟(RTC)——不受OS重启影响"
        check: "定期对比RTC vs 系统时间→偏差>1s→告警"

      - id: "monotonic_clock"
        description: "CLOCK_MONOTONIC——不受NTP调整影响,只增不减"
        purpose: "所有TTL超时基于单调时钟计算——完全免疫NTP操纵"
        implementation: "Python time.monotonic()——所有升级协议的内部超时使用此值"

    cross_verification:
      algorithm: "Kalman滤波融合多源+异常源自动剔除"
      threshold: "任一源偏差>500ms→自动剔除+告警; >2源偏差→P1升级; 全源偏差→P0-FATAL+ALL_STOP"
      reference: "NSA防御经验——'任一源异常>50ns即被切除'"

  ntp_attack_detection:
    time_skimming:
      threat: "攻击者逐步偏移时钟(每步<panic阈值)→最终累积巨大偏差"
      detection: "追踪24h累积偏移量→超过1s→P0升级(即使单步偏差很小)"

    ntp_spoofing:
      threat: "ARP spoofing + 伪造NTP响应→操纵系统时间"
      mitigation: "NTS加密认证→中间人无法伪造签名时间戳"
      fallback: "NTS不可用时→启用chrony maxchange 100 0 0(时间跳变>100s→拒绝+服务终止)"

    replay_attack:
      threat: "重放旧的NTP响应→使系统时间倒退"
      mitigation: "NTS内置freshness机制(nonce/timestamp)"

    panic_threshold_hardening:
      config: "maxchange 100 0 0——100秒以上跳变=panic+停止同步"
      monitoring: "任何panic事件→P0升级+立即暂停所有有时限操作"

  witness_isolation:
    principle: "监控/审计组件不能与Agent共享信任域"
    architecture: |
      ┌──────────────────────────────────────────────┐
      │           独立Witness信任域                    │
      │  ┌──────────────┐  ┌────────────────────┐    │
      │  │VIGIL Runtime  │  │ Merkle Audit       │    │
      │  │(维护观察者)   │  │ Supervisor(审计写)  │    │
      │  │独立用户/容器  │  │ 独立用户/最小权限   │    │
      │  └──────────────┘  └────────────────────┘    │
      │  ┌──────────────┐                             │
      │  │Last Resort    │                             │
      │  │Watchdog(Rust) │                             │
      │  └──────────────┘                             │
      └──────────┬───────────────────────────────────┘
                 │ IPC only (structured, signed)
      ┌──────────▼───────────────────────────────────┐
      │            Agent 信任域                        │
      │  ┌──────────────┐  ┌────────────────────┐    │
      │  │Agent A        │  │Agent B             │    │
      │  │(任务执行)     │  │(任务执行)           │    │
      │  └──────────────┘  └────────────────────┘    │
      └──────────────────────────────────────────────┘
    enforcement: "容器化(Docker/podman with --user)+独立Linux user namespace+独立文件系统挂载"

  c
