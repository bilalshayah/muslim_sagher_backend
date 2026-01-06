from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Question, AnswerChoice, UserQuizAttempt


# ---------------------------------------------------------
# Inline لعرض الخيارات داخل صفحة السؤال
# ---------------------------------------------------------

class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 1
    fields = ("text", "is_correct")
    readonly_fields = ()
    show_change_link = True


# ---------------------------------------------------------
# Admin للسؤال
# ---------------------------------------------------------

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "video", "choices_count")
    search_fields = ("text",)
    list_filter = ("video",)
    inlines = [AnswerChoiceInline]

    def choices_count(self, obj):
        return obj.choices.count()
    choices_count.short_description = "عدد الخيارات"


# ---------------------------------------------------------
# Admin للخيارات
# ---------------------------------------------------------

@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "question", "is_correct")
    list_filter = ("is_correct", "question")
    search_fields = ("text",)

    # تلوين الإجابة الصحيحة داخل الـ admin
    def colored_is_correct(self, obj):
        return "✔️ صحيح" if obj.is_correct else "❌ خطأ"
    colored_is_correct.short_description = "هل هو صحيح؟"


# ---------------------------------------------------------
# Admin لمحاولات الطفل
# ---------------------------------------------------------

@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "video", "score", "completed")
    list_filter = ("completed", "video")
    search_fields = ("user__username",)