from django.shortcuts import render
from .serializers import AzkarSerializer,TitleWithAzkarSerializer,TitleSerializer,CreateAzkarSerializer
from .models import Azkar,AzkarCategory
from rest_framework.views import APIView
from utils.swagger import auto_swagger
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from person.permissions import IsAdmin
# Create your views here.

#انشاء فئة title  جديد
class CreateTitleView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]

    @auto_swagger(
        description="إضافة فئة أذكار جديدة",
        request_body=TitleSerializer,
        responses={201:TitleWithAzkarSerializer}
    )
    def post(self,request):
        serializer=TitleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status":"success",
                "message":"تم إضافة فئة أذكار جديدة",
                "data":serializer.data
            },status=status.HTTP_201_CREATED)
        return Response({
                "status":"error",
                "message":"البيانات غير صحيحية",
                "data":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST) 

#إضافة ذكر جديد ضمن فئة ذات ال id pk    
class CreateAzkarView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]

    @auto_swagger(
        description="إضافة ذكر جديد",
        request_body=CreateAzkarSerializer,
        responses={201:AzkarSerializer}

    )
    def post(self,request,pk):
        
        serializer=CreateAzkarSerializer(data=request.data)
        if serializer.is_valid():
            zikr = serializer.save(title_id=pk)
            return Response({
                "status":"success",
                "message":"تم إضافة ذكر جديد",
                "data":AzkarSerializer(zikr).data
            },status=status.HTTP_201_CREATED)
        return Response({
            "status":"error",
            "message":"بيانات غير صحيحة",
            "data":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)

class UpdateTitleView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]

    @auto_swagger(
        description="تعديل فئة",
        request_body=TitleSerializer,
        responses={200:TitleSerializer}
    )

    def put(self,request,pk):
        try:
            title=AzkarCategory.objects.get(id=pk)
        except AzkarCategory.DoesNotExist:
            return Response({
                "status":"error",
                "message":"الذكر غير موجود",
                
            },status=status.HTTP_404_NOT_FOUND)
        serializer=TitleSerializer(title,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status":"success",
                "message":"تم تعديل الفئة بنجاح",
                "data":serializer.data
            },status=status.HTTP_200_OK)
        return Response({
                "status":"error",
                "message":"بيانات غير صحيحة",
                "data":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)

        
#تعديل ذكر
class UpdateAzkarView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]

    @auto_swagger(
        description="نعديل الذكر",
        request_body=CreateAzkarSerializer,
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
        serializer=CreateAzkarSerializer(zikr,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status":"success",
                "message":"تم تعديل الذكر",
                "data":AzkarSerializer(zikr).data
            },status=status.HTTP_200_OK)
        return Response({
                "status":"error",
                "message":"بيانات غير صحيحة",
                "data":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)


#حذف فئة 
class DeleteTitleView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]
    @auto_swagger(
        description="حذف فئة أذكار",
    )
    def delete(self,request,pk):
        try:
            title=AzkarCategory.objects.get(id=pk)
        except AzkarCategory.DoesNotExist:
            return Response({
                "status":"error",
                "message":"الفئة غير موجودة",
                
            },status=status.HTTP_404_NOT_FOUND)
        title.delete()
        return Response({
            "status": "success",
            "message": "تم حذف الفئة بنجاح"
        }, status=status.HTTP_200_OK)


#حذف ذكر
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


#عرض فئات الاذكار 
class TitleListView(APIView):

    @auto_swagger(
        description="عرض فئات الأذكار",
        responses={200:TitleSerializer}

    )
    def get(self,request):
        title=AzkarCategory.objects.all()
        serializer=TitleSerializer(title,many=True)
        return Response({
            "status":"success",
            "message":"تم جلب جميع الفئات",
            "data":serializer.data
        },status=status.HTTP_200_OK)
    
#عرض أذكار الفئة id
class TitleDetailView(APIView):
    @auto_swagger(
        description="تم عرض أذكار الفئة id",
        responses={200:TitleWithAzkarSerializer}
    
    )
    def get(self,request,pk):
        try:
            title=AzkarCategory.objects.get(id=pk)
        except AzkarCategory.DoesNotExist:
            return Response({
                "status":"error",
                "message":"الفئة غير موجودة",
            },status=status.HTTP_404_NOT_FOUND)
        serializer=TitleWithAzkarSerializer(title)
        return Response({
            "status":"success",
            "message":"تم جلب الفئة بنجاح",
            "data":serializer.data
        },status=status.HTTP_200_OK)



