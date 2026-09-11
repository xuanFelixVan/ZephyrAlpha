/* 功能模块：回测+策略链接（fwInit）（btr-links）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：纯前端交互（无数据源）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L5734-5764），逻辑零改动。
 * 验收单：ACC-F-BACKTEST-BTR-LINKS
 */
/* ==================== I-6c backtest+strategy（btrXxx / fwXxx） ==================== */
var FW_W=[
  {n:'主线龙头回踩',w:35,c:'var(--up)'},
  {n:'行业轮动',w:25,c:'var(--blue)'},
  {n:'低估值防御',w:25,c:'var(--purple)'},
  {n:'打板策略',w:10,c:'var(--orange)'},
  {n:'做T增强',w:5,c:'var(--yellow)'}
];
var FW_H=[
  ['08-21','震荡→震荡偏强','主线龙头 30→35%'],
  ['08-14','偏弱→震荡','低估值防御 20→25%'],
  ['08-07','震荡→偏弱','打板策略 15→10%'],
  ['07-31','偏强→震荡','行业轮动 30→25%'],
  ['07-24','震荡→偏强','主线龙头 25→30%']
];
function fwRender(){
  var w=document.getElementById('fw-weights'); if(!w)return;
  w.innerHTML=FW_W.map(function(r){
    return '<div class="bar-row"><span>'+r.n+'</span><div class="bar"><i style="width:'+r.w+'%;background:'+r.c+'"></i></div><span>'+r.w+'%</span></div>';
  }).join('');
  var h=document.getElementById('fw-hist'); if(!h)return;
  h.innerHTML=FW_H.map(function(r){
    return '<div><b>'+r[0]+'</b> '+r[1]+'：<b>'+r[2]+'</b></div>';
  }).join('');
}
window.fwInit=function(){
  if(window.__fwInited)return; window.__fwInited=1;
  fwRender();
};
/* I-5/I-6 预渲染补充（幂等） */
window.fwInit();
