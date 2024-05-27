from django.contrib import admin
from .models import Conversation, PDF

class PDFInline(admin.TabularInline):
    model = PDF
    extra = 0

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    inlines = [PDFInline]

class PDFAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'description', 'pdf_url', 'created_at')
    search_fields = ('description',)

admin.site.register(Conversation, ConversationAdmin)
admin.site.register(PDF, PDFAdmin)
