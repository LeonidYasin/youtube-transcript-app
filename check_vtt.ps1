# PowerShell script to check VTT file content

# List files matching the pattern
Write-Host "Files matching pattern *qp0HIF3SfI4*:"
Get-ChildItem -Path . -Filter "*qp0HIF3SfI4*" | Select-Object Name, Length, LastWriteTime

# Find VTT files
$vttFiles = Get-ChildItem -Path . -Filter "*.vtt"

if ($vttFiles) {
    Write-Host "`nFound VTT files:"
    foreach ($file in $vttFiles) {
        Write-Host "`nFile: $($file.Name)"
        Write-Host "Size: $($file.Length) bytes"
        
        # Read first 200 bytes as hex
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName) | Select-Object -First 200
        $hex = -join ($bytes | ForEach-Object { $_.ToString("x2") + " " })
        Write-Host "`nFirst 200 bytes (hex):"
        $hex
        
        # Try to read as text with different encodings
        $encodings = @(
            @{Name="UTF-8"; Encoding=[System.Text.Encoding]::UTF8},
            @{Name="UTF-16"; Encoding=[System.Text.Encoding]::Unicode},
            @{Name="Windows-1251"; Encoding=[System.Text.Encoding]::GetEncoding(1251)},
            @{Name="Latin1"; Encoding=[System.Text.Encoding]::GetEncoding(28591)}
        )
        
        foreach ($enc in $encodings) {
            try {
                $content = [System.IO.File]::ReadAllText($file.FullName, $enc.Encoding)
                Write-Host "`n--- $($enc.Name) ---"
                Write-Host $content.Substring(0, [Math]::Min(200, $content.Length))
            } catch {
                Write-Host "`n--- $($enc.Name) Error ---"
                Write-Host $_.Exception.Message
            }
        }
    }
} else {
    Write-Host "No VTT files found in the current directory."
}
