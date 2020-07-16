pip install django
pip install restframework
pip install xlwt
Migration commands : python manage.py migrate
python manage.py makemigrations InternetBanking
python manage.py sqlmigrate InternetBanking 0001
python manage.py runserver
User APIs : get , post ,put, delete,show.
Account APIs : get, post,put, delete, show.
TransactionHistory: get, export_user_xls
