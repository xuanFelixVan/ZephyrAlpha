$file_path = "d:\ZephyrAlpha\docs\10_AI_WORKFLOW\SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md"

$content = Get-Content $file_path -Raw -Encoding UTF8

$encoding_map = @{
    'é¦å¸­æ¶æå¸?' = '首席架构师'
    'èæåæå±ç­ææ¹è¿æ¨¡å?' = '舆情分析层短期改进模块'
    'æ°æ®æºæ©å±?' = '数据源扩展'
    'æåæ´æ?' = '最后更新'
    'éç¨æ¨¡å' = '适用模块'
    'æ°æ®æºæ©å±ãæ·±åº¦å­¦ä¹ ææåæãå®æ¶é¢è­¦ç³»ç»?' = '数据源扩展、深度学习情感分析、实时预警系统'
    'æ å' = '标准'
    'ä¸ä¸éåæºæææ¯è§æ ¼æ å?' = '专业量化机构技术规格标准'
    'æ°æ®æºæ©å±æ¨¡åææ¯è§æ ¼' = '数据源扩展模块技术规格'
    'æ·±åº¦å­¦ä¹ ææåææ¨¡åææ¯è§æ ¼' = '深度学习情感分析模块技术规格'
    'å®æ¶é¢è­¦ç³»ç»æ¨¡åææ¯è§æ ¼' = '实时预警系统模块技术规格'
    'æ°æ®å­å?' = '数据字典'
    'éè¯¯å¤çè§è' = '错误处理规范'
    'ç¯å¢åå¤?' = '环境准备'
    'éè¦æç¤º' = '重要提示'
    'å¨å¼å§å®æ½åï¼è¯·åå®æç¯å¢åå¤å·¥ä½ãè¯¦ç»çç¯å¢åå¤æ­¥éª¤è¯·åèåæ¨¡åèå¾ææ¡£ï¼?' = '在开始实施前，请先完成环境准备工作。详细的环境准备步骤请参考各模块蓝图文档。'
    'æ°æ®æºæ©å±æ¨¡åç¯å¢åå¤?' = '数据源扩展模块环境准备'
    'åèææ¡?' = '参考文档'
    'å¦ç±»æ°æ®éææ¨¡åèå¾' = '另类数据集成模块蓝图'
    'APIå¯é¥ï¼TwitterãRedditãFREDï¼?' = 'API密钥（Twitter、Reddit、FRED）'
    'å¿«éªè¯?' = '快速验证'
    'éªè¯ä¾èµåº?' = '验证依赖库'
    'æ¨éæå¡éç½®ï¼é®ä»¶ãå¾®ä¿¡ãTelegramï¼?' = '推送服务配置（邮件、微信、Telegram）'
    'ç¶æ?' = '状态'
    'è®¾è®¡ä¸?' = '设计中'
    'Twitter APIééå¨æ¥å?' = 'Twitter API适配器接口'
    'ç±»å®ä¹?' = '类定义'
}

foreach ($key in $encoding_map.Keys) {
    $content = $content -replace [regex]::Escape($key), $encoding_map[$key]
}

Set-Content $file_path -Value $content -Encoding UTF8

Write-Host "文件编码修复完成！" -ForegroundColor Green
Write-Host ""
Write-Host "前30行:" -ForegroundColor Yellow
$lines = $content -split "`n"
for ($i = 0; $i -lt [Math]::Min(30, $lines.Count); $i++) {
    Write-Host "$($i+1): $($lines[$i])"
}
