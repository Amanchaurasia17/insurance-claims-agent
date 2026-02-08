"""
Test suite for Insurance Claims Processing Agent
"""

import os
import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import FNOLExtractor, ClaimRouter
from agent.models import ExtractedFields


class TestFNOLExtractor(unittest.TestCase):
    """Test field extraction functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = FNOLExtractor()
    
    def test_extract_policy_number(self):
        """Test policy number extraction"""
        text = "Policy Number: POL-2024-001234"
        fields = self.extractor.extract_fields(text)
        self.assertEqual(fields.policyInformation.policyNumber, "POL-2024-001234")
    
    def test_extract_policyholder_name(self):
        """Test policyholder name extraction"""
        text = "Policyholder Name: John Doe"
        fields = self.extractor.extract_fields(text)
        self.assertEqual(fields.policyInformation.policyholderName, "John Doe")
    
    def test_extract_incident_date(self):
        """Test incident date extraction"""
        text = "Incident Date: 2024-11-15"
        fields = self.extractor.extract_fields(text)
        self.assertEqual(fields.incidentInformation.date, "2024-11-15")
    
    def test_extract_estimated_damage(self):
        """Test damage amount extraction"""
        text = "Estimated Damage: $15,000"
        fields = self.extractor.extract_fields(text)
        self.assertEqual(fields.assetDetails.estimatedDamage, 15000.0)
    
    def test_extract_claim_type(self):
        """Test claim type extraction"""
        text = "Claim Type: auto"
        fields = self.extractor.extract_fields(text)
        self.assertEqual(fields.otherMandatoryFields.claimType, "auto")
    
    def test_identify_missing_fields(self):
        """Test missing field detection"""
        # Create minimal fields
        fields = ExtractedFields(
            policyInformation=None,
            incidentInformation=None,
            involvedParties=None,
            assetDetails=None,
            otherMandatoryFields=None
        )
        
        missing = self.extractor.identify_missing_fields(fields)
        self.assertGreater(len(missing), 0)
        self.assertIn('policyNumber', missing)


class TestClaimRouter(unittest.TestCase):
    """Test routing logic functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.router = ClaimRouter()
        self.extractor = FNOLExtractor()
    
    def test_route_missing_fields(self):
        """Test routing with missing fields"""
        fields = ExtractedFields()
        missing = ['policyNumber', 'incidentDate']
        
        result = self.router.route_claim(fields, missing)
        self.assertEqual(result.route, "Manual Review")
        self.assertIn('missing_fields', result.flags)
    
    def test_route_fraud_detection(self):
        """Test fraud detection routing"""
        text = """
        Incident Date: 2024-11-15
        Description: This claim appears fraudulent and staged with inconsistent details
        Claim Type: auto
        Estimated Damage: $20,000
        Policy Number: POL-123
        Policyholder Name: John Doe
        Location: Main St
        Claimant: John Doe
        """
        
        fields = self.extractor.extract_fields(text)
        missing = self.extractor.identify_missing_fields(fields)
        
        result = self.router.route_claim(fields, missing)
        self.assertEqual(result.route, "Investigation Flag")
        self.assertIn('fraud_indicator', result.flags)
    
    def test_route_injury_claim(self):
        """Test injury claim routing"""
        text = """
        Incident Date: 2024-11-15
        Description: Accident with injuries
        Claim Type: injury
        Estimated Damage: $20,000
        Policy Number: POL-123
        Policyholder Name: John Doe
        Location: Main St
        Claimant: John Doe
        """
        
        fields = self.extractor.extract_fields(text)
        missing = self.extractor.identify_missing_fields(fields)
        
        result = self.router.route_claim(fields, missing)
        self.assertEqual(result.route, "Specialist Queue")
        self.assertIn('injury_claim', result.flags)
    
    def test_route_fast_track(self):
        """Test fast-track routing for low-value claims"""
        text = """
        Incident Date: 2024-11-15
        Description: Minor collision
        Claim Type: auto
        Estimated Damage: $15,000
        Policy Number: POL-123
        Policyholder Name: John Doe
        Location: Main St
        Claimant: John Doe
        """
        
        fields = self.extractor.extract_fields(text)
        missing = self.extractor.identify_missing_fields(fields)
        
        result = self.router.route_claim(fields, missing)
        self.assertEqual(result.route, "Fast-track")
        self.assertIn('low_value', result.flags)
    
    def test_route_standard_processing(self):
        """Test standard processing for high-value claims"""
        text = """
        Incident Date: 2024-11-15
        Description: Major collision
        Claim Type: auto
        Estimated Damage: $50,000
        Policy Number: POL-123
        Policyholder Name: John Doe
        Location: Main St
        Claimant: John Doe
        """
        
        fields = self.extractor.extract_fields(text)
        missing = self.extractor.identify_missing_fields(fields)
        
        result = self.router.route_claim(fields, missing)
        self.assertEqual(result.route, "Standard Processing")


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = FNOLExtractor()
        self.router = ClaimRouter()
    
    def test_process_sample_document(self):
        """Test processing a complete sample document"""
        sample_path = Path(__file__).parent.parent / 'sample_documents' / 'fnol_1_fasttrack.txt'
        
        if not sample_path.exists():
            self.skipTest("Sample document not found")
        
        # Load and extract
        text = self.extractor.load_document(str(sample_path))
        fields = self.extractor.extract_fields(text)
        missing = self.extractor.identify_missing_fields(fields)
        
        # Route
        result = self.router.route_claim(fields, missing)
        
        # Verify routing
        self.assertIsNotNone(result.route)
        self.assertIsNotNone(result.reasoning)
        self.assertGreater(len(result.reasoning), 0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestFNOLExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestClaimRouter))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
