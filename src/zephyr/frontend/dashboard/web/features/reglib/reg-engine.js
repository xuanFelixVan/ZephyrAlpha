/* 功能模块：注册表库引擎（reg-engine）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 REGLIB_D
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L5253-5514），逻辑零改动。
 * 验收单：ACC-F-REGLIB-ENGINE
 */
/* ==================== I-6a 注册表库（regXxx） ==================== */
var REGLIB_D={
  factor:{cn:'因子库',en:'factor',n:140,upd:'2026-08-22',
    desc:'量化因子注册中心：每个因子=可复用研究资产，登记方向/计算口径/IC 口径与聚类分组，因子看板（A7/A8）与选股条件均由此供数。',
    fields:['factor_id 因子标识','direction 多空方向','formula 计算口径','ic_window IC 统计窗','cluster 相似组','status 状态'],
    head:['条目ID','名称','类别','方向','IC 均值','状态','更新日期'],
    rows:[
      ['F-0041','行业动量','动量','做多强势行业','0.048','stable','2026-08-20'],
      ['F-0057','北向增持','资金流','做多增持','0.055','stable','2026-08-21'],
      ['F-0009','估值下限','价值','做多低估值','0.031','testing','2026-08-18'],
      ['F-0003','反转因子','反转','做空高涨幅','0.062','stable','2026-08-22'],
      ['F-0112','质量因子','质量','做多高ROE','0.039','candidate','2026-08-15']],
    dist:{stable:96,testing:18,candidate:10}},
  strategy:{cn:'策略库',en:'strategy',n:146,upd:'2026-08-21',
    desc:'策略注册表：每个策略一份档案（说明/绩效/适用环境/离场说明）——策略是资产不是黑箱，作战室方案与回测实验均引用此库 strategy_id。',
    fields:['strategy_id 策略标识','family 策略族','universe_ref 股票池引用','entry/exit 出入场规则','risk_ref 限额引用','status 状态'],
    head:['条目ID','名称','策略族','适用环境','近一年收益','状态','更新日期'],
    rows:[
      ['S-0007','主线龙头回踩','趋势','强主线行情','+32.4%','stable','2026-08-20'],
      ['S-0012','行业轮动','轮动','风格切换期','+18.6%','stable','2026-08-19'],
      ['S-0003','打板策略','情绪','高赚钱效应','+41.2%','testing','2026-08-17'],
      ['S-0015','低估值防御','价值','弱市防御','+9.8%','stable','2026-08-14'],
      ['S-0019','做T增强','T+0','震荡持仓','+6.3%','candidate','2026-08-11']],
    dist:{stable:15,testing:5,candidate:3}},
  technical_indicator:{cn:'技术指标库',en:'technical_indicator',n:41,upd:'2026-08-18',
    desc:'技术指标注册表：技术分析页 39 指标窗格的数据源——每指标登记参数默认值/信号方向/适用周期，指标增删改走注册表而非硬编码。',
    fields:['ind_id 指标标识','params 默认参数','signal_rule 信号规则','period_fit 适用周期','pane_default 默认窗格','status 状态'],
    head:['条目ID','名称','类别','默认参数','信号口径','状态','更新日期'],
    rows:[
      ['I-001','MA 移动平均线','趋势','5/10/20/60','金叉多/死叉空','stable','2026-08-10'],
      ['I-004','MACD','趋势','12/26/9','DIF/DEA 交叉+柱','stable','2026-08-10'],
      ['I-007','RSI 相对强弱','摆动','6/14/24','>70 超买 <30 超卖','stable','2026-08-12'],
      ['I-009','KDJ','摆动','9/3/3','J 值钝化提示','stable','2026-08-12'],
      ['I-012','BOLL 布林线','通道','20/2','触轨回归','stable','2026-08-15'],
      ['I-015','ATR 真实波幅','波动','14','止损间距参考','testing','2026-08-16']],
    dist:{stable:35,testing:4,candidate:2}},
  universe:{cn:'股票池库',en:'universe',n:18,upd:'2026-08-20',
    desc:'股票池注册表：全A/指数成分/自选板块等选股宇宙的统一定义——条件选股与策略回测的 universe 参数只允许引用在册池，杜绝口径漂移。',
    fields:['universe_id 池标识','members_rule 成分规则','rebalance_freq 调样频率','pit_flag PIT 截断','size 当前规模','status 状态'],
    head:['条目ID','名称','成分规则','调样频率','当前规模','状态','更新日期'],
    rows:[
      ['U-001','全A','全部上市A股','日','5420','stable','2026-08-20'],
      ['U-002','沪深300','指数成分','半年','300','stable','2026-08-20'],
      ['U-003','中证500','指数成分','半年','500','stable','2026-08-20'],
      ['U-004','中证1000','指数成分','半年','1000','stable','2026-08-20'],
      ['U-006','创业板50','指数成分','季度','50','stable','2026-08-19'],
      ['U-011','自选股板块','人工维护','手动','36','testing','2026-08-18']],
    dist:{stable:14,testing:3,candidate:1}},
  benchmark:{cn:'基准库',en:'benchmark',n:9,upd:'2026-08-17',
    desc:'业绩比较基准注册表：回测与复盘的超额收益口径基准——每策略档案必须声明 benchmark_ref，防止「换基准美化业绩」。',
    fields:['bench_id 基准标识','index_code 指数代码','weight_rule 加权口径','daily_src 日行情源','status 状态'],
    head:['条目ID','名称','指数代码','加权口径','用途','状态','更新日期'],
    rows:[
      ['B-001','沪深300','000300.SH','自由流通市值','大盘策略基准','stable','2026-08-17'],
      ['B-002','中证500','000905.SH','自由流通市值','中盘策略基准','stable','2026-08-17'],
      ['B-003','中证1000','000852.SH','自由流通市值','小盘策略基准','stable','2026-08-17'],
      ['B-004','万得全A','881001.WI','总市值','全市场基准','stable','2026-08-16'],
      ['B-006','偏股基金指数','885001.WI','等权','相对排名基准','testing','2026-08-12']],
    dist:{stable:8,testing:1,candidate:0}},
  cost_model:{cn:'成本模型库',en:'cost_model',n:6,upd:'2026-08-15',
    desc:'交易成本模型注册表：佣金/印花税/滑点/冲击成本的显式登记——回测必须引用在册成本模型，禁止「零成本回测」虚增业绩。',
    fields:['cost_id 模型标识','commission 佣金','stamp_tax 印花税','slippage 滑点规则','impact 冲击成本','status 状态'],
    head:['条目ID','名称','佣金','印花税','滑点','状态','更新日期'],
    rows:[
      ['C-001','标准零售','万2.5','卖出千1','固定 2bp','stable','2026-08-10'],
      ['C-002','机构低佣','万1.2','卖出千1','固定 1bp','stable','2026-08-10'],
      ['C-003','冲击成本平方根','万1.5','卖出千1','√参与度','testing','2026-08-14'],
      ['C-004','压力成本','万3','卖出千1','固定 5bp','stable','2026-08-15'],
      ['C-005','零成本(禁用)','0','0','0','candidate','2026-08-01']],
    dist:{stable:5,testing:1,candidate:0}},
  execution_algo:{cn:'执行算法库',en:'execution_algo',n:7,upd:'2026-08-14',
    desc:'执行算法注册表：TWAP/VWAP/POV 等拆单执行规则的登记处——「怎么买」与「买什么」分离，执行损耗可归因可复盘。',
    fields:['algo_id 算法标识','schedule 时间切片规则','participation 参与度上限','venue 通道','status 状态'],
    head:['条目ID','名称','切片规则','参与度上限','适用场景','状态','更新日期'],
    rows:[
      ['E-001','TWAP 时间加权','等时间间隔','—','流动性好中小单','stable','2026-08-10'],
      ['E-002','VWAP 量加权','按历史量能','≤10%','大单拆单','stable','2026-08-10'],
      ['E-003','POV 参与度','跟随实时量','≤8%','隐蔽建仓','testing','2026-08-12'],
      ['E-004','冰山单','显小隐大','—','挂单执行','candidate','2026-08-09'],
      ['E-005','收盘集合竞价','尾盘撮合','—','调仓日执行','stable','2026-08-14']],
    dist:{stable:5,testing:1,candidate:1}},
  risk_limit:{cn:'风险限额库',en:'risk_limit',n:12,upd:'2026-08-19',
    desc:'风险限额注册表：单票/行业/换手/回撤/杠杆等硬约束的集中登记——方案生成与回测门控共用同一套限额，违规即拒单。',
    fields:['limit_id 限额标识','scope 作用域','threshold 阈值','breach_action 触发动作','status 状态'],
    head:['条目ID','名称','作用域','阈值','触发动作','状态','更新日期'],
    rows:[
      ['R-001','单票硬顶','组合','8%','拒单','stable','2026-08-10'],
      ['R-002','行业上限','组合','25%','告警+降档','stable','2026-08-10'],
      ['R-003','单日换手上限','组合','15%','拒单','stable','2026-08-12'],
      ['R-004','最大回撤线','组合','12%','降杠杆','stable','2026-08-15'],
      ['R-005','杠杆上限','组合','1.0x','拒单','stable','2026-08-15'],
      ['R-008','单票集中度预警','组合','6%','告警','testing','2026-08-18']],
    dist:{stable:10,testing:1,candidate:1}},
  data_asset:{cn:'数据资产库',en:'data_asset',n:121,upd:'2026-08-22',
    desc:'数据资产注册表：行情/资金/财报/公告等数据集的全量目录——每张表登记粒度/更新频率/PIT 口径，个股档案各卡即按此目录取数。',
    fields:['asset_id 资产标识','granularity 粒度','freq 更新频率','pit_rule PIT 口径','owner 责任管线','status 状态'],
    head:['条目ID','名称','粒度','更新频率','PIT 口径','状态','更新日期'],
    rows:[
      ['D-0001','kline_daily 日K线','股票×日','日','不复权/前复权双存','stable','2026-08-22'],
      ['D-0012','money_flow 资金流向','股票×日','日','当日收盘后','stable','2026-08-22'],
      ['D-0023','top10_holders 前十大股东','股票×报告期','季','披露日入库','stable','2026-08-20'],
      ['D-0031','income_statement 利润表','股票×季','季','披露日入库','stable','2026-08-20'],
      ['D-0044','announcements 公告','股票×篇','实时','发布时间戳','testing','2026-08-21'],
      ['D-0052','index_daily 指数日行情','指数×日','日','收盘后','stable','2026-08-22']],
    dist:{stable:90,testing:21,candidate:10}},
  chart_pattern:{cn:'K线形态库',en:'chart_pattern',n:256,upd:'2026-08-21',
    desc:'K线形态注册表：单根/组合/经典形态的识别规则与统计胜率——形态信号全部可溯源到在册条目，识别引擎按 registry 驱动。',
    fields:['pattern_id 形态标识','bar_count K线根数','detect_rule 识别规则','win_rate 统计胜率','status 状态'],
    head:['条目ID','名称','类别','K线根数','近5年胜率','状态','更新日期'],
    rows:[
      ['P-0012','锤子线','反转·底','1','58.3%','stable','2026-08-20'],
      ['P-0018','看涨吞没','反转·底','2','56.1%','stable','2026-08-20'],
      ['P-0024','启明星','反转·底','3','59.7%','stable','2026-08-21'],
      ['P-0089','双顶','反转·顶','复合','54.2%','stable','2026-08-19'],
      ['P-0103','头肩底','反转·底','复合','61.5%','testing','2026-08-18']],
    dist:{stable:200,testing:36,candidate:20}},
  field_dictionary:{cn:'字段词典',en:'field_dictionary',n:86,upd:'2026-08-16',
    desc:'字段词典：跨表字段的统一中文名/单位/口径定义——所有页面表格列名必须出自词典，杜绝「同一字段三种叫法」。',
    fields:['field_id 字段标识','cn_name 中文名','unit 单位','definition 口径定义','src_tables 来源表','status 状态'],
    head:['条目ID','字段','中文名','单位','口径','状态','更新日期'],
    rows:[
      ['FD-001','close','收盘价','元','不复权原始收盘','stable','2026-08-10'],
      ['FD-007','adj_factor','复权因子','倍','前复权基准','stable','2026-08-10'],
      ['FD-015','turnover_rate','换手率','%','自由流通股本口径','stable','2026-08-12'],
      ['FD-021','pe_ttm','市盈率TTM','倍','滚动四季净利','stable','2026-08-14'],
      ['FD-034','np_parent','归母净利','亿元','归属母公司股东','testing','2026-08-15']],
    dist:{stable:70,testing:10,candidate:6}},
  experiment:{cn:'实验库',en:'experiment',n:34,upd:'2026-08-22',
    desc:'回测实验注册表：每次回测=一条实验记录（参数快照/数据切片/门控结果）——实验可复现、可对比、可审计，复盘页按 exp_id 回溯。',
    fields:['exp_id 实验标识','strategy_ref 策略引用','param_snapshot 参数快照','gate_result 门控结果','metrics 绩效指标','status 状态'],
    head:['条目ID','名称','策略','区间','门控','年化','状态','更新日期'],
    rows:[
      ['EXP-20260820-03','动量v3·中证500','行业动量','2023-01~2026-06','通过','+18.2%','stable','2026-08-20'],
      ['EXP-20260819-01','反转·全A','反转因子','2022-01~2026-06','通过','+14.7%','stable','2026-08-19'],
      ['EXP-20260817-02','打板·情绪增强','打板策略','2024-01~2026-06','未过','+38.1%','testing','2026-08-17'],
      ['EXP-20260815-04','低波防御·300','低估值防御','2023-01~2026-06','通过','+8.9%','stable','2026-08-15'],
      ['EXP-20260812-01','轮动双因子','行业轮动','2022-01~2026-06','未过','+11.3%','candidate','2026-08-12']],
    dist:{stable:20,testing:9,candidate:5}},
  seat:{cn:'龙虎榜席位库',en:'seat',n:58,upd:'2026-08-19',
    desc:'龙虎榜席位注册表：「谁在买」——知名游资/机构席位画像（风格/成功率/常出没题材），情绪面复盘与打板策略的席位归因数据源。',
    fields:['seat_id 席位标识','alias 市场俗称','style 操作风格','hit_rate 上榜成功率','theme_pref 题材偏好','status 状态'],
    head:['条目ID','席位','俗称','风格','上榜成功率','状态','更新日期'],
    rows:[
      ['SE-003','国泰君安上海江苏路','章盟主','趋势龙头','62.4%','stable','2026-08-18'],
      ['SE-011','国泰君安南京太平南路','作手新一','首板挖掘','57.8%','stable','2026-08-18'],
      ['SE-017','兴业证券陕西分公司','方新侠','主线接力','59.2%','stable','2026-08-19'],
      ['SE-024','深南东路营业部','深南哥','题材轮动','51.6%','testing','2026-08-17'],
      ['SE-030','机构专用','机构席位','价投/调仓','—','stable','2026-08-19']],
    dist:{stable:45,testing:8,candidate:5}},
  regime_cycle:{cn:'周期规则库',en:'regime_cycle',n:15,upd:'2026-08-13',
    desc:'周期规则注册表：规则性时间窗口的显式登记（财报季/月末再平衡/节前效应等）——「什么时候容易发生什么」变成可回测的规则条目而非经验口诀。',
    fields:['cycle_id 规则标识','window 时间窗口','trigger 触发条件','action_hint 策略提示','evidence 历史验证','status 状态'],
    head:['条目ID','名称','时间窗口','策略提示','历史验证','状态','更新日期'],
    rows:[
      ['RC-001','财报披露季','1/4/8/10月末','披露前降题材仓','近5季胜率68%','stable','2026-08-10'],
      ['RC-002','两会窗口','3月上旬','政策题材活跃','近10年7次有效','stable','2026-08-10'],
      ['RC-003','月末再平衡','每月末3日','被动资金尾盘异动','—','stable','2026-08-11'],
      ['RC-004','节前效应','长假前5日','缩量降波动','近5年4次有效','testing','2026-08-12'],
      ['RC-005','解禁高峰窗口','解禁日±5日','回避高解禁占比','—','stable','2026-08-13']],
    dist:{stable:11,testing:3,candidate:1}},
  model:{cn:'模型库',en:'model',n:8,upd:'2026-08-16',
    desc:'ML 模型注册表：模型产物的版本化登记（训练集/特征清单/评估指标）——模型是产物不是黑箱，线上引用必须指向在册版本。',
    fields:['model_id 模型标识','algo 算法','feature_set 特征清单','train_window 训练窗','metric 评估指标','status 状态'],
    head:['条目ID','名称','算法','训练窗','关键指标','状态','更新日期'],
    rows:[
      ['M-002','lgbm_alpha_v2','LightGBM','2020-01~2025-12','IC 0.071','stable','2026-08-15'],
      ['M-003','xgb_sector_cls','XGBoost','2021-01~2025-12','Acc 63.2%','testing','2026-08-14'],
      ['M-004','lstm_regime','LSTM','2018-01~2025-12','F1 0.58','candidate','2026-08-12']],
    dist:{stable:2,testing:2,candidate:1}},
  event_calendar:{cn:'事件日历库',en:'event_calendar',n:42,upd:'2026-08-22',
    desc:'事件日历注册表：离散事件类型（宏观发布/解禁/新股/财报/分红）+ PIT 纪律——只登记「当时已知」的排期，事件日历页（I-5）即由本库供数。',
    fields:['event_id 事件标识','type 事件类型','knowledge_date 最早可知日','occur_date 发生日','importance 重要性','status 状态'],
    head:['条目ID','事件类型','发生日','最早可知日','重要性','状态','更新日期'],
    rows:[
      ['EV-0812','宏观发布·CPI','2026-09-09','2026-08-22','高','stable','2026-08-22'],
      ['EV-0823','限售解禁·某300成分','2026-08-28','2026-08-01','中','stable','2026-08-21'],
      ['EV-0831','新股上市·科创板','2026-08-26','2026-08-20','低','stable','2026-08-20'],
      ['EV-0845','财报披露·中报截止','2026-08-31','2026-01-01','高','stable','2026-08-15'],
      ['EV-0852','分红除权·沪深300成分','2026-08-27','2026-07-30','中','testing','2026-08-19']],
    dist:{stable:30,testing:8,candidate:4}},
  macro_indicator:{cn:'宏观指标库',en:'macro_indicator',n:67,upd:'2026-08-20',
    desc:'宏观指标注册表：CPI/PMI/M2/LPR/社融等指标的发布纪律（发布时间/修订规则/滞后期）——宏观分析页取数口径，回测引用按 knowledge_date 截断防未来函数。',
    fields:['macro_id 指标标识','release_rule 发布规则','revision 修订规则','lag_days 滞后天数','impact 影响面','status 状态'],
    head:['条目ID','指标','发布规则','修订','滞后','状态','更新日期'],
    rows:[
      ['MI-001','CPI 同比','每月9日 9:30','修订入次月','T+0','stable','2026-08-20'],
      ['MI-004','官方制造业PMI','每月最后日 9:00','不修订','T+0','stable','2026-08-20'],
      ['MI-009','M2 同比','每月10~15日','可修订','T+0','stable','2026-08-18'],
      ['MI-012','LPR 报价','每月20日 9:15','不修订','T+0','stable','2026-08-20'],
      ['MI-015','社融存量同比','每月10~15日','可修订','T+0','stable','2026-08-18'],
      ['MI-031','美债10Y收益率','日频','不修订','T+1','testing','2026-08-19']],
    dist:{stable:52,testing:10,candidate:5}},
  portfolio_model:{cn:'组合模型库',en:'portfolio_model',n:8,upd:'2026-08-15',
    desc:'组合构建模型注册表：「买多少」——等权/风险平价/均值方差/目标波动等配权规则的登记处，方案页的推荐仓位即由在册模型计算。',
    fields:['pm_id 模型标识','objective 优化目标','constraints 约束引用','lookback 估计窗','turnover_cap 换手上限','status 状态'],
    head:['条目ID','名称','优化目标','估计窗','换手上限','状态','更新日期'],
    rows:[
      ['PM-001','等权配置','分散','—','—','stable','2026-08-10'],
      ['PM-002','风险平价','风险贡献均衡','250日','月 20%','stable','2026-08-12'],
      ['PM-003','均值方差','夏普最大化','250日','月 30%','testing','2026-08-13'],
      ['PM-004','目标波动率','波动率钉住10%','60日','月 25%','stable','2026-08-14'],
      ['PM-005','核心卫星','核心稳+卫星攻','—','—','candidate','2026-08-15']],
    dist:{stable:5,testing:2,candidate:1}}
};
var REGLIB_ORDER=['factor','strategy','technical_indicator','universe','benchmark','cost_model','execution_algo','risk_limit','data_asset','chart_pattern','field_dictionary','experiment','seat','regime_cycle','model','event_calendar','macro_indicator','portfolio_model'];
var regState={sel:'factor'};
function regEsc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function regDistBadge(s){
  if(s==='stable') return '<span class="badge b-pass">stable</span>';
  if(s==='testing') return '<span class="badge b-warn">testing</span>';
  return '<span class="badge b-na">candidate</span>';
}
function regRenderCards(){
  var q=(document.getElementById('reg-srch').value||'').trim().toLowerCase(), shown=0;
  var html=REGLIB_ORDER.map(function(k){
    var d=REGLIB_D[k];
    var hit=!q||d.cn.toLowerCase().indexOf(q)>=0||d.en.toLowerCase().indexOf(q)>=0;
    if(hit) shown++;
    return '<div class="card factor-card reg-card'+(regState.sel===k?' active':'')+'" data-reg="'+k+'" style="'+(hit?'':'display:none')+'" onclick="regSel(\''+k+'\')">'
      +'<div class="reg-card-top"><i class="reg-dot"></i><b>'+d.cn+'</b><span class="dim reg-en">'+d.en+'</span></div>'
      +'<div class="reg-meta"><span><b class="reg-n">'+d.n+'</b> 条目</span><span class="dim">更新 '+d.upd+'</span></div>'
      +'</div>';
  }).join('');
  document.getElementById('reg-grid').innerHTML=html;
  document.getElementById('reg-cnt').textContent=shown+' / 18 库'+(q?' · 过滤中':' · 点击卡片查看详情');
}
function regRenderDetail(){
  var k=regState.sel, d=REGLIB_D[k];
  var tot=d.dist.stable+d.dist.testing+d.dist.candidate;
  var pct=function(v){return (v/tot*100).toFixed(1)};
  var rows=d.rows.map(function(r){
    var tds='<td class="dim">'+regEsc(r[0])+'</td><td><b>'+regEsc(r[1])+'</b></td>';
    for(var i=2;i<r.length-2;i++) tds+='<td>'+regEsc(r[i])+'</td>';
    tds+='<td>'+regDistBadge(r[r.length-2])+'</td><td class="dim">'+r[r.length-1]+'</td>';
    return '<tr>'+tds+'</tr>';
  }).join('');
  var head='<tr>'+d.head.map(function(h){return '<th>'+h+'</th>'}).join('')+'</tr>';
  document.getElementById('reg-detail').innerHTML=
    '<div class="card">'
    +'<h3>'+d.cn+' <span class="dim">'+d.en+' · '+d.n+' 条目 · 最近更新 '+d.upd+'</span> <span class="badge b-na">演示数据</span> <span class="badge b-fail">完整条目 JSON 导出供数后转真（I-2 流程）</span></h3>'
    +'<div style="font-size:12px;color:var(--dim);margin-bottom:10px">'+d.desc+'</div>'
    +'<div class="sec-title" style="margin-top:0">关键字段 <span class="dim">Key Fields</span></div>'
    +'<div style="margin-bottom:12px">'+d.fields.map(function(f){return '<span class="reg-chip">'+regEsc(f)+'</span>'}).join('')+'</div>'
    +'<div class="sec-title" style="margin-top:0">条目样例 <span class="dim">Sample Entries · '+d.rows.length+' / '+d.n+' 行</span></div>'
    +'<table>'+head+rows+'</table>'
    +'<div class="sec-title">状态分布 <span class="dim">stable '+d.dist.stable+' / testing '+d.dist.testing+' / candidate '+d.dist.candidate+'</span></div>'
    +'<div class="reg-dist">'
      +'<i style="width:'+pct(d.dist.stable)+'%;background:var(--down)" title="stable '+d.dist.stable+'"></i>'
      +'<i style="width:'+pct(d.dist.testing)+'%;background:var(--yellow)" title="testing '+d.dist.testing+'"></i>'
      +'<i style="width:'+pct(d.dist.candidate)+'%;background:var(--faint)" title="candidate '+d.dist.candidate+'"></i>'
    +'</div>'
    +'<div class="lv" style="margin-top:6px"><span><i class="reg-lg" style="background:var(--down)"></i>stable '+d.dist.stable+'</span><span><i class="reg-lg" style="background:var(--yellow)"></i>testing '+d.dist.testing+'</span><span><i class="reg-lg" style="background:var(--faint)"></i>candidate '+d.dist.candidate+'</span></div>'
    +'<div class="note">负反馈也是结果：本卡仅展示 '+d.rows.length+' 条样例，完整 '+d.n+' 条目的 JSON 导出属 I-2 供数流程，转真前系统明说「没有」；PIT 类注册表（event_calendar/macro_indicator）引用须按 knowledge_date 截断</div>'
    +'</div>';
}
function regSel(k){
  regState.sel=k;
  document.querySelectorAll('#reg-grid .reg-card').forEach(function(c){c.classList.toggle('active',c.getAttribute('data-reg')===k)});
  regRenderDetail();
}
function regFilter(){regRenderCards()}
window.reglibInit=function(){ regRenderCards(); regRenderDetail(); };
