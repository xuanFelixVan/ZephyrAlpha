/* ══════════════════════════════════════════════════════════════
   core/home.js — 首页三件套（R18 首页重构 / R21 结论墙 / R19 布局引擎一期）
   ① vdWall：扫描全站 .vd[data-vd-order] 结论卡 → 按实盘交易顺序克隆进首页墙（镜像；真源=各页卡本体）
   ② vdFb：结论卡 ✓/✗ 反馈（R1 人机回环；落 __fbQueue 演示，I-2 转真 C26）
   ③ modLayout：首页模块布局引擎一期（增删/拖拽换位/12 列栅格改宽/保存/锁定/还原，localStorage）
   ④ ovxAi：首页 AI 迷你对话框（演示回复；真源 C30，红线=AI 永不自己下单）
   ⑤ ovxMap：项目全景地图入口覆盖层（真源=depgraph 7,675 模块×73 域，交互树 I-2 施工）
   ══════════════════════════════════════════════════════════════ */

/* ── R21 结论墙 ── */
var VD_PAGE_NAME = { overseas:'外盘天气', warroom:'作战指挥', live:'大盘分析', sector:'板块全景', sentiment:'市场情绪', news:'新闻舆情', policy:'政策资金', t0:'做T 监控', position:'持仓监控', cryptomarket:'币圈市场', sysstatus:'系统状态' };
function vdWall(){
  var wall = document.getElementById('vd-wall');
  if(!wall) return;
  var cards = Array.prototype.slice.call(document.querySelectorAll('.vd[data-vd-order]'));
  cards.sort(function(a,b){ return (+a.getAttribute('data-vd-order')) - (+b.getAttribute('data-vd-order')); });
  wall.innerHTML = '';
  cards.forEach(function(c){
    var cl = c.cloneNode(true);
    cl.removeAttribute('id');
    var pg = c.getAttribute('data-vd-page');
    var src = cl.querySelector('.vd-src');
    if(src){
      src.textContent = (VD_PAGE_NAME[pg]||pg)+' →';
      src.style.cursor='pointer';
      src.setAttribute('onclick',"go('"+pg+"')");
      src.title='点击去源页看全部因子证据';
    }
    wall.appendChild(cl);
  });
  var n = document.getElementById('vd-wall-n');
  if(n) n.textContent = cards.length;
}

/* ── R1 结论卡反馈（✓/✗，人机回环首站） ── */
function vdFb(btn, ok, ev){
  if(ev){ ev.stopPropagation(); }
  var box = btn.parentNode;
  var bs = box.querySelectorAll('button');
  bs[0].classList.remove('vd-ok-on'); bs[1].classList.remove('vd-no-on');
  btn.classList.add(ok ? 'vd-ok-on' : 'vd-no-on');
  window.__fbQueue = window.__fbQueue || [];
  var card = btn.closest('.vd');
  window.__fbQueue.push({ t: Date.now(), vd: card ? card.getAttribute('data-vd') : '?', ok: ok });
  if(typeof gToast === 'function') gToast(ok ? '已记录「判断正确」——喂校验统计与纠错样本库（演示，I-2 转真 C26）' : '已记录「判断有误」——进纠错样本库反推优化（演示）');
}

/* ── R19 布局引擎一期（首页试点） ── */
var MOD_LS_KEY = 'za-ovx-layout-v1';
function modLayout(){
  var grid = document.getElementById('ovx-grid');
  if(!grid) return;
  var mods = Array.prototype.slice.call(grid.querySelectorAll('[data-mod]'));

  /* 每个模块加 chrome（拖拽柄/移除）+ 宽度档 */
  mods.forEach(function(m){
    if(m.querySelector('.mod-chrome')) return;
    var chrome = document.createElement('div');
    chrome.className = 'mod-chrome';
    chrome.innerHTML = '<button class="mod-drag" title="拖拽换位">⠿</button><button title="移出（可从右侧抽屉加回）" onclick="modHide(\''+m.getAttribute('data-mod')+'\')">✕</button>';
    m.appendChild(chrome);
    var size = document.createElement('div');
    size.className = 'mod-size';
    size.innerHTML = '<button onclick="modSpan(\''+m.getAttribute('data-mod')+'\',4)">⅓</button><button onclick="modSpan(\''+m.getAttribute('data-mod')+'\',6)">½</button><button onclick="modSpan(\''+m.getAttribute('data-mod')+'\',12)">全</button>';
    m.appendChild(size);
    /* HTML5 拖拽换位 */
    chrome.querySelector('.mod-drag').setAttribute('draggable','true');
    chrome.querySelector('.mod-drag').addEventListener('dragstart', function(ev){
      ev.dataTransfer.setData('text/plain', m.getAttribute('data-mod'));
    });
    m.addEventListener('dragover', function(ev){ ev.preventDefault(); });
    m.addEventListener('drop', function(ev){
      ev.preventDefault();
      var srcId = ev.dataTransfer.getData('text/plain');
      var src = grid.querySelector('[data-mod="'+srcId+'"]');
      if(src && src !== m){ grid.insertBefore(src, m); modSave(); }
    });
  });

  modLoad();   /* 还原已存布局 */
  /* 抽屉 */
  var drawer = document.getElementById('mod-drawer');
  if(drawer){
    var list = document.getElementById('mod-drawer-list');
    list.innerHTML = '';
    mods.forEach(function(m){
      var id = m.getAttribute('data-mod');
      var name = m.getAttribute('data-mod-name') || id;
      var d = document.createElement('div');
      d.className = 'md-item' + (m.classList.contains('mod-hide') ? ' off' : '');
      d.innerHTML = '<span>'+name+'</span><span class="st">'+(m.classList.contains('mod-hide')?'已移出 · 点击加回':'在版 · 点击移出')+'</span>';
      d.onclick = function(){ modToggle(id); };
      list.appendChild(d);
    });
  }
}
function modToggleEdit(){
  document.body.classList.toggle('mod-edit');
  var on = document.body.classList.contains('mod-edit');
  var dr = document.getElementById('mod-drawer');
  if(dr) dr.classList.toggle('open', on);
  if(typeof gToast==='function') gToast(on ? '布局编辑模式：⠿拖拽换位 · ⅓½全 改宽 · ✕ 移出 · 改完自动保存' : '已退出布局编辑（方案已存本机）');
}
function modHide(id){ var m=document.querySelector('[data-mod="'+id+'"]'); if(m){ m.classList.add('mod-hide'); modSave(); modLayout(); } }
function modShow(id){ var m=document.querySelector('[data-mod="'+id+'"]'); if(m){ m.classList.remove('mod-hide'); modSave(); modLayout(); } }
function modToggle(id){ var m=document.querySelector('[data-mod="'+id+'"]'); if(m){ m.classList.toggle('mod-hide'); modSave(); modLayout(); } }
function modSpan(id, span){ var m=document.querySelector('[data-mod="'+id+'"]'); if(m){ m.style.setProperty('--span', span); modSave(); } }
function modSave(){
  var grid = document.getElementById('ovx-grid'); if(!grid) return;
  var st = [];
  grid.querySelectorAll('[data-mod]').forEach(function(m){
    st.push({ id:m.getAttribute('data-mod'), span:m.style.getPropertyValue('--span')||'12', hide:m.classList.contains('mod-hide') });
  });
  try{ localStorage.setItem(MOD_LS_KEY, JSON.stringify(st)); }catch(e){}
}
function modLoad(){
  var grid = document.getElementById('ovx-grid'); if(!grid) return;
  var st;
  try{ st = JSON.parse(localStorage.getItem(MOD_LS_KEY)||'null'); }catch(e){ st=null; }
  if(!st) return;
  st.forEach(function(s){
    var m = grid.querySelector('[data-mod="'+s.id+'"]');
    if(!m) return;
    m.style.setProperty('--span', s.span);
    m.classList.toggle('mod-hide', !!s.hide);
    grid.appendChild(m);   /* 按保存顺序重排 */
  });
}
function modReset(){
  try{ localStorage.removeItem(MOD_LS_KEY); }catch(e){}
  var grid = document.getElementById('ovx-grid');
  if(grid){ grid.querySelectorAll('[data-mod]').forEach(function(m){ m.classList.remove('mod-hide'); m.style.removeProperty('--span'); }); }
  if(typeof gToast==='function') gToast('已还原默认布局');
  modLayout();
}

/* ── R18 AI 迷你对话框（演示） ── */
function ovxAiSend(){
  var inp = document.getElementById('ovx-ai-in');
  var log = document.getElementById('ovx-ai-log');
  if(!inp || !log || !inp.value.trim()) return;
  var q = inp.value.trim(); inp.value='';
  log.innerHTML += '<div class="m-u">你：'+q.replace(/</g,'&lt;')+'</div>';
  var ans = '（演示回复·真源 C30 待接入）收到「'+q.replace(/</g,'&lt;')+'」——我能干的简单活：查页面/查模块/查任务状态/解释概念；红线：永不自己下单，交易指令一律回你确认（human_gated）。完整对话去「AI 组 → AI 对话」页。';
  log.innerHTML += '<div class="m-a">'+ans+'</div>';
  log.scrollTop = log.scrollHeight;
}

/* ── R18 项目全景地图入口覆盖层 ── */
function ovxMap(open){
  var ov = document.getElementById('map-overlay');
  if(ov) ov.classList.toggle('open', !!open);
}

/* ── ⑥ ovxVideo 首页主视觉视频管理（Owner 2026-09-01）──
 * 居中循环播放（画面+声音）；资源纪律：页面隐藏≠视频暂停（DOM section display:none 不停解码），
 * 故挂 page:show 广播——离开首页即 pause()（彻底停解码+静音），回到首页 play() 续播。
 * 无手势自动播放策略：Chromium 默认禁带声 autoplay；Electron 壳已开 no-user-gesture-required，
 * 普通浏览器兜底=先静音播（muted 不受策略限制），首次点击页面任意处恢复声音。 */
var ovxVideo = (function(){
  var v = null, wantSound = true;
  function el(){ return document.getElementById('home-hero-video'); }
  function tryPlay(){
    v = el(); if(!v) return;
    var p = v.play();
    if(p && p.catch) p.catch(function(){
      /* 自动播放被策略拦截 → 静音重试（保画面循环），等用户首次交互后补声音 */
      v.muted = true;
      v.play().catch(function(){});
    });
  }
  document.addEventListener('page:show', function(e){
    v = el(); if(!v) return;
    if(e.detail === 'home'){ tryPlay(); }
    else if(!v.paused){ v.pause(); }   /* 离开首页：停解码零后台占用 */
  });
  /* 浏览器兜底：首次任意点击恢复声音（Electron 壳不受限，走不到这里） */
  document.addEventListener('click', function once(){
    document.removeEventListener('click', once);
    v = el();
    if(v && v.muted && wantSound){ v.muted = false; }
  });
  return { play: tryPlay };
})();

/* ── 初始化（loader 在全部片段注入+app1~4/backtest 后调用） ── */
(function(){
  vdWall();
  modLayout();
  ovxVideo.play();   /* 首页=默认落地页，加载即播（home 是 active 初始页不走 page:show） */
})();
