from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.

# Making a custom user model. This is a multi role setup. 
class User(AbstractUser):
    # Creates a student field which is set to false by default
    is_student = models.BooleanField('student', default=False)
    # Creates a teacher field which is set to false by default
    is_teacher = models.BooleanField('teacher', default=False)

    def __str__(self):
        role = "Student" if self.is_student else "Teacher" if self.is_teacher else "None"
        return f"{self.username} - {role}"


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
    name = models.CharField(max_length=255)  # Name of the activity
    description = models.TextField(blank=True, null=True)  # Optional description
    progress = models.IntegerField(default=0)  # Progress percentage (0-100)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activities')  # Link to a student
    url_name = models.CharField(max_length=50, blank=True, null=True)  # URL name for activity navigation
    completed = models.BooleanField(default=False)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_progress')  # Link to the user
    level = models.IntegerField(default=1) # The level of the game
    time_taken = models.IntegerField(default=0)  # Time in seconds
    mistakes = models.IntegerField(default=0) # Number of mistakes made
    mismatched_letters = models.TextField()  # Store as a JSON string
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set when the progress is created

    def __str__(self):
        return f"{self.user.username} - Level {self.level}"