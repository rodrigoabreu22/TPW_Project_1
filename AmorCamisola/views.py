from django.shortcuts import render, redirect
from datetime import datetime
from .models import *
from django.http import HttpResponse
from .forms import *

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .models import *
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.

def home(request):
    tparams = {
        'title': 'Home Page',
        'year': datetime.now().year,
    }
    return render(request, 'index.html', tparams)



def createAccount(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        print(form.errors)

        if form.is_valid():
            user = User.objects.filter(username=form.cleaned_data['username'])

            if user:
                return render(request, 'createAccount.html', {'form': form, 'error': True})
            else:
                form.save()
                firstname = form.cleaned_data['firstname']
                lastname = form.cleaned_data['lastname']
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')

                user = authenticate(username=username, password=password)
                auth_login(request, user)

                user = User.objects.create(firstname=firstname, lastname=lastname, username=username, email=email, password=password)
                user.save()

                return redirect('/')
        else:
            return render(request, 'createAccount.html', {'form': form, 'error': True})
    else:
        form = CreateAccountForm()
        return render(request, 'createAccount.html', {'form': form, 'error': False})