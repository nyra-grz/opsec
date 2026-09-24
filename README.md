# opsec

A fake "hacker mode" for your terminal. You type `sudo opsec` and the screen goes full Hollywood: a ghost-shell boot sequence, a port scan, brute-force hash cracking, `ACCESS GRANTED`, data exfiltration and Matrix rain across the whole window. It's **menu-driven**, so you pick the operations yourself — DNS recon, web-vuln scan, directory brute-force, CVE matching, a full exploit chain — or hit `a` and let it auto-run the whole show. You can enter a target (domain, IP or hostname) and the whole show plays against it. Press **Ctrl+C** and it "wipes the logs" before it exits.

It's a single Python file with zero dependencies, and it runs on macOS, Linux and Windows. The IPs, hashes and file names are random.

> **It's all fake.** Nothing on your system is touched, scanned or sent anywhere. There is no network activity, no port scanning, and no files are read or written. The IPs, hashes, file names and the target you type are only displayed as random-looking text.

## Install

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/nyra-grz/opsec/main/install.sh | bash
```

Then run (macOS/Linux need root for the full "effect"):

```bash
sudo opsec
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/nyra-grz/opsec/main/install.ps1 | iex
```

Then run (no admin needed on Windows):

```powershell
opsec
```

Use Windows Terminal for the best look. If `opsec` isn't found, open a new terminal window.

## Requirements

- Python 3.8 or newer — that's it, **stdlib only, zero dependencies**. If Python is missing, the installer installs it for you automatically:
  - **macOS:** Homebrew (`brew install python`), or [uv](https://docs.astral.sh/uv/) when Homebrew isn't present
  - **Linux:** whichever package manager is available — `apt`, `dnf`, `yum`, `pacman`, `apk` or `zypper`
  - **Windows:** `winget`, then Chocolatey, then the official installer from python.org
- On macOS/Linux, force a specific interpreter with `OPSEC_PYTHON=/path/to/python3` (the installer skips detection and auto-install).
- On macOS/Linux `opsec` requires root (`sudo opsec`); on Windows it runs as a normal user

## Where it installs

The installer puts the `opsec` command somewhere already on your PATH, then tells you to run it:

| Platform | Location | PATH |
|---|---|---|
| macOS / Linux | `/usr/local/bin/opsec` | global (`/usr/local/bin`) |
| Windows | `%LOCALAPPDATA%\opsec\opsec.cmd` | user PATH |

Override the macOS/Linux location with the `OPSEC_DEST` env var (a full path to the command). If you point it anywhere else, the installer reminds you to add that directory to your PATH.

## What's on the menu

Type a key and it plays the corresponding operation (then you're back at the menu).

| Key | Operation |
|---|---|
| `1` | firewall-bypass |
| `2` | port-scan |
| `3` | credential-crack |
| `4` | privilege-escalate |
| `5` | data-exfil |
| `6` | memory-dump |
| `7` | proxy-chain |
| `8` | identity-spoof |
| `9` | packet-sniff |
| `s` | ssh-bruteforce |
| `b` | deploy-backdoor |
| `n` | dns-recon |
| `w` | web-vuln-scan |
| `d` | dir-bruteforce |
| `v` | vuln-scan (CVE matching) |
| `e` | exploit-chain |
| `m` | matrix-rain |
| `i` | session-info |
| `a` | auto-run (plays the whole sequence) |
| `t` | set-target (change the session target) |
| `q` | quit |

## Options

| | |
|---|---|
| `--fast` | no delays, everything as fast as possible |
| `Ctrl+C` | quit — with a dramatic exit: *"You were never here."* |

## Uninstall

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/nyra-grz/opsec/main/install.sh | bash -s -- --uninstall
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/nyra-grz/opsec/main/install.ps1))) -Uninstall
```

## Development

Run straight from a checkout — the env var skips the root check so you don't need `sudo`:

```bash
OPSEC_ALLOW_NONROOT=1 python3 opsec.py
```

Run the headless end-to-end smoke test (no root needed):

```bash
bash tools/smoke_test.sh
```

Repository layout:

| File | Purpose |
|---|---|
| `opsec.py` | the whole program — one self-contained Python 3 file |
| `install.sh` | macOS/Linux installer and uninstaller |
| `install.ps1` | Windows installer and uninstaller |
| `tools/smoke_test.sh` | headless end-to-end smoke test |

## License

MIT
