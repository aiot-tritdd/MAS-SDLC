from django.contrib import admin
from .models import Ticket, Artifact, AgentRun
from core.tasks import sync_ticket_to_paperclip
# Register your models here.
@admin.action(description="Sync selected tickets to Paperclip")
def sync_to_paperclip(modeladmin, request, queryset):
    for ticket in queryset:
        sync_ticket_to_paperclip.delay(str(ticket.id))


class TicketAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "priority"]
    actions = [sync_to_paperclip]


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Artifact)
admin.site.register(AgentRun)
