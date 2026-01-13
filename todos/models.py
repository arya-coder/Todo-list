from django.db import models

# Create your models here.

class Todo(models.Model):
    title = models.CharField(max_length=200,null=False,blank=False)
    description = models.TextField(blank=True,null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class TodoHistory(models.Model):
    EVENT_TYPES=[
        ('CREATED','Created'),
        ('UPDATED','Updated'),
        ('CHECKED','Checked'),
        ('UNCHECKED','Unchecked'),
        ('DELETED','Deleted')
    ]

    todo = models.ForeignKey(Todo,on_delete=models.CASCADE,related_name='history')
    event_type = models.CharField(max_length=20,choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True,null=True)

    class Meta:
        ordering =['-timestamp']

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.todo.title}" 

