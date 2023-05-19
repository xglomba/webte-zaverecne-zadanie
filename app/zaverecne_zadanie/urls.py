from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('test/', views.TestView.as_view(), name='test'),
    path('', views.LoginView.as_view()),
    path('export-task-submissions/', views.ExportTaskSubmissionsView.as_view(), name='export_task_submissions'),
    path('compare_solution/', views.CompareEquationsView.as_view(), name='compare_solutions'),
    path('manual/', views.ManualView.as_view(), name='manual')
    path('generate-task/', views.GenerateTaskView.as_view(), name='generate-task')
]
