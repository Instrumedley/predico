# Creates and configures the Predico API on Heroku (monorepo backend/).
# Prerequisites: Heroku CLI installed, logged in (`heroku login`), billing on account.
#
# Usage (from repo root):
#   .\scripts\setup-heroku.ps1 -AppName predico-api -FromEmail you@gmail.com

param(
    [string]$AppName = "predico-ab-api",
    [string]$FromEmail = "",
    [string]$FrontendUrl = "https://CHANGE-ME-after-vercel-deploy.vercel.app",
    [switch]$SkipAddons,
    [switch]$EcoDyno
)

$ErrorActionPreference = "Stop"
$Heroku = "C:\Program Files\Heroku\bin\heroku.cmd"

if (-not (Test-Path $Heroku)) {
    Write-Error "Heroku CLI not found. Install from https://devcenter.heroku.com/articles/heroku-cli"
}

function Invoke-Heroku {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$HerokuArgs
    )
    & $Heroku @HerokuArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Heroku command failed: heroku $($HerokuArgs -join ' ')"
    }
}

Write-Host "Checking Heroku login..." -ForegroundColor Cyan
& $Heroku auth:whoami | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Not logged in. Run this first (opens browser):" -ForegroundColor Yellow
    Write-Host "  heroku login" -ForegroundColor White
    exit 1
}
$whoami = & $Heroku auth:whoami
Write-Host "Logged in as: $whoami" -ForegroundColor Green

$secretKey = -join ((48..57 + 65..90 + 97..122 | Get-Random -Count 64 | ForEach-Object { [char]$_ }))

Write-Host "Linking to app '$AppName'..." -ForegroundColor Cyan
& $Heroku apps:info -a $AppName 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "App not found - creating in EU region..." -ForegroundColor Cyan
    Invoke-Heroku create $AppName --region eu
} else {
    Write-Host "App already exists - attaching git remote." -ForegroundColor Yellow
}
Invoke-Heroku git:remote -a $AppName

Write-Host "Configuring monorepo buildpacks (backend/)..." -ForegroundColor Cyan
Invoke-Heroku buildpacks:clear -a $AppName
Invoke-Heroku buildpacks:add -a $AppName https://github.com/timanovsky/subdir-heroku-buildpack
Invoke-Heroku buildpacks:add -a $AppName heroku/python

Write-Host "Setting config vars..." -ForegroundColor Cyan
Invoke-Heroku config:set -a $AppName `
    PROJECT_PATH=backend `
    ENVIRONMENT=production `
    DEBUG=False `
    SECRET_KEY="$secretKey" `
    EMAIL_ENABLED=True `
    EMAIL_BACKEND=sendgrid `
    FRONTEND_URL="$FrontendUrl" `
    CORS_ORIGINS="$FrontendUrl" `
    DB_POOL_SIZE=5 `
    DB_MAX_OVERFLOW=5

if ($FromEmail) {
    Invoke-Heroku config:set -a $AppName "SES_FROM_EMAIL=$FromEmail"
} else {
    Write-Host "Skipping SES_FROM_EMAIL - set it after you choose a sender email." -ForegroundColor Yellow
}

if (-not $SkipAddons) {
    Write-Host "Adding Postgres Essential-0 (~5 USD/mo)..." -ForegroundColor Cyan
    $pg = (& $Heroku addons -a $AppName 2>&1 | Out-String)
    if ($pg -notmatch "heroku-postgresql") {
        Invoke-Heroku addons:create heroku-postgresql:essential-0 -a $AppName
    } else {
        Write-Host "Postgres add-on already present." -ForegroundColor Yellow
    }

    Write-Host "SendGrid Heroku add-on no longer has a free plan." -ForegroundColor Yellow
    Write-Host "Use SendGrid free tier instead (100 emails/day):" -ForegroundColor Yellow
    Write-Host "  1. Sign up at https://signup.sendgrid.com/"
    Write-Host "  2. Create an API key with Mail Send permission"
    Write-Host "  3. Verify sender: $FromEmail"
    Write-Host "  4. heroku config:set SENDGRID_API_KEY=SG.xxxx -a $AppName"
    Write-Host ""
    Write-Host "Optional free alternative: Mailgun starter add-on (requires code change to mailgun backend)." -ForegroundColor DarkYellow
}

if ($EcoDyno) {
    Write-Host "Using Eco dyno (~5 USD/mo, sleeps when idle)..." -ForegroundColor Cyan
    & $Heroku ps:type eco -a $AppName 2>&1 | Out-Null
} else {
    Write-Host "Setting Basic dyno (~7 USD/mo, always on)..." -ForegroundColor Cyan
    & $Heroku ps:type basic -a $AppName 2>&1 | Out-Null
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "Dyno type will apply after first deploy (Procfile not detected yet)." -ForegroundColor Yellow
    Write-Host "After git push heroku main, run: heroku ps:type basic -a $AppName" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Heroku app ready: https://$AppName.herokuapp.com" -ForegroundColor Green
Write-Host "SECRET_KEY was generated and set on Heroku (not printed)." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your next steps:" -ForegroundColor Cyan
Write-Host "  1. SendGrid: sign up free at https://signup.sendgrid.com/ and run:"
Write-Host "     heroku config:set SENDGRID_API_KEY=SG.xxxx -a $AppName"
Write-Host "     (Verify sender: $FromEmail in SendGrid dashboard)"
Write-Host "  2. Deploy API:        git push heroku main"
Write-Host "  3. After deploy:      heroku ps:type basic -a $AppName"
Write-Host "  4. After Vercel:      heroku config:set FRONTEND_URL=... CORS_ORIGINS=... -a $AppName"
Write-Host "  5. Health check:      curl https://$AppName.herokuapp.com/health"
Write-Host ""
