/* 2026-09-12 拆件批：本文件收敛为全局宿主 chrome（路由 go/导航/主题/语言/折叠、决策弹层入口、
 * 跨页折卡工具 ovxGo/ovxFold、底部 ticker、通用 UI 工具 fsArm/slimAnnot）。
 * 34 个页面引擎区块已按 TRAE-086/SOP 拆至 features/<page>/（清单：docs/_working/2026-09-12-frontend-split-inventory.md）；
 * 加载链见 core/loader.js（新批按原区块顺序挂接，全局函数名零改动）。
 * 全局搜索 srchLate() 尾调用随 srch-overlay.js 迁出（依赖 IND_CAT/REGLIB_D，加载序保证就绪）。
 */

function go(id, el){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.getElementById('p-'+id).classList.add('active');
  try{ history.replaceState(null,'','#'+id); }catch(e){}   /* 路由写 hash（replaceState 不产生历史堆栈）——刷新后停留当前页（Owner 2026-09-01 报障"刷新回首页"修复） */
  if(el)el.classList.add('active');   /* el 可空守卫：go(id) 单参调用合法（高亮由 GRP_OF 兜底）——子代理复验建议 */
  var GRP_OF={overview:'overview',warroom:'ashare',live:'ashare',sector:'ashare',sentiment:'ashare',news:'ashare',policy:'ashare',overseas:'ashare',t0:'ashare',review:'ashare',position:'ashare',strategy:'ashare',factor:'ashare',backtest:'ashare',experiment:'ashare',screener:'ashare',index:'ashare',stockq:'ashare',stock:'ashare',macro:'ashare',chainmap:'ashare',calendar:'ashare',promotion:'ashare',cryptomarket:'crypto',cryptopos:'crypto',cryptostrat:'crypto',cryptobt:'crypto',cryptoinfo:'crypto',reglib:'data',datasrc:'data',rating:'ashare',aichat:'ai',aitask:'ai',models:'sys',task:'sys',fitness:'sys',govana:'sys',modledger:'sys',sysstatus:'sys',pano:'sys',govm:'sys',design:'sys'};   /* IA 市场轴（2026-08-27）：页→组归属唯一表，跨页跳转元素无 data-grp 时兜底；08-29 增 ai 组（aichat/aitask，R5 第六组）；09-10 datainfo 页并入 download（数据总览合并裁定）；09-15 增 govm（治理操作全景，#govm hash 直达组高亮兜底——promotion 五登记先例） */
  var grp=(el&&el.getAttribute('data-grp'))||GRP_OF[id]||'';   /* F3 顶栏：一级分组高亮同步 */
  document.querySelectorAll('.tb-grp').forEach(function(g){ g.classList.toggle('on', g.getAttribute('data-grp')===grp); });
  var initFn=window[{'stock':'stockInit','stockq':'sqInit','cryptomarket':'cmInit','cryptopos':'cpInit','screener':'scrInit','calendar':'calInit','review':'revInit','news':'annInit','policy':'polInit','experiment':'expInit','position':'posInit','index':'renderIdxAll','reglib':'reglibInit','pano':'panoInit','modledger':'modInit','strategy':'fwInit'}[id]];   /* I-5/I-6/I-8 页级初始化钩子（显式映射防短名失配，幂等） */
  if(typeof initFn==='function') initFn();
  document.dispatchEvent(new CustomEvent('page:show',{detail:id}));   /* v7：切页广播——隐藏页 clientWidth=0 时图表退化坐标系，页面激活后需重绘（app2.js 大盘/板块图表组监听本事件） */
}
/* hash 路由恢复（Owner 2026-09-01 报障"刷新回首页"治本）：加载完成后读 location.hash 回到离开前的页面；
 * 顶栏 ↻/F5 刷新与 Electron webContents.reload() 都保留 URL 含 hash。 */
(function(){
  function restore(){
    var id=(location.hash||'').replace('#','');
    if(id && document.getElementById('p-'+id) && !document.getElementById('p-'+id).classList.contains('active')) go(id);
  }
  window.addEventListener('hashchange', restore);
  if(document.readyState!=='loading') setTimeout(restore,0);
  else document.addEventListener('DOMContentLoaded', function(){ setTimeout(restore,0); });
})();
/* 规划页灰化占位负反馈（IA 市场轴 2026-08-27 Owner 裁定）：点击不出页面，toast 说明，不造假 */
function navDis(e,name){ e.stopPropagation(); gToast('「'+name+'」规划中——币版 I-2 真源就绪后接入，结构占位不造假页面'); }
function gToast(t){
  var el=document.getElementById('g-toast'); if(!el) return;
  el.textContent=t; el.style.display='block';
  clearTimeout(window.__gtT); window.__gtT=setTimeout(function(){ el.style.display='none'; },3600);
}
/* ---- 侧边栏：组折叠 / 图标态折叠（状态 localStorage 记忆） ---- */
function foldGroup(grp,folded){
  grp.classList.toggle('fold',folded);
  var ar=grp.querySelector('.ng-ar'); if(ar) ar.textContent=folded?'▸':'▾';
  var sib=grp.nextElementSibling;
  while(sib&&!sib.classList.contains('nav-group')&&!sib.classList.contains('side-foot')){
    if(sib.classList.contains('nav-item')) sib.classList.toggle('hide',folded);
    sib=sib.nextElementSibling;
  }
}
function tg(grp){
  if(document.querySelector('.app').classList.contains('sd-coll')){ sdToggle(); return; }   /* 图标态点组图标=展开侧边 */
  var folded=!grp.classList.contains('fold');
  foldGroup(grp,folded);
  var st={}; try{st=JSON.parse(localStorage.getItem('zk-nav-fold')||'{}');}catch(e){}
  st[grp.querySelector('.ng-t').textContent]=folded?1:0;
  try{localStorage.setItem('zk-nav-fold',JSON.stringify(st));}catch(e){}
}
function sdToggle(){
  var app=document.querySelector('.app');
  var c=app.classList.toggle('sd-coll');
  document.getElementById('sd-tog').textContent=c?'»':'«';
  try{localStorage.setItem('zk-side-coll',c?'1':'');}catch(e){}
}
(function(){   /* F3 顶栏批：清理左侧栏时代遗留的折叠状态键（防止旧 sd-coll 类污染新骨架） */
  try{ localStorage.removeItem('zk-side-coll'); localStorage.removeItem('zk-nav-fold'); }catch(e){}
})();
/* ---- F3 语言选择占位（tbLangTgl：简体/CNY 默认，English 置灰待接入） ---- */
function tbLangTgl(e){
  e.stopPropagation();
  var d=document.getElementById('tb-lang-drop'); if(d) d.classList.toggle('open');
}
document.addEventListener('click',function(e){
  var l=document.getElementById('tb-lang'),d=document.getElementById('tb-lang-drop');
  if(l&&d&&d.classList.contains('open')&&!l.contains(e.target)) d.classList.remove('open');
});
/* ---- 主题外观占位（tbThemeTgl：深色=当前，浅色待接入——全站色系 v7 为暗色单主题，浅色需整套令牌派生，暂占位） ---- */
function tbThemeTgl(e){
  e.stopPropagation();
  var d=document.getElementById('tb-theme-drop'); if(d) d.classList.toggle('open');
}
document.addEventListener('click',function(e){
  var t=document.getElementById('tb-theme'),d=document.getElementById('tb-theme-drop');
  if(t&&d&&d.classList.contains('open')&&!t.contains(e.target)) d.classList.remove('open');
});
function ovxGo(id, link){
  var nav = null;
  document.querySelectorAll('.nav-item').forEach(function(n){
    var oc = n.getAttribute('onclick') || '';
    if (oc.indexOf("go('" + id + "'") === 0) nav = n;
  });
  if (document.getElementById('p-' + id) && nav) { go(id, nav); return; }
  if (link) { var t = link.textContent; link.textContent = '目标页未施工（演示）'; setTimeout(function(){ link.textContent = t; }, 1500); }
}
/* ovxInitSparks IIFE 已随拆件批迁至 features/overseas/ov-mini-cards.js 尾部
 * （其同步回调引用 drawLine/genCandles=idx-engine/idx-patterns，必须晚于两者加载） */
/* ---- L2 资产卡折叠（Owner 2026-08-27） ---- */
function ovxFold(id,btn){
  var el=document.getElementById(id); if(!el)return;
  var open=el.style.display!=='none';
  el.style.display=open?'none':'block';
  btn.textContent=open?'账户明细 ▾':'账户明细 ▴';
}
/* ==================== G-一 底部 ticker 横条（tkXxx：自定义增减/双击跳转/秒级时钟/折叠/localStorage） ==================== */
var TK_POOL=[
 {sym:'sh',nm:'上证指数',code:'000001.SH',px:'3,087.53',chg:'+0.72%',dir:1,tgt:'index'},
 {sym:'sz',nm:'深证成指',code:'399001.SZ',px:'9,741.20',chg:'+1.05%',dir:1,tgt:'index'},
 {sym:'cy',nm:'创业板指',code:'399006.SZ',px:'1,892.44',chg:'-0.31%',dir:-1,tgt:'index'},
 {sym:'kc',nm:'科创综指',code:'000680.SH',px:'986.12',chg:'+1.48%',dir:1,tgt:'index'},
 {sym:'spx',nm:'标普500',code:'SPX · 昨收',px:'5,612.34',chg:'+0.38%',dir:1,tgt:'overseas'},
 {sym:'ndx',nm:'纳斯达克',code:'NDX · 昨收',px:'18,245.60',chg:'+0.61%',dir:1,tgt:'overseas'},
 {sym:'hsi',nm:'恒生指数',code:'HSI',px:'17,890.22',chg:'-0.42%',dir:-1,tgt:'overseas'},
 {sym:'600519',nm:'贵州茅台',code:'600519.SH',px:'1,712.50',chg:'+0.86%',dir:1,tgt:'stock'},
 {sym:'300750',nm:'宁德时代',code:'300750.SZ',px:'289.40',chg:'-1.24%',dir:-1,tgt:'stock'},
 {sym:'688981',nm:'中芯国际',code:'688981.SH',px:'99.20',chg:'+2.10%',dir:1,tgt:'stock'},
 {sym:'if',nm:'沪深300股指期货',code:'IF',px:'—',chg:'待接入',dir:0,tgt:'none',na:1},
 {sym:'nq',nm:'纳指期货CFD',code:'NQ',px:'—',chg:'待接入',dir:0,tgt:'none',na:1}
];
var TK_DEF=['sh','sz','cy','kc','spx','ndx','hsi'];
var tkList;
try{ tkList=JSON.parse(localStorage.getItem('zk-tk')||'null')||TK_DEF.slice(); }catch(e){ tkList=TK_DEF.slice(); }
var tkEdit=false;
function tkSave(){ try{localStorage.setItem('zk-tk',JSON.stringify(tkList));}catch(e){} }
function tkFind(sym){ for(var i=0;i<TK_POOL.length;i++) if(TK_POOL[i].sym===sym) return TK_POOL[i]; return null; }
function tkRender(){
  var box=document.getElementById('tk-items'); if(!box)return;
  box.className='tk-items'+(tkEdit?' editing':'');
  var h='';
  tkList.forEach(function(sym){
    var it=tkFind(sym); if(!it)return;
    var cls=it.dir>0?'up':(it.dir<0?'down':'na');
    h+='<span class="tk-item '+cls+'" ondblclick="tkJump(\''+it.sym+'\')" title="'+it.nm+' '+it.code+(it.na?'（库内无数据·待接入负反馈）':' · 双击跳转')+'">'
      +'<span class="nm">'+it.nm+'</span><span class="cd">'+it.code+'</span>'
      +'<span class="px">'+it.px+'</span><span class="pc">'+it.chg+'</span>'
      +'<span class="rm" onclick="event.stopPropagation();tkRm(\''+it.sym+'\')" title="从横条移除">−</span></span>';
  });
  box.innerHTML=h||'<span class="tk-item na"><span class="nm">清单为空——点右侧 ＋ 添加</span></span>';
}
function tkTglEdit(){
  tkEdit=!tkEdit;
  var b=document.getElementById('tk-edit-btn');
  b.textContent=tkEdit?'完成':'＋';
  b.classList.toggle('on',tkEdit);
  tkSrchShow(tkEdit);
  tkRender();
}
function tkRm(sym){
  tkList=tkList.filter(function(s){return s!==sym;});
  tkSave(); tkRender();
}
function tkAdd(sym){
  if(tkList.indexOf(sym)<0){ tkList.push(sym); tkSave(); tkRender(); }
  tkSrchRender();
}
function tkSrchShow(open){
  var l=document.getElementById('tk-slist'); if(!l)return;
  l.classList.toggle('open',open);
  if(open){ var inp=document.getElementById('tk-srch'); inp.value=''; tkSrchRender(); setTimeout(function(){inp.focus();},50); }
}
function tkSrchRender(){
  var q=(document.getElementById('tk-srch')||{}).value||''; q=q.trim().toLowerCase();
  var res=document.getElementById('tk-sres'); if(!res)return;
  var h='',cnt=0;
  TK_POOL.forEach(function(it){
    if(q&&it.nm.toLowerCase().indexOf(q)<0&&it.code.toLowerCase().indexOf(q)<0&&it.sym.toLowerCase().indexOf(q)<0) return;
    var inList=tkList.indexOf(it.sym)>=0;
    h+='<div class="tk-si'+(it.na?' na':'')+'"><span>'+it.nm+'<span class="mt">'+it.code+(it.na?' · 待接入':'')+'</span></span>'
      +(inList?'<span class="mt">已在横条</span>':'<span class="add" onclick="tkAdd(\''+it.sym+'\')">＋ 添加</span>')+'</div>';
    cnt++;
  });
  res.innerHTML=h||'<div class="tk-si"><span class="mt">无匹配（演示池 12 项；全市场搜索 I-2）</span></div>';
}
document.addEventListener('click',function(e){
  var l=document.getElementById('tk-slist');
  if(l&&l.classList.contains('open')&&!l.contains(e.target)&&e.target.id!=='tk-edit-btn') tkSrchShow(false);
});
function tkJump(sym){
  if(tkEdit) return;   /* 编辑态不跳转 */
  var it=tkFind(sym); if(!it||it.tgt==='none')return;
  if(it.tgt==='overseas'){ ovxGo('overseas',null); return; }
  if(it.tgt==='index'){
    var nav=null;
    document.querySelectorAll('.nav-item').forEach(function(n){ var oc=n.getAttribute('onclick')||''; if(oc.indexOf("go('index'")===0) nav=n; });
    if(nav) go('index',nav);
    var sels=document.querySelectorAll('.tech-sel');
    for(var i=0;i<sels.length;i++){ if(sels[i].getAttribute('data-sym')===it.sym){ techSwitch(it.sym,sels[i]); return; } }
    techSwitch(it.sym,null); return;
  }
  if(it.tgt==='stock'){ scrGoStock(it.code); return; }
}
function tkTglColl(){
  document.body.classList.toggle('tk-coll');
  var c=document.body.classList.contains('tk-coll');
  document.getElementById('tk-coll-btn').textContent=c?'▴':'▾';
  document.getElementById('tk-coll-btn').title=c?'展开横条':'折叠横条（只留时间）';
  try{localStorage.setItem('zk-tk-coll',c?'1':'0');}catch(e){}
}
function tkClockTick(){
  var d=new Date(),p=function(n){return String(n).padStart(2,'0');};
  var elc=document.getElementById('tk-clock'); if(elc) elc.textContent=p(d.getHours())+':'+p(d.getMinutes())+':'+p(d.getSeconds());
}
setInterval(tkClockTick,1000); tkClockTick();
if(localStorage.getItem('zk-tk-coll')==='1'){ document.body.classList.add('tk-coll'); var cb=document.getElementById('tk-coll-btn'); if(cb){cb.textContent='▴';cb.title='展开横条';} }
tkRender();
/* ==================== 模块缩放 A 案（DS-10）：卡片 ⛶ 全屏聚焦（通用，零逐页改动）+ 主图容器纵向拖拽柄 ==================== */
function fsToggle(card){
  var mask=document.getElementById('fs-mask');
  if(!mask){ mask=document.createElement('div'); mask.id='fs-mask'; mask.className='fs-mask'; mask.innerHTML='<span class="fs-tip">ESC / 点击空白 关闭</span>'; document.body.appendChild(mask);
    mask.addEventListener('click',function(e){ if(e.target===mask||e.target.classList.contains('fs-tip')) fsClose(); });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape') fsClose(); });
  }
  if(card){ card.__fsHome={p:card.parentNode,n:card.nextSibling}; mask.appendChild(card); var b=card.querySelector('.fs-btn'); if(b) b.textContent='✕'; mask.classList.add('open'); }   /* 顺序修复（复验抓出真 bug）：先记原位再移入 mask，否则 ESC 后卡片丢失原位 */
}
function fsClose(){
  var mask=document.getElementById('fs-mask'); if(!mask||!mask.classList.contains('open'))return;
  var card=mask.querySelector('.card');
  if(card&&card.__fsHome){ card.__fsHome.p.insertBefore(card,card.__fsHome.n); var b=card.querySelector('.fs-btn'); if(b) b.textContent='⛶'; }
  mask.classList.remove('open');
}
function fsArm(){
  document.querySelectorAll('.main .card > h3').forEach(function(h){
    if(h.querySelector('.fs-btn'))return;
    h.style.display='flex'; h.style.alignItems='baseline'; h.style.gap='6px';
    var b=document.createElement('span'); b.className='fs-btn'; b.textContent='⛶'; b.title='全屏聚焦（DS-10 模块缩放 A 案）';
    b.onclick=function(e){ e.stopPropagation(); fsToggle(h.parentNode); };
    h.appendChild(b);
  });
  /* 主图容器加纵向拖拽柄（sq 个股行情主图 + 技术分析主图盒） */
  var sq=document.querySelector('.sq-mainbox'); if(sq) sq.classList.add('rsz-y');
}
/* fsArm()/slimAnnot() 调用行已随拆件批迁至 features/search/srch-overlay.js 尾部（原语义=全部加载期渲染之后执行） */
/* ==================== 注解收敛 slimAnnot（Owner 2026-08-26 方向：版面简洁化——核心字保留，副注解收 ⓘ 悬浮；通用转换零逐页改动） ==================== */
function slimAnnot(){
  /* A. page-sub：以「——」为界，前=核心句保留可见，后=注解入 data-tip（无——的短 sub 不动） */
  document.querySelectorAll('.page-sub').forEach(function(s){
    if(s.__slimmed) return; s.__slimmed=1;
    var h=s.innerHTML, cut=h.indexOf('——');
    if(cut>10){
      var core=h.slice(0,cut), tip=h.slice(cut).replace(/<[^>]+>/g,'').trim();
      s.innerHTML=core+' <i class="info-ic" data-tip="'+tip.replace(/"/g,'&quot;')+'">!</i>';
    }
  });
  /* B. 卡标题 h3 内的长 dim 注解（>14 字）→ ⓘ 悬浮（badge 保留可见——演示数据标注纪律不动） */
  document.querySelectorAll('.card h3 .dim').forEach(function(d){
    var t=(d.textContent||'').trim();
    if(t.length>14){
      var i=document.createElement('i');
      i.className='info-ic';
      i.setAttribute('data-tip',t.replace(/"/g,'&quot;'));
      i.textContent='!';
      d.replaceWith(i);
    }
  });
}

