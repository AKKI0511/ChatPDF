from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ConversationSerializer, PDFSerializer, UserSerializer
from .models import Conversation, PDF
from .create_pdf.pdf_generator import generate_pdf_from_description
import json

# User registration
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# Create PDF based on user input text
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_pdf(request):
    data = json.loads(request.body)
    description = data.get('description', '')

    if not description:
        return JsonResponse({'error': 'Description cannot be empty'}, status=400)

    # Placeholder for actual PDF generation logic
    pdf_url = generate_pdf_from_description(description)
    if not pdf_url:
        return JsonResponse({'error': 'PDF generation failed'}, status=500)

    # Create or get an active conversation
    conversation, created = Conversation.objects.get_or_create(user=request.user)

    # Create PDF entry
    pdf_entry = PDF.objects.create(conversation=conversation, description=description, pdf_url=pdf_url)

    return JsonResponse({
        'pdfUrl': pdf_entry.pdf_url,
        'conversationId': conversation.id
    })

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Conversation, id=self.kwargs['pk'], user=self.request.user)
