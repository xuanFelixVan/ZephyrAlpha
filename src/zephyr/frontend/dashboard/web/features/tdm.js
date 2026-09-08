/* ── 交易决策全景（横向思维导图树）· 真源 /api/tdm（mtime 缓存）· 30s 轮询自动映射 ──
 * Owner 2026-09-07 裁定：MD 生成图不够直观，前端原生实时渲染；A股·研究栏 tdm.html 承载。
 * 布局：根流组(E建仓/P持仓/X离场/F组合/横切C) → 枝干节点(第二列) → 子节点(第三列)，
 *       DOM 卡片+SVG 贝塞尔连线；配色 production 蓝/design 橙虚/paper 绿（v1.8 语义）。
 * 激活检测：页面片段经 innerHTML 注入（script 不执行），本文件由 loader 显式加载；
 *           30s tick 时仅 p-tdm 可见才 fetch，页面隐藏零开销。 */
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
    var f = n.flow || '';
    if (f === 'entry_flow') return { key: 'E', zh: '建仓流', order: 0 };
    if (f === 'position_flow') return { key: 'P', zh: '持仓流', order: 1 };
    if (f === 'exit_flow') return { key: 'X', zh: '离场流', order: 2 };
    if (f === 'portfolio_flow') return { key: 'F', zh: '组合流', order: 3 };
    return { key: 'C', zh: '横切层(币圈预留)', order: 4 };
  }

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
    var y = 8;
    /* 满屏布局（每次渲染实时量容器——窗口最大化/抽屉开合由 ResizeObserver 触发重渲）：
     * 子节点列锚定右缘铺满全宽，枝干列按比例放中间，流标签最左 */
    var W = canvas.clientWidth || 1400;
    var CW = Math.min(Math.max(Math.floor(W * 0.30), 260), 620);   /* 卡片宽 30%（260~620 夹紧） */
    var X3 = Math.max(W - CW - 14, Math.floor(W * 0.34));          /* 子节点列贴右缘 */
    var X2 = Math.max(150, Math.floor(W * 0.12));                  /* 枝干列 */
    var X1 = 8;                                                    /* 流标签 */

    function card(n, cx, cy) {
      var el = document.createElement('div');
      el.className = 'tn ' + cls(n) + (n.id === TDM.sel ? ' sel' : '');
      el.style.left = cx + 'px'; el.style.top = cy + 'px'; el.style.width = CW + 'px';
      var gist = n.note ? n.note.slice(0, 110) : (n.q || '').slice(0, 100);
      el.innerHTML = '<div class="tn-n">' + (n.autonomy === 'paper' ? '📄 ' : '') + (n.name || n.id) +
        '</div><div class="tn-g">' + gist + '</div>';
      el.title = n.id;
      el.onclick = function () { if (TDM.dragDist > 3) return; TDM.sel = n.id; render(); drawer(); };   /* 拖动平移后松手不算点击 */
      el.dataset.id = n.id;
      host.appendChild(el);
      return el;
    }
    function wire(a, b) { wires.push([a, b]); }

    Object.keys(flows).sort().forEach(function (fo) {
      var g = flows[fo];
      var fel = document.createElement('div');
      fel.className = 'tg';
      fel.style.left = X1 + 'px'; fel.style.top = (y + 20) + 'px';
      fel.innerHTML = g.info.zh + ' <span class="cnt">' + g.items.length + '</span>';
      host.appendChild(fel);
      var gy = y;
      g.items.forEach(function (n) {
        var nel = card(n, X2, gy);
        var chY = gy;
        (kids[n.id] || []).forEach(function (c) {
          var cel = card(c, X3, chY);
          wire(nel, cel);
          chY += cel.offsetHeight + 8;
        });
        gy = Math.max(gy + nel.offsetHeight + 8, chY + 4);
        wire(fel, nel);
      });
      y = gy + 30;
    });

    /* 世界层与树的尺寸用布局常量直接算（X3+CW=内容右缘）——绝不能量 host.offsetWidth：
     * world 是绝对定位收缩包裹、树内卡片全绝对定位不撑宽，量出来恒≈padding 8px，
     * SVG 视口跟着塌成 8px 宽 → 连线全部画到可视区外（b20260908-02 连线消失的根因） */
    var contentW = X3 + CW + 4;
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
        return '<path d="M' + ax + ',' + ay + ' C' + mx + ',' + ay + ' ' + mx + ',' + by + ' ' + bx + ',' + by + '"/>';
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

  function drawer() {
    var box = document.getElementById('tdm-drawer');
    if (!box) return;
    var n = TDM.data && TDM.sel && TDM.data.nodes.find(function (x) { return x.id === TDM.sel; });
    if (!n) { box.style.display = 'none'; return; }
    var byIdMap = {};
    TDM.data.nodes.forEach(function (x) { byIdMap[x.id] = x; });
    var par = n.parent && byIdMap[n.parent];
    var refs = Object.keys(n.refs || {}).map(function (k) {
      var label = REF_ZH[k.replace('_refs', '')] || k.replace('_refs', '');
      return '<div class="kv"><b>' + label + '</b>（' + n.refs[k].length + '）：' + n.refs[k].join('、') + '</div>';
    }).join('');
    var cms = (n.comments || []).map(function (c) { return '<div class="cm">' + c + '</div>'; }).join('')
      || '<div class="cm">（无）</div>';
    box.style.display = 'block';
    box.innerHTML =
      '<h3>' + (n.autonomy === 'paper' ? '📄 ' : '') + n.name +
      ' <span class="dim" style="font-size:11px;font-weight:400">' + n.id + '</span></h3>' +
      '<div class="sec">归属</div><div class="kv">流=' + (FLOW_ZH[n.flow] || n.flow || '—') +
      ' ｜ 层=' + (n.layer || '—') + ' ｜ 时点=' + (n.point || '—') +
      '<br>父节点=' + (par ? par.name + '（' + n.parent + '）' : (n.parent || '无（流根）')) + '</div>' +
      '<div class="sec">问</div><div class="kv">' + (n.q || '—') + '</div>' +
      '<div class="sec">机制（怎么算）</div><div class="kv">' + (n.note || '（待补）') + '</div>' +
      '<div class="sec">治理</div><div class="kv">激活=' + (n.activation || '—') + ' ｜ 档位=' + (n.autonomy || '—') +
      '<br>失效=' + (n.invalidation || '—') +
      '<br>兜底=' + (n.fallback || '—') + '</div>' +
      '<div class="sec">模块锚（MOD）</div><div class="kv">' +
      (n.module_id ? (n.module_ref || '') + (n.module_ref ? ' ｜ ' : '') + n.module_id : '无（红节点——设计态，模块未建/未锚）') + '</div>' +
      (n.mounts && n.mounts.length ? '<div class="sec">策略挂载（STR，' + n.mounts.length + '）</div><div class="kv">' + n.mounts.join('、') + '</div>' : '') +
      (refs ? '<div class="sec">依据锚（八轴引用）</div>' + refs : '') +
      '<div class="sec">设计备注（裁定/欠账原文）</div>' + cms;
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
