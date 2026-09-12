/* ── 产业地图 L1 星系层 · 3D 族星云（B2 一期，Owner 2026-09-10 裁定 3D 化）· 真源 /api/chainmap-galaxy（ig_* 七表，PG 只读）──
 * 47 族 Fibonacci 球面撒点（族越大星越大，确定性几何分布免布局缓存）；拖拽旋转/滚轮推拉/键盘方向/
 * 双击复位；hover 高亮直连邻接；点星进 L2 链层（cm:view/cm:open-cluster 契约不变）。
 * 渲染=three.js r147 UMD（vendor/three/，dockview vendor 先例）；轨道相机手搓球坐标（~60 行，
 * 免 examples/OrbitControls 版本耦合）。旧 2D 力导向渲染退役（git 历史留存）。
 * 模块契约：ZK.registerFeature 注册；与 nav/search/cluster 只经 ZK.bus 通信（cm:view/cm:market）；
 * 画布容器 #cm-canvas-galaxy 本模块独占；演示诚实纪律：无演示数据，断线空态+15s 自动重试；
 * WebGL/three 缺失→诚实报错不做 2D 假降级。验收单：ACC-F-CHAINMAP-GALAXY（rev4）
 * ｜ 拆分清单：docs/_working/2026-09-08-chainmap-component-split-inventory.md
 * ── L1 一级总图（2026-09-12 Owner 拍板④：星云保留+同风格 iFinD 总图，顶栏「星云/总图」切换）──
 * 族=分区底板（蛇形排布）、链=小等距块（大小=公司数）、族间流向线=links 权重投影；
 * 点链块=cm:goto-chain 直达链视图、点底板=cm:open-cluster 进链层；纯 SVG 渲染
 * （#cm-wires-overview 唯一画布），数据同源 galaxy 响应（clusters+links+chains），后端零改动。 */
(function () {
  'use strict';
  var G = { data: null, busy: false, loaded: false, timer: null, market: 'all',
            loadStart: 0, elapsedTimer: null, retryCount: 0,   /* B1 加载态（ACC rev3） */
            loadState: null, mode: '3d',                       /* L1 形态：3d=星云 / ifind=iFinD 总图；loadState=加载/失败态（跨画布共用覆盖层） */
            gl: null, raf: 0, birth: 0, lastPick: null,        /* gl=3D 引擎句柄（initGL 建见注释） */
            ov: { z: 1, x: 0, y: 0 } };                        /* 总图视图（缩放/平移） */
  /* B3 族内链群小星云已撤（Owner 2026-09-10 实测裁定"不用星云了"：族内内容天然带上中下游
   * 序，点族星直开链层列式甬道=chainmap-cluster，B4 按 TDM 视觉升级）——代码见 git 历史 */

  function canvasEl() { return document.getElementById('cm-canvas-galaxy'); }
  function glEl() { return document.getElementById('cm-gl-galaxy'); }
  function loadingEl() { return document.getElementById('cm-loading-galaxy'); }

  /* ── B1 加载态（ACC-F-CHAINMAP-GALAXY rev3 item7/8）──
   * 首算 3-6s（冷缓存最长 20s）期间画布不再是空白：星云闪烁骨架+已等待秒数诚实计数；
   * 断线转失败态（红字+暂停闪烁+重试计数），15s 自动重试机制不变；成功即隐藏。零假数据。
   * 2026-09-12：覆盖层升级为两 L1 画布共用（stage 级），仅当任一 L1 画布可见时显示，
   * 不遮 L2 链层。 */
  function canvasVisible(c) { return !!(c && c.style.display !== 'none'); }
  function l1Visible() { return canvasVisible(canvasEl()) || canvasVisible(ovCanvasEl()); }

  function showLoading(failMode, msg) {
    G.loadState = { fail: !!failMode, msg: msg || '' };
    if (!failMode) G.loadStart = Date.now();
    refreshLoading();
  }

  function refreshLoading() {
    var el = loadingEl();
    if (!el) return;
    var st = G.loadState;
    if (!st || !l1Visible()) {
      el.style.display = 'none';
      if (G.elapsedTimer) { clearInterval(G.elapsedTimer); G.elapsedTimer = null; }
      return;
    }
    el.style.display = 'flex';
    el.classList.toggle('cm-load-fail', st.fail);
    var t = document.getElementById('cm-loading-galaxy-t');
    var s = document.getElementById('cm-loading-galaxy-s');
    if (st.fail) {
      if (t) t.textContent = 'API 断线——' + (st.msg || '取数失败') + '，15s 后自动重试';
      if (s) s.textContent = '已自动重试 ' + G.retryCount + ' 次 · 直至真源恢复 · 真源 ig_*（PG 只读）';
      if (G.elapsedTimer) { clearInterval(G.elapsedTimer); G.elapsedTimer = null; }
      return;
    }
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
    G.loadState = null;
    var el = loadingEl();
    if (el) el.style.display = 'none';
    if (G.elapsedTimer) { clearInterval(G.elapsedTimer); G.elapsedTimer = null; }
  }

  /* ── 3D 引擎（three.js r147 UMD + 手搓轨道相机）──
   * gl={renderer,scene,camera,tex,group,stars:{cid:sprite},starList:[{cid,sprite,base}],
   *     lines:[{s,t,line,baseOp}],linkByPair:{cid:{cid:true}},labels:{cid:el},labelHost,
   *     sph:{theta,phi,r},drag,mouse,ray,hover} */
  var SPH0 = { theta: 0.55, phi: 1.25, r: 340 };

  function glAvailable() {
    try {
      var c = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (c.getContext('webgl') || c.getContext('experimental-webgl')));
    } catch (e) { return false; }
  }

  function glDegrade(reason) {
    var el = loadingEl();
    if (el) {
      if (!canvasVisible(canvasEl())) return;   /* 覆盖层已归总图/L2 场景，别越界遮他画布 */
      el.style.display = 'flex';
      el.classList.add('cm-load-fail');
      var t = document.getElementById('cm-loading-galaxy-t');
      var s = document.getElementById('cm-loading-galaxy-s');
      if (t) t.textContent = '3D 渲染不可用——' + reason;
      if (s) s.textContent = '请用 Chrome / Electron 壳打开（WebGL 必需）· 数据接口无恙';
    }
    var meta = document.getElementById('cm-meta');
    if (meta) { meta.textContent = '3D 渲染不可用（' + reason + '）——/api/chainmap-galaxy 数据接口本身无恙'; meta.classList.add('cm-bad'); }
  }

  function glowTexture() {
    var c = document.createElement('canvas'); c.width = c.height = 128;
    var g = c.getContext('2d');
    var gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, 'rgba(216,232,255,1)');
    gr.addColorStop(0.25, 'rgba(122,176,255,.9)');
    gr.addColorStop(0.6, 'rgba(61,139,255,.30)');
    gr.addColorStop(1, 'rgba(61,139,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
    return new THREE.CanvasTexture(c);
  }

  function initGL() {
    if (G.gl) return G.gl;
    if (typeof THREE === 'undefined') { glDegrade('three.js 库未加载（vendor/three/）'); return null; }
    if (!glAvailable()) { glDegrade('WebGL 不可用'); return null; }
    var renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas: glEl(), antialias: true, alpha: true });
    } catch (e) { glDegrade('WebGL 初始化失败'); return null; }
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(55, 1, 1, 4000);
    /* 背景尘星：远球薄壳随机点（纯装饰坐标，非业务数据，演示诚实纪律不受限） */
    (function () {
      var n = 420, pos = new Float32Array(n * 3);
      for (var i = 0; i < n; i++) {
        var u = Math.random() * 2 - 1, a = Math.random() * Math.PI * 2;
        var r = 700 + Math.random() * 250, s = Math.sqrt(1 - u * u);
        pos[i * 3] = r * s * Math.cos(a); pos[i * 3 + 1] = r * u; pos[i * 3 + 2] = r * s * Math.sin(a);
      }
      var geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      scene.add(new THREE.Points(geo, new THREE.PointsMaterial({ color: 0x7d8aa0, size: 1.6, transparent: true, opacity: 0.4, sizeAttenuation: false })));
    })();
    G.gl = { renderer: renderer, scene: scene, camera: camera, tex: glowTexture(),
             group: null, stars: {}, starList: [], lines: [], linkByPair: {},
             labels: {}, labelHost: document.getElementById('cm-labels-galaxy'),
             sph: { theta: SPH0.theta, phi: SPH0.phi, r: SPH0.r },
             drag: null, mouse: { x: -9, y: -9 }, ray: new THREE.Raycaster(), hover: null };
    bindView3D();
    return G.gl;
  }

  /* 轨道相机：球坐标→相机位姿（手搓 ~60 行核心，免 OrbitControls 依赖） */
  function applyCamera() {
    var gl = G.gl, s = gl.sph;
    var sp = Math.sin(s.phi);
    gl.camera.position.set(s.r * sp * Math.sin(s.theta), s.r * Math.cos(s.phi), s.r * sp * Math.cos(s.theta));
    gl.camera.lookAt(0, 0, 0);
  }

  function bindView3D() {
    var el = glEl();
    if (!el || el.dataset.bound) return;
    el.dataset.bound = '1';
    el.addEventListener('wheel', function (e) {
      e.preventDefault();
      var gl = G.gl; if (!gl) return;
      gl.sph.r = Math.max(90, Math.min(620, gl.sph.r * (e.deltaY < 0 ? 0.9 : 1.1)));
    }, { passive: false });
    el.addEventListener('pointerdown', function (e) {
      var gl = G.gl; if (!gl) return;
      gl.drag = { x: e.clientX, y: e.clientY, th: gl.sph.theta, ph: gl.sph.phi, moved: 0 };
      el.classList.add('dragging');
    });
    window.addEventListener('pointermove', function (e) {
      var gl = G.gl; if (!gl) return;
      var c = glEl(); if (!c) return;
      var r = c.getBoundingClientRect();
      gl.mouse.x = ((e.clientX - r.left) / r.width) * 2 - 1;
      gl.mouse.y = -((e.clientY - r.top) / r.height) * 2 + 1;
      if (!gl.drag) return;
      var dx = e.clientX - gl.drag.x, dy = e.clientY - gl.drag.y;
      gl.drag.moved = Math.max(gl.drag.moved, Math.abs(dx) + Math.abs(dy));
      gl.sph.theta = gl.drag.th - dx * 0.005;
      gl.sph.phi = Math.max(0.15, Math.min(Math.PI - 0.15, gl.drag.ph - dy * 0.005));
    });
    window.addEventListener('pointerup', function (e) {
      var gl = G.gl; if (!gl || !gl.drag) return;
      var moved = gl.drag.moved; gl.drag = null;
      var c = glEl(); if (c) c.classList.remove('dragging');
      if (moved < 6) clickPick(e);   /* 位移<6px 视为点击（点星进簇） */
    });
    el.addEventListener('dblclick', function () {
      var gl = G.gl; if (!gl) return;
      gl.sph.theta = SPH0.theta; gl.sph.phi = SPH0.phi; gl.sph.r = SPH0.r;
    });
    window.addEventListener('keydown', function (e) {
      if (!visible()) return;
      var gl = G.gl; if (!gl) return;
      var d = 0.06;
      if (e.key === 'ArrowLeft') gl.sph.theta -= d;
      else if (e.key === 'ArrowRight') gl.sph.theta += d;
      else if (e.key === 'ArrowUp') gl.sph.phi = Math.max(0.15, gl.sph.phi - d);
      else if (e.key === 'ArrowDown') gl.sph.phi = Math.min(Math.PI - 0.15, gl.sph.phi + d);
      else return;
      e.preventDefault();
    });
    window.addEventListener('resize', fitGL);
  }

  function fitGL() {
    var gl = G.gl, c = canvasEl();
    if (!gl || !c) return;
    var w = c.clientWidth, h = c.clientHeight;
    if (!w || !h) return;
    gl.renderer.setSize(w, h, false);
    gl.camera.aspect = w / h;
    gl.camera.updateProjectionMatrix();
  }

  function clickPick(e) {
    var gl = G.gl, c = glEl();
    if (!gl || !c || !gl.starList.length) { G.lastPick = { early: 'no-gl' }; return; }
    var r = c.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) { G.lastPick = { early: 'out-of-bounds', x: e.clientX, y: e.clientY }; return; }
    var m = new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    gl.ray.setFromCamera(m, gl.camera);
    var hits = gl.ray.intersectObjects(gl.starList.map(function (s) { return s.sprite; }));
    G.lastPick = { x: e.clientX, y: e.clientY, hits: hits.length };
    if (!hits.length) return;
    var cid = hits[0].object.userData.cid, star = gl.stars[cid];
    if (!star) return;
    /* 点族星直开链层列式甬道（Owner 2026-09-10 裁定：族内不用星云，上中下游左→右列式） */
    ZK.bus.emit('cm:view', { view: 'cluster' });
    ZK.bus.emit('cm:open-cluster', { cid: cid, name: star.name, market: G.market });
  }

  /* 47 族 Fibonacci 球面撒点：黄金角均匀分布（确定性几何，坐标与数据零耦合免缓存）；
   * 按公司数降序分配序号——大族错开落位。星大小=公司数（同旧 2D 口径公式族）。 */
  function render() {
    var d = G.data;
    if (!d) return;
    if (G.mode === 'ifind') { renderOverview(); return; }   /* 总图模式：数据到达也只走 SVG 路径，WebGL 惰性到切回星云才初始化 */
    var gl = initGL();
    if (!gl) return;   /* 降级路径：glDegrade 已给出诚实提示 */
    fitGL();
    clearScene();
    var empty = document.getElementById('cm-empty-galaxy');
    if (empty) empty.style.display = 'none';
    var R = 150, GA = 2.399963;
    var ns = d.clusters.slice().sort(function (a, b) { return b.n_companies - a.n_companies; });
    var linkOf = {};
    d.links.forEach(function (l) { (linkOf[l.s] = linkOf[l.s] || {})[l.t] = l.w; (linkOf[l.t] = linkOf[l.t] || {})[l.s] = l.w; });
    var group = new THREE.Group();
    gl.group = group;
    ns.forEach(function (c, i) {
      var y = 1 - 2 * (i + 0.5) / ns.length, rr = Math.sqrt(Math.max(0, 1 - y * y)), a = GA * i;
      var p = new THREE.Vector3(Math.cos(a) * rr * R, y * R, Math.sin(a) * rr * R);
      var base = 5 + Math.sqrt(c.n_companies || 1) * 1.15;
      var mat = new THREE.SpriteMaterial({ map: gl.tex, color: 0x3d8bff, transparent: true, depthWrite: false });
      var sp = new THREE.Sprite(mat);
      sp.position.copy(p);
      sp.scale.setScalar(base * 2.2);
      sp.userData.cid = c.id;
      group.add(sp);
      gl.stars[c.id] = { cid: c.id, name: c.name, sprite: sp, base: base };
      gl.starList.push(gl.stars[c.id]);
      var lb = document.createElement('div');
      lb.className = 'cm-gl-label';
      lb.textContent = c.name;
      lb.title = c.name + '（' + c.n_chains + ' 链 · ' + c.n_companies + ' 公司）';
      if (base >= 10) lb.classList.add('cm-gl-major');
      gl.labelHost.appendChild(lb);
      gl.labels[c.id] = lb;
    });
    d.links.forEach(function (l) {
      var sa = gl.stars[l.s], sb = gl.stars[l.t];
      if (!sa || !sb) return;
      var geo = new THREE.BufferGeometry().setFromPoints([sa.sprite.position, sb.sprite.position]);
      var op = Math.min(0.42, 0.06 + Math.log10((l.w || 1) + 1) * 0.14);
      var line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0x3d8bff, transparent: true, opacity: op }));
      group.add(line);
      gl.lines.push({ s: l.s, t: l.t, line: line, baseOp: op });
      gl.linkByPair[l.s] = gl.linkByPair[l.s] || {};
      gl.linkByPair[l.s][l.t] = true;
      gl.linkByPair[l.t] = gl.linkByPair[l.t] || {};
      gl.linkByPair[l.t][l.s] = true;
    });
    gl.scene.add(group);
    var meta = document.getElementById('cm-meta');
    if (meta) {
      meta.textContent = d.clusters.length + ' 族 · ' + d.chains.length + ' 链 · ' +
        d.clusters.reduce(function (s, c) { return s + c.n_companies; }, 0) + ' 公司（去重口径另计） · 真源 ig_*（PG 只读） · ' + d.generated_at + ' · 3D：拖拽旋转/滚轮推拉/方向键/双击复位 · 点族星进链层';
      meta.classList.remove('cm-bad');
    }
    setCrumb();
    G.birth = performance.now();
    applyHover(null);
    startLoop();
  }

  function clearScene() {
    var gl = G.gl;
    if (gl.group) {
      gl.scene.remove(gl.group);
      gl.group.traverse(function (o) {
        if (o.geometry) o.geometry.dispose();
        if (o.material) { if (o.material.map && o.material.map !== gl.tex) o.material.map.dispose(); o.material.dispose(); }
      });
      gl.group = null;
    }
    gl.stars = {}; gl.starList = []; gl.lines = []; gl.linkByPair = {}; gl.hover = null;
    if (gl.labelHost) gl.labelHost.innerHTML = '';
    gl.labels = {};
  }

  function applyHover(cid) {
    var gl = G.gl;
    if (!gl || gl.hover === cid) return;
    gl.hover = cid;
    var links = cid ? (gl.linkByPair[cid] || {}) : {};
    gl.starList.forEach(function (s) {
      var on = !cid || s.cid === cid || !!links[s.cid];
      s.sprite.material.opacity = (cid && !on) ? 0.14 : 1;
      s.sprite.material.color.setHex(s.cid === cid ? 0xe6c34c : 0x3d8bff);
      var lb = gl.labels[s.cid];
      if (lb) { lb.classList.toggle('cm-on', s.cid === cid); lb.classList.toggle('cm-dim', !!cid && !on); }
    });
    gl.lines.forEach(function (ln) {
      var act = cid && (ln.s === cid || ln.t === cid);
      ln.line.material.opacity = cid ? (act ? 0.95 : 0.03) : ln.baseOp;
    });
  }

  var V3 = null;   /* 复用向量，避免每帧分配 */
  function startLoop() {
    if (G.raf) return;
    var loop = function () {
      var gl = G.gl, gel = glEl();
      if (!gl || !visible() || !gel || gel.offsetParent === null) { stopLoop(); return; }   /* 3D 画布隐藏（总图模式/他视图）也停，零后台占用 */
      G.raf = requestAnimationFrame(loop);
      var now = performance.now();
      if (gl.group) {   /* 星云成形入场：0.9s 缩放+微旋 */
        var k = Math.min(1, (now - G.birth) / 900), e = 1 - Math.pow(1 - k, 3);
        gl.group.scale.setScalar(0.2 + 0.8 * e);
        gl.group.rotation.y = (1 - e) * 0.6;
      }
      applyCamera();
      if (gl.drag) applyHover(null);
      else {
        gl.ray.setFromCamera(new THREE.Vector2(gl.mouse.x, gl.mouse.y), gl.camera);
        var hits = gl.ray.intersectObjects(gl.starList.map(function (s) { return s.sprite; }));
        applyHover(hits.length ? hits[0].object.userData.cid : null);
        glEl().style.cursor = hits.length ? 'pointer' : 'grab';
      }
      /* 标签投影：近侧亮、远侧淡（背面 0.22），v.z>1 视锥后隐藏 */
      var c = canvasEl(), w = c.clientWidth, h = c.clientHeight;
      if (w && h) {
        V3 = V3 || new THREE.Vector3();
        var cn = gl.camera.position.clone().normalize();
        for (var cid in gl.labels) {
          var star = gl.stars[cid], lb = gl.labels[cid];
          V3.copy(star.sprite.position).applyMatrix4(gl.group ? gl.group.matrixWorld : gl.scene.matrixWorld).project(gl.camera);
          if (V3.z > 1) { lb.style.display = 'none'; continue; }
          lb.style.display = 'block';
          lb.style.left = ((V3.x * 0.5 + 0.5) * w) + 'px';
          lb.style.top = ((-V3.y * 0.5 + 0.5) * h) + 'px';
          var facing = star.sprite.position.clone().normalize().dot(cn);
          lb.style.opacity = (0.55 + 0.4 * Math.max(0, facing)).toFixed(2);
        }
      }
      gl.renderer.render(gl.scene, gl.camera);
    };
    G.raf = requestAnimationFrame(loop);
  }

  function stopLoop() {
    if (G.raf) { cancelAnimationFrame(G.raf); G.raf = 0; }
  }

  function setCrumb() {
    var cr = document.getElementById('cm-crumb');
    if (cr) cr.textContent = G.mode === 'ifind' ? '产业地图 · 一级总图' : '产业地图 · 全景星系（3D）';
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
      render();
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

  /* ══ L1 一级总图（ifind 模式，Owner 2026-09-12 拍板④）══
   * 族=分区底板（iFinD 分区底板同语言，蛇形流式排布）、链=小等距块（大小=公司数）、
   * 族间流向线=links 权重投影（贝塞尔+箭头，画在底板下层）。
   * 交互：点链块=cm:goto-chain 直达链视图；点底板=cm:open-cluster 进链层；
   * 滚轮缩放/拖拽平移/双击复位。纯 SVG，#cm-wires-overview 唯一画布。 */
  var OV = { BUDGET: 2360, GAPX: 34, GAPY: 46, ZPAD: 16, HEAD: 26, CELL_GAP: 14, CELL_BUDGET: 620, MAX_LINKS: 20 };
  var ovIndex = { chains: {}, clusters: {} };   /* chain_id→链记录、cid→族记录（点击委托用） */

  function ovCanvasEl() { return document.getElementById('cm-canvas-overview'); }
  function ovWorldEl() { return document.getElementById('cm-world-overview'); }
  function ovSvgEl() { return document.getElementById('cm-wires-overview'); }

  function esc2(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }

  function applyOvView() {
    var w = ovWorldEl();
    if (w) w.style.transform = 'translate(' + G.ov.x + 'px,' + G.ov.y + 'px) scale(' + G.ov.z + ')';
    var b = document.getElementById('cm-zoom-overview');
    if (b) b.textContent = Math.round(G.ov.z * 100) + '%';
  }

  function bindOvView() {
    var c = ovCanvasEl();
    if (!c || c.dataset.bound) return;
    c.dataset.bound = '1';
    c.addEventListener('wheel', function (e) {
      e.preventDefault();
      var r = c.getBoundingClientRect();
      var mx = e.clientX - r.left, my = e.clientY - r.top;
      var nz = Math.max(0.15, Math.min(5, G.ov.z * (e.deltaY < 0 ? 1.12 : 0.89)));
      var k = nz / G.ov.z;
      G.ov.x = mx - (mx - G.ov.x) * k; G.ov.y = my - (my - G.ov.y) * k; G.ov.z = nz;
      applyOvView();
    }, { passive: false });
    var drag = null;
    c.addEventListener('mousedown', function (e) {
      drag = { x: e.clientX, y: e.clientY, vx: G.ov.x, vy: G.ov.y };
      c.classList.add('dragging');
    });
    window.addEventListener('mousemove', function (e) {
      if (!drag) return;
      G.ov.x = drag.vx + (e.clientX - drag.x); G.ov.y = drag.vy + (e.clientY - drag.y);
      applyOvView();
    });
    window.addEventListener('mouseup', function () { drag = null; c.classList.remove('dragging'); });
    c.addEventListener('dblclick', function (e) { if (e.target.closest && e.target.closest('.cm-ov-ch')) return; fitOv(); });
    window.addEventListener('resize', function () { if (G.mode === 'ifind' && l1Visible()) fitOv(); });
  }

  function fitOv() {
    var c = ovCanvasEl(), svg = ovSvgEl();
    if (!c || !svg) return;
    var ww = parseFloat(svg.getAttribute('width')) || 0, wh = parseFloat(svg.getAttribute('height')) || 0;
    if (!ww || !wh) return;
    var r = c.getBoundingClientRect();
    if (!r.width || !r.height) return;
    var z = Math.min((r.width - 24) / ww, (r.height - 24) / wh, 1.4);
    G.ov = { z: z, x: (r.width - ww * z) / 2, y: 46 };   /* y=46：让出左上图例胶囊行，防遮首行族名头 */
    applyOvView();
  }

  /* 链=小等距块：hw 随公司数增长（sqrt 阻尼），双行拆名（括号优先），下挂公司计数 */
  function ovChainSvg(cx, cy, hw, ch) {
    var hh = hw / 2, dp = 12 + hw * 0.18;
    var nm = ch.name, lines;
    if (nm.length <= 7) lines = [nm];
    else {
      var i = nm.indexOf('（');
      lines = (i > 0 && i <= 8) ? [nm.slice(0, i), nm.slice(i)]
        : [nm.slice(0, Math.ceil(nm.length / 2)), nm.slice(Math.ceil(nm.length / 2))];
    }
    var fs = lines.length > 1 ? 10.5 : 11.5;
    var dy = lines.length > 1 ? -3 : 4.5;
    var txt = lines.map(function (l, k) {
      return '<text x="' + cx + '" y="' + (cy + dy + k * 13) + '" text-anchor="middle" font-size="' + fs +
        '" font-weight="700" fill="#d9d6f8">' + esc2(l) + '</text>';
    }).join('');
    var CB = ['#3c3489', '#2e2768', '#26215c', '#afa9ec'];
    return '<g class="cm-ov-ch" data-chain="' + esc2(ch.chain_id) + '">' +
      '<title>' + esc2(nm) + ' · ' + (ch.n_companies || 0) + ' 公司 · ' + (ch.n_nodes || 0) + ' 环节——点击直达链视图</title>' +
      '<polygon class="cube-top" points="' + cx + ',' + (cy - hh) + ' ' + (cx + hw) + ',' + cy + ' ' + cx + ',' + (cy + hh) + ' ' + (cx - hw) + ',' + cy +
      '" fill="' + CB[0] + '" stroke="' + CB[3] + '" stroke-width="1.5"/>' +
      '<polygon points="' + (cx - hw) + ',' + cy + ' ' + cx + ',' + (cy + hh) + ' ' + cx + ',' + (cy + hh + dp) + ' ' + (cx - hw) + ',' + (cy + dp) +
      '" fill="' + CB[1] + '" stroke="' + CB[3] + '" stroke-width="1"/>' +
      '<polygon points="' + (cx + hw) + ',' + cy + ' ' + cx + ',' + (cy + hh) + ' ' + cx + ',' + (cy + hh + dp) + ' ' + (cx + hw) + ',' + (cy + dp) +
      '" fill="' + CB[2] + '" stroke="' + CB[3] + '" stroke-width="1"/>' + txt +
      '<text x="' + cx + '" y="' + (cy + hh + dp + 13) + '" text-anchor="middle" font-size="9.5" fill="#7d8aa0">' + (ch.n_companies || 0) + ' 公司</text></g>';
  }

  function renderOverview() {
    var d = G.data, svg = ovSvgEl();
    if (!svg) return;
    if (!d) { svg.setAttribute('width', 10); svg.setAttribute('height', 10); svg.innerHTML = ''; return; }
    ovIndex = { chains: {}, clusters: {} };
    var plates = [];
    d.clusters.forEach(function (c) {
      var chs = d.chains.filter(function (x) { return x.cluster === c.id; })
        .sort(function (a, b) { return b.n_companies - a.n_companies; });
      var cells = [], x = 0, y = 0, rowMax = 0, maxRight = 0;
      chs.forEach(function (ch) {
        ovIndex.chains[ch.chain_id] = ch;
        var hw = 36 + Math.min(28, Math.sqrt(ch.n_companies || 1) * 3.6);
        var cw = hw * 2, chh = hw + (12 + hw * 0.18) + 20;   /* 顶点全高+侧面厚+计数行 */
        if (x > 0 && x + cw > OV.CELL_BUDGET) { x = 0; y += rowMax + OV.CELL_GAP; rowMax = 0; }
        cells.push({ ch: ch, hw: hw, x: x + cw / 2, y: y + chh / 2 });
        x += cw + OV.CELL_GAP; rowMax = Math.max(rowMax, chh);
        maxRight = Math.max(maxRight, x - OV.CELL_GAP);
      });
      plates.push({ c: c, cells: cells, w: Math.max(maxRight, 1) + OV.ZPAD * 2,
                    h: OV.HEAD + OV.ZPAD + y + rowMax + OV.ZPAD });
      ovIndex.clusters[c.id] = c;
    });
    var px = 0, py = 0, prowMax = 0, pright = 0;
    plates.forEach(function (p) {
      if (px > 0 && px + p.w > OV.BUDGET) { px = 0; py += prowMax + OV.GAPY; prowMax = 0; }
      p.x = px; p.y = py; px += p.w + OV.GAPX; prowMax = Math.max(prowMax, p.h);
      pright = Math.max(pright, p.x + p.w);
      p.center = { x: p.x + p.w / 2, y: p.y + p.h / 2 };
    });
    var worldW = pright + 20, worldH = py + prowMax + 30;
    svg.setAttribute('width', worldW); svg.setAttribute('height', worldH);
    var w = ovWorldEl();
    if (w) { w.style.width = worldW + 'px'; w.style.height = worldH + 'px'; }
    var defs = '<defs><marker id="cmOvAr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="#6f95e0"/></marker></defs>';
    /* 族间流向线：底板下层；全量边画出来是线团（Owner 2026-09-13 实景反馈"很混乱"）——
     * 只画权重前 MAX_OV_LINKS 条主干，弱化常驻样式，悬停底板高亮其相关线（bindOvEvents） */
    var ranked = d.links.slice().sort(function (a, b) { return (b.w || 0) - (a.w || 0); }).slice(0, OV.MAX_LINKS);
    var links = '';
    ranked.forEach(function (l) {
      var pa = null, pb = null;
      plates.forEach(function (p) { if (p.c.id === l.s) pa = p; if (p.c.id === l.t) pb = p; });
      if (!pa || !pb) return;
      var lw = l.w || 0;
      var op = Math.min(0.3, 0.07 + Math.log10(lw + 1) * 0.06);
      var swd = (1 + Math.min(1.4, Math.log10(lw + 1) * 0.4)).toFixed(1);
      var mx = (pa.center.x + pb.center.x) / 2, my = (pa.center.y + pb.center.y) / 2 - 26;
      links += '<path class="cm-ov-link" data-s="' + esc2(l.s) + '" data-t="' + esc2(l.t) + '" d="M' + pa.center.x + ',' + pa.center.y + ' Q' + mx + ',' + my + ' ' + pb.center.x + ',' + pb.center.y +
        '" fill="none" stroke="#6f95e0" stroke-width="' + swd + '" opacity="' + op.toFixed(2) +
        '" marker-end="url(#cmOvAr)"><title>' + esc2((ovIndex.clusters[l.s] || {}).name || l.s) + ' → ' +
        esc2((ovIndex.clusters[l.t] || {}).name || l.t) + ' · 族间供应连接 权重 ' + lw + '</title></path>';
    });
    var body = '';
    plates.forEach(function (p) {
      var g = '<g class="cm-ov-pl" data-cid="' + esc2(p.c.id) + '">';
      g += '<rect x="' + p.x + '" y="' + p.y + '" width="' + p.w + '" height="' + p.h + '" rx="12" fill="#141f38" stroke="#2b3d64"/>';
      g += '<g class="cm-ov-pl-h"><title>' + esc2(p.c.name) + ' · ' + p.c.n_chains + ' 链 · ' + p.c.n_companies + ' 公司——点击进链层</title>' +
        '<text x="' + (p.x + OV.ZPAD) + '" y="' + (p.y + 18) + '" font-size="12.5" font-weight="700" fill="#8fb0ea">' + esc2(p.c.name) + '</text>' +
        '<text x="' + (p.x + p.w - OV.ZPAD) + '" y="' + (p.y + 18) + '" text-anchor="end" font-size="10" fill="#525d70">' + p.c.n_chains + ' 链 · ' + p.c.n_companies + ' 公司</text></g>';
      p.cells.forEach(function (cell) {
        g += ovChainSvg(p.x + OV.ZPAD + cell.x, p.y + OV.HEAD + OV.ZPAD + cell.y, cell.hw, cell.ch);
      });
      g += '</g>';
      body += g;
    });
    svg.innerHTML = defs + links + body;
    bindOvEvents();
    fitOv();
    var meta = document.getElementById('cm-meta');
    if (meta) {
      meta.textContent = d.clusters.length + ' 族 · ' + d.chains.length + ' 链 · ' +
        d.clusters.reduce(function (s, c) { return s + c.n_companies; }, 0) +
        ' 公司（去重口径另计） · iFinD 一级总图 · 点链块直达链视图 · 真源 ig_*（PG 只读） · ' + d.generated_at;
      meta.classList.remove('cm-bad');
    }
    setCrumb();
  }

  function bindOvEvents() {
    var svg = ovSvgEl();
    if (!svg || svg.dataset.bound) return;
    svg.dataset.bound = '1';
    svg.addEventListener('click', function (e) {
      if (!e.target.closest) return;
      var chn = e.target.closest('.cm-ov-ch');
      if (chn) {
        var rec = ovIndex.chains[chn.getAttribute('data-chain')];
        if (!rec) return;
        ZK.bus.emit('cm:view', { view: 'cluster' });
        ZK.bus.emit('cm:goto-chain', { chain_id: rec.chain_id, chain_name: rec.name, cluster: rec.cluster, market: G.market });
        return;
      }
      var pl = e.target.closest('.cm-ov-pl');
      if (pl) {
        var cid = pl.getAttribute('data-cid'), c = ovIndex.clusters[cid];
        if (!c) return;
        ZK.bus.emit('cm:view', { view: 'cluster' });
        ZK.bus.emit('cm:open-cluster', { cid: cid, name: c.name, market: G.market });
      }
    });
    /* 悬停底板=高亮其相关流向线、压暗其余（降噪后的主干线可读性） */
    svg.addEventListener('mouseover', function (e) {
      if (!e.target.closest) return;
      var pl = e.target.closest('.cm-ov-pl');
      if (!pl) return;
      var cid = pl.getAttribute('data-cid');
      svg.classList.add('linkfocus');
      Array.prototype.forEach.call(svg.querySelectorAll('.cm-ov-link'), function (p) {
        p.classList.toggle('on', p.getAttribute('data-s') === cid || p.getAttribute('data-t') === cid);
      });
    });
    svg.addEventListener('mouseout', function (e) {
      if (!e.target.closest) return;
      var to = e.relatedTarget;
      if (to && to.closest && to.closest('.cm-ov-pl')) return;
      svg.classList.remove('linkfocus');
      Array.prototype.forEach.call(svg.querySelectorAll('.cm-ov-link.on'), function (p) { p.classList.remove('on'); });
    });
  }

  /* ── L1 形态切换（顶栏 星云/总图）── 契约不变：cm:view 'galaxy' 恒指 L1（按 G.mode 落到对应画布） */
  function showL1() {
    var m3 = G.mode === '3d';
    var c3 = canvasEl(), cov = ovCanvasEl();
    if (c3) c3.style.display = m3 ? 'block' : 'none';
    if (cov) cov.style.display = m3 ? 'none' : 'block';
    if (m3) {
      if (G.data && !G.gl) render();   /* 数据已在而 WebGL 未建（总图期间到达）：切回时惰性初始化 */
      if (G.gl) { fitGL(); startLoop(); }
      if (!G.loaded) { if (!G.busy) load(); else refreshLoading(); }
      else hideLoading();
    } else {
      stopLoop();
      if (G.data) {
        hideLoading();
        var osv = ovSvgEl();
        if (!osv || !osv.querySelector('.cm-ov-pl')) renderOverview();   /* 首切/切档清空后重排；已有内容保镜头不重置 */
      } else if (!G.busy) load();        /* showLoading 内部按可见性落覆盖层 */
      else refreshLoading();
    }
  }

  function syncToggle() {
    var sw = document.getElementById('cm-l1sw');
    if (!sw) return;
    Array.prototype.forEach.call(sw.querySelectorAll('b[data-mode]'), function (b) {
      b.classList.toggle('act', b.getAttribute('data-mode') === G.mode);
    });
  }

  function setMode(m) {
    if (m !== '3d' && m !== 'ifind') return;
    G.mode = m;
    syncToggle();
    /* 任意层级（L2 链层/L3 公司）点切换钮=一键回 L1（Owner 2026-09-13 反馈：此前仅换模式不动视图）；
     * 已在 L1 时幂等：cm:view 处理器重落当前 mode 画布 */
    ZK.bus.emit('cm:view', { view: 'galaxy' });
  }

  function bindToggle() {
    var sw = document.getElementById('cm-l1sw');
    if (!sw || sw.dataset.bound) return;
    sw.dataset.bound = '1';
    Array.prototype.forEach.call(sw.querySelectorAll('b[data-mode]'), function (b) {
      b.addEventListener('click', function () { setMode(b.getAttribute('data-mode')); });
    });
    syncToggle();
  }

  ZK.bus.on('cm:view', function (d) {
    var c3 = canvasEl(), cov = ovCanvasEl();
    if (c3) c3.style.display = 'none';
    if (cov) cov.style.display = 'none';
    if (d.view === 'galaxy') {
      setCrumb();
      showL1();
    } else {
      stopLoop();   /* 隐藏页零后台占用（home 纯视频先例） */
    }
  });

  /* 市场切档（项4）：galaxy 是簇空间本尊——重拉当前档数据重渲染；meta 行 counts 随档真实变化 */
  ZK.bus.on('cm:market', function (d) {
    G.market = (d && d.market) || 'all';
    G.loaded = false;
    G.data = null;
    var os = ovSvgEl();   /* 总图立即清残影（旧档底板不可见性残留=假数据嫌疑） */
    if (os) os.innerHTML = '';
    if (visible()) load();
  });

  function boot() {
    bindToggle();
    bindOvView();
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
    debug: function () {   /* ACC 机断只读探针：L1 形态+相机球坐标+场景规模+拾取诊断（不暴露可变引用） */
      var glPart = G.gl && { theta: G.gl.sph.theta, phi: G.gl.sph.phi, r: G.gl.sph.r,
        stars: Object.keys(G.gl.stars).length, lines: G.gl.lines.length, webgl: true, lastPick: G.lastPick || null };
      return { mode: G.mode, market: G.market, loaded: G.loaded,
        overview: G.mode === 'ifind' ? { plates: document.querySelectorAll('#cm-wires-overview .cm-ov-pl').length,
          chains: document.querySelectorAll('#cm-wires-overview .cm-ov-ch').length } : null,
        gl: glPart };
    },
    destroy: function () {
      if (G.timer) clearInterval(G.timer);
      if (G.elapsedTimer) { clearInterval(G.elapsedTimer); G.elapsedTimer = null; }
      stopLoop();
      if (G.gl) { G.gl.renderer.dispose(); G.gl = null; }
    }
  });

  if (document.getElementById('p-chainmap')) boot();
})();
