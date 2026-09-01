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
        pg.wait_for_selector("#p-stockq", state="attached", timeout=20000)  # 全部页面片段注入完成的标志（页面默认隐藏，只验存在性）
        yield pg
        browser.close()


def test_all_pages_present(page):
    """loader PAGES 清单每个页面都必须注入 DOM（漏挂=页面消失，modlib 事故类）。"""
    pages = _pages_from_loader()
    missing = [pid for pid in pages if page.evaluate(f"!!document.getElementById('p-{pid}')") is False]
    assert not missing, f"页面片段未注入 DOM: {missing}"


def test_stockq_structure(page):
    """K 线页结构断言（验收单 ACC-F-STOCKQ-COSTLINE 机断条款 + 事件行/时间轴 + sq-stock-header）。"""
    page.wait_for_function("!!(window.ZK && ZK.features && ZK.features['cost-line'])", timeout=20000)  # 等 JS 加载链走完再导航（防竞态）
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
    design_ok = page.evaluate("!!document.querySelector('#p-design') && document.querySelector('#p-design').textContent.includes('DS-11 模块拆件标准')")
    modlib_ok = page.evaluate("!!document.querySelector('#p-modlib') && document.querySelector('#p-modlib').textContent.includes('模块拆件契约试点')")
    assert design_ok, "design 页缺 DS-11 模块拆件标准"
    assert modlib_ok, "modlib 页缺 模块拆件契约试点 区"
