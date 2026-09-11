/* 功能模块：外盘迷你卡（ov-mini-cards）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：确定性模拟数据演示版式
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L3344-3380），逻辑零改动。
 * 验收单：ACC-F-OV-MINI-CARDS
 */
/* ==================== 外盘迷你卡 / T分析分时图 / 板块贡献度 ==================== */
function genIntraday(seed,n){
  n=n||241; var r=lcg(seed),pts=[],p=100;
  for(var i=0;i<n;i++){ p+=(r()-0.5)*0.7; pts.push(p); }
  return pts;
}
function miniSpark(seed,up){
  var pts=genIntraday(seed,60);
  var lo=Math.min.apply(null,pts),hi=Math.max.apply(null,pts);
  var path=pts.map(function(v,i){return (i*3.4).toFixed(1)+','+(34-(v-lo)/(hi-lo)*30).toFixed(1);}).join(' ');
  return '<svg viewBox="0 0 204 38" preserveAspectRatio="none" style="width:100%;height:38px;margin-top:4px"><polyline points="'+path+'" fill="none" stroke="'+(up?'#CA3F64':'#25A750')+'" stroke-width="1.5"/></svg>';
}
function renderOverseas(){
  var grid=document.getElementById('ovs-grid'); if(!grid)return;
  var items=[
    {n:'道琼斯',v:'41,208.6',c:'-0.42%',up:0,time:'昨夜收盘',tag:'利空',tc:'b-sell',s:11},
    {n:'纳斯达克',v:'18,542.3',c:'-0.87%',up:0,time:'昨夜收盘',tag:'利空',tc:'b-sell',s:22},
    {n:'标普500',v:'5,912.4',c:'-0.55%',up:0,time:'昨夜收盘',tag:'利空',tc:'b-sell',s:33},
    {n:'恒生指数',v:'24,318',c:'+0.62%',up:1,time:'实时',tag:'利好',tc:'b-buy',s:44},
    {n:'日经225',v:'39,120',c:'+0.21%',up:1,time:'实时·早盘已收',tag:'中性',tc:'b-na',s:55},
    {n:'韩国KOSPI',v:'2,684',c:'-0.18%',up:0,time:'实时',tag:'中性',tc:'b-na',s:66},
    {n:'富时A50期货',v:'13,542',c:'+0.18%',up:1,time:'实时',tag:'弱利好',tc:'b-buy',s:77},
    {n:'美元指数',v:'104.32',c:'+0.31%',up:1,time:'实时',tag:'弱利空',tc:'b-sell',s:88},
    {n:'离岸人民币',v:'7.2412',c:'-0.12%',up:0,time:'实时',tag:'弱利空',tc:'b-sell',s:99},
    {n:'WTI原油',v:'78.42',c:'+1.20%',up:1,time:'实时',tag:'中性',tc:'b-na',s:111},
    {n:'COMEX黄金',v:'2,412.8',c:'+0.40%',up:1,time:'实时',tag:'中性',tc:'b-na',s:122},
    {n:'美债10Y收益率',v:'4.28%',c:'+3bp',up:0,time:'实时',tag:'弱利空',tc:'b-sell',s:133}
  ];
  var html='';
  items.forEach(function(it){
    html+='<div class="card metric"><div class="l">'+it.n+' <span class="dim">'+it.time+'</span></div>'
      +'<div class="v" style="font-size:17px">'+it.v+' <span style="font-size:13px" class="'+(it.up?'up':'down')+'">'+it.c+'</span></div>'
      +miniSpark(it.s,it.up)
      +'<div class="s" style="margin-top:4px">对A股：<span class="badge '+it.tc+'">'+it.tag+'</span></div></div>';
  });
  grid.innerHTML=html;
}

/* 全球指数 hero 迷你走势初始化（2026-09-12 拆件批自 core/app1.js 宿主迁入：
 * 引用 drawLine/genCandles，本文件加载序在 idx-patterns/idx-engine 之后=前向引用安全；
 * 目标 ovx-sp-* 元素当前全站不存在=既有 no-op，忠实保留） */
(function ovxInitSparks(){
  var defs = [
    ['ovx-sp-sh',  4101, '#CA3F64'],
    ['ovx-sp-sz',  4202, '#CA3F64'],
    ['ovx-sp-cyb', 4303, '#25A750'],
    ['ovx-sp-kc',  4404, '#CA3F64'],
    ['ovx-sp-spx', 4505, '#CA3F64'],
    ['ovx-sp-ndx', 4606, '#CA3F64'],
    ['ovx-sp-hsi', 4707, '#25A750']
  ];
  defs.forEach(function(d){
    if (!document.getElementById(d[0])) return;
    drawLine(d[0], genCandles(d[1]).map(function(k){ return k.c; }), d[2], 180, 60);
  });
})();

