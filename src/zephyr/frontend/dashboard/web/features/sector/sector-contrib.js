/* 功能模块：板块贡献度（sector-contrib）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：确定性模拟数据演示版式
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L3429-3451），逻辑零改动。
 * 验收单：ACC-F-SECTOR-CONTRIB
 */
function renderSectorContrib(){
  var svg=document.getElementById('sector-contrib'); if(!svg)return; svg.innerHTML='';
  var W=1100,H=260,L=10,R=14,T=30,B=14;
  var pts=genIntraday(880001,241); var f=3087.53/pts[240]; pts=pts.map(function(v){return v*f;});
  var lo=Math.min.apply(null,pts),hi=Math.max.apply(null,pts),pad=(hi-lo)*0.15;lo-=pad;hi+=pad;
  var x=function(i){return L+i*(W-L-R)/240;};
  var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-B);};
  var g=el('g',{},svg); grid(g,W,L,R,H,T,B);
  var segs=[[0,30,'半导体+白酒 领涨','#CA3F64'],[30,70,'新能源+地产 拖累','#25A750'],[70,120,'证券+白酒 放量','#CA3F64'],[120,150,'普跌回落','#8a94a6'],[150,240,'半导体+消费电子 强化','#CA3F64']];
  segs.forEach(function(s){
    el('rect',{x:x(s[0]),y:8,width:x(s[1])-x(s[0]),height:H-8-B,fill:s[3],opacity:0.12},g);
    hlabel(g,x(s[0])+6,22,s[2],s[3],10);
  });
  polyline(g,pts.map(function(v,i){return[x(i),yf(v)];}),'#EDEFF2',1.5);
  el('line',{x1:x(120),x2:x(120),y1:8,y2:H-B,stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
}
/* ════════════════════════════════════════════════════════════════════════════
   前端 mock 数据层（2026-08-23 AI-K3-GW-CWIRE，反向账 C 类通道接线）
   每条数据源接口位 ↔ 后端查询接口（src/zephyr/frontend/services/dashboard_feeds.py，
   全部包装 prod 引擎、返回结构化 dict）。当前=演示数据（badge 纪律：页内如实标注），
   真实通道落地后按同名结构替换。
   ════════════════════════════════════════════════════════════════════════════ */
/* BFE-01：query_intraday_buy_sell_points → MOD-SIG-024 盘中 6 买 6 卖（production） */
