/* 功能模块：美债收益率曲线（usyc-curve）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：确定性模拟数据演示版式
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4657-4674），逻辑零改动。
 * 验收单：ACC-F-OV-USYC-CURVE
 */
function usycRender(){
  var svg=document.getElementById('usyc-svg'); if(!svg)return; svg.innerHTML='';
  var W=520,H=220,L=40,R=20,T=16,B=30;
  var tenors=['2Y','5Y','10Y','30Y'],cur=[3.85,3.92,4.28,4.61],prev=[3.92,3.98,4.22,4.55];
  var lo=3.6,hi=4.8;
  var x=function(i){return L+i*(W-L-R)/3;},yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-B);};
  var g=el('g',{},svg); grid(g,W,L,R,H,T,B);
  [3.8,4.0,4.2,4.4,4.6].forEach(function(v){hlabel(svg,4,yf(v)+3,v.toFixed(1)+'%','#666666',9);});
  polyline(g,prev.map(function(v,i){return[x(i),yf(v)];}),'#59626D',1.2,'3 3');
  polyline(g,cur.map(function(v,i){return[x(i),yf(v)];}),'#3D8BFF',1.8);
  cur.forEach(function(v,i){
    el('circle',{cx:x(i),cy:yf(v),r:3,fill:'#3D8BFF'},g);
    hlabel(svg,x(i)-14,yf(v)-8,v.toFixed(2),'#9ec7ee',9);
    hlabel(svg,x(i)-10,H-8,tenors[i],'#999999',10);
  });
  hlabel(svg,L+8,T+12,'短端低于长端=正常化上行（衰退定价消退）','#888888',10);
}
/* ---- 组合政策容忍带（按账号渲染；real 演示，其余待接入负反馈） ---- */
