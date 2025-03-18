import random

import string

import json

from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, HttpResponseForbidden

from .forms import SignUpForm, LoginForm, CreateClassForm, JoinClassForm

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required, user_passes_test

from .models import *

from django.db.models import Count, Prefetch

from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

from django.db.models import Max, Sum, Avg, F
from django.db.models.functions import Length

# Avatar imports
from py_avataaars import (
    PyAvataaar, AvatarStyle, SkinColor, HairColor, FacialHairType,
    TopType, MouthType, EyesType, EyebrowType, NoseType,
    AccessoriesType, ClotheType, ClotheGraphicType, Color  
)


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
        print("classroom")
        if not request.user.is_student:
            return HttpResponseForbidden("You are not authorized to access this page.")
        
        # Get the current users student profile
        try:
            student = Student.objects.get(user=request.user)
            classroom = student.classroom
            activites = Activity.objects.filter(student=student)
        except Student.DoesNotExist:
            classroom = None
            activities = None
            
        # If the student hasn't joined a class, redirect them to the join class page
        # if classroom is None:
        #     return redirect('join_class')
        # print(classroom)
        # Fetch activities linked to the student
        # completed_activities = Activity.objects.filter(student=student, completed=True)
        # pending_activities = Activity.objects.filter(student=student, completed=False)
        
        # progress = Progress.objects.filter(student=student)
        # achievements = Achievement.objects.filter(student=student)
        # announcements = Announcement.objects.filter(classroom=student.classroom)
        leaderboard = LeaderboardEntry.objects.order_by('-points')[:10]
        notifications = Notification.objects.filter(user=request.user).order_by('-date')
        print(notifications)
        return render(request, 'KidVenture/student_page.html', {
            # 'activities': activities,
            # 'completed_activities': completed_activities,
            # 'pending_activities': pending_activities,
            # 'progress': progress,
            # 'achievements': achievements,
            # 'announcements': announcements,
            # 'leaderboard': leaderboard,
            'notifications': notifications,
            'classroom': classroom,
            'teacher': classroom.teacher if classroom else None,
        })
    else:
        return HttpResponseForbidden("You are not authorized to view this page.")


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
            print("Generated Token:", my_class.access_token)  # Debugging
            my_class.save()
            return redirect('classes')
    else:
        form = CreateClassForm()
    return render(request, 'KidVenture/create_class.html', {'form': form})

def is_student(user):
    return user.user_type == 'student'
    
@login_required
def student_homepage(request):
    # Fetch leaderboard data
    leaderboard = (
        GameProgress.objects.values('user__username', 'user__avatar')  # Assuming 'avatar' is a field in the User model
        .annotate(
            max_level=Max('level'),
            total_mistakes=Sum('mistakes'),
            avg_time=Avg('time_taken'),
            total_mismatches=Sum(Length('mismatched_letters'))  # Count mismatches
        )
        .order_by('-max_level', 'total_mistakes', 'avg_time', 'total_mismatches')
    )

    # Fetch other necessary data
    classroom = request.user.classroom if hasattr(request.user, 'classroom') else None
    teacher = classroom.teacher if classroom else None
    notifications = Notification.objects.filter(user=request.user).order_by('-date')

    return render(request, 'KidVenture/student_page.html', {
        'leaderboard': leaderboard,
        'classroom': classroom,
        'teacher': teacher,
        'notifications': notifications,
    })

@login_required
def calendar_view(request):
    if not request.user.is_student:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # You can add additional logic here, such as fetching calendar events.
    # For now, we’ll just render a basic calendar page.
    return render(request, 'KidVenture/calendar_page.html', {})
    

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
# @login_required
# def join_class(request):
#     logger.info("Test1")
#     # If user not student don't let them join a class
#     if not request.user.is_student:
#         return HttpResponseForbidden("Only students can join classes.")

#     if request.method == 'POST':
#         form = JoinClassForm(request.POST)
#         if form.is_valid():
#             logger.info("Test22")
#             # Get token from form
#             access_token = request.POST.get('token')
#             logger.info("Test2")

#             try:
#                 # Find class that has the given token
#                 classroom = Class.objects.get(access_token=access_token)
#             # If not class has a token, say invlaid token  
#             except Class.DoesNotExist:
#                 messages.error(request, "Invalid access token. Please try again.")
#                 logger.info("Test3")
#                 return render(request, 'KidVenture/join_class.html', {"form": form})
        
#             # Check if student is already enrolled
#             if Student.objects.filter(user=request.user, classroom=classroom).exists():
#                 messages.error(request, f"You are already enrolled in {classroom.name}.")
#                 logger.info("Test4")
#                 return render(request, 'KidVenture/join_class.html', {"form": form})
            
#             if Student.objects.filter(user=request.user).exists():
#                 messages.error(request, "You are already enrolled in another class. Leave your current class before joining a new one.")
#                 logger.info("Test5")
#                 return render(request, 'KidVenture/join_class.html', {"form": form})

#             # Create student-class relationship
#             Student.objects.create(user=request.user, classroom=classroom)
#             messages.success(request, f"You have successfully joined {classroom.name} with {classroom.teacher.get_full_name()}!")
#             return redirect('student_homepage')
        
#         else:
#             print(form.errors)
#             return render(request, 'KidVenture/join_class.html', {"form": form})  # Handle invalid form
        
#     else:
#         form = JoinClassForm()

#         # try:
#         #     student = Student.objects.get(user=request.user)
#         #     if student.classroom == classroom:
#         #         messages.error(request, f"You are already enrolled in {classroom.name}.")
#         #     else:
#         #         messages.error(request, "You are already enrolled in another class. Leave your current class before joining a new one.")
#         #     return redirect('join_class')
#         # except Student.DoesNotExist:
#         #     # Student is not enrolled in any class, so add them to this one
#         #     Student.objects.create(user=request.user, classroom=classroom)
#         #     messages.success(request, f"You have successfully joined {classroom.name}.")
#         #     return redirect('classes')

#     return render(request, 'KidVenture/join_class.html', {"form": form})   

@login_required
def join_class(request):
    # If user not student don't let them join a class
    if not request.user.is_student:
        return HttpResponseForbidden("Only students can join classes.")

    if request.method == 'POST':

        # Get toke from form
        access_token = request.POST.get('access_token')
        print("test")
        try:
            # Find class that has the given token
            classroom = Class.objects.get(access_token=access_token)
            print("test1")
        # If not class has a token, say invlaid token  
        except Class.DoesNotExist:
            messages.error(request, "Invalid access token. Please try again.")
            print("test2")
            return redirect('join_class')
    

        try:
            student = Student.objects.get(user=request.user)
            print(student.classroom)
            if student.classroom == classroom:
                messages.error(request, f"You are already enrolled in {classroom.name}.")
                print("test4")
            else:
                messages.error(request, "You are already enrolled in another class. Leave your current class before joining a new one.")
                print("test5")
            return redirect('/')
        except Student.DoesNotExist:
            # Student is not enrolled in any class, so add them to this one
            Student.objects.create(user=request.user, classroom=classroom)
            Notification.objects.create(user=request.user, title="Enrolled", message=f"You have successfully joined {classroom.name}")
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

@csrf_exempt
@login_required
def save_game_progress(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        level = data.get('level')
        time_taken = data.get('time_taken')
        mistakes = data.get('mistakes')
        mismatched_letters = data.get('mismatched_letters')

        GameProgress.objects.create(
            user=request.user,
            level=level,
            time_taken=time_taken,
            mistakes=mistakes,
            mismatched_letters=json.dumps(mismatched_letters)
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_last_session(request):
    try:
        last_progress = GameProgress.objects.filter(user=request.user).latest('timestamp')
        data = {
            'last_level': last_progress.level,
            'time_taken': last_progress.time_taken,
            'mistakes': last_progress.mistakes,
            'mismatched_letters': last_progress.mismatched_letters,
        }
        return JsonResponse(data)
    except GameProgress.DoesNotExist:
        return JsonResponse({'last_level': 1})  # Default to level 1 if no progress found


@login_required
def get_leaderboard(request):
    leaderboard = (
        GameProgress.objects.values('user__username', 'user__avatar')  # Assuming 'avatar' is a field in the User model
        .annotate(
            max_level=Max('level'),
            total_mistakes=Sum('mistakes'),
            avg_time=Avg('time_taken'),
            total_mismatches=Sum(Length('mismatched_letters'))  # Count mismatches
        )
        .order_by('-max_level', 'total_mistakes', 'avg_time', 'total_mismatches')
    )

    return JsonResponse({'leaderboard': list(leaderboard)})


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





def leaderboard_view(request):
    leaderboard = LeaderboardEntry.objects.order_by('-points')  
    return render(request, 'KidVenture/leaderboard.html', {'leaderboard': leaderboard})











import json
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from py_avataaars import PyAvataaar, AvatarStyle, SkinColor, HairColor, FacialHairType, \
    TopType, Color, MouthType, EyesType, EyebrowType, NoseType, AccessoriesType, \
    ClotheType, ClotheGraphicType

@login_required
def edit_avatar(request):
    """Allow users to modify their avatar using arrows to cycle through options."""
    user = request.user  # Get current user

    # ✅ Define available avatar options
    avatar_options = {
        "style": [e.name for e in AvatarStyle],
        "skin_color": [e.name for e in SkinColor],
        "hair_color": [e.name for e in HairColor],
        "facial_hair_type": [e.name for e in FacialHairType],
        "top_type": [e.name for e in TopType],
        "mouth_type": [e.name for e in MouthType],
        "eye_type": [e.name for e in EyesType],
        "eyebrow_type": [e.name for e in EyebrowType],
        "nose_type": [e.name for e in NoseType],
        "accessories_type": [e.name for e in AccessoriesType],
        "clothe_type": [e.name for e in ClotheType],
        "clothe_graphic_type": [e.name for e in ClotheGraphicType],
        "clothe_color": [e.name for e in Color],
    }

    # ✅ Convert options to JSON for JavaScript
    avatar_options_json = json.dumps(avatar_options)

    if request.method == "POST":
        new_avatar_data = request.POST.get("avatar_data")
        print(f"🟢 Received avatar data: {new_avatar_data}")  # ✅ Debugging

        if new_avatar_data:
            try:
                new_avatar_data = json.loads(new_avatar_data)
                print(f"✅ Parsed JSON: {new_avatar_data}")  # ✅ Confirm parsing worked

                # ✅ Generate new avatar
                avatar = PyAvataaar(
                    style=getattr(AvatarStyle, new_avatar_data["style"]),
                    skin_color=getattr(SkinColor, new_avatar_data["skin_color"]),
                    hair_color=getattr(HairColor, new_avatar_data["hair_color"]),
                    facial_hair_type=getattr(FacialHairType, new_avatar_data["facial_hair_type"]),
                    top_type=getattr(TopType, new_avatar_data["top_type"]),
                    mouth_type=getattr(MouthType, new_avatar_data["mouth_type"]),
                    eye_type=getattr(EyesType, new_avatar_data["eye_type"]),
                    eyebrow_type=getattr(EyebrowType, new_avatar_data["eyebrow_type"]),
                    nose_type=getattr(NoseType, new_avatar_data["nose_type"]),
                    accessories_type=getattr(AccessoriesType, new_avatar_data["accessories_type"]),
                    clothe_type=getattr(ClotheType, new_avatar_data["clothe_type"]),
                    clothe_graphic_type=getattr(ClotheGraphicType, new_avatar_data["clothe_graphic_type"]),
                    clothe_color=getattr(Color, new_avatar_data["clothe_color"]),
                )

                # ✅ Save new avatar
                avatar_path = os.path.join(settings.MEDIA_ROOT, "avatars", f"avatar_{user.username}.png")
                os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
                avatar.render_png_file(avatar_path)

                # ✅ Update user avatar field
                user.avatar.name = f"avatars/avatar_{user.username}.png"
                user.save()
                print("✅ Avatar updated successfully!")  # Debugging
            except Exception as e:
                print(f"❌ Error processing avatar: {e}")  # Debugging

        return redirect("home")  # ✅ Redirect after saving

    return render(request, "KidVenture/edit_avatar.html", {
        "avatar_options": avatar_options,
        "avatar_options_json": avatar_options_json,
    })






import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from py_avataaars import PyAvataaar, AvatarStyle, SkinColor, HairColor, FacialHairType, \
    TopType, Color, MouthType, EyesType, EyebrowType, NoseType, AccessoriesType, \
    ClotheType, ClotheGraphicType

@csrf_exempt  # Allows AJAX POST requests without CSRF token issues
def update_avatar_preview(request):
    """Generate and return a live SVG preview based on user selections."""
    if request.method == "POST":
        try:
            avatar_data = json.loads(request.body)  # Parse JSON from request

            # ✅ Generate new avatar SVG
            avatar = PyAvataaar(
                style=getattr(AvatarStyle, avatar_data["style"]),
                skin_color=getattr(SkinColor, avatar_data["skin_color"]),
                hair_color=getattr(HairColor, avatar_data["hair_color"]),
                facial_hair_type=getattr(FacialHairType, avatar_data["facial_hair_type"]),
                top_type=getattr(TopType, avatar_data["top_type"]),
                mouth_type=getattr(MouthType, avatar_data["mouth_type"]),
                eye_type=getattr(EyesType, avatar_data["eye_type"]),
                eyebrow_type=getattr(EyebrowType, avatar_data["eyebrow_type"]),
                nose_type=getattr(NoseType, avatar_data["nose_type"]),
                accessories_type=getattr(AccessoriesType, avatar_data["accessories_type"]),
                clothe_type=getattr(ClotheType, avatar_data["clothe_type"]),
                clothe_graphic_type=getattr(ClotheGraphicType, avatar_data["clothe_graphic_type"]),
                clothe_color=getattr(Color, avatar_data["clothe_color"]),
            )

            return HttpResponse(avatar.render_svg(), content_type="image/svg+xml")  # ✅ Fix here

        except Exception as e:
            return HttpResponse(f"Error: {e}", status=400)

    return HttpResponse("Invalid request", status=400)