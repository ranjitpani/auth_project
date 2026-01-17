from django.shortcuts import redirect
from django.contrib import messages

def delivery_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_delivery_boy:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Delivery access only")
        return redirect("delivery-login")
    return wrapper