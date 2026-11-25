# corrected admin code inserted here
from django.contrib import admin
from .models import Farm, Crop, FarmActivity

class CropInline(admin.TabularInline):
    model = Crop
    extra = 1
    fields = ('name', 'variety', 'status', 'area_planted', 'planted_date', 'expected_harvest_date')

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'area_acres', 'farm_type', 'total_crops', 'created_at')
    list_filter = ('farm_type', 'created_at', 'owner__state')  # Only if User model has 'state'
    search_fields = ('name', 'location', 'owner__phone', 'owner__first_name')  # Only if User model has these fields
    inlines = [CropInline]

    def total_crops(self, obj):
        return obj.total_crops
    total_crops.short_description = 'Total Crops'

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'variety', 'farm', 'status', 'area_planted', 'planted_date', 'expected_harvest_date')
    list_filter = ('status', 'planted_date', 'farm__farm_type')
    search_fields = ('name', 'variety', 'farm__name')

@admin.register(FarmActivity)
class FarmActivityAdmin(admin.ModelAdmin):
    list_display = ('farm', 'activity_type', 'date_performed', 'cost', 'crop')
    list_filter = ('activity_type', 'date_performed', 'farm__farm_type')
    search_fields = ('farm__name', 'description')
