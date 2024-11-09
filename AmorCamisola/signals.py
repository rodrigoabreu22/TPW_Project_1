from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    # Create "Moderators" group with specific permissions
    moderator_group, created = Group.objects.get_or_create(name="Moderators")
    # Create "Users" group with specific permissions
    user_group, created = Group.objects.get_or_create(name="Users")
