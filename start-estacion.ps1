# Estación de huella / recepción (Capa 6 del despliegue).
#
# Sirve el frontend de producción LOCALMENTE en http://localhost y arranca el
# bridge. El navegador en http://localhost puede hablar con el bridge en
# http://localhost:8001 (mismo esquema) y con el backend cloud por HTTPS
# (http→https permitido), evitando el bloqueo mixed-content que sufriría la PWA
# en la nube.
#
# Uso típico en la PC del gym:
#   .\start-estacion.ps1 -ApiUrl https://api.tudominio.com
#
# Flags:
#   -ApiUrl <url>  backend cloud (HTTPS). Si se omite, usa VITE_API_URL del
#                  entorno o de frontend/.env.local / .env.production.
#   -Port <n>      puerto local (default 80; 80 requiere ejecutar como admin).
#   -SkipBuild     no recompila; sirve el dist/ existente (arranque rápido).
#   -NoBridge      no lanza el huellero (útil si ya corre via Task Scheduler).

param(
    [string]$ApiUrl,
    [int]$Port = 80,
    [switch]$SkipBuild,
    [switch]$NoBridge
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$frontendDir = Join-Path $root "frontend"

Write-Host "=== JainSportBox - estación de recepción ===" -ForegroundColor Cyan

# 1. Frontend de producción (build + serve local)
if (-not $SkipBuild) {
    if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
        Write-Host "[frontend] instalando dependencias (npm install)..." -ForegroundColor DarkGray
        Push-Location $frontendDir; npm install; Pop-Location
    }

    if ($ApiUrl) {
        $env:VITE_API_URL = $ApiUrl
        Write-Host "[frontend] build con VITE_API_URL=$ApiUrl" -ForegroundColor Green
    } else {
        Write-Host "[frontend] build usando VITE_API_URL del entorno/.env (no se pasó -ApiUrl)" -ForegroundColor Yellow
    }
    if ($env:VITE_API_URL -and $env:VITE_API_URL -notlike "https://*") {
        Write-Host "[WARN] VITE_API_URL no es HTTPS: el X-Bridge-Secret y los datos viajarían en claro." -ForegroundColor Yellow
    }

    Push-Location $frontendDir
    npm run build
    Pop-Location
} else {
    Write-Host "[frontend] -SkipBuild: sirviendo dist/ existente" -ForegroundColor DarkYellow
}

$distDir = Join-Path $frontendDir "dist"
if (-not (Test-Path $distDir)) {
    Write-Host "[ERROR] No existe frontend/dist. Corré sin -SkipBuild para generarlo." -ForegroundColor Red
    exit 1
}

Write-Host "[serve]    -> http://localhost:$Port  (vite preview, fallback SPA)" -ForegroundColor Green
if ($Port -eq 80) {
    Write-Host "           (puerto 80 requiere ejecutar este script como Administrador)" -ForegroundColor DarkGray
}
$serveCmd = "`$Host.UI.RawUI.WindowTitle='JainSportBox - Estación'; npm run preview -- --port $Port"
Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $serveCmd
) -WorkingDirectory $frontendDir

# 2. Bridge (si no está ya corriendo)
if (-not $NoBridge) {
    $running = Get-Process -Name HuelleroBridge -ErrorAction SilentlyContinue
    if ($running) {
        Write-Host "[bridge]   -> ya corriendo (PID $($running.Id)), no se relanza." -ForegroundColor DarkYellow
    } else {
        $bridgeExe = Join-Path $root "servicio_biometrico\bin\Debug\net48\HuelleroBridge.exe"
        if (-not (Test-Path $bridgeExe)) {
            Write-Host "[bridge]   -> NO encontrado. Compila con: dotnet build servicio_biometrico\HuelleroBridge.csproj" -ForegroundColor Red
        } else {
            Write-Host "[bridge]   -> arrancando como admin (acepta el prompt UAC)" -ForegroundColor Green
            Start-Process -FilePath $bridgeExe -Verb RunAs
        }
    }
}

Write-Host ""
Write-Host "Estación lista. Abrí http://localhost:$Port en el navegador de recepción." -ForegroundColor Cyan
Write-Host "Logs del bridge en vivo: servicio_biometrico\ver-logs.cmd" -ForegroundColor DarkGray
