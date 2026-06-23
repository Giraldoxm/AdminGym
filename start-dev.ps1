# Lanza backend (uvicorn), frontend (npm run dev) y bridge (HuelleroBridge.exe)
# en ventanas separadas. Cerra cada ventana para detener su proceso.
#
# Flags:
#   -NoBridge    no lanza el huellero (util si lo tenes corriendo via Task Scheduler)
#   -NoBackend   no lanza el backend
#   -NoFrontend  no lanza el frontend

param(
    [switch]$NoBridge,
    [switch]$NoBackend,
    [switch]$NoFrontend
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "=== JainSportBox - dev launcher ===" -ForegroundColor Cyan

# 1. Backend (uvicorn dentro del venv)
if (-not $NoBackend) {
    $backendDir = Join-Path $root "backend"
    $venvActivate = Join-Path $root "venv\Scripts\Activate.ps1"

    if (-not (Test-Path (Join-Path $backendDir ".env"))) {
        Write-Host "[WARN] backend/.env no existe. Copia .env.example antes de seguir." -ForegroundColor Yellow
    }

    Write-Host "[1/3] Backend  -> http://localhost:8000" -ForegroundColor Green
    $backendCmd = "`$Host.UI.RawUI.WindowTitle='JainSportBox - Backend'; & '$venvActivate'; uvicorn main:app --reload --port 8000"
    Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd
    ) -WorkingDirectory $backendDir
}

# 2. Frontend
if (-not $NoFrontend) {
    $frontendDir = Join-Path $root "frontend"
    Write-Host "[2/3] Frontend -> http://localhost:5173" -ForegroundColor Green
    $frontendCmd = "`$Host.UI.RawUI.WindowTitle='JainSportBox - Frontend'; npm run dev"
    Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $frontendCmd
    ) -WorkingDirectory $frontendDir
}

# 3. Bridge (si no esta ya corriendo)
if (-not $NoBridge) {
    $running = Get-Process -Name HuelleroBridge -ErrorAction SilentlyContinue
    if ($running) {
        Write-Host "[3/3] Bridge   -> ya corriendo (PID $($running.Id)), no se relanza." -ForegroundColor DarkYellow
    } else {
        $bridgeExe = Join-Path $root "servicio_biometrico\bin\Debug\net48\HuelleroBridge.exe"
        if (-not (Test-Path $bridgeExe)) {
            Write-Host "[3/3] Bridge   -> NO encontrado. Compila con: dotnet build servicio_biometrico\HuelleroBridge.csproj" -ForegroundColor Red
        } else {
            Write-Host "[3/3] Bridge   -> arrancando como admin (acepta el prompt UAC)" -ForegroundColor Green
            Start-Process -FilePath $bridgeExe -Verb RunAs
        }
    }
}

Write-Host ""
Write-Host "Todo lanzado. Cerra cada ventana para detener su proceso." -ForegroundColor Cyan
Write-Host "Logs del bridge en vivo: servicio_biometrico\ver-logs.cmd" -ForegroundColor DarkGray
