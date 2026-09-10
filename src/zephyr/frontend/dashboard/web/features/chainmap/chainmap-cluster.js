/* ── 产业地图 L2 链层（族内产业链上中下游列式）· 真源 /api/chainmap-cluster + /api/chainmap-node ──
 * 分治渲染（2026-09-08 实景验收修正）：簇内 ≤RAIL_MIN 链=整族列式（链 chip 分组）；>RAIL_MIN 链=聚焦模式
 * （单链列式+左侧链选轨，146 链全画=细柱不可读）。分列=tier 三值直读 上游→中游→下游→通用（项2 适配：
 * tier 九值→三值后职能语义拆 function_role，环节卡带职能徽章，列内按职能分组聚集，后端排好序前端直用）；
 * ig_edge 结构边=SVG 贝塞尔（仅跨列，同列边不画防搅线）。点环节→右侧公司面板。
 * 跨链徽章/公司详情卡完整版=二期（Owner 2026-09-08 MVP 边界）。验收单：ACC-F-CHAINMAP-CLUSTER
 * 剩余批（2026-09-10）：股权徽章（F-CHAINMAP-EQUITY-BADGE，cluster 响应 per-node equity 聚合，
 * hover 浮层列明细、listed 行点击 cm:open-company，PERSON:/UNLISTED: 仅展示）+ 催化剂角标
 * （F-CHAINMAP-CATALYST，/api/chainmap-catalyst 零命中空态，受益清单段插环节面板顶部，
 * 方向语义=MOD-ALT-005 既有判定，个股行跳作战池=导航+诚实提示）。验收单：ACC-F-CHAINMAP-EQUITY-BADGE
 * / ACC-F-CHAINMAP-CATALYST */
(function () {
  'use strict';
  var COLS = ['上游', '中游', '下游', '通用'];
  /* function_role 八值徽章缩写（深交所词表；hover tooltip 显全称；空值不渲染） */
  var FR_SHORT = { '生产原料': '原料', '辅助材料': '辅材', '生产设备': '设备', '辅助设备': '辅设',
                   '加工工艺': '工艺', '产品业务': '产品', '技术服务': '服务', '销售渠道': '渠道' };
  var COLW = 252, NODEW = 230, NODEH = 48, CHIPH = 24, PADX = 36, PADTOP = 52, RAIL_MIN = 8;
  /* B4 甬道化（Owner 2026-09-10 裁定"参考交易决策全景效果"）：环节卡升 TDM 双行卡
   * （行1=环节名 600 加粗、行2=职能/股权徽章+公司数灰字），列头加大带底线+环节计数，
   * 连线沿用 TDM 同款贝塞尔灰蓝（#2c3a52）。列序=上中下游左→右不变。 */
  var C = { cid: null, name: '', data: null, busy: false, view: { z: 1, x: 0, y: 0 },
            pos: {}, focusChain: null, focusChainName: null, focusNode: null, market: 'all', cat: null };
  var elByNode = {};   /* node_id → 环节卡元素（聚焦高亮） */
  /* 股权 relation 中译（词表真源=ig_equity_edge DDL 封闭枚举，与 chainmap-company-card EQ_REL_ZH 同源） */
  var EQ_REL_ZH = { invests_in: '对外投资', subsidiary: '子公司', shareholding: '参股',
                    actual_control: '实控', pledge: '质押', judicial_frozen: '司法冻结' };
  var eqHideT = null;  /* 浮层延迟关闭句柄 */

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
    hideEqOverlay(true);   /* 重画前清浮层（旧卡片已销毁，钉住的浮层一并撤） */
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
    /* 列头（单链模式给链标题 chip 让位下移）；B4：列头带环节计数（TDM 列头质感） */
    var colHeadY = single ? 52 : 14;
    var colCount = {};
    groups.forEach(function (g) { g.nodes.forEach(function (n) { colCount[g.col] = (colCount[g.col] || 0) + 1; }); });
    view.cols.forEach(function (col, ci) {
      var h = document.createElement('div');
      h.className = 'cm-col-h';
      h.style.left = (PADX + ci * COLW) + 'px'; h.style.top = colHeadY + 'px';
      h.innerHTML = col + ' <span class="cc">' + (colCount[col] || 0) + '</span>';
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
        /* 股权徽章（F-CHAINMAP-EQUITY-BADGE）：环节落位公司 ∩ ig_equity_edge 有关系的才渲染 */
        var eq = n.equity, eqb = '';
        if (eq && (eq.out > 0 || eq.inn > 0)) {
          var seg = [];
          if (eq.out > 0) seg.push('控' + eq.out);
          if (eq.inn > 0) seg.push('被' + eq.inn + '控');
          eqb = '<span class="eqb" title="股权关系（ig_equity_edge）——悬停看明细">⚙' + seg.join('/') + '</span>';
        }
        el.innerHTML = '<span class="nm" title="' + n.name + '">' + disp + '</span>' +
          '<span class="sub">' +
          (n.function_role ? '<span class="fr" title="职能：' + n.function_role + '">' + (FR_SHORT[n.function_role] || n.function_role) + '</span>' : '') +
          eqb +
          '<span class="ct">' + (n.n_companies > 0 ? n.n_companies + ' 公司' : '暂无落位') + '</span>' +
          '</span>';
        if (!n.n_companies) el.classList.add('empty0');   /* 照抄 TDM 红节点板：棕虚线=暂无公司落位 */
        el.addEventListener('click', function () { openPanel(n, g.chain); });
        el.dataset.chain = g.chain.chain_id;
        elByNode[n.node_id] = el;
        bindEqBadge(el, n);
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
    decorateCatalyst();   /* 重画后补催化角标（C.cat 就绪时；零命中 no-op） */
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

  /* ── 股权徽章明细浮层（F-CHAINMAP-EQUITY-BADGE）：挂 #p-chainmap（transform 祖先之外，
   * position:fixed 视口坐标直用不受画布缩放裁剪）；listed 行点击跳公司详情卡，
   * PERSON:/UNLISTED: 行仅展示（Owner 原则：聚合层看连接、公司层靠徽章/详情）── */
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
  function bindEqBadge(el, n) {
    var badge = el.querySelector('.eqb');
    if (!badge) return;
    badge.addEventListener('mouseenter', function (e) { e.stopPropagation(); showEqOverlay(n, el); });
    badge.addEventListener('mouseleave', function () { eqHideT = setTimeout(function () { hideEqOverlay(); }, 250); });
    badge.addEventListener('click', function (e) {
      e.stopPropagation();
      var ov = eqOverlayEl();
      if (ov && ov.dataset.pin === n.node_id) { hideEqOverlay(true); return; }
      showEqOverlay(n, el);
      var o2 = eqOverlayEl();
      if (o2) o2.dataset.pin = n.node_id;
    });
  }

  /* ── 催化剂角标（F-CHAINMAP-CATALYST）：有未消化/近期事件命中的环节标"催"，
   * 点击=开环节面板（面板顶部自动插受益清单段）；零命中不渲染（禁造数据）── */
  function decorateCatalyst() {
    var cat = C.cat;
    if (!cat || !cat.nodes) return;
    Object.keys(cat.nodes).forEach(function (nid) {
      var el = elByNode[nid];
      if (!el || el.querySelector('.catb')) return;
      var hits = cat.nodes[nid] || [];
      var d = hits[0] || {};
      var b = document.createElement('span');
      b.className = 'catb';
      b.title = '催化命中 ' + hits.length + ' 条：' + (d.theme_id || '') + (d.direction || '') +
        '（' + (d.date || '') + (d.is_future ? ' · 未消化' : '') + '）——点击看受益清单';
      b.textContent = '催';
      b.addEventListener('click', function (e) { e.stopPropagation(); openPanel({ node_id: nid, name: '' }); });
      el.appendChild(b);
    });
  }

  function openPanel(n, chain) {
    var side = document.getElementById('cm-side');
    if (!side) return;
    hideEqOverlay(true);
    side.style.display = 'block';
    side.innerHTML = '<div class="dim" style="font-size:12px">加载公司落位…</div>';
    /* 催化命中的环节（C.cat 角标数据）→ 面板顶部插受益清单段（/api/chainmap-catalyst?node_id=） */
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
            '<div class="cm-sd-s">' + d.node.chain_name + ' · ' + (d.node.tier || '未标注') +
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

  var nameMaps = {};   /* market → {cid: 族名}（crumb 兜底；per-market 懒拉，后端 TTL 缓存近零成本） */
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
        C.cat = null;   /* 换簇清催化数据（旧簇角标随重画消失） */
        hideEqOverlay(true);
        render();
        /* 催化数据异步装饰（F-CHAINMAP-CATALYST）：独立降级——失败/零命中不拖垮链层，仅无角标 */
        ZK.api.fetchChainmapCatalyst(cid, market).then(function (cd) {
          if (C.cid !== cid || C.market !== market) return;   /* 已换簇/换档：丢弃旧响应 */
          if (cd && cd.ok) { C.cat = cd; decorateCatalyst(); }
        }).catch(function () { /* 静默：催化剂为增量装饰 */ });
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
    var mkt = d.market || C.market || 'all';
    C.focusChain = null; C.focusNode = null; C.focusChainName = null;
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

  /* 市场切档（项4）：cid 是 per-market 聚类空间，切档后当前簇失效——回全景星系（新档数据
   * 由 galaxy/nav 各自重拉），杜绝跨档 cid 误配 */
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
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hideEqOverlay(true); });
})();
