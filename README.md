# rec0n

> ⚡ A fully automated subdomain reconnaissance and sensitive data discovery toolkit.

![image](https://github.com/user-attachments/assets/4f1d6e40-2a35-4ffb-b432-ff7728ad3fe2)

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
