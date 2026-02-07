from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from utils.swagger import auto_swagger
from rest_framework.permissions import IsAuthenticated
from person.permissions import IsAdmin
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Story, StoryPage
from .serializers import (
    StorySerializer,
    StoryPageSerializer,
    StoryPageCreateSerializer,
    StoryCreateSerializer

)

class StoryViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    queryset = Story.objects.all().order_by("-created_at")
    serializer_class = StorySerializer
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return StoryCreateSerializer
        return StorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "pages", "get_page"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    # -----------------------------
    # إنشاء قصة
    # -----------------------------
    @auto_swagger(
        description="إنشاء قصة جديدة",
        request_body=StoryCreateSerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    # -----------------------------
    # تعديل قصة
    # -----------------------------
    @auto_swagger(
        description="تعديل قصة",
        request_body=StorySerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    # -----------------------------
    # حذف قصة
    # -----------------------------
    @auto_swagger(
        description="حذف قصة",
        request_body=None
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # -----------------------------
    # عرض قصة واحدة (مع الصفحات)
    # -----------------------------
    @auto_swagger(
        description="عرض قصة كاملة مع الصفحات التابعة لها",
        request_body=None
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # -----------------------------
    # عرض كل القصص
    # -----------------------------
    @auto_swagger(
        description="عرض جميع القصص",
        request_body=None
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

   

    

    # -----------------------------
    # إنشاء صفحة جديدة داخل قصة
    # -----------------------------
    @action(detail=True, methods=["post"])
    @auto_swagger(
        description="إضافة صفحة جديدة داخل قصة",
        request_body=StoryPageCreateSerializer,
    )
    def add_page(self, request, pk=None):
        story = self.get_object()
        serializer = StoryPageCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(story=story)
            return Response({
                "status": "success",
                "message": "تم إضافة الصفحة بنجاح",
                "data": serializer.data
            })

        return Response(serializer.errors, status=400)

    # -----------------------------
    # عرض صفحات القصة
    # -----------------------------
    @action(detail=True, methods=["get"])
    @auto_swagger(description="عرض جميع صفحات القصة")
    def pages(self, request, pk=None):
        story = self.get_object()
        pages = story.pages.all()
        serializer = StoryPageSerializer(pages, many=True)
        return Response({
            "status": "success",
            "message": "تم جلب الصفحات",
            "data": serializer.data
        })

    # -----------------------------
    # عرض صفحة واحدة
    # -----------------------------
    @action(detail=True, methods=["get"], url_path="pages/(?P<page_id>[^/.]+)")
    @auto_swagger(description="عرض صفحة واحدة من القصة")
    def get_page(self, request, pk=None, page_id=None):
        story = self.get_object()
        page = story.pages.filter(id=page_id).first()

        if not page:
            return Response({"status": "error", "message": "الصفحة غير موجودة"}, status=404)

        serializer = StoryPageSerializer(page)
        return Response({
            "status": "success",
            "message": "تم جلب الصفحة",
            "data": serializer.data
        })

    # -----------------------------
    # تعديل صفحة
    # -----------------------------
    @action(detail=True, methods=["put"], url_path="pages/(?P<page_id>[^/.]+)")
    @auto_swagger(description="تعديل صفحة", request_body=StoryPageCreateSerializer)
    def update_page(self, request, pk=None, page_id=None):
        story = self.get_object()
        page = story.pages.filter(id=page_id).first()

        if not page:
            return Response({"status": "error", "message": "الصفحة غير موجودة"}, status=404)

        serializer = StoryPageCreateSerializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "تم تعديل الصفحة",
                "data": serializer.data
            })

        return Response(serializer.errors, status=400)

    # -----------------------------
    # حذف صفحة
    # -----------------------------
    @action(detail=True, methods=["delete"], url_path="pages/(?P<page_id>[^/.]+)")
    @auto_swagger(description="حذف صفحة")
    def delete_page(self, request, pk=None, page_id=None):
        story = self.get_object()
        page = story.pages.filter(id=page_id).first()

        if not page:
            return Response({"status": "error", "message": "الصفحة غير موجودة"}, status=404)

        page.delete()
        return Response({
            "status": "success",
            "message": "تم حذف الصفحة"
        })


