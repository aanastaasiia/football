from django.shortcuts import render
import requests
import sqlite3
from .models import Users

connection = sqlite3.connect('users.db')
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS User (
username TEXT NOT NULL PRIMARY KEY,
password TEXT NOT NULL,
admin TEXT NOT NULL,
icon BLOB          
)
''')
connection.commit()


def registration(request):
    return render(request=request, template_name='register.html')
    

def sendform(request):
    name = str(request.POST.get('username'))
    password = str(request.POST.get('password'))
    admin = False
    cookie = '{}'
    cursor.execute('INSERT INTO User (username, password, admin, icon) VALUES (?, ?, ?, ?)', (name, password, admin, cookie))
    return render(request=request, template_name='mainpage.html' )