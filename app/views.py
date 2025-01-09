from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, Transaction
from .serializers import UserBonusSerializer, TransactionSerializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import status




class BonusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Возвращает текущий уровень бонусов пользователя.
        """
        user = request.user
        user.update_bonus_level()
        serializer = UserBonusSerializer(user)
        return Response(serializer.data)


class TransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Добавляет новую транзакцию и обновляет траты пользователя.
        """
        user = request.user
        amount = request.data.get("amount")
        if not amount:
            return Response({"error": "Amount is required"}, status=400)

        # Создание транзакции
        Transaction.objects.create(user=user, amount=amount)
        user.spending += float(amount)
        user.update_bonus_level()
        return Response({"message": "Transaction added successfully"})

class LoginView(APIView):
    """
    Эндпоинт для аутентификации пользователя и получения AccessToken.
    """

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # Проверка пользователя
        user = authenticate(username=username, password=password)
        if user is not None:
            # Генерация AccessToken
            access_token = AccessToken.for_user(user)
            return Response(
                {
                    "access": str(access_token),
                }
            )
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
