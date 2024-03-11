from django.shortcuts import render, redirect
from django.contrib import messages


def index(request):
    if request.method == "GET":
        zone_list = list()
        return render(request=request,
                      template_name="zones/index.html",
                      context={"zone_list": zone_list, })


def view_zone(request, short_name):
    messages.info(request, "Zone pages not implemented yet.  Come back soon!")
    return redirect("zones:index")
    # return render(request=request,
    #               template_name="zones/view_zone.html",
    #               context={})
