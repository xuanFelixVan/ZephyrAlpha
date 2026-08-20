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
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-DATA-SYMBOL-001 TRAE-082 #ARCH-SYMBOL-NORMALIZE-001
"""symbol 标准化核心实现——TRAE-082 symbol 约定铁律。

详见 zephyr.data.symbol_normalizer.__init__ 模块文档。
"""

from __future__ import annotations

# exchange 码常量（TRAE-082）
EXCHANGE_SH = "SH"  # 上海证券交易所
EXCHANGE_SZ = "SZ"  # 深圳证券交易所
EXCHANGE_BJ = "BJ"  # 北京证券交易所
EXCHANGE_HK = "HK"  # 港交所
EXCHANGE_US = "US"  # 美股（纽交所/纳斯达克统一码）

# A 股裸码首位 → exchange 映射（TRAE-082 1.1.0 + #ARCH-DATA-SYMBOL-002）
# 规则：6/5/9→SH, 0/3/1/2→SZ, 8/4→BJ
# 1.1.0 修订：补 '2'→SZ（深市 B 股 200xxx/201xxx，实测 281K 行）；
#            '9' 由单纯首位映射改为先查 3 位/2 位前缀消歧（见 _PREFIX3/_PREFIX2）
_PREFIX_TO_EXCHANGE: dict[str, str] = {
    "6": EXCHANGE_SH,  # 沪市股票（600519 贵州茅台）
    "9": EXCHANGE_SH,  # 沪市 B 股（900901）——920xxx 等北交所由 _PREFIX2 覆盖
    "5": EXCHANGE_SH,  # 沪市基金/ETF（510050 / 588000 / 501001 LOF）
    "0": EXCHANGE_SZ,  # 深市股票（000001 平安银行）
    "3": EXCHANGE_SZ,  # 深市创业板（300750 宁德时代）
    "1": EXCHANGE_SZ,  # 深市基金/ETF（159915 / 150018 LOF）
    "2": EXCHANGE_SZ,  # 深市 B 股（200026 / 201872）——1.1.0 新增
    "8": EXCHANGE_BJ,  # 北交所（830799）
    "4": EXCHANGE_BJ,  # 北交所老三板（430047）
}

# 3 位前缀 → exchange（消歧：9xx B股/北交所 + 11x/13x 可转债）
# 必须在 _PREFIX_TO_EXCHANGE 之前检查（更具体优先）
_PREFIX3_TO_EXCHANGE: dict[str, str] = {
    "900": EXCHANGE_SH,
    "901": EXCHANGE_SH,
    "902": EXCHANGE_SH,
    "903": EXCHANGE_SH,
    # 可转债（1.1.1 补：'1'→SZ 是深市 ETF 159xxx 规则，但 110/113 是沪市可转债，需 3 位消歧）
    "110": EXCHANGE_SH,
    "113": EXCHANGE_SH,  # 沪市可转债（110064 / 113537）
    "123": EXCHANGE_SZ,
    "128": EXCHANGE_SZ,  # 深市可转债（123xxx / 128xxx，与 '1'→SZ 一致，显式记录）
    # 国债逆回购（'2'→SZ 是深市 B 股，但 204 是沪市国债逆回购）
    "204": EXCHANGE_SH,  # 沪市国债逆回购（204001 GC001）
}

# 2 位前缀 → exchange（北交所 83/43/87/92/93/94）
# '92'/'93'/'94' 必须在此拦截（否则 1 位 '9'→SH 误判）；83/43/87 与 1 位一致（冗余但显式）
_PREFIX2_TO_EXCHANGE: dict[str, str] = {
    "83": EXCHANGE_BJ,
    "43": EXCHANGE_BJ,
    "87": EXCHANGE_BJ,
    "92": EXCHANGE_BJ,
    "93": EXCHANGE_BJ,
    "94": EXCHANGE_BJ,
}

# 指数代码 3 位前缀 → exchange（kline_index 表专用，与股票前缀规则不同）
# 关键差异（TRAE-082 核心消歧）：000xxx 在股票表是深市（000001 平安银行 SZ），
#   在指数表是沪市（000001 上证指数 SH）。故指数表须用本映射而非 _PREFIX_TO_EXCHANGE。
# 规则：000/880/930/931/932→SH，399→SZ，其余→''(未知指数前缀)
_INDEX_PREFIX3_TO_EXCHANGE: dict[str, str] = {
    "000": EXCHANGE_SH,  # 上证系列指数（000001 上证指数 / 000300 沪深300 / 000016 上证50）
    "880": EXCHANGE_SH,  # 申万行业指数（880001 申万全A）
    "930": EXCHANGE_SH,
    "931": EXCHANGE_SH,
    "932": EXCHANGE_SH,  # 中证系列指数
    "399": EXCHANGE_SZ,  # 深证系列指数（399001 深证成指 / 399006 创业板指）
}

# 前缀式 symbol 的交易所前缀映射（lof_list 旧格式：sh501001 / sz159915）
_PREFIX_STR_TO_EXCHANGE: dict[str, str] = {
    "sh": EXCHANGE_SH,
    "sz": EXCHANGE_SZ,
    "bj": EXCHANGE_BJ,
    "hk": EXCHANGE_HK,
}


def derive_exchange(symbol: str) -> str | None:
    """从裸码推导 A 股交易所码（TRAE-082 1.1.0 分层前缀消歧）。

    推导优先级（与 CH MATERIALIZED multiIf 严格对齐，更具体优先）：
      1. 3 位前缀：900/901/902/903 → SH（沪市 B 股，消歧 9xx）
      2. 2 位前缀：83/43/87/92/93/94 → BJ（北交所；92/93/94 必须在此拦截，
         否则 1 位 '9'→SH 误判 920xxx 北交所为沪市）
      3. 1 位前缀：6/5/9→SH, 0/3/1/2→SZ, 8/4→BJ（2→SZ 为 1.1.0 新增深市 B 股）

    港股/美股/期货（字母代码如 AAPL/IF2510）无法从裸码推断，返回 None。

    Args:
        symbol: 裸码（纯数字/字母代码，如 '600519' / '200026' / '920001' / 'AAPL'）

    Returns:
        exchange 码（'SH'/'SZ'/'BJ'）或 None（未知前缀/非 A 股）

    Examples:
        >>> derive_exchange('600519')
        'SH'
        >>> derive_exchange('000001')
        'SZ'
        >>> derive_exchange('200026')   # 深市 B 股（1.1.0 新增）
        'SZ'
        >>> derive_exchange('900901')   # 沪市 B 股（3 位前缀消歧）
        'SH'
        >>> derive_exchange('920001')   # 北交所（2 位前缀 '92'→BJ，避免 '9'→SH 误判）
        'BJ'
        >>> derive_exchange('159915')
        'SZ'
        >>> derive_exchange('AAPL')
        None
    """
    if not symbol:
        return None
    s = str(symbol).strip()
    if not s or not s[0].isdigit():
        return None
    # 优先级1：3 位前缀消歧（9xx：900xxx 沪市 B 股 vs 920xxx 北交所）
    if len(s) >= 3 and s[:3] in _PREFIX3_TO_EXCHANGE:
        return _PREFIX3_TO_EXCHANGE[s[:3]]
    # 优先级2：2 位前缀（北交所 83/43/87/92/93/94）
    if len(s) >= 2 and s[:2] in _PREFIX2_TO_EXCHANGE:
        return _PREFIX2_TO_EXCHANGE[s[:2]]
    # 优先级3：1 位前缀（含 1.1.0 新增 '2'→SZ）
    return _PREFIX_TO_EXCHANGE.get(s[0])


def derive_exchange_index(symbol: str) -> str | None:
    """从裸码推导指数交易所码（kline_index 表专用，TRAE-082 核心消歧）。

    指数代码与股票代码前缀规则不同（同一裸码在不同表语义推导不同 exchange）：
      - 000xxx 股票→SZ（000001 平安银行），指数→SH（000001 上证指数）
      - 399xxx → SZ（深证成指 / 创业板指）
      - 880xxx → SH（申万行业指数）
      - 930/931/932xxx → SH（中证系列指数）

    与 derive_exchange 的关键区别：000xxx 在本函数返回 SH（上证指数），
    在 derive_exchange 返回 SZ（平安银行）。这是 kline_daily vs kline_index
    跨表碰撞消歧的核心——同裸码不同 exchange → 不同 symbol_canonical。

    Args:
        symbol: 指数裸码（纯数字，如 '000001' / '399006' / '880001'）

    Returns:
        exchange 码（'SH'/'SZ'）或 None（未知前缀/非数字）

    Examples:
        >>> derive_exchange_index('000001')   # 上证指数（非平安银行！）
        'SH'
        >>> derive_exchange_index('000300')   # 沪深300
        'SH'
        >>> derive_exchange_index('399006')   # 创业板指
        'SZ'
        >>> derive_exchange_index('880001')   # 申万全A
        'SH'
        >>> derive_exchange_index('AAPL')
        None
    """
    if not symbol:
        return None
    s = str(symbol).strip()
    if not s or not s[0].isdigit() or len(s) < 3:
        return None
    return _INDEX_PREFIX3_TO_EXCHANGE.get(s[:3])


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
            rest = s[len(prefix) :]
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
