$dir = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos"
$indexPath = Join-Path $dir "00_index_trading_decision.md"
$indexLines = Get-Content $indexPath

# Find revision history start (first line matching "| 日期 |")
$revStart = 0
for ($i = 0; $i -lt $indexLines.Count; $i++) {
    if ($indexLines[$i] -match '^\|\s*日期\s*\|') { $revStart = $i; break }
}

# Get actual versions
$files = Get-ChildItem -Path $dir -Filter '*.md' | Where-Object { $_.Name -ne '00_index_trading_decision.md' }
$actualMap = @{}
foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw
    if ($content -match '(?m)^version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?') {
        $actualMap[$f.BaseName] = $matches[1]
    }
}

# For each document, check ONLY lines in §0 catalog, §7.3 occupancy table, §3 status lines
# These are structured lines where one document appears per row
$realDrifts = @()

foreach ($name in $actualMap.Keys) {
    $actual = $actualMap[$name]
    for ($i = 0; $i -lt $revStart; $i++) {
        $line = $indexLines[$i]
        if ($line -notmatch [regex]::Escape($name)) { continue }
        
        # Skip lines that contain multiple doc references (§2 snapshot rows list many docs)
        # Focus on structured single-doc lines: §0 catalog (| [name.md]), §7.3 (| name |), §3 status (| 状态 | ...)
        $isStructured = $false
        if ($line -match "^\| \[$([regex]::Escape($name))\.md\]") { $isStructured = $true }  # §0 catalog
        if ($line -match "^\| $([regex]::Escape($name)) \|") { $isStructured = $true }  # §7.3 occupancy
        if ($line -match "^\| 状态 \|") { $isStructured = $true }  # §3 status row
        if ($line -match "^\| 产出物 \|") { $isStructured = $true }  # §3 product row
        
        if (-not $isStructured) { continue }
        
        # Find version numbers near the doc name on this line
        $vers = [regex]::Matches($line, 'v?([0-9]+\.[0-9]+\.[0-9]+)')
        foreach ($v in $vers) {
            $refVer = $v.Groups[1].Value
            if ($refVer -ne $actual) {
                $realDrifts += "L$($i+1): $name | ref=$refVer | actual=$actual | $($line.Substring(0, [Math]::Min(80, $line.Length)))"
            }
        }
    }
}

if ($realDrifts.Count -eq 0) {
    Write-Output "✅ ZERO DRIFT in structured current-state sections (§0 catalog, §7.3 occupancy, §3 status/product rows)"
} else {
    Write-Output "=== Remaining drifts in structured sections ==="
    $realDrifts | ForEach-Object { Write-Output $_ }
}
