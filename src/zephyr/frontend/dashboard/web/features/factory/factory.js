/* ── 策略生产全景（横向流水线）· 真源 /api/factory（mtime 缓存）· 30s 轮询自动映射 ──
 * Owner 2026-09-14 指定：页面完全照抄交易决策全景（tdm）——同款画布交互（滚轮缩放/拖动平移/
 *           点节点聚焦血统/抽屉 v2/搜索高亮/30s 轮询/三态配色逐色号沿用），仅两处按数据形态适配：
 * ① 布局：TDM 是 4 层思维导图树，工厂图是 E0→E9 十环节流水线——主链一行贯通（列=环节序），
 *    五车道（E1A~E1E）挂 E1 正下方纵列；反馈环（E9→E2/E6→E1）虚线贝塞尔。
 * ② 抽屉：「验证档案」区换为「台账成绩」区（/api/factory/ledger，真源=c1_backtest.strategy_screen，
 *    双窗及格判定与 strategy_screen_query.py bothwin 同口径）。
 * 激活检测：页面片段经 innerHTML 注入（script 不执行），本文件由 loader 显式加载；
 *           30s tick 时仅 p-factory 可见才 fetch，页面隐藏零开销。
 * 聚焦模式（照抄 tdm b20260909-fe）：主链+车道挂载多跳贯通，反馈环只算直连一跳
 *           （主链含反馈环成环，全按多跳必吞全图——15/15 全亮=聚焦失效）；上游居左/下游居右
 *           同水平带（列位=主链距离），无关节点整块下移让路+压暗（只动透明度，三态色语义不变）；
 *           镜头自动适配主带（仅聚焦切换时，轮询重绘不打断手动平移缩放）；退出=Esc/双击空白/工具栏。 */
(function () {
  'use strict';
  var FAC = { data: null, ledger: null, th: null, sel: null, stamp: null, busy: false, dragDist: 0, focus: null, focusFit: null };
  var API_BASE = 'http://127.0.0.1:8890';   /* 与 services/api.js 同源——app:// 模式下相对 fetch 会打到 app://api/factory 必断（tdm 同款坑） */
  /* 画布视图状态（交互规范=visualization_view_template.md §6.6，同 tdm）：滚轮缩放/拖动平移/双击重置/Ctrl+Shift+D 切模式 */
  var view = { z: 1, x: 0, y: 0, dragMode: true, fitted: false };

  function worldEl() { return document.getElementById('factory-world'); }
  function canvasEl() { return document.querySelector('.factory-canvas'); }

  function applyView() {
    var w = worldEl();
    if (w) w.style.transform = 'translate(' + view.x + 'px,' + view.y + 'px) scale(' + view.z + ')';
    var badge = document.getElementById('factory-zoom');
    if (badge) badge.textContent = Math.round(view.z * 100) + '% ｜ ' + (view.dragMode ? '✋ 拖动' : '📋 文字可选');
  }

  /* 以鼠标点为锚缩放（光标处内容保持在光标下——地图类标准手感，照抄 tdm） */
  function zoomAt(cx, cy, factor) {
    var c = canvasEl(); if (!c) return;
    var r = c.getBoundingClientRect();
    var mx = cx - r.left, my = cy - r.top;
    var nz = Math.max(0.2, Math.min(30, view.z * factor));
    var k = nz / view.z;
    view.x = mx - (mx - view.x) * k;
    view.y = my - (my - view.y) * k;
    view.z = nz;
    view.fitted = true;   /* 手动缩放后不再自动适配（尊重用户镜头） */
    applyView();
  }

  /* 自适应镜头：全图收进可视区并居中（工厂图横向 2000px+，首载/退出聚焦时用） */
  function fitView() {
    var c = canvasEl(); if (!c) return;
    var host = document.getElementById('factory-tree');
    if (!host) return;
    var cw = c.clientWidth || 1400, ch = c.clientHeight || 600, pad = 40;
    var fz = Math.max(0.2, Math.min(1, (cw - pad * 2) / Math.max(1, host.offsetWidth),
      (ch - pad * 2) / Math.max(1, host.offsetHeight)));
    view.z = fz;
    view.x = cw / 2 - (host.offsetWidth / 2) * fz;
    view.y = Math.max(8, ch / 2 - (host.offsetHeight / 2) * fz);
    view.fitted = true;
    applyView();
  }

  function setMode(dm) {
    view.dragMode = dm;
    var c = canvasEl();
    if (c) c.classList.toggle('select-mode', !dm);
    var btn = document.getElementById('factory-mode');
    if (btn) btn.textContent = dm ? '✋ 拖动模式' : '📋 选择复制';
    applyView();
  }

  window.factoryToggleMode = function () { setMode(!view.dragMode); };

  /* 退出聚焦：回全景布局+视图复位（保留选中态与抽屉——聚焦是画布镜头，选中是抽屉上下文，两者解耦） */
  function exitFocus() {
    FAC.focus = null; FAC.focusFit = null;
    render();
    fitView();   /* 工厂图横向超宽，z=1 必溢出——回自适应镜头而非 z=1（tdm 树 fit 画布无此问题） */
  }
  window.factoryExitFocus = exitFocus;   /* 工具栏「🎯 聚焦 ✕」onclick 入口 */

  function visible() {
    var el = document.getElementById('p-factory');
    return el && el.offsetParent !== null;
  }

  /* 施工状态三态配色（与 TDM 三态色板逐色号对齐）：蓝=已建 built / 绿=部分建成 partial / 橙虚=未建 pending */
  function cls(n) {
    if (n.build_status === 'built') return 'production';
    if (n.build_status === 'partial') return 'partial';
    return 'design';
  }
  var BUILD_ZH = { built: '已建 · 实锚', partial: '部分建成', pending: '未建 · 设计态' };

  /* 台账判定中文（strategy_screen verdict 枚举；卡片成绩行+抽屉共用） */
  var VERDICT_ZH = { screened_in: '过审', rejected: '筛出', translated_c4: '已翻译', deferred_c4: '挂起',
    oos_tested: 'OOS考', failed_obsolete: '判失效' };

  /* 边分类：反馈环（真源 feedback_loops 声明）=虚线橙；其余（主链 sequence+车道挂载）=实线主链。
   * 真源 edges 是 [from, to] 数组形态（TDM 是对象带 edge_type），先归一化成对象 */
  var FB = {};
  function normEdges(d) {
    FB = {};
    (d.feedback_loops || []).forEach(function (f) { FB[f.from + '>' + f.to] = f.note || ''; });
    return (d.edges || []).map(function (e) {
      if (Array.isArray(e)) return { from_node: e[0], to_node: e[1], edge_type: FB[e[0] + '>' + e[1]] ? 'feedback' : 'sequence' };
      return e;
    });
  }

  function load() {
    if (FAC.busy) return;
    FAC.busy = true;
    fetch(API_BASE + '/api/factory').then(function (r) { return r.json(); }).then(function (d) {
      FAC.busy = false;
      if (!d.ok) {
        var meta0 = document.getElementById('factory-meta');
        if (meta0) meta0.textContent = '面板 API 未重启（无 /api/factory 端点）——服务总闸「↻ 重启面板 API」后恢复';
        return;
      }
      var changed = FAC.stamp && FAC.stamp !== d.generated_at;
      FAC.stamp = d.generated_at;
      FAC.data = d;
      render();
      var meta = document.getElementById('factory-meta');
      if (meta) meta.textContent = d.nodes.length + ' 节点 / ' + d.edges.length + ' 边 · 更新 ' + d.generated_at.slice(5, 16);
      var cnt = document.getElementById('factory-count');   /* 页头节点数=实时真源值，禁硬编码（防节点增减漂移） */
      if (cnt) cnt.textContent = d.nodes.length;
      updateKpi();   /* 施工状态统计即时可见（漏斗部分等 ledger 回来再填） */
      if (changed) { drawer(); }   /* 真源变了：重开抽屉刷新内容 */
      else if (FAC.sel) { drawer(); }
      if (!view.fitted) fitView();   /* 首载自适应镜头（用户手动缩放后不再打扰） */
      /* 台账成绩（卡片成绩行+漏斗+抽屉数据源）：失败降级无成绩行不阻断地图（tdm verdicts 同款套路） */
      fetch(API_BASE + '/api/factory/ledger').then(function (r) { return r.json(); }).then(function (lg) {
        if (lg && (lg.ok || lg.reason)) { FAC.ledger = lg; render(); updateKpi(); if (FAC.sel) drawer(); }
      }).catch(function () { });
    }).catch(function () {
      FAC.busy = false;
      var meta = document.getElementById('factory-meta');
      if (meta) meta.textContent = 'API 断开（面板 API 未启动?）';
    });
  }

  /* 生产漏斗总览条（v2）：收货→过审→已翻译→考生→双窗及格，全部 ledger 实时值（禁硬编码防漂移）；
   * 尾部附施工状态统计（图节点现算 4 built/4 partial/7 pending 式）——台账未达时降级显原因 */
  function updateKpi() {
    var box = document.getElementById('factory-funnel');
    if (!box) return;
    var lg = FAC.ledger;
    if (!lg || lg.ok === false) {
      box.textContent = lg && lg.reason ? '台账不可达：' + lg.reason : '台账加载中…';
    } else {
      function bd(nid, verdict) {
        var ns = lg.nodes && lg.nodes[nid];
        if (!ns) return 0;
        var hit = (ns.breakdown || []).filter(function (b) { return b.verdict === verdict; })[0];
        return hit ? hit.rows : 0;
      }
      var intake = (lg.nodes && lg.nodes['FAC-E1A'] && lg.nodes['FAC-E1A'].total) || 0;
      var passed = bd('FAC-E1A', 'screened_in'), translated = bd('FAC-E3', 'translated_c4');
      var tested = lg.bothwin ? lg.bothwin.tested : 0, win = lg.bothwin ? lg.bothwin.passed : 0;
      function chip(n, label, pct, cls) {
        return '<span class="fn' + (cls ? ' ' + cls : '') + '" title="' + label + '"><b>' + n + '</b><i>' + label +
          (pct != null ? ' · ' + pct + '%' : '') + '</i></span>';
      }
      box.innerHTML =
        chip(intake, '收货') + '<span class="fn-arrow">→</span>' +
        chip(passed, '过审', intake ? Math.round(passed / intake * 100) : null, 'hot') + '<span class="fn-arrow">→</span>' +
        chip(translated, '已翻译') + '<span class="fn-arrow">→</span>' +
        chip(tested, 'OOS考生') + '<span class="fn-arrow">→</span>' +
        chip(win, '双窗及格', tested ? Math.round(win / tested * 100) : null, 'win');
    }
    var bs = document.getElementById('factory-buildstat');
    if (bs && FAC.data) {
      var c = { built: 0, partial: 0, pending: 0 };
      FAC.data.nodes.forEach(function (n) { c[n.build_status] = (c[n.build_status] || 0) + 1; });
      bs.textContent = '施工 ' + (c.built || 0) + ' 已建 · ' + (c.partial || 0) + ' 部分 · ' + (c.pending || 0) + ' 未建';
    }
  }

  function render() {
    var d = FAC.data; if (!d) return;
    var host = document.getElementById('factory-tree');
    var svg = document.getElementById('factory-wire');
    var canvas = document.querySelector('.factory-canvas');
    if (!host || !svg || !canvas) return;
    var byId = {};
    d.nodes.forEach(function (n) { byId[n.id] = n; });
    var edges = normEdges(d);
    /* 车道挂载=父子链（E1→E1A..E1E）：车道节点 parent=喂给它的 stage 节点——聚焦血统走父子链 */
    var kids = {}, parent = {};
    edges.forEach(function (e) {
      var t = byId[e.to_node];
      if (t && t.node_type === 'lane' && byId[e.from_node] && byId[e.from_node].node_type === 'stage') {
        parent[t.id] = e.from_node;
        (kids[e.from_node] = kids[e.from_node] || []).push(t);
      }
    });
    /* 主链环节按 stage 序排（E0..E9）；全部 stage 节点都属唯一流根「策略工厂」 */
    var stages = d.nodes.filter(function (n) { return n.node_type === 'stage'; })
      .sort(function (a, b) { return String(a.stage).localeCompare(String(b.stage)); });

    /* ── 聚焦模式血统计算（照抄 tdm）：主链+车道挂载多跳贯通（上游的上游/下游的下游走到底）；
     * 反馈环只算直连一跳（E9→E2→…→E6→E1 成环，反馈环也多跳必吞全图）。上游居左/下游居右按更近
     * 一侧归位，平局归上游；真源节点消失（数据刷新后 focus 失效）→ 自动退出聚焦 */
    var F = null;
    if (FAC.focus) {
      if (!byId[FAC.focus]) { FAC.focus = null; FAC.focusFit = null; }
      else {
        var walk = function (dir) {
          var dist = {}; dist[FAC.focus] = 0; var q = [FAC.focus];
          while (q.length) {
            var cur = q.shift(), dc = dist[cur];
            edges.forEach(function (e) {
              if (e.edge_type === 'feedback') return;   /* 反馈环不参与多跳（防环吞全图） */
              var a = dir === 'up' ? e.to_node : e.from_node;
              var b = dir === 'up' ? e.from_node : e.to_node;
              if (a === cur && byId[b] && !(b in dist)) { dist[b] = dc + 1; q.push(b); }
            });
            if (dir === 'up') {
              var p = parent[cur];
              if (p && byId[p] && !(p in dist)) { dist[p] = dc + 1; q.push(p); }
            } else (kids[cur] || []).forEach(function (c) {
              if (!(c.id in dist)) { dist[c.id] = dc + 1; q.push(c.id); }
            });
          }
          delete dist[FAC.focus];
          return dist;
        };
        var upD = walk('up'), downD = walk('down');
        /* 反馈环直连一跳：直接喂它的/它直接喂的保持贴身可见 */
        edges.forEach(function (e) {
          if (e.edge_type !== 'feedback') return;
          if (e.to_node === FAC.focus && byId[e.from_node] && (!(e.from_node in upD) || upD[e.from_node] > 1)) upD[e.from_node] = 1;
          if (e.from_node === FAC.focus && byId[e.to_node] && (!(e.to_node in downD) || downD[e.to_node] > 1)) downD[e.to_node] = 1;
        });
        var fset = {}; fset[FAC.focus] = { side: 'self', dist: 0 };
        Object.keys(upD).forEach(function (id) {
          fset[id] = { side: (downD[id] != null && downD[id] < upD[id]) ? 'down' : 'up',
            dist: Math.min(upD[id], downD[id] != null ? downD[id] : Infinity) };
        });
        Object.keys(downD).forEach(function (id) { if (!fset[id]) fset[id] = { side: 'down', dist: downD[id] }; });
        F = { id: FAC.focus, set: fset };
      }
    }
    function inF(el) { return !!F && !!F.set[el.dataset.id]; }

    host.innerHTML = '';
    var wires = [];
    var elById = {};        /* 节点 id → 卡片元素（边连线用） */
    var drawnPairs = {};    /* 已画连线 pair key（车道挂载先画，同对边去重） */
    /* 横向流水线布局：流根标签列(8~LABEL_W) + E0..E9 十列均分剩余宽度——环节永远同列同排，
     * 车道挂 E1 正下方纵列；每次渲染实时量容器，窗口/抽屉变化由 ResizeObserver 触发重渲 */
    var W = canvas.clientWidth || 1400;
    var LABEL_W = 160, GAP = 16;
    var colW = Math.max(150, Math.floor((W - LABEL_W - 16 - GAP * 9) / 10));
    var COLX = [];
    for (var ci = 0; ci < 10; ci++) COLX.push(LABEL_W + ci * (colW + GAP));

    function card(n, cx, cy, kind) {
      var el = document.createElement('div');
      var fd = (F && !F.set[n.id]) ? ' fdim' : '';   /* 聚焦模式：血统主线外压暗（只动透明度，色语义不动） */
      el.className = 'tn ' + kind + ' ' + cls(n) + fd + (n.id === FAC.sel ? ' sel' : '');
      el.style.left = cx + 'px'; el.style.top = cy + 'px'; el.style.width = colW + 'px';
      /* 小字=台账成绩（strategy_screen 实时）+「问」两行钳制；无台账=施工状态文字留位 */
      var st = statLine(n);
      el.innerHTML =
        '<div class="tn-n">' + (n.name || n.id) + '</div>' +
        (st ? '<div class="tn-s">' + st + '</div>' : '') +
        '<div class="tn-g">' + (n.q || '（问待补）') + '</div>';
      el.title = n.id + ' · ' + (BUILD_ZH[n.build_status] || n.build_status || '');
      el.onclick = function () { if (FAC.dragDist > 3) return; FAC.sel = n.id; FAC.focus = n.id; render(); drawer(); };   /* 拖动平移后松手不算点击；点选即聚焦血统 */
      el.dataset.id = n.id;
      host.appendChild(el);
      elById[n.id] = el;
      return el;
    }
    /* 节点成绩行：节点级台账统计前两桶（如「37 已翻译 · 321 挂起」）；未接管台账行的环节显施工状态 */
    function statLine(n) {
      var ns = FAC.ledger && FAC.ledger.nodes && FAC.ledger.nodes[n.id];
      if (ns && ns.breakdown && ns.breakdown.length) {
        return ns.breakdown.slice(0, 2).map(function (b) {
          return b.rows + ' ' + (VERDICT_ZH[b.verdict] || b.verdict);
        }).join(' · ');
      }
      return BUILD_ZH[n.build_status] || '';
    }
    /* 连线样式：主链/车道挂载=实线；反馈环=虚线橙——wire(a,b,dashed,wtype)；
     * 第 4 元=聚焦相关性（聚焦模式下两端都在血统内的边才保亮度，其余压暗） */
    function wire(a, b, dashed, wtype) {
      wires.push([a, b, !!dashed, wtype || 'sequence', !F || (inF(a) && inF(b))]);
    }

    /* 流根标签：唯一根「策略工厂」——树的根部视觉锚点（聚焦模式不画，同 tdm） */
    var rowY = 90;
    if (!F) {
      var fel = document.createElement('div');
      fel.className = 'tg';
      fel.style.left = '8px'; fel.style.top = (rowY + 14) + 'px';
      fel.innerHTML = (d.nickname || d.name_zh || '策略工厂') + ' <span class="cnt">' + stages.length + '</span>';
      host.appendChild(fel);
    }

    /* 主链：十环节一行贯通（列=stage 序）；车道：挂 E1 正下方纵列（连线=父子链实线） */
    var laneParent = null, laneColX = 0;
    stages.forEach(function (n, i) {
      var el = card(n, COLX[Math.min(i, 9)], rowY, 'tn-stage');
      if (n.id === 'FAC-E1') { laneParent = el; laneColX = COLX[Math.min(i, 9)]; }
    });
    var rowBottom = rowY;
    stages.forEach(function (n) {
      var el = elById[n.id];
      rowBottom = Math.max(rowBottom, el.offsetTop + el.offsetHeight);
    });
    var laneY = rowBottom + 64;   /* 反馈环弧线带（链排下方）与车道排之间留带 */
    (kids['FAC-E1'] || []).forEach(function (c) {
      var el = card(c, laneColX, laneY, 'tn-lane');
      wire(laneParent, el, false, 'sequence');
      drawnPairs[laneParent.dataset.id + '>' + c.id] = 1;
      laneY += el.offsetHeight + 12;
    });

    /* ── 聚焦重排（照抄 tdm）：主线拉成一条水平带——选中节点原地不动为锚，上游按血统距离向左、
     * 下游向右各退一列；同列多节点绕选中节点垂直居中堆叠；无关节点整块下移让路+压暗；
     * 主带越出左界时全图右移夹回 */
    if (F) {
      var selEl = elById[F.id];
      var anchorX = selEl.offsetLeft;
      var anchorCY = selEl.offsetTop + selEl.offsetHeight / 2;
      var cols = {};
      Object.keys(F.set).forEach(function (id) {
        var it = F.set[id];
        if (it.side === 'self') return;
        var col = it.side === 'up' ? -it.dist : it.dist;
        (cols[col] = cols[col] || []).push(elById[id]);
      });
      var step = colW + GAP;
      Object.keys(cols).forEach(function (c) {
        var els = cols[c].sort(function (a, b) { return a.offsetTop - b.offsetTop; });
        var hs = els.map(function (el) { return el.offsetHeight; });
        var total = hs.reduce(function (s, h) { return s + h; }, 0) + 10 * (els.length - 1);
        var cy = anchorCY - total / 2;
        els.forEach(function (el, i) {
          el.style.left = (anchorX + c * step) + 'px';
          el.style.top = cy + 'px';
          cy += hs[i] + 10;
        });
      });
      var minX = Infinity, bandBottom = 0;
      Object.keys(F.set).forEach(function (id) {
        var el = elById[id];
        minX = Math.min(minX, el.offsetLeft);
        bandBottom = Math.max(bandBottom, el.offsetTop + el.offsetHeight);
      });
      var dx = Math.max(0, 8 - minX);
      var minY = Infinity;
      Object.keys(elById).forEach(function (id) {
        if (F.set[id]) return;
        minY = Math.min(minY, elById[id].offsetTop);
      });
      var dy = Math.max(0, bandBottom + 70 - minY);
      Object.keys(elById).forEach(function (id) {
        var el = elById[id];
        el.style.left = (el.offsetLeft + dx) + 'px';
        if (!F.set[id] && dy) el.style.top = (el.offsetTop + dy) + 'px';
      });
    }

    /* 全量边连线：主链（车道挂载已画过的对跳过）+反馈环——全景态枝丫完整（同 tdm 全量边策略） */
    edges.forEach(function (e) {
      var a = elById[e.from_node], b = elById[e.to_node];
      if (!a || !b) return;
      var key = e.from_node + '>' + e.to_node;
      if (drawnPairs[key]) return;
      drawnPairs[key] = 1;
      wire(a, b, e.edge_type === 'feedback', e.edge_type);
    });

    /* 世界层与树的尺寸用卡片实测包围盒算（卡片全绝对定位不撑宽——量 host.offsetWidth 恒塌，
     * SVG 视口跟着塌 → 连线全画到可视区外（tdm b20260908-02 连线消失根因，照抄规避）） */
    var contentW = 0, contentH = 0;
    Object.keys(elById).forEach(function (id) {
      var el = elById[id];
      contentW = Math.max(contentW, el.offsetLeft + el.offsetWidth);
      contentH = Math.max(contentH, el.offsetTop + el.offsetHeight);
    });
    if (!F) {   /* 全景态把流根标签也包进包围盒 */
      var tg = host.querySelector('.tg');
      if (tg) contentW = Math.max(contentW, tg.offsetLeft + tg.offsetWidth);
    }
    contentW += 4; contentH += 6;
    host.style.width = contentW + 'px';
    host.style.height = contentH + 'px';   /* 绝对定位子元素不撑高父容器——显式写内容高度 */
    var w = worldEl();
    if (w) {
      w.style.width = Math.max(contentW, canvas.clientWidth) + 'px';
      w.style.height = Math.max(contentH, canvas.clientHeight || 600) + 'px';
    }

    /* 聚焦镜头自动适配（照抄 tdm）：主带收进可视区——仅聚焦目标切换时执行，轮询重绘不重拟合 */
    if (F && FAC.focusFit !== F.id) {
      var bL = Infinity, bT = Infinity, bR = 0, bB = 0;
      Object.keys(F.set).forEach(function (id) {
        var el = elById[id];
        bL = Math.min(bL, el.offsetLeft); bT = Math.min(bT, el.offsetTop);
        bR = Math.max(bR, el.offsetLeft + el.offsetWidth);
        bB = Math.max(bB, el.offsetTop + el.offsetHeight);
      });
      var cw = canvas.clientWidth || 1400, chh = canvas.clientHeight || 600, pad = 70;
      var fz = Math.max(0.2, Math.min(1, (cw - pad * 2) / Math.max(1, bR - bL), (chh - pad * 2) / Math.max(1, bB - bT)));
      view.z = fz;
      view.x = cw / 2 - ((bL + bR) / 2) * fz;
      view.y = chh / 2 - ((bT + bB) / 2) * fz;
      applyView();
      FAC.focusFit = F.id;
    }
    /* 工具栏聚焦指示 pill：聚焦中显示节点名+✕（点击退出），退出后隐藏 */
    var fp = document.getElementById('factory-focus');
    if (fp) {
      fp.style.display = F ? 'inline-block' : 'none';
      if (F) { var fn = document.getElementById('factory-focus-name'); if (fn) fn.textContent = byId[F.id].name || F.id; }
    }

    /* 连线绘制：同步执行——样式写入后读 offsetLeft 会强制浏览器同步排版，坐标本就准确；
     * 套 requestAnimationFrame 在嵌入环境（app:// 窗口遮挡/渲染器节流）rAF 可能永不触发
     * → 连线整幅空白且无任何报错（tdm 2026-09-09 实测坑，照抄同步画根除） */
    (function () {
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
        var color = '#2c3a52';
        if (p[3] === 'feedback') {   /* 反馈环：暗橙虚线，绕链排下方弧线（S 形穿卡难读） */
          color = '#9a5a1a';
          ay = a.offsetTop + a.offsetHeight;
          by = b.offsetTop + b.offsetHeight;
          var dip = Math.max(ay, by) + 46;
          var mx = (ax + bx) / 2;
          return '<path d="M' + ax + ',' + ay + ' C' + mx + ',' + dip + ' ' + mx + ',' + dip + ' ' + bx + ',' + by + '"' +
            ' stroke-dasharray="5 4" stroke="' + color + '"' +
            (p[4] ? '' : ' stroke-opacity="0.08"') + '/>';
        }
        var mx = (ax + bx) / 2;
        return '<path d="M' + ax + ',' + ay + ' C' + mx + ',' + ay + ' ' + mx + ',' + by + ' ' + bx + ',' + by + '"' +
          (p[4] ? '' : ' stroke-opacity="0.08"') + '/>';
      }).join('');
    })();
  }

  /* 窗口缩放/最大化、抽屉开合 → 容器尺寸变了就整图重排（同 tdm） */
  var roTimer = null;
  var ro = new ResizeObserver(function () {
    if (!FAC.data || !visible()) return;
    if (roTimer) clearTimeout(roTimer);
    roTimer = setTimeout(render, 120);
  });

  /* 抽屉 v2（照抄 tdm 分区契约）：标题徽标 → 问 → 机制 → 治理键值网格 → 模块锚 →
   * 台账成绩（async /api/factory/ledger）→ 依据锚 chip 流 → 上/下游节点导航行（点击跳选）→ 设计备注 */
  function drawer() {
    var box = document.getElementById('factory-drawer');
    if (!box) return;
    var n = FAC.data && FAC.sel && FAC.data.nodes.find(function (x) { return x.id === FAC.sel; });
    if (!n) { box.style.display = 'none'; return; }
    function esc(s) {   /* 真源 YAML 文本进 innerHTML——防标签断裂/注入（DDT 铁律） */
      return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
      });
    }
    var RN = FAC.data.ref_names || {};   /* 引用 id → 中文名（注册表翻译真源，API 注入，零硬编码） */
    function zh(id) { return RN[id] ? id + ' ' + RN[id] : id; }
    var byIdMap = {};
    FAC.data.nodes.forEach(function (x) { byIdMap[x.id] = x; });
    /* 上下游连线（谁喂它 / 它喂谁）——全量边按当前节点过滤，带边型 glyph 溯源闭环 */
    var ups = [], downs = [];
    normEdges(FAC.data).forEach(function (e) {
      if (e.from_node === n.id && byIdMap[e.to_node]) downs.push({ x: byIdMap[e.to_node], t: e.edge_type });
      if (e.to_node === n.id && byIdMap[e.from_node]) ups.push({ x: byIdMap[e.from_node], t: e.edge_type });
    });
    /* 状态徽标=画布卡片同语义同色号（DDT 铁律）：蓝已建 / 绿部分建成 / 橙虚未建 */
    var stBdg = '<span class="bdg ' + (n.build_status === 'built' ? 'bdg-prod'
      : n.build_status === 'partial' ? 'bdg-partial' : 'bdg-design') + '">' +
      esc(BUILD_ZH[n.build_status] || n.build_status || '设计态') + '</span>';
    var meta = '环节 ' + (n.stage || '—') + ' ｜ ' + (n.node_type === 'lane' ? '车道 ' + (n.lane || '—') : '主链') +
      ' ｜ 算力 ' + (n.compute_class || '—');
    /* 引用 chip：编号+中文名；hover title 全称 */
    function chip(id) {
      var nm = RN[id] || '';
      return '<span class="chip" title="' + esc(zh(id)) + '"><i>' + esc(id) + '</i>' +
        (nm ? '<b>' + esc(nm) + '</b>' : '') + '</span>';
    }
    /* 节点导航行：状态点+名称+边型+id，点击跳选（抽屉内闭环，不动画布交互） */
    var GLYPH = { sequence: '→', feed: '⇢', broadcast: '⇉', feedback: '↩' };
    function nlink(x, t) {
      var dot = x.build_status === 'built' ? 'prod' : (x.build_status === 'partial' ? 'partial' : 'design');
      return '<div class="nl" data-jump="' + esc(x.id) + '" title="' + esc(x.id) + '">' +
        '<span class="dot dot-' + dot + '"></span><span class="nl-n">' + esc(x.name || x.id) + '</span>' +
        (t ? '<span class="nl-t">' + (GLYPH[t] || '·') + ' ' + esc(t) + '</span>' : '') +
        '<span class="nl-i">' + esc(x.id) + '</span></div>';
    }
    function kv(k, v) {
      return '<span class="k">' + k + '</span><span class="v' + (v ? '' : ' na') + '">' + (v ? esc(v) : '—') + '</span>';
    }
    /* 治理四键网格（键位适配工厂字段，结构同 tdm）：空值显式 '—' 留位不塌行 */
    var gov = '<div class="kgrid">' + kv('环节', n.stage) + kv('车道', n.node_type === 'lane' ? (n.lane || '—') : '') +
      kv('算力', n.compute_class) + kv('施工', BUILD_ZH[n.build_status] || n.build_status) + '</div>';
    var mod = n.module_ref
      ? '<div class="chips">' + chip(String(n.module_ref).split('..')[0]) + (String(n.module_ref).indexOf('..') >= 0 ? '<span class="chip"><i>' + esc(n.module_ref) + '</i></span>' : '') + '</div>' +
        '<div class="code-anchor">代码锚：<a class="mod-copy" href="javascript:void(0)" data-copy="' +
        esc(n.module_ref) + '" title="点击复制路径：' + esc(n.module_ref) + '">' +
        esc(String(n.module_ref).split('/').pop()) + '</a></div>'
      : '<div class="empty">未落码——设计态（施工后 module_ref 自动亮起）</div>';
    /* 依据锚两轴：数据源 + 设计出处（design_refs 是「名称 URL」长串——cm 卡片化，禁 chip 截断丢信息） */
    var refsHtml = '';
    if (n.data_refs && n.data_refs.length)
      refsHtml += '<div class="axis"><div class="axis-h"><b>数据源</b> <span class="cnt">' + n.data_refs.length + '</span></div>' +
        '<div class="chips">' + n.data_refs.map(chip).join('') + '</div></div>';
    if (n.design_refs && n.design_refs.length)
      refsHtml += '<div class="axis"><div class="axis-h"><b>设计出处</b> <span class="cnt">' + n.design_refs.length + '</span></div>' +
        n.design_refs.map(function (r) { return '<div class="cm">' + esc(r) + '</div>'; }).join('') + '</div>';
    /* 仓储（store_refs 三要素：artifact/location/key/retention）——键值行卡片化 */
    var storeHtml = (n.store_refs && n.store_refs.length)
      ? n.store_refs.map(function (s) {
        var a = (s && typeof s === 'object') ? s : { artifact: String(s) };
        return '<div class="cm"><b style="color:#c6cdd8">' + esc(a.artifact || '—') + '</b> → ' +
          esc(a.location || '待定') + ' · key=' + esc(a.key || '—') + ' · 保留 ' + esc(a.retention || '—') + '</div>';
      }).join('')
      : '<div class="empty">（无仓储声明——pending 节点施工时定）</div>';
    /* 设计备注：反馈环成员资格（真源 feedback_loops note）——工厂图无散注释，环即备注 */
    var cms = (FAC.data.feedback_loops || []).filter(function (f) {
      return f.from === n.id || f.to === n.id;
    }).map(function (f) {
      return '<div class="cm">' + (f.from === n.id ? '↩ 反馈出去 → ' + esc(f.to) : '↩ 收到反馈 ← ' + esc(f.from)) +
        '：' + esc(f.note || '') + '</div>';
    }).join('') || '<div class="empty">（无）</div>';
    /* 台账成绩助手：节点级 breakdown + E4 双窗及格名单；降级/未接管显式留位（空态范式） */
    function ledgerHtml(lg) {
      if (!lg) return '<div class="empty">查询中…</div>';
      if (lg.ok === false) return '<div class="empty">' + esc(lg.reason || '台账不可达') + '</div>';
      var ns = lg.nodes && lg.nodes[n.id];
      var html = '';
      if (ns && ns.breakdown && ns.breakdown.length) {
        html += ns.breakdown.map(function (b) {
          return '<div class="cm"><b style="color:#c6cdd8">' + esc(VERDICT_ZH[b.verdict] || b.verdict) +
            '</b> · ' + b.rows + ' 行' +
            (b.sharpe_max != null ? ' · 最高 IS Sharpe ' + Number(b.sharpe_max).toFixed(2) : '') + '</div>';
        }).join('') + '<div class="axis-h" style="margin-top:5px">合计 ' + ns.total + ' 行（台账只增，判定书可溯）</div>';
      } else {
        html += '<div class="empty">该环节尚未接管台账行——施工接通 strategy_screen 后自动亮起</div>';
      }
      /* 理由码分布（v2）：E1A 筛出理由/E3 挂起失效理由——API 节点级 reasons，比例条一眼看主死因 */
      if (ns && ns.reasons && ns.reasons.length) {
        var mx = ns.reasons[0].rows || 1;
        html += '<div class="axis-h" style="margin-top:9px"><b>理由码分布</b>（' +
          (n.id === 'FAC-E1A' ? '筛出/击杀' : '挂起/失效') + '主因 Top ' + ns.reasons.length + '）</div>';
        html += ns.reasons.map(function (r) {
          return '<div class="rs"><span class="rs-n" title="' + esc(r.reason) + '">' + esc(r.reason) + '</span>' +
            '<span class="rs-b"><i style="width:' + Math.max(4, Math.round(r.rows / mx * 100)) + '%"></i></span>' +
            '<span class="rs-c">' + r.rows + '</span></div>';
        }).join('');
      }
      /* 双窗及格名单（全厂唯一判定权的产出物）：挂 E4 考试咽喉，其余环节不重复展示 */
      if (n.id === 'FAC-E4' && lg.bothwin) {
        var bw = lg.bothwin;
        html += '<div class="axis-h" style="margin-top:9px"><b>双窗及格线</b>（' + esc(bw.gate || '') + '）：考生 ' +
          bw.tested + ' · 及格 <b style="color:#7fc98a">' + bw.passed + '</b></div>';
        html += (bw.items || []).map(function (it) {
          return '<div class="cm"><b style="color:#c6cdd8">' + esc(it.strategy_id) + '</b> · IS ' +
            Number(it.is_sharpe || 0).toFixed(2) + ' → ' +
            (it.segments || []).map(function (s) {
              return esc((s.batch || '').replace(/^C4-/, '').replace(/-\d{8}$/, '') + ' ' + Number(s.sharpe || 0).toFixed(2));
            }).join(' → ') + '</div>';
        }).join('') || '<div class="empty">暂无双窗及格者（IS 排名不作数——两窗口两体制，OOS 说了算）</div>';
      }
      return html;
    }
    /* 三高候选榜助手（v3，E1D 消费端）：真源=data/strategy_intake/three_high_candidates.csv（MOD-BT-090 产出）。
     * 最新批 Top 榜：排名+环节+三高旗徽章+合成 z+四支柱 z chip+确定性假说全文；空态显 hint 不冒充失败 */
    function thHtml(th) {
      if (!th) return '<div class="empty">查询中…</div>';
      if (th.ok === false) return '<div class="empty">' + esc(th.reason || '查询失败') + '</div>';
      if (!th.batches || !th.batches.length) return '<div class="empty">' + esc(th.hint || '暂无产出') + '</div>';
      var b = th.batches[0];
      var html = '<div class="axis-h"><b>最新批</b> ' + esc(b.batch) + ' · ' + b.count + ' 候选' +
        (th.batches.length > 1 ? ' ｜ 历史 ' + th.batches.length + ' 批/共 ' + th.total_rows + ' 行' : '') + '</div>';
      html += b.items.map(function (it, i) {
        var flags = (it.three_high_flags || '').split('+').filter(Boolean);
        var pillars = [['增长', it.growth_z], ['壁垒', it.barrier_z], ['利润', it.margin_z], ['咽喉', it.choke_z]];
        return '<div class="cm"><b style="color:#c6cdd8">#' + (i + 1) + ' ' + esc(it.sector) + '</b> · 成员 ' +
          (it.members != null ? Math.round(it.members) : '—') + ' 只 · 合成 z <b style="color:#7db4e8">' +
          Number(it.total_z || 0).toFixed(2) + '</b> ' +
          (flags.length ? '<span class="bdg bdg-partial">' + flags.map(esc).join('+') + '</span>' : '<span class="bdg bdg-gray">未过旗线</span>') +
          '<div style="margin-top:5px;display:flex;gap:5px;flex-wrap:wrap">' +
          pillars.map(function (p) {
            return '<span class="chip"><i>' + p[0] + '</i><b>' + (p[1] == null ? '—' : (p[1] >= 0 ? '+' : '') + Number(p[1]).toFixed(2) + 'σ') + '</b></span>';
          }).join('') + '</div>' +
          (it.hypothesis_zh ? '<div style="margin-top:5px">' + esc(it.hypothesis_zh) + '</div>' : '') +
          '</div>';
      }).join('');
      return html;
    }
    var scroll = box.scrollTop;   /* 30s 轮询重绘保持阅读位置（DDT 实证坑） */
    box.style.display = 'block';
    box.innerHTML =
      '<div class="dr-name">' + esc(n.name || n.id) + '</div>' +
      '<div class="dr-id">' + esc(n.id) + ' · ' + esc(meta) + '</div>' +
      '<div class="dr-badges">' + stBdg + '</div>' +
      '<div class="dr-par">主链上游：' + (ups.length ? esc(ups[0].x.name) + '（' + esc(ups[0].x.id) + '）' : '—') +
      ' ｜ 下游：' + (downs.length ? downs.map(function (x) { return esc(x.x.name); }).join('、') : '—') + '</div>' +
      '<div class="sec">问</div><div class="txt q">' + (n.q ? esc(n.q) : '—') + '</div>' +
      '<div class="sec">机制（怎么算）</div><div class="txt">' + (n.note ? esc(n.note) : '（待补）') + '</div>' +
      '<div class="sec">治理</div>' + gov +
      '<div class="sec">模块锚（MOD）</div>' + mod +
      '<div class="sec">台账成绩（strategy_screen）<span class="cnt" id="factory-led-cnt"></span></div>' +
      '<div id="factory-led">' + ledgerHtml(FAC.ledger) + '</div>' +
      (n.id === 'FAC-E1D' ? '<div class="sec">三高候选榜（E1D 产出）<span class="cnt" id="factory-th-cnt"></span></div>' +
        '<div id="factory-th">' + thHtml(FAC.th) + '</div>' : '') +
      (refsHtml ? '<div class="sec">依据锚（引用）</div>' + refsHtml : '') +
      '<div class="sec">仓储（store_refs）</div>' + storeHtml +
      '<div class="sec">上游（谁喂给它）<span class="cnt">' + ups.length + '</span></div>' +
      (ups.length ? ups.map(function (u) { return nlink(u.x, u.t); }).join('') : '<div class="empty">—</div>') +
      '<div class="sec">下游（它喂给谁）<span class="cnt">' + downs.length + '</span></div>' +
      (downs.length ? downs.map(function (u) { return nlink(u.x, u.t); }).join('') : '<div class="empty">—</div>') +
      '<div class="sec">设计备注（反馈环/裁定）</div>' + cms;
    box.scrollTop = scroll;
    /* 上/下游导航行点击跳选——drawer 内闭环（同 tdm） */
    box.querySelectorAll('[data-jump]').forEach(function (el) {
      el.addEventListener('click', function () {
        FAC.sel = el.getAttribute('data-jump');
        FAC.focus = FAC.sel;   /* 跳选=换焦点：行为与画布点选一致，血统主线跟着换 */
        render();
        drawer();
      });
    });
    /* 代码锚点击=复制源码路径（app:// 下 file:// 链接被 Chromium 拦，复制路径全环境可用，同 tdm） */
    box.querySelectorAll('.mod-copy').forEach(function (el) {
      el.addEventListener('click', function (ev) {
        ev.preventDefault();
        var path = el.getAttribute('data-copy');
        var done = function () {
          var old = el.textContent;
          el.textContent = '已复制路径 ✓';
          setTimeout(function () { el.textContent = old; }, 1200);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(path).then(done, function () { });
        } else {
          var ta = document.createElement('textarea');
          ta.value = path; document.body.appendChild(ta); ta.select();
          try { document.execCommand('copy'); done(); } catch (e) { }
          document.body.removeChild(ta);
        }
      });
    });
    /* 台账成绩：异步刷新（TTL 缓存端点，快）——已切节点/抽屉已重绘时丢弃过期响应（同 tdm 验证档案套路） */
    var ledNode = n.id;
    var ledBox = box.querySelector('#factory-led');
    fetch(API_BASE + '/api/factory/ledger')
      .then(function (r) { return r.json(); })
      .then(function (lg) {
        if (FAC.sel !== ledNode || !ledBox || !ledBox.isConnected) return;
        FAC.ledger = lg;
        var vs = box.scrollTop;
        ledBox.innerHTML = ledgerHtml(lg);
        var lc = box.querySelector('#factory-led-cnt');
        if (lc) lc.textContent = (lg.global && lg.global.total != null) ? '共 ' + lg.global.total + ' 行' : '';
        box.scrollTop = vs;
      })
      .catch(function () {
        if (FAC.sel !== ledNode || !ledBox || !ledBox.isConnected) return;
        ledBox.innerHTML = '<div class="empty">台账不可达（面板 API 未启动?）</div>';
      });
    /* 三高候选榜（仅 E1D 抽屉）：异步拉产出台账——过期响应丢弃同套路 */
    if (n.id === 'FAC-E1D') {
      var thBox = box.querySelector('#factory-th');
      fetch(API_BASE + '/api/factory/threehigh')
        .then(function (r) { return r.json(); })
        .then(function (th) {
          if (FAC.sel !== ledNode || !thBox || !thBox.isConnected) return;
          FAC.th = th;
          var vs = box.scrollTop;
          thBox.innerHTML = thHtml(th);
          var tc = box.querySelector('#factory-th-cnt');
          if (tc) tc.textContent = (th.batches && th.batches.length) ? String(th.batches[0].count) : '';
          box.scrollTop = vs;
        })
        .catch(function () {
          if (FAC.sel !== ledNode || !thBox || !thBox.isConnected) return;
          thBox.innerHTML = '<div class="empty">查询失败（面板 API 未启动?）</div>';
        });
    }
  }

  window.factoryFilter = function (q) {
    q = (q || '').trim().toLowerCase();
    var byId = {};
    (FAC.data ? FAC.data.nodes : []).forEach(function (n) { byId[n.id] = n; });
    document.querySelectorAll('#factory-tree .tn').forEach(function (t) {
      var n = byId[t.dataset.id];
      var hit = !q || (n && ((n.id + ' ' + n.name).toLowerCase().indexOf(q) >= 0));
      t.classList.toggle('hit', !!q && !!hit);
      t.classList.toggle('dimmed', !!q && !hit);
    });
  };

  setInterval(function () { if (visible()) load(); }, 30000);
  /* 頁面切到 factory 时立即拉一次（go() 切 display，用事件捕获不到——轮询兜底+首次延迟，同 tdm） */
  setTimeout(load, 1200);
  var facCanvas = document.querySelector('.factory-canvas');
  if (facCanvas) ro.observe(facCanvas);   /* 尺寸监听：最大化/还原/抽屉开合自动重排 */

  /* ── 画布交互挂接（规范=visualization_view_template.md §6.6，照抄 tdm 四项操作）── */
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
      FAC.dragDist = drag.dist;
      drag = null;
      var cc = canvasEl(); if (cc) cc.classList.remove('dragging');
      setTimeout(function () { FAC.dragDist = 0; }, 0);   /* click 事件派发后再清零 */
    });
    /* ③ 双击空白重置+退出聚焦（双击节点不算——节点双击是两次打开抽屉） */
    c.addEventListener('dblclick', function (e) {
      if (e.target && e.target.closest && e.target.closest('.tn, .tg')) return;
      exitFocus();
    });
    /* ④ Ctrl+Shift+D 切换 拖动/选择复制 模式；⑤ Esc 退出聚焦 */
    document.addEventListener('keydown', function (e) {
      if (e.ctrlKey && e.shiftKey && (e.key === 'D' || e.key === 'd')) {
        e.preventDefault();
        window.factoryToggleMode();
      }
      if (e.key === 'Escape' && FAC.focus) exitFocus();
    });
    setMode(true);   /* 初始同步按钮文案+徽标+光标 */
  })();
})();
