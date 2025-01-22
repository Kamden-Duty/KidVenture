from django import forms #django model for managing forms
from django.contrib.auth.forms import UserCreationForm # Helps simply making sign up forms
from .models import User, Class, Student # The User model creatd in models.py



# Form for logging in
class LoginForm(forms.Form):
    
    # Charfield for holding the username
    username = forms.CharField(
        # Sets input type to text box
        widget = forms.TextInput (
            # Bootstrap adn css styling
            attrs = {
                "class": "form-control",
                "placeholder": "Username",  
                "id": "username", 
            }
        )
    )
    # Charfield for holding the password
    password = forms.CharField(
        # Sets input type to password
        widget = forms.PasswordInput(
            # Bootstrap and css styling
            attrs={
                "class": "form-control",
                "placeholder": "Password",
                "id": "password",
            }
        )
    )


# Form for signing up
class SignUpForm(UserCreationForm):

    # Charfield for holding the username
    username = forms.CharField(
         # Sets input type to text box
        widget = forms.TextInput (
            # Bootstrap and css styling
            attrs = {
                "class": "form-control",
                "placeholder": "Username",
                "id": "username",
            }
        )
    )
    # Emailfield for holding emails
    email = forms.EmailField(
        # Sets input type to email
        widget = forms.EmailInput (
            # Bootstrap and css styling
            attrs = {
                "class": "form-control",
                "placeholder": "Email",
                "id": "email",
            }
        )
    )
    
    # Charfield for holding the password
    password1 = forms.CharField(
        # Sets input type to password
        widget = forms.PasswordInput(
            # Bootstrap and css styling
            attrs={
                "class": "form-control",
                "placeholder": "Password",
                "id": "password1",
            }
        )

    )
    # Charfield for holding the password (used to confirm password)
    password2 = forms.CharField(
        # Sets input type to password
        widget = forms.PasswordInput(
            # Bootstrap and css styling
            attrs={
                "class": "form-control",
                "placeholder": "Confirm Password",
                "id": "password2",
            }
        )

    )

    # field for select the role . ie. Student or Teacher
    role_choices = (

        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    # Choicefield for holding the set role
    role = forms.ChoiceField(
        # Sets choices to our role choices we defined above
        choices=role_choices,
        # Sets type to forms.select (a dropdown menu)
        widget = forms.Select(
            # Bootstrap and css styling
            attrs = {
                "class": "form-control", 
                "id": "role",
            }
        ),

        # Lables the drop down 'role' (We can change it if we come up with a better name or something)
        label = "role"
    )

    # Overriding save to make sure student or teacher is updated in the model when someone signs up
    def save (self, commit=True):
        # Creates a instance of user but does not save
        user = super().save(commit = False)
        # Getting the values of the role field
        role = self.cleaned_data.get("role")

        # Sets student field to true if role is student
        if role == "student":
            user.is_student = True
            user.is_teacher = False

        # Sets teacher field to true if role is teacher
        elif role == "teacher":
            user.is_student = False
            user.is_teacher = True
        
        # if commit is true, save the user
        if commit: 
            user.save()
        
        # returns the user object
        return user

    # Setting what model and fields to have in the form
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")


    




class CreateClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name']


