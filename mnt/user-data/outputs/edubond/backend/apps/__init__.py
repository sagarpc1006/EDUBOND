"""
============================================================
  EduBond Backend – All App Code
  apps/community, marketplace, studyhub, hostel, chat
============================================================
"""

# ════════════════════════════════════════════════════════════
# apps/community/models.py
# ════════════════════════════════════════════════════════════
"""
from django.db import models
from django.conf import settings

TAG_CHOICES = [('general','General'),('roadmap','Roadmap'),('experience','Experience'),('tip','Tip'),('event','Event')]

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default='general')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at']
"""

# ════════════════════════════════════════════════════════════
# apps/community/views.py  (summary – full CRUD)
# ════════════════════════════════════════════════════════════
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Post.objects.all()
        tag = self.request.GET.get('tag')
        if tag: qs = qs.filter(tag=tag)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response({'liked': False, 'count': post.likes.count()})
        post.likes.add(request.user)
        return Response({'liked': True, 'count': post.likes.count()})

# apps/community/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet
router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
urlpatterns = [path('', include(router.urls))]
"""

# ════════════════════════════════════════════════════════════
# apps/marketplace/models.py
# ════════════════════════════════════════════════════════════
"""
from django.db import models
from django.conf import settings

CATEGORY_CHOICES = [('calculator','Calculator'),('books','Books'),('stationery','Stationery'),('electronics','Electronics'),('notes','Notes'),('other','Other')]
CONDITION_CHOICES = [('new','Like New'),('good','Good'),('used','Used')]

class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good')
    contact = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='products/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
"""

# ════════════════════════════════════════════════════════════
# apps/marketplace/views.py
# ════════════════════════════════════════════════════════════
"""
from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Product, ProductPhoto
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'category']
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = Product.objects.filter(is_available=True)
        if self.request.GET.get('category'):
            qs = qs.filter(category=self.request.GET['category'])
        return qs

    def perform_create(self, serializer):
        product = serializer.save(seller=self.request.user)
        for photo in self.request.FILES.getlist('photos'):
            ProductPhoto.objects.create(product=product, image=photo)
"""

# ════════════════════════════════════════════════════════════
# apps/studyhub/models.py
# ════════════════════════════════════════════════════════════
"""
from django.db import models
from django.conf import settings

TYPE_CHOICES = [('notes','Notes'), ('pyq','PYQ')]
YEAR_CHOICES = [('1','1st Year'),('2','2nd Year'),('3','3rd Year'),('4','4th Year')]
BRANCH_CHOICES = [('CSE','CSE'),('IT','IT'),('ECE','ECE'),('EE','EE'),('ME','ME'),('CE','CE'),('CH','CH')]
EXAM_CHOICES = [('mid','Mid-Sem'),('end','End-Sem'),('unit','Unit Test')]

class StudyMaterial(models.Model):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploads')
    title = models.CharField(max_length=300)
    subject = models.CharField(max_length=100)
    material_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES)
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    file = models.FileField(upload_to='studyhub/')
    exam_year = models.IntegerField(null=True, blank=True)   # For PYQs
    exam_type = models.CharField(max_length=10, choices=EXAM_CHOICES, blank=True)
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
"""

# ════════════════════════════════════════════════════════════
# apps/studyhub/views.py
# ════════════════════════════════════════════════════════════
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .models import StudyMaterial
from .serializers import StudyMaterialSerializer

class StudyMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = StudyMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = StudyMaterial.objects.all()
        for f in ['year', 'branch', 'material_type', 'subject']:
            if self.request.GET.get(f):
                qs = qs.filter(**{f: self.request.GET[f]})
        return qs

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        material = self.get_object()
        material.download_count += 1
        material.save(update_fields=['download_count'])
        return FileResponse(material.file.open(), as_attachment=True)
"""

# ════════════════════════════════════════════════════════════
# apps/hostel/models.py
# ════════════════════════════════════════════════════════════
"""
from django.db import models
from django.conf import settings

HOSTEL_TYPE = [('boys','Boys'), ('girls','Girls')]

class Hostel(models.Model):
    hostel_type = models.CharField(max_length=10, choices=HOSTEL_TYPE, unique=True)
    name = models.CharField(max_length=100)
    warden_name = models.CharField(max_length=100)
    warden_phone = models.CharField(max_length=15)
    warden_email = models.EmailField()
    total_rooms = models.IntegerField(default=0)
    occupied_rooms = models.IntegerField(default=0)
    fee_per_sem = models.CharField(max_length=50, blank=True)
    curfew_time = models.TimeField(null=True, blank=True)
    def __str__(self): return self.name
    @property
    def vacant_rooms(self): return self.total_rooms - self.occupied_rooms

class HostelPhoto(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='hostel/')
    caption = models.CharField(max_length=100, blank=True)

class HostelFAQ(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='faqs')
    question = models.TextField()
    answer = models.TextField(blank=True)
    asked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    answered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='answered_faqs')
    created_at = models.DateTimeField(auto_now_add=True)
"""

# ════════════════════════════════════════════════════════════
# apps/chat/models.py
# ════════════════════════════════════════════════════════════
"""
from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_create_room(cls, user1, user2):
        rooms = cls.objects.filter(participants=user1).filter(participants=user2)
        if rooms.exists():
            return rooms.first(), False
        room = cls.objects.create()
        room.participants.add(user1, user2)
        return room, True

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at']
"""

# ════════════════════════════════════════════════════════════
# apps/chat/consumers.py  (Django Channels WebSocket)
# ════════════════════════════════════════════════════════════
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group = f'chat_{self.room_id}'
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']
        msg = await self.save_message(user, data['message'])
        await self.channel_layer.group_send(self.room_group, {
            'type': 'chat_message',
            'message': data['message'],
            'sender_id': user.id,
            'sender_name': user.get_full_name(),
            'timestamp': msg.created_at.isoformat(),
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user, content):
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(room=room, sender=user, content=content)
"""
