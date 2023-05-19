from django.contrib import admin
from django.urls import path
from . import views
from .views import submit_math_view

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('test/', views.TestView.as_view(), name='test'),
    path('', views.LoginView.as_view()),
    path('export-task-submissions/', views.ExportTaskSubmissionsView.as_view(), name='export_task_submissions'),
    path('submit_math/', submit_math_view, name='submit_math'),
    path('previousAssignments/', views.previous_assignments_view, name='previousAssignments'),
]
