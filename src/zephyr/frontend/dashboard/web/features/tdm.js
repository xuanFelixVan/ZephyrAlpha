/* ── 交易决策全景（横向思维导图树）· 真源 /api/tdm（mtime 缓存）· 30s 轮询自动映射 ──
 * Owner 2026-09-07 裁定：MD 生成图不够直观，前端原生实时渲染；A股·研究栏 tdm.html 承载。
 * 布局：根流组(E建仓/P持仓/X离场/F组合/横切C) → 枝干节点(第二列) → 子节点(第三列)，
 *       DOM 卡片+SVG 贝塞尔连线；配色 production 蓝/design 橙虚/paper 绿（v1.8 语义）。
 * 激活检测：页面片段经 innerHTML 注入（script 不执行），本文件由 loader 显式加载；
 *           30s tick 时仅 p-tdm 可见才 fetch，页面隐藏零开销。
 * 抽屉 v2（b20260908-10）：右侧详情抽屉重设计——标题徽标区/治理键值网格/依据锚八轴 chip 流/
 *           上下游节点导航行（点击跳选）/长文行高≥1.6；纯 HTML+CSS，数据契约与画布交互不变。
 * 聚焦模式（b20260909-fe）：点节点自动重排血统主线——亮区=直连一跳+父子链全程（feed 多跳闭包
 *           实测吞全图，已裁定只保直连），上游居左/下游居右同水平带（列位=与选中节点距离），
 *           无关节点整块下移让路+压暗（只动透明度，三态色语义不变）；镜头自动适配主带（仅聚焦
 *           切换时，轮询重绘不打断手动平移缩放）；退出=Esc/双击空白/工具栏「🎯 聚焦 ✕」。 */
(function () {
  'use strict';
  var TDM = { data: null, sel: null, stamp: null, busy: false, dragDist: 0, verdicts: {}, focus: null, focusFit: null };
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

  /* 退出聚焦：回全景布局+视图复位（保留选中态与抽屉——聚焦是画布镜头，选中是抽屉上下文，两者解耦） */
  function exitFocus() {
    TDM.focus = null; TDM.focusFit = null;
    view.z = 1; view.x = 0; view.y = 0;
    render();
    applyView();
  }
  window.tdmExitFocus = exitFocus;   /* 工具栏「🎯 聚焦 ✕」onclick 入口 */

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
      /* 全节点验证态（PB-03）：画布噪音/衰减徽章数据源，失败降级无徽章不阻断地图 */
      fetch(API_BASE + '/api/tdm/verdicts').then(function (r) { return r.json(); }).then(function (vd) {
        if (vd && vd.ok) { TDM.verdicts = vd.verdicts || {}; render(); if (TDM.sel) drawer(); }
      }).catch(function () { });
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

    /* ── 聚焦模式血统计算（b20260909-fe）：亮区口径=直连一跳（feed/sequence/broadcast/feedback 全算）
     * + 父链祖先全程 + 子链后代全程 + 自己。实测裁定依据：feed 边 129 条构成致密网，多跳闭包
     * 会吞全图（125 节点全达，335 计数）；只保直连与树骨架后血统收敛到 3~21 节点，聚焦带可读。
     * 同节点双侧可达按更近一侧归位，距离平局归上游。真源节点消失→自动退出聚焦 */
    var F = null;
    if (TDM.focus) {
      if (!byId[TDM.focus]) { TDM.focus = null; TDM.focusFit = null; }
      else {
        var nb = function (id, dir) {
          var out = [];
          (d.edges || []).forEach(function (e) {
            if (dir === 'up' && e.to_node === id && byId[e.from_node]) out.push(e.from_node);
            if (dir === 'down' && e.from_node === id && byId[e.to_node]) out.push(e.to_node);
          });
          if (dir === 'up') { var p = byId[id].parent; if (p && byId[p]) out.push(p); }
          else (kids[id] || []).forEach(function (c) { out.push(c.id); });
          return out;
        };
        var upD = {}, downD = {};
        /* 树骨架全程：父链祖先（parent 树无环，dd 兜底防脏数据死循环）+ 子链后代 BFS */
        (function () {
          var cur = TDM.focus, dd = 0, p;
          while (dd < 50 && (p = byId[cur].parent) && byId[p]) {
            dd += 1;
            if (!(p in upD) || upD[p] > dd) upD[p] = dd;
            cur = p;
          }
        })();
        (function () {
          var q = [{ id: TDM.focus, d: 0 }];
          while (q.length) {
            var it = q.shift();
            (kids[it.id] || []).forEach(function (c) {
              var cid = c.id;   /* kids 值是节点对象——取 .id，直接用对象会键成 "[object Object]" 幽灵节点 */
              if (!(cid in downD)) { downD[cid] = it.d + 1; q.push({ id: cid, d: it.d + 1 }); }
            });
          }
        })();
        /* 直连一跳覆盖：直接关系优先于结构距离（直接喂它的父辈节点归位更近） */
        nb(TDM.focus, 'up').forEach(function (m) { if (m !== TDM.focus && (!(m in upD) || upD[m] > 1)) upD[m] = 1; });
        nb(TDM.focus, 'down').forEach(function (m) { if (m !== TDM.focus && (!(m in downD) || downD[m] > 1)) downD[m] = 1; });
        var fset = {}; fset[TDM.focus] = { side: 'self', dist: 0 };
        Object.keys(upD).forEach(function (id) {
          fset[id] = { side: (downD[id] != null && downD[id] < upD[id]) ? 'down' : 'up',
            dist: Math.min(upD[id], downD[id] != null ? downD[id] : Infinity) };
        });
        Object.keys(downD).forEach(function (id) { if (!fset[id]) fset[id] = { side: 'down', dist: downD[id] }; });
        F = { id: TDM.focus, set: fset };
      }
    }
    function inF(el) { return !!F && !!F.set[el.dataset.id]; }

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
      var vd = TDM.verdicts && TDM.verdicts[n.id];
      var vtag = '';
      var fd = (F && !F.set[n.id]) ? ' fdim' : '';   /* 聚焦模式：血统主线外压暗（只动透明度，色语义不动） */
      if (vd && (vd.verdict === 'noise' || vd.verdict === 'decaying')) {
        el.className = 'tn tn-d' + depth + ' ' + cls(n) + fd + ' v' + (vd.verdict === 'noise' ? 'n' : 'd') + (n.id === TDM.sel ? ' sel' : '');
        vtag = '<span class="tn-v">' + (vd.verdict === 'noise' ? '噪音' : '衰减') + '</span>';
      } else {
        el.className = 'tn tn-d' + depth + ' ' + cls(n) + fd + (n.id === TDM.sel ? ' sel' : '');
      }
      el.style.left = cx + 'px'; el.style.top = cy + 'px'; el.style.width = colW + 'px';
      /* 小字=「问」全文（不 slice 截断），CSS line-clamp 2：一排放不下自动提行成两行；标题保留 📄 前缀 */
      el.innerHTML = vtag +
        '<div class="tn-n">' + (n.autonomy === 'paper' ? '📄 ' : '') + (n.name || n.id) + '</div>' +
        '<div class="tn-g">' + (n.q || '（问待补）') + '</div>';
      el.title = n.id;
      el.onclick = function () { if (TDM.dragDist > 3) return; TDM.sel = n.id; TDM.focus = n.id; render(); drawer(); };   /* 拖动平移后松手不算点击；点选即聚焦血统 */
      el.dataset.id = n.id;
      host.appendChild(el);
      elById[n.id] = el;
      return el;
    }
    /* 连线样式：parent/sequence/broadcast=实线主链；feed/feedback=虚线喂给——wire(a,b,dashed,type)；
     * 第 5 元=聚焦相关性（聚焦模式下两端都在血统内的边才保亮度，其余压暗） */
    function wire(a, b, dashed, wtype) {
      wires.push([a, b, !!dashed, wtype || 'parent', !F || (inF(a) && inF(b))]);
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
      var fel = null;
      if (!F) {   /* 聚焦模式不画流根标签——画面只留血统主线，流归属由全景态承载 */
        fel = document.createElement('div');
        fel.className = 'tg';
        fel.style.left = '8px'; fel.style.top = (y + 20) + 'px';
        fel.innerHTML = g.info.zh + ' <span class="cnt">' + g.items.length + '</span>';
        host.appendChild(fel);
      }
      var fy = y;
      g.items.forEach(function (n) {
        var cb = place(n, 1, fy, fel);
        fy = cb + 26;
      });
      y = fy + 6;
    });

    /* ── 聚焦重排（b20260909-fe）：主线拉成一条水平带——选中节点原地不动为锚，上游按血统距离向左、
     * 下游向右各退一列（直接上游/下游贴身，越远越外）；同列多节点绕选中节点垂直居中堆叠（单节点
     * 列与选中节点严格同水平线）；无关节点整块下移让路+压暗；主带越出左界时全图右移夹回 */
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
    var contentW, contentH;
    if (F) {   /* 聚焦态尺寸用卡片实测包围盒（重排后列位不再符合 COLX 公式） */
      var mR = 0, mB = 0;
      Object.keys(elById).forEach(function (id) {
        var el = elById[id];
        mR = Math.max(mR, el.offsetLeft + el.offsetWidth);
        mB = Math.max(mB, el.offsetTop + el.offsetHeight);
      });
      contentW = mR + 4; contentH = mB + 6;
    } else {
      contentW = COLX[4] + colW + 4;
      contentH = y + 6;
    }
    host.style.width = contentW + 'px';
    host.style.height = contentH + 'px';   /* 绝对定位子元素不撑高父容器——显式写内容高度 */
    var w = worldEl();
    if (w) {
      w.style.width = Math.max(contentW, canvas.clientWidth) + 'px';
      w.style.height = Math.max(contentH, canvas.clientHeight || 600) + 'px';
    }

    /* 聚焦镜头自动适配：主带收进可视区（上游在视野左、下游在视野右）——仅聚焦目标切换时执行，
     * 30s 轮询重绘不重拟合，不打断用户手动平移缩放 */
    if (F && TDM.focusFit !== F.id) {
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
      TDM.focusFit = F.id;
    }
    /* 工具栏聚焦指示 pill：聚焦中显示节点名+✕（点击退出），退出后隐藏 */
    var fp = document.getElementById('tdm-focus');
    if (fp) {
      fp.style.display = F ? 'inline-block' : 'none';
      if (F) { var fn = document.getElementById('tdm-focus-name'); if (fn) fn.textContent = byId[F.id].name || F.id; }
    }

    /* 连线绘制：同步执行——样式写入后读 offsetLeft 会强制浏览器同步排版，坐标本就准确；
     * 原实现套 requestAnimationFrame，在嵌入环境（app:// 窗口遮挡/渲染器节流）rAF 可能永不触发
     * → 连线整幅空白且无任何报错（2026-09-09 聚焦模式施工实测抓到），同步画根除该脆弱性 */
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
        var mx = (ax + bx) / 2;
        var color = '#2c3a52';
        if (p[3] === 'feedback') color = '#9a5a1a';          /* 反馈边：暗橙 */
        else if (p[3] === 'feed') color = '#44546e';          /* 喂给边：亮一档灰蓝 */
        return '<path d="M' + ax + ',' + ay + ' C' + mx + ',' + ay + ' ' + mx + ',' + by + ' ' + bx + ',' + by + '"' +
          (p[2] ? ' stroke-dasharray="5 4"' : '') +
          (color !== '#2c3a52' ? ' stroke="' + color + '"' : '') +
          (p[4] ? '' : ' stroke-opacity="0.08"') + '/>';   /* 聚焦外压暗边：近隐不消失，保留全景上下文 */
      }).join('');
    })();
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
    /* 验证档案助手（PB-04）：徽章色沿既有语义（valid=绿正反馈，其余灰中性），不发明新色 */
    var VAL_ZH = { valid: '有效', noise: '噪音', pending: '待观察', untested: '未验证', decaying: '衰减中' };
    var VAL_SIG_ZH = { insufficient_samples: '触发<30 次不下结论', oos_decay_suspect: '样本外衰减≥50% 判存疑' };
    function valBadge(v) {
      return '<span class="bdg ' + (v === 'valid' ? 'bdg-paper' : 'bdg-gray') + '">' + esc(VAL_ZH[v] || v || '未验证') + '</span>';
    }
    function valHtml(vd) {
      if (!vd || vd.ok === false) return '<div class="empty">' + esc((vd && vd.reason) || '查询失败') + '</div>';
      var recs = vd.records || [];
      if (!recs.length)
        return valBadge('untested') + '<div class="empty" style="margin-top:5px">尚无验证记录——未进验证批次（排序=离钱近先验：执行→风控→总闸→选股→做T→归因）</div>';
      return valBadge(vd.verdict) + '<div style="margin-top:6px">' + recs.map(function (r) {
        return '<div class="cm"><b style="color:#c6cdd8">' + esc(r.window_start) + ' ~ ' + esc(r.window_end) + '</b> · '
          + valBadge(r.verdict) + ' · 触发 ' + esc(r.triggers) + ' 次'
          + (r.hit_ratio == null ? '' : ' · 命中 ' + Math.round(r.hit_ratio * 100) + '%')
          + (r.significance && r.significance !== 'ok' ? ' · ⚠ ' + esc(VAL_SIG_ZH[r.significance] || r.significance) : '')
          + (r.notes ? '<br>' + esc(r.notes) : '')
          + '<br><span style="color:#525d70;font-size:10.5px">' + esc(r.validation_method) + ' · map@' + esc(r.snapshot_commit || '—') + ' · ' + esc(r.verdict_at) + '</span></div>';
      }).join('') + '</div>';
    }
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
      '<div class="sec">设计备注（裁定/欠账原文）</div>' + cms +
      '<div class="sec">验证档案（回测台账）<span class="cnt" id="tdm-val-cnt"></span></div>' +
      '<div id="tdm-val"><div class="empty">查询中…</div></div>';
    box.scrollTop = scroll;
    /* 上/下游导航行点击跳选——drawer 内闭环 */
    box.querySelectorAll('[data-jump]').forEach(function (el) {
      el.addEventListener('click', function () {
        TDM.sel = el.getAttribute('data-jump');
        TDM.focus = TDM.sel;   /* 跳选=换焦点：行为与画布点选一致，血统主线跟着换 */
        render();
        drawer();
      });
    });
    /* 验证档案：异步查台账（c1_backtest.node_verdict，只读端点）——填充后保持阅读位置；
     * 已切节点/抽屉已重绘（valBox 不在 DOM）时丢弃过期响应 */
    var valNode = n.id;
    var valBox = box.querySelector('#tdm-val');
    fetch(API_BASE + '/api/tdm/validation?node_id=' + encodeURIComponent(valNode))
      .then(function (r) { return r.json(); })
      .then(function (vd) {
        if (TDM.sel !== valNode || !valBox || !valBox.isConnected) return;
        var vs = box.scrollTop;
        valBox.innerHTML = valHtml(vd);
        var vc = box.querySelector('#tdm-val-cnt');
        if (vc) vc.textContent = vd.records && vd.records.length ? String(vd.records.length) : '';
        box.scrollTop = vs;
      })
      .catch(function () {
        if (TDM.sel !== valNode || !valBox || !valBox.isConnected) return;
        valBox.innerHTML = '<div class="empty">台账不可达（面板 API 未启动?）</div>';
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
    /* ③ 双击空白重置+退出聚焦（双击节点不算——节点双击是两次打开抽屉） */
    c.addEventListener('dblclick', function (e) {
      if (e.target && e.target.closest && e.target.closest('.tn, .tg')) return;
      exitFocus();
    });
    /* ④ Ctrl+Shift+D 切换 拖动/选择复制 模式；⑤ Esc 退出聚焦 */
    document.addEventListener('keydown', function (e) {
      if (e.ctrlKey && e.shiftKey && (e.key === 'D' || e.key === 'd')) {
        e.preventDefault();
        window.tdmToggleMode();
      }
      if (e.key === 'Escape' && TDM.focus) exitFocus();
    });
    setMode(true);   /* 初始同步按钮文案+徽标+光标 */
  })();
})();
