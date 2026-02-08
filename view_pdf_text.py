"""
Quick script to view extracted text from PDF
"""
from agent import FNOLExtractor

extractor = FNOLExtractor()
text = extractor.load_document("ACORD-Automobile-Loss-Notice-12.05.16.pdf")

print("="*70)
print("EXTRACTED TEXT FROM PDF")
print("="*70)
print(f"\nTotal characters: {len(text)}\n")
print(text[:2000])  # First 2000 characters
print("\n..." if len(text) > 2000 else "")
print(f"\n[Full text is {len(text)} characters]")
