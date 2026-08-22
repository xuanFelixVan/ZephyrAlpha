# [BLUEPRINT] MOD-INF-051 | 待统筹登记（10号文 §4 Phase 0/1.1 + 18号清单 §5 波2 E1 裁定 llm_runtime_gateway MVP）
# [MODULE] zephyr.integration.llm_runtime_gateway
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.local_model.deepseek_chat; zephyr.integration.local_model.ollama_chat; zephyr.integration.local_model.lsg_gate; zephyr.shared.foundation.constants; zephyr.shared.io.paths(DB_PATH SSoT); zephyr.shared.io.sqlite_factory(get_db_connection); zephyr.shared.security.secrets(get_required_secret)
# [CONSUMERS] 波5 统筹接线（44号 M3-⑨ MOD-PLAN-007 客户端注入）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 调用必登记（每次 infer 含失败/被拦均落 llm_call_log，append-only 仅 INSERT）; LSG 不过不调用（enforce_input 判决 BLOCK/DENY 或 LSG 异常 -> 不发起任何通道调用）; 降级链留痕（每一通道尝试各落一行）; infer 不承载业务语义（task_type 仅登记/对账维度）; SQL 参数化+常量（NO-BARE-SQL）; db_path 默认 None 走 DB_PATH SSoT（测试注入临时库，prediction_log_writer 同款隔离先例）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知 channel -> ValueError（fail-closed 输入校验）; 通道异常（超时/非200/SecretsError 等）不抛 -> 降级下一通道，全失败返回 InferResult(status=error); LSG 判决/异常 -> 捕获 LSGBlockedError 返回 InferResult(status=blocked) 且不发起调用; 登记落库 sqlite3.Error 透传（审计 fail-closed，同 prediction_log_writer 先例）
# [TESTS] tests/model/test_llm_runtime_gateway.py
# [A_module] module_id=MOD-INF-051 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
llm_runtime_gateway — L2/L3 统一 LLM 推理门面 MVP（10号文 §4 + 18号清单 §5 E1 裁定）
========================================================================================

设计真源：10号文 implementation_plans/10_llm_infrastructure.md §4 Phase 0.2/0.3（登记对账）
+ Phase 1.1（统一入口骨架）+ 18号清单 §2 E1 裁定（MVP 范围封顶：单一 infer 签名 +
调用登记落库 + LSG 注入点 + DeepSeek/Qwen/Ollama 三通道链，testing 封顶；
预算硬门/路由级联属 GP1 不做）。首个真实消费场景 = 44号 M3-⑨（MOD-PLAN-007 客户端注入，波5 接线）。

职责边界（纯网关）
------------------
- infer 不承载业务语义：task_type 只是落库登记/日终对账维度，不参与任何路由决策。
- 不做预算硬门（GP1 范围）；只做登记与对账（reconcile_daily_calls 供 44号 §9.14 防超额口径）。

三通道优先级链
--------------
1. DeepSeekChat（L3 主力，local_model/deepseek_chat.py，已 LSG 注入）
2. QwenChat（备用，本模块内置轻量客户端——OpenAI 兼容端点，读 .env
   QWEN_API_KEY/QWEN_BASE_URL/QWEN_MODEL；查重实证仓内无既有 QwenChat，故随 MVP 单文件收敛，
   GP1 转正时可迁 local_model/ 另行登记）
3. OllamaChat（L2 兜底，local_model/ollama_chat.py，本地零费用）

channel 参数显式指定时只打该通道（不静默降级）；缺省按链降级。
单通道失败（异常/超时/非 200 -> RuntimeError）自动降级下一通道并留痕（每尝试落一行）。
LSG 判决 BLOCK/DENY（入口闸门或客户端自闸门）不降级——同一 prompt 换通道重发无意义
（同 deepseek_chat 对 LSGBlockedError 不重试先例）。

LSG 注入点
----------
infer 入口经波1 产物 local_model/lsg_gate.enforce_input（fail-closed：LSG 不可用/扫描异常
同抛 LSGBlockedError）；成功响应再经 enforce_output 由底层客户端自闸门覆盖
（DeepSeek/Ollama 已注入，QwenChat 本模块同款注入）。判决 BLOCK -> 不发起调用 +
status=blocked 落库。

成本口径（元/百万 token，对账报告 docs/_working/reports/2026-08-22-llm-registry-reconciliation.md §四）
----------------------------------------------------------------------------------------------------------
来源：DeepSeek 官网 2026-08-17 调价（引入峰谷分时：高峰=Asia/Shanghai [9:00,12:00)∪[14:00,18:00)，
其余为空闲时段，空闲价=高峰半价）/ 阿里云百炼 qwen-flash 定价页 2026-07-31；校准登记日 2026-08-22
（tracker #254，Owner 已批准）。缓存未命中口径（缓存命中输入价更低，本网关不区分缓存命中，按未命中
保守计价）；任何不确定情形（如无 tz 信息）按峰时计价，防低估成本。
- deepseek-chat / deepseek-v4-flash（同一模型，别称）：高峰 3.0/9.0；空闲 1.5/4.5。
- deepseek-v4-pro：高峰 9.0/27.0；空闲 4.5/13.5。
- deepseek-reasoner：官方已弃用该名称，底层归 deepseek-v4-flash -> 按 v4-flash 同价。
- qwen-flash（百炼，华北2，输入≤128k 档，无峰谷）：0.15/1.5；真跑实证 llm_call_log 模型名=qwen-flash。
- ollama：本地推理零费用 0.0。
- tokens 为估算值（len/4 上取整）：DeepSeekChat/OllamaChat.ask 只回文本不回 usage，
  真 token 计数待波5 真跑接线时从 API usage 字段回填（DeepSeek/Qwen 响应均含 usage，
  Ollama 含 eval_count）。日终对账以登记值汇总 + reconcile 重算 delta 自检。

落库
----
governance.db 新表 llm_call_log（18号清单 §5，92号 D2 同族授权；DDL 常量即本模块真源，
禁止测试侧复刻副本）。生产表由本工单执行建表；新环境/测试库走
``ensure_llm_call_log_table(db_path)`` 幂等建表（CREATE TABLE IF NOT EXISTS）。

用法
----
    gw = LLMRuntimeGateway()
    r = gw.infer("summary_extraction", "压缩这段文本……")
    if r.status == "ok":
        print(r.text, r.cost_yuan)
    daily = reconcile_daily_calls("2026-08-22")
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Final
from zoneinfo import ZoneInfo

from zephyr.integration.local_model import deepseek_chat as _deepseek_chat
from zephyr.integration.local_model.deepseek_chat import DeepSeekChat
from zephyr.integration.local_model.lsg_gate import (
    LSGBlockedError,
    enforce_input,
    enforce_output,
    resolve_lsg_enabled,
)
from zephyr.integration.local_model.ollama_chat import OllamaChat
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.io.sqlite_factory import get_db_connection
from zephyr.shared.security.secrets import get_required_secret

__all__: Final = [
    "CHANNEL_DEEPSEEK",
    "CHANNEL_OLLAMA",
    "CHANNEL_QWEN",
    "DEFAULT_CHANNEL_CHAIN",
    "InferResult",
    "LLMRuntimeGateway",
    "LLM_CALL_LOG_DDL",
    "QwenChat",
    "compute_cost_yuan",
    "ensure_llm_call_log_table",
    "is_valley_period",
    "reconcile_daily_calls",
]

_log = logging.getLogger(__name__)

# ── 通道常量与降级链 ──
CHANNEL_DEEPSEEK: Final[str] = "deepseek"
CHANNEL_QWEN: Final[str] = "qwen"
CHANNEL_OLLAMA: Final[str] = "ollama"
DEFAULT_CHANNEL_CHAIN: Final[tuple[str, ...]] = (CHANNEL_DEEPSEEK, CHANNEL_QWEN, CHANNEL_OLLAMA)

# ── 峰谷计价（Asia/Shanghai；DeepSeek 官网 2026-08-17 调价口径，2026-08-22 校准登记 tracker #254）──
_BEIJING_TZ: Final = ZoneInfo("Asia/Shanghai")
# 高峰时段=[9:00,12:00)∪[14:00,18:00)，其余为空闲（谷时）；空闲价=高峰半价
_PEAK_AM_START_HOUR: Final[int] = 9  # 上午高峰起点（含）
_PEAK_AM_END_HOUR: Final[int] = 12  # 上午高峰终点（不含）
_PEAK_PM_START_HOUR: Final[int] = 14  # 下午高峰起点（含）
_PEAK_PM_END_HOUR: Final[int] = 18  # 下午高峰终点（不含）

# 内置价表（元/百万 token，缓存未命中口径；缓存命中输入价更低，本网关不区分按未命中保守计价）。
# 真源归属：model_pricing.yaml 为定价真源（对账报告 §2.4）；本表为其运行时镜像 + 峰谷维度补齐。
# 来源：DeepSeek 官网 2026-08-17 调价 / 百炼 qwen-flash 页 2026-07-31；2026-08-22 校准（tracker #254）。
_PRICING_PER_MILLION: Final[dict[str, dict[str, float]]] = {
    "deepseek-chat": {"peak_in": 3.0, "peak_out": 9.0, "valley_in": 1.5, "valley_out": 4.5},
    # deepseek-v4-flash 与 deepseek-chat 为同一模型（别称），同价
    "deepseek-v4-flash": {"peak_in": 3.0, "peak_out": 9.0, "valley_in": 1.5, "valley_out": 4.5},
    # deepseek-reasoner 官方已弃用该名称，底层归 deepseek-v4-flash -> 按 v4-flash 同价
    "deepseek-reasoner": {"peak_in": 3.0, "peak_out": 9.0, "valley_in": 1.5, "valley_out": 4.5},
    "deepseek-v4-pro": {"peak_in": 9.0, "peak_out": 27.0, "valley_in": 4.5, "valley_out": 13.5},
    # qwen-flash（阿里云百炼，华北2，输入≤128k 档）：无峰谷 -> 峰谷同价
    "qwen-flash": {"peak_in": 0.15, "peak_out": 1.5, "valley_in": 0.15, "valley_out": 1.5},
}
# 模型名缺失时按通道兜底（deepseek 默认 deepseek-chat 档；qwen 默认 qwen-flash 档；ollama 本地免费不入表）
_PROVIDER_FALLBACK_PRICE_KEY: Final[dict[str, str]] = {
    CHANNEL_DEEPSEEK: "deepseek-chat",
    CHANNEL_QWEN: "qwen-flash",
}

_QWEN_DEFAULT_BASE_URL: Final[str] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
_QWEN_DEFAULT_MODEL: Final[str] = "qwen-flash"
_QWEN_TIMEOUT_S: Final[float] = 60.0

_ERR_MAX_LEN: Final[int] = 300  # 落库 error 摘要截断长度（防长堆栈入审计载体）
_DATE_RE: Final = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ── DDL-as-Code（18号清单 §5；本模块为 llm_call_log schema 唯一真源）──
LLM_CALL_LOG_DDL: Final = """
CREATE TABLE IF NOT EXISTS llm_call_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,               -- 调用发起时点（ISO8601，Asia/Shanghai；谷峰计价与日终对账基准）
    task_type TEXT NOT NULL,        -- 任务类型登记维度（纯标签，不承载业务语义）
    model TEXT NOT NULL,            -- 实际模型版本（未知/未发起=''）
    provider TEXT NOT NULL,         -- 通道（deepseek/qwen/ollama；入口 LSG 拦截=''）
    tokens_in INTEGER NOT NULL DEFAULT 0,   -- 输入 token（MVP 估算值，波5 改 API usage 回填）
    tokens_out INTEGER NOT NULL DEFAULT 0,  -- 输出 token（同上）
    cost_yuan REAL NOT NULL DEFAULT 0.0,    -- 估算成本（元）
    latency_ms INTEGER NOT NULL DEFAULT 0,  -- 通道耗时（毫秒）
    status TEXT NOT NULL,           -- ok / error / blocked
    error TEXT,                     -- 失败/拦截摘要（NULL=无；截断 300 字）
    created_at TEXT NOT NULL        -- 落库时点 UTC ISO8601
)
"""
_DDL_IDX_TS: Final = (
    "CREATE INDEX IF NOT EXISTS idx_llm_call_log_ts ON llm_call_log (ts)"
)

# ── SQL 常量（NO-BARE-SQL 门禁；append-only 仅 INSERT，参数化防注入）──
_SQL_INSERT: Final = (
    "INSERT INTO llm_call_log "
    "(ts, task_type, model, provider, tokens_in, tokens_out, cost_yuan, latency_ms, status, error, created_at) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
_SQL_ROWS_BY_DATE: Final = (
    "SELECT ts, task_type, model, provider, tokens_in, tokens_out, cost_yuan, latency_ms, status, error "
    "FROM llm_call_log WHERE substr(ts, 1, 10) = ?"
)


@dataclass
class InferResult:
    """infer 统一返回（JSON 可序列化——全基元字段，asdict 即可落 JSON）。"""

    text: str
    model_version: str
    provider: str
    tokens_in: int
    tokens_out: int
    cost_yuan: float
    latency_ms: int
    status: str  # ok / error / blocked
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def is_valley_period(ts: datetime) -> bool:
    """谷时判定（DeepSeek 官网 2026-08-17 口径）：高峰=Asia/Shanghai [9:00,12:00)∪[14:00,18:00)，其余为谷时。

    保守原则：ts 无 tz 信息等不确定情形按峰时计价（返回 False，防低估成本）。
    """
    if ts.tzinfo is None:
        return False
    hour = ts.astimezone(_BEIJING_TZ).hour
    in_peak = (
        _PEAK_AM_START_HOUR <= hour < _PEAK_AM_END_HOUR
        or _PEAK_PM_START_HOUR <= hour < _PEAK_PM_END_HOUR
    )
    return not in_peak


def compute_cost_yuan(
    provider: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
    ts: datetime,
) -> float:
    """按内置价表估算成本（元）。ollama 恒 0（本地免费）；qwen 无峰谷（峰谷同价）；未知模型按通道兜底档。"""
    if provider == CHANNEL_OLLAMA:
        return 0.0
    price = _PRICING_PER_MILLION.get(model)
    if price is None:
        fallback_key = _PROVIDER_FALLBACK_PRICE_KEY.get(provider)
        price = _PRICING_PER_MILLION.get(fallback_key) if fallback_key else None
    if price is None:
        return 0.0
    if is_valley_period(ts):
        in_price, out_price = price["valley_in"], price["valley_out"]
    else:
        in_price, out_price = price["peak_in"], price["peak_out"]
    return round((tokens_in / 1_000_000) * in_price + (tokens_out / 1_000_000) * out_price, 6)


def _estimate_tokens(text: str) -> int:
    """MVP token 估算（len/4 上取整）；真 usage 待波5 真跑从 API 响应回填。"""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def _now_beijing() -> datetime:
    return datetime.now(tz=_BEIJING_TZ)


def ensure_llm_call_log_table(db_path: Path | str | None = None) -> Path:
    """幂等建表（CREATE TABLE IF NOT EXISTS + ts 索引）；返回解析后的库路径。"""
    resolved = Path(db_path) if db_path is not None else DB_PATH
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(resolved)
    try:
        conn.execute(LLM_CALL_LOG_DDL)
        conn.execute(_DDL_IDX_TS)
    finally:
        conn.close()
    return resolved


class QwenChat:
    """Qwen 备用通道轻量客户端——OpenAI 兼容端点（requests 直调，对齐 deepseek_chat 风格）。

    读 .env / 环境变量：QWEN_API_KEY（get_required_secret 对齐既有 secret 机制，
    缺失即 SecretsError -> 网关按通道失败降级）、QWEN_BASE_URL、QWEN_MODEL。
    LSG 自闸门与 DeepSeekChat/OllamaChat 同款（构造点解析开关，咽喉点 enforce）。
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        timeout_s: float = _QWEN_TIMEOUT_S,
        lsg_enabled: bool | None = None,
    ) -> None:
        _deepseek_chat._load_env()  # 复用 local_model 既有 .env 加载器（单一实现，防双源）
        self._model = model or os.getenv("QWEN_MODEL", _QWEN_DEFAULT_MODEL)
        self._api_key = api_key  # None -> 调用时 get_required_secret 解析（fail-fast 对齐既有机制）
        self._base_url = (base_url or os.getenv("QWEN_BASE_URL", _QWEN_DEFAULT_BASE_URL)).rstrip("/")
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout_s
        self._lsg_enabled: bool = resolve_lsg_enabled(lsg_enabled)

    # 显式 __repr__ 排除 _api_key（5.110.2 防泄露同款纪律）
    def __repr__(self) -> str:
        return f"QwenChat(model={self._model!r}, base_url={self._base_url!r})"

    @property
    def model(self) -> str:
        return self._model

    def ask(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """发送聊天请求，返回文本响应。失败抛 RuntimeError（网关按通道失败降级）。"""
        import requests

        api_key = self._api_key or get_required_secret("QWEN_API_KEY")

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # LSG 输入闸门（与 deepseek_chat 同款咽喉点注入）——BLOCK/DENY 抛 LSGBlockedError
        enforce_input(
            "\n".join(m["content"] for m in messages),
            source=f"QwenChat.{self._model}",
            enabled=self._lsg_enabled,
        )

        body: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self._temperature,
            "max_tokens": max_tokens if max_tokens is not None else self._max_tokens,
            "stream": False,
        }
        try:
            resp = requests.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            payload = resp.json()
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(f"Qwen API HTTP error: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Qwen API request failed: {exc}") from exc

        choices = payload.get("choices", [])
        if not choices:
            raise RuntimeError("Qwen API empty choices")
        content = choices[0].get("message", {}).get("content", "") or ""
        # LSG 输出闸门——违规输出抛 LSGBlockedError，不返回调用方
        enforce_output(content, source=f"QwenChat.{self._model}", enabled=self._lsg_enabled)
        return content


class LLMRuntimeGateway:
    """L2/L3 统一推理门面——单一 infer 签名 + 三通道降级链 + 调用登记落库 + LSG 注入点。

    clients 参数支持测试注入假通道（通道名 -> 具 ask/model 的对象）；缺省懒构造真实客户端。
    """

    def __init__(
        self,
        *,
        clients: dict[str, Any] | None = None,
        db_path: Path | str | None = None,
        lsg_enabled: bool | None = None,
        chain: tuple[str, ...] | None = None,
    ) -> None:
        self._clients: dict[str, Any] = dict(clients) if clients else {}
        self._db_path = db_path
        self._lsg_enabled: bool = resolve_lsg_enabled(lsg_enabled)
        self._chain: tuple[str, ...] = tuple(chain) if chain else DEFAULT_CHANNEL_CHAIN
        ensure_llm_call_log_table(self._db_path)

    def _get_client(self, channel: str, model: str | None) -> Any:
        """取通道客户端：注入优先（假通道不解释 model 覆盖）；真实客户端默认缓存复用，model 覆盖时临时构造。"""
        injected = self._clients.get(channel)
        if injected is not None:
            return injected
        client = self._build_client(channel, model)
        if model is None:
            self._clients[channel] = client
        return client

    @staticmethod
    def _build_client(channel: str, model: str | None) -> Any:
        if channel == CHANNEL_DEEPSEEK:
            return DeepSeekChat(model=model or _deepseek_chat.DEFAULT_MODEL)
        if channel == CHANNEL_QWEN:
            return QwenChat(model=model)
        if channel == CHANNEL_OLLAMA:
            return OllamaChat(model=model or os.getenv("OLLAMA_INFERENCE_MODEL", "qwen3:8b"))
        raise ValueError(f"未知通道: {channel}")

    def infer(
        self,
        task_type: str,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        channel: str | None = None,
        **kw: Any,
    ) -> InferResult:
        """统一推理入口（纯网关，不承载业务语义；task_type 仅登记维度）。

        流程：LSG 入口闸门（fail-closed）-> 按链/显式通道尝试 -> 成功即返回；
        单通道失败降级留痕；全失败 status=error；LSG 判决 status=blocked 不降级。
        """
        if channel is not None and channel not in DEFAULT_CHANNEL_CHAIN:
            raise ValueError(f"未知通道: {channel}")
        system = str(kw.get("system", ""))

        # LSG 入口注入点（波1 lsg_gate）：判决 BLOCK/DENY 或 LSG 异常 -> 不发起任何通道调用
        entry_ts = _now_beijing()
        entry_start = time.monotonic()
        try:
            enforce_input(prompt, source=f"llm_runtime_gateway.{task_type}", enabled=self._lsg_enabled)
        except LSGBlockedError as exc:
            result = InferResult(
                text="",
                model_version=model or "",
                provider=channel or "",
                tokens_in=0,
                tokens_out=0,
                cost_yuan=0.0,
                latency_ms=int((time.monotonic() - entry_start) * 1000),
                status="blocked",
                error=str(exc)[:_ERR_MAX_LEN],
            )
            self._record(task_type, result, ts=entry_ts)
            return result

        chain = (channel,) if channel else self._chain
        attempt_errors: list[str] = []
        for ch in chain:
            attempt_ts = _now_beijing()
            start = time.monotonic()
            try:
                client = self._get_client(ch, model)
                text = client.ask(
                    prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except LSGBlockedError as exc:
                # 客户端自闸门判决（输入/输出）——不降级，blocked 落库
                latency_ms = int((time.monotonic() - start) * 1000)
                result = InferResult(
                    text="",
                    model_version=model or "",
                    provider=ch,
                    tokens_in=0,
                    tokens_out=0,
                    cost_yuan=0.0,
                    latency_ms=latency_ms,
                    status="blocked",
                    error=str(exc)[:_ERR_MAX_LEN],
                )
                self._record(task_type, result, ts=attempt_ts)
                return result
            except Exception as exc:  # noqa: BLE001 — 通道失败=预期降级路径（超时/非200/SecretsError 等）
                latency_ms = int((time.monotonic() - start) * 1000)
                summary = f"{type(exc).__name__}: {exc}"[:_ERR_MAX_LEN]
                attempt_errors.append(f"{ch}({summary})")
                self._record(
                    task_type,
                    InferResult(
                        text="",
                        model_version=model or "",
                        provider=ch,
                        tokens_in=0,
                        tokens_out=0,
                        cost_yuan=0.0,
                        latency_ms=latency_ms,
                        status="error",
                        error=summary,
                    ),
                    ts=attempt_ts,
                )
                _log.warning("llm_runtime_gateway 通道 %s 失败，降级下一通道: %s", ch, summary)
                continue
            latency_ms = int((time.monotonic() - start) * 1000)
            resolved_model = getattr(client, "model", None) or model or ""
            tokens_in = _estimate_tokens(system + prompt)
            tokens_out = _estimate_tokens(text)
            result = InferResult(
                text=text,
                model_version=str(resolved_model),
                provider=ch,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_yuan=compute_cost_yuan(ch, str(resolved_model), tokens_in, tokens_out, attempt_ts),
                latency_ms=latency_ms,
                status="ok",
            )
            self._record(task_type, result, ts=attempt_ts)
            return result

        return InferResult(
            text="",
            model_version=model or "",
            provider=channel or "",
            tokens_in=0,
            tokens_out=0,
            cost_yuan=0.0,
            latency_ms=int((time.monotonic() - entry_start) * 1000),
            status="error",
            error=("all channels failed: " + " | ".join(attempt_errors))[:_ERR_MAX_LEN],
        )

    def _record(self, task_type: str, result: InferResult, *, ts: datetime) -> None:
        """落库（append-only 仅 INSERT；sqlite3.Error 透传 fail-closed）。"""
        conn = get_db_connection(self._db_path)
        try:
            conn.execute(
                _SQL_INSERT,
                (
                    ts.isoformat(),
                    task_type,
                    result.model_version,
                    result.provider,
                    result.tokens_in,
                    result.tokens_out,
                    result.cost_yuan,
                    result.latency_ms,
                    result.status,
                    result.error,
                    datetime.now(tz=UTC).isoformat(),
                ),
            )
        finally:
            conn.close()


def reconcile_daily_calls(
    day: str | date,
    *,
    db_path: Path | str | None = None,
    expected_cost_yuan: float | None = None,
) -> dict[str, Any]:
    """日终对账：按 llm_call_log 落库行汇总（调用次数×单价=登记成本），与价表重算对照。

    防超额口径（44号 §9.14 联动）：expected_cost_yuan 给定时输出 over_expected 判定；
    None（MVP 缺省）不判定——预算硬门属 GP1。返回 JSON 可序列化 dict。
    """
    day_str = day.isoformat() if isinstance(day, date) else str(day)
    if not _DATE_RE.match(day_str):
        raise ValueError(f"非法日期格式（期望 YYYY-MM-DD）: {day_str!r}")

    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(_SQL_ROWS_BY_DATE, (day_str,)).fetchall()
    finally:
        conn.close()

    by_status: dict[str, int] = {}
    by_provider: dict[str, dict[str, Any]] = {}
    total_tokens_in = 0
    total_tokens_out = 0
    total_cost = 0.0
    recomputed_cost = 0.0
    for row in rows:
        status = row["status"]
        provider = row["provider"]
        by_status[status] = by_status.get(status, 0) + 1
        bucket = by_provider.setdefault(
            provider, {"calls": 0, "tokens_in": 0, "tokens_out": 0, "cost_yuan": 0.0}
        )
        bucket["calls"] += 1
        bucket["tokens_in"] += row["tokens_in"]
        bucket["tokens_out"] += row["tokens_out"]
        bucket["cost_yuan"] = round(bucket["cost_yuan"] + row["cost_yuan"], 6)
        total_tokens_in += row["tokens_in"]
        total_tokens_out += row["tokens_out"]
        total_cost += row["cost_yuan"]
        if status == "ok":
            try:
                row_ts = datetime.fromisoformat(row["ts"])
            except ValueError:
                continue  # 坏行不重算（登记值仍计入 total_cost，delta 显形）
            recomputed_cost += compute_cost_yuan(
                provider, row["model"], row["tokens_in"], row["tokens_out"], row_ts
            )

    total_cost = round(total_cost, 6)
    recomputed_cost = round(recomputed_cost, 6)
    result: dict[str, Any] = {
        "date": day_str,
        "total_calls": len(rows),
        "by_status": by_status,
        "by_provider": by_provider,
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "total_cost_yuan": total_cost,
        "recomputed_cost_yuan": recomputed_cost,
        "cost_delta_yuan": round(total_cost - recomputed_cost, 6),
        "expected_cost_yuan": expected_cost_yuan,
        "over_expected": (
            None if expected_cost_yuan is None else total_cost > expected_cost_yuan
        ),
    }
    return result
