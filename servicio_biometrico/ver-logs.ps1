$logPath = Join-Path $PSScriptRoot "bin\Debug\net48\bridge.log"

if (-not (Test-Path $logPath)) {
    Write-Host "No existe $logPath todavia." -ForegroundColor Yellow
    Write-Host "Arranca el bridge primero (HuelleroBridge.exe)." -ForegroundColor Yellow
    exit 1
}

$Host.UI.RawUI.WindowTitle = "Huellero - Logs en vivo"
Write-Host "=== Logs en vivo del huellero ===" -ForegroundColor Cyan
Write-Host "Archivo: $logPath" -ForegroundColor DarkGray
Write-Host "Ctrl+C para salir." -ForegroundColor DarkGray
Write-Host ""

Get-Content -Path $logPath -Wait -Tail 30 -Encoding UTF8 | ForEach-Object {
    $line = $_
    if     ($line -match '\[ERROR\]|error|Error')          { Write-Host $line -ForegroundColor Red }
    elseif ($line -match '\[WARN\]')                       { Write-Host $line -ForegroundColor Yellow }
    elseif ($line -match '\[HUELLERO\]')                   { Write-Host $line -ForegroundColor Green }
    elseif ($line -match '\[HTTP\]|\[WS\]')                { Write-Host $line -ForegroundColor Cyan }
    elseif ($line -match '=====')                          { Write-Host $line -ForegroundColor Magenta }
    else                                                   { Write-Host $line }
}
