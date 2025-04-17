

# Imports ====================================================================
import random
import string
import json
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from .forms import SignUpForm, LoginForm, CreateClassForm, JoinClassForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from django.db.models import Count, Prefetch
from django.contrib import messages
from django.db.models import Avg, Min
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Max, Sum, Avg, F
from django.db.models.functions import Length
from django.views.decorators.http import require_POST
from .utils import generate_random_username

# Avatar imports
from py_avataaars import (
    PyAvataaar, AvatarStyle, SkinColor, HairColor, FacialHairType,
    TopType, MouthType, EyesType, EyebrowType, NoseType,
    AccessoriesType, ClotheType, ClotheGraphicType, Color  
)



import os


from django.conf import settings
# from py_avataaars import PyAvataaar, AvatarStyle, SkinColor, HairColor, FacialHairType, \
#     TopType, Color, MouthType, EyesType, EyebrowType, NoseType, AccessoriesType, \
#     ClotheType, ClotheGraphicType


# import json
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from py_avataaars import PyAvataaar, AvatarStyle, SkinColor, HairColor, FacialHairType, \
#     TopType, Color, MouthType, EyesType, EyebrowType, NoseType, AccessoriesType, \
#     ClotheType, ClotheGraphicType
# =============================================================================================



# @login_required
# def home(request):
#     return render(request, "KidVenture/home.html")




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


# The home page handles both the main features for both students and teachers hompages. Requires the user to be logged in
@login_required
def home(request):

    # IF the user is a teacher
    if request.user.is_teacher:

        # Gets the total students from 
        total_students = request.user.classes.aggregate(total=Count('students'))['total'] or 0

        # Reterives the studetns progress
        students_progress = (
            Activity.objects.filter(student__classroom__teacher=request.user)
            .values("student__user__username", "name", "progress", "student__classroom__name")
            .order_by("student__user__username")[:4]
        )

        # renders the teacher page and passes the total studnets and progress to the html to be used
        return render(request, "KidVenture/teacher_page.html", {
            'total_students': total_students,
            'students_progress': students_progress
        })

    # Else if hte user is a student
    elif request.user.is_student:
        try:
            # Get student
            student = Student.objects.select_related('classroom').get(user=request.user)
            # Gets the students classroom
            classroom = student.classroom
            # Gets the activities assigned to the student
            activities = Activity.objects.filter(student=student, completed=False)

            # Loops through the activiites checking progress. this is so we can show the students progress on the page
            for activity in activities:
                # If the user has done any part of the actiivy get its complete nad percent complete
                if activity.max_levels > 0:
                    completed_levels = round((activity.progress / 100) * activity.max_levels, 2)
                    percent_complete = round((completed_levels / activity.max_levels) * 100, 2)
                # Else just leave the complete and percent complete 0
                else:
                    completed_levels = 0
                    percent_complete = 0
                # update the activity
                activity.completed_levels = completed_levels
                activity.percent_complete = percent_complete

            raw_leaderboard = (
                GameProgress.objects.filter(user__student__classroom=classroom)
                .values('user__id', 'user__username', 'user__avatar')
                .annotate(
                    max_level=Max('level'),
                    total_mistakes=Sum('mistakes'),
                    avg_time=Avg('time_taken'),
                    total_mismatches=Sum('mismatched_letters')
                )
                .order_by('-max_level', 'total_mistakes', 'avg_time', 'total_mismatches')
            )

            leaderboard = []
            for entry in raw_leaderboard:
                is_current_user = entry['user__id'] == request.user.id
                display_name = entry['user__username'] if is_current_user else generate_random_username()
                leaderboard_entry = {
                    'avatar_url': entry['user__avatar'],
                    'display_name': display_name,
                    'max_level': entry['max_level'],
                    'total_mistakes': entry['total_mistakes'],
                    'avg_time': entry['avg_time'],
                    'total_mismatches': entry['total_mismatches'],
                    'is_active_user': is_current_user,  # Add the flag here
                }
                leaderboard.append(leaderboard_entry)
                print(leaderboard_entry)  # Print the constructed leaderboard entry

            # Gets the students badges
            badges = Badge.objects.filter(user=request.user) if hasattr(request.user, 'badge_set') else []
        # If user is not student set classroom activites leaderboard and badges to empty sets
        except Student.DoesNotExist:
            classroom = None
            activities = []
            leaderboard = []
            badges = []

        
        notifications = Notification.objects.filter(user=request.user).order_by('-date')

        # Renders the stuetn page passing activities, notification, classroom, teacher, leaderboard, and badges to the html
        return render(request, 'KidVenture/student_page.html', {
            'activities': activities,
            'notifications': notifications,
            'classroom': classroom,
            'teacher': classroom.teacher if classroom else None,
            'leaderboard': leaderboard,
            'badges': badges,
        })





# Used to logout the users
@login_required
def logout_view(request):
    logout(request)
    return login_view(request)




# Funtion to create a token for a teacher's class
@login_required
def createToken():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))


# The create class view is used to create classes for the teacher.
@login_required 
def create_class(request):

    # Checks if the user is not a teacher and if they are not return a httmp response telling them  (may remove this could be giving the user too much info)
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not authorized to create a class")

    # Limits the teacher to only having 5 classes 
    if request.user.classes.count() >= 5:
        return HttpResponseForbidden("You cannot create more than 5 classes")

    # If the user create a post request
    if request.method == 'POST':
        # Create our class form
        form = CreateClassForm(request.POST)
        # If the form has the valid input
        if form.is_valid():
            # save the form
            my_class = form.save(commit=False)
            # Get the teacher that created it
            my_class.teacher = request.user
            # Crate the toek for the class useing the token creatiion function
            my_class.access_token = createToken()
            # Saves the class
            my_class.save()
            # Redirect back to the classes page
            return redirect('classes')

    # else creates a blank form
    else:
        form = CreateClassForm()
    # rrenders the create class html and psses the form var into it
    return render(request, 'KidVenture/create_class.html', {'form': form})

def is_student(user):
    return user.user_type == 'student'

# @login_required
# def student_homepage(request):
#     print("classroom")
#     if not request.user.is_student:
#         return HttpResponseForbidden("You are not authorized to access this page.")
    
#     # Get the current user's student profile
#     try:
#         student = Student.objects.get(user=request.user)
#         classroom = student.classroom
#         activities = Activity.objects.filter(student=student)
#     except Student.DoesNotExist:
#         classroom = None
#         activities = None

#     # Fetch leaderboard data
#     leaderboard = (
#         GameProgress.objects.values('user__username', 'user__avatar')  # Assuming 'avatar' is a field in the User model
#         .annotate(
#             max_level=Max('level'),
#             total_mistakes=Sum('mistakes'),
#             avg_time=Avg('time_taken'),
#             total_mismatches=Sum(Length('mismatched_letters'))  # Count mismatches
#         )
#         .order_by('-max_level', 'total_mistakes', 'avg_time', 'total_mismatches')
#     )

#     print('Leaderboard data:', leaderboard)  # Add this line for debugging

#     # Fetch other necessary data
#     notifications = Notification.objects.filter(user=request.user).order_by('-date')

#     return render(request, 'KidVenture/student_page.html', {
#         'leaderboard': leaderboard,
#         'notifications': notifications,
#         'classroom': classroom,
#         'teacher': classroom.teacher if classroom else None,
#     })

@login_required
def calendar_view(request):
    if not request.user.is_student:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # You can add additional logic here, such as fetching calendar events.
    # For now, we’ll just render a basic calendar page.
    return render(request, 'KidVenture/calendar_page.html', {})
    

# This is the main view for our classes here we will load the activiites nad progress for our classes
@login_required
def classes(request):
    # IF the user is not a teacher redirect them back to their home page
    if not request.user.is_teacher:
        return redirect('home')

    # gets and group all of hte non completed activities by classes
    activities = (
        Activity.objects.filter(student__classroom__teacher=request.user, completed=False)
        .values("name", "student__classroom__name", "url_name", "max_levels")  
        .annotate(
            class_progress=Avg("progress"),  
            activity_id=Min("id")  
        )
        .order_by("student__classroom__name")
    )


    # STores the total progress for the clas
    activities_with_progress = []
    # Loops through the activities getting progress to get the average progress for the class for a activity
    for activity in activities:
        class_name = activity["student__classroom__name"]

       # Calcluate the average progress for the class for an activity
        avg_progress = (
            Activity.objects.filter(
                student__classroom__name=class_name, name=activity["name"]
            )
            .aggregate(avg_progress=Avg("progress"))["avg_progress"]
        )

        # Makes sure our progress value is a usable value and not a incomplete value
        avg_progress = round(avg_progress, 2) if avg_progress is not None else 0

        # Stores the  progress in the activity dictionary
        activity["class_progress"] = avg_progress
        activities_with_progress.append(activity)

    # Renders the classes html and passees it "activities"
    return render(
        request, "KidVenture/classes.html", {"activities": activities_with_progress}
    )






# This view is used to delte classes
@login_required
def delete_class(request, class_id):
    # Gets class
    my_class = get_object_or_404(Class, id=class_id)
    # Makes sure the user is the teacher of the clas
    if request.user != my_class.teacher:
         return httpResponseForbidden("You are not authorized to delete a class")

    # Delete class
    my_class.delete()
    # Return user back to the classes page
    return redirect('classes')


# This view allows students to join class using the class token the teacher has to give them
@login_required
def join_class(request):
    # If user not student don't let them join a class
    if not request.user.is_student:
        return HttpResponseForbidden("Only students can join classes.")

    # If request method is post: 
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
            # Get student(user)
            student = Student.objects.get(user=request.user)

            # If the student is already in the class tell them
            if student.classroom == classroom:
                messages.error(request, f"You are already enrolled in {classroom.name}.")

            # If the student is in another clas tell them
            else:
                messages.error(request, "You are already enrolled in another class. Leave your current class before joining a new one.")
            # Redirect back to home or /
            return redirect('/')

        # If the student is not in the class allow them to join
        except Student.DoesNotExist:
            # Student is not enrolled in any class, so add them to this one
            Student.objects.create(user=request.user, classroom=classroom)
            # Notify them
            Notification.objects.create(user=request.user, title="Enrolled", message=f"You have successfully joined {classroom.name}")
            # Give the a message
            messages.success(request, f"You have successfully joined {classroom.name}.")
            # Redirect them back to classes
            return redirect('classes')
    # Renders the join_class html
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


# view for rendering hte matching game html
def alphabet_matching(request):
    return render(request, "KidVenture/alphabet_matching.html")

# view for rendering the memory gam html
def alphabet_memory(request):
    return render(request, "KidVenture/alphabet_memory.html")

# view for rendering the game selectio html (will most likely remove this at some point)
def game_selection(request):
    return render(request, "KidVenture/game_selection.html")



# A view used for saving game progress
@csrf_exempt
@login_required
def save_game_progress(request):

    # If request method is post: 
    if request.method == 'POST':
        try:
            # load the json data and store it in data
            data = json.loads(request.body)

            # Gets the level form data
            level = data.get('level')
            # Gets time_take form data
            time_taken = data.get('time_taken')
            # Gets mistakes from data
            mistakes = data.get('mistakes')
            # Gets the mismatched_letters from data
            mismatched_letters = data.get('mismatched_letters')
            # gets the id of the activity from data
            activity_id = data.get('activity_id')
            # gets the game along with its default
            game = data.get('game', 'matching')

            # Sets activity to non and freepray to true
            activity = None
            is_free_play = True

            # if their is the activity do the get the activity and set free play to false
            if activity_id:
                activity = get_object_or_404(Activity, id=activity_id, student__user=request.user)
                is_free_play = False

            # Create a gameProgress objects with the data we retreived from the request
            GameProgress.objects.create(
                user=request.user,
                level=level,
                time_taken=time_taken,
                mistakes=mistakes,
                mismatched_letters=json.dumps(mismatched_letters),
                activity=activity,
                is_free_play=is_free_play,
                game=game
            )

            # if it is a activity, set the progres to elvel - 1 because that is what they have completed and not what they are on
            if activity:
          
                activity.update_progress(level - 1)
            # Return json response
            return JsonResponse({'status': 'success'})
        
        # This is for debugging so we known a execption occurred
        except Exception as e:
            print(f"Error saving game progress: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    # returns a json response if failed
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


# A view used to get our last stopping point or session
@login_required
def get_last_session(request):
    try:
        # Gets our game value . if it can't it will just set hte deafult which is matching
        game = request.GET.get('game', 'matching')

        # Retreivesi where we left off from the game project object
        last_progress = GameProgress.objects.filter(user=request.user, is_free_play=True, game=game).latest('timestamp')

        # Creates a data dict
        data = {
            'last_level': last_progress.level,
            'time_taken': last_progress.time_taken,
            'mistakes': last_progress.mistakes,
            'mismatched_letters': last_progress.mismatched_letters,
        }
        # Returns our data
        return JsonResponse(data)
    # This would happen if we didn't have any progress
    except GameProgress.DoesNotExist:
        # so our first level would just be 1
        return JsonResponse({'last_level': 1})


# Leaderboard view
@login_required
def get_leaderboard(request):
    # Figures out what game we are using (although not that useful at the moment)
    game = request.GET.get('game', 'matching')

    # Get the active user's username
    active_user_username = request.user.username

    # Gets our leaderboard values by pulling from the game progress
    leaderboard = (
        GameProgress.objects.filter(game=game)
        .values('user__username', 'user__avatar')
        .annotate(
            max_level=Max('level'),
            total_mistakes=Sum('mistakes'),
            avg_time=Avg('time_taken'),
            total_mismatches=Sum('mismatched_letters')
        )
        .order_by('-max_level', 'total_mistakes', 'avg_time', 'total_mismatches')
    )

    # Add a flag to indicate if the user is the active user
    leaderboard_with_active_flag = [
        {
            **entry,
            'is_active_user': entry['user__username'] == active_user_username
        }
        for entry in leaderboard
    ]

    # Return the JSON response with leaderboard info
    return JsonResponse({'leaderboard': leaderboard_with_active_flag})

@login_required
def get_teacher_leaderboard(request):
    # Get the logged-in teacher
    teacher = request.user

    # Get the class or students associated with the teacher
    # Assuming a Class model links teachers to students
    students = Class.objects.filter(teacher=teacher).values_list('students', flat=True)

    # Get the game type (default to 'matching')
    game = request.GET.get('game', 'matching')

    # Filter leaderboard data for the teacher and their students
    leaderboard = (
        GameProgress.objects.filter(game=game, user__id__in=students)
        .values('user__username', 'user__avatar')
        .annotate(
            max_level=Max('level'),
            total_mistakes=Sum('mistakes'),
            avg_time=Avg('time_taken')
        )
        .order_by('-max_level', 'total_mistakes', 'avg_time')
    )

    # Return the leaderboard data as JSON
    return JsonResponse({'leaderboard': list(leaderboard)})

# A view used to assign activites 
def assign_activity(request):
    # If request is post
    if request.method == "POST":
        # Get the classroom id
        class_id = request.POST.get("classroom")
        # Get the name of the activity
        activity_name = request.POST.get("activity_name")
        # Get the description. Which we won't use so it will just be a default of blank
        description = request.POST.get("description")
        # gets the url name
        url_name = request.POST.get("url_name")
        # Gets the number of leves the teacher assigned
        max_levels = int(request.POST.get("max_level", 1))
        # Gets the game will default ot matching if can't find the selected value
        game = request.POST.get("game", "matching")
        # GEts the classroom 
        classroom = get_object_or_404(Class, id=class_id)

        # For studetn in calssroom create activity for them
        for student in classroom.students.all():
            Activity.objects.create(
                name=activity_name,
                description=description,
                progress=0,
                student=student,
                url_name=url_name,
                max_levels=max_levels,
                game=game
            )
        
        # Redirect back to the classes page
        return redirect('classes')
    # Redirect back to the classes page
    return redirect('classes')




# A leaderboard view that just used for points. will probably be chagned later
def leaderboard_view(request):
    leaderboard = LeaderboardEntry.objects.order_by('-points')  
    return render(request, 'KidVenture/leaderboard.html', {'leaderboard': leaderboard})




# View used to edits the users avatars
@login_required
def edit_avatar(request):
    
    # Gets the user
    user = request.user  

    ## Here we make a list of all of the options avlaialbe to use from the pyavvatar library
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

    # This converst our options to json so we can render it on a page in javascript
    avatar_options_json = json.dumps(avatar_options)

    # If request method id post
    if request.method == "POST":
        # Gets teh data from our current avatar =( usually just the deafult values defined in models)
        new_avatar_data = request.POST.get("avatar_data")
     
        # If data contains new avatar setting different from the default or set values for it
        if new_avatar_data:
            try:
                # load the new data from json into our avatar 
                new_avatar_data = json.loads(new_avatar_data)
        

                # Crate oru new avatar using the loaded data inputs
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

                # Save the newly create avatar
                avatar_path = os.path.join(settings.MEDIA_ROOT, "avatars", f"avatar_{user.username}.png")
                os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
                avatar.render_png_file(avatar_path)

                # Update the user's avatar to their new one
                user.avatar.name = f"avatars/avatar_{user.username}.png"
                user.save()
             
            except Exception as e:
                print(f" Error getting avatar: {e}") 

        # Redirects to home
        return redirect("home") 

    # Renders the edit avatar page and passes in the avatar options
    return render(request, "KidVenture/edit_avatar.html", {
        "avatar_options": avatar_options,
        "avatar_options_json": avatar_options_json,
    })







# Used to update our avatar while we are editing so we can see what we are changing live
@csrf_exempt
def update_avatar_preview(request):
    # If the method is post
    if request.method == "POST":
        try:
            # Get and parse the json data 
            avatar_data = json.loads(request.body) 

            # Create the avatar svg for preivew from the currently selected data we are reading
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

            # Return the svg
            return HttpResponse(avatar.render_svg(), content_type="image/svg+xml")  

        except Exception as e:
            return HttpResponse(f"Error: {e}", status=400)

    return HttpResponse("Invalid request", status=400)


# A view used to check the progres on activites
@login_required
def check_activity_progress(request, activity_id):

    # the the activity using the passed in id
    activity = get_object_or_404(Activity, id=activity_id, student__user=request.user)

    # Calculate the progres son the activity
    levels_completed = max(1, math.ceil((activity.progress / 100) * activity.max_levels))

    
    # Checks to see if the user has completed the activity
    if levels_completed >= activity.max_levels:
        # sets the activity completed to ture
        activity.completed = True
        # saves the activity
        activity.save()
        # Returns json response
        return JsonResponse({'completed': True})
    # Returns json reponse
    return JsonResponse({'completed': False})





# This view is used to get our activity progress not just check it. Most likel could have merged this view with the previous
@login_required
def get_activity_progress(request, activity_id):
    try:
        # Gets the activity
        activity = Activity.objects.get(id=activity_id, student__user=request.user)

        # Calculate last completed level based on percentage progress
        last_level = max(1, (round((activity.progress / 100) * activity.max_levels) + 1))
       
        # Returns json repsponse of the last level theyu completed
        return JsonResponse({'last_level': last_level})

    except Activity.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)


# A view used to set the activity to complete 
@csrf_exempt
@login_required
def complete_activity(request, activity_id):
    
    try:
        # Gets the activity
        activity = get_object_or_404(Activity, id=activity_id, student__user=request.user)

        # Mark activity as completed instead of deleting it
        activity.completed = True
        activity.progress = 100
        activity.save()

        # Returns json response
        return JsonResponse({'status': 'success', 'message': 'Activity marked as completed.'})

    except Activity.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Activity not found.'}, status=404)



# This view is used to reset the progress on games. ( NOt used any more will proably delete)
@csrf_exempt
@require_POST
@login_required
def reset_free_play_progress(request):
    
    try:
        # Loads the jsons data into body ( might change name to data not sure which one is more descriptive)
        body = json.loads(request.body)
        # Gets the game type from the loaded data .
        game = body.get('game')

        if not game:
            return JsonResponse({'status': 'error', 'message': 'Missing game parameter.'}, status=400)

        # Delete progress only for this game type
        GameProgress.objects.filter(user=request.user, game=game).delete()
        return JsonResponse({'status': 'success', 'message': f'{game} progress reset.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



# This view is used to delete activities. Once again this is for teachers used
@login_required
def delete_activity(request, activity_id):

    
    # Get the activity
    activity = get_object_or_404(Activity, id=activity_id)

    # Makes sure hte user calling the delete is the teache of the class
    if request.user != activity.student.classroom.teacher:
        return HttpResponseForbidden("You are not authorized to delete this activity.")

    # Delete all activities for this class and name
    Activity.objects.filter(student__classroom=activity.student.classroom, name=activity.name).delete()

    messages.success(request, f"All '{activity.name}' activities for {activity.student.classroom.name} have been deleted.")
    
    return redirect('classes')  # Redirect back to the classes page


# THis is used to completed activities for the teacher so if they want to end the activity without deleting it
@login_required
def complete_class_activity(request, activity_id):
    """Marks all activities for a class as complete."""

    # Get the activity to find the associated class
    activity = get_object_or_404(Activity, id=activity_id)

    # Ensure only the teacher who assigned the activity can complete it
    if request.user != activity.student.classroom.teacher:
        return HttpResponseForbidden("You are not authorized to complete this activity.")

    # Complete all activities for this class and name
    Activity.objects.filter(student__classroom=activity.student.classroom, name=activity.name).update(completed=True)

    messages.success(request, f"All '{activity.name}' activities for {activity.student.classroom.name} have been marked as completed.")
    
    return redirect('classes')  # Redirect back to the classes page







# This view is for getting the progress of a student
@login_required
def progress_overview(request):

    # Makes sure the user is teacher
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Get all classes that belong to the current teacher
    classes = Class.objects.filter(teacher=request.user)

    # Gets teh progress data for all teh teachers students This is a loop in a loop so a big o of n^2
    progress_data = []
    # For classroom (may change name to class. not sure which one is more descriptive) in classes 
    for classroom in classes:
        # for the student in the classroom
        for student in classroom.students.all():
            # For activity in all of the students activities
            for activity in student.activities.all():
                # Calculate percent complete
                # Calcualt the number of copmleted levels
                completed_levels = round((activity.progress / 100) * activity.max_levels, 2)
                # This if check if to prevents errros from happening if the activity assigned levels is 1. 
                if (activity.max_levels > 1 and completed_levels > 1):
                    percent_complete = round(((completed_levels)/ activity.max_levels) * 100, 2) if activity.max_levels else 0
                else:
                    percent_complete = round(((completed_levels)/ activity.max_levels) * 100, 2) if activity.max_levels else 0

                # Adds the caclualte data inot hte progress data
                progress_data.append({
                    "student_name": student.user.username,
                    "class_name": classroom.name,
                    "activity_name": activity.name,
                    "percent_complete": percent_complete
                })
    # Render the progess overview page and passes in the clases nad progress data 
    return render(request, 'KidVenture/progress_overview.html', {
        'classes': classes,
        'progress_data': progress_data,
    })





# THis view is used to retreieve the total progres sof a class 
@login_required
def get_class_total_progress(request, class_id):
    # Gets the activity
    activities = Activity.objects.filter(student__classroom_id=class_id)

    if not activities.exists():
        return JsonResponse({'total_progress': 0})  # No activities, progress is 0%

    # Gets the total progress 
    total_progress = activities.aggregate(total_progress=Avg("progress"))["total_progress"] or 0
    return JsonResponse({'total_progress': round(total_progress, 2)})




# Used to get the assigned activity of a class ( this has a issue if two activites are created with the same name but different levels only one will show though both will be created need to fix )
@login_required
def get_class_activities(request, class_id):
    # Gets the classroom 
    classroom = get_object_or_404(Class, id=class_id, teacher=request.user)
    # Gest teh activities of the classroom 
    activities = Activity.objects.filter(student__classroom=classroom).values_list('name', flat=True).distinct()
    # Returns the activites of the classroom
    return JsonResponse({"activities": list(activities)})
