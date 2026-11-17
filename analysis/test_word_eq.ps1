$ErrorActionPreference = "Stop"
$src = "C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
$dst = "C:\Users\kukat\Desktop\USA\_extract\test_eq2.docx"
Copy-Item $src $dst -Force
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open($dst)
    $p = $null
    for ($i = 1; $i -le $d.Paragraphs.Count; $i++) {
        if ($d.Paragraphs.Item($i).Range.Text -like "ΔT_phys*") { $p = $d.Paragraphs.Item($i); break }
    }
    if ($p -eq $null) { throw "paragraph not found" }
    $rng = $p.Range
    $txt = $rng.Text
    $cut = $txt.IndexOf("   (Eq.")
    if ($cut -lt 0) { $cut = $txt.Length - 1 }
    $start = $rng.Start
    $lin = $txt.Substring(0, $cut)
    $lin = [regex]::Replace($lin, '([^\s_()]+)_([A-Za-z0-9]+(?:,[A-Za-z0-9]+)*)', '$1_{$2}')
    Write-Output ("LIN: " + $lin)
    $r = $d.Range($start, $start + $cut)
    $r.Text = $lin
    $d.OMaths.Add($r) | Out-Null
    $d.OMaths.BuildUp()
    Write-Output ("omaths=" + $d.OMaths.Count)
    $d.Save()
    $d.Close()
    Write-Output "saved"
} finally {
    $w.Quit()
}
