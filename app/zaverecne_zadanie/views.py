from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View

from .forms import EquationForm
from .models import TaskSubmission
from django.contrib.auth.decorators import user_passes_test, login_required
from .utils import export_task_submissions_to_csv, compare_equations
from .models import User, TaskSubmission, Task


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


def previous_assignments_view(request):
    return render(request, 'zaverecne_zadanie/students/previousAssignments.html')


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
        context = {'tasks': self.get_user_tasks(request)}

        return render(request, self.template_name, context=context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        if request.user.is_superuser:
            return redirect('admin:index')
        context = {'tasks': self.get_user_tasks(request)}
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


class TestView(View):
    template_name = 'zaverecne_zadanie/test.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        if request.user.is_superuser:
            return redirect('admin:index')

        return render(request, self.template_name)


class ExportTaskSubmissionsView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        task_submissions = TaskSubmission.objects.all()

        return export_task_submissions_to_csv(task_submissions)


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
