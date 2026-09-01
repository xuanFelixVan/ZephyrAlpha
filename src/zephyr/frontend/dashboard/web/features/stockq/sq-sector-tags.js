/* 功能模块：行业归属标签（sq-sector-tags）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/stock-header（stock_basic.industry + board，argMax 最新口径）
 * 交互：点击标签跳转板块全景页（go('sector')）
 * 四态灯：以迷你状态点呈现（绿=真源 / 黄=延迟 / 红=断线·演示 / 灰=未启动，DS-12）
 * 演示回退：STOCKQ_D[sqCur].tags（仅 3 只演示标的）或占位标签
 * 验收单：ACC-F-STOCKQ-SECTOR-TAGS
 */
(function(){
  function injectStyles(){
    if(document.getElementById('sq-sector-tags-styles')) return;
    var st = document.createElement('style');
    st.id = 'sq-sector-tags-styles';
    st.textContent = '.sq-sector-tags{display:flex;align-items:center;gap:4px;flex-wrap:wrap}'
      + '.sq-sector-tags .badge{cursor:pointer}'
      + '.sq-sector-tags .badge:hover{border-color:var(--blue)}'
      + '.sq-tag-dot{width:6px;height:6px;border-radius:50%;cursor:help;flex:none}'
      + '.sq-tag-dot.dm-真源{background:#25A750}'
      + '.sq-tag-dot.dm-延迟{background:#F0B90B}'
      + '.sq-tag-dot.dm-断线{background:#CA3F64}'
      + '.sq-tag-dot.dm-未启动{background:var(--faint)}';
    document.head.appendChild(st);
  }

  var DOT_TITLE = '数据源状态灯（DS-12）：绿=真源（stock_basic 行业/板块） / 黄=延迟 / 红=断线（回退演示标签） / 灰=服务未启动';

  var mod = {
    id: 'sq-sector-tags',
    chart: null,

    init: function(chart, ctx){
      this.chart = chart;
      injectStyles();
    },

    _tagsHtml: function(tags, mode){
      var h = '<div class="sq-sector-tags">';
      tags.forEach(function(t){
        h += '<span class="badge b-na" title="查看板块全景" onclick="go(\'sector\')">' + t + '</span>';
      });
      return h + '<span class="sq-tag-dot dm-' + mode + '" title="' + DOT_TITLE + '"></span></div>';
    },

    render: function(d){
      var box = document.getElementById('sq-sector-tags');
      if(!box) return;
      var sym = (typeof sqCur !== 'undefined') ? sqCur : null;

      /* 第一拍：演示回退，API 回来后第二拍覆盖 */
      var demo = (typeof STOCKQ_D !== 'undefined' && sym) ? STOCKQ_D[sym] : null;
      if(demo && demo.tags){
        box.innerHTML = this._tagsHtml(demo.tags, '断线');
      } else {
        box.innerHTML = this._tagsHtml(['行业待接入'], '未启动');
      }

      var self = this;
      if(window.ZK && ZK.api && ZK.api.fetchStockHeader && sym){
        ZK.api.fetchStockHeader(sym).then(function(r){
          if(!(r && r.ok && r.data)) return;
          var v = r.data;
          var tags = [];
          if(v.industry) tags.push(v.industry);
          if(v.board && tags.indexOf(v.board) < 0) tags.push(v.board);
          if(!tags.length) tags.push('行业未分类');
          box.innerHTML = self._tagsHtml(tags, '真源');
        }).catch(function(){ /* 静默：演示回退已标"断线" */ });
      }
    },

    destroy: function(){ /* 纯 DOM 渲染，无定时器/监听需清理 */ }
  };

  ZK.registerFeature(mod);
  /* 加载链竞态兜底：若 sqRenderInfo 已执行（容器已在 DOM），注册后主动渲染 */
  if(typeof sqCur !== 'undefined' && document.getElementById('sq-sector-tags')){ mod.render(); }
})();
