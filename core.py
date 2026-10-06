import csv
import json
import logging
import re
from collections import Counter
from pathlib import Path
from disposable_domains import DISPOSABLE_DOMAINS

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s"
    )

def validate_file(path):
    try:
        if path.suffix.lower() == ".txt":
            with open(path, "r",) as file:
                lines = file.readlines()
                data = [line.strip().lower() for line in lines]
                return data
        else:
            raise ValueError(f"Incompatible file format")
    except ValueError as e:
        logging.info(f"The process failed: {e}")
        return []
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        logging.error(f"Problem accessing the file: {e}")
        return []

def validate_email(raw_list):
    valid_pattern = r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$"
    deconstruct_email = r"([\w.+-]+)@([\w-]+\.[a-zA-Z]{2,})"

    try:
        if isinstance(raw_list, list):
            valid_emails = []
            invalid_emails = []

            for email in raw_list:
                        try: 
                            if re.match(valid_pattern, email):
                                match = re.match(deconstruct_email, email)
                                user, domain = match.groups()
                                valid_emails.append({"email": email, "user": user, "domain": domain, "valid": True})
                                logging.info(f"Email processed successfully: {email}")  
                            else:
                                invalid_emails.append(email)
                                raise ValueError(f"suspicious format")                                   
                        except ValueError as e:
                            logging.error(f"Invalid email address {email} : {e}")
            return valid_emails, invalid_emails       
        else:
            raise TypeError(f"Data received in a format that is incompatible with the system")   
    except TypeError as e:          
        logging.critical(f"Error while attempting to process the list: {e}")
        return [], []

def assess_risk(valid_emails):
    white_list = []
    black_list = []

    suspect_list = ["abuse@", "report@", "postmaster@", "admin@"]

    for item in valid_emails:
        try:
            if item["user"] + "@" not in suspect_list:
                white_list.append(item)
                logging.info(f"Classified as not under suspicion: {item['email']}")
            else:
                black_list.append(item)
                logging.info(f"Suspect found: {item['email']}")
        except Exception as e:
            logging.error(f"Unexpected error classifying an item: {e}")

    return white_list, black_list
    
def remove_duplicates(valid_emails):
    seen = set()
    unique_list = []
    duplicates = []

    for item in valid_emails:
        if item["email"] not in seen:
            seen.add(item["email"])
            unique_list.append(item)
        else:
            duplicates.append(item)

    number_of_duplicates = Counter([item["email"] for item in duplicates])

    logging.info(f"duplicates removed")
    return unique_list, duplicates, number_of_duplicates

def load_disposable_domains(path):
    path = Path(path)
    try:
        with open(path, "r", encoding="utf-8") as file:
            return {line.strip().lower() for line in file}
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        logging.error(f"Problem accessing custom domains file: {e}. Falling back to default list.")
        return DISPOSABLE_DOMAINS

def filter_disposable(data, disposable_domains=DISPOSABLE_DOMAINS):
    clean_list = []
    disposable_list = []

    for item in data:
        if item["domain"].lower() in disposable_domains:
            disposable_list.append(item)
            logging.info(f"Disposable domain found: {item['email']}")
        else:
            clean_list.append(item)

    return clean_list, disposable_list

DEFAULT_FIELDNAMES = ["email", "user", "domain", "valid"]

def export_csv(data, path="output.csv", fieldnames=DEFAULT_FIELDNAMES):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def export_json(data, path="output.json"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_discard_report(invalid, duplicate_count, suspicious, disposable):
    report = []

    for email in invalid:
        report.append({"email": email, "reason": "invalid format"})
    for email, count in duplicate_count.items():
        total = count + 1
        report.append({
            "email": email,
            "reason": f"duplicate (appeared {total} times in total, {count} extra occurrence(s) remover)"})
    for item in suspicious:
        report.append({"email": item["email"], "reason": "suspicious/risk account"})
    for item in disposable:
        report.append({"email": item["email"], "reason": "disposable domain"})

    return report