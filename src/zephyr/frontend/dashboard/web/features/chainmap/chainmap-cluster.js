/* ── 产业地图 L2/L3 链层 · iFinD 等距流程图（2026-09-12 Owner 定稿全量重构）──
 * 形态真源=样板 chainmap_ifind_mockup_v2（分区块蜿蜒）：簇内每链=独立 iFinD 块
 * （职能分区底板 材料与零部件/装备/工艺/产品/服务 + 蛇形折行 + 链锚点大块），
 * 链块间蛇形流式排布成整簇画布；列概念废除（列头/L1..Ln 字样不再出现，
 * layer/zone 只做后端下发的布局参数）。环节=等距立方体（全球环节绿色区分、
 * 暂无落位=暗棕虚线），节点下直挂公司 chip（普通环节前 4 家+「+N 家」折叠、
 * 锚点大块直挂 8 家）；流向线=链内 ig_edge（supply 系=红、其余=蓝）。
 * 环节点开=右侧公司抽屉（Owner 拍板④）。聚焦模式沿用 B4r3：>RAIL_MIN 链自
 * 动聚焦活跃环节最丰富的链（整族全量绘制、压暗他链不删卡），链选轨/链名点击=
 * 聚焦开关。股权徽章（F-CHAINMAP-EQUITY-BADGE）hover/click 浮层与催化角标
 * （F-CHAINMAP-CATALYST）改为 SVG 元素沿用。旧列式实现见 git 历史。
 * 验收单：ACC-F-CHAINMAP-CLUSTER / ACC-F-CHAINMAP-EQUITY-BADGE / ACC-F-CHAINMAP-CATALYST */
(function () {
  'use strict';
  /* 深色主题色表（dashboard 纯深色壳；cube=[顶,左,右,描边,文字]） */
  var T = {
    cubeN: ['#3c3489', '#2e2768', '#26215c', '#afa9ec', '#d9d6f8'],
    cubeG: ['#085041', '#063e33', '#04342c', '#5dcaa5', '#bfe8dc'],
    cubeA: ['#0c447c', '#09376b', '#052f58', '#85b7eb', '#e6f1fb'],
    cubeE: ['#2a1c0e', '#221708', '#1a1206', '#8a4a12', '#c9a06a'],
    chip: ['#1b2843', '#31456e', '#c6d4f0'],
    chipMore: ['#16223a', '#31456e', '#8fb0ea'],
    zone: ['#141f38', '#2b3d64', '#8fb0ea'],
    anchorPlate: ['#1a2a4e', '#35507f', '#9fc4f8'],
    edgeR: '#e06a6a', edgeB: '#6f95e0'
  };
  var ZONE_NAMES = ['材料与零部件', '装备', '工艺', '产品', '服务'];
  var TILE_W = 176, HW = 62, HH = 31, DP = 22, CHIP_H = 22, ZPAD = 14, HEAD_H = 26;
  var BLOCK_GAP_X = 26, BLOCK_GAP_Y = 40;      /* 链块间距 */
  var CHAIN_BUDGET = 1160;                      /* 链内蛇形行宽预算 */
  var CLUSTER_BUDGET = 2440;                    /* 链块蛇形行宽预算（整簇） */
  var ANCHOR_MIN_INDEG = 2;                     /* 兜底锚点最小链内入度 */
  var RAIL_MIN = 8;                             /* >8 链=聚焦模式（B4r3 沿用） */
  /* 股权 relation 中译（词表真源=ig_equity_edge DDL 封闭枚举，与 chainmap-company-card EQ_REL_ZH 同源） */
  var EQ_REL_ZH = { invests_in: '对外投资', subsidiary: '子公司', shareholding: '参股',
                    actual_control: '实控', pledge: '质押', judicial_frozen: '司法冻结' };
  var eqHideT = null;
  var elByNode = {};        /* node_id → cube <g> DOM（聚焦高亮/催化角标挂载） */
  var chainG = {};          /* chain_id → 链块 <g> DOM（压暗） */

  var C = { cid: null, name: '', data: null, busy: false, view: { z: 1, x: 0, y: 0 },
            pos: {}, focusChain: null, focusChainName: null, focusNode: null, market: 'all', cat: null,
            focusOff: false, autoFocused: false };

  function canvasEl() { return document.getElementById('cm-canvas-cluster'); }
  function worldEl() { return document.getElementById('cm-world-cluster'); }
  function svgEl() { return document.getElementById('cm-wires-cluster'); }

  function applyView() {
    var w = worldEl();
    if (w) w.style.transform = 'translate(' + C.view.x + 'px,' + C.view.y + 'px) scale(' + C.view.z + ')';
    var b = document.getElementById('cm-zoom-cluster');
    if (b) b.textContent = Math.round(C.view.z * 100) + '%';
  }

  function bindView() {
    var c = canvasEl();
    if (!c || c.dataset.bound) return;
    c.dataset.bound = '1';
    c.addEventListener('wheel', function (e) {
      e.preventDefault();
      var r = c.getBoundingClientRect();
      zoomAt(e.clientX - r.left, e.clientY - r.top, e.deltaY < 0 ? 1.12 : 0.89);
    }, { passive: false });
    var drag = null;
    c.addEventListener('mousedown', function (e) {
      drag = { x: e.clientX, y: e.clientY, vx: C.view.x, vy: C.view.y };
      c.classList.add('dragging');
    });
    window.addEventListener('mousemove', function (e) {
      if (!drag) return;
      C.view.x = drag.vx + (e.clientX - drag.x);
      C.view.y = drag.vy + (e.clientY - drag.y);
      applyView();
    });
    window.addEventListener('mouseup', function () { drag = null; c.classList.remove('dragging'); });
    c.addEventListener('dblclick', function (e) { if (e.target.closest('.cm-nd, .cm-eqb, .cm-rail')) return; fitView(); });
  }

  function zoomAt(mx, my, factor) {
    var nz = Math.max(0.15, Math.min(6, C.view.z * factor));
    var k = nz / C.view.z;
    C.view.x = mx - (mx - C.view.x) * k;
    C.view.y = my - (my - C.view.y) * k;
    C.view.z = nz;
    applyView();
  }

  function fitView() {
    var c = canvasEl(), d = C.viewData;
    if (!c || !d || !d.worldW) return;
    var r = c.getBoundingClientRect();
    var railW = document.getElementById('cm-rail') ? 226 : 0;
    var z = Math.min((r.width - 24 - railW) / d.worldW, (r.height - 24) / d.worldH, 1.4);
    C.view = { z: z, x: railW + (r.width - railW - d.worldW * z) / 2, y: 12 };
    applyView();
  }

  function centerOn(nodeId) {
    var c = canvasEl(), p = C.pos[nodeId];
    if (!c || !p) return;
    var r = c.getBoundingClientRect();
    var railW = document.getElementById('cm-rail') ? 226 : 0;
    var z = Math.max(C.view.z, 0.9);
    C.view = { z: z, x: railW + (r.width - railW) / 2 - p.x * z, y: r.height / 2 - p.y * z };
    applyView();
  }

  function setCrumb(chainName) {
    var cr = document.getElementById('cm-crumb');
    if (!cr) return;
    cr.innerHTML = '<span class="cm-back" id="cm-back">‹ 全景</span>' +
      '<span class="cm-sep">›</span><span>' + C.name + (chainName ? '<span class="cm-sep">›</span>' + chainName : '') + '</span>';
    var back = document.getElementById('cm-back');
    if (back) back.addEventListener('click', function () { ZK.bus.emit('cm:view', { view: 'galaxy' }); });
  }

  /* 显示名：剥链名前缀 + 剥墓碑后缀（B4r4 语义沿用；title/抽屉保留全名） */
  function dispName(chainName, name) {
    var disp = name, pfx = chainName + '-';
    if (disp.indexOf(pfx) === 0 && disp.length > pfx.length) disp = disp.slice(pfx.length);
    disp = disp.replace(/（已并入[^）]*）?\s*$/, '').trim();
    return disp || name;
  }

  function nameLines(t) {
    if (t.length <= 6) return [t];
    var i = t.indexOf('（');
    if (i > 0) return [t.slice(0, i), t.slice(i)];
    return [t.slice(0, Math.ceil(t.length / 2)), t.slice(Math.ceil(t.length / 2))];
  }

  /* ── 链内 iFinD 布局（样板 v2 引擎移植；layer/zone 为 API 下发布局参数）──
   * 返回 {blocks, center, W, H, anchorId, twins, indeg}；
   * blocks=[{kind:'zone',zi,title,rows,rowH,bw,bh,x,y} | {kind:'anchor',anchorId,nacs,twins,bw,bh,x,y}] */
  function buildChainLayout(chain, edgePairs) {
    var nodes = chain.nodes;
    var indeg = {}, byName = {}, i, n;
    for (i = 0; i < nodes.length; i++) { indeg[nodes[i].node_id] = 0; byName[nodes[i].name] = nodes[i].node_id; }
    for (i = 0; i < edgePairs.length; i++) {
      var a = edgePairs[i][0], b = edgePairs[i][1];
      if (indeg[b] != null && a !== b) indeg[b]++;
    }
    var base = chain.name.replace(/产业链$/, '');
    var anchor = byName[chain.name] || byName[base] || null;
    if (!anchor) {
      var best = null, mi = ANCHOR_MIN_INDEG - 1;
      for (i = 0; i < nodes.length; i++) { if (indeg[nodes[i].node_id] > mi) { mi = indeg[nodes[i].node_id]; best = nodes[i].node_id; } }
      anchor = best;
    }
    var anchorName = anchor ? (nodes.filter(function (x) { return x.node_id === anchor; })[0] || {}).name : null;
    var zones = [[], [], [], [], []], twins = [];
    for (i = 0; i < nodes.length; i++) {
      n = nodes[i];
      if (n.node_id === anchor) continue;
      var gi = n.name.indexOf('（全球）');
      if (gi > 0 && byName[n.name.slice(0, gi)] === anchor) { twins.push(n); continue; }   /* 锚点的全球镜像 → 锚点块副立方体 */
      var z = n.zone;
      if (typeof z !== 'number' || z < 0 || z > 4) z = indeg[n.node_id] === 0 ? 0 : 3;     /* API 缺参兜底 */
      zones[z].push(n);
    }
    zones.forEach(function (items) {
      items.sort(function (p, q) {
        var lp = (typeof p.layer === 'number' && p.layer >= 0) ? p.layer : 99;
        var lq = (typeof q.layer === 'number' && q.layer >= 0) ? q.layer : 99;
        return (lp - lq) || (q.n_companies - p.n_companies) || p.name.localeCompare(q.name, 'zh');
      });
    });
    var blocks = [];
    zones.forEach(function (items, zi) {
      if (!items.length) return;
      var cols = Math.min(4, items.length), rows = [];
      items.forEach(function (nn, k) {
        var r = Math.floor(k / cols), cc = k % cols;
        (rows[r] = rows[r] || []).push({ n: nn, c: cc });
      });
      var rowH = rows.map(function (row) {
        return Math.max.apply(null, row.map(function (t) {
          return 100 + Math.min(t.n.n_companies, 4) * CHIP_H + (t.n.n_companies > 4 ? CHIP_H : 0) + 6;
        }));
      });
      blocks.push({ kind: 'zone', zi: zi, title: ZONE_NAMES[zi], rows: rows, rowH: rowH,
        bw: cols * TILE_W + ZPAD * 2, bh: HEAD_H + rowH.reduce(function (p, q) { return p + q; }, 0) + ZPAD });
    });
    var nacs = anchor ? (nodes.filter(function (x) { return x.node_id === anchor; })[0] || {}).n_companies || 0 : 0;
    if (anchor) {
      var rowsN = Math.ceil(Math.max(1, Math.min(nacs, 8)) / 2);
      var bhA = HEAD_H + 12 + rowsN * 24 + (nacs > 8 ? 24 : 0) + 16;
      bhA = Math.max(bhA, twins.length ? HEAD_H + 244 : HEAD_H + 182);
      blocks.push({ kind: 'anchor', anchorId: anchor, nacs: nacs, twins: twins.slice(), bw: 570, bh: bhA });
    }
    var x = 0, y = 0, rowMax = 0, maxRight = 0;
    blocks.forEach(function (b) {
      if (x > 0 && x + b.bw > CHAIN_BUDGET) { x = 0; y += rowMax + BLOCK_GAP_X; rowMax = 0; }
      b.x = x; b.y = y; x += b.bw + BLOCK_GAP_X; rowMax = Math.max(rowMax, b.bh);
      maxRight = Math.max(maxRight, b.x + b.bw);
    });
    var center = {};
    blocks.forEach(function (b) {
      if (b.kind === 'zone') {
        var yy = b.y + HEAD_H;
        b.rows.forEach(function (row, r) {
          row.forEach(function (t) {
            center[t.n.node_id] = { x: b.x + ZPAD + t.c * TILE_W + TILE_W / 2, y: yy + 40 };
          });
          yy += b.rowH[r];
        });
      } else {
        var cx = b.x + 110, cy = b.y + HEAD_H + 78;
        center[b.anchorId] = { x: cx, y: cy };
        b.twins.forEach(function (t, k) { center[t.node_id] = { x: cx, y: cy + HH + DP + 64 + k * 70 }; });
      }
    });
    return { blocks: blocks, center: center, W: maxRight + ZPAD * 2, H: y + rowMax + 60,
             anchorId: anchor, anchorName: anchorName || '', indeg: indeg, twins: twins };
  }

  function nodeNameOf(view, nid) {
    var out = null;
    view.chains.forEach(function (ch) {
      if (out) return;
      var hit = ch.nodes.filter(function (n) { return n.node_id === nid; })[0];
      if (hit) out = hit;
    });
    return out;
  }

  /* ── 簇布局：每链一个 iFinD 块，链块间蛇形流式排布；写 C.pos（全局坐标）── */
  function layoutCluster(view) {
    var chainOf = {};
    view.chains.forEach(function (ch) { ch.nodes.forEach(function (n) { chainOf[n.node_id] = ch.chain_id; }); });
    var edgesByChain = {};
    view.edges.forEach(function (e) {
      var ca = chainOf[e[0]], cb = chainOf[e[1]];
      if (ca != null && ca === cb) (edgesByChain[ca] = edgesByChain[ca] || []).push(e);
    });
    view.chains.forEach(function (ch) {
      ch._layout = buildChainLayout(ch, edgesByChain[ch.chain_id] || []);
      ch._edges = edgesByChain[ch.chain_id] || [];
    });
    var x = 0, y = 0, rowMax = 0, maxRight = 0;
    C.pos = {}; chainG = {}; elByNode = {};
    /* 聚焦链块排首位（存在时），其余保持后端序（n_companies 降序） */
    var ordered = view.chains.slice();
    if (C.focusChain) {
      ordered.sort(function (p, q) { return (q.chain_id === C.focusChain ? 1 : 0) - (p.chain_id === C.focusChain ? 1 : 0); });
    }
    ordered.forEach(function (ch) {
      var lay = ch._layout, bw = Math.max(lay.W, 200), bh = lay.H + 24;   /* +24=链名标题条 */
      if (x > 0 && x + bw > CLUSTER_BUDGET) { x = 0; y += rowMax + BLOCK_GAP_Y; rowMax = 0; }
      ch._ox = x; ch._oy = y;
      Object.keys(lay.center).forEach(function (nid) {
        C.pos[nid] = { x: x + lay.center[nid].x, y: y + 24 + lay.center[nid].y };
      });
      x += bw + BLOCK_GAP_X; rowMax = Math.max(rowMax, bh);
      maxRight = Math.max(maxRight, x - BLOCK_GAP_X);
    });
    view.worldW = maxRight + 20;
    view.worldH = y + rowMax + 40;
    C.viewData = view;
  }

  /* ── SVG 元件 ── */
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }

  function cubeSvg(cx, cy, node, variant, indegN, disp) {
    var c, sw, hw = HW, hh = HH, dp = DP, dash = '';
    if (variant === 'global') { c = T.cubeG; sw = 1.6; }
    else if (variant === 'anchor') { c = T.cubeA; sw = 2; hw = 84; hh = 42; dp = 30; }
    else if (variant === 'anchorTwin') { c = T.cubeG; sw = 1.4; hw = 52; hh = 26; dp = 18; }
    else if (variant === 'empty') { c = T.cubeE; sw = 1.4; dash = ' stroke-dasharray="4 3"'; }
    else { c = T.cubeN; sw = indegN >= 4 ? 2.2 : 1.6; }
    var lines = nameLines(disp);
    var fs = variant === 'anchor' ? 15 : (lines.length > 1 ? 12.5 : (disp.length > 5 ? 12 : 14));
    var dy = lines.length > 1 ? -5 : 5;
    var txt = lines.map(function (l, i) {
      return '<text x="' + cx + '" y="' + (cy + dy + i * 15) + '" text-anchor="middle" font-size="' + fs +
        '" font-weight="700" fill="' + c[4] + '">' + esc(l) + '</text>';
    }).join('');
    return '<g class="cm-nd' + (variant === 'empty' ? ' empty0' : '') + '" data-node="' + node.node_id + '">' +
      '<polygon class="cube-top" points="' + cx + ',' + (cy - hh) + ' ' + (cx + hw) + ',' + cy + ' ' + cx + ',' + (cy + hh) + ' ' + (cx - hw) + ',' + cy +
      '" fill="' + c[0] + '" stroke="' + c[3] + '" stroke-width="' + sw + '"' + dash + '/>' +
      '<polygon points="' + (cx - hw) + ',' + cy + ' ' + cx + ',' + (cy + hh) + ' ' + cx + ',' + (cy + hh + dp) + ' ' + (cx - hw) + ',' + (cy + dp) +
      '" fill="' + c[1] + '" stroke="' + c[3] + '" stroke-width="1"/>' +
      '<polygon points="' + (cx + hw) + ',' + cy + ' ' + cx + ',' + (cy + hh) + ' ' + cx + ',' + (cy + hh + dp) + ' ' + (cx + hw) + ',' + (cy + dp) +
      '" fill="' + c[2] + '" stroke="' + c[3] + '" stroke-width="1"/>' + txt;
  }

  function eqBadgeSvg(cx, cy, node) {
    var eq = node.equity;
    if (!eq || (eq.out <= 0 && eq.inn <= 0)) return '';
    var seg = [];
    if (eq.out > 0) seg.push('控' + eq.out);
    if (eq.inn > 0) seg.push('被' + eq.inn + '控');
    var w = 18 + seg.join('/').length * 7;
    return '<g class="cm-eqb" data-eq="' + node.id + '" title="股权关系（ig_equity_edge）——悬停看明细">' +
      '<rect x="' + (cx + HW - w - 4) + '" y="' + (cy - HH - 4) + '" width="' + w + '" height="15" rx="7" fill="#101b30" stroke="#3a5a8c"/>' +
      '<text x="' + (cx + HW - w / 2 - 4) + '" y="' + (cy - HH + 7.5) + '" text-anchor="middle" font-size="9" fill="#7db4e8">⚙' + esc(seg.join('/')) + '</text></g>';
  }

  function chipSvg(cx, cy, label, more) {
    var w = Math.min(Math.max(label.length * 12 + 16, 56), 164);
    var bg = more ? T.chipMore[0] : T.chip[0], bd = more ? T.chipMore[1] : T.chip[1], tc = more ? T.chipMore[2] : T.chip[2];
    return '<g class="cm-chipm' + (more ? ' chipmore' : '') + '"' + (more ? ' data-node="' + more + '"' : '') + '>' +
      '<rect x="' + (cx - w / 2) + '" y="' + cy + '" width="' + w + '" height="20" rx="6" fill="' + bg + '" stroke="' + bd + '"/>' +
      '<text x="' + cx + '" y="' + (cy + 14) + '" text-anchor="middle" font-size="11" fill="' + tc + '">' + esc(label) + '</text></g>';
  }

  /* ── 渲染整簇 SVG（wires svg 复用为唯一画布；DOM 卡片层退役）── */
  function drawView(view) {
    var svg = svgEl();
    var empty = document.getElementById('cm-empty-cluster');
    if (!svg) return;
    hideEqOverlay(true);
    if (!view.chains.length) {
      svg.setAttribute('width', 10); svg.setAttribute('height', 10);
      svg.innerHTML = '';
      if (empty) { empty.style.display = 'flex'; empty.textContent = '该簇/链无环节数据'; }
      return;
    }
    layoutCluster(view);
    svg.setAttribute('width', view.worldW); svg.setAttribute('height', view.worldH);
    var w = worldEl();
    if (w) { w.style.width = view.worldW + 'px'; w.style.height = view.worldH + 'px'; }
    if (empty) empty.style.display = 'none';
    var defs = '<defs>' +
      '<marker id="cmArR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="' + T.edgeR + '"/></marker>' +
      '<marker id="cmArB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="' + T.edgeB + '"/></marker></defs>';
    var body = '';
    view.chains.forEach(function (ch) {
      var lay = ch._layout, ox = ch._ox, oy = ch._oy;
      var g = '<g class="cm-ch" data-chain="' + ch.chain_id + '">';
      var title = ch.name + ' · ' + ch.n_companies + ' 公司';
      g += '<g class="cm-chainchip" data-chain="' + ch.chain_id + '">' +
        '<rect x="' + ox + '" y="' + oy + '" width="' + Math.max(lay.W, 200) + '" height="20" fill="rgba(0,0,0,0)"/>' +
        '<text x="' + (ox + 2) + '" y="' + (oy + 15) + '" font-size="12.5" font-weight="700" fill="#8fb0ea">' + esc(title) + '</text></g>';
      var anchorBlock = null;
      lay.blocks.forEach(function (b) {
        var by = oy + 24 + b.y;
        if (b.kind === 'zone') {
          g += '<rect x="' + (ox + b.x) + '" y="' + by + '" width="' + b.bw + '" height="' + b.bh + '" rx="10" fill="' + T.zone[0] + '" stroke="' + T.zone[1] + '"/>' +
            '<text x="' + (ox + b.x + ZPAD) + '" y="' + (by + 17) + '" font-size="12" font-weight="700" fill="' + T.zone[2] + '">' + esc(b.title) + '</text>';
        } else {
          anchorBlock = b;
          var an = nodeNameOf(view, b.anchorId);
          g += '<rect x="' + (ox + b.x) + '" y="' + by + '" width="' + b.bw + '" height="' + b.bh + '" rx="10" fill="' + T.anchorPlate[0] + '" stroke="' + T.anchorPlate[1] + '"/>' +
            '<text x="' + (ox + b.x + ZPAD) + '" y="' + (by + 17) + '" font-size="12" font-weight="700" fill="' + T.anchorPlate[2] + '">锚点 · ' + esc(an ? dispName(ch.name, an.name) : '') + '</text>';
        }
      });
      ch._edges.forEach(function (e) {
        var p1 = C.pos[e[0]], p2 = C.pos[e[1]];
        if (!p1 || !p2) return;
        var red = /supply|downstream/.test(e[2] || '');
        var mx = (p1.x + p2.x) / 2, my = (p1.y + p2.y) / 2 - 18;
        g += '<path class="cm-edge" data-f="' + e[0] + '" data-t="' + e[1] + '" d="M' + p1.x + ',' + p1.y +
          ' Q' + mx + ',' + my + ' ' + p2.x + ',' + p2.y + '" fill="none" stroke="' + (red ? T.edgeR : T.edgeB) +
          '" stroke-width="1.8" opacity=".55" marker-end="url(#' + (red ? 'cmArR' : 'cmArB') + ')"/>';
      });
      ch.nodes.forEach(function (n) {
        var p = C.pos[n.node_id];
        if (!p) return;
        var isAnchorTwin = lay.twins.some(function (t) { return t.node_id === n.node_id; });
        var isAnchor = n.node_id === lay.anchorId;
        var disp = dispName(ch.name, n.name);
        var variant = isAnchor ? 'anchor' : (isAnchorTwin ? 'anchorTwin' : (n.name.indexOf('（全球）') > 0 ? 'global' : (n.n_companies > 0 ? 'normal' : 'empty')));
        g += cubeSvg(p.x, p.y, n, variant, lay.indeg[n.node_id] || 0, disp);
        g += eqBadgeSvg(p.x, p.y, n);
        g += '</g>';
        if (isAnchorTwin) return;
        var comps = n.companies || [], nTot = n.n_companies || 0;
        if (isAnchor && anchorBlock) {
          var ax = ox + anchorBlock.x, ay = oy + 24 + anchorBlock.y;
          comps.slice(0, 8).forEach(function (cp, k) {
            g += chipSvg(ax + 240 + (k % 2) * 158, ay + HEAD_H + 12 + Math.floor(k / 2) * 24, cp.name || cp.symbol, null);
          });
          if (nTot > 8) {
            g += chipSvg(ax + 240 + 158, ay + HEAD_H + 12 + Math.ceil(Math.min(comps.length, 8) / 2) * 24,
              '+' + (nTot - 8) + ' 家', n.node_id);
          }
        } else {
          comps.slice(0, 4).forEach(function (cp, k) {
            g += chipSvg(p.x, p.y + HH + DP + 8 + k * CHIP_H, cp.name || cp.symbol, null);
          });
          if (nTot > 4) g += chipSvg(p.x, p.y + HH + DP + 8 + 4 * CHIP_H, '+' + (nTot - 4) + ' 家', n.node_id);
        }
      });
      g += '</g>';
      body += g;
    });
    svg.innerHTML = defs + body;
    /* 重建 cube 元素映射（催化角标挂载 + 聚焦高亮依赖） */
    elByNode = {};
    Array.prototype.forEach.call(svg.querySelectorAll('g.cm-nd'), function (g) {
      elByNode[g.getAttribute('data-node')] = g;
    });
    applyFocus();
    decorateCatalyst();
    fitView();
  }

  /* ── SVG 事件委托：环节/「+N」点击开抽屉、股权徽章 hover/click 浮层、链名聚焦开关 ── */
  function bindSvgEvents(view) {
    var svg = svgEl();
    if (!svg || svg.dataset.bound) return;
    svg.dataset.bound = '1';
    svg.addEventListener('click', function (e) {
      if (!e.target.closest) return;
      var eq = e.target.closest('.cm-eqb');
      if (eq) {
        e.stopPropagation();
        var nid = eq.getAttribute('data-eq');
        var n = nodeNameOf(view, nid);
        if (!n) return;
        var ov = eqOverlayEl();
        if (ov && ov.dataset.pin === nid) { hideEqOverlay(true); return; }
        showEqOverlay(n, eq);
        var o2 = eqOverlayEl();
        if (o2) o2.dataset.pin = nid;
        return;
      }
      var cc = e.target.closest('.cm-chainchip');
      if (cc) {
        var cid = cc.getAttribute('data-chain');
        var ch = (view.chains.filter(function (x) { return x.chain_id === cid; })[0] || {});
        if (C.focusChain === cid) unfocusFocus();
        else focusChain(cid, ch.name);
        return;
      }
      var more = e.target.closest('.chipmore');
      var nd = e.target.closest('.cm-nd');
      var hit = more || nd;
      if (!hit) return;
      var node = nodeNameOf(view, hit.getAttribute('data-node'));
      if (node) openPanel(node);
    });
    svg.addEventListener('mouseover', function (e) {
      if (!e.target.closest) return;
      var eq = e.target.closest('.cm-eqb');
      if (!eq) return;
      if (eqHideT) { clearTimeout(eqHideT); eqHideT = null; }
      var n = nodeNameOf(view, eq.getAttribute('data-eq'));
      if (n) showEqOverlay(n, eq);
    });
    svg.addEventListener('mouseout', function (e) {
      if (!e.target.closest) return;
      var eq = e.target.closest('.cm-eqb');
      if (!eq) return;
      var to = e.relatedTarget;
      if (to && to.closest && to.closest('.cm-eqb')) return;
      eqHideT = setTimeout(function () { hideEqOverlay(); }, 250);
    });
  }

  /* ── 聚焦模式（B4r3 沿用：整族全量绘制，压暗他链不删卡）── */
  function defaultFocus(d) {
    function score(c) {
      var act = 0;
      c.nodes.forEach(function (n) { if (n.n_companies > 0) act++; });
      return [act, c.n_companies, c.n_nodes];
    }
    return d.chains.slice().sort(function (a, b) {
      var sa = score(a), sb = score(b);
      for (var i = 0; i < 3; i++) { if (sb[i] !== sa[i]) return sb[i] - sa[i]; }
      return 0;
    })[0];
  }

  function render() {
    var d = C.data;
    if (!d) return;
    clearRail();
    drawView(d);
    bindSvgEvents(d);
    if (d.chains.length > RAIL_MIN) {
      if (!C.focusChain && !C.focusOff) {
        var def = defaultFocus(d);
        C.focusChain = def.chain_id;
        C.focusChainName = def.name;
        C.autoFocused = true;
        C.needCenter = true;
      }
      buildRail(d, C.focusChain);
      applyFocus();
    }
    var meta = document.getElementById('cm-meta');
    if (meta) {
      var nNodes = d.chains.reduce(function (s, c) { return s + c.nodes.length; }, 0);
      meta.textContent = C.name + ' · ' + d.chains.length + ' 链 ' + nNodes + ' 环节 · iFinD 等距流程图 · 真源 ig_*（PG 只读）' +
        (C.focusChain ? ' · 聚焦「' + (C.focusChainName || '') + '」（点链名取消）' : ' · 点链名聚焦');
      meta.classList.remove('cm-bad');
    }
    setCrumb(C.focusChainName);
    fitView();
    if (C.needCenter) {
      C.needCenter = false;
      var fch = d.chains.filter(function (c) { return c.chain_id === C.focusChain; })[0];
      if (fch && fch._layout) {
        /* 首屏镜头落在聚焦链锚点大块（无锚点回退首节点） */
        var target = fch._layout.anchorId || (fch.nodes[0] && fch.nodes[0].node_id);
        if (target) centerOn(target);
      }
    }
  }

  function buildRail(d, activeId) {
    var c = canvasEl();
    if (!c) return;
    clearRail();
    var rail = document.createElement('div');
    rail.className = 'cm-rail';
    rail.id = 'cm-rail';
    var head = document.createElement('div');
    head.className = 'cm-rail-h';
    head.textContent = '链选单 · ' + d.chains.length + '（点聚焦/取消）';
    rail.appendChild(head);
    d.chains.forEach(function (ch) {
      var r = document.createElement('div');
      r.className = 'cm-rail-i' + (ch.chain_id === activeId ? ' act' : '');
      r.innerHTML = '<span class="nm" title="' + ch.name + '">' + ch.name + '</span><span class="ct">' + ch.n_companies + '</span>';
      r.addEventListener('click', function () {
        if (C.focusChain === ch.chain_id) unfocusFocus();
        else focusChain(ch.chain_id, ch.name);
      });
      rail.appendChild(r);
    });
    c.appendChild(rail);
  }

  function clearRail() {
    var old = document.getElementById('cm-rail');
    if (old && old.parentNode) old.parentNode.removeChild(old);
  }

  function focusChain(chainId, chainName) {
    C.focusChain = chainId;
    C.focusChainName = chainName || null;
    C.focusOff = false;
    C.autoFocused = false;
    if (C.data) render();
    applyFocus();
    if (C.focusNode) centerOn(C.focusNode);
    ZK.bus.emit('cm:chain-active', { chain_id: chainId });
  }

  function unfocusFocus() {
    C.focusChain = null;
    C.focusChainName = null;
    C.focusNode = null;
    C.focusOff = true;
    C.autoFocused = false;
    render();
  }

  function applyFocus() {
    var svg = svgEl();
    if (!svg) return;
    Array.prototype.forEach.call(svg.querySelectorAll('g.cm-ch'), function (g) {
      var cid = g.getAttribute('data-chain');
      chainG[cid] = g;
      g.classList.toggle('dimmed', !!C.focusChain && cid !== C.focusChain);
    });
    Array.prototype.forEach.call(svg.querySelectorAll('.cm-nd.hit'), function (g) { g.classList.remove('hit'); });
    if (C.focusNode && elByNode[C.focusNode] && elByNode[C.focusNode].classList) {
      elByNode[C.focusNode].classList.add('hit');
    }
  }

  /* ── 股权徽章明细浮层（DOM，挂 #p-chainmap；listed 行点击跳公司详情卡）── */
  function eqOverlayEl() { return document.getElementById('cm-eq-overlay'); }
  function hideEqOverlay(now) {
    if (eqHideT) { clearTimeout(eqHideT); eqHideT = null; }
    var ov = eqOverlayEl();
    if (ov && (now || !ov.dataset.pin) && ov.parentNode) ov.parentNode.removeChild(ov);
  }
  function showEqOverlay(n, cardEl) {
    if (eqHideT) { clearTimeout(eqHideT); eqHideT = null; }
    var old = eqOverlayEl();
    if (old && old.parentNode) old.parentNode.removeChild(old);
    var eq = n.equity || {};
    var rows = (eq.rows || []).map(function (r) {
      var zh = EQ_REL_ZH[r.relation] || (r.relation || '股权');
      var ver = r.verification === 'official' ? '官方口径' : (r.verification === 'verified' ? '已核验' : '未核验');
      var nm = r.name || r.symbol || r.ref || '—';
      var idp = r.symbol ? r.symbol : (r.ref || '非上市编码');
      var lk = !!r.symbol;
      return '<div class="cm-eq-r' + (lk ? ' lk' : '') + '"' +
        (lk ? ' data-sym="' + r.symbol + '" data-name="' + nm + '" title="点开对方公司详情卡"'
            : ' title="未上市/个人持有方——仅展示不跳转"') + '>' +
        '<span class="d">' + (r.dir === 'out' ? '控→' : '⬅被控') + '</span>' +
        '<span class="nm">' + nm + '</span>' +
        '<span class="sy">' + idp + '</span>' +
        '<span class="mt">' + zh + (r.stake_pct != null ? ' · 持股 ' + r.stake_pct + '%' : '') + ' · ' + ver + '</span></div>';
    }).join('');
    var total = (eq.out || 0) + (eq.inn || 0);
    var ov = document.createElement('div');
    ov.id = 'cm-eq-overlay';
    ov.innerHTML = '<div class="cm-eq-h">股权关系 · ' + (n.name || '') +
      '（控 ' + (eq.out || 0) + ' / 被 ' + (eq.inn || 0) + ' 控）' +
      (total > (eq.rows || []).length ? ' · 共 ' + total + ' 条' : '') + '</div>' + rows;
    ov.addEventListener('mouseenter', function () { if (eqHideT) { clearTimeout(eqHideT); eqHideT = null; } });
    ov.addEventListener('mouseleave', function () { hideEqOverlay(); });
    ov.addEventListener('click', function (e) {
      var row = e.target.closest ? e.target.closest('.cm-eq-r[data-sym]') : null;
      if (row) { hideEqOverlay(true); ZK.bus.emit('cm:open-company', { symbol: row.getAttribute('data-sym'), name: row.getAttribute('data-name') }); }
    });
    var page = document.getElementById('p-chainmap');
    if (!page) return;
    page.appendChild(ov);
    var r = cardEl.getBoundingClientRect();
    var left = Math.min(r.left, window.innerWidth - 336);
    ov.style.left = Math.max(4, left) + 'px';
    ov.style.top = Math.min(r.bottom + 4, window.innerHeight - 120) + 'px';
  }

  /* ── 催化剂角标（SVG 版）：命中环节 cube 右上角标「催」，点击开环节面板（受益清单段在抽屉顶部）── */
  function decorateCatalyst() {
    var cat = C.cat;
    if (!cat || !cat.nodes) return;
    Object.keys(cat.nodes).forEach(function (nid) {
      var g = elByNode[nid];
      if (!g || !g.querySelector) return;
      if (g.querySelector('.cm-catb')) return;
      var hits = cat.nodes[nid] || [];
      var d0 = hits[0] || {};
      var top = g.querySelector('.cube-top');
      if (!top) return;
      var pts = top.getAttribute('points').split(' ');
      var xs = pts.map(function (p) { return parseFloat(p.split(',')[0]); });
      var ys = pts.map(function (p) { return parseFloat(p.split(',')[1]); });
      var cx = (Math.min.apply(null, xs) + Math.max.apply(null, xs)) / 2, topY = Math.min.apply(null, ys);
      var b = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      b.setAttribute('class', 'cm-catb');
      b.setAttribute('data-cat', nid);
      var title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      title.textContent = '催化命中 ' + hits.length + ' 条：' + (d0.theme_id || '') + (d0.direction || '') +
        '（' + (d0.date || '') + (d0.is_future ? ' · 未消化' : '') + '）——点击看受益清单';
      var c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      c.setAttribute('cx', cx + 34); c.setAttribute('cy', topY - 2); c.setAttribute('r', 8);
      c.setAttribute('fill', '#8a4d1f'); c.setAttribute('stroke', '#b06a2a');
      var t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      t.setAttribute('x', cx + 34); t.setAttribute('y', topY + 2);
      t.setAttribute('text-anchor', 'middle'); t.setAttribute('font-size', '9'); t.setAttribute('fill', '#ffd9a8');
      t.textContent = '催';
      b.appendChild(title); b.appendChild(c); b.appendChild(t);
      b.addEventListener('click', function (e) {
        e.stopPropagation();
        var node = nodeNameOf(C.data, nid);
        if (node) openPanel(node);
      });
      g.appendChild(b);
    });
  }

  /* ── 环节公司抽屉（DOM 沿用；tier 字样退役，副标题改显示职能词）── */
  function openPanel(n) {
    var side = document.getElementById('cm-side');
    if (!side) return;
    hideEqOverlay(true);
    side.style.display = 'block';
    side.innerHTML = '<div class="dim" style="font-size:12px">加载公司落位…</div>';
    var catalyzed = !!(C.cat && C.cat.nodes && C.cat.nodes[n.node_id]);
    ZK.api.fetchChainmapNode(n.node_id)
      .then(function (d) {
        if (!d.ok) { side.innerHTML = '<div class="cm-bad" style="font-size:12px">加载失败：' + (d.error || '') + '</div>'; return; }
        var rows = d.companies.map(function (cp) {
          var cls = (cp.role.indexOf('龙头') >= 0 || cp.role === '核心') ? 'lead' : (cp.role === '参与' ? 'join' : '');
          var xbadge = (cp.n_chains != null && cp.n_chains > 1) ? '<span class="rl xlinks" title="该公司跨 ' + cp.n_chains + ' 条产业链，点行看全部落位">跨' + cp.n_chains + '链</span>' : '';
          return '<div class="cm-co" data-sym="' + cp.symbol + '" data-name="' + (cp.name || '') + '" title="点开公司详情卡" style="cursor:pointer"><span class="rl ' + cls + '">' + (cp.role || '提及') + '</span>' +
            '<span class="nm" title="' + cp.name + '">' + (cp.name || '—') + '</span>' +
            '<span class="sy">' + cp.symbol + '</span>' + xbadge + '<span class="cf">' + (cp.confidence == null ? '' : cp.confidence.toFixed(2)) + '</span></div>';
        }).join('');
        var finish = function (cat) {
          var ben = '';
          if (cat && cat.ok && cat.n_hits > 0) {
            var hitRows = (cat.hits || []).map(function (h) {
              return '<div class="cm-ben-h"><span class="' + (h.direction === '受益' ? 'up' : 'dn') + '">' + h.direction + '</span>' +
                '<span class="th">' + h.theme_id + '</span>' +
                '<span class="dt">' + h.date + (h.is_future ? '（未消化）' : '') + '</span>' +
                '<span class="ds" title="' + h.description + '">' + h.description + '</span></div>';
            }).join('');
            var stockRows = (cat.beneficiaries || []).slice(0, 10).map(function (b) {
              var wr = b.jump ? '<span class="wr" data-sym="' + b.symbol + '" data-name="' + (b.name || '') + '" title="跳作战池">作战池→</span>' : '';
              return '<div class="cm-ben-r"><span class="rl">' + (b.role || '提及') + '</span>' +
                '<span class="nm" title="' + (b.name || '') + '">' + (b.name || '—') + '</span>' +
                '<span class="sy">' + b.symbol + '</span>' + wr + '</div>';
            }).join('');
            ben = '<div class="cm-ben">' +
              '<div class="cm-ben-t">⚡ 催化受益清单（' + (cat.hits || []).length + ' / ' + cat.n_hits + ' 条事件）</div>' +
              hitRows +
              '<div class="cm-ben-st">受益个股（本环节落位 · 角色序 · 前 10 / 共 ' + cat.n_beneficiaries + '）</div>' +
              stockRows +
              '<div class="cm-ben-note">命中粒度=主题→申万行业→链级投影；受益方向=MOD-ALT-005 主题库既有判定；本功能不做涨跌预测（传导预测已证伪裁定留档）。作战池跳转=页面导航+提示（选中接口演示态，未真实入池）。</div>' +
              '</div>';
          }
          side.innerHTML =
            '<span class="cm-x" title="关闭">✕</span>' + ben +
            '<div class="cm-sd-t">' + d.node.name + '</div>' +
            '<div class="cm-sd-s">' + d.node.chain_name +
            (d.node.function_role ? ' · ' + d.node.function_role : '') +
            ' ｜ 公司 ' + d.total + ' 家（按角色/置信度排序，最多展示 200）</div>' +
            (rows || '<div class="dim" style="font-size:12px">该环节暂无公司映射</div>');
          var x = side.querySelector('.cm-x');
          if (x) x.addEventListener('click', function () { side.style.display = 'none'; });
          Array.prototype.forEach.call(side.querySelectorAll('.cm-co[data-sym]'), function (el) {
            el.addEventListener('click', function () {
              ZK.bus.emit('cm:open-company', { symbol: el.getAttribute('data-sym'), name: el.getAttribute('data-name') });
            });
          });
          Array.prototype.forEach.call(side.querySelectorAll('.cm-ben-r .wr[data-sym]'), function (el) {
            el.addEventListener('click', function (ev) {
              ev.stopPropagation();
              if (typeof go === 'function') go('warroom');
              if (typeof gToast === 'function') {
                gToast('「' + (el.getAttribute('data-name') || '') + ' ' + el.getAttribute('data-sym') + '」来自催化受益清单——作战池选中接口为演示态，未真实入池');
              }
            });
          });
        };
        if (catalyzed) {
          ZK.api.fetchChainmapCatalystNode(n.node_id).then(finish).catch(function () { finish(null); });
        } else finish(null);
      }).catch(function (e) {
        side.innerHTML = '<div class="cm-bad" style="font-size:12px">加载失败（' + ((e && e.message) || 'fetch') + '）</div>';
      });
  }

  function show(showIt) {
    var c = canvasEl(), side = document.getElementById('cm-side');
    if (c) c.style.display = showIt ? 'block' : 'none';
    if (side && !showIt) side.style.display = 'none';
    if (!showIt) clearRail();
  }

  var nameMaps = {};
  function ensureNames(market, cb) {
    if (nameMaps[market]) { cb(); return; }
    ZK.api.fetchChainmapGalaxy(market).then(function (d) {
      nameMaps[market] = {};
      if (d.ok) d.clusters.forEach(function (c) { nameMaps[market][c.id] = c.name; });
      cb();
    }).catch(function () { cb(); });
  }

  function loadCluster(cid, market, cb) {
    if (C.busy) return;
    C.busy = true;
    ZK.api.fetchChainmapCluster(cid, market)
      .then(function (d) {
        C.busy = false;
        if (!d.ok) {
          var empty = document.getElementById('cm-empty-cluster');
          if (empty) { empty.style.display = 'flex'; empty.textContent = '簇加载失败（' + (d.error || '') + '）——重进可重试'; }
          return;
        }
        C.cid = cid; C.data = d; C.market = market;
        C.cat = null;
        hideEqOverlay(true);
        render();
        ZK.api.fetchChainmapCatalyst(cid, market).then(function (cd) {
          if (C.cid !== cid || C.market !== market) return;
          if (cd && cd.ok) { C.cat = cd; decorateCatalyst(); }
        }).catch(function () { /* 静默：催化剂为增量装饰 */ });
        if (cb) cb();
      }).catch(function (err) {
        C.busy = false;
        /* 可观测性：渲染/装配异常不得吞成"API 断线"误导（2026-09-12 iFinD 重构批），真实原因上 console+空态 */
        var msg = (err && (err.message || err)) || 'API 断线';
        if (window.console && console.error) console.error('[chainmap] 簇加载/渲染失败:', err || msg);
        var empty = document.getElementById('cm-empty-cluster');
        if (empty) { empty.style.display = 'flex'; empty.textContent = '加载失败（' + msg + '）——稍后重试'; }
      });
  }

  ZK.bus.on('cm:view', function (d) { show(d.view === 'cluster'); });

  ZK.bus.on('cm:open-cluster', function (d) {
    if (!d || !d.cid) return;
    var mkt = d.market || C.market || 'all';
    C.focusChain = null; C.focusNode = null; C.focusChainName = null; C.focusOff = false; C.autoFocused = false;
    C.name = d.name || (nameMaps[mkt] && nameMaps[mkt][d.cid]) || C.name;
    show(true);
    if (C.cid === d.cid && C.market === mkt && C.data) { render(); return; }
    loadCluster(d.cid, mkt, function () { ZK.bus.emit('cm:chain-active', { chain_id: null }); });
  });

  ZK.bus.on('cm:goto-chain', function (d) {
    if (!d || !d.chain_id) return;
    var mkt = d.market || C.market || 'all';
    show(true);
    var open = function () {
      if (!C.name && nameMaps[mkt] && nameMaps[mkt][d.cluster]) C.name = nameMaps[mkt][d.cluster];
      C.focusNode = d.focus_node || null;
      focusChain(d.chain_id, d.chain_name);
      applyFocus();
      if (C.focusNode) centerOn(C.focusNode);
    };
    var go = function () {
      if (C.cid !== d.cluster || C.market !== mkt || !C.data) loadCluster(d.cluster, mkt, open);
      else open();
    };
    if (!nameMaps[mkt]) ensureNames(mkt, go); else go();
  });

  /* 市场切档（项4）：cid 是 per-market 聚类空间，切档后当前簇失效——回全景星系 */
  ZK.bus.on('cm:market', function () {
    C.data = null; C.cid = null; C.focusChain = null; C.focusChainName = null; C.focusNode = null; C.cat = null;
    if (canvasEl() && canvasEl().style.display !== 'none') {
      show(false);
      ZK.bus.emit('cm:view', { view: 'galaxy' });
    }
  });

  ZK.registerFeature({
    id: 'chainmap-cluster',
    init: function () { bindView(); },
    render: function () { if (C.data) render(); },
    destroy: function () { hideEqOverlay(true); }
  });

  if (document.getElementById('p-chainmap')) bindView();
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (C.focusChain) { unfocusFocus(); return; }   /* Esc 先取消链聚焦，再关浮层 */
    hideEqOverlay(true);
  });
})();
