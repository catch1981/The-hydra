
Param(
  [switch]$Force
)
$envPath = "C:\virendir-assistant\.env"
if ((-not (Test-Path $envPath)) -or $Force) {
  function RandB64([int]$n) {
    $bytes = New-Object byte[] $n; (New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
    [Convert]::ToBase64String($bytes)
  }
  Write-Host "=== Virendir configurator ==="
  $sudo = RandB64 48
  $relay = RandB64 48
  $e2e = RandB64 32
  $proj = Read-Host "Firebase PROJECT ID (press Enter to skip)"
  $dburl = if ($proj) { "https://$proj.firebaseio.com" } else { "" }
  $cred = Read-Host "Path to Firebase service account JSON (press Enter to skip)"
  $eleven = Read-Host "ElevenLabs API Key (press Enter to skip)"
  @"
VIREN_SUDO_TOKEN=$sudo
RELAY_SHARED_SECRET=$relay
MESH_E2E_KEY=$e2e
ENABLE_CLOUD=true
ENABLE_BOSS_BATCH=false
FEATURE_PKG_INSTALL=true
FEATURE_REMOTE_SYNC=true
FEATURE_AUTOCODER=true
FEATURE_CLOUD_TEXT=true
CLOUD_BUDGET_DAILY=2.00
FIREBASE_PROJECT=$proj
FIREBASE_DB_URL=$dburl
FIREBASE_CRED=$cred
ELEVENLABS_API_KEY=$eleven
"@ | Out-File -Encoding ASCII $envPath
  Write-Host "Wrote $envPath"
} else {
  Write-Host ".env exists. Use -Force to overwrite."
}
