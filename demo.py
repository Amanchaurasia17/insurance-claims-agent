"""
Demo script to showcase the Insurance Claims Processing Agent
Runs all scenarios and displays results
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import FNOLExtractor, ClaimRouter
from agent.models import ClaimData
import json


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_result_summary(filename, claim_data):
    """Print a summary of the processing result"""
    print(f"📄 Document: {filename}")
    print(f"🎯 Route: {claim_data.recommendedRoute}")
    
    if claim_data.missingFields:
        print(f"⚠️  Missing: {', '.join(claim_data.missingFields)}")
    else:
        print("✅ All fields present")
    
    # Extract key info
    if claim_data.extractedFields.assetDetails and claim_data.extractedFields.assetDetails.estimatedDamage:
        print(f"💰 Damage: ${claim_data.extractedFields.assetDetails.estimatedDamage:,.2f}")
    
    if claim_data.extractedFields.otherMandatoryFields and claim_data.extractedFields.otherMandatoryFields.claimType:
        print(f"📋 Type: {claim_data.extractedFields.otherMandatoryFields.claimType}")
    
    print(f"\n💭 Reasoning: {claim_data.reasoning[:150]}...")
    print("-" * 70)


def run_demo():
    """Run demonstration of all scenarios"""
    
    print_header("Insurance Claims Processing Agent - Demo")
    print("This demo processes 5 sample FNOL documents demonstrating")
    print("different routing scenarios based on business rules.\n")
    
    # Initialize components
    extractor = FNOLExtractor()
    router = ClaimRouter()
    
    # Get sample documents
    sample_dir = Path(__file__).parent / 'sample_documents'
    documents = sorted(sample_dir.glob('*.txt'))
    
    if not documents:
        print("❌ No sample documents found!")
        return
    
    print(f"Found {len(documents)} documents to process\n")
    input("Press Enter to start processing...")
    
    results = []
    
    # Process each document
    for i, doc_path in enumerate(documents, 1):
        print_header(f"Processing Document {i}/{len(documents)}")
        
        try:
            # Load and extract
            print(f"Loading: {doc_path.name}...")
            text = extractor.load_document(str(doc_path))
            print(f"✓ Loaded {len(text)} characters")
            
            print("Extracting fields...")
            fields = extractor.extract_fields(text)
            print("✓ Extraction complete")
            
            print("Validating...")
            missing = extractor.identify_missing_fields(fields)
            print("✓ Validation complete")
            
            print("Routing...")
            route_result = router.route_claim(fields, missing)
            print("✓ Routing complete")
            
            # Create result
            claim_data = ClaimData(
                extractedFields=fields,
                missingFields=missing,
                recommendedRoute=route_result.route,
                reasoning=route_result.reasoning
            )
            
            results.append((doc_path.name, claim_data))
            
            # Print summary
            print()
            print_result_summary(doc_path.name, claim_data)
            
            if i < len(documents):
                input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            continue
    
    # Final summary
    print_header("Processing Complete - Summary")
    
    print("📊 Routing Distribution:\n")
    
    routes = {}
    for filename, claim_data in results:
        route = claim_data.recommendedRoute
        if route not in routes:
            routes[route] = []
        routes[route].append(filename)
    
    for route, files in routes.items():
        print(f"  {route}:")
        for f in files:
            print(f"    • {f}")
        print()
    
    print(f"✅ Successfully processed {len(results)}/{len(documents)} documents")
    print(f"📁 Results saved to: output/\n")
    
    # Show routing rules
    print_header("Routing Rules Applied")
    print("""
    Priority  Condition                          Route
    ────────────────────────────────────────────────────────────────
    1st       Missing mandatory fields       →  Manual Review
    2nd       Fraud keywords detected        →  Investigation Flag
    3rd       Claim type = injury            →  Specialist Queue
    4th       Estimated damage < $25,000     →  Fast-track
    5th       Default                        →  Standard Processing
    """)
    
    print_header("Demo Complete")
    print("To run the agent manually, use:")
    print("  python main.py --file sample_documents/fnol_1_fasttrack.txt")
    print("  python main.py --process-all")
    print("\nFor more information, see README.md\n")


if __name__ == '__main__':
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n❌ Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Demo failed: {str(e)}")
        sys.exit(1)
