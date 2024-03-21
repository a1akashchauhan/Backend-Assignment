from django.db import models
import uuid

class User(models.Model):
    aadhar_id = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    email_id = models.EmailField(max_length=100)
    annual_income = models.DecimalField(max_digits=10, decimal_places=2)
    unique_user_id = models.UUIDField(unique=True)
    credit_score = models.IntegerField()

    def __str__(self):
        return self.name

class Loan(models.Model):
    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unique_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=100)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_period = models.IntegerField()
    disbursement_date = models.DateField()
    emi = models.DecimalField(max_digits=12, decimal_places=2)
    

    def __str__(self):
        return f"Loan ID: {self.loan_id}, User: {self.unique_user_id}, Loan Type: {self.loan_type}"