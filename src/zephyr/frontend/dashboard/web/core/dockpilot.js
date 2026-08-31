/* ══════════════════════════════════════════════════════════════
   core/dockpilot.js — 全站停靠布局引擎（Dockview v8.2 vendor UMD · Owner 2026-08-30 三裁定型→四裁推广）
   手感：四向插入分裂 / sash 拖拽调宽高联动挤压 / 悬浮弹出 / 布局保存+锁定（localStorage）
   架构：
     DockEng.docks = { rootId → { api, registry, storageKey, lockKey } }   每页一个 dock 实例
     DV_REGISTRY   = 全局组件注册表（id → {name, cat, pages:[可用页], make}）——注册中心雏形
     抽屉全局唯一（index.html body 级 #dv-lib），添加时进「当前可见页」的 dock
   渲染器两种：pane(html)=字符串件（试点演示件）；paneDom(el)=DOM 搬移件（真实页面模块，保留 JS 渲染产物与事件）
   ══════════════════════════════════════════════════════════════ */
(function(){
  'use strict';

  /* ---------- 渲染器工厂 ---------- */
  function pane(html){
    return function(){
      var el=document.createElement('div');
      el.className='dv-pane';
      el.innerHTML=html;
      return { element:el, init:function(){} };
    };
  }
  function paneDom(modEl){
    return function(){
      var wrap=document.createElement('div');
      wrap.className='dv-pane';
      /* padding 由 CSS .dv-pane 控制（right:44px 防图标栏遮挡），勿内联覆盖 */
      if(modEl){
        /* 清旧布局引擎（modLayout 半成品）残留：chrome 按钮/隐藏态/栅格档——DOM 搬移前净化 */
        modEl.classList.remove('mod-hide');
        modEl.style.removeProperty('--span');
        modEl.querySelectorAll('.mod-chrome,.mod-size').forEach(function(x){ x.remove(); });
        modEl.style.margin='0';
        wrap.appendChild(modEl);   /* DOM 搬移：ID 全文档唯一故引用不断；svg/已渲染内容随迁无损 */
      }
      return { element:wrap, init:function(){} };
    };
  }

  /* ---------- 全局组件注册表 ---------- */
  var DV_REGISTRY={
    /* —— 试点演示件（组件库页 · 字符串件） —— */
    vd:{ name:'结论卡 · 大盘状态', cat:'容器', pages:['modlib'], make:pane(
      '<div class="vd" style="height:100%;margin:0">'+
        '<div class="vd-top"><span class="vd-tag">今天大盘状态</span><span style="color:var(--faint);font-size:10.5px">大盘分析</span><span style="margin-left:auto;display:inline-flex;gap:6px;align-items:center"><span class="i" style="width:13px;height:13px;border:1px solid var(--faint);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:9px;cursor:help" title="依据：市场宽度 3,842/1,276 + 涨停 58 家 + 成交 9,860 亿 + 四指数综合——13 因子明细见「大盘分析·因子构成面板」">i</span></span></div>'+
        '<div class="vd-main">晴偏多云：上涨 3,842 / 下跌 1,276。<br>涨停 58 家 · 成交 9,860 亿。</div>'+
      '</div>')},
    subidx:{ name:'合并模块 · 副指数', cat:'容器', pages:['modlib'], make:pane(
      '<div class="card" style="height:100%;margin:0">'+
        '<div class="lab">副指数 · 深证 / 创业板 / 科创</div>'+
        '<div class="mrow"><span class="mn">深证成指</span><span class="chip up">+0.84%</span><span class="mnum">12,693.4</span><span class="mnote">成交 11,313 亿</span><span class="mst">偏多</span></div>'+
        '<div class="mrow"><span class="mn">创业板指</span><span class="chip up">+1.22%</span><span class="mnum">2,681.15</span><span class="mnote">成长强于价值</span><span class="mst">多</span></div>'+
        '<div class="mrow"><span class="mn">科创综指</span><span class="chip down">-0.18%</span><span class="mnum">1,342.88</span><span class="mnote">高位分歧</span><span class="mst">震荡</span></div>'+
      '</div>')},
    kpi:{ name:'KPI 卡行 · 资金总览', cat:'容器', pages:['modlib'], make:pane(
      '<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;height:100%">'+
        '<div class="card metric" style="margin:0"><div class="l">总资产</div><div class="v">173.85 万</div><div class="s">3 账户汇总</div></div>'+
        '<div class="card metric" style="margin:0"><div class="l">当日盈亏</div><div class="v up-t">+5,100</div><div class="s">+0.29%</div></div>'+
        '<div class="card metric" style="margin:0"><div class="l">持仓市值</div><div class="v">92.94 万</div><div class="s">76.8% 仓位</div></div>'+
        '<div class="card metric" style="margin:0"><div class="l">当前回撤</div><div class="v down-t">-3.2%</div><div class="s">预算 -15% · 消耗 21%</div></div>'+
      '</div>')},
    zt:{ name:'窄表 · 涨停强度', cat:'表格', pages:['modlib'], make:pane(
      '<div class="card" style="height:100%;margin:0"><div class="lab">涨停强度 · 今昨对比</div>'+
      '<table style="margin-top:6px"><tr><th></th><th>今日</th><th>昨日</th><th>判定</th></tr>'+
      '<tr><td>涨停板</td><td class="up-t">81</td><td>77</td><td><span class="chip up">↑ 回暖</span></td></tr>'+
      '<tr><td>涨停封板率</td><td>81%</td><td>81%</td><td><span class="chip flat">持平</span></td></tr>'+
      '<tr><td>跌停板</td><td class="down-t">2</td><td>4</td><td><span class="chip down">↓ 修复</span></td></tr></table></div>')}
  };

  /* ---------- 引擎 ---------- */
  var docks={};   /* rootId → { api, registry:[ids], storageKey, lockKey, locked, pageId } */

  function toast(t){ if(typeof gToast==='function') gToast(t); }

  function createDock(rootId, pageId, registryIds, storageKey, buildDefault){
    var root=document.getElementById(rootId);
    if(!root||typeof dockview==='undefined') return null;
    if(docks[rootId]) return docks[rootId];

    var locked=true, folded=false;   /* Owner 七裁：默认锁定（纯阅览态），每次打开保持 */
    try{ var savedLock=localStorage.getItem(storageKey+'-lock'); if(savedLock!==null) locked=savedLock==='1'; folded=localStorage.getItem(storageKey+'-fold')==='1'; }catch(e){}

    var api=dockview.createDockview(root,{
      createComponent:function(opts){
        var def=DV_REGISTRY[opts.name];
        return (def?def.make:pane('<div style="padding:14px;color:var(--faint)">未知组件 '+opts.name+'</div>'))();
      },
      theme:dockview.themeDark,
      locked:locked,
      disableAutoResizing:true   /* 禁用自动 resize，让 CSS 控制高度自适应 */
    });

    var d={ api:api, registry:registryIds, storageKey:storageKey, locked:locked, pageId:pageId, resetting:false, editMode:false, folded:folded };
    docks[rootId]=d;

    var saved=null;
    try{ saved=JSON.parse(localStorage.getItem(storageKey)||'null'); }catch(e){}
    /* 兼容处理：旧布局含 pos 面板（已拆分为 pos-a/pos-c），清除重建 */
    if(saved && saved.grid && JSON.stringify(saved).includes('"pos"')){
      try{ localStorage.removeItem(storageKey); saved=null; }catch(e){}
    }
    if(saved){ try{ api.fromJSON(saved); }catch(e){ buildDefault(api); } }
    else buildDefault(api);

    /* 自适应高度（Owner 七裁：内容撑开页面，可无限滚动） */
    function autoHeight(){
      var rootEl=document.getElementById(rootId);
      if(!rootEl) return;
      var shell=rootEl.querySelector('.dv-shell');
      if(!shell) return;
      /* 计算所有面板内容最大高度总和 */
      var totalH=0;
      var panels=rootEl.querySelectorAll('.dv-pane');
      panels.forEach(function(p){
        var h=p.scrollHeight;
        if(h>totalH) totalH=h;   /* 取最高面板作为行高基准 */
      });
      /* 加上行间距和 padding，确保内容完整显示 */
      var rows=rootEl.querySelectorAll('.dv-groupview').length;
      var containerH=Math.max(totalH * Math.ceil(rows/2), 640);   /* 粗略估算：两列布局取一半行数 */
      rootEl.style.height=containerH+'px';
      shell.style.height=containerH+'px';
      /* 通知 dockview 重新布局 */
      if(api.layout) try{ api.layout(rootEl.clientWidth, containerH); }catch(e){}
    }
    setTimeout(autoHeight,100);   /* 初始化后自适应 */
    api.onDidLayoutChange(function(){
      if(d.resetting) return;   /* 还原布局流程中禁回写（Owner 六裁：还原必须精确回出厂，防卸载前事件把当前布局又存回去） */
      try{ localStorage.setItem(storageKey, JSON.stringify(api.toJSON())); }catch(e){}
      setTimeout(autoHeight,50);   /* 布局变化后重新计算高度 */
    });

    /* 外部拖入两步协议（官方文档）：onUnhandledDragOver accept → 四向箭头渲染；onDidDrop → 按方位插入 */
    if(typeof api.onUnhandledDragOver==='function'){
      api.onUnhandledDragOver(function(e){ try{ e.accept(); }catch(err){} });
    }
    if(typeof api.onDidDrop==='function'){
      api.onDidDrop(function(e){
        var name=null;
        try{ name=e.nativeEvent.dataTransfer.getData('text/plain'); }catch(err){}
        if(!name||!DV_REGISTRY[name]) return;
        if(d.registry.indexOf(name)<0){ toast('「'+DV_REGISTRY[name].name+'」未在本页注册'); return; }
        var dir=(typeof e.position==='string'?e.position:null)||'right';
        if(dir==='center') dir='within';
        if(dir==='top') dir='above';
        if(dir==='bottom') dir='below';
        api.addPanel({ id:name+'_'+Date.now(), component:name, title:DV_REGISTRY[name].name, position:{ direction:dir, referenceGroup:e.group||undefined } });
        toast('已添加「'+DV_REGISTRY[name].name+'」到目标位置');
      });
    }
    syncLockBtns();
    paintClean(d);   /* 初始化即应用锁定干净模式（locked=true 恢复时隐藏标签栏/分界线） */
    paintFold(d);    /* 图标栏折叠态恢复 */
    return d;
  }

  /* 锁定干净模式（Owner 六裁）：锁定=纯阅览——隐藏标签栏/✕/拖拽柄/分界线，只呈现模块内容；解锁/编辑恢复 */
  function paintClean(d){
    var root=rootElOf(d);
    var wrap=root&&root.closest('.dv-wrap');
    if(wrap) wrap.classList.toggle('dv-clean', !!d.locked && !d.editMode);
  }
  function rootElOf(d){
    for(var k in docks){ if(docks[k]===d) return document.getElementById(k); }
    return null;
  }
  /* 图标栏折叠（Owner 六裁）：folded 态只留折叠小三角，LS 持久化 */
  function paintFold(d){
    var root=rootElOf(d);
    var bar=root&&root.closest('.dv-wrap')&&root.closest('.dv-wrap').querySelector('.dv-dockbar');
    if(bar) bar.classList.toggle('folded', !!d.folded);
  }

  function activeDock(){
    /* 当前可见页的 dock（抽屉添加组件的目标） */
    for(var k in docks){
      var pg=docks[k].pageId;
      var el=document.getElementById('p-'+pg);
      if(el&&el.classList.contains('active')) return docks[k];
    }
    return null;
  }

  function syncLockBtns(){
    document.querySelectorAll('.dv-ic[data-act="lock"]').forEach(function(b){
      var d=docks[b.getAttribute('data-dock')];
      if(!d) return;
      /* 锁定/编辑合并按钮：锁定=锁图标，编辑=铅笔图标 */
      var svg=b.querySelector('svg');
      if(!svg) return;
      if(d.editMode){
        b.classList.add('on');
        b.setAttribute('data-tip','完成并锁定');
        svg.innerHTML='<path d="M12 20h8.5"/><path d="M16.8 3.7a2 2 0 0 1 2.8 2.8L7.5 18.6 3.5 19.7l1.1-4L16.8 3.7z"/>';
      }else{
        b.classList.toggle('on', !!d.locked);
        b.setAttribute('data-tip', d.locked?'编辑布局':'锁定排列');
        if(d.locked){
          svg.innerHTML='<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>';
        }else{
          svg.innerHTML='<path d="M12 20h8.5"/><path d="M16.8 3.7a2 2 0 0 1 2.8 2.8L7.5 18.6 3.5 19.7l1.1-4L16.8 3.7z"/>';
        }
      }
    });
  }

  /* ---------- 全局动作（工具条/抽屉调用，dock 归属=按钮 data-dock 或当前活跃页） ---------- */
  function dockOf(el){
    var id=el&&el.getAttribute&&el.getAttribute('data-dock');
    return (id&&docks[id])||activeDock();
  }
  window.dvAdd=function(name, dockId){
    var d=(dockId&&docks[dockId])||activeDock();
    if(!d){ toast('当前页无停靠区'); return; }
    var def=DV_REGISTRY[name]; if(!def) return;
    if(d.registry.indexOf(name)<0){ toast('「'+def.name+'」未在本页注册'); return; }
    d.api.addPanel({ id:name+'_'+Date.now(), component:name, title:def.name, position:{ direction:'right' } });
    toast('已添加「'+def.name+'」——拖标题栏到任意模块的上/下/左/右即可分裂插入');
  };
  /* ---------- 布局管理（多布局保存/读取/删除） ---------- */
  function getLayouts(d){
    try{ return JSON.parse(localStorage.getItem(d.storageKey+'-layouts')||'[]'); }catch(e){ return []; }
  }
  function setLayouts(d, layouts){
    try{ localStorage.setItem(d.storageKey+'-layouts', JSON.stringify(layouts)); }catch(e){}
  }
  function saveLayoutAs(d, name){
    var layouts=getLayouts(d);
    var existing=layouts.findIndex(function(l){ return l.name===name; });
    var item={ name:name, time:new Date().toLocaleString('zh-CN'), data:d.api.toJSON() };
    if(existing>=0) layouts[existing]=item;
    else layouts.push(item);
    setLayouts(d, layouts);
    return true;
  }
  function loadLayout(d, name){
    var layouts=getLayouts(d);
    var item=layouts.find(function(l){ return l.name===name; });
    if(!item) return false;
    try{ d.api.fromJSON(item.data); return true; }catch(e){ return false; }
  }
  function deleteLayout(d, name){
    var layouts=getLayouts(d);
    var idx=layouts.findIndex(function(l){ return l.name===name; });
    if(idx<0) return false;
    layouts.splice(idx,1);
    setLayouts(d, layouts);
    return true;
  }
  /* 自定义命名输入框（prompt 在部分环境被阻止，改用内联输入） */
  function showSaveInput(d, onOk){
    var old=document.getElementById('dv-save-input');
    if(old) old.remove();
    var box=document.createElement('div');
    box.id='dv-save-input';
    box.className='dv-save-input';
    box.innerHTML='<div class="dv-si-title">保存布局名称</div>'+
      '<input type="text" id="dv-si-name" placeholder="输入布局名称…" value="布局 '+new Date().toLocaleString('zh-CN', {month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'})+'">'+
      '<div class="dv-si-btns"><button onclick="document.getElementById(\'dv-save-input\').remove()">取消</button><button class="primary" id="dv-si-ok">保存</button></div>';
    document.body.appendChild(box);
    var input=box.querySelector('#dv-si-name');
    input.focus(); input.select();
    box.querySelector('#dv-si-ok').onclick=function(){
      var name=input.value.trim();
      if(!name){ toast('名称不能为空'); return; }
      box.remove();
      onOk(name);
    };
    input.onkeydown=function(e){
      if(e.key==='Enter') box.querySelector('#dv-si-ok').click();
      if(e.key==='Escape') box.remove();
    };
  }
  window.dvSaveAs=function(btn){
    var d=dockOf(btn); if(!d) return;
    showSaveInput(d, function(name){
      if(saveLayoutAs(d, name)){
        toast('布局「'+name+'」已保存');
        renderLayoutPanel(d);
      }
    });
  };
  window.dvLoadLayout=function(btn){
    var d=dockOf(btn); if(!d) return;
    toggleLayoutPanel(d);
  };
  function toggleLayoutPanel(d){
    var panel=document.getElementById('dv-layout-panel');
    if(!panel){ createLayoutPanel(d); return; }
    panel.classList.toggle('open');
    if(panel.classList.contains('open')) renderLayoutPanel(d);
  }
  function createLayoutPanel(d){
    var panel=document.createElement('div');
    panel.id='dv-layout-panel';
    panel.className='dv-layout-panel';
    panel.innerHTML='<div class="dv-lp-head"><span>布局管理</span><span class="dv-lp-close" onclick="document.getElementById(\'dv-layout-panel\').classList.remove(\'open\')">×</span></div><div class="dv-lp-list" id="dv-lp-list"></div>';
    document.body.appendChild(panel);
    setTimeout(function(){ panel.classList.add('open'); renderLayoutPanel(d); },10);
  }
  function renderLayoutPanel(d){
    var list=document.getElementById('dv-lp-list');
    if(!list) return;
    var layouts=getLayouts(d);
    if(!layouts.length){ list.innerHTML='<div class="dv-lp-empty">暂无保存的布局</div>'; return; }
    list.innerHTML=layouts.map(function(l){
      return '<div class="dv-lp-item" data-name="'+l.name.replace(/"/g,'&quot;')+'">'+
        '<div class="dv-lp-info"><div class="dv-lp-name">'+l.name+'</div><div class="dv-lp-time">'+l.time+'</div></div>'+
        '<button class="dv-lp-del" onclick="event.stopPropagation();dvDelLayout(this)" title="删除">×</button>'+
        '</div>';
    }).join('');
    list.querySelectorAll('.dv-lp-item').forEach(function(item){
      item.addEventListener('click',function(){
        var name=item.getAttribute('data-name');
        if(loadLayout(d, name)){
          toast('已切换到布局「'+name+'」');
          toggleLayoutPanel(d);
        }
      });
    });
  }
  window.dvDelLayout=function(btn){
    var item=btn.closest('.dv-lp-item');
    var name=item&&item.getAttribute('data-name');
    if(!name) return;
    var d=activeDock(); if(!d) return;
    if(confirm('确定删除布局「'+name+'」？')){
      deleteLayout(d, name);
      renderLayoutPanel(d);
      toast('布局「'+name+'」已删除');
    }
  };

  window.dvSave=function(btn){
    var d=dockOf(btn); if(!d) return;
    try{ localStorage.setItem(d.storageKey, JSON.stringify(d.api.toJSON())); toast('布局已保存到本机'); }catch(e){}
  };
  /* 锁定/编辑合并按钮（Owner 七裁）：点击切换编辑/锁定，图标自动变（锁定=锁图标，编辑=铅笔图标） */
  window.dvToggleEditLock=function(btn){
    var d=dockOf(btn); if(!d) return;
    if(d.editMode){
      /* 编辑→锁定：退出编辑，自动锁定+保存 */
      d.editMode=false;
      d.locked=true;
      try{ d.api.updateOptions({ locked:true }); }catch(e){}
      try{ localStorage.setItem(d.storageKey+'-lock','1'); localStorage.setItem(d.storageKey, JSON.stringify(d.api.toJSON())); }catch(e){}
      toast('已完成——布局锁定并保存，每次打开保持');
    }else if(d.locked){
      /* 锁定→编辑：解锁进入编辑 */
      d.locked=false;
      d.editMode=true;
      try{ d.api.updateOptions({ locked:false }); }catch(e){}
      try{ localStorage.setItem(d.storageKey+'-lock','0'); }catch(e){}
      toast('编辑布局中——拖标题栏换位 · 拖分隔缝调大小 · 组件库添加；再点一次完成并锁定');
    }else{
      /* 未锁定未编辑（异常态）→ 直接进入编辑 */
      d.editMode=true;
      try{ d.api.updateOptions({ locked:false }); }catch(e){}
      toast('编辑布局中——拖标题栏换位 · 拖分隔缝调大小');
    }
    paintEdit(d); paintClean(d); syncLockBtns();
  };
  /* 保留旧函数作兼容（内部转发到新合并函数） */
  window.dvLock=function(btn){ window.dvToggleEditLock(btn); };
  window.dvEdit=function(btn){ window.dvToggleEditLock(btn); };
  function paintEdit(d){
    /* 编辑态视觉反馈：dock 容器挂 dv-editing 类 → 面板虚线描边 */
    var rootId=null;
    for(var k in docks){ if(docks[k]===d) rootId=k; }
    var root=rootId&&document.getElementById(rootId);
    var wrap=root&&root.closest('.dv-wrap');
    if(wrap) wrap.classList.toggle('dv-editing', !!d.editMode);
  }
  window.dvReset=function(btn){
    var d=dockOf(btn); if(!d) return;
    d.resetting=true;   /* 禁回写：reload 前任何 layout 事件不再把当前布局存回去（还原=精确回出厂） */
    try{ localStorage.removeItem(d.storageKey); }catch(e){}
    location.reload();
  };
  /* 图标栏折叠（Owner 六裁）：folded 态只留折叠小三角，LS 持久化 */
  window.dvBarFold=function(btn){
    var bar=btn&&btn.closest('.dv-dockbar');
    if(!bar) return;
    var wrap=bar.closest('.dv-wrap');
    var rootEl=wrap&&wrap.querySelector('[id]');
    var d=null;
    for(var k in docks){ if(document.getElementById(k)===rootEl|| (wrap&&wrap.contains(document.getElementById(k)))){ d=docks[k]; break; } }
    /* 兜底：按当前活跃 dock */
    if(!d) d=activeDock();
    var folded=!bar.classList.contains('folded');
    bar.classList.toggle('folded', folded);
    if(d){ d.folded=folded; try{ localStorage.setItem(d.storageKey+'-fold', folded?'1':'0'); }catch(e){} }
  };
  window.dvFloat=function(btn){
    var d=dockOf(btn); if(!d) return;
    var p=d.api.activePanel;
    if(!p){ toast('先点选一个面板再弹出'); return; }
    try{ d.api.addFloatingGroup(p, { position:{ left:120, top:80 } }); toast('已弹出为悬浮窗——拖标题栏移动，拖回主区可再停靠'); }
    catch(e){ toast('弹出失败：'+e.message); }
  };

  /* ---------- 组件库抽屉（全局唯一 · 内容随当前页 dock 过滤） ---------- */
  var libCat='全部';
  function libCats(d){
    var set={ '全部':1 };
    (d?d.registry:[]).forEach(function(k){ set[DV_REGISTRY[k].cat||'其他']=1; });
    return Object.keys(set);
  }
  function libRender(){
    var tabs=document.getElementById('dv-lib-tabs'), grid=document.getElementById('dv-lib-grid');
    if(!tabs||!grid) return;
    var d=activeDock();
    var ids=d?d.registry:[];
    tabs.innerHTML=libCats(d).map(function(c){
      return '<span class="tab'+(c===libCat?' on':'')+'" style="padding:3px 10px;font-size:11px;cursor:pointer" onclick="dvLibCat(\''+c+'\')">'+c+'</span>';
    }).join('');
    grid.innerHTML=ids.filter(function(k){
      return libCat==='全部'||(DV_REGISTRY[k].cat||'其他')===libCat;
    }).map(function(k){
      var dd=DV_REGISTRY[k];
      return '<div class="dv-lib-card" draggable="true" data-dv-comp="'+k+'" title="点击添加到停靠区右侧；或按住拖入停靠区任意模块四向分裂">'+
        '<div class="dv-lib-card-t">'+dd.name+'</div>'+
        '<div class="dv-lib-card-c">'+(dd.cat||'其他')+'</div></div>';
    }).join('') || '<div style="grid-column:1/-1;color:var(--faint);font-size:12px;padding:20px 4px">当前页无可添加组件</div>';
    grid.querySelectorAll('.dv-lib-card').forEach(function(card){
      card.addEventListener('click',function(){ window.dvAdd(card.getAttribute('data-dv-comp')); });
      card.addEventListener('dragstart',function(ev){
        ev.dataTransfer.setData('text/plain', card.getAttribute('data-dv-comp'));
        ev.dataTransfer.effectAllowed='move';
      });
    });
  }
  window.dvLibCat=function(c){ libCat=c; libRender(); };
  window.dvLibToggle=function(open){
    var mask=document.getElementById('dv-lib-mask'), lib=document.getElementById('dv-lib');
    if(!mask||!lib) return;
    var on = (typeof open==='boolean') ? open : !lib.classList.contains('open');
    mask.classList.toggle('open',on); lib.classList.toggle('open',on);
    if(on) libRender();
  };

  /* ══════════ 实例①：组件库页试点区（字符串件 4 件） ══════════ */
  function pilotDefault(api){
    try{ api.clear(); }catch(e){}
    /* addPanel 序列（below 无参考=通栏行末；right=行内并排） */
    api.addPanel({ id:'vd', component:'vd', title:DV_REGISTRY.vd.name });
    api.addPanel({ id:'subidx', component:'subidx', title:DV_REGISTRY.subidx.name, position:{ referencePanel:'vd', direction:'right' } });
    api.addPanel({ id:'kpi', component:'kpi', title:DV_REGISTRY.kpi.name, position:{ direction:'below' } });
    api.addPanel({ id:'zt', component:'zt', title:DV_REGISTRY.zt.name, position:{ referencePanel:'kpi', direction:'right' } });
  }
  function pilotInit(){
    var d=createDock('dv-pilot','modlib',['vd','subidx','kpi','zt'],'zk-dock-pilot',pilotDefault);
    if(d) window.__dvApi=d.api;
  }
  window.__DV_REGISTRY=DV_REGISTRY;   /* 调试钩子：注册表检视 */

  /* ══════════ 实例②：全景总览（DOM 搬移件 10 件——现有 data-mod 模块原样入坞，JS 渲染产物随迁） ══════════ */
  var OVX_DEFS=[
    ['decide-a','今日决策 · A股','决策'],['decide-c','今日决策 · 币圈','决策'],
    ['subidx','副指数 · 深证/创业板/科创','行情'],
    ['funds','资金总览','账户'],['pos-a','A股持仓','账户'],['pos-c','币圈持仓','账户'],
    ['wall','决策简报','决策'],['health','健康告警条','系统'],['vfy','算法实时校验','系统'],
    ['ai','AI 助手','工具'],['map','项目全景地图','工具'],['cal','今日日历','工具']
  ];
  function ovxRegister(){
    var grid=document.getElementById('ovx-grid');
    if(!grid) return false;
    OVX_DEFS.forEach(function(def){
      if(DV_REGISTRY[def[0]]) return;
      if(def[0]==='subidx'){
        /* 副指数=字符串件（无独立 DOM 源，直接注册到 overview） */
        DV_REGISTRY[def[0]]={ name:def[1], cat:def[2], pages:['overview'], make:pane(
          '<div class="card" style="height:100%;margin:0">'+
            '<div class="lab">副指数 · 深证 / 创业板 / 科创</div>'+
            '<div class="mrow"><span class="mn">深证成指</span><span class="chip up">+0.84%</span><span class="mnum">12,693.4</span><span class="mnote">成交 11,313 亿</span><span class="mst">偏多</span></div>'+
            '<div class="mrow"><span class="mn">创业板指</span><span class="chip up">+1.22%</span><span class="mnum">2,681.15</span><span class="mnote">成长强于价值</span><span class="mst">多</span></div>'+
            '<div class="mrow"><span class="mn">科创综指</span><span class="chip down">-0.18%</span><span class="mnum">1,342.88</span><span class="mnote">高位分歧</span><span class="mst">震荡</span></div>'+
          '</div>')};
        return;
      }
      var el=grid.querySelector('[data-mod="'+def[0]+'"]');
      if(!el) return;
      DV_REGISTRY[def[0]]={ name:def[1], cat:def[2], pages:['overview'], make:paneDom(el) };
    });
    return true;
  }
  function ovxDefault(api){
    try{ api.clear(); }catch(e){}
    /* 最美观布局（Owner 2026-08-30 六裁）：决策压顶 → 副指数+资金总览并排 → 持仓明细通栏 → 决策简报通栏 → 健康|校验并排 → AI|地图并排 → 日历收尾 */
    api.addPanel({ id:'decide-a', component:'decide-a', title:'今日决策 · A股' });
    api.addPanel({ id:'decide-c', component:'decide-c', title:'今日决策 · 币圈', position:{ referencePanel:'decide-a', direction:'right' } });
    api.addPanel({ id:'subidx', component:'subidx', title:'副指数', position:{ direction:'below' } });
    api.addPanel({ id:'funds', component:'funds', title:'资金总览', position:{ referencePanel:'subidx', direction:'right' } });
    api.addPanel({ id:'pos-a', component:'pos-a', title:'A股持仓', position:{ direction:'below' } });
    api.addPanel({ id:'pos-c', component:'pos-c', title:'币圈持仓', position:{ referencePanel:'pos-a', direction:'right' } });   /* A股|币圈 并排 */
    api.addPanel({ id:'wall', component:'wall', title:'决策简报', position:{ direction:'below' } });
    api.addPanel({ id:'health', component:'health', title:'健康告警条', position:{ direction:'below' } });
    api.addPanel({ id:'vfy', component:'vfy', title:'算法实时校验', position:{ referencePanel:'health', direction:'right' } });
    api.addPanel({ id:'ai', component:'ai', title:'AI 助手', position:{ direction:'below' } });
    api.addPanel({ id:'map', component:'map', title:'项目全景地图', position:{ referencePanel:'ai', direction:'right' } });
    api.addPanel({ id:'cal', component:'cal', title:'今日日历', position:{ direction:'below' } });
    /* 高度由内容自然撑开（Owner 七裁：页面可无限滚动，不固定高度） */
  }
  function ovxInit(){
    if(!ovxRegister()) return;
    var d=createDock('ovx-dock','overview',OVX_DEFS.map(function(x){return x[0];}),'zk-dock-overview-v2',ovxDefault);
    if(d){
      var grid=document.getElementById('ovx-grid');
      if(grid) grid.style.display='none';   /* 源区腾空隐藏：模块 DOM 已入坞 */
      window.__ovxDock=d.api;
    }
  }

  /* ---------- 页面激活钩子（隐藏页 clientWidth=0 防御：激活时初始化+layout 刷新） ---------- */
  document.addEventListener('page:show',function(e){
    var rootId = e.detail==='modlib' ? 'dv-pilot' : (e.detail==='overview' ? 'ovx-dock' : null);
    if(!rootId) return;
    if(e.detail==='modlib') pilotInit();
    if(e.detail==='overview') ovxInit();
    var d=docks[rootId], root=document.getElementById(rootId);
    if(d&&root&&d.api.layout){
      setTimeout(function(){ try{ d.api.layout(root.clientWidth, root.clientHeight); }catch(e){} },30);
    }
  });
})();
