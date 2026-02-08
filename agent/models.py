"""
Data models for insurance claims processing
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EffectiveDates(BaseModel):
    """Policy effective dates"""
    start: Optional[str] = None
    end: Optional[str] = None


class PolicyInformation(BaseModel):
    """Policy-related information"""
    policyNumber: Optional[str] = None
    policyholderName: Optional[str] = None
    effectiveDates: Optional[EffectiveDates] = None


class IncidentInformation(BaseModel):
    """Incident details"""
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class ContactDetails(BaseModel):
    """Contact information"""
    phone: Optional[str] = None
    email: Optional[str] = None


class InvolvedParties(BaseModel):
    """Parties involved in the incident"""
    claimant: Optional[str] = None
    thirdParties: Optional[List[str]] = None
    contactDetails: Optional[ContactDetails] = None


class AssetDetails(BaseModel):
    """Details about the damaged asset"""
    assetType: Optional[str] = None
    assetId: Optional[str] = None
    estimatedDamage: Optional[float] = None


class OtherMandatoryFields(BaseModel):
    """Other required fields"""
    claimType: Optional[str] = None
    attachments: Optional[List[str]] = None
    initialEstimate: Optional[float] = None


class ExtractedFields(BaseModel):
    """All extracted fields from FNOL"""
    policyInformation: Optional[PolicyInformation] = None
    incidentInformation: Optional[IncidentInformation] = None
    involvedParties: Optional[InvolvedParties] = None
    assetDetails: Optional[AssetDetails] = None
    otherMandatoryFields: Optional[OtherMandatoryFields] = None


class ClaimData(BaseModel):
    """Complete claim data structure"""
    extractedFields: ExtractedFields
    missingFields: List[str] = Field(default_factory=list)
    recommendedRoute: str = ""
    reasoning: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "extractedFields": {},
                "missingFields": [],
                "recommendedRoute": "Fast-track",
                "reasoning": "All fields present, low damage amount"
            }
        }


class RoutingResult(BaseModel):
    """Result of routing decision"""
    route: str
    reasoning: str
    confidence: float = 1.0
    flags: List[str] = Field(default_factory=list)
