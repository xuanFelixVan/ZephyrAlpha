$dir = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos"
Get-ChildItem -Path $dir -Filter '*.md' | Where-Object { $_.Name -ne '00_index_trading_decision.md' -and $_.Name -match '^[0-9]' } | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    $ver = "?"
    if ($content -match '(?m)^version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?') {
        $ver = $matches[1]
    }
    "{0,-50} {1}" -f $_.Name, $ver
}
