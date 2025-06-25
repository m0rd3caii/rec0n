import subprocess
import os
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

def banner():
    print(Fore.CYAN + Style.BRIGHT + r"""
 ██▀███ ▓█████ ▄████▄  ▒█████  ███▄    █ 
▓██ ▒ ██▓█   ▀▒██▀ ▀█ ▒██▒  ██▒██ ▀█   █ 
▓██ ░▄█ ▒███  ▒▓█    ▄▒██░  ██▓██  ▀█ ██▒
▒██▀▀█▄ ▒▓█  ▄▒▓▓▄ ▄██▒██   ██▓██▒  ▐▌██▒
░██▓ ▒██░▒████▒ ▓███▀ ░ ████▓▒▒██░   ▓██░
░ ▒▓ ░▒▓░░ ▒░ ░ ░▒ ▒  ░ ▒░▒░▒░░ ▒░   ▒ ▒ 
  ░▒ ░ ▒░░ ░  ░ ░  ▒    ░ ▒ ▒░░ ░░   ░ ▒░
  ░░   ░   ░  ░       ░ ░ ░ ▒    ░   ░ ░ 
   ░       ░  ░ ░         ░ ░          ░ 
              ░                           
                             v1.0
    rec0n - Recon Automation Script
""" + Style.RESET_ALL)

def run_command(command, description):
    print(f"{Fore.BLUE}[+] {description}{Style.RESET_ALL}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout:
                return result.stdout.strip()
            else:
                print(Fore.YELLOW + "[*] Command executed successfully but returned no output." + Style.RESET_ALL)
                return ""
        else:
            print(f"{Fore.RED}[!] Command failed with return code {result.returncode}{Style.RESET_ALL}")
            if result.stderr:
                print(Fore.RED + result.stderr.strip() + Style.RESET_ALL)
            return ""
    except Exception as e:
        print(f"{Fore.RED}[!] Exception occurred: {e}{Style.RESET_ALL}")
        return ""

def run_command_show_output(command, description, output_file=None):
    print(f"{Fore.BLUE}[+] {description}{Style.RESET_ALL}")
    try:
        with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            with open(output_file, "w") if output_file else open(os.devnull, "w") as f:
                for line in proc.stdout:
                    print(Fore.GREEN + line.strip() + Style.RESET_ALL)
                    if output_file:
                        f.write(line)
            proc.wait()
            if proc.returncode != 0:
                error_msg = proc.stderr.read().strip()
                print(f"{Fore.RED}[!] Command failed with return code {proc.returncode}\n{error_msg}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Exception occurred: {e}{Style.RESET_ALL}")

def main():
    os.system("clear" if os.name == "posix" else "cls")
    banner()
    
    domain = input(Fore.YELLOW + "Enter the target domain (e.g. example.com): " + Style.RESET_ALL).strip()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = f"recon-{domain}-{timestamp}"
    os.makedirs(out_dir, exist_ok=True)

    print(f"\nOutput directory: {Fore.GREEN}{out_dir}{Style.RESET_ALL}\n")

    # 1. Subfinder
    run_command_show_output(
        f"subfinder -d {domain} -all -recursive -silent",
        "Running Subfinder...",
        output_file=f"{out_dir}/subdomains.txt"
    )
    # 2. crt.sh — SHOW OUTPUT ONLY NEW
    print(f"{Fore.BLUE}[+] Gathering subdomains from crt.sh...{Style.RESET_ALL}")
    try:
        crt_command = f"""curl -s "https://crt.sh/?q={domain}&output=json" | jq -r '.[].name_value' | grep -Po '(\\w+\\.{domain.replace(".", "\\.")})$' | anew {out_dir}/subdomains.txt"""
        with subprocess.Popen(crt_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stdout:
                line = line.strip()
                if line:
                    print(Fore.GREEN + line + Style.RESET_ALL)
            proc.wait()
            if proc.returncode != 0:
                err = proc.stderr.read().strip()
                print(f"{Fore.RED}[!] Command failed with return code {proc.returncode}\n{err}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Exception occurred: {e}{Style.RESET_ALL}")

    # 3. httpx – SHOW ALIVE
    run_command_show_output(
        f"""httpx-toolkit -l {out_dir}/subdomains.txt -ports 80,443,8080,8000,8123,8313,8888,9090,5555,4444,4443,3000,3001,8443,8081,5000,5001,7001,9200,5601,9000,3838,8880 -threads 200 -silent""",
        "Probing live subdomains with httpx...",
        output_file=f"{out_dir}/subdomains_alive.txt"
    )

    # 4. nuclei - CORS — SHOW OUTPUT
    run_command_show_output(
        f"""nuclei -l {out_dir}/subdomains_alive.txt -tags cors -c 30 -silent""",
        "Scanning for CORS issues with nuclei...",
        output_file=f"{out_dir}/nuclei_cors.txt"
    )

    # 5. Archive.org
    run_command(
        f"""curl -G "https://web.archive.org/cdx/search/cdx" --data-urlencode "url=*.{domain}/*" --data-urlencode "collapse=urlkey" --data-urlencode "output=text" --data-urlencode "fl=original" > {out_dir}/out.txt""",
        "Querying archive.org for historic URLs..."
    )

    # 6. Filter sensitive file extensions
    print(f"{Fore.BLUE}[+] Filtering sensitive file extensions...{Style.RESET_ALL}")
    extensions = r"\.xls|\.xml|\.xlsx|\.sql|\.doc|\.pptx|\.txt|\.zip|\.tar\.gz|\.tgz|\.bak|\.7z|\.rar|\.log|\.cache|\.secret|\.db|\.backup|\.yml|\.gz|\.config|\.csv|\.yaml|\.md5|\.exe|\.dll|\.bin|\.sh|\.tar|\.deb|\.rpm|\.iso|\.img|\.apk|\.msi|\.dmg|\.tmp|\.crt|\.pem|\.key|\.pub|\.asc"
    run_command_show_output(
        f"""cat {out_dir}/out.txt | uro | grep -E "{extensions}" """,
        "Extracting potentially sensitive file URLs...",
        output_file=f"{out_dir}/sensitive_files.txt"
    )

    # 7. Check if sensitive URLs are still alive — SHOW LIVE
    run_command_show_output(
        f"""httpx-toolkit -l {out_dir}/sensitive_files.txt -silent""",
        "Checking if sensitive files are still accessible...",
        output_file=f"{out_dir}/sensitive_files_alive.txt"
    )

    print(f"\n✅ {Fore.GREEN}Recon process completed! Check the results in {out_dir}/{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Process interrupted by user (Ctrl+C). Exiting cleanly...{Style.RESET_ALL}")
        exit(0)
