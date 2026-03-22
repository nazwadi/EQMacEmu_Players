from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .utils import is_staff_member


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not is_staff_member(request.user):
            messages.error(request, "You don't have permission to access that page.")
            return redirect('accounts:list_accounts')
        return view_func(request, *args, **kwargs)
    return wrapper
