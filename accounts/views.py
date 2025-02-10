from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q

from .models import User


def login_view(request):
    msg = ''
    if request.method == "POST":
        username_var = request.POST.get('username')
        password_var = request.POST.get('password')
        user = authenticate(request, username=username_var,
                            password=password_var)

        qs = User.objects.filter(username=username_var)
        if len(qs) < 1:
            messages.error(request, 'This user does not EXIST!')
        try:
            user = User.objects.get(username=username_var)
        except:
            user = None
        if user is not None and not user.check_password(password_var):
            messages.error(request, 'Wrong Password!')
        elif user is None:
            pass
        else:
            login(request, user)
            if request.user.is_authenticated:
                print(request.user)
            else:
                print('Not Authenticated')
            if password_var == 'pass':
                messages.info(
                    request, "You're using the default 'password', please change it before you proceed")
                return redirect('change_password')
            
            elif "next" in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect("home")

    context = {"msg": msg}
    return render(request, 'accounts/login.html', context)



def logout_view(request):
    logout(request)
    return redirect('auth_login')


@login_required
def change_password(request):
    context = {}
    if request.method == "POST":
        new_password = request.POST["new_password"]
        current_password = request.POST["current_password"]
        confirm_password = request.POST["confirm_password"]

        user = User.objects.get(id=request.user.id)
        check = user.check_password(current_password)
        if check == True:
            if new_password != confirm_password:
                context["msg"] = "Password Not Matching "
                context["col"] = "alert-danger"
            else:
                user.set_password(new_password)
                user.save()
                context["msg"] = "Password Change Successfully"
                context["col"] = "alert-success "
                return redirect('auth_logout')
        else:
            context["msg"] = " Current Password is Incorrect "
            context["col"] = "alert-danger"
    return render(request, 'accounts/change_password.html', context)


# @login_required
def search_user(request):
    try:
        query = request.GET.get('q')
    except:
        query = None
    lookups = (Q(file_number__iexact=query) | Q(first_name__icontains=query) |
               Q(last_name__icontains=query) | Q(username__iexact=query))
    if query:
        results = User.objects.filter(lookups).distinct()
        context = {'query': query, "results": results}
        template = 'accounts/search.html'
    else:
        a = "Please enter a search parameter!"
        template = 'accounts/search.html'
        context = {'query1': a}
    return render(request, template, context)


# @login_required
def reset_password(request, id):
    user = User.objects.get(id=id)
    user.set_password("pass")
    user.save()
    messages.success(request, "Password reset successful!")
    return redirect('home')
