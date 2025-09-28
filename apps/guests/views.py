from django.shortcuts import render, redirect, get_object_or_404
from apps.guests.forms import GuestForm
from apps.guests.models import Guest
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def create_guest(request):
    if request.method == "POST":
        form = GuestForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # upload + save do model
            return redirect("guests:guest_success", token=form.instance.token)
    else:
        form = GuestForm()
    return render(request, "guests/create_guest.html", {"form": form})

@staff_member_required
def edit_guest(request, token):
    guest = get_object_or_404(Guest, token=token)
    if request.method == "POST":
        form = GuestForm(request.POST, request.FILES, instance=guest)
        if form.is_valid():
            form.save()
            return redirect("guest_detail", token=token)
    else:
        form = GuestForm(instance=guest)
    return render(request, "guests/edit_guest.html", {"form": form, "guest": guest})

@staff_member_required
def delete_guest(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    if request.method == "POST":
        guest.delete()
        return redirect("admin:guests_guest_changelist")
    return render(request, "guests/confirm_delete.html", {"guest": guest})

def guest_success(request, token=None):
    context = {}
    if token:
        guest = get_object_or_404(Guest, token=token)
        context["guest"] = guest
    return render(request, "guests/guest_success.html", context)

def guest_detail(request, token):
    guest = get_object_or_404(Guest, token=token)
    return render(request, "guests/guest_detail.html", {"guest": guest})
