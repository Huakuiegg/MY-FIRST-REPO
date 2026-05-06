$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$input = Join-Path $here "project_flowchart.md"
$output = Join-Path $here "project_flowchart.png"

if (-not (Test-Path $input)) {
  throw "Missing file: $input"
}

Write-Host "Exporting Mermaid flowchart to PNG..."
Write-Host "Input : $input"
Write-Host "Output: $output"
Write-Host ""

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
  throw "npx not found. Install Node.js first, or use https://mermaid.live to export."
}

Push-Location $here
try {
  # Uses Mermaid CLI without installing globally
  npx --yes @mermaid-js/mermaid-cli -i $input -o $output -b transparent
  Write-Host "Done."
} finally {
  Pop-Location
}

