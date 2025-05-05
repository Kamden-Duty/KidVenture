from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Import for custom avatar creation
from py_avataaars import PyAvataaar, AvatarStyle, SkinColor, HairColor, FacialHairType, TopType, Color, MouthType, EyesType, EyebrowType, NoseType, AccessoriesType, ClotheType, ClotheGraphicType

from PIL import Image
import cairosvg
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver

import os
from django.conf import settings



# Create your models here.

# Making a custom user model. This is a multi role setup. 
class User(AbstractUser):
    # Creates a student field which is set to false by default
    is_student = models.BooleanField('student', default=False)
    # Creates a teacher field which is set to false by default
    is_teacher = models.BooleanField('teacher', default=False)

    # Creates a image field for storing the users avatar --- Note this ImageField must take a jpg or png.
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)


    # A funtion to generate avatars with deafult setting for the users intial profile
    def generate_default_avatar(self):
        avatar = PyAvataaar(
            style=AvatarStyle.CIRCLE,
            skin_color=SkinColor.LIGHT,
            hair_color=HairColor.BROWN,
            facial_hair_type=FacialHairType.DEFAULT,
            facial_hair_color=HairColor.BLACK,
            top_type=TopType.SHORT_HAIR_SHORT_FLAT,
            hat_color=Color.BLACK,
            mouth_type=MouthType.SMILE,
            eye_type=EyesType.DEFAULT,
            eyebrow_type=EyebrowType.DEFAULT,
            nose_type=NoseType.DEFAULT,
            accessories_type=AccessoriesType.DEFAULT,
            clothe_type=ClotheType.GRAPHIC_SHIRT,
            clothe_color=Color.HEATHER,
            clothe_graphic_type=ClotheGraphicType.BAT,
        )

        # Define path to save PNG file
        avatar_path = os.path.join(settings.MEDIA_ROOT, "avatars", f"avatar_{self.username}.png")

        # Ensure the avatars directory exists
        os.makedirs(os.path.dirname(avatar_path), exist_ok=True)

        # Render the avatar as a PNG file
        avatar.render_png_file(avatar_path)

        # Save the file path to the ImageField
        self.avatar.name = f"avatars/avatar_{self.username}.png"



    def __str__(self):
        role = "Student" if self.is_student else "Teacher" if self.is_teacher else "None"
        return f"{self.username} - {role}"



# Generate avatar when user is created
@receiver(post_save, sender=User)
def create_user_avatar(sender, instance, created, **kwargs):
    if created and not instance.avatar:  # Only generate if new user and no avatar set
        instance.generate_default_avatar()
        instance.save()


# This is a class model. It will create a class with a defined name , teacher, and access token (for the student to use to jon)
class Class(models.Model):
    # Name of class
    name = models.CharField(max_length=255)
    # The teacher who owns the class
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes')
    # access_token for students to join with 
    access_token = models.CharField(max_length=4, unique=True, editable=False)
    
    def __str__(self):
        return self.name


# Student model.Has a user isntance and a foreign key to the classroom they belong to
class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classrooms = models.ManyToManyField('Class', related_name='students')

    def __str__(self):
        return self.user.username


# This model is for createing "activities" for our games. This difference from freeplay as in the teacher can assign the number of levels they want complete
class Activity(models.Model):

    # Used to distinguish between games
    games = [
        ('matching', 'Matching Game'),
        ('memory', 'Memory Game'),
    ]

    # Name of the activity
    name = models.CharField(max_length=255) 
    # The description of hte game. not really used much. could probably delete 
    description = models.TextField(blank=True, null=True)  
    # THe students progress on the activity
    progress = models.IntegerField(default=0)  
    # THe studetn doing the activity
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activities')  
    # The url for the game
    url_name = models.CharField(max_length=50, blank=True, null=True)  
    # Checks if the game is completed or not
    completed = models.BooleanField(default=False)
    # The number of levles the teacher wants to assingn
    max_levels = models.IntegerField(default=1)  # Track max levels for this activity
    # THe game for the activity. deafult is the matching game
    game = models.CharField(max_length=20, choices=games, default='matching')
    
    classroom = models.ForeignKey(Class, on_delete=models.CASCADE)



    # Used to update a users progress on the game
    def update_progress(self, completed_levels):

        # used to make sure progress is updated completely
        self.progress = int((completed_levels / float(self.max_levels)) * 100)

    
     

        # If activiyt is > or = to the max levles it is completed so set true and progress 100
        if completed_levels >= self.max_levels:
            self.completed = True
            self.progress = 100  # Ensure it's fully completed

        # IF the completed is marked true, make sure progress is 100
        if self.completed:
            self.progress = 100
      

        # Save updates
        self.save()
        

    def __str__(self):
        return f"{self.name} - {self.student.user.username if self.student and self.student.user else 'Unassigned'}"


class ActivityTemplate(models.Model):
    classroom = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="activity_templates")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url_name = models.CharField(max_length=50, blank=True, null=True)
    max_levels = models.IntegerField(default=1)
    game = models.CharField(max_length=20, choices=Activity.games, default='matching')

    def __str__(self):
        return f"{self.name} for {self.classroom.name}"

# This models is for leaderboard entries. Has the user who made the points and the points made.
class LeaderboardEntry(models.Model):
    # Instance of the user. as in this is the user who has the points
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='leaderboard_entry')
    # The number of points stored
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.points} points"
    

class Badge(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='badges/')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    
    def __str__(self):
        return self.name 
    
class Notification(models.Model):
    title = models.CharField(max_length=255)  # The title of the notification
    message = models.TextField()  # The main content of the notification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")  # Link to the recipient
    date = models.DateTimeField(auto_now_add=True)  # Automatically set when the notification is created
    read = models.BooleanField(default=False)  # Whether the notification has been read

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"



# Stores the progress a user had made on a game. as in their mistakes mistmatched and time taken
class GameProgress(models.Model):

    games = [
        ('matching', 'Matching Game'),
        ('memory', 'Memory Game'),
    ]

    # 
    # A foreign key realted to the user. 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Keeps track of their level
    level = models.IntegerField()
    # The time it took to complete a level
    time_taken = models.FloatField()
    # The number of mistakes made
    mistakes = models.IntegerField()
    # The number of mismatches they had
    mismatched_letters = models.TextField()
    # The time they started
    timestamp = models.DateTimeField(auto_now_add=True)

    # Foreign key to activity. So we know what activity this progress is saving for
    activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.SET_NULL) 
    # Checks if it is free play. 
    is_free_play = models.BooleanField(default=True) 
    # Used to tell what game we are keeping progress of
    game = models.CharField(max_length=20, choices=games, default='matching')

    def __str__(self):
        return f"{self.user.username} - Level {self.level} ({'Free Play' if self.is_free_play else 'Activity'}) - {self.game}"
