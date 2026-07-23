param(
    [string]$Root = "C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon",
    [string]$ChoiceFile = "$env:TEMP\.hal_launchpad_choice"
)

function BoxLine($t) { Write-Host ('  {0}' -f $t) -ForegroundColor Cyan }
function TitleLine($t) { Write-Host ('  {0}' -f $t) -ForegroundColor Red -BackgroundColor Black }
function MenuItem($num, $app, $url) {
    Write-Host ('  [{0}] ' -f $num) -ForegroundColor Yellow -NoNewline
    Write-Host ('{0,-18}' -f $app) -ForegroundColor White -NoNewline
    Write-Host $url -ForegroundColor Green
}

function ShowMenu {
    Clear-Host
    Write-Host ''
    BoxLine '+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+'
    TitleLine '  _   _    _      _         _                      _       _   _  '
    TitleLine ' | | | |  | |    | |       | |     __ _    ___    | |     (_) | | '
    TitleLine ' | |_| |  | |    | |       | |    / _` |  / _ \   | |     | | | | '
    TitleLine ' |  _  |  | |    | |       | |   | (_| | |  __/   | |___  | | | | '
    TitleLine ' | | | |  | |    | |       | |    \__, |  \___|   |_____| |_| |_| '
    TitleLine ' |_| |_|  |____| |_____|  |_____| |___/                            '
    BoxLine '+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+'
    Write-Host ''
    Write-Host '      O====O' -ForegroundColor Yellow
    Write-Host '      ||  ||     HAL HACKATHON CONTROL CENTER' -ForegroundColor Yellow
    Write-Host '     /| [] |\' -ForegroundColor Yellow
    Write-Host '    / | <> | \    Local Streamlit App Launcher' -ForegroundColor Yellow
    Write-Host '   /  |____|  \' -ForegroundColor Yellow
    Write-Host "  '==/      \=='" -ForegroundColor Yellow
    Write-Host '     | 2026 |' -ForegroundColor Yellow
    Write-Host '     |______|' -ForegroundColor Yellow
    Write-Host ''
    BoxLine '-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
    Write-Host ''
    MenuItem '1' 'HAL Guardian'     'http://localhost:8501'
    MenuItem '2' 'HAL Budget'       'http://localhost:8502'
    MenuItem '3' 'miseBot'          'http://localhost:8503'
    Write-Host '  [4] Launch ALL THREE' -ForegroundColor Magenta
    Write-Host '  [V] View IP addresses / URLs' -ForegroundColor Cyan
    Write-Host '  [Q] Quit launcher' -ForegroundColor DarkGray
    Write-Host ''
    BoxLine '-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
    Write-Host '  Close browser tab first, then Ctrl+C in app window and Y to stop.' -ForegroundColor DarkYellow
    Write-Host ''
    $c = Read-Host '  Enter choice [1-4, V, Q]'
    $c | Out-File -FilePath $ChoiceFile -Encoding ascii -NoNewline
}

function ShowIps {
    Clear-Host
    function BoxLine($t) { Write-Host ('  {0}' -f $t) -ForegroundColor Cyan }
    function CenterLine($t) { Write-Host ('  {0}' -f $t) -ForegroundColor Magenta }

    $local = 'localhost'
    $net = (Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp | Select-Object -First 1).IPAddress
    if (-not $net) { $net = '192.168.x.x' }
    try { $ext = (Invoke-WebRequest -Uri 'https://api.ipify.org' -UseBasicParsing -TimeoutSec 5).Content.Trim() } catch { $ext = 'unavailable' }

    Write-Host ''
    BoxLine '+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+'
    CenterLine '           LAUNCHPAD IP / URL VIEWPORT'
    BoxLine '+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+'
    Write-Host ''
    Write-Host '  Local Host:    ' -NoNewline -ForegroundColor White; Write-Host ('http://{0}' -f $local) -ForegroundColor Green
    Write-Host '  Local Network: ' -NoNewline -ForegroundColor White; Write-Host ('http://{0}' -f $net) -ForegroundColor Green
    Write-Host '  External/WAN:  ' -NoNewline -ForegroundColor White; Write-Host ('http://{0}' -f $ext) -ForegroundColor Green
    Write-Host ''
    BoxLine '-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
    Write-Host ''
    Write-Host '  APP              LOCALHOST                  NETWORK                  EXTERNAL' -ForegroundColor Yellow
    Write-Host '  ---              ---------                  -------                  --------'
    Write-Host ('  Guardian  http://{0}:8501  http://{1}:8501  http://{2}:8501' -f $local,$net,$ext) -ForegroundColor White
    Write-Host ('  Budget    http://{0}:8502  http://{1}:8502  http://{2}:8502' -f $local,$net,$ext) -ForegroundColor White
    Write-Host ('  miseBot   http://{0}:8503  http://{1}:8503  http://{2}:8503' -f $local,$net,$ext) -ForegroundColor White
    Write-Host ''
    Write-Host '  Ctrl+click any URL to open. For phone demos, use the NETWORK URL.' -ForegroundColor DarkYellow
    Write-Host ''
    BoxLine '-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
    Read-Host '  Press Enter to return to menu'
}

function LaunchApp($name, $folder, $port) {
    Clear-Host
    Write-Host ''
    Write-Host (" >> Launching {0} on port {1}..." -f $name, $port) -ForegroundColor Magenta
    $path = Join-Path $Root $folder
    Start-Process cmd.exe -ArgumentList '/k', ("cd /d `""{0}`"" && Start-{1}.bat" -f $path, $name) -WindowStyle Normal
    Start-Sleep -Seconds 4
}

while ($true) {
    ShowMenu
    if (-not (Test-Path $ChoiceFile)) { continue }
    $choice = Get-Content $ChoiceFile -Raw
    Remove-Item $ChoiceFile -Force -ErrorAction SilentlyContinue

    switch ($choice.Trim().ToUpper()) {
        '1' { LaunchApp 'HAL-Guardian' 'HAL-Guardian' 8501; ShowIps }
        '2' { LaunchApp 'HAL-Budget' 'HAL-Budget' 8502; ShowIps }
        '3' { LaunchApp 'miseBot' 'miseBot' 8503; ShowIps }
        '4' {
            LaunchApp 'HAL-Guardian' 'HAL-Guardian' 8501
            LaunchApp 'HAL-Budget' 'HAL-Budget' 8502
            LaunchApp 'miseBot' 'miseBot' 8503
            ShowIps
        }
        'V' { ShowIps }
        'Q' {
            Clear-Host
            Write-Host ''
            Write-Host '  Good luck at the hackathon, Steve.' -ForegroundColor Yellow
            Write-Host ''
            Write-Host '  Servers are still running in their own windows.' -ForegroundColor DarkYellow
            Write-Host '  Close each app tab, then Ctrl+C + Y in each server window.' -ForegroundColor DarkYellow
            Write-Host ''
            Start-Sleep -Seconds 2
            exit 0
        }
    }
}
