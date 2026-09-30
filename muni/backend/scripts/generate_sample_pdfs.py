"""Generate sample municipal-policy PDFs under data/documents (dev helper)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "documents"

TOPICS: dict[str, str] = {
    "remote-work-policy": (
        "Remote Work Policy\n\n"
        "Employees may work remotely up to three days per week, subject to "
        "manager approval. Core collaboration hours are 10:00 to 15:00 local "
        "time. Employees must be reachable during core hours and attend "
        "mandatory in-person town halls once per quarter.\n\n"
        "Equipment: the municipality provides a laptop and a stipend of "
        "40 euros per month for internet costs. Remote workers must follow "
        "the information-security policy when handling citizen data."
    ),
    "leave-policy": (
        "Leave Policy\n\n"
        "Full-time employees accrue 25 days of paid annual leave per year. "
        "Leave requests must be submitted through the HR portal at least "
        "14 days in advance. Sick leave requires a medical certificate after "
        "three consecutive days.\n\n"
        "Parental leave follows national regulations: 16 weeks fully paid for "
        "either parent, transferable up to 8 weeks between parents."
    ),
    "it-security-policy": (
        "IT Security Policy\n\n"
        "All staff must enable multi-factor authentication on municipal "
        "accounts. Passwords must be at least 14 characters and rotated "
        "yearly. Suspicious emails must be reported to the security team "
        "within one hour using the phishing button in the mail client.\n\n"
        "Personal devices may access email only through the managed web "
        "client; full VPN access is restricted to enrolled devices."
    ),
    "procurement-policy": (
        "Procurement Policy\n\n"
        "Purchases below 500 euros may be approved by team leads. Purchases "
        "between 500 and 10,000 euros require two written quotes and finance "
        "sign-off. Anything above 10,000 euros goes through a formal tender "
        "process with a minimum three-supplier shortlist.\n\n"
        "All contracts above 50,000 euros must be reviewed by the legal "
        "department before signature."
    ),
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    for slug, body in TOPICS.items():
        target = OUT_DIR / f"{slug}.pdf"
        doc = SimpleDocTemplate(str(target), pagesize=letter)
        doc.build([Paragraph(body.replace("\n\n", "<br/><br/>"), styles["BodyText"]),
                   Spacer(1, 12)])
        print(f"wrote {target}")


if __name__ == "__main__":
    main()
