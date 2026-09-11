/* 功能模块：公司公告面板（ann-panel）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 ANN_D
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4564-4599），逻辑零改动。
 * 验收单：ACC-F-NEWS-ANN-PANEL
 */
/* ==================== I-5 新闻舆情：公司公告（annXxx） ==================== */
var ANN_D=[
  {t:'14:32',ty:'定期报告',code:'300750',nm:'宁德时代',ti:'2026 年半年度报告'},
  {t:'14:10',ty:'重大事项',code:'688981',nm:'中芯国际',ti:'关于签订重大采购合同的公告'},
  {t:'13:48',ty:'分红',code:'600036',nm:'招商银行',ti:'2026 年中期利润分配实施公告'},
  {t:'11:05',ty:'回购',code:'600519',nm:'贵州茅台',ti:'关于回购公司股份进展公告'},
  {t:'10:52',ty:'定期报告',code:'000858',nm:'五粮液',ti:'2026 年半年度报告摘要'},
  {t:'09:58',ty:'减持',code:'002594',nm:'比亚迪',ti:'高管减持计划预披露'},
  {t:'09:31',ty:'重大事项',code:'601012',nm:'隆基绿能',ti:'关于投资建设新产能项目的公告'},
  {t:'08:47',ty:'回购',code:'000333',nm:'美的集团',ti:'回购股份注销完成公告'},
  {t:'08:15',ty:'减持',code:'603259',nm:'药明康德',ti:'股东减持股份结果公告'},
  {t:'07:55',ty:'分红',code:'601318',nm:'中国平安',ti:'2025 年年度权益分派实施公告'}
];
var ANN_BADGE={'定期报告':'b-na','重大事项':'b-warn','减持':'b-sell','回购':'b-buy','分红':'b-pass'};
var annCur='all';
function annRender(){
  var b=document.getElementById('ann-body'); if(!b) return;
  var h='<tr><th>时间</th><th>类型</th><th>代码</th><th>名称</th><th>标题</th><th>链接</th></tr>', n=0;
  ANN_D.forEach(function(a){
    if(annCur!=='all'&&a.ty!==annCur) return;
    n++;
    h+='<tr><td>'+a.t+'</td><td><span class="badge '+ANN_BADGE[a.ty]+'">'+a.ty+'</span></td>'
      +'<td>'+a.code+'</td><td>'+a.nm+'</td><td>'+a.ti+'</td>'
      +'<td><a class="ann-lnk" href="#" onclick="return false">原文</a></td></tr>';
  });
  if(!n) h+='<tr><td colspan="6" class="dim" style="text-align:center">该类型今日无公告</td></tr>';
  b.innerHTML=h;
  var c=document.getElementById('ann-count'); if(c) c.textContent='共 '+n+' 条';
}
function annSet(ty,el){
  var tabs=document.querySelectorAll('#ann-tabs .tab');
  for(var i=0;i<tabs.length;i++) tabs[i].classList.remove('on');
  if(el) el.classList.add('on');
  annCur=ty; annRender();
}
window.annInit=function(){ annRender(); };
