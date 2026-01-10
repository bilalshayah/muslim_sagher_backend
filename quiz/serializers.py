from rest_framework import serializers
from .models import Question, AnswerChoice, UserQuizAttempt

#عرض الخيارات للطفل من دون معرفة الاجابة الصحيحية
class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ["id", "text"]


#عرض الخيار للآدمن  لاي سؤال ينتمي وهل هو الغجابة الصحيحة أم لا
class AnswerChoiceAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ["id", "text", "is_correct", "question"]


#عرض السؤال للطفل مع الخيارات المتعلقة به
class QuestionSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "choices"]


#عرض السؤال للآدمن وهذا السؤال تابع لأي فيديو
class QuestionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text", "video"]

#عرض اسئلة الفيديو مع الخيارات لكل سؤال واي اجابة هي الصحيحة
class QuestionWithChoicesAdminSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceAdminSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "video", "choices"]

#ارجاع اجاابات الطفل كل سؤال مع رقم الخيار الذي تم اختياره

class SubmitQuizAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()


class SubmitQuizSerializer(serializers.Serializer):
    answers = SubmitQuizAnswerSerializer(many=True)

#عرض نتيجة الاختبار
class QuizResultSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = UserQuizAttempt
        fields = ["id", "video", "score", "completed"]


