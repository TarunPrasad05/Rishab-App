from django.db import models
from .manager import UserManager
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    phone_number = models.CharField(max_length=12, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.phone_number

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='menu_images/')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ManyToManyField('Category', related_name='item')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OrderModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    items = models.ManyToManyField('MenuItem', related_name='order', blank=True)
    order_user = models.ForeignKey(User, related_name='userinfo',on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    feedback = models.CharField(max_length=100,default="")
    def __str__(self):
        return f'Order: {self.created_on.strftime("%b %d %I: %M %p")}'