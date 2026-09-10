/* ── 产业地图 L1 星系层 · 3D 族星云（B2 一期，Owner 2026-09-10 裁定 3D 化）· 真源 /api/chainmap-galaxy（ig_* 七表，PG 只读）──
 * 47 族 Fibonacci 球面撒点（族越大星越大，确定性几何分布免布局缓存）；拖拽旋转/滚轮推拉/键盘方向/
 * 双击复位；hover 高亮直连邻接；点星进 L2 链层（cm:view/cm:open-cluster 契约不变）。
 * 渲染=three.js r147 UMD（vendor/three/，dockview vendor 先例）；轨道相机手搓球坐标（~60 行，
 * 免 examples/OrbitControls 版本耦合）。旧 2D 力导向渲染退役（git 历史留存）。
 * 模块契约：ZK.registerFeature 注册；与 nav/search/cluster 只经 ZK.bus 通信（cm:view/cm:market）；
 * 画布容器 #cm-canvas-galaxy 本模块独占；演示诚实纪律：无演示数据，断线空态+15s 自动重试；
 * WebGL/three 缺失→诚实报错不做 2D 假降级。验收单：ACC-F-CHAINMAP-GALAXY（rev4）
 * ｜ 拆分清单：docs/_working/2026-09-08-chainmap-component-split-inventory.md */
(function () {
  'use strict';
  var G = { data: null, busy: false, loaded: false, timer: null, market: 'all',
            loadStart: 0, elapsedTimer: null, retryCount: 0,   /* B1 加载态（ACC rev3） */
            gl: null, raf: 0, birth: 0 };   /* gl=3D 引擎句柄（initGL 建见注释） */

  function canvasEl() { return document.getElementById('cm-canvas-galaxy'); }
  function glEl() { return document.getElementById('cm-gl-galaxy'); }
  function loadingEl() { return document.getElementById('cm-loading-galaxy'); }

  /* ── B1 加载态（ACC-F-CHAINMAP-GALAXY rev3 item7/8）──
   * 首算 3-6s（冷缓存最长 20s）期间画布不再是空白：星云闪烁骨架+已等待秒数诚实计数；
   * 断线转失败态（红字+暂停闪烁+重试计数），15s 自动重试机制不变；成功即隐藏。零假数据。 */
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
    ZK.bus.emit('cm:view', { view: 'cluster' });
    ZK.bus.emit('cm:open-cluster', { cid: cid, name: star.name, market: G.market });
  }

  /* 47 族 Fibonacci 球面撒点：黄金角均匀分布（确定性几何，坐标与数据零耦合免缓存）；
   * 按公司数降序分配序号——大族错开落位。星大小=公司数（同旧 2D 口径公式族）。 */
  function render() {
    var d = G.data;
    if (!d) return;
    var gl = initGL();
    if (!gl) return;   /* 降级路径：glDegrade 已给出诚实提示 */
    fitGL();
    clearScene();
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
        d.clusters.reduce(function (s, c) { return s + c.n_companies; }, 0) + ' 公司（去重口径另计） · 真源 ig_*（PG 只读） · ' + d.generated_at + ' · 3D：拖拽旋转/滚轮推拉/方向键/双击复位';
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
      var gl = G.gl;
      if (!gl || !visible()) { stopLoop(); return; }
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
    if (cr) cr.textContent = '产业地图 · 全景星系（3D）';
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

  ZK.bus.on('cm:view', function (d) {
    var c = canvasEl();
    if (!c) return;
    var show = d.view === 'galaxy';
    c.style.display = show ? 'block' : 'none';
    if (show) {
      setCrumb();
      if (G.gl) { fitGL(); startLoop(); }   /* 回页重启渲染循环+适配尺寸 */
      if (!G.loaded) load();
    } else {
      stopLoop();   /* 隐藏页零后台占用（home 纯视频先例） */
    }
  });

  /* 市场切档（项4）：galaxy 是簇空间本尊——重拉当前档数据重渲染；meta 行 counts 随档真实变化 */
  ZK.bus.on('cm:market', function (d) {
    G.market = (d && d.market) || 'all';
    G.loaded = false;
    G.data = null;
    if (visible()) load();
  });

  function boot() {
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
    debug: function () {   /* ACC 机断只读探针：相机球坐标+场景规模+拾取诊断（不暴露可变引用） */
      return G.gl && { theta: G.gl.sph.theta, phi: G.gl.sph.phi, r: G.gl.sph.r,
        stars: Object.keys(G.gl.stars).length, lines: G.gl.lines.length, webgl: true, lastPick: G.lastPick || null };
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
