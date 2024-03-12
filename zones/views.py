from django.shortcuts import render, redirect
from django.contrib import messages

from common.models.zones import Zone


def index(request):
    if request.method == "GET":

        zone_data = Zone.objects.all()

        return render(request=request,
                      template_name="zones/index.html",
                      context={"zone_data": zone_data, })


def view_zone(request, short_name):
    messages.info(request, "Zone pages not implemented yet.  Come back soon!")
    return redirect("zones:index")
    # return render(request=request,
    #               template_name="zones/view_zone.html",
    #               context={})
