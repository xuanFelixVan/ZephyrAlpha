$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'
$memos = Get-ChildItem $dir -Filter '*.md' | Where-Object { $_.Name -match '^\d+_' } | Sort-Object Name
$keywords = 'TODO|\u5F85\u65BD\u5DE5|\u5F85\u5B9E\u73B0|NotImplementedError|\u5F85\u88C1\u5B9A.*\u65BD\u5DE5|\u65BD\u5DE5\u7F3A\u5931|\u7B97\u6CD5\u7F3A\u5931|\u7F3A\u65BD\u5DE5|\u672A\u5B9E\u73B0.*\u7B97\u6CD5|\u4F2A\u4EE3\u7801.*\u5F85|gap.*\u65BD\u5DE5'
foreach ($memo in $memos) {
    $lines = Get-Content $memo.FullName -Encoding UTF8
    $hits = @()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match $keywords) {
            # Skip revision records
            if ($lines[$i] -match '^\| 2026-08') { continue }
            $hits += "L$($i+1): $($lines[$i].Trim())"
        }
    }
    if ($hits.Count -gt 0) {
        Write-Output "=== $($memo.BaseName) ($($hits.Count) hits) ==="
        $hits | Select-Object -First 5 | ForEach-Object {
            $s = $_
            if ($s.Length -gt 180) { $s = $s.Substring(0, 180) + '...' }
            Write-Output "  $s"
        }
        if ($hits.Count -gt 5) { Write-Output "  ... and $($hits.Count - 5) more" }
        Write-Output ""
    }
}
