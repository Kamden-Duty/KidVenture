from django.contrib import admin
from .models import User, Class, Student, LeaderboardEntry, Badge, Activity, Notification, GameProgress
# Register your models here.


admin.site.register(User)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Activity)
admin.site.register(LeaderboardEntry)
admin.site.register(Badge)
admin.site.register(Notification)
admin.site.register(GameProgress)