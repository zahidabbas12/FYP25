from django.core.cache import cache
from django.conf import settings
from functools import wraps
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

def cache_view(timeout=None):
    """
    Cache decorator for views
    Usage: @cache_view(timeout=300)  # Cache for 5 minutes
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Don't cache for authenticated users
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # Generate cache key
            cache_key = f"view_cache_{request.path}_{request.GET.urlencode()}"
            
            # Try to get from cache
            response = cache.get(cache_key)
            if response is None:
                # If not in cache, get the response
                response = view_func(request, *args, **kwargs)
                # Store in cache
                cache.set(cache_key, response, timeout or settings.CACHE_TTL)
            
            return response
        return _wrapped_view
    return decorator

def cache_method(timeout=None):
    """
    Cache decorator for methods
    Usage: @cache_method(timeout=300)  # Cache for 5 minutes
    """
    def decorator(func):
        @wraps(func)
        def _wrapped_method(self, *args, **kwargs):
            # Generate cache key
            cache_key = f"method_cache_{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is None:
                # If not in cache, get the result
                result = func(self, *args, **kwargs)
                # Store in cache
                cache.set(cache_key, result, timeout or settings.CACHE_TTL)
            
            return result
        return _wrapped_method
    return decorator 