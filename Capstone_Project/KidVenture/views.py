from django.shortcuts import render, redirect

from django.http import HttpResponse, HttpResponseForbidden

from .forms import SignUpForm, LoginForm, CreateClassForm

from django.contrib.auth import authenticate, login, logout


from django.contrib.auth.decorators import login_required

from .models import Class, Student

import random

import string


@login_required
def home(request):
    return render(request, "KidVenture/home.html")


# Create your views here.

# Handles the user registration
def register(request):

    # Used for feedback 
    msg = None

    # If method is POST
    if request.method == "POST":

        # Creates a signUpform instance using the inserted data
        form = SignUpForm(request.POST)
        
        # Makes sure the information entered is valid. IF so, create the user else say the form is not valid
        if form.is_valid():
            user = form.save()
            msg = "user created"
            return redirect("login_view") # Note: change this to home at some point

        else: msg = "form is not valid"

    # If not POST, just render the standard signupform
    else: form = SignUpForm()

    # renders the page passing in form and msg to the page for use
    return render(request, "KidVenture/register.html", {"form": form, "msg": msg})




# Handles the user login
def login_view(request):

    # Creats a instance of the login form. If POST then fill with the entered data else leave it empty(None)
    form = LoginForm(request.POST or None)

    # Used for feedback 
    msg = None

    # If method is POST
    if request.method == "POST":
        
        # Checks to makes sure the data enterd is valid
        if form.is_valid():
            # Gets the username entered
            username = form.cleaned_data.get("username")
            # Gets the password entered
            password = form.cleaned_data.get("password")
            # Authenticates the user if credential our valid returns user object else return none
            user = authenticate(username = username, password = password)

            # If user is not None, login and go to home page
            if user is not None:
                login(request, user)
                return redirect("home")

            # Else tell the user the their credentials are invalid
            else: 
                msg = "invalid credentials"
            
        # Tells the user that their input in not valid for this form
        else: msg = "error validating form"

    # Render the html page and passes in the form and msg vars to it
    return render(request, "KidVenture/login.html", {"form": form, "msg": msg})

@login_required
def home(request):
    if request.user.is_teacher:
        return render(request, "KidVenture/teacher_page.html")
    elif request.user.is_student:
        return render(request, "KidVenture/student_page.html")


# def student(request):
#     return render(request, "KidVenture/student_page.html")
    
# def teacher(request):
#     return render(request, "KidVenture/teacher_page.html")

def logout_view(request):
    logout(request)
    return login_view(request)




# Funtion to create a token for a teacher's class
def createToken():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))


@login_required 
def create_class(request):

    if not request.user.is_teacher:
        return httpResponseForbidden("You are not authorized to create a class")

    if request.method == 'POST':
        form = CreateClassForm(request.POST)
        if form.is_valid():
            my_class = form.save(commit=False)
            my_class.teacher = request.user
            my_class.access_token = createToken()
            my_class.save()
            return redirect('home')
    else:
        form = CreateClassForm()
    return render(request, 'KidVenture/create_class.html', {'form': form})
    
