$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'
$memos = Get-ChildItem $dir -Filter '*.md' | Where-Object { $_.Name -match '^\d+_' } | Sort-Object Name
Write-Output ("Total memos: " + $memos.Count)
Write-Output ""
foreach ($memo in $memos) {
    $content = Get-Content $memo.FullName -Encoding UTF8 -TotalCount 12
    $ver = ''
    $status = ''
    $title = ''
    foreach ($line in $content) {
        if ($line -match 'version:\s*"?(\d+\.\d+\.\d+)"?') { $ver = $matches[1] }
        if ($line -match 'status:\s*(\w+)') { $status = $matches[1] }
        if ($line -match 'title:\s*(.+)') { $title = $matches[1].Trim() }
    }
    $num = $memo.BaseName -replace '^(\d+)_.*', '$1'
    Write-Output ("{0,3}  v{1,-10} {2,-10} {3}" -f $num, $ver, $status, $title)
}
