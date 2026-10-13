from django.contrib import admin
from django.urls import path, include
from accounts.views import UserProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/me/', UserProfileView.as_view(), name='user_profile'),
    path('api/auth/', include('accounts.urls')),
    path('api/cards/', include('cards.urls')),
]