/* 功能模块：全局搜索先行版（srch-overlay）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：静态索引表 SRCH_IDX（AI 问答待接入）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4769-4880, L7114-7115），逻辑零改动。
 * 验收单：ACC-F-SEARCH-OVERLAY
 */
/* ==================== I-8 S1 全局搜索先行版（srchXxx：静态索引表——页面/功能/指标/库条目；AI 问答属后端待接入） ==================== */
var SRCH_IDX=[
 {ty:'页面',t:'首页',p:'home',k:'首页 落地 默认 待建设'},
 {ty:'页面',t:'全景总览',p:'overview',k:'总览 决策 资金 持仓 简报 告警 天气 日历'},
 {ty:'页面',t:'项目地图',p:'projmap',k:'项目地图 模块 依赖 全景 depgraph 域 树'},
 {ty:'页面',t:'作战指挥',p:'warroom',k:'作战室 预案 情景矩阵 观察哨 辩论 风险预算 纪律'},
 {ty:'页面',t:'盘中实时',p:'live',k:'盘中 四指数 regime 决策链 风控 下单 日志 逐笔'},
 {ty:'页面',t:'板块全景',p:'sector',k:'板块 主线 梯队 贡献度 逆势榜 板块档案'},
 {ty:'页面',t:'市场情绪',p:'sentiment',k:'情绪 温度计 涨跌停 连板 两融 宽度 异动'},
 {ty:'页面',t:'新闻舆情',p:'news',k:'新闻 双标签 情绪 公告 热点'},
 {ty:'页面',t:'政策资金',p:'policy',k:'政策 国务院 央行 证监会 地方政府 美联储 国家队 社保 汇金 ETF 地缘'},
 {ty:'页面',t:'外盘速览',p:'overseas',k:'外盘 美股 港股 A50 美元 美债 收益率曲线'},
 {ty:'页面',t:'做T分析',p:'t0',k:'做T 分时 点位 回验 T买 T卖'},
 {ty:'页面',t:'盘后复盘',p:'review',k:'复盘 执行 PnL 归因 打板 龙虎榜 战报 因子'},
 {ty:'页面',t:'持仓监控',p:'position',k:'持仓 账号 盈亏日历 收益分析 阶段盈亏 容忍带 相关性'},
 {ty:'页面',t:'回测结果',p:'backtest',k:'回测 绩效 净值 回撤 交易统计 策略档案'},
 {ty:'页面',t:'实验历史',p:'experiment',k:'实验 runs 门控 对比 元数据'},
 {ty:'页面',t:'框架状态',p:'strategy',k:'框架状态 regime 权重 切换历史 适用性核对'},
 {ty:'页面',t:'因子档案',p:'factor',k:'因子 IC IR 分组 衰减 聚类'},
 {ty:'页面',t:'个股档案',p:'stock',k:'个股 F9 股东 财务 筹码 主营 同行'},
 {ty:'页面',t:'条件选股',p:'screener',k:'选股 筛选 条件 方案 宇宙'},
 {ty:'页面',t:'事件日历',p:'calendar',k:'日历 解禁 新股 财报 宏观 倒计时'},
 {ty:'页面',t:'注册表库',p:'reglib',k:'注册表 18 库 条目 factor strategy'},
 {ty:'页面',t:'研评级',p:'rating',k:'研报 评级 目标价 金股 上调 下调'},
 {ty:'页面',t:'数据源监管',p:'datasrc',k:'数据源 SLA 熔断 测速 告警 provider'},
 {ty:'页面',t:'模型页',p:'models',k:'模型 注册 训练 漂移 影子部署'},
 {ty:'页面',t:'AI 对话',p:'aichat',k:'AI 对话 聊天 指挥 qwen ollama 本地大模型 助手'},
 {ty:'页面',t:'AI 任务队列',p:'aitask',k:'AI 任务 队列 agent 智能体 研究助手 审计'},
 {ty:'页面',t:'技术分析',p:'index',k:'技术分析 K线 指标 形态 叠加 时段 多周期'},
 {ty:'页面',t:'宏观分析',p:'macro',k:'宏观 流动性 周期 天气 FRED'},
 {ty:'页面',t:'产业地图',p:'chainmap',k:'产业链 图谱 上下游'},
 {ty:'页面',t:'任务进度',p:'task',k:'任务 进度 失败 调度'},
 {ty:'页面',t:'适应评估',p:'fitness',k:'fitness 适应 度量 PASS FAIL'},
 {ty:'页面',t:'治理分析',p:'govana',k:'治理 门禁 OLAP'},
 {ty:'页面',t:'模块总账',p:'modledger',k:'模块 总账 域 状态 最近使用'},
 {ty:'页面',t:'系统状态',p:'sysstatus',k:'系统 数据管线 券商 熔断 备份'},
 {ty:'页面',t:'架构全景',p:'pano',k:'架构 全景 域 iframe'},
 {ty:'功能',t:'3×3 情景矩阵',p:'warroom',k:'情景 矩阵 方案 点位 失效',a:'W2'},
 {ty:'功能',t:'多空辩论台+历史辩论',p:'warroom',k:'辩论 多头 空头 风控 veto 历史',a:'W4'},
 {ty:'功能',t:'打板复盘（晋级率/收益）',p:'review',k:'打板 晋级率 炸板率 封板 连板',a:'打板复盘'},
 {ty:'功能',t:'因子级归因（Brinson+因子暴露）',p:'review',k:'归因 Brinson 因子暴露 选股 行业',a:'因子级归因'},
 {ty:'功能',t:'盈亏日历',p:'position',k:'盈亏 日历 日收益 月收益',a:'盈亏日历'},
 {ty:'功能',t:'阶段盈亏表',p:'position',k:'阶段盈亏 本周 本月 近三月 上证指数',a:'阶段盈亏'},
 {ty:'功能',t:'收益分析（多账户曲线）',p:'position',k:'收益分析 跑赢指数 收益率 盈亏金额 总资产',a:'收益分析'},
 {ty:'功能',t:'组合政策容忍带',p:'position',k:'容忍带 偏离 集中度 越限 N3',a:'组合政策容忍带'},
 {ty:'功能',t:'板块档案下钻',p:'sector',k:'板块档案 成分股 资金流历史 舆情',a:'板块档案下钻'},
 {ty:'功能',t:'政策流（分源）',p:'policy',k:'政策流 国务院 央行 证监会 美联储',a:'政策流'},
 {ty:'功能',t:'国家队持仓变动',p:'policy',k:'国家队 社保 汇金 增持 减持',a:'国家队持仓变动'},
 {ty:'功能',t:'美债利率深区',p:'overseas',k:'美债 收益率曲线 利差 TIPS 美元指数',a:'美债利率深区'},
 {ty:'功能',t:'两融情绪',p:'sentiment',k:'两融 融资 融券 余额',a:'两融'},
 {ty:'功能',t:'龙虎榜席位',p:'review',k:'龙虎榜 席位 谁在买',a:'龙虎榜'},
 {ty:'功能',t:'新建回测配置条',p:'backtest',k:'新建回测 发起 配置',a:'新建回测'},
 {ty:'功能',t:'框架状态卡',p:'strategy',k:'框架 状态 regime 权重 切换',a:'当前框架状态'}
];
/* 指标/形态条目=IND_CAT 程序化生成；注册表条目=REGLIB_D 程序化生成（单一事实源） */
IND_CAT.forEach(function(gr){gr.items.forEach(function(it){
  SRCH_IDX.push({ty:'指标',t:it.n,p:'index',k:it.k+' '+gr.g+(it.ok?' 已接入':' 待接入')});
});});
var srchHot=-1;
function srchFilter(){
  var inp=document.getElementById('srch-inp'),drop=document.getElementById('srch-drop');
  var q=inp.value.trim().toLowerCase(); srchHot=-1;
  if(!q){drop.classList.remove('open');drop.innerHTML='';return;}
  var hits=SRCH_IDX.filter(function(e){return (e.t+' '+e.k).toLowerCase().indexOf(q)>=0;}).slice(0,14);
  var h='';
  hits.forEach(function(e,i){
    h+='<div class="srch-it" data-i="'+i+'" onclick="srchGo(+'+i+')"><span class="ty">'+e.ty+'</span><span class="tt">'+e.t+'</span><span class="kw">'+e.k.split(' ').slice(0,3).join(' ')+'</span></div>';
  });
  if(!hits.length) h='<div class="srch-it dis"><span class="tt">无匹配条目</span><span class="kw">试试"板块/指标名/库名"</span></div>';
  h+='<div class="srch-it dis" title="自然语言问功能/问数据——LLM 网关已在治理域 prod，交易域实例化走 CAND"><span class="ty">AI</span><span class="tt">AI 问答（"'+inp.value.trim()+'"）</span><span class="kw">待接入 CAND</span></div>';
  drop.innerHTML=h; drop.classList.add('open');
  window.__srchHits=hits;
}
function srchGo(i){
  var e=(window.__srchHits||[])[i]; if(!e)return;
  var drop=document.getElementById('srch-drop'); drop.classList.remove('open');
  document.getElementById('srch-inp').value='';
  var nav=document.querySelector('.nav-item[onclick^="go(\''+e.p+'\'"]');
  if(nav) nav.click();
  if(e.reg&&typeof regSel==='function'){ setTimeout(function(){regSel(e.reg);},80); }
  if(e.a){ setTimeout(function(){
    var hs=document.querySelectorAll('#p-'+e.p+' h3, #p-'+e.p+' summary, #p-'+e.p+' .sec-title');
    for(var j=0;j<hs.length;j++){ if(hs[j].textContent.indexOf(e.a)>=0){ hs[j].scrollIntoView({behavior:'smooth',block:'center'}); break; } }
  },120); }
}
function srchLate(){   /* REGLIB_D 定义在脚本后段——库条目生成与事件绑定延迟调用（脚本尾 srchLate()） */
  Object.keys(REGLIB_D).forEach(function(rk){
    var rd=REGLIB_D[rk]; SRCH_IDX.push({ty:'库',t:rd.cn+'（'+rd.en+'）',p:'reglib',k:rd.en+' 注册表 '+rd.cn,reg:rk});
  });
  var inp=document.getElementById('srch-inp'); if(!inp)return;
  inp.addEventListener('input',srchFilter);
  inp.addEventListener('keydown',function(e){
    var drop=document.getElementById('srch-drop');
    if(e.key==='Enter'){
      e.preventDefault();
      if(srchHot>=0){var its=drop.querySelectorAll('.srch-it:not(.dis)'); if(its[srchHot]){its[srchHot].click(); return;}}
      if((window.__srchHits||[]).length) srchGo(0);
    }
    else if(e.key==='Escape'){ drop.classList.remove('open'); inp.blur(); }
    else if(e.key==='ArrowDown'||e.key==='ArrowUp'){
      e.preventDefault();
      var items=drop.querySelectorAll('.srch-it:not(.dis)'); if(!items.length)return;
      srchHot+=e.key==='ArrowDown'?1:-1;
      if(srchHot<0)srchHot=items.length-1; if(srchHot>=items.length)srchHot=0;
      items.forEach(function(it,j){it.classList.toggle('hot',j===srchHot);});
    }
  });
  document.addEventListener('click',function(e){
    var box=document.querySelector('.side-srch');
    if(box&&!box.contains(e.target)){var d=document.getElementById('srch-drop'); if(d)d.classList.remove('open');}
  });
}
/* I-8 S1 全局搜索：REGLIB_D 就绪后补全库条目+绑定（防 var 赋值未提升时序缺陷） */
srchLate();

/* 全局 UI 工具武装（2026-09-12 拆件批迁入：原 app1.js L7088/L7112——本文件是 37 个页面引擎文件的最后一个，
 * 保证 cm-engine ciRender/ds-spec-chart 等加载期渲染创建的卡片先落 DOM 再被 ⛶ 全屏武装与注解收敛；
 * 其后仍有契约件/app2-4 等约 30 个文件，但均不在加载期创建 .card/.page-sub，覆盖面与原单文件时代等价） */
fsArm();
slimAnnot();
