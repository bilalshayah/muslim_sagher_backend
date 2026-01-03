from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# -----------------------------
# Unified Response Schemas
# -----------------------------
SUCCESS_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
        "message": openapi.Schema(type=openapi.TYPE_STRING, example="تمت العملية بنجاح"),
        "data": openapi.Schema(type=openapi.TYPE_OBJECT),
    }
)

ERROR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
        "message": openapi.Schema(type=openapi.TYPE_STRING, example="حدث خطأ"),
        "data": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            additional_properties=openapi.Schema(type=openapi.TYPE_STRING)
        )
    }
)

DEFAULT_RESPONSES = {
    200: openapi.Response("نجاح", SUCCESS_SCHEMA),
    201: openapi.Response("تم الإنشاء", SUCCESS_SCHEMA),
    400: openapi.Response("خطأ في البيانات", ERROR_SCHEMA),
    401: openapi.Response("غير مصرح", ERROR_SCHEMA),
    404: openapi.Response("غير موجود", ERROR_SCHEMA),
}

# -----------------------------
# Decorator موحد لكل الـ APIs
# -----------------------------
def auto_swagger(description=None, request_body=None, responses=None):
    """
    Decorator يضيف ردود Swagger موحدة لكل API
    ويمكن تخصيصها عند الحاجة
    """
    final_responses = DEFAULT_RESPONSES.copy()

    # إذا احتجتِ تخصيص API معين
    if responses:
        final_responses.update(responses)

    return swagger_auto_schema(
        operation_description=description,
        request_body=request_body,
        responses=final_responses
    )



