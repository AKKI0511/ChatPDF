from .views import generate_pdf, ConversationDetailView, ConversationListCreateView
from django.urls import path

urlpatterns = [
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
]