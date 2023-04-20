from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from django.contrib.auth.decorators import user_passes_test


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
                return render_super_user_template(request, 'zaverecne_zadanie/teacher/home.html')
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
                return render_super_user_template(request, 'zaverecne_zadanie/teacher/home.html')
            else:
                return render_student_template(request, 'zaverecne_zadanie/students/home.html')
        else:
            messages.error(request, 'Username or password is not correct!')
            return render(request, self.template_name, {'username': username})


class CustomLogoutView(LogoutView):
    template_name = 'zaverecne_zadanie/login.html'
    next_page = reverse_lazy('login')


class HomeView(View):
    template_name = 'zaverecne_zadanie/home.html'

    def get(self, request):
        return render(request, self.template_name)
