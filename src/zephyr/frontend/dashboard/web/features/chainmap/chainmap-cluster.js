/* ── 产业地图 L2 链层（族内产业链上中下游列式）· 真源 /api/chainmap-cluster + /api/chainmap-node ──
 * 分治渲染（2026-09-08 实景验收修正）：簇内 ≤RAIL_MIN 链=整族列式（链 chip 分组）；>RAIL_MIN 链=聚焦模式
 * （单链列式+左侧链选轨，146 链全画=细柱不可读）。tier 分桶列 上游→中游→下游→其他→通用；
 * ig_edge 结构边=SVG 贝塞尔（仅跨列，同列边不画防搅线）。点环节→右侧公司面板。
 * 跨链徽章/公司详情卡完整版=二期（Owner 2026-09-08 MVP 边界）。验收单：ACC-F-CHAINMAP-CLUSTER */
(function () {
  'use strict';
  var COLS = ['上游', '中游', '下游', '其他', '通用'];
  var COLW = 252, NODEW = 230, NODEH = 34, CHIPH = 24, PADX = 36, PADTOP = 46, RAIL_MIN = 8;
  var C = { cid: null, name: '', data: null, busy: false, view: { z: 1, x: 0, y: 0 },
            pos: {}, focusChain: null, focusChainName: null, focusNode: null };
  var elByNode = {};   /* node_id → 环节卡元素（聚焦高亮） */

  function canvasEl() { return document.getElementById('cm-canvas-cluster'); }
  function worldEl() { return document.getElementById('cm-world-cluster'); }

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
    c.addEventListener('dblclick', function (e) { if (e.target.closest('.cm-n, .cm-chip, .cm-rail')) return; fitView(); });
  }

  function zoomAt(mx, my, factor) {
    var nz = Math.max(0.2, Math.min(6, C.view.z * factor));
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
    C.view = { z: z, x: railW + (r.width - railW) / 2 - (p.x + NODEW / 2) * z, y: r.height / 2 - (p.y + NODEH / 2) * z };
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

  /* 列式确定性布局：view= {chains, edges, cols, worldW, worldH, padTop}。
   * 整族模式：链=chip 分组（公司数降序），链跨列时每列各挂 chip（组头随列走）；
   * 单链模式（single）：免重复 chip，仅链标题一枚，环节按列堆叠。 */
  function layout(view) {
    var colSet = {};
    view.chains.forEach(function (ch) {
      ch.nodes.forEach(function (n) { if (!colSet[n.col]) colSet[n.col] = true; });
    });
    var cols = COLS.filter(function (c) { return colSet[c]; });
    if (view.single) {   /* 单链：仅保留该链实际用到的列 */
      var used = {};
      view.chains[0].nodes.forEach(function (n) { used[n.col] = true; });
      cols = COLS.filter(function (c) { return used[c]; });
    }
    if (!cols.length) cols = ['通用'];
    var y0 = view.padTop || PADTOP;
    var nodePos = {}, groups = [];
    var maxBottom = y0;
    cols.forEach(function (col, ci) {
      var x = PADX + ci * COLW;
      var y = y0;
      var list = view.chains.filter(function (ch) {
        return ch.nodes.some(function (n) { return n.col === col; });
      });
      list.forEach(function (ch) {
        var ns = ch.nodes.filter(function (n) { return n.col === col; });
        groups.push({ chain: ch, col: col, x: x, y: y, nodes: ns, chip: !view.single });
        y += (view.single ? 0 : CHIPH + 9);
        ns.forEach(function (n) {
          nodePos[n.node_id] = { x: x, y: y, col: col };
          y += NODEH + 8;
        });
        y += 14;
      });
      maxBottom = Math.max(maxBottom, y);
    });
    view.worldW = PADX * 2 + cols.length * COLW;
    view.worldH = maxBottom + 50;
    view.cols = cols;
    C.pos = nodePos;
    C.viewData = view;
    return groups;
  }

  function render() {
    var d = C.data;
    if (!d) return;
    clearRail();
    if (d.chains.length > RAIL_MIN) renderFocused(d);
    else drawView(d, false);
  }

  function drawView(view, single) {
    var world = worldEl(), svg = document.getElementById('cm-wires-cluster'), host = document.getElementById('cm-nodes-cluster');
    var empty = document.getElementById('cm-empty-cluster');
    if (!world || !svg || !host) return;
    svg.setAttribute('width', view.worldW); svg.setAttribute('height', view.worldH);
    world.style.width = view.worldW + 'px'; world.style.height = view.worldH + 'px';
    host.innerHTML = ''; svg.innerHTML = '';
    if (!view.chains.length || (single && !view.chains[0].nodes.length)) {
      if (empty) { empty.style.display = 'flex'; empty.textContent = '该簇/链无环节数据'; }
      return;
    }
    if (empty) empty.style.display = 'none';
    if (single) view.padTop = PADTOP + 36;   /* 单链模式：链标题 chip 占位，环节下移防压列头（列头 48） */
    var groups = layout(view);
    var frag = document.createDocumentFragment();
    /* 列头（单链模式给链标题 chip 让位下移） */
    var colHeadY = single ? 48 : 12;
    view.cols.forEach(function (col, ci) {
      var h = document.createElement('div');
      h.className = 'cm-col-h';
      h.style.left = (PADX + ci * COLW) + 'px'; h.style.top = colHeadY + 'px';
      h.textContent = col;
      frag.appendChild(h);
    });
    if (single) {   /* 链标题一枚（免重复链头） */
      var ch = view.chains[0];
      var t = document.createElement('div');
      t.className = 'cm-chip';
      t.style.left = PADX + 'px'; t.style.top = '10px'; t.style.width = NODEW + 'px';
      t.textContent = ch.name + ' · ' + ch.n_companies;
      t.title = ch.name + '（' + ch.nodes.length + ' 环节 · ' + ch.n_companies + ' 公司）';
      frag.appendChild(t);
    }
    groups.forEach(function (g) {
      if (g.chip) {
        var chip = document.createElement('div');
        chip.className = 'cm-chip';
        chip.style.left = g.x + 'px'; chip.style.top = g.y + 'px'; chip.style.width = NODEW + 'px';
        chip.textContent = g.chain.name + ' · ' + g.chain.n_companies;
        chip.title = g.chain.name + '（' + g.chain.nodes.length + ' 环节 · ' + g.chain.n_companies + ' 公司）';
        chip.addEventListener('click', function () { focusChain(g.chain.chain_id, g.chain.name); });
        chip.dataset.chain = g.chain.chain_id;
        frag.appendChild(chip);
      }
      g.nodes.forEach(function (n) {
        var p = C.pos[n.node_id];
        var el = document.createElement('div');
        el.className = 'cm-n';
        el.style.left = p.x + 'px'; el.style.top = p.y + 'px'; el.style.width = NODEW + 'px'; el.style.height = NODEH + 'px';
        /* 显示名去链名前缀（数据侧节点名常为「链名-环节」全称，卡内展示冗余；title 保留全称） */
        var disp = n.name;
        var pfx = g.chain.name + '-';
        if (disp.indexOf(pfx) === 0 && disp.length > pfx.length) disp = disp.slice(pfx.length);
        el.innerHTML = '<span class="nm" title="' + n.name + '">' + disp + '</span><span class="ct">' + n.n_companies + '</span>';
        el.addEventListener('click', function () { openPanel(n, g.chain); });
        el.dataset.chain = g.chain.chain_id;
        elByNode[n.node_id] = el;
        frag.appendChild(el);
      });
    });
    host.appendChild(frag);
    /* 结构边：仅跨列（同列边不画防搅线），方向=源列→目标列 */
    var sfrag = document.createDocumentFragment();
    view.edges.forEach(function (e) {
      var a = C.pos[e[0]], b = C.pos[e[1]];
      if (!a || !b || a.col === b.col) return;
      var p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      var aLeft = view.cols.indexOf(a.col) <= view.cols.indexOf(b.col);
      var x1 = aLeft ? a.x + NODEW : a.x, y1 = a.y + NODEH / 2;
      var x2 = aLeft ? b.x : b.x + NODEW, y2 = b.y + NODEH / 2;
      var mx = (x1 + x2) / 2;
      p.setAttribute('d', 'M' + x1 + ',' + y1 + ' C' + mx + ',' + y1 + ' ' + mx + ',' + y2 + ' ' + x2 + ',' + y2);
      sfrag.appendChild(p);
    });
    svg.appendChild(sfrag);
    applyFocus();
    fitView();
  }

  /* 聚焦模式（>RAIL_MIN 链的大簇）：单链列式+左侧链选轨（默认聚焦公司数最大链） */
  function renderFocused(d) {
    var ch = d.chains.filter(function (c) { return c.chain_id === C.focusChain; })[0] || d.chains[0];
    C.focusChain = ch.chain_id;
    C.focusChainName = ch.name;
    var idset = {};
    ch.nodes.forEach(function (n) { idset[n.node_id] = true; });
    var view = { chains: [ch], single: true, worldW: 0, worldH: 0, cols: [],
                 edges: d.edges.filter(function (e) { return idset[e[0]] && idset[e[1]]; }) };
    drawView(view, true);
    buildRail(d, ch.chain_id);
    fitView();
    if (C.focusNode) centerOn(C.focusNode);
    setCrumb(ch.name);
    ZK.bus.emit('cm:chain-active', { chain_id: ch.chain_id });
    var meta = document.getElementById('cm-meta');
    if (meta) {
      meta.textContent = C.name + ' › ' + ch.name + ' · ' + ch.nodes.length + ' 环节 · 公司位 ' + ch.n_companies +
        ' · 结构边 ' + view.edges.length + ' · 换链用左侧选单 · 真源 ig_*（PG 只读）';
      meta.classList.remove('cm-bad');
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
    head.textContent = '链选单 · ' + d.chains.length;
    rail.appendChild(head);
    d.chains.forEach(function (ch) {
      var r = document.createElement('div');
      r.className = 'cm-rail-i' + (ch.chain_id === activeId ? ' act' : '');
      r.innerHTML = '<span class="nm" title="' + ch.name + '">' + ch.name + '</span><span class="ct">' + ch.n_companies + '</span>';
      r.addEventListener('click', function () {
        C.focusChain = ch.chain_id; C.focusChainName = ch.name; C.focusNode = null;
        renderFocused(C.data);
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
    if (C.data && C.data.chains.length > RAIL_MIN) renderFocused(C.data);
    else { applyFocus(); setCrumb(C.focusChainName); }
    ZK.bus.emit('cm:chain-active', { chain_id: chainId });
  }

  function applyFocus() {
    var host = document.getElementById('cm-nodes-cluster');
    if (!host) return;
    var multi = C.data && C.data.chains.length <= RAIL_MIN;   /* 整族模式才淡化他链；聚焦模式全体同链 */
    Array.prototype.forEach.call(host.children, function (el) {
      if (!el.dataset.chain) return;
      el.classList.toggle('dimmed', multi && !!C.focusChain && el.dataset.chain !== C.focusChain);
      el.classList.remove('hit');
    });
    if (C.focusNode && byIdEl(C.focusNode)) byIdEl(C.focusNode).classList.add('hit');
  }

  function byIdEl(nodeId) {
    return elByNode[nodeId] || null;
  }

  function openPanel(n, chain) {
    var side = document.getElementById('cm-side');
    if (!side) return;
    side.style.display = 'block';
    side.innerHTML = '<div class="dim" style="font-size:12px">加载公司落位…</div>';
    ZK.api.fetchChainmapNode(n.node_id)
      .then(function (d) {
        if (!d.ok) { side.innerHTML = '<div class="cm-bad" style="font-size:12px">加载失败：' + (d.error || '') + '</div>'; return; }
        var rows = d.companies.map(function (cp) {
          var cls = (cp.role.indexOf('龙头') >= 0 || cp.role === '核心') ? 'lead' : (cp.role === '参与' ? 'join' : '');
          return '<div class="cm-co"><span class="rl ' + cls + '">' + (cp.role || '提及') + '</span>' +
            '<span class="nm" title="' + cp.name + '">' + (cp.name || '—') + '</span>' +
            '<span class="sy">' + cp.symbol + '</span><span class="cf">' + (cp.confidence == null ? '' : cp.confidence.toFixed(2)) + '</span></div>';
        }).join('');
        side.innerHTML =
          '<span class="cm-x" title="关闭">✕</span>' +
          '<div class="cm-sd-t">' + d.node.name + '</div>' +
          '<div class="cm-sd-s">' + d.node.chain_name + ' · ' + (d.node.tier || '未标注') +
          ' ｜ 公司 ' + d.total + ' 家（按角色/置信度排序，最多展示 200）</div>' +
          (rows || '<div class="dim" style="font-size:12px">该环节暂无公司映射</div>');
        var x = side.querySelector('.cm-x');
        if (x) x.addEventListener('click', function () { side.style.display = 'none'; });
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

  var nameMap = null;   /* cid → 族名（crumb 兜底；懒拉一次 galaxy，后端 TTL 缓存近零成本） */
  function ensureNames(cb) {
    if (nameMap) { cb(); return; }
    ZK.api.fetchChainmapGalaxy().then(function (d) {
      nameMap = {};
      if (d.ok) d.clusters.forEach(function (c) { nameMap[c.id] = c.name; });
      cb();
    }).catch(function () { cb(); });
  }

  function loadCluster(cid, cb) {
    if (C.busy) return;
    C.busy = true;
    ZK.api.fetchChainmapCluster(cid)
      .then(function (d) {
        C.busy = false;
        if (!d.ok) {
          var empty = document.getElementById('cm-empty-cluster');
          if (empty) { empty.style.display = 'flex'; empty.textContent = '簇加载失败（' + (d.error || '') + '）——重进可重试'; }
          return;
        }
        C.cid = cid; C.data = d;
        render();
        if (cb) cb();
      }).catch(function () {
        C.busy = false;
        var empty = document.getElementById('cm-empty-cluster');
        if (empty) { empty.style.display = 'flex'; empty.textContent = 'API 断线——稍后重试'; }
      });
  }

  ZK.bus.on('cm:view', function (d) { show(d.view === 'cluster'); });

  ZK.bus.on('cm:open-cluster', function (d) {
    if (!d || !d.cid) return;
    C.focusChain = null; C.focusNode = null; C.focusChainName = null;
    C.name = d.name || (nameMap && nameMap[d.cid]) || C.name;
    show(true);
    if (C.cid === d.cid && C.data) { render(); return; }
    loadCluster(d.cid, function () { ZK.bus.emit('cm:chain-active', { chain_id: null }); });
  });

  ZK.bus.on('cm:goto-chain', function (d) {
    if (!d || !d.chain_id) return;
    show(true);
    var open = function () {
      if (!C.name && nameMap && nameMap[d.cluster]) C.name = nameMap[d.cluster];
      C.focusNode = d.focus_node || null;
      focusChain(d.chain_id, d.chain_name);
      applyFocus();
      if (C.focusNode) centerOn(C.focusNode);
    };
    var go = function () {
      if (C.cid !== d.cluster || !C.data) loadCluster(d.cluster, open);
      else open();
    };
    if (!nameMap) ensureNames(go); else go();
  });

  ZK.registerFeature({
    id: 'chainmap-cluster',
    init: function () { bindView(); },
    render: function () { if (C.data) render(); },
    destroy: function () { /* 无定时器 */ }
  });

  if (document.getElementById('p-chainmap')) bindView();
})();
