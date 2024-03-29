from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('login', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('add_record/', views.add_record, name='add_record'),
    path('record/<int:pk>', views.customer_record, name='record'),
    path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    path('update_record/<int:pk>', views.update_record, name='update_record'),
    path('take_pictures/<int:pk>', views.take_pictures, name='take_pictures'),
    path('live/', views.live, name='live'),
    path('test/', views.test, name='test'),
    path('camera/<int:pk>', views.camera, name='camera')
]
