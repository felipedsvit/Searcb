import re
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
# Removed Pydantic import as it's not needed in this module

from .constants import (
    MODALIDADE_NAMES, SITUACAO_CONTRATACAO_NAMES, TIPO_CONTRATO_NAMES,
    ESTADOS_BRASIL, VALIDATION_RULES, DATE_FORMATS
)


def validate_cnpj(cnpj: str) -> bool:
    """
    Validate CNPJ format and check digit.
    
    Args:
        cnpj: CNPJ string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not cnpj:
        return False
    
    # Remove non-numeric characters
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Check length
    if len(cnpj) != VALIDATION_RULES["cnpj_length"]:
        return False
    
    # Check if all digits are the same
    if cnpj == cnpj[0] * len(cnpj):
        return False
    
    # Calculate check digits
    def calc_check_digit(cnpj_partial, weights):
        total = sum(int(digit) * weight for digit, weight in zip(cnpj_partial, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # First check digit
    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    check_1 = calc_check_digit(cnpj[:12], weights_1)
    
    # Second check digit
    weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    check_2 = calc_check_digit(cnpj[:13], weights_2)
    
    return int(cnpj[12]) == check_1 and int(cnpj[13]) == check_2


def validate_cpf(cpf: str) -> bool:
    """
    Validate CPF format and check digit.
    
    Args:
        cpf: CPF string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not cpf:
        return False
    
    # Remove non-numeric characters
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Check length
    if len(cpf) != VALIDATION_RULES["cpf_length"]:
        return False
    
    # Check if all digits are the same
    if cpf == cpf[0] * len(cpf):
        return False
    
    # Calculate check digits
    def calc_check_digit(cpf_partial, weights):
        total = sum(int(digit) * weight for digit, weight in zip(cpf_partial, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # First check digit
    weights_1 = list(range(10, 1, -1))
    check_1 = calc_check_digit(cpf[:9], weights_1)
    
    # Second check digit
    weights_2 = list(range(11, 1, -1))
    check_2 = calc_check_digit(cpf[:10], weights_2)
    
    return int(cpf[9]) == check_1 and int(cpf[10]) == check_2


def validate_ni(ni: str, tipo_pessoa: str) -> bool:
    """
    Validate NI (National Identifier) based on person type.
    
    Args:
        ni: National identifier string
        tipo_pessoa: Person type (PF or PJ)
        
    Returns:
        bool: True if valid, False otherwise
    """
    if tipo_pessoa == "PF":
        return validate_cpf(ni)
    elif tipo_pessoa == "PJ":
        return validate_cnpj(ni)
    else:
        return False


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove non-numeric characters
    phone = re.sub(r'[^0-9]', '', phone)
    
    # Check length (10 or 11 digits for Brazilian phones)
    return len(phone) in [10, 11]


def validate_uf(uf: str) -> bool:
    """
    Validate UF (state) code.
    
    Args:
        uf: UF string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not uf:
        return False
    
    return uf.upper() in ESTADOS_BRASIL.keys()


def validate_modalidade_id(modalidade_id: int) -> bool:
    """
    Validate modalidade ID.
    
    Args:
        modalidade_id: Modalidade ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return modalidade_id in MODALIDADE_NAMES.keys()


def validate_situacao_id(situacao_id: int) -> bool:
    """
    Validate situação ID.
    
    Args:
        situacao_id: Situação ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return situacao_id in SITUACAO_CONTRATACAO_NAMES.keys()


def validate_decimal(value: str, max_digits: int = 15, decimal_places: int = 4) -> bool:
    """
    Validate decimal value format.
    
    Args:
        value: Decimal string to validate
        max_digits: Maximum number of digits
        decimal_places: Maximum decimal places
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        decimal_value = Decimal(str(value))
        
        # Check if it's a valid decimal
        if decimal_value.is_nan() or decimal_value.is_infinite():
            return False
        
        # Check number of digits and decimal places
        sign, digits, exponent = decimal_value.as_tuple()
        total_digits = len(digits)
        
        if total_digits > max_digits:
            return False
        
        if exponent < 0 and abs(exponent) > decimal_places:
            return False
        
        return True
    except (InvalidOperation, ValueError):
        return False


def validate_date_string(date_string: str, format_type: str = "iso_date") -> bool:
    """
    Validate date string format.
    
    Args:
        date_string: Date string to validate
        format_type: Format type from DATE_FORMATS
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not date_string:
        return False
    
    try:
        date_format = DATE_FORMATS.get(format_type, DATE_FORMATS["iso_date"])
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not start_date or not end_date:
        return False
    
    return start_date <= end_date


def validate_pagination_params(page: int, page_size: int, max_page_size: int = 500) -> bool:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number
        page_size: Page size
        max_page_size: Maximum page size allowed
        
    Returns:
        bool: True if valid, False otherwise
    """
    return (
        page > 0 and
        page_size > 0 and
        page_size <= max_page_size
    )


def validate_numero_controle_pncp(numero_controle: str) -> bool:
    """
    Validate PNCP control number format.
    
    Args:
        numero_controle: PNCP control number
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not numero_controle:
        return False
    
    # Basic format validation - alphanumeric with hyphens
    pattern = r'^[A-Za-z0-9\-]+$'
    return re.match(pattern, numero_controle) is not None


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string by removing unwanted characters.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length (optional)
        
    Returns:
        str: Sanitized string
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Truncate if necessary
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def format_cnpj(cnpj: str) -> str:
    """
    Format CNPJ with mask.
    
    Args:
        cnpj: CNPJ string
        
    Returns:
        str: Formatted CNPJ
    """
    if not cnpj:
        return ""
    
    # Remove non-numeric characters
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    
    return cnpj


def format_cpf(cpf: str) -> str:
    """
    Format CPF with mask.
    
    Args:
        cpf: CPF string
        
    Returns:
        str: Formatted CPF
    """
    if not cpf:
        return ""
    
    # Remove non-numeric characters
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    return cpf


def format_currency(value: Decimal) -> str:
    """
    Format decimal value as currency.
    
    Args:
        value: Decimal value
        
    Returns:
        str: Formatted currency string
    """
    if value is None:
        return "R$ 0,00"
    
    # Format with thousands separator and 2 decimal places
    formatted = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


def clean_numeric_string(value: str) -> str:
    """
    Clean numeric string by removing non-digit characters.
    
    Args:
        value: String to clean
        
    Returns:
        str: Cleaned string with only digits
    """
    if not value:
        return ""
    
    return re.sub(r'[^0-9]', '', value)


def is_valid_json(json_string: str) -> bool:
    """
    Check if string is valid JSON.
    
    Args:
        json_string: JSON string to validate
        
    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        import json
        json.loads(json_string)
        return True
    except (ValueError, TypeError):
        return False


# PydanticValidators class removed - validators are now used directly in schemas
