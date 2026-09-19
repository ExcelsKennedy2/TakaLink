from django.contrib import admin

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
admin.site.register(WasteReport)
admin.site.register(Reward)
admin.site.register(Notification)
admin.site.register(Payment)
admin.site.register(AIClassification)