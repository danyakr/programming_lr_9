import os
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Transaction
import django

# Устанавливаем настройки перед импортом моделей
os.environ['DJANGO_SETTINGS_MODULE'] = 'lab_9.settings'
django.setup()


class UserModelTest(TestCase):

    def setUp(self):
        """Создание тестового пользователя перед каждым тестом"""
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123", email="test@example.com"
        )

    def test_user_creation(self):
        """Проверяем создание пользователя"""
        user = get_user_model().objects.get(username="testuser")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(user.spending, 0.0)
        self.assertEqual(user.bonus_level, "Silver")
        self.assertEqual(user.cashback, 0.01)

    def test_update_bonus_level(self):
        """Проверяем обновление бонусного уровня в зависимости от трат"""
        self.user.spending = 6000  # Обновляем трату
        self.user.update_bonus_level()  # Применяем обновление
        self.assertEqual(self.user.bonus_level, "Platinum")
        self.assertEqual(self.user.cashback, 0.15)

        self.user.spending = 1200  # Обновляем трату
        self.user.update_bonus_level()  # Применяем обновление
        self.assertEqual(self.user.bonus_level, "Gold")
        self.assertEqual(self.user.cashback, 0.05)

        self.user.spending = 500  # Обновляем трату
        self.user.update_bonus_level()  # Применяем обновление
        self.assertEqual(self.user.bonus_level, "Silver")
        self.assertEqual(self.user.cashback, 0.01)


class TransactionModelTest(TestCase):

    def setUp(self):
        """Создание тестового пользователя и транзакций перед каждым тестом"""
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123", email="test@example.com"
        )
        self.transaction = Transaction.objects.create(
            user=self.user, amount=200
        )

    def test_transaction_creation(self):
        """Проверяем создание транзакции"""
        transaction = Transaction.objects.get(id=self.transaction.id)
        self.assertEqual(transaction.user.username, "testuser")
        self.assertEqual(transaction.amount, 200)
        self.assertIsNotNone(transaction.date)

    def test_user_spending_after_transaction(self):
        """Проверяем, что трат пользователя увеличивается после транзакции"""
        self.assertEqual(self.user.spending, 200)  # Проверяем, что траты пользователя увеличились
        self.assertEqual(self.user.bonus_level, "Silver")  # Траты меньше 1000, уровень "Silver"
        self.assertEqual(self.user.cashback, 0.01)

    def test_bonus_level_update_after_transaction(self):
        """Проверяем, что бонусный уровень обновляется после транзакции"""
        self.user.spending = 1000
        self.user.update_bonus_level()  # Ручное обновление
        self.assertEqual(self.user.bonus_level, "Gold")
        self.assertEqual(self.user.cashback, 0.05)

        # Добавим еще одну транзакцию
        Transaction.objects.create(user=self.user, amount=5000)
        self.user.refresh_from_db()  # Обновляем данные пользователя из базы
        self.assertEqual(self.user.bonus_level, "Platinum")
        self.assertEqual(self.user.cashback, 0.15)


class AuthAPITestCase(APITestCase):

    def setUp(self):
        """Создание тестового пользователя для авторизации"""
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123", email="test@example.com"
        )
        self.login_url = '/auth/login/'  # URL для получения токена

    def test_jwt_token(self):
        """Проверка получения JWT-токена"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'password123'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)  # Проверяем, что токен возвращен


class UserBonusAPITestCase(APITestCase):

    def setUp(self):
        """Создание тестового пользователя для проверки бонусов"""
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123", email="test@example.com"
        )
        self.client.login(username="testuser", password="password123")  # Вход пользователя
        self.bonus_url = '/users/bonus/'  # URL для получения бонусов

    def test_get_bonus(self):
        """Проверка получения информации о бонусах"""
        response = self.client.get(self.bonus_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['spending'], 0.0)  # Начальные траты
        self.assertEqual(response.data['bonus_level'], 'Silver')
        self.assertEqual(response.data['cashback'], 0.01)


class UserTransactionAPITestCase(APITestCase):

    def setUp(self):
        """Создание тестового пользователя для добавления транзакций"""
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123", email="test@example.com"
        )
        self.client.login(username="testuser", password="password123")  # Вход пользователя
        self.transaction_url = '/users/transactions/'  # URL для добавления транзакции

    def test_add_transaction(self):
        """Проверка добавления транзакции"""
        response = self.client.post(self.transaction_url, {
            'amount': 2000  # Сумма транзакции
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Transaction added successfully")
