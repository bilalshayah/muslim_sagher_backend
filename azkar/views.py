from django.shortcuts import render
from .serializers import AzkarSerializer
from .models import Azkar
from rest_framework.views import APIView
from utils.swagger import auto_swagger
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from person.permissions import IsAdmin
# Create your views here.

class CreateAzkarView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]

    @auto_swagger(
        description="إضافة ذكر جديد",
        request_body=AzkarSerializer,
        responses={200:AzkarSerializer}

    )
    def post(self,request):
        serializer=AzkarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status":"success",
                "message":"تم إضافة ذكر جديد",
                "data":serializer.data
            },status=status.HTTP_201_CREATED)
        return Response({
            "status":"error",
            "message":"بيانات غير صحيحة",
            "data":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)

class UpdateAzkarView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]

    @auto_swagger(
        description="نعديل الذكر",
        request_body=AzkarSerializer,
        responses={200:AzkarSerializer}

    )
    def put(self,request,pk):

        try:
            zikr=Azkar.objects.get(id=pk)
        except Azkar.DoesNotExist:
            return Response({
                "status":"error",
                "message":"الذكر غير موجود",
                
            },status=status.HTTP_404_NOT_FOUND)
        serializer=AzkarSerializer(zikr,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status":"success",
                "message":"تم تعديل الذكر",
                "data":serializer.data
            },status=status.HTTP_200_OK)
        return Response({
                "status":"error",
                "message":"بيانات غير صحيحة",
                "data":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
    
class DeleteAzkarView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]

    @auto_swagger(
        description="تم حذف الذكر بنجاح"
    )
    def delete(self,request,pk):
        try:
            zikr=Azkar.objects.get(id=pk)
        except Azkar.DoesNotExist:
            return Response({
                "status":"error",
                "message":"الذكر غير موجود",
                
            },status=status.HTTP_404_NOT_FOUND)
        zikr.delete()
        return Response({
            "status": "success",
            "message": "تم حذف الذكر بنجاح"
        }, status=status.HTTP_200_OK)

class AzkarListView(APIView):

    @auto_swagger(
        description="عرض الأذكار",
        responses={200:AzkarSerializer}

    )
    def get(self,request):
        azkar=Azkar.objects.all()
        serializer=AzkarSerializer(azkar,many=True)
        return Response({
            "status":"success",
            "message":"تم جلب جميع الأذكار",
            "data":serializer.data
        },status=status.HTTP_200_OK)
    
class ZikrDetailView(APIView):
    @auto_swagger(
        description="تم جلب الذكر id",
        responses={200:AzkarSerializer}
    
    )
    def get(self,request,pk):
        try:
            zikr=Azkar.objects.get(id=pk)
        except Azkar.DoesNotExist:
            return Response({
                "status":"error",
                "message":"الذكر غير موجود",
            },status=status.HTTP_404_NOT_FOUND)
        serializer=AzkarSerializer(zikr)
        return Response({
            "status":"success",
            "message":"تم جلب الذكر بنجاح",
            "data":serializer.data
        },status=status.HTTP_200_OK)



