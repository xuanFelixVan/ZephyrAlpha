---
blueprint_id: MOD-FACTORY-001
module_name: knowledge_classifier
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-29
last_updated: 2026-08-29
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_AUTONOMY_CORE
path: src/zephyr/autonomy_core/module_factory/knowledge_classifier.py
granularity: file
---

# MOD-FACTORY-001 knowledge_classifier 蓝图（知识分类器）

> **module_id**: MOD-FACTORY-001 | **域**: D_AUTONOMY_CORE | **优先级**: P1
> **设计真源**: 13号文 `docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/13_module_factory.md` §3.2（知识分类设计）+ §3.1（信息价值四维评分门禁）
> **裁定**: #ARCH-286（归域 D_AUTONOMY_CORE；编号 MOD-FACTORY-001）
> 代码：`src/zephyr/autonomy_core/module_factory/knowledge_classifier.py`

## 0. 定位

模块工厂六环节之"知识分类"（13号文 §3.0 处理 1）：把采集到的知识片段分类到
**已定稿的注册表受控词表**（分类器是"对齐"而非"设计"），产出 v2.0 多维适用性
标注草稿。产出 100% 为建议草稿（human_gated，B-007 成熟度 testing 封顶），
不写任何注册表 YAML。

查重分工：映射裁决归 MOD-FACTORY-002；代码生成归 Phase 2 module_generator；
LLM 通道归 MOD-INF-051 llm_runtime_gateway（本模块只消费其既有 `infer` 签名，
不建新 LLM 通道、不改其源文件）。

## 1. 处理阶梯

`classify(KnowledgeItem) -> ClassificationResult`：

1. 构造受控词表约束 prompt（10 类/6 类/其他分流 + v2.0 十字段 + 既有标签词表）；
2. 经注入网关 `infer("module_factory_classify", ...)` 调用 LLM；
3. JSON 抽取（裸 JSON / markdown 围栏 / 首尾花括号）-> pydantic 严格 schema
   校验（extra=forbid；词表外枚举/交叉字段矛盾一律拒绝）；
4. 信息价值四维评分门禁（§3.1）：相关性/时效性/信息量/可靠性加权平均
   <0.3 -> verdict="rejected"（不进分类）；
5. 标签归并：同义词映射（翻转→反转、破位/跌破→突破、阻力→压力、派发→出货、
   横盘/盘整→震荡、超买超卖→均值回归）-> 词表内保留；词表外新词进
   `tags_pending_registration` 待登记（不静默造词）。

## 2. 接口

```python
FACTOR_CLASSES: tuple[str, ...]        # 10 类（62号文 S2 裁定词表运行时镜像）
STRATEGY_CLASSES: tuple[str, ...]      # 6 类（62号文 S3 裁定词表运行时镜像）
DEFAULT_TAG_VOCAB: frozenset[str]      # v2.0 标签词表（两注册表头部注释并集镜像）
DEFAULT_TAG_SYNONYMS: dict[str, str]   # 同义词归并映射
class KnowledgeClassifierError(Exception)
class LLMInferProtocol(Protocol): .infer(task_type, prompt, ...)  # 对齐 MOD-INF-051
class QualityScores(BaseModel): relevance/timeliness/information/reliability ∈[0,1]
class ClassificationPayload(BaseModel): quality/target_kind/factor_class/strategy_class/
    other_subtype/primary_timeframe/applicable_timeframes/regime_valid/regime_invalid/
    direction/entry_role/applies_to/tags/confidence/rationale（extra=forbid + 交叉字段校验）
@dataclass(frozen=True) QualityGateConfig: threshold=0.3 + 四维权（默认各 0.25）
@dataclass(frozen=True) KnowledgeItem: knowledge_id/title/content/source_ref
@dataclass(frozen=True) ClassificationResult:
    verdict(classified/rejected/error)/classification/quality/quality_score/
    tags_pending_registration/rationale/error/raw_text；human_gate_required 恒 True
class KnowledgeClassifier(llm=None, quality_gate=..., known_tags=None,
                          tag_synonyms=None, max_tokens=2048, temperature=0.1):
    .classify(item) -> ClassificationResult
```

## 3. 不变量

- verdict!="classified" 时 classification 恒为 None（fail-closed 不产半成品）。
- LLM status!=ok / JSON 解析失败 / schema 校验失败 -> verdict="error"，不抛。
- 构造期配置非法（空词表/权重非正/阈值越界）-> KnowledgeClassifierError。
- 词表外 factor_class/strategy_class/枚举值 -> schema 校验拒绝（error）。
- tags 只归并不造词：词表外新词只进 tags_pending_registration。
- 产出 100% human_gated；本模块无任何注册表写路径。

## 4. 依赖

- MOD-INF-051 llm_runtime_gateway（**只消费既有 `infer` 签名**；构造注入，测试 fake）
- pydantic v2（输出 schema 强校验）
- 词表真源：catalogs/factor_registry.yaml + strategy_registry.yaml 头部注释
  （本模块 DEFAULT_TAG_VOCAB/DEFAULT_TAG_SYNONYMS 为其运行时镜像，变更以注册表为准）

## 5. MVP 边界（Phase 1）

- 验收：50 条样本人评一致率 ≥85%（13号文 §4.2 P1-S2，人评环节非本模块职责）。
- 不做：fine-tune 专用分类模型（C1 单 GPU）；多级层次分类树（62号文已用
  条目级多维标注替代）；自动写库（入库走 62号文 candidate 追加 + 人审）。
