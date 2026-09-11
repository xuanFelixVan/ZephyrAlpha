/* 功能模块：政策资金面板（pol-panel）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 POL_D（政策≠新闻独立源）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4600-4628），逻辑零改动。
 * 验收单：ACC-F-POLICY-POL-PANEL
 */
/* ==================== I-8 政策资金（polXxx：政策流分源 tabs；政策≠新闻独立源） ==================== */
var POL_D=[
  {t:'08-24 14:00',src:'国务院',lv:'国家级',lc:'b-buy',title:'国常会：部署进一步扩大内需新一轮举措',impact:'<span class="badge b-buy">利好</span> 消费/基建链',link:1},
  {t:'08-24 09:20',src:'央行',lv:'部委级',lc:'b-na',title:'开展 3,800 亿 MLF 操作（利率持平）',impact:'<span class="badge b-na">中性偏多</span> 流动性维持·银行',link:1},
  {t:'08-23 17:30',src:'证监会',lv:'部委级',lc:'b-na',title:'程序化交易报告制度落地执行（量化监管常态化）',impact:'<span class="badge b-na">中性</span> 量化/券商',link:1},
  {t:'08-22 16:00',src:'证监会',lv:'部委级',lc:'b-buy',title:'上市公司分红指引修订公开征求意见',impact:'<span class="badge b-buy">利好</span> 红利/央企',link:1},
  {t:'08-22 02:00',src:'海外',lv:'海外·央行',lc:'b-sell',title:'美联储 FOMC 纪要：年内或仅降息一次（放鹰）',impact:'<span class="badge b-sell">利空</span> 预期差·北向/成长',link:1},
  {t:'08-21 10:00',src:'地方政府',lv:'省级',lc:'b-buy',title:'某省 2,000 亿专项债提前下达（基建加速）',impact:'<span class="badge b-buy">利好</span> 基建/区域',link:1},
  {t:'08-20 08:30',src:'地方政府',lv:'市级',lc:'b-na',title:'某市购房补贴加码（人才购房）',impact:'<span class="badge b-buy">弱利好</span> 地产链',link:1},
  {t:'08-15 21:30',src:'海外',lv:'海外·央行',lc:'b-na',title:'美联储维持联邦基金利率 4.25–4.50%（FRED DFF 序列在库口径）',impact:'<span class="badge b-na">中性</span> 符合预期·美债 10Y 4.28%',link:1}
];
var polCur='all';
function polRender(){
  var tb=document.getElementById('pol-body'); if(!tb)return;
  var rows=POL_D.filter(function(r){return polCur==='all'||r.src===polCur;});
  var h='<tr><th>时间</th><th>源</th><th>级别</th><th>标题</th><th>影响解读</th><th>原文链</th></tr>';
  rows.forEach(function(r){
    h+='<tr><td>'+r.t+'</td><td>'+r.src+'</td><td><span class="badge '+r.lc+'">'+r.lv+'</span></td><td>'+r.title+'</td><td>'+r.impact+'</td>'
      +'<td><span class="dim" style="cursor:not-allowed" title="原文链待接入（独立政策源接口 I-2）">🔗 原文</span></td></tr>';
  });
  tb.innerHTML=h;
  var c=document.getElementById('pol-count'); if(c)c.textContent=rows.length+' 条';
}
function polSet(src,el){
  document.querySelectorAll('#pol-tabs .tab').forEach(function(t){t.classList.remove('on');});
  if(el) el.classList.add('on');
  polCur=src; polRender();
}
window.polInit=function(){ polRender(); };
