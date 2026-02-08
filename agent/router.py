"""
Claim routing logic based on business rules
"""

from typing import List
from .models import ExtractedFields, RoutingResult


class ClaimRouter:
    """Route claims based on extracted data and business rules"""
    
    # Routing constants
    FAST_TRACK_THRESHOLD = 25000
    FRAUD_KEYWORDS = [
        'fraud', 'fraudulent', 'inconsistent', 'staged',
        'suspicious', 'fabricated', 'false', 'fake'
    ]
    
    # Route types
    ROUTE_MANUAL_REVIEW = "Manual Review"
    ROUTE_INVESTIGATION = "Investigation Flag"
    ROUTE_SPECIALIST_QUEUE = "Specialist Queue"
    ROUTE_FAST_TRACK = "Fast-track"
    ROUTE_STANDARD = "Standard Processing"
    
    def __init__(self):
        """Initialize router"""
        pass
    
    def route_claim(self, extracted_fields: ExtractedFields, missing_fields: List[str]) -> RoutingResult:
        """
        Determine routing based on business rules
        
        Priority order:
        1. Missing mandatory fields → Manual Review
        2. Fraud keywords → Investigation Flag
        3. Injury claim → Specialist Queue
        4. Low damage (< $25,000) → Fast-track
        5. Default → Standard Processing
        
        Args:
            extracted_fields: Extracted claim data
            missing_fields: List of missing mandatory fields
            
        Returns:
            RoutingResult: Routing decision with reasoning
        """
        flags = []
        
        # Rule 1: Missing mandatory fields (highest priority)
        if missing_fields:
            reasoning = (
                f"Missing mandatory fields: {', '.join(missing_fields)}. "
                f"Claim requires manual review to complete information."
            )
            return RoutingResult(
                route=self.ROUTE_MANUAL_REVIEW,
                reasoning=reasoning,
                confidence=1.0,
                flags=['missing_fields']
            )
        
        # Rule 2: Fraud detection
        fraud_detected, fraud_keywords = self._check_fraud_indicators(extracted_fields)
        if fraud_detected:
            reasoning = (
                f"Potential fraud indicators detected: {', '.join(fraud_keywords)}. "
                f"Claim flagged for investigation. Incident description contains suspicious language."
            )
            return RoutingResult(
                route=self.ROUTE_INVESTIGATION,
                reasoning=reasoning,
                confidence=0.8,
                flags=['fraud_indicator']
            )
        
        # Rule 3: Injury claims
        if self._is_injury_claim(extracted_fields):
            reasoning = (
                "Claim type identified as 'injury'. "
                "Routing to specialist queue for medical review and assessment."
            )
            return RoutingResult(
                route=self.ROUTE_SPECIALIST_QUEUE,
                reasoning=reasoning,
                confidence=1.0,
                flags=['injury_claim']
            )
        
        # Rule 4: Fast-track for low-value claims
        damage_amount = self._get_estimated_damage(extracted_fields)
        if damage_amount is not None and damage_amount < self.FAST_TRACK_THRESHOLD:
            reasoning = (
                f"Estimated damage (${damage_amount:,.2f}) is below ${self.FAST_TRACK_THRESHOLD:,} threshold. "
                f"All mandatory fields present. No fraud indicators detected. Eligible for fast-track processing."
            )
            return RoutingResult(
                route=self.ROUTE_FAST_TRACK,
                reasoning=reasoning,
                confidence=1.0,
                flags=['low_value']
            )
        
        # Rule 5: Default to standard processing
        if damage_amount is not None:
            reasoning = (
                f"Estimated damage (${damage_amount:,.2f}) exceeds fast-track threshold. "
                f"Routing to standard processing workflow for full assessment."
            )
        else:
            reasoning = (
                "All mandatory fields present. No special conditions detected. "
                "Routing to standard processing workflow."
            )
        
        return RoutingResult(
            route=self.ROUTE_STANDARD,
            reasoning=reasoning,
            confidence=1.0,
            flags=['standard']
        )
    
    def _check_fraud_indicators(self, extracted_fields: ExtractedFields) -> tuple[bool, List[str]]:
        """
        Check for fraud indicators in claim description
        
        Args:
            extracted_fields: Extracted claim data
            
        Returns:
            Tuple of (fraud_detected: bool, keywords_found: List[str])
        """
        if not extracted_fields.incidentInformation or not extracted_fields.incidentInformation.description:
            return False, []
        
        description = extracted_fields.incidentInformation.description.lower()
        found_keywords = []
        
        for keyword in self.FRAUD_KEYWORDS:
            if keyword in description:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    def _is_injury_claim(self, extracted_fields: ExtractedFields) -> bool:
        """
        Check if claim involves injury
        
        Args:
            extracted_fields: Extracted claim data
            
        Returns:
            bool: True if injury claim
        """
        if not extracted_fields.otherMandatoryFields or not extracted_fields.otherMandatoryFields.claimType:
            return False
        
        claim_type = extracted_fields.otherMandatoryFields.claimType.lower()
        return 'injury' in claim_type or 'bodily' in claim_type or 'medical' in claim_type
    
    def _get_estimated_damage(self, extracted_fields: ExtractedFields) -> float:
        """
        Get estimated damage amount
        
        Args:
            extracted_fields: Extracted claim data
            
        Returns:
            float: Damage amount or None
        """
        # Try asset details first
        if extracted_fields.assetDetails and extracted_fields.assetDetails.estimatedDamage is not None:
            return extracted_fields.assetDetails.estimatedDamage
        
        # Try initial estimate
        if extracted_fields.otherMandatoryFields and extracted_fields.otherMandatoryFields.initialEstimate is not None:
            return extracted_fields.otherMandatoryFields.initialEstimate
        
        return None
