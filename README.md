Email List Sorter

A Python tool for validating, deduplicating, and filtering email lists — with risk-account detection, disposable domain filtering, and detailed logging.

Features

- **Format validation** using regular expressions
- **Deduplication** (case-insensitive — `Joao@Gmail.com` and `joao@gmail.com` are treated as the same address)
- **Risk-account detection** (filters out system addresses like `abuse@`, `admin@`, `postmaster@`, `report@`)
- **Disposable domain filtering**, with a built-in default list and support for a custom list
- **Clean output** in CSV and JSON formats
- **Discard report** listing every removed email and the reason it was removed
- **Detailed logging** of every step, saved to `app.log`
- **Robust error handling** — a problem with one email, or with a missing file, never stops the whole process

Requirements

- Python 3.10 or newer (no external libraries needed — only the standard library)

Project structure

```
email-list-sorter/
├── core.py                  # Core logic: validation, deduplication, filtering, export
├── main.py                  # Entry point — reads input and runs the pipeline
├── disposable_domains.py    # Default list of disposable email domains
├── emails.txt                # Example input file
└── dominios_teste.txt        # Example custom disposable-domain list
```

How to use

1. Prepare a `.txt` file with one email address per line:

   ```
   joao@gmail.com
   maria@empresa.com
   invalido@
   abuse@site.com
   ```

2. Run the script:

   ```
   python main.py
   ```

3. When prompted, enter the path to your email file:

   ```
   Path to the email file: emails.txt
   ```

4. Optionally, choose to use a custom disposable-domain list instead of the built-in default:

   ```
   Use a custom list of disposable domains? (y/n): y
   Path to the domains file: dominios_teste.txt
   ```

   The custom domains file should be a plain `.txt` file with one domain per line (e.g. `mailinator.com`).

Output

Running the tool produces:

| File | Description |
|---|---|
| `result.csv` | Final cleaned list of emails, in CSV format |
| `result.json` | Final cleaned list of emails, in JSON format |
| `discard_report.csv` | Every removed email, with the reason (invalid format, duplicate, risk account, or disposable domain) |
| `app.log` | Full processing log, including every validation, classification, and error |

Example `discard_report.csv`

```
email,reason
invalido@,invalid format
joao@gmail.com,"duplicate (appeared 4 times in total, 3 extra occurrence(s) removed)"
abuse@site.com,suspicious/risk account
gogo@mailinator.com,disposable domain
```

Design notes

- Core functions (`validate_email`, `assess_risk`, `remove_duplicates`, `filter_disposable`, `export_csv`, `export_json`) contain no `input()` or `print()` calls — they only take data in and return data out. This keeps them reusable across different interfaces (command line, a future GUI, or a web app) without rewriting the logic itself.
- Each processing step has its own error handling, so a single malformed email or an inaccessible file never interrupts the rest of the batch.
- Disposable domain filtering falls back to the built-in default list if a custom list file can't be read, and logs the issue — the tool never silently skips protection.