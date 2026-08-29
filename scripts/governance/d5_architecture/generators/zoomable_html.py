# [BLUEPRINT] MOD-GOV_ZOOMABLE_HTML
# [MODULE] scripts.governance.d5_architecture.generators.zoomable_html
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] generate_domain_doc.py（生成 md 后联动生成 HTML）;tmp/md_to_mermaid_html.py（CLI wrapper）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_ZOOMABLE_HTML | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""可缩放 Mermaid HTML 生成器（共享模块）。

从 .md 文件的 mermaid 代码块生成自包含 HTML（浏览器打开可 Ctrl+滚轮无限缩放 +
拖动平移）。供 generate_domain_doc.py 在生成域文档 md 后**联动生成 HTML**，以及
tmp/md_to_mermaid_html.py CLI 调用。

治本（2026-08-01）：从 gitignored 的 tmp/md_to_mermaid_html.py 提取为 tracked 共享
模块，使 generate_domain_doc.py 能在生成 md 后自动同步 HTML 到 _zoomable_html/
子文件夹——reconciler 刷新 md 即联动刷新 HTML，不依赖 tmp/。HTML 集中子文件夹，
不与 .md 混放。

mermaid.min.js 策略：dev 环境（仓库根 tmp/mermaid.min.js 存在）内嵌离线自包含；
其他环境（CI/他人 clone）回退 jsdelivr CDN（HTML 小，需网络）。

[MODULE] scripts.governance.d5_architecture.generators.zoomable_html
[INVARIANTS] 输出幂等(相同md→相同HTML);HTML输出到md同级_zoomable_html/子文件夹
[CONSUMERS] generate_domain_doc.py(联动);tmp/md_to_mermaid_html.py(CLI wrapper)
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 无mermaid块→返回None跳过;mermaid.min.js缺失→CDN降级
[DOMAIN] D_GOVERNANCE
"""

__manifest__ = """
args: []
description: 可缩放 Mermaid HTML 生成器（共享模块）。
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re
import sys
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
# 治本（#ARCH-REGEN-CONCURRENCY-001 P2-2b，2026-08-06）：
# zoomable_html 被 reconcile 以 importlib in-process 加载时，generators 目录不在
# sys.path 上（脚本直接运行时 Python 自动把脚本目录加到 sys.path[0]，但 importlib
# 不加），导致下方 ``from _common import`` 抛 ModuleNotFoundError。提前把本文件
# 所在目录（generators/，即 _common.py 所在目录）加入 sys.path，确保 _common
# 无论直接运行还是 in-process 加载均可导入。
_GENERATORS_DIR = str(_THIS_FILE.parent)
if _GENERATORS_DIR not in sys.path:
    sys.path.insert(0, _GENERATORS_DIR)

# 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：
# 幂等时间源（脚本最近 git commit 时间），消除 datetime.now() 导致的 per-second diff。
from _common import idempotent_timestamp  # noqa: E402

# 仓库根：含 scripts/ 和 src/ 的目录（zoomable_html.py 在 scripts/governance/d5_architecture/generators/）
REPO_ROOT = next(p for p in _THIS_FILE.parents if (p / "scripts").is_dir() and (p / "src").is_dir())

# mermaid.min.js dev-local 位置（gitignored，3.4MB）。存在则内嵌离线，不存在则 CDN 降级。
_MERMAID_LOCAL = REPO_ROOT / "tmp" / "mermaid.min.js"
_CDN_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"

# HTML 集中输出子文件夹名（位于 md 同级目录下，下划线前缀表衍生制品，不参与域文档编号）
# 公开常量：generate_domain_doc.py import 它生成 md 里的 HTML 跳转链接路径。
HTML_SUBDIR = "_zoomable_html"

# Ctrl+滚轮独立缩放每个图（改 SVG 宽高，不依赖浏览器原生 zoom）；双击重置为一屏自适应。
# 1500ms 延迟等 mermaid 渲染完成后再绑定。
_ZOOM_JS = """
  // mermaid 渲染后绑定 Ctrl+滚轮缩放 + 鼠标拖动平移（每个图独立，双击重置）
  // Ctrl+Shift+D 切换 拖动模式（可平移）/ 选择模式（可复制文字）
  var dragEnabled = true;  // 全局开关：true=拖动平移，false=选中复制
  function updateModeUI() {
    document.querySelectorAll('.diagram').forEach(function(d) {
      d.style.cursor = dragEnabled ? 'grab' : 'text';
    });
    var ind = document.getElementById('mode-indicator');
    if (ind) {
      ind.textContent = dragEnabled ? '拖动模式（可平移）' : '选择模式（可复制）';
      ind.style.background = dragEnabled ? '#0277bd' : '#2e7d32';
    }
  }
  document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey && (e.key === 'D' || e.key === 'd')) {
      e.preventDefault();
      dragEnabled = !dragEnabled;
      updateModeUI();
    }
  });
  var diagramFitters = [];
  // 绑定缩放/拖动到一个已渲染的 diagram（renderAll 每渲染完一个图即调用，无需等 setTimeout）
  function bindZoomToDiagram(diagram) {
    var zoomLevel = 1, fitScale = 0, natW = 0, natH = 0;
    var badge = diagram.querySelector('.zoom-badge');
    var vp = diagram.querySelector('.mermaid');  // 固定高度可滚动视口
    function applyZoom() {
      var s = diagram.querySelector('svg');
      if (s && fitScale > 0 && natW > 0) {
        var eff = fitScale * zoomLevel;  // 相对原始尺寸的有效缩放
        s.setAttribute('width', natW * eff);
        s.setAttribute('height', natH * eff);
        s.style.width = (natW * eff) + 'px';
        s.style.height = (natH * eff) + 'px';
      }
      if (badge) badge.textContent = Math.round(fitScale * zoomLevel * 100) + '%';
    }
    // 自适应：图渲染后按视口算出"刚好塞进"的缩放，直接写到 SVG 宽高——布局也跟着缩小，
    // 页面不再超高；zoomLevel 是在此基础上放大的倍数（1=一屏，2=放大两倍），双击回到 1。
    function fitToViewport() {
      var s = diagram.querySelector('svg');
      if (!s) return;
      // 每次都重新量内容尺寸（不缓存）：lateRepair 修框/字体后到会改变 bbox，
      // 用旧缓存会让 fit 失真、修大的框显示不全
      try { var bb = s.getBBox(); if (bb.width > 0 && bb.height > 0) { natW = bb.width; natH = bb.height; } } catch (e) {}
      if (!natW || !natH) { try { natW = s.width.baseVal.value; natH = s.height.baseVal.value; } catch (e) {} }
      if (!natW || !natH) return;
      if (!s.getAttribute('viewBox')) s.setAttribute('viewBox', '0 0 ' + natW + ' ' + natH);
      if (!vp) return;
      var fit = Math.min((vp.clientWidth - 24) / natW, (vp.clientHeight - 24) / natH, 1);
      if (fit > 0 && isFinite(fit)) { fitScale = fit; zoomLevel = 1; vp.scrollLeft = 0; vp.scrollTop = 0; applyZoom(); }
    }
    fitToViewport();
    diagramFitters.push(fitToViewport);
    // 某些浏览器首次 fit 时布局未稳定（getBBox/视口尺寸未就绪），延迟重试兜底
    setTimeout(fitToViewport, 500);
    setTimeout(fitToViewport, 1500);
    // Ctrl+滚轮缩放（改 SVG 宽高；放大后视口内滚动查看）
    diagram.addEventListener('wheel', function(e) {
      if (!e.ctrlKey) return;
      e.preventDefault();
      zoomLevel = Math.max(0.2, Math.min(30, zoomLevel * (e.deltaY < 0 ? 1.15 : 1/1.15)));
      applyZoom();
    }, { passive: false });
    // 鼠标拖动平移 = 滚动视口（仅拖动模式拦截；选择模式放行让浏览器选中文本）
    var dragging = false, startX = 0, startY = 0, startSL = 0, startST = 0;
    diagram.addEventListener('mousedown', function(e) {
      if (!dragEnabled || !vp) return;
      dragging = true;
      startX = e.clientX; startY = e.clientY;
      startSL = vp.scrollLeft; startST = vp.scrollTop;
      diagram.style.cursor = 'grabbing';
      e.preventDefault();
    });
    document.addEventListener('mousemove', function(e) {
      if (!dragging) return;
      vp.scrollLeft = startSL - (e.clientX - startX);
      vp.scrollTop = startST - (e.clientY - startY);
    });
    document.addEventListener('mouseup', function() {
      if (dragging) { dragging = false; diagram.style.cursor = dragEnabled ? 'grab' : 'text'; }
    });
    // 双击重置：回到一屏自适应
    diagram.addEventListener('dblclick', function() { zoomLevel = 1; if (vp) { vp.scrollLeft = 0; vp.scrollTop = 0; } applyZoom(); });
  }
  // 窗口尺寸变化时重新自适应（如调整浏览器窗口）
  window.addEventListener('resize', function() { diagramFitters.forEach(function(f) { f(); }); });
"""


def extract_mermaid_blocks(md_text: str) -> list[tuple[str, str]]:
    """提取 mermaid 代码块，配对上方最近的标题行作为图标题。

    返回 [(title, code), ...]。标题取最近的 #/##/### 行；无标题用"图 N"。
    """
    lines = md_text.split("\n")
    blocks: list[tuple[str, str]] = []
    current_title = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m and not line.strip().startswith("```"):
            current_title = m.group(2).strip()
        if line.strip().startswith("```mermaid"):
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append((current_title or f"图 {len(blocks) + 1}", "\n".join(code_lines)))
        i += 1
    return blocks


def extract_h1(md_text: str) -> str:
    """提取 MD 第一个 H1 标题（# xxx），无则返回空串。

    用于 HTML 大标题——优先用文档自身的 H1（含域中英文名）而非纯文件名。
    """
    for line in md_text.split("\n"):
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            return m.group(1).strip()
    return ""


def _escape_for_html(text: str) -> str:
    """转义 mermaid 代码里的 < > &，使其安全内嵌进 <pre>。注意：不转义引号（不影响）。"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_html(blocks: list[tuple[str, str]], doc_title: str, mermaid_source: str, is_cdn: bool) -> str:
    """生成自包含 HTML。

    mermaid_source: CDN 模式为 URL；内嵌模式为 mermaid.min.js 文件内容。
    """
    script_tag = f'<script src="{mermaid_source}"></script>' if is_cdn else f"<script>{mermaid_source}</script>"
    diagrams_html = []
    for idx, (title, code) in enumerate(blocks, 1):
        safe_code = _escape_for_html(code)
        diagrams_html.append(
            f'<div class="diagram">\n'
            f'  <span class="zoom-badge">100%</span>\n'
            f'  <h2><span class="num">#{idx}</span> {_escape_for_html(title)}</h2>\n'
            f'  <pre class="mermaid">{safe_code}</pre>\n'
            f"</div>"
        )
    diagrams = "\n".join(diagrams_html)
    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源
    gen_time = idempotent_timestamp(Path(__file__))
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- 静态服务器（python -m http.server）无 Cache-Control，浏览器启发式缓存会让用户
     看到旧版 HTML 误以为修复没生效。no-cache 强制每次重验证（文件小，代价可忽略）。 -->
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
<title>{_escape_for_html(doc_title)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
         margin: 24px; background: #fafafa; color: #333; }}
  /* 标题 + 操作提示整体固定在顶部（sticky），滚动时常驻可见 */
  .header-bar {{ position: sticky; top: 0; z-index: 100; background: #fafafa;
                 padding: 10px 0 8px; border-bottom: 1px solid #e0e0e0;
                 box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
  .header-bar h1 {{ font-size: 22px; margin: 0 0 6px 0; }}
  .hint {{ color: #888; font-size: 13px; margin-bottom: 0; padding: 10px 12px;
           background: #f0f4f8; border-left: 3px solid #0277bd; border-radius: 4px; }}
  .hint kbd {{ background: #fff; border: 1px solid #ccc; border-radius: 3px; padding: 1px 5px;
              font-size: 12px; box-shadow: 0 1px 0 #aaa; }}
  .diagram {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
              padding: 16px 20px; margin: 20px 0; overflow: hidden; position: relative;
              cursor: grab; }}
  .diagram h2 {{ font-size: 15px; color: #444; margin: 0 0 12px 0;
                 padding-bottom: 8px; border-bottom: 1px solid #eee; font-weight: 600; }}
  .diagram h2 .num {{ color: #0277bd; margin-right: 6px; }}
  .zoom-badge {{ position: absolute; top: 12px; right: 16px; background: #0277bd; color: #fff;
                 font-size: 12px; padding: 2px 8px; border-radius: 10px; z-index: 10;
                 pointer-events: none; opacity: 0.85; }}
  .mode-badge {{ display: inline-block; background: #0277bd; color: #fff; font-size: 12px;
                 padding: 2px 8px; border-radius: 10px; margin: 0 2px; transition: background 0.2s; }}
  /* .mermaid 是固定高度的可滚动视口：图按"刚好塞进视口"的尺寸渲染（整图一屏可见），
     放大后超出视口则内部滚动（拖动平移=滚动视口），页面整体不再超高。 */
  .mermaid {{ display: block; height: calc(100vh - 170px); min-height: 220px; overflow: auto;
              background: #fff; border-radius: 4px; }}
  .mermaid svg {{ max-width: none !important; display: block; margin: 0 auto; }}
  /* subgraph/cluster 背景透明：Mermaid 默认浅蓝白，强制透明与分图白色背景保持一致。
     无 subgraph 的图（域文档等）无 .cluster 元素，此规则零影响。 */
  .mermaid .cluster rect {{ fill: transparent !important; stroke: transparent !important; }}
  /* 节点标签防裁剪（2026-08-01 三轮治本）：
     ① 生成端 _wrap_label_text 预折行（<br/> 显式断行），测量行数≈渲染行数；
     ② 字号行高必须带 !important——Mermaid v11 为每张图注入 ID 作用域样式
        （形如 #mermaid-N .nodeLabel 规则把字号设回 14px），ID 特异性压过本 class 规则；
     ③ 行高必须 1.5 而非更小：Mermaid 测量阶段用的就是它内联的 line-height:1.5，
        且中文字体（微软雅黑等）字形高度约 1.3em，行高压到 1.3 时字形会超出行框
        绘制——最后一行被框线横穿（用户 Edge 实测踩坑：字体加载完成后二次排版，
        div 盒高量不到字形超出，JS 修复脚本也抓不到）。1.5 与测量阶段一致且给
        中文字形留足空间。纪律详见 visualization_view_template.md §4.10。
     max-width 560px 仅作异常兜底（预折行正常约 ≤300px，远低于 560px 不触发二次
     折行——若调小到会触发二次折行的值，裁剪问题立刻复发）。 */
  .mermaid .nodeLabel, .mermaid .edgeLabel, .mermaid foreignObject div, .mermaid foreignObject span {{
      white-space: normal !important;
      overflow-wrap: anywhere !important;
      word-break: break-word !important;
      max-width: 560px !important;
      font-size: 11px !important;
      line-height: 1.5 !important;
  }}
  .mermaid:empty::after {{ content: "（渲染中…若长期空白请检查 mermaid.js 是否加载成功）";
                           color: #999; font-size: 13px; }}
</style>
</head>
<body>
<div class="header-bar">
<h1>{_escape_for_html(doc_title)}</h1>
<div class="hint">
  缩放：<kbd>Ctrl</kbd> + <kbd>滚轮</kbd> 无限放大/缩小（SVG 矢量清晰）｜
  <kbd>Ctrl</kbd> + <kbd>0</kbd> 重置 ｜ <kbd>Ctrl</kbd> + <kbd>+</kbd>/<kbd>-</kbd> 步进。
  模式：<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>D</kbd> 切换
  <span id="mode-indicator" class="mode-badge">拖动模式（可平移）</span> ↔ 选择模式（可复制文字）。
  共 {len(blocks)} 个图。生成于 {gen_time}（内容异常请先 <kbd>Ctrl</kbd>+<kbd>F5</kbd> 强刷）。
</div>
</div>
{diagrams}
{script_tag}
<script>
  mermaid.initialize({{
    startOnLoad: false,  // 关闭自动加载，改为 renderAll() 手动逐个渲染（小图优先，避免大图阻塞）
    securityLevel: 'loose',
    suppressErrors: false,
    // 放开 mermaid 渲染上限：默认 maxTextSize=50000 + maxEdges=500，大域（如 D_GOV_SCRIPTS
    // 385 节点 ~11万字符、744+ 边）会触发"Edge limit exceeded"/"Syntax error"拒绝渲染。
    // maxTextSize 提到 1亿、maxEdges 提到 1万，让浏览器能渲染任意大图（dagre 布局稍慢但可完成）。
    maxTextSize: 100000000,
    maxEdges: 10000,
    flowchart: {{ useMaxWidth: false, htmlLabels: true, nodeSpacing: 30, rankSpacing: 35 }}
  }});
  // 手动逐个渲染 mermaid 图（startOnLoad=false）。按代码长度升序：小图先渲染立即可见，
  // 大图（如全景图385节点）dagre 布局慢但不阻塞已渲染的小图。每渲染完一个立即绑定缩放。
  var DEBUG = /[?&]debug=1/.test(location.search);
  var repairStats = {{ nodes: 0, repaired: 0, worst: [] }};
  var dbgEl = null;
  // 节点框渲染后实测修复（治本兜底，2026-08-01 第三/四轮）：
  // 节点框由 mermaid 测量阶段算死。若浏览器测量后才完成字体替换（扩展注入 webfont、
  // 系统字体回退慢、页面翻译改文案），文字会重新排版变高/偏移，超出框底被截——用户
  // 实测 Edge（扩展环境）溢出而 Chrome/干净 Edge 正常，且一次性修复抓到 0 个（修复
  // 跑完字体才到）。对策：①用 getBoundingClientRect 实测文字相对框的四向溢出
  // （位置+尺寸并集，偏移也能抓）；②fonts.ready / window load / 2s / 5s 多时点重跑，
  // 字体后到也能二次修复。显示像素差值 ÷ scale 换算回 svg 用户单位（页面缩放免疫）。
  function repairDiagram(svg) {{
    if (!svg) return;
    var scale = 1;
    try {{
      var dispW = svg.getBoundingClientRect().width;
      var vbw = (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width) || svg.width.baseVal.value;
      if (dispW > 0 && vbw > 0) scale = dispW / vbw;
    }} catch (e) {{}}
    if (!isFinite(scale) || scale <= 0) scale = 1;
    svg.querySelectorAll('g.node').forEach(function(g) {{
      var fo = g.querySelector('foreignObject');
      var rect = g.querySelector('rect');
      if (!fo || !rect) return;
      var div = fo.querySelector('div');
      if (!div) return;
      repairStats.nodes++;
      var rR = rect.getBoundingClientRect();
      var dR = div.getBoundingClientRect();
      var up = (rR.top - dR.top) / scale, down = (dR.bottom - rR.bottom) / scale;
      var left = (rR.left - dR.left) / scale, right = (dR.right - rR.right) / scale;
      if (up <= 1 && down <= 1 && left <= 1 && right <= 1) return;
      var pad = 4;
      if (up > 1 || down > 1) {{
        var u = Math.max(up, 0), d = Math.max(down, 0);
        rect.setAttribute('y', rect.y.baseVal.value - u - pad);
        rect.setAttribute('height', rect.height.baseVal.value + u + d + pad * 2);
        fo.setAttribute('y', fo.y.baseVal.value - u - pad);
        fo.setAttribute('height', fo.height.baseVal.value + u + d + pad * 2);
      }}
      if (left > 1 || right > 1) {{
        var l = Math.max(left, 0), rr = Math.max(right, 0);
        rect.setAttribute('x', rect.x.baseVal.value - l - pad);
        rect.setAttribute('width', rect.width.baseVal.value + l + rr + pad * 2);
        fo.setAttribute('x', fo.x.baseVal.value - l - pad);
        fo.setAttribute('width', fo.width.baseVal.value + l + rr + pad * 2);
      }}
      repairStats.repaired++;
      if (DEBUG && repairStats.worst.length < 5) {{
        var cs = window.getComputedStyle(div);
        repairStats.worst.push({{ id: (g.id || '?').slice(-28), up: Math.round(up), down: Math.round(down), font: cs.fontSize, family: cs.fontFamily.slice(0, 42) }});
      }}
    }});
  }}
  function updateDbg() {{
    if (!DEBUG) return;
    if (!dbgEl) {{
      dbgEl = document.createElement('div');
      dbgEl.style.cssText = 'margin-top:6px;padding:8px 12px;background:#fff8e1;border:1px solid #f0c36d;border-radius:4px;font-size:12px;color:#5d4037;white-space:pre-wrap;';
      var hint = document.querySelector('.hint');
      if (hint) hint.appendChild(dbgEl);
    }}
    dbgEl.textContent = '诊断(debug=1)：节点 ' + repairStats.nodes + ' 个，修复 ' + repairStats.repaired + ' 个'
      + (repairStats.worst.length ? ' ｜ 样例: ' + JSON.stringify(repairStats.worst) : '')
      + ' ｜ UA: ' + navigator.userAgent;
  }}
  function repairAllDiagrams() {{
    document.querySelectorAll('.diagram pre.mermaid svg').forEach(function(s) {{ repairDiagram(s); }});
    updateDbg();
  }}
  async function renderAll() {{
    var pres = Array.prototype.slice.call(document.querySelectorAll('.diagram pre.mermaid'));
    var items = pres.map(function(p, i) {{ return {{ pre: p, idx: i, code: p.textContent, size: p.textContent.length }}; }});
    // 先把所有 pre 替换为"渲染中"占位，避免显示原始 mermaid 代码
    items.forEach(function(it) {{
      it.pre.textContent = '';
      it.pre.innerHTML = '<div style="color:#999;padding:12px;font-size:13px">⏳ 渲染中…（大图可能需要数十秒，请稍候）</div>';
    }});
    items.sort(function(a, b) {{ return a.size - b.size; }});
    for (var k = 0; k < items.length; k++) {{
      var it = items[k];
      try {{
        var res = await mermaid.render('mmd-svg-' + it.idx, it.code);
        it.pre.innerHTML = res.svg;
        // 强制 subgraph/cluster 背景为透明（Mermaid 默认浅蓝白，与分图白色背景保持一致）
        it.pre.querySelectorAll('.cluster rect').forEach(function(r) {{
            r.style.fill = 'transparent';
            r.style.stroke = 'transparent';
        }});
        repairDiagram(it.pre.querySelector('svg')); updateDbg();  // 渲染后实测修复（在 bindZoom 前，fit 才能算进新尺寸）
        if (res.bindFunctions) {{ try {{ res.bindFunctions(it.pre); }} catch (e) {{}} }}
      }} catch (err) {{
        it.pre.innerHTML = '<div style="color:#c00;padding:12px;font-size:13px">⚠ 渲染失败: ' + String(err && err.message || err).replace(/</g,'&lt;') + '</div>';
      }}
      var diagram = it.pre.closest('.diagram');
      if (diagram) bindZoomToDiagram(diagram);
      updateModeUI();
      await new Promise(function(r) {{ setTimeout(r, 30); }});  // 让浏览器喘息：刷新已渲染的图
    }}
    updateDbg();
    // 字体/文案后到（扩展注入 webfont、系统字体回退慢、页面翻译）→ 多时点二次修复 + 重新自适应
    function lateRepair() {{
      repairAllDiagrams();
      if (typeof diagramFitters !== 'undefined') diagramFitters.forEach(function(f) {{ f(); }});
    }}
    if (document.fonts && document.fonts.ready) {{
      document.fonts.ready.then(lateRepair);
      if (document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', lateRepair);
    }}
    window.addEventListener('load', lateRepair);
    setTimeout(lateRepair, 2000);
    setTimeout(lateRepair, 5000);
  }}
  renderAll();
{_ZOOM_JS}
</script>
</body>
</html>"""


# 模块级缓存（治本：generate_domain_doc --all 时 73 个域各调一次 emit_zoomable_html，
# 每次 read_text 整个 3.4MB mermaid.min.js ≈ 250MB 重复 IO）。进程内只读一次；
# tmp/mermaid.min.js 是 dev-local 静态资源，进程生命周期内视为不变。
_MERMAID_SOURCE_CACHE: tuple[str, bool, str] | None = None


def resolve_mermaid_source(force_cdn: bool = False) -> tuple[str, bool, str]:
    """返回 (mermaid_source, is_cdn, mode_desc)。

    优先内嵌 tmp/mermaid.min.js（dev 环境离线自包含）；不存在或 force_cdn 时回退 CDN。
    """
    global _MERMAID_SOURCE_CACHE
    if force_cdn:
        return _CDN_URL, True, "CDN"
    if _MERMAID_SOURCE_CACHE is None:
        if _MERMAID_LOCAL.is_file():
            _MERMAID_SOURCE_CACHE = (
                _MERMAID_LOCAL.read_text(encoding="utf-8"),
                False,
                f"内嵌({_MERMAID_LOCAL.stat().st_size // 1024}KB)",
            )
        else:
            _MERMAID_SOURCE_CACHE = (_CDN_URL, True, "CDN")
    return _MERMAID_SOURCE_CACHE


def emit_zoomable_html(
    md_path: Path,
    md_content: str,
    output_dir: Path | None = None,
    force_cdn: bool = False,
) -> Path | None:
    """从 md 内容生成可缩放 HTML，输出到 md 同级 ``_zoomable_html/`` 子文件夹。

    联动入口：generate_domain_doc.py 生成 md 后调用本函数，自动同步 HTML。
    无 mermaid 块时返回 None（跳过，不生成 HTML）。

    Args:
        md_path: md 文件路径（用于确定输出文件名和默认输出目录）。
        md_content: md 文本内容。
        output_dir: HTML 输出目录（默认 md_path.parent / _zoomable_html）。
        force_cdn: 强制用 CDN（不内嵌本地 mermaid.min.js）。

    Returns:
        生成的 HTML 文件路径；无 mermaid 块时返回 None。
    """
    blocks = extract_mermaid_blocks(md_content)
    if not blocks:
        return None
    doc_title = extract_h1(md_content) or md_path.stem
    out_dir = output_dir or (md_path.parent / HTML_SUBDIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{md_path.stem}.html"

    source, is_cdn, _mode = resolve_mermaid_source(force_cdn)
    html = build_html(blocks, doc_title, source, is_cdn)
    out_path.write_text(html, encoding="utf-8", newline="\n")
    return out_path
