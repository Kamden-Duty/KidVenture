from django.db import models
from django.contrib.auth.models import AbstractUser



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
