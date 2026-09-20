from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import (
    ResidentSignUpForm,
    CollectorSignUpForm,
    WasteRequestForm,
    WasteReportForm,
    CollectionItemForm,
)

from .models import WasteRequest, Collection, WasteReport, Reward, CollectionItem, Notification, AIClassification
from .ai_service import classify_waste

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

# Resident Views

@login_required
def resident_dashboard(request):
    if request.user.role != request.user.Role.RESIDENT:
        return redirect("dashboard")

    resident_profile = request.user.resident_profile

    unread_notifications_count = request.user.notifications.filter(
        is_read=False
    ).count()

    return render(
        request,
        "core/resident_dashboard.html",
        {
            "resident_profile": resident_profile,
            "unread_notifications_count": unread_notifications_count,
        },
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

            predicted_category, confidence = classify_waste(
                waste_request.description
            )

            AIClassification.objects.create(
                waste_request=waste_request,
                predicted_category=predicted_category,
                confidence=confidence,
            )

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

    requests = (
        request.user.waste_requests
        .select_related("category", "ai_classification__predicted_category")
        .order_by("-created_at")
    )

    for waste_request in requests:
        if hasattr(waste_request, "ai_classification"):
            waste_request.ai_confidence_percentage = (
                waste_request.ai_classification.confidence * 100
            )

    return render(
        request,
        "core/collection_history.html",
        {
            "requests": requests,
        },
    )

@login_required
def create_waste_report(request):
    if request.user.role != request.user.Role.RESIDENT:
        return redirect("dashboard")

    if request.method == "POST":
        form = WasteReportForm(request.POST, request.FILES)

        if form.is_valid():
            waste_report = form.save(commit=False)
            waste_report.resident = request.user
            waste_report.save()

            return redirect("resident_dashboard")
    else:
        form = WasteReportForm()

    return render(
        request,
        "core/create_waste_report.html",
        {
            "form": form,
        },
    )

@login_required
def waste_report_history(request):
    if request.user.role != request.user.Role.RESIDENT:
        return redirect("dashboard")

    reports = WasteReport.objects.filter(
        resident=request.user
    ).order_by("-created_at")

    return render(
        request,
        "core/waste_report_history.html",
        {
            "reports": reports,
        },
    )

@login_required
def green_points_history(request):
    if request.user.role != request.user.Role.RESIDENT:
        return redirect("dashboard")

    rewards = Reward.objects.filter(
        resident=request.user
    ).order_by("-created_at")

    return render(
        request,
        "core/green_points_history.html",
        {
            "rewards": rewards,
        },
    )

@login_required
def notifications(request):
    user_notifications = request.user.notifications.order_by("-created_at")

    request.user.notifications.filter(
        is_read=False
    ).update(is_read=True)

    return render(
        request,
        "core/notifications.html",
        {
            "notifications": user_notifications,
        },
    )

# Collector Views

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

    Notification.objects.create(
        user=waste_request.resident,
        title="Collection Request Accepted",
        message="Your waste collection request has been accepted by a collector.",
    )

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
def record_collected_waste(request, collection_id):
    if request.user.role != request.user.Role.COLLECTOR:
        return redirect("dashboard")

    collection = Collection.objects.get(
        id=collection_id,
        collector=request.user.collector_profile,
        status=Collection.Status.IN_PROGRESS,
    )

    if request.method == "POST":
        form = CollectionItemForm(request.POST)

        if form.is_valid():
            collection_item = form.save(commit=False)
            collection_item.collection = collection
            collection_item.save()

            return redirect("record_collected_waste", collection_id=collection.id)
    else:
        form = CollectionItemForm()

    items = collection.items.order_by("-id")

    return render(
        request,
        "core/record_collected_waste.html",
        {
            "collection": collection,
            "form": form,
            "items": items,
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

    resident = collection.waste_request.resident
    resident_profile = resident.resident_profile
    # Increase successful collection streak
    resident_profile.successful_collection_streak += 1

    # Award points for successful waste collection
    Reward.objects.create(
        resident=resident,
        points=10,
        reason="Successful waste collection",
    )

    resident_profile.points += 10

    # Award bonus points for recyclable waste
    has_recyclable_waste = collection.items.filter(
        category__is_recyclable=True
    ).exists()

    if has_recyclable_waste:
        Reward.objects.create(
            resident=resident,
            points=5,
            reason="Recyclable waste handed over",
        )

        resident_profile.points += 5

    # Award bonus points for correctly sorted waste
    has_correctly_sorted_waste = collection.items.filter(
        is_correctly_sorted=True
    ).exists()

    if has_correctly_sorted_waste:
        Reward.objects.create(
            resident=resident,
            points=5,
            reason="Correctly sorted waste",
        )

        resident_profile.points += 5

    # Check for 5 successful collection milestone
    completed_collection_count = Collection.objects.filter(
        waste_request__resident=resident,
        status=Collection.Status.COMPLETED,
    ).count()

    five_collection_bonus_reason = "5 successful collections bonus"

    if (
        completed_collection_count >= 5
        and not Reward.objects.filter(
            resident=resident,
            reason=five_collection_bonus_reason,
        ).exists()
    ):
        Reward.objects.create(
            resident=resident,
            points=25,
            reason=five_collection_bonus_reason,
        )

        resident_profile.points += 25

    # Check for 10 successful collection milestone
    ten_collection_bonus_reason = "10 successful collections bonus"

    if (
        completed_collection_count >= 10
        and not Reward.objects.filter(
            resident=resident,
            reason=ten_collection_bonus_reason,
        ).exists()
    ):
        Reward.objects.create(
            resident=resident,
            points=50,
            reason=ten_collection_bonus_reason,
        )

        resident_profile.points += 50

    # Check for 4 consecutive successful collections
    if resident_profile.successful_collection_streak >= 4:
        streak_bonus_reason = "4 consecutive successful collections bonus"

        Reward.objects.create(
            resident=resident,
            points=20,
            reason=streak_bonus_reason,
        )

        resident_profile.points += 20
        resident_profile.successful_collection_streak = 0

    resident_profile.save()

    Notification.objects.create(
        user=resident,
        title="Collection Completed",
        message="Your waste has been collected successfully. You have earned Green Points.",
    )

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