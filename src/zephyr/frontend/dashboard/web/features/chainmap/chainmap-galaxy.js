/* ── 产业地图 L1 星系层（族聚合全景）· 真源 /api/chainmap-galaxy（ig_* 七表，PG 只读）──
 * Owner 2026-09-08 裁定三层缩放方案：L1=族节点（按跨链供应连接 Louvain 聚类，30~48 族），
 * 力导向布局坐标 localStorage 缓存固化（同数据恒定不跳），点族进入 L2 链层。
 * 模块契约：ZK.registerFeature 注册；与 nav/search/cluster 只经 ZK.bus 通信（cm:view/cm:open-cluster）；
 * 画布容器 #cm-canvas-galaxy 本模块独占；演示诚实纪律：无演示数据，断线空态+15s 自动重试直至真源。
 * 验收单：ACC-F-CHAINMAP-GALAXY ｜ 拆分清单：docs/_working/2026-09-08-chainmap-component-split-inventory.md */
(function () {
  'use strict';
  var G = { data: null, busy: false, loaded: false, timer: null, view: { z: 1, x: 0, y: 0 }, lineByPair: null,
            market: 'all',
            loadStart: 0, elapsedTimer: null, retryCount: 0 };   /* B1 加载态（ACC rev3）：首算诚实计时+重试计数 */
  var elByCid = {};   /* cid → 节点元素（hover 邻居高亮） */

  function canvasEl() { return document.getElementById('cm-canvas-galaxy'); }
  function worldEl() { return document.getElementById('cm-world-galaxy'); }

  /* ── B1 加载态（ACC-F-CHAINMAP-GALAXY rev3 item7/8）──
   * 首算 3-6s（冷缓存最长 20s）期间画布不再是空白：星云闪烁骨架+已等待秒数诚实计数；
   * 断线转失败态（红字+暂停闪烁+重试计数），15s 自动重试机制不变；成功即隐藏。零假数据。 */
  function loadingEl() { return document.getElementById('cm-loading-galaxy'); }

  function showLoading(failMode, msg) {
    var el = loadingEl();
    if (!el) return;
    el.style.display = 'flex';
    el.classList.toggle('cm-load-fail', !!failMode);
    var t = document.getElementById('cm-loading-galaxy-t');
    var s = document.getElementById('cm-loading-galaxy-s');
    if (failMode) {
      if (t) t.textContent = 'API 断线——' + (msg || '取数失败') + '，15s 后自动重试';
      if (s) s.textContent = '已自动重试 ' + G.retryCount + ' 次 · 直至真源恢复 · 真源 ig_*（PG 只读）';
      if (G.elapsedTimer) { clearInterval(G.elapsedTimer); G.elapsedTimer = null; }
      return;
    }
    G.loadStart = Date.now();
    if (t) t.textContent = '星系聚类首算中…';
    if (G.elapsedTimer) clearInterval(G.elapsedTimer);
    var tick = function () {
      if (s) s.textContent = '已等待 ' + Math.round((Date.now() - G.loadStart) / 1000) +
        's · 首算约 3-6 秒，冷缓存最长 20 秒 · 真源 ig_*（PG 只读）';
    };
    tick();
    G.elapsedTimer = setInterval(tick, 1000);
  }

  function hideLoading() {
    var el = loadingEl();
    if (el) el.style.display = 'none';
    if (G.elapsedTimer) { clearInterval(G.elapsedTimer); G.elapsedTimer = null; }
  }

  function applyView() {
    var w = worldEl();
    if (w) w.style.transform = 'translate(' + G.view.x + 'px,' + G.view.y + 'px) scale(' + G.view.z + ')';
    var b = document.getElementById('cm-zoom-galaxy');
    if (b) b.textContent = Math.round(G.view.z * 100) + '%';
  }

  function resetView() {
    var c = canvasEl();
    if (!c || !G.data) return;
    var r = c.getBoundingClientRect();
    var W = 2600, H = 1600;
    var z = Math.min((r.width - 24) / W, (r.height - 24) / H);
    G.view = { z: Math.max(0.15, z), x: (r.width - W * z) / 2, y: (r.height - H * z) / 2 };
    applyView();
  }

  /* 交互模板（visualization_view_template.md §6.6）：滚轮缩放（光标锚点）/拖动平移/双击重置 */
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
      drag = { x: e.clientX, y: e.clientY, vx: G.view.x, vy: G.view.y };
      c.classList.add('dragging');
    });
    window.addEventListener('mousemove', function (e) {
      if (!drag) return;
      G.view.x = drag.vx + (e.clientX - drag.x);
      G.view.y = drag.vy + (e.clientY - drag.y);
      applyView();
    });
    window.addEventListener('mouseup', function () { drag = null; c.classList.remove('dragging'); });
    c.addEventListener('dblclick', function (e) { if (e.target.closest('.cm-gn')) return; resetView(); });
  }

  function zoomAt(mx, my, factor) {
    var nz = Math.max(0.15, Math.min(8, G.view.z * factor));
    var k = nz / G.view.z;
    G.view.x = mx - (mx - G.view.x) * k;
    G.view.y = my - (my - G.view.y) * k;
    G.view.z = nz;
    applyView();
  }

  /* 确定性布局 v2：大簇（≥5 公司）力导向（正规 FR：斥力 k²/d + 引力 w·d/k 线性，温度收敛），
   * 小簇/孤链 golden-angle 外环排布（ dwarf 星系带），末段全点碰撞松弛防压盖。
   * 坐标随 generated_at 缓存固化（防每次微跳）。v1 教训：引力用 d² 项在大簇间发散，重簇塌成一坨。 */
  function computeLayout(d) {
    var ns = d.clusters, ls = d.links;
    var key = 'cmGalaxy:v2:' + ns.length + ':' + ls.length + ':' + (d.generated_at || '');
    try {
      var saved = JSON.parse(localStorage.getItem(key) || 'null');
      if (saved && saved.p) return saved.p;
    } catch (e) { /* 缓存坏态重算 */ }
    var W = 2600, H = 1600, cx = W / 2, cy = H / 2, i, j;
    var pos = {}, seed = 20260908;
    function rnd() { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; }
    var MAJOR_MIN = 5;
    var majors = [], minors = [];
    ns.forEach(function (c) { (c.n_companies >= MAJOR_MIN ? majors : minors).push(c); });
    var deg = {};
    ls.forEach(function (l) { deg[l.s] = (deg[l.s] || 0) + 1; deg[l.t] = (deg[l.t] || 0) + 1; });
    var m = majors.length;
    majors.forEach(function (c, i2) {
      var a = 2 * Math.PI * i2 / Math.max(1, m);
      pos[c.id] = { x: cx + Math.cos(a) * W * 0.2 * (0.5 + rnd() * 0.5), y: cy + Math.sin(a) * H * 0.2 * (0.5 + rnd() * 0.5) };
    });
    if (m > 1) {
      var k = 0.5 * Math.sqrt(W * H / m), IT = 300;
      var isMaj = {};
      majors.forEach(function (c) { isMaj[c.id] = true; });
      var disp = {};
      for (var it = 0; it < IT; it++) {
        var t = 1 - it / IT;
        for (i = 0; i < m; i++) {
          var ia = majors[i].id, dx = 0, dy = 0;
          for (j = 0; j < m; j++) {
            if (i === j) continue;
            var ddx = pos[ia].x - pos[majors[j].id].x, ddy = pos[ia].y - pos[majors[j].id].y;
            var dd = Math.max(4, ddx * ddx + ddy * ddy);
            var dist = Math.sqrt(dd);
            var f = (k * k) / dist;   /* 斥力：短程强、长程弱 */
            dx += ddx / dist * f; dy += ddy / dist * f;
          }
          disp[ia] = { x: dx, y: dy };
        }
        ls.forEach(function (l) {
          if (!isMaj[l.s] || !isMaj[l.t]) return;
          var p = pos[l.s], q = pos[l.t];
          if (!p || !q) return;
          var ddx = p.x - q.x, ddy = p.y - q.y;
          var dist = Math.sqrt(ddx * ddx + ddy * ddy) || 1;
          var wgt = Math.min(2.2, Math.log10(l.w + 1) || 0.3);
          var f = (dist / k) * wgt;   /* 引力：线性于距离（d² 会发散塌团） */
          disp[l.s].x -= ddx / dist * f; disp[l.s].y -= ddy / dist * f;
          disp[l.t].x += ddx / dist * f; disp[l.t].y += ddy / dist * f;
        });
        for (i = 0; i < m; i++) {
          var id = majors[i].id, vx = disp[id].x, vy = disp[id].y;
          var dl = Math.sqrt(vx * vx + vy * vy) || 1;
          var lim = Math.min(dl, t * 26 + 2);
          pos[id].x = Math.max(140, Math.min(W - 140, pos[id].x + vx / dl * lim));
          pos[id].y = Math.max(110, Math.min(H - 110, pos[id].y + vy / dl * lim));
        }
      }
    }
    /* 小簇带：golden-angle 椭圆环包住大簇区（矮星系视觉，不跟大簇抢中心） */
    if (minors.length) {
      var bx0 = 1e9, bx1 = -1e9, by0 = 1e9, by1 = -1e9;
      majors.forEach(function (c) {
        var p = pos[c.id];
        if (!p) return;
        bx0 = Math.min(bx0, p.x); bx1 = Math.max(bx1, p.x);
        by0 = Math.min(by0, p.y); by1 = Math.max(by1, p.y);
      });
      if (!majors.length) { bx0 = cx - 200; bx1 = cx + 200; by0 = cy - 150; by1 = cy + 150; }
      var rcx = (bx0 + bx1) / 2, rcy = (by0 + by1) / 2;
      var rx = (bx1 - bx0) / 2 + 190, ry = (by1 - by0) / 2 + 150;
      minors.forEach(function (c, i2) {
        var a = i2 * 2.399963 + 0.7;
        pos[c.id] = {
          x: Math.max(110, Math.min(W - 110, rcx + Math.cos(a) * rx * (1 + (i2 % 3) * 0.14))),
          y: Math.max(90, Math.min(H - 90, rcy + Math.sin(a) * ry * (1 + (i2 % 3) * 0.18)))
        };
      });
    }
    /* 全点碰撞松弛（半径=节点圆 + 间距 14），防压盖 */
    var rad = {};
    ns.forEach(function (c) { rad[c.id] = radiusOf(c.n_companies) + 14; });
    for (var pass = 0; pass < 180; pass++) {
      for (i = 0; i < ns.length; i++) {
        for (j = i + 1; j < ns.length; j++) {
          var A = ns[i].id, B = ns[j].id, pa = pos[A], pb = pos[B];
          if (!pa || !pb) continue;
          var ddx = pb.x - pa.x, ddy = pb.y - pa.y;
          var dist = Math.sqrt(ddx * ddx + ddy * ddy) || 0.5;
          var min = rad[A] + rad[B];
          if (dist < min) {
            var push = (min - dist) / dist * 0.5;
            pa.x -= ddx * push; pa.y -= ddy * push;
            pb.x += ddx * push; pb.y += ddy * push;
          }
        }
      }
      ns.forEach(function (c) {
        var p = pos[c.id];
        if (!p) return;
        p.x = Math.max(110, Math.min(W - 110, p.x));
        p.y = Math.max(90, Math.min(H - 90, p.y));
      });
    }
    try { localStorage.setItem(key, JSON.stringify({ p: pos })); } catch (e) { /* 存不下则每次重算 */ }
    return pos;
  }

  function radiusOf(nCompanies) {
    return Math.min(26 + Math.sqrt(nCompanies || 1) * 1.9, 92);
  }

  function render() {
    var d = G.data;
    if (!d) return;
    var world = worldEl(), svg = document.getElementById('cm-wires-galaxy'), host = document.getElementById('cm-nodes-galaxy');
    var empty = document.getElementById('cm-empty-galaxy');
    if (!world || !svg || !host) return;
    var W = 2600, H = 1600;
    svg.setAttribute('width', W); svg.setAttribute('height', H);
    world.style.width = W + 'px'; world.style.height = H + 'px';
    host.innerHTML = ''; svg.innerHTML = '';
    if (!d.clusters.length) {
      if (empty) { empty.style.display = 'flex'; empty.textContent = '无族数据（ig_* 表为空或聚类退化）'; }
      return;
    }
    if (empty) empty.style.display = 'none';
    var pos = computeLayout(d);
    /* 边层：粗细=连接强度（公司供应链边去重计数），透明度随权重 */
    G.lineByPair = {};
    var frag = document.createDocumentFragment();
    d.links.forEach(function (l) {
      var p = pos[l.s], q = pos[l.t];
      if (!p || !q) return;
      var ln = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      ln.setAttribute('x1', p.x); ln.setAttribute('y1', p.y);
      ln.setAttribute('x2', q.x); ln.setAttribute('y2', q.y);
      ln.setAttribute('stroke', '#3d8bff');
      ln.setAttribute('stroke-width', (0.6 + Math.log10(l.w + 1) * 1.6).toFixed(2));
      ln.setAttribute('opacity', Math.min(0.5, 0.1 + l.w / 900).toFixed(3));
      frag.appendChild(ln);
      (G.lineByPair[l.s] = G.lineByPair[l.s] || {})[l.t] = ln;
      (G.lineByPair[l.t] = G.lineByPair[l.t] || {})[l.s] = ln;
    });
    svg.appendChild(frag);
    /* 点层：大小=公司数，颜色单色系 #3D8BFF 低饱和（Owner UI 纪律） */
    d.clusters.forEach(function (c) {
      var p = pos[c.id];
      if (!p) return;
      var r = radiusOf(c.n_companies);
      var el = document.createElement('div');
      el.className = 'cm-gn';
      el.style.left = (p.x - r) + 'px'; el.style.top = (p.y - r) + 'px';
      el.style.width = (r * 2) + 'px'; el.style.height = (r * 2) + 'px';
      el.style.fontSize = Math.max(10.5, Math.min(15, r / 4.2)).toFixed(1) + 'px';
      el.innerHTML = '<div class="cm-gn-n" title="' + c.name + '（' + c.n_chains + ' 链 · ' + c.n_companies + ' 公司）">' + c.name + '</div>' +
        (r < 32 ? '' : '<div class="cm-gn-s">' + c.n_companies + ' 公司 · ' + c.n_chains + ' 链</div>');
      el.addEventListener('mouseenter', function () { highlight(c.id, true); });
      el.addEventListener('mouseleave', function () { highlight(c.id, false); });
      el.addEventListener('click', function () {
        ZK.bus.emit('cm:view', { view: 'cluster' });
        ZK.bus.emit('cm:open-cluster', { cid: c.id, name: c.name, market: G.market });
      });
      host.appendChild(el);
    });
    resetView();
    var meta = document.getElementById('cm-meta');
    if (meta) {
      meta.textContent = d.clusters.length + ' 族 · ' + d.chains.length + ' 链 · ' +
        d.clusters.reduce(function (s, c) { return s + c.n_companies; }, 0) + ' 公司（去重口径另计） · 真源 ig_*（PG 只读） · ' + d.generated_at;
      meta.classList.remove('cm-bad');
    }
    setCrumb();
  }

  function highlight(cid, on) {
    var c = canvasEl();
    if (!c || !G.lineByPair) return;
    c.classList.toggle('cm-fade', on);
    var links = G.lineByPair[cid] || {};
    Object.keys(links).forEach(function (k) { links[k].classList.toggle('cm-on', on); });
    Object.keys(elByCid).forEach(function (k) {
      elByCid[k].classList.toggle('cm-on', !!(on && (k === cid || links[k])));
    });
  }

  function setCrumb() {
    var cr = document.getElementById('cm-crumb');
    if (cr) cr.textContent = '产业地图 · 全景星系';
  }

  function load() {
    if (G.busy) return;
    G.busy = true;
    showLoading(false);   /* B1：每次取数周期进入加载态（重试周期亦然） */
    ZK.api.fetchChainmapGalaxy(G.market).then(function (d) {
      G.busy = false;
      if (!d.ok) { fail(d.error || '后端返回失败'); return; }
      G.loaded = true;
      G.retryCount = 0;
      hideLoading();
      G.data = d;
      elByCid = {};
      var host = document.getElementById('cm-nodes-galaxy');
      render();
      /* 渲染后建 cid→元素映射（hover 高亮用） */
      if (host) {
        var kids = host.children, idx = 0;
        d.clusters.forEach(function (c) {
          if (kids[idx]) elByCid[c.id] = kids[idx];
          idx++;
        });
      }
    }).catch(function (e) { G.busy = false; fail(e && e.message || 'fetch 失败'); });
  }

  function fail(msg) {
    G.retryCount += 1;
    showLoading(true, msg);   /* B1：画布内失败态（meta 行同步保底，双通道不冲突） */
    var meta = document.getElementById('cm-meta');
    if (meta) {
      meta.textContent = 'API 断线（' + msg + '）—— 15s 后自动重试直至真源';
      meta.classList.add('cm-bad');
    }
    if (!G.timer) G.timer = setInterval(function () {
      if (G.loaded) { clearInterval(G.timer); G.timer = null; return; }
      if (!visible()) return;   /* 页面隐藏不空转，回页自然重试 */
      load();
    }, 15000);
  }

  function visible() {
    var el = document.getElementById('p-chainmap');
    return el && el.offsetParent !== null;
  }

  ZK.bus.on('cm:view', function (d) {
    var c = canvasEl();
    if (!c) return;
    var show = d.view === 'galaxy';
    c.style.display = show ? 'block' : 'none';
    if (show) { setCrumb(); if (!G.loaded) load(); }
  });

  /* 市场切档（项4）：galaxy 是簇空间本尊——重拉当前档数据重渲染；meta 行 counts 随档真实变化 */
  ZK.bus.on('cm:market', function (d) {
    G.market = (d && d.market) || 'all';
    G.loaded = false;
    G.data = null;
    if (visible()) load();
  });

  function boot() {
    bindView();
    if (visible()) load();
    else {
      var t = setInterval(function () {
        if (G.loaded || visible()) { clearInterval(t); if (!G.loaded) load(); }
      }, 1200);
    }
  }

  ZK.registerFeature({
    id: 'chainmap-galaxy',
    init: function () { boot(); },
    render: function () { render(); },
    destroy: function () { if (G.timer) clearInterval(G.timer); if (G.elapsedTimer) { clearInterval(G.elapsedTimer); G.elapsedTimer = null; } }
  });

  if (document.getElementById('p-chainmap')) boot();
})();
