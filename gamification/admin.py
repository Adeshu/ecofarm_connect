from django.contrib import admin
from django.utils.html import format_html
from .models import Badge, UserBadge, Achievement, PointsHistory, Leaderboard

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'rarity', 'points_required', 'earned_count', 'is_active', 'created_at')
    list_filter = ('category', 'rarity', 'is_active', 'created_at')
    search_fields = ('name', 'description')

    def earned_count(self, obj):
        return obj.earned_count
    earned_count.short_description = 'Times Earned'

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('earned_at', 'badge__category', 'badge__rarity')
    search_fields = ('user__phone', 'user__first_name', 'badge__name')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'points_earned', 'achieved_at')
    list_filter = ('achieved_at', 'related_object_type')
    search_fields = ('user__phone', 'user__first_name', 'title')

@admin.register(PointsHistory)
class PointsHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'points_change', 'point_type', 'description', 'created_at')
    list_filter = ('point_type', 'created_at')
    search_fields = ('user__phone', 'user__first_name', 'description')

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'leaderboard_type', 'rank', 'score', 'period_start', 'updated_at')
    list_filter = ('leaderboard_type', 'period_start', 'updated_at')
    search_fields = ('user__phone', 'user__first_name')
