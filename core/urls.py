from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("signup/", views.signup, name="signup"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "resident/dashboard/",
        views.resident_dashboard,
        name="resident_dashboard",
    ),
    path(
        "collector/dashboard/",
        views.collector_dashboard,
        name="collector_dashboard",
    ),
]