# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §alt-data
# [MODULE] scripts.data.sz_open_data.probe_all_new
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.security.secrets; stdlib
# [CONSUMERS] sz_open_data_catalog / akshare_alt_provider 系列映射
# [STARTUP] manual
# [MATURITY] beta
# [INVARIANTS] 双钥匙探测（fetch_with_any_key 主/新钥匙轮试）；字段样例仅 rows=2 不落库
# [MODIFY-GUARD] none
# [STABILITY] beta
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单接口异常->记 FAIL 不阻断全量探测
# [TESTS] 实弹脚本（输出 .runtime/tmp/szcatalog/fields_round2.json 留痕）
# [TTL] permanent
"""30 个新订阅接口全量字段探测（18 个新形态 + 复核统计月报系列列名）。"""
import json
import threading
import urllib.request
import urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded"}
from zephyr.shared.security.secrets import get_secret_or_default
# 双钥匙探测（2026-09-16 治本）：订阅按应用隔离——首轮批绑主钥匙 SZ_OPEN_DATA_APPKEY，
# 0914 扩容批绑新钥匙 SZ_OPEN_DATA_APPKEY_NEW。只用主钥匙会把新钥匙接口误报"未经许可"。
# HTTP 工具（post/get）与钥匙表复用同包 status_all（FUNCTION-DUP 治本：同实现不二写）。
from status_all import KEYS, get, post  # noqa: E402  同目录脚本直跑场景，脚本目录已在 sys.path

NEW = {
    # 第一优先
    "29200/00900227": "气候资料_历史数据",
    "29200/00900273": "地面观测实况",
    "29200/00900291": "环境气象预报",
    "29200/01403151": "水库站点日降雨量",
    # 第三优先
    "29200/01000198": "空气质量日报",
    "29200/01003608": "深圳市和区域空气质量数据",
    "29200/01903509": "二手房源信息",
    "29200/01903508": "商品房批准预售信息",
    "29200/01903511": "一手商品房按面积统计成交",
    "29200/01300964": "市场主体发展统计数据",
    "29200/03302396": "统计年报-企业登记发展情况",
    "29200/51400001": "深圳口岸出入境人员",
    "29200/51400002": "深圳口岸出入境车辆",
    # 第四优先
    "29200/00902986": "能见度探测数据",
    "29200/01400986": "水库水位表",
    "29200/01403149": "水库站点月降雨量",
    "29200/51400005": "机场口岸出入境旅客",
    "29200/51400020": "客船进出港",
}
# 统计月报 12 新系列（列名复核用，rows=2）
STAT12 = {
    "29200/03302384": "stat_private", "29200/03302373": "stat_industry",
    "29200/03302374": "stat_industry_eff", "29200/03302386": "stat_emerging",
    "29200/03302380": "stat_fdi", "29200/03302381": "stat_tourism",
    "29200/03302378": "stat_domestic_trade", "29200/03302376": "stat_construction",
    "29200/03302385": "stat_district", "29200/03302387": "stat_annual_main",
    "29200/03302388": "stat_district_gdp", "29200/03302372": "stat_analysis",
}

def fetch_with_any_key(api, rows):
    """两把钥匙轮试拉取，任一成功即返回；全被拒返回末次错误响应。"""
    last = {}
    for key in KEYS.values():
        if not key:
            continue
        r = get(f"{api}?{urllib.parse.urlencode({'page': 1, 'rows': rows, 'appKey': key})}")
        if isinstance(r, dict) and r.get("errorCode"):
            last = r
            continue
        return r
    return last

def main() -> None:
    """全量探测入口（__main__ 守卫：import 零副作用，IMPORT-SIDE-EFFECT 合规）。"""
    out = {}
    todo = dict(NEW)
    todo.update({k: v + "[STAT]" for k, v in STAT12.items()})
    for rid, name in todo.items():
        try:
            doc = post("https://opendata.sz.gov.cn/data/api/getApiDocument", {"resId": rid})
            ctx = doc[0].get("api_context", "") if isinstance(doc, list) and doc else ""
            if not ctx:
                print(f"{name}: NO api_context")
                continue
            api = f"https://opendata.sz.gov.cn/{ctx}"
            r = fetch_with_any_key(api, 2)
            if isinstance(r, dict) and r.get("errorCode"):
                print(f"{name}: ERR {r.get('errorCode')} {str(r.get('message'))[:50]}")
                out[rid] = {"name": name, "api": ctx, "error": f"{r.get('errorCode')}"}
            else:
                rows = r if isinstance(r, list) else next((v for v in r.values() if isinstance(v, list)), [])
                out[rid] = {"name": name, "api": ctx, "fields": list(rows[0].keys()) if rows else [],
                            "sample": rows[0] if rows else None, "n_fields": len(rows[0]) if rows else 0}
                print(f"{name}: OK {len(rows)}行/{out[rid]['n_fields']}字段")
        except Exception as e:
            print(f"{name}: FAIL {type(e).__name__} {str(e)[:60]}")
        threading.Event().wait(0.4)  # 限频退避：Event().wait 可中断（provider_base 惯例，PERM-TRIGGER 防复发）

    json.dump(out, open('.runtime/tmp/szcatalog/fields_round2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print("saved", len(out))


if __name__ == "__main__":
    main()
