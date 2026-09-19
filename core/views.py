from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import (
    ResidentSignUpForm,
    CollectorSignUpForm,
    WasteRequestForm,
)

from .models import WasteRequest, Collection

def home(request):
    return render(request, "core/home.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    account_type = request.GET.get("type", "resident").lower()

    if account_type == "collector":
        form_class = CollectorSignUpForm
        title = "Create Collector Account"
    else:
        form_class = ResidentSignUpForm
        title = "Create Resident Account"

    if request.method == "POST":
        form = form_class(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = form_class()

    return render(
        request,
        "core/signup.html",
        {
            "form": form,
            "title": title,
            "account_type": account_type,
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        from django.contrib.auth import authenticate

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(
            request,
            "core/login.html",
            {
                "error": "Invalid username or password.",
            },
        )

    return render(request, "core/login.html")


@login_required
def dashboard(request):
    if request.user.role == request.user.Role.RESIDENT:
        return redirect("resident_dashboard")

    if request.user.role == request.user.Role.COLLECTOR:
        return redirect("collector_dashboard")

    return redirect("home")


@login_required
def resident_dashboard(request):
    if request.user.role != request.user.Role.RESIDENT:
        return redirect("dashboard")

    return render(
        request,
        "core/resident_dashboard.html",
    )

@login_required
def create_collection(request):
    if request.user.role != request.user.Role.RESIDENT:
        return redirect("dashboard")

    if request.method == "POST":
        form = WasteRequestForm(request.POST)

        if form.is_valid():
            waste_request = form.save(commit=False)
            waste_request.resident = request.user
            waste_request.save()

            return redirect("resident_dashboard")
    else:
        form = WasteRequestForm()

    return render(
        request,
        "core/create_collection.html",
        {"form": form},
    )

@login_required
def collection_history(request):
    if request.user.role != request.user.Role.RESIDENT:
        return redirect("dashboard")

    requests = request.user.waste_requests.order_by("-created_at")

    return render(
        request,
        "core/collection_history.html",
        {
            "requests": requests,
        },
    )


@login_required
def collector_dashboard(request):
    if request.user.role != request.user.Role.COLLECTOR:
        return redirect("dashboard")

    return render(
        request,
        "core/collector_dashboard.html",
    )

@login_required
def collector_pending_jobs(request):
    if request.user.role != request.user.Role.COLLECTOR:
        return redirect("dashboard")

    pending_requests = (
        WasteRequest.objects
        .filter(status=WasteRequest.Status.PENDING)
        .order_by("-created_at")
    )

    return render(
        request,
        "core/collector_pending_jobs.html",
        {
            "pending_requests": pending_requests,
        },
    )

@login_required
def accept_collection(request, request_id):
    if request.user.role != request.user.Role.COLLECTOR:
        return redirect("dashboard")

    waste_request = WasteRequest.objects.get(
        id=request_id,
        status=WasteRequest.Status.PENDING,
    )

    collector_profile = request.user.collector_profile

    Collection.objects.create(
        waste_request=waste_request,
        collector=collector_profile,
        scheduled_date=waste_request.requested_date,
    )

    waste_request.status = WasteRequest.Status.ACCEPTED
    waste_request.save()

    return redirect("collector_pending_jobs")

@login_required
def collector_active_jobs(request):
    if request.user.role != request.user.Role.COLLECTOR:
        return redirect("dashboard")

    collections = (
        Collection.objects
        .filter(
            collector=request.user.collector_profile,
            status__in=[
                Collection.Status.SCHEDULED,
                Collection.Status.IN_PROGRESS,
            ],
        )
        .select_related("waste_request", "waste_request__category")
        .order_by("-scheduled_date")
    )

    return render(
        request,
        "core/collector_active_jobs.html",
        {
            "collections": collections,
        },
    )

@login_required
def start_collection(request, collection_id):
    if request.user.role != request.user.Role.COLLECTOR:
        return redirect("dashboard")

    collection = Collection.objects.get(
        id=collection_id,
        collector=request.user.collector_profile,
        status=Collection.Status.SCHEDULED,
    )

    collection.status = Collection.Status.IN_PROGRESS
    collection.save()

    return redirect("collector_active_jobs")

@login_required
def complete_collection(request, collection_id):
    if request.user.role != request.user.Role.COLLECTOR:
        return redirect("dashboard")

    collection = Collection.objects.get(
        id=collection_id,
        collector=request.user.collector_profile,
        status=Collection.Status.IN_PROGRESS,
    )

    collection.status = Collection.Status.COMPLETED
    collection.completed_at = timezone.now()
    collection.save()

    collection.waste_request.status = WasteRequest.Status.COLLECTED
    collection.waste_request.save()

    return redirect("collector_completed_jobs")

@login_required
def collector_completed_jobs(request):
    if request.user.role != request.user.Role.COLLECTOR:
        return redirect("dashboard")

    collections = (
        Collection.objects
        .filter(
            collector=request.user.collector_profile,
            status=Collection.Status.COMPLETED,
        )
        .select_related("waste_request", "waste_request__category")
        .order_by("-completed_at")
    )

    return render(
        request,
        "core/collector_completed_jobs.html",
        {
            "collections": collections,
        },
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")