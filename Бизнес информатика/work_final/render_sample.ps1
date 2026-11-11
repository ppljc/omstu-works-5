$src = 'C:\Users\ppljc\omstu-works-5\Бизнес информатика\БИ\БИитог.pptx'
$dst = 'C:\Users\ppljc\omstu-works-5\Бизнес информатика\work_final\sample_slides'
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
