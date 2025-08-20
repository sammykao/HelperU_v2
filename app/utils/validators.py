from typing import Optional



# It's important to not use regex for simple validation like this.
# Regex is slow and unnecessary for this use case!!!

def validate_phone_number(phone: str) -> tuple[bool, Optional[str]]:
    """
    Validate US phone number format without using regex.
    Accepts various input formats and validates as US phone number.
    """
    if not phone or not isinstance(phone, str):
        return False, "Phone number must be a non-empty string"
    
    # Remove all non-digit characters for validation
    digits_only = ''.join(char for char in phone if char.isdigit())
    
    # US phone number validation
    # Must be either 10 digits (local) or 11 digits starting with 1 (with country code)
    if len(digits_only) == 10:
        # 10 digits - local US number
        return True, None
    elif len(digits_only) == 11 and digits_only.startswith('1'):
        # 11 digits starting with 1 - US number with country code
        return True, None
    elif len(digits_only) == 0:
        return False, "Phone number must contain at least some digits"
    elif len(digits_only) < 10:
        return False, f"Phone number too short: {len(digits_only)} digits (need 10-11 for US)"
    elif len(digits_only) > 11:
        return False, f"Phone number too long: {len(digits_only)} digits (max 11 for US)"
    else:
        return False, "Invalid US phone number format. Must be 10 digits or 11 digits starting with 1"

def format_phone_number(phone: str) -> str:
    """
    Format phone number for display without using regex.
    Attempts to format as (XXX) XXX-XXXX for US numbers.
    """
    digits_only = ''.join(char for char in phone if char.isdigit())
    
    # If it's exactly 10 digits, format as US number
    if len(digits_only) == 10:
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    
    # If it's 11 digits and starts with 1, format as US number with country code
    if len(digits_only) == 11 and digits_only.startswith('1'):
        return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
    
    # For other numbers, return with + prefix
    return f"+{digits_only}"

def clean_phone_number(phone: str) -> str:
    """
    Clean phone number to digits only for storage without using regex.
    """
    return ''.join(char for char in phone if char.isdigit())

def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to E.164 format for Vonage API.
    Ensures US country code is properly formatted.
    """
    digits_only = clean_phone_number(phone)
    
    # If it's 10 digits, add US country code
    if len(digits_only) == 10:
        return f"1{digits_only}"
    
    # If it's 11 digits starting with 1, return as is
    if len(digits_only) == 11 and digits_only.startswith('1'):
        return digits_only
    
    # For any other case, return as is (this shouldn't happen with proper validation)
    return digits_only
