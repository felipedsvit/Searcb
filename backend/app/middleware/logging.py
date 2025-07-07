from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import json
from typing import Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()
        
        # Log request
        if self.log_requests:
            await self._log_request(request)
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        if self.log_responses:
            await self._log_response(request, response, process_time)
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    async def _log_request(self, request: Request):
        """Log incoming request."""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} - {user_agent}"
        )
        
        # Log query parameters
        if request.query_params:
            logger.debug(f"Query params: {dict(request.query_params)}")
    
    async def _log_response(self, request: Request, response: Response, process_time: float):
        """Log response."""
        client_ip = request.client.host if request.client else "unknown"
        
        log_level = logging.INFO
        if response.status_code >= 400:
            log_level = logging.ERROR
        elif response.status_code >= 300:
            log_level = logging.WARNING
        
        logger.log(
            log_level,
            f"Response: {request.method} {request.url.path} "
            f"- {response.status_code} - {process_time:.3f}s - {client_ip}"
        )
        
        # Log slow requests
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.3f}s"
            )


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """
    Advanced middleware for detailed request/response logging.
    """
    
    def __init__(self, app, log_body: bool = False, max_body_size: int = 1024):
        super().__init__(app)
        self.log_body = log_body
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Prepare request info
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client": {
                "host": request.client.host if request.client else None,
                "port": request.client.port if request.client else None
            }
        }
        
        # Log request body if enabled
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    request_info["body"] = body.decode("utf-8")
                else:
                    request_info["body"] = f"<body too large: {len(body)} bytes>"
            except Exception as e:
                request_info["body"] = f"<error reading body: {e}>"
        
        # Log request
        logger.info(f"Request: {json.dumps(request_info, indent=2)}")
        
        # Start timer
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Prepare response info
        response_info = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "process_time": process_time
        }
        
        # Log response
        log_level = logging.INFO
        if response.status_code >= 400:
            log_level = logging.ERROR
        elif response.status_code >= 300:
            log_level = logging.WARNING
        
        logger.log(log_level, f"Response: {json.dumps(response_info, indent=2)}")
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers.
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding correlation IDs to requests.
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import uuid
        
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        # Add to request state
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for response compression.
    """
    
    def __init__(self, app, minimum_size: int = 1024):
        super().__init__(app)
        self.minimum_size = minimum_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if client accepts compression
        accept_encoding = request.headers.get("accept-encoding", "")
        
        response = await call_next(request)
        
        # Only compress if client accepts it and response is large enough
        if "gzip" in accept_encoding.lower() and self._should_compress(response):
            import gzip
            
            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Compress body
            if len(body) >= self.minimum_size:
                compressed_body = gzip.compress(body)
                
                # Update response
                response.headers["content-encoding"] = "gzip"
                response.headers["content-length"] = str(len(compressed_body))
                
                # Create new response with compressed body
                from starlette.responses import Response as StarletteResponse
                return StarletteResponse(
                    content=compressed_body,
                    status_code=response.status_code,
                    headers=response.headers,
                    media_type=response.media_type
                )
        
        return response
    
    def _should_compress(self, response: Response) -> bool:
        """Check if response should be compressed."""
        content_type = response.headers.get("content-type", "")
        
        # Don't compress if already compressed
        if "content-encoding" in response.headers:
            return False
        
        # Only compress text-based content
        compressible_types = [
            "text/",
            "application/json",
            "application/javascript",
            "application/xml",
            "application/rss+xml",
            "application/atom+xml"
        ]
        
        return any(content_type.startswith(ct) for ct in compressible_types)
