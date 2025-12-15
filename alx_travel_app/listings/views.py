from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Welcome to ALX Travel API"})
import uuid
import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Booking, Payment

CHAPA_HEADERS = {
    "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
    "Content-Type": "application/json",
}

@api_view(['POST'])
def initiate_payment(request):
    booking_id = request.data.get("booking_id")
    booking = Booking.objects.get(id=booking_id)

    tx_ref = str(uuid.uuid4())

    payload = {
        "amount": str(booking.total_amount),
        "currency": "ETB",
        "email": booking.user.email,
        "first_name": booking.user.first_name,
        "tx_ref": tx_ref,
        "callback_url": "http://127.0.0.1:8000/api/verify-payment/",
        "return_url": "http://127.0.0.1:8000/payment-success/",
        "customization": {
            "title": "Travel Booking Payment"
        }
    }

    response = requests.post(
        f"{settings.CHAPA_BASE_URL}/transaction/initialize",
        json=payload,
        headers=CHAPA_HEADERS
    )

    data = response.json()

    Payment.objects.create(
        booking=booking,
        transaction_id=tx_ref,
        amount=booking.total_amount
    )

    return Response({
        "payment_url": data["data"]["checkout_url"]
    })


@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.GET.get("tx_ref")
    payment = Payment.objects.get(transaction_id=tx_ref)

    response = requests.get(
        f"{settings.CHAPA_BASE_URL}/transaction/verify/{tx_ref}",
        headers=CHAPA_HEADERS
    )

    data = response.json()

    if data["status"] == "success":
        payment.status = "COMPLETED"
        payment.save()
        return Response({"message": "Payment successful"})
    else:
        payment.status = "FAILED"
        payment.save()
        return Response({"message": "Payment failed"})
