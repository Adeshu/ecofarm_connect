import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai

from .models import ChatMessage

# Configure Gemini using the same pattern as EcoLearn:
# prefer GOOGLE_API_KEY but allow GEMINI_API_KEY as a fallback.
api_key = getattr(settings, "GOOGLE_API_KEY", "") or getattr(settings, "GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)


@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_message = (data.get("message") or "").strip()
    if not user_message:
        return JsonResponse({"error": "Message is required"}, status=400)

    if not api_key:
        return JsonResponse(
            {"error": "AI service not configured. Missing GOOGLE_API_KEY / GEMINI_API_KEY."},
            status=500,
        )

    try:
        # Same model and style as EcoLearn chat
        model = genai.GenerativeModel("gemini-2.5-flash")

        system_hint = (
            "You are a friendly sustainable farming assistant for EcoFarm Connect. "
            "Answer briefly (2–5 sentences), explain concepts clearly, and give "
            "practical, eco-friendly tips for farmers and learners."
        )
        prompt = f"{system_hint}\n\nUser question:\n{user_message}"

        chat = model.start_chat()
        response = chat.send_message(prompt)
        bot_reply = (getattr(response, "text", "") or "").strip()

        if not bot_reply:
            bot_reply = "Sorry, I couldn't generate a response right now. Please try again."

        # Save chat history for records
        ChatMessage.objects.create(user_message=user_message, bot_response=bot_reply)

        return JsonResponse({"reply": bot_reply})
    except Exception as exc:
        return JsonResponse(
            {
                "error": "AI chat failed",
                "details": str(exc),
            },
            status=500,
        )
