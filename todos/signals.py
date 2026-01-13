from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from .models import Todo , TodoHistory

@receiver(pre_save,sender=Todo)
def capture_old_state(sender,instance,**kwargs):
    """
    Before saving,we grab the current state of the object from the database 
    before .save() runs for Todo model
    """
    if instance.pk:
        try:
            old_instance = Todo.objects.get(pk=instance.pk)
            instance._old_is_completed = old_instance.is_completed
            instance._old_title = old_instance.title
            instance._old_description = old_instance.description
        except Todo.DoesNotExist:
            pass

@receiver(post_save, sender=Todo)
def log_todo_changes(sender, instance, created, **kwargs):
    """
    After saving, we check what changed and create a history record.
    """
    if created:
        TodoHistory.objects.create(
            todo=instance, 
            event_type='CREATED', 
            details=f"Task created: {instance.title}"
        )
    else:
        # Check for completion status change
        if hasattr(instance, '_old_is_completed') and instance.is_completed != instance._old_is_completed:
            event = 'CHECKED' if instance.is_completed else 'UNCHECKED'
            TodoHistory.objects.create(todo=instance, event_type=event)

        # Check for content updates (Title or Description)
        elif hasattr(instance, '_old_title') and (
            instance.title != instance._old_title or 
            instance.description != instance._old_description
        ):
            TodoHistory.objects.create(
                todo=instance, 
                event_type='UPDATED', 
                details="Content updated"
            )