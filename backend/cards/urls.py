from django.urls import path
from .views import CardListCreateView, CardDetailDeleteView

urlpatterns = [
    path('', CardListCreateView.as_view(), name='card_list_create'),
    path('<int:id>/', CardDetailDeleteView.as_view(), name='card_delete'),
]