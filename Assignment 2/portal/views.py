from django.urls import reverse
from django.shortcuts import render, redirect
from portal.forms import RegisterForm, LogInForm
from django.contrib import messages

DRF_API_URL = 'http://localhost:8000/api/' # DRF URL


# Create your views here.
def login(request):
    # Set Login
    next = request.GET.get('next')
    form = LogInForm(request.POST or None)

    # Requset Post
    if request.method == 'POST':
        print(form)

    # Render Context to HTML
    context = {
        'form' : form
    }
    return render(request, 'portal/login.html', context)

def register(request):
    # Set Register
    next = request.GET.get('next')
    form = RegisterForm(request.POST or None)

    # Request Post
    if request.method == 'POST':
        print(form)

    # Render Context to HTML
    context = {
        'form' : form
    }
    return render(request, 'portal/register.html', context)

def logout(request):
    return render(request, 'portal/login.html')

def home(request):
    return render(request, 'portal/index.html')
