from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse_lazy
from django.views import View

from .forms import EquationForm
from .models import TaskSubmission
from django.contrib.auth.decorators import user_passes_test, login_required
from .utils import export_task_submissions_to_csv
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


@login_required
def user_tasks(request):
    user = request.user
    task_assignments = TaskSubmission.objects.filter(user_id=user.id)
    tasks = Task.objects.filter(id__in=task_assignments.values('task_id'))
    context = {'tasks': tasks}
    return render(request, 'zaverecne_zadanie/students/home.html', context)


class LoginView(View):
    template_name = 'zaverecne_zadanie/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('admin:index')
            else:
                return render_student_template(request, 'zaverecne_zadanie/students/home.html')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin:index')
            else:
                return render_student_template(request, 'zaverecne_zadanie/students/home.html')
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

        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_superuser:
            return redirect('admin:index')

        return render(request, self.template_name)

    @login_required
    def user_tasks(request):
        user = request.user
        task_assignments = TaskSubmission.objects.filter(user_id=user.id)
        tasks = Task.objects.filter(id__in=task_assignments.values('task_id'))
        context = {'tasks': tasks}
        return render(request, 'zaverecne_zadanie/students/home.html', context)


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
