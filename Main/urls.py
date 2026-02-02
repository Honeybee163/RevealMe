from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('riddle_generator', views.Riddle_Generator, name='Riddle_Generator'),
    path('reveal/<uuid:uuid>/', views.confirm_view, name='confirm'),
    path('confirm_link/', views.confirm_link, name='confirm_link'),

]