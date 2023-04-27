from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import Batch, Task, TaskSubmission, User

admin.site.register(Batch)
admin.site.register(Task)
admin.site.register(TaskSubmission)


class CustomUserCreationForm(UserCreationForm):
    """
    A custom form that uses `create_user` to create new users.
    """
    ais_id = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = ('username', 'ais_id', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.ais_id = self.cleaned_data['ais_id']
        user.set_password(self.cleaned_data['password1'])
        user.username = f'x{self.cleaned_data["last_name"]}'
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'ais_id', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('ais_id', 'first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'ais_id', 'email', 'password1', 'password2'),
        }),
    )
    add_form = CustomUserCreationForm


admin.site.register(User, CustomUserAdmin)
