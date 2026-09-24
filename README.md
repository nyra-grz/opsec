# opsec

A fake "hacker mode" for your terminal. You type `sudo opsec` and it goes through an over-the-top show: a ghost-shell boot sequence, an onion proxy chain, brute-force hash cracking, `ACCESS GRANTED`, data exfiltration and Matrix rain across the whole window. Press **Ctrl+C** and it "wipes the logs" before it exits.

**It's all fake.** Nothing on your system is touched, scanned or sent anywhere. The IPs, hashes and files are random.

## Install

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/nyra-grz/opsec/main/install.sh | bash
```

Then run:

```bash
sudo opsec
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/nyra-grz/opsec/main/install.ps1 | iex
```

Then run:

```powershell
opsec
```

On Windows 11 with sudo enabled, `sudo opsec` also works. Use Windows Terminal for the best look. If `opsec` isn't found, open a new terminal window.

## Options

| | |
|---|---|
| `--fast` (macOS/Linux) / `-fast` (Windows) | no delays, everything as fast as possible |
| `Ctrl+C` | quit (with a dramatic exit) |

## Uninstall

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/nyra-grz/opsec/main/install.sh | bash -s -- --uninstall
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/nyra-grz/opsec/main/install.ps1))) -Uninstall
```

## License

MIT
