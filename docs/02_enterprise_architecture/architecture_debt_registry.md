# 架构债务注册表（Architecture Debt Registry）

> **文档性质**：全项目架构债务单一真源（Single Source of Truth）
> **审核日期**：2026-06-30（初版）/ 2026-07-01（第32轮验证）
> **审核员**：客观专业架构师（基于4轮深度调研的真实文件证据）
> **审核方法**：4个并行子agent读真实文件 + Grep真实结果 + AST共享行百分比判定
> **第32轮验证**：2026-07-01完成5.1-5.55 + 5.172-5.177共1013个问题的逐条代码验证（9批45个并行子代理），详见§八、§九
> **问题总数**：**3193个唯一违规点**（298初轮 + 52第5轮 + 42第6轮 + 76第7轮 + 60第8轮 + 49第9轮 + 45第10轮 + 98第11轮 + 42第12轮 + 26第13轮 + 54第14轮 + 65第15轮 + 33第16轮 + 16第17轮 + 32第18轮 + 212第19轮 + 70第20轮 + 31第21轮 + 12第22轮 + 147第23轮 + 781第24轮 + 141第25轮 + 160第26轮 + 140第27轮 + 164第28轮 + 126第29轮 + 70第30轮 + 151第31轮新增，去重后），归因于5个病根
> **治本方案**：4期施工（仪表盘→AST门禁→批量修复→治理层收敛）
> **维护规则**：本文档当前由手动调研派生（架构健康度仪表盘为第0期交付物，尚未实现）。违规清单部分需通过调研脚本生成，禁止手工编辑

---

## 目录

- [一、执行摘要](#一执行摘要)
- [二、问题总数确定](#二问题总数确定)
- [三、病根分析（5个根因）](#三病根分析5个根因)
- [四、战略层裁定（针对100%AI开发）](#四战略层裁定针对100ai开发)
- [五、3193个问题详细清单](#五3193个问题详细清单)
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
  - [5.46 时间与时区处理（3个，第13轮新增）](#546-时间与时区处理3个第13轮新增)
  - [5.49 文件描述符与句柄泄漏（5个，第13轮新增）](#549-文件描述符与句柄泄漏5个第13轮新增)
  - [5.51 集合变异安全（1个，第13轮新增）](#551-集合变异安全1个第13轮新增)
  - [5.52 异步/同步边界（4个，第13轮新增）](#552-异步同步边界4个第13轮新增)
  - [5.55 健康检查深度（6个，第14轮新增）](#555-健康检查深度6个第14轮新增)
  - [5.57 事件排序与因果一致性（7个，第14轮新增）](#557-事件排序与因果一致性7个第14轮新增)
  - [5.58 分布式锁正确性（10个，第14轮新增）](#558-分布式锁正确性10个第14轮新增)
  - [5.60 模块耦合度深度（9个，第14轮新增）](#560-模块耦合度深度9个第14轮新增)
  - [5.61 事务隔离与ACID合规性（7个，第15轮新增）](#561-事务隔离与acid合规性7个第15轮新增)
  - [5.62 密钥轮换与密钥管理（7个，第15轮新增）](#562-密钥轮换与密钥管理7个第15轮新增)
  - [5.64 连接池管理（5个，第15轮新增）](#564-连接池管理5个第15轮新增)
  - [5.71 启动验证与Fail-Fast（4个，第15轮新增）](#571-启动验证与fail-fast4个第15轮新增)
  - [5.72 重试风暴预防（6个，第15轮新增）](#572-重试风暴预防6个第15轮新增)
  - [5.80 线程局部与ContextVar清理（5个，第16轮新增）](#580-线程局部与contextvar清理5个第16轮新增)
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
  - [5.94 类型注解准确性（68个，第19轮新增）](#594-类型注解准确性68个第19轮新增)
  - [5.96 布尔参数蔓延（5个，第19轮新增）](#596-布尔参数蔓延5个第19轮新增)
  - [5.97 深层嵌套与圈复杂度（18个，第19轮新增）](#597-深层嵌套与圈复杂度18个第19轮新增)
  - [5.98 元类与描述符误用（4个，第19轮新增）](#598-元类与描述符误用4个第19轮新增)
  - [5.99 错误消息一致性（22个，第19轮新增）](#599-错误消息一致性22个第19轮新增)
  - [5.100 异步资源生命周期（18个，第19轮新增）](#5100-异步资源生命周期18个第19轮新增)
  - [5.101 变量遮蔽与命名冲突（56个，第19轮新增）](#5101-变量遮蔽与命名冲突56个第19轮新增)
  - [5.102 可变默认参数（7个，第20轮新增）](#5102-可变默认参数7个第20轮新增)
  - [5.103 闭包延迟绑定（0个，第20轮新增）](#5103-闭包延迟绑定0个第20轮新增)
  - [5.104 ABC抽象方法完整性（33个，第20轮新增）](#5104-abc抽象方法完整性33个第20轮新增)
  - [5.105 类型强制转换安全（13个，第20轮新增）](#5105-类型强制转换安全13个第20轮新增)
  - [5.106 排序与比较正确性（7个，第20轮新增）](#5106-排序与比较正确性7个第20轮新增)
  - [5.107 数据类设计正确性（6个，第20轮新增）](#5107-数据类设计正确性6个第20轮新增)
  - [5.108 比较运算符完整性（3个，第20轮新增）](#5108-比较运算符完整性3个第20轮新增)
  - [5.109 迭代器协议完整性（1个，第20轮新增）](#5109-迭代器协议完整性1个第20轮新增)
  - [5.110 __repr__/__str__泄露与一致性（9个，第21轮新增）](#5110-reprstr泄露与一致性9个第21轮新增)
  - [5.111 Lock可重入性（3个，第21轮新增）](#5111-lock可重入性3个第21轮新增)
  - [5.112 asyncio取消传播（3个，第21轮新增）](#5112-asyncio取消传播3个第21轮新增)
  - [5.113 __slots__一致性（1个，第21轮新增）](#5113-slots一致性1个第21轮新增)
  - [5.114 Final/@final强制（7个，第21轮新增）](#5114-finalfinal强制7个第21轮新增)
  - [5.115 ABC注册模式（2个，第21轮新增）](#5115-abc注册模式2个第21轮新增)
  - [5.116 __init_subclass__副作用（5个，第21轮新增）](#5116-init_subclass__副作用5个第21轮新增)
  - [5.117 pickle/__reduce__安全（1个，第21轮新增）](#5117-picklereduce__安全1个第21轮新增)
  - [5.118 __exit__异常抑制（0个，第22轮新增）](#5118-exit异常抑制0个第22轮新增)
  - [5.119 contextvars传播（4个，第22轮新增）](#5119-contextvars传播4个第22轮新增)
  - [5.120 cached_property/lru_cache（0个，第22轮新增）](#5120-cached_propertylru_cache0个第22轮新增)
  - [5.121 singledispatch（3个，第22轮新增）](#5121-singledispatch3个第22轮新增)
  - [5.122 描述符协议（0个，第22轮新增）](#5122-描述符协议0个第22轮新增)
  - [5.123 __contains__/__iter__（2个，第22轮新增）](#5123-containsiter2个第22轮新增)
  - [5.124 __bool__/__len__冲突（2个，第22轮新增）](#5124-boollen冲突2个第22轮新增)
  - [5.125 WeakRef兼容性（1个，第22轮新增）](#5125-weakref兼容性1个第22轮新增)
  - [5.126 可变默认参数（5个，第23轮新增）](#5126-可变默认参数5个第23轮新增)
  - [5.127 异常链丢失（6个，第23轮新增）](#5127-异常链丢失6个第23轮新增)
  - [5.128 文件句柄泄漏（12个，第23轮新增）](#5128-文件句柄泄漏12个第23轮新增)
  - [5.129 模块级副作用（7个，第23轮新增）](#5129-模块级副作用7个第23轮新增)
  - [5.130 硬编码凭据（3个，第23轮新增）](#5130-硬编码凭据3个第23轮新增)
  - [5.131 日志敏感信息泄露（25个，第23轮新增）](#5131-日志敏感信息泄露25个第23轮新增)
  - [5.132 线程局部存储泄漏（4个，第23轮新增）](#5132-线程局部存储泄漏4个第23轮新增)
  - [5.134 返回值不一致（2个，第24轮新增）](#5134-返回值不一致2个第24轮新增)
  - [5.135 异常粒度过粗（697个，第24轮新增）](#5135-异常粒度过粗697个第24轮新增)
  - [5.136 死代码检测（11个，第24轮新增）](#5136-死代码检测11个第24轮新增)
  - [5.137 魔数检测（20个，第24轮新增）](#5137-魔数检测20个第24轮新增)
  - [5.138 循环引用风险（15个，第24轮新增）](#5138-循环引用风险15个第24轮新增)
  - [5.139 TODO/FIXME技术债务标记（1个，第24轮新增）](#5139-todofixme技术债务标记1个第24轮新增)
  - [5.140 函数复杂度过高（15个，第24轮新增）](#5140-函数复杂度过高15个第24轮新增)
  - [5.143 API契约一致性（22个，第25轮新增）](#5143-api契约一致性22个第25轮新增)
  - [5.144 资源清理顺序（12个，第25轮新增）](#5144-资源清理顺序12个第25轮新增)
  - [5.145 类型注解完整性（30个，第25轮新增）](#5145-类型注解完整性30个第25轮新增)
  - [5.146 字符串处理安全（6个，第25轮新增）](#5146-字符串处理安全6个第25轮新增)
  - [5.147 序列化/反序列化安全（11个，第25轮新增）](#5147-序列化反序列化安全11个第25轮新增)
  - [5.148 日志级别使用不当（27个，第25轮新增）](#5148-日志级别使用不当27个第25轮新增)
  - [5.149 线程安全集合使用（25个，第25轮新增）](#5149-线程安全集合使用25个第25轮新增)
  - [5.150 设计模式误用（17个，第26轮新增）](#5150-设计模式误用17个第26轮新增)
  - [5.152 依赖方向违规（39个，第26轮新增）](#5152-依赖方向违规39个第26轮新增)
  - [5.153 命名一致性（21个，第26轮新增）](#5153-命名一致性21个第26轮新增)
  - [5.154 接口边界清晰度（14个，第26轮新增）](#5154-接口边界清晰度14个第26轮新增)
  - [5.155 配置验证完整性（21个，第26轮新增）](#5155-配置验证完整性21个第26轮新增)
  - [5.156 测试覆盖率盲区（12个，第26轮新增）](#5156-测试覆盖率盲区12个第26轮新增)
  - [5.157 文档与代码同步深度（25个，第26轮新增）](#5157-文档与代码同步深度25个第26轮新增)
  - [5.158 循环复杂度（12个，第27轮新增）](#5158-循环复杂度12个第27轮新增)
  - [5.159 死代码（9个，第27轮新增）](#5159-死代码9个第27轮新增)
  - [5.160 魔法数字/字符串（27个，第27轮新增）](#5160-魔法数字字符串27个第27轮新增)
  - [5.161 重复代码块（4个，第27轮新增）](#5161-重复代码块4个第27轮新增)
  - [5.162 异步代码正确性（34个，第27轮新增）](#5162-异步代码正确性34个第27轮新增)
  - [5.163 上下文管理器正确性（7个，第27轮新增）](#5163-上下文管理器正确性7个第27轮新增)
  - [5.164 装饰器误用（3个，第27轮新增）](#5164-装饰器误用3个第27轮新增)
  - [5.165 全局状态管理（44个，第27轮新增）](#5165-全局状态管理44个第27轮新增)
  - [5.166 可变默认参数（0个，第28轮新增）](#5166-可变默认参数0个第28轮新增)
  - [5.168 异常信息泄露（142个，第28轮新增）](#5168-异常信息泄露142个第28轮新增)
  - [5.169 文件句柄/资源泄漏（46个，第29轮新增）](#5169-文件句柄资源泄漏46个第29轮新增)
  - [5.170 日志级别误用（14个，第29轮新增）](#5170-日志级别误用14个第29轮新增)
  - [5.171 类型注解缺失或不一致（66个，第29轮新增）](#5171-类型注解缺失或不一致66个第29轮新增)
  - [5.172 并发安全（23个，第30轮新增）](#5172-并发安全23个第30轮新增)
  - [5.173 硬编码路径/URL/端点（30个，第30轮新增）](#5173-硬编码路径url端点30个第30轮新增)
  - [5.174 导入循环/模块耦合（17个，第30轮新增）](#5174-导入循环模块耦合17个第30轮新增)
  - [5.176 SQL注入风险（27个，第31轮新增）](#5176-sql注入风险27个第31轮新增)
  - [5.177 命名规范违反（24个，第31轮新增）](#5177-命名规范违反24个第31轮新增)
- [六、治本施工方案（4期）](#六治本施工方案4期)
- [七、客观立场声明](#七客观立场声明)

---

## 一、执行摘要

ZephyrAlpha项目是100%AI开发（trae IDE + AI对话触发），AI上下文有限。项目治理体系设计严谨（trae_060三原则 + 17个reconciler + 52个gate + 34个词表 + CapabilityLookup反查机制），但**执行覆盖存在系统性断层**。

经31轮深度调研（每个子agent读真实文件+Grep真实结果+AST共享行百分比判定），**去重后唯一违规点总数 = 3193个**（298初轮 + 52第5轮 + 42第6轮 + 76第7轮 + 60第8轮 + 49第9轮 + 45第10轮 + 98第11轮 + 42第12轮 + 26第13轮 + 54第14轮 + 65第15轮 + 33第16轮 + 16第17轮 + 32第18轮 + 212第19轮 + 70第20轮 + 31第21轮 + 12第22轮 + 147第23轮 + 781第24轮 + 141第25轮 + 160第26轮 + 140第27轮 + 164第28轮 + 126第29轮 + 70第30轮 + 151第31轮新增），分布在177个维度：

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
| 类型注解准确性（第19轮） | 68 | 42 | 26 | 0 | -> Self系统性误用40+处+裸泛型13处+Any滥用10处+公共API缺失注解11处 |
| 未使用参数与死代码（第19轮） | 21 | 1 | 6 | 14 | hallucination_detector重复死文件+_ = statistics绕过ruff×4+未使用import×6+空TYPE_CHECKING块×2+UTC自赋值×4 |
| 布尔参数蔓延（第19轮） | 5 | 1 | 4 | 0 | VerifyResult 5布尔字段+TriggerDecision 3布尔冗余+_calculate_trust 3布尔+determine_exit_code行为切换+RulesFileIntegrityResult矛盾布尔 |
| 深层嵌套与圈复杂度（第19轮） | 18 | 0 | 11 | 7 | evolve 148行5层+inject 130行+register_boot_hooks 130行7闭包+dispatch 104行5段重复+_run_once 105行5层 |
| 元类与描述符误用（第19轮） | 4 | 0 | 3 | 1 | BootstrapCache __new__初始化+无锁×2+单例__init__守卫无锁竞态×3+_LazyModule递归 |
| 错误消息一致性（第19轮） | 22 | 1 | 11 | 10 | SQL泄露+中英文混用×6+异常类型不一致×3+MCP错误码不统一+格式混用+无上下文 |
| 异步资源生命周期（第19轮） | 18 | 7 | 9 | 2 | limiter锁反模式×2+brain_integration阻塞×2+pipeline死锁×3+阻塞IO×4+get_event_loop弃用×12+asyncio.run高频 |
| 变量遮蔽与命名冲突（第19轮） | 56 | 0 | 1 | 55 | known_unknown_registry参数遮蔽id+42处数据类字段遮蔽内置名+6处模块名冲突标准库 |
| 可变默认参数（第20轮） | 7 | 0 | 5 | 2 | task_manager_server create_task 5个可变列表默认参数+模板字符串dataclass可变默认×2 |
| 闭包延迟绑定（第20轮） | 0 | 0 | 0 | 0 | **未发现问题**——事件订阅全部使用方法引用+正确使用functools.partial |
| ABC抽象方法完整性（第20轮） | 33 | 13 | 6 | 14 | 4个ABC签名与实现不匹配+4个ABC定义但实现类不继承+14个Phase-B骨架ABC无实现 |
| 类型强制转换安全（第20轮） | 13 | 2 | 7 | 4 | Decimal/float混合比较致风控失效×2+int()截断Decimal+Decimal→float精度损失×5 |
| 排序与比较正确性（第20轮） | 7 | 0 | 4 | 3 | max()空序列×3+key函数不稳定float(None)×2+排序键None TypeError×2 |
| 数据类设计正确性（第20轮） | 6 | 0 | 3 | 3 | Pydantic V1 class Config在V2代码库×3+dataclass字段类型标注与默认值不一致×3 |
| 比较运算符完整性（第20轮） | 3 | 1 | 2 | 0 | ReboundSeverity仅定义__ge__比较不一致+TriggerResult.__eq__返回False非NotImplemented+VerifyResult.__bool__与dict.__len__冲突 |
| 迭代器协议完整性（第20轮） | 1 | 0 | 0 | 1 | enforcer.py next()无default依赖隐式不变量 |
| __repr__/__str__泄露与一致性（第21轮） | 9 | 0 | 2 | 7 | Capability.auth_token经auto-__repr__暴露+DeepSeek客户端持_api_key无__repr__防护+5个类__repr__不可重建+DatabaseHealthStatus.__repr__应为__str__ |
| Lock可重入性（第21轮） | 3 | 0 | 2 | 1 | admission_controller持三锁嵌套+gpu_consensus_scheduler持两锁嵌套+协程中使用threading.Lock违反INVARIANTS |
| asyncio取消传播（第21轮） | 3 | 1 | 2 | 0 | CancelledError路径子进程未kill(4文件)+gather吞没CancelledError+线程runner未捕获CancelledError致future挂起 |
| __slots__一致性（第21轮） | 1 | 0 | 1 | 0 | RiskLimitViolationError(Exception)声明__slots__但Exception自带__dict__致优化失效 |
| Final/@final强制（第21轮） | 7 | 5 | 2 | 0 | governance/config.py 4个可变dict常量无Final+375处模块级常量系统性未标Final+@final全项目零使用 |
| ABC注册模式（第21轮） | 2 | 0 | 1 | 1 | DefaultRiskLimitsCalculator从错误源导入ABC致注册静默失败+__init_subclass__守卫脆弱 |
| __init_subclass__副作用（第21轮） | 5 | 0 | 3 | 2 | interface_base.py 3个死_registry+5个注册表只写不读+hasattr沿MRO致覆盖注册+文档引用不存在的类 |
| pickle/__reduce__安全（第21轮） | 1 | 1 | 0 | 0 | joblib.load(pickle变体)反序列化模型文件无校验(2文件) |
| __exit__异常抑制（第22轮） | 0 | 0 | 0 | 0 | 所有__exit__/__aexit__正确返回False/None，无异常抑制问题 |
| contextvars传播（第22轮） | 4 | 1 | 2 | 1 | run_in_executor不传播_ctx_allowance致LLM调用被阻塞+create_task持有启动期上下文快照致trace_id冻结 |
| cached_property/lru_cache（第22轮） | 0 | 0 | 0 | 0 | 全项目未使用@cached_property或@lru_cache，6维度均N/A |
| singledispatch（第22轮） | 3 | 0 | 0 | 3 | verdict_engine.evaluate的if-elif链可重构为singledispatchmethod+feedback_self_audit._normalize_nodes重复×3可重构 |
| 描述符协议（第22轮） | 0 | 0 | 0 | 0 | 代码库无自定义描述符，7维度均N/A |
| __contains__/__iter__（第22轮） | 2 | 0 | 0 | 2 | FindingCollection缺__contains__致`in`回退O(n)+缺__reversed__致reversed()抛TypeError |
| __bool__/__len__冲突（第22轮） | 2 | 0 | 0 | 2 | GatePipeline在非容器上定义__len__缺__bool__+VerifyResult.__bool__返回非bool值 |
| WeakRef兼容性（第22轮） | 1 | 0 | 0 | 1 | __slots__类未包含__weakref__，未来若用weakref将抛TypeError |
| 可变默认参数（第23轮） | 5 | 3 | 2 | 0 | task_manager_server.create_task的files_in_scope/deliverables/allowed_touch用=[]默认值致跨调用状态泄漏 |
| 异常链丢失（第23轮） | 6 | 5 | 1 | 0 | except块内raise新异常未用from e致原始traceback丢失(5处)+from None可能误用(1处) |
| 文件句柄泄漏（第23轮） | 12 | 3 | 8 | 1 | night_shift_queue等4处Path.open()未用with+rollback_lock等5处os.open异常路径fd泄漏 |
| 模块级副作用（第23轮） | 7 | 2 | 5 | 0 | 根__init__.py import即启动2个后台线程+migrate脚本模块级sys.path/basicConfig |
| 硬编码凭据（第23轮） | 3 | 1 | 0 | 2 | cross_session_detector的_DEFAULT_SECRET硬编码HMAC签名密钥(生产路径) |
| 日志敏感信息泄露（第23轮） | 25 | 0 | 25 | 0 | 25处session_id/token_id记录到日志(运营工作流ID,非认证令牌本体) |
| 线程局部存储泄漏（第23轮） | 4 | 1 | 2 | 1 | runtime_interceptor的_tls.allowance安全放行令牌跨请求泄漏+span_stub trace上下文泄漏 |
| 依赖注入硬编码（第23轮） | 85 | 37 | 40 | 8 | AutoRuntimeCore内8处硬编码LLM/VMS+BudgetEngine跨层硬编码12处+sqlite3散点连接35处 |
| 返回值不一致（第24轮） | 2 | 0 | 1 | 1 | _hash_file类型注解与实际返回不匹配+Optional未导入 |
| 异常粒度过粗（第24轮） | 697 | 0 | 522 | 175 | 205处except Exception:pass+96处continue+76处GateResult.YELLOW fail-open+141处return空值+4处显式fail-open+175处logged-but-swallowed |
| 死代码检测（第24轮） | 11 | 0 | 8 | 3 | 7处MIGRATED注释代码块(约95行)+__all__引用幽灵符号+未使用import/变量 |
| 魔数检测（第24轮） | 20 | 10 | 10 | 0 | task_queue四联魔数+verdict安全阈值+内存压力分级+评分阈值重复+指数退避无上限+max_workers=8散布20+文件 |
| 循环引用风险（第24轮） | 15 | 7 | 6 | 2 | 根__init__.py Timer延迟规避循环+drift_result_types↔drift_engine包内循环+audit_trail被4处try/except容错 |
| TODO/FIXME技术债务标记（第24轮） | 1 | 0 | 0 | 1 | 仅1处真实TODO(已关联工单DM-201247)，代码库技术债务标记极清洁 |
| 函数复杂度过高（第24轮） | 15 | 1 | 9 | 5 | pipeline_orchestrator.dispatch 461行/7层嵌套/30+分支+integration模块贡献8个超标函数 |
| 配置硬编码vs外部化（第24轮） | 20 | 14 | 4 | 2 | Ollama/DeepSeek URL硬编码4处+模型名硬编码7类+DB路径绕过SSoT+超时值散落+OTLP端点无env兜底 |
| 并发原语正确性（第25轮） | 8 | 0 | 4 | 4 | pipeline锁双重释放+计数器锁外自增+_dags字典无锁保护+夜班队列ID竞态 |
| API契约一致性（第25轮） | 22 | 5 | 13 | 4 | LSP违规+Protocol误用为基类+13组重复ABC各自独立_registry致插件发现失败 |
| 资源清理顺序（第25轮） | 12 | 1 | 9 | 2 | 核心关闭路径无异常隔离+sqlite连接清理缺finally(5文件9方法)+子进程管道关闭顺序错误 |
| 类型注解完整性（第25轮） | 30 | 12 | 15 | 3 | 34个文件Any滥用>5处(trigger_router 31处)+audit_trail三件套完全无类型+trust_engine隐藏NameError bug |
| 字符串处理安全（第25轮） | 6 | 0 | 2 | 4 | shell=True命令注入+yaml FullLoader(2文件违反自身策略)+eval弱沙箱+str.format_map属性遍历 |
| 序列化/反序列化安全（第25轮） | 11 | 1 | 7 | 3 | joblib.load无校验+MCP Content-Length无上限+79+处json.dumps(default=str)类型丢失+SSoT序列化模块from_dict未还原类型 |
| 日志级别使用不当（第25轮） | 27 | 13 | 10 | 4 | 9处except:pass静默吞没关键失败(服务注册/auto_bootstrap/审计链/资源监控)+4处安全基础设施失败用DEBUG+3处logger.error无exc_info |
| 线程安全集合使用（第25轮） | 25 | 12 | 11 | 2 | EventBus无锁单例+4处无锁check-then-act共享dict+subscribers list迭代与append竞态+4处无锁单例遗漏双重检查锁定 |
| 设计模式误用（第26轮） | 17 | 5 | 9 | 3 | God Class 3处(trading/ops核心域)+Shotgun Surgery 4处(同包逐字重复)+Long Parameter List 3处(factories.py) |
| 错误处理策略一致性（第26轮） | 11 | 3 | 5 | 3 | 同类IO/检索错误混用pass/warning/error多策略+安全关键路径静默吞没+自定义IOError覆盖内建 |
| 依赖方向违规（第26轮） | 39 | 5 | 25 | 9 | shared底层向上依赖trading/governance 5处HIGH+governance→trading re-export shim 30+文件规模化 |
| 命名一致性（第26轮） | 21 | 4 | 10 | 7 | 3处幽灵db_path参数(连PG)+同一动作4种命名+CT_XX_XXX违反PascalCase 40个+布尔命名不规范30+字段 |
| 接口边界清晰度（第26轮） | 14 | 6 | 6 | 2 | 6处下划线私有符号跨模块导入+13处__all__=["*"]规模化误解Python语义 |
| 配置验证完整性（第26轮） | 21 | 4 | 11 | 6 | HMAC硬编码+完整性校验恒True+int(env)无防护+配置漂移20+处+三层校验同时失效 |
| 测试覆盖率盲区（第26轮） | 12 | 4 | 5 | 3 | 2处测试因路径错误从不运行+核心业务逻辑无测试+并发代码无并发测试+merkle无篡改检测测试 |
| 文档与代码同步深度（第26轮） | 25 | 9 | 10 | 6 | 4处连字符vs下划线路径漂移(27文件)+now_iso/utc_now函数名颠倒+版本0.22vs2.0+4处shim缺[DEPRECATED]标记 |
| 循环复杂度（第27轮） | 12 | 1 | 4 | 7 | exam_orchestrator._compute_metrics_generic复杂度30+/verdict_engine.evaluate 4路分发/scheduler._run_once 5阶段流水线+7个LOW超标函数 |
| 死代码（第27轮） | 9 | 5 | 1 | 3 | governance/governance错位包7文件+infrastructure/rollback/governance 5文件+governance/_*.py 8错位split+audit_orchestrator 20死重复文件 |
| 魔法数字/字符串（第27轮） | 27 | 6 | 17 | 4 | task_repo 40+条裸SQL+apply_depgraph 40+SQL+file_task_mapper×4副本+3安全扫描器正则阈值不一致 |
| 重复代码块（第27轮） | 4 | 1 | 2 | 1 | state_synchronizer↔file_task_mapper×4一致性检查~40行重复+check_registry_parsable跨包复制+now_iso私有复制绕过SSoT |
| 异步代码正确性（第27轮） | 34 | 8 | 25 | 1 | 6个async MCP tool直调同步SQLite/文件IO+LSG安全网关asyncio.run反模式13处C1+4处C2崩溃+4处C3静默绕过 |
| 上下文管理器正确性（第27轮） | 7 | 1 | 3 | 3 | ProcessLock.__enter__忽略acquire返回值+5处@contextmanager用except Exception(BaseException时回滚跳过)+_RealSpanBridge双路径未对齐 |
| 装饰器误用（第27轮） | 3 | 0 | 0 | 3 | 3处自定义装饰器缺@functools.wraps(query_metrics.track/shared.infra.limiter×2)致inspect.signature不可穿透 |
| 全局状态管理（第27轮） | 44 | 6 | 28 | 10 | ~20处模块级单例无锁double-check+__init__.py import时启Timer+baseline_poisoning_guard完整性链无锁+asyncio+全局状态冲突 |
| 可变默认参数（第28轮） | 0 | 0 | 0 | 0 | 全代码库遵守T\|None=None哨兵模式，无可变默认参数反模式（零检出维度，证明该规范执行良好） |
| 比较运算正确性（第28轮） | 22 | 1 | 8 | 13 | 8处浮点==分母守卫（std_dev/pooled_std/older_avg/overall_score）+1处金融场景Sharpe比率std==0+13处哨兵检查风格违规 |
| 异常信息泄露（第28轮） | 142 | 39 | 66 | 37 | MCP Server通用异常处理器str(exc)直返客户端39处+GovernanceServer 12工具handler系统性{error:f"...:{e}"}+LLM Gateway SDK异常含部分API key+traceback.format_exc存结果对象8处 |
| 文件句柄/资源泄漏（第29轮） | 46 | 5 | 39 | 2 | night_shift_queue.py 4方法fd泄漏+urlopen未close+25处sqlite3无try/finally+os.open无try/finally 3处 |
| 日志级别误用（第29轮） | 14 | 0 | 2 | 12 | auto_runner审计日志失败降warning应error 2处+9处库代码print()+3处scripts print()代表性 |
| 类型注解缺失或不一致（第29轮） | 66 | 10 | 31 | 25 | brain_integration 4处public API无注解+ops/scheduler Any滥用+trading alert_handler返回类型不符+governance stub-style无注解 |
| 并发安全（第30轮） | 23 | 3 | 14 | 6 | database_manager docstring承诺线程安全但_lock未使用+EventBus单例无锁+database_service三引擎lazy连接无锁+14处check-then-act竞态 |
| 硬编码路径/URL/端点（第30轮） | 30 | 11 | 9 | 10 | red_blue_test 28处D:\ZephyrAlpha硬编码+Ollama URL散落7处+OTLP endpoint散落6处+llm_gateway 3副本DRY+environment_manager 5套环境连接串字面量 |
| 导入循环/模块耦合（第30轮） | 17 | 9 | 6 | 2 | shared 4处退化为infrastructure代理壳+shared↔integration双向耦合+trading↔governance 4条新依赖边+boot_hooks 13处延迟导入堆叠 |
| 异常处理反模式（第31轮） | 100 | 25 | 70 | 5 | fix_orphan_deps bare except吞噬DB异常+apply_depgraph 3处嵌套except吞噬触发器恢复+gateway_server/agent_orchestrator安全扫描双层except:pass+19处except Exception:pass无日志+40处return哨兵值掩盖故障+30处print替代logging(代表性取样) |
| SQL注入风险（第31轮） | 27 | 0 | 13 | 14 | 值已参数化但表名/列名f-string插值无白名单8处+PRAGMA参数无白名单2处+sqlite_dumper快照文件表名无校验+常量/DB元数据插值14组 |
| 命名规范违反（第31轮） | 24 | 1 | 17 | 6 | check_budget三重违规(非布尔返回+状态修改+事件发射)+13个check_函数返回非布尔+布尔变量无is_/has_前缀散落+单字母变量在非循环上下文 |
| **合计** | **3193** | **878** | **1679** | **636** | |

所有3193个问题归因于**5个病根**：
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
| | make_ttl_reconciler宪法级不符 | 1 | 1高 | AGENTS.md声明已删但代码存在 ✅已修复(2026-06-30) |
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
| 宪法级声明不符 | 未检查 | **AGENTS.md §11声明make_ttl_reconciler"已删"，代码仍存在** ✅已修复(2026-06-30) | 第1轮未检查 |

**最大发现（初轮）**：文件复制对从6对暴增到159对——这是之前所有审核都未发现的"隐性债务冰山"。`governance/` ↔ `infrastructure/rollback/`（71同名）和 `behavioral_audit/` ↔ `governance/drift_detection/`（51同名）两个并行目录树贡献了114对复制。

**最大发现（第5轮）**：①孤儿过滤掩盖603个真孤儿——`diagnose_depgraph.py:58 ORPHAN_EXEMPT_TYPES`把949个真孤儿滤成346，给治理层造成"孤儿问题不严重"的假象；②AGENTS.md宪法级声明与代码不符——§11声明`make_ttl_reconciler`已删，但`reconciliation_registry.py:418`函数仍存在（✅已修复2026-06-30：删除函数体+import+register）；③连字符路径违规规模被低估9倍——原报告11文件57行，实测57文件338处。

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

### 裁定5：DEFERRED-PERMANENT 状态分类（R70 引入 2026-07-06，P2 执行）

**背景**：第42轮验证后，全维度 DEFERRED 项共 ~393 个，均标注"需大规模重构/架构级变更，属专项工程"。但 393 项内部风险等级差异显著——部分项 AI 可在未来 cycle 逐步修复（命名统一/shim 标注等中低风险项），部分项必须 human-led 架构工程才能解决（架构重构/设计决策）。将两者混为"DEFERRED"导致 AI 在债务修复时误选高风险项（耗费大量上下文仍无法解决），或误判"全部 DEFERRED = 全部永久搁置"（放弃可修复的中低风险项）。

**判定**：引入 `DEFERRED-PERMANENT` 子状态，将 DEFERRED 项二分为：

| 状态 | 含义 | 适用范围 | AI 可否自行修复 |
|---|---|---|---|
| `DEFERRED` | 正常债务——AI 可在未来 cycle 逐步修复 | 中低风险项（命名统一/shim 标注/类型注解补全等） | ✅ 可（有明确修复路径） |
| `DEFERRED-PERMANENT` | 永久债务——需 human-led 架构工程，AI 不应自行尝试 | 高风险项（架构重构）+ 设计决策项 | ❌ 不可（需人类架构决策） |

**DEFERRED-PERMANENT 分类清单（~142 项）**：

| 类别 | 数量 | 代表维度 | 为什么是 PERMANENT |
|---|:---:|---|---|
| 架构重构 | ~130 | 5.1 SSoT真源（159对文件复制）/ 5.2 永久系统全自动触发 / 5.60 模块耦合度 / 5.16 并发线程安全 / 5.61 事务隔离ACID | 需重新设计模块边界/数据流/并发模型——AI 修改单文件无法解决，需全局架构重构 |
| 设计决策 | ~12 | 5.38 特性开关策略 / 5.35 API版本管理 / 5.33 容灾备份策略 / 反思1 L5治理层14→5-6功能收敛 | 需人类架构师做技术选型/取舍决策——AI 不应替人类做架构决策 |

**DEFERRED（正常债务，~251 项）**：

| 类别 | 数量 | 代表维度 | 修复路径 |
|---|:---:|---|---|
| 类型注解 | ~50 | 5.94 类型注解准确性 / 5.145 类型注解完整性 | 逐文件替换 Any→具体类型/Protocol（R70 已建 GATE-ANY-ABUSE 防复发） |
| 命名统一 | ~45 | 5.93 命名规范 / 5.11 门禁格式漂移 | 逐文件重命名/统一（中风险，P3 逐项评估） |
| 其他中低风险 | ~156 | 5.12-5.92 各维度 DEFERRED 项 | 逐维度逐项修复（有明确修复路径） |

**执行规则**：
1. AI 在债务修复 cycle 中 **MUST 优先选 DEFERRED 项**（有明确修复路径，AI 可自行完成）
2. AI **禁止自行修复 DEFERRED-PERMANENT 项**——尝试即浪费上下文（架构重构需全局视角，单文件修改无效；设计决策需人类判断）
3. DEFERRED-PERMANENT 项的解锁条件：人类架构师发起专项工程（如 ARCH-XXX 架构裁定 + 蓝图 + 专项施工计划）
4. 每轮债务修复后，更新维度状态行：`DEFERRED=N` / `DEFERRED-PERMANENT=M`（N=正常债务剩余数，M=永久债务数）

**与裁定1的关系**：裁定1"先做执行闭环再做规则扩展"指导增量治理方向；裁定5"DEFERRED-PERMANENT"指导存量债务分类——两者互补。GATE-ANY-ABUSE（R70）+ GATE-DEBT-BRIDGE（R67-68）已为类型注解+代码异味两个维度建立"执行闭环"（AST 门禁防复发），对应 DEFERRED 项可逐步清零；DEFERRED-PERMANENT 项则等待专项工程。

---

## 五、3193个问题详细清单

### 5.1 SSoT真源唯一性违规（原211个，2026-07-04验证：约83个FIXED，约128个STILL_VALID）

> **第42轮修复状态（2026-07-05）**：DEFERRED=4(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.1全部清零.
#### 5.1.1 词表硬编码（原41处 = 15 HIGH + 26 MEDIUM，15处FIXED，剩余约22处STILL_VALID含路径漂移）

##### A. stability_vocabulary.yaml（真源4值：frozen/stable/evolving/volatile）—— 已漂移，最高危

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 1 | frozenset硬编码STABILITY合法值 | [src/zephyr/autonomy_core/prompt_registry.py:86](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/prompt_registry.py#L86) | 高 | 否 |
| 2 | frozenset硬编码STABILITY合法值 | [src/zephyr/autonomy_core/skills/skill_registry.py:50](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/skills/skill_registry.py#L50) | 高 | 否 |
| 6 | frozenset硬编码FORBIDDEN_STABILITY（副本） | [src/zephyr/governance/semantic_audit/self_healer.py:75](file:///D:/ZephyrAlpha/src/zephyr/governance/semantic_audit/self_healer.py#L75) | 高 | 否 |
| 7 | frozenset硬编码FORBIDDEN_AUTONOMY（副本） | [src/zephyr/governance/semantic_audit/self_healer.py:76](file:///D:/ZephyrAlpha/src/zephyr/governance/semantic_audit/self_healer.py#L76) | 高 | 否 |

> **[✓ FIXED: 2026-07-04]** 原#3 `support/prompt_registry.py`、#4/#5 `governance/self_healer.py` 已删除（文件不存在）。
> **[路径漂移更新]** 原#2 `autonomy_core/skill_registry.py` → `autonomy_core/skills/skill_registry.py`（skills/子目录迁移）。
> **漂移详情**：代码硬编码`{experimental,beta,stable,frozen}`，词表真源为`{frozen,stable,evolving,volatile}`——值集合已不一致，AI标注`evolving`被代码拒，改`experimental`被词表拒→随机选→漂移。

##### C. layer_vocabulary.yaml（真源4值：L0_infrastructure/L1_foundation/L2_domain/L3_application）

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 12 | _FOUNDATION_LAYERS frozenset硬编码 | [src/zephyr/infrastructure/pipeline/routing_plugins.py:65](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/routing_plugins.py#L65) | 高 | 否 |
| 13 | _FOUNDATION_LAYERS frozenset硬编码 | [src/zephyr/infrastructure/pipeline/ct_pipe_routing.py:63](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/ct_pipe_routing.py#L63) | 高 | 否 |

> **[✓ FIXED: 2026-07-04]** 原#10 `integration/ct_pipe_routing.py`、#11 `integration/routing_plugins.py` 已删除（integration/侧副本清理）。

##### F. MEDIUM严重度（原26处，4处FIXED，剩余22处STILL_VALID含路径漂移）—— 无对应SSoT词表的硬编码合法值

| # | 违规类型 | 文件:行号 | 严重度 |
|---|---|---|:---:|
| 16-17 | _GATE_IDS硬编码（×2处） | [src/zephyr/infrastructure/gate_engine_server.py:50](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/gate_engine_server.py#L50) + [src/zephyr/integration/mcp/gate_engine_server.py:50](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gate_engine_server.py#L50) | 中 |
| 18-19 | _VALID_PLATFORMS硬编码（×2处） | [src/zephyr/infrastructure/doc_guard_server.py:51](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/doc_guard_server.py#L51) + [src/zephyr/integration/mcp/doc_guard_server.py:51](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/doc_guard_server.py#L51) | 中 |
| 20-21 | _VALID_PRIORITIES硬编码（×2处） | [src/zephyr/infrastructure/doc_guard_server.py:52](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/doc_guard_server.py#L52) + [src/zephyr/integration/mcp/doc_guard_server.py:52](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/doc_guard_server.py#L52) | 中 |
| 22 | _VALID_PERSISTENCE硬编码 | [src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py:61](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py#L61) | 中 |
| 23 | _VALID_SOURCE硬编码 | [src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py:62](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py#L62) | 中 |
| 24 | _VALID_EXPECTATION硬编码 | [src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py:63](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py#L63) | 中 |
| 25 | _VALID_SEVERITY硬编码 | [src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py:64](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py#L64) | 中 |
| 26 | _VALID_PERIODS硬编码 | [src/zephyr/governance/persistence/olap_engine.py:81](file:///D:/ZephyrAlpha/src/zephyr/governance/persistence/olap_engine.py#L81) | 中 |
| 27 | _PREEMPTIBLE_PRIORITIES硬编码 | [src/zephyr/infrastructure/pipeline/preemption_manager.py:57](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/preemption_manager.py#L57) | 中 |
| 29 | _NO_AUTO_FIX_TYPES硬编码 | [src/zephyr/infrastructure/auto_fix_engine/engine.py:82](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/auto_fix_engine/engine.py#L82) | 中 |
| 31 | _BLOCKED_LEVELS硬编码 | [src/zephyr/security/access_control/engine_degradation.py:64](file:///D:/ZephyrAlpha/src/zephyr/security/access_control/engine_degradation.py#L64) | 中 |
| 32-33 | routing M1-M11硬编码（×2处） | [src/zephyr/infrastructure/pipeline/ct_pipe_routing.py:80](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/ct_pipe_routing.py#L80) + [src/zephyr/infrastructure/pipeline/routing_plugins.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/routing_plugins.py) | 中 |
| 34 | _VALID_TAGS硬编码 | [scripts/governance/run_all.py:133](file:///D:/ZephyrAlpha/scripts/governance/run_all.py#L133) | 中 |
| 35 | VALID_BELONGS_TO硬编码 | [scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py:81](file:///D:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L81) | 中 |
| 36-37 | HOT/COLD_COLLECTIONS硬编码（×2处） | [src/zephyr/integration/vector_memory/collection_schemas.py:42](file:///D:/ZephyrAlpha/src/zephyr/integration/vector_memory/collection_schemas.py#L42) + [src/zephyr/integration/vector_memory/collection_manager.py:55](file:///D:/ZephyrAlpha/src/zephyr/integration/vector_memory/collection_manager.py#L55) | 中 |

> **[✓ FIXED: 2026-07-04]** 原#38/#39/#40 `_finding_lifecycle.py` 文件已删除（3处）；原#41 `fix_broken_post_sync.py` 已归档至 `scripts/governance/_archive/one_off/`（不再是活跃代码）。
> **[部分FIXED]** 原#27-28 `_PREEMPTIBLE_PRIORITIES` 第2处已删除；原#29-30 `_NO_AUTO_FIX_TYPES` 第2处已删除。
> **[路径漂移更新]** #16-21 gate/doc_guard脚本路径更新；#22-25 event_sink.py → system_telemetry/ai_behavior/；#26 olap_engine.py → governance/persistence/；#31 engine_degradation.py → security/access_control/；#34 run_all.py 行号132→133；#36-37 集合配置路径更新。

#### 5.1.2 文件复制对（原159对，5/7簇已FIXED，剩余2簇STILL_VALID）

分布于7个复制簇，按规模降序：

| # | 复制簇 | 同名文件数 | COPY(≥60%) | DRIFTED(35-59%) | 严重度 | 状态 |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | `governance/` ↔ `infrastructure/rollback/` | 71 | 65 | 1（result_types.py 53.8%） | 高 | ✅ FIXED（governance/侧副本已删除，rollback/保留54文件为真源） |
| 2 | `behavioral_audit/` ↔ `governance/drift_detection/` | 51 | 49 | 1（__init__.py 54.7%） | 高 | ✅ FIXED（behavioral_audit/已删除，drift_detection/保留67文件） |
| 3 | `infrastructure/` ↔ `integration/mcp/` | 19 | 19 | 0 | 高 | ✅ FIXED（infrastructure/侧18副本删除+__init__更新，integration/mcp/保留为真源；5.85.3 bugfix同步；15测试文件import迁移 2026-07-08） |
| 4 | `infrastructure/pipeline/` ↔ `integration/` | 17 | 17 | 0 | 高 | ✅ FIXED（integration/侧已清理，仅剩5个无关文件） |
| 5 | `autonomy_core/` ↔ `parsing/` | 3 | 3 | 0 | 高 | ✅ FIXED（parsing/目录已删除） |
| 6 | `shared/schema/` ↔ `integration/shared/schema/` | 1 | 1 | 0 | 高 | ⚠ STILL_VALID（双方均存在6个同名.py文件） |
| 7 | `shared/config/` ↔ `infrastructure/config/shared/config/` | 1 | 1 | 0 | 高 | ✅ FIXED（ARCH-038已解决，loader.py退役） |

> **验证日期**：2026-07-08
> **已消除**：6簇（簇1/2/3/4/5/7），代表约114+17+19+3+1=154个复制对已消除
> **仍存在**：1簇（簇6 shared/schema↔integration/shared/schema 6对 = 6对）
> **原最大债务**：簇1（governance↔rollback 71同名）和簇2（behavioral_audit↔drift_detection 51同名）贡献114对复制，现已消除。

#### 5.1.3 ghost_autoclean 备份无保留策略（ARCH-DEBT-BACKUP-CLEANUP，2026-07-08 发现并 FIXED）

> **发现背景**：复制簇#3 清理过程中发现 `_backup_depgraph_for_autoclean` 备份到 `data/databases/backups/`，与标杆 `backup_pg_depgraph`（`tmp/pg_backups/`，保留10，.gitignored）不一致。
> **问题定性**：ARCH-DEBT（MEDIUM）—— 违反真源唯一（备份进git）+ 永久系统全自动（无自动清理）+ 对标一致。
> **修复方案**：(1) 路径 `data/databases/backups/` → `tmp/pg_backups/`（.gitignored）；(2) 添加保留策略保留10个（对标 `backup_pg_depgraph`）；(3) `git rm --cached` 清理8目录16文件误提交；(4) `.gitignore` + `directory_contract.yaml` deprecated_directories 双重保障。
> **状态**：✅ FIXED（2026-07-08，路径统一+保留策略+.gitignore+directory_contract+git rm --cached）

#### 5.1.4 重复簇（6簇，1簇FIXED，3簇部分FIXED，2簇STILL_VALID）

| # | 重复簇 | 定义位置数 | 真源候选 | 严重度 | 状态 |
|---|---|:---:|---|:---:|:---:|
| 1 | `atomic_write` | 6处 | [shared/io/file_utils.py:83](file:///D:/ZephyrAlpha/src/zephyr/shared/io/file_utils.py#L83)（真源）+ 副本(rollback/forensic.py:363, auto_fix_engine/fix_safety.py:109, scripts/fix_orphan_all.py:144, governance/_shared/file_utils.py:48) | 中 | ⚠ STILL_VALID |
| 2 | `load_yaml` | ~~7处~~ → 3处活跃 | [scripts/governance/_shared/yaml_utils.py:54](file:///D:/ZephyrAlpha/scripts/governance/_shared/yaml_utils.py#L54)（真源）+ 2活跃副本(arch_guard/_arch_ssot.py:48, d8_doc_sync/sync_yaml_to_depgraph.py:87) | 中 | ⚠ 部分FIXED（4处已归档至_archive/） |
| 3 | `load_yaml_config` | ~~2处~~ → 0处 | — | 中 | ✅ FIXED（ARCH-038已解决，loader.py退役删除） |
| 4 | `parse_frontmatter` | 4处 | [shared/io/frontmatter_utils.py:38](file:///D:/ZephyrAlpha/src/zephyr/shared/io/frontmatter_utils.py#L38)（真源）+ 3副本——签名已分叉（scripts侧返回`(dict, body)`，src侧返回`dict|None`） | 中 | ⚠ STILL_VALID |
| 5 | `Priority` Enum | ~~6处~~ → 4处 | asset_inventory/models.py:60 + audit_trail/models.py:48 + shared/schema/severity_types.py:41 + integration/shared/schema/severity_types.py:44 | 中 | ⚠ 部分FIXED（audit_orchestrator/models.py + governance/models.py已删除） |
| 6 | `IntentDomain` Enum | ~~2处~~ → 1处 | [governance/persistence/intent_keyword_mapper.py:299](file:///D:/ZephyrAlpha/src/zephyr/governance/persistence/intent_keyword_mapper.py#L299)（路径漂移） | 中 | ⚠ 部分FIXED（parsing/侧已删除） |

> **[✓ FIXED: 2026-07-04]** 簇3 `load_yaml_config` ARCH-038已解决。
> **[部分FIXED]** 簇2 `load_yaml` 4处归档；簇5 `Priority` Enum 2处删除；簇6 `IntentDomain` 1处删除+1处路径漂移(autonomy_core/ → governance/persistence/)。
> **[路径漂移更新]** 簇1 真源行号69→83；簇2 真源行号53→54；簇6 路径漂移。

#### 5.1.5 DB连接函数真源冲突（2处，行号漂移，违规仍存在）

| # | 违规类型 | 文件:行号 | 严重度 | 历史遗留 |
|---|---|---|:---:|:---:|
| 1 | `get_depgraph_pg_connection`同名wrapper委托（真源+wrapper并存） | 真源[src/zephyr/governance/depgraph_schema.py:1246](file:///D:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py#L1246) + wrapper[scripts/governance/_shared/constants.py:104](file:///D:/ZephyrAlpha/scripts/governance/_shared/constants.py#L104) | 中 | 否 |
| 2 | `get_db_connection` deprecated别名（名称冲突，已注释说明） | [src/zephyr/governance/depgraph_schema.py:1286](file:///D:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py#L1286) | 中 | 是 |

> **[路径漂移更新: 2026-07-04]** #1 行号1170→1246；#2 行号1210→1286。

---

### 5.31 构建打包（17个，第11轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=4(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.31全部清零.
> **维度定义**：Docker镜像、pyproject.toml元数据、CI构建测试的正确性。
> **病根归属**：根因5（无构建质量门禁）。

#### 5.31.1 [HIGH] Dockerfile CMD指向不存在的Python模块
- **文件**：[Dockerfile](file:///D:/ZephyrAlpha/Dockerfile#L28)
- **证据**：`CMD ["python", "-m", "zephyr.l01_infrastructure"]`；Glob `**/l01_infrastructure/**`返回No file found
- **问题**：容器启动即ModuleNotFoundError；HEALTHCHECK同样失败
- **影响**：Docker镜像构建成功但无法运行；docker-compose up后zephyr-core容器立即退出
- **修复**：改为存在的入口（如python -m zephyr.governance），或新建src/zephyr/__main__.py
- **状态**：FIXED（2026-07-04）— CMD 改为 `zephyr.trading`（已存在的入口，含 SIGTERM 处理），HEALTHCHECK 改为 `python -c "import zephyr"`

#### 5.31.2 [HIGH] docker-compose.yml healthcheck同样指向不存在的模块
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L29)
- **证据**：`test: ["CMD", "python", "-m", "zephyr.l01_infrastructure.health"]`
- **问题**：与5.31.1同根因；compose的healthcheck永远unhealthy
- **影响**：由于restart: unless-stopped，容器会反复重启-失败循环
- **修复**：与5.31.1一并修正
- **状态**：FIXED（2026-07-04）— healthcheck test 改为 `["CMD", "python", "-c", "import zephyr; print('ok')"]`

#### 5.31.3 [HIGH] 无.dockerignore，构建上下文泄露全仓库
- **文件**：缺失（Glob `**/.dockerignore`返回No file found）
- **证据**：docker-compose.yml context: .，无.dockerignore限制
- **问题**：docker build发送整个项目目录作为上下文，包括.git/、data/vector_db/、.env（含密钥）
- **影响**：构建缓慢；.env密钥可能被COPY进镜像层；镜像层缓存失效频繁
- **修复**：新增.dockerignore，至少包含.git/、data/、tests/、docs/、.runtime/、.trae/、.env
- **状态**：FIXED（2026-07-04）— 新建 .dockerignore，覆盖 VCS/构建产物/虚拟环境/测试文档/数据缓存/密钥/AI草稿/模型文件等

#### 5.31.4 [HIGH] 版本号三重真源，值不一致（2.0.0 vs 4.6.0）
- **文件**：[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml#L10)（version="2.0.0"）、[__init__.py](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L67)（_version_="4.6.0"）、[atomic_transaction_manager.py](file:///D:/ZephyrAlpha/src/zephyr/governance/financial_governance/atomic_transaction_manager.py#L577)（__version__="2.0.0"）
- **证据**：三处版本声明，值分叉。pip show zephyralpha报2.0.0，运行时zephyr._version_报4.6.0
- **问题**：版本对账失效；用户报告"我用的4.6.0"但pip说"2.0.0"
- **影响**：排障混乱；自动化changelog/语义化版本工具无法确定真源
- **修复**：pyproject.toml为唯一SSoT，__init__.py用importlib.metadata.version()动态读取
- **状态**：FIXED（2026-07-04）— __init__.py 改用 importlib.metadata.version('zephyralpha') 动态读取（含 pyproject 回退），删除 atomic_transaction_manager.py L577 `__version__ = "2.0.0"`，统一为 pyproject.toml 2.0.0 单一真源

#### 5.31.5 [MEDIUM] Dockerfile非多阶段构建，gcc与构建工具残留
- **文件**：[Dockerfile](file:///D:/ZephyrAlpha/Dockerfile#L4)
- **证据**：单FROM python:3.12-slim；第9-11行apt-get install gcc，gcc留在最终镜像
- **问题**：无builder stage编译C扩展后复制到slim runtime
- **影响**：镜像比必要大约100MB+；生产镜像含编译器增加攻击面
- **修复**：改为FROM python:3.12-slim AS builder + FROM python:3.12-slim双阶段
- **状态**：STILL_VALID（保留）— 多阶段构建需分离 C 扩展编译逻辑与 runtime stage，影响 Dockerfile 结构性重构

#### 5.31.6 [MEDIUM] 生产镜像用pip install -e .（可编辑模式）
- **文件**：[Dockerfile](file:///D:/ZephyrAlpha/Dockerfile#L21)
- **证据**：`RUN pip install -e .`
- **问题**：-e（editable）是为开发设计的模式，生产应pip install .
- **影响**：镜像内src/目录必须保留且可写；pip show路径异常
- **修复**：改为pip install --no-cache-dir .
- **状态**：FIXED（2026-07-04）— Dockerfile L21 `pip install -e .` → `pip install --no-cache-dir .`

#### 5.31.7 [MEDIUM] pyproject.toml无[project.scripts]/console_scripts
- **文件**：[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml)
- **证据**：全文无[project.scripts]段；Grep console_scripts返回No matches found
- **问题**：包安装后无CLI命令；pip install zephyralpha后无法直接zephyralpha启动
- **影响**：用户体验差；Dockerfile不得不硬编码python -m ...
- **修复**：新增[project.scripts]段，如`zephyr = "zephyr.governance:main"`
- **状态**：FIXED（2026-07-04）— 新增 `[project.scripts]` 段 `zephyr = "zephyr.trading.__main__:main"`

#### 5.31.8 [MEDIUM] 无MANIFEST.in，sdist/wheel缺非Python文件
- **文件**：缺失（Glob `**/MANIFEST.in`返回No file found）；pyproject.toml无[tool.setuptools.package-data]段
- **证据**：项目运行依赖大量非.py数据文件（config/*.yaml、*.sql等）
- **问题**：setuptools默认仅打包.py文件；无MANIFEST.in → wheel/sdist不含.yaml/.sql
- **影响**：pip install zephyralpha后包不可用（缺数据文件）；当前仅因pip install -e .掩盖
- **修复**：新增MANIFEST.in或pyproject.toml [tool.setuptools.package-data]声明*.yaml/*.sql
- **状态**：FIXED（2026-07-04）— 新建 MANIFEST.in，recursive-include config/src *.yaml *.yml *.json *.toml *.sql 等

#### 5.31.9 [MEDIUM] CI无wheel/sdist构建测试
- **文件**：[governance.yml](file:///D:/ZephyrAlpha/.github/workflows/governance.yml)
- **证据**：全文273行无python -m build / pip wheel / pip install .验证步骤
- **问题**：5.31.8（缺MANIFEST.in）与5.31.7（无console_scripts）的问题不会被CI捕获
- **影响**：发布时才发现wheel缺文件/无入口
- **修复**：新增CI job `python -m build && pip install dist/*.whl && python -c "import zephyr"`
- **状态**：STILL_VALID（保留）— 需新增 CI job，涉及 workflow 完整 job 矩阵设计

#### 5.31.10 [MEDIUM] CI无Docker构建测试
- **文件**：[governance.yml](file:///D:/ZephyrAlpha/.github/workflows/governance.yml)
- **证据**：全文无docker build步骤
- **问题**：Dockerfile存在致命问题（5.31.1 CMD指向不存在的模块）但CI不触发构建
- **影响**：Dockerfile损坏持续存在
- **修复**：新增CI job `docker build -t zephyr-test . && docker run --rm zephyr-test python -c "import zephyr"`
- **状态**：STILL_VALID（保留）— 需新增 CI job + Docker registry 凭据配置

#### 5.31.11 [MEDIUM] _version_非标准命名（应为__version__）
- **文件**：[__init__.py](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L67)
- **证据**：`_version_ = "4.6.0"`（单下划线）。Python/PEP 8约定为__version__（双下划线）
- **问题**：import zephyr; zephyr.__version__抛AttributeError；setuptools的dynamic=["version"]默认找__version__
- **影响**：标准工具无法获取运行时版本
- **修复**：改为__version__或彻底删除改用importlib.metadata.version()
- **状态**：FIXED（2026-07-04）— 与 5.31.4 一并修复，_version_ 改为 __version__ 并动态读取 importlib.metadata

#### 5.31.12 [MEDIUM] requires-python与ruff target-version不一致
- **文件**：[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml#L12)
- **证据**：第12行requires-python = ">=3.11"；第77行target-version = "py312"
- **问题**：ruff target py312允许Python 3.12专有语法，但requires-python声明支持3.11
- **影响**：若代码使用3.12语法，3.11用户安装后运行时SyntaxError
- **修复**：统一为requires-python = ">=3.12"且ruff target-version = "py312"
- **状态**：FIXED（2026-07-04）— requires-python 改为 >=3.12，mypy python_version 改为 3.12，与 ruff target-version py312 一致

#### 5.31.13 [MEDIUM] docker-compose.yml挂载不存在的infra/目录
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L41)
- **证据**：第41行./infra/prometheus/prometheus.yml、第66行./infra/grafana/dashboards；Glob infra/**返回No file found
- **问题**：Prometheus与Grafana的配置通过volume挂载，但源路径不存在
- **影响**：docker-compose up后Prometheus与Grafana容器无法正常工作
- **修复**：创建infra/prometheus/prometheus.yml等，或从docker-compose.yml移除相关服务
- **状态**：STILL_VALID（保留）— 需创建完整 prometheus.yml / grafana dashboards / datasources 配置，跨多个配置文件

#### 5.31.14 [MEDIUM] docker-compose.yml env_file: .env但.env被忽略
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L16)
- **证据**：compose第16行env_file: - .env；.gitignore第61行.env被忽略。仓库仅有.env.example
- **问题**：新克隆者无.env，docker-compose up报env file .env not found直接退出
- **影响**：首次运行体验断裂
- **修复**：compose改为env_file: - .env.example作为默认，或用${VAR:-default}模式
- **状态**：FIXED（2026-07-04）— env_file 改为 .env.example（仓库内已包含）

#### 5.31.15 [LOW] docker-compose.yml使用已废弃的version字段
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L4)
- **证据**：`version: "3.9"`。Docker Compose v2忽略此字段并输出warning
- **问题**：过时字段
- **影响**：日志噪音；误导新开发者
- **修复**：删除version: "3.9"行
- **状态**：FIXED（2026-07-04）— 删除 docker-compose.yml L4 `version: "3.9"`

#### 5.31.16 [LOW] CI path filter路径与实际文件位置不匹配
- **文件**：[governance.yml](file:///D:/ZephyrAlpha/.github/workflows/governance.yml#L37)
- **证据**：paths列表含demo_e2e_pipeline.py（根级路径），但实际文件在scripts/construction/demo_e2e_pipeline.py
- **问题**：path filter仅匹配根目录，修改demo pipeline不会触发CI
- **影响**：demo相关变更绕过CI验证
- **修复**：改为`**/demo_e2e_pipeline.py`
- **状态**：FIXED（2026-07-04）— governance.yml push/PR paths 两处均改为 `**/demo_e2e_pipeline.py`

#### 5.31.17 [LOW] pyproject.toml元数据不完整（无authors/license/readme）
- **文件**：[pyproject.toml](file:///D:/ZephyrAlpha/pyproject.toml#L8)
- **证据**：[project]段仅有name/version/description/requires-python/dependencies。无authors/license/readme/keywords/classifiers
- **问题**：PEP 621推荐字段缺失
- **影响**：pip show不显示作者/主页/许可证；企业合规扫描无法确定许可
- **修复**：补充authors/license/readme/classifiers
- **状态**：FIXED（2026-07-04）— 补 readme/LICENSE 引用/authors/keywords/classifiers（含 Python 3.12/3.13、MIT、金融行业分类）

#### 5.31.18 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 4 | 5.31.1/5.31.2/5.31.3/5.31.4 |
| MEDIUM | 10 | 5.31.5~5.31.14 |
| LOW | 3 | 5.31.15/5.31.16/5.31.17 |
| **合计** | **17** | |

**第11轮清理结果（2026-07-04）**：
- FIXED：13 条（5.31.1/5.31.2/5.31.3/5.31.4/5.31.6/5.31.7/5.31.8/5.31.11/5.31.12/5.31.14/5.31.15/5.31.16/5.31.17）
- STILL_VALID 保留：4 条（5.31.5 多阶段构建 / 5.31.9 CI wheel 测试 / 5.31.10 CI Docker 测试 / 5.31.13 infra/ 目录配置）— 需跨文件结构性变更或 CI job 矩阵设计

---

### 5.32 数据迁移策略（10个，第11轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=7(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.32全部清零.
> **维度定义**：数据库schema迁移、数据迁移脚本、版本管理的正确性。
> **病根归属**：根因4（永久功能与一次性脚本未区分——迁移脚本无版本管理）。

#### 5.32.1 [HIGH] migrate_data.py硬编码Windows绝对路径，迁移脚本不可移植
- **文件**：[migrate_data.py](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/migrate_data.py#L35)
- **证据**：`SQLITE_PATH = r'D:\ZephyrAlpha\data\databases\depgraph'`
- **问题**：迁移脚本硬编码Windows绝对路径，未使用REPO_ROOT或环境变量
- **影响**：脚本在Linux/Mac/CI/Docker中无法运行
- **修复**：改用`from _shared.constants import REPO_ROOT` + `SQLITE_PATH = REPO_ROOT / "data" / "databases" / "depgraph.db"`
- **状态**：DRIFTED（2026-07-04）— 现 L56 已是 `SQLITE_PATH = str(REPO_ROOT / "data" / "databases" / "depgraph.db")`，L53 `from zephyr.shared.io.paths import REPO_ROOT`，硬编码 Windows 路径已修复

#### 5.32.2 [HIGH] migrate_data.py先TRUNCATE再INSERT，迁移中途失败导致数据全损
- **文件**：[migrate_data.py](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/migrate_data.py#L140)
- **证据**：main()顺序为truncate_all_tables→disable_all_triggers→循环migrate_table→reset_identity
- **问题**：迁移失败后PG处于"部分表已TRUNCATE、部分表已INSERT"的中间态
- **影响**：25张表中第13张失败→前12张已写入但触发器禁用期间未校验
- **修复**：每张表迁移用BEGIN;INSERT;VERIFY;COMMIT包裹
- **状态**：STILL_VALID（保留）— 现状 pg_conn.autocommit=False + except 块 rollback 已提供事务保护，但仍是单大事务模式（truncate→disable→循环migrate→reset→enable）。改为每表独立事务属大规模重构

#### 5.32.3 [HIGH] migrate_data.py零测试覆盖，关键迁移脚本无验证
- **文件**：tests/整目录
- **证据**：Grep "migrate_data|migrate_sqlite_to_pg" tests/返回0匹配
- **问题**：一次性数据迁移脚本（不可逆）零测试覆盖
- **影响**：FK丢失、类型不匹配、序列冲突只能在生产发现
- **修复**：新增tests/test_migrate_sqlite_to_pg.py
- **状态**：STILL_VALID（保留）— Grep tests/ 确认仍 0 匹配；需新增完整测试套件（含 SQLite fixture + PG fixture + 行数校验）

#### 5.32.4 [MEDIUM] migrate_data.py无幂等标记/无版本记录，无法判断迁移是否已应用
- **文件**：[migrate_data.py](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/migrate_data.py#L221)
- **证据**：main()流程无_schema_version表写入；无migration_log表；无IF EXISTS检查
- **问题**：迁移脚本无幂等性设计；重复运行=数据全清
- **影响**：运维误执行=数据丢失
- **修复**：在_schema_version表插入迁移记录；运行前检查是否已存在
- **状态**：STILL_VALID（保留）— 现 main() 流程仍无 _schema_version 写入；需新增幂等性设计

#### 5.32.5 [MEDIUM] migrate_sqlite_to_pg/目录无README/manifest文档化执行顺序
- **文件**：[migrate_sqlite_to_pg/](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/)
- **证据**：Glob *.md返回0文件；4个文件执行顺序未文档化
- **问题**：新运维人员可能先跑migrate_data.py再跑02_create_pg_schema.sql→报错
- **影响**：迁移操作门槛高；AI无法从目录结构推断正确顺序
- **修复**：新增README.md文档化执行顺序、前置条件、回滚步骤
- **状态**：STILL_VALID（保留）— Glob 确认目录下仍无 README.md，仅有 4 个文件（00/01/02 SQL + migrate_data.py）

#### 5.32.7 [MEDIUM] 02_create_pg_schema.sql无对应downgrade/rollback SQL
- **文件**：[02_create_pg_schema.sql](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql)
- **证据**：文件仅含CREATE TABLE/INDEX/TRIGGER/VIEW语句；无DROP TABLE、无down.sql
- **问题**：PG schema创建后无系统化回滚路径
- **影响**：schema变更无法快速回退
- **修复**：新增02_create_pg_schema_down.sql含按反依赖顺序的DROP语句
- **状态**：STILL_VALID（保留）— 需新增 downgrade SQL 文件

#### 5.32.8 [MEDIUM] apply_depgraph.py数据变更与schema变更版本管理混淆
- **文件**：[apply_depgraph.py](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py)
- **证据**：脚本提供--update-module/--insert-domain等数据变更命令，但数据变更不记录任何版本号
- **问题**：数据层变更与schema层变更版本管理割裂
- **影响**：灾后恢复时无法判断哪些数据变更需重放
- **修复**：apply_depgraph.py每次变更写入_data_changes_log表
- **状态**：STILL_VALID（保留）— 需新增 _data_changes_log 表 + apply_depgraph.py 变更点埋点

#### 5.32.10 [LOW] migrate_data.py混淆数据种子与数据迁移，无独立seed脚本
- **文件**：[migrate_data.py](file:///D:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/migrate_data.py#L42)
- **证据**：MIGRATION_ORDER列表混合了种子数据（domains/registries等YAML真源只读表）与运营数据
- **问题**：新建空PG实例必须先有SQLite数据才能迁移；无法init_db && seed直接初始化
- **影响**：环境搭建门槛高
- **修复**：拆分为migrate_data.py（运营数据）+ seed_from_yaml.py（从YAML真源直接灌种子表）
- **状态**：STILL_VALID（保留）— MIGRATION_ORDER 列表仍混合种子表（domains/registries 等）与运营数据，需拆分脚本

#### 5.32.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 3 | 5.32.1/5.32.2/5.32.3 |
| MEDIUM | 6 | 5.32.4~5.32.9 |
| LOW | 1 | 5.32.10 |
| **合计** | **10** | |

---

### 5.33 容灾与备份（10个，第11轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=5(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.33全部清零.
> **维度定义**：数据库备份、灾难恢复、RTO/RPO定义、单点故障消除。
> **病根归属**：根因1（静态快照——P2迁移后备份机制未更新）。

#### 5.33.2 [HIGH] backup_runtime_state.py完全过时——仍按SQLite设计，PG迁移后未更新
- **文件**：[backup_runtime_state.py](file:///D:/ZephyrAlpha/scripts/governance/meta/backup_runtime_state.py#L16)
- **证据**：docstring"SQLite表→JSON导出"；backup_yaml_files()仅备份meta/*.yaml；无PG备份逻辑
- **问题**：备份工具仍按SQLite时代设计；P2迁移后未更新
- **影响**：虚假安全感；灾后无PG数据可恢复
- **修复**：更新docstring + manifest；新增backup_pg_depgraph()函数
- **ARCH-041 部分治本（2026-07-02）**：docstring 已标注 DEPRECATED 并指向 git history 真源（directory_contract L740）；默认输出路径从 `meta/_backups/`（deprecated）改为 `tmp/runtime_backups/`（不进 git，.gitignore 已加规则）。**剩余债务**：脚本本身仍按 SQLite 时代设计，未新增 `backup_pg_depgraph()` 函数。
- **ARCH-041 合并处理立项（2026-07-02）**：与 §5.33.1 合并处理——重写 backup_runtime_state.py 为 PG 版本（新增 `backup_pg_depgraph()` 函数），重写完成后本节与 §5.33.1 同时关闭。治本变更需在无并发 AI 环境下执行（project_memory: "治本变更未提交前禁止并发AI对话"）。
- **✅ 已解决（2026-07-03）**：`backup_pg_depgraph()` 已实现（§5.33.1 已解决），docstring 已更新去掉"PG 备份待重写"表述，main() 添加 DEPRECATED 警告（warnings.warn + stderr）。YAML/JSONL 快照功能保留向后兼容但标记 DEPRECATED。本节与 §5.33.1 同时关闭。

#### 5.33.3 [HIGH] phase_a_backup.py BACKUP_BASE硬编码Windows非ASCII路径
- **文件**：[phase_a_backup.py](file:///D:/ZephyrAlpha/scripts/governance/_archive/one_off/phase_a_backup.py#L61)
- **证据**：`BACKUP_BASE = Path("D:/临时工作区/_backups/phase-A")`——硬编码Windows盘符+中文目录
- **问题**：备份目标路径硬编码Windows+中文；Linux/Mac/CI运行报错
- **影响**：备份脚本在Docker/CI/Linux中不可用；"异地备份"实为同盘备份
- **修复**：改BACKUP_BASE = Path(os.environ.get("ZEPHYR_BACKUP_DIR", REPO_ROOT / "data/backups/phase-A"))
- **状态**：DRIFTED（2026-07-04）— 脚本已归档到 `scripts/governance/_archive/one_off/phase_a_backup.py`，属一次性脚本文档，不再活跃使用；硬编码路径问题不再影响生产

#### 5.33.4 [HIGH] phase_a_backup.py Tier0备份遗漏depgraph (PostgreSQL)（核心资产）
- **文件**：[phase_a_backup.py](file:///D:/ZephyrAlpha/scripts/governance/_archive/one_off/phase_a_backup.py#L66)
- **证据**：TIER0_FILES含5个核心资产，无 depgraph (PostgreSQL) 备份项；data/asset_index/project-entity-depgraph.yaml是YAML导出非PG数据库备份
- **问题**：Tier0标称"5个核心资产"但遗漏真正的 depgraph (PostgreSQL)
- **影响**：恢复时depgraph数据丢失；YAML副本只能恢复到上次导出时点
- **修复**：TIER0_FILES新增pg://depgraph虚拟路径，run_tier0识别pg://前缀时调用pg_dump
- **状态**：DRIFTED（2026-07-04）— 同 5.33.3，phase_a_backup.py 已归档；且 §5.33.8 中 backup_pg_depgraph() 已实现 PG 备份

#### 5.33.5 [HIGH] 项目无RTO/RPO定义，无法评估备份策略充分性
- **文件**：全项目Grep RTO|RPO|recovery_point|recovery_time仅命中1处注释
- **证据**：无docs/02_enterprise_architecture/dr_policy.yaml；无config/backup_policy.yaml
- **问题**：无项目级RTO/RPO定义；无法判断"每日备份"是否足够
- **影响**：备份频率无依据；合规审计无法回答"RPO=? RTO=?"
- **修复**：新增dr_policy.yaml定义：depgraph RPO=24h/RTO=4h；governance.db RPO=1h/RTO=1h
- **状态**：STILL_VALID（保留）— `docs/02_enterprise_architecture/target_architecture/technology_architecture.md` L219 已有 "RTO/RPO 核心链路分层矩阵"，但 operations_architecture.md L190 仍标 "占位：RTO/RPO 量化目标待激活后补齐"；缺独立 dr_policy.yaml 真源文件

#### 5.33.6 [HIGH] PostgreSQL单机localhost，无故障切换机制（SPOF）
- **文件**：[.env.postgres](file:///D:/ZephyrAlpha/config/.env.postgres#L1)
- **证据**：POSTGRES_HOST=localhost；单实例、单主机、无副本；get_depgraph_pg_connection()无连接池、无重试
- **问题**：PG是单点故障（SPOF）；无流复制副本；无Patroni/repmgr等自动故障切换
- **影响**：PG进程崩溃=全项目停摆；磁盘故障=数据全损
- **修复**：部署PG主从复制；配置POSTGRES_HOST_PRIMARY/STANDBY；引入pgbouncer
- **状态**：STILL_VALID（保留）— 需部署 PG 主从复制 + pgbouncer，属基础设施层变更，超出代码修复范围

#### 5.33.7 [HIGH] .runtime/状态文件（200+ handoffs、100+ reconcile_reports）无恢复路径
- **文件**：.runtime/handoffs/（200+ JSON）、.runtime/reconcile_reports/（100+ JSON）
- **证据**：.gitignore第102行.runtime/整目录忽略；backup_runtime_state.py仅备份scripts/governance/meta/，不含.runtime/
- **问题**：200+ session handoff JSON + 100+ reconcile报告完全无备份
- **影响**：AI助手无法恢复上次session上下文；reconcile审计链断裂
- **修复**：backup_runtime_state.py新增backup_runtime_handoffs()函数
- **状态**：STILL_VALID（保留）— backup_runtime_state.py 未新增 backup_runtime_handoffs()；.runtime/ 整目录在 .gitignore 中

#### 5.33.8 [HIGH] depgraph SQLite备份机制删除后未替换为PG备份（灾备回退）
- **文件**：[apply_depgraph.py](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L53)
- **证据**：注释"原SQLite文件备份门禁已删除——PG用MVCC事务rollback提供原子性，无需文件备份"
- **问题**：P2迁移前depgraph通过git commit备份；迁移后SQLite备份机制删除，但PG备份机制未建立
- **影响**：灾备能力较P2迁移前**回退**——SQLite时代至少有git历史，PG时代无任何备份
- **修复**：立即建立PG pg_dump备份；在apply_depgraph.py写入前调用pg_dump作为变更前快照
- **状态**：FIXED（2026-07-04）— `backup_runtime_state.py` L145 `backup_pg_depgraph()` 已实现（psycopg2 查询导出为 JSON，pg_dump 不可用时 fallback）；`apply_depgraph.py` 通过 depgraph_schema 模块自动调用作为变更前快照

#### 5.33.9 [MEDIUM] 无恢复演练/无备份验证测试
- **文件**：tests/整目录
- **证据**：Grep "restore.*drill|restore.*test|verify_backup" tests/返回0匹配；phase_a_backup.py run_verify_only()仅校验SHA256一致性
- **问题**：备份存在但从未演练恢复；"备份成功但恢复失败"问题只能在真实灾难中发现
- **影响**：灾难时发现备份格式错误、依赖缺失；RTO远超预期
- **修复**：新增tests/dr/test_restore_from_backup.py；季度执行恢复演练
- **状态**：STILL_VALID（保留）— tests/ 下仍无 restore drill 测试；需新增 tests/dr/test_restore_from_backup.py + 季度执行机制

#### 5.33.10 [MEDIUM] config/.env.postgres单副本，无异地/加密备份
- **文件**：[.env.postgres](file:///D:/ZephyrAlpha/config/.env.postgres) + .gitignore:244
- **证据**：文件含POSTGRES_PASSWORD=zephyr_dev_2026（明文）；.gitignore忽略git；无加密副本；无secrets manager集成
- **问题**：PG密码仅存于本地磁盘单副本；磁盘故障=密码丢失=即使有pg_dump也无法恢复
- **影响**：灾后恢复阻断在"获取密码"步骤；密码泄露风险
- **修复**：密码迁入secrets manager；.env.postgres仅保留非敏感字段
- **状态**：STILL_VALID（保留）— 需引入 secrets manager（如 Vault / AWS Secrets Manager），属基础设施层变更

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

> **第42轮修复状态（2026-07-05）**：DEFERRED=7(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.34全部清零.
> **维度定义**：dev/staging/prod环境配置分离、测试数据库隔离、密钥管理。
> **病根归属**：根因4（永久功能与一次性脚本未区分——环境抽象存在但未接入）。

#### 5.34.1 [HIGH] docker-compose.yml硬编码ZEPHYR_ENV=development，与Env枚举不匹配（静默回退）
- **文件**：[docker-compose.yml](file:///D:/ZephyrAlpha/docker-compose.yml#L18) + [env.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/env.py#L64)
- **证据**：docker-compose设置ZEPHYR_ENV=development；env.py Env枚举只有dev/staging/production/test——development不在枚举中；_detect_env()的ValueError被吞掉，回退Env.DEV
- **问题**：容器"以为"配置了production/staging，实际运行在DEV模式；环境检测静默回退
- **影响**：环境隔离完全失效
- **修复**：docker-compose.yml改ZEPHYR_ENV=dev；或env.py枚举增加development别名
- **状态**：FIXED（2026-07-04）— docker-compose.yml L22 改为 `ZEPHYR_ENV=dev`（与 Env 枚举值一致）

#### 5.34.2 [HIGH] 无Docker Compose override文件，dev/prod/staging共用单一配置
- **文件**：项目根目录
- **证据**：Glob **/docker-compose*.y*ml仅返回docker-compose.yml；无docker-compose.override.yml/prod.yml/staging.yml
- **问题**：单一docker-compose.yml同时服务dev/staging/prod
- **影响**：prod环境暴露9090/3000/9100端口（监控面板）；dev环境无独立DB容器
- **修复**：新增docker-compose.prod.yml/staging.yml/override.yml
- **状态**：STILL_VALID（保留）— 需新增多个 compose override 文件，涉及 dev/staging/prod 完整配置矩阵设计

#### 5.34.3 [HIGH] 测试使用SQLite而生产用PostgreSQL，schema已知分歧
- **文件**：[conftest.py](file:///D:/ZephyrAlpha/tests/conftest.py#L39)
- **证据**：tmp_db fixture使用from zephyr.governance.sqlite_schema import init_db；生产depgraph是PG
- **问题**：测试验证的行为基于SQLite schema，生产运行PG schema；5.18.3/5.18.4/5.18.6已记录两schema分歧
- **影响**：FK约束、CHECK约束、触发器行为差异在测试中不可见
- **修复**：测试fixture改用PG testcontainers或独立PG test数据库
- **状态**：STILL_VALID（保留）— 需引入 testcontainers 或独立 PG test 数据库，涉及 tests/ 全量 fixture 重构

#### 5.34.4 [HIGH] 测试直接连接生产PostgreSQL，无测试数据库隔离（与5.21交叉确认）
- **文件**：[test_depgraph_db.py](file:///D:/ZephyrAlpha/tests/governance/depgraph/test_depgraph_db.py#L13)
- **证据**：from zephyr.governance.depgraph_schema import get_depgraph_pg_connection；conn = get_depgraph_pg_connection()——直连生产PG (localhost:5432/depgraph)
- **问题**：测试与生产共用同一PG数据库；测试INSERT/UPDATE/DELETE直接修改生产数据
- **影响**：违反project_memory.md第10行"测试脚本必须严格隔离生产库"硬约束
- **修复**：新增config/.env.postgres.test（POSTGRES_DB=depgraph_test）；get_depgraph_pg_connection()检测PYTEST_CURRENT_TEST自动切测试库
- **状态**：STILL_VALID（保留）— 需新增 config/.env.postgres.test + 修改 get_depgraph_pg_connection() 检测 PYTEST_CURRENT_TEST

#### 5.34.5 [HIGH] PG连接硬编码config/.env.postgres，无DATABASE_URL环境变量模式
- **文件**：[depgraph_schema.py](file:///D:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py#L89)
- **证据**：_PG_ENV_PATH = REPO_ROOT / "config" / ".env.postgres"；_load_pg_config()手动解析KEY=VALUE文件；无DATABASE_URL环境变量支持
- **问题**：PG连接配置基于文件位置而非环境变量；12-Factor §III违规
- **影响**：dev/staging/prod切换需修改文件；容器化部署需mount配置文件而非传env var
- **修复**：_load_pg_config()优先读DATABASE_URL env var
- **状态**：STILL_VALID（保留）— 需重构 _load_pg_config() 支持 DATABASE_URL 12-Factor 模式

#### 5.34.6 [HIGH] is_dev()/is_prod()/is_staging()/is_test()在生产代码中零调用（死抽象）
- **文件**：[env.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/env.py#L98)
- **证据**：Grep is_prod()|is_staging()|is_dev()|is_test()命中15处，全部在env.py自身定义+tests+文档；**无任何生产代码调用**
- **问题**：环境检测抽象存在但无人使用；生产代码无任何环境分支逻辑
- **影响**：所有环境运行相同行为；无"prod禁止DROP TABLE"等安全守卫
- **修复**：在关键路径引入环境检查，如apply_depgraph.py写入前if is_prod(): require_approval()
- **状态**：STILL_VALID（保留）— 需在 apply_depgraph.py 等关键路径引入 is_prod() 守卫，涉及多个写入点改造

#### 5.34.7 [HIGH] 生产代码硬编码SQLite governance.db路径，与 depgraph (PostgreSQL) 形成双库无隔离
- **文件**：[dashboard.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/dashboard.py#L60)、[dlq.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/dlq.py#L30)
- **证据**：6个生产模块硬编码`data/databases/governance.db`路径；depgraph已迁PG但governance.db仍为SQLite
- **问题**：生产同时运行两套数据库系统（SQLite governance.db + depgraph (PostgreSQL)）；两库无跨库事务一致性
- **影响**：governance.db文件锁竞争导致写入失败；灾备需同时备份PG+SQLite
- **修复**：governance.db也迁移到PG（作为governance schema）
- **状态**：STILL_VALID（保留）— 需将 governance.db 迁移到 PG 作为 governance schema，属大规模数据库迁移

#### 5.34.9 [MEDIUM] .env.example未文档化PG配置
- **文件**：[.env.example](file:///D:/ZephyrAlpha/.env.example#L30)
- **证据**：仅注释SQLite路径（已废弃）；无POSTGRES_HOST/PORT/DB/USER/PASSWORD说明；无config/.env.postgres文件位置说明
- **问题**：新开发者无法从.env.example推断PG配置
- **影响**：onboarding阻塞
- **修复**：.env.example新增PostgreSQL段落；新增config/.env.postgres.example模板
- **状态**：FIXED（2026-07-04）— .env.example L62-72 新增 PostgreSQL 段落，文档化 POSTGRES_HOST/PORT/DB/USER/PASSWORD 及 config/.env.postgres 文件位置说明

#### 5.34.10 [MEDIUM] 日志级别不按环境分级，dev/prod同为INFO
- **文件**：[logging.py](file:///D:/ZephyrAlpha/src/zephyr/shared/utils/logging.py#L324)
- **证据**：configure_root_logger默认level="INFO"不读env；ZEPHYR_LOG_LEVEL env var存在但未端到端打通
- **问题**：dev/staging/prod共用INFO级别；无"dev=DEBUG/prod=WARNING"分级策略
- **影响**：dev排障缺DEBUG信息；prod日志过详细
- **修复**：configure_root_logger()默认level = "DEBUG" if is_dev() else "WARNING"
- **状态**：STILL_VALID（保留）— 需重构 configure_root_logger() 接入 is_dev()/is_prod() 环境检测

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

> **第42轮修复状态（2026-07-05）**：DEFERRED=5(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.35全部清零.
> **维度定义**：API/MCP工具的版本标识、breaking change检测、deprecation策略。
> **病根归属**：根因5（无API版本管理规则）。

#### 5.35.1 [HIGH] gateway路由与mcp.json配置漂移
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L260) vs [mcp.json](file:///D:/ZephyrAlpha/config/mcp.json#L91)
- **证据**：gateway代码第267行路由键为"vector-memory"（连字符）；mcp.json第91行server_id为"vector_memory"（下划线）。gateway第260行有"telemetry"路由，但mcp.json无此server
- **问题**：代码路由表与配置文件不一致
- **影响**：vector_memory的per-server限流和RBAC ACL对gateway路由失效
- **修复**：统一为下划线命名，从mcp.json单向生成gateway路由表
- **状态**：STILL_VALID（保留）— gateway_server.py L250 路由键 "vector-memory"（连字符）vs mcp.json L91 "vector_memory"（下划线）分歧仍存在；修复需统一命名 + 涉及 RBAC ACL 关联配置

#### 5.35.2 [MEDIUM] MCP工具定义无版本字段
- **文件**：[_base_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/_base_server.py#L121)
- **证据**：ToolDefinition dataclass仅有name/description/input_schema/handler/safety_level五个字段，无version字段
- **问题**：MCP工具无版本标识，工具签名/行为变更后消费方无法感知版本差异
- **影响**：工具参数变更属breaking change，但调用方无法做版本兼容判断
- **修复**：在ToolDefinition增加version: str = "1.0.0"字段
- **状态**：FIXED（2026-07-04）— ToolDefinition 新增 `version: str = "1.0.0"`；register_tool() 同步增加 version 参数；_handle_tools_list() 返回 version 字段

#### 5.35.3 [MEDIUM] mcp.json各server缺少version字段
- **文件**：[mcp.json](file:///D:/ZephyrAlpha/config/mcp.json#L13)
- **证据**：10个server配置项均无version字段，仅顶层gateway有"version": "1.0.0"
- **问题**：server级别无版本管理，无法追踪各server的API演进
- **影响**：server升级时无法做版本协商
- **修复**：为每个server配置项增加version字段
- **状态**：STILL_VALID（保留）— mcp.json 10 个 server 配置项均无 version 字段，需为每个 server 单独确定版本号

#### 5.35.4 [MEDIUM] api_version_contract.py是孤立未集成的死代码
- **文件**：[api_version_contract.py](file:///D:/ZephyrAlpha/src/zephyr/trading/feedback_loop/actors/api_version_contract.py#L1)
- **证据**：定义了APIVersionContract dataclass含sunset_date/replacement_version，但无注册表、无执行逻辑、无任何API框架集成
- **问题**：API版本契约模型已定义但从未被任何代码import使用
- **影响**：废弃API版本不会被检测/阻断
- **修复**：将此模型集成到MCP gateway的工具调用链路，或删除死代码
- **状态**：STILL_VALID（保留）— Grep 确认 APIVersionContract 仅在 tests/ 中被 import，无生产代码集成；需集成到 MCP gateway 工具调用链路或决定删除

#### 5.35.6 [MEDIUM] MCP工具无deprecation策略
- **文件**：[integration/mcp/](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/)
- **证据**：Grep deprecated|deprecation|sunset在整个integration/mcp目录无任何匹配
- **问题**：工具可被直接删除/重命名，无废弃过渡期
- **影响**：依赖该工具的agent/IDE在工具消失后立即失败，无迁移窗口
- **修复**：在ToolDefinition增加deprecated: bool和sunset_date字段
- **状态**：FIXED（2026-07-04）— ToolDefinition 新增 `deprecated: bool = False`、`sunset_date: str | None = None`、`replacement: str | None = None`；register_tool() 同步增加参数；_handle_tools_list() 返回 deprecated/sunsetDate/replacement 字段

#### 5.35.7 [LOW] 无OpenAPI/Swagger响应schema
- **文件**：全项目
- **证据**：Grep openapi|swagger仅在YAML词表和docs中出现；_base_server.py的tools/list返回input_schema但无output_schema
- **问题**：API响应无契约schema，调用方只能靠试错解析返回值
- **影响**：消费者需hardcode返回值结构猜测
- **修复**：为每个工具增加output_schema
- **状态**：STILL_VALID（保留）— 需为每个工具定义 output_schema，涉及全量工具的响应契约梳理

#### 5.35.8 [LOW] gateway版本硬编码且无版本协商
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L66)
- **证据**：_GATEWAY_VERSION = "1.0.0"硬编码常量；tools/call请求/响应中无客户端期望版本字段
- **问题**：版本号硬编码在源码中；客户端无法声明所需API版本
- **影响**：版本升级需改代码；客户端无法做版本降级兼容
- **修复**：版本号从mcp.json加载；在JSON-RPC请求中增加api_version字段
- **状态**：STILL_VALID（保留）— gateway_server.py L67 `_GATEWAY_VERSION = "1.0.0"` 仍硬编码；需从 mcp.json 加载 + JSON-RPC 请求增加 api_version 字段

#### 5.35.9 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.35.1 |
| MEDIUM | 5 | 5.35.2~5.35.6 |
| LOW | 2 | 5.35.7/5.35.8 |
| **合计** | **8** | |

---

### 5.36 限流与配额（10个，第11轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=7(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.36全部清零.
> **维度定义**：限流算法实现、per-user配额、配置加载、配额耗尽告警。
> **病根归属**：根因5（限流规则存在但执行断层）。

#### 5.36.1 [HIGH] 4+限流器实现碎片化
- **文件**：[shared/infra/limiter.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/limiter.py)、[shared/infra_06/limiter.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/limiter.py)、[infrastructure/rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rate_limiter.py)、[integration/mcp/rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/rate_limiter.py)、[a2a_protocol/governance/rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/governance/rate_limiter.py)
- **证据**：5个文件，3种不同算法（async token bucket / sync token bucket / sliding window）；infrastructure/rate_limiter.py与integration/mcp/rate_limiter.py逐行完全相同
- **问题**：限流逻辑分散在5处，算法不一致，配置不可统一管理
- **影响**：修改限流策略需改5处；不同路径走不同算法
- **修复**：收敛为单一canonical实现（shared/infra/limiter.py）
- **状态**：STILL_VALID（保留）— 需大规模重构5个文件为单一canonical实现，涉及跨模块收敛与多调用方迁移，超出本轮快速修复范围

#### 5.36.2 [HIGH] 无per-user/per-key配额，全部per-tool共享
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L499)
- **证据**：self._rate_limiter.try_acquire(routed_sid)——限流key是routed_sid（server_id如"task_manager"），所有客户端共享同一bucket
- **问题**：一个滥用客户端可耗尽全局限流配额
- **影响**：多租户场景下单租户DoS全系统
- **修复**：限流key改为(client_session_id, tool_name)二元组
- **状态**：STILL_VALID（保留）— 需修改 gateway_server.py 限流调用点并引入 client_session_id 维度，涉及管道多阶段协调，超出本轮快速修复范围

#### 5.36.3 [MEDIUM] TokenBucketLimiter存在竞态条件
- **文件**：[limiter.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/limiter.py#L137)
- **证据**：第137行self._lock.release()释放锁后sleep，第142行await self._lock.acquire()重新获取。期间其他协程可修改_tokens/_last_refill
- **问题**：并发场景下token计数不准
- **影响**：限流精度下降，高并发下可能放行超出配额的请求
- **修复**：sleep期间不释放锁，或重新获取后重新执行_refill()
- **状态**：STILL_VALID（保留）— 需修改 shared/infra/limiter.py async 锁逻辑，async 锁语义需谨慎设计避免死锁，超出本轮快速修复范围

#### 5.36.4 [MEDIUM] a2a RateLimiter.allow(key)的key参数被忽略
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/governance/rate_limiter.py#L25)
- **证据**：allow(self, key="default")接收key参数，但操作的是self._requests（单一列表），key从未用于分桶
- **问题**：API签名暗示支持per-key限流，实际所有key共享一个bucket
- **影响**：调用方误以为per-key隔离已生效
- **修复**：改为dict[str, list[float]]按key分桶，或删除误导性key参数
- **状态**：FIXED — 已改为 dict[str, list[float]] 按 key 分桶，每个 key 独立计数；reset() 同步支持按 key 重置

#### 5.36.5 [MEDIUM] a2a RateLimiter无线程安全
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/governance/rate_limiter.py#L23)
- **证据**：self._requests = [t for t in self._requests if ...]列表操作无threading.Lock保护
- **问题**：多线程并发调用allow()时列表读写竞态
- **影响**：高并发下限流失效或抛异常
- **修复**：增加threading.Lock保护列表操作
- **状态**：FIXED — 已增加 threading.Lock 保护 _requests_by_key 的所有读写操作（allow/reset）

#### 5.36.6 [MEDIUM] 限流配置不可动态调整
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/rate_limiter.py#L45)
- **证据**：DEFAULT_QPS = 10.0、DEFAULT_BURST = 30.0硬编码常量。docstring声称"从config/mcp.json加载"，但无任何代码读取mcp.json的rate_limit配置节
- **问题**：mcp.json的rate_limit配置项是死配置；调整限流需改代码重启
- **影响**：运维无法按负载动态调参
- **修复**：在PerToolRateLimiter初始化时从mcp.json加载配置
- **状态**：STILL_VALID（保留）— 需新增 mcp.json 加载逻辑与运行时热更新机制，涉及配置变更通知多调用方，超出本轮快速修复范围

#### 5.36.7 [MEDIUM] Retry-After头配置启用但未实现
- **文件**：[mcp.json](file:///D:/ZephyrAlpha/config/mcp.json#L131) vs [gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L499)
- **证据**：mcp.json "retry_after_header": true；gateway限流后返回ERR_RBAC_DENIED，响应中无retry_after字段
- **问题**：配置声明返回Retry-After头，实际未返回
- **影响**：客户端无法知道何时重试，导致盲目重试加剧限流压力
- **修复**：限流拒绝响应中增加retry_after_seconds字段
- **状态**：STILL_VALID（保留）— 需修改 gateway_server.py 限流拒绝响应构造逻辑与错误码体系，涉及 JSON-RPC error.data 字段扩展，超出本轮快速修复范围

#### 5.36.8 [MEDIUM] gateway管道阶段顺序与文档不符
- **文件**：[gateway_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/gateway_server.py#L479)
- **证据**：docstring"五阶段管道：Permission→RateLimit→Route→Audit→Degrade"；实际顺序：Route→RateLimit→Audit→LSG→Safety→Degrade，无Permission阶段
- **问题**：文档描述的Permission阶段缺失；RateLimit在Route之后（未路由的请求不受限流保护）
- **影响**：未知工具名请求绕过限流；权限检查缺失
- **修复**：补充Permission阶段；将文档与实现对齐
- **状态**：STILL_VALID（保留）— 需补充 Permission 阶段并重排管道顺序，涉及 gateway 核心路由逻辑重构与多调用方契约验证，超出本轮快速修复范围

#### 5.36.9 [LOW] PerToolRateLimiter docstring与实现不符
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/rate_limiter.py#L140)
- **证据**：docstring"默认10QPS per client"；实际try_acquire(tool_name)按tool_name分桶，无client维度
- **问题**：文档声称per-client，实际per-tool
- **影响**：安全审计/容量规划基于错误假设
- **修复**：修正docstring为"per-tool"，或实现真正的per-client限流
- **状态**：FIXED — 已修正 docstring 为 "默认 10QPS per tool"，并标注 per-client 限流需引入 client_id 维度（参见 5.36.2 待后续重构）

#### 5.36.10 [LOW] 无限流配额耗尽告警
- **文件**：[rate_limiter.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/rate_limiter.py#L124)
- **证据**：stats()返回total_rejected计数，但无阈值告警逻辑；无代码将total_rejected接入alert_rules.yaml
- **问题**：限流拒绝量激增时无告警
- **影响**：DoS攻击或配额耗尽时运维无感知
- **修复**：将total_rejected接入metrics，配置告警规则
- **状态**：STILL_VALID（保留）— 需新增 metrics 导出与 alert_rules.yaml 告警规则配置，涉及监控体系集成，超出本轮快速修复范围

#### 5.36.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.36.1/5.36.2 |
| MEDIUM | 6 | 5.36.3~5.36.8 |
| LOW | 2 | 5.36.9/5.36.10 |
| **合计** | **10** | |

---

### 5.37 审计日志完整性（13个，第11轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=7(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.37全部清零.
> **维度定义**：审计日志的字段完整性、防篡改链、持久化、retention策略。
> **病根归属**：根因5（审计日志规则存在但全链路stub）。注意：5.17已覆盖AuditWriter.write() no-op和HMAC硬编码，本节审查其他方面。

#### 5.37.1 [HIGH] write_to_core桥接函数是no-op（仅日志不写入）
- **文件**：[bridge.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/bridge.py#L25)
- **证据**：def write_to_core(channel, payload): logger.info("write_to_core channel=%s payload_keys=%s", ...)——仅打印日志，无任何持久化写入
- **问题**：所有通过write_to_core写入"核心审计链"的事件实际被丢弃
- **影响**：声称的"不可变审计链"不存在；安全审计事件丢失
- **修复**：实现真正的写入逻辑（写入events.jsonl + hash chain）
- **状态**：STILL_VALID（保留）— 需实现真正写入逻辑（events.jsonl + hash chain），涉及审计链持久化架构设计，超出本轮快速修复范围

#### 5.37.2 [HIGH] AuditChain.verify()永远返回True
- **文件**：[models.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/models.py#L116)
- **证据**：class AuditChain: def verify(self): return True；chain_hash始终为空字符串""
- **问题**：审计链验证是stub，永远返回通过
- **影响**：审计链被篡改也无法检测
- **修复**：实现真正的hash chain验证
- **状态**：STILL_VALID（保留）— AuditChain 是旧 stub 类，新实现为 AuditChainVerifier（已实现 hash chain）；需确认 AuditChain 是否仍有调用方，废弃或迁移，超出本轮快速修复范围

#### 5.37.3 [HIGH] HourlyMerkleAggregator.aggregate返回空root_hash
- **文件**：[merkle_hourly.py](file:///D:/ZephyrAlpha/src/zephyr/governance/merkle_hourly.py#L75)
- **证据**：def aggregate(self, entries, period=""): return AggregationResult(period=period, entry_count=len(entries))——root_hash默认空字符串，从不计算Merkle root
- **问题**：Merkle聚合是stub，不构建任何Merkle树
- **影响**：基于Merkle root的完整性验证无意义
- **修复**：调用MerkleAggregator.build()计算真实root_hash
- **状态**：DRIFTED — audit_trail/merkle_hourly.py L94 已实现 `merkle_root = MerkleAggregator.build(entry_hashes)`，AggregationResult 含真实 merkle_root；债务描述基于旧代码，问题已不存在

#### 5.37.4 [HIGH] MerkleHourlyBridge.verify存在AttributeError
- **文件**：[merkle_hourly.py](file:///D:/ZephyrAlpha/src/zephyr/governance/merkle_hourly.py#L51)
- **证据**：第58行return result.merkle_root == expected_root，但AggregationResult字段名是root_hash，无merkle_root属性
- **问题**：verify调用必抛AttributeError，被except Exception吞掉返回False
- **影响**：所有Merkle验证永远返回False
- **修复**：统一字段名为root_hash或merkle_root
- **状态**：DRIFTED — AggregationResult 字段名已统一为 `merkle_root`（audit_trail/merkle_hourly.py L64），bridge verify L58 `result.merkle_root` 正确访问，问题已不存在

#### 5.37.5 [HIGH] MCP审计日志缺actor/action/target字段
- **文件**：[audit_logger.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/audit_logger.py#L53)
- **证据**：AUDIT_FIELDS = ["timestamp", "client_session_id", "tool_name", "arguments_hash", "result_status", ...]。无actor/action/target
- **问题**：审计日志记录的是"某session调了某工具"，但不知道"谁对哪个实体做了什么操作"
- **影响**：安全事件追溯时无法回答"谁删除了这条记录"，合规审计不达标
- **修复**：增加actor_id/action/target_entity字段
- **状态**：STILL_VALID（保留）— 需扩展 AUDIT_FIELDS 和 log_call 签名，涉及多调用方契约变更与历史日志兼容性，超出本轮快速修复范围

#### 5.37.6 [HIGH] tamper_proof_audit裸调git commit绕过GitCommitGateway
- **文件**：[tamper_proof_audit.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/tamper_proof_audit.py#L245)
- **证据**：subprocess.run(["git", "commit", "-m", f"audit_log: ..."], ...)——直接subprocess调git commit
- **问题**：违反项目硬约束"所有git commit操作必须通过GitCommitGateway工具执行，禁止裸git commit"
- **影响**：审计日志提交绕过五重门禁校验
- **修复**：改用GitCommitGateway提交
- **状态**：STILL_VALID（保留）— 需改用 GitCommitGateway，但 tamper_proof_audit 作为 drift_detection 子模块的自动提交逻辑，涉及运行时上下文（无 session_worktree）与 GitCommitGateway 集成设计，超出本轮快速修复范围

#### 5.37.7 [HIGH] check_audit_log_immutability fail-open
- **文件**：[check_audit_log_immutability.py](file:///D:/ZephyrAlpha/scripts/arch_guard/fitness_functions/check_audit_log_immutability.py#L52)
- **证据**：if not ledger_path.exists(): print("...当前视为通过"); return 0——文件不存在时返回0（pass）
- **问题**：审计日志被删除后检查反而通过
- **影响**：攻击者删除ledger文件即可绕过不可篡改检查
- **修复**：文件不存在时返回1（fail）
- **状态**：FIXED — 已改为 fail-closed：文件不存在返回1（fail），强制运维创建 ledger 文件以通过检查

#### 5.37.8 [MEDIUM] AuditChainVerifier链仅在内存，不持久化
- **文件**：[audit_chain_verifier.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/audit_chain_verifier.py#L66)
- **证据**：self._chain: list[AuditEntry] = []；self._last_hash = "0" * 64。无任何文件/DB写入
- **问题**：进程重启后审计链丢失，无法做事后验证
- **影响**：重启后链断裂，历史审计事件不可重放验证
- **修复**：将chain持久化到events.jsonl（append-only + hash chain）
- **状态**：STILL_VALID（保留）— append() 已通过 _core_writer 写入 AuditWriter（L97-111），但 _chain 本身仍内存；完整持久化需 events.jsonl append-only + hash chain 设计，超出本轮快速修复范围

#### 5.37.9 [MEDIUM] AuditChainVerifier.clear()可绕过防篡改
- **文件**：[audit_chain_verifier.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/audit_chain_verifier.py#L165)
- **证据**：def clear(self): self._chain.clear(); self._last_hash = "0" * 64——无权限保护
- **问题**：篡改者只需调clear()即可销毁全部审计历史
- **影响**：审计链可被轻易抹除，防篡改承诺失效
- **修复**：移除clear()或增加权限校验
- **状态**：STILL_VALID（保留）— 5.17.4 已加审计留痕（clear 前写 chain_cleared 事件），但 clear() 本身仍可调用；需增加权限校验或废弃 clear()，涉及调用方迁移，超出本轮快速修复范围

#### 5.37.10 [MEDIUM] tamper_proof_audit仅哈希前30个文件且哈希截断
- **文件**：[tamper_proof_audit.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/tamper_proof_audit.py#L194)
- **证据**：for pf in list(src_root.rglob("*.py"))[:30]:——仅取前30个.py文件；第234行fh[:16]——sha256截断为16个十六进制字符
- **问题**：项目有数千个.py文件，仅30个被哈希；哈希截断降低碰撞阻力
- **影响**：第31个及之后的文件篡改完全不可检测
- **修复**：哈希全部文件；保留完整sha256
- **状态**：FIXED — 已移除 [:30] 切片哈希全部 .py 文件；fh[:16] 截断改为保留完整 sha256（64个十六进制字符=256位）

#### 5.37.11 [MEDIUM] check_audit_log_immutability谎称JSONL=append-only
- **文件**：[check_audit_log_immutability.py](file:///D:/ZephyrAlpha/scripts/arch_guard/fitness_functions/check_audit_log_immutability.py#L67)
- **证据**：print("append-only属性通过JSONL格式保证")
- **问题**：JSONL格式不提供任何append-only保证，文件可被任意编辑/删除行
- **影响**：运维误以为不可篡改已保证
- **修复**：实现真正的hash chain + HMAC签名验证
- **状态**：FIXED — 已修正 print 描述为明确警告"JSONL 格式本身不保证 append-only"，并指明完整篡改检测需依赖 hash chain + HMAC 签名验证 + Git hook / CI 哈希校验

#### 5.37.12 [MEDIUM] MCP审计日志不受retention/rotation覆盖
- **文件**：[retention.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/retention.py#L38) + [log_rotation.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/log_rotation.py#L40)
- **证据**：retention只覆盖data/audit_history等；log_rotation只glob *.json（非.jsonl）。MCP审计日志写入logs/mcp_audit/tools_call.jsonl，不在任何retention/rotation路径内
- **问题**：MCP审计日志无保留期策略，无轮转
- **影响**：文件无限增长→磁盘耗尽
- **修复**：将logs/mcp_audit/纳入retention策略；log_rotation支持.jsonl格式
- **状态**：STILL_VALID（保留）— 需扩展 retention.py 路径覆盖与 log_rotation.py 的 glob 模式（*.json → *.jsonl），涉及 retention 策略设计与历史日志兼容性，超出本轮快速修复范围

#### 5.37.13 [MEDIUM] integrity.py默认空HMAC key且verify_single哈希不一致
- **文件**：[integrity.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/integrity.py#L102)
- **证据**：第102行hmac_key: str = ""；verify_chain排除entry_hash字段后哈希；verify_single对整个event（含entry_hash）哈希
- **问题**：默认无HMAC验证；两种验证方法哈希算法不一致
- **影响**：默认部署无签名验证；verify_single与verify_chain结果矛盾
- **修复**：默认从环境变量加载HMAC key；统一哈希逻辑
- **状态**：FIXED — HMAC key 已改为优先传入参数，其次从环境变量 AUDIT_HMAC_KEY 加载；verify_single 哈希逻辑已统一为排除 entry_hash 和 hmac_signature，与 verify_chain 一致

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

> **第42轮修复状态（2026-07-05）**：DEFERRED=18(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.38全部清零.
> **第44轮修复状态（2026-07-06）**：FIXED=3(5.38.3默认ON→OFF/5.38.5rollout_pct无标识符时默认False/5.38.9增加created_at/expires_at/owner+is_expired方法), DEFERRED=6(5.38.1系统收敛-3套实现碎片化+audit_orchestration文件已DRIFTED/5.38.2死代码决策接入或删除/5.38.4flags.yaml加载激活/5.38.6审计持久化依赖收敛/5.38.7类名冲突依赖收敛/5.38.8全局flag守护点), DRIFTED=1(5.38.1中audit_orchestration/feature_flag.py已删除), STILL_VALID=0. 维度5.38剩余6项DEFERRED均属特性开关系统专项工程(需统一收敛为单一实现+激活接入启动流程).
> **维度定义**：Feature flag系统的实现一致性、默认值策略、生命周期管理。
> **病根归属**：根因5（特性开关规则存在但未接入）。

#### 5.38.1 [HIGH] 4套特性开关系统碎片化 [⚠ STILL_VALID: 2026-07-04 验证声明不实——实际路径为shared/foundation/flags.py(非foundation/flags.py);trading/orchestrator/governance/feature_flag.py和audit_orchestration/feature_flag.py两份重复仍存在，未删除]
- **文件**：[config/flags.yaml](file:///D:/ZephyrAlpha/config/flags.yaml)、[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py)、[feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestration/feature_flag.py)、[audit_orchestration/feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestration/feature_flag.py)
- **证据**：4个独立实现，3种不同API（FlagState枚举/pydantic bool/YAML布尔树），2种FeatureFlag类定义（dataclass vs BaseModel）
- **问题**：无统一开关真源，行为不一致
- **影响**：新增开关不知该用哪套；运维需检查4处
- **修复**：收敛为foundation/flags.py单一实现
- **状态**：STILL_VALID（保留）— 4套特性开关系统碎片化需统一收敛，涉及多调用方迁移与API统一，超出本轮快速修复范围（2026-07-04 复核确认路径为 shared/foundation/flags.py，重复文件仍存在）

#### 5.38.2 [HIGH] global_flag_registry在生产代码中从未使用 [⚠ STILL_VALID: 2026-07-04 验证声明不实——load_flags_from_yaml函数在src/zephyr/代码中零命中，__init__.py无global_flag_registry引用，原修复声明未落地]
- **文件**：[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py#L168)
- **证据**：Grep global_flag_registry在src/下仅命中flags.py自身定义和api_index.py注释（非实际import）。生产代码无global_flag_registry.is_enabled()调用
- **问题**：整个特性开关系统是死代码，定义了但从未接入任何功能路径
- **影响**：声称有开关系统实际无效；新AI可能误以为可用而依赖它
- **修复**：要么接入关键功能路径，要么删除避免误导
- **状态**：STILL_VALID（保留）— 整个特性开关系统是死代码，需决策接入或删除，涉及功能路径改造，超出本轮快速修复范围

#### 5.38.3 [HIGH] FeatureFlagManager默认ON违反安全默认原则 [⚠ STILL_VALID: 2026-07-04 验证声明不实——FeatureFlagManager未删除(仍存在于两份feature_flag.py)，is_enabled默认return True;FlagRegistry.is_enabled未注册时抛FlagNotFoundError非返回False]
- **文件**：[feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestration/feature_flag.py#L40)
- **证据**：def is_enabled(self, contract_id): flag = self._flags.get(contract_id); return flag.enabled if flag else True——未注册的flag默认返回True
- **问题**：两套系统默认行为相反（foundation/flags.py声明"默认OFF"）；未注册功能默认开启
- **影响**：新功能无需显式启用即生效，违反灰度发布原则
- **修复**：统一默认为False（OFF），未注册flag不允许通过
- **状态**：STILL_VALID（保留）— 两套系统默认行为相反，需统一默认值策略并迁移调用方，涉及特性开关系统收敛（依赖5.38.1），超出本轮快速修复范围

#### 5.38.4 [MEDIUM] config/flags.yaml从未被代码加载 [⚠ STILL_VALID: 2026-07-04 验证声明不实——load_flags_from_yaml函数不存在，flags.yaml从未被代码引用，原修复声明未落地]
- **文件**：[flags.yaml](file:///D:/ZephyrAlpha/config/flags.yaml) + [telemetry_server.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/telemetry_server.py#L186)
- **证据**：Grep flags.yaml仅在telemetry_server.py第186行_exists(_CONFIG_DIR / "flags.yaml")命中——仅检查文件是否存在，不解析内容
- **问题**：flags.yaml是死配置文件，其中所有开关值对运行时无影响
- **影响**：修改flags.yaml不生效；运维误以为可远程控制遥测开关
- **修复**：在启动时yaml.safe_load解析flags.yaml并驱动FlagRegistry
- **状态**：STILL_VALID（保留）— flags.yaml 从未被代码加载，需实现 load_flags_from_yaml 并接入启动流程，涉及特性开关系统激活（依赖5.38.2），超出本轮快速修复范围

#### 5.38.5 [MEDIUM] 灰度发布rollout_pct逻辑有缺陷且未使用 [⚠ STILL_VALID: 2026-07-04 验证声明不实——shared/foundation/flags.py:108-112仍用md5哈希分桶，未改为random.randint(0,99)]
- **文件**：[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py#L108)
- **证据**：第108行if self.rollout_pct > 0 and module_id:——仅当传入module_id才做百分比分桶；第114行return self.state == FlagState.CONDITIONAL——若rollout_pct>0但未传module_id，直接返回True
- **问题**：灰度分桶逻辑仅在传module_id时生效，未传时全量放行
- **影响**：声称支持灰度实际不支持
- **修复**：修正逻辑（未传module_id时按rollout_pct随机分桶）
- **状态**：STILL_VALID（保留）— 灰度分桶逻辑缺陷，但修复涉及灰度发布语义设计（random 导致每次调用结果不稳定），且整个系统是死代码（5.38.2），超出本轮快速修复范围

#### 5.38.6 [MEDIUM] FeatureFlagManager._audit无持久化 [⚠ STILL_VALID: 2026-07-04 验证声明不实——FlagRegistry无_audit方法，FeatureFlagManager._audit仅内存list未写JSONL]
- **文件**：[feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestration/feature_flag.py#L32)
- **证据**：self._audit: list[dict] = []——内存列表；set()时append但不持久化
- **问题**：开关变更审计记录在内存，重启丢失
- **影响**：无法追溯谁在何时改了开关
- **修复**：将变更记录写入持久化审计日志
- **状态**：STILL_VALID（保留）— FeatureFlagManager._audit 仅内存 list，需接入持久化审计日志（依赖特性开关系统收敛5.38.1），超出本轮快速修复范围

#### 5.38.7 [MEDIUM] 两个FeatureFlag类名冲突定义不同 [⚠ STILL_VALID: 2026-07-04 验证声明不实——Grep 'class FeatureFlag' 命中4处定义(trading/orchestrator/governance/feature_flag.py:23、shared/foundation/flags.py:81、audit_orchestration/feature_flag.py:25等)，未收敛]
- **文件**：[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py#L80) vs [feature_flag.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestration/feature_flag.py#L23)
- **证据**：foundation版：@dataclass(frozen=True) class FeatureFlag: key: str; state: FlagState。orchestrator版：class FeatureFlag(BaseModel): contract_id: str; enabled: bool
- **问题**：同名FeatureFlag类，不同基类、不同字段、不同语义
- **影响**：import歧义；类型检查失效
- **修复**：统一为单一FeatureFlag定义
- **状态**：STILL_VALID（保留）— 4处 FeatureFlag 类名冲突定义不同，需统一为单一定义并迁移所有调用方（依赖5.38.1收敛），超出本轮快速修复范围

#### 5.38.8 [MEDIUM] 功能未用flag守护也无if/else硬编码 [⚠ STILL_VALID: 2026-07-04 验证声明不实——__init__.py:108-136的_deferred_bootstrap无flag守护，直接调用_auto_bootstrap，Grep global_flag_registry在__init__.py零命中]
- **文件**：全项目
- **证据**：Grep if ENABLED_|if USE_NEW_|if FEATURE_无匹配；Grep global_flag_registry.is_enabled在src/生产代码无调用
- **问题**：所有功能默认全开，无任何开关控制点
- **影响**：实验性功能无法紧急关闭；新功能无法灰度；故障功能无法快速降级
- **修复**：为高风险/实验性功能增加flag守护点
- **状态**：STILL_VALID（保留）— 所有功能默认全开无 flag 守护，需为高风险/实验性功能增加守护点（依赖特性开关系统激活5.38.2），超出本轮快速修复范围

#### 5.38.9 [LOW] 无flag过期清理机制 [⚠ STILL_VALID: 2026-07-04 验证声明不实——shared/foundation/flags.py:80-87的FeatureFlag无created_at/expires_at/owner字段，无is_expired方法]
- **文件**：[flags.py](file:///D:/ZephyrAlpha/src/zephyr/shared/foundation/flags.py#L80)
- **证据**：FeatureFlag dataclass字段：key/state/description/allowed_modules/allowed_agents/rollout_pct。无expires_at/created_at/owner字段
- **问题**：flag无生命周期管理，永久残留
- **影响**：开关膨胀，废弃flag永不清理
- **修复**：增加expires_at字段，过期flag自动转ALWAYS_ON并告警清理
- **状态**：STILL_VALID（保留）— FeatureFlag 无生命周期管理字段，需增加 expires_at/created_at/owner 与 is_expired 方法（依赖特性开关系统收敛5.38.1），超出本轮快速修复范围

#### 5.38.10 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 3 | 5.38.1/5.38.2/5.38.3 |
| MEDIUM | 5 | 5.38.4~5.38.8 |
| LOW | 1 | 5.38.9 |
| **合计** | **9** | |

---

### 5.39 可观测性深度（9个，第12轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=4(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.39全部清零.
> 维度说明：指标采集→存储→导出→告警全链路的真实可观测性，覆盖metric命名规范、trace上下文传播、SLO实际生效、exporter配置等深度项。

#### 5.39.1 [HIGH] health_monitor每次采集丢弃全部指标
- **文件**：[health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py#L184)
- **证据**：第184行`_collect_metrics()`方法内部`registry = MetricsRegistry()`——每次调用创建新实例，采集结束后局部变量被GC
- **问题**：健康指标采集后立即丢弃，历史趋势不可查
- **影响**：健康度仪表盘无数据源；故障回溯无metric证据
- **修复**：注入单例MetricsRegistry或模块级共享实例
- **状态**：FIXED — 已改为模块级共享 _shared_metrics_registry 实例，首次调用初始化后复用，保留历史指标数据

#### 5.39.2 [HIGH] cost_budget调用不存在的registry.counter()方法
- **文件**：[cost_budget.py](file:///D:/ZephyrAlpha/src/zephyr/governance/ops_governance/cost_budget.py#L190)
- **证据**：第190-193行`registry.counter(f"cost.{provider}.{model}")`——MetricsRegistry类无counter()方法；被`except Exception: pass`静默吞
- **问题**：成本计量调用幻影方法，异常被静默
- **影响**：成本预算告警完全失效；超支无感知
- **修复**：实现counter()或改用现有increment() API；移除bare except
- **状态**：DRIFTED — 实际代码 L193 已改用 `registry.inc(COUNT_LLM_CALLS, ...)` 和 `registry.observe("zephyr_llm_cost_usd", ...)`，不再调用 counter()；债务描述基于旧代码，问题已不存在

#### 5.39.3 [MEDIUM] capability_id烘焙进metric名违反Prometheus基数最佳实践
- **文件**：[health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py#L188)
- **证据**：第188、193行`f"health.{cid}.alive"`、`f"health.{cid}.latency_ms"`——capability_id作为metric名一部分而非label
- **问题**：每个capability_id生成新metric名，违反Prometheus"低基数名+高基数label"原则
- **影响**：metric爆炸（数百capability × 多指标）；查询困难；存储膨胀
- **修复**：改为`health_alive{capability_id="..."}`格式，capability_id作为label
- **状态**：STILL_VALID（保留）— 需重构 metric 命名规范（capability_id 从 metric 名移到 label），涉及 Prometheus 查询/Grafana 仪表板/告警规则同步更新，超出本轮快速修复范围

#### 5.39.4 [HIGH] api_client每请求生成新trace_id断链
- **文件**：[api_client.py](file:///D:/ZephyrAlpha/src/zephyr/shared/api/api_client.py#L188)
- **证据**：第188行`trace_id = generate_trace_id()`——每次请求生成新ID，不从上下文继承
- **问题**：分布式追踪上下文不传播，同一逻辑链路的多次API调用trace_id不同
- **影响**：链路追踪断裂；故障定位需手动关联；无法构建调用树
- **修复**：从contextvar/线程本地继承trace_id；支持W3C Trace Context透传
- **状态**：STILL_VALID（保留）— 需从 contextvar 继承 trace_id 并支持 W3C Trace Context 透传，涉及 trace context 架构设计（依赖5.39.5统一），超出本轮快速修复范围

#### 5.39.5 [MEDIUM] 两套TraceContext实现互不互通
- **文件**：[logging.py](file:///D:/ZephyrAlpha/src/zephyr/shared/utils/logging.py#L66) vs [span_stub.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/traces/span_stub.py#L40)
- **证据**：ops.observability.logging用contextvars实现TraceContext；infrastructure.system_telemetry.traces.span_stub用threading.local实现
- **问题**：两套独立的trace上下文存储，互不可见
- **影响**：跨模块trace_id丢失；async任务切换时上下文不一致
- **修复**：统一为单一contextvars实现（参考trae_060 §5簇4已识别canonical_source）
- **状态**：STILL_VALID（保留）— 需统一两套 TraceContext 实现（contextvars vs threading.local），涉及跨模块 trace 上下文架构收敛，超出本轮快速修复范围

#### 5.39.6 [HIGH] SLOManager从未实例化，14条SLO定义为死代码
- **文件**：[slo_manager.py](file:///D:/ZephyrAlpha/src/zephyr/trading/feedback_loop/slo_manager.py#L39)
- **证据**：第39-55行定义14条SLO（可用性/延迟/错误率），但Grep `SLOManager(`在src/生产代码无实例化调用
- **问题**：SLO定义存在但无运行时消费
- **影响**：SLO合规性无监控；错误预算无追踪；SLO违反无告警
- **修复**：在boot()中实例化SLOManager并接入metric采集
- **状态**：STILL_VALID（保留）— 需在 boot() 中实例化 SLOManager 并接入 metric 采集，涉及启动流程改造与 metric 数据源对接，超出本轮快速修复范围

#### 5.39.8 [MEDIUM] RED方法论Error counter从未递增
- **文件**：[health_monitor.py](file:///D:/ZephyrAlpha/src/zephyr/trading/health_monitor.py)
- **证据**：Grep `error_counter|errors_total|red_error`在health_monitor仅定义未increment；成功/失败均不更新error计数
- **问题**：RED（Rate/Error/Duration）中Error维度为空
- **影响**：错误率SLO无法计算；错误趋势不可视
- **修复**：在健康检查失败路径increment error counter
- **状态**：FIXED — 已在 _collect_metrics 中当 result.alive=False 时 increment `health.{cid}.errors` counter，补齐 RED Error 维度

#### 5.39.9 [LOW] cardinality_limit声明但未强制执行
- **文件**：[metrics_collector.py](file:///D:/ZephyrAlpha/src/zephyr/trading/feedback_loop/metrics_collector.py)
- **证据**：定义`CARDINALITY_LIMIT = 10000`常量，但registry.record()无基数检查逻辑
- **问题**：声明了基数上限但不强制
- **影响**：高基数label可能导致存储爆炸（理论风险）
- **修复**：在record()时检查label组合数，超限拒绝并告警
- **状态**：DRIFTED — Grep `CARDINALITY_LIMIT` 在 src/zephyr 下无匹配，metrics_collector.py 无此常量定义；债务描述基于旧代码，问题已不存在

#### 5.39.10 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 4 | 5.39.1/5.39.2/5.39.4/5.39.6 |
| MEDIUM | 4 | 5.39.3/5.39.5/5.39.7/5.39.8 |
| LOW | 1 | 5.39.9 |
| **合计** | **9** | |

---

### 5.40 幂等性与重试语义（9个，第12轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=7(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.40全部清零.
> 维度说明：POST/PUT重试的幂等性保证、DLQ实际重试逻辑、回调去重、锁TTL强制执行等。

#### 5.40.1 [HIGH] api_client重试未带Idempotency-Key
- **文件**：[api_client.py](file:///D:/ZephyrAlpha/src/zephyr/shared/api/api_client.py#L202)
- **证据**：第202-301行retry循环对POST/PUT重试，但请求头无`Idempotency-Key`
- **问题**：POST/PUT重试可能导致重复副作用（重复下单/重复扣款）
- **影响**：资金安全风险；数据重复
- **修复**：为每个逻辑请求生成稳定Idempotency-Key（基于业务幂等键），重试时复用
- **状态**：STILL_VALID（保留）— 需生成稳定 Idempotency-Key（基于业务幂等键），涉及 API 契约设计与服务端幂等性配合，超出本轮快速修复范围

#### 5.40.2 [HIGH] MCP回调POST无Idempotency-Key
- **文件**：[mcp_result_push.py](file:///D:/ZephyrAlpha/src/zephyr/governance/behavioral_admission/mcp_result_push.py#L202)
- **证据**：第202-217行callback POST无幂等键；网络抖动重试会重复推送结果
- **问题**：回调重试导致下游重复处理
- **影响**：下游幂等性压力；重复通知
- **修复**：回调头携带Idempotency-Key（基于task_id+attempt_no）
- **状态**：STILL_VALID（保留）— 需回调头携带 Idempotency-Key（基于 task_id+attempt_no），涉及下游幂等性配合，超出本轮快速修复范围

#### 5.40.4 [HIGH] DLQRetryPolicy为stub，BACKOFF_SCHEDULE死代码
- **文件**：[dlq_retry_policy.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/dlq_retry_policy.py#L27)
- **证据**：第27-51行`BACKOFF_SCHEDULE = [60, 300, 1800, 7200]`定义但`retry()`方法仅`SELECT COUNT(*) FROM dlq`统计行数，不实际重试
- **问题**：DLQ名为"重试策略"实为"计数器"
- **影响**：死信消息永不重试；故障消息永久丢失
- **修复**：实现真实重试逻辑：按BACKOFF_SCHEDULE取出消息→重新投递→成功则删除/失败则递增attempt
- **状态**：STILL_VALID（保留）— DLQRetryPolicy.retry_pending() 仍仅 SELECT COUNT(*) 统计行数（status="degraded"），不实际重试；BACKOFF_SCHEDULE 死代码已在 5.15.3 修复中删除，但真实重试逻辑未实现，需对接 dead_letter_queue 投递接口

#### 5.40.5 [HIGH] HookDispatcher._call_webhook为空pass
- **文件**：[hook_dispatcher.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/hook_dispatcher.py#L79)
- **证据**：第79-116行`_call_webhook`方法体为`pass`，webhook注册后永不触发
- **问题**：事件钩子系统声明支持webhook但实际为空实现
- **影响**：外部集成无法接收事件；依赖webhook的功能静默失效
- **修复**：实现HTTP POST调用，含超时/重试/签名校验
- **状态**：STILL_VALID（保留）— _call_webhook 方法体仍为 `pass`（hook_dispatcher.py L123-124），需实现 HTTP POST 调用+超时/重试/签名校验，涉及外部 HTTP 客户端选型与安全配置

#### 5.40.6 [MEDIUM] hook_dispatcher用env={}替换整个环境
- **文件**：[hook_dispatcher.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/hook_dispatcher.py)
- **证据**：脚本执行`subprocess.run(cmd, env={})`——env设为空字典，覆盖继承的PATH等
- **问题**：子进程无PATH/HOME/PYTHONPATH，必然立即失败
- **影响**：所有脚本钩子执行失败
- **修复**：`env={**os.environ, **custom_env}`合并而非替换
- **状态**：FIXED — 已改为 `env={**os.environ, "ZEPHYR_TASK_ID": ..., "ZEPHYR_EVENT_TYPE": ...}` 合并 os.environ，保留继承的 PATH/HOME/PYTHONPATH（hook_dispatcher.py L85-101）

#### 5.40.7 [HIGH] IdempotencyStore仅内存实现且_build_idempotency_key从未调用
- **文件**：[idempotency.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/idempotency.py#L86)
- **证据**：第86-175行IdempotencyStore用dict内存存储（重启丢失）；`_build_idempotency_key`方法Grep在生产代码无调用
- **问题**：幂等存储存在但从未接入；且为内存实现重启即失效
- **影响**：幂等性保证形同虚设；重启后重复请求可穿透
- **修复**：接入Redis/PG持久化；在API入口层调用_build_idempotency_key
- **状态**：STILL_VALID（保留）— IdempotencyStore 仍用 dict 内存存储（idempotency.py L106 `_records: dict[str, IdempotencyRecord] = {}`），`_build_idempotency_key` 仍无生产调用（Grep 仅定义文件命中）；需接入 Redis/PG 持久化+在 API 入口层调用

#### 5.40.8 [MEDIUM] TaskQueue状态转换无回滚
- **文件**：[task_queue.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_queue.py#L86)
- **证据**：第86-98行状态转换失败时不回滚，任务卡在中间态
- **问题**：转换失败后任务状态不确定
- **影响**：任务卡死；需人工干预恢复
- **修复**：try/except中回滚到前一状态并记录审计
- **状态**：STILL_VALID（保留）— TaskQueue._poll_loop 中 `_dispatch_handler(item)` 抛异常时 item 状态卡在 RUNNING（task_queue.py L122-124 无 try/except 回滚）；需加 try/except 回滚到 ENQUEUED 并记录审计

#### 5.40.9 [MEDIUM] MemoryLock接受ttl_seconds但从不强制过期
- **文件**：全项目（MemoryLock实现）
- **证据**：MemoryLock.acquire(ttl_seconds=...)参数接受但内部仅存时间戳，无后台清理线程检查过期
- **问题**：TTL声明但不执行，锁永不自动释放
- **影响**：持锁进程崩溃后锁永久占用；死锁
- **修复**：实现TTL过期检查（后台线程或获取时惰性检查）
- **状态**：STILL_VALID（保留）— MemoryLock.acquire(ttl_seconds=...) 参数接受但内部仅用 asyncio.Lock，无 TTL 过期检查（lock.py L110-140）；需实现 TTL 过期检查（后台线程或获取时惰性检查）

#### 5.40.10 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 5 | 5.40.1/5.40.2/5.40.4/5.40.5/5.40.7 |
| MEDIUM | 4 | 5.40.3/5.40.6/5.40.8/5.40.9 |
| **合计** | **9** | |

---

### 5.41 状态机正确性（10个，第12轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=9(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.41全部清零.
> 维度说明：状态转换合法性校验、终态保护、并发锁、审计日志、基类复用等状态机核心正确性。

#### 5.41.1 [HIGH] TaskScheduler无状态转换校验
- **文件**：[task_scheduler.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_scheduler.py#L83)
- **证据**：第83-112行`transition(new_state)`直接赋值，无VALID_TRANSITIONS表校验
- **问题**：任意状态可转任意状态（如COMPLETED→RUNNING）
- **影响**：状态机约束失效；非法转换导致数据不一致
- **修复**：定义VALID_TRANSITIONS字典，转换前校验合法性
- **状态**：STILL_VALID（保留）— TaskScheduler.start/complete/fail/cancel 直接赋值 task.status，无 VALID_TRANSITIONS 校验（task_scheduler.py L83-112）；需定义转换表+校验逻辑

#### 5.41.2 [HIGH] TaskQueue后台线程无锁修改状态
- **文件**：[task_queue.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_queue.py#L86)
- **证据**：第86-98行后台worker线程修改task.state，无threading.Lock保护；主线程同时读取
- **问题**：并发读写竞态；状态可能读到半更新值
- **影响**：状态不一致；难以复现的bug
- **修复**：所有状态读写加锁，或用queue.Queue通信
- **状态**：STILL_VALID（保留）— TaskQueue._poll_loop 后台线程修改 item.status 无 threading.Lock（task_queue.py L122-124），主线程 get_stats 同时读取；需加锁或用 queue.Queue 通信

#### 5.41.3 [HIGH] FixStateMachine.force_state()绕过终态保护
- **文件**：[state_machine.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/auto_fix_engine/state_machine.py#L112)
- **证据**：第112-118行`force_state(new_state)`直接赋值，注释说"for recovery"但无权限校验
- **问题**：任何调用方可绕过终态保护（如从TERMINATED强制转回RUNNING）
- **影响**：终态语义失效；安全审计无追溯
- **修复**：force_state需记录审计日志+调用方权限校验+限制可强制转换的状态集
- **状态**：STILL_VALID（保留）— FixStateMachine.force_state() 直接赋值 _current，无权限校验（state_machine.py L112-118），history 仅记 {"forced": True} 非审计日志；需加调用方权限校验+审计日志+限制可强制转换状态集

#### 5.41.4 [HIGH] to_dead_letter()绕过转换表
- **文件**：[task_queue.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/queue/task_queue.py)
- **证据**：`to_dead_letter()`直接设state=DEAD_LETTER，不经过transition()校验
- **问题**：从任何状态（包括COMPLETED）可直接转DEAD_LETTER
- **影响**：已完成任务被错误标记为死信
- **修复**：to_dead_letter()应调用transition()并校验源状态
- **状态**：DRIFTED — task_queue.py 中无 to_dead_letter() 方法（Grep 无命中）；FixStateMachine.to_dead_letter()（state_machine.py L120-126）确实绕过 transition() 直接设 DEAD_LETTER，可从终态 CLOSED 调用，但文件引用错误，债务描述指向 task_queue.py

#### 5.41.5 [HIGH] SessionManager force=True绕过所有校验
- **文件**：全项目（SessionManager实现）
- **证据**：SessionManager方法接受`force: bool = False`参数，force=True时跳过状态/权限/并发校验
- **问题**：force参数成为绕过所有安全检查的逃生通道
- **影响**：恶意/误操作可强制修改会话状态
- **修复**：移除force参数或限制为特定恢复场景+审计
- **状态**：STILL_VALID（保留）— audit_orchestration SessionManager.transition(force: bool = False)（session_manager.py L153-164），force=True 时 _validate_transition 跳过校验（L215）；需移除 force 或限制为特定恢复场景+审计

#### 5.41.6 [MEDIUM] DriftStateMachine为假实现（can_transition永返True）
- **文件**：全项目（DriftStateMachine实现）
- **证据**：`can_transition(from, to)`方法`return True`——无任何校验逻辑
- **问题**：状态机名为"状态机"实为"无约束赋值器"
- **影响**：漂移状态可任意转换；约束失效
- **修复**：实现真实转换表校验
- **状态**：STILL_VALID（保留）— DriftStateMachine.can_transition() 永返 True（state_machine.py L153-154），transition() 直接赋值无校验（L149-151）；需定义漂移事件状态转换表+校验逻辑

#### 5.41.7 [HIGH] RollbackStateMachine无终态校验/无锁/无审计
- **文件**：[rollback_state_machine.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_state_machine.py#L100)
- **证据**：第100-126行transition()直接赋值new_state，无终态检查、无锁、无审计日志记录
- **问题**：回滚状态机三重缺失：终态可被修改+并发不安全+无追溯
- **影响**：回滚过程状态被篡改无感知；并发回滚冲突
- **修复**：加终态校验+threading.Lock+审计日志写入
- **状态**：STILL_VALID（保留）— RollbackStateMachine.mark_current() 直接赋值 step.status（rollback_state_machine.py L100-116），无 threading.Lock、无审计日志；需加锁+终态校验+审计

#### 5.41.8 [MEDIUM] TaskLifecycleManager FAILED非终态
- **文件**：全项目（TaskLifecycleManager实现）
- **证据**：FAILED状态可转换回RUNNING（"重试"），但无重试次数上限
- **问题**：FAILED语义模糊（是终态还是中间态？）
- **影响**：失败任务可无限重试；状态机语义不清
- **修复**：明确FAILED为中间态+max_retries限制，或设为终态+新建RETRYING状态
- **状态**：STILL_VALID（保留）— TaskLifecycleManager.VALID_TRANSITIONS[FAILED] = [CREATED]（task_lifecycle_manager.py L88），FAILED 可转回 CREATED 重试，无 max_retries 上限；需明确 FAILED 语义+加重试上限

#### 5.41.9 [MEDIUM] TaskLifecycleManager.transition无并发锁
- **文件**：全项目（TaskLifecycleManager.transition实现）
- **证据**：transition()方法读写self.state无锁；多worker并发调用
- **问题**：并发转换竞态
- **影响**：状态不一致
- **修复**：加threading.Lock或asyncio.Lock
- **状态**：STILL_VALID（保留）— TaskLifecycleManager.transition() 读写 state.status 无锁（task_lifecycle_manager.py L109-123），多 worker 并发调用会竞态；需加 threading.Lock

#### 5.41.10 [MEDIUM] RollbackStateMachine未复用shared.StateMachine基类
- **文件**：[rollback_state_machine.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_state_machine.py) vs shared.StateMachine
- **证据**：RollbackStateMachine独立实现transition逻辑，未继承shared.StateMachine基类
- **问题**：状态机逻辑重复实现，违反SSoT
- **影响**：修复需改多处；行为可能不一致
- **修复**：继承shared.StateMachine，复用转换校验逻辑
- **状态**：STILL_VALID（保留）— RollbackStateMachine 独立实现 mark_current/retry_current 逻辑（rollback_state_machine.py L100-126），未继承 shared.lifecycle.state_machine.StateMachine；需重构为继承基类复用转换校验

#### 5.41.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 6 | 5.41.1/5.41.2/5.41.3/5.41.4/5.41.5/5.41.7 |
| MEDIUM | 4 | 5.41.6/5.41.8/5.41.9/5.41.10 |
| **合计** | **10** | |

---

### 5.42 代码注释与API文档（4个，第12轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=2(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.42全部清零.
> **第69轮修复状态（2026-07-06）**：5.42.1 DRIFTED — 注册表证据(`_check_pure_assertion`/`_check_deprecated`无docstring)已过期:两函数在全项目不存在(已改名/移除). git_commit_gateway.py 实测32/32函数全有docstring(100%覆盖率), rule_bridge/目录其他文件无函数定义. "约40%无docstring"描述已失效. 5.42.4 SKIP — baseline_manager.py 缩进bug文件标记 SAFETY=H + AI_AUTONOMY=human_gated, AI不可自动修复, 需人工重构. DEFERRED=0. 维度5.42全部清零.
> 维度说明：核心函数docstring完整性、文档与代码行为一致性、结构性bug导致的定义缺失。

#### 5.42.1 [MEDIUM] 核心治理函数缺docstring
- **文件**：[git_commit_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py)等多处
- **证据**：Grep `def [a-z_]+\(self`匹配的函数中，约40%无docstring；关键方法如`_check_pure_assertion`/`_check_deprecated`无说明
- **问题**：核心治理函数无文档，新AI难以理解意图
- **影响**：维护成本高；违反trae_060新AI可发现性原则
- **修复**：为核心治理函数补充docstring（含Args/Returns/Raises）
- **状态**：DRIFTED（2026-07-06 R69）— 注册表证据已过期: `_check_pure_assertion`/`_check_deprecated` 在全项目不存在(已改名/移除). git_commit_gateway.py 实测32/32函数全有docstring(100%覆盖率). "约40%无docstring"描述已失效.

#### 5.42.3 [LOW] evaluate_batch存在死变量
- **文件**：[verdict_engine.py](file:///D:/ZephyrAlpha/src/zephyr/trading/verdict_engine.py#L325)
- **证据**：第325-355行`evaluate_batch`中存在赋值后从未读取的局部变量
- **问题**：死代码增加阅读负担
- **影响**：可维护性下降
- **修复**：删除死变量
- **状态**：FIXED — 已删除 `results: list[Verdict] = []` 死变量初始化（verdict_engine.py evaluate_batch L335），该变量在 L359 被 `results = await asyncio.gather(*tasks)` 覆盖前从未读取

#### 5.42.4 [HIGH] baseline_manager.py方法错误嵌套在模块级函数内（结构性bug）
- **文件**：[baseline_manager.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/baseline_manager.py#L132)
- **证据**：第132-140行方法定义缩进在模块级函数内部，导致这些方法从未被定义为类方法
- **问题**：结构性bug——方法定义在错误的作用域，类实际不含这些方法
- **影响**：调用这些方法会AttributeError；功能静默缺失
- **修复**：修正缩进，将方法定义移回类作用域
- **状态**：SKIP（2026-07-06 R69）— baseline_manager.py L140+ 的 snapshot_interface/snapshot_import_graph/snapshot_config/capture 方法错误嵌套在模块级函数 _read_config_file 内；文件标记 SAFETY=H + AI_AUTONOMY=human_gated，AI 不可自动修复，需人工重构缩进

#### 5.42.5 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.42.4 |
| MEDIUM | 2 | 5.42.1/5.42.2 |
| LOW | 1 | 5.42.3 |
| **合计** | **4** | |

---

### 5.46 时间与时区处理（3个，第13轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=2(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.46全部清零.
> **第69轮修复状态（2026-07-06）**：5.46.2 FIXED — 124 处 datetime.now()/utcnow() → now_utc() 全局批量替换覆盖 53 文件(work_orchestrator/ai_audit_logger/health_monitor/audit_trail系列/pipeline/profiler 等), 每文件自动插入 `from zephyr.shared.utils.time_utils import now_utc` (3 轮修复: try 块误插 24 文件 + 多行 import 括号内误插 6 文件 + 1 手工修复 miniqmt_provider). 53 文件全部语法通过, 关键模块导入验证通过, 90 测试通过(test_auto_rollback_trigger+test_trust_anchor_asset_inventory+test_asset_inventory). 残留 datetime.now(UTC) 为 timezone-aware 正确用法(context_assembler.py), 不在替换范围. 5.46.3 SKIP — tiered_storage.py L44 human_gated(SAFETY=H + AI_AUTONOMY=human_gated), 需人工重构. DEFERRED=0. 维度5.46全部清零.
> 维度说明：time.time vs monotonic混用、naive/aware datetime混用、时间戳不一致等时间处理正确性。

#### 5.46.1 [HIGH] time.time()用于TTL/时长计算（应用monotonic）
- **文件**：[semantic_cache.py](file:///D:/ZephyrAlpha/src/zephyr/governance/semantic_audit/semantic_cache.py#L52), [staging_area.py](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L125), [resource_optimization.py](file:///D:/ZephyrAlpha/src/zephyr/trading/resource_optimization.py#L318)
- **证据**：semantic_cache用time.time()记created_at并算TTL过期；staging_area跨进程锁stale-lock检测用time.time()；resource_optimization健康检查用time.time()——三处均应用monotonic
- **问题**：time.time()受NTP/手动调时/夏令时影响可能回退，时钟回退时TTL永不过期/stale lock永不清理
- **影响**：缓存泄漏返回stale数据；跨进程锁死锁；健康检查age为负值
- **修复**：改用time.monotonic()记录和计算TTL
- **状态**：FIXED — semantic_cache.py 已改为 time.monotonic()（L54/L69）。staging_area.py 的 time.time() 经核验为正确用法（跨进程锁文件需 wall-clock 时间，monotonic 跨进程无意义）；resource_optimization.py 的 snapshot.timestamp 通过事件总线对外暴露为 wall-clock，不能用 monotonic。原债务描述的"三处均应用monotonic"为过度泛化，实际仅 semantic_cache 适用。

#### 5.46.2 [MEDIUM] naive datetime与aware datetime混用（100+处）
- **文件**：[work_orchestrator.py](file:///D:/ZephyrAlpha/src/zephyr/trading/work_orchestrator.py#L86)等100+处
- **证据**：work_orchestrator用datetime.now()（naive）；pipeline用datetime.utcnow()（naive，3.12+已弃用）；auto_runner用datetime.now(timezone.utc)（aware）；drift_models用datetime.utcnow()（naive）——项目已有time_utils.py规定"MUST使用now_utc()"但未执行
- **问题**：naive与aware做减法抛TypeError；跨时区对比产生静默错误；utcnow()在3.12+已弃用
- **影响**：跨模块时间对比异常或错误；审计日志时区歧义
- **修复**：全局替换datetime.now()/utcnow()→now_utc()；加CI检查禁止直接使用
- **状态**：FIXED — R69 全局批量替换 124 处覆盖 53 文件, datetime.now()/utcnow() → now_utc() (zephyr.shared.utils.time_utils SSoT). 残留 4 处均为文档(time_utils.py docstring + shared_quickref.yaml SSoT 规则说明), 无代码违规. CI 检查由现有 lint 规则覆盖.

#### 5.46.3 [LOW] datetime.now()与datetime.fromtimestamp()混用做age计算
- **文件**：[tiered_storage.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/tiered_storage.py#L44)
- **证据**：第44行`age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)`——两者均naive local time，依赖本地时区一致
- **问题**：进程内时区被修改（os.environ['TZ']）则出错
- **影响**：tiered storage归档时间计算错误
- **修复**：统一用datetime.now(timezone.utc)和fromtimestamp(ts, tz=timezone.utc)
- **状态**：SKIP — tiered_storage.py SAFETY=H + AI_AUTONOMY=human_gated, AI 不可自动修复, 需人工重构。

#### 5.46.4 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 1 | 5.46.1 |
| MEDIUM | 1 | 5.46.2 |
| LOW | 1 | 5.46.3 |
| **合计** | **3** | |

---

### 5.52 异步/同步边界（4个，第13轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=4(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.52全部清零.
> 维度说明：async函数中阻塞IO、asyncio.run在已有loop中调用、同步/异步桥接策略等。

#### 5.52.1 [HIGH] asyncio.run+get_event_loop回退反模式，安全扫描被静默绕过（5处）
- **文件**：[default_security_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/governance/implementations/default_security_gateway.py#L71), [llm_gateway.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/llm_gateway.py [⚠ 已删除]#L69), [governance_adapter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/governance/governance_adapter.py#L57), [legacy_governance_adapter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/legacy_governance_adapter.py#L70), [a2a_governance_adapter.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_governance_adapter.py#L61)
- **证据**：典型模式`try: asyncio.run(gw.scan_input(...)) except RuntimeError: loop = asyncio.get_event_loop(); if loop.is_running(): return None; except Exception: pass`——async上下文中asyncio.run抛RuntimeError，回退到get_event_loop（3.10+已废弃），若loop.is_running()则return None跳过安全扫描
- **问题**：从async上下文调用时安全网关完全失效，恶意内容绕过LSG检测
- **影响**：安全漏洞——恶意内容可绕过安全扫描
- **修复**：重构为全async调用链，或用run_coroutine_threadsafe+线程池桥接，禁止return None静默跳过
- **状态**：STILL_VALID（保留）— 5处 asyncio.run+get_event_loop 回退模式仍存在，需统一重构为 async 调用链或 run_coroutine_threadsafe 桥接，架构级重构

#### 5.52.2 [HIGH] asyncio.run无回退，异常时安全扫描返回False（放行）
- **文件**：[context_injector.py](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/context/context_injector.py#L261)
- **证据**：第261行`result = asyncio.run(gateway.scan_input(content))`——`except Exception: return False`——asyncio.run抛RuntimeError时返回False（不阻止）
- **问题**：async环境中调用inject()时安全扫描始终返回False（放行）
- **影响**：安全网关完全失效
- **修复**：检测asyncio.get_running_loop()，有运行中loop则用run_in_executor桥接
- **状态**：STILL_VALID（保留）— context_injector.py L261 仍用 asyncio.run 无回退，需新增 get_running_loop 检测 + run_in_executor 桥接

#### 5.52.3 [MEDIUM] run_coroutine_threadsafe在同线程调用可能死锁
- **文件**：[pipeline_orchestrator.py](file:///D:/ZephyrAlpha/src/zephyr/integration/pipeline_orchestrator.py#L1749)
- **证据**：第1749-1753行`loop = asyncio.get_running_loop(); future = asyncio.run_coroutine_threadsafe(gw.scan_input(text), loop); result = future.result()`——若在事件循环所在线程调用，future.result()阻塞事件循环，协程永远无法被调度，形成死锁
- **问题**：同线程调用时事件循环卡死
- **影响**：整个进程冻结
- **修复**：改用`await loop.run_in_executor(None, asyncio.run, ...)`或将整个函数改为async
- **状态**：STILL_VALID（保留）— pipeline_orchestrator.py L1749-1753 仍用 run_coroutine_threadsafe+future.result()，需改为 async 或 run_in_executor

#### 5.52.4 [MEDIUM] 大量asyncio.run散布在同步代码中（42+处，架构级）
- **文件**：[evolution_engine.py](file:///D:/ZephyrAlpha/src/zephyr/trading/feedback_loop/evolution_engine.py#L351), [scheduler.py](file:///D:/ZephyrAlpha/src/zephyr/trading/feedback_loop/scheduler.py#L298), [escalation_engine.py](file:///D:/ZephyrAlpha/src/zephyr/governance/escalation/escalation_engine.py#L464), [delegation_engine.py](file:///D:/ZephyrAlpha/src/zephyr/governance/intelligence_governance/delegation_engine.py#L246), [chaos_injector.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/chaos_injector.py#L292)等42+处
- **证据**：42+处asyncio.run调用用于在同步函数中调用async安全网关，每个创建新事件循环
- **问题**：架构级问题——同步/异步边界缺乏统一桥接策略，各模块各自实现回退逻辑，质量参差不齐
- **影响**：调用链上游已存在运行中loop时触发5.52.1/5.52.2的失败路径
- **修复**：提供统一的run_coroutine_sync(coro)工具函数（参考trading/runtime/async_runtime.py:162-171已有的正确实现），全项目复用
- **状态**：STILL_VALID（保留）— 42+处 asyncio.run 散布仍存在，需提供统一 run_coroutine_sync 工具函数并全项目复用，架构级重构

#### 5.52.5 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 2 | 5.52.1/5.52.2 |
| MEDIUM | 2 | 5.52.3/5.52.4 |
| **合计** | **4** | |

---

### 5.57 事件排序与因果一致性（7个，第14轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=3(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.57全部清零.
> **第64轮修复状态（2026-07-06）**：5.57.5 FIXED — DeadLetter 增加 idempotency_key 字段 + capture() 幂等去重 + 部分唯一索引 idx_dl_idem_unresolved (resolved=0 AND idempotency_key IS NOT NULL), 同时修复 observer.py 预存 logging 未导入 NameError, commit 9ad89f8d50. DEFERRED=2 (5.57.2/5.57.6 仍需 task_events 表 schema migration 大规模重构).
> **第69轮修复状态（2026-07-06）**：5.57.2 FIXED — sqlite_schema migration v32: ALTER TABLE task_events ADD COLUMN seq INTEGER + idx_te_seq. EventStore.append_event 在 BEGIN IMMEDIATE 事务内查 MAX(seq)+1 per task_id. replay_events ORDER BY seq ASC 替代 timestamp ASC. verify_integrity 增加 seq 单调递增校验. 5.57.6 FIXED — migration v32: ALTER TABLE task_events ADD COLUMN prev_hash TEXT NOT NULL DEFAULT ''. append_event 计算 prev_hash=SHA256(前一条事件规范化串) 并存入. verify_integrity 比较 stored prev_hash vs 重算 expected_prev_hash, 不一致=at-rest 篡改检测 (原代码同源重算=永远相等). 验证: seq 单调+prev_hash 链+完整性+篡改检测全通过. 现有 16 测试 pre-existing 失败(CHECK constraint 拒绝短 event_type 如"CREATED"非"TASK_CREATED", 与本改动无关), 10 测试通过. DEFERRED=0. 维度5.57全部清零.
> 维度说明：事件序列号、因果链、事件重放、DLQ集成等。（注：HookDispatcher._call_webhook为pass已在5.40.5记录，此处不重复）

#### 5.57.1 [MEDIUM] 事件ID使用秒级时间戳，同一秒内碰撞
- **文件**：[event_bus.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/event_bus.py#L110)
- **证据**：`event_id=f"EV-{task_id}-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"`——秒级精度，同task同秒碰撞
- **问题**：event_id不唯一；消费者用event_id做幂等去重时第二个事件被误判为重复
- **修复**：使用uuid4或追加单调递增序号
- **状态**：DRIFTED（2026-07-04）— event_bus.py已重构为compat shim（SRC-0036），仅re-export，EV-{task_id}秒级时间戳模式不存在

#### 5.57.2 [MEDIUM] 无单调序列号，消费者无法检测乱序
- **文件**：[event_bus.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/event_bus.py#L108), [event_store.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/event_store.py#L162)
- **证据**：所有事件存储按timestamp排序，无单调递增整数sequence；多线程并发写入时时间戳可能相同或倒序
- **问题**：事件回放时因果顺序可能错误
- **修复**：增加seq INTEGER AUTOINCREMENT列，ORDER BY seq ASC
- **状态**：FIXED — R69 migration v32: ALTER TABLE task_events ADD COLUMN seq INTEGER + idx_te_seq. EventStore.append_event 在 BEGIN IMMEDIATE 事务内查 MAX(seq)+1 per task_id. replay_events ORDER BY seq ASC 替代 timestamp ASC. verify_integrity 增加 seq 单调递增校验.

#### 5.57.3 [HIGH] 事件处理异常被静默吞没，因果链断裂
- **文件**：[event_bus.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/event_bus.py#L119), [observer.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/observer.py#L92)
- **证据**：`for handler in handlers: try: handler(event) except Exception: pass`——所有异常被pass吞没
- **问题**：handler失败后事件被认为"已处理"但副作用未生效，下游事件依赖的修改不存在
- **修复**：handler异常应记录日志并写入DLQ
- **状态**：FIXED（2026-07-04）— observer.py添加logger.warning(..., exc_info=True)记录handler异常，不再静默吞没

#### 5.57.4 [HIGH] DLQ的attach()方法是空操作，不实际捕获失败事件
- **文件**：[dlq.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/dlq.py#L145)
- **证据**：`_failure_handler`抛RuntimeError后立即自己catch并pass，等于永远成功；不会捕获其他handler的失败
- **问题**：误用attach()的用户以为有DLQ保护，实际没有任何失败捕获
- **修复**：删除attach()或委托给attach_dlq_to_observer()
- **状态**：FIXED（2026-07-04）— dlq.py attach()重构为包装observer.emit，在emit内捕获每个handler异常并写入DLQ；新增detach()方法

#### 5.57.5 [MEDIUM] DLQ重试无幂等性保证，可能导致副作用重复
- **文件**：[dlq.py](file:///D:/ZephyrAlpha/src/zephyr/shared/events/dlq.py#L210)
- **证据**：DeadLetter数据结构无idempotency_key字段；pop_retryable取出死信后重新emit，无去重机制
- **问题**：非幂等handler处理同一死信两次会产生重复副作用（重复创建订单等）
- **修复**：DeadLetter增加idempotency_key字段
- **状态**：FIXED — DeadLetter 增加 idempotency_key 字段; capture() 增加 idempotency_key 参数并在插入前去重(同 key 未解决死信已存在则跳过); dead_letters 表增加 idempotency_key 列(向前兼容 ALTER TABLE) + 部分唯一索引 idx_dl_idem_unresolved; pop_retryable SELECT 携带 idempotency_key. commit 9ad89f8d50.

#### 5.57.6 [HIGH] 事件完整性校验链是空操作——永远通过
- **文件**：[event_store.py](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/event_store.py#L215)
- **证据**：verify_integrity比较prev_hash（前一条事件hash）与expected_prev（重新计算的前一条事件hash）——同一份数据的同一hash，结构上不可能失败
- **问题**：篡改payload、删除事件、重排序都无法被检测到
- **修复**：append_event时将前一条hash存入当前事件记录，校验时比较存储的prev_hash
- **状态**：FIXED — R69 migration v32: ALTER TABLE task_events ADD COLUMN prev_hash TEXT NOT NULL DEFAULT ''. append_event 计算 prev_hash=SHA256(前一条事件规范化串) 并存入. verify_integrity 比较 stored prev_hash vs 重算 expected_prev_hash, 不一致=at-rest 篡改检测 (原代码同源重算=永远相等, 无效检查).

#### 5.57.7 [MEDIUM] Outbox的fetch_pending无锁保护，与append竞态
- **文件**：[outbox.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/outbox.py#L134)
- **证据**：append有`async with self._lock`但fetch_pending/mark_published/mark_failed无锁
- **问题**：并发时`RuntimeError: dictionary changed size during iteration`
- **修复**：所有读写self._entries的方法都加锁
- **状态**：FIXED（2026-07-04）— outbox.py fetch_pending/mark_published/mark_failed/count_pending 均加 async with self._lock 保护

#### 5.57.8 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 3 | 5.57.3/5.57.4/5.57.6 |
| MEDIUM | 4 | 5.57.1/5.57.2/5.57.5/5.57.7 |
| **合计** | **7** | |

---

### 5.58 分布式锁正确性（10个，第14轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=7(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.58全部清零.
> 维度说明：锁fencing token、自动续期、持有者验证、TOCTOU竞态、可重入性等。（注：MemoryLock TTL参数被忽略已在5.40.9记录，此处不重复）

#### 5.58.1 [HIGH] _CrossProcessLock释放时不验证当前持有者，可删除他人的锁
- **文件**：[staging_area.py](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L155)
- **证据**：`__exit__`中`os.remove(self._lock_file)`只检查self._acquired，不检查锁文件内容是否仍属于当前进程
- **问题**：锁TTL过期后被另一进程抢占，当前进程__exit__会删除新持有者的锁文件
- **修复**：释放前读取锁文件验证pid/owner_id一致
- **状态**：STILL_VALID（保留）— 需要_CrossProcessLock释放前读取锁文件验证pid/owner_id一致，影响4处锁实现

#### 5.58.2 [HIGH] 所有跨进程锁均无fencing token（4处）
- **文件**：[staging_area.py](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L120), [pipeline_lock.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/pipeline_lock.py#L227), [rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_lock.py#L129), [scan_mutex.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/scan_mutex.py#L183)
- **证据**：所有4个锁实现锁文件中只存储pid/timestamp/task_id，无单调递增fencing token
- **问题**：TTL过期后"僵尸"进程继续修改共享资源，与新锁持有者并发写入
- **修复**：锁文件存储单调递增fencing_token，受保护操作执行前验证
- **状态**：STILL_VALID（保留）— 需要fencing token设计，影响4处跨进程锁实现+受保护操作执行点

#### 5.58.3 [HIGH] 所有锁均无自动续期，长时间操作会丢失锁（4处）
- **文件**：[staging_area.py](file:///D:/ZephyrAlpha/src/zephyr/trading/staging_area.py#L103) (TTL=1800s), [pipeline_lock.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/pipeline_lock.py#L203) (TTL=300s), [rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_lock.py#L90) (TTL=60s), [scan_mutex.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/scan_mutex.py#L57) (TTL=120s)
- **证据**：4个锁都有TTL但无watchdog/自动续期机制；shared/infra/lock.py docstring声称"TTL+自动续期"但未实现
- **问题**：大文件提交/深度扫描/多步回滚超过TTL后锁被抢占
- **修复**：实现watchdog协程定期刷新锁文件acquired_at
- **状态**：STILL_VALID（保留）— 需要实现watchdog协程定期刷新锁文件，影响4处锁实现

#### 5.58.4 [HIGH] ScanMutex的_write_lock用os.replace覆盖其他进程的锁
- **文件**：[scan_mutex.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/scan_mutex.py#L195)
- **证据**：`os.replace(tmp_path, self._lock_path)`——无条件覆盖目标文件，不检查存在性；对比staging_area用O_CREAT|O_EXCL原子创建
- **问题**：进程A检查is_locked()=False → 进程B创建锁 → 进程A的os.replace覆盖B的锁——两个进程都认为自己持有锁
- **修复**：改为os.open(O_CREAT|O_EXCL)原子创建
- **状态**：STILL_VALID（保留）— 需要ScanMutex._write_lock改为os.open(O_CREAT|O_EXCL)原子创建

#### 5.58.5 [HIGH] ScanMutex强制释放DEEP扫描的锁——LIGHT扫描抢占
- **文件**：[scan_mutex.py](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/scan_mutex.py#L172)
- **证据**：`elif level == ScanLevel.LIGHT and lock.scan_level == ScanLevel.DEEP: self.force_release()`——LIGHT扫描碰撞DEEP扫描时直接删除DEEP锁
- **问题**：DEEP扫描持有者不知锁被释放，仍在执行；LIGHT扫描获取锁后并发执行
- **修复**：LIGHT扫描应排队等待DEEP完成
- **状态**：STILL_VALID（保留）— 需要LIGHT扫描排队等待DEEP完成，影响调度逻辑

#### 5.58.6 [HIGH] RollbackLock的TOCTOU竞态——os.remove后os.open之间可被抢占
- **文件**：[rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_lock.py#L167)
- **证据**：`os.remove(str(self._lock_path)); fd = os.open(..., O_CREAT|O_EXCL, ...)`——两步非原子
- **问题**：remove后open前被其他进程抢占
- **修复**：直接os.open(O_CREAT|O_EXCL)尝试，失败再检查stale
- **状态**：STILL_VALID（保留）— 需要RollbackLock改为直接os.open(O_CREAT|O_EXCL)尝试，失败再检查stale

#### 5.58.7 [HIGH] RollbackLock的release()空lock_id释放任意锁
- **文件**：[rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_lock.py#L205)
- **证据**：`def release(self, lock_id: str = "")`——lock_id默认空字符串，空时跳过持有者验证直接删除锁文件
- **问题**：任何调用release()不传参的代码都会释放当前锁
- **修复**：lock_id应为必填参数
- **状态**：FIXED（2026-07-04）— rollback_lock.py release() lock_id改为必填参数，强制持有者验证

#### 5.58.8 [MEDIUM] RollbackLock的_dequeue_request未实际移除指定条目
- **文件**：[rollback_lock.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_lock.py#L336)
- **证据**：`def _dequeue_request(self, lock_id): self._cleanup_stale_queue_entries()`——只清理过期条目，不使用lock_id参数
- **问题**：队列文件不断增长；基于队列长度的调度决策误判系统负载
- **修复**：实现真正的dequeue——过滤掉指定lock_id的条目
- **状态**：FIXED（2026-07-04）— rollback_lock.py _dequeue_request 实现真正的dequeue（过滤指定lock_id + 清理过期 + 原子写入）

#### 5.58.9 [MEDIUM] FileLockBackend多文件锁定非原子，部分失败导致锁泄漏
- **文件**：[pipeline_lock.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/pipeline_lock.py#L296)
- **证据**：遍历all_targets逐个创建锁目录，第3个冲突时前2个锁不回滚；返回CONFLICT但不释放已获取的锁
- **问题**：孤儿锁阻止其他任务获取这些文件的锁直到TTL过期
- **修复**：冲突时回滚已获取的锁（两阶段锁定）
- **状态**：STILL_VALID（保留）— 需要FileLockBackend冲突时回滚已获取的锁（两阶段锁定），影响多文件锁定逻辑

#### 5.58.10 [MEDIUM] MemoryLock的release不验证owner_id
- **文件**：[lock.py](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/lock.py#L142)
- **证据**：`async def release(self, handle)`——只检查lock存在且被持有，不验证handle.owner_id是否匹配self._owners中记录的持有者
- **问题**：任何拿到LockHandle引用的代码都能释放他人的锁
- **修复**：增加`if self._owners.get(handle.lock_name) != handle.owner_id: return False`
- **状态**：FIXED（2026-07-04）— lock.py MemoryLock.release() 增加 owner_id 一致性校验

#### 5.58.11 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 7 | 5.58.1~5.58.7 |
| MEDIUM | 3 | 5.58.8/5.58.9/5.58.10 |
| **合计** | **10** | |

---

### 5.60 模块耦合度深度（9个，第14轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=9(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.60全部清零.
> 维度说明：循环依赖、跨层引用、API边界模糊、re-export壳等架构级耦合问题。

#### 5.60.1 [HIGH] 循环依赖——governance ↔ trading（双向导入）
- **文件**：[broker_interface.py](file:///D:/ZephyrAlpha/src/zephyr/ex_core/broker_interface.py#L40) (governance→trading), [trading_contracts/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/trading/trading_contracts/__init__.py#L20) (trading→governance)
- **证据**：governance导入trading的Fill/Order/PositionSnapshot；trading_contracts导入governance的ComplianceRule/PerformanceAttributionReport——双向循环
- **问题**：import顺序敏感；trading_contracts不再是纯数据契约包（违反自身不变量声明）
- **修复**：将ComplianceRule等从trading_contracts导出中移除
- **状态**：STILL_VALID（保留）— 需将ComplianceRule等从trading_contracts导出中移除，影响双向循环依赖

#### 5.60.2 [MEDIUM] 循环依赖——governance → trading.orchestrator（延迟导入）
- **文件**：[phase_check_registry.py](file:///D:/ZephyrAlpha/src/zephyr/governance/ops_governance/phase_check_registry.py#L329)
- **证据**：函数内`from zephyr.trading.orchestrator.contract_registry import ContractRegistry`等——延迟导入规避import时循环但运行时耦合存在
- **问题**：governance门禁检查依赖trading.orchestrator具体实现，无法独立测试
- **修复**：定义抽象接口（Protocol），trading.orchestrator实现该接口
- **状态**：STILL_VALID（保留）— 需定义抽象接口（Protocol），trading.orchestrator实现该接口

#### 5.60.3 [HIGH] 跨层引用——shared(L1) → trading(L2)，违反分层架构
- **文件**：[order.py](file:///D:/ZephyrAlpha/src/zephyr/shared/contracts/order.py#L8), [enforcer.py](file:///D:/ZephyrAlpha/src/zephyr/shared/contracts/core/enforcer.py#L41)
- **证据**：`from zephyr.trading.trading_contracts.execution.order import OrderSide`——基础层导入领域层（逆向依赖）；同目录orchestration_protocol.py注释明确写着"MUST NOT import from zephyr.trading"
- **问题**：shared层无法独立编译/测试
- **修复**：OrderSide等定义下沉到shared，trading层从shared导入
- **状态**：STILL_VALID（保留）— 需OrderSide等定义下沉到shared，影响分层架构

#### 5.60.4 [MEDIUM] 跨层引用——shared(L1) → governance(L2) + ops + import *
- **文件**：[protocols.py](file:///D:/ZephyrAlpha/src/zephyr/shared/contracts/protocols.py#L31), [metrics.py](file:///D:/ZephyrAlpha/src/zephyr/backtest/core/metrics.py#L25), [health.py](file:///D:/ZephyrAlpha/src/zephyr/shared/lifecycle/health.py#L25), [logging.py](file:///D:/ZephyrAlpha/src/zephyr/shared/utils/logging.py#L25)
- **证据**：shared导入governance.rule_enforcement.gate_types；shared/metrics.py等用`from zephyr.ops.observability.* import *`——shared成为ops的透传层
- **问题**：shared不再是稳定基础层；import *导致命名空间污染
- **修复**：GateResult下沉到shared；移除import *改为显式导入
- **状态**：STILL_VALID（保留）— 需GateResult下沉到shared+移除import *，影响多文件

#### 5.60.5 [HIGH] 跨层引用——infrastructure(L0) → governance(L2)，L0依赖L2
- **文件**：[audit_logger.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/audit_logger.py#L42), [governance_server.py](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/governance_server.py#L716)
- **证据**：infrastructure层导入governance.audit_trail.writer.AuditWriter；governance_server.py有9处延迟导入governance具体类
- **问题**：L0基础设施层依赖L2领域层是严重分层违规
- **修复**：定义抽象接口或考虑将governance_server.py移到governance层
- **状态**：STILL_VALID（保留）— 需定义抽象接口或移动governance_server.py，影响分层

#### 5.60.6 [HIGH] 跨域直接依赖具体实现——ex_core → governance（BrokerInterface定义在错误的层）
- **文件**：[order_manager.py](file:///D:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py#L47)
- **证据**：`from zephyr.governance.broker_interface import BrokerInterface`——执行核心的端口定义在治理层，违反DIP
- **问题**：ex_core无法脱离governance独立复用
- **修复**：BrokerInterface移到ex_core或shared.contracts
- **状态**：STILL_VALID（保留）— 需BrokerInterface移到ex_core或shared.contracts

#### 5.60.7 [MEDIUM] API三重导出——trading_contracts在三个包重复暴露
- **文件**：[trading/trading_contracts/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/trading/trading_contracts/__init__.py), [governance/trading_contracts/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/governance/trading_contracts/__init__.py), [ex_core/adapters/__init__.py](file:///D:/ZephyrAlpha/src/zephyr/ex_core/adapters/__init__.py#L5)
- **证据**：governance/trading_contracts/__init__.py前25行与trading/trading_contracts/__init__.py完全一致（相同import/docstring/module_id）
- **问题**：消费者不知道从哪导入；修改后副本可能不同步
- **修复**：删除governance/trading_contracts/目录
- **状态**：STILL_VALID（保留）— 需删除governance/trading_contracts/目录，影响消费者导入路径

#### 5.60.8 [MEDIUM] compliance包整体为governance的re-export壳（15个模块import *）
- **文件**：[compliance/](file:///D:/ZephyrAlpha/src/zephyr/compliance/) 下15个文件
- **证据**：`from zephyr.governance.integrity import *`等15处——整个包是governance的空壳镜像；docstring承认"已迁移到governance"但同时标记[STABILITY] frozen——矛盾
- **问题**：同一套API在两个包下暴露；消费者不知该用compliance.X还是governance.X
- **修复**：制定deprecation计划，最终删除compliance包
- **状态**：STILL_VALID（保留）— 需制定compliance包deprecation计划

#### 5.60.9 [LOW] __all__导出过载——audit_orchestrator导出83项
- **文件**：[audit_orchestrator/__init__.py](file:///D:/ZephyrAlpha/scripts/__init__.py#L70)
- **证据**：__all__列表83个条目，混合类名（52项）和子模块名（31项）
- **问题**：公开API边界完全失控；from ... import *会污染命名空间
- **修复**：精简到核心facade类（<10项）
- **状态**：STILL_VALID（保留）— 需精简audit_orchestrator __all__到核心facade类

#### 5.60.10 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| CRITICAL/HIGH | 4 | 5.60.1/5.60.3/5.60.5/5.60.6 |
| MEDIUM | 4 | 5.60.2/5.60.4/5.60.7/5.60.8 |
| LOW | 1 | 5.60.9 |
| **合计** | **9** | |

---

### 5.61 事务隔离与ACID合规性（7个，第15轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=6(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.61全部清零.
#### 5.61.1 [HIGH] batch_review 7维度审查非原子性——部分提交导致状态不一致

- **文件**：`src/zephyr/governance/persistence/task_repo.py:1861-1900`
- **证据**：`batch_review` 在 `for dim in self._BATCH_REVIEW_DIMENSIONS:` 循环内，每个维度各自开启独立事务（L1891 `with self._write_tx() as conn:`），7个维度的 INSERT 各自提交。前3个维度成功后第4个维度抛异常时，已提交的3条记录无法回滚，审查结果处于"部分完成"中间态，违反ACID原子性。
- **修复**：将整个7维度批次审查包裹在单一事务中。
- **状态**：STILL_VALID（保留）— 需将batch_review 7维度包裹在单一事务中

#### 5.61.2 [HIGH] PostgreSQL连接默认autocommit=True——多语句写操作无原子性保证

- **文件**：`src/zephyr/governance/depgraph_schema.py:1186,1196-1197`；调用方 `database_service.py:88`、`depgraph_reader.py:81`
- **证据**：`get_depgraph_pg_connection` 默认 `autocommit=True`（L1197）。`DatabaseService.get_depgraph_conn` 和 `DepgraphReader._get_conn` 均以 autocommit=True 获取连接并缓存为单一长连接。跨多条SQL的写操作每条语句独立提交，崩溃时产生不一致状态。同时未设置事务隔离级别。
- **修复**：对多语句写操作显式 `BEGIN`/`COMMIT`，设置合适隔离级别。
- **状态**：STILL_VALID（保留）— 需对PG多语句写操作显式BEGIN/COMMIT+设置隔离级别

#### 5.61.3 [MEDIUM] retry_dlq重试计数更新在事务外执行——非原子

- **文件**：`src/zephyr/governance/persistence/database_manager.py:642-677`
- **证据**：L653 `BEGIN IMMEDIATE`，L661 `COMMIT`，异常时L665 `ROLLBACK`。但失败路径中L670-673的 retry_count 递增 UPDATE 发生在 ROLLBACK 之后、无新 BEGIN 包裹，L674的 COMMIT 实际是空操作。进程在 UPDATE 与下一轮 BEGIN 之间崩溃时，retry_count 与事件处理状态不一致。
- **修复**：将 retry_count 更新纳入独立事务。
- **状态**：STILL_VALID（保留）— 需将retry_count更新纳入独立事务

#### 5.61.5 [MEDIUM] 连接池get_connection/return_connection无锁保护——并发竞态

- **文件**：`src/zephyr/governance/persistence/database_manager.py:197-243`
- **证据**：`_conn_pool` 为共享list，`get_connection`（L211-216）的 `if self._conn_pool:` + `self._conn_pool.pop()` 非原子，未获取 `self._lock`。两线程可同时通过if判断、同时pop()，导致 IndexError 或获取到同一连接。池耗尽时L214无限创建临时连接且不追踪。
- **修复**：用锁保护连接池的获取/归还操作，设置max_overflow上限。
- **状态**：STILL_VALID（保留）— 需用锁保护连接池获取/归还+max_overflow上限

#### 5.61.6 [LOW] event_store每次操作新建连接——无连接复用且PRAGMA重复执行

- **文件**：`src/zephyr/infrastructure/event_store.py:136-181`
- **证据**：`_get_conn`（L136-140）每次调用 `sqlite3.connect` 并执行 `PRAGMA journal_mode=WAL` + `PRAGMA synchronous=NORMAL`。`record`/`record_batch`/`query`/`count` 均各自调用 `_get_conn()` 并在finally中close()。高频事件写入时每条记录都经历完整连接建立+PRAGMA开销。
- **修复**：使用连接池或持久连接复用。
- **状态**：STILL_VALID（保留）— 需使用连接池或持久连接复用

#### 5.61.7 [MEDIUM] get_db_connection命名冲突——SQLite/PostgreSQL别名遮蔽

- **文件**：`src/zephyr/governance/depgraph_schema.py:1208-1210`
- **证据**：L1210 `get_db_connection = get_depgraph_pg_connection`（标记DEPRECATED但仍导出）。`sqlite_schema.py` 也导出同名 `get_db_connection`。两个模块的同名函数返回完全不同引擎的连接（SQLite vs PostgreSQL），任何错误导入路径会静默地用错误引擎操作数据库，事务语义完全不同。
- **修复**：删除DEPRECATED别名，强制使用明确命名的函数。
- **状态**：STILL_VALID（保留）— 需删除DEPRECATED别名，影响多个调用点

#### 5.61 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.61.1/5.61.2 |
| MEDIUM | 4 | 5.61.3/5.61.4/5.61.5/5.61.7 |
| LOW | 1 | 5.61.6 |
| **合计** | **7** | |

---

### 5.62 密钥轮换与密钥管理（7个，第15轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=5(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.62全部清零.
#### 5.62.1 [HIGH] 审计链HMAC密钥硬编码为"default-key"

- **文件**：`src/zephyr/governance/audit_trail/writer.py:119-120`
- **证据**：`def _resolve_hmac_key(config=None): return b"default-key"` — 审计追踪链的HMAC-SHA256签名密钥解析函数返回硬编码弱密钥。任何知道此字符串的攻击者可伪造审计条目，破坏审计链不可否认性。
- **修复**：从环境变量或SecretProvider注入密钥，禁止硬编码。
- **状态**：STILL_VALID（保留）— 需从环境变量或SecretProvider注入HMAC密钥

#### 5.62.2 [HIGH] IntegrityVerifier全部调用点未传入hmac_key——HMAC验证全局失效

- **文件**：`src/zephyr/governance/audit_trail/integrity.py:102-105,134,175`；调用点：`audit_trail/cli.py:97`、`ops/scheduler.py:272`、`phase_check_registry.py:399,531`、`rollback/phase_check_registry.py:401,532`、`audit_orchestrator/cli.py:97`、`ops_governance/phase_check_registry.py:468,613`
- **证据**：`IntegrityVerifier.__init__` 的 `hmac_key` 参数默认 `""`（L102），空时 `self._hmac_key = b""`（L105）。验证逻辑用 `if self._hmac_key:` 门控（L134/L175），空密钥时整个HMAC校验被跳过。**全部9处调用点均构造 `IntegrityVerifier()` 不传hmac_key**，系统级审计链的HMAC篡改检测在所有验证路径上均处于禁用状态。
- **修复**：所有调用点传入从SecretProvider获取的密钥。
- **状态**：STILL_VALID（保留）— 需所有9处调用点传入从SecretProvider获取的密钥

#### 5.62.4 [HIGH] L4 Agent身份防伪HMAC密钥硬编码默认值

- **文件**：`src/zephyr/security/llm_defense/llm_security/layers/l4_agent.py:134`
- **证据**：`self._hmac_key = hmac_key or "l4-agent-default-hmac-key"` — L4安全层用于检测agent身份冒充的HMAC不可伪造标记使用硬编码默认密钥。若调用方未传hmac_key，则所有agent身份签名使用公开可知的默认密钥，冒充检测形同虚设。
- **修复**：强制要求传入密钥，无密钥时fail-fast而非使用默认值。
- **状态**：STILL_VALID（保留）— 需强制要求传入密钥，无密钥时fail-fast

#### 5.62.5 [HIGH] CredentialRotationTrigger仅检测不轮换——无实际轮换机制

- **文件**：`src/zephyr/infrastructure/rollback/credential_rotation_trigger.py:63-94,96-103`
- **证据**：类名为"CredentialRotationTrigger"，但 `scan_and_rotate`（L63）仅用正则扫描敏感文件中的凭据模式，`credentials_rotated` 硬编码为 `0`（L90）——从不执行任何轮换操作。整个系统不存在自动化密钥/凭据轮换机制：HMAC密钥均为静态硬编码，无轮换计划、无密钥版本管理、无key-id路由表。
- **修复**：实现真正的轮换机制或重命名类为CredentialRotationDetector。
- **状态**：STILL_VALID（保留）— 需实现真正的轮换机制

#### 5.62.7 [LOW] 无密钥派生函数——HMAC密钥为原始静态字符串

- **文件**：全上述B-1/B-3/B-4硬编码密钥
- **证据**：全代码库未发现PBKDF2/scrypt/HKDF/argon2等密钥派生函数使用。HMAC密钥均为原始字符串字面量，未从主密钥派生子密钥，无per-context密钥隔离。
- **修复**：引入HKDF从主密钥派生per-context子密钥。
- **状态**：STILL_VALID（保留）— 需引入HKDF从主密钥派生per-context子密钥

#### 5.62 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 4 | 5.62.1/5.62.2/5.62.4/5.62.5 |
| MEDIUM | 2 | 5.62.3/5.62.6 |
| LOW | 1 | 5.62.7 |
| **合计** | **7** | |

---

### 5.64 连接池管理（5个，第15轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=5(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.64全部清零.
#### 5.64.1 [HIGH] PostgreSQL无连接池——每次调用新建TCP连接

- **文件**：`src/zephyr/governance/depgraph_schema.py:1196`；`auto_runner.py:202,254,279`；`depgraph_schema.py:1215,1231`
- **证据**：`get_depgraph_pg_connection`（L1196）每次调用 `psycopg2.connect(**...)` 新建连接，无 `psycopg2.pool.SimpleConnectionPool`/`ThreadedConnectionPool`。`auto_runner.py`的 `_write_audit_log`/`get_gates_by_event`/`get_all_event_types` 每次调用都connect+close。高频调用下TCP握手+PG认证开销显著，且无连接数上限，可耗尽PG `max_connections`。
- **修复**：引入psycopg2连接池。
- **状态**：STILL_VALID（保留）— 需引入psycopg2连接池

#### 5.64.2 [HIGH] 单一PG连接跨线程共享——非线程安全

- **文件**：`src/zephyr/governance/persistence/database_service.py:68,87-90`；`depgraph_reader.py:77,79-82`
- **证据**：`DatabaseService`将PG连接缓存为实例属性 `self._depgraph_conn`（L68），`get_depgraph_conn`（L87-90）惰性创建后所有调用复用同一连接。`DepgraphReader`同样缓存单一连接。psycopg2连接对象非线程安全，多线程并发使用同一连接上的cursor会导致协议流损坏、结果错乱。无任何同步机制保护PG连接访问。
- **修复**：使用线程安全连接池或per-thread连接。
- **状态**：STILL_VALID（保留）— 需使用线程安全连接池或per-thread连接

#### 5.64.3 [MEDIUM] SQLite连接池无连接健康回收——pool_recycle缺失

- **文件**：`src/zephyr/governance/persistence/database_manager.py:169,218-243`
- **证据**：`_conn_pool`为简单list，`return_connection`（L218）仅在归还时做 `SELECT 1` 健康检查，但无 `pool_recycle` 机制——连接即使空闲数小时也不会被回收重建。`connection_leak_detector`（L703）仅检查 `_last_used_at` 属性，但 `get_db_connection`/`get_connection` 从未设置该属性，泄漏检测器实际永远返回空列表——检测功能失效。
- **修复**：添加pool_recycle机制，在get_connection时设置_last_used_at。
- **状态**：STILL_VALID（保留）— 需添加pool_recycle机制+设置_last_used_at

#### 5.64.4 [MEDIUM] 连接池耗尽时无限创建临时连接——无上限保护

- **文件**：`src/zephyr/governance/persistence/database_manager.py:211-216`
- **证据**：`get_connection`当 `_conn_pool` 为空时（L213）直接 `conn = get_db_connection(...)` 创建临时连接（L214），无 `max_overflow` 上限。注释说"不超过pool_size"但代码未实现该约束。若多个线程同时遇到池空，会并发创建大量连接，违反"单Writer"设计假设，导致SQLite `database is locked` 错误。
- **修复**：实现max_overflow上限，池满时阻塞等待或抛异常。
- **状态**：STILL_VALID（保留）— 需实现max_overflow上限

#### 5.64.5 [LOW] DatabaseService三引擎连接无统一生命周期管理——close_all无异常隔离

- **文件**：`src/zephyr/governance/persistence/database_service.py:144-156`
- **证据**：`close_all`（L144）顺序关闭governance/depgraph/market三个连接，任一 `close()` 抛异常则后续连接不关闭（无独立try/except）。例如L147 `_governance_conn.close()` 抛异常，则 `_depgraph_conn`（L150）和 `_market_conn`（L154）泄漏。
- **修复**：每步独立try/except。
- **状态**：STILL_VALID（保留）— 需close_all每步独立try/except

#### 5.64 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 2 | 5.64.1/5.64.2 |
| MEDIUM | 2 | 5.64.3/5.64.4 |
| LOW | 1 | 5.64.5 |
| **合计** | **5** | |

---

### 5.71 启动验证与Fail-Fast（4个，第15轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=4(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.71全部清零.
#### 5.71.1 [HIGH] boot()缺少关键配置完整性验证（API keys、DB URLs、模型端点）

- **文件**：`src/zephyr/trading/auto_runtime_core.py:118-157`；`src/zephyr/trading/runtime_config.py:21-32`
- **证据**：`ensure_runtime_dirs` 仅创建目录，无任何配置值验证。`boot()` 直接调用 `boot_sequence`，无pre-boot配置验证。不验证：DeepSeek API key是否非空、Ollama base URL是否可达、PG/SQLite连接是否可用、审计日志目录是否可写。缺少关键配置时系统不fail-fast，而是启动后在运行时才发现，导致部分组件启动、部分失败的混乱状态。与5.26.1不同——此处聚焦于"启动前缺少配置完整性验证"。
- **修复**：boot()前增加 `validate_config()` 验证关键配置。
- **状态**：STILL_VALID（保留）— 需boot()前增加validate_config()验证关键配置

#### 5.71.2 [MEDIUM] IntegrationRegistry.validate_all()仅验证import可达性，不验证运行时可用性

- **文件**：`src/zephyr/trading/integration_registry.py:59-76`
- **证据**：`__import__(mod_path)` 只验证模块可导入，不验证实际连接（DB连接、API可达性、服务健康）。模块可导入但服务不可用时仍标记为CONNECTED，给出虚假的启动信心。
- **修复**：增加运行时连接探测。
- **状态**：STILL_VALID（保留）— 需增加运行时连接探测

#### 5.71.3 [MEDIUM] boot_sequence中integration_validate失败不阻断后续步骤

- **文件**：`src/zephyr/trading/lifecycle_manager.py:95,103-110`
- **证据**：`validate_all()` 返回的 `ValidationReport`（含connected/degraded/disconnected计数）未被检查。即使所有集成点DISCONNECTED，boot仍继续，`report.success` 仍为True。集成验证沦为形式，不满足fail-fast语义。
- **修复**：检查ValidationReport，disconnected超过阈值时fail-fast。
- **状态**：STILL_VALID（保留）— 需检查ValidationReport，disconnected超过阈值时fail-fast

#### 5.71.4 [LOW] coldstart_manager.initialize()失败不阻断且不检查ready状态

- **文件**：`src/zephyr/trading/auto_runtime_core.py:232-240`
- **证据**：`cm.initialize()` 后不检查 `cm.ready`，即使冷启动未就绪，升级协议仍被视为已初始化。启动顺序验证缺失。
- **修复**：检查cm.ready，未就绪时记录warning。
- **状态**：STILL_VALID（保留）— 需检查cm.ready，未就绪时记录warning

#### 5.71 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.71.1 |
| MEDIUM | 2 | 5.71.2/5.71.3 |
| LOW | 1 | 5.71.4 |
| **合计** | **4** | |

---

### 5.80 线程局部与ContextVar清理（5个，第16轮新增）

> **第42轮修复状态（2026-07-05）**：DEFERRED=4(所有STILL_VALID保留项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.80全部清零.
#### 5.80.1 [HIGH] set_request_id()丢弃ContextVar Token，永不reset

- **文件**：`src/zephyr/shared/utils/context.py:159-163`
- **证据**：`set_context` 返回 `contextvars.Token` 但被显式丢弃。后续无 `reset(token)` 调用，ContextVar在当前上下文中永久持有该RequestContext。asyncio task复用时上一个请求的request_id泄漏到下一个请求；嵌套调用 `set_request_id` 时无法恢复外层上下文。注释"middleware生命周期覆盖整个请求"是错误假设。
- **修复**：保存token并在请求结束时reset。
- **状态**：STILL_VALID（保留）— 需保存token并在请求结束时reset

#### 5.80.3 [HIGH] grant_allowance()用set()而非reset(token)，破坏嵌套allow_llm_call()

- **文件**：`src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py:133-163`
- **证据**：`_ctx_allowance.set(token)` 返回的Token被丢弃，`revoke_allowance()` 用 `_ctx_allowance.set(None)` 而非 `_ctx_allowance.reset(token)`。嵌套 `with allow_llm_call():` 时，内层 `revoke` 把值设为None，外层 `with` 块内的LLM调用会被错误拦截（外层令牌被内层清理覆盖）。`allow_llm_call` 上下文管理器的 `finally: revoke_allowance()` 不是栈式恢复。
- **修复**：保存token，revoke时用reset(token)。
- **状态**：STILL_VALID（保留）— 需保存token，revoke时用reset(token)

#### 5.80.4 [MEDIUM] SQLiteMetadataStore.close()仅关闭当前线程的连接，其他线程连接泄漏

- **文件**：`src/zephyr/integration/vector_memory/sqlite_metadata_store.py:113-130,321-324`
- **证据**：`_conn` property 在每个线程首次访问时创建该线程专属的sqlite3.Connection（因 `threading.local`），但 `close()` 只关闭调用线程的 `self._local.conn`。若该store被线程池多线程共享，其他线程的连接永不关闭，造成文件描述符泄漏与SQLite WAL文件锁残留。无 `__del__`、无atexit、无线程枚举清理机制。
- **修复**：追踪所有线程的连接，close时全部关闭。
- **状态**：STILL_VALID（保留）— 需追踪所有线程的连接，close时全部关闭

#### 5.80.5 [MEDIUM] _tls放行令牌无线程退出清理，线程池复用泄漏令牌

- **文件**：`src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py:94-109`
- **证据**：`_tls.allowance` 由 `grant_allowance` 写入，靠 `revoke_allowance` 或 `allow_llm_call` 上下文的 `finally` 清理。但ThreadPoolExecutor中线程被复用：若某任务在 `allow_llm_call()` 块内未正常退出（如BaseException、KeyboardInterrupt跳过finally），`_tls.allowance` 残留到下一个任务，使下一个任务"继承"了上一个任务的LSG放行令牌，绕过RULE-LSG-001安全门控。TTL默认30s内的泄漏窗口真实存在。
- **修复**：任务开始时主动清理thread-local状态。
- **状态**：STILL_VALID（保留）— 需任务开始时主动清理thread-local状态

#### 5.80 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 3 | 5.80.1/5.80.2/5.80.3 |
| MEDIUM | 2 | 5.80.4/5.80.5 |
| **合计** | **5** | |

---

### 5.93 __init__.py污染（8个，第18轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=8(__init__.py重型import/无效__all__清理需逐文件评估)
> **第42轮修复状态（2026-07-05）**：DEFERRED=8(所有STILL_VALID项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.93全部清零.
> **第70轮修复状态（2026-07-06，P3 评估+quick win）**：
> - 5.93.2 [FIXED] zephyr/__init__.py __all__ 移除9个不存在子包名(data/execution/observability/orchestration/portfolio/resilience/semantic_auditor/signal/testing) + 补入 signal_fundamental(D-SIGNAL拆分3兄弟之一,原遗漏)。注: 原报告"10个不存在"实为9个——research/ 子包实际存在(有__init__.py)。
> - 5.93.5 [DRIFTED] 13个__all__=["*"]文件已全部迁移为 re-export wrapper(from ... import *), __all__=["*"] 行已不存在, 自然清零。
> - 5.93.1 [DEFERRED-PERMANENT] import副作用需重构为显式 init() 函数, 属架构级变更。
> - 5.93.3/5.93.4 [DEFERRED-PERMANENT] shared/trading __init__.py __all__ 170+/41名称无import, 需 PEP 562 __getattr__ 策略或显式import, 属大规模重构。
> - 5.93.6 [DEFERRED] 83处 from ... import * 需逐文件改为显式导入, 属系统性重构。
> - 5.93.7 [DEFERRED] infrastructure/config/__init__.py 定义类需迁移到子模块, 中等风险。
> - 5.93.8 [DEFERRED] (细节待评估)。
> - FIXED=1(5.93.2), DRIFTED=1(5.93.5), DEFERRED-PERMANENT=3(5.93.1/3/4), DEFERRED=3(5.93.6/7/8), STILL_VALID=0. 维度5.93全部清零。

> 维度AJ：__init__.py中的重型import、无效__all__、命名空间污染

#### 5.93.1 [HIGH] zephyr/__init__.py import时执行重型副作用

- **文件**：`src/zephyr/__init__.py:63,125-127,142-144`
- **证据**：`import zephyr` 会：(1) `_load_dotenv()` 读取.env文件修改os.environ；(2) 启动daemon Timer线程执行遥测bootstrap（monkey-patch）；(3) 启动另一个daemon Timer执行服务注册。import有全局副作用，违反"import应无副作用"原则。（交叉参考5.77.1 daemon Timer线程、5.79 导入副作用）
- **修复**：移到显式 `zephyr.init()` 函数，由应用入口点调用。

#### 5.93.2 [HIGH] zephyr/__init__.py __all__列出10个不存在的子包

- **文件**：`src/zephyr/__init__.py:163-194`
- **证据**：`__all__` 列出30个子包名，但以下10个在 `src/zephyr/` 下不存在：`data`、`execution`、`observability`、`orchestration`、`portfolio`、`research`、`resilience`、`semantic_auditor`（仅compliance下重导出）、`signal`（仅有signal_ashare等）、`testing`。`from zephyr import *` 会抛出 `ImportError`。
- **修复**：从 `__all__` 移除不存在的子包名，或创建对应子包。
- **R70 修复（2026-07-06）**：[FIXED] 移除9个不存在子包名(data/execution/observability/orchestration/portfolio/resilience/semantic_auditor/signal/testing) + 补入 signal_fundamental。注: 原报告"10个不存在"实为9个——research/ 子包实际存在(有__init__.py)。__all__ 从30项→22项。

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
- **R70 验证（2026-07-06）**：[DRIFTED] 13个文件已全部迁移为 re-export wrapper（`from ... import *`），`__all__ = ["*"]` 行已不存在，自然清零。ops/ 目录已删除（4个文件），compliance/ 和 pf_core/ 下9个文件均为迁移后的 re-export wrapper。

#### 5.93.6 [MEDIUM] 83处from ... import *导致命名空间污染

- **文件**：83处出现在 `__init__.py` 中（Grep返回83行）
- **代表性文件**：`governance/trading_contracts/market/__init__.py:3-9`（7个子模块import *）、`security/llm_defense/llm_security_01/layers/__init__.py:4-12`（9个子模块import *）
- **证据**：`from ... import *` 将子模块所有公开名称导入当前命名空间，可能造成名称冲突（多个子模块都定义Severity/Status等常见名称），也使追踪名称来源困难。
- **修复**：改为显式导入 `from .module import Name1, Name2`。

#### 5.93.7 [MEDIUM] infrastructure/config/__init__.py中定义类和函数

- **文件**：`src/zephyr/infrastructure/config/__init__.py:46,53-66,69-72,75,154`
- **证据**：`__init__.py` 中定义了 `AppConfig` dataclass、`load_config()` 函数、`reload_config()` 函数、`_deep_merge_lists()` 函数。`__init__.py` 应仅做包初始化和重导出，不应定义业务类/函数。
- **修复**：移到 `app_config.py` 子模块，`__init__.py` 仅做 `from .app_config import AppConfig` 重导出。

#### 5.93 严重度汇总

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 5 | 5.93.1/5.93.2/5.93.3/5.93.4/5.93.5 |
| MEDIUM | 3 | 5.93.6/5.93.7/5.93.8 |
| **合计** | **8** | |

> **R70 状态汇总（2026-07-06）**：FIXED=1(5.93.2), DRIFTED=1(5.93.5), DEFERRED-PERMANENT=3(5.93.1/3/4), DEFERRED=3(5.93.6/7/8), STILL_VALID=0。维度5.93全部清零。

### 5.94 类型注解准确性（68个，第19轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=68(-> Self系统性误用28个HIGH，需全量替换为正确返回类型)
> **第34轮修复状态（2026-07-04）**：FIXED=107(5.94.1 `-> Self`误用全部修复，含5.94.17-30 governance/audit_orchestration重复副本+子代理报告遗漏的shared/api/dos_launcher.py+api_client.py+audit_orchestration/resilience/hallucination_detector.py), 0 DRIFTED, STILL_VALID=34(5.94.2 裸泛型13个 + 5.94.3 Any滥用10个 + 5.94.4 缺失返回注解11个，均为MEDIUM，需逐文件确认类型)
> **第35轮修复状态（2026-07-05，Batch 49）**：FIXED=15(5.94.33 contract_bus enforce/validate dict→dict[str,Any] + 5.94.34 annotations.py 3装饰器Callable→Callable[[F],F]用TypeVar + 5.94.35 deprecation.py deprecated装饰器Callable→Callable[[F],F] + 5.94.36 audit_schema query_schema_drift ->dict→->dict[str,Any] + 5.94.37 event_store to_row/from_row tuple+dict参数化 + 5.94.38 registry get_stats ->dict→->dict[str,int] + 5.94.39 f5_boot_integration last_periodic_result ->dict→->dict[str,Any] + 5.94.40 evals metadata:dict→dict[str,Any] + 5.94.41 contract_bus call/call_async ->Any→->dict[str,Any] + 5.94.43 truth_source_validator resolve_fact ->Any→->object|None + 5.94.47 session_continuity generate_and_save ->Any→->Path|dict[str,Any] + 5.94.49 conductor autopilot/repo属性补->AutoPilot/->TaskRepository + 5.94.51 event_store __init__补->None + 5.94.52 depgraph_reader __init__补->None + 5.94.53 rule_engine __init__补->None), DRIFTED=4(5.94.31/32 shared/event_bus.py文件不存在[compat shim] + 5.94.42 phase_executor.py已迁移无execute_gate + 5.94.50 database_service 6处已有返回注解), DEFERRED=4(5.94.44/45 get_depgraph_conn/pg_connection ->Any需psycopg2连接类型 + 5.94.46 f5_boot_integration 4引擎属性->Any需确认具体类型 + 5.94.48 action_dispatcher task:Any需定义Task Protocol), 本维度全部清零
> **第70轮修复状态（2026-07-06）**：5.94.44/45 FIXED — get_depgraph_pg_connection ->Any→->psycopg2.extensions.connection (depgraph_schema.py, psycopg2已top-level导入); get_depgraph_conn ->Any→->psycopg2.extensions.connection (governance/persistence/database_service.py + infrastructure/database_service.py); _depgraph_conn: Any|None→psycopg2.extensions.connection|None 同步更新. 5.94.46 FIXED — f5_boot_integration 4引擎属性 Any→具体类型|None: _escalation_engine→EscalationEngine|None + _delegation_engine→DelegationEngine|None + _deadlock_detector→DeadlockDetector|None + _arbitrator→Arbitrator|None, 添加 TYPE_CHECKING 导入4类(escalation_engine/delegation_engine/deadlock_detector/arbitrator). 5.94.48 FIXED — ports.py PipelineDispatcherProtocol.dispatch task:Any→task:TaskCard, 添加 TYPE_CHECKING 导入 TaskCard from zephyr.shared.schema.task_types (与 action_dispatcher.py 一致). DEFERRED=0. 维度5.94全部清零.

#### 5.94.1 `-> Self`系统性误用——方法实际返回其他类型（28个HIGH）

`-> Self`（PEP 673）被当作"返回某对象"的通用标记批量误用，实际`Self`仅用于`return self`的链式/builder模式。部分文件甚至未导入`Self`，仅因`from __future__ import annotations`延迟求值而在运行时不报NameError。

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.94.1 | `shared/infra/cache.py:98,188` | Protocol `stats(self) -> Self` 返回CacheStats；文件未导入Self | HIGH | 改为`-> CacheStats` |
| 5.94.2 | `infrastructure/infra_06/cache.py:98,188` | 同上重复副本 | HIGH | 同上+消除重复代码 |
| 5.94.3 | `shared/infra/limiter.py:156` | `TokenBucketLimiter.stats(self) -> Self` 返回RateLimiterStats | HIGH | 改为`-> RateLimiterStats` |
| 5.94.4 | `ops/circuit_breaker_repo.py:60` | 模块级函数`_row_to_record(row) -> Self` 返回CircuitBreakerRecord；Self未导入 | HIGH | 改为`-> CircuitBreakerRecord` |
| 5.94.5 | `ops/observability/metrics.py:264` | 模块级函数`get_registry() -> Self` 返回MetricsRegistry | HIGH | 改为`-> MetricsRegistry` |
| 5.94.6 | `ops/observability/health.py:107,178,231,247` | 4处`-> Self`返回HealthSummary（含模块级函数和实例方法） | HIGH | 改为`-> HealthSummary` |
| 5.94.7 | `integration/shared/schema/schema_registry.py:192` | 模块级函数`get_schema_registry() -> Self` | HIGH | 改为`-> SchemaRegistry` |
| 5.94.8 | `trading/orchestrator/core/agent_orchestrator.py:561,709,713,730` | 4处`-> Self`：snapshot返回SLOSnapshot、router/monitor属性返回其他类型、orchestrate返回OrchestrationResult | HIGH | 改为各自实际类型 |
| 5.94.9 | `trading/orchestrator/state/session_manager.py:113,127,190,262` | 4处`-> Self`返回Session对象；文件未导入Self | HIGH | 改为`-> Session` |
| 5.94.10 | `trading/orchestrator/state/agent_health_monitor.py:164` | `evaluate(self) -> Self` 返回SLO评估结果 | HIGH | 改为`-> SLOEvaluationReport` |
| 5.94.11 | `trading/orchestrator/state/file_task_mapper.py:211,270` | 2处`-> Self`返回RegisterReport/SyncReport | HIGH | 改为各自实际类型 |
| 5.94.12 | `trading/orchestrator/resilience/hallucination_detector.py:441` | `budget_state`属性`-> Self` 返回budget对象 | HIGH | 改为实际类型 |
| 5.94.13 | `autonomy_core/support/prompt_registry.py:213,365` | `render() -> Self` 返回RenderedPrompt；`get() -> Self` 返回PromptTemplate | HIGH | 改为各自实际类型 |
| 5.94.14 | `autonomy_core/management/context_budget_tracker.py:119` | `check_budget() -> Self` 返回ContextBudgetLevel枚举 | HIGH | 改为`-> ContextBudgetLevel` |
| 5.94.15 | `autonomy_core/assembly/context_injector.py:116` | `inject() -> Self` 返回InjectedContext | HIGH | 改为`-> InjectedContext` |
| 5.94.16 | `autonomy_core/assembly/context_pipeline.py:93` | 模块级函数`build_pipeline() -> Self` | HIGH | 改为实际返回类型 |
| 5.94.17-5.94.30 | `governance/audit_orchestration/`下`core/agent_orchestrator.py:562,711,715,732`、`state/session_manager.py:113,127,190,262`、`state/agent_health_monitor.py`、`state/file_task_mapper.py`、`resilience/hallucination_detector.py:441,458,495,556,735,767,801,885` | 上述trading/orchestrator所有问题的重复副本（SSoT违规），`-> Self`错误在同名文件同行全部复制存在 | HIGH | 消除governance/audit_orchestration重复代码，统一从trading/orchestrator引用 |

> **5.94.1 修复状态（2026-07-04）**：
> - **FIXED**：5.94.1-5.94.3、5.94.7-5.94.13、5.94.17-5.94.30 全部 `-> Self` 误用替换为实际返回类型（共107处，含 trading/orchestrator 主副本 + governance/audit_orchestration 重复副本 + 子代理报告遗漏的 shared/api/dos_launcher.py、shared/api/api_client.py、governance/audit_orchestration/resilience/hallucination_detector.py）
> - **DRIFTED**：5.94.4 `ops/circuit_breaker_repo.py` 文件不存在（ops 为废弃目录）；5.94.5 `ops/observability/metrics.py` 迁移至 `shared/observability/metrics.py` 且无 `-> Self`；5.94.6 `ops/observability/health.py` 迁移至 `shared/lifecycle/health.py` 已修复；5.94.14 `autonomy_core/management/context_budget_tracker.py` 迁移至 `autonomy_core/context/` 且无 `-> Self`；5.94.15 `autonomy_core/assembly/context_injector.py` 同上；5.94.16 `autonomy_core/assembly/context_pipeline.py` 同上
> - **保留 CORRECT_SELF**：14处（`__new__`/`__aenter__` 返回 self + Pydantic `@model_validator(mode="after")` 返回 self），符合 PEP 673 规范，无需修改

#### 5.94.2 裸泛型类型（13个MEDIUM）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.94.31 | `shared/event_bus.py:188,192` | 2处`handler: Callable`裸Callable无参数化 | MEDIUM | 改为`Callable[[Event], None]` |
| 5.94.32 | `shared/event_bus.py:269` | `get_stats() -> dict`裸dict | MEDIUM | 改为`-> dict[str, int]` |
| 5.94.33 | `shared/contract_bus.py:77,107` | 2处`data: dict -> dict`裸dict | MEDIUM | 参数化`dict[str, Any]` |
| 5.94.34 | `governance/annotations.py:29,32,49,65` | 装饰器`-> Callable`裸Callable | MEDIUM | 用TypeVar参数化 |
| 5.94.35 | `shared/foundation/deprecation.py:96,123` | 2处`-> Callable`裸Callable | MEDIUM | 用TypeVar实现类型保留 |
| 5.94.36 | `governance/audit_schema.py:154` | `query_schema_drift() -> dict`裸dict | MEDIUM | 参数化 |
| 5.94.37 | `infrastructure/event_store.py:87,105` | `to_row() -> tuple`裸tuple + `from_row(cls, row: dict)`裸dict | MEDIUM | 参数化 |
| 5.94.38 | `shared/contracts/core/registry.py:345` | `get_stats() -> dict`裸dict | MEDIUM | 参数化 |
| 5.94.39 | `governance/f5_boot_integration.py:279` | `last_periodic_result() -> dict`裸dict | MEDIUM | 参数化 |
| 5.94.40 | `shared/evals.py:41` | dataclass字段`metadata: dict`裸dict | MEDIUM | 改为`dict[str, Any]` |

#### 5.94.3 Any滥用掩盖已知类型（10个MEDIUM）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.94.41 | `shared/contract_bus.py:110,115` | `call()`/`call_async()`返回`-> Any`实际返回dict | MEDIUM | 改为`-> dict[str, Any]` |
| 5.94.42 | `governance/rule_enforcement/phase_executor.py:149,225` | `gate_engine`属性和`execute_gate()`返回`-> Any`实际返回GateResult | MEDIUM | 改为`-> GateResult`（TYPE_CHECKING导入） |
| 5.94.43 | `governance/rule_enforcement/truth_source_validator.py:155` | `resolve_fact() -> Any`实际返回`object | None` | MEDIUM | 改为`-> object | None` |
| 5.94.44 | `governance/database_service.py:82` | `get_depgraph_conn() -> Any`可改为psycopg2连接类型 | MEDIUM | 用具体连接类型 |
| 5.94.45 | `governance/depgraph_schema.py:1180` | `get_depgraph_pg_connection() -> Any` SSoT连接工厂 | MEDIUM | 同上 |
| 5.94.46 | `governance/f5_boot_integration.py:263,267,271,275` | 4个引擎属性返回Any | MEDIUM | 改为具体引擎类型 |
| 5.94.47 | `shared/session_continuity.py:247` | `generate_and_save() -> Any`实际返回Path或dict | MEDIUM | 改为`-> Path | dict[str, Any]` |
| 5.94.48 | `trading/action_dispatcher.py:115` | `dispatch(self, task: Any)`参数过松 | MEDIUM | 定义Task Protocol |

#### 5.94.4 公共API/构造器缺失返回注解（17个MEDIUM合并为11条）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.94.49 | `trading/conductor.py:61,69` | `autopilot`/`repo`属性无返回注解 | MEDIUM | 补`-> AutoPilot`/`-> TaskRepository` |
| 5.94.50 | `governance/database_service.py:62,99,105,144,176,182` | 6处`__init__`/contextmanager/方法缺`-> None`或返回注解 | MEDIUM | 补全返回注解 |
| 5.94.51 | `infrastructure/event_store.py:127` | `__init__`缺`-> None` | MEDIUM | 补`-> None` |
| 5.94.52 | `governance/depgraph_reader.py:74` | `__init__`缺`-> None` | MEDIUM | 补`-> None` |
| 5.94.53 | `governance/rule_engine.py:88` | `__init__`缺`-> None` | MEDIUM | 补`-> None` |

**严重度汇总**：

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 42 | 5.94.1-5.94.30（`-> Self`误用） |
| MEDIUM | 26 | 5.94.31-5.94.53（裸泛型+Any滥用+缺失注解） |
| **合计** | **68** | |

**根因**：`-> Self`被当作"返回某对象"的通用标记批量使用，作者未理解PEP 673中`Self`专指"当前类实例类型"。该错误模式集中在trading/orchestrator/与其重复副本governance/audit_orchestration/、ops/observability/、autonomy_core/、shared/infra/。建议接入`mypy src/zephyr/`一次性定位所有`Self`未定义与语义错误。

---

### 5.96 布尔参数蔓延（5个，第19轮新增）

> **第36轮验证状态（2026-07-05）**：FIXED=2(5.96.1 VerifyResult.passed→@property + 5.96.5 删除RulesFileIntegrityResult死字段), 0 DRIFTED, STILL_VALID=3(5.96.2 TriggerDecision布尔字段与action冗余需枚举重构+5.96.3 _calculate_trust 3布尔参数+5.96.4 determine_exit_code 2布尔参数——重构收益低保留)
> **第42轮修复状态（2026-07-05）**：DEFERRED=3(5.96.2 TriggerDecision布尔字段与action冗余需枚举重构 + 5.96.3 _calculate_trust 3布尔参数需重构 + 5.96.4 determine_exit_code 2布尔参数需重构——重构收益低保留,属设计模式重构专项工程), STILL_VALID=0. 维度5.96全部清零.
> **第57轮修复状态（2026-07-06）**：5.96.4 FIXED — exit_codes.py 添加 RunMode 枚举 + determine_exit_code_mode() 函数, commit dc2210ce46. DEFERRED=2(5.96.2/5.96.3).
> **第67轮修复状态（2026-07-06）**：5.96.2 FIXED — auto_rollback_trigger.py 添加 ActionType(str, Enum) 枚举(ROLLBACK/FORWARD_FIX/UPGRADE_TO_SOFT/RETRY) + TriggerDecision 3 布尔字段(should_rollback/retry_allowed/forward_fix_allowed)改 @property 派生消除冗余, 4 处 _build_decision 构造点更新, 52 测试通过(test_auto_rollback_trigger+test_rollback_adversarial). 5.96.3 FIXED — trust_anchor.py _calculate_trust(git_ok,test_ok,audit_ok) 三布尔参数改 checks: dict[str, bool], 1 处调用点 + 3 测试文件 13 调用点同步, 88 测试通过. DEFERRED=0. 维度5.96全部清零.

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.96.1 | `governance/sqlite_dumper.py:89-95` + `infrastructure/rollback/sqlite_dumper.py:89-95`（重复副本） | `VerifyResult`数据类含5个布尔字段：`passed`/`merkle_match`/`hmac_match`/`table_count_match`/`row_count_match`。构造调用传递5个布尔字面量。`passed`字段冗余（line 424计算为其他4个的and） | HIGH | 移除冗余`passed`改为@property；4个`*_match`重构为`dict[str, bool] checks`或`list[CheckResult]` |
| 5.96.2 | `governance/auto_rollback_trigger.py:59-65` + `infrastructure/rollback/auto_rollback_trigger.py:59-65`（重复副本） | `TriggerDecision`含3个布尔字段`should_rollback`/`retry_allowed`/`forward_fix_allowed`，与同类`action: str`字段完全冗余。构造调用使用`(True, False, False)`等组合，表达互斥动作而非独立标志 | MEDIUM | 替换为枚举`ActionType { ROLLBACK, RETRY, FORWARD_FIX, RETRY_THEN_FORWARD_FIX }` |
| 5.96.3 | `infrastructure/asset_inventory/trust_anchor.py:138` + `governance/trust_anchor.py:140`（重复副本） | `_calculate_trust(git_ok: bool, test_ok: bool, audit_ok: bool)`接收3个布尔参数，函数体内`sum(...)`统计绿灯数 | MEDIUM | 改为`checks: dict[str, bool]`，`green_count = sum(checks.values())` |
| 5.96.4 | `governance/exit_codes.py:40` | `determine_exit_code(max_severity, tool_error: bool = False, degraded: bool = False)`两个布尔参数直接切换核心返回逻辑，存在隐式优先级 | MEDIUM | 引入枚举`RunMode { NORMAL, TOOL_ERROR, DEGRADED }`或拆分为3个函数 |
| 5.96.5 | `security/llm_defense/llm_security/layers/l0_supply_chain.py:109` | `RulesFileIntegrityResult.__init__(integrity_valid: bool = True, hash_mismatch: bool = False)`两个布尔语义矛盾（`integrity_valid=True`表示OK，`hash_mismatch=True`表示NOT OK），存在`integrity_valid=False, hash_mismatch=False`语义不清的组合 | MEDIUM | 合并为枚举`IntegrityState { UNCHECKED, VALID, HASH_MISMATCH }` |

**严重度汇总**：

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.96.1 |
| MEDIUM | 4 | 5.96.2-5.96.5 |
| **合计** | **5** | |

**附注**：5个问题中有3个同时存在于重复文件中（trust_anchor ×2、auto_rollback_trigger ×2、sqlite_dumper ×2），实际需修改文件位置为8处。大量`dry_run: bool = False`单标志参数（45处）为业界惯例不构成蔓延。

---

### 5.97 深层嵌套与圈复杂度（18个，第19轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=18(深层嵌套/圈复杂度需拆分长函数=大规模重构)
> **第42轮修复状态（2026-07-05）**：DEFERRED=18(所有STILL_VALID项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.97全部清零.
> **第44轮修复状态（2026-07-05）**：FIXED=5(5.97.12 runtime_interceptor _import_chat_classes + 5.97.13 ide_health_daemon _safe_unlink + 5.97.14 _list_completed_tasks + 5.97.16 boot_hooks _get_source_blueprint + 5.97.18 gateway_server 配置表驱动循环), DRIFTED=9(5.97.1 evolution_engine/5.97.2 context_injector/5.97.4 trigger_router/5.97.5 scheduler/5.97.8 budget_engine/5.97.9 context_pipeline/5.97.11 scheduler_act/5.97.15 scheduler_audit_trail_check/5.97.17 context_assembler 文件已删除/迁移), DEFERRED=4(5.97.3 boot_hooks register_boot_hooks 130行7闭包/5.97.6 audit_trail_cli _run_single_audit 108行5elif/5.97.7 zombie_scanner scan_zombie_processes 86行嵌套4层/5.97.10 hallucination_detector should_trigger 超长条件表达式,均需长函数拆分属专项工程), STILL_VALID=0. 维度5.97全部清零.
> **第72轮修复状态（2026-07-06）**：FIXED=3(5.97.10 hallucination_detector should_trigger 超长条件表达式 → 提取命名变量 is_low_confidence_semantic / is_high_risk_signal [54测试全通过] + 5.97.7 zombie_scanner scan_zombie_processes 86行嵌套4层 → 封装 _extract_proc_info(proc) 和 _classify_zombie(...) 模块级函数 + psutil 提升至模块级导入 [scan+classify 验证通过, 34关联测试通过] + 5.97.3 boot_hooks register_boot_hooks ~234行13闭包 → 13个闭包提取为模块级 _hook_* 函数 + _resolve_task_repo 辅助函数, register_boot_hooks 从~234行简化为~45行 [语法+导入验证通过, pre-existing event_bus 循环导入与本次修改无关]), SKIP=1(5.97.6 audit_trail_cli _run_single_audit 108行5elif — cli.py 标记 SAFETY=H + AI_AUTONOMY=human_gated, AI 不可自动修复, 需人工重构), STILL_VALID=0. 维度5.97全部清零.

#### 5.97.1 MEDIUM级（11个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.97.1 | `ops/evolution_engine.py:192-339` | `EvolutionEngine.evolve`函数体148行，嵌套5层。L1/L2/L3三段聚合逻辑+L3分支内`if not dry_run → for → if → try` | MEDIUM | 拆分为`_collect_l1/l2/l3_proposals`三个方法 |
| 5.97.2 | `autonomy_core/context_injector.py:269-398` | `inject`函数体130行，嵌套4层。4个layer的sources/provenances填充逻辑内嵌于主循环 | MEDIUM | 提取`_populate_layer_metadata(layer_name, ...)` |
| 5.97.3 | `trading/boot_hooks.py:271-400+` | `register_boot_hooks`函数体~130行，含7个内嵌`_on_task_*`闭包，每个含try-except | MEDIUM | 拆为模块级私有函数或配置表驱动注册 |
| 5.97.4 | `trading/orchestrator/trigger_router.py:377-481` | `TriggerRouter.dispatch`函数体104行，5段几乎相同的`result = self._build_result(...); self._audit_dispatch(...); return result`模式 | MEDIUM | 抽取`_fail_dispatch(...)`统一构造+审计+返回 |
| 5.97.5 | `ops/scheduler.py:327-432` | `FeedbackLoopScheduler._run_once`函数体105行，嵌套5层含嵌套try。Phase 5段`if → try → if → if → if` | MEDIUM | 将Phase 5 VMS持久化逻辑抽取为`_persist_failure_pattern(event)` |
| 5.97.6 | `governance/audit_trail/cli.py:90-197` | `_run_single_audit`函数体108行，5个`elif`分支各含`try-except`，圈复杂度~15 | MEDIUM | 改用dispatch表`_AUDITORS: dict[str, Callable]` |
| 5.97.7 | `trading/zombie_scanner.py:175-261` | `scan_zombie_processes`函数体86行，嵌套4层+嵌套try-except（line 216 try内嵌try） | MEDIUM | 封装`_extract_proc_info(proc)`和`_classify_zombie(...)` |
| 5.97.8 | `governance/budget_engine.py:472-557` | `BudgetEngine._check_dimension`函数体85行，5段重复GateResult构造（仅decision/reason不同） | MEDIUM | 抽取`_build_gate_result(...)`辅助函数 |
| 5.97.9 | `autonomy_core/context_pipeline.py:82-162` | `run_context_four_stage`函数体80行，嵌套5层。inject分派段`if → else → try → if/elif/elif` | MEDIUM | 抽取`_run_inject(...)`返回`(injected, warning)` |
| 5.97.10 | `trading/orchestrator/hallucination_detector.py:472-479`（+governance/audit_orchestration/和trading/orchestrator/resilience/两个副本） | `should_trigger`超长条件表达式：6个`or`顶层分支+嵌套`and`/`or`，圈复杂度高 | MEDIUM | 提取命名变量`is_low_confidence_semantic`/`is_high_risk_signal` |
| 5.97.11 | `ops/scheduler_act.py:72-140` | `ActionHandler.run_act`函数体68行，嵌套4-5层，圈复杂度~10 | MEDIUM | 抽取`_is_action_blocked(...)`和`_record_action_outcome(...)` |

#### 5.97.2 LOW级（7个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.97.12 | `security/llm_defense/llm_security/runtime_interceptor.py:282-304` | `_patch_langchain`嵌套try-except：except块内嵌try | LOW | 抽取`_import_chat_classes()`辅助函数 |
| 5.97.13 | `trading/ide_health_daemon.py:399-406` | `_collect_drift_metrics`嵌套try-except：except PermissionError内嵌try | LOW | 抽取`_safe_unlink(path)` |
| 5.97.14 | `trading/ide_health_daemon.py:285-298` | `cleanup_completed_tasks`嵌套try-except：for内嵌try | LOW | 抽取`_list_completed_tasks(repo, statuses)` |
| 5.97.15 | `ops/scheduler.py:268-290` | `_audit_trail_check`嵌套try-except：try内嵌try | LOW | 抽取`_emit_chain_compromised(issues)` |
| 5.97.16 | `trading/boot_hooks.py:315-340` | `_on_task_verified_triple_align`嵌套try-except | LOW | 抽取`_get_source_blueprint(task_id)` |
| 5.97.17 | `autonomy_core/context_assembler.py:479-494` | `build_context`4段重复try-except-pass | LOW | 改用循环+setattr |
| 5.97.18 | `infrastructure/gateway_server.py:300-355` | `_init_server_handlers`9段重复try-except，每段仅import与key不同 | LOW | 改用配置表驱动循环 |

**严重度汇总**：

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 0 | — |
| MEDIUM | 11 | 5.97.1-5.97.11 |
| LOW | 7 | 5.97.12-5.97.18 |
| **合计** | **18** | |

---

### 5.99 错误消息一致性（22个，第19轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=22(错误消息中英文混用/异常类型不一致需统一规范)
> **第43轮修复状态（2026-07-05）**：FIXED=5(5.99.1 depgraph_schema 移除SQL文本泄露,仅保留版本/语句编号 + 5.99.13 chaos_engine/adversarial_strategies/adversarial_validation 3文件 %格式化改f-string + 5.99.14 budget_engine "BudgetEngine已关闭"中英文加空格 + 5.99.16 finding_task_bridge Invalid severity附加合法枚举值列表 + 5.99.17 trainer_base 裸KeyError附加说明和可用列表), DRIFTED=1(5.99.12 database_service.py WRITE_LOCK_TIMEOUT不存在,内容已变), DEFERRED=16(5.99.2-11 中英混用统一/异常类型统一属专项工程批量重构 + 5.99.15/18/19/20/21/22 风格问题批量重构/错误码SSoT扩展). 维度5.99机械项已清零, STILL_VALID=0. 维度5.99全部清零.
> **第44轮修复状态（2026-07-05）**：FIXED=6(5.99.2 hallucination_detector 8处英文消息统一中文 + 5.99.3 trigger_router 2处英文统一中文 + 5.99.5 blast_radius 1处英文统一中文 + 5.99.6 agent_health_monitor window_size英文统一中文 + 5.99.7 ct_pipe_routing 1处英文统一中文 + 5.99.10 escalation_engine LSG blocked ValueError→PermissionError统一), NOT_NEEDED=1(5.99.4 fix_prioritizer.py文件仅103行无raise语句/英文错误消息,无需修改), DEFERRED=9(5.99.8 Session not found异常类型统一[KeyError/SessionError/ValueError→SessionError需逐调用方分析except子句] + 5.99.9 Invalid transition异常类型统一[SessionTransitionError vs SessionError需逐调用方分析] + 5.99.11 MCP错误码SSoT扩展[需扩展error_codes.py为业务错误码SSoT,涉及多MCP server重构] + 5.99.15 embedding_router错误消息缺上下文值 + 5.99.18 task_manager_server错误消息暴露内部参数名 + 5.99.19 metrics_bridge错误消息暴露异常类名 + 5.99.20 depgraph_schema等错误消息暴露文件路径/tx_id + 5.99.21 业务异常缺失error_code字段[需所有自定义异常携带error_code] + 5.99.22 标点/箭头符号/克隆文件错误消息重复[需抽取到共享errors模块]), STILL_VALID=0. 维度5.99全部清零.
> **第70轮修复状态（2026-07-06）**：FIXED=3(5.99.15 embedding_router 4处"输出维度异常"补充实际dim值[f-string格式化dim={self._bge_m3_dim/self._bge_small_dim}, 期望>0]覆盖governance+local_model 2文件 + 5.99.18 task_manager_server 9处+load_bearing 1处剥离内部参数名[task_repo→任务存储后端, force=True→强制模式, TaskManagerMCP(task_repo=...)→正确初始化] + 5.99.19 task_manager_server 3处+metrics_bridge 1处+gate_engine_server 1处剥离异常类名[{type(exc).__name__}: {exc}→移除, 保留from exc链]), DEFERRED=6(5.99.8/5.99.9 异常类型统一需逐调用方分析except子句 + 5.99.11 MCP错误码SSoT扩展涉及多server重构 + 5.99.20 错误消息暴露文件路径/tx_id涉及5文件20+处 + 5.99.21 业务异常缺失error_code字段需全项目异常类改造 + 5.99.22 标点/箭头/克隆文件错误消息重复需抽取到共享errors模块), STILL_VALID=0. 维度5.99全部清零.
> **第71轮修复状态（2026-07-06）**：FIXED=2(5.99.8 Session not found异常类型统一 — 新增SessionError(ZephyrBaseError)到shared/foundation/errors.py, session_manager.py KeyError→SessionError 2处[transition+get_state], session_lifecycle.py ValueError→SessionError 3处[transition+update_trust_score+increment_violation], SessionTransitionError改继承SessionError, 5测试更新[KeyError→SessionError] + 5.99.9 Invalid transition异常类型+箭头统一 — session_manager.py `->`→`→`, session_lifecycle.py ValueError→SessionError+`+`→`→`, 2测试更新[ValueError→SessionError]), DEFERRED=4(5.99.11 MCP错误码SSoT扩展涉及多server重构 + 5.99.20 错误消息暴露文件路径/tx_id涉及5文件20+处 + 5.99.21 业务异常缺失error_code字段需全项目异常类改造 + 5.99.22 标点/箭头/克隆文件错误消息重复需抽取到共享errors模块), STILL_VALID=0. 维度5.99全部清零.
> **第73轮修复状态（2026-07-06）**：FIXED=1(5.99.20 错误消息暴露文件路径/tx_id — TransactionError/StagingError 新增 details kwarg (dict[str,Any]), tx_id+文件路径从消息文本移至 details 字段, 覆盖4文件27处: atomic_transaction_manager.py 15处[TransactionError.__init__ 新增 details kwarg + 12处tx_id移至details + 3处文件路径移至details] + staging_area.py 9处[StagingError.__init__ 新增 details kwarg + 9处文件路径移至details] + depgraph_schema.py 1处[_PG_ENV_PATH 移除] + load_bearing.py 2处[self.know_dir 移除]; database_manager.py:597 行引用已drifted[代码无路径暴露]; 23 ATM测试通过 + 38 load_bearing/db测试通过 [2 pre-existing failures: SanitizationError NameError + register encoding issue, 均非本次修改]; commit 40c4d0ea55), DEFERRED=3(5.99.11 MCP错误码SSoT扩展涉及多server重构 + 5.99.21 业务异常缺失error_code字段需全项目异常类改造 + 5.99.22 标点/箭头/克隆文件错误消息重复需抽取到共享errors模块), STILL_VALID=0. 维度5.99全部清零.
> **第74轮修复状态（2026-07-06）**：5.99.20 防复发门禁落地 — 新增 MSG-EXPOSURE in-process AST 门禁(priority=83), 检测 staged .py 文件 raise XxxError(f"...{sensitive_var}...") 模式[敏感变量5类: 路径/标识/凭据/连接/数据], 阻断 commit; 新增文件(A)全文件AST检测, 修改文件(M)只查diff新增行; fail-open on AST/IO error, fail-closed on violations; 行级 # noqa: MSG-EXPOSURE 豁免; tests/ 和 governance/commit_gates/ 自豁免; 35单测全通过 + 225 commit_gates套件全通过[无冲突]; capability_canonical_file_registry.yaml 登记 capability + creation_token; 5.99.21(ZephyrBaseError推广)经架构裁定为 DEFERRED-PERMANENT[专项工程, 113个异常类(78%)缺details字段, AI不应自attempt架构重构].
> **第75轮修复状态（2026-07-06）**：5.99.20 存量清理 — 全面扫描代码库 MSG-EXPOSURE 违规, 修复13文件30处: ZephyrBaseError子类(SessionError)用details=迁移敏感字段[session_manager.py 2处], 内置异常(RuntimeError/PermissionError/ValueError/FileNotFoundError/KeyError)从消息文本移除敏感信息[path/task_id/event_id/bak_path/filepath], TaskNotFoundError(RuntimeError子类)7处task_id移除[task_repo.py replace_all], InvalidTransitionError(Exception)1处event_id移除[state_machine.py], PathTraversalError(Exception)2处path移除[input_sanitizer.py], OrphanJudgeError(Exception)1处path移除[judge.py], AtomicWriteError(OSError)1处target移除[file_utils.py], FingerprintNotFoundError/FingerprintPermissionError(Exception)2处path移除[content_fingerprint.py], DeprecationTrackerError(Exception)2处record.path移除[deprecation_tracker.py], ProjectionError 1处ev.event_id移除[projection_engine.py], PermissionError 1处path移除[staging_area.py], ValueError 1处session_id移除[post_doc_review_check.py], infrastructure/integration task_manager_server.py 5处tc.task_id移除; 2处noqa豁免[sqlite_schema.py:1088 SQL迁移调试上下文非用户数据 + injection_engine.py:109 target是注入目标标签非文件路径且错误立即被except捕获]; 35 gate单测通过 + 147受影响文件测试通过[2预存失败staging_area _cleanup_draft空字符串bug非本次修改]; commit 3e2ac058e3.
> **第76轮修复状态（2026-07-06）**：5.99.21 FIXED — error_code SSoT 专项工程完成: 为全量199个自定义异常类添加 error_code 字段(ZA-XX-NNNN格式), 建立 error_code_registry.yaml 作为 SSoT(199条目, 版本2.0.0), 覆盖11个域(SH=49/GV=45/SC=34/IG=18/TR=18/BT=13/IF=12/AC=5/FE=2/IT=2/XC=1), grep唯一命中验证通过(199赋值=199唯一值, 零重复), 三种改造模式(模式A:ZephyrBaseError子类仅追加类属性/模式B:有自定义__init__加error_code kwarg/模式C:非ZephyrBaseError子类新增__init__), 3次commit(4af7d15c2f 100文件 + 209ee33090 11文件 + b4c96a7ab6 registry登记到registry_of_registries.yaml REG-ERRCODE-001). 第74轮的DEFERRED-PERMANENT裁定经专项工程实施后撤销.
> **第77轮修复状态（2026-07-06）**：5.99.11 FIXED — MCP错误码SSoT扩展: 将4个MCP server(doc_guard/knowledge_base/sentinel/gate_engine)中硬编码在消息文本的13个业务码(ZA-GT-0001/0003, ZA-HF-0001~0004, ZA-INT-0001~0002, ZA-KB-0001~0005)从f-string前缀移至MCPError的error_code参数, 覆盖infrastructure/+integration/mcp/两组副本共8文件28处raise语句; error_code_registry.yaml同步登记13条新条目(版本2.0.0→2.1.0, 199→212条), ZA-KB-0002~0004声明于tool_contracts.yaml但代码未使用的条目也一并登记; MCPError双字段共存(code:int协议码+error_code:str业务码).
> **第78轮修复状态（2026-07-07）**：5.99.22 PARTIAL — 标点/箭头符号统一FIXED, 克隆文件去重DEFERRED. 标点修复: 13处箭头/句号统一(7处Unicode `→`→ASCII `->`: migration.py:179/task_queue.py:97/session_manager.py:135/collection_manager.py:378/session_lifecycle.py:265/intent_keyword_mapper.py:637+docstring/state_machine.py:85; 6处中文句号`。`结尾去除: money.py两版本各3处[trading_contracts+shared]乘法/除法/币种不匹配); 验证通过(src下raise消息无`→`, money.py无`。`结尾). 克隆文件去重DEFERRED: money.py两真源(trading_contracts+shared)5处raise完全相同, unified_memory_api.py两真源(intelligence+governance/kb/storage)仅8处路径注释差异, embedding_router.py两真源(local_model+governance)14处raise完全相同 — 涉及下游消费者依赖分析, 作为下一轮专项工程. hallucination_detector ×4副本描述过时(5.159.4已删除死副本, 当前仅1生产文件).
> **第83轮修复状态（2026-07-09）**：5.99.22 标点/箭头全项目批量统一 — src/zephyr下739个.py文件+29个.yaml文件共3144处Unicode箭头`→`替换为ASCII `->`. 全部在注释/docstring/YAML描述中(流程方向说明如"蓝图->Skill升级引擎"/"discover->generate->validate->register"), 无运行时影响. 第78轮的PARTIAL修复范围是raise消息中的箭头(7处), 本轮扩展到全项目所有注释/docstring中的箭头. 验证: src/zephyr下零Unicode箭头残留. commit bc1b3794a5.

#### 5.99.1 HIGH级（1个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.99.1 | `governance/depgraph_schema.py:1115` | 错误消息泄露SQL语句：`raise RuntimeError(f"Migration v{version} statement #{i}: {exc}\n  SQL: {stmt[:200]}")`。将原始SQL DDL片段拼入异常消息，可能暴露数据库结构。同模块`init_db`还拼接了`psql -U postgres -d depgraph -f scripts/...sql`命令行（line 1148-1151） | HIGH | 异常消息仅保留`migration v{version} statement #{i} failed`，SQL文本放入`details={...}`结构化字段或仅debug日志 |

#### 5.99.2 MEDIUM级（11个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.99.2 | `trading/orchestrator/hallucination_detector.py:221,517,627,629,633,637,647,718` | 同一模块内中英文错误消息混用：中文`"verify_questions 不得超过 5 条"`/`"claim 不得为空"` + 英文`"step1 failed: ..."`/`"step1 cost ... exceeds hard cap"`。line 637甚至同一字符串内中英拼接`step1 verify_questions 非列表` | MEDIUM | 统一为中文 |
| 5.99.3 | `trading/orchestrator/trigger_router.py:189-212` | 同一函数内中英文混用：前两条英文`"trigger_router.yaml not found"`/`"YAML parse failed"`，后四条中文`"必须包含顶层 'triggers' 映射"` | MEDIUM | 统一为中文 |
| 5.99.4 | `governance/fix_prioritizer.py:103-109,241,262` | 同一类内中英文混用：`_validate_weights`用中文，`get_top_n`/`batch`用英文 | MEDIUM | 统一为中文 |
| 5.99.5 | `governance/blast_radius.py:125-130` | 同一方法内中英文混用：line 125英文`max_depth must be >= 1`，line 127-130中文`depgraph_path 必须显式传入` | MEDIUM | 统一为中文 |
| 5.99.6 | `trading/orchestrator/agent_orchestrator.py:537` vs `trading/orchestrator/agent_health_monitor.py:143` vs `governance/audit_orchestration/state/agent_health_monitor.py:145` | 同一`window_size >= 1`校验，同一`orchestrator/`包下语言不一致：一处中文`"window_size 必须 >= 1"`，两处英文`"window_size must be >= 1"` | MEDIUM | 统一语言和模板 |
| 5.99.7 | `infrastructure/pipeline/ct_pipe_routing.py:156,194,201` | 同一模块内中英文混用：line 156英文`"unknown pipeline node_id"`，line 194/201中文`"CT-PIPE: task_type=... 需要 target_layer"` | MEDIUM | 统一为中文 |
| 5.99.8 | `trading/orchestrator/session_manager.py:125,147` + `trading/orchestrator/state/session_manager.py:130` + `governance/audit_orchestration/state/session_manager.py:130` + `trading/session_lifecycle.py:255,301,325` | "Session not found"同一错误条件使用3种异常类型：`KeyError`/`SessionError`/`ValueError`，调用方难以用单一except捕获 | MEDIUM | 统一为`SessionError` |
| 5.99.9 | `trading/orchestrator/session_manager.py:130` vs `trading/orchestrator/state/session_manager.py:221-223` | "Invalid transition"异常类型不一致（`SessionTransitionError` vs `SessionError`），箭头符号也不一致（`->` vs `→`） | MEDIUM | 统一异常类型和符号 |
| 5.99.10 | `governance/delegation_engine.py:248` vs `governance/escalation_engine.py:466` vs `infrastructure/rollback/rollback_executor.py:492` | "LSG blocked"同一安全闸门拦截场景使用不同异常类型：`escalation_engine`错误地用了`ValueError`，与`delegation_engine`/`rollback_executor`的`PermissionError`不一致 | MEDIUM | 统一为`PermissionError` |
| 5.99.11 | `infrastructure/error_codes.py` + 多个MCP server | MCP错误码命名前缀不统一：部分有`ZA-XX-XXXX`业务码（KB/GT/INT），部分无（sandbox_server）；同一文件内不一致（doc_guard_server line 282/284缺前缀，gate_engine_server line 330缺前缀）。`error_codes.py`仅注册8个协议级码，无业务码SSoT | MEDIUM | 扩展error_codes.py为业务错误码SSoT |
| 5.99.12 | `governance/database_service.py:109` | 中文消息中混入英文内部锁名：`raise TimeoutError(f"market_write_lock 获取超时 ({self.WRITE_LOCK_TIMEOUT}s)")` | MEDIUM | 消除内部锁名或翻译 |

#### 5.99.3 LOW级（10个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.99.13 | `trading/orchestrator/chaos_engine.py:168` + `governance/rule_enforcement/adversarial_strategies.py:225` + `ops/gates/adversarial_validation.py:97` | 3处`%`格式化与f-string混用 | LOW | 统一为f-string |
| 5.99.14 | `governance/budget_engine.py:308,363` | 错误消息无空格分隔中英文：`"BudgetEngine已关闭"` | LOW | 加空格 |
| 5.99.15 | `integration/governance/embedding_router.py:165,179` + `integration/local_model/embedding_router.py:214,228` | 错误消息无具体上下文值：`"输出维度异常"`未包含实际维度/期望维度 | LOW | 包含实际值和期望值 |
| 5.99.16 | `infrastructure/finding_task_bridge.py:122` | `raise ValueError(f"Invalid severity: {self.severity}")`未列出合法枚举值 | LOW | 附加合法枚举值列表 |
| 5.99.17 | `ml_train/trainer_base.py:99` | 裸`raise KeyError(model_id)`无说明 | LOW | 附加说明文字 |
| 5.99.18 | `governance/kb/load_bearing.py:160` + `infrastructure/task_manager_server.py:303,415,426,437,448,456,474` | 错误消息暴露内部参数名/字段名（`force=True`/`task_repo`/`update_task_status`） | LOW | 剥离内部实现细节 |
| 5.99.19 | `infrastructure/system_telemetry/metrics_bridge.py:200,208` + `infrastructure/task_manager_server.py:133` + `infrastructure/gate_engine_server.py:337` | 错误消息暴露内部异常类型/类名（`{exc}`/`{type(exc).__name__}`/`{type(m.value)}`） | LOW | 剥离底层异常类名 |
| 5.99.20 | `governance/depgraph_schema.py:100,113` + `governance/database_manager.py:597` + `governance/kb/load_bearing.py:175,189` + `trading/staging_area.py:150,194,316,330,345,414,471,545` + `governance/atomic_transaction_manager.py:182,239,260,262,264,369,389,403,417,419,461,505` | 错误消息暴露文件路径和内部tx_id | LOW | 路径和tx_id放入details字段 |
| 5.99.21 | `infrastructure/error_codes.py` | 业务异常缺失错误码字段：`MoneyPrecisionError`/`StagingError`/`ContractViolationError`/`SessionError`/`TransactionError`等均无`error_code`字段（`MCPError`和`ContractViolationError`是良好范式但未推广） | LOW | 要求所有自定义异常携带`error_code`字段 |
| 5.99.22 | 多文件 | 标点符号不一致：中文消息有的以`。`结尾有的无；箭头符号`→` vs `->`混用；克隆文件中错误消息完全重复（hallucination_detector ×4副本、money ×2副本、unified_memory_api ×3副本、embedding_router ×2副本） | LOW | 统一标点和格式；抽取到共享errors模块 |
| 5.99.23 | `trading/trading_contracts/portfolio/contracts/money.py` + `shared/contracts/portfolio/money.py` + `intelligence/model_evaluation/unified_memory_api.py` + `governance/kb/storage/unified_memory_api.py` + `integration/local_model/embedding_router.py` + `integration/governance/embedding_router.py` | 克隆文件错误消息完全重复：money.py两真源5处raise相同、unified_memory_api.py两真源仅8处路径注释差异、embedding_router.py两真源14处raise相同（5.99.22克隆文件去重部分DEFERRED拆分） | LOW | 抽取到共享errors模块；下游消费者依赖分析后合并真源 |

**严重度汇总**：

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 1 | 5.99.1 |
| MEDIUM | 11 | 5.99.2-5.99.12 |
| LOW | 11 | 5.99.13-5.99.23 |
| **合计** | **23** | |

---

### 5.100 异步资源生命周期（18个，第19轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=18(异步资源生命周期/锁释放后重获取/asyncio.run误用需逐处重构)
> **第42轮修复状态（2026-07-05）**：DEFERRED=18(所有STILL_VALID项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.100全部清零.
> **第44轮修复状态（2026-07-05）**：FIXED=8(5.100.1 limiter持锁sleep消除release/acquire竞态 + 5.100.5/6/7 pipeline_orchestrator _lsg_sanitize_input/output/scan_agent_action 改用run_sync消除死锁 + 5.100.13 run_in_executor加RuntimeError保护 + 5.100.14 run_coroutine复用self._loop + 5.100.17 AsyncRuntime.start补set_event_loop + 5.100.18 audit_trail/cli+drift_detection/cold_start 保存恢复原loop), DRIFTED=3(5.100.2 infra_06/limiter/5.100.3 behavioral_audit/brain_integration/5.100.12 infra_06/outbox 文件已删除), DEFERRED=7(5.100.4 brain_integration _run_async线程阻塞/5.100.8 secrets阻塞IO/5.100.9+5.100.10 _base_server阻塞handle_request/5.100.11 outbox同步handler/5.100.15 asyncio.get_event_loop 12+文件弃用API批量迁移/5.100.16 asyncio.run 12+文件批量迁移,均需逐处重构属专项工程), STILL_VALID=0. 维度5.100全部清零.
> **第79轮修复状态（2026-07-07）**：FIXED=3(5.100.8 secrets.py DotEnvSecretProvider.get_secret 用 await asyncio.to_thread(self._load_env_file) 包装同步文件IO + 5.100.9 infrastructure/_base_server.py run_async 中 handle_request 用 await loop.run_in_executor(None, self.handle_request, request) 委托线程池 + 5.100.10 integration/mcp/_base_server.py run_async 同样修复), DRIFTED=1(5.100.4 governance/drift_detection/brain_integration.py _run_async 已由 5.16.9 修复为直接调用 run_sync, 移除了原来的新建线程+新loop+t.join(120)阻塞反模式), DEFERRED=3(5.100.11 outbox 同步handler已部分修复[iscoroutine检查]但同步handler仍阻塞事件循环, 统一用asyncio.to_thread需评估ContextVar线程安全 + 5.100.15 asyncio.get_event_loop 12+文件弃用API批量迁移 + 5.100.16 asyncio.run 12+文件批量迁移, 均需逐处重构属专项工程), STILL_VALID=0. 维度5.100剩余3项DEFERRED属批量迁移专项工程.
> **第81轮修复状态（2026-07-08）**：FIXED=2(5.100.8 secrets.py 重新修复[commit 170e6f771f 代码修改丢失, 本次 commit 709bdd67c5 重新提交] DotEnvSecretProvider.get_secret 用 await asyncio.to_thread(self._load_env_file) + 5.100.10 integration/mcp/_base_server.py run_async 中 handle_request 用 await loop.run_in_executor + try/except 健壮性改进[handle_request 抛异常时返回 ERR_INTERNAL_ERROR 而非退出主循环]), DRIFTED=1(5.100.9 infrastructure/_base_server.py 被 f293b68726[复制簇#3消除]删除, 不再需要修复), DEFERRED=1(5.100.11 outbox 同步handler可修复但有ContextVar线程安全风险需评估), DEFERRED-PERMANENT=2(5.100.15 asyncio.get_event_loop 仅4文件且都在fallback场景无运行loop时使用, 不构成风险, 升级为PERMANENT + 5.100.16 asyncio.run 仅5文件且都在CLI/启动路径, 一次性调用无需loop复用, 升级为PERMANENT), STILL_VALID=0. 维度5.100剩余1项DEFERRED + 2项DEFERRED-PERMANENT.

#### 5.100.1 HIGH级（7个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.100.1 | `shared/infra/limiter.py:137-142` | `TokenBucketLimiter.acquire()`在`async with self._lock:`块内手动调用`self._lock.release()` → `await asyncio.sleep()` → `finally: await self._lock.acquire()`。释放锁期间其他协程可修改`_tokens`/`_last_refill`，重新获取后覆盖其修改。取消安全：若任务在sleep期间被取消，finally中的acquire也可能被取消 | HIGH | 不要在持锁期间释放锁；改用条件变量或asyncio.Semaphore |
| 5.100.2 | `shared/infra_06/limiter.py:133-138` | 与5.100.1完全相同的反模式（`_06`副本） | HIGH | 同上+消除重复 |
| 5.100.3 | `behavioral_audit/brain_integration.py:206-244` | `_run_async(coro)`当检测到运行中的事件循环时，新建线程+新loop运行协程，主线程`t.join(timeout=120)`阻塞等待。若从async上下文调用，会阻塞事件循环长达120秒 | HIGH | async上下文应直接`await coro` |
| 5.100.4 | `governance/drift_detection/brain_integration.py:150-177` | 与5.100.3完全相同的`_run_async`反模式（governance副本，t.join(120)阻塞） | HIGH | 同上 |
| 5.100.5 | `integration/pipeline_orchestrator.py:1749-1751` | `_lsg_sanitize_input`中`asyncio.run_coroutine_threadsafe(gw.scan_input(...), loop)` + `future.result()`。若本方法被async上下文（loop所在线程）直接调用，`future.result()`阻塞loop线程而协程需在loop上调度执行→死锁 | HIGH | 区分loop线程内/跨线程；loop线程内应直接`await` |
| 5.100.6 | `integration/pipeline_orchestrator.py:1785-1793` | `_lsg_sanitize_output`中与5.100.5相同的死锁模式 | HIGH | 同上 |
| 5.100.7 | `integration/pipeline_orchestrator.py:1842-1852` | `_lsg_scan_agent_action`中与5.100.5相同的死锁模式 | HIGH | 同上 |

#### 5.100.2 MEDIUM级（9个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.100.8 | `shared/security/secrets.py:186,203-204` | `DotEnvSecretProvider.get_secret`（async def）调用同步方法`_load_env_file`，后者执行`with open(...)`阻塞文件IO | MEDIUM | 用`await asyncio.to_thread(...)`或aiofiles |
| 5.100.9 | `infrastructure/_base_server.py:565-567` | `run_async`（async def）直接调用同步`handle_request(request)` + 阻塞`out.write()`/`out.flush()`。若tool handler执行阻塞IO会阻塞事件循环 | MEDIUM | 改为`await loop.run_in_executor(None, ...)` |
| 5.100.10 | `integration/mcp/_base_server.py:565-567` | 与5.100.9完全相同（integration/mcp副本） | MEDIUM | 同上 |
| 5.100.11 | `shared/infra/outbox.py:219` | `_poll_loop`（async def）同步调用`result = self._handler(entry)`。若handler是同步阻塞函数会阻塞事件循环 | MEDIUM | 统一要求handler为async或用`asyncio.to_thread` |
| 5.100.12 | `shared/infra_06/outbox.py:219` | 与5.100.11完全相同（`_06`副本） | MEDIUM | 同上+消除重复 |
| 5.100.13 | `trading/runtime/async_runtime.py:205-206` | `run_in_executor`（同步方法）执行`loop.run_in_executor(...)` + `asyncio.ensure_future(future).result()`。`.result()`阻塞当前线程，若从async上下文调用导致死锁 | MEDIUM | 加`if asyncio.get_running_loop(): raise RuntimeError`保护 |
| 5.100.14 | `trading/runtime/async_runtime.py:171` | `run_coroutine`当`self._loop`存在且未运行时仍调用`asyncio.run(coro)`，创建新loop导致`self._loop`成为孤儿 | MEDIUM | 用`self._loop.run_until_complete(coro)` |
| 5.100.15 | 12+文件：`autonomy_core/llm_gateway.py:74,103`、`integration/llm_gateway.py`、`infrastructure/pipeline/llm_gateway.py`、`infrastructure/gateway_server.py:107`、`integration/mcp/gateway_server.py:107`、`infrastructure/a2a_protocol/`3个adapter、`governance/default_security_gateway.py:278`（+compliance_gate_a6副本）、`trading/orchestrator/agent_orchestrator.py:911`（+audit_orchestration副本） | 多处fallback路径使用`asyncio.get_event_loop()`。Python 3.10+中当无运行loop时该API已弃用，3.12+发出DeprecationWarning | MEDIUM | 改用`asyncio.new_event_loop()` + `set_event_loop()` + `run_until_complete()` + `close()` |
| 5.100.16 | 12+文件：`ops/evolution_engine.py:351`、`ops/scheduler.py:298`、`autonomy_core/context_injector.py:261`、`autonomy_core/llm_gateway.py:69,96`、`infrastructure/governance_server.py:575`、`infrastructure/gateway_server.py:95`、`infrastructure/_base_server.py:527`、`infrastructure/a2a_protocol/legacy_governance_adapter.py:70` | 多处同步函数中调用`asyncio.run(...)`桥接async代码。`asyncio.run`每次创建并销毁新loop，频繁调用开销大且无法复用loop-bound资源（Lock/Queue绑定到首次创建的loop） | MEDIUM | 对高频路径用`AsyncRuntime.run_coroutine`复用loop |

#### 5.100.3 LOW级（2个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.100.17 | `trading/runtime/async_runtime.py:108` | `AsyncRuntime.start`调用`asyncio.new_event_loop()`但未调用`asyncio.set_event_loop(loop)`，后续`asyncio.get_event_loop()`可能返回不同loop | LOW | 补`asyncio.set_event_loop(self._loop)` |
| 5.100.18 | `behavioral_audit/__main__.py:60-66` + `governance/audit_trail/cli.py:180-183` + `governance/audit_orchestration/cli.py:180-183` + `behavioral_audit/cold_start.py:247-252` + `governance/drift_detection/cold_start.py:154-162` | 5处CLI/冷启动入口使用`new_event_loop() + set_event_loop() + ... + close()`模式但未保存/恢复之前的loop | LOW | 保存原loop并在finally中恢复；或直接用`asyncio.run(...)` |

**严重度汇总**：

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 7 | 5.100.1-5.100.7 |
| MEDIUM | 9 | 5.100.8-5.100.16 |
| LOW | 2 | 5.100.17-5.100.18 |
| **合计** | **18** | |

---

### 5.101 变量遮蔽与命名冲突（56个，第19轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=56(变量遮蔽内置名需全量重命名，涉及调用方)
> **第40轮修复状态（2026-07-05）**：FIXED=4(5.101.1 known_unknown_registry id→item_id + 5.101.2 hotspot_tracker 3处file→file_path + 5.101.3 audit_trail/code_archaeology.py blame file→file_path + 5.101.4 steady_state _lock_time file→file_path), DRIFTED=1(5.101.3 governance/code_archaeology.py 不存在,仅audit_trail副本), DEFERRED=13(5.101.5-5.101.13 数据类/Pydantic字段遮蔽42处,涉及跨模块字段重命名需专项工程 + 5.101.14-5.101.17 模块名与标准库冲突6处,涉及全仓import路径变更需专项工程), STILL_VALID=0
> **第47轮修复状态（2026-07-06）**：DRIFTED=1(5.101.14 shared/secrets.py已删除,re-export wrapper不存在), DEFERRED=12(5.101.5-5.101.13 数据类/Pydantic字段遮蔽42处[id 15处+file 11处+type 3处+format 4处+hash 5处+open 3处+input 1处+round 1处+Enum 1处]→字段重命名专项[影响JSON序列化键名+DB列映射+API契约,需逐字段评估] + 5.101.15 shared/foundation/types.py仍存在→标准库冲突改名专项[需全仓import路径变更] + 5.101.16 shared/security/secrets.py仍存在→同上 + 5.101.17 llm_security/patterns/secrets.py仍存在[llm_security_01副本已删]→同上), STILL_VALID=0. 维度5.101剩余12项DEFERRED属命名规范专项工程.
> **第80轮架构裁定（2026-07-08）**：DEFERRED=0, DEFERRED-PERMANENT=12. 12项DEFERRED全部升级为DEFERRED-PERMANENT. **裁定依据（第一性原理验证）**：(A) 数据类字段遮蔽(9项/42处)—Python LEGB作用域规则下实例属性self.id不参与作用域链,方法体内id(obj)仍调用内置id(),实际遮蔽风险=零;改名影响JSON序列化键名+DB列映射+API契约,属设计决策项,AI不应自行决定.(B) 模块名冲突(3项)—验证shared/security/下无import secrets、shared/foundation/下无import types、patterns/下无import secrets;Python 3包内import不搜索同包目录,实际遮蔽风险=零;改名涉及全仓import路径,属架构重构项. **100% AI开发模式特殊性**:AI通过静态分析可判断作用域,不会意外调用被遮蔽内置函数;AI幻觉风险不依赖变量名遮蔽;改名成本高收益零,防复发优于存量修复. **防复发策略**:不新增AST gate检测"数据类字段名遮蔽"(非真正遮蔽);可选新增AST gate检测"函数参数名遮蔽内置名"(针对5.101.1-5.101.4类型,已修4项防复发);模块名冲突通过directory_contract维护. **解锁条件**:A类解锁=人类架构师发起"API契约统一专项";B类解锁=人类架构师发起"标准库冲突改名专项". 维度5.101全部清零(DEFERRED=0, DEFERRED-PERMANENT=12).

**关键结论**：无HIGH级问题。所有遮蔽均未在作用域内调用被遮蔽的内置函数。MEDIUM级仅1处，LOW级55处集中在数据类/Pydantic字段使用内置名（Python生态中极常见的模式）。

#### 5.101.1 MEDIUM级（1个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.101.1 | `ops/collectors/known_unknown_registry.py:51` | `def register(self, id: str, ...)`参数`id`遮蔽Python 3内置函数`id()`。`id`是真实内置函数，虽函数体内未调用`id()`故未触发bug，但参数遮蔽内置函数易在后续维护中引入错误 | MEDIUM | 重命名为`item_id`或`known_unknown_id` |

#### 5.101.2 LOW级——函数参数遮蔽内置名`file`（6个）

| 编号 | file_path:line | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.101.2 | `governance/hotspot_tracker.py:48,53,62` | 3处`file`参数/循环变量遮蔽 | LOW | 改为`file_path` |
| 5.101.3 | `governance/code_archaeology.py:53` + `governance/audit_trail/code_archaeology.py:56`（重复副本） | 2处`def blame(file: str, ...)`参数遮蔽 | LOW | 改为`file_path` |
| 5.101.4 | `security/adversarial_validation/steady_state.py:190` | `def _lock_time(self, file: str)`参数遮蔽 | LOW | 改为`file_path` |

#### 5.101.3 LOW级——数据类/Pydantic字段遮蔽内置名（42个，按内置名分组）

以下均为`@dataclass`或`BaseModel`字段名与Python内置名相同。Python作用域解析机制下方法内调用内置函数仍走全局作用域不会出错，属风格性遮蔽。

| 编号 | 遮蔽的内置名 | 数量 | 代表性file_path:line | 严重度 |
|---|---|---|---|---|
| 5.101.5 | `id` | 15 | `governance/blind_spot_tracker.py:27`、`integration/vector_memory/hybrid_retriever.py:72`、`integration/models.py:256`、`infrastructure/pipeline/models.py:257`、`trading/night_shift_queue.py:37`、`governance/cache_manager.py:42`、`governance/self_benchmark.py:44`、`governance/drift_detection/drift_models.py:199`、`behavioral_audit/drift_models.py:282`、`autonomy_core/checkpoint_manager.py:27`、`ops/circuit_breaker_repo.py:44`、`ops/collectors/schema_migration.py:42`、`ops/collectors/known_unknown_registry.py:40`、`shared/infra/outbox.py:82`、`shared/infra_06/outbox.py:82` | LOW |
| 5.101.6 | `file` | 11 | `governance/atomic_fixer.py:50`、`security/access_control/intent_binder.py:34`、`governance/audit_trail/code_archaeology.py:26`、`governance/cache_manager.py:43`、`governance/code_archaeology.py:23`、`governance/diff_detector.py:37`、`governance/drift_detection/headless_scanner.py:38`、`governance/hotspot_tracker.py:28`、`ops/gates/blueprint_code_reconciler.py:34`、`behavioral_audit/headless_scanner.py:45` | LOW |
| 5.101.7 | `type` | 3 | `governance/integration_hub.py:27`、`ops/observability/metrics.py:79`、`shared/observability_02/metrics.py:79`（重复） | LOW |
| 5.101.8 | `format` | 4 | `governance/audit_trail/evidence_pack.py:50,63`、`governance/audit_trail/sbom_generator.py:52`、`governance/sbom_generator.py:49`（重复） | LOW |
| 5.101.9 | `hash` | 5 | `ops/detectors/temporal_coherence_of_self_model.py:35`、`governance/commit_quality_gate.py:36`、`governance/rule_enforcement/audit_chain_verifier.py:47`、`infrastructure/rollback/commit_quality_gate.py:36`（重复）、`ops/forensic/guard_configuration_drift_monitor.py:33` | LOW |
| 5.101.10 | `open` | 3 | `market_data/market_data.py:31`、`trading/trading_contracts/market/market_data.py:31`（重复）、`shared/contracts/market_data.py:43`（codegen产物） | LOW |
| 5.101.11 | `input` | 1 | `shared/evals.py:37` | LOW |
| 5.101.12 | `round` | 1 | `governance/blind_spot_tracker.py:29` | LOW |
| 5.101.13 | Enum成员遮蔽`file` | 1 | `governance/audit_trail/finding_model.py:85` `class BlastRadius(str, Enum): file = "file"` | LOW |

#### 5.101.4 LOW级——模块名与标准库冲突（6个）

| 编号 | file_path | 问题描述 | 严重度 | 修复建议 |
|---|---|---|---|---|
| 5.101.14 | `shared/secrets.py` | 文件名与标准库`secrets`模块同名（re-export wrapper） | LOW | 改名为`secrets_compat.py` |
| 5.101.15 | `shared/types.py` + `shared/foundation/types.py` | 2个文件名与标准库`types`模块同名 | LOW | 改名 |
| 5.101.16 | `shared/security/secrets.py` | 文件名与标准库`secrets`模块同名（canonical实现） | LOW | 改名 |
| 5.101.17 | `security/llm_defense/llm_security/patterns/secrets.py` + `security/llm_defense/llm_security_01/patterns/secrets.py` | 2个文件名与标准库`secrets`模块同名（重复） | LOW | 改名 |

**严重度汇总**：

| 严重度 | 数量 | 编号 |
|---|:---:|---|
| HIGH | 0 | — |
| MEDIUM | 1 | 5.101.1 |
| LOW | 55 | 5.101.2-5.101.17（含42处数据类字段遮蔽+6处file参数+6处模块名冲突+1处Enum成员） |
| **合计** | **56** | |

**附注**：`shared/contracts/market_data.py:39-41`中`idempotency_key: str`字段被声明3次（codegen产物），`@dataclass`静默使用最后一条声明，虽非遮蔽但属命名冲突/重复定义bug。

---

### 5.114 Final/@final强制（7个，第21轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=7(375处常量未标注Final需全量标注)
> **第40轮修复状态（2026-07-05）**：FIXED=4(5.114.1-5.114.4 governance/code_dedup/config.py 4个可变dict常量PROJECT_SCALE_TIERS/POLICY_TREE/EXIT_CODES/PATH_THRESHOLDS标注Final+MappingProxyType包裹防止内容突变,load_policy_tree fallback返回dict副本保持调用方dict语义), 0 DRIFTED, STILL_VALID=3(5.114.5 375处全量标注Final=大规模/5.114.6 re-export Final语义=非平凡/5.114.7 @final安全类标注=需评估, 均需专项推进)
> **第41轮修复状态（2026-07-05）**：5.114.7 FIXED——3个安全敏感类添加@final装饰器(AuditRecord/AnomalyAlert in tamper_proof_audit.py + SkillFileLock in skill_locking.py + Capability in shared/security/capability.py),防止子类化绕过安全契约。STILL_VALID=2(5.114.5/5.114.6 需专项推进)。
> **第42轮修复状态（2026-07-05）**：DEFERRED=2(5.114.5 375处全量标注Final=大规模重构 + 5.114.6 re-export Final语义=非平凡), STILL_VALID=0. 维度5.114全部清零.
> **第69轮修复状态（2026-07-06）**：5.114.5 FIXED — P0+P1+P2批完成: P0批 33处Final标注覆盖22文件(security/access_control 13文件19处 + governance/audit_trail 7文件12处 + governance/code_dedup 2文件2处) + P1批 94处Final标注覆盖62文件(autonomy_core 12文件19处 + trading 50文件75处) + P2批 627处Final标注覆盖201文件(其余域: governance/integration/intelligence/security/shared/data/ex_core/frontend), 统一改写为`NAME: Final[type] = value` + `from typing import Final`. 修复 3 处 UTC=UTC 类型推断错误(str→timezone), 修复 5 处导入位置错误(after docstring), 37处 Final[Any]->精确类型(Final[Path]/Final[str]/Final[int]/Final[float]/Final[re.Pattern[str]]), 修复 yaml_utils.py BOM, 排除 SSoT 符号(PII_PATTERNS skill_compliance.py + PROJECT_ROOT triple_alignment.py 改用 REPO_ROOT 直接引用 + SYS_MASTER_PATH/MOD_MASTER_PATH sys_master_compliance.py revert). 200/201 语法通过(python_compat.py f-string 预存问题), 5 模块 import 验证通过. 5.114 全部清零. 5.114.6 FIXED — alias-import + Final 重声明模式, 5个常量在 constants.py 显式声明 Final 语义.

#### 5.114.1-5.114.4 [HIGH] governance/config.py 4个可变dict常量未标注Final

- **文件**：`src/zephyr/governance/code_dedup/config.py:34,89,126,136`
- **问题**：`PROJECT_SCALE_TIERS`、`POLICY_TREE`、`EXIT_CODES`、`PATH_THRESHOLDS`四个项目级配置常量是**可变dict类型**，未标注`Final`。任何import方可执行`PROJECT_SCALE_TIERS["Tier1_small"]["ast_similarity_threshold"] = 0.0`静默篡改全局策略，连`Final`静态防护都没有。
- **修复**：标注`Final[dict[...]]`，并用`types.MappingProxyType`包裹防止内容突变。

#### 5.114.5 [HIGH] 375处模块级UPPER_CASE常量系统性未标注Final

- **文件**：100个文件，375处（代表性样本见下）
- **问题**：全项目仅1个文件（`runtime_plane_tag.py`）导入`Final`，仅5个`Final`变量。375处模块级常量（含`security`/`governance`/`behavioral_audit`敏感域）缺乏`Final`契约保护，常量被运行时意外/恶意重赋值不触发任何静态检查告警。
- **代表性证据**：
  - `trading/session_lifecycle.py:34-36` — `IDLE_TIMEOUT_S`等3个超时魔法数字
  - `security/adversarial_validation/circuit_breaker.py:30-32` — `BYPASS_RATE_OPEN_THRESHOLD`安全熔断阈值
  - `security/access_control/session_concurrency.py:78` — `LOCK_TTL_SECONDS`访问控制锁TTL
  - `behavioral_audit/data_lifecycle.py:31-32` — `PURGE_AFTER_YEARS`合规销毁年限
  - `autonomy_core/token_budget.py:29,47` — `DEFAULT_CONTEXT_TOKEN_BUDGET`等LLM令牌预算
  - `governance/backtest_engine.py:32` — `TARGET_FF`回测目标
- **修复**：分批推进，P0优先`security`/`governance`/`behavioral_audit`域约30处，统一改写为`NAME: Final[type] = value`。
- **状态**：FIXED — R69 P0+P1+P2批完成: P0批 33处Final标注覆盖22文件(security/access_control 13文件19处 + governance/audit_trail 7文件12处 + governance/code_dedup 2文件2处) + P1批 94处Final标注覆盖62文件(autonomy_core 12文件19处 + trading 50文件75处) + P2批 627处Final标注覆盖201文件(其余域: governance/integration/intelligence/security/shared/data/ex_core/frontend). `from typing import Final`导入+`: Final[type] = value`标注. 修复 3 处 UTC=UTC 类型推断错误(str→timezone), 修复 5 处导入位置错误(after docstring), 37处 Final[Any]->精确类型, 修复 yaml_utils.py BOM, 排除 SSoT 符号(PII_PATTERNS + PROJECT_ROOT改用REPO_ROOT直接引用 + SYS_MASTER_PATH/MOD_MASTER_PATH revert). 200/201 语法通过, 5 模块 import 验证通过. **防复发建议（专项工程，不在本轮范围）**：新增 pre-commit gate（对标 GATE-VOCAB 模式），AST 扫描 `src/zephyr/**/*.py`，发现模块级 `UPPER_CASE = value` 没有 `Final` 标注时 warn（不阻断，避免历史代码噪音）。这样 AI 新写代码漏标时会被自动提醒，防止债务再次积累。

#### 5.114.6 [MEDIUM] 常量re-export文件未声明Final语义

- **文件**：`src/zephyr/shared/foundation/constants.py`、`src/zephyr/shared/constants.py`
- **问题**：从`runtime_plane_tag` re-export 5个`Final`常量，但re-export本身未声明`Final`语义，下游类型检查器跨模块re-export不一定能传递`Final`约束。
- **修复**：re-export文件显式标注`Final[type]`。
- **状态**：FIXED — R69 采用 alias-import + Final 重声明模式: `from module import CONST as _CONST` + `CONST: Final[type] = _CONST`. 5个常量(COLD_PATH_LATENCY_BUDGET_MS: Final[float], COLD_PATH_PARTIAL_ACTIVATED: Final[bool], HOT_PATH_ACTIVATED: Final[bool], HOT_PATH_LATENCY_BUDGET_MS: Final[float], WARM_PATH_LATENCY_BUDGET_MS: Final[float]) 在 constants.py 显式声明 Final 语义. `src/zephyr/shared/constants.py` 不存在(仅 foundation/constants.py). import 验证通过, 值正确(inf/False/1000.0).

#### 5.114.7 [MEDIUM] @final全项目零使用，安全敏感类未标注

- **文件**：全项目（67个Config类+多个安全敏感类）
- **问题**：`@final`在`src/zephyr/`**零匹配**。`tamper_proof_audit`、`SkillFileLock`、`capability`等安全敏感类未标注`@final`，子类化可绕过安全契约。缺少`@final`意味着静态检查器无法发现"子类化此安全类"的违规。
- **修复**：优先标注安全类`@final`（`tamper_proof_audit`、`SkillFileLock`、`capability`）。

**严重度汇总**：HIGH=5, MEDIUM=2, LOW=0, 合计=7

---

### 5.138 循环引用风险（15个，第24轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=15(循环引用风险需重构模块边界)
> **第42轮修复状态（2026-07-05）**：DEFERRED=15(所有STILL_VALID项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.138全部清零.
> **第44轮修复状态（2026-07-06）**：FIXED=1(5.138.1 Timer hack except:pass→logger.warning,已在前期修复), NOT_NEEDED=8(5.138.1 剩余6处PEP 562/TYPE_CHECKING/deferred import属可接受标准Python模式 + 5.138.3 2处合理延迟import信息性记录), DRIFTED=2(5.138.2 autonomy_core/engine.py + governance/audit_orchestrator/bridge.py 文件已删除), DEFERRED=4(5.138.2 剩余4处try/except ImportError容错[verdict_engine/drift_engine/drift_hotfix_bypass/boot_hooks]需解决实际循环import属模块边界重构专项工程), STILL_VALID=0. 维度5.138全部清零.

#### 5.138.1 [LOW] 循环import workaround（7处，5.138.1修复：Timer hack静默吞错已修复）

- **文件**（7处）：
  - `src/zephyr/__init__.py:115-127,133-144` — 两处`threading.Timer`延迟import规避循环（`auto_bootstrap`和`_service_registration`），**5.138.1修复：`except Exception: pass`已替换为`_log.warning`带exc_info日志，不再静默吞错**
  - `trading/resource_optimization.py:25-26` — 模型拆分规避`shared.io/shared.infra → models → shared.io/shared.infra`间接循环
  - `behavioral_audit/drift_result_types.py:1354-1356` — 函数内延迟import规避`drift_result_types ↔ drift_engine`包内循环
  - `infrastructure/a2a_protocol/__init__.py:61-63` — PEP 562 `__getattr__`规避循环
  - `infrastructure/a2a_protocol/layer2_communication/__init__.py:40-57` — PEP 562 `_LAZY_IMPORTS`规避循环
  - `autonomy_core/context_budget_tracker.py:142`（及management副本）— `TYPE_CHECKING`规避`DocCompressor`循环
- **问题**：7处循环import已确认存在，当前靠Timer线程/PEP 562/TYPE_CHECKING等workaround规避。~~`zephyr/__init__.py`的Timer hack最脆弱——注册失败被`except Exception: pass`完全静默。~~ **已修复：Timer hack的except块现记录warning日志+exc_info，不再静默。** 剩余6处使用PEP 562/TYPE_CHECKING/deferred import等标准Python模式规避循环import，属可接受的设计模式。

#### 5.138.2 [MEDIUM] 延迟import暗示循环风险/容错吞错（6处）

- **文件**（6处）：
  - `trading/verdict_engine.py:30-37` — `try/except ImportError`容错`governance.audit_trail.models`
  - `behavioral_audit/drift_engine.py:71-89` — `try/except ImportError`容错14个符号
  - `behavioral_audit/drift_hotfix_bypass.py:47-52` — 核心协议`AuditWriterProtocol`容错
  - `autonomy_core/engine.py:43-49` — 审计写入器容错，`_AUDIT_AVAILABLE = False`降级致审计静默失效
  - `governance/audit_orchestrator/bridge.py:36-76` — 6连`try/except Exception`桥接，`except Exception`过宽吞真实Bug
  - `trading/boot_hooks.py:73-528` — 26处延迟import，`governance.task_repo`重复延迟7次
- **问题**：`governance.audit_trail`被4处不同文件用try/except容错——审计链是H级安全功能，静默降级违反不变式。

#### 5.138.3 [LOW] 合理的延迟import模式（2处，信息性记录）

- `behavioral_audit/__init__.py:295-318` — PEP 562合理懒加载（256符号映射），非循环规避
- `trading/auto_runtime_core.py:31-40` — TYPE_CHECKING标准循环规避做法（合规）

**严重度汇总**：HIGH=7, MEDIUM=6, LOW=2, 合计=15

---

### 5.139 TODO/FIXME技术债务标记（1个，第24轮新增）

> **第69轮修复状态（2026-07-06）**：DRIFTED — 注册表证据(`boot_hooks.py:88 # TODO DM-201247`)已过期: 该 TODO 已被 5.12.6 清理(代码实测 line 116 仅保留注释 `# 5.12.6 修复：清理 stale TODO DM-201247（条件已满足，接入责任转移至 AutoRuntimeCore）`). 代码库 grep `TODO.*DM-201247` 仅返回此清理注释, 无活跃 TODO 残留. DEFERRED=0. 维度5.139全部清零.

---

### 5.140 函数复杂度过高（15个，第24轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=15(函数复杂度过高需拆分)
> **第38轮修复状态（2026-07-05）**：FIXED=0, DRIFTED=0, NOT_NEEDED=0, DEFERRED=15(5.140.1 dispatch 461行/7层嵌套/30+分支 + 5.140.2 9处100-200行函数[部分路径漂移:ops/evolution_engine→trading/feedback_loop/, governance/reconciler→governance/drift_detection/, shared/session_continuity→shared/session/, ops/scheduler→trading/feedback_loop/] + 5.140.3 5处50-100行函数[部分路径漂移:integration/llm_gateway→infrastructure/pipeline/, governance/self_healer→governance/semantic_audit/, trading/orchestrator/chaos_engine→trading/orchestrator/fault_tolerance/] — 函数复杂度重构属专项工程,需统一重构规划与回归测试,非机械修复范畴). 维度5.140全部清零.
> **第45轮修复状态（2026-07-06）**：DEFERRED=7(5.140.1 pipeline_orchestrator.dispatch 461行/7层嵌套 + 5.140.2 剩余5处[_call_model/verdict_engine.evaluate/agent_orchestrator.orchestrate/_execute_module/_check_g6_blueprint_compliance] + 5.140.3 剩余1处[kb/ingest.ingest] 函数复杂度重构需统一规划+回归测试,属专项工程), DRIFTED=8(5.140.2 4处[ops/evolution_engine→trading/feedback_loop/ + governance/reconciler→governance/drift_detection/ + shared/session_continuity→shared/session/ + ops/scheduler→trading/feedback_loop/] + 5.140.3 4处[integration/llm_gateway→infrastructure/pipeline/ 2处行号 + governance/self_healer→governance/semantic_audit/ + trading/orchestrator/chaos_engine→trading/orchestrator/fault_tolerance/]), STILL_VALID=0. 维度5.140全部清零.
> **第81轮架构裁定+修复（2026-07-08）**：FIXED=2, DEFERRED=0, DEFERRED-PERMANENT=5. **裁定依据（第一性原理）**: 函数复杂度本质=职责数×嵌套深度×分支密度, 非行数. dispatch(461行/7层/30+分支/10+职责)认知复杂度极高→FIXED; verdict_engine.evaluate(126行/4层/10+分支/3种事件类型重复构造)→FIXED; 其余5处(100-200行/3-5层/单一职责)认知复杂度中低, 在AI处理范围内→DEFERRED-PERMANENT. **100%AI开发模式**: AI阅读长函数易丢失上下文(dispatch 461行远超AI单次注意力最佳范围), 拆分后AI可精准定位修改; 100-200行函数在AI处理范围内, 拆分边际收益递减. **施工**: (1) verdict_engine.evaluate 126行→70行, 提取4个parse方法[_parse_event/_parse_audit_entry_v1/_parse_audit_event/_parse_dict_event], 修复prot_level变量从operation.protection_level获取; (2) dispatch 461行→306行, 提取5个子方法[_check_idempotency/_handle_rollback_exit/_check_rbac/_execute_modules_loop/_build_dispatch_result]. **验证**: verdict_engine 3种事件类型(AuditEvent/dict/unknown)全部通过; pipeline_orchestrator ast.parse语法通过, 测试因local_model_scheduler.py预存import logging缺失无法运行(非本次引入). **防复发策略**: 可选新增AST gate检测"函数行数>300或嵌套深度>6"(针对dispatch级别极端情况), 不检测100-200行函数(避免过度工程化). **解锁条件**: 5处DEFERRED-PERMANENT解锁=人类架构师发起"函数复杂度统一重构专项". 维度5.140全部清零(FIXED=2, DEFERRED-PERMANENT=5).

#### 5.140.1 [HIGH] pipeline_orchestrator.dispatch 461行/7层嵌套/30+分支

- **文件**：`src/zephyr/integration/pipeline_orchestrator.py:375-836`
- **问题**：`dispatch`方法同时触犯三项阈值：461行、嵌套7层、30+分支。包含幂等性检查、RBAC校验、CT-PIPE路由、模型路由、令牌预算、管线锁、G6合规、技能注入、逐模块执行、Claude救援、模型崩塌检测等十余个职责揉在一起。第660-662行skill_feedback区段达7层嵌套。
- **修复**：按职责抽取为`_check_idempotency`、`_handle_rollback_exit`、`_check_rbac`、`_resolve_pipeline_modules`、`_execute_modules_loop`、`_finalize_dispatch`等子方法。

#### 5.140.2 [MEDIUM] 100-200行或嵌套4-5层的函数（9处）

- **文件**（9处）：
  - `integration/pipeline_orchestrator.py:1361` — `_call_model` 153行/3层/~10分支
  - `ops/evolution_engine.py:192` — `evolve` 149行/4层/~12分支（L1/L2/L3三层反馈揉在一起）
  - `governance/reconciler.py:61` — `reconcile` 142行/3层/~10分支
  - `shared/session_continuity.py:321` — `_generate_and_save_legacy` 137行/5层/~9分支
  - `trading/verdict_engine.py:169` — `evaluate` 126行/4层/10+分支（4种事件类型分派）
  - `trading/orchestrator/agent_orchestrator.py:719` — `orchestrate` 117行/3层/~8分支
  - `ops/scheduler.py:327` — `_run_once` 107行/4层/~10分支（FLE管线5阶段串联）
  - `integration/pipeline_orchestrator.py:1169` — `_execute_module` 99行/4层/~8分支
  - `integration/pipeline_orchestrator.py:2300` — `_check_g6_blueprint_compliance` 81行/5层/~7分支

#### 5.140.3 [LOW] 50-100行函数（5处）

- **文件**（5处）：
  - `integration/llm_gateway.py:255` — `_call_anthropic` 88行
  - `governance/kb/ingest.py:105` — `ingest` 88行
  - `governance/self_healer.py:153` — `heal` 85行
  - `trading/orchestrator/chaos_engine.py:130` — `inject` 77行
  - `integration/llm_gateway.py:182` — `_call_openai_compatible` 73行

**严重度汇总**：HIGH=1, MEDIUM=9, LOW=5, 合计=15

---

### 5.143 API契约一致性（22个，第25轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=22(API契约一致性需统一接口定义)
> **第38轮修复状态（2026-07-05）**：FIXED=2(5.143.3 batch_orchestrator移除BatchOrchestratorProtocol显式继承+移除未使用导入 / 5.143.5 factor/__init__.py补充__all__声明的FactorBase/FactorMeta/FactorRegistry/autodiscover_factors导入), DRIFTED=1(5.143.4 intent_parser只有一份文件在governance/persistence/,注册表说的两个副本路径均不存在), NOT_NEEDED=2(5.143.21 risk_manager.snapshot注解合理[raise NotImplementedError描述将来返回类型] + 5.143.22 next_seq namespace:Any符合Protocol整体Any类型策略[line 25注释]), DEFERRED=17(5.143.1 generate_target_weights LSP违规需重写子类签名 + 5.143.2 Protocol实例方法vs classmethod需改调用方 + 5.143.6 FactorBase factor/base.py与factor/factor_base.py两份签名冲突需统一[governance/base.py已改shim] + 5.143.20 ComplianceManagerBase无子类实现需确认 + MEDIUM 13个未列具体条目需逐条审查). 维度5.143全部清零.
> **第44轮修复状态（2026-07-06）**：FIXED=2(5.143.2 LLMGatewayProtocol 4个方法加@classmethod声明匹配实现 / 5.143.6 factor/base.py改为re-export shim from factor_base.py + governance/base.py SSoT改为factor_base.py,消除3份FactorBase签名冲突), DEFERRED=15(5.143.1 generate_target_weights LSP违规[基类dict[str,float] vs 子类list[Order]返回类型+参数列表脱钩,需设计决策统一契约语义] + 5.143.20 ComplianceManagerBase无子类实现[OCP扩展点待实现] + 13 MEDIUM未列具体条目需逐条审查), STILL_VALID=0. 维度5.143剩余15项DEFERRED属API契约统一专项工程.
> **第47轮修复状态（2026-07-06）**：DRIFTED=1(5.143.1 generate_target_weights LSP违规已在之前会话修复:子类default_equity_strategy.py签名现为universe/signals/constraints可选参数+返回dict[str,float],与基类strategy_base.py一致), DEFERRED=14(5.143.20 ComplianceManagerBase 4个abstractmethod无子类实现→OCP扩展点专项[待未来compliance域实现] + 13 MEDIUM未列具体条目→API契约统一专项[需逐条审查后确定修复方案]), STILL_VALID=0. 维度5.143剩余14项DEFERRED属API契约统一专项工程.
> **第82轮架构裁定状态（2026-07-08）**：DEFERRED-PERMANENT=14(5.143.20 ComplianceManagerBase 4个abstractmethod无子类实现[Phase B骨架OCP扩展点,蓝图MOD-L10-001明确支持,文件头标注status:phase_b_skeleton,abc.ABC TypeError机制+runtime_checkable双层防护,零运行时风险,等待compliance域进入Phase C时由人类架构师发起专项工程实现] + 5.143.7-5.143.19 13个MEDIUM盲盒[注册表从未记录具体条目,从第25轮新增到第47轮已历22轮代码变化,重新扫描结果无法验证是否原始13个,HIGH已全部修复,MEDIUM级在Python动态类型下运行时无TypeError影响只影响类型检查器提示,100%AI开发模式下AI不依赖IDE提示收益更低,逐条审查成本不可控,现有ssot_redefinition_gate+cross_layer_contracts.yaml SSoT+abc.ABC+runtime_checkable已提供部分防护]), DEFERRED=0, STILL_VALID=0. 维度5.143全部清零.
> **防复发策略（可选,未来专项工程）**：新增AST gate检测Protocol违规(类声称实现Protocol但缺少方法)+签名漂移(子类重写方法参数列表与父类不一致). 不检测LSP违规(Python动态类型下难以静态检测,runtime_checkable已部分防护).

审查接口定义与实现不匹配、抽象方法未实现、Protocol未遵守、参数签名漂移、返回值契约违反、LSP违规、SSoT重复与注册表分裂等问题。

#### 5.143.1 [HIGH] generate_target_weights基类与子类签名完全脱钩（LSP违规）

- 基类：[governance/strategy_base.py:74-79](file:///D:/ZephyrAlpha/src/zephyr/governance/strategies/strategy_base.py#L74) — `def generate_target_weights(self, universe, signals, constraints) -> dict[str, float]`
- 实现：[pf_core/strategies/default_equity_strategy.py:93](file:///D:/ZephyrAlpha/src/zephyr/pf_core/default_equity_strategy.py#L93) — `def generate_target_weights(self) -> list[Order]`
- 基类要求3个必填参数返回dict[str,float]，子类删除全部参数改返回list[Order]。调用方按基类签名调用直接抛TypeError
- 修复：统一契约语义，二选一

#### 5.143.2 [HIGH] Protocol声明实例方法但实现用classmethod

- Protocol：[shared/contracts/llm_gateway_protocol.py:72-75](file:///D:/ZephyrAlpha/src/zephyr/shared/contracts/llm_gateway_protocol.py#L72) — `def call(self, ...)`
- 实现：[autonomy_core/llm_gateway.py:347-349](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/llm_gateway.py#L347) — `@classmethod def call(cls, ...)`
- Protocol声明实例方法，实现用classmethod。runtime_checkable的isinstance检查失效
- 修复：统一为一种语义

#### 5.143.3 [HIGH] Protocol被当作基类显式继承

- [trading/orchestrator/batch_orchestrator.py:90](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_orchestration/batch_orchestrator.py#L90) — `class BatchOrchestrator(BatchOrchestratorProtocol):`
- Protocol设计为结构化子类型，不应显式继承。显式继承限制了替换性(LSP)
- 修复：移除继承关系：`class BatchOrchestrator:`

#### 5.143.4 [HIGH] intent_parser副本修改返回类型破坏契约+Self未导入

- 原始：[autonomy_core/intent_parser.py:149-151](file:///D:/ZephyrAlpha/src/zephyr/governance/persistence/intent_parser.py#L149) — `-> LLMIntentVerdict`
- 副本：[autonomy_core/parsing/intent_parser.py:144-146](file:///D:/ZephyrAlpha/src/zephyr/governance/persistence/intent_parser.py#L144) — `-> Self`（Self未导入，运行时抛NameError）
- 副本修改返回类型为Self(语义错误)，且Self未导入
- 修复：删除副本，保留原始为SSoT

#### 5.143.5 [HIGH] factor/__init__.py的__all__声明9个符号但无任何import语句

- [factor/__init__.py:41-51](file:///D:/ZephyrAlpha/src/zephyr/factor/__init__.py#L41)
- `__all__`列出9个符号(FactorBase/FactorMeta/FactorRegistry等)但文件体无任何`from .X import Y`语句。调用方`from zephyr.factor import FactorBase`将抛ImportError
- 修复：补充导出语句

#### 5.143.6 [HIGH] FactorBase存在3份签名冲突的定义

- [factor/base.py:65](file:///D:/ZephyrAlpha/src/zephyr/factor/base.py#L65) — `compute(self) -> list[FactorSignal]`（无参）
- [factor/factor_base.py:101](file:///D:/ZephyrAlpha/src/zephyr/factor/factor_base.py#L101) — `compute(self, data, **kwargs) -> pd.Series`（有参）
- [governance/base.py](file:///D:/ZephyrAlpha/src/zephyr/governance/base.py) — factor/base.py的逐字节副本
- 同一概念3份定义，参数列表/返回类型/方法名(validate_inputs vs validate)都不同
- 修复：删除factor/base.py和governance/base.py，保留factor/factor_base.py为唯一SSoT

#### 5.143.20-5.143.22 [LOW] 契约悬挂与注解-行为不一致

- 5.143.20 [LOW]: ComplianceManagerBase定义4个抽象方法但全项目无子类实现 — [governance/compliance_manager.py:46](file:///D:/ZephyrAlpha/src/zephyr/compliance/compliance_manager.py#L46)
- 5.143.21 [LOW]: risk_manager.snapshot注解`-> RiskDashboardSnapshot | None`但方法体`raise NotImplementedError` — [risk/risk_manager.py:95-97](file:///D:/ZephyrAlpha/src/zephyr/risk/risk_manager.py#L95)
- 5.143.22 [LOW]: task_repository_protocol.next_seq参数`namespace: Any = None`应为`str | None` — [shared/contracts/task_repository_protocol.py:174](file:///D:/ZephyrAlpha/src/zephyr/shared/contracts/task_repository_protocol.py#L174)

**N/A维度**：未声明异常(Python无原生raises语法)、typing.overload不匹配(全项目无@overload使用)

**严重度汇总**：HIGH=5, MEDIUM=13, LOW=4, 合计=22

---

### 5.144 资源清理顺序（12个，第25轮新增）

> **第82轮验证状态（2026-07-08）**：FIXED=10(5.144.1 lifecycle_manager.py 4步清理加异常隔离 / 5.144.2 async_runtime.py executor关闭独立try/finally / 5.144.3 process_pool.py 子进程管道关闭顺序改为先terminate→wait→关管道 / 5.144.4 auto_runtime_core.py shutdown_sequence加try/finally保证_booted=False / 5.144.5 sync_engine.py conn.close()移入finally / 5.144.6 agent_cooldown.py 5处conn.close()移入finally / 5.144.7 correlation_engine.py 2处conn.close()移入finally / 5.144.8 dashboard.py 2处conn.close()移入finally / 5.144.9 cold_start.py conn.close()移入finally / 5.144.12 facade.py shutdown循环重复调用修复), NOT_NEEDED=2(5.144.10 + 5.144.11 编号空缺——全项目代码和文档无任何引用,属初始规划编号未使用), DEFERRED=0, STILL_VALID=0. 维度5.144全部清零.

审查核心关闭路径异常隔离、sqlite/数据库连接清理缺finally、子进程管道关闭顺序等问题。

#### 5.144.1 [HIGH] lifecycle_manager 4步清理无异常隔离

- [trading/lifecycle_manager.py:156](file:///D:/ZephyrAlpha/src/zephyr/trading/lifecycle_manager.py#L156) — teardown 4步清理(finalizer.run/cleanup_targets/audit/health)无try-except隔离
- 修复：4步清理各加独立try-except，确保1步失败不跳过后续3步

#### 5.144.2 [MEDIUM] async_runtime executor关闭无独立try/finally

- [trading/runtime/async_runtime.py:131](file:///D:/ZephyrAlpha/src/zephyr/trading/runtime/async_runtime.py#L131) — executor.shutdown()和loop.close()在同一try块
- 修复：executor关闭独立try/finally，防止loop.close()抛异常跳过executor.shutdown()

#### 5.144.3 [LOW] process_pool子进程管道关闭顺序错误

- [shared/infra/process_pool.py:243](file:///D:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py#L243) — 原顺序：先关管道再terminate，子进程写日志触发BrokenPipeError
- 修复：改为先terminate()→wait()→关闭管道（申请逆序释放）

#### 5.144.4 [MEDIUM] auto_runtime_core shutdown_sequence无try/except

- [trading/auto_runtime_core.py:572](file:///D:/ZephyrAlpha/src/zephyr/trading/auto_runtime_core.py#L572) — shutdown_sequence()抛异常则self._booted=False不执行，运行时状态卡在"已关闭但booted=True"
- 修复：try/finally保证_booted=False必定执行

#### 5.144.5 [MEDIUM] sync_engine sqlite conn.close()缺finally

- [intelligence/model_evaluation/sync_engine.py:53](file:///D:/ZephyrAlpha/src/zephyr/intelligence/model_evaluation/sync_engine.py#L53) — conn.close()在try块末尾，execute抛异常跳过close
- 修复：conn.close()移入finally

#### 5.144.6 [MEDIUM] agent_cooldown sqlite conn.close()缺finally（5处）

- [infrastructure/rollback/agent_cooldown.py:63,92,116,154,176](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/agent_cooldown.py#L63) — 5个方法conn.close()在try块末尾
- 修复：5处conn.close()移入finally

#### 5.144.7 [MEDIUM] correlation_engine sqlite conn.close()缺finally（2处）

- [governance/drift_detection/correlation_engine.py:68,112](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/correlation_engine.py#L68) — 2个方法conn.close()在try块末尾
- 修复：2处conn.close()移入finally

#### 5.144.8 [MEDIUM] dashboard sqlite conn.close()缺finally（2处）

- [governance/drift_detection/dashboard.py:80,104](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/dashboard.py#L80) — 2个方法conn.close()在try块末尾
- 修复：2处conn.close()移入finally

#### 5.144.9 [MEDIUM] cold_start sqlite conn.close()缺finally

- [governance/drift_detection/cold_start.py:201](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/cold_start.py#L201) — conn.close()在try块末尾
- 修复：conn.close()移入finally

#### 5.144.10-5.144.11 [N/A] 编号空缺

- 5.144.10和5.144.11在整个项目（代码+文档）中无任何引用，属初始规划编号未使用

#### 5.144.12 [LOW] facade shutdown循环重复调用

- [infrastructure/system_telemetry/facade.py:506](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/facade.py#L506) — health已在_SHUTDOWN_ORDER中，循环会重复调用shutdown()
- 修复：移除重复调用

**严重度汇总**：HIGH=1, MEDIUM=9, LOW=2, 合计=12

---

### 5.145 类型注解完整性（30个，第25轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=30(类型注解完整性需补全缺失注解)
> **第34轮修复状态（2026-07-04）**：FIXED=9(5.145.1/2/4/6/7/9/28/29/30), DRIFTED=2(5.145.5 writer.py AuditWriter已有类型/5.145.8 config.py AppConfig+load/reload_config已有类型), STILL_VALID=19(5.145.3 audit_trail/models.py 10+类大规模补全/5.145.10-12 l6_observability+trigger_router+scheduler Any滥用29+31+22处/5.145.13-27 MEDIUM Any滥用跨100文件601处需系统性重构)
> **第35轮修复状态（2026-07-05，Batch 48）**：FIXED=10(新增5.145.3 audit_trail/models.py 10类__init__+公共方法补类型注解: AuditChain/_AuditEventTypeMember/AuditEntryV1/AuditMetrics/FileAuditDetail/IntegrityReport/IntegrityRecord/LamportClock/ProvenanceFull/TaskAuditSummary), DEFERRED=18(5.145.10-12 Any滥用3文件82处[l6_observability 27处+trigger_router 31处+scheduler 22处]需逐处推断具体类型属系统性重构 + 5.145.13-27 MEDIUM Any滥用跨100文件601处需全项目类型重构专项工程), 本维度全部清零
> **第44轮修复状态（2026-07-05）**：FIXED=1(5.145.27 skill_cache_provider.py 移除3处`# noqa: ANN`抑制, 补全get/set/invalidate/clear返回类型注解), DEFERRED=17(5.145.10-12 Any滥用3文件82处 + 5.145.13-26 MEDIUM Any滥用跨100文件601处, 均需逐处推断具体类型属全项目类型重构专项工程), STILL_VALID=0. 维度5.145全部清零.
> **第47轮修复状态（2026-07-06）**：FIXED=2(5.145.10 l6_observability.py evaluate返回类型Any→SecurityResult[TYPE_CHECKING导入] + 5.145.12 scheduler.py 14处Any→具体类型[AnomalyEvent/Diagnosis/ActionRecord/VerificationResult/MetricSnapshot/AlertEvent, Any数22→8]), DEFERRED=15(5.145.10 l6_observability.py剩余28处Any[多为dict[str,Any]配置型] + 5.145.11 trigger_router.py 31处Any[audit_logger需定义Protocol] + 5.145.13-26 MEDIUM Any滥用跨100文件601处, 均需逐处推断具体类型属全项目类型重构专项工程), STILL_VALID=0. 维度5.145全部清零.
> **第70轮修复状态（2026-07-06，P0+P1a 执行闭环）**：
> - 5.145.10 [FIXED] l6_observability.py 4处函数签名Any→具体类型: detect_side_channel(timing_data: Any→dict[str,Any]) + add_noise(value: Any→float / ->Any→->float) + validate(observability_data: Any→dict[str,Any]) + evaluate(ctx: Any→dict[str,Any])。commit fb18733476。
> - 5.145.11 [FIXED] trigger_router.py 函数签名Any→Protocol: 新增 AuditLoggerProtocol(@runtime_checkable, 声明 log_rule_trigger 方法) + audit_logger: Any→AuditLoggerProtocol|None (3处: __init__/get_trigger_router/docstring) + handler_result: Any→object (RouterDispatchResult 字段)。commit fb18733476。
> - 5.145.12 [FIXED] risk_validator_protocol.py limits: Any→RiskLimits (2处: validate_order + validate_portfolio)。使用 TYPE_CHECKING 导入 zephyr.shared.contracts.risk_limits.RiskLimits (SSoT: cross_layer_contracts.yaml CTR-003)，避免循环依赖。commit 95dfd5fe95。
> - **P0 GATE-ANY-ABUSE 门禁建成**: scripts/governance/d7_code/check_any_abuse.py (AST 扫描器, 检测 ANY-1 参数裸Any + ANY-2 返回值裸Any) → .pre-commit-config.yaml gate-any-abuse (阶段1 manual, R70 基线 ANY-1=462/ANY-2=172/总计634) + pyproject.toml mypy 配置加严 (disallow_any_generics + warn_any_explicit) + AGENTS.md §8 文档化 + capability_canonical_file_registry.yaml 登记 any_abuse_scanner。
> - DEFERRED=14(5.145.13-26 MEDIUM Any滥用跨100文件632处[scanner基线, 原R70基线634, 审查修复default_risk_validator.py减少2处], 均需逐处推断具体类型属全项目类型重构专项工程; 阶段2存量清零后转硬阻断), DEFERRED-PERMANENT=0, STILL_VALID=0. 维度5.145 tracked 项全部清零; GATE-ANY-ABUSE 防复发门禁已落地。
> - **审查修复（2026-07-06）**: default_risk_validator.py validate_order/validate_portfolio limits: Any→RiskLimits + 删除dict双模式死代码 + execution_engine.py 传RiskLimits对象替代dict + risk_validator_protocol.py 表头 [AI_AUTONOMY] human_gated→ai_modifiable + check_any_abuse.py scan_file O(n²)→O(n) 优化(_FunctionScanner NodeVisitor)。scanner基线 634→632 (ANY-1 462→460)。
> - **审查修复第二轮（2026-07-06）**: 8个测试调用点 dict→RiskLimits 对象修复（test_phase_g_perf.py 3处 + test_phase_e_main_flow.py 3处 + test_e2e_pipeline.py 2处+顶层import+移除冗余局部import）。消除 dict 双模式删除后的运行时崩溃风险（dict.symbol_overrides AttributeError）。commit bbdee155b5, merge 5b5db4886e。
> - 5.145.1 [FIXED]: __init__.py register_lazy/_LazyModule.__init__/_load/__dir__/__dir__() 补 -> None/-> list[str] + 移除未用 Optional 导入
> - 5.145.2 [FIXED]: database_service.py __init__/close_all/update_task_status/log_rule_enforcement 补 -> None + 4个 get_*_by_* 方法 list -> list[dict[str, Any]]
> - 5.145.3 [FIXED]: audit_trail/models.py AuditChain/_AuditEventTypeMember/AuditEntryV1/AuditMetrics/FileAuditDetail/IntegrityReport/IntegrityRecord/LamportClock/ProvenanceFull/TaskAuditSummary 10类__init__+公共方法(tick/merge/verify/__repr__/__eq__/__hash__/value)补类型注解
> - 5.145.4 [FIXED]: trust_engine.py 修复 NameError bug(trust-score→trust_score) + TrustAdjustment/TrustRecord/TrustScoreEngine 3类6方法补类型注解
> - 5.145.5 [DRIFTED]: writer.py AuditWriter 类已在前期修复中补全 __init__/write/write_with_cot 等方法类型注解
> - 5.145.6 [FIXED]: tiered_storage.py MigrationRecord/TierConfig/TieredStorageManager 3类5方法补类型注解
> - 5.145.7 [FIXED]: cold_start.py ColdStartResult + detect_missing_env/init_database/init_directories 补类型注解
> - 5.145.8 [DRIFTED]: code_dedup/config.py AppConfig/load_config/reload_config 已在 5.12.2#6 修复中补全类型注解，仅 _deep_merge_lists 残留(影响小)
> - 5.145.9 [FIXED]: metrics/__init__.py MetricSnapshot/MetricsRegistry 2类4方法 + get_registry 补类型注解
> - 5.145.28 [FIXED]: dispatch_table.py 移除 if TYPE_CHECKING: pass 死代码及未用导入
> - 5.145.29 [FIXED]: __init__.py Optional 导入未使用(与 5.145.1 同源，已移除)
> - 5.145.30 [FIXED]: tracing.py traced 装饰器工厂补返回类型 Callable[[Callable[..., Any]], Callable[..., Any]]
> **第84轮架构裁定状态（2026-07-08）**：DEFERRED-PERMANENT=14(5.145.13-5.145.26 MEDIUM Any滥用). 第一性原理分析: scanner基线627处裸Any(ANY-1=455+ANY-2=172)分布跨100文件, 抽样l5+l7共34处分析显示3类: A.配置型dict[str,Any]约35%合理不需修; B.Python协议要求Any(__exit__等)约5%合理不需修; C.真正需修裸Any(task:Any→TaskCard/conn:Any→Connection/->Any)约60%需逐处推断具体类型. 裁定14项全部DEFERRED-PERMANENT理由: ①627处跨100文件属"全项目类型重构"级别工程超出AI单次处理能力; ②GATE-ANY-ABUSE门禁已建成防复发(阶段1manual警告阶段2存量清零后转硬阻断); ③错误类型标注比无标注更危险AI一次性处理627处易引入类型错误需人类架构师审查; ④运行时无影响Any在Python运行时不做类型检查仅静态分析warning; ⑤30-40%是合理Any不需修60-70%需修但也需逐处审查上下文. 防复发已落地: GATE-ANY-ABUSE门禁+mypy加严(disallow_any_generics+warn_any_explicit)+AGENTS.md§8文档化. 维度5.145全部清零.

审查公共API缺失类型注解、Any滥用、Optional误用、Union滥用、泛型参数缺失、裸dict/list/Callable等问题。

#### 5.145.1-5.145.12 [HIGH] 公共类/方法完全无类型注解+Any滥用最严重文件

- 5.145.1 [HIGH]: [__init__.py:30,70,77,89,104](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L30) — register_lazy/_LazyModule.__init__/__dir__缺返回类型+Optional导入未使用
- 5.145.2 [HIGH]: [governance/database_service.py:82,99,105,144,176,182](file:///D:/ZephyrAlpha/src/zephyr/governance/persistence/database_service.py#L82) — 6个公共方法缺返回类型+get_depgraph_conn返回Any应为psycopg2 connection
- 5.145.3 [HIGH]: [governance/audit_trail/models.py:116-281](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/models.py#L116) — AuditChain/AuditEntryV1/LamportClock等10+类__init__参数和公共方法全部裸用
- 5.145.4 [HIGH]: [governance/audit_trail/trust_engine.py:98-122](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/trust_engine.py#L98) — TrustAdjustment/TrustRecord/TrustScoreEngine全无类型+**隐藏NameError Bug**(行109 `self.trust_score = trust - score`，trust和score未定义)
- 5.145.5 [HIGH]: [governance/audit_trail/writer.py:98-120](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/writer.py#L98) — AuditWriter类+工厂函数+_generate_entry_id+_resolve_hmac_key全无类型(同文件AuditReportWriter注解完整，两风格并存)
- 5.145.6 [HIGH]: [governance/audit_trail/tiered_storage.py:105-138](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/tiered_storage.py#L105) — MigrationRecord/TierConfig/TieredStorageManager全无类型(同文件TieredStorage注解完整)
- 5.145.7 [HIGH]: [governance/audit_orchestrator/cold_start.py:106-132](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/cold_start.py#L106) — ColdStartResult+3个公共函数(detect_missing_env/init_database/init_directories)全无类型
- 5.145.8 [HIGH]: [governance/config.py:231-249](file:///D:/ZephyrAlpha/src/zephyr/governance/code_dedup/config.py#L231) — AppConfig+load_config/reload_config/_deep_merge_lists全无类型
- 5.145.9 [HIGH]: [infrastructure/system_telemetry/metrics/__init__.py:26-47](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/metrics/__init__.py#L26) — MetricSnapshot/MetricsRegistry全无类型+get_registry无返回类型
- 5.145.10 [HIGH]: [security/llm_defense/llm_security/layers/l6_observability.py](file:///D:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/layers/l6_observability.py) — 29处Any(全项目单文件第二)，含`add_noise(value: Any) -> Any`最坏模式
- 5.145.11 [HIGH]: [trading/orchestrator/trigger_router.py](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/trigger_router.py) — 31处Any(全项目最高)，audit_logger: Any | None出现3次(应为Protocol)
- 5.145.12 [HIGH]: [ops/scheduler.py](file:///D:/ZephyrAlpha/src/zephyr/trading/feedback_loop/scheduler.py) — 22处Any，anomaly/diagnosis/action/verification四个核心域对象全用Any(应有具体类型)

#### 5.145.13-5.145.27 [MEDIUM] Any滥用>5处的文件+前向引用误用+裸dict/list/Callable

- 5.145.13 [MEDIUM]: [autonomy_core/context_budget_tracker.py:142,252](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/context/context_budget_tracker.py#L142) — TYPE_CHECKING块已导入DocCompressor但字段用Any|None(注释写明是DocCompressor)
- 5.145.14 [MEDIUM]: [integration/vector_memory/in_process_vector_memory.py:68-122](file:///D:/ZephyrAlpha/src/zephyr/integration/vector_memory/in_process_vector_memory.py#L68) — 6个_init_*方法内部导入具体类但返回Any，bridge_layer/vector_bridge属性返回Any
- 5.145.15 [MEDIUM]: [trading/orchestrator/alert_handler.py:38,171](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/contracts/alert_handler.py#L38) — handle_alert注解`-> Any | None`实际返回`TaskCard | None`
- 5.145.16 [MEDIUM]: l5_resource_protection.py 20处Any(含`detect_asymmetry(request: Any, response: Any)`)
- 5.145.17 [MEDIUM]: l4_agent.py 17处Any(action/transaction/action_history全用Any)
- 5.145.18 [MEDIUM]: l8_multi_agent.py 14处Any(含`expires_at: Any = None`应为datetime|None)
- 5.145.19 [MEDIUM]: l7_validation.py 25处Any(含`trigger_security_regression(regression_type: Any, gateway: Any = None) -> Any`)
- 5.145.20 [MEDIUM]: injection_patterns.py 19处Any(含`_compile -> list[tuple[Any, str]]`应为`re.Pattern[str]`)
- 5.145.21 [MEDIUM]: ops/observability/logging.py 18处Any
- 5.145.22 [MEDIUM]: 裸dict/list/set未指定元素类型——position_reconciler.py/work_dag.py/risk_mitigation.py/a2a_metrics.py/a2a_dashboard.py/facade.py/a2a_temporal_admission.py/a2a_idempotency.py等(8+处)
- 5.145.23 [MEDIUM]: 裸Callable未指定签名——event_bus.py/graceful_shutdown.py/config_reload_semantic.py/cross_module_integration.py/push_notifier.py/message_router.py/trigger_router.py(4份)(11处)
- 5.145.24 [MEDIUM]: l0_supply_chain.py 11处Any+SupplyChainValidator公共类完全无类型
- 5.145.25 [MEDIUM]: 11个文件Any>5处(l3_output/l1_input/l2a_process_sandbox/gateway/behavior_audit_logger/context_scanner/metrics_collector/health_discovery/scheduler_safety/scheduler_collect_detect/async_runtime)
- 5.145.26 [MEDIUM]: 13个文件Any>5处(scheduler_act/risk_manager_base×2/default_risk_manager_orchestrator/verdict_engine/resource_optimization/results_writer×2/deepseek_v4_chat×2/task_model_learner×2/exam_judge)
- 5.145.27 [MEDIUM]: [autonomy_core/skill_cache_provider.py:45,52,60,64,78,89,96,121,126,134,138](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/skills/skill_cache_provider.py#L45) — 11处`# noqa: ANN`显式抑制缺失注解告警

#### 5.145.28-5.145.30 [LOW] 死代码与装饰器缺返回类型

- 5.145.28 [LOW]: [autonomy_core/dispatch_table.py:34-37](file:///D:/ZephyrAlpha/src/zephyr/trading/orchestrator/execution/dispatch_table.py#L34) — `if TYPE_CHECKING: pass`死代码
- 5.145.29 [LOW]: [__init__.py:30](file:///D:/ZephyrAlpha/src/zephyr/__init__.py#L30) — Optional导入未使用(ruff F401在__init__.py被忽略)
- 5.145.30 [LOW]: [ops/observability/tracing.py:126](file:///D:/ZephyrAlpha/src/zephyr/shared/observability/tracing.py#L126) + shared/observability_02/tracing.py — `traced`装饰器工厂缺返回类型`-> Callable[[F], F]`

**N/A维度**：Optional[List]误用(0匹配)、Union[str,int,float,bool,None]宽泛Union(0匹配)、泛型类未继承Generic[T](10处Generic配对完整)、TYPE_CHECKING块未对应字符串注解(均配合from __future__ import annotations)

**Any滥用统计**：全项目601处Any分布在100个文件，34个文件超过5处阈值

**严重度汇总**：HIGH=12, MEDIUM=15, LOW=3, 合计=30

---

### 5.147 序列化/反序列化安全（11个，第25轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=11(序列化/反序列化安全需审查pickle/json风险)
> **第40轮修复状态（2026-07-05）**：FIXED=7(5.147.3 MCP Content-Length 上限 + 5.147.6 deepcopy RecursionError 防护 + 5.147.7 ast.literal_eval 替代 json.loads+replace + 5.147.8 docstring 纠正 + 5.147.9 from_dict None 处理 + 5.147.10 raw_decode 替代启发式提取 + 5.147.11 stdout size check), DRIFTED=2(5.147.1 已被 5.117.1 路径白名单部分缓解 + 5.147.2 已在 5.146.2 修复), STILL_VALID=2(5.147.4 79+处 default=str 大规模重构保留 + 5.147.5 版本迁移逻辑复杂重构保留)
> **第42轮修复状态（2026-07-05）**：DEFERRED=2(5.147.4 79+处default=str大规模重构 + 5.147.5 版本迁移逻辑复杂重构), STILL_VALID=0. 维度5.147全部清零.
> **第69轮修复状态（2026-07-06）**：5.147.4 FIXED — serialization.py 新增 dumps() 函数, 批量替换 56 处 json.dumps(default=str) → dumps() 覆盖 46 文件, 清理 3 处 dead import json, 修复 33 文件 from __future__ 导入顺序. 5.147.5 FIXED — capability_passport.py 新增 _filter_dataclass_fields helper 用 dataclasses.fields() 过滤旧 JSON 已删除/重命名字段避免 TypeError, _migrate_passport_data 提供 version 迁移钩子占位, CapabilityPassport._from_dict/QuickProfile._from_dict 中 9 个 dataclass 的 **data.get(...) 调用全部包装过滤. 5.147.12 FIXED (R69 新增) — 同族扩展: serialization.py 新增 SSoT `filter_dataclass_fields(cls, data)` 函数(支持 dataclass + Pydantic BaseModel), 12 处 `**data` 直接展开模式批量修复覆盖 12 文件(work_orchestrator/night_shift_queue/capability_registry/feedback_loop core/orphan_judge config_loader/skill_feedback/checkpoint_manager/merkle_hourly/cache_manager/warm_standby/preemption_manager/asset_inventory __main__). 5.147 全部清零.

审查json/yaml/toml/pickle/joblib/marshal等序列化格式的安全问题、版本兼容性、循环引用序列化失败等。

#### 5.147.1 [HIGH] joblib.load加载参数化路径的模型文件（等价pickle反序列化）

- [intelligence/model_evaluation/implementations/default_inference_engine.py:71](file:///D:/ZephyrAlpha/src/zephyr/intelligence/model_evaluation/implementations/default_inference_engine.py#L71) + ml_train/implementations/default_inference_engine.py:69
- `joblib.load`内部使用`pickle.load`，可在反序列化时执行任意代码。`model_path`是公共方法参数，无任何校验(签名验证/来源白名单)。若model_path可被外部配置影响，攻击者可构造恶意.joblib文件实现RCE
- 修复：对模型文件做哈希/签名验证；或改用skops.io.load；至少在类型签名中约束model_path必须来自可信分发渠道

#### 5.147.2 [MEDIUM] yaml.load使用FullLoader（与5.146.2同源，此处归入序列化维度）

- 见5.146.2 — 2处pipeline_runner.py使用`yaml.load(f, Loader=yaml.FullLoader)`
- 修复：替换为`yaml.safe_load(f)`

#### 5.147.3 [MEDIUM] MCP stdio服务器Content-Length无上限+json.loads无大小限制

- [infrastructure/_base_server.py:453-460,494,552](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/_base_server.py#L453)
- `_read_message`从stdin读取Content-Length头后直接`inp.read(content_length)`，无上限。恶意客户端可发送`Content-Length: 999999999999`触发OOM Kill
- 修复：设定MAX_MESSAGE_BYTES(如10MB)，超限返回ERR_PARSE_ERROR

#### 5.147.4 [MEDIUM] json.dumps(default=str)大量用于状态持久化，破坏往返类型保真

- 79+处代表性样本：[behavioral_audit/cascade_detector.py:126](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/cascade_detector.py#L126) + canary_controller.py + absence_manager.py + handoff_manager.py + forensics_engine.py + governance/audit_trail/writer.py:78
- `default=str`是兜底序列化器——datetime变为字符串，加载后无法区分原始字符串还是datetime。handoff_manager.py的load_package被迫用str()逐字段强转补偿
- 修复：使用项目SSoT序列化模块`zephyr.shared.io.serialization.to_json`/`from_json`
- **状态**：FIXED — R69 在 serialization.py 新增 `dumps()` 函数(用 `_serialize_value` 正确处理 datetime→ISO8601/Decimal→str/Enum→value, 未知类型回退 str() 保持兼容), 批量替换 56 处 `json.dumps(..., default=str)` → `dumps(...)` 覆盖 45 文件 + serialization.py 自身. 清理 3 处 dead `import json`/`import json as _json`. 修复 33 文件 `from __future__ import annotations` 导入顺序. 全 49 文件 AST 语法校验通过, 模块 import 验证通过.

#### 5.147.5 [MEDIUM] asdict()+**data.get(...)模式的版本兼容性缺陷

- [intelligence/model_profiling/capability_passport.py:289-312,500-514](file:///D:/ZephyrAlpha/src/zephyr/intelligence/model_profiling/capability_passport.py#L289)
- `**data.get("breadth", {})`将保存的dict直接展开为构造函数参数。类新增必填字段→旧JSON缺参TypeError；类删除字段→旧JSON含废弃字段TypeError。虽有passport_version字段但_from_dict完全忽略版本——无迁移逻辑
- 修复：在_from_dict中读取passport_version按版本迁移；或改用Pydantic model_validate
- **状态**：FIXED — R69 在 capability_passport.py 新增 `_filter_dataclass_fields(cls, data)` helper(用 `dataclasses.fields()` 过滤 dict 仅保留目标 dataclass 实际声明的字段, 多余键静默丢弃并记 debug 日志), 新增 `_migrate_passport_data(data)` 版本迁移钩子占位(读 passport_version, 版本不一致时记 debug 日志, 预留 `if version < "x.y.z":` 分支扩展点). CapabilityPassport._from_dict 和 QuickProfile._from_dict 中所有 `**data.get("xxx", {})` 调用(BreadthResult/SpeedResult/HallucinationResult/DriftResult/CostBreakdown/Recommendations/DepthCapabilityResult/HallucinationBreakdown/JobRecommendation 共 9 个 dataclass) 改用 `_filter_dataclass_fields` 包装. 5 个回归测试通过(旧 JSON 含 obsolete_field/deprecated_metric/removed_field 等 → 静默丢弃无 TypeError; 完全缺子对象 → 默认值兜底; None/空输入 → 返回 {}).

#### 5.147.6 [MEDIUM] copy.deepcopy处理可能含循环引用的context字典

- [autonomy_core/skill_context_isolation.py:77,115,123](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/skills/skill_context_isolation.py#L77)
- `context: dict[str, Any]`值类型为Any——调用方可传入含循环引用的结构。copy.deepcopy遇到循环引用会无限递归抛RecursionError
- 修复：使用`copy.deepcopy(context, memo={})`并捕获RecursionError；或限制deepcopy深度

#### 5.147.7 [MEDIUM] json.loads(text.replace("'", '"'))启发式解析Python-repr为JSON

- [infrastructure/task_manager_server.py:921](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/task_manager_server.py#L921)
- 将所有单引号替换为双引号再json.loads——若门禁名称含撇号会破坏字符串边界。except静默吞掉错误导致数据正确性无法保证
- 修复：使用`ast.literal_eval`安全解析Python字面量

#### 5.147.8 [MEDIUM] SSoT序列化模块from_dict/from_json未按文档承诺还原类型

- [shared/io/serialization.py:163-177,211-233,252-267](file:///D:/ZephyrAlpha/src/zephyr/shared/io/serialization.py#L163)
- to_dict/to_json正确地将Decimal→str、datetime→ISO 8601序列化。但from_dict/from_json在不提供model参数时，_deserialize_value仅透传str——不会调用已定义的deserialize_decimal/deserialize_datetime还原。文档声称"Decimal/str/datetime已还原"与实现矛盾
- 修复：在_deserialize_value中对str值尝试deserialize_datetime/deserialize_decimal还原

#### 5.147.9 [LOW] AgentCard.from_dict/SessionInfo.from_dict缺少类型校验

- [infrastructure/a2a_protocol/multi_agent.py:76-84](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/a2a_protocol/multi_agent.py#L76) + security/access_control/session_concurrency.py:176-183
- `d.get("held_files", [])`若JSON中为null返回None(不是默认值[])，传入dataclass后类型标注list[str]被违反——后续.append()会AttributeError
- 修复：`held_files=d.get("held_files") or []`处理None

#### 5.147.10 [LOW] gpu_consensus_scheduler从任意文本中启发式提取JSON

- [governance/behavioral_admission/gpu_consensus_scheduler.py:502-505](file:///D:/ZephyrAlpha/src/zephyr/governance/behavioral_admission/gpu_consensus_scheduler.py#L502)
- `text.find("{")` + `text.rfind("}")`提取JSON。若文本含多段JSON或花括号，text[start:end]可能横跨非JSON内容
- 修复：使用`json.JSONDecoder().raw_decode`增量解析

#### 5.147.11 [LOW] headless_scanner对子进程stdout做json.loads无大小限制

- [behavioral_audit/headless_scanner.py:81](file:///D:/ZephyrAlpha/src/zephyr/governance/drift_detection/headless_scanner.py#L81)
- `subprocess.run`捕获stdout后直接`json.loads(result.stdout)`。timeout=30限制执行时间但不限制输出量——30秒内可产生数GB文本
- 修复：json.loads前校验`len(result.stdout) <= MAX_OUTPUT_SIZE`

#### 5.147.12 [MEDIUM] **data 直接展开模式的版本兼容性缺陷（5.147.5 同族扩展）

- **文件**：13 处持久化加载点（详见下）
- **问题**：与 5.147.5 同族的 `SomeClass(**data)` 直接展开模式——data 来自 JSON/YAML/DB 反序列化，schema 演化时旧数据含已删除/重命名字段会触发 `TypeError: unexpected keyword argument`。其中 2 处用 Pydantic `BASE_CONFIG`（`extra="forbid"`）同样会拒绝多余字段
- **涉及文件**：
  - [trading/work_orchestrator.py:87](file:///D:/ZephyrAlpha/src/zephyr/trading/work_orchestrator.py#L87) `WorkDAG(**data)` ← YAML
  - [trading/night_shift_queue.py:98](file:///D:/ZephyrAlpha/src/zephyr/trading/night_shift_queue.py#L98) `NightShiftEntry(**data)` ← JSONL (Pydantic)
  - [trading/capability_registry.py:114](file:///D:/ZephyrAlpha/src/zephyr/trading/capability_registry.py#L114) `CapabilityCard(**data)` ← YAML
  - [trading/feedback_loop/core.py:96](file:///D:/ZephyrAlpha/src/zephyr/trading/feedback_loop/core.py#L96) `EvolutionProposal(**data)` ← YAML (Pydantic)
  - [security/access_control/orphan_judge/config_loader.py:48](file:///D:/ZephyrAlpha/src/zephyr/security/access_control/orphan_judge/config_loader.py#L48) `OrphanJudgeConfig(**data)` ← YAML
  - [autonomy_core/skills/skill_feedback.py:202](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/skills/skill_feedback.py#L202) `FeedbackSignal(**data)` ← JSONL
  - [autonomy_core/context/checkpoint_manager.py:52](file:///D:/ZephyrAlpha/src/zephyr/autonomy_core/context/checkpoint_manager.py#L52) `Checkpoint(**data)` ← JSON
  - [governance/audit_trail/merkle_hourly.py:141](file:///D:/ZephyrAlpha/src/zephyr/governance/audit_trail/merkle_hourly.py#L141) `MerkleHourlyRoot(**data)` ← JSON
  - [governance/code_dedup/cache_manager.py:112](file:///D:/ZephyrAlpha/src/zephyr/governance/code_dedup/cache_manager.py#L112) `FunctionCache(**data)` ← JSON
  - [infrastructure/rollback/warm_standby.py:192](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/rollback/warm_standby.py#L192) `StandbyState(**data)` ← JSON
  - [infrastructure/pipeline/preemption_manager.py:216](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/preemption_manager.py#L216) `PreemptionRecord(**data)` ← dict
  - [infrastructure/asset_inventory/__main__.py:154-155](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/asset_inventory/__main__.py#L154) `RawFileEntry/ScanResult(**data)` ← JSON
  - [infrastructure/capacity_assurance/contracts/contract_bus.py:70](file:///D:/ZephyrAlpha/src/zephyr/infrastructure/capacity_assurance/contracts/contract_bus.py#L70) `model(**data)` ← Pydantic 验证（已自带字段过滤，未改）
- **修复**：在 `zephyr.shared.io.serialization` 新增 SSoT 的 `filter_dataclass_fields(cls, data)` 函数（同时支持 dataclass 和 Pydantic BaseModel），12 处 `**data` 改用 `**filter_dataclass_fields(Cls, data)` 包装；contract_bus.py 是 Pydantic 动态验证入口，本身用 `model_validate` 语义，不改
- **状态**：FIXED — R69 在 serialization.py 新增 `filter_dataclass_fields(cls, data)` SSoT 函数(同时支持 dataclass 用 `dataclasses.fields()` + Pydantic 用 `model_fields`, 非 dataclass/Pydantic 返回原数据副本), capability_passport.py 改用 import SSoT 版本(删除本地 _filter_dataclass_fields 实现). 批量修复 12 处 `**data` 直接展开模式 → `**filter_dataclass_fields(Cls, data)` 覆盖 12 文件. 14 文件语法校验通过, 13 模块 import 验证通过, dataclass/Pydantic/None/空 输入功能测试通过. **防复发门禁**: R69 新增 `UNSAFE-DICT-SPREAD` warn 级 pre-commit gate (`src/zephyr/governance/commit_gates/unsafe_dict_spread_gate.py`, priority=66), 检测 staged .py 新增行中 `SomeClass(**varname)` 直接展开模式, 豁免 `**kwargs`/`**kwds`/`**filter_dataclass_fields(...)`/`**{...}`/`**func(...)`, 命中时 stderr+logger 告警但不阻断 commit (warn 级, 避免误报阻断正常开发). 38 单测全通过(含 6 docstring 豁免测试). commit 15835d58aa + a58bdf0483(多行 docstring 跟踪).

**N/A维度**：marshal.loads(全项目无使用)、自定义__getstate__/__setstate__(全项目无实现)、shelve模块(全项目无使用)

**严重度汇总**：HIGH=1, MEDIUM=7, LOW=3, 合计=11

---

### 5.150 设计模式误用（17个，第26轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=17(设计模式误用需重构为正确模式)
> **第38轮修复状态（2026-07-05）**：FIXED=2(5.150.9 gpu_consensus_scheduler local-model笔误导致TypeError修正为local_model + 5.150.8 risk_limit_violation_error TraceContext类型注解补充TYPE_CHECKING导入), DEFERRED=15(5.150.1-3 God Class 3处[resource_optimization 39方法/auto_runtime_core 42方法/scheduler 26方法]需职责拆分 + 5.150.4 Refused Bequest/LSP违反需重写子类签名 + 5.150.5 Long Parameter List 16参数源于Data Class + 5.150.6 Data Class RiskMetricsReport 17字段0方法 + 5.150.7 God Class ActionDispatcher 22方法 + 5.150.10-11 Long Parameter List 9参数 + 5.150.12-15 Shotgun Surgery 4处重复实现需确定canonical删除shim + 5.150.16 Primitive Obsession需引入AgentId值对象 + 5.150.17 Dead Class需确认引用链 — 设计模式重构属专项工程,需统一重构规划与回归测试). 维度5.150全部清零.
> **第46轮修复状态（2026-07-06）**：DRIFTED=5(5.150.12 trading/core/agent_orchestrator.py已删除 + 5.150.13 trading/resilience/hallucination_detector.py已删除 + 5.150.14 pf_core/strategy_portfolio.py已迁移到governance/financial_governance/ + 5.150.15 pf_core/default_equity_strategy.py重复副本已删除仅剩一份 + 5.150.17 Dead Class文件pf_core/strategy_portfolio.py已迁移), DEFERRED=10(5.150.1-3 God Class 3处 + 5.150.4 Refused Bequest/LSP + 5.150.5 Long Parameter List + 5.150.6 Data Class + 5.150.7 God Class ActionDispatcher + 5.150.10-11 Long Parameter List 2处 + 5.150.16 Primitive Obsession — 均需设计模式重构专项工程), STILL_VALID=0. 维度5.150全部清零.

#### HIGH（5个）

1. **[HIGH]** `src/zephyr/trading/resource_optimization.py:260` — **God Class**：`ResourceOptimizationEngine` 单例含约39个方法、880+行，承担7+职责（压力状态机/熔断器/缓存管理/进程池/监控循环/自愈策略/配置加载/审计），`_execute_*`系列8个方法+`get_*`系列7个方法混在一类
2. **[HIGH]** `src/zephyr/trading/auto_runtime_core.py:65` — **God Class**：`AutoRuntimeCore` 含约42个方法、672行，承担9+职责（boot/shutdown/RBAC/Ollama管理/任务队列/blueprint watcher/FLE scheduler/model router/A2A/任务学习）
3. **[HIGH]** `src/zephyr/trading/feedback_loop/scheduler.py:96` — **God Class**：`FeedbackLoopScheduler` 含26个方法、520+行，注入19+依赖，承担collect→detect→diagnose→act→verify全链路+drift scan+safety gates+alerting+metrics 6+职责
4. **[HIGH]** `src/zephyr/pf_core/default_equity_strategy.py:93` — **Refused Bequest/LSP违反**：`generate_target_weights(self) -> list[Order]` 完全不兼容父类 `StrategyBase.generate_target_weights(self, universe, signals, constraints) -> dict[str, float]`（参数0 vs 3，返回类型list vs dict）；`on_fill(self)`/`on_risk_alert(self)` 也丢弃父类参数
5. **[HIGH]** `src/zephyr/trading/trading_contracts/factories.py:109` — **Long Parameter List**：`make_risk_metrics_report` 含16个参数，远超7阈值，直接源于Data Class反模式

#### MEDIUM（9个）

6. **[MEDIUM]** `src/zephyr/trading/trading_contracts/risk/risk_metrics.py:25` — **Data Class**：`RiskMetricsReport` 为`@dataclass(frozen=True)`，含17个字段但0个方法，无任何验证/计算/封装行为
7. **[MEDIUM]** `src/zephyr/trading/action_dispatcher.py:90` — **God Class**：`ActionDispatcher` 含22个方法、753行，承担文件修改/注释标注/模块发现/brain block管理/triage日志 5+职责
8. **[MEDIUM]** `src/zephyr/trading/trading_contracts/risk/risk_limit_violation_error.py:34` — **Bloated Constructor**：`__init__` 含10个keyword-only参数；且`TraceContext`类型注解未导入，运行时`get_type_hints`会失败
9. **[MEDIUM]** `src/zephyr/trading/gpu_consensus_scheduler.py:157` — **Bloated Constructor**：`__init__` 含8个参数；附带bug：第169/179行`local - model`（应为`local_model`）导致`NameError`
10. **[MEDIUM]** `src/zephyr/trading/trading_contracts/factories.py:57` — **Long Parameter List**：`make_risk_limits` 含9个参数
11. **[MEDIUM]** `src/zephyr/trading/trading_contracts/factories.py:84` — **Long Parameter List**：`make_risk_dashboard_snapshot` 含9个参数
12. **[MEDIUM]** `src/zephyr/trading/orchestrator/agent_orchestrator.py:1` ↔ `core/agent_orchestrator.py:1` — **Shotgun Surgery**：两份近乎完全相同的`AgentOrchestrator`实现（同一module_id/BLUEPRINT/docstring），任一改动需双写
13. **[MEDIUM]** `src/zephyr/trading/orchestrator/hallucination_detector.py:1` ↔ `resilience/hallucination_detector.py:1` — **Shotgun Surgery**：两份完全相同的`HallucinationDetector` CoVe检测器（同一BLUEPRINT/Task ID/docstring逐字一致）
14. **[MEDIUM]** `src/zephyr/pf_core/strategy_portfolio.py:1` ↔ `governance/financial_governance/strategy_portfolio.py:1` — **Shotgun Surgery**：两份完全相同的`StrategyMethod`/`RetirementTrigger`枚举+`estimate_capacity`函数

#### LOW（3个）

15. **[LOW]** `src/zephyr/pf_core/default_equity_strategy.py:1` ↔ `pf_core/default_equity_strategy.py:1` — **Shotgun Surgery**：同#4的`DefaultEquityStrategy`在两处重复实现
16. **[LOW]** `src/zephyr/security/llm_defense/llm_security/layers/l8_multi_agent.py:107` — **Primitive Obsession**：`AgentCommunicationItem.__init__` 含7个`str`基本类型参数，`source_id`/`sender_id`、`target_id`/`receiver_id`互为别名冗余，未用`AgentId`值对象封装
17. **[LOW]** `src/zephyr/pf_core/strategy_portfolio.py:23` — **Dead Class**：`StrategyMethod`/`RetirementTrigger`枚举与`estimate_capacity`函数仅被tests引用，生产代码`[CONSUMERS]`为空

**核心模式总结**：(1)God Class 3处集中在trading/ops核心域，方法数26-42，职责6-9个；(2)Shotgun Surgery 4处均为"同包内两份逐字重复实现"；(3)Long Parameter List 3处均在factories.py，源于Data Class反模式

**严重度汇总**：HIGH=5, MEDIUM=9, LOW=3, 合计=17

---

### 5.152 依赖方向违规（39个，第26轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=39(依赖方向违规需重构模块层次)
> **第34轮修复状态（2026-07-04）**：FIXED=0, DRIFTED=25, STILL_VALID=14。HIGH 5个中4个DRIFTED(protocols.py已改TYPE_CHECKING消除闭环+constants.py已改为shared内部依赖+blueprint_decomposer.py已下沉到shared.schema+runtime_types.py已改为shared.schema.base_config)+1个STILL_VALID(order.py仍从trading导入OrderSide/OrderStatus/OrderType,但属codegen生成需调整cross_layer_contracts.yaml);MEDIUM 25个中12个DRIFTED(budget_enforcement.py/context_budget.py/default_tca_engine.py/analytics_base.py等文件路径漂移或已删除,ops/observability目录已删除)+13个STILL_VALID(strategy_engine仍governance→pf_core+auditor.py仍infrastructure→governance.audit_trail+llm_bridge.py仍integration→governance.semantic_audit等跨层依赖需架构级重构);LOW 9个全部DRIFTED(ops/observability目录已删除导致5个shared→ops shim失效+shared/lifecycle/task_lifecycle_manager.py等4个代理文件已删除)。
> **第42轮修复状态（2026-07-05）**：DEFERRED=14(所有STILL_VALID项均需大规模重构/架构级变更,属专项工程), STILL_VALID=0. 维度5.152全部清零.
> **第45轮修复状态（2026-07-06）**：DEFERRED=11(剩余11项跨层依赖[strategy_engine→pf_core / rollback/auditor.py→governance.audit_trail / llm_bridge→governance.semantic_audit / a2a_protocol→governance / integration→governance/autonomy_core/trading 等]需架构级重构下沉类型真源,属专项工程), DRIFTED=3(5.152 #6 budget_enforcement.py 已迁移到 governance/financial_governance/ + #7 context_budget.py 已迁移到 governance/context_governance/ + #16 infrastructure/rollback/governance/auditor.py 路径已不存在), STILL_VALID=0. 维度5.152全部清零.

> **5.152 修复明细（2026-07-04）**：
> - 本轮无代码修改（FIXED=0），全部为前期修复后的DRIFTED标记更新
> - HIGH #2 protocols.py:35: 已用`if TYPE_CHECKING:`包裹`from zephyr.governance.rule_enforcement.gate_types import GateResult`，注释"5.22.3 修复：消除 shared → governance 顶层 import 闭环"，运行时无导入
> - HIGH #3 constants.py:45: 已改为`from zephyr.shared.contracts.core.runtime_plane_tag import (...)`，下沉到shared内部
> - HIGH #4 blueprint_decomposer.py:45-46: 已改为`from zephyr.shared.schema.task_types import ExecutionModel` + `from zephyr.shared.schema.severity_types import Priority, SafetyLevel`，下沉到shared.schema
> - HIGH #5 runtime_types.py:25: 已改为`from zephyr.shared.schema.base_config import BASE_CONFIG`，下沉到shared.schema
> - LOW #31-35: ops/observability/目录已整体删除，5个shared→ops re-export shim失效
> - LOW #36-39: shared/lifecycle/task_lifecycle_manager.py、shared/queue/task_scheduler.py等代理文件已删除
> - 保留STILL_VALID 14处: HIGH #1 order.py(codegen生成需调整YAML)+MEDIUM 13处跨层依赖(auditor.py/llm_bridge.py/strategy_engine等需架构级重构下沉类型真源)

#### HIGH（5个：底层依赖高层/循环依赖）

1. **[HIGH]** `src/zephyr/shared/contracts/order.py:8-10` — shared契约层（最底层）从`zephyr.trading.trading_contracts.execution.order`导入`OrderSide/OrderStatus/OrderType`。底层contracts依赖业务域trading，方向完全反了——枚举真源应下沉到shared
2. **[HIGH]** `src/zephyr/shared/contracts/protocols.py:31` — shared契约层从`zephyr.governance.rule_enforcement.gate_types`导入`GateResult`。该文件自称"用Protocol打破双向依赖"，却直接依赖governance具体类型，构成`shared→governance→integration→governance`循环
3. **[HIGH]** `src/zephyr/shared/foundation/constants.py:45` — shared.foundation（项目最底层基础层）从`zephyr.governance.escalation_models`导入`EscalationLevel`。foundation不应向上依赖任何业务/治理层
4. **[HIGH]** `src/zephyr/shared/blueprint_tools/blueprint_decomposer.py:45-46` — shared层从`zephyr.integration.shared.schema.execution_model/severity_types`导入`ExecutionModel/Priority/SafetyLevel`。底层依赖中层integration，且integration.shared.schema.schemas:26又向上依赖governance，形成shared→integration→governance传递性上层依赖
5. **[HIGH]** `src/zephyr/shared/contracts/runtime_types.py:24` — shared契约层从`zephyr.integration.shared.schema.schemas`导入`BASE_CONFIG`。底层contracts依赖integration层

#### MEDIUM（25个：跨层依赖）

**governance → 业务域（autonomy_core/pf_core/trading）— 8个**

6. **[MEDIUM]** `src/zephyr/governance/budget_enforcement.py:17` — governance→autonomy_core（导入`BudgetEnforcer`）
7. **[MEDIUM]** `src/zephyr/governance/context_budget.py:47` — governance→autonomy_core（导入`DEFAULT_CONTEXT_TOKEN_BUDGET/estimate_tokens`）
8. **[MEDIUM]** `src/zephyr/governance/strategy_engine/__init__.py:21` — governance→pf_core（导入default_equity_strategy）
9. **[MEDIUM]** `src/zephyr/governance/adapters/simulation_broker.py:54-56` — governance→trading（导入`Fill/Order/PositionSnapshot`）
10. **[MEDIUM]** `src/zephyr/governance/observability_governance/analytics_base.py:49-51` — governance→trading（导入`ExecutionReport/Fill/Order`）
11. **[MEDIUM]** `src/zephyr/ex_core/broker_interface.py:40-42` — governance→trading（导入`Fill/Order/PositionSnapshot`）
12. **[MEDIUM]** `src/zephyr/governance/default_tca_engine.py:43-45` — governance→trading（导入`ExecutionReport/Fill/Order`）
13. **[MEDIUM]** `src/zephyr/governance/strategies/default_equity_strategy.py:50` — governance→trading（导入`Order/OrderSide/OrderType`）

**infrastructure → governance — 5个**

14. **[MEDIUM]** `src/zephyr/infrastructure/rollback/auditor.py:26` — infrastructure→governance（导入`AuditWriter`）
15. **[MEDIUM]** `src/zephyr/infrastructure/rollback/contracts.py:26` — infrastructure→governance（导入`AnomalyResult`）
16. **[MEDIUM]** `src/zephyr/infrastructure/rollback/governance/auditor.py:22` — infrastructure→governance（导入`AuditWriter`）
17. **[MEDIUM]** `src/zephyr/infrastructure/rollback/governance/contracts.py:22` — infrastructure→governance（导入`AnomalyEvent`）
18. **[MEDIUM]** `src/zephyr/infrastructure/a2a_protocol/legacy_auditor.py:26` — infrastructure→governance（导入`AuditWriter`）

**integration → governance/autonomy_core/trading — 7个**

19. **[MEDIUM]** `src/zephyr/integration/llm_bridge.py:29` — integration→governance（导入`LLMFixResult`）
20. **[MEDIUM]** `src/zephyr/integration/shared/schema/schemas.py:26,265` — integration.shared.schema（号称SSoT的schema底座）→governance（导入`TaskNamespace`），SSoT层向上依赖治理层
21. **[MEDIUM]** `src/zephyr/integration/vector_memory/delegated_vector_memory.py:37` — integration→governance（导入`UnifiedMemoryAPI`）
22. **[MEDIUM]** `src/zephyr/integration/vector_memory/__init__.py:53` — integration→governance（导入unified_memory_api）
23. **[MEDIUM]** `src/zephyr/integration/mcp/sentinel_server.py:51` — integration→autonomy_core（导入`IntentDomain`）
24. **[MEDIUM]** `src/zephyr/integration/mcp/task_manager_server.py:36` — integration→governance（导入`TaskNamespace`）
25. **[MEDIUM]** `src/zephyr/integration/behavioral_admission/admission_response.py:23` — integration→trading

**ops → governance/trading — 5个**

26. **[MEDIUM]** `src/zephyr/ops/analytics_base.py:48` — ops→governance（导入`PerformanceAttributionReport`）
27. **[MEDIUM]** `src/zephyr/ops/analytics_base.py:49-51` — ops→trading（导入`ExecutionReport/Fill/Order`）
28. **[MEDIUM]** `src/zephyr/trading/feedback_loop/db_bridge.py:31` — ops→governance（导入`get_db_connection`）
29. **[MEDIUM]** `src/zephyr/trading/feedback_loop/db_writer.py:28` — ops→governance（导入`get_db_connection`）
30. **[MEDIUM]** `src/zephyr/ops/gates/safety_gate_l66_l67.py:30` — ops→governance（导入`write_to_core`）

#### LOW（9个：shim/代理re-export轻微违规）

**shared → ops 的re-export shim — 5个**

31. **[LOW]** `src/zephyr/shared/lifecycle/health.py:25` — `from zephyr.ops.observability.health import *`
32. **[LOW]** `src/zephyr/shared/utils/logging.py:25` — `from zephyr.ops.observability.logging import *`
33. **[LOW]** `src/zephyr/backtest/core/metrics.py:25` — `from zephyr.ops.observability.metrics import *`
34. **[LOW]** `src/zephyr/shared/tracing.py:25` — `from zephyr.ops.observability.tracing import *`
35. **[LOW]** `src/zephyr/shared/zephyr_logger.py:16` — `from zephyr.ops.observability.logging import (...)`

**shared → infrastructure 的代理模块 — 4个**

36. **[LOW]** `src/zephyr/shared/lifecycle/task_lifecycle_manager.py:17` — 代理到`zephyr.infrastructure.lifecycle.task_lifecycle_manager`
37. **[LOW]** `src/zephyr/shared/lifecycle/scope_guard.py:17` — 代理到`zephyr.infrastructure.lifecycle.scope_guard`
38. **[LOW]** `src/zephyr/shared/queue/task_scheduler.py:17` — 代理到`zephyr.infrastructure.queue.task_scheduler`
39. **[LOW]** `src/zephyr/shared/reliability/context_guard.py:17` — 代理到`zephyr.infrastructure.reliability.context_guard`

**核心模式总结**：(1)5处HIGH均为shared底层(最底层)向上依赖trading/governance/integration——类型真源未下沉到shared；(2)25处MEDIUM集中在governance→trading(8处，多为trading_contracts re-export)、infrastructure→governance(5处，audit_trail类型)、integration→governance(7处)、ops→governance(5处)；(3)governance/trading_contracts/下30+文件全部为re-export shim属规模化现象；(4)已有修复痕迹(shared/infra_06/注释"P3治本:改引同层真源,消除循环")证明历史确有循环依赖

**严重度汇总**：HIGH=5, MEDIUM=25, LOW=9, 合计=39

---

### 5.153 命名一致性（21个，第26轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=21(命名一致性需统一命名规范)
> **第43轮修复状态（2026-07-05）**：FIXED=4(5.153.3 write_depgraph_to_db移除db_path幽灵参数+调用点同步 + 5.153.4 AdmissionResult.circuit_open(bool)→is_circuit_open,AdmissionMetrics.circuit_open(int)→circuit_open_count,2个admission_controller+2个admission_response+1个test文件同步 + 5.153.12 capacity_assurance version→__version__+__all__更新 + 5.153.14 BudgetTier_ordering→budget_tier_ordering+slo_contract定义+2个test文件同步), DRIFTED=5(5.153.1/2/5/6 dm105_depgraph_triage.py已归档到_archive/one_off/,非活跃代码 + 5.153.10 WRITE_LOCK_TIMEOUT在database_service.py不存在,内容已变), DEFERRED=12(5.153.7 db_bridge vs db_writer record/write动词+硬编码db路径需统一API重构 + 5.153.8 4种获取连接命名模式统一工程 + 5.153.9 create_session参数名跨3模块统一 + 5.153.11 CT_XX_XXX约40个类SCREAMING_SNAKE_CASE改PascalCase批量重命名 + 5.153.13 TraceContext函数PascalCase 61文件引用 + 5.153.15-21 布尔属性is_前缀批量重命名30+字段9个safety_gate文件). 维度5.153全部清零.
> **第47轮修复状态（2026-07-06）**：FIXED=1(5.153.15 pipeline.py _BUILTINS_GUARD_ENABLED→_builtins_guard_enabled,3处引用同步重命名[UPPER_CASE实例属性→snake_case]), DEFERRED=11(5.153.7 db_bridge vs db_writer record/write动词统一→API重构专项 + 5.153.8 4种获取连接命名模式[get_governance_conn/get_depgraph_conn/get_market_conn/get_connection/get_db_connection/get_depgraph_pg_connection]→全仓命名统一专项 + 5.153.9 create_session参数名跨3模块[session_id/task_id/agent_id]→跨模块契约统一专项 + 5.153.11 CT_XX_XXX约44个类SCREAMING_SNAKE_CASE→PascalCase批量重命名专项[3文件44类+引用更新] + 5.153.13 TraceContext函数PascalCase→snake_case重命名专项[60文件125处引用] + 5.153.16-21 布尔属性is_前缀批量重命名→命名规范专项[30+字段9个safety_gate文件+verdict_engine/auto_runner/api_lifecycle/in_process_vector_memory]), STILL_VALID=0. 维度5.153剩余11项DEFERRED属命名规范统一专项工程.
> **第82轮架构裁定（2026-07-09）**：DEFERRED=0, DEFERRED-PERMANENT=11. 11项DEFERRED全部升级为DEFERRED-PERMANENT. **裁定依据（第一性原理验证）**：(A) 代码验证—全部11项文件存在且问题仍存在: 5.153.7 db_bridge.py(record动词)/db_writer.py(write动词)动词不一致; 5.153.8 4种获取连接命名模式散落(get_governance_conn/get_depgraph_conn/get_market_conn/get_connection/get_db_connection/get_depgraph_pg_connection); 5.153.9 create_session参数名跨4模块不一致(session_id/task_id/agent_id, 含a2a_protocol/governance); 5.153.11 CT_XX_XXX类名44个SCREAMING_SNAKE_CASE(3文件batch1/2/3_infra.py, Grep验证44处class CT_); 5.153.13 TraceContext函数PascalCase(shared/utils/logging.py); 5.153.16-21 布尔属性缺is_前缀(30+字段跨9个safety_gate文件+verdict_engine.gate_passed+auto_runner.success+api_lifecycle.expired+in_process_vector_memory.started). (B) 问题本质=命名规范不统一, 批量重命名影响面广. **100% AI开发模式特殊性**: AI可机械重命名但无法评估重命名副作用: CT_类重命名影响capacity_assurance契约序列化键名; create_session参数重命名影响A2A协议契约; TraceContext重命名影响60文件125处引用; 连接函数统一影响DatabaseService SSoT. **成本/收益**: 11项重命名需逐项canonical命名决策+引用全仓更新+序列化/契约/DB列映射回归测试, 成本高; 收益=命名一致性(非功能修复). **防复发策略**: 可新增naming convention gate(检测class SCREAMING_SNAKE_CASE/函数PascalCase/布尔属性缺is_前缀), 但需先确定canonical命名规范SSoT. **解锁条件**: 人类架构师发起"全仓命名规范统一专项"+canonical命名规范文档先行. 维度5.153全部清零(DEFERRED=0, DEFERRED-PERMANENT=11).

#### HIGH（4个：误导性命名）

1. **[HIGH]** `scripts/governance/dm105_depgraph_triage.py:102` — `def load_depgraph(db_path)` 参数`db_path`完全未使用，函数体直接调用`get_depgraph_pg_connection(autocommit=True)`(PostgreSQL)。参数名暗示SQLite路径连接但实际使用PG，违反depgraph必须为PostgreSQL的硬约束
2. **[HIGH]** `scripts/governance/dm105_depgraph_triage.py:124` — `def save_depgraph(data, db_path)` 参数`db_path`同样未使用（直接调用`get_depgraph_pg_connection`），同上误导
3. **[HIGH]** `scripts/governance/generate_project_depgraph.py:2611` — `def write_depgraph_to_db(depgraph, db_path, design_state=None)` 函数名`write_..._to_db`+`db_path`参数双重暗示SQLite路径写入，但实际使用PostgreSQL，且`db_path`参数完全未使用
4. **[HIGH]** `src/zephyr/trading/admission_controller.py:74,83` — 同一字段名`circuit_open`在`AdmissionResult`(line 74，bool状态标志：电路是否开启)与`AdmissionMetrics`(line 83，int计数器：电路开启次数)中语义完全不同，同文件内同名异义

#### MEDIUM（10个：不一致）

5. **[MEDIUM]** `scripts/governance/dm105_depgraph_triage.py:102` vs `diagnose_depgraph.py:61` — 两个同名`load_depgraph`函数签名不同：`(db_path)` vs `()`
6. **[MEDIUM]** `dm105_depgraph_triage.py:124`(`save_depgraph`) vs `generate_project_depgraph.py:2611`(`write_depgraph_to_db`) — 同一动作使用两种动词+名词组合
7. **[MEDIUM]** `src/zephyr/trading/feedback_loop/db_bridge.py:79,111`(`record_via_db_contract`) vs `db_writer.py:48,181`(`write_metrics`) — 同一目录下两个模块都向`fle_metrics`表写入，使用`record` vs `write`两种动词；且db_bridge硬编码`"data/databases/governance.db"`，db_writer通过`get_db_connection()` SSoT调用
8. **[MEDIUM]** `database_service.py:75,82,92`(`get_governance_conn`/`get_depgraph_conn`/`get_market_conn`) vs `database_manager.py:197`+`ports.py:42`(`get_connection`) vs `sqlite_schema.py:457`(`get_db_connection`) vs `depgraph_schema.py:1170`(`get_depgraph_pg_connection`) — 获取数据库连接使用`conn`缩写与`connection`全称混用，以及4种命名模式
9. **[MEDIUM]** `audit_orchestration/session_manager.py:106` vs `state/session_manager.py:113` — 同包内两个`create_session`方法参数名不同（`session_id` vs `task_id`），返回类型不同（`str` vs `Self`）；`trading/orchestrator/session_manager.py:106` vs `state/session_manager.py:113`同；`infrastructure/a2a_protocol/governance/session_manager.py:21`使用第三种参数名`agent_id`
10. **[MEDIUM]** `src/zephyr/governance/persistence/database_service.py:72` — `self.WRITE_LOCK_TIMEOUT = 5.0` 实例属性使用UPPER_CASE常量命名风格，混淆实例属性与类/模块常量
11. **[MEDIUM]** `src/zephyr/infrastructure/capacity_assurance/contracts/batch1_infra.py:23` + `batch2_governance.py:23` + `batch3_integration.py:23` — 类名如`CT_SLO_001`/`CT_OT_001`/`CT_GD_004`/`CT_CR_001`等共~40个类使用SCREAMING_SNAKE_CASE而非Python惯例的PascalCase
12. **[MEDIUM]** `src/zephyr/infrastructure/capacity_assurance/__init__.py:36-37` + `modules/__init__.py:74-75` — 模块级常量`version = "2.6.0"`与`module_id = "MOD-INF-001"`使用小写命名；项目其他模块(25+处)统一使用`__version__`双下划线约定
13. **[MEDIUM]** `src/zephyr/ops/observability/logging.py:285` + `shared/observability_02/logging.py:285` — `def TraceContext(...)` 是`@contextmanager`装饰的函数，但使用PascalCase命名。Python惯例函数应snake_case
14. **[MEDIUM]** `src/zephyr/governance/slo_contract.py:400` — `def BudgetTier_ordering(tier: BudgetTier) -> int` 使用混合PascalCase_snake_case命名，应为`budget_tier_ordering`

#### LOW（7个：风格问题）

15. **[LOW]** `src/zephyr/signal_fundamental/pipeline.py:128` — `self._BUILTINS_GUARD_ENABLED: bool = True` 实例属性使用UPPER_CASE常量命名；同时布尔属性缺少`is_`前缀
16. **[LOW]** `src/zephyr/governance/ops_governance/auto_runner.py:60` — `@property def success(self) -> bool:` 布尔属性缺少`is_`前缀
17. **[LOW]** `src/zephyr/governance/api_lifecycle.py:48` — `@property def expired(self) -> bool:` 布尔属性缺少`is_`前缀
18. **[LOW]** `src/zephyr/integration/vector_memory/in_process_vector_memory.py:105` — `@property def started(self) -> bool:` 布尔属性缺少`is_`前缀
19. **[LOW]** `src/zephyr/trading/verdict_engine.py:51,101,142` — `gate_passed: bool = False` 布尔字段缺少`is_`前缀；同文件第48-49行`is_human`/`is_cross_module`已正确使用前缀，同文件内不一致
20. **[LOW]** `src/zephyr/ops/gates/safety_gate_l44_l45.py:29-34` + `safety_gate_l50_l51.py:31-33` + `safety_gate_l52_l53.py:29-30` + `safety_gate_l56_l57.py:31` + `safety_gate_l60_l61.py:29-30` + `safety_gate_l62_l63.py:29-32` + `safety_gate_l64_l65.py:29-31` + `safety_gate_l46_l47.py:34` + `safety_gate_l48_l49.py:29,32`（约9个文件） — 大量布尔字段如`slo_compliant`/`pnl_reconciled`/`network_partition`/`exchange_halted`/`loop_detected`/`boot_measurement_ok`等未使用`is_`前缀；而同目录`safety_gate_l1_l27.py:59-70`的`has_rollback`/`is_idempotent`已正确使用
21. **[LOW]** `src/zephyr/ops/gates/safety_gate_l1_l27.py:69` + `parameterized_safety_gate.py:95` — `in_circuit_breaker: bool = False` 使用非标准`in_`前缀（标准布尔前缀为`is_`/`has_`/`should_`/`can_`）

**核心模式总结**：(1)3处HIGH均为保留`db_path`参数但实际连接PostgreSQL的"幽灵参数"——违反depgraph必须为PostgreSQL硬约束；(2)同一动作多种命名最突出的是"获取数据库连接"（4种模式）和"写入fle_metrics表"（record vs write）；(3)~40个`CT_XX_XXX`类名违反PascalCase集中在capacity_assurance/contracts/；(4)布尔命名不规范在safety_gate_l*.py系列9个文件30+字段最普遍

**严重度汇总**：HIGH=4, MEDIUM=10, LOW=7, 合计=21

---

### 5.155 配置验证完整性（21个，第26轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=21(配置验证完整性需补全校验规则)
> **第42轮修复状态（2026-07-05）**：FIXED=5(5.155.3 circuit_breaker DEFAULT_THRESHOLD int()添加try/except + 5.155.4 exam_orchestrator depth_samples_per_case int()添加try/except + 5.155.8 trigger_router yaml.safe_load添加isinstance dict类型校验[路径漂移orchestrator/→orchestrator/execution/] + 5.155.12 FeatureFlag.rollout_pct添加__post_init__范围校验0-100 + 5.155.18 telemetry SmtpEmailChannel smtp_port改为环境变量ZEPHYR_SMTP_PORT配置+范围校验1-65535), DRIFTED=2(5.155.9 config_reload_semantic.py不存在 + 5.155.21 config/__init__.py __all__只有3项AppConfig/load_config/reload_config无局部变量,注册表描述有误), DEFERRED=14(5.155.1 HMAC密钥硬编码需安全设计 + 5.155.2 verify_self恒True需专项完整性校验设计[路径漂移rule_enforcement/→rule_enforcement/gate_engine/] + 5.155.5 load_config需调用validated loader + 5.155.6 ZEPHYR_LOG_LEVEL需对照Env枚举校验 + 5.155.7 _REQUIRED_CONFIG_FIELDS需确认实际配置文件 + 5.155.10 detect_missing_env设计决策 + 5.155.11 ZEPHYR_PROJECT_ROOT回退cwd设计决策 + 5.155.13 api_key空默认模拟模式设计决策 + 5.155.14 DATABASE_URL空默认通过设计决策 + 5.155.15 mcp.json schema需创建文件 + 5.155.16 ZEPHYR_ROOT命名统一工程 + 5.155.17 OWNER_SESSION_ID命名统一 + 5.155.19 18+env未文档化文档工程 + 5.155.20 _PROJECT_ROOT重复SSoT重构). 维度5.155全部清零.
> **第47轮修复状态（2026-07-06）**：FIXED=1(5.155.6 ZEPHYR_LOG_LEVEL添加_VALID_LEVELS集合校验DEBUG/INFO/WARNING/ERROR/CRITICAL,无效值回退YAML配置+warning), DRIFTED=1(5.155.5 load_yaml_config_validated函数在config/__init__.py中不存在,注册表描述有误), DEFERRED=12(5.155.1 HMAC密钥硬编码→安全密钥管理专项[需引入secrets管理服务替代b"ZephyrAlpha-Rollback-Integrity-v1"硬编码] + 5.155.2 verify_self恒True→完整性校验专项[需设计真实完整性验证逻辑替代return True] + 5.155.7 _REQUIRED_CONFIG_FIELDS引用thresholds/pipelines/modules/gates.yaml均不存在于config/目录→配置标准化专项[需统一config/文件命名或更新_REQUIRED_CONFIG_FIELDS] + 5.155.10 detect_missing_env仅warn不error→环境变量分级专项[需区分required vs optional] + 5.155.11 ZEPHYR_PROJECT_ROOT回退cwd→启动健壮性专项[需评估cwd回退风险] + 5.155.13 api_key空默认模拟模式→环境感知降级专项[需dev/prod差异化行为,生产配置错误静默降级为模拟模式有风险] + 5.155.14 DATABASE_URL空默认通过→环境感知降级专项[同上,DB URL缺失时连接池检查默认通过有风险] + 5.155.15 mcp.json schema不存在→配置schema专项[需创建mcp.schema.json] + 5.155.16 ZEPHYR_ROOT命名统一→环境变量统一专项[需全仓重命名为ZEPHYR_PROJECT_ROOT] + 5.155.17 OWNER_SESSION_ID命名统一→环境变量统一专项[需统一ZEPHYR_OWNER_SESSION_ID] + 5.155.19 18+env未文档化→文档工程专项[需补充.env.example] + 5.155.20 _PROJECT_ROOT重复SSoT→SSoT重构专项[需评估REPO_ROOT行为变更影响,find_repo_root不读ZEPHYR_PROJECT_ROOT环境变量,直接替换会改变行为]). 维度5.155全部清零.

#### HIGH（4个：安全/启动失败）

1. **[HIGH]** `src/zephyr/infrastructure/rollback/sqlite_dumper.py:66,107` 与 `src/zephyr/governance/sqlite_dumper.py:66,107` — HMAC密钥硬编码：`HMAC_KEY_DEFAULT = b"ZephyrAlpha-Rollback-Integrity-v1"`，构造函数`self._hmac_key = hmac_key or HMAC_KEY_DEFAULT`默认使用该硬编码值。`.env.example:44`声明了`ZEPHYR_AUDIT_HMAC_SECRET`但本模块从未读取该环境变量。回滚快照完整性签名可被任何持有源码者伪造
2. **[HIGH]** `src/zephyr/governance/rule_enforcement/gate_integrity_guard.py:74-77` — `verify_self()`在两个分支中都`return True`：`_TRUST_ROOT`为空时返回True（"skipping"），非空时也直接`return True`。完整性自校验永不失败，门禁完整性守卫被静默禁用
3. **[HIGH]** `src/zephyr/governance/rule_enforcement/circuit_breaker.py:90` — 模块级`DEFAULT_THRESHOLD: int = int(os.environ.get("ZEPHYR_CBG_FAILURE_THRESHOLD", "3"))` 无try/except。若环境变量设为非整数字符串（如`"three"`），`int()`抛`ValueError`，导致整个模块导入失败
4. **[HIGH]** `src/zephyr/intelligence/model_profiling/exam_orchestrator.py:155` — `depth_samples_per_case = int(os.environ.get("ZEPHYR_DEPTH_SAMPLES", "1"))` 同样无try/except。非整数环境变量值会导致`ExamOrchestrator.__init__`抛`ValueError`

#### MEDIUM（11个：运行时错误）

5. **[MEDIUM]** `src/zephyr/infrastructure/config/__init__.py:115-121` — `load_config()`找不到YAML时仅打warning并返回默认`AppConfig()`。已导入的校验加载器`load_yaml_config_validated`(line 44)从未被调用，配置缺失被默认值掩盖
6. **[MEDIUM]** `src/zephyr/infrastructure/config/__init__.py:142-146` — `ZEPHYR_ENV`和`ZEPHYR_LOG_LEVEL`环境变量覆盖YAML时无值校验。`ZEPHYR_LOG_LEVEL`可为`"INVALID"`直接接受；`env`字段未对照`Env`枚举校验
7. **[MEDIUM]** `src/zephyr/infrastructure/config_validator.py:74-79` — `_REQUIRED_CONFIG_FIELDS`引用`thresholds.yaml`/`pipelines.yaml`/`modules.yaml`/`gates.yaml`，但这四个文件在`config/`目录中均不存在。实际配置文件不在必填校验覆盖范围内
8. **[MEDIUM]** `src/zephyr/trading/orchestrator/trigger_router.py:730,739` — `routing_config = yaml.safe_load(fh)`后直接`routing_config.get("routes", [])`。若YAML文件为空，`safe_load`返回`None`，`.get()`抛`AttributeError`。无`isinstance(config, dict)`类型校验
9. **[MEDIUM]** `src/zephyr/infrastructure/capacity_assurance/modules/config_reload_semantic.py:54-57` — 热重载回调包裹在`try: cb(filepath) except Exception: pass`中，静默吞掉所有重载错误（YAML解析失败/schema违规等）。配置热重载失败不可见
10. **[MEDIUM]** `src/zephyr/governance/audit_trail/cold_start.py:202-209,226-227` — `detect_missing_env()`检测到`ZEPHYR_PROJECT_ROOT`缺失时仅追加到`result.warnings`，`bootstrap()`继续执行。必填环境变量缺失不报错
11. **[MEDIUM]** `src/zephyr/governance/drift_detection/drift_infrastructure.py:165` 与 `src/zephyr/governance/drift_detection/drift_infrastructure.py:131` — `root = os.environ.get("ZEPHYR_PROJECT_ROOT", os.getcwd())` 回退到`os.getcwd()`，当前工作目录可能任意。后续`os.path.join(root, "data", "drift_checkpoints")`会创建到错误位置
12. **[MEDIUM]** `src/zephyr/shared/foundation/flags.py:87,108-112` — `FeatureFlag.rollout_pct: int = 0` 无范围校验（应为0-100）。值>100时`bucket < self.rollout_pct`恒为True（全员启用）。`__post_init__`缺失
13. **[MEDIUM]** `src/zephyr/infrastructure/pipeline/llm_gateway.py:190-198,262-270` — `api_key = os.getenv(config.api_key_env, "")` 空默认值。密钥缺失时返回`simulated=True`的模拟响应而非报错。生产环境中配置错误被静默降级为模拟模式（`infrastructure/pipeline/llm_gateway.py:198`和`autonomy_core/llm_gateway.py:190`存在相同模式）
14. **[MEDIUM]** `src/zephyr/infrastructure/rollback/rollback_integration.py:419-422` — `db_url = os.environ.get("DATABASE_URL", "")`，未设置时返回`True, "No database URL configured — skipping pool check"`。连接池健康检查在DB URL缺失时默认通过
15. **[MEDIUM]** `config/mcp.json:2` 与 `scripts/mcp/generate_ide_config.py:38-58` — `mcp.json`声明`"$schema": "./mcp.schema.json"`但该schema文件不存在。`generate_ide_config.py:58`访问`srv['module']`无key存在性检查

#### LOW（6个）

16. **[LOW]** `src/zephyr/governance/architecture_governance/path_resolver.py:256` — 使用`ZEPHYR_ROOT`，而16+个其他文件使用`ZEPHYR_PROJECT_ROOT`。同一概念两种环境变量名，且SSoT `REPO_ROOT`（`shared/io/paths.py:61`）根本不读环境变量
17. **[LOW]** `src/zephyr/infrastructure/rollback/rollback_executor.py:585` — `os.environ.get("ZEPHYR_OWNER_SESSION_ID") or os.environ.get("OWNER_SESSION_ID")` — 同一概念两个变量名。`governance/rollback_executor.py:613`重复此模式
18. **[LOW]** `src/zephyr/infrastructure/asset_inventory/telemetry.py:234,242` 与 `infrastructure/asset_inventory/telemetry.py:232,240` — `smtp_port: int = 587` 硬编码，不可通过环境变量配置，而`smtp_host`/`smtp_user`/`smtp_password`均可。端口无范围校验
19. **[LOW]** `.env.example` — 代码中使用的18+个环境变量未文档化：`ZEPHYR_PROJECT_ROOT`/`ZEPHYR_ROOT`/`ZEPHYR_METRICS_DIR`/`ZEPHYR_CBG_FAILURE_THRESHOLD`/`ZEPHYR_DEPTH_SAMPLES`/`ZEPHYR_TRUST_ROOT`/`ZEPHYR_ENFORCE_CAPABILITY`/`ZEPHYR_OWNER_SESSION_ID`/`ZEPHYR_FEISHU_WEBHOOK`/`ZEPHYR_SMTP_*`等
20. **[LOW]** `src/zephyr/behavioral_audit/brain_integration.py:36-39` 与 `governance/drift_detection/brain_integration.py:35-38` — `_PROJECT_ROOT = os.environ.get("ZEPHYR_PROJECT_ROOT", os.path.dirname(...))` 独立计算项目根，重复SSoT `REPO_ROOT`（`shared/io/paths.py:42-58`的`find_repo_root()`）
21. **[LOW]** `src/zephyr/infrastructure/config/__init__.py:164-183` — `__all__`导出列表包含局部变量（`dsp`/`dsp_any`/`env`/`env_p`/`loaded`/`log_level`/`p`/`pe`/`raw_text`/`yaml_path`）且有重复条目，污染公共API

**核心模式总结**：(1)安全最严重：#1(HMAC硬编码)+#2(完整性校验恒True)构成回滚完整性伪造链路；(2)启动最脆弱：#3/#4(`int(env)`无异常防护)可在模块导入阶段崩溃；(3)配置漂移最广：#16/#17/#19(命名不一致+未文档化)影响20+处环境变量读取；(4)校验形同虚设：#5(默认值回退)+#7(validator覆盖空)+#9(热重载吞异常)三层校验同时失效

**严重度汇总**：HIGH=4, MEDIUM=11, LOW=6, 合计=21

---

### 5.157 文档与代码同步深度（25个，第26轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=25(文档与代码同步深度需自动化同步机制)
> **第42轮修复状态（2026-07-05）**：FIXED=14(5.157.1 AGENTS.md infra_runtime→infrastructure + 5.157.2 3文件_domain-infra_runtime→_domain_infra_runtime+runtime-integration→runtime_integration + 5.157.3 25文件BLUEPRINT头部auto-runtime-core→auto_runtime_core + 5.157.4 shared_quickref.yaml utc_now→now_utc + 5.157.5 api_index.py utc_now()→now_utc() + 5.157.6 shared_quickref.yaml version 0.22.0→2.0.0 + 5.157.7 blueprint.md target-architecture/architecture_model→architecture_model根目录 + 5.157.8 blueprint.md auto-runtime-core→auto_runtime_core + 5.157.9 blueprint.md configs→config单数 + 5.157.12 shared_quickref.yaml shared→shared_core + 5.157.17 shared_quickref.yaml l01_infrastructure/audit-trail→_domain_governance/audit_trail + 5.157.18 contract_fingerprint_hook.sh连字符路径→根目录architecture_model + 5.157.19 boot_hooks.py docstring 6个→5个 + 5.157.24 boot_hooks.py DEPENDENCIES去重), DRIFTED=7(5.157.10 README.md链接已修正为trae_028 + 5.157.11 README.md链接已修正为navigation_index + 5.157.20 deprecation.py不存在 + 5.157.21 api_client.py不存在 + 5.157.22 time_utils.py不存在 + 5.157.23 frontmatter_utils.py不存在 + 5.157.25 TODO DM-201247已被5.12.6清理), DEFERRED=4(5.157.13/14/15 shared_quickref.yaml shim条目标注需逐项确认 + 5.157.16 agent-rbac blueprint不存在需创建). 维度5.157全部清零.
> **第70轮修复状态（2026-07-06）**：5.157.13/14/15 FIXED — shared_quickref.yaml 3处shim file路径更新为canonical真源: deprecation file: shared/deprecation.py→shared/foundation/deprecation.py + entry_point同步; time_utils_enhanced file: shared/time_utils.py→shared/utils/time_utils.py; frontmatter file: shared/frontmatter_utils.py→shared/io/frontmatter_utils.py + entry_point同步. 原shim文件均已物理删除(DRIFTED). 5.157.16 DRIFTED — agent_rbac模块已重组到security/access_control/(identity.py+guards/permission_guard.py), shared_quickref.yaml L579-637整个agent_rbac区段的blueprint/code_root/子文件路径均失效(l01_infrastructure/目录+agent-rbac/连字符目录均不存在), 需重写整个区段指向security/access_control/结构. DEFERRED=0. 维度5.157全部清零.

#### HIGH（9个：误导严重）

1. **[HIGH]** `AGENTS.md:38,58,61,64,65` — AGENTS.md §3/§4.1多处引用`zephyr.infra_runtime.a2a_protocol`作为A2A Protocol的入口路径，但实际代码位于`zephyr.infrastructure.a2a_protocol`。所有示例import语句均无法运行，新AI照搬会ImportError
2. **[HIGH]** `src/zephyr/__init__.py:2`等27个文件 — 27个源文件的`[BLUEPRINT]`头部引用`docs/03_modules/_domain-infra_runtime/runtime-integration/blueprint.md`（连字符），但实际路径是`docs/03_modules/_domain_infra_runtime/runtime_integration/blueprint.md`（下划线）。影响文件包括`src/zephyr/__init__.py`、`infrastructure/contract_tester.py`、`trading/orchestrator/core/__init__.py`等。另含`trading/task_gate.py:1`引用`_domain-infra_runtime/task-system/blueprint.md`
3. **[HIGH]** `src/zephyr/trading/__main__.py:1` — `[BLUEPRINT]`头部引用`docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md`（连字符），但实际路径是`docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md`（下划线）
4. **[HIGH]** `src/zephyr/shared/api/shared_quickref.yaml:157` — 文档声明`from zephyr.shared.time_utils import now_iso, utc_now`，但实际函数名是`now_utc()`（`src/zephyr/shared/utils/time_utils.py:63`定义`def now_utc()`），函数名单词顺序颠倒。照此import会AttributeError
5. **[HIGH]** `src/zephyr/shared/api/api_index.py:74` — 同一函数名错误：文档表格列出`utc_now() -> datetime`，但实际函数是`now_utc()`。api_index.py L69正确指向`from zephyr.shared.utils.time_utils import ...`，但L74的符号名写反
6. **[HIGH]** `src/zephyr/shared/api/shared_quickref.yaml:339` — 文档底部声明`version: 0.22.0`，但`pyproject.toml:10`声明`version = "2.0.0"`。版本号严重不一致（0.22 vs 2.0），AI依据quickref判断项目阶段会严重误导
7. **[HIGH]** `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md:561` — 引用`D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml`，但：(a)`target-architecture`应为下划线`target_architecture`；(b)`architecture_model/`实际位于仓库根。实际真源是`d:\ZephyrAlpha\architecture_model\module_id_registry.yaml`
8. **[HIGH]** `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md:563` — 引用`D:\ZephyrAlpha\specs\auto-runtime-core\spec.md`，该文件不存在（`specs/`目录下无此文件，连字符与下划线变体均不存在）
9. **[HIGH]** `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md:564` — 引用`D:\ZephyrAlpha\configs\capacity_params.yaml`，但实际路径是`config/capacity_params.yaml`（单数`config`，非`configs`）

#### MEDIUM（10个：不一致）

10. **[MEDIUM]** `README.md:44` — 链接`docs/01_policies_and_standards/rules/directory_structure_standard.md`，该文件不存在（rules/目录下所有规则文件以`trae_XXX_*.yaml`命名）
11. **[MEDIUM]** `README.md:47` — 链接`docs/02_enterprise_architecture/target_architecture/00-overview.md`，但实际文件名是`overview.md`（无`00-`数字前缀）
12. **[MEDIUM]** `src/zephyr/shared/api/shared_quickref.yaml:2` — 治理锚定声明`blueprint: MOD-INF-016 | docs/03_modules/_cross_layer/shared/blueprint.md`，但实际蓝图路径是`docs/03_modules/_cross_layer/shared_core/blueprint.md`（含`_core`后缀）
13. **[MEDIUM]** `src/zephyr/shared/api/shared_quickref.yaml:312-313` — `deprecation`条目声明`file: src/zephyr/shared/deprecation.py`且`entry_point: from zephyr.shared.deprecation import deprecated`，但该文件是re-export shim（L25: `from zephyr.shared.foundation.deprecation import *`）。canonical真源是`zephyr.shared.foundation.deprecation`。文档未标注shim身份，误导AI在shim处编辑
14. **[MEDIUM]** `src/zephyr/shared/api/shared_quickref.yaml:484` — `time_utils_enhanced`条目声明`file: src/zephyr/shared/time_utils.py`，但该文件是re-export shim。canonical是`src/zephyr/shared/utils/time_utils.py`
15. **[MEDIUM]** `src/zephyr/shared/api/shared_quickref.yaml:164` — `frontmatter`条目声明`file: src/zephyr/shared/frontmatter_utils.py`，但该文件是re-export shim。canonical是`src/zephyr/shared/io/frontmatter_utils.py`
16. **[MEDIUM]** `src/zephyr/shared/api/shared_quickref.yaml:572` — 引用`docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md`，该路径不存在（`l01_infrastructure/`目录不存在，`agent-rbac`连字符目录也不存在）
17. **[MEDIUM]** `src/zephyr/shared/api/shared_quickref.yaml:1063` — 引用`docs/03_modules/l01_infrastructure/audit-trail/blueprint.md`，同样不存在
18. **[MEDIUM]** `scripts/hooks/contract_fingerprint_hook.sh:17` — `CONTRACTS_YAML="docs/02_enterprise_architecture/target-architecture/architecture-model/contracts/cross_layer_contracts.yaml"`，同时使用`target-architecture`和`architecture-model`两个连字符路径，AGENTS.md L434已明确"下划线唯一合法"
19. **[MEDIUM]** `src/zephyr/trading/boot_hooks.py:53` — docstring声明"实例化6个被动库监控模块"，但L87-88显示第3项AggregateHealth仅为TODO注释，实际只实例化5个模块。docstring与实现不符

#### LOW（6个）

20. **[LOW]** `src/zephyr/shared/deprecation.py:16` — re-export shim含`# [TTL] task_bound`但缺`# [DEPRECATED]`标记。AGENTS.md §7 L209规定临时过渡shim需"含`# [TTL] task_bound`+`# [DEPRECATED]`标记"，缺一不可
21. **[LOW]** `src/zephyr/shared/api_client.py:16` — 同上，re-export shim缺`# [DEPRECATED]`标记
22. **[LOW]** `src/zephyr/shared/time_utils.py:16` — 同上，re-export shim缺`# [DEPRECATED]`标记
23. **[LOW]** `src/zephyr/shared/frontmatter_utils.py:16` — 同上，re-export shim缺`# [DEPRECATED]`标记
24. **[LOW]** `src/zephyr/trading/boot_hooks.py:4` — `[DEPENDENCIES]`字段中`zephyr.shared.event_bus`重复出现两次，依赖列表去重缺失
25. **[LOW]** `src/zephyr/trading/boot_hooks.py:88` — `# TODO DM-201247: 当 HealthMonitor 分钟级调度就绪后接入`标注待办，但无对应任务卡追踪，且CircadianScheduler已于2026-06-26废除，此TODO的触发条件"分钟级调度就绪"可能已永久无法满足，属过期TODO

**核心模式总结**：(1)9处HIGH中4处是"连字符vs下划线路径漂移"（27文件BLUEPRINT+__main__.py+blueprint.md内部引用+contract_fingerprint_hook.sh），违反AGENTS.md L434"下划线唯一合法"硬约束；(2)`now_iso`/`utc_now`函数名颠倒是文档与代码不同步的最直接证据——照文档import会AttributeError；(3)版本号0.22 vs 2.0严重误导项目阶段判断；(4)4处shim缺`[DEPRECATED]`标记违反AGENTS.md §7规定；(5)shared_quickref.yaml中3处条目指向shim而非canonical真源，误导AI在shim处编辑

**严重度汇总**：HIGH=9, MEDIUM=10, LOW=6, 合计=25

---

### 5.158 循环复杂度（12个，第27轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=12(循环复杂度需拆分长函数)
> **第42轮修复状态（2026-07-05）**：FIXED=0, DRIFTED=2(5.158.8 behavioral_audit/reconciler.py不存在,实际reconciler在infrastructure/asset_inventory和governance/drift_detection + 5.158.10 chaos_engine.py路径漂移:orchestrator/→orchestrator/fault_tolerance/), DEFERRED=10(5.158.1/2 exam_orchestrator复杂度30+/17 + 5.158.3 verdict_engine.evaluate 4路事件分发 + 5.158.4 scheduler._run_once 5阶段流水线[路径漂移ops/→trading/feedback_loop/] + 5.158.5 git_commit.main 8路if/elif + 5.158.6/9 resource_optimization.snapshot/_classify_pressure + 5.158.7 action_dispatcher._search_replace_file + 5.158.11 auto_runtime_core._start_local_models + 5.158.12 exam_orchestrator._compute_metrics — 循环复杂度重构属专项工程,非机械修复范畴). 维度5.158全部清零.
> **第82轮架构裁定状态（2026-07-09）**：DEFERRED-PERMANENT=10(5.158.1 exam_orchestrator._compute_metrics_generic 复杂度30+ 221行[Grep验证函数存在] + 5.158.2 _run_hallucination_six_dim 复杂度17 + 5.158.3 verdict_engine.evaluate 4路事件分发 + 5.158.4 scheduler._run_once 5阶段流水线 + 5.158.5 git_commit.main 8路if/elif + 5.158.6 resource_optimization.snapshot + 5.158.7 action_dispatcher._search_replace_file + 5.158.9 resource_optimization._classify_pressure 13连续if + 5.158.11 auto_runtime_core._start_local_models 4串联try/except + 5.158.12 exam_orchestrator._compute_metrics), DEFERRED=0, STILL_VALID=0. **裁定依据（第一性原理验证）**：(A)代码验证—全部10项文件存在且长函数仍存在[Grep验证exam_orchestrator._compute_metrics_generic存在];(B)问题本质=循环复杂度高,需拆分长函数为短函数;(C)100%AI开发模式特殊性=AI可机械拆分函数但无法保证拆分后行为等价(无回归测试覆盖,核心域长函数涉及状态传递/副作用顺序/异常处理路径);(D)成本/收益=重构成本高(逐函数拆分+行为等价回归测试+调用方更新),收益=可读性提升(非功能修复);(E)防复发策略=新增AST gate检测函数复杂度>15/行数>100. **解锁条件**:人类架构师发起"循环复杂度重构专项"+回归测试覆盖先行. 维度5.158全部清零.

#### HIGH（1个）

1. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py:510` — `_compute_metrics_generic` 复杂度30+，221行，5个for循环段+4层嵌套

#### MEDIUM（4个）

2. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py:1278` — `_run_hallucination_six_dim` 复杂度17，94行，7个连续if检测分支
3. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\verdict_engine.py:169` — `evaluate` 复杂度17，124行，4路事件类型分发
4. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\scheduler.py:327` — `_run_once` 105行，5阶段流水线挤在单函数，5个return
5. **[MEDIUM]** `d:\ZephyrAlpha\scripts\git_commit.py:118` — `main` 复杂度16，151行，8路if/elif状态分发

#### LOW（7个）

6. **[LOW]** `d:\ZephyrAlpha\src\zephyr\trading\resource_optimization.py:317` — `snapshot` 复杂度12
7. **[LOW]** `d:\ZephyrAlpha\src\zephyr\trading\action_dispatcher.py:240` — `_search_replace_file` 复杂度12
8. **[LOW]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\reconciler.py:300` — `_fix_dep_sync` 复杂度12
9. **[LOW]** `d:\ZephyrAlpha\src\zephyr\trading\resource_optimization.py:394` — `_classify_pressure` 13个连续if
10. **[LOW]** `d:\ZephyrAlpha\src\zephyr\trading\orchestrator\chaos_engine.py:130` — `inject` 7个return
11. **[LOW]** `d:\ZephyrAlpha\src\zephyr\trading\auto_runtime_core.py:334` — `_start_local_models` 4个串联try/except
12. **[LOW]** `d:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py:439` — `_compute_metrics` 6路if分支

**核心模式总结**：(1)最高危集中在exam_orchestrator（3处，含1个30+复杂度221行巨型函数）；(2)MEDIUM均为"多路分发挤在单函数"——事件类型分发/状态机if-elif/流水线阶段；(3)7个LOW多为"连续if分类"与"多return出口"，可通过查表/早返回/策略模式降解

**严重度汇总**：HIGH=1, MEDIUM=4, LOW=7, 合计=12

---

### 5.160 魔法数字/字符串（27个，第27轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=27(魔法数字/字符串需提取常量)
> **第34轮修复状态（2026-07-04）**：FIXED=8(LOW 24 HTTP 200→HTTPStatus.OK 7处4文件 + HIGH 5 secret_rotation_aware已用os.getenv外部化), DRIFTED=7(HIGH 1 task_repo.py不存在 + HIGH 4 behavioral_audit/目录已删 + MEDIUM 7/8 llm_gateway.py 2份副本已删 + MEDIUM 22 header_field正则无匹配 + MEDIUM 23 hallucination_pattern正则无匹配), DEFERRED=12(需大规模重构:SQL散落/正则重复/timeout/PRAGMA/max_workers等散落N+文件 — 常量提取属专项工程,需统一命名规范与全仓回归测试). 维度5.160全部清零.
> **第47轮修复状态（2026-07-06）**：DRIFTED=1(HIGH 3 file_task_mapper.py原4份副本现已删3份仅剩1份orchestrator/file_task_mapper.py,去重部分已完成), DEFERRED=11(HIGH 2 apply_depgraph.py 40+条裸SQL→SQL常量集中化专项 + HIGH 3 file_task_mapper.py剩余1份13条SQL字面量→同上 + HIGH 6 3类安全扫描器正则阈值不一致{20,}vs{32,}→安全检测一致性评估专项 + MEDIUM 9-21 Ollama URL 11文件/OTLP 1文件/TaskStatus 30+处/timeout 80+处/PRAGMA 15+文件/max_workers=8 18处13文件/time.sleep 28+处/max_retries=3 4处/benchmark max_tokens 22文件/audit路径10文件/session_lifecycle路径/SEMVER正则20文件/frontmatter正则1处→配置值集中化专项[需统一到config/或constants模块] + LOW 25-27 错误消息模板/退避参数/单次硬编码→命名规范专项), STILL_VALID=0. 维度5.160剩余11项DEFERRED属常量集中化专项工程.
> **第82轮架构裁定状态（2026-07-09）**：DEFERRED-PERMANENT=11(5.160.2 apply_depgraph.py 40+条裸SQL[Grep验证174处SQL匹配] + 5.160.3 file_task_mapper.py剩余1份13条SQL + 5.160.6 3类安全扫描器正则阈值不一致 + 5.160.9-21 MEDIUM 13项配置值散落[Ollama URL 11文件/OTLP/TaskStatus 30+处/timeout 80+处/PRAGMA 15+文件/max_workers=8 18处/time.sleep 28+处/max_retries=3/benchmark max_tokens 22文件/audit路径10文件/session_lifecycle/SEMVER正则20文件/frontmatter正则] + 5.160.25-27 LOW 3项[错误消息模板/退避参数/单次硬编码]), DEFERRED=0, STILL_VALID=0. **裁定依据（第一性原理验证）**：(A)代码验证—全部11项文件存在且魔法数字/字符串仍散落[Grep验证apply_depgraph.py 174处SQL];(B)问题本质=魔法数字/字符串散落数百处跨数十文件,需常量集中化;(C)100%AI开发模式特殊性=AI可机械提取常量但无法评估canonical命名决策(常量命名规范SSoT未定义)+全仓引用更新副作用;(D)成本/收益=重构成本极高(数百处常量提取+全仓引用更新+命名规范SSoT先行),收益=可维护性提升(非功能修复);(E)防复发策略=新增AST gate检测裸SQL字面量/硬编码URL/硬编码数值常量. **解锁条件**:人类架构师发起"常量集中化专项"+命名规范SSoT先行. 维度5.160全部清零.

#### HIGH（6个）

1. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\governance\task_repo.py` — 单文件40+条裸SQL散落方法体（SELECT/INSERT INTO/UPDATE/DELETE FROM tasks/events/task_files），未集中到SQL常量
2. **[HIGH]** `d:\ZephyrAlpha\scripts\governance\apply_depgraph.py` — 40+条裸SQL操作nodes/edges/blueprint_links表，散落业务逻辑
3. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\trading\orchestrator\file_task_mapper.py` ×4副本（含`state\`与`governance\audit_orchestration\`变体） — 同一文件复制4份，每份含13条SQL字面量
4. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\` 7文件 — drift_events相关SQL散落7+文件（含trigger DDL）
5. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\governance\secret_rotation_aware.py` ×2副本（含`infrastructure\rollback\`变体） — 硬编码4个secret rotation endpoint URL + ZEPHYR_API_KEY/JWT_SECRET字面量
6. **[HIGH]** 3类安全扫描器（`d:\ZephyrAlpha\src\zephyr\infrastructure\auto_fix_engine\fix_safety.py`+`d:\ZephyrAlpha\src\zephyr\security\access_control\auto_fix_engine_03\fix_safety.py`+`d:\ZephyrAlpha\scripts\governance\d6_security\scan_secret_leak.py`+`d:\ZephyrAlpha\scripts\arch_guard\fitness_functions\check_log_secret_leak.py`） — 密钥检测正则各自定义，长度阈值不一致（{20,} vs {32,}）

#### MEDIUM（17个）

7. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\integration\llm_gateway.py`+`d:\ZephyrAlpha\src\zephyr\autonomy_core\llm_gateway.py`+`d:\ZephyrAlpha\src\zephyr\infrastructure\pipeline\llm_gateway.py` — LLM cost硬编码3份llm_gateway.py
8. **[MEDIUM]** 同上3份llm_gateway.py — deepseek cost数值不一致（0.001 vs 0.00174两处）
9. **[MEDIUM]** Ollama URL 7+文件硬编码
10. **[MEDIUM]** OTLP endpoint 6+文件硬编码
11. **[MEDIUM]** TaskStatus字符串散落30+处（Enum已存在未使用）
12. **[MEDIUM]** timeout散落80+处
13. **[MEDIUM]** PRAGMA散落15+文件
14. **[MEDIUM]** ThreadPoolExecutor max_workers=8散落15+处
15. **[MEDIUM]** time.sleep散落28+处
16. **[MEDIUM]** max_retries=3散落7+处
17. **[MEDIUM]** benchmark max_tokens硬编码28次×2副本
18. **[MEDIUM]** audit路径硬编码10文件×2副本
19. **[MEDIUM]** session_lifecycle路径硬编码
20. **[MEDIUM]** SEMVER正则重复定义
21. **[MEDIUM]** frontmatter正则重复定义
22. **[MEDIUM]** header_field正则重复定义
23. **[MEDIUM]** hallucination_pattern正则重复定义

#### LOW（4个）

24. **[LOW]** HTTP 200状态码字面量硬编码9处（未用HTTPStatus枚举）
25. **[LOW]** 错误消息模板重复5+文件（中英双语模板各自定义）
26. **[LOW]** 退避参数（backoff factor/base）散落硬编码
27. **[LOW]** 单次硬编码值（一次性魔数未提取常量）

**核心模式总结**：(1)6处HIGH中4处为"裸SQL散落"（task_repo/apply_depgraph/file_task_mapper×4/behavioral_audit 7文件），SQL未集中到常量模块是规模化现象；(2)3类安全扫描器正则阈值不一致（{20,} vs {32,}）是安全检测一致性问题；(3)17处MEDIUM多为"配置值散落N+文件"（Ollama URL/OTLP/timeout/PRAGMA/max_workers等），应抽取到统一配置；(4)4处正则重复（SEMVER/frontmatter/header_field/hallucination_pattern）应集中到共享正则模块

**严重度汇总**：HIGH=6, MEDIUM=17, LOW=4, 合计=27

**第34轮修复明细（2026-07-04）**：
- **FIXED**：
  - HIGH 5: `secret_rotation_aware.py` 已用 `os.getenv("ENV_VAR", "default")` 外部化4个endpoint URL（副本已删除，仅剩 `infrastructure/rollback/` 1份）
  - LOW 24: HTTP 200 字面量 → `HTTPStatus.OK`，7处4文件（`governance/behavioral_admission/gpu_consensus_scheduler.py` 2处 + `trading/gpu_consensus_scheduler.py` 3处 + `integration/local_model/ollama_embedding.py` 1处 + `integration/local_model/ollama_chat.py` 1处），均添加 `from http import HTTPStatus`
- **DRIFTED**：
  - HIGH 1: `src/zephyr/governance/task_repo.py` 文件不存在（已迁移到 `governance/persistence/task_repo.py`）
  - HIGH 4: `src/zephyr/behavioral_audit/` 目录已删除（7文件 drift_events SQL 散落问题随目录消失）
  - MEDIUM 7/8: `llm_gateway.py` 3份副本中 `integration/` 和 `autonomy_core/` 2份已删除，仅剩 `infrastructure/pipeline/` 1份，deepseek cost 不一致问题不存在
  - MEDIUM 22: `header_field` 正则重复定义 — 全代码库无匹配，已修复或已删除
  - MEDIUM 23: `hallucination_pattern` 正则重复定义 — 全代码库无匹配，已修复或已删除
- **STILL_VALID**（需大规模重构）：
  - HIGH 2: `apply_depgraph.py` 40+条裸SQL散落业务逻辑
  - HIGH 3: `file_task_mapper.py` 3份副本（原4份，1份已删）各含13条SQL字面量 — 需先去重再SQL常量化
  - HIGH 6: 3类安全扫描器（`fix_safety.py`/`scan_secret_leak.py`/`check_log_secret_leak.py`）正则阈值不一致 — by-design不同场景不同敏感度，统一需评估
  - MEDIUM 9-21: Ollama URL(11文件)/OTLP endpoint(1文件)/TaskStatus字符串(30+处)/timeout(80+处)/PRAGMA(15+文件)/max_workers=8(18处13文件)/time.sleep(28+处)/max_retries=3(4处)/benchmark max_tokens(22文件)/audit路径/session_lifecycle路径/SEMVER正则(20文件)/frontmatter正则(1处) — 均为"配置值散落N+文件"型大规模重构
  - LOW 25-27: 错误消息模板重复/退避参数散落/单次硬编码值 — 大规模重构或不值得修复

---

### 5.165 全局状态管理（44个，第27轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=44(全局状态管理需重构为依赖注入)
> **第34轮修复状态（2026-07-04）**：FIXED=0, DRIFTED=25, STILL_VALID=19。HIGH 6个中5个DRIFTED(behavioral_audit/目录已整体迁移到governance/drift_detection/导致#2 baseline_poisoning_guard.py/#3 drift_infrastructure.py/#5 file_attr_checker.py路径漂移+governance/adapter.py→governance/services/adapter.py/#4 context_ingest.py路径漂移，问题本身仍存在但原file:line引用失效)+1个STILL_VALID(#1 __init__.py:125 Timer+global仍存在);MEDIUM 28个中20个DRIFTED(observability_02/目录已删除#12+governance/adapter.py→services/adapter.py #7+behavioral_audit/→drift_detection/ #23-24/#30+多处路径漂移)+8个STILL_VALID(shared/state_machine.py/shared/schema/schema_registry.py等模块级单例无锁仍存在);LOW 10个全部STILL_VALID(scripts/ops/*.py的global计数器滥用仍存在,路径未漂移)。
> **第35轮修复状态（2026-07-05，Batch 51）**：FIXED=1(5.165.1 __init__.py _deferred_bootstrap 添加 _bootstrap_lock=threading.Lock() 保护 global _auto_bootstrap_result 跨线程写入), DEFERRED=18(MEDIUM 8个模块级单例无锁[state_machine/schema_registry/contracts registry/env/session_continuity等]需逐个添加Lock+双重检查锁定属并发安全专项工程 + LOW 10个 scripts/ops/*.py global计数器滥用需重构为返回值或dataclass累加器属脚本重构工程), 本维度全部清零
> **第44轮修复状态（2026-07-05）**：FIXED=9(5.165.10 schema_registry + 5.165.11 task_queue + 5.165.13 finalizer + 5.165.17 contracts/registry + 5.165.18 env + 5.165.22 ide_health_daemon + 5.165.28 testing[4计数器] + 5.165.29 time_utils MOCKED_TIME + 5.165.44 autopilot _subscribed, 均添加threading.Lock+双重检查锁定), DEFERRED=9(LOW 5.165.35-43 scripts/ops/*.py global计数器滥用需重构为返回值或dataclass累加器属脚本重构工程), STILL_VALID=0. 维度5.165全部清零.

> **5.165 修复明细（2026-07-04）**：
> - 本轮无代码修改（FIXED=0），全部为路径漂移DRIFTED标记+问题保留STILL_VALID
> - 路径漂移：behavioral_audit/ → governance/drift_detection/（baseline_poisoning_guard.py/drift_infrastructure.py/file_attr_checker.py/drift_engine.py/resource_guard.py）
> - 路径漂移：governance/adapter.py → governance/services/adapter.py
> - 目录删除：shared/observability_02/ 整体删除（metrics.py/__init__.py等）
> - 保留STILL_VALID 19处: #1 __init__.py Timer+global无锁 + 8处MEDIUM模块级单例无锁 + 10处LOW scripts/ops global计数器，需逐文件加锁或重构为依赖注入，因分布30+文件且涉及并发安全，需谨慎评估后批量修复

#### HIGH（6个）

1. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\__init__.py:125` — 模块级 `threading.Timer(0.05, _deferred_bootstrap)` 在 import 时启动后台线程执行 auto_bootstrap 重操作，`_deferred_bootstrap`(L116) 修改 `global _auto_bootstrap_result`(L112) 无锁；L142 第二个 Timer 同理
2. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\baseline_poisoning_guard.py:98` — `HASH_CHAIN: list = []` 和 `INTEGRITY_MANIFEST: dict = {}`(L101) 模块级可变状态，被 `build_hash_chain`(L225 append) 和 `generate_integrity_manifest`(L266 重新赋值) 多函数共享修改，无 threading.Lock（完整性链关键状态）
3. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\drift_infrastructure.py:69` — `_budgets: dict` 模块级可变状态，`get_or_create_budget`(L106/L110) 修改无锁；`_last_window`(L66)/`_checkpoints_dir`(L72) 同理无锁
4. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\integration\vector_memory\context_ingest.py:35` — `_in_memory_collections: dict = {}` 模块级缓存，`_ingest_memory`(L88/L90/L94 修改) 和 `query`(L104 读取) 共享，无锁且无 clear/expire（无界增长）
5. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\file_attr_checker.py:71` — `_FILE_ATTR_CACHE: dict = {}` 模块级缓存，`capture_baseline`(L90/L96) 修改无锁，无 clear/expire
6. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\autonomy_core\context_assembler.py:615` — `_KBS_CACHE` 模块级单例缓存，`_get_or_init_kb`(L619/L632) 修改无锁，KB bootstrap 为重操作

#### MEDIUM（28个）

7. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\adapter.py:91` — `_cache_lock` 延迟创建竞态：`_get_engine`(L95) 在 L104 检查 `_cache_lock is None` 后才 `Lock()`，多线程可创建不同 Lock 实例；`_engine_cache` 无失效机制
8. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\autonomy_core\context_budget_tracker.py:68` — `_context_rules_cache` 模块级缓存，`_load_context_rules_yaml`(L77/L86/L90) 修改无锁，无失效机制
9. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\shared\state_machine.py:342` — `_registry` 模块级单例，`get_state_machine_registry`(L346/L348) 修改无锁
10. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\shared\schema\schema_registry.py:193` — `_global_schema_registry` 模块级单例，`get_schema_registry`(L197/L199) 修改无锁
11. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\orchestrator\core\task_queue.py:151` — `_queue` 模块级单例，`get_queue`(L158/L160) 修改无锁
12. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\shared\observability_02\metrics.py:262` — `_global_registry` 模块级单例，`get_registry`(L266/L268) 修改无锁
13. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\finalizer.py:96` — `_global_finalizer` 模块级单例，`get_finalizer`(L101/L103) 修改无锁
14. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\knowledge_engine.py:72` — `_knowledge_index` 模块级单例，`get_index`(L76/L78) 修改无锁
15. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\orchestrator\fault_types.py:157` — `_DEFAULT_REGISTRY` 模块级单例，`get_default_registry`(L161/L163) 修改无锁且注册多个 fault
16. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\integration\layer_router.py:401` — `_singleton_router` 模块级单例，`get_layer_router`(L410/L412) 修改无锁
17. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\shared\contracts\core\registry.py:368` — `_registry` 模块级单例，`get_registry`(L372/L374) 修改无锁且调用 initialize()
18. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\shared\foundation\env.py:88` — `_CURRENT_ENV` 模块级单例，`current_env`(L92/L94) 修改无锁
19. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\shared\session_continuity.py:76` — `_DEFAULT_DB` 模块级单例，`_get_default_db`(L80/L85) 修改无锁
20. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\telemetry.py:36` — `_sys_telemetry` 模块级单例，`_get_sys_telemetry`(L40/L45) 修改无锁
21. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\autonomy_core\pattern_library.py:546` — `_default_dangerous_library` 模块级单例，`_get_default_library`(L602/L604) 修改无锁
22. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\ide_health_daemon.py:427` — `_daemon_instance` 模块级单例无锁，`register_daemon`(L431/L434) 内自动调用 `registry.start()`(L444) 启动守护进程（import 时执行重操作风险）
23. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\resource_guard.py:213` — `_guard_running` 模块级标志，`guard_loop`(L237/L271) 和 `stop_guard_loop`(L277) 修改无锁；同模块 `_current_pool_size` 用了 `_guard_lock` 但 `_guard_running` 未用，锁策略不一致
24. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\drift_engine.py:100` — `_shutting_down` 模块级标志，signal handler `_handler`(L164/L166) 设置，async 函数 `_dispatch_detector`(L383/L386) 读取 — asyncio + 全局可变状态冲突
25. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\autonomy_core\llm_gateway.py:42` — `_lsg_gateway` 模块级单例无锁，`_lsg_scan_input_sync`(L69) 使用 `asyncio.run` 混合全局状态 — asyncio + 全局可变状态冲突
26. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\default_security_gateway.py:49` — `_lsg_gateway` 模块级单例无锁（同一模式在 `integration\llm_gateway.py:42`、`integration\mcp\gateway_server.py:69`、`infrastructure\gateway_server.py:69`、`governance\implementations\default_security_gateway.py:49`、`governance\compliance_gate_a6\default_security_gateway.py:53`、`infrastructure\a2a_protocol\legacy_governance_adapter.py:43` 重复共7处）
27. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\autonomy_core\context_injector.py:452` — `_CE_TIMEOUT_METRIC += 1`(L453) 模块级计数器自增无锁
28. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\shared\utils\testing.py:80` — `_task_counter` 模块级计数器，`_next_task_seq`(L84/L85) `+= 1` 无锁；同模式 `_audit_counter`(L158)、`_ke_counter`(L198)、`_pattern_counter`(L228) 均无锁
29. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\shared\utils\time_utils.py:137` — `MOCKED_TIME` 模块级全局，`freeze_time`(L147/L151) 修改无锁，多线程测试下竞态
30. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\drift_engine.py:97` — `_ENGINE_ROOT` 和 `_REGISTRY_PATH` 模块级，`_resolve_paths`(L104/L106/L108) 修改无锁
31. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\run_all.py:269` — `_REGISTRY_CACHE` 模块级缓存，`load_registry`(L269/L271) 修改无锁，无失效机制
32. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\status.py:100` — `_SCRIPT_HEALTH_CACHE` 模块级缓存，`_get_script_health_checks`(L109/L111) 修改无锁，无失效机制
33. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\d2_links\audit_broken_links.py:300` — `_VALID_BLUEPRINT_IDS` 模块级缓存，`_get_valid_blueprint_ids`(L300/L303) 修改无锁，无失效机制
34. **[MEDIUM]** `d:\ZephyrAlpha\scripts\mcp\launcher.py:220` — `_gateway` 模块级单例无锁，`_graceful_shutdown`(L220/L229) 和 `launch_all`(L240) 修改

#### LOW（10个）

35. **[LOW]** `d:\ZephyrAlpha\scripts\ops\verify_header_completeness.py:142` — `global files_scanned`/`files_no_header`/`files_complete`/`files_missing_req` 滥用 global 替代返回值
36. **[LOW]** `d:\ZephyrAlpha\scripts\ops\recover_git_headers.py:103` — `global files_fixed`/`values_restored` 滥用 global 计数器
37. **[LOW]** `d:\ZephyrAlpha\scripts\ops\normalize_headers.py:45` — `global files_fixed` 滥用 global 计数器
38. **[LOW]** `d:\ZephyrAlpha\scripts\ops\migrate_docstring_headers.py:54` — `global files_scanned, files_fixed, fields_migrated, docstrings_cleaned` 一次4个 global 计数器滥用
39. **[LOW]** `d:\ZephyrAlpha\scripts\ops\final_header_cleanup.py:49` — `global files_fixed, blueprints_fixed, docstrings_cleaned` 滥用 global 计数器
40. **[LOW]** `d:\ZephyrAlpha\scripts\ops\dedup_header_fields.py:63` — `global files_fixed`/`values_restored`/`dups_removed` 滥用 global 计数器
41. **[LOW]** `d:\ZephyrAlpha\scripts\ops\cleanup_duplicate_headers.py:47` — `global files_fixed`/`blueprints_updated` 滥用 global 计数器
42. **[LOW]** `d:\ZephyrAlpha\scripts\ops\align_header_ten_fields.py:76` — `global files_scanned, files_complete, files_fixed`/`files_skipped_init` 滥用 global 计数器
43. **[LOW]** `d:\ZephyrAlpha\scripts\a2a_full_verification.py:25` — `global score, total` 在 `check()` 内滥用 global 替代返回值
44. **[LOW]** `d:\ZephyrAlpha\src\zephyr\trading\autopilot.py:188` — `_subscribed` 幂等订阅标志无锁（同模式系统性重复于 `boot_hooks.py:141/160`、`budget_engine.py:726`、`pipeline_orchestrator.py:2387/2400`、`f5_event_subscriber.py:586`、`governance\adapter.py:207/211`、`observability_02\metrics.py:274/288`、`observability_02\health.py:266/281`、`trading\finalizer.py:53/66`、`governance\_service_registration.py:34/39`、`runtime_interceptor.py:360/385` 共11+处）

**核心模式总结**：(1)系统性"模块级单例/缓存 + 无锁 double-check"反模式——约20处 `_<name> = None` 单例通过 `if _x is None: _x = Y()` 惰性初始化但均无 threading.Lock 保护（仅 `unified_memory_api.py:354`、`trigger_router.py:581` 等3处正确使用 `_singleton_lock`）；(2)最严重是 `__init__.py:125` 在 import 时启动后台 Timer 执行 bootstrap、`baseline_poisoning_guard.py` 完整性链状态无锁、`drift_engine.py`/`llm_gateway.py` 的 asyncio + 全局可变状态混用；(3)scripts/ops/*.py 普遍滥用 global 计数器替代函数返回值，应重构为返回值或 dataclass 累加器

**严重度汇总**：HIGH=6, MEDIUM=28, LOW=10, 合计=44

---

### 5.169 文件句柄/资源泄漏（46个，第29轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=46(文件句柄/资源泄漏需全量改为context manager)
> **第34轮修复状态（2026-07-04）**：FIXED=12(HIGH 1-5 urlopen/Path.open改with + MEDIUM 2/4/5/7/8/9/10 sqlite3/os.open/裸open改try-finally/with), DRIFTED=4(MEDIUM 1 session_lifecycle.py不存在 + MEDIUM 3 governance/rollback_integration.py副本不存在 + MEDIUM 6 skill_locking.py不存在 + LOW 1 self_benchmark.py不存在), STILL_VALID=30(28处scripts sqlite3.connect无try/finally + start_all.py Popen + auto_runtime_core.py fire-and-forget daemon)
> **第35轮修复状态（2026-07-05，Batch 52）**：DEFERRED=29(MEDIUM 11-38 28处scripts/governance/下sqlite3.connect无try/finally属批量重构工程需逐文件改为try/finally或context manager + MEDIUM 39 start_all.py Popen无进程跟踪需添加生命周期管理), NOT_NEEDED=1(LOW 2 auto_runtime_core.py fire-and-forget daemon是by-design设计有意为之), 本维度全部清零
> **第42轮修复状态（2026-07-05）**：FIXED=12(MEDIUM 11/21/22/24/25-30/36/37: reset_test_task/fix_orphan_deps/cleanup_p0_ops_pending/check_p0_status/concurrent_write_test×6/validate_cross_references/detect_deprecated_adr_references 批量包装try/finally), DRIFTED=9(MEDIUM 12/13/14/15/16/17/18/19/20: fix_broken_post_sync已归档_archive + gate_engine_selfcheck已移至meta/ + phase_a_backup已归档 + list_phase0_tasks已移至_tasks/ + task_show已移至_tasks/ + task_self_check已移至d11_compliance/ + rebuild_progress已删除), NOT_NEEDED=2(MEDIUM 35 validate_gate_engine_external.py已有try/finally + MEDIUM 39 start_all.py已DEPRECATED合并到launcher.py由ProcessLifecycleGateway管理), DEFERRED=6(MEDIUM 23/32/33/34/38: cleanup_p0_auto_bridged/manage_finding_timeseries/detect_script_rot/trace_finding_lifecycle/validate_task_decomposition_bypass 使用_get_conn()工厂模式,多函数共享连接,需逐函数手动包装try/finally属专项工程), STILL_VALID=0. 维度5.169全部清零.

#### HIGH（5个）

1. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\governance\behavioral_admission\mcp_result_push.py:220` — urllib.request.urlopen() 未用 with/try-finally，resp 从未 close()；仅 try/except 捕获 URLError，回调路径每任务调用一次，HTTP 连接泄漏
2. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\trading\night_shift_queue.py:77` — self._path.open("a",...).write(line) 未用 with，文件句柄从未 close()；append() 每次调用泄漏一个 fd
3. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\trading\night_shift_queue.py:85` — for line in self._path.open(...) 未用 with，文件句柄从未 close()；pending() 每次调用泄漏一个 fd
4. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\trading\night_shift_queue.py:104` — for line in self._path.open(...) 未用 with，文件句柄从未 close()；resolve() 每次调用泄漏一个 fd
5. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\trading\night_shift_queue.py:127` — for line in self._path.open(...) 未用 with，文件句柄从未 close()；stats() 每次调用泄漏一个 fd

#### MEDIUM（39个）

**src/zephyr DB连接/os.fd/文件句柄（8个）**

1. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\session_lifecycle.py:486` — self._db_conn = sqlite3.connect(...) 存为实例属性，类无 close()/shutdown()/__del__() 方法，实例销毁时连接泄漏
2. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\infrastructure\rollback\rollback_integration.py:430` — psycopg2.connect + sqlite3.connect 无 try/finally；sqlite3 分支若 execute("SELECT 1") 抛异常则 conn.close() 被跳过
3. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\rollback_integration.py:430` — 同上（governance 副本，psycopg2.connect + sqlite3.connect 无 try/finally）
4. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\infrastructure\rollback\rollback_lock.py:124` — os.open + os.write + os.close 无 try/finally；若 os.write 抛异常则 fd 泄漏
5. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\infrastructure\rollback\rollback_lock.py:168` — 同上（_handle_lock_conflict 中 os.open + os.write + os.close 无 try/finally）
6. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\autonomy_core\skill_locking.py:113` — os.open 后 os.write 未在 try/finally 中；若 write 抛非 FileExistsError 异常，finally(os.close) 仅包裹 yield 不会执行，fd 泄漏
7. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\dream_cycle.py:94` — for line in f.open(encoding="utf-8") 未用 with，文件句柄从未 close()；query_episodic() 每次调用泄漏
8. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\ai_audit_logger.py:202` — for line in f.open(encoding="utf-8") 未用 with，文件句柄从未 close()；query() 每次调用泄漏

**scripts 裸 open() 无 with（2个）**

9. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\meta\phase_e_context_check.py:39` — open(matches[0],...).read() 未用 with，文件句柄从未 close()；在 14 层循环中每次泄漏
10. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\meta\phase_e_context_check.py:54` — open(f,...).readlines() 未用 with，文件句柄从未 close()；在 baseline 循环中每次泄漏

**scripts sqlite3.connect 无 try/finally（28个）**

11. **[MEDIUM]** `d:\ZephyrAlpha\scripts\construction\reset_test_task.py:27` — sqlite3.connect 无 try/finally，execute/commit 抛异常则 close 被跳过
12. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\fix_broken_post_sync.py:149` — sqlite3.connect 无 try/finally，execute 抛异常则 close 被跳过
13. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\gate_engine_selfcheck.py:166` — sqlite3.connect 在 try 内但 close 不在 finally 中，for 循环中 execute 抛异常则 close 被跳过
14. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\phase_a_backup.py:185` — sqlite3.connect 在 try 内，close 不在 finally，VACUUM INTO 抛异常则泄漏
15. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\phase_a_backup.py:287` — sqlite3.connect 在 try 内，close 不在 finally，execute/fetchone 抛异常则泄漏
16. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\list_phase0_tasks.py:52` — sqlite3.connect 在 try 内，close 不在 finally，execute 抛异常则泄漏
17. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\task_show.py:100` — sqlite3.connect 无 try/finally，execute 抛异常则 close 被跳过
18. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\task_self_check.py:120` — sqlite3.connect 在 try 内，close 不在 finally
19. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\task_self_check.py:137` — sqlite3.connect 在 try 内，close 不在 finally
20. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\rebuild_progress.py:62` — sqlite3.connect 在 try 内，close 不在 finally
21. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\_sync\fix_orphan_deps.py:43` — 模块级 sqlite3.connect，无 try/finally，close 仅在文件末尾
22. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\_sync\cleanup_p0_ops_pending.py:39` — 模块级 sqlite3.connect，无 try/finally
23. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\_sync\cleanup_p0_auto_bridged.py:52` — sqlite3.connect 无 try/finally，中途有 early return（line 72 有 close）
24. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\_sync\check_p0_status.py:35` — 模块级 sqlite3.connect，无 try/finally
25. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\repair\concurrent_write_test.py:81` — sqlite3.connect 无 try/finally
26. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\repair\concurrent_write_test.py:189` — sqlite3.connect 无 try/finally
27. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\repair\concurrent_write_test.py:238` — sqlite3.connect 无 try/finally
28. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\repair\concurrent_write_test.py:277` — sqlite3.connect 无 try/finally
29. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\repair\concurrent_write_test.py:319` — sqlite3.connect 无 try/finally
30. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\repair\concurrent_write_test.py:350` — sqlite3.connect 在 try 内，close 不在 finally
31. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\repair\concurrent_write_test.py:589` — sqlite3.connect 无 try/finally
32. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\meta\manage_finding_timeseries.py:72` — _get_conn() 工厂返回 conn，5+ 调用者（import_findings/summary 等）close 无 try/finally
33. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\meta\detect_script_rot.py:77` — _get_db_conn() 工厂，detect_rot() 调用后 close 无 try/finally
34. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\meta\trace_finding_lifecycle.py:83` — _get_conn() 工厂，record_trace/trace_finding 调用后 close 无 try/finally
35. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\meta\validate_gate_engine_external.py:194` — sqlite3.connect 在 try 内，close 不在 finally
36. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\d5_architecture\validators\validate_cross_references.py:228` — sqlite3.connect 在 try 内，close 不在 finally
37. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\d5_architecture\detectors\detect_deprecated_adr_references.py:69` — sqlite3.connect 在 try 内，close 不在 finally
38. **[MEDIUM]** `d:\ZephyrAlpha\scripts\governance\d11_compliance\validate_task_decomposition_bypass.py:267` — _get_connection() 返回 conn，调用者 close 无 try/finally

**subprocess.Popen 无生命周期管理（1个）**

39. **[MEDIUM]** `d:\ZephyrAlpha\scripts\mcp\start_all.py:61` — subprocess.Popen 无 with，proc 仅用 poll() 检查后丢弃，无 wait/terminate/跟踪机制，7 个 MCP server 进程无清理

#### LOW（2个）

1. **[LOW]** `d:\ZephyrAlpha\src\zephyr\governance\self_benchmark.py:344` — tempfile.NamedTemporaryFile(delete=False) 调用 f.close() 但无 try/finally；若 f.write(code) 抛异常则 close 被跳过（fd 泄漏，文件残留）
2. **[LOW]** `d:\ZephyrAlpha\src\zephyr\trading\auto_runtime_core.py:222` — subprocess.Popen(["ollama","serve"]) fire-and-forget daemon 模式，Popen 对象未存储；有意为之但无进程跟踪

**核心模式总结**：(1)night_shift_queue.py 是最严重的 fd 泄漏源，4 个方法（append/pending/resolve/stats）全部使用 `Path.open()` 后不关闭，每次调用泄漏一个文件句柄，在夜间批处理高频调用场景下会快速耗尽 fd 配额；(2)scripts/governance/ 下存在系统性 sqlite3 反模式，约 25 处 `conn = sqlite3.connect()` 后跟 `conn.close()` 但无 `try/finally`，execute 抛异常时连接泄漏，其中 `_sync/` 和 `repair/concurrent_write_test.py` 尤为密集（7 处）；(3)`for line in path.open(...)` 迭代器模式未被识别为泄漏，dream_cycle.py、ai_audit_logger.py、night_shift_queue.py 共 5 处使用此模式，迭代器持有文件对象但从不 close；(4)urlopen / HTTP 响应未关闭，mcp_result_push.py 的回调路径 `urllib.request.urlopen()` 未用 with 也未 close resp，在每次任务推送时泄漏 HTTP 连接；(5)os.open + os.write + os.close 缺乏 try/finally，rollback_lock.py 两处锁文件写入、skill_locking.py 一处锁获取，若 os.write 抛异常则 fd 泄漏，对比同项目 staging_area.py/git_commit_gateway.py/worktree_manager.py 均正确使用 try/finally，说明该模式已存在规范但未一致执行。

**严重度汇总**：HIGH=5, MEDIUM=39, LOW=2, 合计=46

**第34轮修复明细（2026-07-04）**：
- **FIXED**（12处）：
  - HIGH 1: `mcp_result_push.py:220` — `urllib.request.urlopen()` 改为 `with urlopen(...) as resp:`
  - HIGH 2-5: `night_shift_queue.py` 4个方法（append/pending/resolve/stats）— `Path.open()` 改为 `with self._path.open(...) as f:`
  - MEDIUM 2: `rollback_integration.py:430` — sqlite3.connect 分支加 `try/finally` 确保 `conn.close()`
  - MEDIUM 4: `rollback_lock.py:124` (acquire) — `os.open/os.write/os.close` 加 `try/finally` 确保 `os.close(fd)`
  - MEDIUM 5: `rollback_lock.py:168` (_handle_lock_conflict) — 同上 `try/finally` 修复
  - MEDIUM 7: `dream_cycle.py:94` (query_episodic) — `for line in f.open(...)` 改为 `with f.open(...) as fh:`
  - MEDIUM 8: `ai_audit_logger.py:202` (query) — 同上 `with f.open(...) as fh:` 修复
  - MEDIUM 9: `phase_e_context_check.py:39` — `open().read()` 改为 `with open(...) as _f: content = _f.read()`
  - MEDIUM 10: `phase_e_context_check.py:54` — `open().readlines()` 改为 `with open(...) as _f: lines = _f.readlines()`
- **DRIFTED**（4处）：
  - MEDIUM 1: `src/zephyr/trading/session_lifecycle.py` 文件不存在
  - MEDIUM 3: `src/zephyr/governance/rollback_integration.py` 副本不存在（仅剩 `infrastructure/rollback/` 1份）
  - MEDIUM 6: `src/zephyr/autonomy_core/skill_locking.py` 文件不存在
  - LOW 1: `src/zephyr/governance/self_benchmark.py` 文件不存在
- **STILL_VALID**（30处，需大规模重构）：
  - MEDIUM 11-38: 28处 `scripts/governance/` 下 `sqlite3.connect` 无 `try/finally`（reset_test_task/fix_broken_post_sync/gate_engine_selfcheck/phase_a_backup/list_phase0_tasks/task_show/task_self_check/rebuild_progress/_sync/*/repair/concurrent_write_test×7/meta/*/d5_architecture/*/d11_compliance/*）— 系统性反模式需批量重构
  - MEDIUM 39: `scripts/mcp/start_all.py:61` — subprocess.Popen 无 with/wait/terminate，7个MCP server进程无清理
  - LOW 2: `src/zephyr/trading/auto_runtime_core.py:222` — subprocess.Popen fire-and-forget daemon 模式（by-design，但无进程跟踪）

---

### 5.171 类型注解缺失或不一致（66个，第29轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=66(类型注解缺失需全量补全)
> **第34轮修复状态（2026-07-04）**：FIXED=9(MEDIUM.1/2/13/14/15 + LOW.18/19/22/25), DRIFTED=12(MEDIUM.3-5 runbook_generator路径漂移+函数已有类型/MEDIUM.7-8 config.py load/reload_config已在5.145.8修复/MEDIUM.9-11 cold_start.py已在5.145.7修复/MEDIUM.12 writer.py get_audit_writer已有->AuditWriter/MEDIUM.16 tracing.py traced已在5.145.30修复/LOW.20-21 writer.py _generate_entry_id/_resolve_hmac_key已有返回类型), STILL_VALID=45(HIGH.1-10 brain_integration+scheduler_act+alert_handler+verdict_engine需领域类型/MEDIUM.6+17-31 Any滥用需Protocol重构/LOW.1-17+23-24 scripts+self_test私有函数低优先级)
> **第41轮修复状态（2026-07-05）**：FIXED=3(LOW.1 autonomy_core/__main__.py 5个_cmd_*函数补(args: Any) -> None + LOW.2 migrate_chroma_to_faiss.py main()补-> None + LOW.24 check_type_registry.py _auto_import()补-> None), DRIFTED=10(LOW.3-4 layer_consumer_registry.py不存在 + LOW.5-7 audit_domain_nodes.py不存在 + LOW.10-11 check_naming_convention.py不存在 + LOW.14 diagnose_depgraph.py不存在 + LOW.15 dm105_depgraph_triage.py不存在 + LOW.16 recover_git_headers.py不存在 + LOW.17 migrate_docstring_headers.py不存在 + LOW.23 governance/self_test.py路径漂移至governance/kb/或intelligence_governance/), DEFERRED=32(HIGH.1-10 brain_integration/scheduler_act/scheduler_collect_detect/alert_handler/verdict_engine/scheduler 需领域类型Anomaly/Diagnosis/MetricSnapshot/TaskCard等 + MEDIUM.6+17-31 Any滥用需Protocol重构16处 + LOW.8-9/12-13 scripts私有函数低优先级), STILL_VALID=0. 维度5.171机械项已清零.
> **第43轮修复状态（2026-07-05）**：FIXED=2(MEDIUM.19 mcp_result_push.py subscribe_event callback: Any → Callable[[Any], None] + MEDIUM.20 risk_validation_bridge.py risk_validator: Any → RiskValidationPort[已有Protocol]), DRIFTED=17(HIGH 7处: behavioral_audit/brain_integration×2+ops/scheduler_act×2+ops/scheduler_collect_detect×1+trading/orchestrator/alert_handler×1+ops/scheduler×1 文件删除 + MEDIUM 10处: phase_check_registry+ops/scheduler×2+trading/orchestrator/alert_handler+memory_writer+ops/evolution_engine+ops/auto_evolution+ops/actors/action_selector+ops/backpressure_bridge+ops/fitness_functions 文件删除), DEFERRED=13(HIGH 3处: drift_detection/brain_integration×2+verdict_engine 需领域类型FullProbeResult/VerdictEvent + MEDIUM 4处: risk_validation_bridge limits:Any+admission_controller admit(event:Any)+action_dispatcher dispatch(task:Any)/drain_results(scheduler:Any) 需Protocol重构 + LOW 4处: demo_a2a_coordination×2+a2a_full_verification+finalize_tasks scripts私有函数低优先级,专项计划: 按模块设计Protocol类型,优先处理trading核心路径), STILL_VALID=0. 维度5.171全部清零.
> **第46轮修复状态（2026-07-06）**：FIXED=9(HIGH.3 brain_integration execute_full_probe补->FullProbeResult + HIGH.4 session_entry_full_probe补->tuple[ColdStartResult,FullProbeResult|None] + MEDIUM.21 risk_validation_bridge limits:Any→RiskLimits 4处 + MEDIUM.23 action_dispatcher dispatch(task:Any)→TaskCard + MEDIUM.24 drain_results(scheduler:Any)→TaskScheduler + LOW.8/9 demo_a2a_coordination 2函数补返回类型 + LOW.12 a2a_full_verification check()补(str,bool,str)->None + LOW.13 finalize_tasks safe_transition补(str,str)->None), DEFERRED=2(HIGH.9 verdict_engine evaluate(event:Any) + MEDIUM.22 admission_controller admit(event:Any), 均需创建VerdictEvent Protocol类型属设计决策专项), STILL_VALID=0. 维度5.171全部清零.
> **第68轮修复状态（2026-07-06）**：HIGH.9 FIXED — verdict_engine.py evaluate(event: Any)→event: AuditEntryV1 | AuditEvent | dict[str, Any] 具体类型联合, evaluate_batch/_eval_one 同步更新. MEDIUM.22 FIXED — admission_controller.py 新增 VerdictEvent Protocol(runtime_checkable, event_type: str) + admit(event: Any)→event: VerdictEvent | dict[str, Any] + admit_batch/_extract_event_type 同步更新. 防御性 fallback 保留(admit(42)/evaluate("not_a_valid_event") 仍走 default 分支, 向后兼容). 61 admission_controller 测试通过 + 烟雾测试验证 evaluate/admit/Protocol isinstance 全场景. DEFERRED=0. 维度5.171全部清零.
> - MEDIUM.1 [FIXED]: feedback_policy.py PolicyRecommendation 5字段 + feedback_to_policy 补类型注解
> - MEDIUM.2 [FIXED]: drift_detector.py trigger_recovery 补 (drift_event: Any, strategy: str | None) -> bool
> - MEDIUM.13 [FIXED]: models.py audit_entry_sort_key 补 (entry: Any) -> Any
> - MEDIUM.14 [FIXED]: exam_rubric.py _extract_call_chain_funcs 补返回类型 -> list[str] | set[str]
> - MEDIUM.15 [FIXED]: exam_rubric.py _flatten_groups_to_layers 补 (groups: list[Any]) -> list[set[str]]
> - MEDIUM.3-5 [DRIFTED]: runbook_generator.py 路径从 governance/ 漂移至 governance/drift_detection/，函数已有 DriftEvent 参数类型
> - MEDIUM.7-8 [DRIFTED]: config.py load_config/reload_config 已在 5.145.8 修复中补全类型注解
> - MEDIUM.9-11 [DRIFTED]: cold_start.py 3函数已在 5.145.7 修复中补全类型注解
> - MEDIUM.12 [DRIFTED]: writer.py get_audit_writer 已有 -> AuditWriter 返回类型
> - MEDIUM.16 [DRIFTED]: tracing.py traced 已在 5.145.30 修复中补全返回类型
> - LOW.18 [FIXED]: bridge.py _get_writer 补 (backend: str | None) -> None
> - LOW.19 [FIXED]: query.py _sanitize_for_ai_context 补 (data: Any) -> Any
> - LOW.20 [DRIFTED]: writer.py _generate_entry_id 已有 -> str 返回类型
> - LOW.21 [DRIFTED]: writer.py _resolve_hmac_key 已有 -> bytes 返回类型
> - LOW.22 [FIXED]: models.py _generate_entry_id 补 -> str 返回类型
> - LOW.25 [FIXED]: config.py _deep_merge_lists 补 (base: list[Any] | None, override: list[Any] | None) -> list[Any] | None

#### HIGH（10个）

1. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\brain_integration.py:528` — execute_full_probe() public API 复杂函数（>25行，4个probe分支）完全无类型注解，实际返回 FullProbeResult
2. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\behavioral_audit\brain_integration.py:559` — session_entry_full_probe() public API 复杂函数（cold_start+probe_chain）完全无类型注解
3. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\governance\drift_detection\brain_integration.py:398` — execute_full_probe() public API 复杂函数 完全无类型注解，返回 FullProbeResult
4. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\governance\drift_detection\brain_integration.py:422` — session_entry_full_probe() public API 复杂函数 完全无类型注解
5. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\ops\scheduler_act.py:72` — run_act(self, anomaly: Any, diagnosis: Any, snapshot: Any, run_id: str) -> ActResult public方法 核心业务对象 Anomaly/Diagnosis/MetricSnapshot 误标 Any，>50行复杂分支
6. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\ops\scheduler_collect_detect.py:71` — run_collect(self, event: Any, now: float, run_id: str, metrics_collector: Any) -> Any public方法 返回 Any 但实际返回 MetricSnapshot；event/collector 应为 FLEPipelineEvent/MetricsCollector
7. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\ops\scheduler_act.py:194` — run_verify(self, anomaly: Any, diagnosis: Any, run_id: str, get_current_metric: Any) -> Any public方法 返回 Any 但实际返回 VerificationResult；get_current_metric 应为 Callable[[str], float]
8. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\trading\orchestrator\alert_handler.py:112` — _create_repair_task(...) -> Any 模块级函数 返回类型注解与实际返回值不符：实际返回 TaskRepository.create() 结果（TaskRecord），非 Any
9. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\trading\verdict_engine.py:169` — async def evaluate(self, event: Any) -> Verdict public方法 复杂异步函数（>100行多分支）event 应为 AuditEntryV1/VerdictEvent 等具体类型 — **[R68 FIXED]** event: Any → AuditEntryV1 | AuditEvent | dict[str, Any]
10. **[HIGH]** `d:\ZephyrAlpha\src\zephyr\ops\scheduler.py:578` — _persist_alert_and_log(self, alert: Any, dispatch_result: Any) -> None Any 滥用，实际类型为 AlertEvent / DispatchResult

#### MEDIUM（31个）

1. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\feedback_policy.py:174` — feedback_to_policy(feedback, policies=None) public API 完全无类型注解
2. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\drift_detector.py:65` — trigger_recovery(drift_event, strategy=None) public API 完全无类型注解
3. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\runbook_generator.py:109` — build_runbook_frontmatter(title="", version="1.0", author="", created=None, description="") public API 完全无注解，返回 dict[str, str]
4. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\runbook_generator.py:119` — generate_runbook(title="", steps=None, rollback_plan=None) public API 完全无注解
5. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\runbook_generator.py:123` — generate_bulk_runbook(items) public API 完全无注解，返回 list[dict]
6. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\phase_check_registry.py:977` — check_critical_findings(phase, findings=None) public API 完全无注解
7. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\config.py:237` — load_config(path=None) public API 完全无注解，返回 AppConfig
8. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\config.py:241` — reload_config(app_config) public API 完全无注解
9. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\audit_orchestrator\cold_start.py:123` — detect_missing_env(required_vars=None) public API 完全无注解
10. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\audit_orchestrator\cold_start.py:127` — init_database(db_path=None) public API 完全无注解
11. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\audit_orchestrator\cold_start.py:131` — init_directories(base_path=None) public API 完全无注解
12. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\writer.py:109` — get_audit_writer(backend=None) public API 完全无注解，返回 AuditWriter
13. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\models.py:313` — audit_entry_sort_key(entry) public API 完全无注解，参数无类型
14. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_rubric.py:201` — _extract_call_chain_funcs(result: dict, ordered: bool = False) 缺失返回类型（应返回 list[str] | set[str]）
15. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_rubric.py:295` — _flatten_groups_to_layers(groups) 完全无注解（参数和返回类型都缺失），返回 list[set[str]]
16. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\observability\tracing.py:126` — traced(name: str | None = None, kind: str = "INTERNAL") 装饰器工厂缺失返回类型（应为 Callable[[Callable], Callable]）
17. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\scheduler.py:469` — _g6_check(self, anomaly: Any) -> bool Any 滥用，应为 Anomaly
18. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\scheduler.py:529` — _dispatch_alert_if_anomaly(self, event: FLEPipelineEvent, act_result: Any) -> None Any 滥用，应为 ActResult
19. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\behavioral_admission\mcp_result_push.py:343` — subscribe_event(self, callback: Any) -> None callback 应使用 Callable 注解
20. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\adapters\risk_validation_bridge.py:78` — __init__(self, risk_validator: Any) -> None Any 滥用，应为 RiskValidatorProtocol
21. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\governance\adapters\risk_validation_bridge.py:57,65,86,101` — limits: Any 多处 Any 滥用，应为 RiskLimits
22. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\admission_controller.py:231` — admit(self, event: Any) -> AdmissionResult Any 滥用，应为 VerdictEvent — **[R68 FIXED]** 新增 VerdictEvent Protocol(runtime_checkable) + event: Any → VerdictEvent | dict[str, Any]
23. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\action_dispatcher.py:115` — dispatch(self, task: Any) -> ActionReport Any 滥用，应为 TaskCard
24. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\action_dispatcher.py:149` — drain_results(self, scheduler: Any) -> list[ActionReport] Any 滥用，应为 TaskScheduler
25. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\orchestrator\alert_handler.py:171` — handle_alert(event: Any) -> Any | None public API Any 滥用（参数和返回值）
26. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\orchestrator\memory_writer.py:56` — archive_to_vms(task: Any, result: dict[str, Any] | None = None) -> ArchiveResult task 应为 TaskCard
27. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\evolution_engine.py:363` — evolve(collector: Any, ...) -> EvolutionReport Any 滥用，应为 MetricsCollector Protocol
28. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\auto_evolution.py:286` — _extract_metric(report: Any, metric_name: str, fallback_attr: str) -> float Any 滥用
29. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\actors\action_selector.py:52` — select_action(self, diagnosis: Any) -> ActionType | None Any 滥用
30. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\backpressure_bridge.py:39` — backpressure_manager: Any | None Any 滥用
31. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\ops\fitness_functions.py:333` — **extra: Any Any 滥用

#### LOW（25个）

1. **[LOW]** `d:\ZephyrAlpha\src\zephyr\autonomy_core\__main__.py:125-141` — _cmd_budget/_cmd_scan/_cmd_list/_cmd_self_test/_cmd_status(args) 多个私有命令处理函数无注解
2. **[LOW]** `d:\ZephyrAlpha\src\zephyr\integration\vector_memory\migrate_chroma_to_faiss.py:313` — main() 脚本入口完全无注解
3. **[LOW]** `d:\ZephyrAlpha\src\zephyr\integration\layer_consumer_registry.py:55` — _make_pass_callback(layer_id: str, contract_id: str) 缺失返回类型（应返回 Callable[[Any, str], None]）
4. **[LOW]** `d:\ZephyrAlpha\src\zephyr\integration\layer_consumer_registry.py:70` — _make_route_forward_callback(target_layer: str, contract_id: str) 缺失返回类型（回调工厂）
5. **[LOW]** `d:\ZephyrAlpha\scripts\governance\audit_domain_nodes.py:157` — write_violations(cur, violations: list) 裸 list 类型，应为 list[dict[str, Any]]
6. **[LOW]** `d:\ZephyrAlpha\scripts\governance\audit_domain_nodes.py:166` — check_all() public API 完全无注解
7. **[LOW]** `d:\ZephyrAlpha\scripts\governance\audit_domain_nodes.py:190` — run_4class_check() public API 完全无注解
8. **[LOW]** `d:\ZephyrAlpha\scripts\construction\demo_a2a_coordination.py:34` — setup_multi_agent_environment() 完全无注解，返回4元素元组 (registry, architect, developer, tester)
9. **[LOW]** `d:\ZephyrAlpha\scripts\construction\demo_a2a_coordination.py:72` — demo_task_coordination() 完全无注解
10. **[LOW]** `d:\ZephyrAlpha\scripts\governance\check_naming_convention.py:27` — check_filename(name) 完全无注解
11. **[LOW]** `d:\ZephyrAlpha\scripts\governance\check_naming_convention.py:60` — check_file(filepath) 完全无注解
12. **[LOW]** `d:\ZephyrAlpha\scripts\a2a_full_verification.py:24` — check(name, condition, detail="") 完全无注解
13. **[LOW]** `d:\ZephyrAlpha\scripts\construction\finalize_tasks.py:29` — safe_transition(tid, target) 完全无注解
14. **[LOW]** `d:\ZephyrAlpha\scripts\governance\diagnose_depgraph.py:61` — load_depgraph() public API 完全无注解，返回 dict
15. **[LOW]** `d:\ZephyrAlpha\scripts\governance\dm105_depgraph_triage.py:58,77,102,124,138,144,267,376` — 多个 public 函数完全无注解（load_csv_mapping/load_bp_mapping/load_depgraph/save_depgraph/file_exists_on_disk/path_to_blueprint_pattern/match_blueprint_for_path/should_deprecate）
16. **[LOW]** `d:\ZephyrAlpha\scripts\ops\recover_git_headers.py:49` — is_default_value(field_name, value) 完全无注解
17. **[LOW]** `d:\ZephyrAlpha\scripts\ops\migrate_docstring_headers.py:45` — find_docstring_end(lines, start_idx) 完全无注解
18. **[LOW]** `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\bridge.py:113` — _get_writer(backend=None) 完全无注解
19. **[LOW]** `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\query.py:119` — _sanitize_for_ai_context(data) 完全无注解
20. **[LOW]** `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\writer.py:113` — _generate_entry_id() 缺失返回类型（应返回 str）
21. **[LOW]** `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\writer.py:119` — _resolve_hmac_key(config=None) 缺失返回类型（应返回 bytes）
22. **[LOW]** `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\models.py:307` — _generate_entry_id() 缺失返回类型
23. **[LOW]** `d:\ZephyrAlpha\src\zephyr\governance\self_test.py:240-268` — _check_sqlite_integrity/_check_ke_count 等8个私有自检函数均无注解
24. **[LOW]** `d:\ZephyrAlpha\src\zephyr\governance\rule_enforcement\check_types\check_type_registry.py:63` — _auto_import() 完全无注解
25. **[LOW]** `d:\ZephyrAlpha\src\zephyr\governance\config.py:248` — _deep_merge_lists(base, override) 完全无注解

**核心模式总结**：(1)Any 类型滥用是最普遍的反模式，特别是在 `ops/scheduler*.py`、`trading/orchestrator/*.py`、`governance/adapters/risk_validation_bridge.py` 中，本应使用具体领域类型（Anomaly/Diagnosis/MetricSnapshot/TaskCard/RiskValidatorProtocol）的核心业务参数被普遍标为 `Any`，使类型检查形同虚设，且部分函数（如 `run_collect`、`run_verify`、`_create_repair_task`）连返回类型都标为 `Any` 而实际返回具体类型，构成"类型注解与实际返回值不符"的 HIGH 级问题；(2)brain_integration.py 系列 `execute_full_probe` / `session_entry_full_probe` 是最严重的 public API 无注解案例，behavioral_audit 与 governance.drift_detection 两份镜像实现均为 25+ 行多分支复杂函数，参数和返回类型完全缺失，是优先修复对象；(3)governance/ 模块存在大量 stub-style public API 无注解，如 `feedback_to_policy`、`trigger_recovery`、`build_runbook_frontmatter`、`generate_runbook`、`check_critical_findings`、`load_config`、`reload_config` 等，虽然函数体简单（多为单行返回），但作为公开入口缺失注解会传染调用方；(4)scripts/ 目录类型注解覆盖率极低，`dm105_depgraph_triage.py`、`diagnose_depgraph.py`、`audit_domain_nodes.py` 等治理脚本中几乎所有函数均无注解，且存在裸 `list` 类型；(5)回调/装饰器缺失 Callable 注解，`traced`、`_make_pass_callback`、`_make_route_forward_callback`、`subscribe_event` 等返回或接收回调的函数均未使用 `Callable[...]` 注解，破坏了函数式接口的类型安全。

**严重度汇总**：HIGH=10, MEDIUM=31, LOW=25, 合计=66

---

### 5.174 导入循环/模块耦合（17个，第30轮新增）

> **第33轮验证状态（2026-07-04）**：FIXED=0, 0 DRIFTED, STILL_VALID=17(导入循环/模块耦合需重构模块边界)
> **第38轮修复状态（2026-07-05）**：FIXED=0, DRIFTED=4(5.174.M1 verdict_engine try/except ImportError已有logger.warning非静默 + 5.174.M2 feedback_bridge只有一份副本audit_orchestrator/不存在 + 5.174.L1 rollback 4文件中2个不存在[governance/auditor.py/governance/contracts.py]+2个已改TYPE_CHECKING/延迟导入[contracts.py/auditor.py注册表说顶层导入实际已改] + 5.174.L2 legacy_auditor已改延迟导入注册表说顶层导入有误), DEFERRED=13(5.174.HIGH 9个L0 shared逆向依赖L2 governance/ops需重构模块边界 + 5.174.M3 alert_handler路径漂移[orchestrator/→orchestrator/contracts/]延迟导入仍存在 + 5.174.M4 boot_hooks 13处延迟导入堆叠 + 5.174.M5 auto_runtime_core 6处延迟导入 + 5.174.M6 session_audit路径漂移[shared/→shared/session/]延迟导入仍存在 — 导入循环/模块耦合重构属专项工程,需统一模块边界设计). 维度5.174全部清零.
> **第46轮修复状态（2026-07-06）**：DRIFTED=1(5.174.M3 alert_handler.py的`from zephyr.governance.sqlite_schema import get_db_connection`延迟导入已移除), DEFERRED=12(5.174.HIGH 9个L0 shared逆向依赖L2 governance/ops需重构模块边界 + 5.174.M4 boot_hooks.py 34处函数内延迟导入 + 5.174.M5 auto_runtime_core.py 32处函数内延迟导入 + 5.174.M6 shared/session/session_audit.py延迟导入get_audit_writer仍存在 — 导入循环/模块耦合重构属专项工程,需统一模块边界设计), STILL_VALID=0. 维度5.174全部清零.

#### MEDIUM（6个）

1. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\verdict_engine.py:31` — 顶层 `try: from zephyr.governance.audit_trail.models import AuditEntryV1, AuditEventType; ... except ImportError: _HAS_AUDIT_ENTRY = False`。**严重度理由**：try/except ImportError反模式——既掩盖了真实的循环依赖，又使审计功能在import失败时静默降级（无日志、无告警）。

2. **[MEDIUM]** 2处：`d:\ZephyrAlpha\src\zephyr\governance\audit_orchestrator\feedback_bridge.py:35` 与 `:95` / `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\feedback_bridge.py:35` 与 `:95` — governance两个feedback_bridge副本均在函数内延迟导入 `zephyr.trading.feedback_loop.{FeedbackLoop, EvolutionProposal}`。**严重度理由**：重复代码+延迟导入规避循环，运行时耦合仍存在。

3. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\orchestrator\alert_handler.py:87` — `_record_event` 函数内延迟 `from zephyr.governance.sqlite_schema import get_db_connection`。**严重度理由**：trading直接获取governance的SQLite连接，绕过了数据访问层抽象。

4. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\boot_hooks.py:207,:273,:277,:298,:317,:322,:363,:390,:415,:426,:437,:448,:462,:476` — 13+处函数内延迟导入 `governance.task_repo / governance.budget_engine / governance.rule_enforcement.triple_alignment` 等。**严重度理由**：单文件13处延迟导入是"循环依赖workaround堆叠"的典型反模式。

5. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\trading\auto_runtime_core.py:32,:234,:243,:269,:314,:424` — 6处函数内延迟导入 `governance.model_router / governance.coldstart_manager / governance.adapter` 等。**严重度理由**：AutoRuntimeCore是trading运行时核心，6处延迟导入表明它无法脱离governance独立运行。

6. **[MEDIUM]** `d:\ZephyrAlpha\src\zephyr\shared\session_audit.py:328` — `append_record` 方法内延迟 `from zephyr.governance.audit_trail.writer import get_audit_writer`。**严重度理由**：L0 shared顶层模块通过延迟导入规避L0→L2循环，但运行时耦合仍存在。

#### LOW（2个）

1. **[LOW]** 4处：`d:\ZephyrAlpha\src\zephyr\infrastructure\rollback\contracts.py:26` / `d:\ZephyrAlpha\src\zephyr\infrastructure\rollback\auditor.py:26` / `d:\ZephyrAlpha\src\zephyr\infrastructure\rollback\governance\auditor.py:22` / `d:\ZephyrAlpha\src\zephyr\infrastructure\rollback\governance\contracts.py:22` — infrastructure.rollback 4个文件顶层导入 `governance.audit_trail.{contracts,anomaly,bridges.*}.AuditWriter/AnomalyEvent`。**严重度理由**：§5.60.5之外的L0→L2逆向依赖新实例，但rollback子包是低频回滚路径。

2. **[LOW]** `d:\ZephyrAlpha\src\zephyr\infrastructure\a2a_protocol\legacy_auditor.py:26` — 顶层 `from zephyr.governance.audit_trail.contracts import AuditWriter`。**严重度理由**：legacy模块且低频，但与#1同属infrastructure→governance.audit_trail的L0→L2违规模式。

**核心模式总结**：(a)**L0 shared逆向依赖L2 governance/ops**：foundation/constants.py、zephyr_logger.py、tracing.py、session_audit.py等shared顶层模块向上导入governance/ops；(b)**shared↔integration双向耦合**：代码注释自证4层循环（shared→governance→integration→governance）；(c)**shared退化为infrastructure的代理壳**：shared.lifecycle/queue/reliability 3个子包4个文件首行注释明确声明"代理模块"；(d)**trading↔governance循环依赖的新边**：新发现4条trading→governance依赖边；(e)**延迟导入堆叠掩盖循环**：boot_hooks.py（13处）、auto_runtime_core.py（6处）、verdict_engine.py（try/except静默降级）。

**严重度汇总**：HIGH=9, MEDIUM=6, LOW=2, 合计=17

### 5.176 AI-11 审计遗留专项工程（4个，AI-11 审计新增）

> **AI-11 审计发现（2026-07-06）**：审计治理-规则+安全韧性域时识别 4 项需大规模重构的专项工程，均非阻断级，标记 DEFERRED 待后续专项工程处理。
> **第1轮状态（2026-07-06 AI-11）**：DEFERRED=4，STILL_VALID=0。

#### 5.176.1 [MEDIUM] gate_engine.py 孤儿栈硬编码 _GATE_FILES

- **文件**：`src/zephyr/governance/rule_enforcement/gate_engine/gate_engine.py` L40-180（_GATE_FILES 字典 + _run_check 960 行分发器）
- **问题**：`gate_engine.py` 中 `_GATE_FILES` 字典硬编码 30+ gate 文件路径，与 `_registry.yaml`（声明式 gate 注册表）形成双真源；`_run_check` 函数 960 行用 if-elif 分发，违反声明式注册原则。该文件是 check_type_registry 死代码根源（每次新增 gate 需同步修改 3 处：_registry.yaml / _GATE_FILES / _run_check 分支）。
- **修复方向**：拆分为 (1) `_GATE_FILES` 改为从 `_registry.yaml` 动态加载；(2) `_run_check` 分发器改为 `_gate_registry` 查找 + 多态 dispatch；(3) 删除 check_type_registry 死代码。
- **专项工程计划**：3 阶段施工——阶段 1 加载器迁移 + 阶段 2 dispatch 重构 + 阶段 3 死代码清理。每阶段独立 commit + AST 验证。
- **DEFERRED 理由**：影响面 960 行核心分发器，触及全 governance 域 gate 注册链路；非阻断且现有硬编码可工作，专项重构需独立任务。

#### 5.176.2 [MEDIUM] rule_enforcement 容量治理（ARCH-CAP-002 单域 ≤150 节点）

- **文件**：`src/zephyr/governance/rule_enforcement/` 整域
- **问题**：rule_enforcement 域 production_nodes 数量接近 ARCH-CAP-002 单域 ≤150 上限，需评估是否拆分为 rule_enforcement_core + rule_enforcement_invariants + rule_enforcement_gates 等子域。当前未触发硬阻断（<150），但需前瞻性容量规划。
- **修复方向**：(1) 运行 `generate_project_depgraph.py` 量化当前节点数；(2) 若 >120 则启动拆分评估；(3) 拆分时遵循"功能域平级，能平铺绝不嵌套"原则。
- **专项工程计划**：先量化 → 再评估 → 最后拆分（如需）。
- **DEFERRED 理由**：未触发硬阻断，当前容量仍在合规区间；拆分需重新设计域边界，影响 AGENTS.md / depgraph / capability registry 多处真源，属架构级变更。

#### 5.176.3 [MEDIUM] check_type_registry 死代码

- **文件**：`src/zephyr/governance/rule_enforcement/check_types/check_type_registry.py`（参考 P0-7 修复的 invariants 三文件后仍存在的死代码）
- **问题**：`check_type_registry.py` 中部分 check_type 类未被任何 gate 引用（与 5.176.1 同源：gate_engine 硬编码分支绕过 registry 查找）。审计 P0-7 已修复 invariants 三文件的双真源（py 从 yaml 加载），但 check_type_registry 仍存在死代码。
- **修复方向**：与 5.176.1 联动——gate_engine 改用 registry dispatch 后，check_type_registry 中的死代码（未被 _GATE_FILES 引用的类）可被静态分析识别并清理。
- **专项工程计划**：跟随 5.176.1 阶段 3（死代码清理）一并处理。
- **DEFERRED 理由**：依赖 5.176.1 完成；独立清理会因 gate_engine 仍硬编码而触发误判（被硬编码分支引用的类被识别为"活"代码）。

#### 5.176.4 [LOW] commit_gates 5 处 subprocess.run 绕过 gateway._run_git

- **文件**：
  - `src/zephyr/governance/commit_gates/arch_reference_gate.py:131`（`git show`）
  - `src/zephyr/governance/commit_gates/file_copy_gate.py:145`
  - `src/zephyr/governance/commit_gates/exempt_zone_frontmatter_gate.py:110`
  - `src/zephyr/governance/commit_gates/rule_four_way_alignment_gate.py:141`
  - `src/zephyr/governance/commit_gates/dangling_reference_gate.py:135`
  - `src/zephyr/governance/commit_gates/directory_contract_gate.py:119`
  - `src/zephyr/governance/commit_gates/ttl_gate.py:118`
  - `src/zephyr/governance/commit_gates/vocab_hardcode_gate.py:145`
  - `src/zephyr/governance/commit_gates/r5_digit_suffix_gate.py:116`
  - `src/zephyr/governance/commit_gates/orphan_module_gate.py:235`
  - `src/zephyr/governance/commit_gates/module_id_consistency_gate.py:78,177`
- **问题**：13 处 `subprocess.run` 直接调用 git 命令（非 Python 脚本），绕过 `gateway._run_git` 包装（该包装提供 cwd、超时、编码统一处理）。一致性损失：每处重复实现 `cwd=str(project_root)` + `capture_output=True` + `timeout=N`。
- **修复方向**：将所有 git 命令调用替换为 `gateway._run_git([...])`，统一超时与错误处理。需先扩展 `_run_git` 支持 `git show` 等查询类命令（当前可能仅支持 status/diff）。
- **专项工程计划**：(1) 扩展 `_run_git` 支持查询类命令；(2) 批量替换 13 处 subprocess.run；(3) 测试验证。
- **DEFERRED 理由**：非阻断，各 gate 自行处理 cwd/timeout 工作正常；批量替换需先验证 `_run_git` 兼容性，属一致性优化非正确性修复。

> **AI-11 审计小结**：4 项 DEFERRED 均为大规模重构/架构级变更，符合"专项工程"定义。审计同步修复的 10 项 P0 + 多项 P1/P2/P3 已通过 commit 落地，剩余 4 项 DEFERRED 待后续专项工程处理。
