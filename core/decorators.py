from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """
    Decorator that restricts access to a view to users whose `role`
    attribute is in `roles`. Unauthenticated users are redirected to login.
    Doctors with role=DOCTOR but is_approved=False are redirected to the
    pending approval page (handled separately in doctor_dashboard view).
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, "You do not have permission to access that page.")
                return redirect('dashboard_redirect')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required('ADMIN')(view_func)


def doctor_required(view_func):
    return role_required('DOCTOR')(view_func)


def patient_required(view_func):
    return role_required('PATIENT')(view_func)
