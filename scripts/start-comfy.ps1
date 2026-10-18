$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeScripts = Join-Path $projectRoot 'runtime\python\Scripts'
$comfyExe = Join-Path $runtimeScripts 'comfy.exe'
$comfyWorkspace = Join-Path $projectRoot 'runtime\comfy'

if (-not (Test-Path -LiteralPath $comfyExe)) {
    throw "comfy.exe not found. Follow docs/INSTALLATION_PLAN.md first."
}

if (-not (Test-Path -LiteralPath (Join-Path $comfyWorkspace 'main.py'))) {
    throw "ComfyUI workspace not found. Follow docs/INSTALLATION_PLAN.md first."
}

# comfy-cli's Windows background launcher re-invokes `comfy` by name.
# Keep this PATH adjustment local to this script process.
$env:PATH = "$runtimeScripts;$env:PATH"

& $comfyExe --skip-prompt --workspace $comfyWorkspace launch --background
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

