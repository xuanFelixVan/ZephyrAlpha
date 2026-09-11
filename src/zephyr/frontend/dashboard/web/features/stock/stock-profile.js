/* 功能模块：个股档案页引擎（stock-profile）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 STOCK_D（含 F9 补强族）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L3708-4055, L5221-5252），逻辑零改动。
 * 验收单：ACC-F-STOCK-PROFILE
 */
/* ==================== I-5 个股档案（p-stock）：stockXxx 前缀 ==================== */
var STOCK_CUR='600519';
var STOCK_D={
  '600519':{
    code:'600519',name:'贵州茅台',industry:'白酒 · 申万食品饮料',listDate:'2001-08-27',
    mcap:'2.15 万亿',floatShares:'12.56 亿股',price:'1,712.50',chg:'+0.86%',chgUp:true,
    indices:['沪深300','上证50','中证A50'],seed:519,
    boundary:{boxLower:'1,688.00',noAdd:'1,745.00',mustExit:'1,662.00',state:'持有区（价在箱体内）',stateCls:'b-pass'},
    holders:[
      [1,'中国贵州茅台酒厂（集团）','国资','54.07','0.00'],
      [2,'香港中央结算（陆股通）','外资','6.91','+0.12'],
      [3,'中央汇金资产管理','国资','0.86','0.00'],
      [4,'中国证券金融股份','国资','0.64','0.00'],
      [5,'易方达蓝筹精选混合','基金','0.58','+0.05'],
      [6,'上证50ETF','基金','0.52','+0.02'],
      [7,'贵州国有资本运营','国资','0.45','0.00'],
      [8,'沪深300ETF','基金','0.41','+0.03'],
      [9,'社保基金一一零组合','社保','0.28','+0.01'],
      [10,'林园投资（私募）','其他','0.22','-0.01']
    ],
    instSum:{fund:'1,286 家 · 6.82%',ssf:'2 家 · 0.41%',qfii:'8 家 · 1.12%'},
    execs:[
      ['董事长','丁雄军','2021-09','—','0'],
      ['总经理','王莉','2023-08','96.3','0'],
      ['财务总监','蒋焰','2021-11','82.5','0'],
      ['董事会秘书','刘刚','2022-04','74.8','0']
    ],
    fin:{
      q:['24Q1','24Q2','24Q3','24Q4','25Q1','25Q2','25Q3','25Q4'],
      rev:[457.8,369.7,396.7,383.9,506.0,389.2,410.5,398.4],
      profit:[240.7,176.3,191.3,193.5,268.5,188.4,201.2,205.6],
      years:['2023','2024','2025 TTM'],
      revY:['1,476.9 亿','1,608.4 亿','1,652.1 亿'],
      npY:['747.3 亿','862.3 亿','886.2 亿'],
      gm:['91.9%','92.1%','92.3%'],
      roe:['34.2%','33.5%','32.8%'],
      debt:['18.1%','17.6%','17.2%'],
      ocf:['665.9 亿','782.4 亿','810.3 亿']
    },
    flow:{
      today:[['主力','+38,420'],['超大单','+21,130'],['大单','+17,290'],['中单','-8,640'],['小单','-29,780']],
      d5:['+86,240','+52,110','+34,130','-21,470','-64,770']
    },
    anns:[
      ['2026-08-08','定期报告','2026 年半年度报告全文'],
      ['2026-07-29','分红','2025 年度末期分红实施公告（10 派 276.24 元）'],
      ['2026-07-15','回购','回购股份进展公告（累计回购 0.08%）'],
      ['2026-06-20','重大事项','2025 年度股东大会决议公告'],
      ['2026-05-30','减持','董监高减持计划终止公告'],
      ['2026-04-25','定期报告','2026 年第一季度报告']
    ],
    ratings:{buy:38,add:9,neutral:3},
    chip:{
      periods:['25Q3','25Q4','26Q1','26Q2'],
      holders:[15.2,14.6,13.9,13.1],
      inst:[1286,1312,1348,1395],
      pledge:'0%（无质押）'
    },
    biz:{
      seg:[['茅台酒',86.2],['系列酒',13.8]],
      peers:[
        ['贵州茅台','24.3','8.6','32.8%','2.15 万亿',1],
        ['五粮液','14.2','3.1','22.5%','5,003 亿',0],
        ['泸州老窖','15.8','4.2','28.6%','2,590 亿',0]
      ],
      div:'2025 年度末期 10 派 276.24 元（2026-07-29 实施，股息率约 1.6%）'
    },
    sector:'白酒'
  },
  '300750':{
    code:'300750',name:'宁德时代',industry:'电池 · 申万电力设备',listDate:'2018-06-11',
    mcap:'1.28 万亿',floatShares:'43.90 亿股',price:'289.40',chg:'-1.24%',chgUp:false,
    indices:['沪深300','创业板指'],seed:750,
    boundary:{boxLower:'278.00',noAdd:'296.50',mustExit:'271.00',state:'回踩区（接近箱底，看承接）',stateCls:'b-warn'},
    holders:[
      [1,'曾毓群','个人','23.32','0.00'],
      [2,'宁波梅山保税港区瑞庭投资','其他','11.21','0.00'],
      [3,'香港中央结算（陆股通）','外资','11.85','+0.34'],
      [4,'黄世霖','个人','10.61','0.00'],
      [5,'宁波联合创新新能源','其他','6.78','0.00'],
      [6,'李平','个人','4.58','0.00'],
      [7,'易方达创业板ETF','基金','1.12','+0.06'],
      [8,'华泰柏瑞沪深300ETF','基金','0.96','+0.04'],
      [9,'社保基金四一三组合','社保','0.52','+0.02'],
      [10,'QFII·摩根士丹利国际','QFII','0.48','-0.03']
    ],
    instSum:{fund:'1,542 家 · 8.35%',ssf:'3 家 · 0.86%',qfii:'11 家 · 1.64%'},
    execs:[
      ['董事长','曾毓群','2011-12','—','1,023,654,000'],
      ['总经理','周佳','2022-08','312.6','1,850,000'],
      ['财务总监','郑舒','2017-06','186.4','120,000'],
      ['董事会秘书','蒋理','2018-04','158.2','86,000']
    ],
    fin:{
      q:['24Q1','24Q2','24Q3','24Q4','25Q1','25Q2','25Q3','25Q4'],
      rev:[797.7,869.0,922.8,1029.6,847.0,902.4,968.8,1082.3],
      profit:[105.1,123.6,131.4,148.0,118.9,139.6,147.2,162.8],
      years:['2023','2024','2025 TTM'],
      revY:['4,009.2 亿','3,620.1 亿','3,800.5 亿'],
      npY:['441.2 亿','507.4 亿','568.5 亿'],
      gm:['22.9%','24.4%','25.1%'],
      roe:['21.6%','22.8%','23.4%'],
      debt:['69.3%','67.8%','66.5%'],
      ocf:['928.3 亿','1,012.6 亿','1,086.4 亿']
    },
    flow:{
      today:[['主力','-56,230'],['超大单','-38,410'],['大单','-17,820'],['中单','+12,350'],['小单','+43,880']],
      d5:['-84,120','-51,360','-32,760','+28,540','+55,580']
    },
    anns:[
      ['2026-08-12','重大事项','H 股上市进展公告（聆讯后资料集刊载）'],
      ['2026-07-26','定期报告','2026 年半年度报告预约披露公告'],
      ['2026-06-18','分红','2025 年度权益分派实施（10 派 45.53 元）'],
      ['2026-05-22','回购','回购注销部分限制性股票公告'],
      ['2026-04-28','定期报告','2026 年第一季度报告'],
      ['2026-03-15','重大事项','换电网络战略合作协议签署公告']
    ],
    ratings:{buy:45,add:7,neutral:2},
    chip:{
      periods:['25Q3','25Q4','26Q1','26Q2'],
      holders:[22.8,23.5,24.1,23.6],
      inst:[1542,1496,1508,1533],
      pledge:'0.2%（比例极低）'
    },
    biz:{
      seg:[['动力电池',68.5],['储能',18.2],['其他',13.3]],
      peers:[
        ['宁德时代','22.5','4.9','23.4%','1.28 万亿',1],
        ['比亚迪','18.6','3.9','17.8%','7,150 亿',0],
        ['亿纬锂能','28.4','3.2','12.6%','1,020 亿',0]
      ],
      div:'2025 年度 10 派 45.53 元（2026-06-18 实施）'
    },
    sector:'锂电池'
  },
  '688981':{
    code:'688981',name:'中芯国际',industry:'半导体制造 · 申万电子',listDate:'2020-07-16',
    mcap:'7,860 亿',floatShares:'79.30 亿股（A+H）',price:'99.20',chg:'+2.35%',chgUp:true,
    indices:['沪深300','科创50'],seed:981,
    boundary:{boxLower:'94.50',noAdd:'103.80',mustExit:'91.00',state:'拉升区（近禁加仓线，禁追）',stateCls:'b-buy'},
    holders:[
      [1,'大唐控股（香港）','国资','11.02','0.00'],
      [2,'鑫芯（香港）投资（大基金）','国资','7.76','0.00'],
      [3,'香港中央结算（陆股通）','外资','4.35','+0.28'],
      [4,'国家集成电路产业基金二期','国资','1.62','0.00'],
      [5,'华夏科创50ETF','基金','1.48','+0.07'],
      [6,'易方达科创50ETF','基金','0.92','+0.05'],
      [7,'GIC Private Limited（QFII）','QFII','0.86','-0.04'],
      [8,'华夏半导体芯片ETF','基金','0.74','+0.03'],
      [9,'社保基金一一八组合','社保','0.51','+0.02'],
      [10,'中金公司（做市）','其他','0.38','0.00']
    ],
    instSum:{fund:'896 家 · 5.94%',ssf:'1 家 · 0.51%',qfii:'6 家 · 1.38%'},
    execs:[
      ['董事长','高永岗','2022-03','—','0'],
      ['联合首席执行官','赵海军','2017-05','—','186,000'],
      ['财务总监','吴俊峰','2021-06','268.4','52,000'],
      ['董事会秘书','郭光莉','2020-08','156.7','28,000']
    ],
    fin:{
      q:['24Q1','24Q2','24Q3','24Q4','25Q1','25Q2','25Q3','25Q4'],
      rev:[71.2,80.3,85.0,91.6,78.5,88.2,93.7,99.4],
      profit:[8.9,10.6,11.2,12.8,9.8,11.5,12.4,13.6],
      years:['2023','2024','2025 TTM'],
      revY:['452.5 亿','578.0 亿','642.6 亿'],
      npY:['48.2 亿','53.5 亿','58.6 亿'],
      gm:['19.8%','21.4%','22.6%'],
      roe:['3.2%','3.6%','3.9%'],
      debt:['35.4%','36.1%','36.8%'],
      ocf:['186.4 亿','224.8 亿','252.3 亿']
    },
    flow:{
      today:[['主力','+72,150'],['超大单','+46,820'],['大单','+25,330'],['中单','-14,260'],['小单','-57,890']],
      d5:['+213,400','+138,600','+74,800','-42,150','-171,250']
    },
    anns:[
      ['2026-08-14','重大事项','成熟制程产能扩建项目公告（月增 4 万片）'],
      ['2026-07-30','定期报告','2026 年半年度业绩快报'],
      ['2026-06-25','回购','H 股回购公告（回购 0.05%）'],
      ['2026-05-18','重大事项','大基金三期增资参股子公司公告'],
      ['2026-04-26','定期报告','2026 年第一季度报告'],
      ['2026-03-28','分红','2025 年度利润分配预案说明（留存投研）']
    ],
    ratings:{buy:28,add:12,neutral:6},
    chip:{
      periods:['25Q3','25Q4','26Q1','26Q2'],
      holders:[38.2,36.5,35.1,33.8],
      inst:[896,910,934,962],
      pledge:'0%（无质押）'
    },
    biz:{
      seg:[['成熟制程',72.4],['先进制程',27.6]],
      peers:[
        ['中芯国际','118.0','5.1','3.9%','7,860 亿',1],
        ['华虹公司','56.2','2.4','4.8%','1,180 亿',0],
        ['晶合集成','48.5','2.1','5.2%','620 亿',0]
      ],
      div:'留存投研不分红（2025 年度利润分配预案说明，2026-03-28 公告）'
    },
    sector:'半导体'
  }
};
function stockD(){return STOCK_D[STOCK_CUR];}
function stockSwitch(code,elm){
  STOCK_CUR=code;
  var ns=document.querySelectorAll('.stock-sel');
  for(var i=0;i<ns.length;i++){ ns[i].classList.toggle('on',ns[i]===elm); }
  stockRenderAll();
}
function navOf(id){   /* F3 顶栏适配：按 onclick 属性匹配导航节点（顶栏二级项无 title 属性）；2026-08-25 第二次补写（首次写入被并发覆写冲掉） */
  var nav=null;
  document.querySelectorAll('.nav-item').forEach(function(n){ var oc=n.getAttribute('onclick')||''; if(oc.indexOf("go('"+id+"'")===0) nav=n; });
  return nav;
}
function stockGoT0(){var n=navOf('t0');if(n)go('t0',n);}
function stockGoSector(){var n=navOf('sector');if(n)go('sector',n);}
function stockHolderBadge(t){
  var m={'国资':'b-buy','外资':'b-warn','基金':'b-pass','社保':'b-buy','QFII':'b-warn','个人':'b-na','其他':'b-na'};
  return '<span class="badge '+(m[t]||'b-na')+'">'+t+'</span>';
}
function stockAnnBadge(t){
  var m={'定期报告':'b-pass','重大事项':'b-warn','减持':'b-fail','回购':'b-buy','分红':'b-buy'};
  return '<span class="badge '+(m[t]||'b-na')+'">'+t+'</span>';
}
function stockRenderHead(){
  var s=stockD();
  var idx=s.indices.map(function(t){return '<span class="badge b-pass" style="margin-right:4px">'+t+'</span>';}).join('');
  document.getElementById('stock-head').innerHTML=
    '<div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:10px">'
    +'<span style="font-size:18px;font-weight:700">'+s.name+'</span>'
    +'<span class="dim">'+s.code+'</span>'+idx
    +'<span style="margin-left:auto">最新价 <b style="font-size:20px;font-variant-numeric:tabular-nums" class="'+(s.chgUp?'up':'down')+'">'+s.price+'</b> '
    +'<b class="'+(s.chgUp?'up':'down')+'">'+s.chg+'</b></span></div>'
    +'<div class="stock-kv">'
    +'<div><div class="l">申万行业 <span class="dim">SW Industry</span></div><b>'+s.industry+'</b></div>'
    +'<div><div class="l">上市日期 <span class="dim">List Date</span></div><b>'+s.listDate+'</b></div>'
    +'<div><div class="l">总市值 <span class="dim">Market Cap</span></div><b>'+s.mcap+'</b></div>'
    +'<div><div class="l">流通股本 <span class="dim">Float Shares</span></div><b>'+s.floatShares+'</b></div>'
    +'</div>';
}
function stockRenderK(){
  var s=stockD();
  var svg=document.getElementById('stock-k'); svg.innerHTML='';
  var d=genCandles(s.seed);
  var W=520,H=220,L=10,R=10,T=12,B=18;
  var rg=rangeOf(d);
  var bw=(W-L-R)/d.length;
  var x=function(i){return L+i*bw;};
  var yf=function(v){return T+(rg[1]-v)/(rg[1]-rg[0])*(H-T-B);};
  grid(svg,W,L,R,H,T,B);
  drawCandles(svg,d,x,yf,bw*0.68);
  var pts=[];
  for(var i=0;i<d.length;i++){var m=ma(d,20,i);pts.push(m==null?null:[x(i)+bw*0.34,yf(m)]);}
  polyline(svg,pts,'#FFD54F',1.4);
  hlabel(svg,L,H-4,'120 日 · 黄=MA20 · seed='+s.seed,'#59626D',10);
}
function stockRenderBoundary(){
  var b=stockD().boundary;
  document.getElementById('stock-boundary').innerHTML=
    '<table>'
    +'<tr><th style="width:120px">箱底 <span class="dim">box_lower</span></th><td><b>'+b.boxLower+'</b> <span class="dim">跌破即弱化</span></td></tr>'
    +'<tr><th>禁加仓价 <span class="dim">no_add_price</span></th><td class="warn"><b>'+b.noAdd+'</b> <span class="dim">之上只持不加</span></td></tr>'
    +'<tr><th>必出价 <span class="dim">must_exit</span></th><td class="down"><b>'+b.mustExit+'</b> <span class="dim">跌破无条件离场</span></td></tr>'
    +'<tr><th>当前状态机</th><td><span class="badge '+b.stateCls+'">'+b.state+'</span></td></tr>'
    +'</table>'
    +'<div class="note">明日边界=作战室 L15 裁定的个股级投影，与本页 K 线同图互验；分时买卖点 <span class="stock-link" onclick="stockGoT0()">→ 去做T分析</span></div>';
}
function stockRenderHolders(){
  var s=stockD();
  var h='<tr><th style="width:46px">排名</th><th>股东名称</th><th style="width:64px">性质</th><th style="width:78px">持股比例</th><th style="width:92px">较上期变动</th></tr>';
  s.holders.forEach(function(r){
    var cls=r[4].indexOf('+')===0?'up':(r[4].indexOf('-')===0?'down':'dim');
    h+='<tr><td>'+r[0]+'</td><td>'+r[1]+'</td><td>'+stockHolderBadge(r[2])+'</td><td>'+r[3]+'%</td><td class="'+cls+'">'+(r[4]==='0.00'?'—':r[4]+' pct')+'</td></tr>';
  });
  var m=s.instSum;
  h+='<tr><td colspan="5" style="background:var(--panel2)" class="dim">机构持仓汇总：基金 <b>'+m.fund+'</b> ｜ 社保 <b>'+m.ssf+'</b> ｜ QFII <b>'+m.qfii+'</b></td></tr>';
  document.getElementById('stock-holders').innerHTML=h;
}
function stockRenderExecs(){
  var s=stockD();
  var h='<tr><th style="width:90px">职务</th><th>姓名</th><th style="width:90px">任期起始</th><th style="width:90px">年薪（万）</th><th>持股数（股）</th></tr>';
  s.execs.forEach(function(r){
    h+='<tr><td>'+r[0]+'</td><td><b>'+r[1]+'</b></td><td>'+r[2]+'</td><td>'+r[3]+'</td><td>'+r[4]+'</td></tr>';
  });
  document.getElementById('stock-execs').innerHTML=h;
}
function stockRenderFin(){
  var f=stockD().fin;
  var svg=document.getElementById('stock-fin-svg'); svg.innerHTML='';
  var W=520,H=200,L=8,R=8,T=10,B=22,n=f.q.length;
  var maxR=Math.max.apply(null,f.rev),maxP=Math.max.apply(null,f.profit);
  var gw=(W-L-R)/n;
  for(var i=0;i<n;i++){
    var b1=(f.rev[i]/maxR)*(H-T-B)*0.92,b2=(f.profit[i]/maxP)*(H-T-B)*0.92;
    el('rect',{x:(L+i*gw+gw*0.14).toFixed(1),y:(H-B-b1).toFixed(1),width:(gw*0.32).toFixed(1),height:b1.toFixed(1),fill:'#3D8BFF'},svg);
    el('rect',{x:(L+i*gw+gw*0.52).toFixed(1),y:(H-B-b2).toFixed(1),width:(gw*0.32).toFixed(1),height:b2.toFixed(1),fill:'#F0B90B'},svg);
    hlabel(svg,L+i*gw+gw*0.22,H-6,f.q[i],'#59626D',9);
  }
  var rows=[
    ['营业收入 <span class="dim">Revenue</span>',f.revY],
    ['归母净利 <span class="dim">Net Profit</span>',f.npY],
    ['毛利率 <span class="dim">Gross Margin</span>',f.gm],
    ['净资产收益率 <span class="dim">ROE</span>',f.roe],
    ['资产负债率 <span class="dim">Debt Ratio</span>',f.debt],
    ['经营现金流 <span class="dim">OCF</span>',f.ocf]
  ];
  var h='<tr><th>指标</th><th>'+f.years[0]+'</th><th>'+f.years[1]+'</th><th>'+f.years[2]+'</th></tr>';
  rows.forEach(function(r){h+='<tr><td>'+r[0]+'</td><td>'+r[1][0]+'</td><td>'+r[1][1]+'</td><td>'+r[1][2]+'</td></tr>';});
  document.getElementById('stock-fin-table').innerHTML=h;
}
function stockRenderFlow(){
  var s=stockD();
  var h='<tr><th>资金档位</th><th>当日净额（万元）</th><th>近 5 日累计（万元）</th></tr>';
  s.flow.today.forEach(function(r,i){
    var d5=s.flow.d5[i];
    h+='<tr><td>'+r[0]+'</td><td class="'+(r[1].indexOf('+')===0?'up':'down')+'">'+r[1]+'</td><td class="'+(d5.indexOf('+')===0?'up':'down')+'">'+d5+'</td></tr>';
  });
  document.getElementById('stock-flow').innerHTML=h;
}
function stockRenderAnns(){
  var s=stockD();
  var h='<tr><th style="width:88px">日期</th><th style="width:80px">类型</th><th>标题</th></tr>';
  s.anns.forEach(function(r){
    h+='<tr><td>'+r[0]+'</td><td>'+stockAnnBadge(r[1])+'</td><td>'+r[2]+'</td></tr>';
  });
  document.getElementById('stock-anns').innerHTML=h;
}
function stockRenderRatings(){
  var r=stockD().ratings,tot=r.buy+r.add+r.neutral;
  document.getElementById('stock-ratings').innerHTML=
    '<div class="bar-row"><span>买入 <span class="dim">Buy</span></span><div class="bar"><i class="g" style="width:'+(r.buy/tot*100).toFixed(0)+'%"></i></div><span class="up">'+r.buy+' 家</span></div>'
    +'<div class="bar-row"><span>增持 <span class="dim">Overweight</span></span><div class="bar"><i style="width:'+(r.add/tot*100).toFixed(0)+'%"></i></div><span>'+r.add+' 家</span></div>'
    +'<div class="bar-row"><span>中性 <span class="dim">Neutral</span></span><div class="bar"><i class="y" style="width:'+(r.neutral/tot*100).toFixed(0)+'%"></i></div><span class="warn">'+r.neutral+' 家</span></div>'
    +'<div class="note">研报中心待建设（S7），落地后点亮 <span class="badge b-na">待接入</span> 后端落地后点亮（I-2 流程）（负反馈也是结果——系统明说「没有」）</div>';
}
function stockRenderLinks(){
  var s=stockD();
  document.getElementById('stock-links').innerHTML=
    '所属板块：<b>'+s.sector+'</b>　<span class="stock-link" onclick="stockGoSector()">→ 去板块全景（梯队/资金证据链）</span><br>'
    +'做T点位：<span class="stock-link" onclick="stockGoT0()">→ 去做T分析（分时 ▲▼ 信号回验）</span><br>'
    +'<span class="dim">相似标的对比：<span class="badge b-na">待接入</span> 后端落地后点亮（I-2 流程）（负反馈也是结果——系统明说「没有」）</span>';
}
function stockRenderAll(){
  stockRenderHead();stockRenderK();stockRenderBoundary();stockRenderHolders();
  stockRenderExecs();stockRenderFin();stockRenderChip();stockRenderPeer();stockRenderFlow();stockRenderAnns();
  stockRenderRatings();stockRenderLinks();
}
window.stockInit=function(){stockRenderAll();};
/* ==================== I-5b F9 补强（并入 stockXxx 族） ==================== */
function stockRenderChip(){
  var c=stockD().chip; if(!c){var e0=document.getElementById('stock-chip');if(e0)e0.innerHTML='<tr><td class="dim">筹码数据缺省（演示口径未内置本标的）</td></tr>';return;}
  var h='<tr><th style="width:64px">报告期</th><th>股东户数（万户） <span class="dim">Holders</span></th><th style="width:82px">环比 <span class="dim">QoQ</span></th><th>主力持仓机构（家） <span class="dim">Institutions</span></th></tr>';
  for(var i=0;i<c.periods.length;i++){
    var qoq=i===0?null:(c.holders[i]-c.holders[i-1])/c.holders[i-1]*100;
    var ins=i===0?null:c.inst[i]-c.inst[i-1];
    h+='<tr><td>'+c.periods[i]+'</td>'
      +'<td><b>'+c.holders[i].toFixed(1)+'</b></td>'
      +'<td class="'+(qoq==null?'dim':(qoq<0?'down':'up'))+'">'+(qoq==null?'—':(qoq>0?'+':'')+qoq.toFixed(1)+'%')+'</td>'
      +'<td>'+c.inst[i]+(ins==null?'':' <span class="'+(ins>=0?'up':'down')+'" style="font-size:10px">'+(ins>=0?'+':'')+ins+'</span>')+'</td></tr>';
  }
  h+='<tr><td colspan="4" style="background:var(--panel2)">股权质押比例 <span class="dim">Pledge Ratio</span>：<b>'+c.pledge+'</b></td></tr>';
  document.getElementById('stock-chip').innerHTML=h;
}
function stockRenderPeer(){
  var b=stockD().biz; if(!b){var e1=document.getElementById('stock-peer');if(e1)e1.innerHTML='<span class="dim">主营/同行数据缺省（演示口径未内置本标的）</span>';return;}
  var seg='';
  b.seg.forEach(function(r){
    seg+='<div class="bar-row"><span>'+r[0]+'</span><div class="bar"><i style="width:'+r[1]+'%"></i></div><span>'+r[1].toFixed(1)+'%</span></div>';
  });
  var t='<tr><th>公司</th><th>PE TTM</th><th>PB</th><th>ROE</th><th>市值</th></tr>';
  b.peers.forEach(function(r){
    t+='<tr'+(r[5]?' class="stock-peer-self"':'')+'><td><b>'+r[0]+'</b>'+(r[5]?' <span class="badge b-pass">本公司</span>':'')+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td><td>'+r[3]+'</td><td>'+r[4]+'</td></tr>';
  });
  document.getElementById('stock-peer').innerHTML=
    '<div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start">'
    +'<div style="flex:1;min-width:220px"><div class="sec-title" style="margin-top:0">主营构成 <span class="dim">Main Business · 营收占比</span></div>'+seg+'</div>'
    +'<div style="flex:1.2;min-width:300px"><div class="sec-title" style="margin-top:0">同行比较 <span class="dim">Peer Comparison</span></div><table>'+t+'</table></div>'
    +'</div>'
    +'<div style="margin-top:10px;font-size:12px">分红送转 <span class="dim">Dividend</span>：<b>'+b.div+'</b></div>';
}
