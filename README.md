# rec0n

> ⚡ A fully automated subdomain reconnaissance and sensitive data discovery toolkit.

![poc](https://raw.githubusercontent.com/m0rd3caii/rec0n/refs/heads/main/poc.gif)

---

## 🛠 Features

- 🔎 Subdomain enumeration (`subfinder`, `crt.sh`)
- 🌐 Live host detection with `httpx`
- 🔥 Vulnerability scanning (CORS) using `nuclei`
- 🧾 Historical data collection from `archive.org`
- 🕵️‍♂️ Sensitive file discovery (`.sql`, `.xml`, `.zip`, etc.)
- 🚨 Live sensitive file validation
- 🎨 Clean, colored CLI output for easy reading
- 📁 Organized output directory per scan

## 📦 Requirements

Install the following tools before using `rec0n`:

- [subfinder](https://github.com/projectdiscovery/subfinder)
- [httpx](https://github.com/projectdiscovery/httpx)
- [nuclei](https://github.com/projectdiscovery/nuclei)
- [anew](https://github.com/tomnomnom/anew)
- [uro](https://github.com/s0md3v/uro)
- [jq](https://stedolan.github.io/jq/)
- Python 3.7+

- Install required Python modules:

```bash
pip3 install -r requirements.txt
```

❤️ Credits
Inspired by tools from:

- ProjectDiscovery
- TomNomNom
- s0md3v
- The Bug Bounty community
