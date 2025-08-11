
# Quick checks
$HostPort = "127.0.0.1:8765"
try { $h = Invoke-RestMethod "http://$HostPort/healthz" -TimeoutSec 3; Write-Host "healthz:" ($h | ConvertTo-Json -Compress) } catch { Write-Host $_.Exception.Message }
# Sudo test (if token present)
if ($env:VIREN_SUDO_TOKEN) {
  $b = @{ cmd="git --version"; sudo=$true; sudo_token=$env:VIREN_SUDO_TOKEN } | ConvertTo-Json
  try { $r = Invoke-RestMethod -Method Post -Uri "http://$HostPort/tools/shell" -ContentType "application/json" -Body $b; $r | ConvertTo-Json } catch { Write-Host $_.Exception.Message }
}
