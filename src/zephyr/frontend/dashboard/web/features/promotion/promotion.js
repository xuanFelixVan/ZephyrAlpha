/* 功能模块：策略转正审批页（promotion-page，C5 / S13）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 自举：registerFeature 只登记不初始化（加载链竞态惯例）——样式注入+首渲染在文件顶层做，
 *       全局入口 promoRefresh/promoDecide 供页面 onclick 直绑（先例 bt-battle-stage 的 window.btRenderStage）
 * 数据源：GET /api/promotion-advisories（建议清单真源=zephyr.strategy_pipeline.promotion_advisory.list_advisories 的 HTTP 投影）
 *         POST /api/promotion-decide（Owner 拍板 approve/reject；执行器=decide(token=None, via="frontend")）
 *         GET /api/ops-notifications（运营告警通知板横幅，治理战役 A2：OOM critical 等运营事件唯一前端出口，
 *                                     2026-09-15 裁定飞书/SMTP 裁撤后通知唯一出口=本页）
 * 拍板交互：两段式确认（先例 services/sv-page.js need_confirm→window.confirm→提交）；
 *           批准文案锚定整装语义「批准=进入整装组合，非单策略直进实盘」（S13 §5.5）
 * 三态配色：promote=绿 b-pass / hold=灰 b-na / demote=红 b-fail（全站 badge 六族惯例）
 * 授权：写端点=Owner 2026-09-15 通宵自主执行指令+宪法 §5 拍板门位数字化（api_server 第四获准写端点）
 */
(function(){
  function injectStyles(){
    if(document.getElementById('promo-page-style'))return;
    var st=document.createElement('style');st.id='promo-page-style';
    st.textContent=[
      '.promo-card{margin-bottom:14px}',
      '.promo-head{display:flex;gap:10px;align-items:center;flex-wrap:wrap}',
      '.promo-evi{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;font-size:11px;color:var(--dim)}',
      '.promo-evi b{color:var(--text)}',
      '.promo-act{display:flex;gap:8px;align-items:center;margin-top:10px;padding-top:8px;border-top:1px solid var(--hair);flex-wrap:wrap}',
      '.promo-receipt{margin-top:8px;padding:8px 10px;background:var(--input);border:1px solid var(--hair);border-radius:5px;font-size:11px}',
      /* 运营告警横幅（A2）：critical 红边醒目，已解除灰显折叠 */
      '.promo-alert-banner{margin-bottom:14px}',
      '.promo-alert-item{padding:10px 12px;border:1px solid var(--hair);border-left:3px solid var(--fail,#e5484d);border-radius:5px;background:var(--input);margin-bottom:8px;font-size:12px}',
      '.promo-alert-item.promo-alert-resolved{border-left-color:var(--hair);opacity:.55}',
      '.promo-alert-item b{font-size:12px}',
      '.promo-alert-meta{margin-top:4px;font-size:10px;color:var(--dim);word-break:break-all}'
    ].join('');
    document.head.appendChild(st);
  }
  /* 建议三态 → 徽章（唯一映射表，禁散落 if） */
  var REC_BADGE={promote:['b-pass','建议转正'],hold:['b-na','继续观察'],demote:['b-fail','建议降级']};
  var DEC_BADGE={approve:['b-pass','已批准'],reject:['b-fail','已驳回']};
  var LC_ZH={candidate:'候选',backtest:'回测',sim:'模拟盘',paper:'纸面',production:'生产',live:'实盘',monitoring:'监控',shelved:'搁置',decayed:'衰减',retired:'退役'};
  var EMPTY_TXT='暂无待审策略——模拟盘+整装回测出成绩后自动出现在这里';
  var LIST=null;          /* 最近一次 /api/promotion-advisories 快照 */
  var PROMO_TIMER=null;
  var PROMO_BUSY=false;   /* 拍板在途暂停轮询重绘（防 confirm 期间 DOM 被换） */

  function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function num(v,d){return (v==null||isNaN(Number(v)))?'—':Number(v).toFixed(d==null?2:d);}

  function recBadge(rec){
    var m=REC_BADGE[rec]||['b-na',rec||'未知'];
    return '<span class="badge '+m[0]+'">'+esc(m[1])+'</span>';
  }
  /* 整装回测四指标摘要（sharpe/最大回撤/总收益/面板对账，C5 蓝图 §5.3） */
  function eviFw(fw){
    if(!fw)return '<span>整装回测 <b>—</b>（无产物）</span>';
    return '<span>整装回测 sharpe <b>'+num(fw.sharpe)+'</b></span>'
      +'<span>最大回撤 <b class="down">'+num(fw.max_dd*100,1)+'%</b></span>'
      +'<span>总收益 <b class="'+(Number(fw.total_return)>=0?'up':'down')+'">'+num(fw.total_return*100,1)+'%</b></span>'
      +'<span>面板对账 <span class="badge '+(fw.panel_ok?'b-pass':'b-warn')+'">'+(fw.panel_ok?'通过':'未过')+'</span></span>'
      +(fw.run_id?'<span class="dim">run '+esc(fw.run_id)+'</span>':'');
  }
  function cardHtml(a,i){
    var dec=a.decision;
    var h='<div class="card promo-card" id="promo-card-'+i+'">'
      +'<div class="promo-head"><b>'+esc(a.strategy_id)+'</b>'
      +'<span class="badge b-na">'+esc(LC_ZH[a.lifecycle_now]||a.lifecycle_now||'未知')+'</span>'
      +recBadge(a.recommendation)
      +'<span class="dim" style="margin-left:auto;font-size:10px">生成 '+(a.generated_at?esc(String(a.generated_at)).slice(0,19).replace('T',' '):'—')+' · '+esc(a.advisory_id)+'</span></div>'
      +'<div class="promo-evi">'
      +'<span>模拟盘通过 <b class="up">'+esc(a.evidence&&a.evidence.sim_pass_months!=null?a.evidence.sim_pass_months:'—')+'</b> 月</span>'
      +'<span>破限 <b class="'+((a.evidence&&a.evidence.sim_breach_months)>0?'down':'')+'">'+esc(a.evidence&&a.evidence.sim_breach_months!=null?a.evidence.sim_breach_months:'—')+'</b> 月</span>'
      +eviFw(a.evidence&&a.evidence.fw_backtest)
      +'</div>';
    if(dec){
      var db=DEC_BADGE[dec.decision]||['b-na',dec.decision||'已决'];
      h+='<div class="promo-receipt"><span class="badge '+db[0]+'">'+esc(db[1])+'</span> '
        +(dec.new_lifecycle?'<span>新状态 <b>'+esc(LC_ZH[dec.new_lifecycle]||dec.new_lifecycle)+'</b> · </span>':'')
        +(dec.message?'<span class="dim">'+esc(dec.message)+'</span> · ':'')
        +(dec.decided_at?'<span class="dim">拍板于 '+esc(String(dec.decided_at)).slice(0,19).replace('T',' ')+'</span>':'')
        +(dec.receipt?'<div class="dim" style="margin-top:4px;word-break:break-all">回执 '+esc(typeof dec.receipt==='string'?dec.receipt:JSON.stringify(dec.receipt))+'</div>':'')
        +'</div>';
    }else{
      h+='<div class="promo-act">'
        +'<span class="btn" style="color:var(--text)" onclick="promoDecide('+i+',\'approve\')">✓ 批准（进整装）</span>'
        +'<span class="btn" style="color:var(--up)" onclick="promoDecide('+i+',\'reject\')">✗ 驳回（退回观察）</span>'
        +'<span class="dim" style="font-size:10px">批准=进入整装组合（TDM sleeve 权重已挂），非单策略直进实盘</span>'
        +'</div>';
    }
    return h+'</div>';
  }
  function render(){
    var box=document.getElementById('promo-body');if(!box)return;
    if(!LIST){box.innerHTML='<div class="dim" style="padding:20px 0">加载中…</div>';return;}
    if(!LIST.length){box.innerHTML='<div class="card" style="border-left:3px solid var(--hair);text-align:center;padding:26px 0;color:var(--dim)">'+EMPTY_TXT+'</div>';return;}
    box.innerHTML=LIST.map(cardHtml).join('');
  }
  function load(){
    if(!window.ZK||!ZK.api)return;
    ZK.api.fetchPromotionAdvisories().then(function(r){
      if(!r)throw new Error('空响应');
      LIST=(r&&r.data)||[];
      render();
      if(r&&r.ok===false){   /* 执行器缺位=空态+暗色原因（不吓人，演示诚实纪律） */
        var box=document.getElementById('promo-body');
        if(box)box.innerHTML+='<div class="dim" style="font-size:10px;margin-top:-6px">执行器未就绪：'+esc(r.error||'')+'</div>';
      }
    }).catch(function(e){
      var box=document.getElementById('promo-body');
      if(box&&!box.innerHTML.trim()){
        box.innerHTML='<div class="card" style="border-left:3px solid var(--up)"><b style="color:var(--up)">⚠ API 拉取失败（'+esc(e&&e.message||e)+'）</b><div class="dim" style="font-size:11px;margin-top:4px">面板 API（127.0.0.1:8890）未运行或超时——15 秒后自动重试</div></div>';
      }
      setTimeout(load,15000);   /* 15s 自动重试至真源（TRAE-086 §truth_source_wiring） */
    });
  }
  /* 拍板：两段式确认（sv-page need_confirm 先例）→ POST → 成功局部刷新该卡 */
  function decide(i,decision){
    if(!LIST||!LIST[i])return;
    var a=LIST[i];
    var isApp=decision==='approve';
    var msg=(isApp?'确认批准【'+a.strategy_id+'】转正？':'确认驳回【'+a.strategy_id+'】？')
      +'\n建议 ID：'+a.advisory_id
      +'\n当前状态：'+(LC_ZH[a.lifecycle_now]||a.lifecycle_now||a.lifecycle_now)+' · 建议：'+(REC_BADGE[a.recommendation]||[,'?'])[1]
      +(isApp?'\n\n批准=进入整装组合（TDM sleeve 权重已挂），非单策略直进实盘。':'\n\n驳回=退回模拟盘继续观察。')
      +'\n拍板将服务端留痕回执。';
    if(!window.confirm(msg))return;
    PROMO_BUSY=true;
    var btn=document.querySelector('#promo-card-'+i+' .promo-act');
    if(btn)btn.innerHTML='<span class="dim">拍板提交中…</span>';
    ZK.api.postPromotionDecide(a.advisory_id,decision).then(function(r){
      PROMO_BUSY=false;
      if(r&&r.ok){
        LIST[i].decision={decision:decision,message:r.message,new_lifecycle:r.new_lifecycle,receipt:r.receipt,decided_at:new Date().toISOString()};
        var el=document.getElementById('promo-card-'+i);   /* 局部刷新：仅替换该卡为已决回执态 */
        if(el){
          var tmp=document.createElement('div');
          tmp.innerHTML=cardHtml(LIST[i],i);
          if(tmp.firstChild){el.replaceWith(tmp.firstChild);}else{render();}
        }else{render();}
      }else{
        render();   /* 恢复按钮态 */
        alert('拍板被拒：'+(r&&r.message||r&&r.error||'?'));
      }
    }).catch(function(e){
      PROMO_BUSY=false;
      render();
      alert('拍板请求失败：'+(e&&e.message||e));
    });
  }
  /* 全局入口（页面 onclick 直绑） */
  window.promoRefresh=function(){LIST=null;render();load();};
  window.promoDecide=decide;

  /* ── 运营告警横幅（A2，2026-09-16）：/api/ops-notifications 轮询渲染 ──
   * 通知唯一出口=本页（2026-09-15 裁定）。critical=红边醒目；已解除 1h 内灰显。
   * 拉取失败静默（横幅是增强信息，不与建议卡抢错误位——promote 页自身错误语义不受影响）。 */
  function alertItemHtml(n){
    var resolved=!!n.resolved_at;
    var first=n.first_seen?esc(String(n.first_seen)).slice(0,19).replace('T',' '):'—';
    var cls='promo-alert-item'+(resolved?' promo-alert-resolved':'');
    return '<div class="'+cls+'" data-key="'+esc(n.key||'')+'">'
      +'<b>'+(resolved?'[已解除] ':'')+esc(n.title||n.key||'运营告警')+'</b> '
      +'<span class="badge '+(resolved?'b-na':'b-fail')+'">'+esc(String(n.severity||'').toUpperCase()||'?')+'</span>'
      +'<div>'+esc(n.message||'')+'</div>'
      +'<div class="promo-alert-meta">首次 '+first+' · 第 '+esc(n.count||1)+' 次 · 来源 '+esc(n.source||n.module_id||'')+(resolved?' · 已解除':'')+'</div>'
      +'</div>';
  }
  function renderAlerts(items){
    var box=document.getElementById('promo-alert-banner');if(!box)return;
    if(!items||!items.length){box.innerHTML='';box.style.display='none';return;}
    box.style.display='';
    box.innerHTML=items.map(alertItemHtml).join('');
  }
  function loadAlerts(){
    if(!(window.ZK&&ZK.api&&ZK.api.fetchOpsNotifications))return;
    ZK.api.fetchOpsNotifications().then(function(r){
      renderAlerts((r&&r.ok!==false&&r.data)||[]);
    }).catch(function(){renderAlerts([]);});   /* 静默：横幅失败不影响建议卡 */
  }
  window.promoRefreshAlerts=loadAlerts;   /* 全局入口（同 promoRefresh 惯例） */

  var mod={
    id:'promotion-page',
    chart:null,
    init:function(chart,ctx){this.chart=chart;injectStyles();},
    render:function(d){render();},
    destroy:function(){
      if(PROMO_TIMER){clearInterval(PROMO_TIMER);PROMO_TIMER=null;}
      var st=document.getElementById('promo-page-style');if(st)st.remove();
    }
  };
  if(window.ZK&&ZK.registerFeature){ZK.registerFeature(mod);}
  else{window.ZK=window.ZK||{};ZK._pendingFeatures=ZK._pendingFeatures||[];ZK._pendingFeatures.push(mod);}
  injectStyles();   /* 加载即注入（registerFeature 只登记不初始化惯例） */
  /* 自举：容器已注入即首拉+30s 轮询（拍板在途跳过，防 confirm 期间重绘）；
   * 运营告警横幅容器同场注入（A2：promo-body 之前），与建议卡同拍轮询 */
  if(document.getElementById('promo-body')){
    var banner=document.createElement('div');
    banner.id='promo-alert-banner';banner.className='promo-alert-banner';banner.style.display='none';
    document.getElementById('promo-body').parentNode.insertBefore(banner,document.getElementById('promo-body'));
    load();
    loadAlerts();
    PROMO_TIMER=setInterval(function(){
      if(!PROMO_BUSY&&document.getElementById('promo-body'))load();
      if(document.getElementById('promo-alert-banner'))loadAlerts();
    },30000);
  }
})();
