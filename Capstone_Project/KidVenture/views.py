from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, HttpResponseForbidden

from .forms import SignUpForm, LoginForm, CreateClassForm

from django.contrib.auth import authenticate, login, logout


from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Class, Student, Activity, Notification

import random

import string

from django.db.models import Count, Prefetch

from django.contrib import messages


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
        total_students = request.user.classes.aggregate(total=Count('students'))['total'] or 0
        return render(request, "KidVenture/teacher_page.html", {'total_students': total_students })
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
        return HttpResponseForbidden("You are not authorized to create a class")

    if request.user.classes.count() >= 5:
        return HttpResponseForbidden("You cannot create more than 5 classes")

    if request.method == 'POST':
        form = CreateClassForm(request.POST)
        if form.is_valid():
            my_class = form.save(commit=False)
            my_class.teacher = request.user
            my_class.access_token = createToken()
            my_class.save()
            return redirect('classes')
    else:
        form = CreateClassForm()
    return render(request, 'KidVenture/create_class.html', {'form': form})

def is_student(user):
    return user.user_type == 'student'
    
@login_required
@user_passes_test(is_student)
def student_homepage(request):
    # Get the current user's student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch activities linked to the student
    completed_activities = Activity.objects.filter(student=student, completed=True)
    pending_activities = Activity.objects.filter(student=student, completed=False)
    
    progress = Progress.objects.filter(student=student)
    achievements = Achievement.objects.filter(student=student)
    # announcements = Announcement.objects.filter(classroom=student.classroom)
    leaderboard = LeaderboardEntry.objects.order_by('-points')[:10]
    notifications = Notification.objects.filter(user=request.user).order_by('-date')

    return render(request, 'KidVenture/student_page.html', {
        # 'activities': activities,
        'completed_activities': completed_activities,
        'pending_activities': pending_activities,
        'progress': progress,
        'achievements': achievements,
        # 'announcements': announcements,
        'leaderboard': leaderboard,
        'notifications': notifications,
    })

    

def classes(request):
    if not request.user.is_teacher:
        return redirect('home')
  
    # Get unique activities per class (ignoring duplicates per student)
    activities = Activity.objects.values("name", "student__classroom__name", "url_name").distinct().order_by("student__classroom__name")

    return render(request, 'KidVenture/classes.html', {"activities": activities})




@login_required
def delete_class(request, class_id):

    my_class = get_object_or_404(Class, id=class_id)

    if request.user != my_class.teacher:
         return httpResponseForbidden("You are not authorized to delete a class")

    my_class.delete()

    return redirect('classes')


"""
# View to allow teacher to add students to their classes
@login_required
def add_student(request, class_id):

    # If user is not a teacher don't allow them to add students
    if not request.user.is_teacher:
        return httpResponseForbidden("You are not authorized to add students")

    # Get class 
    my_class = get_object_or_404(Class, id=class_id)

    # If user is not teachr of said class, dont allow them to add students to it
    if request.user != my_class.teacher:
        return httpResponseForbidden("You are not authorized to add students to this class")

    
    if request.method == 'POST':
        # Get students name from from
        student_username = request.POST.get('student_username')

        # Try to get student
        try:
            student_user = User.objects.get(username=student_username, is_student=True)
        except User.DoesNotExist:
            messages.error(request, "Student not found or is not a student")
            return redirect('classes')

    # If student not in class already add them. else student is already in class
    if not Student.objects.filter(user=student_user, classroom=my_class).exists():
        Student.objects.create(user=student_user, classroom=my_class)
        messages.success(request, f"Student {student_username} added to {my_class.name}")
    else:
        message.error(request, f"Student {student_username} is already in this class")

    # Stay on classes page
    return redirect('classes')
"""

# View for allowing student to join classes by entering their respective tokens
@login_required
def join_class(request):
    # If user not student don't let them join a class
    if not request.user.is_student:
        return HttpResponseForbidden("Only students can join classes.")

    if request.method == 'POST':

        # Get toke from form
        access_token = request.POST.get('access_token')

        try:
            # Find class that has the given token
            classroom = Class.objects.get(access_token=access_token)
        # If not class has a token, say invlaid token  
        except Class.DoesNotExist:
            messages.error(request, "Invalid access token. Please try again.")
            return redirect('join_class')

        try:
            student = Student.objects.get(user=request.user)
            if student.classroom == classroom:
                messages.error(request, f"You are already enrolled in {classroom.name}.")
            else:
                messages.error(request, "You are already enrolled in another class. Leave your current class before joining a new one.")
            return redirect('join_class')
        except Student.DoesNotExist:
            # Student is not enrolled in any class, so add them to this one
            Student.objects.create(user=request.user, classroom=classroom)
            messages.success(request, f"You have successfully joined {classroom.name}.")
            return redirect('classes')

    return render(request, 'KidVenture/join_class.html')   






# A view for allowing teacher to view all of thier current students and what classes they are in.
@login_required
def teacher_students(request):

    # Make sure the user is a teacher
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not authorized to view this page")

    # Get all classes and students for teacher
    classes = request.user.classes.prefetch_related(Prefetch('students', queryset=Student.objects.select_related('user')))

    # Render page
    return render(request, 'KidVenture/teacher_students.html', {'classes': classes})

        

# View for removing students from classes
@login_required
def delete_student(request, student_id, class_id):
    
    # If user not teacher, don't let them delete student
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not authorized to delete student")

    # Make sure class belongs to current user
    classroom = get_object_or_404(Class, id=class_id, teacher=request.user)


    # Find and makre sure student are part of class
    student = get_object_or_404(Student, id=student_id, classroom=classroom)


    # If request post, delete student
    if request.method == "POST":
        student.delete()
        return redirect("teacher_students")

def alphabet_matching(request):
    return render(request, "KidVenture/alphabet_matching.html")

def alphabet_memory(request):
    return render(request, "KidVenture/alphabet_memory.html")

def game_selection(request):
    return render(request, "KidVenture/game_selection.html")





def assign_activity(request):
    if request.method == "POST":
        class_id = request.POST.get("classroom")
        activity_name = request.POST.get("activity_name")
        description = request.POST.get("description")
        url_name = request.POST.get("url_name")

        classroom = get_object_or_404(Class, id=class_id)

        # Assign the activity to all students in the class
        for student in classroom.students.all():
            Activity.objects.create(
                name=activity_name,
                description=description,
                progress=0,  # Start at 0%
                student=student,
                url_name=url_name
            )

        return redirect('classes')  # Redirect back to the page

    return redirect('classes')


