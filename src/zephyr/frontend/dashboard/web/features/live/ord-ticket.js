/* 功能模块：盘中下单票据+日志过滤（ord-ticket）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：纯前端交互（无数据源）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L3591-3593, L3670-3707），逻辑零改动。
 * 验收单：ACC-F-LIVE-ORD-TICKET
 */

/* ==================== I-5 功能补齐批脚本（stock/screener/calendar/overview+live/review+news/experiment+position） ==================== */
/* ---- I-5 总览增量（ovx 前缀） ---- */
/* ---- 交互实测修复：盘中 委托/成交 tabs + 撤单 + 下单面板（ordXxx） ---- */
function ordTab(k,el){
  document.querySelectorAll('#ord-tabs .tab').forEach(function(t){t.classList.remove('on');});
  el.classList.add('on');
  document.getElementById('ord-tab-ord').style.display=k==='ord'?'':'none';
  document.getElementById('ord-tab-fill').style.display=k==='fill'?'':'none';
}
function ordCancel(el,what){
  if(!confirm('human_gated 确认：撤销委托「'+what+'」？\n（演示——真实撤单通道待接入 I-2）'))return;
  el.textContent='已撤(演示)'; el.style.opacity=0.5; el.onclick=null;
}
function ordDirTgl(){
  var d=document.getElementById('ord-dir');
  d.textContent=d.textContent.indexOf('买入')>=0?'卖出 ▾':'买入 ▾';
}
function ordSubmit(){
  var c=document.getElementById('ord-code').value.trim()||'（空）';
  var q=document.getElementById('ord-qty').value.trim()||'0';
  var p=document.getElementById('ord-px').value.trim()||'0';
  var d=document.getElementById('ord-dir').textContent.indexOf('买入')>=0?'买':'卖';
  var fb=document.getElementById('ord-fb');
  if(!confirm('human_gated 二次确认：'+d+' '+c+' ×'+q+' @'+p+'\n提交后进入 Owner 审批队列（演示——真实下单通道未接，券商接入后转真）')){fb.textContent='已取消';return;}
  fb.textContent='已进入审批队列（演示）：'+d+' '+c+' ×'+q+' @'+p+' · 待 Owner 审批';
}
function ordEstop(){
  var fb=document.getElementById('ord-fb');
  if(!confirm('human_gated 确认：紧急停止——撤销全部待审批/挂单？\n（演示——与熔断开关联动，真实通道待接入 I-2）'))return;
  fb.textContent='紧急停止已触发（演示）：待审批 2 笔已冻结，挂单一键全撤';
}
/* ---- I-5 盘中日志流（log 前缀） ---- */
function logFilter(lv, el){

  document.querySelectorAll('#log-chips .tab').forEach(function(c){ c.classList.remove('on'); });
  el.classList.add('on');
  document.querySelectorAll('#log-stream .log-line').forEach(function(l){
    l.style.display = (lv === 'all' || l.getAttribute('data-lv') === lv) ? '' : 'none';
  });
}
