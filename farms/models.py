from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid

class Farm(models.Model):
    FARM_TYPE_CHOICES = [
        ('organic', 'Organic'),
        ('conventional', 'Conventional'),
        ('sustainable', 'Sustainable'),
        ('permaculture', 'Permaculture'),
        ('hydroponic', 'Hydroponic'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    area_acres = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    farm_type = models.CharField(max_length=20, choices=FARM_TYPE_CHOICES, default='organic')
    description = models.TextField(blank=True)
    established_date = models.DateField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.owner.get_full_name()}"

    @property
    def total_crops(self):
        return self.crops.count()

    @property
    def active_crops(self):
        return self.crops.filter(status__in=['planted', 'growing']).count()


class Crop(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('planted', 'Planted'),
        ('growing', 'Growing'),
        ('flowering', 'Flowering'),
        ('fruiting', 'Fruiting'),
        ('harvested', 'Harvested'),
        ('failed', 'Failed'),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='crops')
    name = models.CharField(max_length=100)
    variety = models.CharField(max_length=100, blank=True)
    planted_date = models.DateField(null=True, blank=True)
    expected_harvest_date = models.DateField(null=True, blank=True)
    actual_harvest_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    area_planted = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)])
    expected_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} at {self.farm.name}"

    @property
    def days_since_planted(self):
        from django.utils import timezone
        if self.planted_date:
            return (timezone.now().date() - self.planted_date).days
        return 0

    @property
    def yield_efficiency(self):
        if self.expected_yield and self.actual_yield:
            return (self.actual_yield / self.expected_yield) * 100
        return 0


class FarmActivity(models.Model):
    ACTIVITY_TYPES = [
        ('planting', 'Planting'),
        ('watering', 'Watering'),
        ('fertilizing', 'Fertilizing'),
        ('weeding', 'Weeding'),
        ('pest_control', 'Pest Control'),
        ('harvesting', 'Harvesting'),
        ('soil_testing', 'Soil Testing'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='activities')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    date_performed = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_performed']
        verbose_name_plural = 'Farm Activities'

    def __str__(self):
        return f"{self.activity_type} at {self.farm.name}"
