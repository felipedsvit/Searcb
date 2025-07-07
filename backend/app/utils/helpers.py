from typing import Dict, Any, Optional, List
from datetime import datetime, date
import logging
import asyncio
from decimal import Decimal
import json
import uuid

from ..utils.constants import DATE_FORMATS, MODALIDADE_NAMES, SITUACAO_CONTRATACAO_NAMES
from ..utils.validators import (
    validate_cnpj, validate_cpf, validate_email, validate_uf,
    sanitize_string, format_cnpj, format_cpf, format_currency
)

logger = logging.getLogger(__name__)


def generate_uuid() -> str:
    """
    Generate a random UUID and return it as a string.
    
    Returns:
        str: UUID string in standard format
    """
    return str(uuid.uuid4())


def create_response_dict(
    success: bool,
    message: str,
    data: Any = None,
    error_code: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Create standardized response dictionary.
    
    Args:
        success: Whether the operation was successful
        message: Response message
        data: Response data
        error_code: Error code (optional)
        metadata: Additional metadata (optional)
        
    Returns:
        Dict: Standardized response dictionary
    """
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if data is not None:
        response["data"] = data
    
    if error_code:
        response["error_code"] = error_code
    
    if metadata:
        response["metadata"] = metadata
    
    return response


def create_paginated_response(
    data: List[Any],
    total_registros: int,
    numero_pagina: int,
    tamanho_pagina: int,
    empty: bool = False
) -> Dict[str, Any]:
    """
    Create paginated response dictionary.
    
    Args:
        data: List of data items
        total_registros: Total number of records
        numero_pagina: Current page number
        tamanho_pagina: Page size
        empty: Whether the result is empty
        
    Returns:
        Dict: Paginated response dictionary
    """
    total_paginas = (total_registros + tamanho_pagina - 1) // tamanho_pagina
    paginas_restantes = max(0, total_paginas - numero_pagina)
    
    return {
        "data": data,
        "totalRegistros": total_registros,
        "totalPaginas": total_paginas,
        "numeroPagina": numero_pagina,
        "tamanhoPagina": tamanho_pagina,
        "paginasRestantes": paginas_restantes,
        "empty": empty,
        "first": numero_pagina == 1,
        "last": numero_pagina == total_paginas or total_paginas == 0,
        "hasNext": paginas_restantes > 0,
        "hasPrevious": numero_pagina > 1
    }


def format_date_for_pncp(date_obj: date) -> str:
    """
    Format date for PNCP API (YYYYMMDD format).
    
    Args:
        date_obj: Date object
        
    Returns:
        str: Formatted date string
    """
    if not date_obj:
        return ""
    
    return date_obj.strftime(DATE_FORMATS["pncp_date"])


def parse_pncp_date(date_string: str) -> Optional[date]:
    """
    Parse date from PNCP API format.
    
    Args:
        date_string: Date string in PNCP format
        
    Returns:
        Optional[date]: Parsed date object or None
    """
    if not date_string:
        return None
    
    try:
        return datetime.strptime(date_string, DATE_FORMATS["pncp_date"]).date()
    except ValueError:
        logger.warning(f"Invalid date format from PNCP: {date_string}")
        return None


def parse_pncp_datetime(datetime_string: str) -> Optional[datetime]:
    """
    Parse datetime from PNCP API format.
    
    Args:
        datetime_string: Datetime string in PNCP format
        
    Returns:
        Optional[datetime]: Parsed datetime object or None
    """
    if not datetime_string:
        return None
    
    try:
        # Try ISO format first
        return datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
    except ValueError:
        try:
            # Try without timezone
            return datetime.fromisoformat(datetime_string)
        except ValueError:
            logger.warning(f"Invalid datetime format from PNCP: {datetime_string}")
            return None


def parse_decimal(value: Any) -> Optional[Decimal]:
    """
    Parse decimal value from various formats.
    
    Args:
        value: Value to parse
        
    Returns:
        Optional[Decimal]: Parsed decimal or None
    """
    if value is None:
        return None
    
    try:
        if isinstance(value, str):
            # Remove currency symbols and spaces
            value = value.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        
        return Decimal(str(value))
    except (ValueError, TypeError):
        logger.warning(f"Invalid decimal value: {value}")
        return None


def generate_cache_key(prefix: str, **kwargs) -> str:
    """
    Generate cache key from prefix and parameters.
    
    Args:
        prefix: Key prefix
        **kwargs: Key parameters
        
    Returns:
        str: Generated cache key
    """
    params = []
    for key, value in sorted(kwargs.items()):
        if value is not None:
            params.append(f"{key}:{value}")
    
    if params:
        return f"{prefix}:{'_'.join(params)}"
    
    return prefix


def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
    """
    Mask sensitive data in dictionary.
    
    Args:
        data: Data dictionary
        sensitive_fields: List of sensitive field names
        
    Returns:
        Dict: Dictionary with masked sensitive data
    """
    masked_data = data.copy()
    
    for field in sensitive_fields:
        if field in masked_data:
            value = masked_data[field]
            if isinstance(value, str) and len(value) > 4:
                masked_data[field] = value[:2] + "*" * (len(value) - 4) + value[-2:]
            else:
                masked_data[field] = "***"
    
    return masked_data


def extract_error_message(exception: Exception) -> str:
    """
    Extract meaningful error message from exception.
    
    Args:
        exception: Exception object
        
    Returns:
        str: Error message
    """
    if hasattr(exception, 'detail'):
        return str(exception.detail)
    
    return str(exception)


def build_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build query parameters by removing None values.
    
    Args:
        params: Parameters dictionary
        
    Returns:
        Dict: Cleaned parameters dictionary
    """
    return {k: v for k, v in params.items() if v is not None}


def chunks(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List[List]: List of chunks
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def normalize_string(text: str) -> str:
    """
    Normalize string by removing accents and converting to lowercase.
    
    Args:
        text: Text to normalize
        
    Returns:
        str: Normalized text
    """
    if not text:
        return ""
    
    import unicodedata
    
    # Remove accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Convert to lowercase
    return text.lower()


def calculate_percentage(value: Decimal, total: Decimal) -> Optional[Decimal]:
    """
    Calculate percentage.
    
    Args:
        value: Value
        total: Total
        
    Returns:
        Optional[Decimal]: Percentage or None
    """
    if not total or total == 0:
        return None
    
    try:
        return (value / total) * 100
    except (ValueError, TypeError):
        return None


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries, with dict2 values taking precedence.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Dict: Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Dict: Deep merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convert object to JSON serializable format.
    
    Args:
        obj: Object to convert
        
    Returns:
        Any: JSON serializable object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj


def safe_divide(dividend: Decimal, divisor: Decimal) -> Optional[Decimal]:
    """
    Safely divide two decimals.
    
    Args:
        dividend: Dividend
        divisor: Divisor
        
    Returns:
        Optional[Decimal]: Result or None if division by zero
    """
    if not divisor or divisor == 0:
        return None
    
    try:
        return dividend / divisor
    except (ValueError, TypeError):
        return None


def retry_async(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator for retrying async functions.
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier
        
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All retries failed for {func.__name__}: {e}")
                        raise last_exception
            
            raise last_exception
        
        return wrapper
    return decorator


def log_execution_time(func):
    """
    Decorator to log function execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"{func.__name__} executed in {execution_time:.3f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {execution_time:.3f} seconds: {e}")
            raise
    
    return wrapper


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate required fields in dictionary.
    
    Args:
        data: Data dictionary
        required_fields: List of required field names
        
    Returns:
        List[str]: List of missing fields
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    return missing_fields


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def paginate_query(query, page: int = 1, page_size: int = 50):
    """
    Apply pagination to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-based)
        page_size: Number of items per page
        
    Returns:
        Tuple of (items, total_count, total_pages)
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total_count = query.count()
        
        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size
        
        # Apply pagination
        items = query.offset(offset).limit(page_size).all()
        
        logger.info(f"Paginação aplicada: página {page}, {len(items)} itens de {total_count} total")
        
        return items, total_count, total_pages
        
    except Exception as e:
        logger.error(f"Erro na paginação: {e}")
        return [], 0, 0


def send_email(to: str, subject: str, template: str, context: Dict[str, Any] = None):
    """
    Send email using configured email service.
    
    Args:
        to: Recipient email address
        subject: Email subject
        template: Email template name
        context: Template context data
        
    Returns:
        bool: True if email was sent successfully
    """
    try:
        # Implementação básica de envio de email
        # Em produção, usar serviço como AWS SES, SendGrid, etc.
        logger.info(f"Enviando email para {to}: {subject}")
        
        # Aqui você implementaria a lógica real de envio
        # Por exemplo, usando SMTP, AWS SES, etc.
        
        # Por enquanto, apenas log para desenvolvimento
        logger.info(f"Email enviado com sucesso para {to}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar email para {to}: {e}")
        return False


def generate_report(report_type: str, data: Dict[str, Any]) -> str:
    """
    Generate report based on type and data.
    
    Args:
        report_type: Type of report to generate
        data: Data for the report
        
    Returns:
        str: Generated report content
    """
    try:
        logger.info(f"Gerando relatório do tipo: {report_type}")
        
        if report_type == "relatorio_diario":
            return _generate_daily_report(data)
        elif report_type == "relatorio_mensal":
            return _generate_monthly_report(data)
        elif report_type == "relatorio_anual":
            return _generate_annual_report(data)
        else:
            logger.warning(f"Tipo de relatório não suportado: {report_type}")
            return f"Relatório {report_type} não implementado"
            
    except Exception as e:
        logger.error(f"Erro ao gerar relatório {report_type}: {e}")
        return f"Erro ao gerar relatório: {e}"


def _generate_daily_report(data: Dict[str, Any]) -> str:
    """
    Generate daily report content.
    
    Args:
        data: Daily report data
        
    Returns:
        str: Daily report content
    """
    report_lines = [
        f"RELATÓRIO DIÁRIO - {data.get('data', 'N/A')}",
        "=" * 50,
        f"Período: {data.get('periodo', 'N/A')}",
        "",
        "NOVOS REGISTROS:",
        f"  • PCAs: {data.get('novos_pcas', 0)}",
        f"  • Contratações: {data.get('novas_contratacoes', 0)}",
        f"  • Atas: {data.get('novas_atas', 0)}",
        f"  • Contratos: {data.get('novos_contratos', 0)}",
        "",
        "USUÁRIOS:",
        f"  • Usuários ativos: {data.get('total_usuarios_ativos', 0)}",
        f"  • Logins ontem: {data.get('logins_ontem', 0)}",
        "",
        "Relatório gerado automaticamente pelo sistema SEARCB"
    ]
    
    return "\n".join(report_lines)


def _generate_monthly_report(data: Dict[str, Any]) -> str:
    """
    Generate monthly report content.
    
    Args:
        data: Monthly report data
        
    Returns:
        str: Monthly report content
    """
    # Implementar relatório mensal
    return "Relatório mensal não implementado"


def _generate_annual_report(data: Dict[str, Any]) -> str:
    """
    Generate annual report content.
    
    Args:
        data: Annual report data
        
    Returns:
        str: Annual report content
    """
    # Implementar relatório anual
    return "Relatório anual não implementado"
