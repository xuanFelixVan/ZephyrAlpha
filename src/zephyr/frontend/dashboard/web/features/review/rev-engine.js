/* 功能模块：盘后复盘引擎（rev-engine）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 REVIEW_D
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4472-4563），逻辑零改动。
 * 验收单：ACC-F-REVIEW-ENGINE
 */
/* ==================== I-5 盘后复盘：周期切换 + 交易统计（revXxx） ==================== */
var REVIEW_D={
  day:{
    execTitle:'今日执行回看', pnlTitle:'PnL 对账 + 归因',
    exec:[
      ['买 贵州茅台 ×100','<span class="up">✅ 成交 @1712.5</span>','—'],
      ['买 中国平安 ×200','<span class="badge b-warn">未执行</span>','风控拦截：行业集中度超限'],
      ['卖 宁德时代 ×400','<span class="badge b-warn">部分 200</span>','跌停附近流动性不足，剩余挂单价外']
    ],
    pnlL1:'当日已实现盈亏', rl:'+8,412', rlC:'up', df:'0（平）', dfC:'up',
    ur:'+21,308', urC:'up', corp:'今日无',
    alpha:'选股 +1.8% / 行业轮动 +0.9% / 配比 -0.3%',
    tca:'滑点 0.08% · 冲击 0.03% · 佣金 0.05%（优于 VWAP 基准 0.02%）',
    kpi:[['交易次数','14',''],['胜率','64.3%',''],['盈亏比','1.9',''],['平均持仓','3.2 天',''],['最大单笔盈利','+2.1 万','up'],['最大单笔亏损','-0.8 万','down']],
    scene:[['高开高走','5战4胜',80,'g'],['高开平走','3战2胜',67,'g'],['平开高走','4战3胜',75,'g'],['其他','2战0胜',8,'r']],
    sector:[['半导体','4战3胜',75,'g'],['白酒','3战3胜',100,'g'],['AI算力','3战1胜',33,'r'],['新能源','4战2胜',50,'y']]
  },
  week:{
    execTitle:'本周执行回看', pnlTitle:'PnL 对账 + 归因（本周）',
    exec:[
      ['计划委托 32 笔（买 14 / 卖 18）','<span class="up">✅ 成交 28 笔</span>','4 笔未执行：风控拦截 ×2 / 流动性不足 ×2'],
      ['买 贵州茅台 ×100 等买入 14 笔','<span class="up">✅ 成交 13 笔</span>','中国平安风控拦截（行业集中度超限）'],
      ['卖 宁德时代 ×400 等卖出 18 笔','<span class="badge b-warn">成交 15 笔（2 笔部分）</span>','跌停/低流动性场景 3 笔，剩余挂单价外']
    ],
    pnlL1:'本周已实现盈亏', rl:'+31,205', rlC:'up', df:'0（平）', dfC:'up',
    ur:'+18,762', urC:'up', corp:'茅台分红到账，调成本 -1,200',
    alpha:'选股 +3.1% / 行业轮动 +1.4% / 配比 -0.6%',
    tca:'滑点 0.09% · 冲击 0.04% · 佣金 0.05%（与 VWAP 基准持平）',
    kpi:[['交易次数','46',''],['胜率','60.9%',''],['盈亏比','1.7',''],['平均持仓','3.6 天',''],['最大单笔盈利','+3.4 万','up'],['最大单笔亏损','-1.5 万','down']],
    scene:[['高开高走','16战11胜',69,'g'],['高开平走','9战5胜',56,'y'],['平开高走','12战8胜',67,'g'],['其他','9战4胜',44,'r']],
    sector:[['半导体','14战9胜',64,'g'],['白酒','9战7胜',78,'g'],['AI算力','11战5胜',45,'r'],['新能源','12战7胜',58,'y']]
  },
  month:{
    execTitle:'本月执行回看', pnlTitle:'PnL 对账 + 归因（本月）',
    exec:[
      ['计划委托 131 笔（买 58 / 卖 73）','<span class="up">✅ 成交 118 笔</span>','13 笔未执行：风控 ×5 / 流动性 ×6 / 拒单 ×2'],
      ['买入 58 笔','<span class="up">✅ 成交 55 笔</span>','拦截主因：行业集中度 / 单票仓位上限'],
      ['卖出 73 笔','<span class="badge b-warn">成交 63 笔（6 笔部分）</span>','跌停/低流动性场景 8 笔，剩余挂单价外']
    ],
    pnlL1:'本月已实现盈亏', rl:'+96,540', rlC:'up', df:'-320（已查明：分红计税口径）', dfC:'down',
    ur:'+12,430', urC:'up', corp:'2 笔分红到账调成本',
    alpha:'选股 +5.6% / 行业轮动 +2.2% / 配比 -1.1%',
    tca:'滑点 0.10% · 冲击 0.04% · 佣金 0.05%（略劣于 VWAP 基准 0.01%）',
    kpi:[['交易次数','188',''],['胜率','58.5%',''],['盈亏比','1.6',''],['平均持仓','4.1 天',''],['最大单笔盈利','+6.8 万','up'],['最大单笔亏损','-2.9 万','down']],
    scene:[['高开高走','62战38胜',61,'g'],['高开平走','35战19胜',54,'y'],['平开高走','51战31胜',61,'g'],['其他','40战22胜',55,'y']],
    sector:[['半导体','55战33胜',60,'g'],['白酒','34战24胜',71,'g'],['AI算力','48战24胜',50,'y'],['新能源','51战29胜',57,'y']]
  }
};
function revBars(id,rows){
  var box=document.getElementById(id); if(!box) return;
  var h='';
  rows.forEach(function(r){
    h+='<div class="bar-row wide"><span>'+r[0]+' <span class="dim" style="font-size:10px">'+r[1]+'</span></span>'
      +'<div class="bar"><i class="'+r[3]+'" style="width:'+r[2]+'%"></i></div><span>'+r[2]+'%</span></div>';
  });
  box.innerHTML=h;
}
function revRender(p){
  var d=REVIEW_D[p]; if(!d) return;
  var et=document.getElementById('rev-exec-title'); if(et) et.textContent=d.execTitle;
  var pt=document.getElementById('rev-pnl-title'); if(pt) pt.textContent=d.pnlTitle;
  var eb=document.getElementById('rev-exec-body');
  if(eb){
    var h='<tr><th>计划</th><th>实际</th><th>偏差原因</th></tr>';
    d.exec.forEach(function(r){ h+='<tr><td>'+r[0]+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td></tr>'; });
    eb.innerHTML=h;
  }
  var pb=document.getElementById('rev-pnl-body');
  if(pb){
    pb.innerHTML='<tr><td>'+d.pnlL1+'</td><td class="'+d.rlC+'">'+d.rl+'</td><td>对账差异</td><td class="'+d.dfC+'">'+d.df+'</td></tr>'
      +'<tr><td>未实现盈亏</td><td class="'+d.urC+'">'+d.ur+'</td><td>公司行为调成本</td><td>'+d.corp+'</td></tr>'
      +'<tr><td>Alpha 拆解</td><td colspan="3">'+d.alpha+'</td></tr>'
      +'<tr><td>TCA 执行质量</td><td colspan="3">'+d.tca+'</td></tr>';
  }
  var kb=document.getElementById('rev-kpi');
  if(kb){
    var h2='';
    d.kpi.forEach(function(k){
      h2+='<div class="card metric rev-kpi"><div class="l">'+k[0]+'</div><div class="v'+(k[2]?' '+k[2]:'')+'" style="font-size:18px">'+k[1]+'</div></div>';
    });
    kb.innerHTML=h2;
  }
  revBars('rev-scene',d.scene);
  revBars('rev-sector',d.sector);
}
function revSet(p,el){
  var tabs=document.querySelectorAll('#rev-tabs .tab');
  for(var i=0;i<tabs.length;i++) tabs[i].classList.remove('on');
  if(el) el.classList.add('on');
  revRender(p);
}
window.revInit=function(){ revRender('day'); };
