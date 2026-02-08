"""
Main entry point for Insurance Claims Processing Agent
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from agent import FNOLExtractor, ClaimRouter
from agent.models import ClaimData


class ClaimsProcessor:
    """Main claims processing orchestrator"""
    
    def __init__(self):
        """Initialize processor with extractor and router"""
        self.extractor = FNOLExtractor()
        self.router = ClaimRouter()
    
    def process_document(self, file_path: str) -> ClaimData:
        """
        Process a single FNOL document
        
        Args:
            file_path: Path to FNOL document
            
        Returns:
            ClaimData: Processing result
        """
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(file_path)}")
        print(f"{'='*60}\n")
        
        # Step 1: Load document
        print("Step 1: Loading document...")
        text = self.extractor.load_document(file_path)
        print(f"✓ Extracted {len(text)} characters\n")
        
        # Step 2: Extract fields
        print("Step 2: Extracting fields...")
        extracted_fields = self.extractor.extract_fields(text)
        print("✓ Field extraction complete\n")
        
        # Step 3: Identify missing fields
        print("Step 3: Validating mandatory fields...")
        missing_fields = self.extractor.identify_missing_fields(extracted_fields)
        if missing_fields:
            print(f"⚠ Missing fields: {', '.join(missing_fields)}\n")
        else:
            print("✓ All mandatory fields present\n")
        
        # Step 4: Route claim
        print("Step 4: Determining routing...")
        routing_result = self.router.route_claim(extracted_fields, missing_fields)
        print(f"✓ Route: {routing_result.route}\n")
        
        # Create result
        claim_data = ClaimData(
            extractedFields=extracted_fields,
            missingFields=missing_fields,
            recommendedRoute=routing_result.route,
            reasoning=routing_result.reasoning
        )
        
        return claim_data
    
    def save_result(self, claim_data: ClaimData, output_path: str):
        """
        Save processing result to JSON file
        
        Args:
            claim_data: Processing result
            output_path: Output file path
        """
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                claim_data.model_dump(exclude_none=False),
                f,
                indent=2,
                ensure_ascii=False
            )
        
        print(f"✓ Result saved to: {output_path}\n")
    
    def print_result(self, claim_data: ClaimData):
        """
        Print processing result in readable format
        
        Args:
            claim_data: Processing result
        """
        print("\n" + "="*60)
        print("PROCESSING RESULT")
        print("="*60)
        
        # Routing decision
        print(f"\n🎯 Recommended Route: {claim_data.recommendedRoute}")
        print(f"\n💭 Reasoning:\n{claim_data.reasoning}")
        
        # Missing fields
        if claim_data.missingFields:
            print(f"\n⚠ Missing Fields: {', '.join(claim_data.missingFields)}")
        else:
            print(f"\n✓ All mandatory fields present")
        
        # Extracted fields summary
        print("\n📋 Extracted Fields Summary:")
        
        if claim_data.extractedFields.policyInformation:
            pi = claim_data.extractedFields.policyInformation
            print(f"  Policy: {pi.policyNumber or 'N/A'}")
            print(f"  Policyholder: {pi.policyholderName or 'N/A'}")
        
        if claim_data.extractedFields.incidentInformation:
            ii = claim_data.extractedFields.incidentInformation
            print(f"  Incident Date: {ii.date or 'N/A'}")
            print(f"  Location: {ii.location or 'N/A'}")
        
        if claim_data.extractedFields.assetDetails:
            ad = claim_data.extractedFields.assetDetails
            if ad.estimatedDamage:
                print(f"  Estimated Damage: ${ad.estimatedDamage:,.2f}")
        
        if claim_data.extractedFields.otherMandatoryFields:
            om = claim_data.extractedFields.otherMandatoryFields
            print(f"  Claim Type: {om.claimType or 'N/A'}")
        
        print("\n" + "="*60 + "\n")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Insurance Claims Processing Agent - Process FNOL documents'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Path to FNOL document to process'
    )
    parser.add_argument(
        '--process-all',
        action='store_true',
        help='Process all sample documents'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file path (optional)'
    )
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='Output only JSON without readable format'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.process_all:
        parser.print_help()
        print("\nError: Must specify either --file or --process-all")
        sys.exit(1)
    
    # Create processor
    processor = ClaimsProcessor()
    
    # Process documents
    if args.process_all:
        # Process all sample documents
        sample_dir = Path(__file__).parent / 'sample_documents'
        if not sample_dir.exists():
            print(f"Error: Sample documents directory not found: {sample_dir}")
            sys.exit(1)
        
        # Get all txt files
        files = sorted(sample_dir.glob('*.txt'))
        if not files:
            print(f"Error: No FNOL documents found in {sample_dir}")
            sys.exit(1)
        
        print(f"\nFound {len(files)} documents to process\n")
        
        # Process each file
        for file_path in files:
            try:
                claim_data = processor.process_document(str(file_path))
                
                # Save to output directory
                output_dir = Path(__file__).parent / 'output'
                output_file = output_dir / f"{file_path.stem}_result.json"
                processor.save_result(claim_data, str(output_file))
                
                if not args.json_only:
                    processor.print_result(claim_data)
                
            except Exception as e:
                print(f"✗ Error processing {file_path.name}: {str(e)}\n")
                continue
        
        print(f"\n{'='*60}")
        print(f"Processing complete! Results saved to: output/")
        print(f"{'='*60}\n")
    
    else:
        # Process single file
        try:
            claim_data = processor.process_document(args.file)
            
            # Handle output
            if args.output:
                processor.save_result(claim_data, args.output)
            
            if args.json_only:
                # Print JSON to stdout
                print(json.dumps(
                    claim_data.model_dump(exclude_none=False),
                    indent=2,
                    ensure_ascii=False
                ))
            else:
                processor.print_result(claim_data)
            
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    main()
