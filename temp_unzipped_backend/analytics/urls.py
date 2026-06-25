from django.urls import path
from .views import AdminAnalyticsView, DoctorAnalyticsView

urlpatterns = [
    path('dashboard/', AdminAnalyticsView.as_view(), name='admin-analytics-dashboard'),
    path('doctor/', DoctorAnalyticsView.as_view(), name='doctor-analytics'),
]

