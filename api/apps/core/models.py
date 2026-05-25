from django.db import models


class ProcessingRequest(models.Model):
    class Feature(models.TextChoices):
        REFRAME = "reframe", "Reframe"
        FACE_DETECTION = "face_detection", "Face Detection"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    feature = models.CharField(max_length=50, choices=Feature)
    status = models.CharField(max_length=20, choices=Status, default=Status.PENDING)
    input_params = models.JSONField(default=dict)
    input_file_url = models.URLField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.feature} | {self.status} | {self.created_at:%Y-%m-%d %H:%M}"


class ProcessingResult(models.Model):
    request = models.OneToOneField(
        ProcessingRequest, on_delete=models.CASCADE, related_name="result"
    )
    output_url = models.URLField(max_length=1000, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for request {self.request_id}"