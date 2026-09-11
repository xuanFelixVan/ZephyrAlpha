/* 功能模块：指数页指标计算+形态识别库（idx-patterns）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：纯函数库（无数据源，输入=K线数组）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L251-2267），逻辑零改动。
 * 验收单：ACC-F-IDX-PATTERNS
 */
function lcg(seed){var s=seed>>>0||1;return function(){s=(s*1103515245+12345)%2147483648;return s/2147483648;};}
function genCandles(seed,nb){
  var r=lcg(seed), n=nb||N_BARS, price=100, arr=[];
  var u=n/120;   /* 趋势分段按长度等比缩放（四.A 周/月 240 根可达；既有调用 genCandles(seed) 不受影响） */
  var segs=[[0,Math.round(36*u),0.55],[Math.round(36*u),Math.round(62*u),-0.5],[Math.round(62*u),Math.round(94*u),0.04],[Math.round(94*u),n,0.5]];
  for(var i=0;i<n;i++){
    var tr=0; for(var s=0;s<segs.length;s++){ if(i>=segs[s][0]&&i<segs[s][1]) tr=segs[s][2]; }
    var o=price, c=o+tr+(r()-0.5)*2.4;
    var h=Math.max(o,c)+r()*1.2, l=Math.min(o,c)-r()*1.2;
    arr.push({o:o,c:c,h:h,l:l,v:50+r()*60+Math.abs(tr)*40}); price=c;
  }
  /* 注入量能脉冲/枯竭（保证天量/地量标注路径可达；位置随 seed 确定性变化；%n 防 nb<120 时越界——币圈 sparkline genCandles(seed,40) 场景） */
  arr[(30+seed%15)%n].v*=3.1;
  arr[(75+seed%10)%n].v*=3.0;
  arr[(50+seed%8)%n].v*=0.25;
  return arr;
}
function rangeOf(d){var lo=1e9,hi=-1e9;d.forEach(function(k){lo=Math.min(lo,k.l);hi=Math.max(hi,k.h);});var pad=(hi-lo)*0.12;return[lo-pad,hi+pad];}
function ma(d,n,i){if(i<n-1)return null;var s=0;for(var j=i-n+1;j<=i;j++)s+=d[j].c;return s/n;}
function emaArr(vals,n){var a=2/(n+1),out=[],e=vals[0];for(var i=0;i<vals.length;i++){e=(i===0)?vals[i]:a*vals[i]+(1-a)*e;out.push(e);}return out;}
function kdjCalc(d){
  var K=[],D=[],J=[],k=50,dd=50;
  for(var i=0;i<d.length;i++){
    var s=Math.max(0,i-8),hh=-1e9,ll=1e9;
    for(var j=s;j<=i;j++){hh=Math.max(hh,d[j].h);ll=Math.min(ll,d[j].l);}
    var rsv=hh>ll?(d[i].c-ll)/(hh-ll)*100:50;
    k=2/3*k+1/3*rsv; dd=2/3*dd+1/3*k;
    K.push(k);D.push(dd);J.push(3*k-2*dd);
  }
  return[K,D,J];
}
function macdCalc(d){
  var c=d.map(function(k){return k.c;});
  var e12=emaArr(c,12),e26=emaArr(c,26);
  var dif=c.map(function(_,i){return e12[i]-e26[i];});
  var dea=emaArr(dif,9);
  var hist=dif.map(function(v,i){return (v-dea[i])*2;});
  return[dif,dea,hist];
}
function fractals(d){
  var tops=[],bots=[];
  for(var i=1;i<d.length-1;i++){
    if(d[i].h>d[i-1].h&&d[i].h>d[i+1].h&&d[i].l>d[i-1].l&&d[i].l>d[i+1].l) tops.push(i);
    if(d[i].l<d[i-1].l&&d[i].l<d[i+1].l&&d[i].h<d[i-1].h&&d[i].h<d[i+1].h) bots.push(i);
  }
  return{tops:tops,bots:bots};
}
/* ---- 追加指标计算（注册表常用项真实公式） ---- */
function rsiCalc(d,n){
  var up=0,dn=0,out=[];
  for(var i=0;i<d.length;i++){
    if(i===0){out.push(50);continue;}
    var ch=d[i].c-d[i-1].c;
    up=(up*(n-1)+Math.max(ch,0))/n; dn=(dn*(n-1)+Math.max(-ch,0))/n;
    out.push(dn===0?100:100-100/(1+up/dn));
  }
  return out;
}
function wrCalc(d,n){
  var out=[];
  for(var i=0;i<d.length;i++){
    var s=Math.max(0,i-n+1),hh=-1e9,ll=1e9;
    for(var j=s;j<=i;j++){hh=Math.max(hh,d[j].h);ll=Math.min(ll,d[j].l);}
    out.push(hh>ll?(hh-d[i].c)/(hh-ll)*(-100):-50);
  }
  return out;
}
function rocCalc(d,n){ return d.map(function(k,i){ return i>=n?(k.c/d[i-n].c-1)*100:0; }); }
function mtmCalc(d,n){ return d.map(function(k,i){ return i>=n?k.c-d[i-n].c:0; }); }
function obvCalc(d){
  var out=[],acc=0;
  for(var i=0;i<d.length;i++){
    if(i===0){acc=d[i].v;}
    else if(d[i].c>d[i-1].c) acc+=d[i].v;
    else if(d[i].c<d[i-1].c) acc-=d[i].v;
    out.push(acc);
  }
  return out;
}
function atrCalc(d,n){
  var out=[],acc=0;
  for(var i=0;i<d.length;i++){
    var tr=i===0?d[i].h-d[i].l:Math.max(d[i].h-d[i].l,Math.abs(d[i].h-d[i-1].c),Math.abs(d[i].l-d[i-1].c));
    acc=i<n?acc+tr/n:(acc*(n-1)+tr)/n;
    out.push(acc);
  }
  return out;
}
function candlePats(d){
  var found=[];
  for(var i=2;i<d.length;i++){
    var a=d[i-2],b=d[i-1],c=d[i];
    var body=Math.abs(c.c-c.o),range=c.h-c.l,upSh=c.h-Math.max(c.o,c.c),dnSh=Math.min(c.o,c.c)-c.l;
    if(range>0&&body/range<0.1) found.push({i:i,n:'十字星',dir:0});
    if(dnSh>2*body&&upSh<=body&&c.c>b.c) found.push({i:i,n:'锤子线',dir:1});
    if(b.c<b.o&&c.c>c.o&&c.c>=b.o&&c.o<=b.c) found.push({i:i,n:'看涨吞没',dir:1});
    if(b.c>b.o&&c.c<c.o&&c.c<=b.o&&c.o>=b.c) found.push({i:i,n:'看跌吞没',dir:-1});
    if(a.c<a.o&&Math.abs(b.c-b.o)<(a.o-a.c)*0.4&&c.c>c.o&&c.c>(a.o+a.c)/2) found.push({i:i,n:'启明星',dir:1});
    if(a.c>a.o&&Math.abs(b.c-b.o)<(a.c-a.o)*0.4&&c.c<c.o&&c.c<(a.o+a.c)/2) found.push({i:i,n:'黄昏星',dir:-1});
  }
  return found;
}
/* ---- I-1a 趋势类计算（7 项：wma/dema/tema/sar/dmi/adx） ---- */
function wmaArr(vals,n){
  var out=[],den=n*(n+1)/2;
  for(var i=0;i<vals.length;i++){
    if(i<n-1){out.push(null);continue;}
    var s=0; for(var j=0;j<n;j++) s+=vals[i-n+1+j]*(j+1);
    out.push(s/den);
  }
  return out;
}
function demaArr(vals,n){
  var e1=emaArr(vals,n),e2=emaArr(e1,n),out=[];
  for(var i=0;i<vals.length;i++) out.push(i<2*(n-1)?null:2*e1[i]-e2[i]);
  return out;
}
function temaArr(vals,n){
  var e1=emaArr(vals,n),e2=emaArr(e1,n),e3=emaArr(e2,n),out=[];
  for(var i=0;i<vals.length;i++) out.push(i<3*(n-1)?null:3*e1[i]-3*e2[i]+e3[i]);
  return out;
}
function sarCalc(d,step,mx){
  var out=[];
  for(var z=0;z<d.length;z++) out.push(null);
  if(d.length<3) return out;
  var up=d[2].c>=d[0].c;                                  /* 初始趋势：第3根收盘相对首根 */
  var sar=up?Math.min(d[0].l,d[1].l):Math.max(d[0].h,d[1].h);
  var ep=up?Math.max(d[0].h,d[1].h,d[2].h):Math.min(d[0].l,d[1].l,d[2].l);
  var af=step;
  out[2]=sar;
  for(var i=3;i<d.length;i++){
    sar=sar+af*(ep-sar);
    if(up){
      if(sar>d[i-1].l) sar=d[i-1].l;                      /* SAR 不得进入前两根低点之上 */
      if(sar>d[i-2].l) sar=d[i-2].l;
      if(d[i].h>ep){ep=d[i].h;af=Math.min(af+step,mx);}
      if(d[i].l<sar){up=false;sar=ep;ep=d[i].l;af=step;}  /* 下穿翻转：SAR 跳到前 EP */
    }else{
      if(sar<d[i-1].h) sar=d[i-1].h;
      if(sar<d[i-2].h) sar=d[i-2].h;
      if(d[i].l<ep){ep=d[i].l;af=Math.min(af+step,mx);}
      if(d[i].h>sar){up=true;sar=ep;ep=d[i].h;af=step;}
    }
    out[i]=sar;
  }
  return out;
}
function dmiCalc(d,n){
  /* Wilder 平滑：+DI/-DI 自第 n 根起有值，ADX 自第 2n-1 根起有值，之前填 null */
  var len=d.length,pdi=[],mdi=[],adx=[];
  for(var z=0;z<len;z++){pdi.push(null);mdi.push(null);adx.push(null);}
  var sTR=0,sP=0,sM=0,dxs=[],adxV=null;
  for(var i=1;i<len;i++){
    var up=d[i].h-d[i-1].h,dn=d[i-1].l-d[i].l;
    var pdm=(up>dn&&up>0)?up:0, mdm=(dn>up&&dn>0)?dn:0;
    var tr=Math.max(d[i].h-d[i].l,Math.abs(d[i].h-d[i-1].c),Math.abs(d[i].l-d[i-1].c));
    if(i<=n){sTR+=tr;sP+=pdm;sM+=mdm;}
    else{sTR=sTR-sTR/n+tr;sP=sP-sP/n+pdm;sM=sM-sM/n+mdm;}
    if(i>=n){
      var pi=sTR>0?100*sP/sTR:0, mi=sTR>0?100*sM/sTR:0;
      pdi[i]=pi; mdi[i]=mi;
      var dx=(pi+mi)>0?100*Math.abs(pi-mi)/(pi+mi):0;
      if(adxV===null){
        dxs.push(dx);
        if(dxs.length===n){var s=0;for(var q=0;q<n;q++)s+=dxs[q];adxV=s/n;adx[i]=adxV;}
      }else{
        adxV=(adxV*(n-1)+dx)/n; adx[i]=adxV;
      }
    }
  }
  return [pdi,mdi,adx];
}
function adxCalc(d,n){ return dmiCalc(d,n)[2]; }
/* ---- I-1b/I-1c 震荡+波动类计算（10 项） ---- */
function cciCalc(d,n){
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n-1){out.push(null);continue;}
    var s=0;
    for(var j=i-n+1;j<=i;j++) s+=(d[j].h+d[j].l+d[j].c)/3;
    var mtp=s/n, md=0;
    for(var j2=i-n+1;j2<=i;j2++) md+=Math.abs((d[j2].h+d[j2].l+d[j2].c)/3-mtp);
    md/=n;
    var tp=(d[i].h+d[i].l+d[i].c)/3;
    out.push(md===0?0:(tp-mtp)/(0.015*md));
  }
  return out;
}
function stochRsiCalc(d,n){          /* StochRSI(n,3,3)，复用 rsiCalc（自 0 起有值） */
  var RS=rsiCalc(d,n),raw=[],K=[],D=[];
  var i,j;
  for(i=0;i<d.length;i++){
    if(i<n-1){raw.push(null);continue;}
    var hh=-1e9,ll=1e9;
    for(j=i-n+1;j<=i;j++){hh=Math.max(hh,RS[j]);ll=Math.min(ll,RS[j]);}
    raw.push(hh>ll?(RS[i]-ll)/(hh-ll)*100:50);
  }
  for(i=0;i<d.length;i++){
    if(i<n+1){K.push(null);continue;}      /* %K=SMA3(raw)，需 i>=n-1+2 */
    K.push((raw[i]+raw[i-1]+raw[i-2])/3);
  }
  for(i=0;i<d.length;i++){
    if(i<n+3){D.push(null);continue;}      /* %D=SMA3(%K) */
    D.push((K[i]+K[i-1]+K[i-2])/3);
  }
  return [K,D];
}
function cmoCalc(d,n){
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n){out.push(null);continue;}
    var su=0,sd=0;
    for(var j=i-n+1;j<=i;j++){
      var ch=d[j].c-d[j-1].c;
      if(ch>0)su+=ch;else sd-=ch;
    }
    out.push(su+sd===0?0:100*(su-sd)/(su+sd));
  }
  return out;
}
function uoCalc(d){                   /* UO(7,14,28)，周期按任务裁定硬编码 */
  var bp=[],tr=[];
  for(var i=0;i<d.length;i++){
    var pc=i===0?d[i].o:d[i-1].c;
    bp.push(d[i].c-Math.min(d[i].l,pc));
    tr.push(Math.max(d[i].h,pc)-Math.min(d[i].l,pc));
  }
  var out=[];
  for(var i2=0;i2<d.length;i2++){
    if(i2<28){out.push(null);continue;}
    var b7=0,t7=0,b14=0,t14=0,b28=0,t28=0;
    for(var j2=i2-6;j2<=i2;j2++){b7+=bp[j2];t7+=tr[j2];}
    for(var j3=i2-13;j3<=i2;j3++){b14+=bp[j3];t14+=tr[j3];}
    for(var j4=i2-27;j4<=i2;j4++){b28+=bp[j4];t28+=tr[j4];}
    var r7=t7===0?0:b7/t7, r14=t14===0?0:b14/t14, r28=t28===0?0:b28/t28;
    out.push(100*(4*r7+2*r14+r28)/7);
  }
  return out;
}
function kcCalc(d){                   /* 中轨=EMA20（emaArr 自 0 起有值），轨=中轨±2×ATR(14) */
  var c=d.map(function(k){return k.c;});
  var mid=emaArr(c,20), at=atrCalc(d,14), up=[], low=[];
  for(var i=0;i<d.length;i++){up.push(mid[i]+2*at[i]);low.push(mid[i]-2*at[i]);}
  return [up,mid,low];
}
function dcCalc(d,n){                 /* 窗口含当前根（与 ma/boll 分支口径一致），短窗用部分窗口 */
  var up=[],mid=[],low=[];
  for(var i=0;i<d.length;i++){
    var s=Math.max(0,i-n+1),hh=-1e9,ll=1e9;
    for(var j=s;j<=i;j++){hh=Math.max(hh,d[j].h);ll=Math.min(ll,d[j].l);}
    up.push(hh);low.push(ll);mid.push((hh+ll)/2);
  }
  return [up,mid,low];
}
function stdCalc(d,n){
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n-1){out.push(null);continue;}
    var m=ma(d,n,i),sd=0;
    for(var j=i-n+1;j<=i;j++)sd+=(d[j].c-m)*(d[j].c-m);
    out.push(Math.sqrt(sd/n));
  }
  return out;
}
function bollBands(d,n,k){            /* bollw/bollb 共用；口径与 boll 分支一致（ma 前 19 根为 null） */
  var up=[],mid=[],low=[];
  for(var i=0;i<d.length;i++){
    var m=ma(d,n,i);
    if(m===null){up.push(null);mid.push(null);low.push(null);continue;}
    var sd=0;
    for(var j=i-n+1;j<=i;j++)sd+=(d[j].c-m)*(d[j].c-m);
    sd=Math.sqrt(sd/n);
    up.push(m+k*sd);mid.push(m);low.push(m-k*sd);
  }
  return [up,mid,low];
}
function bollwCalc(d,n,k){
  var BB=bollBands(d,n,k),out=[];
  for(var i=0;i<d.length;i++){
    out.push(BB[0][i]===null?null:(BB[0][i]-BB[2][i])/BB[1][i]*100);
  }
  return out;
}
function bollbCalc(d,n,k){
  var BB=bollBands(d,n,k),out=[];
  for(var i=0;i<d.length;i++){
    if(BB[0][i]===null){out.push(null);continue;}
    var den=BB[0][i]-BB[2][i];
    out.push(den===0?0.5:(d[i].c-BB[2][i])/den);
  }
  return out;
}
function hvCalc(d,n){                 /* 日收益对数标准差×√252 年化，输出百分数 */
  var r=[null];
  for(var i=1;i<d.length;i++) r.push(Math.log(d[i].c/d[i-1].c));
  var out=[];
  for(var i2=0;i2<d.length;i2++){
    if(i2<n){out.push(null);continue;}
    var m=0;
    for(var j=i2-n+1;j<=i2;j++)m+=r[j];
    m/=n;
    var sd=0;
    for(var j2=i2-n+1;j2<=i2;j2++)sd+=(r[j2]-m)*(r[j2]-m);
    out.push(Math.sqrt(sd/n)*Math.sqrt(252)*100);
  }
  return out;
}
/* ---- I-1d 量能类计算（7 项） ---- */
function mfiCalc(d,n){                 /* MFI(n)：典型价资金流比率，0~100；前 n 根 null */
  var tp=[],i;
  for(i=0;i<d.length;i++) tp.push((d[i].h+d[i].l+d[i].c)/3);
  var out=[];
  for(i=0;i<d.length;i++){
    if(i<n){out.push(null);continue;}
    var pos=0,neg=0;
    for(var j=i-n+1;j<=i;j++){
      var rmf=tp[j]*d[j].v;
      if(tp[j]>tp[j-1]) pos+=rmf;
      else if(tp[j]<tp[j-1]) neg+=rmf;
    }
    out.push(neg===0?100:100-100/(1+pos/neg));
  }
  return out;
}
function vwapCalc(d){                  /* 窗口锚定 VWAP：从第 0 根累计 ΣTP·V/ΣV */
  var out=[],tpv=0,sv=0;
  for(var i=0;i<d.length;i++){
    var k=d[i],tp=(k.h+k.l+k.c)/3;
    tpv+=tp*k.v; sv+=k.v;
    out.push(sv===0?tp:tpv/sv);
  }
  return out;
}
function vrCalc(d,n){                  /* VR(n)：(涨量+平量/2)/(跌量+平量/2)×100；前 n 根 null */
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n){out.push(null);continue;}
    var up=0,dn=0,fl=0;
    for(var j=i-n+1;j<=i;j++){
      if(d[j].c>d[j-1].c) up+=d[j].v;
      else if(d[j].c<d[j-1].c) dn+=d[j].v;
      else fl+=d[j].v;
    }
    var den=dn+fl/2;
    out.push(den===0?200:(up+fl/2)/den*100);
  }
  return out;
}
function adlCalc(d){                   /* ADL：累计 ΣCLV×v，h=l 时 CLV=0 */
  var out=[],acc=0;
  for(var i=0;i<d.length;i++){
    var k=d[i],rg=k.h-k.l;
    var clv=rg>0?((k.c-k.l)-(k.h-k.c))/rg:0;
    acc+=clv*k.v; out.push(acc);
  }
  return out;
}
function pvtCalc(d){                   /* PVT：累计 Σ((c-c_prev)/c_prev)×v */
  var out=[],acc=0;
  for(var i=0;i<d.length;i++){
    if(i>0&&d[i-1].c!==0) acc+=(d[i].c-d[i-1].c)/d[i-1].c*d[i].v;
    out.push(acc);
  }
  return out;
}
function cmfCalc(d,n){                 /* CMF(n)：滚动 Σ(CLV×v)/Σv；前 n-1 根 null */
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n-1){out.push(null);continue;}
    var sv=0,scv=0;
    for(var j=i-n+1;j<=i;j++){
      var k=d[j],rg=k.h-k.l;
      var clv=rg>0?((k.c-k.l)-(k.h-k.c))/rg:0;
      scv+=clv*k.v; sv+=k.v;
    }
    out.push(sv===0?0:scv/sv);
  }
  return out;
}
function wvadCalc(d,n){                /* WVAD：(c-o)/(h-l)×v（h=l 时 0）+ n 根均线；返回 [WV,MA] */
  var WV=[],WM=[];
  for(var i=0;i<d.length;i++){
    var k=d[i],rg=k.h-k.l;
    WV.push(rg>0?(k.c-k.o)/rg*k.v:0);
  }
  for(i=0;i<d.length;i++){
    if(i<n-1){WM.push(null);continue;}
    var s=0; for(var j=i-n+1;j<=i;j++) s+=WV[j];
    WM.push(s/n);
  }
  return[WV,WM];
}
/* ---- I-1e K线形态识别 20 种扩容版（chart_pattern 注册表 18 条目/20 规则；旧 candlePats 保留供回滚） ---- */
function candlePats20(d){
  var n=d.length,found=[],i;
  var avgB=0;
  for(i=0;i<n;i++) avgB+=Math.abs(d[i].c-d[i].o);
  avgB=n?avgB/n:1; if(avgB<=0) avgB=1e-9;   /* 全序列均实体：「大实体/容差」统一基准 */
  function an(k){var b=Math.abs(k.c-k.o),r=k.h-k.l;if(r<=0)r=1e-9;return{b:b,r:r,u:k.h-Math.max(k.o,k.c),d:Math.min(k.o,k.c)-k.l};}
  function r5(i){return i>=5&&d[i-5].c>0?d[i].c/d[i-5].c-1:0;}   /* 前5根涨跌幅：区分趋势段与震荡段 */
  /* ---- 单根类 8 ---- */
  function isHammer(i){var p=an(d[i]);return r5(i)<=-0.01&&p.d>=1.8*p.b&&p.u<=p.b&&p.d>=0.45*p.r;}
  function isHangMan(i){var p=an(d[i]);return r5(i)>=0.01&&p.d>=1.8*p.b&&p.u<=p.b&&p.d>=0.45*p.r;}
  function isInvHammer(i){var p=an(d[i]);return r5(i)<=-0.01&&p.u>=1.8*p.b&&p.d<=p.b&&p.u>=0.45*p.r;}
  function isShootStar(i){var p=an(d[i]);return r5(i)>=0.01&&p.u>=1.8*p.b&&p.d<=p.b&&p.u>=0.45*p.r;}
  function isDoji(i){var p=an(d[i]);return p.b/p.r<=0.1;}
  function isGravestone(i){var p=an(d[i]);return p.b/p.r<=0.1&&p.d/p.r<=0.1&&p.u/p.r>=0.6;}
  function isBigYang(i){var p=an(d[i]);return d[i].c>d[i].o&&p.b>=avgB&&p.u<=0.2*p.r&&p.d<=0.2*p.r;}
  function isBigYin(i){var p=an(d[i]);return d[i].c<d[i].o&&p.b>=avgB&&p.u<=0.2*p.r&&p.d<=0.2*p.r;}
  /* ---- 双根类 8 ---- */
  function isBullEngulf(i){var b=d[i-1],c=d[i];return b.c<b.o&&Math.abs(b.c-b.o)>=0.4*avgB&&c.c>c.o&&c.c>=b.o&&c.o<=b.c;}
  function isBearEngulf(i){var b=d[i-1],c=d[i];return b.c>b.o&&Math.abs(b.c-b.o)>=0.4*avgB&&c.c<c.o&&c.c<=b.o&&c.o>=b.c;}
  function isPiercing(i){var b=d[i-1],c=d[i];return b.c<b.o&&Math.abs(b.c-b.o)>=0.5*avgB&&c.c>c.o&&c.o<=b.c&&c.c>(b.o+b.c)/2&&c.c<b.o;}
  function isDarkCloud(i){var b=d[i-1],c=d[i];return b.c>b.o&&Math.abs(b.c-b.o)>=0.5*avgB&&c.c<c.o&&c.o>=b.c&&c.c<(b.o+b.c)/2&&c.c>b.o;}
  function isBullHarami(i){var b=d[i-1],c=d[i],bb=Math.abs(b.c-b.o),cb=Math.abs(c.c-c.o);return r5(i)<=-0.01&&b.c<b.o&&bb>=0.8*avgB&&cb<=0.6*bb&&Math.max(c.o,c.c)<=b.o&&Math.min(c.o,c.c)>=b.c;}
  function isBearHarami(i){var b=d[i-1],c=d[i],bb=Math.abs(b.c-b.o),cb=Math.abs(c.c-c.o);return r5(i)>=0.01&&b.c>b.o&&bb>=0.8*avgB&&cb<=0.6*bb&&Math.max(c.o,c.c)<=b.c&&Math.min(c.o,c.c)>=b.o;}
  function isTweezerBot(i){
    if(r5(i)>-0.01)return false;
    var p=an(d[i]),tol=0.3*avgB;
    for(var j=Math.max(1,i-3);j<i;j++){var q=an(d[j]);if(Math.abs(d[i].l-d[j].l)<=tol&&q.d>=0.3*q.r&&p.d>=0.3*p.r)return true;}
    return false;
  }
  function isTweezerTop(i){
    if(r5(i)<0.01)return false;
    var p=an(d[i]),tol=0.3*avgB;
    for(var j=Math.max(1,i-3);j<i;j++){var q=an(d[j]);if(Math.abs(d[i].h-d[j].h)<=tol&&q.u>=0.3*q.r&&p.u>=0.3*p.r)return true;}
    return false;
  }
  /* ---- 三根类 4 ---- */
  function isMorningStar(i){var a=d[i-2],b=d[i-1],c=d[i];return a.c<a.o&&Math.abs(b.c-b.o)<(a.o-a.c)*0.4&&c.c>c.o&&c.c>(a.o+a.c)/2;}
  function isEveningStar(i){var a=d[i-2],b=d[i-1],c=d[i];return a.c>a.o&&Math.abs(b.c-b.o)<(a.c-a.o)*0.4&&c.c<c.o&&c.c<(a.o+a.c)/2;}
  function isThreeWhite(i){
    var a=d[i-2],b=d[i-1],c=d[i];
    return a.c>a.o&&b.c>b.o&&c.c>c.o&&b.c>a.c&&c.c>b.c
      &&Math.abs(a.c-a.o)>=0.5*avgB&&Math.abs(b.c-b.o)>=0.5*avgB&&Math.abs(c.c-c.o)>=0.5*avgB
      &&a.o>0&&(c.c-a.o)/a.o>=0.012;
  }
  function isThreeCrows(i){
    var a=d[i-2],b=d[i-1],c=d[i];
    return a.c<a.o&&b.c<b.o&&c.c<c.o&&b.c<a.c&&c.c<b.c
      &&Math.abs(a.c-a.o)>=0.5*avgB&&Math.abs(b.c-b.o)>=0.5*avgB&&Math.abs(c.c-c.o)>=0.5*avgB
      &&a.o>0&&(a.o-c.c)/a.o>=0.012;
  }
  for(i=2;i<n;i++){
    if(isHammer(i)) found.push({i:i,n:'锤子线',dir:1});
    if(isHangMan(i)) found.push({i:i,n:'上吊线',dir:-1});
    if(isInvHammer(i)) found.push({i:i,n:'倒锤子线',dir:1});
    if(isShootStar(i)) found.push({i:i,n:'射击之星',dir:-1});
    if(isDoji(i)) found.push({i:i,n:'十字星',dir:0});
    if(isGravestone(i)) found.push({i:i,n:'墓碑十字',dir:-1});
    if(isBigYang(i)) found.push({i:i,n:'大阳线',dir:1});
    if(isBigYin(i)) found.push({i:i,n:'大阴线',dir:-1});
    if(isBullEngulf(i)) found.push({i:i,n:'看涨吞没',dir:1});
    if(isBearEngulf(i)) found.push({i:i,n:'看跌吞没',dir:-1});
    if(isPiercing(i)) found.push({i:i,n:'刺透线',dir:1});
    if(isDarkCloud(i)) found.push({i:i,n:'乌云盖顶',dir:-1});
    if(isBullHarami(i)) found.push({i:i,n:'看涨孕线',dir:1});
    if(isBearHarami(i)) found.push({i:i,n:'看跌孕线',dir:-1});
    if(isTweezerBot(i)) found.push({i:i,n:'镊子底',dir:1});
    if(isTweezerTop(i)) found.push({i:i,n:'镊子顶',dir:-1});
    if(isMorningStar(i)) found.push({i:i,n:'启明星',dir:1});
    if(isEveningStar(i)) found.push({i:i,n:'黄昏星',dir:-1});
    if(isThreeWhite(i)) found.push({i:i,n:'红三兵',dir:1});
    if(isThreeCrows(i)) found.push({i:i,n:'三只乌鸦',dir:-1});
  }
  return found;
}
/* ---- I-1 后续子批：RSI 背离检测（摆动点配对：价格峰谷 × RSI 峰谷） ---- */
function rsiDivergence(d,RS){
  var n=d.length,pk=[],vl=[],i,j;
  for(i=2;i<n-2;i++){   /* 窗口 2 的收盘价摆动点 */
    if(d[i].c>=d[i-1].c&&d[i].c>=d[i-2].c&&d[i].c>=d[i+1].c&&d[i].c>=d[i+2].c) pk.push(i);
    if(d[i].c<=d[i-1].c&&d[i].c<=d[i-2].c&&d[i].c<=d[i+1].c&&d[i].c<=d[i+2].c) vl.push(i);
  }
  var out=[];
  for(j=1;j<pk.length;j++){   /* 峰对峰：价格新高 + RSI 走低 = 顶背离 */
    var a=pk[j-1],b=pk[j];
    if(b-a<5) continue;
    if(d[b].c>d[a].c&&RS[b]<RS[a]-2) out.push({i1:a,i2:b,dir:-1,n:'顶背离'});
  }
  for(j=1;j<vl.length;j++){   /* 谷对谷：价格新低 + RSI 走高 = 底背离 */
    var a2=vl[j-1],b2=vl[j];
    if(b2-a2<5) continue;
    if(d[b2].c<d[a2].c&&RS[b2]>RS[a2]+2) out.push({i1:a2,i2:b2,dir:1,n:'底背离'});
  }
  return out;
}
/* ---- I-1 后续子批：经典形态库扩展批（19 规则，叠加在 candlePats20 之上；pat 渲染器=39 规则合集） ---- */
function patExt(d){
  var n=d.length,found=[],i;
  var avgB=0,avgR=0;
  for(i=0;i<n;i++){avgB+=Math.abs(d[i].c-d[i].o);avgR+=(d[i].h-d[i].l);}
  avgB=n?avgB/n:1; avgR=n?avgR/n:1; if(avgB<=0)avgB=1e-9; if(avgR<=0)avgR=1e-9;
  function an(k){var b=Math.abs(k.c-k.o),r=k.h-k.l;if(r<=0)r=1e-9;return{b:b,r:r,u:k.h-Math.max(k.o,k.c),d:Math.min(k.o,k.c)-k.l};}
  function r5(i){return i>=5&&d[i-5].c>0?d[i].c/d[i-5].c-1:0;}
  /* ---- 单根类 7 ---- */
  function isDragonfly(i){var p=an(d[i]);return p.b/p.r<=0.1&&p.u/p.r<=0.1&&p.d/p.r>=0.6;}
  function isLongLeg(i){var p=an(d[i]);return p.b/p.r<=0.15&&p.u/p.r>=0.35&&p.d/p.r>=0.35;}
  function isSpinTop(i){var p=an(d[i]);return p.b/p.r<=0.35&&p.b<=0.6*avgB&&p.u>=0.5*p.b&&p.d>=0.5*p.b&&p.u>=0.15*p.r&&p.d>=0.15*p.r;}
  function isHighWave(i){var p=an(d[i]);return p.b/p.r<=0.2&&p.r>=1.8*avgR&&p.u>=p.b&&p.d>=p.b;}
  function isRickshaw(i){var p=an(d[i]);return p.b/p.r<=0.1&&p.u/p.r>=0.3&&p.d/p.r>=0.3;}
  function isBeltBull(i){var p=an(d[i]);return d[i].c>d[i].o&&p.d<=0.05*p.r&&p.b>=avgB&&r5(i)<=-0.01;}
  function isBeltBear(i){var p=an(d[i]);return d[i].c<d[i].o&&p.u<=0.05*p.r&&p.b>=avgB&&r5(i)>=0.01;}
  /* ---- 双根类 4 ---- */
  function isHaramiCrossBull(i){var b=d[i-1],c=d[i],bb=b.o-b.c,cp=an(c);return r5(i)<=-0.01&&b.c<b.o&&bb>=0.8*avgB&&cp.b/cp.r<=0.1&&c.h<=b.o&&c.l>=b.c;}
  function isHaramiCrossBear(i){var b=d[i-1],c=d[i],bb=b.c-b.o,cp=an(c);return r5(i)>=0.01&&b.c>b.o&&bb>=0.8*avgB&&cp.b/cp.r<=0.1&&c.h<=b.c&&c.l>=b.o;}
  function isCounterBull(i){var b=d[i-1],c=d[i];return r5(i)<=-0.01&&b.c<b.o&&c.c>c.o&&Math.abs(c.c-b.c)<=0.3*avgB&&Math.abs(b.c-b.o)>=0.5*avgB;}
  function isCounterBear(i){var b=d[i-1],c=d[i];return r5(i)>=0.01&&b.c>b.o&&c.c<c.o&&Math.abs(c.c-b.c)<=0.3*avgB&&Math.abs(b.c-b.o)>=0.5*avgB;}
  /* ---- 三根类 4 ---- */
  function isMorningDoji(i){var a=d[i-2],b=d[i-1],c=d[i],bp=an(b);return a.c<a.o&&(a.o-a.c)>=0.5*avgB&&bp.b/bp.r<=0.1&&b.c<a.c&&c.c>c.o&&c.c>(a.o+a.c)/2;}
  function isEveningDoji(i){var a=d[i-2],b=d[i-1],c=d[i],bp=an(b);return a.c>a.o&&(a.c-a.o)>=0.5*avgB&&bp.b/bp.r<=0.1&&b.c>a.c&&c.c<c.o&&c.c<(a.o+a.c)/2;}
  function isAbandonBaby(i){var a=d[i-2],b=d[i-1],c=d[i],bp=an(b);return a.c<a.o&&(a.o-a.c)>=0.5*avgB&&bp.b/bp.r<=0.1&&b.h<a.l&&c.c>c.o&&(c.c-c.o)>=0.5*avgB&&c.l>b.h;}
  function isAbandonTop(i){var a=d[i-2],b=d[i-1],c=d[i],bp=an(b);return a.c>a.o&&(a.c-a.o)>=0.5*avgB&&bp.b/bp.r<=0.1&&b.l>a.h&&c.c<c.o&&(c.o-c.c)>=0.5*avgB&&c.h<b.l;}
  for(i=2;i<n;i++){
    if(isDragonfly(i)) found.push({i:i,n:'蜻蜓十字',dir:0});
    if(isLongLeg(i)) found.push({i:i,n:'长腿十字',dir:0});
    if(isSpinTop(i)) found.push({i:i,n:'纺锤顶',dir:0});
    if(isHighWave(i)) found.push({i:i,n:'高浪线',dir:0});
    if(isRickshaw(i)) found.push({i:i,n:'黄包车夫',dir:0});
    if(isBeltBull(i)) found.push({i:i,n:'看涨腰带线',dir:1});
    if(isBeltBear(i)) found.push({i:i,n:'看跌腰带线',dir:-1});
    if(isHaramiCrossBull(i)) found.push({i:i,n:'看涨孕线十字',dir:1});
    if(isHaramiCrossBear(i)) found.push({i:i,n:'看跌孕线十字',dir:-1});
    if(isCounterBull(i)) found.push({i:i,n:'看涨反击线',dir:1});
    if(isCounterBear(i)) found.push({i:i,n:'看跌反击线',dir:-1});
    if(isMorningDoji(i)) found.push({i:i,n:'启明十字星',dir:1});
    if(isEveningDoji(i)) found.push({i:i,n:'黄昏十字星',dir:-1});
    if(isAbandonBaby(i)) found.push({i:i,n:'弃婴（底部）',dir:1});
    if(isAbandonTop(i)) found.push({i:i,n:'弃婴（顶部）',dir:-1});
  }
  return found;
}
/* ---- I-1 第三批（2026-08-23 CWIRE）：CANDLE 持续形态/三根族余项 16 规则（对齐注册表 PAT-CANDLE-032/033/034/042/044/045/048/049/050/052/053/054） ---- */
function patExt2(d){
  var n=d.length,found=[],i;
  var avgB=0;
  for(i=0;i<n;i++) avgB+=Math.abs(d[i].c-d[i].o);
  avgB=n?avgB/n:1; if(avgB<=0)avgB=1e-9;
  function an(k){var b=Math.abs(k.c-k.o),r=k.h-k.l;if(r<=0)r=1e-9;return{b:b,r:r,u:k.h-Math.max(k.o,k.c),d:Math.min(k.o,k.c)-k.l};}
  function r5(i){return i>=5&&d[i-5].c>0?d[i].c/d[i-5].c-1:0;}
  /* 持续五根族：上升/下降三法（PAT-CANDLE-054） */
  function isRising3(i){   /* 大阳 + 三根小实体收敛于首根实体 + 大阳创新高 */
    var a=d[i-4],e=d[i];
    if(!(a.c>a.o&&(a.c-a.o)>=avgB&&e.c>e.o&&(e.c-e.o)>=avgB&&e.c>a.c))return false;
    for(var j=i-3;j<=i-1;j++){var k=d[j];if(Math.abs(k.c-k.o)>=0.6*(a.c-a.o))return false;if(k.l<a.o||k.h>a.c*1.01)return false;}
    return true;
  }
  function isFalling3(i){
    var a=d[i-4],e=d[i];
    if(!(a.c<a.o&&(a.o-a.c)>=avgB&&e.c<e.o&&(e.o-e.c)>=avgB&&e.c<a.c))return false;
    for(var j=i-3;j<=i-1;j++){var k=d[j];if(Math.abs(k.c-k.o)>=0.6*(a.o-a.c))return false;if(k.h>a.o||k.l<a.c*0.99)return false;}
    return true;
  }
  /* 双根持续：分手线（052）/入颈线（048）/上颈线（049）/插入线（050）/并排阳线（053） */
  function isSepBull(i){var b=d[i-1],c=d[i];return r5(i-1)>=0.01&&b.c<b.o&&c.c>c.o&&Math.abs(c.o-b.o)<=0.3*avgB&&Math.abs(b.c-b.o)>=0.5*avgB;}
  function isSepBear(i){var b=d[i-1],c=d[i];return r5(i-1)<=-0.01&&b.c>b.o&&c.c<c.o&&Math.abs(c.o-b.o)<=0.3*avgB&&Math.abs(b.c-b.o)>=0.5*avgB;}
  function isInNeck(i){var b=d[i-1],c=d[i];return r5(i)<=-0.01&&(b.o-b.c)>=avgB&&c.c>c.o&&Math.abs(c.c-b.c)<=0.15*(b.o-b.c);}
  function isOnNeck(i){var b=d[i-1],c=d[i];return r5(i)<=-0.01&&(b.o-b.c)>=avgB&&c.c>c.o&&Math.abs(c.c-b.l)<=0.1*(b.o-b.c);}
  function isThrust(i){var b=d[i-1],c=d[i];var mid=(b.o+b.c)/2;return r5(i)<=-0.01&&(b.o-b.c)>=avgB&&c.c>c.o&&c.c>b.c&&c.c<mid;}   /* 插入线：收复昨收但未过实体中点 */
  function isSideWhite(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)>=0.01&&a.c>a.o&&b.c>b.o&&c.c>c.o&&b.o>a.c*1.005&&Math.abs(c.o-b.o)<=0.3*avgB&&Math.abs((c.c-c.o)-(b.c-b.o))<=0.5*avgB;}
  /* 三根族余项：内含三线（032）/外包三线（033）/两只乌鸦（045）/跳空双鸦（044）/大敌当前（042）/三线打击（034） */
  function is3InsideUp(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)<=-0.01&&(a.o-a.c)>=0.8*avgB&&b.c>b.o&&Math.abs(b.c-b.o)<=0.6*(a.o-a.c)&&Math.max(b.o,b.c)<=a.o&&Math.min(b.o,b.c)>=a.c&&c.c>c.o&&c.c>a.o;}
  function is3InsideDn(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)>=0.01&&(a.c-a.o)>=0.8*avgB&&b.c<b.o&&Math.abs(b.c-b.o)<=0.6*(a.c-a.o)&&Math.max(b.o,b.c)<=a.c&&Math.min(b.o,b.c)>=a.o&&c.c<c.o&&c.c<a.o;}
  function is3OutsideUp(i){var a=d[i-2],b=d[i-1],c=d[i];return a.c<a.o&&b.c>b.o&&b.c>=a.o&&b.o<=a.c&&c.c>c.o&&c.c>b.c;}
  function is3OutsideDn(i){var a=d[i-2],b=d[i-1],c=d[i];return a.c>a.o&&b.c<b.o&&b.c<=a.o&&b.o>=a.c&&c.c<c.o&&c.c<b.c;}
  function isTwoCrows(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)>=0.01&&a.c>a.o&&(a.c-a.o)>=0.5*avgB&&b.c<b.o&&b.o>a.c*1.003&&c.c<c.o&&c.o>b.o&&c.c<b.c&&c.c>a.c;}
  function isGap2Crows(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)>=0.01&&a.c>a.o&&(a.c-a.o)>=0.5*avgB&&b.c<b.o&&b.l>a.c*1.003&&c.c<c.o&&c.o>b.o&&c.c<b.o&&c.c>a.c;}
  function isAdvBlock(i){
    var a=d[i-2],b=d[i-1],c=d[i];
    if(!(a.c>a.o&&b.c>b.o&&c.c>c.o&&b.c>a.c&&c.c>b.c))return false;
    var ba=a.c-a.o,bb=b.c-b.o,bc=c.c-c.o;
    return ba>=0.5*avgB&&bb<ba*0.85&&bc<bb*0.85&&an(c).u>bc*0.5;   /* 实体递减+上影拉长=推进受阻 */
  }
  function is3LineStrike(i){
    var a=d[i-3],b=d[i-2],c=d[i-1],e=d[i];
    return a.c>a.o&&b.c>b.o&&c.c>c.o&&b.c>a.c&&c.c>b.c
      &&(a.c-a.o)>=0.5*avgB&&(b.c-b.o)>=0.5*avgB&&(c.c-c.o)>=0.5*avgB
      &&e.c<e.o&&(e.o-e.c)>=avgB&&e.o>=c.c*0.99&&e.c<a.o;   /* 三连阳后大阴吞没=持续蓄势（Bulkowski 口径偏多） */
  }
  for(i=4;i<n;i++){
    if(isRising3(i)) found.push({i:i,n:'上升三法',dir:1});
    if(isFalling3(i)) found.push({i:i,n:'下降三法',dir:-1});
    if(isSepBull(i)) found.push({i:i,n:'看涨分手线',dir:1});
    if(isSepBear(i)) found.push({i:i,n:'看跌分手线',dir:-1});
    if(isInNeck(i)) found.push({i:i,n:'入颈线',dir:-1});
    if(isOnNeck(i)) found.push({i:i,n:'上颈线',dir:-1});
    if(isThrust(i)) found.push({i:i,n:'插入线',dir:-1});
    if(isSideWhite(i)) found.push({i:i,n:'并排阳线',dir:1});
    if(is3InsideUp(i)) found.push({i:i,n:'内含三线涨',dir:1});
    if(is3InsideDn(i)) found.push({i:i,n:'内含三线跌',dir:-1});
    if(is3OutsideUp(i)) found.push({i:i,n:'外包三线涨',dir:1});
    if(is3OutsideDn(i)) found.push({i:i,n:'外包三线跌',dir:-1});
    if(isTwoCrows(i)) found.push({i:i,n:'两只乌鸦',dir:-1});
    if(isGap2Crows(i)) found.push({i:i,n:'跳空双鸦',dir:-1});
    if(isAdvBlock(i)) found.push({i:i,n:'大敌当前',dir:-1});
    if(is3LineStrike(i)) found.push({i:i,n:'三线打击',dir:1});
  }
  return found;
}
/* ---- 图表形态 zigzag 公共构建（fractals 压缩：同型留更极端者，异型距离≥3 入列） ---- */
function zigzagPts(d){
  var fr=fractals(d),zz=[];
  var pts=fr.tops.map(function(t){return{i:t,tp:1};}).concat(fr.bots.map(function(b){return{i:b,tp:-1};}));
  pts.sort(function(a,b){return a.i-b.i;});
  pts.forEach(function(p){
    var L=zz[zz.length-1];
    if(!L){zz.push(p);return;}
    if(p.tp===L.tp){
      if((p.tp===1&&d[p.i].h>=d[L.i].h)||(p.tp===-1&&d[p.i].l<=d[L.i].l)) zz[zz.length-1]=p;
    }else if(p.i-L.i>=3){zz.push(p);}
  });
  return zz;
}
/* ---- I-1 第三批（2026-08-23 CWIRE）：CHART 三角/楔形/旗形/矩形/三重顶底 10 规则（对齐注册表 PAT-CHART-005~011/015/017/018） ---- */
function chartPats2(d){
  var n=d.length,found=[],i;
  var zz=zigzagPts(d);
  function slope(arr,acc){   /* 最小二乘斜率（按 zz 点位价格），acc: 取值函数 */
    var m=arr.length;if(m<3)return 0;
    var sx=0,sy=0,sxy=0,sxx=0;
    for(var k=0;k<m;k++){var v=acc(arr[k]);sx+=k;sy+=v;sxy+=k*v;sxx+=k*k;}
    var den=m*sxx-sx*sx; if(!den)return 0;
    return (m*sxy-sx*sy)/den;
  }
  function flat(arr,acc,tol){var vs=arr.map(acc),mn=Math.min.apply(null,vs),mx=Math.max.apply(null,vs);return mn>0&&(mx-mn)/mn<=tol;}
  /* 当前结构（末端 6 个 zz 点）：三角/楔形/矩形（单一标注） */
  if(zz.length>=6){
    var seg=zz.slice(-6);
    var tops=seg.filter(function(p){return p.tp===1;}),bots=seg.filter(function(p){return p.tp===-1;});
    if(tops.length>=2&&bots.length>=2){
      var tS=slope(tops,function(p){return d[p.i].h;}),bS=slope(bots,function(p){return d[p.i].l;});
      var ref=d[seg[seg.length-1].i].c, eps=ref*0.0015;   /* 斜率阈值≈每点 0.15% */
      var tFlat=flat(tops,function(p){return d[p.i].h;},0.02),bFlat=flat(bots,function(p){return d[p.i].l;},0.02);
      var end=seg[seg.length-1].i;
      if(tFlat&&bFlat&&Math.abs(tS)<=eps&&Math.abs(bS)<=eps) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'矩形箱体',dir:0});
      else if(tFlat&&bS>eps) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'上升三角形',dir:1});
      else if(bFlat&&tS<-eps) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'下降三角形',dir:-1});
      else if(tS<-eps&&bS>eps) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'对称三角形',dir:0});
      else if(tS>eps&&bS>tS*1.3) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'上升楔形',dir:-1});
      else if(tS<-eps&&bS<0&&bS>tS) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'下降楔形',dir:1});
    }
  }
  /* 三重顶/底（zz 顶底交替，五点结构 T,B,T,B,T / B,T,B,T,B，全部窗口扫描逐处标注） */
  for(i=4;i<zz.length;i++){
    var u1=zz[i-4],u3=zz[i-2],u5=zz[i];
    if(u1.tp===1&&zz[i-3].tp===-1&&u3.tp===1&&zz[i-1].tp===-1&&u5.tp===1
      &&flat([u1,u3,u5],function(p){return d[p.i].h;},0.02)&&(u5.i-u1.i)>=10)
      found.push({i:u5.i,i2:u1.i,mid:u3.i,n:'三重顶',dir:-1});
    if(u1.tp===-1&&zz[i-3].tp===1&&u3.tp===-1&&zz[i-1].tp===1&&u5.tp===-1
      &&flat([u1,u3,u5],function(p){return d[p.i].l;},0.02)&&(u5.i-u1.i)>=10)
      found.push({i:u5.i,i2:u1.i,mid:u3.i,n:'三重底',dir:1});
  }
  /* 旗形（全序列扫描：旗杆 8 根内涨幅≥8% + 旗面 5+ 根窄幅反漂，防误检用区间收益口径） */
  for(i=13;i<n;i++){
    var poleEnd=i-5;
    var poleRet=d[poleEnd].c/d[i-13].o-1;
    var bodyLo=1e18,bodyHi=-1e18,drift=0;
    for(var k=poleEnd+1;k<=i;k++){bodyLo=Math.min(bodyLo,d[k].l);bodyHi=Math.max(bodyHi,d[k].h);drift+=d[k].c-d[k-1].c;}
    var range=(bodyHi-bodyLo)/d[poleEnd].c;
    if(poleRet>=0.08&&range<=0.05&&drift<0&&drift>-0.06*d[poleEnd].c) found.push({i:i,i2:i-13,mid:poleEnd,n:'多头旗形',dir:1});
    if(poleRet<=-0.08&&range<=0.05&&drift>0&&drift<0.06*d[poleEnd].c) found.push({i:i,i2:i-13,mid:poleEnd,n:'空头旗形',dir:-1});
  }
  return found;
}
/* ---- 图表形态 4 种（fractals zigzag 简化识别：双顶/双底/头肩顶/头肩底），全部匹配位置同时标注 ---- */
function chartPats(d){
  var zz=zigzagPts(d),i;
  var found=[];
  for(i=2;i<zz.length;i++){   /* 三点结构：双顶/双底 */
    var p1=zz[i-2],p2=zz[i-1],p3=zz[i];
    if(p1.tp===1&&p2.tp===-1&&p3.tp===1){
      var h1=d[p1.i].h,h3=d[p3.i].h,vl=d[p2.i].l;
      if(Math.abs(h1-h3)/h1<=0.03&&(p3.i-p1.i)>=8&&(h1-vl)/h1>=0.03)
        found.push({i:p3.i,i2:p1.i,mid:p2.i,n:'双顶',dir:-1});
    }
    if(p1.tp===-1&&p2.tp===1&&p3.tp===-1){
      var l1=d[p1.i].l,l3=d[p3.i].l,vh=d[p2.i].h;
      if(Math.abs(l1-l3)/l1<=0.03&&(p3.i-p1.i)>=8&&(vh-l1)/l1>=0.03)
        found.push({i:p3.i,i2:p1.i,mid:p2.i,n:'双底',dir:1});
    }
  }
  for(i=4;i<zz.length;i++){   /* 五点结构：头肩顶/头肩底 */
    var q1=zz[i-4],q2=zz[i-3],q3=zz[i-2],q4=zz[i-1],q5=zz[i];
    if(q1.tp===1&&q2.tp===-1&&q3.tp===1&&q4.tp===-1&&q5.tp===1){
      var s1=d[q1.i].h,hd=d[q3.i].h,s2=d[q5.i].h,n1=d[q2.i].l,n2=d[q4.i].l;
      if(hd>s1*1.015&&hd>s2*1.015&&Math.abs(s1-s2)/s1<=0.05&&Math.abs(n1-n2)/n1<=0.04&&(q5.i-q1.i)>=15)
        found.push({i:q5.i,i2:q1.i,mid:q3.i,n:'头肩顶',dir:-1});
    }
    if(q1.tp===-1&&q2.tp===1&&q3.tp===-1&&q4.tp===1&&q5.tp===-1){
      var b1=d[q1.i].l,bd=d[q3.i].l,b2=d[q5.i].l,k1=d[q2.i].h,k2=d[q4.i].h;
      if(bd<b1*0.985&&bd<b2*0.985&&Math.abs(b1-b2)/b1<=0.05&&Math.abs(k1-k2)/k1<=0.04&&(q5.i-q1.i)>=15)
        found.push({i:q5.i,i2:q1.i,mid:q3.i,n:'头肩底',dir:1});
    }
  }
  return found;
}
/* ---- I-1 第四批（2026-08-25 子代理产码主会话集成）：CANDLE 族余项 36 条目/49 规则（PAT-CANDLE-015/018/024/027/028/031/035/036/037/038/039/041/043/046/047/055/056/057/058/059/060/061/062/063/064/065/066/067/068/071/072/073/074/075/076/077） ---- */
function patExt3(d){
  var n=d.length,found=[],i,j;
  var avgB=0;
  for(i=0;i<n;i++) avgB+=Math.abs(d[i].c-d[i].o);
  avgB=n?avgB/n:1; if(avgB<=0)avgB=1e-9;
  function an(k){var b=Math.abs(k.c-k.o),r=k.h-k.l;if(r<=0)r=1e-9;return{b:b,r:r,u:k.h-Math.max(k.o,k.c),d:Math.min(k.o,k.c)-k.l};}
  function r5(i){return i>=5&&d[i-5].c>0?d[i].c/d[i-5].c-1:0;}
  var hasV=false;
  for(i=0;i<n;i++){if(typeof d[i].v=='number'){hasV=true;break;}}
  var M5=[],M10=[],M20=[],ATR=[],AV=[];
  for(i=0;i<n;i++){
    var s=0,k;
    if(i>=4){s=0;for(k=i-4;k<=i;k++)s+=d[k].c;M5.push(s/5);}else M5.push(null);
    if(i>=9){s=0;for(k=i-9;k<=i;k++)s+=d[k].c;M10.push(s/10);}else M10.push(null);
    if(i>=19){s=0;for(k=i-19;k<=i;k++)s+=d[k].c;M20.push(s/20);}else M20.push(null);
    if(i>=14){s=0;for(k=i-13;k<=i;k++){var p0=d[k-1].c;s+=Math.max(d[k].h-d[k].l,Math.abs(d[k].h-p0),Math.abs(d[k].l-p0));}ATR.push(s/14);}else ATR.push(null);
    if(hasV&&i>=20){s=0;for(k=i-20;k<i;k++)s+=d[k].v;AV.push(s/20);}else AV.push(null);
  }
  function volOK(i,m){return AV[i]!=null&&typeof d[i].v=='number'?d[i].v>=m*AV[i]:true;}
  function maru(k){var p=an(k);return p.u<=0.05*p.r&&p.d<=0.05*p.r&&p.b>=0.5*avgB;}
  function isCloseMaruY(i){var p=an(d[i]);return d[i].c>d[i].o&&p.b>=0.5*avgB&&p.u<=0.05*p.r;}
  function isCloseMaruN(i){var p=an(d[i]);return d[i].c<d[i].o&&p.b>=0.5*avgB&&p.d<=0.05*p.r;}
  function isTakuri(i){var p=an(d[i]);return r5(i)<=-0.01&&p.b<=0.3*avgB&&p.d>=3*p.b&&p.d>=0.5*p.r&&p.u<=0.1*p.r;}
  function isLongLine(i){var p=an(d[i]);return p.b/p.r>=0.8;}
  function isShortLine(i){var p=an(d[i]);return p.b/p.r<=0.25;}
  function isLimitUpFlat(i){var k=d[i],pc=d[i-1].c;return pc>0&&(k.h-k.l)<=0.001*pc&&k.c>=pc*1.098;}
  function isLimitDnFlat(i){var k=d[i],pc=d[i-1].c;return pc>0&&(k.h-k.l)<=0.001*pc&&k.c<=pc*0.902;}
  function isSkyGround(i){var k=d[i],pc=d[i-1].c;return pc>0&&k.o>=pc*1.02&&k.h>=pc*1.098&&k.c<=pc*0.902;}
  function isGroundSky(i){var k=d[i],pc=d[i-1].c;return pc>0&&k.l<=pc*0.902&&k.c>=pc*1.098&&volOK(i,3);}
  function isYangThruMA(i){
    if(i<20||M5[i-1]==null||M10[i-1]==null||M20[i-1]==null)return false;
    var k=d[i],p=an(k),lo=Math.min(M5[i-1],M10[i-1],M20[i-1]),hi=Math.max(M5[i-1],M10[i-1],M20[i-1]);
    return k.c>k.o&&p.b/p.r>=0.6&&k.o<lo&&k.c>hi;
  }
  function isNR7(i){
    if(i<7)return false;var r=d[i].h-d[i].l;
    for(j=i-6;j<i;j++){if(r>d[j].h-d[j].l)return false;}
    return r>0;
  }
  function isKeyRevTop(i){var a=d[i-1],k=d[i];return r5(i-1)>=0.01&&k.h>a.h&&k.l<a.l&&k.c<a.c&&volOK(i,1.5);}
  function isKeyRevBot(i){var a=d[i-1],k=d[i];return r5(i-1)<=-0.01&&k.h>a.h&&k.l<a.l&&k.c>a.c&&volOK(i,1.5);}
  function isWRB(i){
    if(ATR[i]==null)return false;var p=an(d[i]);
    return p.r>=2*ATR[i]&&p.b/p.r>=0.6;
  }
  function isOopsDown(i){var a=d[i-1],k=d[i];return k.o>a.h&&k.c<=a.h&&k.c>=a.l;}
  function isOopsUp(i){var a=d[i-1],k=d[i];return k.o<a.l&&k.c>=a.l&&k.c<=a.h;}
  function isDojiStarT(i){var a=d[i-1],b=d[i],pb=an(b);return r5(i-1)>=0.01&&a.c>a.o&&(a.c-a.o)>=avgB&&pb.b/pb.r<=0.1&&Math.min(b.o,b.c)>a.c;}
  function isDojiStarB(i){var a=d[i-1],b=d[i],pb=an(b);return r5(i-1)<=-0.01&&a.c<a.o&&(a.o-a.c)>=avgB&&pb.b/pb.r<=0.1&&Math.max(b.o,b.c)<a.c;}
  function isKickBull(i){var a=d[i-1],b=d[i];return a.c<a.o&&maru(a)&&b.c>b.o&&maru(b)&&b.o>a.h;}
  function isKickBear(i){var a=d[i-1],b=d[i];return a.c>a.o&&maru(a)&&b.c<b.o&&maru(b)&&b.o<a.l;}
  function isKickLenBull(i){return isKickBull(i)&&(d[i].c-d[i].o)>(d[i-1].o-d[i-1].c);}
  function isKickLenBear(i){return isKickBear(i)&&(d[i-1].c-d[i-1].o)<(d[i].o-d[i].c);}
  function isHomingPigeon(i){var a=d[i-1],b=d[i];return r5(i)<=-0.01&&a.c<a.o&&(a.o-a.c)>=0.5*avgB&&b.c<b.o&&Math.max(b.o,b.c)<=a.o&&Math.min(b.o,b.c)>=a.c;}
  function isMatchingLow(i){var a=d[i-1],b=d[i];return r5(i)<=-0.01&&a.c<a.o&&(a.o-a.c)>=0.5*avgB&&b.c<b.o&&Math.abs(b.c-a.c)<=0.005*a.c;}
  function isCuoRou(i){
    var a=d[i-1],b=d[i],pa=an(a),pb=an(b);
    if(!(pa.u>=2*pa.b&&pa.b/pa.r<=0.33&&pb.d>=2*pb.b&&pb.b/pb.r<=0.33))return false;
    if(!(Math.max(b.o,b.c)<=a.h&&Math.min(b.o,b.c)>=a.l))return false;
    return Math.abs(r5(i))>=0.01;
  }
  function isIdent3Crows(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c<a.o&&b.c<b.o&&c.c<c.o
      &&(a.o-a.c)>=0.5*avgB&&(b.o-b.c)>=0.5*avgB&&(c.o-c.c)>=0.5*avgB
      &&b.c<a.c&&c.c<b.c&&Math.abs(b.o-a.c)<=0.2*avgB&&Math.abs(c.o-b.c)<=0.2*avgB;
  }
  function is3StarsSouth(i){var a=d[i-2],b=d[i-1],c=d[i],pa=an(a),pb=an(b),pc=an(c);
    return r5(i)<=-0.01
      &&a.c<a.o&&pa.b>=0.5*avgB&&pa.d>pa.b
      &&b.c<b.o&&pb.b<pa.b&&b.o>a.c&&b.l>a.l&&pb.d>0
      &&c.c<c.o&&pc.b<=0.5*pb.b&&c.h<=b.h&&c.l>=b.l&&pc.u<=0.2*pc.r&&pc.d<=0.2*pc.r;
  }
  function isUnique3River(i){var a=d[i-2],b=d[i-1],c=d[i];
    return r5(i)<=-0.01
      &&a.c<a.o&&(a.o-a.c)>=avgB
      &&b.c<b.o&&Math.max(b.o,b.c)<=a.o&&Math.min(b.o,b.c)>=a.c&&b.l<a.l
      &&c.c>c.o&&(c.c-c.o)<=0.6*avgB&&c.c<b.c;
  }
  function isStickSandwich(i){var a=d[i-2],b=d[i-1],c=d[i];
    return r5(i)<=-0.01&&a.c<a.o&&(a.o-a.c)>=0.5*avgB&&b.c>b.o&&c.c<c.o&&Math.abs(c.c-a.c)<=0.2*avgB;
  }
  function isTristarTop(i){var a=d[i-2],b=d[i-1],c=d[i],pa=an(a),pb=an(b),pc=an(c);
    return r5(i)>=0.01&&pa.b/pa.r<=0.1&&pb.b/pb.r<=0.1&&pc.b/pc.r<=0.1&&b.l>Math.max(a.h,c.h);
  }
  function isTristarBot(i){var a=d[i-2],b=d[i-1],c=d[i],pa=an(a),pb=an(b),pc=an(c);
    return r5(i)<=-0.01&&pa.b/pa.r<=0.1&&pb.b/pb.r<=0.1&&pc.b/pc.r<=0.1&&b.h<Math.min(a.l,c.l);
  }
  function isStalled(i){var a=d[i-2],b=d[i-1],c=d[i],pc=an(c);
    return r5(i)>=0.01&&a.c>a.o&&(a.c-a.o)>=0.5*avgB&&b.c>b.o&&(b.c-b.o)>=0.5*avgB&&b.c>a.c
      &&c.c>c.o&&(c.c-c.o)<=0.5*(b.c-b.o)&&Math.abs(c.o-b.c)<=0.3*avgB&&pc.u>=0.3*pc.r;
  }
  function isGap3Up(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c>a.o&&b.c>b.o&&b.o>a.c&&c.c<c.o&&c.o<=b.c&&c.o>=b.o&&c.c<a.c&&c.c>a.o;
  }
  function isGap3Dn(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c<a.o&&b.c<b.o&&b.o<a.c&&c.c>c.o&&c.o>=b.c&&c.o<=b.o&&c.c>a.c&&c.c<a.o;
  }
  function isTasukiUp(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c>a.o&&b.c>b.o&&b.o>a.c&&c.c<c.o&&c.o<=b.c&&c.o>=b.o&&c.c<b.o&&c.c>a.c;
  }
  function isTasukiDn(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c<a.o&&b.c<b.o&&b.o<a.c&&c.c>c.o&&c.o>=b.c&&c.o<=b.o&&c.c>b.o&&c.c<a.c;
  }
  function isLadderBottom(i){var a=d[i-4],b=d[i-3],c=d[i-2],e=d[i-1],f=d[i],pe=an(e);
    return r5(i-4)<=-0.01
      &&a.c<a.o&&b.c<b.o&&c.c<c.o&&b.c<a.c&&c.c<b.c&&b.o<a.o&&c.o<b.o
      &&e.c<e.o&&pe.u>=0.3*pe.r
      &&f.c>f.o&&f.o>e.o;
  }
  function isConcealBaby(i){var a=d[i-3],b=d[i-2],c=d[i-1],e=d[i];
    return r5(i-3)<=-0.01
      &&a.c<a.o&&maru(a)&&b.c<b.o&&maru(b)
      &&c.c<c.o&&c.o<b.c&&c.h>b.c
      &&e.c<e.o&&e.h>=c.h&&e.l<=c.l;
  }
  function isMatHold(i){var a=d[i-4],f=d[i],ba=a.c-a.o;
    if(!(a.c>a.o&&ba>=avgB))return false;
    if(!(f.c>f.o&&(f.c-f.o)>=avgB))return false;
    var b=d[i-3],c=d[i-2],e=d[i-1];
    if(!(f.c>Math.max(a.c,b.c,c.c,e.c)))return false;
    var ks=[b,c,e];
    for(j=0;j<3;j++){if(Math.abs(ks[j].c-ks[j].o)>=0.6*ba)return false;if(ks[j].l<a.o)return false;}
    return b.o>a.c;
  }
  function isBreakawayBot(i){var a=d[i-4],b=d[i-3],c=d[i-2],e=d[i-1],f=d[i];
    return a.c<a.o&&(a.o-a.c)>=avgB&&b.c<b.o&&b.o<a.c
      &&c.c<b.c&&e.c<c.c
      &&f.c>f.o&&(f.c-f.o)>=avgB&&f.c>b.c&&f.c<a.c;
  }
  function isBreakawayTop(i){var a=d[i-4],b=d[i-3],c=d[i-2],e=d[i-1],f=d[i];
    return a.c>a.o&&(a.c-a.o)>=avgB&&b.c>b.o&&b.o>a.c
      &&c.c>b.c&&e.c>c.c
      &&f.c<f.o&&(f.o-f.c)>=avgB&&f.c<b.c&&f.c>a.c;
  }
  function isHikkakeBull(i){
    var t,s;
    for(t=i-2;t>=Math.max(1,i-4);t--){
      if(!(d[t].h<=d[t-1].h&&d[t].l>=d[t-1].l))continue;
      for(s=t+1;s<i;s++){if(d[s].c<d[t].l&&d[i].c>d[t].h)return true;}
    }
    return false;
  }
  function isHikkakeBear(i){
    var t,s;
    for(t=i-2;t>=Math.max(1,i-4);t--){
      if(!(d[t].h<=d[t-1].h&&d[t].l>=d[t-1].l))continue;
      for(s=t+1;s<i;s++){if(d[s].c>d[t].h&&d[i].c<d[t].l)return true;}
    }
    return false;
  }
  function isHikkakeModBull(i){
    var t,s,mx,brk;
    for(t=i-2;t>=Math.max(1,i-4);t--){
      if(!(d[t].h<=d[t-1].h&&d[t].l>=d[t-1].l))continue;
      mx=d[t].h;brk=false;
      for(s=t+1;s<i;s++){if(d[s].c<d[t].l)brk=true;if(d[s].h>mx)mx=d[s].h;}
      if(brk&&d[i].c>mx)return true;
    }
    return false;
  }
  function isHikkakeModBear(i){
    var t,s,mn,brk;
    for(t=i-2;t>=Math.max(1,i-4);t--){
      if(!(d[t].h<=d[t-1].h&&d[t].l>=d[t-1].l))continue;
      mn=d[t].l;brk=false;
      for(s=t+1;s<i;s++){if(d[s].c>d[t].h)brk=true;if(d[s].l<mn)mn=d[s].l;}
      if(brk&&d[i].c<mn)return true;
    }
    return false;
  }
  function isSankuUp(i){
    var g=[],m,filled;
    for(j=Math.max(1,i-8);j<=i-1;j++){
      if(d[j].l>=d[j-1].h*1.003){
        filled=false;
        for(m=j+1;m<=i-1;m++){if(d[m].l<=d[j-1].h){filled=true;break;}}
        if(!filled)g.push(j);
      }
    }
    return g.length>=3&&g[g.length-1]===(i-1)&&d[i].c<d[i].o;
  }
  function isSankuDn(i){
    var g=[],m,filled;
    for(j=Math.max(1,i-8);j<=i-1;j++){
      if(d[j].h<=d[j-1].l*0.997){
        filled=false;
        for(m=j+1;m<=i-1;m++){if(d[m].h>=d[j-1].l){filled=true;break;}}
        if(!filled)g.push(j);
      }
    }
    return g.length>=3&&g[g.length-1]===(i-1)&&d[i].c>d[i].o;
  }
  function isTowerTop(i){
    var a=d[i-4],e=d[i],pa=an(a),pe=an(e),mid=(a.o+a.c)/2;
    if(!(a.c>a.o&&pa.b>=avgB&&pa.b/pa.r>=0.7))return false;
    if(!(e.c<e.o&&pe.b>=avgB&&pe.b/pe.r>=0.6))return false;
    for(j=i-3;j<=i-1;j++){var q=d[j];if(q.h-q.l>0.5*pa.r)return false;if(q.l<mid)return false;}
    return e.c<mid&&r5(i-4)>=0;
  }
  function isTowerBot(i){
    var a=d[i-4],e=d[i],pa=an(a),pe=an(e),mid=(a.o+a.c)/2;
    if(!(a.c<a.o&&pa.b>=avgB&&pa.b/pa.r>=0.7))return false;
    if(!(e.c>e.o&&pe.b>=avgB&&pe.b/pe.r>=0.6))return false;
    for(j=i-3;j<=i-1;j++){var q=d[j];if(q.h-q.l>0.5*pa.r)return false;if(q.h>mid)return false;}
    return e.c>mid&&r5(i-4)<=0;
  }
  for(i=4;i<n;i++){
    if(isCloseMaruY(i)) found.push({i:i,n:'收盘光头光脚线',dir:1});
    if(isCloseMaruN(i)) found.push({i:i,n:'收盘光头光脚线',dir:-1});
    if(isTakuri(i)) found.push({i:i,n:'探水竿',dir:1});
    if(isDojiStarT(i)) found.push({i:i,n:'十字星组合',dir:-1});
    if(isDojiStarB(i)) found.push({i:i,n:'十字星组合',dir:1});
    if(isKickBull(i)) found.push({i:i,n:'反冲双胞胎',dir:1});
    if(isKickBear(i)) found.push({i:i,n:'反冲双胞胎',dir:-1});
    if(isKickLenBull(i)) found.push({i:i,n:'长度反冲',dir:1});
    if(isKickLenBear(i)) found.push({i:i,n:'长度反冲',dir:-1});
    if(isIdent3Crows(i)) found.push({i:i,n:'同款三乌鸦',dir:-1});
    if(is3StarsSouth(i)) found.push({i:i,n:'南方三星',dir:1});
    if(isUnique3River(i)) found.push({i:i,n:'独特三河底',dir:1});
    if(isLadderBottom(i)) found.push({i:i,n:'阶梯底',dir:1});
    if(isStickSandwich(i)) found.push({i:i,n:'条形三明治',dir:1});
    if(isTristarTop(i)) found.push({i:i,n:'三星形态',dir:-1});
    if(isTristarBot(i)) found.push({i:i,n:'三星形态',dir:1});
    if(isConcealBaby(i)) found.push({i:i,n:'藏燕吞没',dir:1});
    if(isStalled(i)) found.push({i:i,n:'停滞形态',dir:-1});
    if(isHomingPigeon(i)) found.push({i:i,n:'归鸽',dir:1});
    if(isMatchingLow(i)) found.push({i:i,n:'相抵双阳',dir:1});
    if(isMatHold(i)) found.push({i:i,n:'垫形整理',dir:1});
    if(isBreakawayBot(i)) found.push({i:i,n:'脱离形态',dir:1});
    if(isBreakawayTop(i)) found.push({i:i,n:'脱离形态',dir:-1});
    if(isGap3Up(i)) found.push({i:i,n:'跳空三法',dir:1});
    if(isGap3Dn(i)) found.push({i:i,n:'跳空三法',dir:-1});
    if(isTasukiUp(i)) found.push({i:i,n:'兔跳缺口',dir:1});
    if(isTasukiDn(i)) found.push({i:i,n:'兔跳缺口',dir:-1});
    if(isHikkakeBull(i)) found.push({i:i,n:'日垣陷阱',dir:1});
    if(isHikkakeBear(i)) found.push({i:i,n:'日垣陷阱',dir:-1});
    if(isHikkakeModBull(i)) found.push({i:i,n:'日垣修正陷阱',dir:1});
    if(isHikkakeModBear(i)) found.push({i:i,n:'日垣修正陷阱',dir:-1});
    if(isLongLine(i)) found.push({i:i,n:'长线',dir:d[i].c>=d[i].o?1:-1});
    if(isShortLine(i)) found.push({i:i,n:'短线',dir:0});
    if(isLimitUpFlat(i)) found.push({i:i,n:'一字涨停板',dir:1});
    if(isLimitDnFlat(i)) found.push({i:i,n:'一字跌停板',dir:-1});
    if(isCuoRou(i)) found.push({i:i,n:'搓揉线',dir:r5(i)>=0.01?-1:1});
    if(isSkyGround(i)) found.push({i:i,n:'天地板',dir:-1});
    if(isGroundSky(i)) found.push({i:i,n:'地天板',dir:1});
    if(isYangThruMA(i)) found.push({i:i,n:'一阳穿多线',dir:1});
    if(isNR7(i)) found.push({i:i,n:'窄幅整理日',dir:0});
    if(isKeyRevTop(i)) found.push({i:i,n:'关键反转日（外包反转）',dir:-1});
    if(isKeyRevBot(i)) found.push({i:i,n:'关键反转日（外包反转）',dir:1});
    if(isWRB(i)) found.push({i:i,n:'宽幅推进K线',dir:d[i].c>=d[i].o?1:-1});
    if(isOopsDown(i)) found.push({i:i,n:'跳空反向陷阱',dir:-1});
    if(isOopsUp(i)) found.push({i:i,n:'跳空反向陷阱',dir:1});
    if(isSankuUp(i)) found.push({i:i,n:'三空（酒田五法）',dir:-1});
    if(isSankuDn(i)) found.push({i:i,n:'三空（酒田五法）',dir:1});
    if(isTowerTop(i)) found.push({i:i,n:'塔形顶',dir:-1});
    if(isTowerBot(i)) found.push({i:i,n:'塔形底',dir:1});
  }
  return found;
}
/* ---- I-1 第四批：CHART 西方经典族 30 规则（PAT-CHART-003/012/013/014/019/020/021/022/023/024/025/026/039/040/041/042/043/044/045/046/047/048/049/050/051/057/058/059/060/061） ---- */
function chartPats3(d){
  var n=d.length,found=[],i,j,k;
  var zz=zigzagPts(d);
  function slope(arr,acc){
    var m=arr.length;if(m<3)return 0;
    var sx=0,sy=0,sxy=0,sxx=0;
    for(var q=0;q<m;q++){var v=acc(arr[q]);sx+=q;sy+=v;sxy+=q*v;sxx+=q*q;}
    var den=m*sxx-sx*sx; if(!den)return 0;
    return (m*sxy-sx*sy)/den;
  }
  function flat(arr,acc,tol){var vs=arr.map(acc),mn=Math.min.apply(null,vs),mx=Math.max.apply(null,vs);return mn>0&&(mx-mn)/mn<=tol;}
  function zpr(p){return p.tp===1?d[p.i].h:d[p.i].l;}
  function maxH(a,b){var r=-1e18;a=Math.max(0,a);b=Math.min(n-1,b);for(var q=a;q<=b;q++)r=Math.max(r,d[q].h);return r;}
  function minL(a,b){var r=1e18;a=Math.max(0,a);b=Math.min(n-1,b);for(var q=a;q<=b;q++)r=Math.min(r,d[q].l);return r;}
  function avgRg(a,b){var s=0,c=0;a=Math.max(0,a);b=Math.min(n-1,b);for(var q=a;q<=b;q++){s+=d[q].h-d[q].l;c++;}return c?s/c:0;}
  function volA(a,b){var s=0,c=0;a=Math.max(0,a);b=Math.min(n-1,b);for(var q=a;q<=b;q++){if(d[q].v===undefined)return null;s+=d[q].v;c++;}return c?s/c:null;}
  function push1(o){for(var q=0;q<found.length;q++)if(found[q].n===o.n&&found[q].i===o.i)return;found.push(o);}
  for(i=5;i<zz.length;i++){
    var seg=zz.slice(i-5,i+1);
    var tops=seg.filter(function(p){return p.tp===1;}),bots=seg.filter(function(p){return p.tp===-1;});
    if(tops.length<2||bots.length<2)continue;
    var tS=slope(tops,function(p){return d[p.i].h;}),bS=slope(bots,function(p){return d[p.i].l;});
    var ref=d[seg[5].i].c,eps=ref*0.0015;
    var bb1=bots[bots.length-2],bb2=bots[bots.length-1],tt1=tops[tops.length-2],tt2=tops[tops.length-1];
    var end=seg[5].i,lim=Math.min(n-1,end+10);
    if(tS>eps&&bS>tS*1.3){
      var railS=(d[bb2.i].l-d[bb1.i].l)/(bb2.i-bb1.i);
      for(j=end+1;j<=lim;j++){
        if(d[j].c<d[bb2.i].l+railS*(j-bb2.i)){push1({i:j,i2:seg[0].i,mid:seg[2].i,n:'楔形破位',dir:-1});break;}
      }
    }else if(tS<-eps&&bS<0&&bS>tS){
      var railS2=(d[tt2.i].h-d[tt1.i].h)/(tt2.i-tt1.i);
      for(j=end+1;j<=lim;j++){
        if(d[j].c>d[tt2.i].h+railS2*(j-tt2.i)){push1({i:j,i2:seg[0].i,mid:seg[2].i,n:'楔形破位',dir:1});break;}
      }
    }
  }
  for(i=12;i<n;i++){
    for(var fl=4;fl<=8;fl++){
      var pe=i-fl;if(pe<1)break;
      var ps=Math.max(0,pe-8);
      var pr1=d[pe].c/d[ps].o-1;
      if(Math.abs(pr1)<0.10)continue;
      var hf=Math.floor(fl/2);
      var hA=maxH(pe+1,pe+hf),hB=maxH(pe+hf+1,i);
      var lA=minL(pe+1,pe+hf),lB=minL(pe+hf+1,i);
      if(hB<hA*0.995&&lB>lA*1.005&&(hA-lA)/d[pe].c<=0.06){
        push1({i:i,i2:ps,mid:pe,n:'三角旗',dir:pr1>0?1:-1});
        break;
      }
    }
  }
  for(i=3;i<zz.length;i++){
    var c1=zz[i-3],c2=zz[i-2],c3=zz[i-1],c4=zz[i];
    if(c1.tp===1&&c2.tp===-1&&c3.tp===1&&c4.tp===-1){
      var r1=d[c1.i].h,r2=d[c3.i].h,cb=d[c2.i].l;
      var rim=(r1+r2)/2,dep=(rim-cb)/rim;
      if(Math.abs(r1-r2)/r1<=0.05&&dep>=0.08&&dep<=0.33&&(c3.i-c1.i)>=20){
        var loI=c1.i,loV=1e18;
        for(j=c1.i;j<=c3.i;j++){if(d[j].l<loV){loV=d[j].l;loI=j;}}
        var pos=(loI-c1.i)/(c3.i-c1.i);
        var hd=(r2-d[c4.i].l)/(rim-cb);
        if(pos>=0.25&&pos<=0.75&&hd>0&&hd<=0.40&&d[c4.i].l>cb)
          push1({i:c4.i,i2:c1.i,mid:c2.i,n:'杯柄形',dir:1});
      }
    }
    if(c1.tp===-1&&c2.tp===1&&c3.tp===-1&&c4.tp===1){
      var e1=d[c1.i].l,e2=d[c3.i].l,ct=d[c2.i].h;
      var rim2=(e1+e2)/2,hgt=(ct-rim2)/rim2;
      if(Math.abs(e1-e2)/e1<=0.05&&hgt>=0.08&&hgt<=0.33&&(c3.i-c1.i)>=20){
        var hiI=c1.i,hiV=-1e18;
        for(j=c1.i;j<=c3.i;j++){if(d[j].h>hiV){hiV=d[j].h;hiI=j;}}
        var pos2=(hiI-c1.i)/(c3.i-c1.i);
        var hb=(d[c4.i].h-e2)/(ct-rim2);
        if(pos2>=0.25&&pos2<=0.75&&hb>0&&hb<=0.40&&d[c4.i].h<ct)
          push1({i:c4.i,i2:c1.i,mid:c2.i,n:'倒杯柄形',dir:-1});
      }
    }
  }
  var WL=[24,36,48];
  for(var wi=0;wi<3;wi++){
    var LN=WL[wi],qp=Math.floor(LN/4);
    for(i=LN-1;i<n;i+=2){
      var st=i-LN+1,m0=0,m1=0,m2=0,m3=0,c0=0,cc1=0,cc2=0,c3=0;
      for(j=0;j<LN;j++){
        var gg=Math.min(3,Math.floor(j/qp));
        if(gg===0){m0+=d[st+j].c;c0++;}else if(gg===1){m1+=d[st+j].c;cc1++;}
        else if(gg===2){m2+=d[st+j].c;cc2++;}else{m3+=d[st+j].c;c3++;}
      }
      m0/=c0;m1/=cc1;m2/=cc2;m3/=c3;
      var rUp=(m1-m0)/m0,rDn=(m2-m3)/m2;
      if(m1>m0&&m2>=m1*0.995&&m3<m2&&rUp>=0.02&&rUp<=0.15&&rDn>0&&Math.abs(rUp-rDn)/rUp<=0.6)
        push1({i:i,i2:st,mid:st+Math.floor(LN/2),n:'圆弧顶',dir:-1});
      var bDn=(m0-m1)/m1,bUp=(m3-m2)/m3;
      if(m1<m0&&m2<=m1*1.005&&m3>m2&&bDn>=0.02&&bDn<=0.15&&bUp>0&&Math.abs(bDn-bUp)/bDn<=0.6)
        push1({i:i,i2:st,mid:st+Math.floor(LN/2),n:'圆弧底',dir:1});
    }
  }
  for(i=5;i<zz.length;i++){
    var sg6=zz.slice(i-5,i+1);
    var tp6=sg6.filter(function(p){return p.tp===1;}),bt6=sg6.filter(function(p){return p.tp===-1;});
    if(tp6.length<2||bt6.length<2)continue;
    var tS6=slope(tp6,function(p){return d[p.i].h;}),bS6=slope(bt6,function(p){return d[p.i].l;});
    var rf6=d[sg6[5].i].c,ep6=rf6*0.0015;
    if(tS6>ep6&&bS6<-ep6
      &&(d[tp6[tp6.length-1].i].h-d[tp6[0].i].h)/d[tp6[0].i].h>=0.01
      &&(d[bt6[0].i].l-d[bt6[bt6.length-1].i].l)/d[bt6[0].i].l>=0.01)
      push1({i:sg6[5].i,i2:sg6[0].i,mid:sg6[2].i,n:'扩散喇叭形',dir:0});
  }
  for(i=7;i<zz.length;i++){
    var dm=zz.slice(i-7,i+1);
    var dtp=dm.filter(function(p){return p.tp===1;}),dbt=dm.filter(function(p){return p.tp===-1;});
    if(dtp.length!==4||dbt.length!==4)continue;
    var dh0=d[dtp[0].i].h,dh1=d[dtp[1].i].h,dh2=d[dtp[2].i].h,dh3=d[dtp[3].i].h;
    var dl0=d[dbt[0].i].l,dl1=d[dbt[1].i].l,dl2=d[dbt[2].i].l,dl3=d[dbt[3].i].l;
    if(!(dh1>dh0&&dh2>=dh1*0.99&&dh3<dh2&&dl1<dl0&&dl2<=dl1*1.01&&dl3>dl2))continue;
    var wide=(Math.max(dh1,dh2)-Math.min(dl1,dl2))/d[dm[4].i].c;
    if(wide<0.04)continue;
    push1({i:dm[7].i,i2:dm[0].i,mid:dm[4].i,n:'钻石形',dir:0});
  }
  for(i=10;i<n-3;i++){
    if(d[i].h>=maxH(i-10,i-1)&&d[i].h>=maxH(i+1,Math.min(n-1,i+10))){
      var li=i,lw=1e18;for(j=Math.max(0,i-10);j<i;j++){if(d[j].l<lw){lw=d[j].l;li=j;}}
      var ri=-1,rw=1e18;for(j=i+1;j<=Math.min(n-1,i+10);j++){if(d[j].l<rw){rw=d[j].l;ri=j;}}
      if(ri>0&&i-li>=2&&ri-i>=2&&(d[i].h-lw)/lw>=0.12&&(d[i].h-rw)/d[i].h>=0.12)
        push1({i:ri,i2:li,mid:i,n:'V形顶',dir:-1});
    }
    if(d[i].l<=minL(i-10,i-1)&&d[i].l<=minL(i+1,Math.min(n-1,i+10))){
      var hi2=i,hh2=-1e18;for(j=Math.max(0,i-10);j<i;j++){if(d[j].h>hh2){hh2=d[j].h;hi2=j;}}
      var ri2=-1,rw2=-1e18;for(j=i+1;j<=Math.min(n-1,i+10);j++){if(d[j].h>rw2){rw2=d[j].h;ri2=j;}}
      if(ri2>0&&i-hi2>=2&&ri2-i>=2&&(hh2-d[i].l)/hh2>=0.12&&(rw2-d[i].l)/d[i].l>=0.12)
        push1({i:ri2,i2:hi2,mid:i,n:'V形底',dir:1});
    }
  }
  for(i=2;i<n-1;i++){
    if(d[i].l>d[i-1].h*1.005){
      var islLo=d[i].l;
      for(j=i+1;j<=Math.min(n-1,i+3);j++){
        if(d[j].h<d[j-1].l*0.995&&d[j].h<islLo&&islLo>d[i-1].h){
          push1({i:j,i2:i-1,mid:Math.floor((i+j-1)/2),n:'岛形反转',dir:-1});
          break;
        }
        islLo=Math.min(islLo,d[j].l);
      }
    }
    if(d[i].h<d[i-1].l*0.995){
      var islHi=d[i].h;
      for(j=i+1;j<=Math.min(n-1,i+3);j++){
        if(d[j].l>d[j-1].h*1.005&&d[j].l>islHi&&islHi<d[i-1].l){
          push1({i:j,i2:i-1,mid:Math.floor((i+j-1)/2),n:'岛形反转',dir:1});
          break;
        }
        islHi=Math.max(islHi,d[j].h);
      }
    }
  }
  for(i=12;i<n-3;i++){
    if(d[i].l>minL(i-3,i-1)||d[i].l>minL(i+1,i+3))continue;
    var hiA=-1e18,hiI=i;
    for(j=Math.max(0,i-12);j<i;j++){if(d[j].h>hiA){hiA=d[j].h;hiI=j;}}
    var drp=(hiA-d[i].l)/hiA;if(drp<0.15)continue;
    var bh=-1e18,bi=-1;
    for(j=i+1;j<=Math.min(n-1,i+8);j++){if(d[j].h>bh){bh=d[j].h;bi=j;}}
    var rt=(bh-d[i].l)/(hiA-d[i].l);
    if(bi>0&&rt>=0.15&&rt<=0.5)push1({i:bi,i2:hiI,mid:i,n:'死猫跳',dir:-1});
  }
  for(i=4;i<zz.length;i++){
    var w1=zz[i-4],w2=zz[i-3],w3=zz[i-2],w4=zz[i-1],w5=zz[i];
    if(w5.i-w1.i<10)continue;
    if(w1.tp===-1&&w2.tp===1&&w3.tp===-1&&w4.tp===1&&w5.tp===-1){
      var wl1=d[w1.i].l,wl3=d[w3.i].l,wl5=d[w5.i].l;
      if(wl3<wl1&&wl5<wl3){
        var v13=wl1+(wl3-wl1)*(w5.i-w1.i)/(w3.i-w1.i);
        if(wl5<=v13*1.03&&wl5>=v13*0.94&&d[w4.i].h<d[w2.i].h)
          push1({i:w5.i,i2:w1.i,mid:w3.i,n:'沃尔夫浪',dir:1});
      }
    }
    if(w1.tp===1&&w2.tp===-1&&w3.tp===1&&w4.tp===-1&&w5.tp===1){
      var wh1=d[w1.i].h,wh3=d[w3.i].h,wh5=d[w5.i].h;
      if(wh3>wh1&&wh5>wh3){
        var v13b=wh1+(wh3-wh1)*(w5.i-w1.i)/(w3.i-w1.i);
        if(wh5>=v13b*0.97&&wh5<=v13b*1.06&&d[w4.i].l>d[w2.i].l)
          push1({i:w5.i,i2:w1.i,mid:w3.i,n:'沃尔夫浪',dir:-1});
      }
    }
  }
  for(i=3;i<zz.length;i++){
    var q1=zz[i-3],q2=zz[i-2],q3=zz[i-1],q4=zz[i];
    if(q1.tp===-1&&q2.tp===1&&q3.tp===-1&&q4.tp===1
      &&d[q3.i].l>d[q1.i].l&&d[q4.i].h>d[q2.i].h){
      for(j=q4.i+1;j<Math.min(n,q4.i+21);j++){
        if(d[j].c<d[q3.i].l){push1({i:j,i2:q1.i,mid:q4.i,n:'卡西莫多反转',dir:-1});break;}
      }
    }
    if(q1.tp===1&&q2.tp===-1&&q3.tp===1&&q4.tp===-1
      &&d[q3.i].h<d[q1.i].h&&d[q4.i].l<d[q2.i].l){
      for(j=q4.i+1;j<Math.min(n,q4.i+21);j++){
        if(d[j].c>d[q3.i].h){push1({i:j,i2:q1.i,mid:q4.i,n:'卡西莫多反转',dir:1});break;}
      }
    }
  }
  for(i=5;i<zz.length;i++){
    var s1=zz[i-5],s2=zz[i-4],s3=zz[i-3],s4=zz[i-2],s5=zz[i-1],s6=zz[i];
    if(s1.tp===-1&&s2.tp===1&&s3.tp===-1&&s4.tp===1&&s5.tp===-1&&s6.tp===1){
      var L1=d[s1.i].l,H1=d[s2.i].h,L2=d[s3.i].l,H2=d[s4.i].h,L3=d[s5.i].l,H3=d[s6.i].h;
      if(L2>L1&&L3>L2&&H2>H1&&H3>H2
        &&(H1-L2)<=(H1-L1)*0.45&&(H2-L3)<=(H2-L2)*0.45)
        push1({i:s6.i,i2:s1.i,mid:s3.i,n:'上升扇贝',dir:1});
    }
    if(s1.tp===1&&s2.tp===-1&&s3.tp===1&&s4.tp===-1&&s5.tp===1&&s6.tp===-1){
      var uH1=d[s1.i].h,uL1=d[s2.i].l,uH2=d[s3.i].h,uL2=d[s4.i].l,uH3=d[s5.i].h,uL3=d[s6.i].l;
      if(uH2<uH1&&uH3<uH2&&uL2<uL1&&uL3<uL2
        &&(uH2-uL1)<=(uH1-uL1)*0.45&&(uH3-uL2)<=(uH2-uL2)*0.45)
        push1({i:s6.i,i2:s1.i,mid:s3.i,n:'下降扇贝',dir:-1});
    }
  }
  for(i=4;i<zz.length;i++){
    var g1=zz[i-4],g2=zz[i-3],g3=zz[i-2],g4=zz[i-1],g5=zz[i];
    var ar=avgRg(Math.max(0,g1.i-20),g5.i);
    if(g1.tp===1&&g2.tp===-1&&g3.tp===1&&g4.tp===-1&&g5.tp===1){
      var pH1=d[g1.i].h,pH2=d[g3.i].h,pH3=d[g5.i].h;
      if(Math.abs(pH1-pH3)/pH1<=0.02&&pH2<=pH1*0.98
        &&g3.i-g1.i>=5&&g5.i-g3.i>=5
        &&(d[g1.i].h-d[g1.i].l)>=ar*1.5&&(d[g5.i].h-d[g5.i].l)>=ar*1.5)
        push1({i:g5.i,i2:g1.i,mid:g3.i,n:'牛角顶',dir:-1});
    }
    if(g1.tp===-1&&g2.tp===1&&g3.tp===-1&&g4.tp===1&&g5.tp===-1){
      var pL1=d[g1.i].l,pL2=d[g3.i].l,pL3=d[g5.i].l;
      if(Math.abs(pL1-pL3)/pL1<=0.02&&pL2>=pL1*1.02
        &&g3.i-g1.i>=5&&g5.i-g3.i>=5
        &&(d[g1.i].h-d[g1.i].l)>=ar*1.5&&(d[g5.i].h-d[g5.i].l)>=ar*1.5)
        push1({i:g5.i,i2:g1.i,mid:g3.i,n:'牛角底',dir:1});
    }
  }
  for(i=13;i<n;i++){
    var ar2=avgRg(i-12,i-2);
    if(Math.abs(d[i].h-d[i-1].h)/d[i].h<=0.005
      &&(d[i].h-d[i].l)>=ar2*1.5&&(d[i-1].h-d[i-1].l)>=ar2*1.5
      &&d[i].h>=maxH(i-12,i-2)&&d[i].c/d[i-11].o-1>=0.10)
      push1({i:i,i2:i-11,mid:i-1,n:'管道顶',dir:-1});
    if(Math.abs(d[i].l-d[i-1].l)/d[i].l<=0.005
      &&(d[i].h-d[i].l)>=ar2*1.5&&(d[i-1].h-d[i-1].l)>=ar2*1.5
      &&d[i].l<=minL(i-12,i-2)&&d[i].c/d[i-11].o-1<=-0.10)
      push1({i:i,i2:i-11,mid:i-1,n:'管道底',dir:1});
  }
  for(i=0;i<zz.length;i++){
    var pk=zz[i];
    if(pk.i<35)continue;
    var a0=pk.i-30,b0=pk.i-15;
    if(pk.tp===1){
      var sl1=(d[b0].c-d[a0].c)/(b0-a0);
      if(sl1<=0||sl1>d[a0].c*0.003)continue;
      var bmp=d[pk.i].h-d[b0].c,ldn=d[b0].c-d[a0].c;
      if(bmp/(pk.i-b0)<sl1*1.5||bmp<ldn*2)continue;
      for(j=pk.i+1;j<Math.min(n,pk.i+21);j++){
        if(d[j].c<d[a0].c+sl1*(j-a0)){push1({i:j,i2:a0,mid:pk.i,n:'冲高回撤反转顶',dir:-1});break;}
      }
    }else{
      var sl2=(d[b0].c-d[a0].c)/(b0-a0);
      if(sl2>=0||-sl2>d[a0].c*0.003)continue;
      var bmp2=d[b0].c-d[pk.i].l,ldn2=d[a0].c-d[b0].c;
      if(bmp2/(pk.i-b0)<-sl2*1.5||bmp2<ldn2*2)continue;
      for(j=pk.i+1;j<Math.min(n,pk.i+21);j++){
        if(d[j].c>d[a0].c+sl2*(j-a0)){push1({i:j,i2:a0,mid:pk.i,n:'冲高回撤反转底',dir:1});break;}
      }
    }
  }
  for(i=4;i<zz.length;i++){
    var A1=Math.abs(zpr(zz[i-3])-zpr(zz[i-4])),A2=Math.abs(zpr(zz[i-2])-zpr(zz[i-3]));
    var A3=Math.abs(zpr(zz[i-1])-zpr(zz[i-2])),A4=Math.abs(zpr(zz[i])-zpr(zz[i-1]));
    if(!(A1>0&&A2<=A1*0.75&&A3<=A2*0.75&&A4<=A3*0.75))continue;
    if(A4/zpr(zz[i])>0.05)continue;
    var vF=volA(zz[i-4].i,zz[i-2].i),vL=volA(zz[i-2].i,zz[i].i);
    if(vF!==null&&vL!==null&&vL>=vF)continue;
    push1({i:zz[i].i,i2:zz[i-4].i,mid:zz[i-2].i,n:'波动收缩形态',dir:1});
  }
  for(i=2;i<zz.length;i++){
    var f1=zz[i-2],f2=zz[i-1],f3=zz[i];
    if(f1.tp===-1&&f2.tp===1&&f3.tp===-1){
      var lo1=d[f1.i].l,hh3=d[f2.i].h,lo3=d[f3.i].l;
      if(lo3>lo1&&(hh3-lo3)<=(hh3-lo1)*0.786&&(f3.i-f1.i)>=6){
        for(j=f3.i+1;j<Math.min(n,f3.i+21);j++){
          if(d[j].c>hh3){push1({i:j,i2:f1.i,mid:f2.i,n:'一二三反转',dir:1});break;}
          if(d[j].c<lo3)break;
        }
      }
    }
    if(f1.tp===1&&f2.tp===-1&&f3.tp===1){
      var fh1=d[f1.i].h,fl2=d[f2.i].l,fh3=d[f3.i].h;
      if(fh3<fh1&&(fh3-fl2)<=(fh1-fl2)*0.786&&(f3.i-f1.i)>=6){
        for(j=f3.i+1;j<Math.min(n,f3.i+21);j++){
          if(d[j].c<fl2){push1({i:j,i2:f1.i,mid:f2.i,n:'一二三反转',dir:-1});break;}
          if(d[j].c>fh3)break;
        }
      }
    }
  }
  for(i=4;i<zz.length;i++){
    var k1=zz[i-4],k2=zz[i-3],k3=zz[i-2],k4=zz[i-1],k5=zz[i];
    if(k5.i-k1.i>40)continue;
    if(k1.tp===-1&&k2.tp===1&&k3.tp===-1&&k4.tp===1&&k5.tp===-1){
      if(d[k3.i].l>d[k1.i].l&&d[k4.i].h>d[k2.i].h&&d[k5.i].l>d[k3.i].l*0.98)
        push1({i:k5.i,i2:k1.i,mid:k4.i,n:'罗斯钩',dir:1});
    }
    if(k1.tp===1&&k2.tp===-1&&k3.tp===1&&k4.tp===-1&&k5.tp===1){
      if(d[k3.i].h<d[k1.i].h&&d[k4.i].l<d[k2.i].l&&d[k5.i].h<d[k3.i].h*1.02)
        push1({i:k5.i,i2:k1.i,mid:k4.i,n:'罗斯钩',dir:-1});
    }
  }
  for(i=2;i<zz.length;i++){
    var W1=zz[i-2],W2=zz[i-1],W3=zz[i];
    if(W3.i-W1.i<30)continue;
    if(W1.tp===-1&&W2.tp===1&&W3.tp===-1){
      var bl1=d[W1.i].l,bl3=d[W3.i].l,bnk=d[W2.i].h;
      if(Math.abs(bl1-bl3)/bl1<=0.05&&(bnk-Math.max(bl1,bl3))/bnk>=0.05){
        var lwg=maxH(W1.i-20,W1.i-1);
        if((lwg-bl1)/lwg>=0.15){
          for(j=W3.i+1;j<Math.min(n,W3.i+26);j++){
            if(d[j].c>=bl3+(bnk-bl3)*0.5){push1({i:j,i2:W1.i,mid:W2.i,n:'大W底',dir:1});break;}
          }
        }
      }
    }
    if(W1.tp===1&&W2.tp===-1&&W3.tp===1){
      var th1=d[W1.i].h,th3=d[W3.i].h,tvl=d[W2.i].l;
      if(Math.abs(th1-th3)/th1<=0.05&&(Math.min(th1,th3)-tvl)/th1>=0.05){
        var lwl=minL(W1.i-20,W1.i-1);
        if((th1-lwl)/lwl>=0.15){
          for(j=W3.i+1;j<Math.min(n,W3.i+26);j++){
            if(d[j].c<=th3-(th3-tvl)*0.5){push1({i:j,i2:W1.i,mid:W2.i,n:'大M顶',dir:-1});break;}
          }
        }
      }
    }
  }
  for(j=1;j<n;j++){
    var gu=d[j].l>d[j-1].h*1.005,gd=d[j].h<d[j-1].l*0.995;
    if(!gu&&!gd)continue;
    var gdir=gu?1:-1,fill3=false,fill5=false;
    for(k=j+1;k<=Math.min(n-1,j+5);k++){
      var filled=gu?(d[k].l<=d[j-1].h):(d[k].h>=d[j-1].l);
      if(filled){if(k-j<=3)fill3=true;fill5=true;break;}
    }
    var nn=null,dd=gdir;
    if(fill3){
      var mv=j>20?(d[j-1].c/d[j-20].c-1):0;
      if(gdir===1&&mv>=0.12){nn='缺口·衰竭型';dd=-1;}
      else if(gdir===-1&&mv<=-0.12){nn='缺口·衰竭型';dd=1;}
      else nn='缺口·普通型';
    }else if(!fill5){
      var r0=Math.max(0,j-15);
      var rh=maxH(r0,j-1),rl=minL(r0,j-1),rr=(rh-rl)/d[j-1].c;
      var mv2=j>10?(d[j-1].c/d[j-10].c-1):0;
      var vb=volA(j-20,j-1);
      if(rr<=0.08&&((gu&&d[j].l>rh)||(gd&&d[j].h<rl))
        &&(vb===null||d[j].v===undefined||d[j].v>=vb*1.5))nn='缺口·突破型';
      else if(gdir===1&&mv2>=0.06)nn='缺口·逃逸型';
      else if(gdir===-1&&mv2<=-0.06)nn='缺口·逃逸型';
      else nn='缺口·普通型';
    }
    if(nn)push1({i:j,i2:j-1,mid:j,n:nn,dir:dd});
  }
  for(i=8;i<zz.length;i++){
    var cx=zz.slice(i-8,i+1),okT=true,okB=true;
    for(k=0;k<9;k++){
      if(cx[k].tp!==(k%2===0?1:-1))okT=false;
      if(cx[k].tp!==(k%2===0?-1:1))okB=false;
    }
    if(okT){
      var x1=d[cx[0].i].h,x2=d[cx[2].i].h,xh=d[cx[4].i].h,x3=d[cx[6].i].h,x4=d[cx[8].i].h;
      var xls=(x1+x2)/2,xrs=(x3+x4)/2;
      if(xh>x1*1.015&&xh>x2*1.015&&xh>x3*1.015&&xh>x4*1.015
        &&Math.abs(x1-x2)/x1<=0.05&&Math.abs(x3-x4)/x3<=0.05
        &&Math.abs(xls-xrs)/xls<=0.06
        &&flat([cx[1],cx[3],cx[5],cx[7]],function(p){return d[p.i].l;},0.05)
        &&cx[8].i-cx[0].i>=20)
        push1({i:cx[8].i,i2:cx[0].i,mid:cx[4].i,n:'复合头肩',dir:-1});
    }
    if(okB){
      var y1=d[cx[0].i].l,y2=d[cx[2].i].l,yh=d[cx[4].i].l,y3=d[cx[6].i].l,y4=d[cx[8].i].l;
      var yls=(y1+y2)/2,yrs=(y3+y4)/2;
      if(yh<y1*0.985&&yh<y2*0.985&&yh<y3*0.985&&yh<y4*0.985
        &&Math.abs(y1-y2)/y1<=0.05&&Math.abs(y3-y4)/y3<=0.05
        &&Math.abs(yls-yrs)/yls<=0.06
        &&flat([cx[1],cx[3],cx[5],cx[7]],function(p){return d[p.i].h;},0.05)
        &&cx[8].i-cx[0].i>=20)
        push1({i:cx[8].i,i2:cx[0].i,mid:cx[4].i,n:'复合头肩',dir:1});
    }
  }
  for(i=12;i<n;i++){
    for(var fl2=3;fl2<=5;fl2++){
      var pe2=i-fl2;
      var pr2=d[pe2].c/d[Math.max(0,pe2-8)].o-1;
      if(pr2<0.15)continue;
      var fr2=(maxH(pe2+1,i)-minL(pe2+1,i))/d[pe2].c;
      if(fr2>0.04)continue;
      var vp=volA(pe2-8,pe2),vf=volA(pe2+1,i);
      if(vp!==null&&vf!==null&&vf>=vp)continue;
      push1({i:i,i2:Math.max(0,pe2-8),mid:pe2,n:'高紧旗',dir:1});
      break;
    }
  }
  return found;
}
/* ---- I-1 第四批：CHART A股特色/打板族 12 + TD序列 2 + 民间形态 5 + 布鲁克斯 1 = 20 规则（PAT-CHART-027~038、052~056、062） ---- */
function chartPats4(d){
  var n=d.length,found=[],i,j,k;
  var zz=zigzagPts(d);
  function maAt(x,p){var s=Math.max(0,x-p+1),sum=0,cnt=0;for(var t=s;t<=x;t++){sum+=d[t].c;cnt++;}return cnt?sum/cnt:d[x].c;}
  function vok(x){return x>=0&&x<n&&typeof d[x].v==='number'&&d[x].v>0;}
  function anyV(a,b){for(var t=a;t<=b;t++){if(vok(t))return true;}return false;}
  function avgV(a,b){var sum=0,cnt=0;for(var t=a;t<=b;t++){if(vok(t)){sum+=d[t].v;cnt++;}}return cnt?sum/cnt:0;}
  function lu(x){return x>=1&&d[x].c>=d[x-1].c*1.098;}
  function ld(x){return x>=1&&d[x].c<=d[x-1].c*0.902;}
  function luP(x){return x>=1?d[x-1].c*1.098:1e18;}
  for(i=2;i<n;i++){
    if(lu(i)&&(d[i-1].c<d[i-1].o||ld(i-1)||d[i-1].c<=d[i-2].c*0.95)&&d[i].c>d[i-1].o)
      found.push({i:i,i2:i-1,mid:i,n:'反包涨停',dir:1});
  }
  for(i=3;i<n;i++){
    if(!lu(i))continue;
    for(j=Math.max(1,i-11);j<=i-2;j++){
      if(!lu(j))continue;
      var hh28=-1e18,ll28=1e18;
      for(k=j+1;k<i;k++){hh28=Math.max(hh28,d[k].h);ll28=Math.min(ll28,d[k].l);}
      if((hh28-ll28)/d[j].c>0.08)continue;
      if(anyV(j+1,i-1)&&vok(j)&&avgV(j+1,i-1)>=d[j].v)continue;
      found.push({i:i,i2:j,mid:j+1+Math.floor((i-j-1)/2),n:'涨停双响炮',dir:1});
      break;
    }
  }
  var a29=0;
  while(a29<n-3){
    var rim=d[a29].c,b29=-1,blo=1e18;
    for(k=a29+1;k<=Math.min(n-1,a29+5);k++){if(d[k].l<blo){blo=d[k].l;b29=k;}}
    if(b29>0&&rim>0&&(rim-blo)/rim>=0.10){
      var vsh=true;
      if(anyV(Math.max(0,b29-1),Math.min(n-1,b29+1))&&anyV(Math.max(0,a29-5),a29-1))
        vsh=avgV(Math.max(0,b29-1),Math.min(n-1,b29+1))<avgV(Math.max(0,a29-5),a29-1);
      var rec=-1;
      for(k=b29+1;k<=Math.min(n-1,b29+10);k++){if(d[k].c>=blo+0.8*(rim-blo)){rec=k;break;}}
      if(rec>0&&vsh){found.push({i:rec,i2:a29,mid:b29,n:'黄金坑',dir:1});a29=rec+1;continue;}
    }
    a29++;
  }
  for(i=9;i<n;i++){
    var g30=d[i-9].c>0?d[i].c/d[i-9].c-1:0;
    if(g30<0.05||g30>0.15)continue;
    var sy=0,burst=false;
    for(k=i-9;k<=i;k++){var bd=(d[k].c-d[k].o)/d[k].o;if(bd>0&&bd<0.012)sy++;}
    if(sy<7)continue;
    if(anyV(i-9,i)){var av30=avgV(i-9,i);for(k=i-9;k<=i;k++){if(vok(k)&&d[k].v>2*av30){burst=true;break;}}}
    if(!burst)found.push({i:i,i2:i-9,mid:i-4,n:'碎阳慢涨',dir:1});
  }
  for(i=59;i<n;i++){
    var hi60=-1e18,lo60=1e18;
    for(k=i-59;k<=i;k++){hi60=Math.max(hi60,d[k].h);lo60=Math.min(lo60,d[k].l);}
    if(hi60<=lo60||(d[i].c-lo60)/(hi60-lo60)>0.334)continue;
    var hh31=-1e18,ll31=1e18;
    for(k=i-14;k<=i;k++){hh31=Math.max(hh31,d[k].h);ll31=Math.min(ll31,d[k].l);}
    if((hh31-ll31)/ll31>0.12)continue;
    var m5=maAt(i,5),m10=maAt(i,10),m20=maAt(i,20);
    var mMx=Math.max(m5,Math.max(m10,m20)),mMn=Math.min(m5,Math.min(m10,m20));
    if(mMn>0&&(mMx-mMn)/mMn<=0.03)found.push({i:i,i2:i-14,mid:i-7,n:'低位箱体蓄势',dir:0});
  }
  for(i=1;i<n;i++){
    if(!lu(i))continue;
    var frst=true;
    for(j=Math.max(1,i-60);j<i;j++){if(lu(j)){frst=false;break;}}
    if(frst&&!(i<n-1&&lu(i+1)))found.push({i:i,i2:Math.max(0,i-1),mid:i,n:'首板试盘',dir:1});
  }
  for(i=2;i<n;i++){
    if(!lu(i))continue;
    var s33=i;while(s33-1>=1&&lu(s33-1))s33--;
    var cbn=i-s33+1;
    if(cbn>=2&&(i+1>=n||!lu(i+1)))
      found.push({i:i,i2:s33,mid:s33+Math.floor((cbn-1)/2),n:'连板×'+cbn,dir:1});
  }
  for(i=3;i<n;i++){
    var e34=-1;
    for(j=i-1;j>=Math.max(1,i-3);j--){if(lu(j)){e34=j;break;}}
    if(e34<0)continue;
    var s34=e34;while(s34-1>=1&&lu(s34-1))s34--;
    if(e34-s34+1<2)continue;
    var dd34=0;
    for(k=e34+1;k<=i;k++){dd34=Math.max(dd34,(d[e34].c-d[k].l)/d[e34].c);}
    if(dd34>=0.06)continue;
    if(anyV(e34+1,i)&&vok(e34)&&avgV(e34+1,i)>=d[e34].v)continue;
    found.push({i:i,i2:s34,mid:e34,n:'断板温和洗盘',dir:0});
  }
  for(i=1;i<n;i++){
    var lp35=luP(i);
    if(d[i].h>=lp35&&d[i].c>=lp35&&d[i].l<lp35)found.push({i:i,i2:i-1,mid:i,n:'烂板回封',dir:0});
  }
  for(i=1;i<n;i++){
    var lp36=luP(i);
    if(d[i].c<lp36)continue;
    var core=(d[i].o+d[i].h+d[i].l+d[i].c)/4;
    if(core>lp36*0.97)continue;
    if(anyV(Math.max(0,i-5),i-1)&&vok(i)&&d[i].v>1.2*avgV(Math.max(0,i-5),i-1))continue;
    found.push({i:i,i2:Math.max(0,i-1),mid:i,n:'尾盘偷袭板',dir:0});
  }
  var cB=0,cS=0;
  for(i=4;i<n;i++){
    cB=d[i].c<d[i-4].c?cB+1:0;
    cS=d[i].c>d[i-4].c?cS+1:0;
    if(cB===9)found.push({i:i,i2:i-8,mid:i-4,n:'TD买9',dir:1});
    if(cS===9)found.push({i:i,i2:i-8,mid:i-4,n:'TD卖9',dir:-1});
  }
  var st52=0,g52=-1,p52=-1;
  for(i=61;i<n;i++){
    var f5=maAt(i,5),mA=maAt(i,10),s60=maAt(i,60),pf5=maAt(i-1,5),pmA=maAt(i-1,10);
    if(st52===0){
      if(f5>mA&&pf5<=pmA&&f5>s60){st52=1;g52=i;}
    }else if(st52===1){
      if(f5<s60*0.98||i-g52>25){st52=0;}
      else if(i-g52>=2&&f5<=mA*1.01){st52=2;p52=i;}
    }else{
      if(f5<s60*0.98||i-p52>15){st52=0;}
      else if(f5<=mA*1.01){p52=i;}
      else if(f5>mA&&pf5<=pmA*1.01){found.push({i:i,i2:g52,mid:p52,n:'老鸭头',dir:1});st52=0;}
    }
  }
  for(i=4;i<n;i++){
    for(var b53=Math.max(1,i-5);b53<=i-3;b53++){
      var bdB=(d[b53].c-d[b53].o)/d[b53].o;
      if(bdB<0.05)continue;
      if(b53>=20&&d[b53].c<d[b53-20].c*1.08)continue;
      var hh53=-1e18,ll53=1e18;
      for(k=b53+1;k<=i;k++){hh53=Math.max(hh53,d[k].h);ll53=Math.min(ll53,d[k].l);}
      if((hh53-ll53)/d[b53].c>0.05)continue;
      if(ll53<(d[b53].o+d[b53].c)/2)continue;
      found.push({i:i,i2:b53,mid:b53+1+Math.floor((i-b53-1)/2),n:'空中加油',dir:1});
      break;
    }
  }
  for(i=4;i<zz.length;i++){
    var z1=zz[i-4],z2=zz[i-3],z3=zz[i-2],z4=zz[i-1],z5=zz[i];
    if(z1.tp===1&&z2.tp===-1&&z3.tp===1&&z4.tp===-1&&z5.tp===1&&(z5.i-z1.i)>=10){
      var hh1=d[z1.i].h,hh2=d[z3.i].h,hh3=d[z5.i].h;
      if(hh2<hh1&&hh3<hh2){
        found.push({i:z5.i,i2:z1.i,mid:z3.i,n:'三降峰',dir:-1});
        if(d[z4.i].l<d[z2.i].l)found.push({i:z5.i,i2:z1.i,mid:z3.i,n:'三峰穹顶',dir:-1});
      }
    }
    if(z1.tp===-1&&z2.tp===1&&z3.tp===-1&&z4.tp===1&&z5.tp===-1&&(z5.i-z1.i)>=10){
      var bb1=d[z1.i].l,bb2=d[z3.i].l,bb3=d[z5.i].l;
      if(bb2>bb1&&bb3>bb2)found.push({i:z5.i,i2:z1.i,mid:z3.i,n:'三升谷',dir:1});
    }
  }
  for(i=3;i<zz.length;i++){
    var wA=zz[i-3],wB=zz[i-2],wC=zz[i-1],wD=zz[i];
    if(wA.tp===1&&wB.tp===-1&&wC.tp===1&&wD.tp===-1&&(wD.i-wA.i)>=6
      &&d[wC.i].h<d[wA.i].h&&d[wD.i].l>=d[wB.i].l*0.99&&d[wA.i].c>maAt(wA.i,20))
      found.push({i:wD.i,i2:wA.i,mid:wB.i,n:'H2回调买点',dir:1});
    if(wA.tp===-1&&wB.tp===1&&wC.tp===-1&&wD.tp===1&&(wD.i-wA.i)>=6
      &&d[wC.i].l>d[wA.i].l&&d[wD.i].h<=d[wB.i].h*1.01&&d[wA.i].c<maAt(wA.i,20))
      found.push({i:wD.i,i2:wA.i,mid:wB.i,n:'L2反弹卖点',dir:-1});
  }
  return found;
}
/* ---- I-1 第四批：TREND 族 13 规则（PAT-TREND-001~013） ---- */
function trendPats(d){
  var n=d.length,found=[],i,j,k;
  if(n<2) return found;
  var zz=zigzagPts(d);
  function maAt(idx,p){
    if(idx<p-1) return null;
    var s=0; for(var q=idx-p+1;q<=idx;q++) s+=d[q].c;
    return s/p;
  }
  function linfit(pts,acc){
    var m=pts.length,sx=0,sy=0,sxy=0,sxx=0,v;
    for(var q=0;q<m;q++){ v=acc(pts[q]); sx+=pts[q].i; sy+=v; sxy+=pts[q].i*v; sxx+=pts[q].i*pts[q].i; }
    var den=m*sxx-sx*sx; if(!den) return null;
    var a=(m*sxy-sx*sy)/den;
    return [a,(sy-a*sx)/m];
  }
  function atrAvg(len){
    var s=0,c=0,q,tr;
    for(q=Math.max(1,n-len);q<n;q++){
      tr=Math.max(d[q].h-d[q].l,Math.abs(d[q].h-d[q-1].c),Math.abs(d[q].l-d[q-1].c));
      s+=tr; c++;
    }
    return c?s/c:0;
  }
  for(i=1;i<n;i++){
    var f0=maAt(i-1,5),s0=maAt(i-1,20),f1=maAt(i,5),s1=maAt(i,20);
    if(f0===null||s0===null||f1===null||s1===null) continue;
    if(f0<=s0&&f1>s1) found.push({i:i,i2:Math.max(0,i-3),mid:Math.max(0,i-1),n:'均线金叉',dir:1});
    else if(f0>=s0&&f1<s1) found.push({i:i,i2:Math.max(0,i-3),mid:Math.max(0,i-1),n:'均线死叉',dir:-1});
  }
  if(n>=60){
    var m5=maAt(n-1,5),m10=maAt(n-1,10),m20=maAt(n-1,20),m60=maAt(n-1,60);
    var an='均线缠绕',ad=0;
    if(m5>m10&&m10>m20&&m20>m60){ an='均线多头排列'; ad=1; }
    else if(m5<m10&&m10<m20&&m20<m60){ an='均线空头排列'; ad=-1; }
    found.push({i:n-1,i2:n-3,mid:n-2,n:an,dir:ad});
  }
  var bots=[],tops=[];
  for(i=0;i<zz.length;i++){ if(zz[i].tp===1) tops.push(zz[i]); else bots.push(zz[i]); }
  var upFit=null,dnFit=null;
  if(bots.length>=3){
    var bs=bots.slice(-3),fu=linfit(bs,function(p){return d[p.i].l;});
    if(fu&&fu[0]>0&&(bs[2].i-bs[0].i)>=8
      &&Math.abs(d[bs[2].i].l-(fu[0]*bs[2].i+fu[1]))/d[bs[2].i].l<0.015){
      upFit={f:fu,pts:bs};
      found.push({i:bs[2].i,i2:bs[0].i,mid:bs[1].i,n:'上升趋势线',dir:1});
    }
  }
  if(tops.length>=3){
    var ts=tops.slice(-3),fd=linfit(ts,function(p){return d[p.i].h;});
    if(fd&&fd[0]<0&&(ts[2].i-ts[0].i)>=8
      &&Math.abs(d[ts[2].i].h-(fd[0]*ts[2].i+fd[1]))/d[ts[2].i].h<0.015){
      dnFit={f:fd,pts:ts};
      found.push({i:ts[2].i,i2:ts[0].i,mid:ts[1].i,n:'下降趋势线',dir:-1});
    }
  }
  if(upFit){
    var inT=[],w=0,wi=-1;
    for(i=0;i<tops.length;i++) if(tops[i].i>=upFit.pts[0].i&&tops[i].i<=upFit.pts[2].i) inT.push(tops[i]);
    for(i=0;i<inT.length;i++){
      var dv=d[inT[i].i].h-(upFit.f[0]*inT[i].i+upFit.f[1]);
      if(dv>w){ w=dv; wi=inT[i].i; }
    }
    if(inT.length>=2&&wi>=0&&w/d[wi].h>=0.01)
      found.push({i:upFit.pts[2].i,i2:upFit.pts[0].i,mid:wi,n:'上升通道',dir:1});
  }
  if(dnFit){
    var inB=[],w2=0,wi2=-1;
    for(i=0;i<bots.length;i++) if(bots[i].i>=dnFit.pts[0].i&&bots[i].i<=dnFit.pts[2].i) inB.push(bots[i]);
    for(i=0;i<inB.length;i++){
      var dv2=(dnFit.f[0]*inB[i].i+dnFit.f[1])-d[inB[i].i].l;
      if(dv2>w2){ w2=dv2; wi2=inB[i].i; }
    }
    if(inB.length>=2&&wi2>=0&&w2/d[wi2].l>=0.01)
      found.push({i:dnFit.pts[2].i,i2:dnFit.pts[0].i,mid:wi2,n:'下降通道',dir:-1});
  }
  if(zz.length>=6){
    var seg=zz.slice(-6),st=[],sb=[];
    for(i=0;i<6;i++){ if(seg[i].tp===1) st.push(seg[i]); else sb.push(seg[i]); }
    if(st.length>=2&&sb.length>=2){
      var th=0,bl=0,ok=true;
      for(i=0;i<st.length;i++) th+=d[st[i].i].h; th/=st.length;
      for(i=0;i<sb.length;i++) bl+=d[sb[i].i].l; bl/=sb.length;
      for(i=0;i<st.length;i++) if(Math.abs(d[st[i].i].h-th)/th>0.02) ok=false;
      for(i=0;i<sb.length;i++) if(Math.abs(d[sb[i].i].l-bl)/bl>0.02) ok=false;
      if(ok&&(seg[5].i-seg[0].i)>=20&&(th-bl)/bl>=0.01)
        found.push({i:seg[5].i,n:'水平箱体通道',dir:0,zone:{i1:seg[0].i,i2:n-1,p1:th,p2:bl}});
    }
  }
  if(zz.length>=3){
    var q1=zz[zz.length-3],q2=zz[zz.length-2],q3=zz[zz.length-1];
    if(q3.i-q1.i>=10)
      found.push({i:q3.i,i2:q1.i,mid:q2.i,n:'安德鲁音叉',dir:q1.tp===-1?1:-1});
  }
  if(bots.length>=1){
    var ai=bots[bots.length-1].i,atr=atrAvg(20);
    if(atr>0&&(n-1-ai)>=4)
      found.push({i:n-1,i2:ai,mid:ai+Math.floor((n-1-ai)/2),n:'江恩1x1角度线',dir:1});
  }
  if(bots.length>=1){
    var P0=d[bots[bots.length-1].i].l,rt=Math.sqrt(P0),gl=[];
    for(k=1;k<=8;k++){ var pk=rt+k*0.125; gl.push({p:pk*pk,t:'九方R'+k,col:'#C9A227'}); }
    found.push({i:n-1,n:'江恩九方图',dir:0,lvl:gl});
  }
  if(zz.length>=2){
    var T=zz[zz.length-1],B=zz[zz.length-2];
    if(T.tp===1&&B.tp===-1&&(T.i-B.i)>=8&&(d[T.i].h-d[B.i].l)/d[B.i].l>=0.05){
      var mi=B.i+Math.floor((T.i-B.i)/2);
      found.push({i:n-1,i2:B.i,mid:mi,n:'速度阻力线1/3',dir:1});
      found.push({i:n-1,i2:B.i,mid:mi,n:'速度阻力线2/3',dir:1});
    }
  }
  if(zz.length>=3){
    var g3=zz[zz.length-1];
    found.push({i:g3.i,i2:zz[zz.length-3].i,mid:zz[zz.length-2].i,n:'江恩摆动',dir:g3.tp===1?1:-1});
  }
  return found;
}
/* ---- I-1 第四批：SR 族 10 规则（PAT-SR-001~010） ---- */
function srPats(d){
  var n=d.length,found=[],i,j,k;
  if(n<2) return found;
  var zz=zigzagPts(d),tops=[];
  for(i=0;i<zz.length;i++) if(zz[i].tp===1) tops.push(zz[i]);
  for(i=tops.length-1;i>=0;i--){
    var t=tops[i];
    if(t.i>=n-2||t.i<n-40) continue;
    var res=d[t.i].h,bk=-1,bb=-1;
    for(j=t.i+1;j<n;j++){ if(d[j].h>res){ bk=j; break; } }
    if(bk<0) continue;
    for(j=bk;j<n&&j<=bk+2;j++){ if(d[j].c<res){ bb=j; break; } }
    if(bb>=0){ found.push({i:bb,i2:t.i,mid:bk,n:'压力位突破失败',dir:-1}); break; }
  }
  for(i=tops.length-1;i>=0;i--){
    var t2=tops[i];
    if(t2.i>=n-3||t2.i<n-60) continue;
    var rs2=d[t2.i].h,bo=-1,rt2=-1;
    for(j=t2.i+1;j<n;j++){ if(d[j].c>rs2*1.01){ bo=j; break; } }
    if(bo<0) continue;
    for(j=bo+1;j<n;j++){ if(d[j].l<=rs2*1.01&&d[j].c>rs2){ rt2=j; break; } }
    if(rt2>=0){ found.push({i:rt2,i2:t2.i,mid:bo,n:'支撑压力互换',dir:1}); break; }
  }
  if(n>=8){
    var ORH=-1e18,ORL=1e18;
    for(i=0;i<5;i++){ ORH=Math.max(ORH,d[i].h); ORL=Math.min(ORL,d[i].l); }
    var boI=-1,bdI=-1,slI=-1;
    for(i=5;i<n;i++){
      if(boI<0&&d[i].c>ORH) boI=i;
      if(bdI<0&&d[i].c<ORL) bdI=i;
      if(slI<0&&d[i].c<ORL*0.995) slI=i;
    }
    if(boI>=0) found.push({i:boI,i2:0,mid:4,n:'分时突破',dir:1});
    if(bdI>=0) found.push({i:bdI,i2:0,mid:4,n:'分时破位',dir:-1});
    if(slI>=0) found.push({i:slI,i2:0,mid:4,n:'止损破位',dir:-1});
  }
  var H=d[n-1].h,L=d[n-1].l,C=d[n-1].c,R=H-L,PP=(H+L+C)/3;
  found.push({i:n-1,n:'经典枢轴点',dir:0,lvl:[
    {p:H+2*(PP-L),t:'R3',col:'#CA3F64'},{p:PP+R,t:'R2',col:'#CA3F64'},{p:2*PP-L,t:'R1',col:'#CA3F64'},
    {p:PP,t:'PP',col:'#FFD54F'},
    {p:2*PP-H,t:'S1',col:'#25A750'},{p:PP-R,t:'S2',col:'#25A750'},{p:L-2*(H-PP),t:'S3',col:'#25A750'}
  ]});
  found.push({i:n-1,n:'斐波那契枢轴点',dir:0,lvl:[
    {p:PP+R,t:'R3',col:'#CA3F64'},{p:PP+0.618*R,t:'R2',col:'#CA3F64'},{p:PP+0.382*R,t:'R1',col:'#CA3F64'},
    {p:PP,t:'PP',col:'#FFD54F'},
    {p:PP-0.382*R,t:'S1',col:'#25A750'},{p:PP-0.618*R,t:'S2',col:'#25A750'},{p:PP-R,t:'S3',col:'#25A750'}
  ]});
  found.push({i:n-1,n:'卡玛利拉枢轴',dir:0,lvl:[
    {p:C+R*1.1/2,t:'R4',col:'#CA3F64'},{p:C+R*1.1/4,t:'R3',col:'#CA3F64'},
    {p:C+R*1.1/6,t:'R2',col:'#CA3F64'},{p:C+R*1.1/12,t:'R1',col:'#CA3F64'},
    {p:C-R*1.1/12,t:'S1',col:'#25A750'},{p:C-R*1.1/6,t:'S2',col:'#25A750'},
    {p:C-R*1.1/4,t:'S3',col:'#25A750'},{p:C-R*1.1/2,t:'S4',col:'#25A750'}
  ]});
  found.push({i:n-1,n:'昨日高低点',dir:0,lvl:[
    {p:d[n-2].h,t:'昨高',col:'#CA3F64'},{p:d[n-2].l,t:'昨低',col:'#25A750'}
  ]});
  var LB=Math.min(64,n),mh=-1e18,ml=1e18;
  for(i=n-LB;i<n;i++){ mh=Math.max(mh,d[i].h); ml=Math.min(ml,d[i].l); }
  if(mh>ml){
    var mv=[];
    for(k=0;k<=8;k++) mv.push({p:ml+(mh-ml)*k/8,t:'MML '+k+'/8',col:k===4?'#FFD54F':'#8D9E63'});
    found.push({i:n-1,n:'穆雷数学线',dir:0,lvl:mv});
  }
  var vh=-1e18,vl=1e18,vs=0,vc=0;
  for(i=0;i<n;i++){ vh=Math.max(vh,d[i].h); vl=Math.min(vl,d[i].l); if(d[i].v!==undefined){ vs+=d[i].v; vc++; } }
  if(vh>vl){
    var avgV=vc>0?vs/vc:1,NB=12,bw=(vh-vl)/NB,bins=[];
    for(i=0;i<NB;i++) bins.push(0);
    for(i=0;i<n;i++){
      var bi=Math.floor(((d[i].h+d[i].l+d[i].c)/3-vl)/bw);
      if(bi<0) bi=0; if(bi>=NB) bi=NB-1;
      bins[bi]+=(d[i].v!==undefined?d[i].v:Math.abs(d[i].c-d[i].o)*avgV);
    }
    var b1=0,b2=-1;
    for(i=1;i<NB;i++) if(bins[i]>bins[b1]) b1=i;
    for(i=0;i<NB;i++){ if(i>=b1-1&&i<=b1+1) continue; if(b2<0||bins[i]>bins[b2]) b2=i; }
    var vv=[{p:vl+(b1+0.5)*bw,t:'量能密集1',col:'#7E57C2'}];
    if(b2>=0&&bins[b2]>0) vv.push({p:vl+(b2+0.5)*bw,t:'量能密集2',col:'#7E57C2'});
    found.push({i:n-1,n:'成交量分布支撑阻力',dir:0,lvl:vv});
  }
  return found;
}
/* ---- I-1 第四批：FIB 斐波那契族 17 规则（PAT-FIB-001~017） ---- */
function fibPats(d){
  var n=d.length,found=[],i,k,j;
  var zz=zigzagPts(d);
  function pv(p){return p.tp===1?d[p.i].h:d[p.i].l;}
  function near(v,t,tol){return Math.abs(v-t)<=tol*t;}
  function inR(v,lo,hi,tol){return v>=lo*(1-tol)&&v<=hi*(1+tol);}
  function hit(P,dir,nm){found.push({i:P[4].i,i2:P[0].i,mid:P[3].i,n:nm,dir:dir});}
  var TOL=0.08;
  var leg=null;
  if(zz.length>=2){
    var LA=zz[zz.length-2],LB=zz[zz.length-1];
    var pA=pv(LA),pB=pv(LB);
    if(Math.abs(pB-pA)/pA>=0.05) leg={a:LA,b:LB,pA:pA,pB:pB,up:LB.tp===1};
  }
  if(leg){
    var span=leg.pB-leg.pA,bars=leg.b.i-leg.a.i,eI=leg.b.i;
    var rr=[0.236,0.382,0.5,0.618,0.786],lv1=[];
    for(k=0;k<rr.length;k++) lv1.push({p:leg.pB-rr[k]*span,t:(rr[k]*100).toFixed(1)+'%',col:'#C9A227'});
    found.push({i:eI,n:'斐波那契回撤',dir:leg.up?1:-1,lvl:lv1});
    var er=[1.272,1.618,2.618],lv2=[];
    for(k=0;k<er.length;k++) lv2.push({p:leg.pA+er[k]*span,t:(er[k]*100).toFixed(1)+'%',col:'#7E57C2'});
    found.push({i:eI,n:'斐波那契扩展',dir:leg.up?1:-1,lvl:lv2});
    var fr=[0.382,0.5,0.618],lv3=[];
    for(k=0;k<fr.length;k++){
      var anch=leg.pB-fr[k]*span;
      lv3.push({p:leg.pA+(anch-leg.pA)*(n-1-leg.a.i)/bars,t:'扇'+(fr[k]*100).toFixed(1)+'%',col:'#25A750'});
    }
    found.push({i:n-1,n:'斐波那契扇形',dir:leg.up?1:-1,lvl:lv3});
    var kS=span/bars,lv4=[];
    for(k=0;k<fr.length;k++){
      var R=fr[k]*Math.sqrt(2)*bars,dx=n-1-leg.b.i;
      var dy=dx<R?Math.sqrt(R*R-dx*dx):0;
      lv4.push({p:leg.pB-kS*dy,t:'弧'+(fr[k]*100).toFixed(1)+'%',col:'#AB47BC'});
    }
    found.push({i:n-1,n:'斐波那契弧形',dir:leg.up?1:-1,lvl:lv4});
    var tm=[1,1.618,2.618,4.236],lv5=[];
    for(k=0;k<tm.length;k++){
      var tb=leg.a.i+Math.round(tm[k]*bars);
      if(tb<n) lv5.push({p:d[tb].c,t:'T×'+tm[k]+'@'+tb,col:'#78909C'});
    }
    if(lv5.length) found.push({i:eI,n:'斐波那契时间区间',dir:0,lvl:lv5});
  }
  if(zz.length>=3){
    var m=zz.length,levs=[];
    var legs=[[zz[m-3],zz[m-2]],[zz[m-2],zz[m-1]]];
    var r1=[0.382,0.5,0.618],e1=[1.272,1.618];
    for(k=0;k<2;k++){
      var pa=pv(legs[k][0]),pb=pv(legs[k][1]),sp=pb-pa;
      if(!sp) continue;
      for(j=0;j<r1.length;j++) levs.push(pb-r1[j]*sp);
      for(j=0;j<e1.length;j++) levs.push(pa+e1[j]*sp);
    }
    levs.sort(function(a,b){return a-b;});
    var cl=[],cur=[];
    for(k=0;k<levs.length;k++){
      if(cur.length&&Math.abs(levs[k]-cur[cur.length-1])/cur[cur.length-1]>0.008){cl.push(cur);cur=[];}
      cur.push(levs[k]);
    }
    if(cur.length) cl.push(cur);
    var lv6=[];
    for(k=0;k<cl.length;k++){
      if(cl[k].length>=2){
        var s=0;for(j=0;j<cl[k].length;j++) s+=cl[k][j];
        lv6.push({p:s/cl[k].length,t:'共振×'+cl[k].length,col:'#FF7043'});
      }
    }
    if(lv6.length) found.push({i:zz[m-1].i,n:'斐波那契共振簇',dir:0,lvl:lv6});
  }
  for(i=4;i<zz.length;i++){
    var P=[zz[i-4],zz[i-3],zz[i-2],zz[i-1],zz[i]];
    if(P[0].tp!==-P[1].tp||P[1].tp!==-P[2].tp||P[2].tp!==-P[3].tp||P[3].tp!==-P[4].tp) continue;
    var dir=P[4].tp===-1?1:-1;
    var pX=pv(P[0]),pA2=pv(P[1]),pB2=pv(P[2]),pC=pv(P[3]),pD=pv(P[4]);
    var XA=Math.abs(pA2-pX),AB=Math.abs(pB2-pA2),BC=Math.abs(pC-pB2),CD=Math.abs(pD-pC);
    var XC=Math.abs(pC-pX),XD=Math.abs(pD-pX);
    if(XA/pX<0.03) continue;
    if(!XA||!AB||!BC||!XC) continue;
    var rB=AB/XA,rC=BC/AB,rDXA=XD/XA,rDBC=CD/BC,rDXC=CD/XC,rCXA=XC/XA;
    if(near(rB,0.618,TOL)&&inR(rC,0.382,0.886,TOL)&&inR(rDBC,1.272,1.618,TOL)&&near(CD/AB,1,0.10)) hit(P,dir,'ABCD谐波形态');
    if(near(rB,0.618,TOL)&&near(rDXA,0.786,TOL)&&inR(rDBC,1.272,1.618,TOL)) hit(P,dir,'加特利形态');
    if(inR(rB,0.382,0.5,TOL)&&near(rDXA,0.886,TOL)&&inR(rDBC,1.618,2.618,TOL)) hit(P,dir,'蝙蝠形态');
    if(near(rB,0.382,TOL)&&near(rDXA,1.13,TOL)&&inR(rDBC,2.0,3.618,TOL)) hit(P,dir,'变体蝙蝠形态');
    if(near(rB,0.786,TOL)&&inR(rDXA,1.272,1.618,TOL)&&inR(rDBC,1.618,2.24,TOL)) hit(P,dir,'蝴蝶形态');
    if(inR(rB,0.382,0.618,TOL)&&near(rDXA,1.618,TOL)&&inR(rDBC,2.618,3.618,TOL)) hit(P,dir,'螃蟹形态');
    if(near(rB,0.886,TOL)&&near(rDXA,1.618,TOL)&&inR(rDBC,2.24,3.618,TOL)) hit(P,dir,'深螃蟹形态');
    if(inR(rB,1.13,1.618,TOL)&&inR(rDXC,0.886,1.13,TOL)&&inR(rDBC,1.618,2.24,TOL)) hit(P,dir,'鲨鱼形态');
    if(inR(rB,0.382,0.618,TOL)&&inR(rCXA,1.272,1.414,TOL)&&near(rDXC,0.786,TOL)) hit(P,dir,'赛弗形态');
    var g1=P[2].i-P[0].i,g2=P[4].i-P[2].i;
    var sym=Math.abs(g1-g2)/Math.max(g1,g2)<=0.3;
    var ladder=P[0].tp===1?(pB2>pX&&pD>pB2):(pB2<pX&&pD<pB2);
    if(inR(rB,1.272,1.618,TOL)&&inR(rDBC,1.272,1.618,TOL)&&sym&&ladder) hit(P,dir,'三推形态');
    if(inR(rB,1.13,1.618,TOL)&&inR(rC,1.618,2.24,TOL)&&near(rDBC,0.5,TOL)) hit(P,dir,'谐波5-0形态');
  }
  return found;
}
/* ---- I-1 第四批：STRUCT 威科夫/SMC/VSA + 供需区 + 开盘区间 + ELW 楔形 27 规则（PAT-STRUCT-001~016/019~025/037/038、PAT-ELW-007/008） ---- */
function structPats(d){
  var n=d.length,found=[],i,j;
  if(n<10)return found;
  var zz=zigzagPts(d);
  var vols=[],avgV=0,avgB=0,avgR=0;
  for(i=0;i<n;i++){
    var bd=Math.abs(d[i].c-d[i].o);
    vols.push((d[i].v!==undefined&&d[i].v!==null)?d[i].v:bd);
    avgV+=vols[i];avgB+=bd;avgR+=d[i].h-d[i].l;
  }
  avgV/=n;avgB/=n;avgR/=n;
  function body(x){return Math.abs(d[x].c-d[x].o);}
  function bmid(x){return (d[x].h+d[x].l)/2;}
  function flatZZ(pts,acc,tol){
    var mn=1e18,mx=-1e18;
    pts.forEach(function(p){var v=acc(p);if(v<mn)mn=v;if(v>mx)mx=v;});
    return mn>0&&(mx-mn)/mn<=tol;
  }
  function slopeZZ(pts,acc){
    var m=pts.length;if(m<2)return 0;
    var sx=0,sy=0,sxy=0,sxx=0;
    for(var q=0;q<m;q++){var v=acc(pts[q]);sx+=q;sy+=v;sxy+=q*v;sxx+=q*q;}
    var dn=m*sxx-sx*sx;if(!dn)return 0;
    return (m*sxy-sx*sy)/dn;
  }
  var topAt=[],botAt=[],trendAt=[],zi=0,lT=null,lB=null,tt=[],bb=[];
  for(i=0;i<n;i++){
    while(zi<zz.length&&zz[zi].i<i){
      if(zz[zi].tp===1){lT=zz[zi];tt.push(zz[zi]);}else{lB=zz[zi];bb.push(zz[zi]);}
      zi++;
    }
    topAt[i]=lT;botAt[i]=lB;
    if(tt.length>=2&&bb.length>=2){
      var tA=d[tt[tt.length-2].i].h,tB2=d[tt[tt.length-1].i].h;
      var bA=d[bb[bb.length-2].i].l,bB2=d[bb[bb.length-1].i].l;
      trendAt[i]=(tB2>tA&&bB2>bA)?1:(tB2<tA&&bB2<bA)?-1:0;
    }else trendAt[i]=0;
  }
  var lastChoch=0;
  for(i=1;i<n;i++){
    var zp=topAt[i],zb=botAt[i];
    if(zp){
      var zpP=d[zp.i].h;
      if(d[i].c>zpP&&d[i-1].c<=zpP){
        found.push({i:i,i2:zp.i,mid:zb?zb.i:zp.i,n:'结构突破BOS',dir:1});
        for(j=i-1;j>=Math.max(0,i-10);j--)
          if(d[j].c<d[j].o){found.push({i:i,n:'订单块OB',dir:1,zone:{i1:j,i2:i,p1:d[j].h,p2:d[j].l}});break;}
        if(trendAt[i]===-1&&lastChoch!==1){lastChoch=1;found.push({i:i,i2:zp.i,mid:zb?zb.i:zp.i,n:'性格转变CHoCH',dir:1});}
      }
      if(d[i].h>zpP*1.0005&&d[i-1].h<=zpP*1.0005)
        for(j=i;j<=Math.min(i+3,n-1);j++)
          if(d[j].c<zpP){found.push({i:j,i2:zp.i,mid:i,n:'流动性扫荡',dir:-1});break;}
    }
    if(zb){
      var zbP=d[zb.i].l;
      if(d[i].c<zbP&&d[i-1].c>=zbP){
        found.push({i:i,i2:zb.i,mid:zp?zp.i:zb.i,n:'结构突破BOS',dir:-1});
        for(j=i-1;j>=Math.max(0,i-10);j--)
          if(d[j].c>d[j].o){found.push({i:i,n:'订单块OB',dir:-1,zone:{i1:j,i2:i,p1:d[j].h,p2:d[j].l}});break;}
        if(trendAt[i]===1&&lastChoch!==-1){lastChoch=-1;found.push({i:i,i2:zb.i,mid:zp?zp.i:zb.i,n:'性格转变CHoCH',dir:-1});}
      }
      if(d[i].l<zbP*0.9995&&d[i-1].l>=zbP*0.9995)
        for(j=i;j<=Math.min(i+3,n-1);j++)
          if(d[j].c>zbP){found.push({i:j,i2:zb.i,mid:i,n:'流动性扫荡',dir:1});break;}
    }
  }
  var rg=null;
  if(zz.length>=6){
    var seg=zz.slice(-6);
    var st=seg.filter(function(p){return p.tp===1;}),sb=seg.filter(function(p){return p.tp===-1;});
    var span=seg[seg.length-1].i-seg[0].i;
    if(st.length>=2&&sb.length>=2&&span>=20
      &&flatZZ(st,function(p){return d[p.i].h;},0.03)&&flatZZ(sb,function(p){return d[p.i].l;},0.03)){
      var th=st.map(function(p){return d[p.i].h;}),bl=sb.map(function(p){return d[p.i].l;});
      var rTop=(Math.min.apply(null,th)+Math.max.apply(null,th))/2;
      var rBot=(Math.min.apply(null,bl)+Math.max.apply(null,bl))/2;
      var w0=Math.max(0,n-60),wHi=-1e18,wLo=1e18;
      for(i=w0;i<n;i++){wHi=Math.max(wHi,d[i].h);wLo=Math.min(wLo,d[i].l);}
      var third=(wHi-wLo)/3,pos2=(rTop+rBot)/2,kind=0;
      if(pos2<=wLo+third)kind=1;else if(pos2>=wHi-third)kind=-1;
      rg={i1:seg[0].i,i2:seg[seg.length-1].i,top:rTop,bot:rBot,kind:kind};
      if(kind===1)found.push({i:rg.i2,n:'威科夫吸筹区间',dir:1,zone:{i1:rg.i1,i2:rg.i2,p1:rTop,p2:rBot}});
      else if(kind===-1)found.push({i:rg.i2,n:'威科夫派发区间',dir:-1,zone:{i1:rg.i1,i2:rg.i2,p1:rTop,p2:rBot}});
    }
  }
  if(rg){
    var springI=-1,upI=-1,sosI=-1,sowI=-1,end2=Math.min(n-1,rg.i2+8);
    for(i=rg.i1+1;i<=end2;i++){
      if(springI<0&&d[i].l<rg.bot*0.995)
        for(j=i+1;j<=Math.min(i+5,n-1);j++)
          if(d[j].c>rg.bot){springI=j;found.push({i:j,i2:i,mid:(i+j)>>1,n:'威科夫弹簧',dir:1});break;}
      if(upI<0&&d[i].h>rg.top*1.005)
        for(j=i+1;j<=Math.min(i+5,n-1);j++)
          if(d[j].c<rg.top){upI=j;found.push({i:j,i2:i,mid:(i+j)>>1,n:'威科夫上冲',dir:-1});break;}
      if(sosI<0&&d[i].c>d[i].o&&d[i].c>rg.top&&d[i-1].c<=rg.top&&vols[i]>=1.5*avgV){
        sosI=i;found.push({i:i,i2:rg.i1,mid:(rg.i1+i)>>1,n:'威科夫强势信号SOS',dir:1});
      }
      if(sowI<0&&d[i].c<d[i].o&&d[i].c<rg.bot&&d[i-1].c>=rg.bot&&vols[i]>=1.5*avgV){
        sowI=i;found.push({i:i,i2:rg.i1,mid:(rg.i1+i)>>1,n:'威科夫弱势信号SOW',dir:-1});
      }
    }
    var ev1=Math.max(springI,sosI);
    if(ev1>0)for(i=ev1+1;i<=Math.min(ev1+15,n-1);i++)
      if(d[i].l<=rg.top*1.01&&d[i].c>rg.top){found.push({i:i,i2:ev1,mid:(ev1+i)>>1,n:'威科夫最后支撑点LPS',dir:1});break;}
    var ev2=Math.max(upI,sowI);
    if(ev2>0)for(i=ev2+1;i<=Math.min(ev2+15,n-1);i++)
      if(d[i].h>=rg.bot*0.99&&d[i].c<rg.bot){found.push({i:i,i2:ev2,mid:(ev2+i)>>1,n:'威科夫最后供给点LPSY',dir:-1});break;}
  }
  for(i=2;i<n;i++){
    if(d[i].l>d[i-2].h&&(d[i].l-d[i-2].h)/d[i-2].h>=0.001)
      found.push({i:i,n:'公允价值缺口FVG',dir:1,zone:{i1:i-2,i2:i,p1:d[i].l,p2:d[i-2].h}});
    if(d[i].h<d[i-2].l&&(d[i-2].l-d[i].h)/d[i].h>=0.001)
      found.push({i:i,n:'公允价值缺口FVG',dir:-1,zone:{i1:i-2,i2:i,p1:d[i-2].l,p2:d[i].h}});
  }
  function pool(pts,acc,nm,dir,col){
    var g=[];
    function flush(){
      if(g.length>=2){
        var pv2=0;g.forEach(function(p){pv2+=acc(p);});pv2/=g.length;
        found.push({i:g[g.length-1].i,n:nm+'×'+g.length,dir:dir,lvl:[{p:pv2,t:nm+'×'+g.length,col:col}]});
      }
    }
    for(var q=0;q<pts.length;q++){
      if(!g.length){g.push(pts[q]);continue;}
      var mn=1e18,mx=-1e18;
      g.concat([pts[q]]).forEach(function(p){var v=acc(p);if(v<mn)mn=v;if(v>mx)mx=v;});
      if((mx-mn)/mn<=0.0015)g.push(pts[q]);else{flush();g=[pts[q]];}
    }
    flush();
  }
  pool(zz.filter(function(p){return p.tp===1;}),function(p){return d[p.i].h;},'等高池',-1,'#FF8A65');
  pool(zz.filter(function(p){return p.tp===-1;}),function(p){return d[p.i].l;},'等低池',1,'#4DB6AC');
  if(zz.length>=2){
    var z1=zz[zz.length-2],z2=zz[zz.length-1];
    var pA=z1.tp===1?d[z1.i].h:d[z1.i].l,pB=z2.tp===1?d[z2.i].h:d[z2.i].l;
    found.push({i:z2.i,n:'溢价折价区',dir:0,lvl:[{p:(pA+pB)/2,t:'溢价/折价分界',col:'#FFD54F'}]});
  }
  for(i=1;i<n-1;i++){
    var rng=Math.max(d[i].h-d[i].l,1e-12),cpos=(d[i].c-d[i].l)/rng;
    if(vols[i]>=2*avgV&&body(i)>=1.5*avgB&&d[i].c<d[i].o&&cpos<=0.33&&d[i+1].c>=d[i].c)
      found.push({i:i+1,i2:i-1,mid:i,n:'VSA抛售高潮',dir:1});
    if(vols[i]>=2*avgV&&body(i)>=1.5*avgB&&d[i].c>d[i].o&&cpos>=0.67&&d[i+1].c<=d[i].c)
      found.push({i:i+1,i2:i-1,mid:i,n:'VSA买入高潮',dir:-1});
    var loS=Math.min(d[i].o,d[i].c)-d[i].l;
    if(vols[i]>=1.5*avgV&&loS>=2*body(i)&&d[i+1].c>=d[i].c)
      found.push({i:i+1,i2:i-1,mid:i,n:'VSA停止量',dir:1});
    if(vols[i]>=1.5*avgV&&d[i].c>d[i].o&&body(i)>=1.5*avgB&&d[i].c<bmid(i))
      found.push({i:i,i2:i-1,mid:i,n:'VSA伪上冲',dir:-1});
    if(i>=5){
      if(vols[i]<0.7*avgV&&body(i)<=0.5*avgB&&d[i].c<=d[i].o&&d[i-1].c<d[i-5].c)
        found.push({i:i,i2:i-2,mid:i-1,n:'VSA无供给',dir:1});
      if(vols[i]<0.7*avgV&&body(i)<=0.5*avgB&&d[i].c>=d[i].o&&d[i-1].c>d[i-5].c)
        found.push({i:i,i2:i-2,mid:i-1,n:'VSA无需求',dir:-1});
      if(vols[i]<avgV&&rng<=avgR&&d[i].c>bmid(i)&&d[i-1].c<d[i-5].c)
        found.push({i:i,i2:i-2,mid:i-1,n:'VSA测试bar',dir:1});
    }
  }
  if(n>=8){
    var oHi=-1e18,oLo=1e18,brkU=false,brkD=false;
    for(i=0;i<5;i++){oHi=Math.max(oHi,d[i].h);oLo=Math.min(oLo,d[i].l);}
    for(i=5;i<n;i++){
      if(!brkU&&d[i].c>oHi){brkU=true;found.push({i:i,i2:0,mid:4,n:'开盘区间突破(上)',dir:1});}
      if(!brkD&&d[i].c<oLo){brkD=true;found.push({i:i,i2:0,mid:4,n:'开盘区间突破(下)',dir:-1});}
      if(brkU&&brkD)break;
    }
  }
  for(i=3;i<n-1;i++){
    for(var bl2=3;bl2<=6;bl2++){
      if(i+bl2>=n)break;
      var bHi=-1e18,bLo=1e18;
      for(j=i;j<i+bl2;j++){bHi=Math.max(bHi,d[j].h);bLo=Math.min(bLo,d[j].l);}
      if((bHi-bLo)/bLo>0.03)continue;
      var dep=i+bl2,strong=body(dep)>=1.5*avgB;
      if((strong&&d[dep].c>d[dep].o&&d[dep].c>bHi)||d[dep].l>bHi){
        found.push({i:dep,n:'需求区',dir:1,zone:{i1:i,i2:dep,p1:bHi,p2:bLo}});i=dep;break;
      }
      if((strong&&d[dep].c<d[dep].o&&d[dep].c<bLo)||d[dep].h<bLo){
        found.push({i:dep,n:'供应区',dir:-1,zone:{i1:i,i2:dep,p1:bHi,p2:bLo}});i=dep;break;
      }
    }
  }
  if(zz.length>=5){
    var wg=zz.slice(-5);
    var wt=wg.filter(function(p){return p.tp===1;}),wb=wg.filter(function(p){return p.tp===-1;});
    if(wt.length>=2&&wb.length>=2){
      var tS=slopeZZ(wt,function(p){return d[p.i].h;}),bS=slopeZZ(wb,function(p){return d[p.i].l;});
      var eps=d[wg[wg.length-1].i].c*0.0015;
      var mv=d[wg[0].i].c/d[Math.max(0,wg[0].i-30)].c-1;
      if(tS>eps&&bS>tS*1.3){
        if(mv>=0.08)found.push({i:wg[4].i,i2:wg[0].i,mid:wg[2].i,n:'终结楔形',dir:-1});
        else found.push({i:wg[4].i,i2:wg[0].i,mid:wg[2].i,n:'引导楔形',dir:1});
      }else if(tS<-eps&&bS<0&&bS>tS){
        if(mv<=-0.08)found.push({i:wg[4].i,i2:wg[0].i,mid:wg[2].i,n:'终结楔形',dir:1});
        else found.push({i:wg[4].i,i2:wg[0].i,mid:wg[2].i,n:'引导楔形',dir:-1});
      }
    }
  }
  return found;
}
