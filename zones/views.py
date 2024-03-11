from django.shortcuts import render, redirect


def index(request):
    if request.method == "GET":
        zone_list = list()
        return render(request=request,
                      template_name="zones/index.html",
                      context={"zone_list": zone_list, })


def view_zone(request, short_name):
    return redirect("zones:index")
    # return render(request=request,
    #               template_name="zones/view_zone.html",
    #               context={})
