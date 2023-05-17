import os.path
import shutil
import zipfile

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.db import models
from zaverecne_zadanie.utils import parse_latex
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ais_id = models.IntegerField(unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=False, verbose_name=_('first_name'))
    last_name = models.CharField(max_length=30, blank=False, verbose_name=_('last_name'))

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.ais_id})'


class Batch(models.Model):
    name = models.CharField(max_length=255, primary_key=True, unique=True, verbose_name=_('name'))
    file = models.FileField(upload_to='latex', verbose_name=_('file'))
    images = models.FileField(upload_to='images/zip', blank=True, null=True, verbose_name=_('images'))
    points = models.IntegerField(blank=True, null=True, verbose_name=_('points'))
    allowed_from = models.DateTimeField(blank=True, null=True, verbose_name=_('allowed_from'))
    allowed_to = models.DateTimeField(blank=True, null=True, verbose_name=_('allowed_to'))

    class Meta:
        verbose_name = _('batch')
        verbose_name_plural = _('batchs')

    def clean(self):
        # Check if a batch with the same file name already exists
        existing_batches = Batch.objects.filter(file__icontains=self.file.name)
        if existing_batches.exists():
            # If a batch with the same file name exists, raise a validation error
            raise ValidationError({'file': ['A batch with the same file name already exists.']})
        elif not self.file.path.endswith(".tex"):
            raise ValidationError({'file': ['Unsupported file type. You can upload only ".tex" files.']})
        super().clean()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        tasks = parse_latex(self.file.path)
        tmp_unzipped_folder_path = '../static/images/tmp'
        if self.images:
            images_zip_path = self.images.path
            with zipfile.ZipFile(images_zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_unzipped_folder_path)
        for task in tasks:
            new_task = Task(task=task.get('task', ''), solution=task.get('solution', ''), batch=self)
            if task.get('image') is not None:
                print("Latex image path: " + task.get('image'))
                source_path = os.path.join(tmp_unzipped_folder_path, 'images',
                task.get('image')).replace('\\', '/')
                try:
                    with open(source_path, 'rb') as f:
                        new_task.image.save(task.get('image'), ImageFile(f))
                except FileNotFoundError as e:
                    pass
            new_task.save()
        if os.path.exists(tmp_unzipped_folder_path):
            shutil.rmtree(tmp_unzipped_folder_path)

    def __str__(self):
        return f'{self.name} [{self.points} point/s]'


class Task(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    task = models.CharField(max_length=32767, verbose_name=_('task'))
    solution = models.CharField(max_length=32767, verbose_name=_('solution'))
    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name=_('image'))
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, verbose_name=_('batch'))

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')

    def __str__(self):
        return f'Task {self.id} ({self.batch})'


class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_('task'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(blank=True, null=True, verbose_name=_('points'))

    class Meta:
        verbose_name = _('task_submission')
        verbose_name_plural = _('tasks_submissions')
        unique_together = ('task', 'user',)

    def __str__(self):
        return f'Task {self.task.id} (batch {self.task.batch.name}) - ({self.user.username} - {self.user.ais_id})'