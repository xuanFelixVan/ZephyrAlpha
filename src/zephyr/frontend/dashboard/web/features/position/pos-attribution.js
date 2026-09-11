/* 功能模块：盈亏归因+experiment 阶段门控（pos-attribution）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 POS_ATTR
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4881-4908），逻辑零改动。
 * 验收单：ACC-F-POS-ATTRIBUTION
 */
/* ==================== I-5 experiment+position：阶段门控 / 盈亏归因 ==================== */
window.expInit=function(){
  if(window.__expInited)return; window.__expInited=1;
  if(window.expNames&&expNames.length<5){
    expNames.push('c1_mock_20260815_sector_v2','c1_mock_20260814_defensive');
  }
  expNavRender();
};
var POS_ATTR={
  stocks:[['中芯国际','+1.82 万',1.82,100],['贵州茅台','+1.05 万',1.05,58],['中微公司','+0.46 万',0.46,25],
          ['宁德时代','-0.64 万',-0.64,35],['隆基绿能','-0.38 万',-0.38,21]],
  sector:[['白酒','+2.31 万',2.31,100],['半导体','+1.12 万',1.12,48],['新能源','-0.88 万',-0.88,38]],
  factor:[['动量','+1.65 万',1.65,100],['质量','+1.20 万',1.20,73],['残差','+1.12 万',1.12,68],['反转','-0.42 万',-0.42,25]],
  total:'合计 +4.55 万 = 当日持仓盈亏（对账闭合）'
};
function posBarRow(label,amt,val,w){
  var cls=val>=0?'g':'r', tc=val>=0?'up':'down';
  return '<div class="bar-row pos-bar-row"><span>'+label+'</span>'
    +'<div class="bar"><i class="'+cls+'" style="width:'+w+'%"></i></div>'
    +'<span class="'+tc+'">'+amt+'</span></div>';
}
function posRenderAttr(){
  var s=document.getElementById('pos-attr-stocks'); if(!s)return;
  s.innerHTML=POS_ATTR.stocks.map(function(r){return posBarRow(r[0],r[1],r[2],r[3]);}).join('');
  document.getElementById('pos-attr-sector').innerHTML=POS_ATTR.sector.map(function(r){return posBarRow(r[0],r[1],r[2],r[3]);}).join('');
  document.getElementById('pos-attr-factor').innerHTML=POS_ATTR.factor.map(function(r){return posBarRow(r[0],r[1],r[2],r[3]);}).join('');
  document.getElementById('pos-attr-total').textContent=POS_ATTR.total;
}
