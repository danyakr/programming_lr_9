from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    spending = models.FloatField(default=0.0)

    
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set", 
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set", 
        blank=True,
    )

    def update_bonus_level(self):
        """
        Обновляет бонусный уровень на основе текущих трат.
        """
        if self.spending >= 5000:
            self.bonus_level = "Platinum"
            self.cashback = 0.15
        elif self.spending >= 1000:
            self.bonus_level = "Gold"
            self.cashback = 0.05
        else:
            self.bonus_level = "Silver"
            self.cashback = 0.01
        self.save()


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
