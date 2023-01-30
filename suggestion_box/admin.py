from django.contrib import admin
from django.utils import timezone

from .models import Suggestion


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ["title", "creator", "status", "processed"]
    list_filter = ["status", "archived"]
    date_hierarchy = "created"
    readonly_fields = ["created"]

    def save_model(self, request, obj: Suggestion, form, change):
        if obj.status != "pending" and not obj.processed_by:
            obj.processed_by = request.user
            obj.processed = timezone.now()
        super().save_model(request, obj, form, change)
