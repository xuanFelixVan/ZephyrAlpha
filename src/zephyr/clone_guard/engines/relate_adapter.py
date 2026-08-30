# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.relate_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); zephyr.clone_guard.engines.echo_guard_adapter (Finding); datasketch (MinHash, MinHashLSH); re; fnmatch; keyword; logging; pathlib
# [CONSUMERS] zephyr.clone_guard.orchestrator; zephyr.clone_guard.mcp_server
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 datasketch MinHash LSH 进程内调用，统一 detect() 接口；datasketch 未装/语料空返回空 + degraded；severity 仅 review/acknowledged（预筛器不直接 extract）；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect()/search() 永不抛异常——datasketch 未装/异常返回 ([], degraded=True)
# [TESTS] tests/clone_guard/test_relate_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
RelateAdapter — relate 快速预筛适配器（Phase C L2/L3 加速器，Path B: datasketch MinHash LSH）。

封装 datasketch 的 MinHash + LSH（局部敏感哈希）进程内调用，对编排层暴露统一
detect() 接口 + search() 方法（L0 按语义搜已有函数）。

**Path B 裁定**（见 clone-guard-engine-verification-ruling.md §2.1 / §3.1-P1）：真实
relate 是 Zig 二进制（The-Billy-Company/relate，Apache-2.0），无预编译资产，源码编译
需 Zig 0.16.0 + 三 repo 耦合（Path A 不可行）。Path B 采用 datasketch（MIT，纯 Python，
依赖 numpy 已在项目中）实现等价的 MinHash LSH 近重查询——用成熟库而非自研算法（守
"不自研"原则）。datasketch 未装时降级返回空（守 blueprint §5.2）。

核心算法（标准 MinHash LSH，非自研）：
  1. 文本归一化：去文档串 + 注释 + 字符串字面量 → 分词 → 标识符归一化（ID/N）
  2. k-gram shingling：归一化 token 序列按 k=``relate_shingle_size`` 滑窗生成 shingle 集合
  3. MinHash 签名：num_perm=``relate_num_perm`` 个排列哈希 → 固定长度签名
  4. LSH 候选查询：签名分带哈希到桶 → 近重候选集（亚线性查询）
  5. 相似度 = MinHash 签名 Jaccard 估计

**标识符归一化**（Type-2 克隆检测关键）：将非关键字标识符统一替换为 ``ID``、数字替换为
``N``，使变量重命名的 Type-2 克隆产生相同 token 序列，显著提高 Jaccard 召回。

与 reDUP/echo-guard 互补——relate 是预筛器（轻量、无模型），reDUP/echo-guard 是精检器。
relate 不直接判 extract（预筛结果保守，仅 review/acknowledged），由精检器决定升级。

降级策略（守 blueprint §5.2）：
  - datasketch 未安装 → degraded=True, 返回空列表
  - relate_enabled=False → degraded=True, 返回空列表
  - 语料为空（无可索引文件）→ 返回空（degraded=False，无匹配非故障）
  - 异常 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表（severity 仅 review/acknowledged）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: relate_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: relate_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RelateAdapter
#   name_en: RelateAdapter
#   intro: relate 快速预筛适配器（Phase C L2/L3 加速器，Path B: datasketch MinHash…
#   desc: relate 快速预筛适配器（Phase C L2/L3 加速器，Path B: datasketch MinHash LSH）。 封装 datasketch MinHash L…；公共方法（定义序）: health_…
#   inputs: repo_root config
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: RelateAdapter
#   downstream: zephyr.clone_guard.orchestrator; zephyr.clone_guard.mcp_server
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import fnmatch
import keyword
import logging
import re
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__ = ["RelateAdapter"]

# 保留的关键词集合（Python keywords + 常见隐式名称）——其余标识符归一化为 ID
# 使 Type-2 克隆（变量重命名）产生相同 token 序列，提高 Jaccard 召回
_KEYWORDS: frozenset[str] = frozenset(keyword.kwlist) | frozenset({"self", "cls", "True", "False", "None"})

# datasketch 延迟导入——未装时降级（守 §5.2）；避免模块导入期硬依赖
_DATASKETCH_AVAILABLE: bool | None = None


def _check_datasketch() -> bool:
    """检查 datasketch 是否可导入（结果缓存）。"""
    global _DATASKETCH_AVAILABLE
    if _DATASKETCH_AVAILABLE is None:
        try:
            import datasketch  # noqa: F401  可导入性检查

            _DATASKETCH_AVAILABLE = True
            logger.debug("datasketch %s 可用——relate Path B 全功能", getattr(datasketch, "__version__", "?"))
        except ImportError:
            _DATASKETCH_AVAILABLE = False
            logger.debug("datasketch 未安装——relate Path B 降级为空")
    return _DATASKETCH_AVAILABLE


class RelateAdapter:
    """relate 快速预筛适配器（Phase C L2/L3 加速器，Path B: datasketch MinHash LSH）。

    封装 datasketch MinHash LSH 进程内调用，对编排层暴露统一 detect() 接口 +
    search() 方法。severity 仅 review/acknowledged（预筛器不直接 extract）。

    索引策略：进程内惰性构建——首次 detect()/search() 时扫描仓库 .py 文件（排除
    ignore_paths）构建 MinHash LSH 索引；亦可通过 index() 显式注入语料（测试/L2 阶段1）。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or CloneGuardConfig()
        # 进程内索引（惰性构建）
        self._lsh = None  # MinHashLSH 实例
        self._sketches: dict[str, object] = {}  # {relative_path: MinHash}
        self._indexed: bool = False

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """检查 relate 是否可用（datasketch 可导入即 True——索引按需构建）。"""
        return _check_datasketch()

    def index(self, files: list[str]) -> int:
        """显式构建 MinHash LSH 索引（L2 审计阶段1 / 测试注入语料）。

        Args:
            files: 语料文件路径列表（相对或绝对路径）。

        Returns:
            成功索引的文件数（跳过空文件/读取失败/重复键）。
        """
        if not _check_datasketch():
            logger.debug("RelateAdapter.index: datasketch 未安装，跳过")
            return 0

        from datasketch import MinHash, MinHashLSH

        self._lsh = MinHashLSH(
            threshold=self._config.relate_threshold,
            num_perm=self._config.relate_num_perm,
        )
        self._sketches = {}
        count = 0
        for f in files:
            content = self._read_file(f)
            if content is None:
                continue
            shingles = self._normalize_and_shingle(content)
            if not shingles:
                continue
            mh = self._make_minhash(shingles, MinHash)
            key = self._to_relative_path(f)
            try:
                self._lsh.insert(key, mh)
            except ValueError:
                continue  # 重复键——跳过（同一路径二次索引）
            self._sketches[key] = mh
            count += 1
        self._indexed = True
        logger.debug("RelateAdapter.index: 索引 %d 文件（共 %d 输入）", count, len(files))
        return count

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件与已索引语料的快速预筛候选（L2/L3 加速场景）。

        Args:
            files: 待检测文件路径列表（相对路径）。
            timeout: 超时秒数（进程内计算为建议值，非硬中断——L2/L3 非热路径）。

        Returns:
            (findings, degraded) 元组：degraded=True 表示不可用/异常。
        """
        if not files:
            return [], False

        if not self._config.relate_enabled:
            logger.debug("relate 已在配置中禁用，跳过检测")
            return [], True

        if not _check_datasketch():
            logger.debug("RelateAdapter.detect: datasketch 未安装，降级")
            return [], True

        from datasketch import MinHash

        # 惰性构建语料索引（排除本次输入文件，避免自匹配）
        if not self._indexed:
            self._build_corpus_index(exclude=set(self._to_relative_path(f) for f in files))

        if not self._sketches:
            return [], False  # 语料为空——无匹配（非故障，degraded=False）

        findings: list[Finding] = []
        for f in files:
            content = self._read_file(f)
            if content is None:
                continue
            shingles = self._normalize_and_shingle(content)
            if not shingles:
                continue
            mh = self._make_minhash(shingles, MinHash)
            source = self._to_relative_path(f)
            candidates = self._lsh.query(mh)
            for cand_key in candidates:
                if cand_key == source:
                    continue  # 跳过自匹配
                cand_mh = self._sketches.get(cand_key)
                if cand_mh is None:
                    continue
                sim = mh.jaccard(cand_mh)
                if sim < self._config.relate_threshold:
                    continue  # LSH 候选但实际相似度低于阈值
                findings.append(self._make_finding(source, cand_key, sim, len(findings)))

        return findings, False

    def search(self, query: str, top_k: int | None = None) -> list[Finding]:
        """L0 按语义搜已有函数（MCP search_functions 工具复用）。

        Args:
            query: 搜索查询（函数签名/片段/代码文本）。
            top_k: 返回 top-k 结果（None 时用 config.relate_top_k）。

        Returns:
            Finding 列表（severity 均为 acknowledged，预筛结果不阻断）。
        """
        if not self._config.relate_enabled:
            return []
        if not _check_datasketch():
            logger.debug("RelateAdapter.search: datasketch 未安装，返回空")
            return []
        if not query or not query.strip():
            return []

        from datasketch import MinHash

        if not self._indexed:
            self._build_corpus_index()

        if not self._sketches:
            return []

        shingles = self._normalize_and_shingle(query)
        if not shingles:
            return []

        mh = self._make_minhash(shingles, MinHash)

        # search 是非对称查询（短 query vs 长文件）——LSH 阈值过高会漏召回。
        # 改用暴力 MinHash Jaccard 遍历全部语料签名，按相似度降序取 top-k。
        scored: list[tuple[float, str]] = []
        for cand_key, cand_mh in self._sketches.items():
            sim = mh.jaccard(cand_mh)
            if sim > 0.0:
                scored.append((sim, cand_key))
        scored.sort(reverse=True)

        k = top_k or self._config.relate_top_k
        results: list[Finding] = []
        for sim, cand_key in scored[:k]:
            results.append(self._make_finding("<query>", cand_key, sim, len(results), force_acknowledged=True))
        return results

    # ------------------------------------------------------------------
    # 内部：归一化 + MinHash + 索引构建
    # ------------------------------------------------------------------

    def _normalize_and_shingle(self, text: str) -> set[str]:
        """归一化文本并生成 k-gram shingle 集合。

        归一化（使 Type-2 克隆可检测）：
          1. 去除三引号文档串 + 字符串字面量 + 全行注释 + 空行
          2. 分词 → 标识符归一化（非关键字→ID，数字→N，保留关键字/运算符）
          3. k-gram shingling（token 不足 k 时整体作为一个 shingle）

        标识符归一化使变量重命名的 Type-2 克隆产生相同 token 序列，显著提高 Jaccard 召回。
        """
        # 去除三引号文档串
        text = re.sub(r'"""[\s\S]*?"""', "", text)
        text = re.sub(r"'''[\s\S]*?'''", "", text)
        # 去除字符串字面量（单/双引号）——字面量值变化不影响代码结构
        text = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', "S", text)
        text = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", "S", text)
        # 去除全行注释 + 空行
        lines: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            lines.append(stripped)
        code = "\n".join(lines)

        # 分词（\w+ 词 + [^\w\s] 运算符/标点）+ 标识符归一化
        raw_tokens = re.findall(r"\w+|[^\w\s]", code)
        tokens: list[str] = []
        for t in raw_tokens:
            if t in _KEYWORDS:
                tokens.append(t)
            elif t[0].isalpha() or t[0] == "_":
                tokens.append("ID")
            elif t[0].isdigit():
                tokens.append("N")
            else:
                tokens.append(t)  # 运算符/标点

        if not tokens:
            return set()

        k = self._config.relate_shingle_size
        if len(tokens) < k:
            return {" ".join(tokens)}  # token 不足 k——整体作为一个 shingle

        return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}

    def _make_minhash(self, shingles: set[str], minhash_cls) -> object:
        """从 shingle 集合构造 MinHash 签名。"""
        mh = minhash_cls(num_perm=self._config.relate_num_perm)
        for s in shingles:
            mh.update(s.encode("utf-8"))
        return mh

    def _build_corpus_index(self, exclude: set[str] | None = None) -> int:
        """扫描仓库 .py 文件构建语料索引（排除 ignore_paths + exclude 集合）。

        Args:
            exclude: 需排除的相对路径集合（如本次 detect 的输入文件，避免自匹配）。

        Returns:
            成功索引的文件数。
        """
        exclude = exclude or set()
        files: list[str] = []
        for p in self._repo_root.rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            rel = self._to_relative_path(str(p))
            if rel in exclude:
                continue
            # 排除忽略路径——与 orchestrator._filter_files 一致（目录前缀 startsWith，其余 fnmatch）
            if any(
                rel.startswith(pat) if pat.endswith("/") else fnmatch.fnmatch(rel, pat)
                for pat in self._config.ignore_paths
            ):
                continue
            files.append(str(p))
        return self.index(files)

    def _read_file(self, file_path: str) -> str | None:
        """读取文件内容（UTF-8，失败返回 None）。"""
        try:
            p = Path(file_path)
            if not p.is_absolute():
                p = self._repo_root / p
            if not p.exists() or not p.is_file():
                return None
            return p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:  # noqa: BLE001  读取失败降级跳过
            logger.debug("RelateAdapter: 读取文件失败(%s: %s)", file_path, e)
            return None

    def _make_finding(
        self, source: str, existing: str, sim: float, idx: int, force_acknowledged: bool = False
    ) -> Finding:
        """构造 Finding（severity 仅 review/acknowledged，永不 extract）。"""
        severity = "acknowledged" if force_acknowledged or sim < self._config.relate_threshold else "review"
        return Finding(
            finding_id=f"RL-{idx}-{source}-{existing}",
            severity=severity,
            clone_type="T2",  # MinHash token 级结构相似度（T2 类）
            similarity=round(sim, 4),
            source_file=source,
            source_function="unknown",  # MVP 文件级粒度——函数级由精检器负责
            source_lineno=0,
            existing_file=existing,
            existing_function="unknown",
            existing_lineno=0,
            import_suggestion=None,  # 预筛器不建议导入路径
        )

    def _to_relative_path(self, file_path: str) -> str:
        """将绝对路径转为相对仓库根目录的路径（归一化斜杠）。"""
        try:
            p = Path(file_path)
            if p.is_absolute():
                rel = p.relative_to(self._repo_root)
                return str(rel).replace("\\", "/")
            return file_path.replace("\\", "/")
        except ValueError:
            return file_path.replace("\\", "/")
