from django.shortcuts import redirect

def bus_partner_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_bus_partner:
            return view_func(request, *args, **kwargs)
        return redirect("bus_login")
    return wrapper
