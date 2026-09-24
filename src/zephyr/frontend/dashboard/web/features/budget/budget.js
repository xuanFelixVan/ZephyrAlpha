/* 功能模块：预算分析建议卡页（budget-page，C7 / M5）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 自举：registerFeature 只登记不初始化（加载链竞态惯例）——样式注入+首渲染在文件顶层做，
 *       全局入口 budgetRefresh 供页面 onclick 直绑（先例 promotion-page 的 window.promoRefresh）
 * 数据源：GET /api/budget-advisories（建议清单真源=zephyr.intelligence.budget_analyzer 的
 *         只读投影函数（见该模块 render_budget_advisory_*）HTTP 投影，只读）
 * 渲染纪律：只渲染建议文案+直达链接文本（url_text 纯文本展示）——零提交控件，
 *           页内唯一可交互控件=刷新（仅重拉数据）；账户动作由 Owner 人工执行
 * 四档配色：notify=灰 b-na / warning=黄 b-warn / model_switch=黄 b-warn / halt=红 b-fail（全站 badge 六族惯例）
 * 防御：fetch 失败渲染错误卡，绝不抛未捕获异常（建议卡失败不拖垮仪表盘）
 */
(function(){
  function injectStyles(){
    if(document.getElementById('budget-page-style'))return;
    var st=document.createElement('style');st.id='budget-page-style';
    st.textContent=[
      '.budget-card{margin-bottom:14px}',
      '.budget-head{display:flex;gap:10px;align-items:center;flex-wrap:wrap}',
      '.budget-evi{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;font-size:11px;color:var(--dim)}',
      '.budget-evi b{color:var(--text)}',
      '.budget-alerts{margin-top:8px;display:flex;flex-direction:column;gap:6px}',
      '.budget-alert-item{padding:6px 10px;background:var(--input);border:1px solid var(--hair);border-left:3px solid var(--hair);border-radius:5px;font-size:11px}',
      '.budget-alert-halt{border-left-color:var(--fail,#e5484d)}',
      '.budget-alert-warn{border-left-color:#f5a623}',
      '.budget-link{margin-top:8px;padding:6px 10px;background:var(--input);border:1px solid var(--hair);border-radius:5px;font-size:11px;color:var(--dim);word-break:break-all}',
      '.budget-toolbar{display:flex;gap:8px;align-items:center;margin-bottom:10px;font-size:11px;color:var(--dim)}',
      '.budget-err{padding:10px 12px;border:1px solid var(--hair);border-left:3px solid var(--fail,#e5484d);border-radius:5px;font-size:12px;margin-bottom:10px}'
    ].join('');
    document.head.appendChild(st);
  }
  /* 四档告警 → 徽章+边色（唯一映射表，禁散落 if） */
  var TIER_BADGE={notify:['b-na','提示'],warning:['b-warn','警告'],model_switch:['b-warn','建议降档'],halt:['b-fail','熔断线']};
  var TIER_BORDER={notify:'budget-alert-item',warning:'budget-alert-item budget-alert-warn',model_switch:'budget-alert-item budget-alert-warn',halt:'budget-alert-item budget-alert-halt'};

  function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function num(v,d){return (v==null||isNaN(Number(v)))?'—':Number(v).toFixed(d==null?2:d);}

  function tierBadge(t){
    var m=TIER_BADGE[t]||['b-na',t||'未知'];
    return '<span class="badge '+m[0]+'">'+esc(m[1])+'</span>';
  }
  function alertItemHtml(a){
    return '<div class="'+esc(TIER_BORDER[a.tier]||'budget-alert-item')+'">'
      +tierBadge(a.tier)+' <b>'+esc(a.action_text||'')+'</b>'
      +'<span style="color:var(--dim)">（占比 '+num(a.ratio!=null?a.ratio*100:null,1)+'% / 阈值 '+num(a.threshold!=null?a.threshold*100:null,0)+'%）</span>'
      +'</div>';
  }
  function cardHtml(d){
    var top=d.topup_advice||{};
    var links=(d.links||[]).map(function(l){
      return '<div class="budget-link">'+esc(l.label||'直达链接')+'：<b>'+esc(l.url_text||'')+'</b>（纯文本，不内置任何控件）</div>';
    }).join('');
    return '<div class="card budget-card">'
      +'<div class="budget-head"><b>'+esc(d.date||'—')+'</b>'
      +'<span class="badge '+(Number(d.daily_usd)>Number(d.daily_limit_usd)?'b-fail':'b-pass')+'">日耗 '+num(d.daily_usd)+' / 限 '+num(d.daily_limit_usd)+' USD</span>'
      +(d.subscription_quota_used!=null?'<span class="badge b-na">Coding Plan 配额占用 '+num(d.subscription_quota_used*100,1)+'%（不折美元）</span>':'')
      +'</div>'
      +'<div class="budget-evi">'
      +'<span>30 天外推 <b>'+num(d.predicted_30d_usd)+' USD/天</b></span>'
      +'<span>7d 速率 <b>'+num(d.burn_7d_usd)+'</b></span>'
      +'<span>30d 速率 <b>'+num(d.burn_30d_usd)+'</b></span>'
      +'<span>免费窗节省 <b>'+num(d.free_savings_usd)+' USD</b></span>'
      +'<span>样本 <b>'+esc(d.sample_days==null?'—':d.sample_days)+'</b> 天</span>'
      +'</div>'
      +(d.predicted_note?'<div class="budget-link">'+esc(d.predicted_note)+'</div>':'')
      +((d.alerts&&d.alerts.length)?'<div class="budget-alerts">'+d.alerts.map(alertItemHtml).join('')+'</div>':'<div class="budget-evi" style="margin-top:8px"><span class="badge b-pass">四档告警：全部未触发</span></div>')
      +(top.action_text?'<div class="budget-evi" style="margin-top:8px"><span>建议动作 <b>'+esc(top.action_text)+'</b></span></div>':'')
      +links
      +'</div>';
  }
  function errCard(msg){
    return '<div class="budget-err"><b>预算建议卡拉取失败：</b>'+esc(msg)+'——数据源 /api/budget-advisories 暂不可达，可点"刷新"重试；本页为只读增强信息，失败不影响仪表盘其余页面。</div>';
  }
  function renderCards(data){
    var box=document.getElementById('budget-body');if(!box)return;
    var list=(data&&data.ok!==false&&data.date)?[data]:[];   /* 单日报告卡（日报告即一张卡） */
    box.innerHTML='<div class="budget-toolbar"><button class="btn" onclick="budgetRefresh()">刷新</button>'
      +'<span>数据只读 · 账户动作由 Owner 人工执行 · 更新于 '+esc((data&&data.generated_at)||'—')+'</span></div>'
      +(list.length?list.map(cardHtml).join(''):'暂无预算报告——budget_analyzer 尚未产出当日数据');
  }
  function load(){
    var box=document.getElementById('budget-body');if(!box)return;
    if(!window.ZK||!ZK.api)return;   /* 通道未就绪守卫（schedulegate.js 同款）：本轮跳过，60s 轮询兜底 */
    ZK.api.fetchJson('/api/budget-advisories', 10000).then(function(data){   /* 唯一通道纪律：经 ZK.api（绝对 BASE）——裸相对 fetch 在桌面壳 app:// 回退模式会打到 app://api/... 必断（tdm.js API_BASE 同坑） */
      if(data&&data.ok===false){renderCardsRaw(errCard(data.error||'未知错误'));return;}
      renderCards(data);
    }).catch(function(e){
      renderCardsRaw(errCard((e&&e.message)||String(e)));   /* 防御：失败渲染错误卡，不抛未捕获 */
    });
  }
  function renderCardsRaw(html){
    var box=document.getElementById('budget-body');if(!box)return;
    box.innerHTML='<div class="budget-toolbar"><button class="btn" onclick="budgetRefresh()">刷新</button><span>数据只读 · 账户动作由 Owner 人工执行</span></div>'+html;
  }

  /* 全局入口（刷新=唯一交互控件，仅重拉数据） */
  window.budgetRefresh=function(){load();};

  var mod={
    id:'budget-page',
    chart:null,
    init:function(chart,ctx){this.chart=chart;injectStyles();},
    render:function(d){load();},
    destroy:function(){
      if(BUDGET_TIMER){clearInterval(BUDGET_TIMER);BUDGET_TIMER=null;}
      var st=document.getElementById('budget-page-style');if(st)st.remove();
    }
  };
  var BUDGET_TIMER=null;
  if(window.ZK&&ZK.registerFeature){ZK.registerFeature(mod);}
  else{window.ZK=window.ZK||{};ZK._pendingFeatures=ZK._pendingFeatures||[];ZK._pendingFeatures.push(mod);}
  injectStyles();   /* 加载即注入（registerFeature 只登记不初始化惯例） */
  /* 自举：容器已注入即首拉+60s 轮询（只读页，无在途互斥需求） */
  if(document.getElementById('budget-body')){
    load();
    BUDGET_TIMER=setInterval(function(){
      if(document.getElementById('budget-body'))load();
    },60000);
  }
})();
