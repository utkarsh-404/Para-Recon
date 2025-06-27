# 🛡️ Parameter Testing Toolkit

A comprehensive CLI tool for scanning web applications for potential parameter vulnerabilities.

## 🔧 Features

* 🔸 **Website Crawler** — Crawls all internal links from a domain.
* 📅 **Parameter Extractor** — Collects all query parameters from discovered URLs.
* 🤠 **Wayback URL Collector** — Gathers archived URLs from the Wayback Machine.
* 💣 **Parameter Fuzzer** — Brute-forces hidden GET/POST parameters using a wordlist.
* 🛠️ **Auth/Debug Parameter Tester** — Tries sensitive parameters like `admin=true`, `debug=1`.
* 📄 **PDF/JSON Report Generator** — Outputs results in human- and machine-readable formats.
* ✅ **Auto-detects differences** — Highlights any param that changes server behavior.

## ⚙️ Requirements

* Python 3.8+
* Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```

## 🚀 How to Use

```bash
python recon.py
```

Then follow the prompts:

* Enter a target URL (e.g., `https://example.com/search`)
* Choose GET or POST
* Provide a parameter wordlist (default: `params.txt`)
* Optionally check for sensitive debug parameters
* Save output as PDF/JSON

## 📂 Output

* `report.json` — Raw results
* `report.pdf` — Printable summary
* Console output shows:

  * All parameters tested
  * Parameters that triggered changes (status code or length)

## 📌 Notes

* Works best on dynamic or API endpoints, not static HTML pages.
* Add your own parameters to `params.txt` for deeper testing.

## 🧠 Example Use Case

Testing for:

* Broken Access Control
* Hidden Admin Panels
* Misconfigured Debug Modes
* IDOR / Input reflection

---

Created with 💻 by \[Utkarsh Raj]
