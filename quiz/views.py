from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from utils.swagger import auto_swagger
from person.permissions import IsAdmin

from points.models import UserPoints
from .models import Question, AnswerChoice, UserQuizAttempt
from .serializers import (
    QuestionSerializer,
    AnswerChoiceSerializer,
    QuestionAdminSerializer,
    AnswerChoiceAdminSerializer,
    SubmitQuizSerializer,
    QuestionWithChoicesAdminSerializer
)


# ---------------------------------------------------------
# 1) APIs الخاصة بالطفل (User-facing)
# ---------------------------------------------------------

class VideoQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    @auto_swagger(description="جلب أسئلة الفيديو مع الخيارات")
    def get(self, request, video_id):
        # منع إعادة الاختبار
        if UserQuizAttempt.objects.filter(user=request.user, video_id=video_id).exists():
            return Response({
                "status": "error",
                "message": "لقد أكملت الاختبار مسبقًا",
                "data": None
            }, status=400)

        questions = Question.objects.filter(video_id=video_id)[:5]
        serializer = QuestionSerializer(questions, many=True)

        return Response({
            "status": "success",
            "message": "تم جلب الأسئلة",
            "data": serializer.data
        })


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="إرسال إجابات الطفل وحساب النتيجة",
        request_body=SubmitQuizSerializer
    )
    def post(self, request, video_id):

        # منع إعادة الاختبار
        if UserQuizAttempt.objects.filter(user=request.user, video_id=video_id).exists():
            return Response({
                "status": "error",
                "message": "لا يمكنك إعادة الاختبار",
                "data": None
            }, status=400)

        serializer = SubmitQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers = serializer.validated_data["answers"]

        # عدد أسئلة الفيديو
        questions_count = Question.objects.filter(video_id=video_id).count()

        if questions_count == 0:
            return Response({
                "status": "error",
                "message": "لا يوجد أسئلة لهذا الفيديو",
                "data": None
            }, status=400)

        # قيمة النقطة الواحدة
        point_value = 10 / questions_count

        correct_answers = 0
        detailed_results = []

        for ans in answers:
            q_id = ans.get("question_id")
            c_id = ans.get("choice_id")

            try:
                choice = AnswerChoice.objects.get(id=c_id, question_id=q_id)
                is_correct = choice.is_correct

                if is_correct:
                    correct_answers += 1

                detailed_results.append({
                    "question_id": q_id,
                    "selected_choice": c_id,
                    "is_correct": is_correct
                })

            except AnswerChoice.DoesNotExist:
                detailed_results.append({
                    "question_id": q_id,
                    "selected_choice": c_id,
                    "is_correct": False
                })

        # حساب النقاط النهائية
        score = correct_answers * point_value

        # شرط النجاح: يجب أن تكون النقاط 6 أو أكثر
        points_added = 0
        if score >= 6:
            points_added = score

            # إضافة النقاط الكلية
            user_points, _ = UserPoints.objects.get_or_create(user=request.user)
            user_points.total_points += points_added
            user_points.save()

        # حفظ المحاولة
        UserQuizAttempt.objects.create(
            user=request.user,
            video_id=video_id,
            score=score,
            completed=True
        )

        return Response({
            "status": "success",
            "message": "تم إرسال الإجابات وحساب النتيجة",
            "data": {
                "correct_answers": correct_answers,
                "score": round(score, 2),
                "points_added": round(points_added, 2),
                "details": detailed_results
            }
        }, status=200)

       


# ---------------------------------------------------------
# 2) APIs الخاصة بالآدمن (Dashboard)
# ---------------------------------------------------------

class QuestionCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @auto_swagger(
        description="إضافة سؤال جديد",
        request_body=QuestionAdminSerializer
    )
    def post(self, request):
        serializer = QuestionAdminSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()
            return Response({
                "status": "success",
                "message": "تم إنشاء السؤال",
                "data": QuestionAdminSerializer(question).data
            }, status=201)

        return Response({
            "status": "error",
            "message": "خطأ في البيانات",
            "data": serializer.errors
        }, status=400)


class QuestionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @auto_swagger(
        description="تعديل سؤال",
        request_body=QuestionAdminSerializer
    )
    def put(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        serializer = QuestionAdminSerializer(question, data=request.data, partial=True)

        if serializer.is_valid():
            question = serializer.save()
            return Response({
                "status": "success",
                "message": "تم تعديل السؤال",
                "data": QuestionAdminSerializer(question).data
            })

        return Response({
            "status": "error",
            "message": "خطأ في البيانات",
            "data": serializer.errors
        }, status=400)
    
    
    @auto_swagger(description="حذف سؤال")
    def delete(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        question.delete()

        return Response({
            "status": "success",
            "message": "تم حذف السؤال",
            "data": None
        })


class AnswerChoiceCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @auto_swagger(
        description="إضافة خيار لسؤال",
        request_body=AnswerChoiceAdminSerializer
    )
    def post(self, request):
        question_id = request.data.get("question")
        is_correct = request.data.get("is_correct", False)

        # لا أكثر من 3 خيارات
        if AnswerChoice.objects.filter(question_id=question_id).count() >= 3:
            return Response({
                "status": "error",
                "message": "لا يمكن إضافة أكثر من 3 خيارات لهذا السؤال",
                "data": None
            }, status=400)

        # لا أكثر من خيار صحيح واحد
        if is_correct:
            if AnswerChoice.objects.filter(question_id=question_id, is_correct=True).exists():
                return Response({
                    "status": "error",
                    "message": "يوجد خيار صحيح مسبقًا لهذا السؤال",
                    "data": None
                }, status=400)

        serializer = AnswerChoiceAdminSerializer(data=request.data)
        if serializer.is_valid():
            choice = serializer.save()
            return Response({
                "status": "success",
                "message": "تم إضافة الخيار",
                "data": AnswerChoiceAdminSerializer(choice).data
            }, status=201)

        return Response({
            "status": "error",
            "message": "خطأ في البيانات",
            "data": serializer.errors
        }, status=400)


class AnswerChoiceDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @auto_swagger(
        description="تعديل خيار",
        request_body=AnswerChoiceAdminSerializer
    )
    def put(self, request, pk):
        choice = get_object_or_404(AnswerChoice, pk=pk)

        # إذا تم تعديل خيار إلى صحيح، تأكد أنه الوحيد
        if request.data.get("is_correct") is True:
            if AnswerChoice.objects.filter(
                question=choice.question,
                is_correct=True
            ).exclude(id=choice.id).exists():
                return Response({
                    "status": "error",
                    "message": "يوجد خيار صحيح آخر لهذا السؤال",
                    "data": None
                }, status=400)

        serializer = AnswerChoiceAdminSerializer(choice, data=request.data, partial=True)

        if serializer.is_valid():
            choice = serializer.save()
            return Response({
                "status": "success",
                "message": "تم تعديل الخيار",
                "data": AnswerChoiceAdminSerializer(choice).data
            })

        return Response({
            "status": "error",
            "message": "خطأ في البيانات",
            "data": serializer.errors
        }, status=400)

    @auto_swagger(description="حذف خيار")
    def delete(self, request, pk):
        choice = get_object_or_404(AnswerChoice, pk=pk)
        choice.delete()

        return Response({
            "status": "success",
            "message": "تم حذف الخيار",
            "data": None
        })
#عرض الأسئلة للفيديو مع الخيارات والاجابة الصحيحة
class AdminVideoQuestionsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @auto_swagger(description="جلب أسئلة الفيديو مع الخيارات والإجابة الصحيحة (للآدمن)")
    def get(self, request, video_id):
        questions = Question.objects.filter(video_id=video_id)
        serializer = QuestionWithChoicesAdminSerializer(questions, many=True)

        return Response({
            "status": "success",
            "message": "تم جلب الأسئلة مع الخيارات",
            "data": serializer.data
        })