/* 功能模块：股票搜索框（sq-search-box）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/stock-search（stock_basic 表）+ localStorage（自选）+ 演示池（fallback）
 * 交互：输入联想、回车选股、加自选、切换自选/持仓 tab
 * 验收单：ACC-F-STOCKQ-SEARCH-BOX
 */
(function(){
  function injectStyles(){
    if(document.getElementById('sq-search-box-styles')) return;
    var st = document.createElement('style');
    st.id = 'sq-search-box-styles';
    st.textContent = '.sq-search-list{max-height:280px;overflow-y:auto}'
      + '.sq-search-item{display:flex;align-items:center;justify-content:space-between;padding:6px 10px;cursor:pointer;border-bottom:1px solid var(--hair);font-size:12px}'
      + '.sq-search-item:hover{background:var(--card7-hi)}'
      + '.sq-search-item .nm{font-weight:600;color:var(--text)}'
      + '.sq-search-item .cd{font-size:10px;color:var(--faint);margin-left:6px}'
      + '.sq-search-item .mkt{font-size:9px;color:var(--faint);margin-left:auto}'
      + '.sq-search-item .fav{color:var(--up);font-size:14px;cursor:pointer;padding:0 4px}'
      + '.sq-search-empty{padding:20px;text-align:center;color:var(--faint);font-size:11px}';
    document.head.appendChild(st);
  }

  function renderResults(box, results, query){
    if(!results.length){
      box.innerHTML = '<div class="sq-search-empty">无匹配股票</div>';
      return;
    }
    var h = '';
    results.forEach(function(r){
      var inFav = (typeof sqFav !== 'undefined' && sqFav.indexOf(r.symbol) >= 0);
      h += '<div class="sq-search-item" onclick="sqSelFromSearch(\'' + r.symbol + '\')">'
        + '<span><span class="nm">' + r.name + '</span><span class="cd">' + r.symbol + '</span></span>'
        + '<span class="mkt">' + (r.market || '') + '</span>'
        + (inFav
          ? '<span class="fav" onclick="event.stopPropagation();sqFavRm(\'' + r.symbol + '\')" title="移出自选">✕</span>'
          : '<span class="fav" onclick="event.stopPropagation();sqFavAdd(\'' + r.symbol + '\')" title="加入自选">＋</span>')
        + '</div>';
    });
    box.innerHTML = h;
  }

  function renderFallback(box, query){
    /* API 失败：回退演示池搜索 */
    var pool = (typeof SQ_POOL !== 'undefined') ? SQ_POOL : [];
    var results = [];
    for(var i = 0; i < pool.length; i++){
      var p = pool[i];
      if(p.nm.indexOf(query) >= 0 || p.code.indexOf(query) >= 0 || p.sym.indexOf(query) >= 0){
        results.push({symbol: p.sym, name: p.nm, market: ''});
      }
    }
    renderResults(box, results, query);
  }

  var mod = {
    id: 'sq-search-box',
    chart: null,
    _el: null,
    _timer: null,

    init: function(chart, ctx){
      this.chart = chart;
      injectStyles();
      this._el = document.getElementById('sq-srch');
      if(!this._el) return;
      this._bind();
    },

    _bind: function(){
      var self = this;
      var input = this._el;
      if(!input) return;

      /* 替换原 oninput，由组件接管 */
      input.oninput = function(){ self._onInput(input.value); };

      /* 回车选第一个 */
      input.onkeydown = function(e){
        if(e.key === 'Enter'){
          var first = document.querySelector('.sq-search-item');
          if(first) first.click();
        }
      };
    },

    _onInput: function(query){
      var self = this;
      clearTimeout(this._timer);
      this._timer = setTimeout(function(){
        self._search(query.trim());
      }, 300);
    },

    _search: function(query){
      var listBox = document.getElementById('sq-list');
      if(!listBox) return;
      if(!query){ listBox.innerHTML = ''; return; }

      if(window.ZK && ZK.api && ZK.api.fetchStockSearch){
        ZK.api.fetchStockSearch(query).then(function(r){
          if(r && r.ok && r.data){
            renderResults(listBox, r.data, query);
          } else {
            renderFallback(listBox, query);
          }
        }).catch(function(){
          renderFallback(listBox, query);
        });
      } else {
        renderFallback(listBox, query);
      }
    },

    render: function(d){ /* 无独立 render，由输入驱动 */ },
    destroy: function(){
      clearTimeout(this._timer);
      if(this._el){ this._el.oninput = null; this._el.onkeydown = null; }
      this._el = null;
    }
  };

  ZK.registerFeature(mod);
  if(typeof sqCur !== 'undefined'){ mod.init(); }
})();
