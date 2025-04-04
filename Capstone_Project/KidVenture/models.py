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



    def generate_default_avatar(self):
        """Generate a default avatar and save it to the user's profile."""
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



class Class(models.Model):
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes')
    access_token = models.CharField(max_length=4, unique=True, editable=False)
    
    def __str__(self):
        return self.name



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    classroom = models.ForeignKey(Class,  on_delete=models.CASCADE, related_name='students')

    def __str__(self):
         return self.user.username if self.user else "Unassigned Student"

class Activity(models.Model):

    GAME_CHOICES = [
        ('matching', 'Matching Game'),
        ('memory', 'Memory Game'),
    ]

    name = models.CharField(max_length=255)  
    description = models.TextField(blank=True, null=True)  
    progress = models.IntegerField(default=0)  
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activities')  
    url_name = models.CharField(max_length=50, blank=True, null=True)  
    completed = models.BooleanField(default=False)
    max_levels = models.IntegerField(default=1)  # Track max levels for this activity
    game_type = models.CharField(max_length=20, choices=GAME_CHOICES, default='matching')


    def update_progress(self, completed_levels):
        """Update activity progress based on completed levels"""
        # Ensure progress is updated correctly
        self.progress = int((completed_levels / float(self.max_levels)) * 100)

    
     

        # Check if activity is completed
        if completed_levels >= self.max_levels:
            self.completed = True
            self.progress = 100  # Ensure it's fully completed

        if self.completed:
            self.progress = 100
      

        # Save updates
        self.save()

    def __str__(self):
        return f"{self.name} - {self.student.user.username if self.student and self.student.user else 'Unassigned'}"

    
class LeaderboardEntry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='leaderboard_entry')
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

class GameProgress(models.Model):

    GAME_CHOICES = [
        ('matching', 'Matching Game'),
        ('memory', 'Memory Game'),
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.IntegerField()
    time_taken = models.FloatField()
    mistakes = models.IntegerField()
    mismatched_letters = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.SET_NULL) 
    is_free_play = models.BooleanField(default=True) 
    game_type = models.CharField(max_length=20, choices=GAME_CHOICES, default='matching')

    def __str__(self):
        return f"{self.user.username} - Level {self.level} ({'Free Play' if self.is_free_play else 'Activity'}) - {self.game_type}"
