from pathlib import Path
from core import (
    validate_file, validate_email,assess_risk, remove_duplicates,
      load_disposable_domains, filter_disposable, export_csv, export_json, build_discard_report
)

def main(folder, custom_domains_path=None):
    path = Path(folder)
    data = validate_file(path)

    valid, invalid = validate_email(data)
    unique, duplicates_items, duplicate_count = remove_duplicates(valid)
    approved, suspicious = assess_risk(unique)

    if custom_domains_path:
        domains = load_disposable_domains(custom_domains_path)
        clean, disposable = filter_disposable(approved, domains)
    else:
        clean, disposable = filter_disposable(approved)

    discard_report = build_discard_report(invalid, duplicate_count, suspicious, disposable)

    export_csv(discard_report, "discard_report.csv", fieldnames=["email", "reason"])
    export_csv(clean, "result.csv")
    export_json(clean, "result.json")

    print(f"Processed: {len(data)}")
    print(f"Valid: {len(valid)} | Invalid: {len(invalid)}")
    print(f"Unique: {len(unique)} | Duplicates removed: {sum(duplicate_count.values())}")
    print(f"Approved: {len(approved)} | Suspicious: {len(suspicious)}")
    print(f"Clean: {len(clean)} | Disposable: {len(disposable)}")
if __name__ == "__main__":
    path = input("Path to the email file: ")
    
    use_custom = input("Use a custom list of disposable domains? (y/n): ")
    if use_custom.lower() == "y":
        domains_path = input("Path to the domains file: ")
        main(path, domains_path)
    else:
        main(path)