/* 功能模块：资源排班周历页引擎（rw-engine，MOD-RESCHED-VIEW）
 * 契约：页面引擎模块——全局函数族（页面 onclick/oninput 直接绑定全局名）；
 * 数据源：window.RW_VIEW_DATA（features/resourceweek/rw-data.js，生成器机生禁手改——
 *        本引擎零 fetch、零写路径，纯只读渲染）；
 * 渲染：泳道=实体（246px 名列）× 7 天列（每列 0-1440 分钟线性映射）；块 hover=title 画像。
 * 冲突：RW_VIEW_DATA.conflicts（真源=闸 run_all_checks，block 红块+顶部冲突条）。
 * 刷新：重跑 scripts/governance/generators/generate_resource_week_view.py 后刷新页面（loader 破缓存）。
 * 验收：渲染全部实体（scheduled 泳道块 + unscheduled 清单段）；数据全部来自生成器。
 */
/* ==================== 资源排班周历（rwXxx） ==================== */
var rwState = { filter: '', data: null };

function rwInit() {
  var world = document.getElementById('rw-world');
  if (!world) return;
  var d = window.RW_VIEW_DATA;
  if (!d || !d.lanes) {
    world.innerHTML = '<div style="padding:16px;color:#8a94a6;font-size:12px">rw-data.js 未加载或为空——重跑 generate_resource_week_view.py 生成数据。</div>';
    var meta0 = document.getElementById('rw-meta');
    if (meta0) meta0.textContent = '无数据';
    return;
  }
  rwState.data = d;
  var conflictIds = {};
  (d.conflicts || []).forEach(function (c) {
    if (c.severity === 'block') (c.task_ids || []).forEach(function (t) { conflictIds[t] = c.reason_code; });
  });
  var h = '';
  /* 表头：名列 + 7 天列（每天 24 小时线） */
  h += '<div class="rw-grid">';
  h += '<div class="rw-head" style="text-align:left">实体（' + d.total_entities + '）</div>';
  for (var i = 0; i < 7; i++) h += '<div class="rw-head">' + (d.days[i] || ('D' + i)) + '</div>';
  /* 泳道：排程实体（有时间块）在前，unscheduled 段在后 */
  var scheduled = d.lanes.filter(function (l) { return !l.unscheduled; });
  var unscheduled = d.lanes.filter(function (l) { return l.unscheduled; });
  scheduled.sort(function (a, b) { return a.task_id < b.task_id ? -1 : 1; });
  unscheduled.sort(function (a, b) { return a.task_id < b.task_id ? -1 : 1; });
  scheduled.forEach(function (l) { h += rwLaneHtml(l, conflictIds); });
  /* unscheduled 分隔行 + 常驻/无窗实体清单 */
  h += '<div class="rw-name" style="border-bottom:1px solid #263042;color:#7d8aa0;background:#0a0e16">— 常驻/无窗/手动实体（' + unscheduled.length + '，不占时间块）—</div>';
  h += '<div class="rw-day" style="grid-column:span 7;height:auto;padding:6px 8px;border-bottom:1px solid #263042">';
  h += unscheduled.map(function (l) {
    var cls = 'rw-tag' + (conflictIds[l.task_id] ? ' conflict' : '');
    var tip = rwTip(l);
    return '<span class="' + cls + '" title="' + tip + '" style="display:inline-block;font-size:11px;margin:2px 4px;padding:2px 8px;border-radius:6px;background:#0e2612;border:1px solid #2e7d32;' + (conflictIds[l.task_id] ? 'background:#2a1216;border-color:#7a1f2b;' : '') + '">' + l.task_id + '</span>';
  }).join('');
  h += '</div></div>';
  world.innerHTML = h;
  /* 冲突条 */
  var bar = document.getElementById('rw-confbar');
  if (bar) {
    var blocks = (d.conflicts || []).filter(function (c) { return c.severity === 'block'; });
    var warns = (d.conflicts || []).filter(function (c) { return c.severity === 'warning' || c.severity === 'warn'; });
    if (blocks.length || warns.length) {
      bar.style.display = 'block';
      var bh = '<b style="color:#d05a6a">阻断级冲突 ' + blocks.length + '</b>　';
      blocks.forEach(function (c) {
        bh += '<span class="rw-conf" title="' + rwEsc(c.detail) + '">⛔ ' + rwEsc(c.task_ids.join('+')) + ' · ' + c.reason_code + (c.at ? ' · ' + c.at.slice(0, 16) : '') + '</span>';
      });
      if (warns.length) bh += '<b style="color:#c9a227;margin-left:10px">警示 ' + warns.length + '</b>　' + warns.slice(0, 5).map(function (c) {
        return '<span class="rw-conf" style="border-color:#8a6d1a" title="' + rwEsc(c.detail) + '">⚠ ' + rwEsc(c.task_ids.join('+')) + ' · ' + c.reason_code + '</span>';
      }).join('');
      bar.innerHTML = bh;
    } else {
      bar.style.display = 'none';
    }
  }
  var meta = document.getElementById('rw-meta');
  if (meta) meta.textContent = '生成于 ' + (d.generated_at || '—') + ' · 注册表 ' + (d.registry_sha256 || '—').slice(0, 8) + ' · 排程 ' + d.scheduled + '/' + d.total_entities + ' · 冲突 ' + ((d.conflicts || []).filter(function (c) { return c.severity === 'block'; })).length;
}

function rwLaneHtml(l, conflictIds) {
  var conf = conflictIds[l.task_id];
  var h = '<div class="rw-lane" data-task="' + l.task_id + '">';
  h += '<div class="rw-name" title="' + rwTip(l) + '"' + (conf ? ' style="color:#d05a6a"' : '') + '>' + (conf ? '⛔ ' : '') + rwEsc(l.task_id) + '</div>';
  for (var day = 0; day < 7; day++) {
    h += '<div class="rw-day">';
    for (var hr = 1; hr < 24; hr++) {
      h += '<div class="rw-hour" style="left:' + (hr / 24 * 100) + '%"></div>';
    }
    var slot = null;
    for (var si = 0; si < (l.slots || []).length; si++) if (l.slots[si].dow === day) { slot = l.slots[si]; break; }
    if (slot) {
      slot.ranges.forEach(function (r) {
        var left = r[0] / 1440 * 100, w = Math.max((r[1] - r[0]) / 1440 * 100, 0.3);
        var cls = 'rw-blk' + (l.trading_sensitive ? ' e0' : '') + (conf ? ' conflict' : '');
        h += '<div class="' + cls + '" style="left:' + left + '%;width:' + w + '%" title="' + rwTip(l, r) + '"></div>';
      });
    }
    h += '</div>';
  }
  h += '</div>';
  return h;
}

function rwTip(l, r) {
  var t = l.task_id + '｜' + l.resource_class + '｜池=' + l.pool;
  if (l.exclusive_group && l.exclusive_group.length) t += '｜互斥组=' + l.exclusive_group.join(',');
  if (l.peak_mem_gb != null) t += '｜申报内存=' + l.peak_mem_gb + 'GB';
  if (l.measured_peak_mem_gb != null) t += '｜实测=' + l.measured_peak_mem_gb + 'GB';
  if (l.measured_p90_duration_min != null) t += '｜P90时长=' + l.measured_p90_duration_min + 'min';
  if (l.window_expr) t += '｜cron=' + l.window_expr;
  if (r) t += '｜本周块=' + r[0] + '→' + r[1] + '分';
  return rwEsc(t);
}

function rwEsc(s) {
  return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function rwFilter(q) {
  rwState.filter = (q || '').trim().toLowerCase();
  var lanes = document.querySelectorAll('#rw-world .rw-lane');
  lanes.forEach(function (el) {
    var tid = (el.getAttribute('data-task') || '').toLowerCase();
    var tag = el.nextElementSibling; /* unscheduled 标签行不随 lane 隐藏 */
    el.style.display = (!rwState.filter || tid.indexOf(rwState.filter) >= 0) ? '' : 'none';
  });
  /* unscheduled 标签过滤：直接操作分隔行后的 span（在 grid 里，无独立容器——按 title 匹配） */
  document.querySelectorAll('#rw-world .rw-day .rw-tag').forEach(function (sp) {
    if (!rwState.filter) { sp.style.display = ''; return; }
    var name = (sp.getAttribute('title') || '').toLowerCase();
    sp.style.display = name.indexOf(rwState.filter) >= 0 ? '' : 'none';
  });
}

/* 自启动：页面片段先于引擎脚本注入（loader 保序），DOM 就绪即可渲染 */
(function () {
  if (document.getElementById('rw-world')) rwInit();
  else setTimeout(function () { if (document.getElementById('rw-world')) rwInit(); }, 300);
})();
