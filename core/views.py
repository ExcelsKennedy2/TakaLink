from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ResidentSignUpForm, CollectorSignUpForm


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
def collector_dashboard(request):
    if request.user.role != request.user.Role.COLLECTOR:
        return redirect("dashboard")

    return render(
        request,
        "core/collector_dashboard.html",
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")