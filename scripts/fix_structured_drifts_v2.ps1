$dir = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos"
$indexPath = Join-Path $dir "00_index_trading_decision.md"
$lines = Get-Content $indexPath -Encoding UTF8

# Get actual versions
$files = Get-ChildItem -Path $dir -Filter '*.md' | Where-Object { $_.Name -ne '00_index_trading_decision.md' }
$actualMap = @{}
foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?') {
        $actualMap[$f.BaseName] = $matches[1]
    }
}

# Find revision history start
$revStart = $lines.Count
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\|\s*\u65E5\u671F\s*\|') { $revStart = $i; break }
}

$fixCount = 0
$fixLog = @()

for ($i = 0; $i -lt $revStart; $i++) {
    $line = $lines[$i]
    $modified = $false

    foreach ($name in $actualMap.Keys) {
        $actual = $actualMap[$name]
        if ($line -notmatch [regex]::Escape($name)) { continue }

        # Pattern A: S0 catalog "| [name.md](name.md) | desc with vOLD | active |"
        # Replace vOLD in description (2nd content column = cells[2])
        if ($line -match "^\|\s*\[$([regex]::Escape($name))\.md\]") {
            $cells = $line -split '\|'
            if ($cells.Count -ge 4) {
                for ($c = 2; $c -lt $cells.Count - 1; $c++) {
                    $oldCell = $cells[$c]
                    $newCell = [regex]::Replace($oldCell, 'v[0-9]+\.[0-9]+\.[0-9]+', "v$actual")
                    if ($newCell -ne $oldCell) {
                        $oldVer = [regex]::Match($oldCell, 'v([0-9]+\.[0-9]+\.[0-9]+)').Groups[1].Value
                        if ($oldVer -and $oldVer -ne $actual) {
                            $cells[$c] = $newCell
                            $fixLog += "L$($i+1) S0: $name v$oldVer -> v$actual"
                            $modified = $true
                        }
                    }
                }
                if ($modified) { $lines[$i] = $cells -join '|' }
            }
            continue
        }

        # Pattern B: S7.3 occupancy "| name | topic | owner | status with vOLD |"
        if ($line -match "^\|\s*$([regex]::Escape($name))\s*\|") {
            $cells = $line -split '\|'
            if ($cells.Count -ge 4) {
                # Replace version in last content cell (status column)
                $lastIdx = $cells.Count - 2
                $oldCell = $cells[$lastIdx]
                $newCell = [regex]::Replace($oldCell, 'v[0-9]+\.[0-9]+\.[0-9]+', "v$actual")
                if ($newCell -ne $oldCell) {
                    $oldVer = [regex]::Match($oldCell, 'v([0-9]+\.[0-9]+\.[0-9]+)').Groups[1].Value
                    if ($oldVer -and $oldVer -ne $actual) {
                        $cells[$lastIdx] = $newCell
                        $lines[$i] = $cells -join '|'
                        $fixLog += "L$($i+1) S7.3: $name v$oldVer -> v$actual"
                        $modified = $true
                    }
                }
            }
            continue
        }

        # Pattern C: S3 product "| \u4EA7\u51FA\u7269 | [name](name.md) vOLD |"
        if ($line -match "^\|\s*\u4EA7\u51FA\u7269\s*\|\s*\[$([regex]::Escape($name))\]") {
            $oldLine = $lines[$i]
            $newLine = [regex]::Replace($oldLine, "(\[$([regex]::Escape($name))\]\($([regex]::Escape($name))\.md\)\s+)v[0-9]+\.[0-9]+\.[0-9]+", "`${1}v$actual")
            if ($newLine -ne $oldLine) {
                $lines[$i] = $newLine
                $fixLog += "L$($i+1) S3prod: $name -> v$actual"
                $modified = $true
            }
            continue
        }

        # Pattern D: S3 status "| \u72B6\u6001 | \u2705 \u5DF2\u5B9A\u7A3F vOLD\uFF08[name]"
        if ($line -match "^\|\s*\u72B6\u6001\s*\|.*\[$([regex]::Escape($name))\]") {
            $oldLine = $lines[$i]
            $newLine = [regex]::Replace($oldLine, '(\| \u72B6\u6001 \| \u2705 \u5DF2\u5B9A\u7A3F )v[0-9]+\.[0-9]+\.[0-9]+', "`${1}v$actual", 1)
            if ($newLine -ne $oldLine) {
                $oldVer = [regex]::Match($oldLine, '(\| \u72B6\u6001 \| \u2705 \u5DF2\u5B9A\u7A3F )v([0-9]+\.[0-9]+\.[0-9]+)').Groups[2].Value
                if ($oldVer -ne $actual) {
                    $lines[$i] = $newLine
                    $fixLog += "L$($i+1) S3status: $name v$oldVer -> v$actual"
                    $modified = $true
                }
            }
            continue
        }
    }
}

# Write back
$lines | Set-Content $indexPath -Encoding UTF8

Write-Output "=== Fixed $fixCount lines ==="
$fixLog | ForEach-Object { Write-Output $_ }
