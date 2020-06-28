from django.urls import path
from . import views

#from .views import  base,ChartData

urlpatterns = [
   #path('', views.base, name='dashboard-base'),
   path('', views.functionselection, name='dashboard-functionselection'),
   path('ajax/load-functiondetails/', views.load_functiondetails, name='ajax_load_functiondetails'),  # <-- this one here
  # path('ajax/load-/', views.load_managers, name='ajax_load_managers'),  # <-- this one here

]
