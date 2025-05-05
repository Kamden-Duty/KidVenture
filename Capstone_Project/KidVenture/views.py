

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
from .utils import generate_random_username, award_badges
from django.templatetags.static import static
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from .forms import TempPasswordResetForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from .forms import TempPasswordResetForm, TempSetPasswordForm

from django.http import HttpResponseRedirect
from django.urls import reverse

# Avatar imports
from py_avataaars import (
    PyAvataaar, AvatarStyle, SkinColor, HairColor, FacialHairType,
    TopType, MouthType, EyesType, EyebrowType, NoseType,
    AccessoriesType, ClotheType, ClotheGraphicType, Color  
)



import os


from django.conf import settings

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

    

    # Used for feedback 
    msg = None
    form = LoginForm()

    # If method is POST
    if request.method == "POST":

        # Creats a instance of the login form. If POST then fill with the entered data else leave it empty(None)
        form = LoginForm(request.POST or None)

        
        print(f"post reqruest found")
        # Checks to makes sure the data enterd is valid
        if form.is_valid():
            print(f"form is valid")
            # Gets the username entered
            username = form.cleaned_data.get("username")
            # Gets the password entered
            password = form.cleaned_data.get("password")
            # Authenticates the user if credential our valid returns user object else return none
            user = authenticate(username = username, password = password)

            # If user is not None, login and go to home page
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))

            # Else tell the user the their credentials are invalid
            else: 
                msg = "invalid credentials"
            
        # Tells the user that their input in not valid for this form
        else: msg = "error validating form"
    print(f'cound not find post')
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
            Activity.objects.filter(student__classrooms__teacher=request.user)
            .values("student__user__username", "name", "progress", "student__classrooms__name")
            .order_by("student__user__username")[:4]
        )

        # renders the teacher page and passes the total studnets and progress to the html to be used
        return render(request, "KidVenture/teacher_page.html", {
            'total_students': total_students,
            'students_progress': students_progress
        })

    # Else if hte user is a student
    elif request.user.is_student:
        activities = []
        leaderboard = []
        progress_data = []
        free_play = False
        earned_badges = []
        earned_names = set()
        classrooms = []
        teacher = None

        badge_definitions = [
            {"name": "Speedster", "image": static("KidVenture/images/badges/speedster.png")},
            {"name": "Accuracy Master", "image": static("KidVenture/images/badges/accuracy_master.png")},
            {"name": "Mismatch Minor", "image": static("KidVenture/images/badges/mismatch_minor.png")},
        ]
        try:
            # Get student
            student = Student.objects.get(user=request.user)
            classrooms = student.classrooms.all()
            activities = Activity.objects.filter(student=student, completed=False)

            progress_data = []

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
                
                level_details = []
                levels_qs = GameProgress.objects.filter(
                    user=request.user,
                    activity=activity,
                    is_free_play=False,
                    game=activity.game
                ).order_by('level')

                for level in levels_qs:
                    level_details.append({
                        'level': level.level,
                        'time': round(level.time_taken, 2),
                        'mistakes': level.mistakes,
                        'mismatches': level.mismatched_letters,
                        'timestamp': level.timestamp.strftime('%Y-%m-%d %H:%M'),
                    })
                


                progress_data.append({
                    'class_name': activity.classroom,
                    'activity_name': activity.name,
                    'progress_percent': percent_complete,
                    'completed_levels': completed_levels,
                    'max_levels': activity.max_levels,
                    'levels': level_details,
                })
                
            free_play = True

            new_badges = award_badges(student)
            earned_badges = Badge.objects.filter(student=student.user)
            earned_names = {b.name for b in earned_badges}

            for badge in new_badges:
                messages.success(request, f"Congratulations! You've just earned the '{badge.name}' badge!")

            badges = earned_badges
            
            RANDOM_AVATARS = [f"fake_avatars/fake_avatar_{i}.png" for i in range(1, 11)]
            

            # Leaderboard with points calculation
            base_points = 10  # Base points per level
            # Convert classrooms queryset to a list of IDs
            classroom_ids = classrooms.values_list('id', flat=True)

            # Corrected raw_leaderboard query
            raw_leaderboard = (
                GameProgress.objects.filter(user__student__classrooms__id__in=classroom_ids)
                .values('user__id', 'user__username', 'user__avatar')
                .annotate(
                    max_level=Max('level'),
                    total_points=Sum(F('level') * base_points),  # Calculate total points
                    total_mistakes=Sum('mistakes'),
                    avg_time=Avg('time_taken'),
                    total_mismatches=Sum('mismatched_letters')
                )
                .order_by('-total_points', '-max_level', 'total_mistakes', 'avg_time', 'total_mismatches')
            )

            leaderboard = []
            for entry in raw_leaderboard:
                is_current_user = entry['user__id'] == request.user.id
                display_name = entry['user__username'] if is_current_user else generate_random_username()
                avatar_url = entry['user__avatar'] if is_current_user else random.choice(RANDOM_AVATARS)

                leaderboard_entry = {
                    'avatar_url': avatar_url,
                    'display_name': display_name,
                    'max_level': entry['max_level'],
                    'total_points': entry['total_points'],  # Use total points for sorting
                    'total_mistakes': entry['total_mistakes'],
                    'avg_time': entry['avg_time'],
                    'total_mismatches': entry['total_mismatches'],
                    'is_active_user': is_current_user, 
                }
                leaderboard.append(leaderboard_entry)
            
            

        # If user is not student set classroom activites leaderboard and badges to empty sets
        except Student.DoesNotExist:
            classroom = None
            activities = []
            leaderboard = []
            badges = []
            progress_data = []

        
        notifications = Notification.objects.filter(user=request.user).order_by('-date')
        unread_count = notifications.filter(read=False).count()  # Count unread notifications

        # Renders the student page passing activities, notification, classroom, teacher, leaderboard, and badges to the html
        return render(request, 'KidVenture/student_page.html', {
            'activities': activities,
            'notifications': notifications,
            'classrooms': classrooms,
            'teacher': classrooms.first().teacher if classrooms else None,
            'leaderboard': leaderboard,
            'badges': earned_badges,
            'progress_data': progress_data,
            'badge_definitions': badge_definitions,
            'earned_names': earned_names,
            'show_freeplay': free_play,
            'unread_count': unread_count,
            'show_nav': True,
        })
        


@login_required
def mark_all_read(request):
    if request.method == "POST":
        # Update all unread notifications for the logged-in user
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        # Redirect back to the same page (or another page if needed)
        return HttpResponseRedirect(reverse('home'))
    return JsonResponse({'success': False}, status=400)

    
@login_required
def view_profile(request):
    # get the Student row for this user
    # user = get_object_or_404(User, user=request.user)
    date_joined = request.user.date_joined
    return render(request, 'KidVenture/profile.html', {
        'date_joined': date_joined,
        'show_nav': False,
    })


# Used to logout the users
@login_required
def logout_view(request):
    logout(request)
    return redirect('login_view')




# Funtion to create a token for a teacher's class
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

@login_required
def student_homepage(request):
    print("classroom")
    if not request.user.is_student:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get the current user's student profile
    try:
        student = Student.objects.get(user=request.user)
        classroom = student.classroom
        activities = Activity.objects.filter(student=student)
    except Student.DoesNotExist:
        classroom = None
        activities = None

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

    print('Leaderboard data:', leaderboard)  # Add this line for debugging

    # Fetch other necessary data
    notifications = Notification.objects.filter(user=request.user).order_by('-date')

    return render(request, 'KidVenture/student_page.html', {
        'leaderboard': leaderboard,
        'notifications': notifications,
        'classroom': classroom,
        'teacher': classroom.teacher if classroom else None,
    })

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
        Activity.objects.filter(classroom__teacher=request.user, completed=False)
        .values("name", "classroom__name", "url_name", "max_levels", "classroom__id")  
        .annotate(
            class_progress=Avg("progress"),  
            activity_id=Min("id")  
        )
        .order_by("classroom__name")
    )


    # STores the total progress for the clas
    activities_with_progress = []
    # Loops through the activities getting progress to get the average progress for the class for a activity
    for activity in activities:
        class_id = activity["classroom__id"]

       # Calcluate the average progress for the class for an activity
        avg_progress = (
            Activity.objects.filter(
                classroom__id = class_id, name=activity["name"]
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
         return HttpResponseForbidden("You are not authorized to delete a class")

    # Delete class
    my_class.delete()
    # Return user back to the classes page
    return redirect('classes')



@login_required
def join_class(request):
    # If user not student don't let them join a class
    if not request.user.is_student:
        return HttpResponseForbidden("Only students can join classes.")

    if request.method == 'POST':
        access_token = request.POST.get('access_token')

        try:
            classroom = Class.objects.get(access_token=access_token)
        except Class.DoesNotExist:
            messages.error(request, "Invalid access token. Please try again.")
            return redirect('join_class')

        # Get or create the student record for the user
        student, created = Student.objects.get_or_create(user=request.user)

        # Check if the student is already enrolled in this class
        if classroom in student.classrooms.all():
            messages.error(request, f"You are already enrolled in {classroom.name}.")
        else:
            student.classrooms.add(classroom)

            # Assign activities to the student
            create_student_activities(student, classroom)

            # Send a notification
            Notification.objects.create(
                user=request.user,
                title="Enrolled",
                message=f"You have successfully joined {classroom.name}"
            )

            messages.success(request, f"You have successfully joined {classroom.name}.")
            return redirect('classes')

    return render(request, 'KidVenture/join_class.html', {
        'show_nav' : False,
    })

@login_required
def create_student_activities(student, classroom):
    # Loop over each activity template for this class
    for template in classroom.activity_templates.all():
        # Create a corresponding Activity for the student
        Activity.objects.create(
            name=template.name,
            description=template.description,
            progress=0,
            student=student,
            url_name=template.url_name,
            max_levels=template.max_levels,
            game=template.game
        )



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
    student = get_object_or_404(Student, id=student_id)

    # Find and makre sure student are part of class
    student = get_object_or_404(Student, id=student_id)


    # Mke sure the student is in the classroom.      this should always pass, but is just in case something did break
    if classroom not in student.classrooms.all():
        return HttpResponseForbidden("This student is not in the specified class")



    # If request post, delete student
    if request.method == "POST":
        student.classrooms.remove(classroom)
        Activity.objects.filter(student=student, classroom=classroom).delete()
        return redirect("teacher_students")


# view for rendering hte matching game html
def alphabet_matching(request):
    return render(request, "KidVenture/alphabet_matching.html")

# view for rendering the memory gam html
def alphabet_memory(request):
    return render(request, "KidVenture/alphabet_memory.html")

# # view for rendering the game selectio html (will most likely remove this at some point)
# def game_selection(request):
#     return render(request, "KidVenture/game_selection.html")



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
            Notification.objects.create(
                user=request.user,
                title="Game Progress",
                message=f"You have successfully completed {level-1} levels in {game} game."
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
    teacher = request.user
    game = request.GET.get('game', 'matching')

    # Get all students (with user info) in this teacher's classes
    student_users = User.objects.filter(student__classrooms__teacher=request.user).distinct()

    leaderboard = []

    for user in student_users:
        # Get their game progress for the selected game
        progress = (
            GameProgress.objects
            .filter(user=user, game=game)
            .aggregate(
                max_level=Max('level'),
                total_mistakes=Sum('mistakes'),
                avg_time=Avg('time_taken')
            )
        )

        leaderboard.append({
            'user__username': user.username,
            'user__avatar': user.avatar.name if user.avatar else 'default.png',
            'max_level': progress['max_level'] or 0,
            'total_mistakes': progress['total_mistakes'] or 0,
            'avg_time': round(progress['avg_time'], 2) if progress['avg_time'] else 0.0
        })
        
    leaderboard.sort(
    key=lambda x: (-x['max_level'], x['total_mistakes'], x['avg_time'])
)


    return JsonResponse({'leaderboard': leaderboard})


# A view used to assign activites 
@login_required
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
        teacher = classroom.teacher


        activity_exist = Activity.objects.filter(name=activity_name, classroom=classroom).first()
        
        if activity_exist:
         
            messages.error(request, f"An activity with the name '{activity_name}'")
            return redirect('assign_activity')  

        # For studetn in calssroom create activity for them
        for student in classroom.students.all():
            Activity.objects.create(
                name=activity_name,
                description=description,
                progress=0,
                student=student,
                classroom=classroom,
                url_name=url_name,
                max_levels=max_levels,
                game=game,
             
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
@login_required
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

    # Ensure the user is the teacher of the class associated with the activity
    if not activity.student.classrooms.filter(teacher=request.user).exists():
        return HttpResponseForbidden("You are not authorized to delete this activity.")

    # Delete all activities for this class and name
    Activity.objects.filter(student__classrooms__teacher=request.user, name=activity.name).delete()

    messages.success(request, f"All '{activity.name}' activities for the associated class have been deleted.")
    
    return redirect('classes')  # Redirect back to the classes page


# THis is used to completed activities for the teacher so if they want to end the activity without deleting it
@login_required
def complete_class_activity(request, activity_id):
 
    # Get the activity to find the associated class
    activity = get_object_or_404(Activity, id=activity_id)
    classroom = activity.classroom

    # Ensure only the teacher who assigned the activity can complete it
    if request.user != classroom.teacher:
        return HttpResponseForbidden("You are not authorized to complete this activity.")

    # Complete all activities for this class and name
    Activity.objects.filter(
        classroom=classroom,
        name=activity.name
    ).update(completed=True)

    messages.success(request, f"All '{activity.name}' activities for {classroom.name} have been marked as completed.")
    
    
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

            class_activities = student.activities.filter(classroom=classroom)


            # For activity in all of the students activities
            for activity in class_activities:
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
                    "class_id": classroom.id,
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
    activities = Activity.objects.filter(student__classrooms__id=class_id)

    if not activities.exists():
        return JsonResponse({'total_progress': 0})  # No activities, progress is 0%

    # Gets the total progress 
    total_progress = activities.aggregate(total_progress=Avg("progress"))["total_progress"] or 0
    return JsonResponse({'total_progress': round(total_progress, 2)})




# Used to get the assigned activity of a class ( this has a issue if two activites are created with the same name but different levels only one will show though both will be created need to fix )
@login_required
def get_class_activities(request, class_id):
    # Get the classroom
    classroom = get_object_or_404(Class, id=class_id, teacher=request.user)
    
    # Get all activity
    activities = Activity.objects.filter(
        classroom=classroom
    ).values_list('name', flat=True).distinct()

    return JsonResponse({"activities": list(activities)})






class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name       = 'KidVenture/password_reset.html'
    email_template_name = 'KidVenture/password_reset_email.html'
    subject_template_name = 'KidVenture/password_reset_subject.txt'
    form_class          = TempPasswordResetForm
    success_url         = reverse_lazy('home')
    success_message     = "We've emailed you instructions for setting your password."

class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name   = 'KidVenture/password_reset_confirm.html'
    form_class      = TempSetPasswordForm
    success_url     = reverse_lazy('password_reset_complete')
    success_message = "Your password has been set. You can now log in."
