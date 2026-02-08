# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FNOL Document (PDF/TXT)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Document Loader                            │
│  • PDF Extraction (PyPDF2)                                      │
│  • Text File Reading                                            │
│  • Format Detection                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FNOL Extractor Engine                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Pattern-Based Extraction (Regex)                        │  │
│  │  • Policy Information                                    │  │
│  │  • Incident Details                                      │  │
│  │  • Involved Parties                                      │  │
│  │  • Asset Information                                     │  │
│  │  • Mandatory Fields                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Field Validation Layer                         │
│  • Missing Field Detection                                      │
│  • Type Validation (Pydantic)                                   │
│  • Format Verification                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Routing Decision Engine                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Priority-Based Rules:                                   │  │
│  │  1. Missing Fields → Manual Review                       │  │
│  │  2. Fraud Keywords → Investigation                       │  │
│  │  3. Injury Claims → Specialist Queue                     │  │
│  │  4. Low Value → Fast-track                               │  │
│  │  5. Default → Standard Processing                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Output Generator                           │
│  • JSON Formatting                                              │
│  • Reasoning Explanation                                        │
│  • Result Validation                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Structured JSON Output                          │
│  {                                                              │
│    "extractedFields": {...},                                    │
│    "missingFields": [...],                                      │
│    "recommendedRoute": "...",                                   │
│    "reasoning": "..."                                           │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          Main.py                                 │
│                   (CLI Entry Point)                              │
│  • Argument Parsing                                              │
│  • Orchestration Logic                                           │
│  • Batch Processing                                              │
└────────┬─────────────────────────────────────────────┬──────────┘
         │                                             │
         ▼                                             ▼
┌──────────────────────────┐              ┌──────────────────────┐
│   FNOLExtractor          │              │    ClaimRouter       │
│   (extractor.py)         │              │    (router.py)       │
│  ┌────────────────────┐  │              │  ┌────────────────┐ │
│  │ load_document()    │  │              │  │ route_claim()  │ │
│  │ extract_fields()   │  │              │  │ _check_fraud() │ │
│  │ identify_missing() │  │              │  │ _is_injury()   │ │
│  └────────────────────┘  │              │  └────────────────┘ │
└────────┬─────────────────┘              └─────────┬────────────┘
         │                                          │
         └──────────────┬───────────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   Data Models       │
              │   (models.py)       │
              │  ┌───────────────┐  │
              │  │ ClaimData     │  │
              │  │ ExtractedFields│ │
              │  │ RoutingResult │  │
              │  └───────────────┘  │
              │  Pydantic Models    │
              └─────────────────────┘
```

## Data Flow Diagram

```
Input Document
      │
      ▼
┌──────────────┐
│   Load Doc   │ ─────► Parse Format (PDF/TXT)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Extract Text │ ─────► Raw Text Content
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│  Apply Regex Patterns        │
│  • Policy: [A-Z0-9\-]+       │
│  • Date: \d{4}-\d{2}-\d{2}   │
│  • Amount: \$[\d,]+          │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Create Structured Objects   │
│  (Pydantic Models)           │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Validate Fields             │
│  • Check mandatory present   │
│  • Type validation           │
└──────┬───────────────────────┘
       │
       ├──► Missing? ────► Manual Review
       │
       ├──► Fraud? ─────► Investigation
       │
       ├──► Injury? ────► Specialist
       │
       ├──► Low $? ─────► Fast-track
       │
       └──► Default ────► Standard
              │
              ▼
        ┌──────────┐
        │   JSON   │
        │  Output  │
        └──────────┘
```

## Module Dependency Graph

```
                    main.py
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
    FNOLExtractor           ClaimRouter
           │                       │
           └───────────┬───────────┘
                       │
                       ▼
                  models.py
           (Pydantic Data Models)
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
    PolicyInfo  IncidentInfo  AssetDetails
```

## File Structure

```
Synapx/
│
├── agent/                          # Core agent package
│   ├── __init__.py                # Package initialization
│   ├── extractor.py               # Field extraction engine
│   ├── router.py                  # Routing decision logic
│   └── models.py                  # Pydantic data models
│
├── sample_documents/              # Test FNOL documents
│   └── ACORD-Automobile-Loss-Notice-12.05.16.pdf  # ACORD form template
│
├── tests/                         # Test suite
│   ├── __init__.py
│   └── test_agent.py             # Unit & integration tests
│
├── output/                        # Processed results (JSON)
│   └── acord_form_result.json    # Sample output
│
├── main.py                        # CLI entry point
├── demo.py                        # Interactive demo
├── view_pdf_text.py              # PDF text viewer utility
├── requirements.txt               # Python dependencies
│
├── README.md                      # Main documentation
└── ARCHITECTURE.md                # This file
```

## Processing Pipeline

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌────────┐
│  Load   │───▶│ Extract │───▶│ Validate │───▶│  Route  │───▶│ Output │
└─────────┘    └─────────┘    └──────────┘    └─────────┘    └────────┘
    │              │               │                │              │
    │              │               │                │              │
    ▼              ▼               ▼                ▼              ▼
  PDF/TXT    Regex Patterns   Mandatory      Business Rules    JSON
   Files      + Parsing        Fields          Priority          Format
```

## Routing Decision Tree

```
                    Start
                      │
                      ▼
           ┌─────────────────────┐
           │ Missing Mandatory?  │
           └─────────┬───────────┘
                  Yes│  No
             ┌───────┴───────┐
             ▼               ▼
      Manual Review    ┌──────────────┐
                       │ Fraud Words? │
                       └──────┬───────┘
                           Yes│  No
                      ┌────────┴────────┐
                      ▼                 ▼
               Investigation      ┌──────────┐
                  Flag            │ Injury?  │
                                  └─────┬────┘
                                     Yes│  No
                                ┌───────┴────────┐
                                ▼                ▼
                           Specialist      ┌──────────┐
                             Queue         │ Low $?   │
                                           └─────┬────┘
                                              Yes│  No
                                         ┌────────┴────────┐
                                         ▼                 ▼
                                    Fast-track        Standard
                                                    Processing
```

## Extension Points

```
┌─────────────────────────────────────────────────────────┐
│               Future Enhancements                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Machine Learning Integration                       │
│     ├─ NER for field extraction                        │
│     ├─ Classification for routing                      │
│     └─ Confidence scoring                              │
│                                                         │
│  2. OCR Support                                        │
│     ├─ Scanned documents                               │
│     ├─ Image preprocessing                             │
│     └─ Tesseract/Azure Form Recognizer                 │
│                                                         │
│  3. API Layer                                          │
│     ├─ REST API with FastAPI                           │
│     ├─ Async processing                                │
│     └─ Webhook notifications                           │
│                                                         │
│  4. Database Integration                               │
│     ├─ PostgreSQL/MongoDB                              │
│     ├─ Claim history tracking                          │
│     └─ Analytics dashboard                             │
│                                                         │
│  5. Advanced Validation                                │
│     ├─ Cross-field validation                          │
│     ├─ Business rule engine                            │
│     └─ Configurable rules                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────┐
│                  Technology Stack                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Language:        Python 3.8+                       │
│  Data Models:     Pydantic 2.5+                     │
│  PDF Processing:  PyPDF2 3.0+                       │
│  Pattern Match:   Regex (built-in re module)       │
│  Testing:         unittest (built-in)               │
│  CLI:             argparse (built-in)               │
│  Date Parsing:    python-dateutil                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---
