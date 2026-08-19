# Downloads the latest 10-K filing for AAPL, MSFT, JPM from SEC EDGAR.
#
# SEC EDGAR requires every request to self-identify via a User-Agent header
# (name/app + a real contact email) — no API key or signup needed, just this
# header. See https://www.sec.gov/os/webmaster-faq#developers

import os
import time
import requests

USER_AGENT = "Yogesh-AI-Engineer-Curriculum thegoyalyogesh@gmail.com"
HEADERS = {"User-Agent": USER_AGENT}

COMPANIES = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "JPM": "0000019617",
}

OUT_DIR = "../tracker/projects/1-sec-10k-analyzer"


def get_latest_10k(cik: str) -> dict:
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    data = requests.get(url, headers=HEADERS).json()
    recent = data["filings"]["recent"]

    for i, form in enumerate(recent["form"]):
        if form == "10-K":
            return {
                "accession": recent["accessionNumber"][i],
                "primary_doc": recent["primaryDocument"][i],
                "filing_date": recent["filingDate"][i],
            }
    raise ValueError("No 10-K found in recent filings")


def download_filing(ticker: str, cik: str):
    filing = get_latest_10k(cik)
    accession_no_dashes = filing["accession"].replace("-", "")
    doc_url = (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
        f"{accession_no_dashes}/{filing['primary_doc']}"
    )

    response = requests.get(doc_url, headers=HEADERS)
    response.raise_for_status()

    out_path = os.path.join(OUT_DIR, f"{ticker}_10K_{filing['filing_date']}.htm")
    with open(out_path, "wb") as f:
        f.write(response.content)

    print(f"{ticker}: filed {filing['filing_date']} -> {out_path} ({len(response.content):,} bytes)")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for ticker, cik in COMPANIES.items():
        download_filing(ticker, cik)
        time.sleep(0.2)  # stay well under SEC's rate limit
