# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.memory_bank
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""


memory_bank.py — AI 读写结构化持久上下文 (DD: memory_bank, TASK-014 beta c)
==========================================================================
6 个结构化 .md 文件, AI 可读写, 作为跨 session 的持久上下文存储。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: AI 读写请求参数 字符串
#   fields: filename（库文件名）+ heading（章节标题）+ content（写入内容）
#   code: read_file/write_section(filename, heading, content) L68-78
# - id: I2
#   name: 记忆库目录 .md 文件 磁盘文件
#   fields: BANK_FILES 白名单 6 个结构化 markdown（project_brief/product_context/system_patterns/active_context/progress_tracker/decision_log）
#   code: BANK_FILES L33-40
# 层: 算法
# - id: A1
#   name_zh: ① 文件名白名单校验
#   name_en: _validate_filename
#   intro: 只允许读写白名单里的 6 个 .md，其他文件名直接拒绝
#   desc: 补 .md 后缀后比对 BANK_FILES，不在名单内 raise ValueError
#   inputs: I1
#   outputs: 校验通过/ValueError
# - id: A2
#   name_zh: ② 记忆库目录初始化
#   name_en: MemoryBank.__init__
#   intro: 建目录并给缺失的库文件写上标题头
#   desc: mkdir(parents=True, exist_ok=True) + 6 个文件不存在则写入 "# 标题" 首行
#   inputs: I2
#   outputs: 初始化后的记忆库目录
# - id: A3
#   name_zh: ③ 分节追加写入
#   name_en: write_section
#   intro: 在库文件末尾追加带 UTC 时间戳的章节
#   desc: 读旧文 + 拼 "\n## {heading}\n> Updated: {UTC时间}\n{content}" 后整体写回
#   inputs: I1 A1 A2
#   outputs: 追加后的 md 文件
# - id: A4
#   name_zh: ④ 读取与导出
#   name_en: read_file/list_all/export_json
#   intro: 读单个文件全文、列各文件大小、导出全部内容为字典
#   desc: read_file 返回 str；list_all 返回 {库名: 字节数}；export_json 返回 {库名: 全文}
#   inputs: I1 I2 A1
#   outputs: 文件内容/大小字典/全量字典
# 层: 输出
# - id: O1
#   name_zh: 记忆库 md 文件
#   name_en: memory bank md files
#   intro: 落盘持久化的 6 个结构化上下文文件，跨 session 保留
#   downstream: 无下游/内部使用（AI 跨 session 读写，[CONSUMERS] 头为空）
# - id: O2
#   name_zh: 读取结果
#   name_en: read results
#   intro: 返回给调用方 AI 的文件内容字符串或汇总字典
#   downstream: 无下游/内部使用（调用方 AI 自省）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A3
# A2 --> A3
# I1 --> A4
# I2 --> A4
# A1 --> A4
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

from typing import Final
from datetime import UTC, timezone, datetime
from pathlib import Path

UTC: Final[timezone] = UTC

BANK_FILES: Final[list] = [
    "project_brief.md",
    "product_context.md",
    "system_patterns.md",
    "active_context.md",
    "progress_tracker.md",
    "decision_log.md",
]


class MemoryBank:
    """AI 读写 6 类结构化持久上下文 (DD: memory_bank)。

    Using::

        bank = MemoryBank(root_dir=".memory")
        bank.write_section("decision_log", " "Approved: use ONNX int8")
        decisions = bank.read_file("decision_log")
    """

    def __init__(self, root_dir: str | Path = ".ce_memory") -> None:
        self._root = Path(root_dir)
        self._root.mkdir(parents=True, exist_ok=True)
        for fname in BANK_FILES:
            fp = self._root / fname
            if not fp.exists():
                fp.write_text(f"# {fname.replace('.md', '').replace('_', ' ').title()}\n\n", encoding="utf-8")

    @staticmethod
    @staticmethod
    def validate_filename(filename) -> None:
        """公共接口：validate_filename（Stage 4 公共化）。"""
        return __class__._validate_filename(filename)


    def read_file(self, filename: str) -> str:
        self._validate_filename(filename)
        return (self._root / _resolve_filename(filename)).read_text(encoding="utf-8")

    def write_section(self, filename: str, heading: str, content: str) -> None:
        self._validate_filename(filename)
        fp = self._root / _resolve_filename(filename)
        existing = fp.read_text(encoding="utf-8") if fp.exists() else ""
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        entry = f"\n## {heading}\n\n> Updated: {timestamp}\n\n{content}\n"
        fp.write_text(existing + entry, encoding="utf-8")

    def list_all(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for fname in BANK_FILES:
            fp = self._root / fname
            if fp.exists():
                key = fname.replace(".md", "")
                result[key] = fp.stat().st_size
        return result

    def export_json(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for fname in BANK_FILES:
            fp = self._root / fname
            if fp.exists():
                key = fname.replace(".md", "")
                result[key] = fp.read_text(encoding="utf-8")
        return result

    @staticmethod
    def _validate_filename(filename: str) -> None:
        basename = filename if filename.endswith(".md") else f"{filename}.md"
        if basename not in BANK_FILES:
            raise ValueError(f"Invalid bank file. Must be one of {BANK_FILES}")

    @property
    def root_dir(self) -> Path:
        return self._root


def _resolve_filename(filename: str) -> str:
    return filename if filename.endswith(".md") else f"{filename}.md"
