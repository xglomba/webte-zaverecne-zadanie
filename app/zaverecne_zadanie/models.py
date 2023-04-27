from django.contrib.auth.models import AbstractUser
from django.db import models

from zaverecne_zadanie.utils import parse_latex


class User(AbstractUser):
    ais_id = models.IntegerField(unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.ais_id})'


class Batch(models.Model):
    name = models.CharField(max_length=255, primary_key=True, unique=True)
    file = models.FileField(upload_to='.')
    points = models.IntegerField(blank=True, null=True)
    allowed_from = models.DateTimeField(blank=True, null=True)
    allowed_to = models.DateTimeField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
        parse_latex(self.file.path, self.name)

    def __str__(self):
        return f'{self.name} ({self.allowed_from} - {self.allowed_to}) [{self.points} p.]'


class Task(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    task = models.CharField(max_length=32767)
    solution = models.CharField(max_length=32767)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    def __str__(self):
        return f'Task {self.id} ({self.batch})'


class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()

    class Meta:
        unique_together = ('task', 'user',)
