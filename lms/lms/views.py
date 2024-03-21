# views.py
from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import pandas as pd
from .models import User, Loan
from django.http import JsonResponse
from datetime import datetime, timedelta


admin.site.register(User)
admin.site.register(Loan)
def index(request):
    return render(request, 'index.html')


@csrf_exempt 
def registeruser(request):
    if request.method == 'POST':
        
        user_data = request.body.decode('utf-8')
        user_data=json.loads(user_data)
        errors =[]

        df = pd.read_csv(r"C:\Users\Akash Chauhan\OneDrive\Desktop\lms\lms\lms\data.csv")

        aadhar_id= user_data["Aadhar ID"]
        name= user_data["name"]
        email_id=user_data["email_id"]
        annual_income= user_data["annual_income"]
        user_df = df[df['user'] == aadhar_id]
        total_amount =0

        if not aadhar_id:
            errors.append('Aadhar ID is missing')

        unique_user_id = uuid.uuid4()

        for index, row in user_df.iterrows():
            if row["transaction_type"] == "CREDIT":
                total_amount= total_amount+row["amount"]
            else:
                total_amount=total_amount- row["amount"]

        credit_score=300
        if total_amount>=1000000:
            credit_score=900
        elif total_amount<= 100000:
            credit_score=300
        else:
            x= 1000000-total_amount
            y= x//15000
            if(x%15000):
                y=y+1

            credit_score= max(900-y,300)

        try:
            User.objects.create(
                aadhar_id=aadhar_id,
                name=name,
                email_id=email_id,
                annual_income=annual_income,
                unique_user_id=unique_user_id,
                credit_score=credit_score
            )
        except Exception as e:
            errors.append(str(e))
        
    
        if errors:
            return JsonResponse({'Error': '; '.join(errors)}, status=400)
        else:
            return JsonResponse({'Error': None, 'unique_user_id': str(unique_user_id)}, status=200)
    else:
        return JsonResponse({'Error': 'Invalid request method'}, status=400)
    
    


@csrf_exempt 
def applyloan(request):
    if request.method == 'POST':


        user_data = request.body.decode('utf-8')
        user_data=json.loads(user_data)

        print(user_data)

        uuid= user_data["uuid"]
        # credit_score= user_data["credit_score"]
        loan_type= user_data["loan_type"]
        # income= user_data["income"]
        loan_amount=float(user_data["loan_amount"])
        rate=float(user_data["rate"])
        time= int(user_data["period"])
        disbursement_date_str= user_data["disbursement_date"]

        disbursement_date = datetime.strptime(disbursement_date_str, '%Y-%m-%d')

        user = User.objects.get(unique_user_id= uuid)
        income= float(user.annual_income)
        credit_score= user.credit_score

        if credit_score<450:
            return JsonResponse({'Error': 'You are not eligible for loan due to less credit score'}, status=400)
        


        if income <= 150000:
            return JsonResponse({'Error': 'You are not eligible for loan due to less annual income'}, status=400)
        

        if (validate_loan_amount(loan_amount,loan_type)):
            return JsonResponse({'Error': 'Loan amouny is out of bounds.'}, status=400)


        
        monthly_income= income/12

        if rate<14:
            return HttpResponse("Interest rate should be higher than or equal to 14%")


        monthly_rate= rate/12
        monthly_rate=monthly_rate/100
        time_in_month=time*12
        
        k= ((1+monthly_rate)**time_in_month)/((1+monthly_rate)**(time_in_month-1))
        emi= (loan_amount*monthly_rate)*(k)


        if emi > (0.6*monthly_income):
            return JsonResponse({'Error': 'EMI is higher than 60 percent of your monthly income, try increasing duration or lower interest options.'}, status=400)
        
        profit= emi*time_in_month

        print(profit)

        if profit<100000:
            return JsonResponse({'Error': 'EMI not possible at this interest rate, Amount and Duration'}, status=400)
        
        due_dates = calculate_due_dates(emi, time, disbursement_date)

        loan = Loan.objects.create(
            unique_user_id= user,
            loan_type=loan_type,
            loan_amount=loan_amount,
            interest_rate=rate,
            term_period=time,
            disbursement_date=disbursement_date,
            emi=emi
        )
        response_data = {
            'Error': None,
            'Loan_id': loan.loan_id,
            'Due_dates': due_dates
        }

        return JsonResponse(response_data, status=200)
        
    else:
        return JsonResponse({'Error': 'Invalid request method'}, status=400)
    
def validate_loan_amount(loan_type, loan_amount):
    if loan_type == 'Car' and loan_amount > 750000:
        return True
    elif loan_type == 'Home' and loan_amount > 8500000:
        return True
    elif loan_type == 'Educational' and loan_amount > 5000000:
        return True
    elif loan_type == 'Personal' and loan_amount > 1000000:
        return True
    return False

def calculate_due_dates(emi, term_period, disbursement_date):
    due_dates = []
    for i in range(term_period*12):
        due_date = disbursement_date + timedelta(days=30 * (i + 1)) 
        due_dates.append({'Date': due_date.strftime('%Y-%m-%d'), 'Amount_due': emi})
    return due_dates
