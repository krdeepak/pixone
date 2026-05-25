from django.contrib import admin
from .models import ProcessingRequest, ProcessingResult


class ProcessingResultInline(admin.StackedInline):
    model = ProcessingResult
    readonly_fields = ("output_url", "metadata", "created_at")
    extra = 0


@admin.register(ProcessingRequest)
class ProcessingRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "feature", "status", "created_at")
    list_filter = ("feature", "status")
    readonly_fields = ("input_params", "input_file_url", "created_at")
    inlines = [ProcessingResultInline]


@admin.register(ProcessingResult)
class ProcessingResultAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "output_url", "created_at")
    readonly_fields = ("output_url", "metadata", "created_at")