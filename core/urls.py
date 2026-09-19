from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("signup/", views.signup, name="signup"),

    path("dashboard/", views.dashboard, name="dashboard"),

    # Resident URLs

    path(
        "resident/dashboard/",
        views.resident_dashboard,
        name="resident_dashboard",
    ),
    path(
    "resident/create-collection/",
    views.create_collection,
    name="create_collection",
    ),
    path(
    "resident/collection-history/",
    views.collection_history,
    name="collection_history",
    ),
    path(
        "resident/report-waste/",
        views.create_waste_report,
        name="create_waste_report",
    ),
    path(
        "resident/waste-report-history/",
        views.waste_report_history,
        name="waste_report_history",
    ),
    path(
        "resident/green-points-history/",
        views.green_points_history,
        name="green_points_history",
    ),

    # Collector URLs

    path(
        "collector/dashboard/",
        views.collector_dashboard,
        name="collector_dashboard",
    ),
    path(
        "collector/pending-jobs/",
        views.collector_pending_jobs,
        name="collector_pending_jobs",
    ),
    path(
        "collector/accept/<int:request_id>/",
        views.accept_collection,
        name="accept_collection",
    ),
    path(
        "collector/active-jobs/",
        views.collector_active_jobs,
        name="collector_active_jobs",
    ),
    path(
        "collector/record-waste/<int:collection_id>/",
        views.record_collected_waste,
        name="record_collected_waste",
    ),
    path(
        "collector/start/<int:collection_id>/",
        views.start_collection,
        name="start_collection",
    ),
    path(
        "collector/complete/<int:collection_id>/",
        views.complete_collection,
        name="complete_collection",
    ),
    path(
        "collector/completed-jobs/",
        views.collector_completed_jobs,
        name="collector_completed_jobs",
    ),
]