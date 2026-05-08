from django.contrib import admin
from .models import Ticket, Artifact, AgentRun

# Register your models here.
admin.site.register(Ticket)
admin.site.register(Artifact)
admin.site.register(AgentRun)
