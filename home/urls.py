from django.urls import path
from django.conf.urls.static import static
from . import views


urlpatterns = [
   path('cpi', views.cpipage, name='cpipage'),
   path('',views.home, name='home'),
   path('registerCampusPartner/', views.registerCampusPartner, name='registerCampusPartner'),
   path('registerCampusPartnerUser/', views.registerCampusPartnerUser, name='registerCampusPartnerUser'),
   path('uploadProject/', views.uploadProject, name='uploadProject'),
   path('uploadCommunity/', views.uploadCommunity, name='uploadCommunity'),
   path('uploadCampus/', views.uploadCampus, name='uploadCampus'),
]
