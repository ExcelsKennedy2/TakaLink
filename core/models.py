from django.contrib.auth.models import AbstractUser
from django.db import models
# Incase something is missing here, there was a shorter version

class User(AbstractUser):
    class Role(models.TextChoices):
        RESIDENT = "RESIDENT", "Resident"
        COLLECTOR = "COLLECTOR", "Collector"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESIDENT,
    )


class ResidentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="resident_profile",
    )
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    points = models.PositiveIntegerField(default=0)
    successful_collection_streak = models.PositiveIntegerField(default=0)

    @property
    def green_level(self):
        if self.points >= 2500:
            return "Planet Protector"
        elif self.points >= 1000:
            return "Eco Guardian"
        elif self.points >= 500:
            return "Green Champion"
        elif self.points >= 100:
            return "Recycling Hero"
        else:
            return "Eco Starter"

    @property
    def next_green_level(self):
        if self.points < 100:
            return "Recycling Hero"
        elif self.points < 500:
            return "Green Champion"
        elif self.points < 1000:
            return "Eco Guardian"
        elif self.points < 2500:
            return "Planet Protector"
        else:
            return "Max Level"

    @property
    def points_to_next_level(self):
        if self.points < 100:
            return 100 - self.points
        elif self.points < 500:
            return 500 - self.points
        elif self.points < 1000:
            return 1000 - self.points
        elif self.points < 2500:
            return 2500 - self.points
        else:
            return 0

    @property
    def green_progress(self):
        if self.points >= 2500:
            return 100
        elif self.points >= 1000:
            return ((self.points - 1000) / 1500) * 100
        elif self.points >= 500:
            return ((self.points - 500) / 500) * 100
        elif self.points >= 100:
            return ((self.points - 100) / 400) * 100
        else:
            return (self.points / 100) * 100

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Business(models.Model):
    name = models.CharField(max_length=200)
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
    )
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CollectorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="collector_profile",
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collectors",
    )
    phone_number = models.CharField(max_length=20)
    verification_status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class WasteCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_recyclable = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class WasteRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        COLLECTED = "COLLECTED", "Collected"
        CANCELLED = "CANCELLED", "Cancelled"

    resident = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="waste_requests",
    )
    category = models.ForeignKey(
        WasteCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="waste_requests",
    )
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="waste_requests/",
        blank=True,
        null=True,
    )
    location = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    requested_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id} - {self.resident.username}"


class Collection(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    waste_request = models.OneToOneField(
        WasteRequest,
        on_delete=models.CASCADE,
        related_name="collection",
    )
    collector = models.ForeignKey(
        CollectorProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="collections",
    )
    scheduled_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Collection #{self.id}"


class CollectionItem(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="items",
    )
    category = models.ForeignKey(
        WasteCategory,
        on_delete=models.PROTECT,
        related_name="collection_items",
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    unit = models.CharField(max_length=20, default="kg")
    is_correctly_sorted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category.name} - {self.quantity} {self.unit}"


class WasteReport(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        REVIEWING = "REVIEWING", "Under Review"
        RESOLVED = "RESOLVED", "Resolved"
        REJECTED = "REJECTED", "Rejected"

    resident = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="waste_reports",
    )
    description = models.TextField()
    location = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="waste_reports/",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report #{self.id}"


class Reward(models.Model):
    resident = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="rewards",
    )
    points = models.PositiveIntegerField(default=0)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resident.username} - {self.points} points"


class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    resident = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    reference = models.CharField(
        max_length=100,
        unique=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - {self.amount}"


class AIClassification(models.Model):
    waste_request = models.OneToOneField(
        WasteRequest,
        on_delete=models.CASCADE,
        related_name="ai_classification",
    )
    predicted_category = models.ForeignKey(
        WasteCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ai_classifications",
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI classification for request #{self.waste_request.id}"