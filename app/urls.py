from django.urls import path

from . import views

app_name = "app"

urlpatterns = [
    path('', views.index, name="index"),
    path('accounts/login', views.Login.as_view(), name="login"),
    path('accounts/signup', views.Register.as_view(), name="register"),
    path('profile/<str:name>', views.profile, name="profile"),
    path('accounts/logout', views.logout_view, name="logout"),
    path('lessons/browse', views.browse, name="browse"),
    path('search', views.search, name="search"),
    path('lesson/<str:name>', views.lesson, name="lesson"),
    path('lesson/new/create', views.CreateLesson.as_view(), name="create"),
    path('try/ide', views.IDE.as_view(), name="ide"),
    path('contact', views.Contact.as_view(), name="contact"),
]
