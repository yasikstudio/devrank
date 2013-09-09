from django.db import models

class CustomUserManager(models.Manager):
    def create_user(self, username, email):
        return self.model._default_manager.create(username=username)

class DevUser(models.Model):
    username = models.CharField(max_length=30)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    def is_authenticated(self):
        return True

    def __unicode__(self):
        return self.username

