/* 功能模块：个股行情二级页宿主引擎（sq-host-engine）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示回退 STOCKQ_D+SQ_POOL（真源=sq-* 组件族）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L5866-6197），逻辑零改动。
 * 验收单：ACC-F-STOCKQ-HOST-ENGINE
 */
/* ==================== G-四.A 个股行情二级页引擎（sqXxx：左列表+K线滚轮缩放+指标窗格+筹码峰+事件时间线+报错+右资料面板） ==================== */
var SQ_POOL=[
 {sym:'600519',code:'600519.SH',nm:'贵州茅台',px:'1,712.50',pc:'+0.86%',dir:1},
 {sym:'300750',code:'300750.SZ',nm:'宁德时代',px:'289.40',pc:'-1.24%',dir:-1},
 {sym:'688981',code:'688981.SH',nm:'中芯国际',px:'99.20',pc:'+2.10%',dir:1},
 {sym:'600276',code:'600276.SH',nm:'恒瑞医药',px:'61.20',pc:'+0.45%',dir:1},
 {sym:'002594',code:'002594.SZ',nm:'比亚迪',px:'252.00',pc:'-0.62%',dir:-1},
 {sym:'601318',code:'601318.SH',nm:'中国平安',px:'48.35',pc:'+0.18%',dir:1}
];
var SQ_HOLD=['600519','300750','688981','600276','002594','601318'];   /* 与汇总持仓 3 账户同源 */
var STOCKQ_D={
 '600519':{nm:'贵州茅台',tags:['白酒','沪深300','上证50','中证A50'],intro:'中国白酒绝对龙头，飞天茅台为高端白酒定价锚；渠道库存去化节奏与批价韧性是核心跟踪变量。',
  l2:[[1720.00,12],[1718.50,8],[1716.00,21],[1714.50,15],[1713.00,33],[1712.00,42],[1711.50,26],[1710.00,51],[1708.50,18],[1706.00,29]],
  kv:[['最高','1,725.00'],['最低','1,698.00'],['开盘','1,701.00'],['昨收','1,698.00'],['量比','0.86'],['成交量','2.41 万手'],['成交额','41.2 亿'],['振幅','1.59%'],['换手','0.19%'],['涨停','1,867.80'],['跌停','1,528.20'],['市盈(静)','22.6'],['市盈TTM','21.8'],['总市值','2.15 万亿'],['总股本','12.56 亿'],['流通值','2.15 万亿'],['流通股','12.56 亿'],['外盘','1.28 万手'],['内盘','1.13 万手']],
  guxing:[['涨停成功次数(近一年)','1'],['涨停被砸次数','0'],['封板成功率','100%（1/1）'],['次日高开概率','62%'],['次日平均涨幅','+1.4%']],
  fin:[['ROE(TTM)','26.4%'],['毛利率','91.8%'],['净利率','52.1%'],['资产负债率','18.2%'],['商誉/净资产','0.00%'],['营收(一季)','514.4 亿 +10.7%'],['净利(一季)','268.5 亿 +11.6%'],['经营现金流','286.3 亿']],
  news:[['<b>白酒景气上行</b>：中秋备货批价企稳 2,300 元，渠道信心修复','正面 · 行业轮动信号同源'],['茅台 8 月配额投放节奏放缓，挺价意图明确','正面'],['北向连续 5 日增持茅台，累计 +18.6 亿','正面']],
  val:{t:'2,150.00',n:32,up:'+25.5%',note:'32 家机构一致预期（analyst_forecast 在库 1,628 行）'}},
 '300750':{nm:'宁德时代',tags:['新能源','创业板50','电池龙头'],intro:'全球动力电池市占率第一，麒麟/神行电池技术代差领先；跟踪排产、碳酸锂价格与海外产能落地。',
  l2:[[290.00,45],[289.80,62],[289.60,38],[289.40,74],[289.20,29],[289.00,88],[288.80,53],[288.50,41],[288.00,66],[287.50,37]],
  kv:[['最高','293.80'],['最低','286.20'],['开盘','292.50'],['昨收','293.00'],['量比','1.12'],['成交量','18.6 万手'],['成交额','53.8 亿'],['振幅','2.59%'],['换手','0.48%'],['涨停','351.60'],['跌停','234.40'],['市盈(静)','19.4'],['市盈TTM','18.1'],['总市值','1.27 万亿'],['总股本','44.0 亿'],['流通值','1.13 万亿'],['流通股','39.2 亿'],['外盘','9.2 万手'],['内盘','9.4 万手']],
  guxing:[['涨停成功次数(近一年)','2'],['涨停被砸次数','1'],['封板成功率','67%（2/3）'],['次日高开概率','55%'],['次日平均涨幅','+0.9%']],
  fin:[['ROE(TTM)','21.8%'],['毛利率','25.6%'],['净利率','12.4%'],['资产负债率','62.3%'],['商誉/净资产','0.8%'],['营收(一季)','797.7 亿 -10.4%'],['净利(一季)','105.1 亿 +7.0%'],['经营现金流','212.6 亿']],
  news:[['<b>触发移动止损线</b>：距止损 1.8%，风控已推送审批','风险 · 风控事件'],['神行 Pro 电池发布，4C 快充下放量','正面'],['碳酸锂价格再探 9 万/吨，成本端改善','正面']],
  val:{t:'328.00',n:28,up:'+13.3%',note:'28 家机构一致预期'}},
 '688981':{nm:'中芯国际',tags:['半导体','科创50','国产替代'],intro:'大陆晶圆代工龙头，成熟制程满载、先进制程爬坡；国产化率提升与设备招标是核心催化。',
  l2:[[99.50,120],[99.40,86],[99.30,95],[99.20,140],[99.10,72],[99.00,165],[98.90,98],[98.80,110],[98.60,88],[98.40,76]],
  kv:[['最高','100.20'],['最低','96.80'],['开盘','97.10'],['昨收','97.16'],['量比','1.45'],['成交量','96.2 万手'],['成交额','94.8 亿'],['振幅','3.50%'],['换手','1.21%'],['涨停','116.60'],['跌停','77.72'],['市盈(静)','88.2'],['市盈TTM','76.5'],['总市值','7,902 亿'],['总股本','79.6 亿'],['流通值','3,961 亿'],['流通股','39.9 亿'],['外盘','51.1 万手'],['内盘','45.1 万手']],
  guxing:[['涨停成功次数(近一年)','4'],['涨停被砸次数','2'],['封板成功率','67%（4/6）'],['次日高开概率','68%'],['次日平均涨幅','+2.1%']],
  fin:[['ROE(TTM)','4.2%'],['毛利率','21.5%'],['净利率','8.6%'],['资产负债率','35.1%'],['商誉/净资产','0.00%'],['营收(一季)','125.9 亿 +23.4%'],['净利(一季)','10.8 亿 +12.6%'],['经营现金流','48.2 亿']],
  news:[['<b>半导体设备国产化突破 40%</b>：招标放量，代工产能利用率 95%+','正面 · 主线候选'],['大基金三期拟减持 0.5 亿股','偏空 · 已在政策资金页登记'],['美实体清单新规影响有限（成熟制程为主）','中性']],
  val:{t:'112.00',n:25,up:'+12.9%',note:'25 家机构一致预期'}}
};
var SQ_EVENTS=[
 {dt:'08-26 20:30',tt:'核心PCE物价指数环比（美国）',ic:'📅',pub:'—',exp:'0.2%',prev:'0.1%',imp:'中性偏空',sec:'成长/科技承压，防御相对占优',ana:'预期高于前值=通胀黏性→美元偏强、北向风偏受抑；对 A 股中性偏空。对当前标的影响：外资重仓白马（茅台）受北向变量直接传导，成长股估值边际压制。'},
 {dt:'08-28 09:30',tt:'8 月官方制造业 PMI',ic:'📊',pub:'—',exp:'49.8',prev:'49.5',imp:'中性偏多',sec:'若重回荣枯线附近→顺周期/白酒消费链受益',ana:'预期小幅回升但仍处收缩区间；若超预期→复苏交易升温利好顺周期；不及预期→政策加码预期升温。对当前标的：消费白马看需求端验证。'},
 {dt:'09-01',tt:'宁德时代解禁 1.2 亿股',ic:'🔓',pub:'—',exp:'—',prev:'—',imp:'利空个股/中性板块',sec:'新能源链情绪承压，关注承接力度',ana:'解禁规模约 340 亿元（占流通 3.1%），历史规律：大额解禁前 5 日承压、落地日利空出尽概率高。对当前标的：若为宁德=直接利空；同板块其他标的情绪传导有限。'},
 {dt:'10-31',tt:'三季报披露截止',ic:'📑',pub:'—',exp:'—',prev:'—',imp:'个股分化',sec:'业绩兑现行情，警惕商誉/减值雷',ana:'三季报窗口=业绩验证期：白酒看渠道回款、新能源看排产、半导体看产能利用率。对当前标的：关注毛利率与现金流两个先行指标。'}
];
var sqCur='600519',sqListMode='fav',sqTf='日';
/* 刷新原地续看（2026-09-03 Owner 诉求）：上次浏览的股票/周期/列表模式持久化——刷新不再回默认 600519 */
try{ var _sqs=JSON.parse(localStorage.getItem('zk-sq-state')||'null'); if(_sqs){ if(_sqs.sym)sqCur=_sqs.sym; if(_sqs.tf)sqTf=_sqs.tf; if(_sqs.mode)sqListMode=_sqs.mode; } }catch(e){}
function sqStateSave(){ try{ localStorage.setItem('zk-sq-state',JSON.stringify({sym:sqCur,tf:sqTf,mode:sqListMode})); }catch(e){} }
sqStateSave();
var sqFav; try{ sqFav=JSON.parse(localStorage.getItem('zk-sq-fav')||'null')||['600519','300750','688981']; }catch(e){ sqFav=['600519','300750','688981']; }
function sqPoolFind(sym){ for(var i=0;i<SQ_POOL.length;i++) if(SQ_POOL[i].sym===sym) return SQ_POOL[i]; return null; }
var sqDraw={mode:null,items:[],pend:null};   /* v4.3 KLineChart overlay 接管后废弃，保留空对象防误引用 */
/* ---------- KLineChart 引擎状态（v4.3：自研 canvas 全退役；滚轮缩放/拖拽平移/十字光标/画线/指标均由库内建） ---------- */
var klpChart=null;
var klpDataMode='未启动';   /* 数据源状态灯（DS-12 四态）：真源=绿 / 延迟=黄 / 断线=红（回退演示） / 未启动=灰 */
var klpIndMap={};   /* 指标名 → 窗格 ID（KLineChart v10 分配，用于 removeIndicator 定位） */
var klpPeriodMap={'分时':{span:1,type:'minute'},'1分':{span:1,type:'minute'},'3分':{span:3,type:'minute'},'5分':{span:5,type:'minute'},'15分':{span:15,type:'minute'},'30分':{span:30,type:'minute'},'60分':{span:60,type:'minute'},'120分':{span:120,type:'minute'},'2小时':{span:2,type:'hour'},'4小时':{span:4,type:'hour'},'6小时':{span:6,type:'hour'},'12小时':{span:12,type:'hour'},'日':{span:1,type:'day'},'2日':{span:2,type:'day'},'3日':{span:3,type:'day'},'5日':{span:5,type:'day'},'周':{span:1,type:'week'},'2周':{span:2,type:'week'},'月':{span:1,type:'month'},'3月':{span:3,type:'month'}};
var KLP_ALL_TFS=['分时','1分','3分','5分','15分','30分','60分','120分','2小时','4小时','6小时','12小时','日','2日','3日','5日','周','2周','月','3月'];   /* 全量周期矩阵（弹层） */
var klpTfVis; try{ klpTfVis=JSON.parse(localStorage.getItem('zk-klp-tfvis')||'null'); }catch(e){}
if(!klpTfVis||!klpTfVis.length) klpTfVis=['分时','5分','15分','30分','60分','日','周','月'];   /* 主栏显示集合（localStorage 记忆，弹层编辑模式可改） */
function klpBars(){   /* genCandles → KLineChart 格式（种子=股票+周期：切票/切周期各自确定性变化；时间戳按周期步长合成） */
  var per=klpPeriodMap[sqTf]||klpPeriodMap['日'];
  var seed=(+sqCur)+per.span*17+({'minute':1,'hour':2,'day':3,'week':4,'month':5}[per.type]||3)*1000+(sqTf==='分时'?7:0);
  var d=genCandles(seed,240);
  var step=per.type==='minute'?per.span*60000:per.type==='hour'?per.span*3600000:per.type==='week'?per.span*7*86400000:per.type==='month'?30*86400000:86400000;
  var end=new Date(2026,7,28).getTime();   /* 演示口径末日基准 */
  if(sqTf==='分时') end=new Date(2026,7,28,15,0).getTime();   /* 分时末日锚定 15:00 收盘 */
  return d.map(function(k,i){ return {timestamp:end-(d.length-1-i)*step,open:+k.o.toFixed(2),high:+k.h.toFixed(2),low:+k.l.toFixed(2),close:+k.c.toFixed(2),volume:Math.round(k.v)}; });
}
function sqInit(){
  sqRenderList();
  if(window.ZK && ZK.features && ZK.features['sq-stock-header']){ ZK.features['sq-stock-header'].init(); }
  if(window.ZK && ZK.features && ZK.features['sq-key-data']){ ZK.features['sq-key-data'].init(); }
  if(window.ZK && ZK.features && ZK.features['sq-sector-tags']){ ZK.features['sq-sector-tags'].init(); }
  if(window.ZK && ZK.features && ZK.features['sq-fav-list']){ ZK.features['sq-fav-list'].init(); }
  if(window.ZK && ZK.features && ZK.features['sq-position-list']){ ZK.features['sq-position-list'].init(); }
  sqRenderHead(); sqRenderInfo();
  var el=document.getElementById('klp-chart');
  if(!el) return;
  if(klpChart){ klpChart.resize(); return; }   /* 幂等：go() 每次 show 都调 sqInit，重进页面只 resize */
  /* 注册 AVL 分时均价线指标（累计成交额/累计成交量；无成交额字段用典型价×量近似，演示口径） */
  klinecharts.registerIndicator({
    name:'AVL', shortName:'均价',
    calcParams:[],
    figures:[{key:'avl',title:'均价',type:'line'}],
    calc:function(bars){
      var r=[],sumPV=0,sumV=0;
      for(var i=0;i<bars.length;i++){
        var b=bars[i],tp=(b.high+b.low+b.close)/3,v=b.volume||1;
        sumPV+=tp*v; sumV+=v;
        r.push({avl:+(sumPV/sumV).toFixed(4)});
      }
      return r;
    }
  });
  /* plainLine 纯横线模板已迁入功能模块 features/cost-line.js（模块契约 pilot；手册 FEH-KLC-001：内置 priceLine 价签删不掉才自注册） */
  /* 注册自定义矩形覆盖物（KLineChart v10 无内置 rect） */
  klinecharts.registerOverlay({
    name:'rect',
    totalStep:3,
    needDefaultPointFigure:true,
    needDefaultXAxisFigure:true,
    needDefaultYAxisFigure:true,
    mode:'weak_magnet',
    modeSensitivity:8,
    createPointFigures:function(o){
      var cd=o.coordinates;
      if(cd.length<2) return [];
      var x1=cd[0].x,y1=cd[0].y,x2=cd[1].x,y2=cd[1].y;
      return [{type:'rect',attrs:{x:Math.min(x1,x2),y:Math.min(y1,y2),width:Math.abs(x2-x1),height:Math.abs(y2-y1)},styles:{color:'rgba(61,139,255,0.08)',borderColor:'#3D8BFF',borderSize:1,borderStyle:'dashed'}}];
    }
  });
  klpChart=klinecharts.init(el,{
    styles:{
      grid:{horizontal:{color:'#171717',size:1},vertical:{color:'#171717',size:1}},
      candle:{
        bar:{upColor:'#CA3F64',downColor:'#25A750',upBorderColor:'#CA3F64',downBorderColor:'#25A750',upWickColor:'#CA3F64',downWickColor:'#25A750'},
        priceMark:{high:{color:'#A0A6AD',textSize:10},low:{color:'#A0A6AD',textSize:10},last:{lineColor:'#CA3F64',textBackgroundColor:'#CA3F64',textColor:'#000000'}}
      },
      indicator:{
        ohlc:{upColor:'#CA3F64',downColor:'#25A750'},
        bars:[{style:'fill',upColor:'#CA3F64',downColor:'#25A750'}],
        lines:[{color:'#FFA726',size:1.3},{color:'#EC407A',size:1.3},{color:'#27C6DA',size:1.3},{color:'#3D8BFF',size:1.3},{color:'#AB47BC',size:1.3}],
        lastValueMark:{text:{color:'#A0A6AD',size:10}},
        tooltip:{
          features:[   /* 图上指标标签行操作图标（欧易式：眼睛显隐/齿轮设置/×删除；点击只发 action，行为由订阅实现） */
            {id:'eye',position:'right',type:'path',content:{path:'M1 6 Q5.5 1 10 6 Q5.5 11 1 6 Z M5.5 4.2 A1.8 1.8 0 1 0 5.5 7.8 A1.8 1.8 0 1 0 5.5 4.2',style:'stroke',lineWidth:1.1},size:12,padding:2,margin:{left:6}},
            {id:'gear',position:'right',type:'path',content:{path:'M6 1 L7 1 L7.4 2.4 L8.8 2 L9.6 2.8 L8.8 4.2 L10 4.9 L10 6.1 L8.8 6.8 L9.6 8.2 L8.8 9 L7.4 8.6 L7 10 L6 10 L5.6 8.6 L4.2 9 L3.4 8.2 L4.2 6.8 L3 6.1 L3 4.9 L4.2 4.2 L3.4 2.8 L4.2 2 L5.6 2.4 Z M6.5 4.3 A1.2 1.2 0 1 0 6.5 6.7 A1.2 1.2 0 1 0 6.5 4.3',style:'stroke',lineWidth:1},size:12,padding:2,margin:{left:4}},
            {id:'close',position:'right',type:'path',content:{path:'M2.5 2.5 L9.5 9.5 M9.5 2.5 L2.5 9.5',style:'stroke',lineWidth:1.4},size:12,padding:2,margin:{left:4}}
          ]
        }
      },
      xAxis:{show:false,axisLine:{color:'#2E2E2E'},tickText:{color:'#59626D',size:10},tickLine:{color:'#2E2E2E'}},   /* show:false——隐藏内置时间轴（下方自定义 klp-timeline 为唯一时间轴，Owner 实测两条重复） */
      yAxis:{axisLine:{color:'#2E2E2E'},tickText:{color:'#C6C6C6',size:12},tickLine:{color:'#2E2E2E'}},
      crosshair:{horizontal:{line:{color:'#EDEFF2',style:'dash'},text:{backgroundColor:'#1A1C1E',color:'#EDEFF2'}},vertical:{line:{color:'#EDEFF2',style:'dash'},text:{backgroundColor:'#1A1C1E',color:'#EDEFF2'}}},
      separator:{color:'#1A1C1E'}
    }
  });
  /* 功能模块挂载（模块契约 pilot）：成本线模块 init（plainLine 模板注册随模块迁入 features/cost-line.js） */
  if(window.ZK && ZK.features && ZK.features['cost-line']){ ZK.features['cost-line'].init(klpChart); }
  klpChart.setDataLoader({
    getBars:function(params){   /* v10 数据契约：init 返回全量；forward/backward 返回空（演示口径无更多数据，否则库会无限向前加载卡死主线程——浏览器实证） */
      if(params&&params.type==='init'){
        /* 数据源状态灯（DS-12 四态）：真源绿（数据新鲜）/ 延迟黄（取到但过期）/ 断线红（回退演示）/ 未启动灰 */
        var done=false;
        var freshnessMs={'minute':30*60000,'hour':6*3600000,'day':5*86400000,'week':10*86400000,'month':40*86400000};   /* day=5 天：覆盖周五→周一自然间隔，超=真延迟 */
        var modeOf=function(bars){
          var tp=(klpPeriodMap[sqTf]||{}).type||'day';
          var last=bars&&bars.length?bars[bars.length-1].timestamp:0;
          return (Date.now()-last <= (freshnessMs[tp]||freshnessMs.day)) ? '真源' : '延迟';
        };
        var finish=function(bars,mode){ if(done) return; done=true; klpDataMode=mode; sqRenderHead(); params.callback(bars); };
        /* SWR（2026-09-03 刷新秒出）：缓存直出不依赖 ZK.api（冷加载 hash 直入时 api.js 可能未就位——
         * 2026-09-03 浏览器实测：竞态下原逻辑永久落演示分支，K 线刷新后是假数据且不被网络覆盖） */
        try{
          var klCached=JSON.parse(localStorage.getItem('zk-kl-last')||'null');
          if(klCached && klCached.sym===sqCur && klCached.tf===sqTf && klCached.bars && klCached.bars.length) finish(klCached.bars, modeOf(klCached.bars));
        }catch(e){}
        var klNet=function(){   /* 网络取数：api.js 未就位返回 false 由外层重试；到货后缓存已渲染则 applyNewData 全量覆盖 */
          if(!(window.ZK && ZK.api)) return false;
          ZK.api.fetchKline(sqCur,sqTf).then(function(r){
            if(r && r.ok && r.bars && r.bars.length){
              try{ localStorage.setItem('zk-kl-last',JSON.stringify({sym:sqCur,tf:sqTf,bars:r.bars})); }catch(e){}
              if(done){ klpDataMode=modeOf(r.bars); sqRenderHead(); if(klpChart)klpChart.applyNewData(r.bars); }
              else finish(r.bars, modeOf(r.bars));
            } else { if(!done) finish(klpBars(),'断线'); }
          }).catch(function(){ if(!done) finish(klpBars(),'断线'); });
          return true;
        };
        if(klNet()){
          setTimeout(function(){ finish(klpBars(),'断线'); },6000);   /* 兜底防悬挂 */
        } else {
          var klTries=0;   /* api.js 加载竞态：250ms 轮询至多 10s，就位即取真源（期间缓存/演示已先行渲染） */
          var klWait=setInterval(function(){
            klTries++;
            if(klNet()||klTries>40){ clearInterval(klWait); if(klTries>40&&!done) finish(klpBars(),'未启动'); }
          },250);
        }
      }
      else{ params.callback([]); }
    }
  });
  klpChart.setSymbol({ticker:sqCur,pricePrecision:2,volumePrecision:0});
  klpChart.setPeriod(klpPeriodMap[sqTf]);
  /* 默认指标：MA 主图叠加 + VOL/MACD 副图 */
  klpToggleInd('MA'); klpToggleInd('VOL'); klpToggleInd('MACD');
  /* 画线工具绑定（左栏竖排：工具件 + 功能件磁吸/锁定/显隐） */
  document.querySelectorAll('#klp-drawbar .klp-draw-item').forEach(function(item){
    item.addEventListener('click',function(){
      var mode=item.getAttribute('data-draw'),id=item.id;
      /* 功能件：磁吸/锁定/显隐（不改变工具选中态） */
      if(id==='klp-magnet'){ klpDrawState.magnet=!klpDrawState.magnet; item.classList.toggle('on',klpDrawState.magnet); sqToast(klpDrawState.magnet?'磁吸已开：落点自动吸附 K 线开收高低价':'磁吸已关'); return; }
      if(id==='klp-lock'){ klpDrawState.lock=!klpDrawState.lock; item.classList.toggle('on',klpDrawState.lock); klpChart.overrideOverlay({groupId:'draw',lock:klpDrawState.lock}); sqToast(klpDrawState.lock?'画线已锁定（禁止拖动）':'画线已解锁'); return; }
      if(id==='klp-visible'){ klpDrawState.visible=!klpDrawState.visible; item.classList.toggle('on',klpDrawState.visible); klpChart.overrideOverlay({groupId:'draw',visible:klpDrawState.visible}); return; }
      if(!mode) return;
      /* 工具件：互斥选中 */
      document.querySelectorAll('#klp-drawbar .klp-draw-item').forEach(function(i){ i.classList.remove('on'); });
      item.classList.add('on');
      if(mode==='removeAll'){ klpChart.removeOverlay({groupId:'draw'}); return; }   /* 只清画线组，标注层不受影响 */
      if(mode==='crosshair'){ return; }   /* 十字光标=默认态，无需建 overlay */
      var ov={name:mode,groupId:'draw',lock:klpDrawState.lock,mode:klpDrawState.magnet?'weak_magnet':'normal'};
      if(mode==='text'){   /* 文字标注：先输入文字再落点 */
        var t=prompt('输入标注文字','');
        if(t===null){ item.classList.remove('on'); document.querySelector('#klp-drawbar .klp-draw-item[data-draw="crosshair"]').classList.add('on'); return; }
        ov.name='simpleAnnotation'; ov.extendData=t||'文本';
      }
      klpChart.createOverlay(ov);
      var steps={segment:2,rayLine:2,rect:2,fibonacciLine:2,priceChannelLine:3,parallelStraightLine:3}[ov.name]||1;
      sqToast('在图表上点击 '+steps+' 次落点完成作图');
    });
  });
  /* 筹码峰随十字光标重算（v4.4：crosshair 事件只有像素坐标，convertFromPixel 反查 dataIndex，驱动独立筹码峰模块） */
  klpChart.subscribeAction('onCrosshairChange',function(e){
    if(!klpMarks.chip||!e||e.paneId!=='candle_pane') return;
    var pt=klpChart.convertFromPixel({x:e.x,y:e.y},{paneId:'candle_pane'});
    if(pt&&pt.dataIndex!=null) klpChipRender(pt.dataIndex);
  });
  /* 图上指标标签行操作（眼睛=显隐 / 齿轮=设置弹窗定位 / ×=删除）——v10 只发 action，行为在此实现 */
  klpChart.subscribeAction('onIndicatorTooltipFeatureClick',function(d){
    if(!d||!d.indicator) return;
    var name=d.indicator.name,fid=d.feature&&d.feature.id;
    if(fid==='eye'){ klpChart.overrideIndicator({name:name,visible:!d.indicator.visible}); }
    else if(fid==='gear'){ klpIndTabMode=(KLP_IND_MAIN.indexOf(name)>=0?'main':'sub'); klpIndSel=name; klpIndPop(); }
    else if(fid==='close'){
      klpChart.removeIndicator({name:name});
      delete klpIndMap[name];
      document.querySelectorAll('.klp-ind-tgl').forEach(function(b){ if(b.textContent===name) b.classList.remove('on'); });
    }
  });
  /* 尺寸联动：窗口 resize / 页面重新显示（左右栏收放在 klpTogglePanel 内延迟 resize） */
  window.addEventListener('resize',function(){ if(klpChart) klpChart.resize(); klpTimelineRender(); });
  document.addEventListener('page:show',function(e){ if(e.detail==='stockq'&&klpChart){ klpChart.resize(); klpTimelineRender(); } });
  /* 初始视口滚到最新 K 线（v10 默认不滚） */
  setTimeout(function(){ if(klpChart&&klpChart.scrollToRealTime) klpChart.scrollToRealTime(); },50);
  /* 时间轴模块：可见范围变化同步重渲染（库 action + DOM 事件双保险——v10 部分 action 订阅可能静默失效） */
  try{ klpChart.subscribeAction('onVisibleRangeChange',function(){ klpTimelineRender(); }); }catch(e2){}
  try{ klpChart.subscribeAction('onScroll',function(){ klpTimelineRender(); }); }catch(e2){}
  try{ klpChart.subscribeAction('onZoom',function(){ klpTimelineRender(); }); }catch(e2){}
  var klpTlPending=false;
  function klpTlLazy(){ if(klpTlPending) return; klpTlPending=true; setTimeout(function(){ klpTlPending=false; klpTimelineRender(); },60); }   /* 节流 */
  el.addEventListener('wheel',klpTlLazy,{passive:true});
  el.addEventListener('mouseup',klpTlLazy);
  el.addEventListener('mousemove',function(e){ if(e.buttons>0) klpTlLazy(); });   /* 拖拽平移中 */
  /* 时间轴拖拽调高 */
  var tlGrip=document.getElementById('klp-tl-grip');
  if(tlGrip) tlGrip.addEventListener('mousedown',function(e){
    e.preventDefault();
    var tl=document.getElementById('klp-timeline'),startY=e.clientY,startH=tl.getBoundingClientRect().height;
    function mv(ev){ tl.style.height=Math.max(24,Math.min(64,startH+ev.clientY-startY))+'px'; }
    function up(){ document.removeEventListener('mousemove',mv); document.removeEventListener('mouseup',up); if(klpChart) klpChart.resize(); }
    document.addEventListener('mousemove',mv); document.addEventListener('mouseup',up);
  });
  /* 标注层初始化（买卖点/筹码峰/事件图标，默认全开） */
  klpRefreshMarks();
}
function sqSel(sym){
  sqCur=sym;
  sqStateSave();
  sqRenderList(); sqRenderHead(); sqRenderInfo();
  if(klpChart){ klpChart.setSymbol({ticker:sym,pricePrecision:2,volumePrecision:0}); klpRefreshMarks(); }   /* v10：setSymbol 自动经 dataLoader 重取数，标注层随后重算 */
}
function sqTfSet(tf,elm){
  sqTf=tf;
  sqStateSave();
  document.querySelectorAll('#sq-head .sq-tfs .tab').forEach(function(t){t.classList.remove('on');});
  if(elm)elm.classList.add('on');
  if(!klpChart) return;
  var isTs=(tf==='分时');
  /* 分时模式：面积图样式 + AVL 均价线（KLineChart 无原生分时，v4.4 组合实现）；K 线周期恢复蜡烛样式 */
  klpChart.setStyles({candle:{type:isTs?'area':'candle_solid'}});
  var hasAVL=klpChart.getIndicators({paneId:'candle_pane',name:'AVL'}).length>0;
  if(isTs&&!hasAVL){ klpChart.createIndicator({name:'AVL',paneId:'candle_pane'},true); }
  if(!isTs&&hasAVL){ klpChart.removeIndicator({name:'AVL'}); }
  klpChart.setPeriod(klpPeriodMap[tf]);
  klpRefreshMarks();   /* 标注层随后重算 */
}
function sqRenderHead(){
  /* v2：股票标题已拆为功能模块 sq-stock-header（features/stockq/sq-stock-header.js）
     回退：若模块未加载则保留原内联渲染（兼容旧加载链） */
  if(window.ZK && ZK.features && ZK.features['sq-stock-header']){
    ZK.features['sq-stock-header']._symbol = sqCur;
    ZK.features['sq-stock-header'].render();
    return;
  }
  var p=sqPoolFind(sqCur),d=STOCKQ_D[sqCur];
  var h='<span class="nm">'+(d?d.nm:p.nm)+'</span><span class="cd">'+p.code+(d?'':'（资料待接入）')+'</span>'
    +'<span class="px '+(p.dir>=0?'up':'down')+'">'+p.px+'</span><span class="chg '+(p.dir>=0?'up':'down')+'">'+p.pc+'</span>'
    +'<span class="klp-datamode dm-'+klpDataMode+'" title="数据源状态灯（DS-12）：绿=真源正常 / 黄=数据延迟（取到但过期） / 红=断线（回退演示数据） / 灰=服务未启动">'+(klpDataMode==='真源'?'● 真源':klpDataMode==='延迟'?'● 延迟':klpDataMode==='断线'?'● 断线·演示':'○ 未启动')+'</span>'
    +'<span class="sq-tfs">'+klpTfVis.map(function(t){return '<span class="tab'+(t===sqTf?' on':'')+'" onclick="sqTfSet(\''+t+'\',this)">'+t+'</span>';}).join('')+'<span class="tab klp-tf-more" title="更多周期（含自定义主栏显示/快捷键 1~9）" onclick="klpTfPop(event)">▾</span></span>'
    +'<span class="klp-marks">'
    +'<span class="klp-mark-tgl'+(klpMarks.bs?' on':'')+'" title="量化买卖点：±3 根摆动高低点信号标注（▲买 ▼卖，灰色弱提示）" onclick="klpTglMark(\'bs\',this)">⇅</span>'
    +'<span class="klp-mark-tgl'+(klpMarks.trade?' on':'')+'" title="真实成交买卖点：实盘/回测成交标记（红框 B=买入 绿框 S=卖出）" onclick="klpTglMark(\'trade\',this)">◍</span>'
    +'<span class="klp-mark-tgl'+(klpMarks.chip?' on':'')+'" title="筹码峰：48 桶成本分布+POC 成本线+获利比例，随光标重算" onclick="klpTglMark(\'chip\',this)">▤</span>'
    +'<span class="klp-mark-tgl'+(klpMarks.evt?' on':'')+'" title="事件时间线：财报/解禁/宏观事件图标（整行收展），点击查看详情" onclick="klpTglMark(\'evt\',this)">⚑</span>'
    +'<span class="klp-mark-tgl'+(klpMarks.cost?' on':'')+'" title="成本线：筹码峰平均成本横线（黄色虚线，悬停显示成本/数量）" onclick="klpTglMark(\'cost\',this)">¥</span>'
    +'</span>'
    +'<span class="sq-togs"><span class="sq-fb" onclick="fbReport(\'chart\',\'K线工作台（'+p.nm+'）\',this)">⚑报错</span></span>';
  document.getElementById('sq-head').innerHTML=h;
}
/* ---------- 指标开关（MA/BOLL/SAR 主图叠加；其余副图独立窗格，可叠多个） ---------- */
function klpToggleInd(name){
  if(!klpChart) return;
  var btn=null;
  document.querySelectorAll('.klp-ind-tgl').forEach(function(b){ if(b.textContent===name) btn=b; });
  var isMain=(name==='MA'||name==='BOLL'||name==='SAR');
  if(klpIndMap[name]){
    /* 移除：v10 removeIndicator(filter) 按 name 匹配 */
    klpChart.removeIndicator({name:name});
    delete klpIndMap[name];
    if(btn) btn.classList.remove('on');
  }else{
    /* 添加：v10 createIndicator(value, isStack)——paneId 在 indicator 对象上指定；calcParams/styles 走逐线编辑配置（v4.5） */
    var spec=klpIndSpec(name);
    if(isMain) spec.paneId='candle_pane';
    var pid=klpChart.createIndicator(spec,isMain);
    klpIndMap[name]=pid||name;
    if(btn) btn.classList.add('on');
  }
}
/* ---------- 模块化布局：左右栏显隐（title 随状态切换中文提示） ---------- */
function klpTogglePanel(side){
  var el2=document.getElementById('klp-'+side);
  if(!el2) return;
  el2.classList.toggle('collapsed');
  var collapsed=el2.classList.contains('collapsed');
  var btn=document.getElementById('klp-tgl-'+(side==='left'?'l':'r'));
  if(btn) btn.title=side==='left'?(collapsed?'显示列表':'隐藏列表'):(collapsed?'显示资料':'隐藏资料');
  if(klpChart) setTimeout(function(){ klpChart.resize(); },220);   /* 等 CSS .2s 过渡结束后重算图表尺寸 */
}
/* ---------- 画线竖排整条显隐（欧易式） ---------- */
var klpDrawState={magnet:false,lock:false,visible:true};   /* 画线功能件状态：磁吸/锁定/显隐 */
function klpToggleDrawCol(){
  var dc=document.getElementById('klp-drawcol');
  if(!dc) return;
  dc.classList.toggle('collapsed');
  if(klpChart) setTimeout(function(){ klpChart.resize(); },220);
}
