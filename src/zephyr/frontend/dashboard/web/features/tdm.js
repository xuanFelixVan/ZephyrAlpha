/* ── 交易决策全景（横向思维导图树）· 真源 /api/tdm（mtime 缓存）· 30s 轮询自动映射 ──
 * Owner 2026-09-07 裁定：MD 生成图不够直观，前端原生实时渲染；A股·研究栏 tdm.html 承载。
 * 布局：根流组(E建仓/P持仓/X离场/F组合/横切C) → 枝干节点(第二列) → 子节点(第三列)，
 *       DOM 卡片+SVG 贝塞尔连线；配色 production 蓝/design 橙虚/paper 绿（v1.8 语义）。
 * 激活检测：页面片段经 innerHTML 注入（script 不执行），本文件由 loader 显式加载；
 *           30s tick 时仅 p-tdm 可见才 fetch，页面隐藏零开销。
 * 抽屉 v2（b20260908-10）：右侧详情抽屉重设计——标题徽标区/治理键值网格/依据锚八轴 chip 流/
 *           上下游节点导航行（点击跳选）/长文行高≥1.6；纯 HTML+CSS，数据契约与画布交互不变。 */
(function () {
  'use strict';
  var TDM = { data: null, sel: null, stamp: null, busy: false, dragDist: 0 };
  var API_BASE = 'http://127.0.0.1:8890';   /* 与 services/api.js 同源——app:// 模式下相对 fetch 会打到 app://api/tdm 必断 */
  /* 画布视图状态（交互规范=visualization_view_template.md §6.6：滚轮缩放/拖动平移/双击重置/Ctrl+Shift+D 切模式） */
  var view = { z: 1, x: 0, y: 0, dragMode: true };

  function worldEl() { return document.getElementById('tdm-world'); }
  function canvasEl() { return document.querySelector('.tdm-canvas'); }

  function applyView() {
    var w = worldEl();
    if (w) w.style.transform = 'translate(' + view.x + 'px,' + view.y + 'px) scale(' + view.z + ')';
    var badge = document.getElementById('tdm-zoom');
    if (badge) badge.textContent = Math.round(view.z * 100) + '% ｜ ' + (view.dragMode ? '✋ 拖动' : '📋 文字可选');
  }

  /* 以鼠标点为锚缩放（光标处内容保持在光标下——地图类标准手感） */
  function zoomAt(cx, cy, factor) {
    var c = canvasEl(); if (!c) return;
    var r = c.getBoundingClientRect();
    var mx = cx - r.left, my = cy - r.top;
    var nz = Math.max(0.2, Math.min(30, view.z * factor));
    var k = nz / view.z;
    view.x = mx - (mx - view.x) * k;
    view.y = my - (my - view.y) * k;
    view.z = nz;
    applyView();
  }

  function setMode(dm) {
    view.dragMode = dm;
    var c = canvasEl();
    if (c) c.classList.toggle('select-mode', !dm);
    var btn = document.getElementById('tdm-mode');
    if (btn) btn.textContent = dm ? '✋ 拖动模式' : '📋 选择复制';
    applyView();
  }

  window.tdmToggleMode = function () { setMode(!view.dragMode); };

  function visible() {
    var el = document.getElementById('p-tdm');
    return el && el.offsetParent !== null;
  }

  function flowOf(n) {
    if (n.id && n.id.indexOf('TDM-C') === 0) return { key: 'C', zh: '币圈镜像', order: 4 };   /* 币圈壳节点 flow 字段也是 entry_flow，按 id 前缀分家 */
    var f = n.flow || '';
    if (f === 'entry_flow') return { key: 'E', zh: '建仓流', order: 0 };
    if (f === 'position_flow') return { key: 'P', zh: '持仓流', order: 1 };
    if (f === 'exit_flow') return { key: 'X', zh: '离场流', order: 2 };
    if (f === 'portfolio_flow') return { key: 'F', zh: '组合流', order: 3 };
    return { key: 'U', zh: '未分组', order: 9 };
  }

  /* 配色=施工状态三态（Owner 2026-09-08 裁定保留）：蓝=实锚（有模块）/ 橙虚线=🔴红节点（设计态）/ 绿=📄paper（实盘执行档）；
   * 层级不占颜色——层级由列位+字号梯度承载（tn-d1~d4 只管大小不管色） */
  function cls(n) {
    if (n.autonomy === 'paper') return 'paper';
    return n.module_ref ? 'production' : 'design';
  }

  function load() {
    if (TDM.busy) return;
    TDM.busy = true;
    fetch(API_BASE + '/api/tdm').then(function (r) { return r.json(); }).then(function (d) {
      TDM.busy = false;
      if (!d.ok) {
        var meta0 = document.getElementById('tdm-meta');
        if (meta0) meta0.textContent = '面板 API 未重启（无 /api/tdm 端点）——服务总闸「↻ 重启面板 API」后恢复';
        return;
      }
      var changed = TDM.stamp && TDM.stamp !== d.generated_at;
      TDM.stamp = d.generated_at;
      TDM.data = d;
      render();
      var meta = document.getElementById('tdm-meta');
      if (meta) meta.textContent = d.nodes.length + ' 节点 / ' + d.edges.length + ' 边 · 更新 ' + d.generated_at.slice(5, 16);
      var cnt = document.getElementById('tdm-count');   /* 页头赚点数=实时真源值，禁硬编码（防节点增减漂移） */
      if (cnt) cnt.textContent = d.nodes.length;
      if (changed) { drawer(); }   /* 真源变了：重开抽屉刷新内容 */
      else if (TDM.sel) { drawer(); }
    }).catch(function () {
      TDM.busy = false;
      var meta = document.getElementById('tdm-meta');
      if (meta) meta.textContent = 'API 断开（面板 API 未启动?）';
    });
  }

  function render() {
    var d = TDM.data; if (!d) return;
    var host = document.getElementById('tdm-tree');
    var svg = document.getElementById('tdm-wire');
    var canvas = document.querySelector('.tdm-canvas');
    if (!host || !svg || !canvas) return;
    var byId = {};
    d.nodes.forEach(function (n) { byId[n.id] = n; });
    var kids = {};
    d.nodes.forEach(function (n) {
      if (n.parent && byId[n.parent]) (kids[n.parent] = kids[n.parent] || []).push(n);
    });
    var flows = {};
    d.nodes.forEach(function (n) {
      if (n.parent && byId[n.parent]) return;
      var fl = flowOf(n);
      (flows[fl.order] = flows[fl.order] || { info: fl, items: [] }).items.push(n);
    });

    host.innerHTML = '';
    var wires = [];
    var elById = {};        /* 节点 id → 卡片元素（边连线用） */
    var drawnPairs = {};    /* 已画连线 pair key（父链先画，同对边去重） */
    var y = 8;
    /* 四层一列布局：流标签列(8~LABEL_W) + L1~L4 四列均分剩余宽度——同层永远同列，层级即列号；
     * 每次渲染实时量容器，窗口/抽屉变化由 ResizeObserver 触发重渲 */
    var W = canvas.clientWidth || 1400;
    var LABEL_W = 215, GAP = 12;   /* 流根标签 24px 字号所需宽度（最长"横切层·币圈"≈205px） */
    var colW = Math.max(170, Math.floor((W - LABEL_W - 16 - GAP * 3) / 4));
    var COLX = [0, LABEL_W, LABEL_W + (colW + GAP), LABEL_W + (colW + GAP) * 2, LABEL_W + (colW + GAP) * 3];

    function card(n, cx, cy, depth) {
      var el = document.createElement('div');
      el.className = 'tn tn-d' + depth + ' ' + cls(n) + (n.id === TDM.sel ? ' sel' : '');
      el.style.left = cx + 'px'; el.style.top = cy + 'px'; el.style.width = colW + 'px';
      /* 小字=「问」全文（不 slice 截断），CSS line-clamp 2：一排放不下自动提行成两行；标题保留 📄 前缀 */
      el.innerHTML = '<div class="tn-n">' + (n.autonomy === 'paper' ? '📄 ' : '') + (n.name || n.id) + '</div>' +
        '<div class="tn-g">' + (n.q || '（问待补）') + '</div>';
      el.title = n.id;
      el.onclick = function () { if (TDM.dragDist > 3) return; TDM.sel = n.id; render(); drawer(); };   /* 拖动平移后松手不算点击 */
      el.dataset.id = n.id;
      host.appendChild(el);
      elById[n.id] = el;
      return el;
    }
    /* 连线样式：parent/sequence/broadcast=实线主链；feed/feedback=虚线喂给——wire(a,b,dashed,type) */
    function wire(a, b, dashed, wtype) {
      wires.push([a, b, !!dashed, wtype || 'parent']);
    }

    /* 递归布局：节点排在自己层列的 y 处；子节点从父同 y 起往下排（思维导图惯例）；
     * 返回子树底部 y——父的下一个兄弟排在其整棵子树之后。树深≤4（门禁锁死），dd 兜底夹紧 */
    function place(n, depth, y, parentEl) {
      var dd = Math.min(Math.max(depth, 1), 4);
      var el = card(n, COLX[dd], y, dd);
      if (parentEl) {
        wire(parentEl, el, false, 'parent');
        drawnPairs[parentEl.dataset.id + '>' + n.id] = 1;   /* 父链已画的对，边循环跳过 */
      }
      var cy = y, bottom = y + el.offsetHeight;
      (kids[n.id] || []).forEach(function (c) {
        var cb = place(c, depth + 1, cy, el);
        cy = cb + 8;
        bottom = Math.max(bottom, cb);
      });
      return bottom;
    }

    Object.keys(flows).sort().forEach(function (fo) {
      var g = flows[fo];
      var fel = document.createElement('div');
      fel.className = 'tg';
      fel.style.left = '8px'; fel.style.top = (y + 20) + 'px';
      fel.innerHTML = g.info.zh + ' <span class="cnt">' + g.items.length + '</span>';
      host.appendChild(fel);
      var fy = y;
      g.items.forEach(function (n) {
        var cb = place(n, 1, fy, fel);
        fy = cb + 26;
      });
      y = fy + 6;
    });

    /* 全量依赖边连线（171 条）：父链之外的 sequence/feed/broadcast/feedback 全画——
     * 用户记忆中"全景图枝丫繁茂"=边完整版（此前只画 ~100 条父链，交叉喂给线全缺失） */
    (d.edges || []).forEach(function (e) {
      var a = elById[e.from_node], b = elById[e.to_node];
      if (!a || !b) return;
      var key = e.from_node + '>' + e.to_node;
      if (drawnPairs[key]) return;
      drawnPairs[key] = 1;
      var t = e.edge_type || 'feed';
      wire(a, b, t === 'feed' || t === 'feedback', t);
    });

    /* 世界层与树的尺寸用布局常量直接算（X3+CW=内容右缘）——绝不能量 host.offsetWidth：
     * world 是绝对定位收缩包裹、树内卡片全绝对定位不撑宽，量出来恒≈padding 8px，
     * SVG 视口跟着塌成 8px 宽 → 连线全部画到可视区外（b20260908-02 连线消失的根因） */
    var contentW = COLX[4] + colW + 4;
    var contentH = y + 6;
    host.style.width = contentW + 'px';
    host.style.height = contentH + 'px';   /* 绝对定位子元素不撑高父容器——显式写内容高度 */
    var w = worldEl();
    if (w) {
      w.style.width = Math.max(contentW, canvas.clientWidth) + 'px';
      w.style.height = Math.max(contentH, canvas.clientHeight || 600) + 'px';
    }

    requestAnimationFrame(function () {
      var ww = w ? w.offsetWidth : contentW;
      var hh = Math.max(contentH, canvas.clientHeight || 600);
      svg.style.width = ww + 'px';
      svg.style.height = hh + 'px';
      svg.setAttribute('width', ww);
      svg.setAttribute('height', hh);
      svg.innerHTML = wires.map(function (p) {
        var a = p[0], b = p[1];
        var ax = a.offsetLeft + a.offsetWidth, ay = a.offsetTop + a.offsetHeight / 2;
        var bx = b.offsetLeft, by = b.offsetTop + b.offsetHeight / 2;
        var mx = (ax + bx) / 2;
        var color = '#2c3a52';
        if (p[3] === 'feedback') color = '#9a5a1a';          /* 反馈边：暗橙 */
        else if (p[3] === 'feed') color = '#44546e';          /* 喂给边：亮一档灰蓝 */
        return '<path d="M' + ax + ',' + ay + ' C' + mx + ',' + ay + ' ' + mx + ',' + by + ' ' + bx + ',' + by + '"' +
          (p[2] ? ' stroke-dasharray="5 4"' : '') +
          (color !== '#2c3a52' ? ' stroke="' + color + '"' : '') + '/>';
      }).join('');
    });
  }

  /* 窗口缩放/最大化、抽屉开合 → 容器尺寸变了就整树重排（防"渲染瞬间量宽后窗口变了布局僵死"） */
  var roTimer = null;
  var ro = new ResizeObserver(function () {
    if (!TDM.data || !visible()) return;
    if (roTimer) clearTimeout(roTimer);
    roTimer = setTimeout(render, 120);
  });

  var FLOW_ZH = { entry_flow: '建仓流 E', position_flow: '持仓流 P', exit_flow: '离场流 X', portfolio_flow: '组合流 F' };
  var REF_ZH = { factor: '因子', data: '数据源', cost_model: '成本模型', risk_limit: '风险限额', threshold: '阈值',
    event: '事件', algo: '算法', universe: '股票域', strategy: '策略', indicator: '技术指标' };

  /* 抽屉 v2（b20260908-10 重设计）：分区层次=标题徽标 → 问 → 机制 → 治理键值网格 → 模块锚 →
   * 策略挂载 → 依据锚八轴 chip 流 → 上/下游节点导航行（点击跳选）→ 设计备注；纯 HTML+CSS，数据契约不变 */
  function drawer() {
    var box = document.getElementById('tdm-drawer');
    if (!box) return;
    var n = TDM.data && TDM.sel && TDM.data.nodes.find(function (x) { return x.id === TDM.sel; });
    if (!n) { box.style.display = 'none'; return; }
    function esc(s) {   /* 真源 YAML 文本进 innerHTML——防标签断裂/注入 */
      return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
      });
    }
    var RN = TDM.data.ref_names || {};   /* 引用 id → 中文名（注册表翻译真源，API 注入） */
    function zh(id) { return RN[id] ? id + ' ' + RN[id] : id; }
    var byIdMap = {};
    TDM.data.nodes.forEach(function (x) { byIdMap[x.id] = x; });
    var par = n.parent && byIdMap[n.parent];
    /* 上下游连线（谁喂它 / 它喂谁）——全量边按当前节点过滤，带边型 glyph 溯源闭环 */
    var ups = [], downs = [];
    (TDM.data.edges || []).forEach(function (e) {
      if (e.from_node === n.id && byIdMap[e.to_node]) downs.push({ x: byIdMap[e.to_node], t: e.edge_type });
      if (e.to_node === n.id && byIdMap[e.from_node]) ups.push({ x: byIdMap[e.from_node], t: e.edge_type });
    });
    /* 状态徽标=画布卡片同语义：📄paper 绿 / 实锚蓝 / 🔴红节点橙虚 */
    var stBdg = n.autonomy === 'paper'
      ? '<span class="bdg bdg-paper">📄 paper · 实盘执行</span>'
      : (n.module_ref
        ? '<span class="bdg bdg-prod">实锚 · 已接模块</span>'
        : '<span class="bdg bdg-design">🔴 红节点 · 设计态</span>');
    var meta = (n.id.indexOf('TDM-C') === 0 ? '币圈镜像' : (FLOW_ZH[n.flow] || n.flow || '—')) +
      ' ｜ 层 ' + (n.layer || '—') + ' ｜ ' + (n.point || '—');
    /* 引用 chip：编号+中文名；hover title 全称（名称截断时兜底可读） */
    function chip(id) {
      var nm = RN[id] || '';
      return '<span class="chip" title="' + esc(zh(id)) + '"><i>' + esc(id) + '</i>' +
        (nm ? '<b>' + esc(nm) + '</b>' : '') + '</span>';
    }
    /* 节点导航行：状态点+名称+边型+id，点击跳选（抽屉内溯源，不动画布交互） */
    var GLYPH = { sequence: '→', feed: '⇢', broadcast: '⇉', feedback: '↩' };
    function nlink(x, t) {
      var dot = x.autonomy === 'paper' ? 'paper' : (x.module_ref ? 'prod' : 'design');
      return '<div class="nl" data-jump="' + esc(x.id) + '" title="' + esc(x.id) + (t ? ' · ' + esc(t) : '') + '">' +
        '<span class="dot dot-' + dot + '"></span><span class="nl-n">' + esc(x.name || x.id) + '</span>' +
        (t ? '<span class="nl-t">' + (GLYPH[t] || '·') + ' ' + esc(t) + '</span>' : '') +
        '<span class="nl-i">' + esc(x.id) + '</span></div>';
    }
    function kv(k, v) {
      return '<span class="k">' + k + '</span><span class="v' + (v ? '' : ' na') + '">' + (v ? esc(v) : '—') + '</span>';
    }
    /* 治理四键网格：空值显式 '—' 留位不塌行（验收基准 TDM-E-L1-S1 四键全空） */
    var gov = '<div class="kgrid">' + kv('激活', n.activation) + kv('档位', n.autonomy) +
      kv('失效', n.invalidation) + kv('兜底', n.fallback) + '</div>';
    var mod = n.module_id
      ? '<div class="chips">' + chip(n.module_id) + '</div>' +
        (n.module_ref ? '<div class="empty" style="margin-top:4px">module_ref = ' + esc(n.module_ref) + '</div>' : '')
      : '<div class="empty">无（红节点——设计态，模块未建/未锚）</div>';
    var mounts = (n.mounts && n.mounts.length)
      ? '<div class="chips">' + n.mounts.map(chip).join('') + '</div>'
      : '<div class="empty">（无挂载——本节点为判定/编排节点，不直接驱动策略）</div>';
    /* 依据锚：八轴分组——每轴 label+计数 一行，chip 流式排布（禁顿号长串） */
    var AXES = ['factor_refs', 'data_refs', 'cost_model_refs', 'risk_limit_refs', 'threshold_refs', 'event_refs', 'algo_refs'];
    var refsHtml = AXES.filter(function (k) { return n.refs && n.refs[k] && n.refs[k].length; }).map(function (k) {
      var label = REF_ZH[k.replace('_refs', '')] || k.replace('_refs', '');
      return '<div class="axis"><div class="axis-h"><b>' + esc(label) + '</b> <span class="cnt">' + n.refs[k].length + '</span></div>' +
        '<div class="chips">' + n.refs[k].map(chip).join('') + '</div></div>';
    }).join('');
    var cms = (n.comments || []).map(function (c) { return '<div class="cm">' + esc(c) + '</div>'; }).join('') ||
      '<div class="empty">（无）</div>';
    var scroll = box.scrollTop;   /* 30s 轮询重绘保持阅读位置 */
    box.style.display = 'block';
    box.innerHTML =
      '<div class="dr-name">' + (n.autonomy === 'paper' ? '📄 ' : '') + esc(n.name || n.id) + '</div>' +
      '<div class="dr-id">' + esc(n.id) + ' · ' + esc(meta) + '</div>' +
      '<div class="dr-badges">' + stBdg + '</div>' +
      '<div class="dr-par">父节点：' + (par ? esc(par.name) + '（' + esc(n.parent) + '）' : (n.parent ? esc(n.parent) : '无（流根）')) + '</div>' +
      '<div class="sec">问</div><div class="txt q">' + (n.q ? esc(n.q) : '—') + '</div>' +
      '<div class="sec">机制（怎么算）</div><div class="txt">' + (n.note ? esc(n.note) : '（待补）') + '</div>' +
      '<div class="sec">治理</div>' + gov +
      '<div class="sec">模块锚（MOD）</div>' + mod +
      '<div class="sec">策略挂载（STR）</div>' + mounts +
      (refsHtml ? '<div class="sec">依据锚（八轴引用）</div>' + refsHtml : '') +
      '<div class="sec">上游（谁喂给它）<span class="cnt">' + ups.length + '</span></div>' +
      (ups.length ? ups.map(function (u) { return nlink(u.x, u.t); }).join('') : '<div class="empty">—</div>') +
      '<div class="sec">下游（它喂给谁）<span class="cnt">' + downs.length + '</span></div>' +
      (downs.length ? downs.map(function (u) { return nlink(u.x, u.t); }).join('') : '<div class="empty">—</div>') +
      '<div class="sec">设计备注（裁定/欠账原文）</div>' + cms;
    box.scrollTop = scroll;
    /* 上/下游导航行点击跳选——drawer 内闭环 */
    box.querySelectorAll('[data-jump]').forEach(function (el) {
      el.addEventListener('click', function () {
        TDM.sel = el.getAttribute('data-jump');
        render();
        drawer();
      });
    });
  }

  window.tdmFilter = function (q) {
    q = (q || '').trim().toLowerCase();
    var byId = {};
    (TDM.data ? TDM.data.nodes : []).forEach(function (n) { byId[n.id] = n; });
    document.querySelectorAll('#tdm-tree .tn').forEach(function (t) {
      var n = byId[t.dataset.id];
      var hit = !q || (n && ((n.id + ' ' + n.name).toLowerCase().indexOf(q) >= 0));
      t.classList.toggle('hit', !!q && !!hit);
      t.classList.toggle('dimmed', !!q && !hit);
    });
  };

  setInterval(function () { if (visible()) load(); }, 30000);
  /* 頁面切到 tdm 时立即拉一次（go() 切 display，用事件捕获不到——轮询兜底+首次延迟） */
  setTimeout(load, 1200);
  var tdmCanvas = document.querySelector('.tdm-canvas');
  if (tdmCanvas) ro.observe(tdmCanvas);   /* 尺寸监听：最大化/还原/抽屉开合自动重排 */

  /* ── 画布交互挂接（规范=visualization_view_template.md §6.6，移植 zoomable_html 四项操作）── */
  (function () {
    var c = canvasEl();
    if (!c) return;
    /* ① 滚轮缩放（0.2x~30x，1.15 倍步进，以光标为锚） */
    c.addEventListener('wheel', function (e) {
      e.preventDefault();
      zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? 1.15 : 1 / 1.15);
    }, { passive: false });
    /* ② 拖动平移（拖动模式；按住左键位移画布，位移>3px 判定为拖动而非点击） */
    var drag = null;
    c.addEventListener('mousedown', function (e) {
      if (!view.dragMode || e.button !== 0) return;
      drag = { sx: e.clientX, sy: e.clientY, ox: view.x, oy: view.y, dist: 0 };
      c.classList.add('dragging');
    });
    window.addEventListener('mousemove', function (e) {
      if (!drag) return;
      var dx = e.clientX - drag.sx, dy = e.clientY - drag.sy;
      drag.dist = Math.max(drag.dist, Math.abs(dx) + Math.abs(dy));
      view.x = drag.ox + dx; view.y = drag.oy + dy;
      applyView();
    });
    window.addEventListener('mouseup', function () {
      if (!drag) return;
      TDM.dragDist = drag.dist;
      drag = null;
      var cc = canvasEl(); if (cc) cc.classList.remove('dragging');
      setTimeout(function () { TDM.dragDist = 0; }, 0);   /* click 事件派发后再清零 */
    });
    /* ③ 双击空白重置（双击节点不算——节点双击是两次打开抽屉） */
    c.addEventListener('dblclick', function (e) {
      if (e.target && e.target.closest && e.target.closest('.tn, .tg')) return;
      view.z = 1; view.x = 0; view.y = 0;
      applyView();
    });
    /* ④ Ctrl+Shift+D 切换 拖动/选择复制 模式 */
    document.addEventListener('keydown', function (e) {
      if (e.ctrlKey && e.shiftKey && (e.key === 'D' || e.key === 'd')) {
        e.preventDefault();
        window.tdmToggleMode();
      }
    });
    setMode(true);   /* 初始同步按钮文案+徽标+光标 */
  })();
})();
