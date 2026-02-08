"""
Field extraction from FNOL documents
"""

import re
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dateutil import parser as date_parser

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

from .models import (
    ExtractedFields, PolicyInformation, IncidentInformation,
    InvolvedParties, AssetDetails, OtherMandatoryFields,
    EffectiveDates, ContactDetails
)


class FNOLExtractor:
    """Extract structured data from FNOL documents"""
    
    # Mandatory fields for validation
    MANDATORY_FIELDS = [
        'policyNumber',
        'policyholderName',
        'incidentDate',
        'incidentLocation',
        'incidentDescription',
        'claimant',
        'claimType',
        'estimatedDamage'
    ]
    
    def __init__(self):
        """Initialize extractor"""
        self.text_content = ""
        self.extracted_data = {}
        
    def load_document(self, file_path: str) -> str:
        """
        Load document from file (PDF or TXT)
        
        Args:
            file_path: Path to the FNOL document
            
        Returns:
            str: Extracted text content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        if not PDF_SUPPORT:
            raise ImportError("PyPDF2 not installed. Install with: pip install pypdf2")
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def extract_fields(self, text: str) -> ExtractedFields:
        """
        Extract all fields from document text
        
        Args:
            text: Document text content
            
        Returns:
            ExtractedFields: Structured extracted data
        """
        self.text_content = text
        
        # Extract each section
        policy_info = self._extract_policy_information()
        incident_info = self._extract_incident_information()
        parties = self._extract_involved_parties()
        asset_details = self._extract_asset_details()
        other_fields = self._extract_other_mandatory_fields()
        
        return ExtractedFields(
            policyInformation=policy_info,
            incidentInformation=incident_info,
            involvedParties=parties,
            assetDetails=asset_details,
            otherMandatoryFields=other_fields
        )
    
    def _extract_policy_information(self) -> PolicyInformation:
        """Extract policy-related information"""
        # Policy Number (various formats)
        policy_number = self._extract_pattern(
            r'Policy\s*(?:Number|#|No\.?)[\s:]*([A-Z0-9\-]+)',
            flags=re.IGNORECASE
        )
        
        # Policyholder Name - improved pattern to stop at newline
        policyholder = self._extract_pattern(
            r'Policyholder(?:\s+Name)?[\s:]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+?)(?:\n|$)',
            flags=re.IGNORECASE
        )
        
        # Effective Dates
        effective_dates = self._extract_effective_dates()
        
        return PolicyInformation(
            policyNumber=policy_number,
            policyholderName=policyholder,
            effectiveDates=effective_dates
        )
    
    def _extract_effective_dates(self) -> Optional[EffectiveDates]:
        """Extract policy effective dates"""
        # Look for date ranges
        date_range_pattern = r'Effective\s+Date[s]?[\s:]*(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})'
        match = re.search(date_range_pattern, self.text_content, re.IGNORECASE)
        
        if match:
            return EffectiveDates(start=match.group(1), end=match.group(2))
        
        # Try alternate formats
        start_date = self._extract_pattern(r'Start\s+Date[\s:]*(\d{4}-\d{2}-\d{2})', flags=re.IGNORECASE)
        end_date = self._extract_pattern(r'End\s+Date[\s:]*(\d{4}-\d{2}-\d{2})', flags=re.IGNORECASE)
        
        if start_date or end_date:
            return EffectiveDates(start=start_date, end=end_date)
        
        return None
    
    def _extract_incident_information(self) -> IncidentInformation:
        """Extract incident details"""
        # Incident Date
        incident_date = self._extract_pattern(
            r'(?:Incident|Accident)\s+Date[\s:]*(\d{4}-\d{2}-\d{2})',
            flags=re.IGNORECASE
        )
        
        # Incident Time
        incident_time = self._extract_pattern(
            r'(?:Incident|Accident)\s+Time[\s:]*(\d{1,2}:\d{2}(?:\s*[AP]M)?)',
            flags=re.IGNORECASE
        )
        
        # Location
        location = self._extract_pattern(
            r'Location[\s:]*([^\n]+)',
            flags=re.IGNORECASE
        )
        
        # Description (multi-line)
        description = self._extract_description()
        
        return IncidentInformation(
            date=incident_date,
            time=incident_time,
            location=location,
            description=description
        )
    
    def _extract_description(self) -> Optional[str]:
        """Extract incident description (may be multi-line)"""
        pattern = r'(?:Incident\s+)?Description[\s:]*\n?([^\n]+(?:\n(?![A-Z][a-z]+\s*:)[^\n]+)*)'
        match = re.search(pattern, self.text_content, re.IGNORECASE)
        
        if match:
            desc = match.group(1).strip()
            # Clean up extra whitespace
            desc = re.sub(r'\s+', ' ', desc)
            return desc
        
        return None
    
    def _extract_involved_parties(self) -> InvolvedParties:
        """Extract information about involved parties"""
        # Claimant - improved pattern to stop at newline
        claimant = self._extract_pattern(
            r'Claimant(?:\s+Name)?[\s:]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+?)(?:\n|$)',
            flags=re.IGNORECASE
        )
        
        # Third parties
        third_parties = self._extract_third_parties()
        
        # Contact details
        phone = self._extract_pattern(
            r'(?:Phone|Tel|Contact)[\s:]*(\+?[\d\s\-\(\)]{7,})',
            flags=re.IGNORECASE
        )
        
        email = self._extract_pattern(
            r'Email[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            flags=re.IGNORECASE
        )
        
        contact_details = ContactDetails(phone=phone, email=email) if (phone or email) else None
        
        return InvolvedParties(
            claimant=claimant,
            thirdParties=third_parties,
            contactDetails=contact_details
        )
    
    def _extract_third_parties(self) -> Optional[List[str]]:
        """Extract third party names"""
        pattern = r'Third\s+Part(?:y|ies)[\s:]*([A-Z][^\n]+)'
        match = re.search(pattern, self.text_content, re.IGNORECASE)
        
        if match:
            parties_text = match.group(1).strip()
            # Remove common non-name terms
            parties_text = re.sub(r'\s*(?:None|N/?A)\s*$', '', parties_text, flags=re.IGNORECASE)
            if not parties_text or parties_text.lower() in ['none', 'n/a']:
                return None
            # Split by common separators
            parties = re.split(r'[,;]|\s+and\s+', parties_text)
            return [p.strip() for p in parties if p.strip() and p.strip().lower() not in ['none', 'n/a']]
        
        return None
    
    def _extract_asset_details(self) -> AssetDetails:
        """Extract asset information"""
        # Asset Type
        asset_type = self._extract_pattern(
            r'Asset\s+Type[\s:]*([A-Za-z]+)',
            flags=re.IGNORECASE
        )
        
        # Asset ID (VIN, serial number, etc.)
        asset_id = self._extract_pattern(
            r'(?:Asset\s+ID|VIN|Serial\s+Number)[\s:]*([A-Z0-9]+)',
            flags=re.IGNORECASE
        )
        
        # Estimated Damage
        estimated_damage = self._extract_currency_amount('Estimated\s+Damage')
        
        return AssetDetails(
            assetType=asset_type,
            assetId=asset_id,
            estimatedDamage=estimated_damage
        )
    
    def _extract_other_mandatory_fields(self) -> OtherMandatoryFields:
        """Extract other mandatory fields"""
        # Claim Type
        claim_type = self._extract_pattern(
            r'Claim\s+Type[\s:]*([A-Za-z]+)',
            flags=re.IGNORECASE
        )
        
        # Attachments
        attachments = self._extract_attachments()
        
        # Initial Estimate
        initial_estimate = self._extract_currency_amount('Initial\s+Estimate')
        
        return OtherMandatoryFields(
            claimType=claim_type,
            attachments=attachments,
            initialEstimate=initial_estimate
        )
    
    def _extract_attachments(self) -> Optional[List[str]]:
        """Extract list of attachments"""
        pattern = r'Attachments[\s:]*([^\n]+)'
        match = re.search(pattern, self.text_content, re.IGNORECASE)
        
        if match:
            attachments_text = match.group(1).strip()
            # Split by common separators
            attachments = re.split(r'[,;]', attachments_text)
            return [a.strip() for a in attachments if a.strip()]
        
        return None
    
    def _extract_pattern(self, pattern: str, flags: int = 0) -> Optional[str]:
        """
        Extract first match of a pattern
        
        Args:
            pattern: Regex pattern
            flags: Regex flags
            
        Returns:
            Matched string or None
        """
        match = re.search(pattern, self.text_content, flags)
        return match.group(1).strip() if match else None
    
    def _extract_currency_amount(self, field_name: str) -> Optional[float]:
        """
        Extract currency amount
        
        Args:
            field_name: Name of the field to search for
            
        Returns:
            float: Amount or None
        """
        pattern = rf'{field_name}[\s:]*\$?\s*([\d,]+(?:\.\d{{2}})?)'
        match = re.search(pattern, self.text_content, re.IGNORECASE)
        
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                return None
        
        return None
    
    def identify_missing_fields(self, extracted_fields: ExtractedFields) -> List[str]:
        """
        Identify missing mandatory fields
        
        Args:
            extracted_fields: Extracted data
            
        Returns:
            List of missing field names
        """
        missing = []
        
        # Check policy information
        if not extracted_fields.policyInformation or not extracted_fields.policyInformation.policyNumber:
            missing.append('policyNumber')
        if not extracted_fields.policyInformation or not extracted_fields.policyInformation.policyholderName:
            missing.append('policyholderName')
        
        # Check incident information
        if not extracted_fields.incidentInformation or not extracted_fields.incidentInformation.date:
            missing.append('incidentDate')
        if not extracted_fields.incidentInformation or not extracted_fields.incidentInformation.location:
            missing.append('incidentLocation')
        if not extracted_fields.incidentInformation or not extracted_fields.incidentInformation.description:
            missing.append('incidentDescription')
        
        # Check involved parties
        if not extracted_fields.involvedParties or not extracted_fields.involvedParties.claimant:
            missing.append('claimant')
        
        # Check other mandatory fields
        if not extracted_fields.otherMandatoryFields or not extracted_fields.otherMandatoryFields.claimType:
            missing.append('claimType')
        if not extracted_fields.assetDetails or extracted_fields.assetDetails.estimatedDamage is None:
            missing.append('estimatedDamage')
        
        return missing
