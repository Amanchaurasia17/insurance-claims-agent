# Autonomous Insurance Claims Processing Agent

## Problem Statement
A lightweight AI agent that processes First Notice of Loss (FNOL) documents by:
- Extracting key fields from insurance claims
- Identifying missing or inconsistent information
- Classifying claims and routing them to appropriate workflows
- Providing explanations for routing decisions

## Features
✅ Extract policy, incident, and party information from FNOL documents  
✅ Identify missing mandatory fields  
✅ Intelligent claim routing based on business rules  
✅ Support for PDF and TXT document formats  
✅ JSON output with extracted data and routing recommendations  
✅ Fraud detection keywords and special case handling  

## Project Structure
```
Synapx/
├── agent/
│   ├── __init__.py
│   ├── extractor.py       # Field extraction logic
│   ├── router.py          # Routing rules engine
│   └── models.py          # Data models (Pydantic)
├── sample_documents/      # Sample FNOL documents
│   └── ACORD-Automobile-Loss-Notice-12.05.16.pdf
├── tests/
│   ├── __init__.py
│   └── test_agent.py      # Unit tests
├── output/                # Processed claims output
├── main.py                # Main entry point
├── demo.py                # Interactive demo
├── view_pdf_text.py       # PDF text viewer utility
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps
```bash
# Clone the repository
git clone <repository-url>
cd insurance-claims-agent

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Process a Document
```bash
python main.py --file sample_documents/ACORD-Automobile-Loss-Notice-12.05.16.pdf
```

### Process with Output to File
```bash
python main.py --file sample_documents/ACORD-Automobile-Loss-Notice-12.05.16.pdf --output output/result.json
```

### View Extracted PDF Text
```bash
python view_pdf_text.py
```

## Routing Rules

The agent applies the following routing logic:

| Condition | Route | Priority |
|-----------|-------|----------|
| Missing mandatory fields | **Manual Review** | Highest |
| Fraud keywords detected | **Investigation Flag** | High |
| Claim type = injury | **Specialist Queue** | High |
| Estimated damage < $25,000 | **Fast-track** | Medium |
| Default | **Standard Processing** | Low |

### Fraud Keywords
The system flags claims containing: `fraud`, `fraudulent`, `inconsistent`, `staged`, `suspicious`, `fabricated`, `false`

## Output Format

```json
{
  "extractedFields": {
    "policyInformation": {
      "policyNumber": "POL-2024-001234",
      "policyholderName": "John Doe",
      "effectiveDates": {
        "start": "2024-01-01",
        "end": "2025-01-01"
      }
    },
    "incidentInformation": {
      "date": "2024-11-15",
      "time": "14:30",
      "location": "123 Main St, Springfield",
      "description": "Vehicle collision at intersection"
    },
    "involvedParties": {
      "claimant": "John Doe",
      "thirdParties": ["Jane Smith"],
      "contactDetails": {
        "phone": "555-1234",
        "email": "john.doe@email.com"
      }
    },
    "assetDetails": {
      "assetType": "Vehicle",
      "assetId": "VIN123456789",
      "estimatedDamage": 15000
    },
    "otherMandatoryFields": {
      "claimType": "auto",
      "attachments": ["photo1.jpg", "police_report.pdf"],
      "initialEstimate": 15000
    }
  },
  "missingFields": [],
  "recommendedRoute": "Fast-track",
  "reasoning": "Estimated damage ($15,000) is below $25,000 threshold. All mandatory fields present. No fraud indicators detected."
}
```

## Technical Approach

### 1. Document Parsing
- **PDF Support**: Uses PyPDF2 for PDF text extraction
- **Text Files**: Direct file reading with UTF-8 encoding
- **Preprocessing**: Text normalization and cleanup

### 2. Field Extraction
- **Pattern Matching**: Regex-based extraction for structured fields
- **Contextual Search**: Keyword-based field identification
- **Validation**: Type checking and format validation using Pydantic

### 3. Missing Field Detection
- Compares extracted fields against mandatory field checklist
- Reports specific missing fields with field names
- Differentiates between missing and incomplete data

### 4. Routing Engine
- Rule-based decision tree implementation
- Priority-based rule evaluation (highest priority first)
- Multi-condition support (can flag multiple issues)

### 5. Reasoning Generation
- Explains routing decision with specific evidence
- References extracted field values
- Highlights any red flags or special conditions

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Or use the included test script:
```bash
python tests/test_agent.py
```

## Sample Documents

The project includes a sample ACORD standard insurance form:

- **ACORD-Automobile-Loss-Notice-12.05.16.pdf** - Standard ACORD automobile loss notice form template

## Extensibility

### Adding New Fields
Edit `agent/models.py` to add new field definitions to the data models.

### Custom Routing Rules
Modify `agent/router.py` to add or update routing logic in the `route_claim()` method.

### Supporting New Document Formats
Extend `agent/extractor.py` with additional parsers (e.g., DOCX, images with OCR).

## Additional Utilities

### view_pdf_text.py
Quick utility to view raw text extracted from PDF documents:
```bash
python view_pdf_text.py
```

### demo.py
Interactive demo script to showcase the agent's capabilities:
```bash
python demo.py
```

## Future Enhancements

- 🔄 OCR support for scanned documents
- 🤖 Machine learning model for advanced field extraction
- 📊 Dashboard for claim analytics
- 🔗 Integration with insurance management systems
- 📧 Email notification system
- 🌐 REST API for remote processing
- 🗄️ Database storage for processed claims

---

## Project Overview

**Current Status:** Production-ready insurance claims processing agent

**Key Components:**
- ✅ Field extraction engine with regex patterns
- ✅ Priority-based routing system (5 rules)
- ✅ PDF and text document support
- ✅ Type-safe data models (Pydantic)
- ✅ Comprehensive test suite (12 tests)
- ✅ JSON output format
- ✅ CLI interface with multiple options

**Files:** 13 core files | **Code:** ~1,500 lines | **Tests:** 12/12 passing
