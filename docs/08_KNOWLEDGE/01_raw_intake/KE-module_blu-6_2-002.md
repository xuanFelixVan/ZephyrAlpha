---
module_id: KE-module_blu-6_2-002
title: 6.2 四层输出验证
category: module_blueprint
---

# 6.2 四层输出验证

6.2 四层输出验证

```
L3 Output Security
├── 子层3A：Schema 验证
│   ├── Pydantic v2 strict mode + extra='forbid'
│   ├── JSON Schema 注册表（每个工具调用的期望输出格式）
│   ├── 类型强制验证（禁止隐式类型转换）
│   ├── 枚举值验证（只允许预定义的合法值集合）
│   └── 长度/范围验证（输出大小安全边界）
│
├── 子层3B：代码执行沙箱（整合原 L2 ProcessSandbox）
│   ├── 核心原则：LLM 输出 ≠ 可执行代码
│   ├── 禁止 exec() / eval() / compile() / 直接 subprocess
│   ├── 代码执行隔离手段：
│   │   ├── Docker 容器沙箱（推荐，完全隔离）
│   │   ├── WebAssembly (WASI) 运行时（轻量，NVIDIA推荐）
│   │   ├── Windows Job Object + 受限Token（Windows原生方案）
│   │   └── Python RestrictedPython / pysandbox（仅限纯Python）
│   ├── subprocess 路径白名单（从原 L2 迁移）
│   ├── 高危命令禁止（rm -rf / chmod 777 / sudo / eval）
│   ├── 环境变量白名单过滤
│   └── timeout 强制执行（默认 60s，可配）
│
├── 子层3C：敏感数据脱敏
│   ├── PII 检测与脱敏：
│   │   ├── 手机号 / 身份证号 / 邮箱 / IP / MAC
│   │   ├── 银行卡号 / 信用卡号
│   │   ├── 地址 / 姓名 / 企业名称
│   │   └── 使用 Microsoft Presidio（开源，可离线）
│   ├── Secret/凭据检测：
│   │   ├── API Key 模式（sk-* / akia* / ai-* 等 25+ 种）
│   │   ├── Token / Bearer / JWT
│   │   ├── 私钥（-----BEGIN ... PRIVATE KEY-----）
│   │   ├── 数据库连接字符串
│   │   └── 云服务凭证（AKID / 密钥对）
│   ├── 内部敏感关键词过滤
│   │   ├── 策略参数 / 内部API地址 / 服务器配置
│   │   └── 自定义敏感词库（可由 AI 辅助维护）
│   └── 脱敏策略：
│       ├── Block：完全阻断（凭据类）
│       ├── Mask：部分遮盖（PII 类，如 138****1234）
│       └── Flag：标记+告警（中文等需人工判断的）
│
└── 子层3D：幻觉与真实性检测
    ├── 事实核查（AlignScore / NVIDIA Nemotron 事实性评估）
    ├── 来源归因（输出中的声明是否有引文支持）
    ├── 不确定性标记（模型自身置信度低时应明确标记）
    ├── 幻觉检测提示词工程：
    │   └── "如果无法确定，请明确说'我不确定'而非编造"
    └── 输出语义安全检查：
        ├── NVIDIA Content Safety（23类不安全内容）
        ├── 暴力/色情/仇恨/自残等内容检测
        └── 政治敏感/违法内容检测
```
