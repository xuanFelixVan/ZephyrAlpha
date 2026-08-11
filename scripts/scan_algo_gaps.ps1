$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'
$memos = Get-ChildItem $dir -Filter '*.md' | Where-Object { $_.Name -match '^\d+_' } | Sort-Object Name
$keywords = 'TODO|待施工|待实现|NotImplementedError|待裁定.*施工|施工缺失|算法缺失|缺施工|未实现.*算法|伪代码.*待|gap.*施工'
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
