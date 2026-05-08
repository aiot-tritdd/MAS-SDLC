from django.db import models
import uuid
# Create your models here.


class Ticket(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        RESEARCH_IN_PROGRESS = "research_in_progress", "Research in Progress"
        NEEDS_APPROVAL = "needs_approval", "Needs Approval"
        APPROVED = "approved", "Approved"
        BUILDING = "building", "Building"
        BUILD_COMPLETE = "build_complete", "Build Complete"
        FAILED = "failed", "Failed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=255, choices=Status.choices, default=Status.NEW
    )
    priority = models.CharField(
        max_length=255, choices=Priority.choices, default=Priority.MEDIUM
    )

    paperclip_issue_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Artifact(models.Model):
    class Type(models.TextChoices):
        RESEARCH = "research", "Research"
        ARCHITECTURE = "architecture", "Architecture"
        CODE = "code", "Code"
        TEST_RESULTS = "test_results", "Test Results"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="artifacts"
    )
    artifact_type = models.CharField(max_length=255, choices=Type.choices)
    title = models.CharField(max_length=255)
    content = models.TextField()
    file_path = models.CharField(max_length=500, null=True, blank=True)
    agent_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.artifact_type} - {self.ticket.title} - {self.agent_name}"

    class Meta:
        ordering = ["created_at"]


class AgentRun(models.Model):
    class Status(models.TextChoices):
        TIMEOUT = "timeout", "Timeout"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="agent_runs"
    )
    agent_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=255, choices=Status.choices, default=Status.RUNNING
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    prompt_tokens = models.IntegerField(null=True, blank=True)
    completion_tokens = models.IntegerField(null=True, blank=True)
    estimated_cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    decision_summary = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    artifacts_produced = models.JSONField(default=list)

    def __str__(self):
        return f"{self.agent_name} - {self.ticket.title}"
