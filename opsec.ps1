# opsec - fake hacker mode for Windows. Pure show, touches nothing on the system.
# Usage: opsec [-fast]      (also works as "sudo opsec" on Windows 11)
param([switch]$fast)

$E = [char]27
$G = "$E[32m"; $BG = "$E[1;32m"; $R = "$E[1;31m"; $Y = "$E[1;33m"; $C = "$E[1;36m"
$W = "$E[1;97m"; $D = "$E[2;32m"; $N = "$E[0m"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$rng = [System.Random]::new()
$oldCtrlC = [Console]::TreatControlCAsInput
[Console]::TreatControlCAsInput = $true   # Ctrl+C is read as a key so the exit sequence can play

function out([string]$s) { [Console]::Write($s) }
function line([string]$s = '') { [Console]::WriteLine($s) }
function rnd([int]$n) { $rng.Next($n) }
function pick { $args[(rnd $args.Count)] }
function cols { [Console]::WindowWidth }
function rows { [Console]::WindowHeight }

function restore {
  out "$N$E[?7h$E[?25h"
  [Console]::TreatControlCAsInput = $oldCtrlC
}

function cleanup {
  $script:fast = $false
  restore
  line "$N"; line
  line "$R[!] SIGINT received. Killing session...$N"
  Start-Sleep -Milliseconds 300
  line "$G[+] Wiping logs............ ${BG}done$N"
  Start-Sleep -Milliseconds 200
  line "$G[+] Shredding RAM cache.... ${BG}done$N"
  Start-Sleep -Milliseconds 200
  line "$G[+] Tor circuit closed..... ${BG}done$N"
  Start-Sleep -Milliseconds 300
  line
  line "$W    You were never here.$N"
  line
  exit 0
}

function check-ctrlc {
  while ([Console]::KeyAvailable) {
    $k = [Console]::ReadKey($true)
    if ($k.Key -eq 'C' -and ($k.Modifiers -band [ConsoleModifiers]::Control)) { cleanup }
  }
}

function zz([double]$s) {
  check-ctrlc
  if (-not $fast) { Start-Sleep -Milliseconds ([int]($s * 1000)) }
}

function type_out([string]$s) {  # typewriter effect
  foreach ($ch in $s.ToCharArray()) { out $ch; zz 0.012 }
  line
}

function rand_ip  { "$((rnd 223) + 1).$(rnd 256).$(rnd 256).$((rnd 254) + 1)" }
function rand_hex([int]$n) { -join (1..$n | ForEach-Object { '{0:x}' -f (rnd 16) }) }

function spinner([string]$label, [int]$secs) {
  $f = '|/-\'
  for ($i = 0; $i -lt $secs * 10; $i++) {
    out "`r$Y[$($f[$i % 4])]$N $label"
    zz 0.1
  }
  line "`r$BG[+]$N $label ${BG}OK$N"
}

function progress([string]$label) {
  $w = 34; $p = 0
  while ($p -lt 100) {
    $p += (rnd 9) + 1; if ($p -gt 100) { $p = 100 }
    $fill = [int][math]::Floor($p * $w / 100)
    $bar = ('#' * $fill) + ('.' * ($w - $fill))
    out ("`r{0}{1,-28}{2} [{3}{4}{5}] {6,3}%" -f $G, $label, $N, $BG, $bar, $N, $p)
    zz (0.03 + (rnd 6) / 100)
  }
  line
}

function banner {
  [Console]::Clear()
  out $BG
  line @'

    ██████╗ ██████╗ ███████╗███████╗ ██████╗
   ██╔═══██╗██╔══██╗██╔════╝██╔════╝██╔════╝
   ██║   ██║██████╔╝███████╗█████╗  ██║
   ██║   ██║██╔═══╝ ╚════██║██╔══╝  ██║
   ╚██████╔╝██║     ███████║███████╗╚██████╗
    ╚═════╝ ╚═╝     ╚══════╝╚══════╝ ╚═════╝
'@
  out $N
  line "$D   ghost-shell v6.6.6  //  operator: $W$env:USERNAME$D  //  clearance: ${R}OMEGA$N"
  line
}

function boot {
  foreach ($m in 'ghost.ko', 'netphantom.ko', 'kstealth.ko', 'tor_bridge.ko', 'memcloak.ko', 'ids_blind.ko') {
    line "$G[ ${BG}OK$G ]$N Loading kernel module $W$m$N"
    zz 0.15
  }
  line
  $mac = (1..6 | ForEach-Object { rand_hex 2 }) -join ':'
  spinner "Spoofing MAC address -> $mac" 1
  spinner "Randomizing hostname -> $(pick NULL-NODE SHADOW ZERO-X DARKSTAR PHANTOM)-$(rand_hex 4)" 1
  spinner "Disabling telemetry" 1
  line
}

function proxy_chain {
  line "$C[*] Building onion proxy chain...$N"
  $lands = 'Iceland', 'Romania', 'Panama', 'Seychelles', 'Moldova', 'Switzerland', 'Estonia', 'Belize', 'Malta', 'Tonga'
  for ($i = 1; $i -le 6; $i++) {
    line ("    {0}hop {1}{2}  {3,-16} {4}-->{5}  {6}{7}{8}  {9}({10}ms){11}" -f `
      $D, $i, $N, (rand_ip), $G, $N, $W, $lands[(rnd $lands.Count)], $N, $D, ((rnd 300) + 20), $N)
    zz 0.25
  }
  line "$BG[+] Location masked. Traceback probability: 0.0003%$N"
  line
}

function hexdump_fake([int]$lines = 14) {
  for ($i = 0; $i -lt $lines; $i++) {
    $row = (1..8 | ForEach-Object { rand_hex 4 }) -join ' '
    line "${D}0x$(rand_hex 8)$N  $G$row$N"
    zz 0.03
  }
}

function crack([string]$target) {
  $charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%&*'
  $len = $target.Length; $locked = 0
  line "$C[*] Brute-forcing hash $(rand_hex 32)...$N"
  while ($locked -le $len) {
    $rest = ''
    for ($i = $locked; $i -lt $len; $i++) { $rest += $charset[(rnd $charset.Length)] }
    out "`r    ${D}key:$N $BG$($target.Substring(0, $locked))$R$rest$N"
    zz 0.04
    if ((rnd 4) -eq 0) { $locked++ }
  }
  line
  line ("{0}[+] Hash cracked in {1}.{2:000}s{3}" -f $BG, (rnd 9), (rnd 1000), $N)
  line
}

function matrix([int]$secs) {
  $charset = '01ABCDEF#$%&@*+=<>?/\|'
  $w = cols; $h = rows
  $drops = @(0) * ($w + 1); $trail = @(0) * ($w + 1)
  # every column gets a drop, spread over the whole screen from the first frame
  for ($c = 1; $c -le $w; $c++) {
    $drops[$c] = (rnd ($h + [int]($h / 3))) - [int]($h / 3)
    $trail[$c] = (rnd ([int]($h / 2) + 1)) + [int]($h / 3) + 4
  }
  out "$E[?25l$E[?7l"; [Console]::Clear()
  $end = [DateTime]::Now.AddSeconds($secs)
  $sb = [System.Text.StringBuilder]::new()
  while ([DateTime]::Now -lt $end) {
    [void]$sb.Clear()
    for ($c = 1; $c -le $w; $c++) {
      $y = $drops[$c]; $t = $trail[$c]
      if ($y -ge 1 -and $y -le $h) { [void]$sb.Append("$E[$y;${c}H$W").Append($charset[(rnd $charset.Length)]) }
      if ($y - 1 -ge 1 -and $y - 1 -le $h) { [void]$sb.Append("$E[$($y - 1);${c}H$G").Append($charset[(rnd $charset.Length)]) }
      if ($y - $t -ge 1 -and $y - $t -le $h) { [void]$sb.Append("$E[$($y - $t);${c}H ") }
      $y++
      if ($y - $t -gt $h) {
        $y = -(rnd ([int]($h / 3) + 1))
        $trail[$c] = (rnd ([int]($h / 2) + 1)) + [int]($h / 3) + 4
      }
      $drops[$c] = $y
    }
    out $sb.ToString()
    check-ctrlc
    Start-Sleep -Milliseconds 50
  }
  out "$N$E[?7h"; [Console]::Clear(); out "$E[?25h"
}

function access_granted {
  $msg = '  ACCESS  GRANTED  '
  $pad = [math]::Max(0, [int]((cols) - $msg.Length - 4) / 2)
  $sp = ' ' * [int]$pad; $bar = '═' * ($msg.Length + 2)
  line
  line "$sp$BG╔$bar╗$N"
  line "$sp$BG║ $E[5;1;97;42m$msg$N$BG ║$N"
  line "$sp$BG╚$bar╝$N"
  line
}

function target_info([string]$t) {
  line "$C[*] Target acquired: $W$t$N"
  line ("    {0,-12} {1}" -f 'IP:', (rand_ip))
  line ("    {0,-12} {1}" -f 'OS:', (pick 'Linux 6.8' 'Windows Server 2019' 'FreeBSD 14' 'Solaris 11' 'Cisco IOS 15.2'))
  line ("    {0,-12} {1}, {2}, {3}" -f 'Open ports:', (pick 22 80 443 3306 8080), (pick 21 25 3389 5432 6379), (pick 8443 9000 27017 11211))
  line ("    {0,-12} {1}" -f 'Firewall:', (pick 'pfSense' 'Palo Alto PA-5450' 'FortiGate 600F' 'Cisco ASA'))
  zz 0.4
  line
}

function module_breach {
  target_info (pick "mainframe.$(rand_hex 3).gov" "db-cluster-0$(rnd 9).corp" "satellite-uplink-$(rand_hex 2)" 'swift-gateway.bank' "vault.$(rand_hex 4).mil")
  progress 'Bypassing firewall'
  progress 'Injecting payload'
  progress 'Escalating privileges'
  line
  crack (pick 'Tr0ub4dor&3' 'hunter2' 'P@ssw0rd!1337' 'root:toor' 'CorrectHorseBattery')
  access_granted
  zz 0.8
}

function module_exfil {
  line "$C[*] Exfiltrating data via DNS tunnel...$N"
  foreach ($f in 'customers.db', 'salaries_2026.xlsx', 'launch_codes.txt', 'keys.pem', 'shadow', 'backup.tar.gz', 'emails.pst') {
    out ("    {0}{1,-22}{2} {3,6} KB  {4}" -f $W, $f, $N, ((rnd 90000) + 100), $G)
    for ($k = 0; $k -lt 16; $k++) { out '▮'; zz 0.02 }
    line " $BG✓$N"
  }
  line
}

function module_scan {
  $net = "$((rnd 223) + 1).$(rnd 256).$(rnd 256)"
  line "$C[*] Scanning subnet $net.0/24...$N"
  for ($i = 0; $i -lt 10; $i++) {
    line ("    {0}{1}.{2,-4}{3} {4}{5,-6}{6} {7}" -f $W, $net, ((rnd 254) + 1), $N, `
      $BG, (pick open open open filtered), $N, (pick ssh http https mysql redis rdp smb telnet))
    zz 0.1
  }
  line
}

function module_hex {
  line "$C[*] Dumping memory segment 0x$(rand_hex 8)...$N"
  hexdump_fake 16
  line
}

try {
  banner
  type_out "$G> Initializing ghost-shell...$N"
  zz 0.3
  boot
  proxy_chain
  zz 0.5
  matrix 3
  banner
  while ($true) {
    & (pick module_breach module_exfil module_scan module_hex)
    zz 0.6
    if ((rnd 5) -eq 0) { matrix 2; banner }
  }
} finally {
  restore
}
