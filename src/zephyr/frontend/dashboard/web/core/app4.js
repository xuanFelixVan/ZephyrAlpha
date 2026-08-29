/* 长城任务四·批 3：新闻两天滚动窗（演示数据，点击展开详情+分析） */
(function(){
var FEED=[
 ['11:42','半导体国产替代政策细则落地：三期基金注资提速','财联社','利好','可预测','A','半导体/中芯国际','政策面两月前已有预期，属兑现型利好——警惕利好出尽；但注资额度超一致预期 12%，增量信息有效。'],
 ['11:05','宁德时代三季报预增 18% 超一致预期','研报','利好','可预测','A','宁德时代/新能源','一致预期 +12% vs 实际 +18%=超预期；PEAD 历史漂移统计 20 日均值 +2.3%（MOD-SIG-110）。'],
 ['10:38','央行开展 3800 亿 MLF 操作 利率持平','央行','中性','可预测','B','银行/流动性','量增价平=维持宽松不加码；符合预期，市场反应平淡属正常。'],
 ['10:12','某消费电子公司发布新品 股价高开低走','东财','利好','可预测','B','消费电子','该涨不涨=弱——利好兑现出货特征，预期差判定=低于预期。'],
 ['09:55','美联储官员：通胀仍有韧性 不急于降息','外媒','利空','突发','B','全球风险资产','偏鹰——隔夜传导 β 弱影响（MOD-SIG-117），A 股开盘承压有限。'],
 ['09:31','某医药公司集采传闻 股价不跌反涨','财联社','利空','突发','A','创新药','该跌不跌=强——利空释放完就是利好；预期差判定=强。'],
 ['08-27 22:14','存储芯片现货价连续 6 周上涨','东财','利好','可预测','B','半导体/存储','涨价周期延续——去年存储涨价新闻首发时板块未动，本轮已提前定价。'],
 ['08-27 18:40','农业农村部：秋粮长势总体良好','新华社','中性','可预测','C','农业','常规通报；首次出现的涨价预期类新闻才有埋伏价值，本条无增量。'],
 ['08-27 16:20','证监会就程序化交易新规答记者问','证监会','中性','可预测','B','券商/量化','撤单率/申报笔数红线重申——与本系统 cancel_rate_guard 口径一致。'],
 ['08-27 14:05','韩国半导体出口同比 +21%','外媒','利好','可预测','B','半导体','韩股开盘早=盘前预案输入（R13）；全球半导体景气共振。']];
var feed=document.getElementById('news-feed');if(!feed)return;
var html='<table><tr><th style="width:80px">时间</th><th>标题</th><th>来源</th><th>倾向</th><th>可预测</th><th>影响</th></tr>';
FEED.forEach(function(n,i){
 html+='<tr class="news-row" onclick="newsTgl('+i+')" style="cursor:pointer"><td class="dim">'+n[0]+'</td><td>'+n[1]+'</td><td class="dim">'+n[2]+'</td><td><span class="badge '+(n[3]==='利好'?'b-buy':(n[3]==='利空'?'b-sell':'b-na'))+'">'+n[3]+'</span></td><td class="dim">'+n[4]+'</td><td><span class="badge '+(n[5]==='A'?'b-warn':'b-na')+'">'+n[5]+'</span></td></tr>';
 html+='<tr id="news-d-'+i+'" style="display:none"><td></td><td colspan="5"><div style="background:var(--input);border:1px solid var(--border);border-radius:6px;padding:10px;font-size:12px"><b>详情</b>：'+n[1]+'（库内全文 I-2）<br><b>分析</b>：'+n[7]+'<br><b>关联标的</b>：<span class="dim">'+n[6]+'</span> · <b>来源</b>：<span class="dim">'+n[2]+'（原文链接：库内无 URL 字段，待接入）</span> <span class="vfy-wrap" style="float:right">分析对不对：<button class="vfy-no" onclick="event.stopPropagation();ovxVfy(this,0)">✗</button></span></div></td></tr>';
});
feed.innerHTML=html+'</table>';
})();
function newsTgl(i){var d=document.getElementById('news-d-'+i);if(d)d.style.display=d.style.display==='none'?'':'none';}
