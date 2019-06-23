from django.urls import path
from rango import views
from rango.views import ProfileView

urlpatterns = [
    path('', views.index, name = 'index'),
    path('about/', views.about, name = 'about'),
    path('category/<slug:category_name_slug>/', views.show_category, name = 'show_category'),
    path('add_category/', views.add_category, name = 'add_category'),
    path('category/<slug:category_name_slug>/add_page/', views.add_page, name = 'add_page'),
    path('restricted/', views.restricted, name='restricted'),
    path('goto/', views.goto_url, name = 'goto'),
    path('register_profile/', views.register_profile, name = 'register_profile'),
    path('profile/<username>/', ProfileView.as_view(), name='profile'),
]