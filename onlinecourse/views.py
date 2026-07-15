from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import logging

from .models import Course, Enrollment, Submission, Choice


logger = logging.getLogger(__name__)


# User registration
def registration_request(request):
    context = {}

    if request.method == 'GET':
        return render(
            request,
            'onlinecourse/user_registration_bootstrap.html',
            context
        )

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        if User.objects.filter(username=username).exists():
            context['message'] = "User already exists."
            return render(
                request,
                'onlinecourse/user_registration_bootstrap.html',
                context
            )

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        login(request, user)

        return redirect('onlinecourse:index')


# Login
def login_request(request):
    context = {}

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['psw']

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')

        context['message'] = "Invalid username or password."

    return render(
        request,
        'onlinecourse/user_login_bootstrap.html',
        context
    )


# Logout
def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


# Check enrollment
def check_if_enrolled(user, course):

    if not user.is_authenticated:
        return False

    return Enrollment.objects.filter(
        user=user,
        course=course
    ).exists()


# Course list page
class CourseListView(generic.ListView):

    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):

        courses = Course.objects.order_by(
            '-total_enrollment'
        )[:10]

        user = self.request.user

        for course in courses:
            course.is_enrolled = check_if_enrolled(
                user,
                course
            )

        return courses



# Course details page
class CourseDetailView(generic.DetailView):

    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'



# Enroll user
def enroll(request, course_id):

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    if request.user.is_authenticated:

        if not check_if_enrolled(request.user, course):

            Enrollment.objects.create(
                user=request.user,
                course=course,
                mode='honor'
            )

            course.total_enrollment += 1
            course.save()

    return HttpResponseRedirect(
        reverse(
            'onlinecourse:course_details',
            args=(course.id,)
        )
    )



# Submit exam
def submit(request, course_id):

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=course
    )

    submission = Submission.objects.create(
        enrollment=enrollment
    )

    answers = extract_answers(request)

    submission.choices.set(answers)

    return HttpResponseRedirect(
        reverse(
            'onlinecourse:exam_result',
            args=(
                course_id,
                submission.id
            )
        )
    )



# Extract answers
def extract_answers(request):

    submitted_answers = []

    for key in request.POST:

        if key.startswith('choice'):

            choice_id = int(request.POST[key])

            submitted_answers.append(
                choice_id
            )

    return Choice.objects.filter(
        id__in=submitted_answers
    )



# Exam result
def show_exam_result(request, course_id, submission_id):

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    submission = get_object_or_404(
        Submission,
        id=submission_id
    )

    selected_choices = submission.choices.all()

    total_score = 0

    for question in course.question_set.all():

        correct_choices = question.choice_set.filter(
            is_correct=True
        )

        selected = selected_choices.filter(
            question=question
        )

        if set(correct_choices) == set(selected):
            total_score += question.grade


    context = {
        'course': course,
        'grade': total_score,
        'choices': selected_choices
    }


    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        context
    )