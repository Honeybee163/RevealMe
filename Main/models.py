import uuid
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    message = models.TextField(max_length=1000)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.message



class Riddle(models.Model):
    riddle_id=models.ForeignKey(Message, on_delete=models.CASCADE,related_name='riddles')
    riddle=models.TextField(max_length=1000)
    answer=models.CharField(max_length=100)
    hint=models.TextField(max_length=1000,null=True)
    
    def __str__(self):
        return self.riddle
    
    
