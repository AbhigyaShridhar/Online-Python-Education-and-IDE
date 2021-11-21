from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import User, Lesson, Message, Question
from .forms import CreateForm, QuestionForm
import sys

# Create your views here.
def index(request):
    return render(request, "app/index.html")

@login_required(login_url='/accounts/login/')
def profile(request, name):
    try:
        user = User.objects.get(username=name)
    except User.DoesNotExist:
        return HttpResponse("Query Does not Exist")

    lessons_completed = user.lessons
    completed = lessons_completed.count()
    lessons_authored = Lesson.objects.filter(owner=user)
    authored = lessons_authored.count()
    return render(request, "app/profile.html", {
        'user': user,
        'completed': completed,
        'authored': authored,
        'lessons_authored': lessons_authored,
        'lessons_completed': lessons_completed,
    })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("app:index"))

class Login(View):
    template = "app/login.html"
    success_url = 'app:profile'

    def get(self, request):
        return render(request, self.template, {
            #context
        })

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if not user is None:
            login(request, user)
            return HttpResponseRedirect(reverse(self.success_url, kwargs={'name': user.username}))

        return render(request, self.template, {
            'message': "Invalid ID or Password",
        })

class Register(View):
    template = "app/registration.html"
    success_url = "app:profile"

    def get(self, request):
        return render(request, self.template, {
            #context
        })

    def post(self, request):
        email = request.POST["email"]
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        p1 = request.POST["p1"]
        p2 = request.POST["p2"]

        if not p1 == p2:
            return render(request, self.template, {
                'message': "passwords don't match!",
            })

        if not email or not username or not first_name or not last_name or not p1:
            return render(request, self.template, {
                'message': "Please provide all required fields",
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=p1)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            login(request, user)
        except IntegrityError as e:
            print(e)
            return render(request, self.template, {
                "message": "An account with these credentials already exists..",
            })

        return HttpResponseRedirect(reverse(self.success_url, kwargs={'name': user.username}))

@login_required(login_url='/accounts/login/')
def browse(request):
    lessons = Lesson.objects.all()
    return render(request, "app/lessons.html", {
        'lessons': lessons,
    })

@login_required(login_url='/accounts/login/')
def search(request):
    query = request.POST['search_input']
    output = []
    lessons = Lesson.objects.all()
    for lesson in lessons:
        if query in lesson.content:
            output.append(poll)

    return render(request, "app/lessons.html", {
        'lessons': output,
        'count': len(output),
    })

@login_required(login_url='/accounts/login/')
def lesson(request, name):
  try:
    L = Lesson.objects.get(title=name)
  except Lesson.DoesNotExist:
    return render(request, "app/lessons.html", {
      'message': "Query Does not Exist.."
    })
  question = True
  try:
      q = Question.objects.get(lesson=L)
  except Question.DoesNotExist:
      question = False
      q = None

  done = False
  if L in request.user.lessons.all():
      done = True
  return render(request, "app/lesson.html", {
    'lesson': L,
    'form': QuestionForm(),
    'question': question,
    'q': q,
    'done': done,
  })

class CreateLesson(LoginRequiredMixin, View):
    login_url='/accounts/login/'
    template = "app/create-lesson.html"
    success_url = 'app:lesson'

    def get(self, request):
        return render(request, self.template, {
          'form': CreateForm(),
        })

    def post(self, request):
        form = CreateForm(request.POST)
        lesson = form.save(commit=False)
        lesson.owner = self.request.user
        if not form.is_valid():
            ctx = { 'form': CreateForm() }
            return render(request, self.template_name, ctx)
        lesson.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse(self.success_url, kwargs={'name': lesson.title}))

class Contact(View):
    template = "app/contact-us.html"

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        name = request.POST["name"]
        email = request.POST["email"]
        message = request.POST["message"]

        m = Message.objects.create(name=name, email=email, message=message)
        m.save()
        return render(request, self.template, {
            "message": "Thank you for contacting Us!!",
        })

class IDE(View):
    template = "app/ide.html"

    def get(self, request):
        return render(request, self.template, {
            "output": "Remember to add an extra space at the end of each line of input"
        })

    def post(self, request):
        code_part = request.POST['code_area']
        input_part = request.POST['input_area']
        y = input_part
        input_part = input_part.split("\n")
        for i in input_part:
            j = i
            i = i.split(" ")
        def input():
            return input_part
        try:
            orig_stdout = sys.stdout
            sys.stdout = open('file.txt', 'w')
            exec(code_part)
            sys.stdout.close()
            sys.stdout=orig_stdout
            output = open('file.txt', 'r').read()
        except Exception as e:
            sys.stdout.close()
            sys.stdout=orig_stdout
            output = e
        print(output)
        return render(request, self.template, {
            "code":code_part,
            "input":y,
            "output":output
            })

@login_required(login_url='/accounts/login/')
def add_question(request, id):
    try:
        lesson = Lesson.objects.get(id=id)
    except Lesson.DoesNotExist:
        return HttpResponse("Invalid Query")
    form = QuestionForm(request.POST)
    q = form.save(commit=False)
    q.lesson = lesson
    q.save()
    form.save_m2m()
    return HttpResponseRedirect(reverse('app:lesson', kwargs={'name': lesson.title}))

@login_required(login_url='/accounts/login/')
def complete(request, id):
    try:
        lesson = Lesson.objects.get(id=id)
        user = request.user
        user.lessons.add(lesson)
    except Lesson.DoesNotExist:
        return HttpResponse("Invalid Query")
    return HttpResponseRedirect(reverse('app:profile', kwargs={'name': user.username}))

class Solve(View):
    template = "app/ide.html"

    def get(self, request, id):
        try:
            l = Lesson.objects.get(id=id)
        except Lesson.DoesNotExist:
            return HttpResponse("Invalid Query")
        try:
            exp = Question.objects.get(lesson=l)
        except Question.DoesNotExist:
            return HttpResponse("Invalid Query")
        return render(request, self.template, {
            "output": "Remember to add an extra space at the end of each line of input",
            'out': True,
            'exp': exp,
            'lesson': l,
        })

    def post(self, request, id):
        try:
            l = Lesson.objects.get(id=id)
        except Lesson.DoesNotExist:
            return HttpResponse("Invalid Query")
        try:
            exp = Question.objects.get(lesson=l)
        except Question.DoesNotExist:
            return HttpResponse("Invalid Query")
        code_part = request.POST['code_area']
        input_part = request.POST['input_area']
        y = input_part
        input_part = input_part.split("\n")
        for i in input_part:
            j = i
            i = i.split(" ")
        def input():
            return input_part
        try:
            orig_stdout = sys.stdout
            sys.stdout = open('file.txt', 'w')
            exec(code_part)
            sys.stdout.close()
            sys.stdout=orig_stdout
            output = open('file.txt', 'r').read()
        except Exception as e:
            sys.stdout.close()
            sys.stdout=orig_stdout
            output = e
        #print(output)
        return render(request, self.template, {
            "code":code_part,
            "input":y,
            "output":output,
            'out': True,
            'exp': exp,
            'lesson': l,
            })
