from django.contrib import admin
from .models import QuestCategory, Quest, QuestCompletion, QuestStep, QuestStepCompletion

@admin.register(QuestCategory)
class QuestCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'quests_count', 'created_at')
    search_fields = ('name', 'description')

    def quests_count(self, obj):
        return obj.quests.count()
    quests_count.short_description = 'Quests Count'

class QuestStepInline(admin.TabularInline):
    model = QuestStep
    extra = 1
    fields = ('title', 'order', 'points_value', 'is_required')
    ordering = ('order',)

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'points_reward', 'is_active', 'completion_count', 'created_at')
    list_filter = ('category', 'difficulty', 'is_active', 'status', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('prerequisites',)
    inlines = [QuestStepInline]

    def completion_count(self, obj):
        return obj.completion_count
    completion_count.short_description = 'Completions'

@admin.register(QuestCompletion)
class QuestCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quest', 'is_completed', 'points_earned', 'started_at', 'completed_at')
    list_filter = ('is_completed', 'started_at', 'completed_at', 'quest__category')
    search_fields = ('user__phone', 'user__first_name', 'quest__title')
    readonly_fields = ('started_at',)

@admin.register(QuestStep)
class QuestStepAdmin(admin.ModelAdmin):
    list_display = ('quest', 'title', 'order', 'points_value', 'is_required')
    list_filter = ('is_required', 'quest__category')
    search_fields = ('quest__title', 'title')
