from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class PDF(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='pdfs')
    description = models.TextField()
    pdf_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
