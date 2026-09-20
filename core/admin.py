from django.contrib import admin
from django.db import transaction

admin.site.site_header = "TakaLink Administration"
admin.site.site_title = "TakaLink Admin"
admin.site.index_title = "TakaLink Management"

from .models import (
    AIClassification,
    Business,
    Collection,
    CollectionItem,
    CollectorProfile,
    Notification,
    Payment,
    ResidentProfile,
    Reward,
    User,
    WasteCategory,
    WasteReport,
    WasteRequest,
)


admin.site.register(User)
admin.site.register(ResidentProfile)
admin.site.register(Business)
admin.site.register(CollectorProfile)
admin.site.register(WasteCategory)
admin.site.register(WasteRequest)
admin.site.register(Collection)
admin.site.register(CollectionItem)
@admin.register(WasteReport)
class WasteReportAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            previous_status = None

            if change:
                previous_report = WasteReport.objects.get(pk=obj.pk)
                previous_status = previous_report.status

            super().save_model(request, obj, form, change)

            if (
                obj.status == WasteReport.Status.RESOLVED
                and previous_status != WasteReport.Status.RESOLVED
            ):
                Reward.objects.create(
                    resident=obj.resident,
                    points=15,
                    reason=f"Resolved waste report #{obj.id}",
                )

                obj.resident.resident_profile.points += 15
                obj.resident.resident_profile.save()

                Notification.objects.create(
                    user=obj.resident,
                    title="Waste Report Resolved",
                    message="Your waste report has been reviewed and resolved. You have earned 15 Green Points.",
                )

admin.site.register(Reward)
admin.site.register(Notification)
admin.site.register(Payment)
admin.site.register(AIClassification)