#!/usr/bin/env python3
# opsec - fake hacker mode. Pure show, touches nothing on the system.
# Usage: sudo opsec [--fast]

import os
import sys
import time
import random
import shutil
import secrets
import signal
import atexit
import getpass

if os.name == "nt":
    try:
        import ctypes
        _k32 = ctypes.windll.kernel32
        _hout = _k32.GetStdHandle(-11)
        _mode = ctypes.c_uint32()
        if _k32.GetConsoleMode(_hout, ctypes.byref(_mode)):
            _k32.SetConsoleMode(_hout, _mode.value | 0x0004)
    except Exception:
        pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

G = "\033[32m"
BG = "\033[1;32m"
R = "\033[1;31m"
Y = "\033[1;33m"
C = "\033[1;36m"
W = "\033[1;97m"
D = "\033[2;32m"
N = "\033[0m"

SPEED = 0 if "--fast" in sys.argv else 1


def is_root():
    if os.name == "nt":
        return True
    try:
        return os.geteuid() == 0
    except AttributeError:
        return True


if (not is_root()) and os.environ.get("OPSEC_ALLOW_NONROOT") != "1":
    print(R + "[!] opsec: operation not permitted. Root clearance required." + N)
    print(D + "    try: sudo opsec" + N)
    sys.exit(1)


def zz(seconds):
    if SPEED:
        time.sleep(seconds)


def cols():
    return shutil.get_terminal_size(fallback=(80, 24)).columns


def rows():
    return shutil.get_terminal_size(fallback=(80, 24)).lines


def clear_screen():
    sys.stdout.write("\033[H\033[2J")
    sys.stdout.flush()


def type_out(s):
    for ch in s:
        sys.stdout.write(ch)
        sys.stdout.flush()
        zz(0.012)
    sys.stdout.write("\n")
    sys.stdout.flush()


def rand_ip():
    return ".".join((
        str(random.randint(1, 223)),
        str(random.randint(0, 255)),
        str(random.randint(0, 255)),
        str(random.randint(1, 254)),
    ))


def rand_hex(n):
    return "".join(secrets.choice("0123456789abcdef") for _ in range(n))


def pick(*items):
    return random.choice(items)


def pick_host():
    return pick(
        "mainframe." + rand_hex(3) + ".gov",
        "db-cluster-0" + str(random.randint(0, 8)) + ".corp",
        "satellite-uplink-" + rand_hex(2),
        "swift-gateway.bank",
        "vault." + rand_hex(4) + ".mil",
        "relay-" + rand_hex(2) + ".gov",
    )


def spinner(label, seconds):
    frames = "|/-\\"
    total = int(seconds * 10)
    for i in range(total):
        sys.stdout.write("\r" + Y + "[" + frames[i % 4] + "]" + N + " " + label)
        sys.stdout.flush()
        zz(0.1)
    sys.stdout.write("\r" + BG + "[+]" + N + " " + label + " " + BG + "OK" + N + "\n")
    sys.stdout.flush()


def progress(label):
    w = 34
    p = 0
    while p < 100:
        p += random.randint(1, 9)
        if p > 100:
            p = 100
        fill = p * w // 100
        bar = "#" * fill + "." * (w - fill)
        sys.stdout.write("\r" + G + ("%-28s" % label) + N + " [" + BG + bar + N + "] %3d%%" % p)
        sys.stdout.flush()
        zz(0.03 + random.randint(0, 5) / 100)
    sys.stdout.write("\n")
    sys.stdout.flush()


def matrix(seconds):
    frames = int(seconds * 20)
    w = cols()
    h = rows()
    charset = "01ABCDEF#$%&@*+=<>?/\\|"
    drops = [0] * (w + 1)
    trail = [0] * (w + 1)
    for c in range(1, w + 1):
        drops[c] = random.randrange(h + h // 3) - h // 3
        trail[c] = random.randrange(h // 2 + 1) + h // 3 + 4
    sys.stdout.write("\033[?25l")
    clear_screen()
    sys.stdout.write("\033[?7l")
    sys.stdout.flush()
    for _ in range(frames):
        frame = ""
        for c in range(1, w + 1):
            y = drops[c]
            t = trail[c]
            if 1 <= y <= h:
                frame += "\033[%d;%dH" % (y, c) + W + random.choice(charset)
            if 1 <= y - 1 <= h:
                frame += "\033[%d;%dH" % (y - 1, c) + G + random.choice(charset)
            if 1 <= y - t <= h:
                frame += "\033[%d;%dH " % (y - t, c)
            y += 1
            if y - t > h:
                y = -(random.randrange(h // 3 + 1))
                trail[c] = random.randrange(h // 2 + 1) + h // 3 + 4
            drops[c] = y
        sys.stdout.write(frame)
        sys.stdout.flush()
        zz(0.05)
    sys.stdout.write(N + "\033[?7h")
    clear_screen()
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def read_key():
    if os.name == "nt":
        import msvcrt
        return msvcrt.getwch()
    import termios
    import tty
    try:
        fd = sys.stdin.fileno()
    except Exception:
        ch = sys.stdin.read(1)
        return ch if ch else ""
    if not os.isatty(fd):
        ch = sys.stdin.read(1)
        return ch if ch else ""
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        data = os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return data.decode("utf-8", "ignore") if data else ""


def read_line(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    try:
        interactive = os.isatty(sys.stdin.fileno())
    except Exception:
        interactive = False
    if not interactive:
        line = "".join(c for c in sys.stdin.readline().strip() if c.isprintable())
        sys.stdout.write("\n")
        sys.stdout.flush()
        return line[:64]
    chars = []
    while True:
        ch = read_key()
        if ch == "" or ch in ("\r", "\n"):
            break
        if ch in ("\x7f", "\b"):
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue
        if ch in ("\x00", "\xe0"):
            read_key()
            continue
        if ch == "\x03":
            cleanup("SIGINT received")
        if ch.isprintable() and len(chars) < 64:
            chars.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()
    return "".join(chars).strip()


def restore_terminal():
    sys.stdout.write("\033[0m\033[?25h\033[?7h")
    sys.stdout.flush()


atexit.register(restore_terminal)


def _on_sigint(sig, frame):
    cleanup("SIGINT received")


signal.signal(signal.SIGINT, _on_sigint)

SESSION = rand_hex(4).upper()
NODE = pick("NULL-NODE", "SHADOW", "ZERO-X", "DARKSTAR", "PHANTOM") + "-" + rand_hex(2)
EGRESS = rand_ip()
START_TS = time.time()
OPS = 0
TARGET = ""


def active_target():
    return TARGET if TARGET else pick_host()


# chrome - faithful port of opsec bash: banner, boot, proxy_chain, hexdump_fake,
# crack, access_granted, target_info, op_info, cleanup
# Function definitions only; no imports, no top-level code.


def banner():
    clear_screen()
    print(BG, end="")
    print()
    print("    ██████╗ ██████╗ ███████╗███████╗ ██████╗")
    print("   ██╔═══██╗██╔══██╗██╔════╝██╔════╝██╔════╝")
    print("   ██║   ██║██████╔╝███████╗█████╗  ██║")
    print("   ██║   ██║██╔═══╝ ╚════██║██╔══╝  ██║")
    print("   ╚██████╔╝██║     ███████║███████╗╚██████╗")
    print("    ╚═════╝ ╚═╝     ╚══════╝╚══════╝ ╚═════╝")
    print(N, end="")
    try:
        user = getpass.getuser()
    except Exception:
        user = "root"
    print(f"{D}   ghost-shell v7.0.0  //  operator: {W}{user}{D}  //  clearance: {R}OMEGA{N}")
    print(f"{D}   session {W}{SESSION}{D}  //  node {W}{NODE}{D}  //  uplink {W}{EGRESS}{D}  //  {Y}simulation only{N}")
    print()


def boot():
    mods = ["ghost.ko", "netphantom.ko", "kstealth.ko", "tor_bridge.ko",
            "memcloak.ko", "ids_blind.ko", "fwghost.ko"]
    for m in mods:
        print(f"{G}[ {BG}OK{G} ]{N} Loading kernel module {W}{m}{N}")
        zz(0.15)
    print()
    mac = ":".join(rand_hex(2) for _ in range(6))
    spinner(f"Spoofing MAC address -> {mac}", 1)
    hn = f"{pick('NULL-NODE', 'SHADOW', 'ZERO-X', 'DARKSTAR', 'PHANTOM')}-{rand_hex(4)}"
    spinner(f"Randomizing hostname -> {hn}", 1)
    spinner("Disabling telemetry", 1)
    print()


def proxy_chain():
    print(f"{C}[*] Building onion proxy chain...{N}")
    lands = ("Iceland", "Romania", "Panama", "Seychelles", "Moldova",
             "Switzerland", "Estonia", "Belize", "Malta", "Tonga")
    for i in range(1, 7):
        print(f"    {D}hop {i}{N}  {rand_ip():<16} {G}-->{N}  {W}{pick(*lands)}{N}  {D}({random.randint(20, 319)}ms){N}")
        zz(0.25)
    print(f"{BG}[+] Location masked. Traceback probability: 0.0003%{N}")
    print()


def hexdump_fake(lines=14):
    for _ in range(lines):
        row = " ".join(rand_hex(4) for _ in range(8))
        print(f"{D}0x{rand_hex(8)}{N}  {G}{row}{N}")
        zz(0.03)


def crack(target):
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%&*"
    length = len(target)
    locked = 0
    print(f"{C}[*] Brute-forcing hash {rand_hex(32)}...{N}")
    while locked <= length:
        out = target[:locked]
        for _ in range(locked, length):
            out += charset[random.randrange(len(charset))]
        sys.stdout.write(f"\r    {D}key:{N} {BG}{out[:locked]}{R}{out[locked:]}{N}")
        sys.stdout.flush()
        zz(0.04)
        if random.randrange(4) == 0:
            locked += 1
    sys.stdout.write(f"\n{BG}[+] Hash cracked in {random.randrange(9)}.{random.randrange(1000):03d}s{N}\n\n")
    sys.stdout.flush()


def access_granted():
    msg = "  ACCESS  GRANTED  "
    w = cols()
    pad = (w - len(msg) - 4) // 2
    if pad < 0:
        pad = 0
    head = " " * pad
    rule = "═" * (len(msg) + 2)
    print()
    print(f"{head}{BG}╔{rule}╗{N}")
    print(f"{head}{BG}║ \033[5;1;97;42m{msg}{N}{BG} ║{N}")
    print(f"{head}{BG}╚{rule}╝{N}")
    print()


def target_info(host):
    print(f"{C}[*] Target acquired: {W}{host}{N}")
    ip = host if host.replace(".", "").isdigit() else rand_ip()
    print(f"    {'IP:':<12} {ip}")
    print(f"    {'OS:':<12} {pick('Linux 6.8', 'Windows Server 2019', 'FreeBSD 14', 'Solaris 11', 'Cisco IOS 15.2')}")
    ports = f"{pick(22, 80, 443, 3306, 8080)}, {pick(21, 25, 3389, 5432, 6379)}, {pick(8443, 9000, 27017, 11211)}"
    print(f"    {'Open ports:':<12} {ports}")
    print(f"    {'Firewall:':<12} {pick('pfSense', 'Palo Alto PA-5450', 'FortiGate 600F', 'Cisco ASA')}")
    zz(0.4)
    print()


def op_info():
    up = int(time.time() - START_TS)
    try:
        user = getpass.getuser()
    except Exception:
        user = "root"
    info = (
        ("session:", SESSION),
        ("operator:", user),
        ("node:", NODE),
        ("target:", TARGET or "(random)"),
        ("uptime:", f"{up}s"),
        ("ops run:", str(OPS)),
        ("egress:", f"{EGRESS} via 6-hop chain"),
        ("stealth:", "ON (ids_blind loaded)"),
        ("traceback:", "0.0003%"),
    )
    for label, value in info:
        print(f"    {D}{label:<12}{N} {value}")
    print()


def ask_target():
    global TARGET
    print(f"{C}[*] Enter a target for this session {D}(domain, IP or hostname){N}")
    print(f"{D}    simulation only - nothing is contacted, resolved or scanned{N}")
    t = read_line(f"    {BG}target ▸ {N}")
    if t:
        TARGET = t
        print(f"{BG}[+] Target locked:{N} {W}{t}{N}")
    elif TARGET:
        print(f"{D}[i] Keeping current target: {W}{TARGET}{N}")
    else:
        print(f"{D}[i] No target set - random names will be used. Press [t] in the menu to set one.{N}")
    zz(0.5)
    print()


def cleanup(reason="SIGINT received"):
    if not reason:
        reason = "SIGINT received"
    sys.stdout.write(N + "\033[?7h\033[?25h")
    sys.stdout.flush()
    print()
    print()
    print(f"{R}[!] {reason}. Killing session...{N}")
    zz(0.3)
    print(f"{G}[+] Wiping logs............ {BG}done{N}")
    zz(0.2)
    print(f"{G}[+] Shredding RAM cache.... {BG}done{N}")
    zz(0.2)
    print(f"{G}[+] Tor circuit closed..... {BG}done{N}")
    zz(0.3)
    print()
    print(f"{W}    You were never here.{N}")
    print()
    sys.exit(0)


# ops set A - faithful port of opsec bash functions:
# op_firewall, op_scan, op_crack, op_privesc, op_sniff, op_ssh
# Function definitions only; no imports, no top-level code.


def op_firewall():
    target_info(active_target())
    fw = pick('Palo Alto PA-5450 (stateful)', 'FortiGate 600F', 'Cisco ASA 5525-X',
              'pfSense 2.7 / pf', 'Juniper SRX345')
    print(f"{C}[*] Edge firewall: {W}{fw}{N}")
    zz(0.4)
    print(f"{C}[*] Enumerating rule base...{N}")
    for r in (
        '1024  DENY   any          -> dmz     : 22',
        '1025  ALLOW  10.0.0.0/8   -> any     : 443',
        '1288  DENY   any          -> mgmt    : 8443',
        '2048  ALLOW  admin-net    -> any     : 22',
        '4096  DENY   any          -> any     : * (implicit)',
    ):
        print(f"    {D}{r}{N}")
        zz(0.15)
    zz(0.2)
    print(f"{C}[*] Probing state table (91% used)...{N}")
    zz(0.3)
    progress("Bypassing firewall")
    progress("Tunneling through allowed egress :443")
    progress("Rewriting IDS signatures")
    print(f"{BG}[+] Firewall evaded. 0 alerts.{N}")
    print()


def op_scan():
    host = TARGET or f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    print(f"{C}[*] Stealth SYN scan vs {W}{host}{N}{C}...{N}")
    zz(0.3)
    print(f"    {D}{'PORT':<12} {'STATE':<10} {'SERVICE':<14} {'BANNER'}{N}")
    for p in (
        '22/tcp      open       ssh            OpenSSH 9.6',
        '80/tcp      open       http           nginx 1.27.0',
        '443/tcp     open       https          nginx 1.27.0',
        '3306/tcp    filtered   mysql          --',
        '8080/tcp    open       http-proxy     Squid 6.1',
        '6379/tcp    closed     redis          --',
        '27017/tcp   open       mongodb        7.0.12',
    ):
        print(f"    {G}{p}{N}")
        zz(0.12)
    print(f"{BG}[+] 5 open, 1 filtered, 1 closed - OS guess: Linux 6.8 (96%){N}")
    print()


def op_crack():
    print(f"{C}[*] Pulling hashes from /etc/shadow (12 entries){N}")
    print(f"    {D}$2b$12${rand_hex(22)}{N}")
    zz(0.3)
    crack(pick('Tr0ub4dor&3', 'hunter2', 'P@ssw0rd!1337', 'root:toor', 'CorrectHorseBattery'))
    access_granted()
    zz(0.8)


def op_privesc():
    host = active_target()
    cve = f"CVE-{random.randint(2024, 2027)}-{random.randint(1000, 9999)}"
    print(f"{C}[*] Shell: www-data (uid=33) on {W}{host}{N}")
    zz(0.3)
    progress("Enumerating SUID binaries")
    print(f"    {D}found: /usr/bin/pkexec, /usr/bin/sudo 1.9.14{N}")
    print(f"    {D}kernel: Linux 6.8.0-45-generic  ->  exploit match {W}{cve}{N}")
    zz(0.3)
    progress("Crafting heap spray")
    progress("Escalating privileges")
    print(f"{BG}[+] root shell spawned. uid=0(root) gid=0(root){N}")
    print(f"{W}    root@{host[:10]}:~# _{N}")
    print()


def op_sniff():
    print(f"{C}[*] NIC -> monitor mode (mon0){N}")
    zz(0.3)
    print(f"{C}[*] Capturing 802.11 + TCP streams...{N}")
    for _ in range(10):
        ts = (f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:"
              f"{random.randint(0, 59):02d}.{random.randint(0, 999):03d}")
        src = f"{rand_ip()}:{random.randint(1024, 61023)}"
        dst = f"{rand_ip()}:{pick(443, 80, 53, 22, 8443)}"
        proto = pick('TCP', 'TLS', 'DNS', 'UDP')
        info = pick('SYN', 'ACK', 'Client Hello', 'GET /login', 'DNS query A', 'FIN')
        print(f"    {D}{ts}{N}  {W}{src:<21}{N} {G}->{N} {W}{dst:<21}{N} {Y}{proto:<6}{N} {info}")
        zz(0.08)
    print(f"{BG}[+] 3 sessions reassembled, 2 credential pairs recovered{N}")
    print()


def op_ssh():
    host = TARGET or rand_ip()
    print(f"{C}[*] Credential spray vs ssh://{host}:22 (threads: 64){N}")
    zz(0.3)
    n = random.randint(4, 6)
    for _ in range(n):
        cred = pick('root:root', 'admin:admin', 'admin:password', 'guest:guest',
                    'test:test', 'oracle:oracle', 'www:www', 'svc:svc')
        print(f"    {W}{cred:<34}{N} {R}DENIED{N}")
        zz(0.18)
    user = pick('svc_backup', 'deploy', 'gitlab-runner')
    pw = pick('Backup2026!', 'deploy$2026', 'Str0ng!Pass', 'ch4ng3m3_2026')
    pair = f"{user}:{pw}"
    print(f"    {W}{pair:<34}{N} {BG}ACCEPTED{N}")
    print(f"{BG}[+] Valid credentials: {user} / {pw}{N}")
    print()


def op_dns():
    dom = TARGET or (pick("necronet", "hypercorp", "darkstar-systems", "nova-bank", "orbital-systems")
                     + "." + pick("com", "net", "io", "gov"))
    print(f"{C}[*] DNS reconnaissance vs {W}{dom}{N}")
    zz(0.3)
    print(f"{C}[*] Querying nameservers...{N}")
    print(f"    {D}A     {N} {dom:<34} {W}{rand_ip()}{N}")
    print(f"    {D}MX    {N} {('mail.' + dom):<34} {W}{rand_ip()}{N}")
    print(f"    {D}TXT   {N} {('v=spf1 include:_spf.' + dom):<34} {D}...{N}")
    zz(0.3)
    print(f"{C}[*] Enumerating subdomains (wordlist: 4,978 entries)...{N}")
    subs = ["www", "mail", "vpn", "dev", "staging", "admin", "api", "portal",
            "git", "jenkins", "jira", "db", "backup", "test", "old", "cdn", "files", "monitor"]
    for s in sorted(random.sample(subs, 10)):
        print(f"    {G}[+] {s + '.' + dom:<40}{N} {W}{rand_ip()}{N}")
        zz(0.12)
    print(f"{BG}[+] 10 subdomains found. Wildcard DNS: off.{N}")
    print()


def op_webscan():
    host = TARGET or pick_host()
    pool = (
        ("CRITICAL", "SQL injection (error-based)", "/product?id=1'"),
        ("CRITICAL", "Authentication bypass", "/admin/../admin"),
        ("HIGH", "Reflected XSS", "/search?q=<script>"),
        ("HIGH", "Local file inclusion", "/download?file=../../etc/passwd"),
        ("HIGH", "Insecure direct object reference", "/api/v1/users/1337"),
        ("MEDIUM", "Open redirect", "/login?next=//evil.example"),
        ("MEDIUM", "Directory listing enabled", "/backup/"),
        ("MEDIUM", "Missing security headers", "HSTS, CSP, X-Frame-Options"),
        ("LOW", "Server version disclosure", "nginx/1.18.0"),
        ("LOW", "Outdated frontend library", "jQuery 1.7.1"),
    )
    sev_color = {"CRITICAL": R, "HIGH": Y, "MEDIUM": C, "LOW": D}
    findings = random.sample(pool, random.randint(5, 8))
    print(f"{C}[*] Web vulnerability scan vs {W}https://{host}{N}")
    zz(0.3)
    progress("Crawling target")
    print(f"    {D}pages crawled: {random.randint(90, 400)}   forms: {random.randint(3, 14)}   parameters: {random.randint(20, 80)}{N}")
    progress("Fuzzing parameters")
    progress("Testing injection points")
    print()
    for sev, name, path in findings:
        print(f"    {sev_color[sev]}[{sev:<8}]{N} {name:<38} {D}{path}{N}")
        zz(0.15)
    counts = {}
    for sev, _, _ in findings:
        counts[sev] = counts.get(sev, 0) + 1
    summary = []
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if sev in counts:
            summary.append(f"{sev_color[sev]}{counts[sev]} {sev.lower()}{N}")
    print()
    print(f"{BG}[+] {len(findings)} findings:{N} {'  '.join(summary)}")
    print(f"{D}    report: ~/opsec-reports/{host}-{rand_hex(6)}.html (simulated){N}")
    print()


def op_dirbust():
    host = TARGET or pick_host()
    wl = pick("common.txt", "raft-medium-directories.txt", "dirb-big.txt")
    print(f"{C}[*] Directory brute-force vs {W}https://{host}{N}")
    print(f"    {D}wordlist: {wl} ({random.randint(4000, 22000)} entries){N}")
    zz(0.3)
    pool = (
        ("/admin", "301", "-> /admin/"),
        ("/backup.zip", "200", f"{random.randint(2, 900)} MB"),
        ("/.git/HEAD", "200", "ref: refs/heads/main"),
        ("/api/v1/", "401", "auth required"),
        ("/config.php.bak", "200", "2.1 KB"),
        ("/uploads/", "403", "forbidden"),
        ("/phpmyadmin/", "200", "v4.9.5"),
        ("/server-status", "403", "forbidden"),
        ("/wp-login.php", "200", "WordPress"),
        ("/.env", "200", "1.2 KB"),
    )
    found = random.sample(pool, random.randint(4, 7))
    for path, code, note in found:
        col = BG if code == "200" else (Y if code == "301" else D)
        print(f"    {col}[{code}]{N} {path:<22} {D}{note}{N}")
        zz(0.2)
    print(f"{BG}[+] {len(found)} paths discovered.{N}")
    print()


def op_vulnscan():
    host = TARGET or pick_host()
    services = (
        ("22/tcp", "OpenSSH 7.4", "CRITICAL"),
        ("80/tcp", "nginx 1.18.0", "MEDIUM"),
        ("443/tcp", "OpenSSL 1.1.1", "HIGH"),
        ("3306/tcp", "MySQL 5.7.31", "HIGH"),
        ("8080/tcp", "Apache Tomcat 9.0.30", "CRITICAL"),
    )
    sev_color = {"CRITICAL": R, "HIGH": Y, "MEDIUM": C, "LOW": D}
    print(f"{C}[*] Vulnerability scan vs {W}{host}{N}")
    zz(0.3)
    hits = random.sample(services, random.randint(3, 5))
    for port, svc, sev in hits:
        cve = f"CVE-{random.randint(2018, 2027)}-{random.randint(1000, 29999)}"
        print(f"    {W}{port:<9}{N} {svc:<20} {sev_color[sev]}{sev:<8}{N} {cve}")
        zz(0.2)
    print(f"{BG}[+] {len(hits)} vulnerable services matched. Exploit modules available: {len(hits)}{N}")
    print(f"{D}    hint: press [e] to run the full exploit chain{N}")
    print()


def op_exploitchain():
    host = TARGET or pick_host()
    cve = f"CVE-{random.randint(2020, 2027)}-{random.randint(1000, 29999)}"
    stages = (
        ("recon", "services fingerprinted, 3 entry points"),
        ("weaponize", cve + " module compiled"),
        ("initial access", "reverse shell to " + rand_ip() + ":443"),
        ("privilege escalation", "uid=0(root) / nt authority\\system"),
        ("persistence", "systemd unit + cron + SSH key"),
        ("lateral movement", str(random.randint(2, 6)) + " internal hosts pivoted"),
        ("objective", "domain admin - crown jewels staged"),
    )
    print(f"{C}[*] Building exploit chain vs {W}{host}{N}")
    zz(0.3)
    for i, (stage, detail) in enumerate(stages, 1):
        print(f"    {D}stage {i}{N}  {stage:<22} {W}{detail}{N}")
        zz(0.25)
    print()
    print(f"{BG}[+] Chain complete: initial access -> root -> domain admin{N}")
    access_granted()
    zz(0.8)


# --- ops set B + menu (ported from bash opsec) ---


def op_exfil():
    files = ["customers.db", "salaries_2026.xlsx", "launch_codes.txt", "keys.pem",
             "shadow", "backup.tar.gz", "emails.pst"]
    print(f"{C}[*] Exfiltrating data via DNS tunnel...{N}")
    for f in files:
        sys.stdout.write(f"    {W}{f:<22}{N} {random.randint(100, 90099):6d} KB  {G}")
        sys.stdout.flush()
        for _ in range(16):
            sys.stdout.write("▮")
            sys.stdout.flush()
            zz(0.02)
        sys.stdout.write(f" {BG}✓{N}\n")
    print()


def op_memdump():
    print(f"{C}[*] Attaching to sshd (pid {random.randint(100, 9099)}), dumping RSS 210 MB...{N}")
    zz(0.3)
    hexdump_fake(16)
    print(f"{BG}[+] Carved: 3 private keys, 1 session token, 2 configs{N}")
    print()


def op_spoof():
    mac = ":".join(rand_hex(2) for _ in range(6))
    hn = f"{pick('NULL-NODE', 'SHADOW', 'ZERO-X', 'DARKSTAR', 'PHANTOM')}-{rand_hex(4)}"
    spinner(f"Spoofing MAC -> {mac}", 1)
    spinner(f"Randomizing hostname -> {hn}", 1)
    spinner("Rotating TLS fingerprint", 1)
    spinner("Cloaking timezone + locale", 1)
    print(f"{BG}[+] Identity masked. Fingerprint entropy 99.2%.{N}")
    print()


def op_backdoor():
    print(f"{C}[*] Deploying persistent implant {W}kbeacon{C}...{N}")
    lines = [
        "writing /usr/lib/systemd/system/kbeacon.service",
        "beacon interval 60s (jitter 30%)",
        f"rendezvous: {rand_hex(16)}.onion",
        "patching auditd rules",
    ]
    for s in lines:
        print(f"    {BG}[ok]{N} {s}")
        zz(0.2)
    spinner("First check-in", 1)
    print(f"{BG}[+] Implant live. Persistence: systemd + cron.{N}")
    print()


def op_auto():
    keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "s", "b", "n", "w", "d", "v", "e"]
    n = random.randint(3, 5)
    type_out(f"{C}> AUTO-OP engaged - {n} operations queued{N}")
    zz(0.3)
    for _ in range(n):
        run_op(pick(*keys))
        zz(0.4)


def run_op(key):
    global OPS
    OPS += 1
    if key == "1":
        op_firewall()
    elif key == "2":
        op_scan()
    elif key == "3":
        op_crack()
    elif key == "4":
        op_privesc()
    elif key == "5":
        op_exfil()
    elif key == "6":
        op_memdump()
    elif key == "7":
        proxy_chain()
    elif key == "8":
        op_spoof()
    elif key == "9":
        op_sniff()
    elif key == "s":
        op_ssh()
    elif key == "b":
        op_backdoor()
    elif key == "n":
        op_dns()
    elif key == "w":
        op_webscan()
    elif key == "d":
        op_dirbust()
    elif key == "v":
        op_vulnscan()
    elif key == "e":
        op_exploitchain()
    elif key == "m":
        matrix(6)
    elif key == "i":
        op_info()
    elif key == "a":
        op_auto()
    # unknown key: no-op (still counted, like bash)


def paint_menu():
    banner()
    print(f"    {C}══ OPERATIONS {'═' * 42}{N}")
    print()
    rows = [
        ("1", "firewall-bypass", "8", "identity-spoof", "n", "dns-recon"),
        ("2", "port-scan", "9", "packet-sniff", "w", "web-vuln-scan"),
        ("3", "credential-crack", "s", "ssh-bruteforce", "d", "dir-bruteforce"),
        ("4", "privilege-escalate", "b", "deploy-backdoor", "v", "vuln-scan"),
        ("5", "data-exfil", "m", "matrix-rain", "e", "exploit-chain"),
        ("6", "memory-dump", "i", "session-info", "t", "set-target"),
        ("7", "proxy-chain", "a", "auto-run", "", ""),
    ]
    for k1, n1, k2, n2, k3, n3 in rows:
        line = f"      {BG}[{k1}]{N} {n1:<20} {BG}[{k2}]{N} {n2:<20}"
        if k3:
            line += f" {BG}[{k3}]{N} {n3}"
        print(line)
    print(f"      {BG}[q]{N} {'quit':<20}")
    print()
    print(f"    {D}target:{N} {W}{TARGET or '(random per op)'}{N} {D}- press [t] to change{N}")
    print()
    sys.stdout.write(f"    {BG}op ▸ {N}")
    sys.stdout.flush()


def menu():
    while True:
        paint_menu()
        k = read_key()
        if k == "":  # EOF / piped input
            break
        print()
        if k in ("q", "Q"):
            cleanup("User logout")
        low = k.lower()
        if low == "t":
            ask_target()
            continue
        if low in "123456789sbmianwdve":
            run_op(low)
        else:
            continue
        print()
        print(f"    {D}-- op complete --{N}")
        sys.stdout.write(f"    {D} press any key for menu ▸ {N}")
        sys.stdout.flush()
        read_key()


def main():
    banner()
    type_out(f"{G}> Initializing ghost-shell v7.0.0...{N}")
    zz(0.3)
    boot()
    proxy_chain()
    zz(0.4)
    matrix(2)
    ask_target()
    menu()


if __name__ == "__main__":
    main()
