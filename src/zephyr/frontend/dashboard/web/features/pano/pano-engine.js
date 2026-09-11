/* 功能模块：架构全景页引擎（pano-engine）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据（层列卡）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L5515-5598），逻辑零改动。
 * 验收单：ACC-F-PANO-ENGINE
 */
/* ==================== I-6a 架构全景（panoXxx） ==================== */
var PANO_BASE='http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/';
var PANO_DOMAINS=[
 ['01_d_contracts','契约'],['02_d_infrastructure','基础设施'],['03_d_infra_a2a',''],['04_d_infra_ops',''],
 ['05_d_infra_recovery','容灾'],['06_d_infra_runtime',''],['07_d_infra_telemetry','遥测'],['08_d_shared','共享'],
 ['09_d_alt_data','另类数据'],['10_d_autonomy_core','自治核心'],['11_d_data','数据'],['12_d_data_eng','数据工程'],
 ['13_d_data_gov','数据治理'],['14_d_data_sec','数据安全'],['15_d_fbl_detectors','探测器'],['16_d_fbl_diagnosers','诊断器'],
 ['17_d_fbl_verification','验证'],['18_d_feedback_loop','反馈环'],['19_d_gov_code_quality','代码质量'],['20_d_gov_ops_resilience','运维韧性'],
 ['21_d_integration','集成'],['22_d_integration_gateway','网关'],['23_d_mkt_data','行情数据'],['24_d_ops','运维'],
 ['25_d_orchestrator','编排器'],['26_d_reporting','报告'],['27_d_security','安全'],['28_d_security_llm','LLM安全'],
 ['29_d_archive_scripts',''],['30_d_arch_guard','架构守卫'],['31_d_arch_scripts',''],['32_d_ashare_signal','A股信号'],
 ['33_d_audittest',''],['34_d_autonomy_perm','自治权限'],['35_d_backtest','回测'],['36_d_code_scripts',''],
 ['37_d_compliance','合规'],['38_d_compliance_scripts',''],['39_d_cross_asset','跨资产'],['40_d_data_scripts',''],
 ['41_d_digital_twin','数字孪生'],['42_d_exec_sim','执行仿真'],['43_d_ex_core','执行核心'],['44_d_ex_sor','智能路由'],
 ['45_d_factor','因子'],['46_d_frontend','前端'],['47_d_fundamental_signal','基本面信号'],['48_d_governance','治理'],
 ['49_d_gov_audit','审计'],['50_d_gov_docs','文档'],['51_d_gov_drift','漂移'],['52_d_gov_enforcement','执行'],
 ['53_d_gov_repair','修复'],['54_d_gov_rule','规则'],['55_d_gov_scripts',''],['56_d_intelligence','情报'],
 ['57_d_knowledge','知识'],['58_d_meta_scripts',''],['59_d_ml_serve','模型服务'],['60_d_ml_train','模型训练'],
 ['61_d_pf_alloc','组合配置'],['62_d_pf_core','组合核心'],['63_d_plan','计划'],['64_d_position','持仓'],
 ['65_d_regime','市场状态'],['66_d_risk','风险'],['67_d_sec_scripts',''],['68_d_sell_decision','卖出决策'],
 ['70_d_sigqc','信号质量'],['71_d_simulation','仿真'],['72_d_struct_scripts',''],['73_d_trading','交易']
];
var panoInited=false, panoCur='01_d_contracts', panoProbeTimer=null;
function panoUrl(k){ return PANO_BASE+(k||panoCur)+'.html'; }
function panoCn(k){
  for(var i=0;i<PANO_DOMAINS.length;i++) if(PANO_DOMAINS[i][0]===k) return PANO_DOMAINS[i][1];
  return '';
}
function panoRenderGrid(){
  var h='';
  for(var i=0;i<PANO_DOMAINS.length;i++){
    var d=PANO_DOMAINS[i];
    h+='<div class="pano-dom" data-k="'+d[0]+'" onclick="panoSelect(\''+d[0]+'\')">'
      +'<div class="pd-num">'+d[0].slice(0,2)+'</div>'
      +'<div class="pd-nm" title="'+d[0]+'">'+d[0].slice(3)+'</div>'
      +'<div class="pd-cn">'+(d[1]||'&nbsp;')+'</div>'
      +'</div>';
  }
  document.getElementById('pano-grid').innerHTML=h;
  document.getElementById('pano-count').textContent='共 '+PANO_DOMAINS.length+' 域';
}
function panoFilter(){
  var q=(document.getElementById('pano-srch').value||'').trim().toLowerCase(), shown=0;
  document.querySelectorAll('#pano-grid .pano-dom').forEach(function(el){
    var k=el.getAttribute('data-k'), cn=panoCn(k);
    var hit=!q || k.toLowerCase().indexOf(q)>=0 || (cn && cn.toLowerCase().indexOf(q)>=0);
    el.style.display=hit?'':'none';
    if(hit) shown++;
  });
  document.getElementById('pano-none').style.display=shown?'none':'';
  document.getElementById('pano-count').textContent='显示 '+shown+' / '+PANO_DOMAINS.length+' 域';
}
function panoSelect(k){
  panoCur=k;
  document.querySelectorAll('#pano-grid .pano-dom').forEach(function(el){
    el.classList.toggle('on', el.getAttribute('data-k')===k);
  });
  var url=panoUrl(k), cn=panoCn(k);
  document.getElementById('pano-url').value=url;
  document.getElementById('pano-cur-cn').textContent=k+(cn?' · '+cn:'');
  var fr=document.getElementById('pano-frame');
  fr.style.display=''; fr.src=url;
  document.getElementById('pano-off').style.display='none';
  panoProbe(url);
}
function panoProbe(url){
  if(panoProbeTimer) clearTimeout(panoProbeTimer);
  panoProbeTimer=setTimeout(function(){
    if(url!==panoUrl()) return;
    fetch(url,{method:'GET',mode:'no-cors',cache:'no-store'})   /* GET 替代 HEAD：消除 python http.server 下 Chrome ERR_ABORTED 噪音 */
      .then(function(){})
      .catch(function(){
        document.getElementById('pano-frame').style.display='none';
        document.getElementById('pano-off').style.display='';
      });
  },800);
}
function panoOpenNew(){ window.open(panoUrl(),'_blank'); }
window.panoInit=function(){
  if(panoInited){ panoProbe(panoUrl()); return; }
  panoInited=true;
  panoRenderGrid();
  panoSelect('01_d_contracts');
};
