import requests
import json
from reportlab.pdfgen import canvas
from urllib.parse import urlparse, urljoin, parse_qs
from bs4 import BeautifulSoup
import tldextract

# --------------------- Website Crawler ---------------------
class LinkFinder:
    def __init__(self, target, limit=100):
        self.start = target.rstrip('/')
        self.done = set()
        self.queue = [self.start]
        self.results = set()
        self.limit = limit
        self.base = tldextract.extract(self.start).top_domain_under_public_suffix

    def go(self):
        print("[*] Crawling site...")
        while self.queue and len(self.done) < self.limit:
            current = self.queue.pop(0)
            self.done.add(current)
            try:
                r = requests.get(current, timeout=5)
                html = BeautifulSoup(r.text, 'html.parser')
                self.results.add(current)
                for tag in html.find_all("a", href=True):
                    new_url = urljoin(current, tag['href'])
                    if self._inside(new_url):
                        self.queue.append(new_url)
            except:
                continue
        return list(self.results)

    def _inside(self, u):
        parts = urlparse(u)
        dom = tldextract.extract(u).top_domain_under_public_suffix
        return parts.scheme in ['http', 'https'] and dom == self.base

# --------------------- Parameter Extractor ---------------------
class ParamGrabber:
    def __init__(self, links):
        self.links = links
        self.params = {}

    def find(self):
        print("[*] Getting parameters...")
        for link in self.links:
            q = urlparse(link).query
            if q:
                keys = list(parse_qs(q).keys())
                self.params[link] = keys
        return self.params

# --------------------- Wayback URL Collector ---------------------
class ArchivePuller:
    def __init__(self, domain):
        self.d = domain

    def grab(self):
        print("[*] Hitting Wayback Machine...")
        api = f"https://web.archive.org/cdx/search/cdx?url={self.d}/*&output=json&fl=original&collapse=urlkey"
        tries = 3
        while tries:
            try:
                r = requests.get(api, timeout=30)
                data = r.json()
                return [x[0] for x in data[1:]]
            except Exception as err:
                print(f"[!] Error: {err}")
                tries -= 1
        return []

# --------------------- Parameter Fuzzer ---------------------
def fuzz_parameters(url, method="GET", wordlist="params.txt", keyword=None):
    results = []
    print("\n[+] Baseline comparison request...")
    try:
        baseline = requests.get(url, timeout=5)
        base_len = len(baseline.text)
        base_code = baseline.status_code
        print(f"Baseline → Status: {base_code}, Length: {base_len}\n")
    except Exception as e:
        print(f"[x] Failed to get baseline: {e}")
        return results

    with open(wordlist, 'r') as f:
        params = f.read().splitlines()

    for param in params:
        payload = {param: 'test123'}
        try:
            if method.upper() == "GET":
                r = requests.get(url, params=payload, timeout=5)
            else:
                r = requests.post(url, data=payload, timeout=5)

            result = {
                "param": param,
                "value": "test123",
                "status": r.status_code,
                "length": len(r.text)
            }
            results.append(result)
            print(f"{r.status_code} | {len(r.text)} bytes | Param: {param}")
        except Exception as e:
            print(f"[x] Error with param {param} → {e}")
    return results, base_len, base_code

# --------------------- Auth/Debug Parameter Tester ---------------------
suspicious_params = {
    "admin": "true",
    "is_admin": "1",
    "debug": "1",
    "access": "admin",
    "test": "1",
    "dev": "1"
}

def test_suspicious_parameters(url, base_len):
    print("[*] Testing common auth/debug parameters...")
    results = []
    for key, val in suspicious_params.items():
        try:
            r = requests.get(url, params={key: val}, timeout=5)
            result = {
                "param": key,
                "value": val,
                "status": r.status_code,
                "length": len(r.text)
            }
            results.append(result)
            print(f"{key}={val} → Status: {r.status_code}, Length: {len(r.text)}")
        except Exception as e:
            print(f"[!] Error testing {key} → {e}")
    return results

# --------------------- JSON Report Generator ---------------------
def save_json_report(data, filename="report.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"[+] JSON saved to {filename}")

# --------------------- PDF Report Generator ---------------------
def save_pdf_report(results, filename="report.pdf"):
    c = canvas.Canvas(filename)
    c.drawString(50, 800, "Parameter Testing Report")
    y = 770
    for r in results:
        line = f"{r['param']} = {r['value']} → Status: {r['status']} Length: {r['length']}"
        if y < 50:
            c.showPage()
            y = 800
        c.drawString(50, y, line)
        y -= 20
    c.save()
    print(f"[+] PDF saved to {filename}")

# --------------------- Interactive Input CLI ---------------------
if __name__ == "__main__":
    print("\n--- Parameter Testing Toolkit ---")
    url = input("Enter target URL (e.g. https://example.com/search): ").strip()

    if not urlparse(url).scheme:
        url = "https://" + url

    method = input("Request Method (GET/POST) [GET]: ").strip().upper() or "GET"
    wordlist = input("Path to wordlist [params.txt]: ").strip() or "params.txt"
    keyword = input("Optional keyword to look for in responses (leave blank if none): ").strip() or None

    run_auth_test = input("Run auth/debug param tests? (y/n): ").strip().lower() == 'y'
    save_reports = input("Save results as PDF/JSON? (y/n): ").strip().lower() == 'y'

    all_results = []

    print("\n[+] Running Crawler, Param Extractor & Wayback Lookup...")
    lf = LinkFinder(url)
    found_links = lf.go()

    pg = ParamGrabber(found_links)
    found_params = pg.find()
    for link, keys in found_params.items():
        print(f"{link} → {keys}")

    domain = urlparse(url).netloc
    arch = ArchivePuller(domain)
    wayback_urls = arch.grab()
    print(f"[+] Found {len(wayback_urls)} URLs from Wayback Machine (showing 10):")
    for w in wayback_urls[:10]:
        print(w)

    print("\n[+] Starting Parameter Fuzzing...")
    fuzzed, base_len, base_code = fuzz_parameters(url, method, wordlist, keyword)
    all_results.extend(fuzzed)

    if run_auth_test:
        print("\n[+] Running Auth/Debug Tester...")
        auth_results = test_suspicious_parameters(url, base_len)
        all_results.extend(auth_results)

    if save_reports:
        save_json_report(all_results)
        save_pdf_report(all_results)

    print("\n[*] Parameters with noticeable differences:")
    for r in all_results:
        if r['length'] != base_len or r['status'] != base_code:
            print(f"[!] {r['param']}={r['value']} → Status: {r['status']}, Length: {r['length']}")
