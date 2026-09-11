/* 功能模块：模块总账引擎（mod-engine）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据（模块行）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L5599-5733），逻辑零改动。
 * 验收单：ACC-F-MODLEDGER-ENGINE
 */
/* ==================== I-6b 模块总账（modXxx） ==================== */
var MOD_DOMS=[
  ['D_REGIME','市场状态'],['D_FACTOR','因子'],['D_BACKTEST','回测'],['D_RISK','风险'],
  ['D_PLAN','计划'],['D_POSITION','持仓'],['D_DATA','数据'],['D_GOVERNANCE','治理'],
  ['D_FRONTEND','前端'],['D_ML_TRAIN','模型训练'],['D_TRADING','交易'],['D_ORCHESTRATOR','编排']
];
var MOD_ST={stable:['stable','b-pass'],testing:['testing','b-test'],planned:['planned','b-warn'],cand:['cand','b-na']};
var MOD_SRC={'学术报告':'b-src-aca','GitHub':'b-src-git','项目报告':'b-src-prj','社区实践':'b-src-com'};
var MOD_D=[
 ['D_REGIME','市场状态检测器','regime_detector','学术报告','Hamilton 区制转换','stable','盘中实时页','日频 regime 判定 + 4 态输出','g','08-23'],
 ['D_REGIME','体制转换检测器','regime_shift_detector','学术报告','CUSUM 变点检测','testing','盘中实时页','分钟级体制切换预警','g','08-22'],
 ['D_REGIME','BM-SEL-04 次日 8 态预测','nextday_8state_forecast','项目报告','90 号 §7 裁定暂缓','planned','作战指挥页 · 待接入','次日开盘形态概率分布','w','—'],
 ['D_REGIME','波动率状态分类器','vol_regime_classifier','学术报告','GARCH(1,1)','stable','盘中实时页','波动三态（低/中/高）标注','g','08-23'],
 ['D_REGIME','趋势强度计','trend_strength_meter','GitHub','ADX 改造','stable','技术分析页','趋势/震荡二分类 + 强度分','y','07-18'],
 ['D_REGIME','市场宽度监视','market_breadth_watch','社区实践','涨跌家数比','stable','全景总览页','涨跌家数 / 新高新低汇总','g','08-23'],
 ['D_REGIME','情绪状态聚合器','sentiment_regime_agg','社区实践','CAND-117 登记','cand','—','新闻情绪 → 状态层输入','w','—'],
 ['D_FACTOR','行业动量因子','industry_momentum_factor','项目报告','','stable','因子档案页','申万一级 20 日动量排名','g','08-23'],
 ['D_FACTOR','北向增持因子','northbound_holding_factor','项目报告','','stable','因子档案页','北向持仓变动日频因子','g','08-23'],
 ['D_FACTOR','GAP-F-38 因子聚类','factor_cluster_engine','社区实践','CAND-038 登记','cand','因子档案页 · 待接入','因子相关谱系聚类去重','w','—'],
 ['D_FACTOR','反转因子（5 日）','reversal_5d_factor','学术报告','Jegadeesh 短期反转','stable','因子档案页','5 日反转 IC 跟踪','g','08-21'],
 ['D_FACTOR','换手率稳定度因子','turnover_stability_factor','社区实践','','stable','因子档案页','换手变异系数反向因子','y','06-30'],
 ['D_FACTOR','财报超预期因子','earnings_surprise_factor','学术报告','PEAD 漂移','testing','因子档案页','公告后漂移窗口收益','g','08-20'],
 ['D_FACTOR','拥挤度合成因子','crowding_composite','项目报告','软拥挤约束（夜班 #205）','stable','风险仪表盘','交易拥挤度 0-100 合成','g','08-23'],
 ['D_FACTOR','量价背离因子','price_volume_diverge_factor','GitHub','CAND-052 登记','cand','—','量价相关系数滚动窗口','w','—'],
 ['D_BACKTEST','回测引擎内核','backtest_engine_core','项目报告','rqalpha 二次封装','stable','回测结果页','事件驱动日/分钟双频','g','08-23'],
 ['D_BACKTEST','绩效归因器','performance_attributor','学术报告','Brinson 分解','stable','回测结果页','行业配置/选股双维归因','g','08-22'],
 ['D_BACKTEST','滑点模型','slippage_model','社区实践','冲击成本平方根律','stable','回测结果页','分档滑点 + 冲击成本','g','08-20'],
 ['D_BACKTEST','成交模拟器','fill_simulator','项目报告','','stable','回测结果页','涨跌停不可成交规则','g','08-23'],
 ['D_BACKTEST','参数扫描器','param_sweep_runner','GitHub','网格/贝叶斯','testing','实验门控页','批量参数组合并行','y','07-02'],
 ['D_BACKTEST','过拟合检验器','overfit_detector','学术报告','Deflated Sharpe','planned','实验门控页 · 待接入','DSR / PBO 双指标门禁','w','—'],
 ['D_BACKTEST','走步前进验证器','walk_forward_validator','学术报告','','testing','回测结果页','滚动样本外一致性','g','08-19'],
 ['D_RISK','回撤守门员','drawdown_guardian','项目报告','','stable','持仓页','组合回撤阈值硬拦截','g','08-23'],
 ['D_RISK','行业集中度约束','industry_concentration_cap','项目报告','夜班 #205/#207','stable','风险仪表盘','单行业暴露上限校验','g','08-23'],
 ['D_RISK','相关性净额器','correlation_netting','学术报告','GAP-F-04','testing','持仓页','高相关持仓合并计风险','g','08-21'],
 ['D_RISK','压力测试引擎','StressTestEngine（MOD-RK-12）','项目报告','BFE-32','stable','盘后复盘页','历史三情景重放','g','08-18'],
 ['D_RISK','流动性风险计','liquidity_risk_meter','学术报告','Amihud 非流动性','stable','风险仪表盘','冲击成本口径流动性分','y','06-12'],
 ['D_RISK','熔断开关','kill_switch','项目报告','','stable','系统状态页','极端行情一键切断交易','g','08-23'],
 ['D_RISK','尾部风险预期缺口','expected_shortfall_es','学术报告','CVaR 97.5% · CAND-044','cand','—','ES 日频估计','w','—'],
 ['D_PLAN','明日边界生成器','TomorrowBoundary（MOD-PLAN-001）','项目报告','','stable','作战指挥页','次日价格边界三件套','g','08-23'],
 ['D_PLAN','情景计划器','ScenarioPlan（MOD-PLAN-005）','项目报告','','stable','作战指挥页','3×3 情景矩阵方案','g','08-23'],
 ['D_PLAN','仓位缩放器','position_scaler','项目报告','','stable','作战指挥页','进攻/防守档仓位系数','g','08-22'],
 ['D_PLAN','信号聚合器','signal_aggregator（MOD-SIG-061/062）','项目报告','','testing','作战指挥页','主线概率 + 梯队完整度','g','08-23'],
 ['D_PLAN','交易计划持久化','plan_persistence','项目报告','','stable','盘后复盘页','计划-执行留痕对照','g','08-20'],
 ['D_PLAN','计划合规审计','plan_compliance_audit','项目报告','CAND-072 登记','cand','—','偏离计划自动标注','w','—'],
 ['D_POSITION','持仓台账','position_ledger','项目报告','','stable','持仓页','实盘/模拟双账簿','g','08-23'],
 ['D_POSITION','盈亏归因器','pnl_attribution','学术报告','逐票→板块→因子','stable','持仓页','三层盈亏拆解','g','08-23'],
 ['D_POSITION','做T辅助器','intraday_t_helper','社区实践','','stable','T分析页','日内点位 + 回补提示','y','07-25'],
 ['D_POSITION','保证金监视器','margin_monitor','项目报告','','planned','持仓页 · 待接入','两融维持担保比例','w','—'],
 ['D_POSITION','红利再投资器','dividend_reinvest','社区实践','','stable','持仓页','除权现金流自动记账','g','08-15'],
 ['D_POSITION','持仓快照同步','position_snapshot_sync','GitHub','','testing','—','券商接口对账快照','g','08-23'],
 ['D_DATA','数据清单生成器','generate_data_inventory','项目报告','121 表扫描','stable','系统状态页','全表扫描 + 异常标注','g','08-23'],
 ['D_DATA','分钟K线构建器','minute_bar_builder','项目报告','','stable','数据管理页','1/5/15/30/60min 聚合','g','08-23'],
 ['D_DATA','复权因子链路','adj_factor_pipeline','项目报告','夜班 #196/#197/#198','testing','数据管理页','前复权因子持续生产','g','08-22'],
 ['D_DATA','北向资金采集器','northbound_collector','项目报告','','stable','数据管理页','港交所持股日频','g','08-23'],
 ['D_DATA','新闻事件抽取器','news_event_extractor','GitHub','FinNLP 改造','testing','新闻公告页','事件标签 + 情绪打分','g','08-21'],
 ['D_DATA','财报下载器','financial_report_fetcher','社区实践','tushare 主源','stable','数据管理页','三大报表季度同步','y','06-28'],
 ['D_DATA','盘口快照存档器','snapshot_archiver','项目报告','','stable','—','五档快照 3 秒落盘','g','08-23'],
 ['D_DATA','宏观指标注册表','macro_indicator_registry','项目报告','CAND-091 登记','cand','宏观分析页 · 待接入','指标发布纪律登记','w','—'],
 ['D_GOVERNANCE','任务调度内核','task_scheduler','项目报告','tasks.yaml 167 任务','stable','任务进度页','156 启用任务节拍','g','08-23'],
 ['D_GOVERNANCE','适应度函数评估','fitness_function_eval','学术报告','演进式架构','stable','适应评估页','5 项度量门禁','g','08-20'],
 ['D_GOVERNANCE','门禁统计器','gate_stats','项目报告','','planned','治理分析页 · 待接入','通过/拦截率 OLAP','w','—'],
 ['D_GOVERNANCE','幻觉拦截器','hallucination_interceptor','项目报告','','stable','适应评估页','生成内容事实校验','g','08-19'],
 ['D_GOVERNANCE','审计日志器','audit_logger','项目报告','','stable','任务进度页','操作全留痕回放','g','08-23'],
 ['D_GOVERNANCE','缺口总账','gap_ledger','项目报告','CAND-005 登记','cand','—','已知缺口登记 + 闭环','w','—'],
 ['D_FRONTEND','仪表盘原型','dashboard_mockup','项目报告','v1.3','stable','本页','单文件全页原型','g','08-23'],
 ['D_FRONTEND','回测面板','app_panel.py','项目报告','Streamlit','stable','回测结果页','绩效看板','g','08-22'],
 ['D_FRONTEND','图表渲染器','chart_renderer','社区实践','轻量 canvas','stable','技术分析页','K线 + 指标多窗格','g','08-21'],
 ['D_FRONTEND','页面-模块映射表','page_module_mapping','项目报告','人工种子+生成器','testing','本页','前端显示列供数','g','08-23'],
 ['D_FRONTEND','主题令牌库','theme_tokens','项目报告','','stable','全局','色板/字号统一令牌','g','08-20'],
 ['D_FRONTEND','实时推送网关','realtime_push_gateway','GitHub','WebSocket · CAND-077','cand','—','行情秒级推前端','w','—'],
 ['D_FRONTEND','移动端适配层','mobile_adapter','社区实践','','planned','待接入','小屏断点重排','w','—'],
 ['D_ML_TRAIN','训练数据装配器','train_dataset_builder','项目报告','','stable','实验门控页','样本/标签/切分三件套','g','08-21'],
 ['D_ML_TRAIN','特征选择器','feature_selector','学术报告','LGBM 重要性','testing','因子档案页','因子池逐轮淘汰','g','08-18'],
 ['D_ML_TRAIN','元标签器','meta_labeler','学术报告','López de Prado','planned','实验门控页 · 待接入','次级信号过滤','w','—'],
 ['D_ML_TRAIN','模型登记处','model_registry','社区实践','MLflow 风格','stable','实验门控页','版本/指标/工件索引','g','08-20'],
 ['D_ML_TRAIN','在线学习管线','online_learning_pipe','GitHub','CAND-063 登记','cand','—','日频增量更新','w','—'],
 ['D_ML_TRAIN','超参优化器','hyperparam_optimizer','GitHub','Optuna','stable','实验门控页','贝叶斯搜索预算控制','y','07-09'],
 ['D_TRADING','订单路由器','order_router','项目报告','','stable','交易执行页','QMT/模拟双通道分发','g','08-23'],
 ['D_TRADING','委托频率哨兵','order_rate_sentinel','项目报告','','stable','系统状态页','异常委托频率熔断前置','g','08-23'],
 ['D_TRADING','智能拆单器','smart_order_splitter','学术报告','TWAP / VWAP','testing','交易执行页','大单切片执行','g','08-22'],
 ['D_TRADING','竞价量分析器','auction_volume_analyzer','项目报告','D2 确认口径','stable','作战指挥页','竞价量比监测','g','08-23'],
 ['D_TRADING','回执对账器','execution_reconciler','项目报告','','stable','盘后复盘页','委托-成交-持仓三对照','g','08-23'],
 ['D_TRADING','算法交易引擎','algo_trading_engine','GitHub','CAND-084 登记','cand','—','策略化执行算法库','w','—'],
 ['D_ORCHESTRATOR','全景图生成器','depgraph_generator','项目报告','6,869 节点','stable','本页','依赖全景 + build_status','g','08-23'],
 ['D_ORCHESTRATOR','日报编排器','daily_report_orchestrator','项目报告','','stable','全景总览页','盘后报告串行编排','g','08-22'],
 ['D_ORCHESTRATOR','夜班工作流','night_shift_workflow','项目报告','','stable','任务进度页','缺陷修复批次执行','g','08-23'],
 ['D_ORCHESTRATOR','数据质量看门','data_quality_watchdog','社区实践','','testing','系统状态页','时间戳/空表异常扫描','g','08-23'],
 ['D_ORCHESTRATOR','跨层血缘解析器','lineage_resolver','学术报告','CAND-029 登记','cand','—','L1-L10 表级血缘','w','—'],
 ['D_ORCHESTRATOR','发布列车','release_train','项目报告','','planned','待接入','版本窗口 + 回滚预案','w','—']
];
var modDom='all',modSt='all',modQ='';
function modRenderTabs(){
  var h='<span class="tab'+(modDom==='all'?' on':'')+'" onclick="modSetDom(\'all\')">全部</span>';
  MOD_DOMS.forEach(function(dk){
    h+='<span class="tab'+(modDom===dk[0]?' on':'')+'" onclick="modSetDom(\''+dk[0]+'\')">'+dk[1]+'</span>';
  });
  document.getElementById('mod-domtabs').innerHTML=h;
}
function modRenderTable(){
  var q=modQ.toLowerCase(),shown=0;
  var h='<tr><th style="width:230px">模块</th><th style="width:150px">来源</th><th style="width:78px">状态</th><th style="width:150px">前端显示</th><th>功能说明</th><th style="width:96px">最近使用</th></tr>';
  MOD_DOMS.forEach(function(dk){
    if(modDom!=='all'&&modDom!==dk[0]) return;
    var rows=MOD_D.filter(function(r){
      if(r[0]!==dk[0]) return false;
      if(modSt!=='all'&&r[5]!==modSt) return false;
      if(q&&r[1].toLowerCase().indexOf(q)<0&&r[2].toLowerCase().indexOf(q)<0) return false;
      return true;
    });
    if(!rows.length) return;
    var nB=rows.filter(function(r){return r[5]==='stable'||r[5]==='testing';}).length;
    var nP=rows.filter(function(r){return r[5]==='planned';}).length;
    var nC=rows.filter(function(r){return r[5]==='cand';}).length;
    h+='<tr class="mod-dom"><td colspan="6">'+dk[0]+' '+dk[1]
      +' <span class="dim" style="font-weight:400">· '+rows.length+' 模块（已建 '+nB+' · 设计 '+nP+' · 候选 '+nC+'）</span></td></tr>';
    rows.forEach(function(r){
      shown++;
      var lamp=r[8]==='g'?'<span class="dot ok"></span>'+r[9]
        :(r[8]==='y'?'<span class="dot y"></span>'+r[9]:'<span class="dot w"></span>—');
      h+='<tr><td>'+r[1]+'<div class="mod-en">'+r[2]+'</div></td>'
        +'<td><span class="badge '+MOD_SRC[r[3]]+'">'+r[3]+'</span>'+(r[4]?'<div class="mod-en">'+r[4]+'</div>':'')+'</td>'
        +'<td><span class="badge '+MOD_ST[r[5]][1]+'">'+MOD_ST[r[5]][0]+'</span></td>'
        +'<td>'+(r[6]==='—'?'<span class="na">—</span>':r[6])+'</td>'
        +'<td class="dim">'+r[7]+'</td>'
        +'<td>'+lamp+'</td></tr>';
    });
  });
  if(!shown) h+='<tr><td colspan="6" class="na">无匹配模块——请调整域筛选 / 状态筛选或搜索词</td></tr>';
  document.getElementById('mod-table').innerHTML=h;
  document.getElementById('mod-count').textContent='显示 '+shown+' / 演示 '+MOD_D.length+' 行（全量 6,912 行 I-2 转真）';
}
function modSetDom(k){modDom=k;modRenderTabs();modRenderTable();}
function modSetSt(v){modSt=v;modRenderTable();}
function modSetQ(v){modQ=v;modRenderTable();}
window.modInit=function(){ modRenderTabs(); modRenderTable(); };
