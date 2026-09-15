/* ── 治理操作全景（七层流水线 L0→L6）· 真源 /api/govm（mtime 缓存）· 30s 轮询自动映射 ──
 * 真源=config/governance_operations_map.yaml（GOMAP-001，骨架机生 scripts/governance/generate_governance_map.py，
 * families 层全量重建、pipeline/out_of_scope_refs 人工语义层）——本文件只读渲染：
 * ① 布局：竖向流水线（层卡 L0→L6 顺序贯通，左轨=层徽+名称+竖连线）——每层=层体（职责行+挂载
 *    chip 流+配置真源+未接线候选项），未接线候选项=橙虚框警示卡+note 大白话（治理缺口直读）。
 * ② 统计：counts 机生值（总模块/疑似孤儿）+七族计数+接线三态分布，全部真源现算零硬编码
 *    （宪法 §9.5 静态清单禁手工维护）；页面片头计数 #govm-count 同源填充。
 * 激活检测：页面片段经 innerHTML 注入（script 不执行），本文件由 loader 显式加载；
 *           30s tick 时仅 p-govm 可见才 fetch，页面隐藏零开销（tdm/factory 同款）。
 * 模块路径点击=复制全路径（app:// 下 file:// 链接被拦，复制路径是全环境可用的最短动作——tdm 代码锚同款）。 */
(function () {
  'use strict';
  var GOVM = { data: null, stamp: null, busy: false };
  var API_BASE = 'http://127.0.0.1:8890';   /* 与 services/api.js 同源——app:// 模式下相对 fetch 会打到 app://api/govm 必断（tdm/factory 同款坑） */

  function visible() {
    var el = document.getElementById('p-govm');
    return el && el.offsetParent !== null;
  }

  /* 真源文本进 innerHTML——防标签断裂/注入（tdm esc 同款） */
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* 接线三态（真源 wiring 枚举；色板沿 tdm/factory 既有语义，不发明新色）。族名=L*_ 键原文
   * （机生标识，非翻译对象——禁硬编码翻译字典，宪法 §9.9） */
  var WIRING_KEYS = { wired: 0, wired_by_header: 0, suspect_orphan: 0 };

  function load() {
    if (GOVM.busy) return;
    GOVM.busy = true;
    fetch(API_BASE + '/api/govm').then(function (r) { return r.json(); }).then(function (d) {
      GOVM.busy = false;
      if (!d.ok) {
        var meta0 = document.getElementById('govm-meta');
        if (meta0) meta0.textContent = '面板 API 未重启（无 /api/govm 端点）——服务总闸「↻ 重启面板 API」后恢复';
        return;
      }
      GOVM.stamp = d.generated_at;
      GOVM.data = d;
      render();
      var meta = document.getElementById('govm-meta');
      if (meta) {
        var mm = 0, dd = 0;
        (d.layers || []).forEach(function (l) { mm += (l.mounts || []).length; dd += (l.disconnected || []).length; });
        meta.textContent = (d.layers || []).length + ' 层 · 挂载 ' + mm + ' · 未接线候选 ' + dd +
          ' · 更新 ' + String(d.generated_at || '').slice(5, 16);
      }
      var cnt = document.getElementById('govm-count');   /* 页头计数=实时真源值，禁硬编码（tdm-count 同款） */
      if (cnt) cnt.textContent = d.counts && d.counts.total_modules != null ? d.counts.total_modules : '—';
    }).catch(function () {
      GOVM.busy = false;
      var meta = document.getElementById('govm-meta');
      if (meta) meta.textContent = 'API 断开（面板 API 未启动?）';
    });
  }

  /* 统计 chip（工厂 .fn 同款三态：hot=机生 headline / ok=已接线 / warn=橙虚孤儿） */
  function gs(k, v, cls) {
    return '<span class="gs' + (cls ? ' ' + cls : '') + '"><i>' + esc(k) + '</i><b>' + esc(v) + '</b></span>';
  }

  function modChip(p) {
    return '<span class="chip" title="点击复制模块路径：' + esc(p) + '" data-copy="' + esc(p) + '"><i>' + esc(p) + '</i></span>';
  }

  /* 复制路径反馈（tdm .mod-copy done() 同款：chip 文本临时替换 1.2s） */
  function copyText(path, el) {
    var done = function () {
      var old = el.getAttribute('data-old') || el.textContent;
      el.setAttribute('data-old', old);
      el.textContent = '已复制 ✓';
      setTimeout(function () { el.textContent = old; el.removeAttribute('data-old'); }, 1200);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(path).then(done, function () { });
    } else {
      var ta = document.createElement('textarea');
      ta.value = path; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { }
      document.body.removeChild(ta);
    }
  }

  function render() {
    var d = GOVM.data; if (!d) return;
    var pipe = document.getElementById('govm-pipeline');
    var stats = document.getElementById('govm-stat-chips');
    var oos = document.getElementById('govm-oos');
    if (!pipe || !stats || !oos) return;

    /* ── 统计条：counts 机生值 + 七族现算计数 + 接线三态现算分布（零硬编码计数）── */
    var fams = d.families || {};
    var wsum = { wired: 0, wired_by_header: 0, suspect_orphan: 0 };
    var chips = [];
    var c = d.counts || {};
    chips.push(gs('总模块', c.total_modules != null ? c.total_modules : '—', 'hot'));
    chips.push(gs('疑似孤儿', c.suspect_orphans != null ? c.suspect_orphans : '—', 'warn'));
    Object.keys(fams).forEach(function (k) {
      (fams[k] || []).forEach(function (m) { if (m && m.wiring in WIRING_KEYS) wsum[m.wiring] += 1; });
      chips.push(gs(k, (fams[k] || []).length, ''));
    });
    chips.push(gs('已接线', wsum.wired, 'ok'));
    chips.push(gs('头声明接线', wsum.wired_by_header, ''));
    chips.push(gs('疑似孤儿(族算)', wsum.suspect_orphan, 'warn'));
    stats.innerHTML = chips.join('');

    /* ── 七层流水线（L0→L6 顺序渲染；空态显式留位——无挂载/无候选/无配置都不塌区）── */
    pipe.innerHTML = '';
    (d.layers || []).forEach(function (l, i) {
      var el = document.createElement('div');
      el.className = 'gl';
      var mounts = (l.mounts || []).map(modChip).join('');
      var cfg = (l.config_refs || []).map(function (r) {
        return '<span class="cr" title="配置真源（config/*.yaml）">' + esc(r) + '</span>';
      }).join('');
      var dcs = (l.disconnected || []).map(function (x) {
        return '<div class="dc"><span class="dc-m">⚠ ' + esc(x.mod) + '</span>' +
          (x.note_zh ? '<span class="dc-n">' + esc(x.note_zh) + '</span>' : '') + '</div>';
      }).join('');
      el.innerHTML =
        '<div class="gl-rail"><span class="gl-badge">' + esc(l.id) + '</span>' +
        '<span class="gl-name">' + esc(l.name_zh) + '</span>' +
        (i < (d.layers || []).length - 1 ? '<span class="gl-line"></span>' : '') + '</div>' +
        '<div class="gl-body">' +
        '<div class="gl-role">' + esc(l.desc_zh || '（职责待补）') + '</div>' +
        '<div class="gl-h">挂载模块 <span class="cnt">' + (l.mounts || []).length + '</span></div>' +
        (mounts ? '<div class="chips">' + mounts + '</div>' : '<div class="empty">（无挂载——本层为人工语义占位）</div>') +
        (cfg ? '<div class="gl-h">配置真源 <span class="cnt">' + (l.config_refs || []).length + '</span></div>' +
          '<div class="chips">' + cfg + '</div>' : '') +
        '<div class="gl-h">未接线候选 <span class="cnt">' + (l.disconnected || []).length + '</span></div>' +
        (dcs || '<div class="empty">（无——本层全量接线）</div>') +
        '</div>';
      pipe.appendChild(el);
    });

    /* ── 图外引用（out_of_scope_refs：边界即语义——哪些治理体系不在本图）── */
    var refs = d.out_of_scope_refs || [];
    oos.innerHTML =
      '<div class="oos-h">图外引用 <span class="cnt">' + refs.length + '</span>' +
      '<span class="oos-tip">—— 声明边界：下列治理体系不在本图（门禁是每模块配套非流水线节点等）</span></div>' +
      (refs.length ? refs.map(function (r) {
        return '<div class="oos-it"><span class="oos-n">' + esc(r.name_zh) + '</span>' +
          (r.ref ? '<span class="oos-r">' + esc(r.ref) + '</span>' : '') +
          (r.note_zh ? '<span class="oos-w">' + esc(r.note_zh) + '</span>' : '') + '</div>';
      }).join('') : '<div class="empty">（无）</div>');
  }

  /* 挂载 chip 点击复制：事件委托挂一次（render() 重复重建 DOM 不重复绑） */
  var pipeWired = false;
  function wirePipe() {
    var pipe = document.getElementById('govm-pipeline');
    if (!pipe || pipeWired) return;
    pipeWired = true;
    pipe.addEventListener('click', function (ev) {
      var t = ev.target && ev.target.closest ? ev.target.closest('[data-copy]') : null;
      if (!t) return;
      copyText(t.getAttribute('data-copy'), t);
    });
  }

  setInterval(function () { if (visible()) load(); }, 30000);
  /* 页面切到 govm 时立即拉一次（go() 切 display，用事件捕获不到——轮询兜底+首次延迟，tdm 同款） */
  setTimeout(function () { wirePipe(); load(); }, 1200);
  window.govmReady = true;   /* IIFE 自举完成标志（冒烟测试等待锚，同 tdmToggleMode 先例） */
})();
