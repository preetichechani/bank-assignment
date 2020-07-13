from django.contrib import admin
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


urlpatterns = [
    path('', views.home, name = 'home-page'),
    path('user/', views.get_user_template, name='user_view'),
    path('users/',views.UsersView.as_view()),
    path('user/<int:id>/',views.UserView.as_view()),
    path('user/add_new_user',views.add_user_template ,name='adding_user'),
    path('accounts/',views.AccountsView.as_view()),
    path('account/<int:id>/',views.AccountView.as_view()),
    path('transaction/excel/', views.excel_template,name='select_range' ),
    path('export/excel/', views.export_user_xls, name='export_excel'),
    path('transactions/',views.TransactionView.as_view()),
]