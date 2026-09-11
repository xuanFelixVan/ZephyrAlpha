/* 功能模块：作战室 3×3 情景矩阵（wr-scenario-matrix）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据（含决策弹层 openDecision/closeDecision）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L77-176），逻辑零改动。
 * 验收单：ACC-F-WR-SCENARIO-MATRIX
 */
/* ==================== 作战室：3×3 情景矩阵方案展开（演示数据；字段契约对齐 MOD-PLAN-005 ScenarioPlan / MOD-PLAN-001 TomorrowBoundary / MOD-SIG-061/062） ==================== */
var WR={
 '00':{t:'高开 >+2% + 高走',act:'进攻',bc:'b-buy',logic:'强势确认：高开且 30 分钟站稳 VWAP，主线延续 → 按进攻档加仓（仓位 ×1.2 缩放）',
   sec:[['半导体','72%','主线概率最高·梯队完整'],['AI 算力','58%','跟随主线']],
   stk:[['中芯国际','龙头','回踩 91.20 不破（box_lower 附近）','8%→12%（×1.2，封顶 firm 8% 单票）','96.80（no_add_price）','89.50（must_exit）','板块涨停家数 <5 即作废','2.8:1','+0.9R'],
        ['中微公司','中军','突破 188.50 放量确认（breakout_confirm：放量站稳10分钟）','6%','195.00','182.00','龙头炸板不回封','2.1:1','+0.5R']],
   bal:'0%（进攻情景不配压舱石）'},
 '01':{t:'高开 >+2% + 平走',act:'观察',bc:'b-na',logic:'高开兑现压力（新闻页双标签：可预测利好=兑现风险）→ 不追高、不开新仓，持仓按 must_exit 纪律管理',
   sec:[],stk:[],bal:'0%'},
 '02':{t:'高开 >+2% + 低走',act:'防守',bc:'b-sell',logic:'冲高回落=利好兑现信号 → 减仓至 5 成；触发=跌破 VWAP 且 30 分钟收不回',
   sec:[],stk:[],bal:'10%（沪深300ETF 底仓）'},
 '10':{t:'平开 ±2% + 高走',act:'进攻·轻仓试',bc:'b-buy',logic:'平开走强=无外盘借力下的内生强势 → 买主线龙头回踩（最可能格：W3 观察哨逐项确认后执行）',
   sec:[['半导体','72%','主线概率最高（MOD-SIG-061）'],['机器人','51%','次主线候选']],
   stk:[['中芯国际','龙头','回踩 90.10（今日 VWAP 上沿）','6%→8%（×1.0）','96.80','89.50','板块涨停家数 <5 即作废','2.5:1','+0.7R'],
        ['汇川技术','中军','突破 62.30 放量确认','5%','65.00','60.10','龙头中芯国际炸板','1.9:1','+0.4R']],
   bal:'0%'},
 '11':{t:'平开 ±2% + 平走',act:'观察',bc:'b-na',logic:'震荡延续 → 以持仓做T为主（联动 T分析页点位），10:00 后不开新仓',
   sec:[],stk:[],bal:'0%'},
 '12':{t:'平开 ±2% + 低走',act:'防守',bc:'b-sell',logic:'弱势确认 → 减仓观察；失效触发=主线跌停 >3 家 → 清进攻仓',
   sec:[],stk:[],bal:'15%（沪深300ETF+中证500ETF）'},
 '20':{t:'低开 <-2% + 高走',act:'黄金坑',bc:'b-buy',logic:'低开翻红=恐慌盘被主力接走（需 D2 竞价量 ≥1.2× 确认，D3>0.6 则信号作废）→ 重仓低吸主线',
   sec:[['半导体','68%','恐慌低吸主线龙头'],['证券','45%','护盘预期']],
   stk:[['中芯国际','龙头','翻红瞬间 89.80 附近','10%（黄金坑专项）','94.00','87.20','翻红失败回落 VWAP 下方=作废','3.2:1','+1.1R'],
        ['东方财富','中军','站稳 24.50','6%','26.00','23.80','指数二次探底破前低','2.4:1','+0.6R']],
   bal:'10%'},
 '21':{t:'低开 <-2% + 平走',act:'观察',bc:'b-na',logic:'方向不明 → 观望等 30 分钟确认；不抄底（A股社区纪律：低开不翻红不动手）',
   sec:[],stk:[],bal:'20%'},
 '22':{t:'低开 <-2% + 低走',act:'退潮',bc:'b-sell',logic:'退潮信号（空间板被核+主线跌停蔓延）→ 清进攻仓观望，压舱石顶上',
   sec:[],stk:[],bal:'40%（沪深300ETF 25%+中证500ETF 15%，防御性底仓最大化）'}
};
function warRender(k){
  var d=WR[k],h='<div style="border-top:1px solid var(--border);padding-top:10px">'
    +'<div style="font-size:13px;margin-bottom:8px">方案详情：<b>'+d.t+'</b> <span class="badge '+d.bc+'">'+d.act+'</span></div>'
    +'<div style="font-size:12px;color:var(--dim);margin-bottom:10px">'+d.logic+'</div>';
  if(d.sec.length){
    h+='<div class="sec-title" style="margin-top:0">① 买什么板块（主线概率排序，MOD-SIG-061）</div><table><tr><th>板块</th><th>主线概率</th><th>依据</th></tr>';
    d.sec.forEach(function(s){h+='<tr><td>'+s[0]+'</td><td class="up">'+s[1]+'</td><td>'+s[2]+'</td></tr>';});
    h+='</table>';
  }
  if(d.stk.length){
    h+='<div class="sec-title">② 买什么个股（龙头/中军定位，MOD-SIG-062；点位/仓位=MOD-PLAN-001 边界×档位缩放）· 点击个股名看决策卡（A4）</div><table><tr><th>个股</th><th>定位</th><th>买入点位</th><th>仓位</th><th>禁加仓价</th><th>必出价</th><th>失效条件</th><th>盈亏比</th><th>期望值</th></tr>';
    d.stk.forEach(function(s){h+='<tr><td><b style="cursor:pointer;color:var(--text);text-decoration:underline" onclick="openDecision(\''+s[0]+'\')">'+s[0]+'</b></td><td>'+s[1]+'</td><td>'+s[2]+'</td><td>'+s[3]+'</td><td>'+s[4]+'</td><td>'+s[5]+'</td><td class="down">'+s[6]+'</td><td>'+s[7]+'</td><td class="up">'+s[8]+'</td></tr>';});
    h+='</table>';
  }
  if(!d.sec.length){h+='<div style="font-size:12px;color:var(--dim);background:var(--input);border-radius:6px;padding:10px">'+d.act+'情景：不开新仓。持仓按 must_exit_price 纪律管理，触发条件全数值化（可证伪），满足即执行、不满足即等待。</div>';}
  h+='<div class="note">③ 防御压舱石（该情景宽基 ETF 配置）：'+d.bal+'；失效条件=逻辑破坏点（非止损价）——逻辑坏了方案立即作废，不等价格触发</div></div>';
  document.getElementById('wr-detail').innerHTML=h;
}
function warSel(k,el){
  document.querySelectorAll('#wr-grid .wr-cell').forEach(function(c){
    if(c.dataset.ob)c.style.border=c.dataset.ob;
  });
  if(!el.dataset.ob)el.dataset.ob=el.style.border;
  el.style.border='2px solid var(--text)';
  warRender(k);
}
warRender('10');  /* 默认展开最可能格 */
/* A4 决策卡开关 */
function openDecision(name){document.getElementById('dc-name').textContent=name;document.getElementById('decision-mask').style.display='block';}
function closeDecision(){document.getElementById('decision-mask').style.display='none';}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeDecision();});
var expNames=['c1_mock_20260819_sector','c1_mock_20260818_multi','c1_mock_20260817_daban'];
/* 交互实测修复：实验历史净值 JS 渲染 + 勾选 2 run 双线对比（expCk/expNavRender） */
var expCk=[];
function expLine(i){
  var r=lcg(20260800+i*37),pts=[],p=145;
  for(var k=0;k<13;k++){p-=(r()*14+4);pts.push(p);}
  return pts;
}
function expNavRender(){
  var svg=document.getElementById('exp-nav-svg'); if(!svg)return;
  var lv=document.getElementById('exp-nav-lv');
  var idxs=expCk.length?expCk.slice(0,2):[(window.__expCur||0)];
  var cols=['#3D8BFF','#AB47BC'],h='';
  idxs.forEach(function(ri,k){
    var pts=expLine(ri),d='';
    pts.forEach(function(y,j){d+=(j?'L':'M')+(j*50)+','+Math.max(4,Math.min(155,y)).toFixed(0)+' ';});
    h+='<path d="'+d.trim()+'" fill="none" stroke="'+cols[k]+'" stroke-width="1.5"/>';
  });
  svg.innerHTML=h;
  if(lv)lv.innerHTML=idxs.map(function(ri,k){return '<span style="color:'+cols[k]+'">— '+expNames[ri]+'</span>';}).join(' ');
}
function expCkTgl(){
  expCk=[];
  document.querySelectorAll('.exp-ck').forEach(function(c){if(c.checked)expCk.push(+c.dataset.i);});
  if(expCk.length>2){
    var last=expCk[expCk.length-1];
    document.querySelectorAll('.exp-ck').forEach(function(c){c.checked=(+c.dataset.i===expCk[1]||+c.dataset.i===last);});
    expCk=[expCk[1],last];
  }
  expNavRender();
}
function expSel(i, el){
  document.querySelectorAll('.run-item').forEach(r=>r.classList.remove('on'));
  el.classList.add('on');
  window.__expCur=i;
  document.getElementById('exp-title').textContent=expNames[i]+' · 详情';
  expNavRender();
}

