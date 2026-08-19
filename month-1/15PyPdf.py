# pypdf vs pdfplumber, compared on a real SEC 10-K (Apple's, downloaded by
# 15sec_download.py + converted to PDF). Two things get compared:
#   1. Full-document extraction speed (Risk Factors etc. are plain prose --
#      speed matters when you're processing hundreds of pages of it).
#   2. Table quality on the actual income statement page -- this is where the
#      two libraries genuinely diverge.

import time
from pypdf import PdfReader
import pdfplumber

PDF_PATH = "../tracker/projects/1-sec-10k-analyzer/AAPL_10K_2025-10-31.pdf"
TABLE_PAGE = 54  # 0-indexed -- Apple's CONSOLIDATED STATEMENTS OF OPERATIONS

# 1. Full-document text extraction: speed + total characters
print("=== Full-document extraction ===\n")

start = time.time()
reader = PdfReader(PDF_PATH)
pypdf_text = "".join(page.extract_text() for page in reader.pages)
pypdf_time = time.time() - start
print(f"pypdf:      {len(reader.pages)} pages, {len(pypdf_text):,} chars, {pypdf_time:.2f}s")

start = time.time()
with pdfplumber.open(PDF_PATH) as pdf:
    plumber_text = "".join(page.extract_text() or "" for page in pdf.pages)
plumber_time = time.time() - start
print(f"pdfplumber: {len(pdf.pages)} pages, {len(plumber_text):,} chars, {plumber_time:.2f}s")
print(f"\npdfplumber was {plumber_time / pypdf_time:.1f}x slower than pypdf on the same document.")

# 2. Table quality: same page, both libraries, side by side
print("\n\n=== Table extraction on the income statement page ===\n")

print("--- pypdf (plain text, no table awareness) ---")
print(reader.pages[TABLE_PAGE].extract_text()[:600])

print("\n--- pdfplumber (plain text mode, same page) ---")
with pdfplumber.open(PDF_PATH) as pdf:
    print(pdf.pages[TABLE_PAGE].extract_text()[:600])

print("\n--- pdfplumber (structured table mode: extract_tables()) ---")
with pdfplumber.open(PDF_PATH) as pdf:
    table = pdf.pages[TABLE_PAGE].extract_tables()[0]
    for row in table[:10]:
        print(row)
