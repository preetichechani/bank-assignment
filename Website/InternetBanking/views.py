import datetime
import io
from decimal import Decimal

import xlwt
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . models import User, Account , TransactionHistory
from . serializer import userSerializer,accountSerializer , TransactionHistorySerializer
from django.template import loader
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
import json

def home(request):
    template = loader.get_template('home_page.html')
    context = { }
    return HttpResponse(template.render(context,request))

def get_user_template(request):
    template = loader.get_template('user.html')
    context = { }
    return HttpResponse(template.render(context, request))

def add_user_template(request):
    template = loader.get_template('add_new_user.html')
    context = { }
    return HttpResponse(template.render(context, request))

def excel_template(request):
    template = loader.get_template('generate_excel.html')
    account = Account.objects.all();
    context = { 'ac' : account}
    return HttpResponse(template.render(context, request))

class UsersView(APIView):
    #api_view(["GET"])
    #@csrf_exempt
    #@permission_classes([IsAuthenticated])
    def get(self,request):
        user_data: object = User.objects.all()
        serializer = userSerializer(user_data,many=True)
        return JsonResponse({'user_data': serializer.data}, safe=False, status=status.HTTP_200_OK)

    def post(self,request):
        user = User()
        try:
            user.username = request.data.get('username')
            user.email = request.data.get('email')
            user.contact_no = request.data.get('contact_no')
            user.gender = request.data.get('gender')
            user.save()
            serializer = userSerializer(user)
            return JsonResponse({'user_data':serializer.data }, safe=False, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something went wrong'}, safe=False,
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class UserView(APIView):

    def put(self,request,id):
        user = User.objects.filter(pk=id).first()
        try:
            user.username = request.data.get('username')
            user.email = request.data.get('email')
            user.contact_no = request.data.get('contact_no')
            user.gender = request.data.get('gender')
            user.save()
            serializer = userSerializer(user)
            return JsonResponse({'user_data': serializer.data}, safe=False, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something went wrong'}, safe=False,
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self,request,id):
        user = User.objects.filter(pk=id).first()
        try:
            user.delete()
            return Response({'Message': 'User deleted'},status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something went wrong'}, safe=False,
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def get(self,request,id):
        try:
            user: object = User.objects.get(pk=id)
            serializer = userSerializer(user)
            return JsonResponse({'user': serializer.data}, safe=False, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something went wrong'}, safe=False,
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class AccountsView(APIView):

    def get(self,request):
        account_data: object = Account.objects.all()
        serializer = accountSerializer(account_data, many=True)
        # return Response(serializer.data)
        return JsonResponse({'account_data': serializer.data}, safe=False, status=status.HTTP_200_OK)

    def post(self,request):
        try:
            user = User.objects.get(pk=request.data.get('user'))
            serializer = accountSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            return JsonResponse({'account_data':serializer.data }, safe=False, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something went wrong'}, safe=False,
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class AccountView(APIView):

    def put(self,request,id):
        account = Account.objects.filter(pk=id).first()
        transaction = TransactionHistory()
        try:
            if request.data.get('action')=='Withdraw':
                amount = request.data.get('amount')
                if Decimal(account.total_balance)-Decimal(amount) > 0:
                    transaction.credit = amount
                    transaction.account = Account.objects.get(pk=id)
                    transaction.debit = '00.00'
                    account.total_balance = Decimal(account.total_balance)-Decimal(amount)
                    account.save()
                    transaction.save()
                    subject='Transaction'
                    message = 'Amount Withdraw Successfully from your account'
                    user = User.objects.get(pk=account.id)
                    email_from  = settings.EMAIL_HOST_USER
                    to_list = [user.email]
                    send_mail(subject,message,email_from ,to_list)
                else:
                    return JsonResponse({'error': 'Insufficient Balance'}, safe=False, status=status.HTTP_400_BAD_REQUEST)
            elif request.data.get('action')=='Deposit':
                amount = request.data.get('amount')
                transaction.debit = amount
                transaction.account = Account.objects.get(pk=id)
                transaction.credit = '00.00'
                account.total_balance = Decimal(account.total_balance)+Decimal(amount)
                account.save()
                transaction.save()
                subject = 'Transaction'
                message = 'Amount Deposit Successfully to your account'
                user = User.objects.get(pk=account.id)
                email_from = settings.EMAIL_HOST_USER
                to_list = [user.email]
                send_mail(subject, message, email_from, to_list)
            elif request.data.get('action')=='Deactivate':
                user_status = request.data.get('is_active')
                account.is_active = user_status
                account.save()
            elif request.data.get('action')=='Activate':
                user_status = request.data.get('is_active')
                account.is_active = user_status
                account.save()
            else:
                return JsonResponse({'error': 'No Such Action..'}, safe=False, status=status.HTTP_404_NOT_FOUND)
            serializer = accountSerializer(account)
            return JsonResponse({'Message': 'Transaction Successful. Email Sent to your email id'}, safe=False, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Something went wrong'}, safe=False,
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self,request,id):
        account = Account.objects.filter(pk=id).first()
        try:
            account.delete()
            return Response({'Message': 'Account deleted'},status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Something went wrong'}, safe=False,
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def get(self,request,id):
        try:
            account: object = Account.objects.get(pk=id)
            serializer = accountSerializer(account)
            return JsonResponse({'account': serializer.data}, safe=False, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something went wrong'}, safe=False,
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class TransactionView(APIView):
    def get(self,request):
        user_data: object = TransactionHistory.objects.all()
        serializer = TransactionHistorySerializer(user_data,many=True)
        return JsonResponse({'user_data': serializer.data}, safe=False, status=status.HTTP_200_OK)


#Writing Data To Excel
def export_user_xls(request):
    output = io.BytesIO()
    #response = HttpResponse(content_type='application/ms-excel')
    #response['Content-Disposition'] = 'attachment; filename="users.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Transaction History Data')  # this will make a sheet named Users Data
    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Debit', 'Credit','Account Number']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)  # at 0 row 0 column

        # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    print(request)
    start_date = request.GET.get('start_date')
    #start_date1 = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    #print(start_date1)
    end_date = request.GET.get('end_date')
    #end_date1 = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    account_id = request.GET.get('account_id')
    #TransactionHistory.objects.filter(created_at__range=(start_date, end_date),account_id= account_id).all
    #rows = TransactionHistory.objects.filter(created_at__range=[start_date, end_date],account_id= account_id).all().values_list('debit', 'credit', 'account')
    #rows = TransactionHistory.objects.filter(account_id=account_id).all().values_list('debit', 'credit', 'account')
    rows = TransactionHistory.objects.all().values_list('debit', 'credit', 'account')
    print(rows.count())
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)


    filename = 'users.xls'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    wb.save(response)

    return response
