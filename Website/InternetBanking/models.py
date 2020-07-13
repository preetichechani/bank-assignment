from django.db import models

GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female')
    )
class User(models.Model):
    username =models.CharField(max_length=30)
    email =models.EmailField(unique=True,null=False,blank=False)
    contact_no = models.IntegerField(unique=True)
    gender =models.CharField(choices=GENDER_CHOICES,max_length=6)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class Account(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    total_balance = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account_number

class TransactionHistory(models.Model):
    debit = models.DecimalField(max_digits=12, decimal_places=2,blank=True,null=True)
    credit = models.DecimalField(max_digits=12, decimal_places=2,blank=True,null=True)
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
