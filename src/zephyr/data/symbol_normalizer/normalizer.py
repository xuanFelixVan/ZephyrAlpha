# [BLUEPRINT] MOD-L00-004 | docs/03_modules/ | §symbol_normalizer
# [MODULE] zephyr.data.symbol_normalizer.normalizer
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.data.symbol_normalizer.__init__
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 纯函数无副作用；幂等（已带后缀原样返回）；空输入→空输出；未知前缀→exchange=None
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入→空输出；未知前缀→exchange=None（不擅自推断）
# [TESTS] tests/data/test_symbol_normalizer.py
# [TTL] permanent
# [ARCH-REF] #ARCH-DATA-SYMBOL-001 TRAE-082 #ARCH-SYMBOL-NORMALIZE-001
"""symbol 标准化核心实现——TRAE-082 symbol 约定铁律。

详见 zephyr.data.symbol_normalizer.__init__ 模块文档。
"""
from __future__ import annotations

# exchange 码常量（TRAE-082）
EXCHANGE_SH = "SH"      # 上海证券交易所
EXCHANGE_SZ = "SZ"      # 深圳证券交易所
EXCHANGE_BJ = "BJ"      # 北京证券交易所
EXCHANGE_HK = "HK"      # 港交所
EXCHANGE_US = "US"      # 美股（纽交所/纳斯达克统一码）

# A 股裸码首位 → exchange 映射（TRAE-082 + #ARCH-SYMBOL-NORMALIZE-001）
# 规则：6/9→SH, 0/3→SZ, 5→SH(沪市基金/ETF), 1→SZ(深市基金/ETF), 8/4→BJ
# 对标 tushare ts_code 后缀 + akshare 前缀推断
_PREFIX_TO_EXCHANGE: dict[str, str] = {
    "6": EXCHANGE_SH,   # 沪市股票（600519 贵州茅台 / 900901 B 股）
    "9": EXCHANGE_SH,   # 沪市 B 股（900901）
    "0": EXCHANGE_SZ,   # 深市股票（000001 平安银行）
    "3": EXCHANGE_SZ,   # 深市创业板（300750 宁德时代）
    "5": EXCHANGE_SH,   # 沪市基金/ETF（510050 / 588000 / 501001 LOF）
    "1": EXCHANGE_SZ,   # 深市基金/ETF（159915 / 150018 LOF）
    "8": EXCHANGE_BJ,   # 北交所（830799）
    "4": EXCHANGE_BJ,   # 北交所老三板（430047）
}

# 前缀式 symbol 的交易所前缀映射（lof_list 旧格式：sh501001 / sz159915）
_PREFIX_STR_TO_EXCHANGE: dict[str, str] = {
    "sh": EXCHANGE_SH,
    "sz": EXCHANGE_SZ,
    "bj": EXCHANGE_BJ,
    "hk": EXCHANGE_HK,
}


def derive_exchange(symbol: str) -> str | None:
    """从裸码首位推导 A 股交易所码。

    按首位数字推断：6/9→SH, 0/3→SZ, 5→SH, 1→SZ, 8/4→BJ。
    港股/美股/期货无法从裸码推断（需显式提供 exchange），返回 None。

    Args:
        symbol: 裸码（纯数字/字母代码，如 '600519' / '159915' / 'AAPL'）

    Returns:
        exchange 码（'SH'/'SZ'/'BJ'）或 None（未知前缀/非 A 股）

    Examples:
        >>> derive_exchange('600519')
        'SH'
        >>> derive_exchange('000001')
        'SZ'
        >>> derive_exchange('159915')
        'SZ'
        >>> derive_exchange('510050')
        'SH'
        >>> derive_exchange('AAPL')
        None
    """
    if not symbol:
        return None
    s = str(symbol).strip()
    if not s:
        return None
    # 仅对纯数字裸码做前缀推断（字母代码如 AAPL/IF2510 不推断）
    if not s[0].isdigit():
        return None
    return _PREFIX_TO_EXCHANGE.get(s[0])


def split_suffix_symbol(symbol_with_suffix: str) -> tuple[str, str | None]:
    """拆分带后缀的 symbol 为 (裸码, exchange)。

    后缀式 symbol（tushare/akshare 格式）：159865.SZ / 600519.SH / 000001.SZ
    拆分为裸码 + exchange 两列（TRAE-082 阶段2 小表归一）。

    幂等：纯裸码（无 '.'）返回 (symbol, None)，exchange 需另行 derive。

    Args:
        symbol_with_suffix: 带后缀的 symbol（'159865.SZ'）

    Returns:
        (裸码, exchange) 元组，如 ('159865', 'SZ')；无后缀返回 (原值, None)

    Examples:
        >>> split_suffix_symbol('159865.SZ')
        ('159865', 'SZ')
        >>> split_suffix_symbol('600519')
        ('600519', None)
        >>> split_suffix_symbol('AAPL.US')
        ('AAPL', 'US')
    """
    if not symbol_with_suffix:
        return ("", None)
    s = str(symbol_with_suffix).strip()
    if "." not in s:
        return (s, None)
    parts = s.split(".", 1)
    return (parts[0], parts[1].upper() if parts[1] else None)


def split_prefix_symbol(symbol_with_prefix: str) -> tuple[str, str | None]:
    """拆分前缀式 symbol 为 (裸码, exchange)。

    前缀式 symbol（lof_list 旧格式）：sh501001 / sz159915 / bj430047
    拆分为裸码 + exchange 两列（TRAE-082 阶段2 小表归一）。

    幂等：纯裸码（无字母前缀）返回 (symbol, None)。

    Args:
        symbol_with_prefix: 前缀式 symbol（'sh501001'）

    Returns:
        (裸码, exchange) 元组，如 ('501001', 'SH')；无前缀返回 (原值, None)

    Examples:
        >>> split_prefix_symbol('sh501001')
        ('501001', 'SH')
        >>> split_prefix_symbol('sz159915')
        ('159915', 'SZ')
        >>> split_prefix_symbol('600519')
        ('600519', None)
    """
    if not symbol_with_prefix:
        return ("", None)
    s = str(symbol_with_prefix).strip()
    if not s:
        return ("", None)
    # 检查是否以已知交易所前缀开头（sh/sz/bj/hk，大小写不敏感）
    lower = s.lower()
    for prefix, exchange in _PREFIX_STR_TO_EXCHANGE.items():
        if lower.startswith(prefix):
            rest = s[len(prefix):]
            # 仅当剩余部分非空才视为前缀式（避免误判 sh 等单字符）
            if rest:
                return (rest, exchange)
    return (s, None)


def to_canonical(symbol: str, exchange: str) -> str:
    """构造 symbol_canonical（跨表 JOIN 的 canonical 身份键）。

    symbol_canonical = concat(symbol, '.', exchange)，如 '600519.SH' / '000001.SZ'。
    单字段唯一标识全球任一可交易标的（TRAE-082 INV-003）。

    Args:
        symbol: 裸码（'600519'）
        exchange: exchange 码（'SH'）

    Returns:
        symbol_canonical（'600519.SH'）

    Examples:
        >>> to_canonical('600519', 'SH')
        '600519.SH'
        >>> to_canonical('000001', 'SZ')
        '000001.SZ'
    """
    if not symbol:
        return ""
    if not exchange:
        return str(symbol)
    return "{}.{}".format(symbol, exchange)


def normalize_symbol(symbol: str) -> tuple[str, str | None]:
    """归一化任意格式 symbol 为 (裸码, exchange)。

    自动识别三种格式（TRAE-082 三套约定归一）：
      1. 裸码（600519）→ derive_exchange 推导 → ('600519', 'SH')
      2. 后缀式（600519.SH）→ split_suffix_symbol → ('600519', 'SH')
      3. 前缀式（sh501001）→ split_prefix_symbol → ('501001', 'SH')

    优先级：后缀式 > 前缀式 > 裸码推导（后缀/前缀显式优于推导）。

    Args:
        symbol: 任意格式 symbol

    Returns:
        (裸码, exchange) 元组；exchange 可能为 None（无法推断）

    Examples:
        >>> normalize_symbol('600519')
        ('600519', 'SH')
        >>> normalize_symbol('600519.SH')
        ('600519', 'SH')
        >>> normalize_symbol('sh501001')
        ('501001', 'SH')
        >>> normalize_symbol('AAPL')
        ('AAPL', None)
    """
    if not symbol:
        return ("", None)
    s = str(symbol).strip()
    if not s:
        return ("", None)
    # 优先级1：后缀式（含 '.'）
    if "." in s:
        return split_suffix_symbol(s)
    # 优先级2：前缀式（sh/sz/bj/hk 开头）
    bare, exchange = split_prefix_symbol(s)
    if exchange is not None:
        return (bare, exchange)
    # 优先级3：裸码推导
    return (s, derive_exchange(s))


def is_bare_symbol(symbol: str) -> bool:
    """判断 symbol 是否为裸码（无后缀无前缀）。

    裸码 = 纯代码，不含 '.' 且不以交易所前缀（sh/sz/bj/hk）开头。
    用于 provider 写入路径校验（TRAE-082 INV-001：symbol 列只存裸码）。

    Args:
        symbol: 待检查的 symbol

    Returns:
        True 若为裸码

    Examples:
        >>> is_bare_symbol('600519')
        True
        >>> is_bare_symbol('600519.SH')
        False
        >>> is_bare_symbol('sh501001')
        False
    """
    if not symbol:
        return False
    s = str(symbol).strip()
    if "." in s:
        return False
    lower = s.lower()
    for prefix in _PREFIX_STR_TO_EXCHANGE:
        if lower.startswith(prefix) and len(s) > len(prefix):
            return False
    return True
