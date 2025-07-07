from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable
from collections import defaultdict

from ..core.config import settings
from ..core.cache import cache

logger = logging.getLogger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting API requests.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.requests_per_minute = settings.RATE_LIMIT_REQUESTS
        self.window_size = settings.RATE_LIMIT_WINDOW
        self.memory_store = defaultdict(list)  # Fallback if Redis is not available
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/", "/favicon.ico"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not await self._is_request_allowed(client_id):
            logger.warning(f"Rate limit exceeded for client {client_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(self.window_size)}
            )
        
        # Record request
        await self._record_request(client_id)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_size)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from token
        authorization = request.headers.get("authorization")
        if authorization:
            try:
                from ..core.security import security_service
                token = authorization.replace("Bearer ", "")
                payload = security_service.verify_token(token)
                return f"user:{payload.get('sub', 'unknown')}"
            except Exception:
                pass
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def _is_request_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limit."""
        try:
            # Try Redis first
            current_time = int(time.time())
            window_start = current_time - self.window_size
            
            # Use Redis if available
            if cache.health_check():
                key = f"rate_limit:{client_id}"
                
                # Remove old entries
                cache.client.zremrangebyscore(key, 0, window_start)
                
                # Count current requests
                current_requests = cache.client.zcard(key)
                
                return current_requests < self.requests_per_minute
            else:
                # Fall back to memory store
                return self._is_request_allowed_memory(client_id)
        
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Allow request if rate limiting fails
            return True
    
    def _is_request_allowed_memory(self, client_id: str) -> bool:
        """Memory-based rate limiting fallback."""
        current_time = time.time()
        window_start = current_time - self.window_size
        
        # Clean old entries
        self.memory_store[client_id] = [
            timestamp for timestamp in self.memory_store[client_id]
            if timestamp > window_start
        ]
        
        return len(self.memory_store[client_id]) < self.requests_per_minute
    
    async def _record_request(self, client_id: str):
        """Record a request for rate limiting."""
        try:
            current_time = int(time.time())
            
            # Use Redis if available
            if cache.health_check():
                key = f"rate_limit:{client_id}"
                cache.client.zadd(key, {str(current_time): current_time})
                cache.client.expire(key, self.window_size)
            else:
                # Fall back to memory store
                self.memory_store[client_id].append(current_time)
        
        except Exception as e:
            logger.error(f"Error recording request: {e}")
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        try:
            if cache.health_check():
                key = f"rate_limit:{client_id}"
                current_requests = cache.client.zcard(key)
                return max(0, self.requests_per_minute - current_requests)
            else:
                current_requests = len(self.memory_store[client_id])
                return max(0, self.requests_per_minute - current_requests)
        
        except Exception as e:
            logger.error(f"Error getting remaining requests: {e}")
            return self.requests_per_minute


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    Middleware for IP whitelisting.
    """
    
    def __init__(self, app, whitelist: list = None):
        super().__init__(app)
        self.whitelist = whitelist or []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.whitelist:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        
        if client_ip not in self.whitelist:
            logger.warning(f"Access denied for IP: {client_ip}")
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        return await call_next(request)


class MaintenanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for maintenance mode.
    """
    
    def __init__(self, app, maintenance_mode: bool = False, allowed_paths: list = None):
        super().__init__(app)
        self.maintenance_mode = maintenance_mode
        self.allowed_paths = allowed_paths or ["/health", "/"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if self.maintenance_mode and request.url.path not in self.allowed_paths:
            logger.info(f"Maintenance mode: blocking request to {request.url.path}")
            raise HTTPException(
                status_code=503,
                detail="System is under maintenance. Please try again later.",
                headers={"Retry-After": "3600"}
            )
        
        return await call_next(request)


class APIVersionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API versioning.
    """
    
    def __init__(self, app, supported_versions: list = None, default_version: str = "v1"):
        super().__init__(app)
        self.supported_versions = supported_versions or ["v1"]
        self.default_version = default_version
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract version from URL or headers
        version = self._extract_version(request)
        
        if version and version not in self.supported_versions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported API version: {version}. Supported versions: {', '.join(self.supported_versions)}"
            )
        
        # Set default version if not specified
        if not version:
            version = self.default_version
        
        # Add version to request state
        request.state.api_version = version
        
        response = await call_next(request)
        
        # Add version to response headers
        response.headers["X-API-Version"] = version
        
        return response
    
    def _extract_version(self, request: Request) -> str:
        """Extract API version from request."""
        # Try URL path first
        path_parts = request.url.path.split("/")
        if len(path_parts) >= 3 and path_parts[2].startswith("v"):
            return path_parts[2]
        
        # Try headers
        return request.headers.get("X-API-Version", "")


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """
    Middleware for limiting request size.
    """
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            raise HTTPException(
                status_code=413,
                detail=f"Request too large. Maximum size: {self.max_size} bytes"
            )
        
        return await call_next(request)


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Middleware for setting cache control headers.
    """
    
    def __init__(self, app, default_max_age: int = 300):  # 5 minutes default
        super().__init__(app)
        self.default_max_age = default_max_age
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Set cache headers for GET requests
        if request.method == "GET" and response.status_code == 200:
            # Different cache policies for different endpoints
            if "/static/" in request.url.path:
                response.headers["Cache-Control"] = "public, max-age=86400"  # 24 hours
            elif "/api/" in request.url.path:
                response.headers["Cache-Control"] = f"public, max-age={self.default_max_age}"
            else:
                response.headers["Cache-Control"] = "no-cache"
        
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware for redirecting HTTP to HTTPS.
    """
    
    def __init__(self, app, redirect_https: bool = True):
        super().__init__(app)
        self.redirect_https = redirect_https
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if self.redirect_https and request.url.scheme == "http":
            # Skip redirect for health checks
            if request.url.path in ["/health", "/"]:
                return await call_next(request)
            
            # Redirect to HTTPS
            from starlette.responses import RedirectResponse
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=301)
        
        return await call_next(request)


# Simple rate limiter decorator for endpoints
class SimpleLimiter:
    """Simple rate limiter decorator"""
    
    def __init__(self):
        self.rate_limiter = RateLimitingMiddleware(None)
    
    def limit(self, rate: str):
        """Decorator for rate limiting endpoints"""
        def decorator(func):
            # For now, just return the function as-is
            # In a full implementation, this would apply rate limiting
            func._rate_limit = rate
            return func
        return decorator

# Export a default limiter instance
limiter = SimpleLimiter()

# Alias for compatibility
rate_limit = limiter.limit
