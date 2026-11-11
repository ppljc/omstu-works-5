param([string]$src, [string]$dst)
New-Item -ItemType Directory -Force -Path $dst | Out-Null
$app = New-Object -ComObject PowerPoint.Application
try {
    $pres = $app.Presentations.Open($src, $true, $false, $false)
    $pres.Export($dst, 'PNG', 1280, 720)
    $pres.Close()
    Write-Output 'EXPORTED'
} finally {
    $app.Quit()
}
