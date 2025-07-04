from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles):
    """
    Decorator to restrict access based on user roles.
    Usage: @role_required(['doctor']) or @role_required(['patient', 'doctor'])
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied("You don't have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def doctor_required(view_func):
    """
    Decorator to restrict access to doctors only.
    """
    return role_required(['doctor'])(view_func)

def patient_required(view_func):
    """
    Decorator to restrict access to patients only.
    """
    return role_required(['patient'])(view_func)