from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views import View
from django.utils import timezone
from .forms import EquationForm
from .models import TaskSubmission, Batch
from django.contrib.auth.decorators import user_passes_test, login_required
from .utils import export_task_submissions_to_csv
from .models import User, TaskSubmission, Task, Batch
from django.db.models import Q
import random


@user_passes_test(lambda u: u.is_superuser)
def render_super_user_template(request, template):
    return render(request, template)


def render_student_template(request, template):
    return render(request, template)


def submit_math_view(request):
    if request.method == 'POST':
        math_content = request.POST.get('math_content')
        return HttpResponse('Math content submitted successfully.')
    else:
        return HttpResponse('Invalid request method.')


def equation_editor(request):
    if request.method == 'POST':
        form = EquationForm(request.POST)
        if form.is_valid():
            equation = form.cleaned_data['equation']
            # Process the equation as needed
    else:
        form = EquationForm()
    return render(request, 'home.html', {'form': form})


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
        if request.user.is_superuser:
            return redirect('admin:index')
        tasks = self.get_user_tasks(request)
        batches = self.get_batches(tasks)
        context = {'tasks': tasks, 'batches': batches}
        return render(request, self.template_name, context=context)

    def post(self, request):
        if request.user.is_superuser:
            return redirect('admin:index')
        tasks = self.get_user_tasks(request)
        batches = self.get_batches(tasks)
        context = {'tasks': tasks, 'batches': batches}
        return render(request, self.template_name, context=context)

    def get_user_tasks(self, request):
        user = request.user
        task_assignments = TaskSubmission.objects.filter(user_id=user.id)
        return Task.objects.filter(id__in=task_assignments.values('task_id'))

    def get_batches(self, tasks):
        current_date = timezone.now()
        batches = Batch.objects.filter(
            Q(allowed_from__isnull=True) | Q(allowed_from__lte=current_date),
            Q(allowed_to__isnull=True) | Q(allowed_to__gte=current_date)
        )
        filtered_batches = []
        for batch in batches:
            task_count = Task.objects.filter(batch=batch).count()
            if len([task for task in tasks if task.batch == batch]) < task_count:
                filtered_batches.append(batch)
        return filtered_batches


class TestView(View):
    template_name = 'zaverecne_zadanie/test.html'

    def get(self, request):
        if request.user.is_superuser:
            return redirect('admin:index')

        return render(request, self.template_name)


class ExportTaskSubmissionsView(View):
    def get(self, request):
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
