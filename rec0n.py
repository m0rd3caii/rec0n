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

def filter_sqli_urls(katana_out, sqlifilter_out):
    print(f"{Fore.BLUE}[+] Filtering potential SQLi URLs with gf...{Style.RESET_ALL}")
    try:
        with subprocess.Popen(f"cat {katana_out} | gf sqli*", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc, \
             open(sqlifilter_out, "w") as outfile:
            lines_found = 0
            for line in proc.stdout:
                line = line.strip()
                if line:
                    print(Fore.GREEN + line + Style.RESET_ALL)
                    outfile.write(line + "\n")
                    lines_found += 1
            proc.wait()
            if proc.returncode != 0:
                err = proc.stderr.read().strip()
                print(f"{Fore.RED}[!] Error filtering SQLi URLs: {err}{Style.RESET_ALL}")

        if lines_found == 0:
            print(f"{Fore.YELLOW}[!] No potential SQLi URLs found.{Style.RESET_ALL}")
            return False
        else:
            print(f"{Fore.GREEN}[+] Found {lines_found} potential SQLi URLs.{Style.RESET_ALL}")
            return True

    except Exception as e:
        print(f"{Fore.RED}[!] Exception during SQLi filtering: {e}{Style.RESET_ALL}")
        return False

def run_sqlmap_on_urls(sqlifilter_out):
    print(f"{Fore.BLUE}[+] Starting sqlmap scans on filtered URLs...{Style.RESET_ALL}")
    try:
        with open(sqlifilter_out, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            print(f"{Fore.YELLOW}[!] No URLs found in {sqlifilter_out} to scan with sqlmap.{Style.RESET_ALL}")
            return

        for url in lines:
            print(f"{Fore.CYAN}[~] Running sqlmap on: {url}{Style.RESET_ALL}")
            command = f"sqlmap -u \"{url}\" --parse-errors --current-db --invalid-logical --invalid-bignum --invalid-string --risk 3 --batch"
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in proc.stdout:
                print(Fore.GREEN + line.strip() + Style.RESET_ALL)
            proc.wait()
            if proc.returncode != 0:
                err = proc.stderr.read().strip()
                print(f"{Fore.RED}[!] sqlmap command failed: {err}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Exception running sqlmap: {e}{Style.RESET_ALL}")

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
        crt_command = f"""curl -s "https://crt.sh/?q={domain}&output=json" | jq -r '.[].name_value' | grep -Po '(\\w+\\.{domain.replace('.', '\\.')})$' | anew {out_dir}/subdomains.txt"""
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

    # 3. httpx – SHOW ALIVE
    run_command_show_output(
        f"httpx-toolkit -l {out_dir}/subdomains.txt -ports 80,443,8080,8000,8123,8313,8888,9090,5555,4444,4443,3000,3001,8443,8081,5000,5001,7001,9200,5601,9000,3838,8880 -threads 200 -silent",
        "Probing live subdomains with httpx...",
        output_file=f"{out_dir}/subdomains_alive.txt"
    )

    # 4. nuclei - CORS — SHOW OUTPUT
    run_command_show_output(
        f"nuclei -l {out_dir}/subdomains_alive.txt -tags cors -c 30 -silent",
        "Scanning for CORS issues with nuclei...",
        output_file=f"{out_dir}/nuclei_cors.txt"
    )

    # 5. Archive.org
    run_command(
        f"""curl -G "https://web.archive.org/cdx/search/cdx" --data-urlencode "url=*.{domain}/*" --data-urlencode "collapse=urlkey" --data-urlencode "output=text" --data-urlencode "fl=original" > {out_dir}/out.txt""",
        "Querying archive.org for historic URLs..."
    )

    # 6. Filter sensitive file extensions and keywords
    print(f"{Fore.BLUE}[+] Filtering sensitive file extensions...{Style.RESET_ALL}")
    extensions = (
        r"/(admin|config|backup|logs|uploads|tmp|var|wp-content|vendor|node_modules|\.git|\.svn)|"
        r"\.log|\.sql|\.env|\.conf|\.bak|\.txt|\.json|\.xml|\.yaml|\.yml|\.ini|\.pem|\.key|\.cer|\.crt|"
        r"\.pfx|\.zip|\.tar|\.gz|\.7z|\.rar|\.tgz|\.rdp|\.ppk|\.sh|\.bat|\.ps1|\.php|\.py|\.java|\.js|"
        r"\.html|\.htaccess|\.DS_Store|config|settings|secrets|credentials|password|api_key|database|"
        r"dump|env|\.gitignore|\.htpasswd|wp-config\.php|robots\.txt|sitemap\.xml|web\.config|"
        r"package-lock\.json|composer\.lock"
    )
    run_command_show_output(
        f"cat {out_dir}/out.txt | uro | grep -Ei \"{extensions}\"",
        "Extracting potentially sensitive file URLs...",
        output_file=f"{out_dir}/sensitive_files.txt"
    )

    # 7. Check if sensitive URLs are still alive — SHOW LIVE
    run_command_show_output(
        f"httpx-toolkit -l {out_dir}/sensitive_files.txt -silent",
        "Checking if sensitive files are still accessible...",
        output_file=f"{out_dir}/sensitive_files_alive.txt"
    )

    # 8. Katana crawling with live subdomains
    katana_out = f"{out_dir}/katanacrawl.txt"
    run_command_show_output(
        f"katana -list {out_dir}/subdomains_alive.txt -o {katana_out} -d 4 -jc -ef css,png,svg,ico,woff,gif",
        "Running Katana crawling on live subdomains...",
        output_file=katana_out
    )

    # 9. Filter URLs with gf for potential SQLi
    sqlifilter_out = f"{out_dir}/sqlifilter.txt"
    has_sqli = filter_sqli_urls(katana_out, sqlifilter_out)

    # 10. Ask user if they want to run sqlmap on filtered URLs
    if has_sqli:
        use_sqlmap = input(Fore.YELLOW + "\nDo you want to run sqlmap on the filtered URLs? (y/N): " + Style.RESET_ALL).strip().lower()
        if use_sqlmap == "y":
            run_sqlmap_on_urls(sqlifilter_out)
    else:
        print(f"{Fore.YELLOW}[!] No URLs to run sqlmap on.{Style.RESET_ALL}")

    print(f"\n✅ {Fore.GREEN}Recon process completed! Check the results in {out_dir}/{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Process interrupted by user (Ctrl+C). Exiting cleanly...{Style.RESET_ALL}")
        exit(0)
