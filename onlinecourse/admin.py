from django.contrib import admin

from .models import (
    Course,
    Lesson,
    Instructor,
    Learner,
    Enrollment,
    Question,
    Choice,
    Submission,
)

# Register your models here.

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Enrollment)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Submission)