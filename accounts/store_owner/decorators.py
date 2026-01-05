from django.shortcuts import redirect
from django.contrib import messages

def store_owner_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("store_owner_login")
        if not request.user.is_store_owner:
            messages.error(request, "Access denied")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper