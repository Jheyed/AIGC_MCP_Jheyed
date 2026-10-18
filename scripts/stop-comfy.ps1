$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$comfyExe = Join-Path $projectRoot 'runtime\python\Scripts\comfy.exe'
$comfyWorkspace = Join-Path $projectRoot 'runtime\comfy'

if (-not (Test-Path -LiteralPath $comfyExe)) {
    throw "comfy.exe not found."
}

& $comfyExe --skip-prompt --workspace $comfyWorkspace stop
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

