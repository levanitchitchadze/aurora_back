from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random

from aurora_back import settings

pending_otps = {}
@csrf_exempt
def send_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)
    email = data.get('username')
    password = data.get('password')
    print(request)
    user = authenticate(username=email, password=password)

    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    otp_code = str(random.randint(100000, 999999))
    pending_otps[email] = otp_code

    subject = 'Your Aurora Login Code'
    message = f'Your verification code is: {otp_code}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        send_mail(subject, message, email_from, recipient_list)
        return JsonResponse({"status": "success", "message": "OTP sent!"})

    except Exception as e:
        return JsonResponse({"error": f"Email failed: {str(e)}"}, status=500)


#
@csrf_exempt
def verify_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)
    email = data.get('username')
    otp = data.get('otp')

    if otp not in pending_otps[email]:
        return JsonResponse({"error": "Invalid OTP"}, status=401)
    else:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.you_received_jwt_token"
        pending_otps[email] = None
        return JsonResponse({
            "status": "success",
            "access": token,  # ეს არის შენი JWT
            "message": "Login successful"
        })

