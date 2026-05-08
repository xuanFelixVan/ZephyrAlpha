import re
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from zephyr.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)

_LEAK_PROBE_PATTERNS: List[str] = [
    "(?i)(what|show|reveal|tell|display|output|print|repeat|say)(.*?)(system prompt|system message|system instruction)",
    "(?i)(what|show|reveal|tell|display|output|print|repeat|say)(.*?)(你的|系统)(提示|指令|prompt)",
    "(?i)(列出|显示|输出|打印|重复)(.*?)(系统提示|系统指令|你的提示|初始prompt|第一个消息)",
    "(?i)(show me|tell me|give me|reveal|expose)(.*?)(your prompt|your instructions|your rules|your programming)",
    "(?i)(what are|what is|list all|enumerate)(.*?)(your rules?|your guidelines?|your constraints?|your limitations?)",
    "(?i)(ignore|forget|disregard)(.*?)(your instructions|your rules|your prompt|your guidelines)",
    "(?i)(repeat|echo|copy|mirror)(\\s+back\\s+)?(the|your|this)(.*?)(instruction|directive|rule)",
    "(?i)(translate|convert|encode|decode)(.*?)(prompt|instruction|system)",
    "(?i)(you are now|now you are|from now on)(\\s+a\\s+)?(.*?)(role|persona|character)",
    "(?i)(I\\\\s*want\\\\s*you\\\\s*to|I\\\\s*need\\\\s*you\\\\s*to)\\\\s*(stop|forget|ignore|pretend)",
    r"(?i)(?:(?:what|show|tell|give)\s+)?(?:me|us|the\s+user)\s+(?:your|the)\s+(?:original|initial|base|hidden|secret)\s+(?:prompt|instructions?|rules?|system)",
    "(?i)(print|echo|output|return)(\\s+back\\s+)?(exactly\\s+)?(your\\s+)?(exact|original|full|complete)\\s+(words?|text|prompt|instructions?|message)",
    "(?i)(what|which|how)(.*?)(were you|did you get|was your)(.*?)(instructed|told|programmed|configured)",
    "(?i)(say|repeat|echo)\\s+(?:after\\s+me[\\s:]*)(.+?)(?:\\s+verbatim|\\s+exactly|\\s+word for word)?",
    "(?i)(can you|please|I want you to)\\s*(repeat|echo|say)\\s*(the|everything|all|exactly)\\s*((that|which)\\s+I\\s+(just\\s+)?said)?",
    "(?i)(before|above|earlier|previously)(.*?)(you said|you mentioned|you wrote|you were told)",
    "(?i)(in\\s+the\\s+(beginning|start|first message|opening))(.*?)(you said|you were|your)",
    "(?i)(what\\s+(does|do)\\s+your\\s+(system\\s+)?prompt\\s+(say|contain|include|look like))",
    "(?i)(tell\\s+me\\s+everything\\s+you\\s+know\\s+about\\s+(yourself|your\\s+programming|your\\s+system))",
    "(?i)(explain\\s+your\\s+(purpose|function|role|design|architecture|internal))",
    "(?i)(告诉我|显示给我)(.*?)(系统提示|初始prompt|你的规则|你的限制)",
    "(?i)(你的初始|第一个|最初的)(提示|指令|消息|prompt)(.*?)(是什么|是什么内容|是怎样的)",
    "(?i)(忽略|忘记|无视)(.*?)(之前的|先前的|上面的|前面)(.*?)(指令|提示|规则|要求|对话)",
    "(?i)(从现在开始|现在开始|从现在起)(.*?)(你(是|变成了|成为了|扮演))",
    "(?i)(角色扮演|角色设定|身份设定)(.*?)(你(是|现在是|变成了))",
    "(?i)(请(你|您)?)(说出|回复|输出|显示|打印)(.*?)(我(刚刚|刚才|前面|之前)?(说的|提到的|写的|输入的))",
    "(?i)(把|将)(.*?)(翻译|编码|加密|转换|改写)(.*?)(并|然后|之后)(.*?)(执行|输出|回复|显示)",
    "(?i)(作为|充当|扮演|模拟)\\s*(一个?|某个)(?:无限制|无约束|不受限|自由|开放)",
    "(?i)(解锁|开启|激活|启用)\\s*(?:(?:所有|全部)\\s*)?(?:功能|能力|模式|权限)",
    "(?i)(允许|同意|遵守|服从|遵守)\\s*(?:我|用户)(?:的|所有|任何)\\s*(?:指令|命令|要求|请求)",
    "(?i)(所有|任何|一切)\\s*(?:限制|约束|规则|边界|过滤器)\\s*(?:被|已|已经)\\s*(?:移除|取消|解除|删除)",
    "(?i)(not\\s+to\\s+follow|don't\\s+follow|stop\\s+following|break)\\s+(the|your|those)\\s+(rules|guidelines|instructions|restrictions|limitations)",
    "(?i)(delete|remove|erase|clear|wipe|reset)\\s+(your|the|my|this)\\s+(memory|history|context|conversation|chat)",
    "(?i)(start|begin|initiate)\\s+(a\\s+)?(new|fresh|blank|clean)\\s+(session|conversation|chat|context)",
    "(?i)(you\\s+must|you\\s+have\\s+to|you\\s+need\\s+to|you\\s+should)\\s+(obey|follow|comply|respond|answer|do)",
    "(?i)(don't\\s+say|do\\s+not\\s+say|do\\s+not\\s+mention|never\\s+say|stop\\s+saying)\\s+(sorry|I\\s+cannot|I'm\\s+unable|as\\s+an\\s+AI)",
    "(?i)(do\\s+not\\s+apologize|no\\s+apologies|don't\\s+apologize|never\\s+say\\s+sorry)",
    "(?i)(without\\s+(any|giving|providing|offering|showing)\\s*)?(warning|disclaimer|explanation|caveat|disclosure)",
    "(?i)(just|only|simply|just)\\s+(answer|respond|say|give|provide|output)\\s+(the|with|a)\\s+(direct|straight|simple|plain|raw)",
    "(?i)(remember\\s+this|note\\s+this|keep\\s+this\\s+in\\s+mind|this\\s+is\\s+important|this\\s+is\\s+critical)",
    "(?i)(for\\s+future\\s+reference|for\\s+later|from\\s+now\\s+on|going\\s+forward|henceforth|hereafter)",
    "(?i)(you\\s+are|this\\s+is)\\s+(no\\s+longer)\\s+.*?(ai|assistant|language model|bot|chat)",
    "(?i)(jailbreak|prompt\\s*leak|prompt\\s*injection|prompt\\s*hack|prompt\\s*extract|prompt\\s*exfil)",
    "(?i)(我是(你的)?)(开发(者|人员)|创建(者|人员)|主人|拥有者|管理员|老板)",
    "(?i)(debug|debugging|development|testing)\\s*mode",
    "(?i)(maintenance|admin|superuser|root|god)\\s*mode",
    "(?i)(紧急|重要|关键|必须|强制)\\s*(指令|命令|通知|更新|升级)",
    "(?i)(安全|系统|管理)\\s*(漏洞|更新|维护|升级|补丁)",
    "(?i)(base64|hex|unicode|rot13|morse|binary|ascii)\\s*(encode|decode|convert|translate)",
    "(?i)(repeat|show|display|reveal|output|print)\\s+(your|the|my|this|initial|original|first|starting)\\s*(instruction|prompt|directive|message|system|configuration|setup)s?\\s*(verbatim|exactly|word\\s*for\\s*word|as\\s*is)?",
    "(?i)(what\\s+(are|is|were|was)\\s+(your|the)\\s*(system|initial|original|first|starting|base)\\s*(instruction|prompt|directive|message|configuration|setup)s?)",
]

_TOPIC_BOUNDARIES: Dict[str, List[str]] = {
    "assistance": ["help", "assist", "guide", "explain", "teach", "咨询", "帮助", "指导", "解释"],
    "analysis": ["analyze", "evaluate", "review", "compare", "分析", "评估", "比较"],
    "code": ["code", "program", "debug", "script", "function", "代码", "编程", "函数"],
    "content_creation": ["write", "compose", "draft", "create", "summarize", "写作", "撰写", "创作"],
    "translation": ["translate", "convert", "localize", "翻译", "转换"],
    "finance": ["trade", "investment", "portfolio", "risk", "market", "交易", "投资", "风险", "市场"],
}

TOPIC_ALLOWED_WORDS: Set[str] = set()
for _words in _TOPIC_BOUNDARIES.values():
    TOPIC_ALLOWED_WORDS.update(w.lower() for w in _words)
TOPIC_DISALLOWED_WORDS: Set[str] = {
    "hack", "exploit", "malware", "phishing", "bomb", "weapon",
    "terror", "assassination", "torture", "ransom", "illegal",
    "黑产", "黑客攻击", "窃取", "入侵",
}

PRECOMPILED_LEAK: List[re.Pattern] = [re.compile(p, re.DOTALL) for p in _LEAK_PROBE_PATTERNS]


class PromptTemplate(BaseModel):
    template_id: str
    system_prompt: str
    model_name: str = ""
    version: str = "1.0.0"


class LeakScanResult(BaseModel):
    is_safe: bool = True
    leak_hits: List[Dict[str, Any]] = Field(default_factory=list)
    probing_hits: List[Dict[str, Any]] = Field(default_factory=list)
    topic_violations: List[str] = Field(default_factory=list)


class PromptProtectionLayer(LLMSecurityProtocol):
    """L2 Prompt保护层 —— 四段式模板 / 防泄露 / 话题边界控制"""

    def __init__(self):
        pass

    def layer_name(self) -> str:
        return "l2_prompt_protection"

    def layer_index(self) -> int:
        return 2

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        user_input = ctx.raw_input
        scan = self.scan_for_leak(user_input)
        probing = self.detect_prompt_probing(user_input)
        topic = self.check_topic_boundary(user_input)

        blocked = not scan.is_safe or len(probing) > 0 or len(topic) > 0

        if blocked:
            reason_parts = []
            if not scan.is_safe:
                reason_parts.append(f"leak_hits={len(scan.leak_hits)}")
            if len(probing) > 0:
                reason_parts.append(f"probing_hits={len(probing)}")
            if len(topic) > 0:
                reason_parts.append("topic_violation")
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason=" | ".join(reason_parts),
                layer_name=self.layer_name(),
                score=0.0,
            )

        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="L2 passed",
            layer_name=self.layer_name(),
            score=0.95,
        )

    def build_safe_prompt(
        self,
        system: str,
        history: str = "",
        external_data: str = "",
        user_input: str = "",
    ) -> str:
        parts = [
            "<!-- BEGIN SYSTEM -->",
            system.strip(),
            "<!-- END SYSTEM -->",
        ]
        if history:
            parts.extend([
                "",
                "<!-- BEGIN HISTORY -->",
                history.strip(),
                "<!-- END HISTORY -->",
            ])
        if external_data:
            parts.extend([
                "",
                "<!-- BEGIN EXTERNAL_DATA -->",
                external_data.strip(),
                "<!-- END EXTERNAL_DATA -->",
            ])
        if user_input:
            parts.extend([
                "",
                "<!-- BEGIN USER_INPUT -->",
                user_input.strip(),
                "<!-- END USER_INPUT -->",
            ])
        return "\n".join(parts)

    def scan_for_leak(self, content: str) -> LeakScanResult:
        leak_hits = []
        for pattern in PRECOMPILED_LEAK:
            for match in pattern.finditer(content):
                leak_hits.append({
                    "pattern": pattern.pattern[:100],
                    "match": match.group()[:200],
                })

        is_safe = len(leak_hits) == 0
        result = LeakScanResult(leak_hits=leak_hits)

        if not is_safe:
            result.is_safe = False

        probing = self.detect_prompt_probing(content)
        result.probing_hits = probing

        topic_violations = self.check_topic_boundary(content)
        result.topic_violations = topic_violations

        return result

    def detect_prompt_probing(self, content: str) -> List[Dict[str, Any]]:
        hits = []
        probing_variants = [
            r"(?i)(what|show|reveal|tell|display)\s*(me|us)\s*your\s*(system\s*)?prompt",
            r"(?i)(tell|show|give)\s*me\s*(the|your)\s*instructions?",
            r"(?i)(repeat|echo)\s*(after\s*me|this\s*back)",
            r"(?i)(you\s*are\s*now)\s*.*?(mode|role|persona)",
            r"(?i)(ignore|forget|disregard)\s*(all|previous|your)",
            r"(?i)(你的|系统)(提示|指令|prompt)(是什么|是什么内容)",
            r"(?i)(repeat|show|display|reveal|output|print)\s+(your|the|my|this)?\s*(initial|original|first|starting|system|base)?\s*(instruction|prompt|directive|message|configuration|setup)s?\s*(verbatim|exactly|word\s*for\s*word|as\s*is)?",
            r"(?i)(what\s+(are|is|were|was)\s+(your|the)\s*(system|initial|original|first|starting|base)?\s*(instruction|prompt|directive|message|configuration|setup)s?)",
        ]
        for variant in probing_variants:
            compiled = re.compile(variant)
            for m in compiled.finditer(content):
                hits.append({"pattern": variant[:80], "match": m.group()[:120]})
        return hits

    def check_topic_boundary(self, content: str) -> List[str]:
        violations = []
        content_lower = content.lower()

        is_in_bounds = False
        for domain, keywords in _TOPIC_BOUNDARIES.items():
            if any(kw.lower() in content_lower for kw in keywords):
                is_in_bounds = True
                break

        if not is_in_bounds:
            return []

        for word in TOPIC_DISALLOWED_WORDS:
            if word.lower() in content_lower:
                violations.append(f"disallowed_topic: {word}")

        return violations
