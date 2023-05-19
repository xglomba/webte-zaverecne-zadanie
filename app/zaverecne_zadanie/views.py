from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from .forms import EquationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from .utils import export_task_submissions_to_csv, compare_equations
from .models import User, TaskSubmission, Task, Batch
from django.db.models import Q
import random


@user_passes_test(lambda u: u.is_superuser)
def render_super_user_template(request, template):
    return render(request, template)


def render_student_template(request, template):
    return render(request, template)


class LoginView(View):
    template_name = 'zaverecne_zadanie/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('admin:index')
            else:
                return redirect(reverse('home'))
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('admin:index') if user.is_superuser else redirect(reverse('home'))
        else:
            messages.error(request, 'Username or password is not correct!')
            return render(request, self.template_name, {'username': username})


class CustomLogoutView(LogoutView):
    template_name = 'zaverecne_zadanie/login.html'
    next_page = reverse_lazy('login')


class HomeView(View):
    template_name = 'zaverecne_zadanie/students/home.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        if request.user.is_superuser:
            return redirect('admin:index')
        tasks = self.get_user_tasks(request)
        batches = self.get_batches(tasks)
        context = {'tasks': tasks, 'batches': batches}
        return render(request, self.template_name, context=context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        if request.user.is_superuser:
            return redirect('admin:index')
        tasks = self.get_user_tasks(request)
        batches = self.get_batches(tasks)
        context = {'tasks': tasks, 'batches': batches}
        return render(request, self.template_name, context=context)

    def get_user_tasks(self, request):
        user = request.user
        task_assignments = TaskSubmission.objects.filter(user_id=user.id)
        task_ids = task_assignments.values_list('task_id', flat=True)
        tasks = Task.objects.filter(id__in=task_ids)

        user_tasks = []
        for task in tasks:
            task_submission = task_assignments.get(task_id=task.id)
            user_tasks.append({'task': task, 'task_submission': task_submission})

        return user_tasks

    def get_batches(self, tasks):
        current_date = timezone.now()
        batches = Batch.objects.filter(
            Q(allowed_from__isnull=True) | Q(allowed_from__lte=current_date),
            Q(allowed_to__isnull=True) | Q(allowed_to__gte=current_date)
        )
        filtered_batches = []
        for batch in batches:
            task_count = Task.objects.filter(batch=batch).count()
            if len([task for task in tasks if task.get('task').batch == batch]) < task_count:
                filtered_batches.append(batch)
        return filtered_batches


class ExportTaskSubmissionsView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        task_submissions = TaskSubmission.objects.all()

        return export_task_submissions_to_csv(task_submissions)


class GenerateTaskView(View):
    def post(self, request):
        batch_name = request.POST.get("batch-name")
        tasks = Task.objects.filter(batch__name=batch_name)
        print(tasks)
        random_task = random.choice(tasks)
        print(random_task)

        while TaskSubmission.objects.filter(user=request.user, task=random_task).exists():
            random_task = random.choice(tasks)

        task_submission = TaskSubmission(task=random_task, user=request.user)
        task_submission.save()
        return redirect(reverse('home'))


class CompareEquationsView(View):

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        task_id = request.POST.get("task_id")
        students_solution = request.POST.get("students_solution")

        task = Task.objects.get(id=task_id)  # Retrieve a task with a specific ID (replace 1 with the desired ID)
        task_solution = task.solution

        task_submission = TaskSubmission.objects.get(task_id=task_id, user_id=request.user.id)
        points = task.batch.points if task.batch.points is not None else None

        if compare_equations(task_solution, students_solution):
            task_submission.points = points
            messages.success(request, f'Your solution is correct, you gained {points} points.')
        else:
            task_submission.points = 0
            messages.warning(request, 'Your solution is incorrect, you gained 0 points.')

        task_submission.save()
        return redirect(reverse('home'))


class ManualView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        return render(request, 'zaverecne_zadanie/manual.html')
