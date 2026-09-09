# [BLUEPRINT] MOD-FE-003 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""仪表盘前端冒烟安全网（结构断言型，非像素级——视觉翻新不误伤，功能消失当场报警）。

覆盖（对应四件套验收单"机断"条款的自动化形态）：
1. test_all_pages_present —— loader.js PAGES 清单里每个页面片段都注入 DOM（modlib 漏挂事故类回归拦截）
2. test_stockq_structure —— K 线页关键结构：事件行/时间轴/¥ 开关/成本线模块已注册
3. test_overview_structure —— 总览页关键结构：图标栏/持仓双模块
4. test_spec_pages_sections —— 设计规范 DS-11 / 模块样板"十、模块拆件契约试点"存在

运行：python -m pytest tests/frontend/test_dashboard_smoke.py -x -q
自含：自起 http.server（临时端口），无需外部服务；需 playwright + chromium（python -m playwright install chromium）。
"""

from __future__ import annotations

import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

WEB_DIR = Path(__file__).resolve().parents[2] / "src" / "zephyr" / "frontend" / "dashboard" / "web"

pytestmark = pytest.mark.skipif(not WEB_DIR.exists(), reason="dashboard web dir missing")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _pages_from_loader() -> list[str]:
    """从 loader.js 解析 PAGES 清单（真源唯一，防硬编码漂移）。"""
    text = (WEB_DIR / "core" / "loader.js").read_text(encoding="utf-8")
    m = re.search(r"var PAGES = \[(.*?)\]", text, re.S)
    assert m, "loader.js PAGES array not found"
    return re.findall(r'"([^"]+)"', m.group(1))


@pytest.fixture(scope="module")
def base_url():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(WEB_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except OSError:
            time.sleep(0.2)
    else:
        proc.kill()
        pytest.fail("http.server 未能启动")
    yield url
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="module")
def page(base_url):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        pg = browser.new_page()
        pg.goto(base_url + "/index.html")
        pg.wait_for_selector(
            "#p-stockq", state="attached", timeout=20000
        )  # 全部页面片段注入完成的标志（页面默认隐藏，只验存在性）
        yield pg
        browser.close()


def test_all_pages_present(page):
    """loader PAGES 清单每个页面都必须注入 DOM（漏挂=页面消失，modlib 事故类）。"""
    pages = _pages_from_loader()
    missing = [pid for pid in pages if page.evaluate(f"!!document.getElementById('p-{pid}')") is False]
    assert not missing, f"页面片段未注入 DOM: {missing}"


def test_stockq_structure(page):
    """K 线页结构断言（验收单 ACC-F-STOCKQ-COSTLINE 机断条款 + 事件行/时间轴 + sq-stock-header）。"""
    page.wait_for_function(
        "!!(window.ZK && ZK.features && ZK.features['cost-line'])", timeout=20000
    )  # 等 JS 加载链走完再导航（防竞态）
    page.evaluate("go('stockq')")  # 走应用内导航函数（改 hash 不触发 sqInit）
    page.wait_for_timeout(3000)  # sqInit + 数据落盘 + 标注开关行渲染
    checks = page.evaluate(
        """({
        evtrow: !!document.getElementById('klp-evtrow'),
        timeline: !!document.querySelector('.klp-timeline'),
        cost_toggle: !!document.querySelector('.klp-mark-tgl[onclick*="cost"]'),
        cost_module: !!(window.ZK && ZK.features && ZK.features['cost-line']),
        chart_ready: !!(window.ZK && ZK.features['cost-line'] && ZK.features['cost-line'].chart),
        stock_header_module: !!(window.ZK && ZK.features && ZK.features['sq-stock-header']),
        stock_header_rendered: !!document.querySelector('#sq-head .sq-stock-header'),
        stock_header_dm: !!document.querySelector('#sq-head .klp-datamode'),
        key_data_module: !!(window.ZK && ZK.features && ZK.features['sq-key-data']),
        key_data_rendered: !!(document.querySelector('#sq-key-data .sq-kv-grid') || document.querySelector('#sq-key-data .sq-intro')),
        key_data_mode: !!document.querySelector('#sq-key-data .sq-kd-mode'),
        sector_tags_module: !!(window.ZK && ZK.features && ZK.features['sq-sector-tags']),
        sector_tags_rendered: !!(document.querySelector('#sq-sector-tags .badge')),
        fav_list_module: !!(window.ZK && ZK.features && ZK.features['sq-fav-list']),
        fav_list_status: !!document.querySelector('#sq-list .sq-list-status'),
        fav_list_rows: !!document.querySelector('#sq-list .sq-si'),
        position_list_module: !!(window.ZK && ZK.features && ZK.features['sq-position-list']),
        order_book_module: !!(window.ZK && ZK.features && ZK.features['sq-order-book']),
        order_book_rendered: !!(document.querySelector('#sq-order-book .sq-l2') || document.querySelector('#sq-order-book .sq-intro')),
        order_book_mode: !!document.querySelector('#sq-order-book .sq-ob-mode'),
        event_row_module: !!(window.ZK && ZK.features && ZK.features['sq-event-row']),
        event_row_live: !!(window.ZK && ZK.features && ZK.features['sq-event-row'] && ZK.features['sq-event-row'].getEvents()),
    })"""
    )
    fails = [k for k, v in checks.items() if not v]
    assert not fails, f"stockq 结构断言失败: {fails}"


def test_overview_structure(page):
    """总览页结构断言：竖排图标栏 + 持仓双模块（pos 拆分事故类回归拦截）。"""
    page.evaluate("go('overview')")
    page.wait_for_timeout(2500)
    checks = page.evaluate(
        """({
        dockbar: !!document.querySelector('.dv-dockbar'),
        pos_a: !!document.querySelector('[data-mod="pos-a"]'),
        pos_c: !!document.querySelector('[data-mod="pos-c"]'),
    })"""
    )
    fails = [k for k, v in checks.items() if not v]
    assert not fails, f"overview 结构断言失败: {fails}"


def test_spec_pages_sections(page):
    """设计规范 DS-11 / 模块样板拆件契约试点存在（标准文档消失类回归拦截）。"""
    design_ok = page.evaluate(
        "!!document.querySelector('#p-design') && document.querySelector('#p-design').textContent.includes('DS-11 模块拆件标准')"
    )
    modlib_ok = page.evaluate(
        "!!document.querySelector('#p-modlib') && document.querySelector('#p-modlib').textContent.includes('模块拆件契约试点')"
    )
    assert design_ok, "design 页缺 DS-11 模块拆件标准"
    assert modlib_ok, "modlib 页缺 模块拆件契约试点 区"


def test_chainmap_structure(page):
    """产业地图页结构断言（ACC-F-CHAINMAP-* 机断条款静态形态；API 断连也须过——验结构不验数据）。"""
    page.wait_for_function(
        "!!(window.ZK && ZK.features && ZK.features['chainmap-cluster'])", timeout=20000
    )  # 加载链尾模块注册完成=四模块全载（galaxy→nav→search→cluster 顺序）
    page.evaluate("go('chainmap')")
    page.wait_for_timeout(800)
    checks = page.evaluate(
        """({
        galaxy_canvas: !!document.getElementById('cm-canvas-galaxy'),
        cluster_canvas: !!document.getElementById('cm-canvas-cluster'),
        nav: !!document.getElementById('cm-nav'),
        search_input: !!document.querySelector('#cm-search-slot .cm-si'),
        side_panel: !!document.getElementById('cm-side'),
        m_galaxy: !!(window.ZK && ZK.features && ZK.features['chainmap-galaxy']),
        m_nav: !!(window.ZK && ZK.features && ZK.features['chainmap-nav']),
        m_search: !!(window.ZK && ZK.features && ZK.features['chainmap-search']),
        m_cluster: !!(window.ZK && ZK.features && ZK.features['chainmap-cluster']),
        m_company: !!(window.ZK && ZK.features && ZK.features['chainmap-company-card']),
    })"""
    )
    fails = [k for k, v in checks.items() if not v]
    assert not fails, f"chainmap 结构断言失败: {fails}"


def test_tdm_structure(page):
    """交易决策全景页结构断言（ACC-F-TDM-MAP/DRAWER 机断条款静态形态；API 断连也须过——验结构不验数据）。"""
    page.wait_for_function("!!window.tdmToggleMode", timeout=20000)  # tdm.js IIFE 自举完成标志（loader 加载链尾段）
    page.evaluate("go('tdm')")
    page.wait_for_timeout(500)
    checks = page.evaluate(
        """({
        world: !!document.getElementById('tdm-world'),
        tree: !!document.getElementById('tdm-tree'),
        wire: !!document.getElementById('tdm-wire'),
        drawer: !!document.getElementById('tdm-drawer'),
        meta: !!document.getElementById('tdm-meta'),
        search: !!document.getElementById('tdm-srch'),
        legend_anchor: document.querySelector('#p-tdm').textContent.includes('实锚（有模块）'),
        legend_design: document.querySelector('#p-tdm').textContent.includes('红节点（设计态）'),
        legend_paper: document.querySelector('#p-tdm').textContent.includes('实盘执行'),
    })"""
    )
    fails = [k for k, v in checks.items() if not v]
    assert not fails, f"tdm 结构断言失败: {fails}"
    # 模块脚本静态断言：抽屉函数 + 真源 fetch（源码级，防功能被静默摘除）
    src = (WEB_DIR / "features" / "tdm.js").read_text(encoding="utf-8")
    assert "function drawer()" in src, "tdm.js 缺 drawer() 函数"
    assert "/api/tdm" in src, "tdm.js 缺 /api/tdm 真源 fetch"
    # 验证档案分区（PB-04 P0-3）：台账端点 fetch + 分区标题 + 未验证徽章路径（防分区被静默摘除）
    assert "/api/tdm/validation" in src, "tdm.js 缺 /api/tdm/validation 台账 fetch"
    assert "验证档案" in src, "tdm.js 缺「验证档案」分区"
    assert "未验证" in src, "tdm.js 缺「未验证」空态徽章"
    # 算法锚分区（F-TDM-ALGOANCHOR）：分区标题 + 空态文案 + algo_refs/model_refs 字段读取（防分区被静默摘除）
    assert "算法锚" in src, "tdm.js 缺「算法锚」分区"
    assert "未登记算法锚" in src, "tdm.js 缺「未登记算法锚」空态"
    assert "model_refs" in src, "tdm.js 缺 model_refs 字段读取"
    # 算法大白话常显站位（Owner 三轮反馈）：无数据也必须留位显「未登记喂给说明」
    assert "算法大白话" in src, "tdm.js 缺「算法大白话」站位标题"
    assert "未登记喂给说明" in src, "tdm.js 缺「未登记喂给说明」空态站位"
