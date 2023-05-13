from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('', views.LoginView.as_view()),
    path('export-task-submissions/', views.ExportTaskSubmissionsView.as_view(), name='export_task_submissions'),
]
