/* 功能模块：条件选股引擎（scr-engine）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 SCR_STOCKS+方案 localStorage
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4056-4356），逻辑零改动。
 * 验收单：ACC-F-SCREENER-ENGINE
 */
/* ==================== I-5 条件选股（scrXxx 前缀） ==================== */
var SCR_FIELDS={
  pe:   {cat:'val',cn:'市盈率',en:'PE',ops:['<','>','介于']},
  pb:   {cat:'val',cn:'市净率',en:'PB',ops:['<','>','介于']},
  ps:   {cat:'val',cn:'市销率',en:'PS',ops:['<','>','介于']},
  div:  {cat:'val',cn:'股息率',en:'DIV',unit:'%',ops:['<','>','介于']},
  revg: {cat:'gro',cn:'营收增速',en:'RevG',unit:'%',ops:['<','>','介于']},
  npg:  {cat:'gro',cn:'净利增速',en:'NPG',unit:'%',ops:['<','>','介于']},
  roe:  {cat:'gro',cn:'净资产收益率',en:'ROE',unit:'%',ops:['<','>','介于']},
  ma20: {cat:'tec',cn:'收盘价 vs MA20',en:'MA20 Pos',ops:['上方','下方'],nov:1},
  ret20:{cat:'tec',cn:'20日涨跌幅',en:'RET20',unit:'%',ops:['<','>','介于']},
  turn: {cat:'tec',cn:'换手率',en:'TURN',unit:'%',ops:['<','>','介于']},
  mfin: {cat:'cap',cn:'主力净流入',en:'MFIN',unit:'万',ops:['<','>','介于']},
  north:{cat:'cap',cn:'北向持股变动',en:'NORTH',unit:'%',ops:['<','>','介于']},
  lg:   {cat:'emo',cn:'涨停基因',en:'LimitGene',unit:'次/60日',ops:['>','介于'],demo:1},
  cons: {cat:'emo',cn:'连板数',en:'ConsL',unit:'板',ops:['>','介于'],demo:1}
};
var SCR_UNI={all:['全A',5420],hs300:['沪深300',300],zz500:['中证500',500],zz1000:['中证1000',1000],watch:['自选股板块',36]};
var SCR_PRESETS=[
  {cn:'低估值高ROE',c:[{f:'pe',op:'<',v1:20,v2:null},{f:'roe',op:'>',v1:15,v2:null}]},
  {cn:'强势突破',c:[{f:'ma20',op:'上方',v1:null,v2:null},{f:'ret20',op:'>',v1:10,v2:null}]},
  {cn:'资金抢筹',c:[{f:'mfin',op:'>',v1:5000,v2:null},{f:'turn',op:'>',v1:3,v2:null}]}
];
var SCR_COLS=[
  {k:'code',cn:'代码',en:'Code',fixed:1},{k:'name',cn:'名称',en:'Name',fixed:1},
  {k:'price',cn:'现价',en:'Price',fixed:1},{k:'chg',cn:'涨跌幅',en:'Chg%',fixed:1},
  {k:'pe',cn:'市盈率',en:'PE',on:1},{k:'pb',cn:'市净率',en:'PB',on:0},
  {k:'div',cn:'股息率',en:'DIV',on:0},{k:'roe',cn:'净资产收益率',en:'ROE',on:1},
  {k:'revg',cn:'营收增速',en:'RevG',on:0},{k:'npg',cn:'净利增速',en:'NPG',on:0},
  {k:'ret20',cn:'20日涨幅',en:'RET20',on:0},{k:'turn',cn:'换手率',en:'TURN',on:0},
  {k:'mfin',cn:'主力净流入',en:'MFIN',on:1},{k:'north',cn:'北向变动',en:'NORTH',on:0},
  {k:'hit',cn:'命中条件数',en:'Hits',fixed:1},{k:'op',cn:'操作',en:'Op',fixed:1}
];
var SCR_STOCKS=[
  {code:'600519.SH',name:'贵州茅台',price:1688.00,chg:0.85,pe:28.5,pb:9.8,ps:15.2,div:1.8,revg:15.2,npg:16.5,roe:33.2,ma20:1,ret20:3.2,turn:0.28,mfin:12500,north:0.42},
  {code:'300750.SZ',name:'宁德时代',price:178.50,chg:2.35,pe:22.8,pb:4.6,ps:2.8,div:0.9,revg:28.5,npg:35.2,roe:21.5,ma20:1,ret20:12.6,turn:3.05,mfin:28600,north:0.85},
  {code:'688981.SH',name:'中芯国际',price:91.30,chg:3.85,pe:65.2,pb:3.2,ps:8.5,div:0,revg:22.0,npg:18.5,roe:8.5,ma20:1,ret20:15.8,turn:3.25,mfin:35200,north:0.15},
  {code:'002594.SZ',name:'比亚迪',price:245.60,chg:-1.25,pe:19.5,pb:3.8,ps:1.2,div:1.2,revg:18.5,npg:22.0,roe:18.2,ma20:-1,ret20:-5.2,turn:1.45,mfin:-8500,north:-0.32},
  {code:'000858.SZ',name:'五粮液',price:128.90,chg:0.52,pe:15.8,pb:3.5,ps:5.8,div:3.2,revg:8.5,npg:10.2,roe:22.5,ma20:-1,ret20:-2.1,turn:0.55,mfin:3200,north:0.08},
  {code:'603259.SH',name:'药明康德',price:68.50,chg:1.85,pe:18.2,pb:2.8,ps:3.2,div:1.5,revg:5.5,npg:8.8,roe:15.8,ma20:1,ret20:6.5,turn:1.25,mfin:5600,north:0.22},
  {code:'002415.SZ',name:'海康威视',price:32.80,chg:0.95,pe:21.5,pb:3.2,ps:2.5,div:2.2,revg:6.8,npg:9.5,roe:16.8,ma20:1,ret20:4.2,turn:0.85,mfin:6800,north:0.12},
  {code:'601012.SH',name:'隆基绿能',price:18.50,chg:-2.15,pe:12.5,pb:1.8,ps:0.9,div:1.8,revg:-15.2,npg:-45.5,roe:5.2,ma20:-1,ret20:-8.5,turn:1.85,mfin:-12500,north:-0.55},
  {code:'600036.SH',name:'招商银行',price:38.50,chg:0.35,pe:6.8,pb:0.95,ps:2.2,div:5.2,revg:2.5,npg:3.8,roe:15.5,ma20:-1,ret20:1.2,turn:0.35,mfin:4500,north:0.18},
  {code:'601318.SH',name:'中国平安',price:52.80,chg:0.65,pe:8.5,pb:0.88,ps:0.9,div:4.8,revg:3.2,npg:12.5,roe:12.8,ma20:1,ret20:5.5,turn:0.65,mfin:8900,north:0.28}
];
var scrConds=[],scrHits=[],scrInPool={},scrInited=false;
function scrEsc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function scrToast(m){
  var d=document.createElement('div');
  d.className='scr-toast'; d.textContent=m;
  document.body.appendChild(d);
  setTimeout(function(){d.style.opacity='0';d.style.transition='opacity .4s';setTimeout(function(){d.remove();},400);},2200);
}
function scrCatFields(){
  var cat=document.getElementById('scr-cat').value, h='';
  Object.keys(SCR_FIELDS).forEach(function(k){
    var f=SCR_FIELDS[k];
    if(f.cat===cat) h+='<option value="'+k+'">'+f.cn+' '+f.en+'</option>';
  });
  document.getElementById('scr-field').innerHTML=h;
}
function scrAddCond(){
  var k=document.getElementById('scr-field').value;
  if(!k) return;
  scrConds.push({f:k,op:SCR_FIELDS[k].ops[0],v1:null,v2:null});
  scrRenderConds();
}
function scrDelCond(i){ scrConds.splice(i,1); scrRenderConds(); }
function scrOpSwap(i,v){ scrConds[i].op=v; scrRenderConds(); }
function scrVal(i,n,v){ scrConds[i]['v'+n]=v; }
function scrInputs(c,i,f){
  var h='<input class="scr-inp" type="number" value="'+(c.v1==null?'':c.v1)+'" oninput="scrVal('+i+',1,this.value)">';
  if(c.op==='介于') h+='<span class="dim">~</span><input class="scr-inp" type="number" value="'+(c.v2==null?'':c.v2)+'" oninput="scrVal('+i+',2,this.value)">';
  if(f.unit) h+='<span class="dim" style="font-size:11px">'+f.unit+'</span>';
  return h;
}
function scrRenderConds(){
  var box=document.getElementById('scr-conds');
  if(!scrConds.length){
    box.innerHTML='<div class="note" style="margin:2px 0 8px">暂无条件——从上方「添加条件」或点预置方案；空条件执行=样本池全量命中</div>';
    return;
  }
  var h='';
  scrConds.forEach(function(c,i){
    var f=SCR_FIELDS[c.f];
    h+='<div class="scr-cond"><div class="r1"><span>'
      +(i>0?'<span class="dim" style="font-size:10px">AND </span>':'')
      +f.cn+' <span class="dim">'+f.en+'</span>'
      +(f.demo?' <span class="badge b-warn">演示</span>':'')
      +'</span><span class="scr-del" onclick="scrDelCond('+i+')" title="删除条件">×</span></div>'
      +'<div class="r2"><select class="sel scr-op" onchange="scrOpSwap('+i+',this.value)">'
      +f.ops.map(function(o){return '<option'+(o===c.op?' selected':'')+'>'+o+'</option>';}).join('')
      +'</select>'
      +(f.nov?'<span class="dim" style="font-size:11px">无需阈值</span>':scrInputs(c,i,f))
      +'</div></div>';
  });
  box.innerHTML=h;
}
function scrPass(s,c){
  var f=SCR_FIELDS[c.f];
  if(f.demo) return true;
  var v=s[c.f];
  if(f.nov) return c.op===f.ops[0]? v>0 : v<0;
  var a=parseFloat(c.v1), b=parseFloat(c.v2);
  if(c.op==='<') return isNaN(a)||v<a;
  if(c.op==='>') return isNaN(a)||v>a;
  if(c.op==='介于'){
    if(isNaN(a)||isNaN(b)) return true;
    return v>=Math.min(a,b)&&v<=Math.max(a,b);
  }
  return true;
}
function scrRun(){
  if(!scrInited){ window.scrInit(); return; }
  var t0=new Date().getTime(), real=[], demo=[];
  scrConds.forEach(function(c){ (SCR_FIELDS[c.f].demo?demo:real).push(c); });
  scrHits=[];
  SCR_STOCKS.forEach(function(s){
    for(var i=0;i<real.length;i++) if(!scrPass(s,real[i])) return;
    var h=real.length;
    demo.forEach(function(){ if(Math.random()<0.5) h++; });
    scrHits.push({s:s,hit:h});
  });
  var ms=(new Date().getTime()-t0)+Math.round(30+Math.random()*80);
  var un=SCR_UNI[document.getElementById('scr-uni').value];
  var sh='命中 <b style="color:var(--text)">'+scrHits.length+'</b> 只 ｜ 宇宙 '+un[0]
    +' 共 <b style="color:var(--text)">'+un[1]+'</b> 只 <span class="badge b-na">演示样本池 10 只 · universe 注册表 待接入</span>'
    +' ｜ 执行 <b style="color:var(--text)">'+ms+'</b> ms <span class="dim">演示</span>';
  if(demo.length) sh+=' <span class="badge b-warn">含演示条件·命中数随机演示</span>';
  document.getElementById('scr-sum-l').innerHTML=sh;
  scrRenderTable();
}
function scrClear(){ scrConds=[]; scrRenderConds(); scrRun(); }
function scrPct(v,d){ return '<span class="'+(v>=0?'up':'down')+'">'+(v>=0?'+':'')+v.toFixed(d)+'%</span>'; }
function scrMfin(v){
  var t=Math.abs(v)>=10000? (v>=0?'+':'')+(v/10000).toFixed(2)+'亿' : (v>=0?'+':'')+Math.round(v)+'万';
  return '<span class="'+(v>=0?'up':'down')+'">'+t+'</span>';
}
function scrCell(s,k){
  switch(k){
    case 'code':  return s.code;
    case 'name':  return '<b>'+s.name+'</b>';
    case 'price': return s.price.toFixed(2);
    case 'chg':   return scrPct(s.chg,2);
    case 'pe':    return s.pe.toFixed(1);
    case 'pb':    return s.pb.toFixed(2);
    case 'div':   return s.div>0? s.div.toFixed(1)+'%':'—';
    case 'roe':   return s.roe.toFixed(1)+'%';
    case 'revg':  return scrPct(s.revg,1);
    case 'npg':   return scrPct(s.npg,1);
    case 'ret20': return scrPct(s.ret20,1);
    case 'turn':  return s.turn.toFixed(2)+'%';
    case 'mfin':  return scrMfin(s.mfin);
    case 'north': return scrPct(s.north,2);
  }
  return '—';
}
function scrGoStock(code){
  var nav=navOf('stock');
  if(!nav){scrToast('个股档案页未找到');return;}
  var short=code.split('.')[0];
  if(!STOCK_D[short]){scrToast('「'+code+'」档案演示数据未内置（仅 3 只演示标的），全量档案待接入');return;}
  go('stock',nav);
  var sels=document.querySelectorAll('.stock-sel');
  for(var i=0;i<sels.length;i++){
    if(sels[i].textContent.indexOf(short)===0){stockSwitch(short,sels[i]);break;}
  }
}
function scrOpCell(s){
  var a='<span style="color:var(--text);cursor:pointer;text-decoration:underline" onclick="scrGoStock(\''+s.code+'\')" title="去个股档案页">档案</span>';
  if(scrInPool[s.code]) return a+' <span class="badge b-pass">已加入（演示）</span>';
  return a+' <span class="btn" style="padding:2px 10px;font-size:11px" onclick="scrPool(\''+s.code+'\')">入作战池</span>';
}
/* ---- I-8 循环升级 R10：个股档案搜索（stockSrchGo——池内切换/池外待接入负反馈） ---- */
function stockSrchGo(){
  var inp=document.getElementById('stock-q'); if(!inp)return;
  var q=inp.value.trim();
  if(!q)return;
  var hit=null;
  for(var k in STOCK_D){
    var d=STOCK_D[k];
    if(k.indexOf(q)>=0||(d.name&&d.name.indexOf(q)>=0)){hit=k;break;}
  }
  if(hit){ inp.value=''; scrGoStock(hit+'.SH'); return; }
  scrToast('「'+q+'」档案演示数据未内置（仅 3 只演示标的：600519/300750/688981），全量档案待接入（负反馈也是结果——系统明说「没有」）');
}
/* ---- I-8 循环升级 R11：新闻检索（newsFilter/newsFSet——彭博 NSE 同位关键词搜索+双标签筛选） ---- */
var newsFCur='all';
function newsFilter(){
  var q=(document.getElementById('news-q')||{}).value||''; q=q.trim().toLowerCase();
  var rows=document.querySelectorAll('#news-table tr'),shown=0,total=0;
  rows.forEach(function(tr,i){
    if(i===0)return;
    total++;
    var txt=tr.textContent.toLowerCase();
    var okQ=!q||txt.indexOf(q)>=0;
    var okF=newsFCur==='all'||txt.indexOf(newsFCur)>=0;
    tr.style.display=(okQ&&okF)?'':'none';
    if(okQ&&okF)shown++;
  });
  var c=document.getElementById('news-fcount'); if(c)c.textContent=shown+' / '+total+' 条';
}
function newsFSet(f,el){
  document.querySelectorAll('#news-ftabs .tab').forEach(function(t){t.classList.remove('on');});
  if(el)el.classList.add('on'); newsFCur=f; newsFilter();
}
function scrRenderTable(){
  var cols=[];
  SCR_COLS.forEach(function(c){ if(c.fixed||c.on) cols.push(c); });
  var h='<tr>';
  cols.forEach(function(c){ h+='<th>'+c.cn+' <span class="dim" style="font-weight:400">'+c.en+'</span></th>'; });
  h+='</tr>';
  if(!scrHits.length){
    h+='<tr><td colspan="'+cols.length+'" class="dim" style="text-align:center;padding:16px">无命中——放宽条件或更换宇宙后重新执行（空结果也是结果，负反馈不掩饰）</td></tr>';
  }
  var demoN=0;
  scrConds.forEach(function(c){ if(SCR_FIELDS[c.f].demo) demoN++; });
  scrHits.forEach(function(r){
    h+='<tr>';
    cols.forEach(function(c){
      if(c.k==='hit'){
        h+='<td>'+(scrConds.length? '<b>'+r.hit+'</b> / '+scrConds.length+(demoN?' <span class="badge b-warn">演</span>':'') : '—')+'</td>';
      }else if(c.k==='op'){
        h+='<td>'+scrOpCell(r.s)+'</td>';
      }else{
        h+='<td>'+scrCell(r.s,c.k)+'</td>';
      }
    });
    h+='</tr>';
  });
  document.getElementById('scr-table').innerHTML=h;
}
function scrToggleCol(k,on){
  SCR_COLS.forEach(function(c){ if(c.k===k) c.on=on?1:0; });
  scrRenderTable();
}
function scrPool(code){
  scrInPool[code]=1;
  scrRenderTable();
  var nm='';
  SCR_STOCKS.forEach(function(s){ if(s.code===code) nm=s.name; });
  scrToast(nm+' 已加入作战池（演示）——作战室 W1 作战池联动示意');
}
function scrPreset(i){
  var p=SCR_PRESETS[i];
  scrConds=JSON.parse(JSON.stringify(p.c));
  scrRenderConds();
  scrRun();
  scrToast('预置方案「'+p.cn+'」已载入并执行（演示）');
}
function scrPlansGet(){ try{ return JSON.parse(localStorage.getItem('zk-screener-plans')||'{}'); }catch(e){ return {}; } }
function scrRenderPlans(sel){
  sel=sel||'';
  var p=scrPlansGet(), ks=Object.keys(p);
  var h='<option value="">已存方案（'+ks.length+'）载入…</option>';
  ks.forEach(function(k){ h+='<option value="'+scrEsc(k)+'"'+(k===sel?' selected':'')+'>'+scrEsc(k)+'</option>'; });
  document.getElementById('scr-plans').innerHTML=h;
}
function scrSavePlan(){
  var n=prompt('方案名称（保存到本机 localStorage）：');
  if(!n) return;
  var p=scrPlansGet();
  p[n]={u:document.getElementById('scr-uni').value,c:JSON.parse(JSON.stringify(scrConds))};
  try{ localStorage.setItem('zk-screener-plans',JSON.stringify(p)); }catch(e){}
  scrRenderPlans(n);
  scrToast('方案「'+n+'」已保存');
}
function scrLoadPlan(){
  var elm=document.getElementById('scr-plans'), k=elm.value;
  if(!k) return;
  var p=scrPlansGet();
  if(!p[k]) return;
  document.getElementById('scr-uni').value=p[k].u||'all';
  scrConds=JSON.parse(JSON.stringify(p[k].c||[]));
  scrRenderConds();
  scrRun();
  scrToast('方案「'+k+'」已载入并执行');
}
function scrDelPlan(){
  var elm=document.getElementById('scr-plans'), k=elm.value;
  if(!k){ scrToast('请先在已存方案下拉中选择要删除的方案'); return; }
  var p=scrPlansGet();
  delete p[k];
  try{ localStorage.setItem('zk-screener-plans',JSON.stringify(p)); }catch(e){}
  scrRenderPlans();
  scrToast('方案「'+k+'」已删除');
}
window.scrInit=function(){
  if(scrInited) return;
  scrInited=true;
  scrCatFields();
  var h='';
  SCR_COLS.forEach(function(c){
    if(c.fixed) return;
    h+='<label><input type="checkbox"'+(c.on?' checked':'')+' onchange="scrToggleCol(\''+c.k+'\',this.checked)"> '+c.cn+' <span class="dim">'+c.en+'</span></label>';
  });
  document.getElementById('scr-colcfg').innerHTML=h;
  scrRenderPlans();
  scrRenderConds();
  scrRun();
};
