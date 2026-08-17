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

# Find S7.3 occupancy table region (between "## 7.3" and next "## " heading)
$sec73Start = -1
$sec73End = $lines.Count
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^## 7\.3') { $sec73Start = $i }
    elseif ($sec73Start -ge 0 -and $lines[$i] -match '^## [0-9]') { $sec73End = $i; break }
}
Write-Output "S7.3 region: lines $($sec73Start+1) to $($sec73End)"

# Find S0 catalog region (between "## 0." and "## 1.")
$sec0Start = -1
$sec0End = $lines.Count
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^## 0\.') { $sec0Start = $i }
    elseif ($sec0Start -ge 0 -and $lines[$i] -match '^## 1\.') { $sec0End = $i; break }
}
Write-Output "S0 region: lines $($sec0Start+1) to $($sec0End)"

$fixCount = 0
$fixLog = @()

# Fix S7.3 occupancy table rows
for ($i = $sec73Start; $i -lt $sec73End; $i++) {
    $line = $lines[$i]
    # Match rows starting with "| docname |"
    if ($line -match '^\|\s*(\d{2}_[a-z_]+)\s*\|') {
        $docName = $matches[1]
        if ($actualMap.ContainsKey($docName)) {
            $actual = $actualMap[$docName]
            # Replace the LAST version number on the line (in status column)
            $newLine = [regex]::Replace($line, 'v?[0-9]+\.[0-9]+\.[0-9]+(?=\s*\|?\s*$)', "v$actual")
            # If that didn't work (version not at end), try replacing any v?version in last cell
            if ($newLine -eq $line) {
                # Try: replace version in the last | cell |
                $cells = $line -split '\|'
                if ($cells.Count -ge 2) {
                    $lastCell = $cells[$cells.Count - 2]
                    $newLastCell = [regex]::Replace($lastCell, 'v?[0-9]+\.[0-9]+\.[0-9]+', "v$actual")
                    if ($newLastCell -ne $lastCell) {
                        $cells[$cells.Count - 2] = $newLastCell
                        $newLine = $cells -join '|'
                    }
                }
            }
            if ($newLine -ne $line) {
                # Verify the old version was different
                $oldVers = [regex]::Matches($line, 'v?([0-9]+\.[0-9]+\.[0-9]+)')
                foreach ($ov in $oldVers) {
                    if ($ov.Groups[1].Value -ne $actual) {
                        $fixLog += "L$($i+1) S7.3: $docName $($ov.Groups[1].Value) -> $actual"
                        break
                    }
                }
                $lines[$i] = $newLine
                $fixCount++
            }
        }
    }
}

# Fix S0 catalog rows - replace version in description
for ($i = $sec0Start; $i -lt $sec0End; $i++) {
    $line = $lines[$i]
    if ($line -match '^\|\s*\[(\d{2}_[a-z_]+)\.md\]') {
        $docName = $matches[1]
        if ($actualMap.ContainsKey($docName)) {
            $actual = $actualMap[$docName]
            # Replace version number(s) in the description cell (2nd column)
            $cells = $line -split '\|'
            if ($cells.Count -ge 3) {
                $descCell = $cells[1]
                $newDesc = [regex]::Replace($descCell, 'v[0-9]+\.[0-9]+\.[0-9]+', "v$actual")
                if ($newDesc -ne $descCell) {
                    $cells[1] = $newDesc
                    $newLine = $cells -join '|'
                    $oldVers = [regex]::Matches($descCell, 'v([0-9]+\.[0-9]+\.[0-9]+)')
                    foreach ($ov in $oldVers) {
                        if ($ov.Groups[1].Value -ne $actual) {
                            $fixLog += "L$($i+1) S0: $docName $($ov.Groups[1].Value) -> $actual"
                            break
                        }
                    }
                    $lines[$i] = $newLine
                    $fixCount++
                }
            }
        }
    }
}

# Write back
$lines | Set-Content $indexPath -Encoding UTF8

Write-Output ""
Write-Output "=== Fixed $fixCount lines ==="
$fixLog | ForEach-Object { Write-Output $_ }
