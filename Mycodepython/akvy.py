'''
Note: In order to run this program, there should be atleast one entry in admin
'''

import random
import re
import mysql.connector
import reportlab
import os
import yagmail
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

my_db = mysql.connector.connect(host= 'movie', user= 'root', password= 'Lado**1268', buffered= True, port= 3306)
my_cursor = my_db.cursor()

try:
    my_cursor.execute('create database movie_book')
    my_cursor.execute('use movie_book')
except:
    my_cursor.execute('use movie_book')

try:
    my_cursor.execute('create table Admin('
                      'Name varchar(20) NOT NULL, '
                      'Email varchar(30) NOT NULL, '
                      'Mob_No varchar(10), '
                      'Status varchar(15) default "Activated", '
                      'Password varchar(15) NOT NULL)')
except:
    pass
my_db.commit()

try:
    my_cursor.execute('create table Customer('
                      'Name varchar(20) NOT NULL,'
                      'Email varchar(30) NOT NULL,'
                      'Mob_No varchar(10) NOT NULL,'
                      'Status varchar(15) default "Activated",'
                      'Password varchar(15) NOT NULL)')
    my_cursor.execute('create table movie('
                      'Movie_ID int NOT NULL PRIMARY KEY AUTO_INCREMENT,'
                      'Movie_Name varchar(20) NOT NULL,'
                      'Show_Time varchar(30) NOT NULL,'
                      'Avail_Tickets varchar(30) NOT NULL,'
                      'Price varchar(6) NOT NULL)')
    my_cursor.execute('create table cust_book('
                      'Cust_Name varchar(30) NOT NULL,' 
                      'Cust_Email varchar(30) NOT NULL,'
                      'Movie_ID int NOT NULL,'
                      'Movie_Name varchar(20) NOT NULL,'
                      'Show_time varchar(30) NOT NULL,'
                      'Booked_Tickets int NOT NULL,'
                      'Total_Ticket_Price int NOT NULL,'
                      'Food_ID varchar(3) default "0",'
                      'Fd_Combo varchar(30) default "NO",'
                      'Fd_Quant varchar(6) default "0",'
                      'Fd_Price varchar(6) default "0",' 
                      'Total_Price int default "0")')
    my_cursor.execute('create table food('
                      'Food_ID int NOT NULL PRIMARY KEY AUTO_INCREMENT,'
                      'Food_Combo varchar(20) NOT NULL,'
                      'Price varchar(6) NOT NULL,'
                      'Avail_Quantity varchar(3) NOT NULL)')
except:
    pass

my_db.commit()

n = None
p = None


def view_booked_details(email):
    q1 = 'select exists(select * from cust_book where Cust_Email="%s")' % (email)
    my_cursor.execute(q1)
    result = my_cursor.fetchone()
    if result[0] == 0:
        print('Sorry....you have no bookings')
        flag = 0
    else:
        flag = 1
        qq = 'select Movie_ID,Movie_Name,Show_time,Booked_Tickets,Total_Ticket_Price,Total_Price,Food_ID from cust_book where Cust_Email=%s'
        my_cursor.execute(qq, (email,))
        rr = my_cursor.fetchone()

        print("\nMovie ID: {}"
              "\nMovie Name: {}"
              "\nShow Time: {}"
              "\nBooked Tickets: {}"
              "\nTotal Ticket Price: {}".format(rr[0], rr[1], rr[2], rr[3], rr[4]))

        qq1 = 'select Food_ID,Fd_Combo,Fd_Quant,Fd_Price from cust_book where Cust_Email=%s'
        my_cursor.execute(qq1, (email,))
        rr1 = my_cursor.fetchall()
        # print(rr1)
        for i in rr1:
            if i[0] != "0":
                print("\nFood ID: {}"
                      "\nFood Combo: {}"
                      "\nQuantity: {}"
                      "\nFood Price: {}".format(i[0], i[1], i[2], i[3]))
        print('\nTotal Price ', rr[5])
        return flag


def cancel_everything(email,name):
    view=view_booked_details(email)
    if view==1:
        inp=input('\nDo you want to cancel entire bookings [y/n]: ').lower()
        if inp=='y':
            otp=send_otp(email,name)
            print('\nOTP has been sent to {}'.format(email))
            inpp=input('\nEnter the OTP: ')
            if inpp.isdigit() and otp==int(inpp):
                qq='select Booked_Tickets, Fd_Quant, Food_ID,Movie_ID from cust_book where Cust_Email=%s'
                my_cursor.execute(qq,(email,))
                r1=my_cursor.fetchall()
                q1='select Avail_Tickets from movie where Movie_ID=%s'
                my_cursor.execute(q1,(r1[0][3],))
                re1=my_cursor.fetchone()
                quer1='update movie set Avail_Tickets=%s where Movie_ID=%s'
                my_cursor.execute(quer1,(str(int(re1[0])+int(r1[0][0])),r1[0][3]))
                my_db.commit()
                for i in r1:
                    if(i[2]!="0"):
                        qu2='select Avail_Quantity from food where Food_ID=%s'
                        my_cursor.execute(qu2,(i[2],))
                        re1=my_cursor.fetchone()
                        quer='update food set Avail_Quantity=%s where Food_ID=%s'
                        my_cursor.execute(quer,(str(int(re1[0])+int(i[1])),i[2]))
                        my_db.commit()
                qu='delete from cust_book where Cust_Email=%s'
                my_cursor.execute(qu,(email,))
                my_db.commit()
                print('\nYour Bookings successfully cancelled !!!. You will be refunded soon...!!!')
            else:
                print('\nInvalid OTP')
        elif inp=='n':
            pass
        else:
            print('\nInvalid option')


def cancel_ticket(email, name):
    view = view_booked_details(email)
    if view == 1:
        inp_val = input('\nEnter the number of tickets to cancel: ')
        que1 = 'select Booked_Tickets,Movie_ID,Total_Ticket_Price,Total_Price from cust_book where Cust_Email=%s'
        my_cursor.execute(que1, (email,))
        res1 = my_cursor.fetchone()
        one_tick = int(res1[2]) / int(res1[0])
        if inp_val.isdigit():
            if res1[0] == int(inp_val):
                inp1 = input(
                    '\nBy cancelling entire tickets, food order will be cancelled. Do you want to proceed? [y/n]: ').lower()
                if inp1 == 'y':
                    otp = send_otp(email, name)
                    print('OTP has been sent to {}'.format(email))
                    inpp = input('Enter the OTP: ')
                    if inpp.isdigit() and otp == int(inpp):
                        que3 = 'select Avail_Tickets from movie where Movie_ID=%s'
                        my_cursor.execute(que3, (res1[1],))
                        res2 = my_cursor.fetchone()
                        ad = int(res2[0]) + int(inp_val)
                        que4 = 'update movie set Avail_Tickets=%s where Movie_ID=%s'
                        my_cursor.execute(que4, (str(ad), res1[1]))
                        my_db.commit()
                        que5 = 'select Food_ID,Fd_Quant from cust_book where Cust_Email=%s'
                        my_cursor.execute(que5, (email,))
                        rs = my_cursor.fetchall()
                        for i in rs:
                            que6 = 'select Avail_Quantity from food where Food_ID=%s'
                            my_cursor.execute(que6, (i[0],))
                            rs1 = my_cursor.fetchone()
                            que7 = 'update food set Avail_Quantity=%s where Food_ID=%s'
                            my_cursor.execute(que7, (str(int(rs1[0]) + int(i[1])), i[0]))
                            my_db.commit()
                        que2 = 'delete from cust_book where Cust_Email=%s'
                        my_cursor.execute(que2, (email,))
                        my_db.commit()
                        print(
                            '\nYour entire ticket booking is cancelled so, your food order is also cancelled. You will be refunded soon !!!')
                    else:
                        print('\nInvalid OTP')
                elif inp1 == 'n':
                    pass
                else:
                    print("\nInvalid Option")

            elif int(inp_val) < res1[0]:
                otp = send_otp(email, name)
                print('OTP has been sent to your mail')
                inpp = input('Enter the OTP: ')
                if inpp.isdigit() and otp == int(inpp):
                    co = int(inp_val) * one_tick
                    que2 = 'update cust_book set Booked_Tickets=%s, Total_Ticket_Price=%s,Total_Price=%s where Cust_Email=%s'
                    my_cursor.execute(que2,
                                      (res1[0] - int(inp_val), str(int(res1[2]) - co), str(int(res1[3]) - co), email,))
                    my_db.commit()
                    que3 = 'select Avail_Tickets from movie where Movie_ID=%s'
                    my_cursor.execute(que3, (res1[1],))
                    res2 = my_cursor.fetchone()
                    ad = int(res2[0]) + int(inp_val)
                    que4 = 'update movie set Avail_Tickets=%s where Movie_ID=%s'
                    my_cursor.execute(que4, (str(ad), res1[1]))
                    my_db.commit()
                    print('Selected number of tickets cancelled. You will be refunded soon !!!')
                else:
                    print('Invalid OTP')
            else:
                print('Invalid number of tickets')
        else:
            print('Invalid Selection')


def total_combo_cancel(email, name):
    view = view_booked_details(email)
    qqq = 'select Food_ID from cust_book where Cust_Email=%s'
    my_cursor.execute(qqq, (email,))
    rrr = my_cursor.fetchall()
    l = []
    for j in rrr:
        if j[0] != '0':
            l.append(j[0])
    if view == 1 and len(l) != 0:
        inp = input('\nDo you want to cancel total combo [y/n]: ').lower()
        if inp == 'y':
            otp = send_otp(email, name)
            print('\nOTP has been sent to your mail')
            inpp = input('\nEnter the OTP: ')
            if inpp.isdigit() and otp == int(inpp):
                qu1 = 'select Total_Ticket_Price,Fd_Quant,Food_ID,Total_Price from cust_book where Cust_Email=%s'
                my_cursor.execute(qu1, (email,))
                re = my_cursor.fetchall()
                if (int(re[0][0]) == int(re[0][3])):
                    print("\nSorry...You have no food bookings")
                else:
                    for i in re:
                        if i[2] != "0":
                            qu2 = 'select Avail_Quantity from food where Food_ID=%s'
                            my_cursor.execute(qu2, (i[2],))
                            re1 = my_cursor.fetchone()
                            qu3 = 'update food set Avail_Quantity=%s where Food_ID=%s'
                            my_cursor.execute(qu3, (str(int(i[1]) + int(re1[0])), i[2]))
                            my_db.commit()
                            qu = 'update cust_book set Food_ID=%s,Fd_Quant=%s,Fd_Price=%s,Fd_Combo=%s where Cust_Email=%s and Food_ID=%s'
                            my_cursor.execute(qu, ("0", "0", "0", "NO", email, i[2]))
                            my_db.commit()
                        qqu = 'update cust_book set Total_Price =%s where Cust_Email=%s'
                        my_cursor.execute(qqu, (int(re[0][0]), email))
                        my_db.commit()

                    print('\nYour Combo successfully cancelled !!!. You will be refunded soon !!!')
            else:
                print('\nInvalid OTP')
        elif inp == 'n':
            pass
        else:
            print('\nInvalid option')
    else:
        print('\nNo food bookings available')


def cancel_food(email, name):
    view = view_booked_details(email)
    qqq = 'select Food_ID from cust_book where Cust_Email=%s'
    my_cursor.execute(qqq, (email,))
    rrr = my_cursor.fetchall()
    l = []
    for j in rrr:
        if j[0] != '0':
            l.append(j[0])
    if view == 1 and len(l) != 0:
        inp2 = input('\nEnter the Food ID to cancel: ')
        # print(l)
        if inp2 in l:
            que1 = 'select Fd_Quant,Fd_Price,Total_Price from cust_book where Cust_Email=%s and Food_ID=%s'
            my_cursor.execute(que1, (email, inp2))
            res1 = my_cursor.fetchone()
            # print(res1)
            one_food = int(res1[1]) / int(res1[0])
            inp3 = input('Enter the quantity to cancel: ')
            if inp3.isdigit():
                if int(res1[0]) == int(inp3):
                    otp = send_otp(email, name)
                    print('\nOTP has been sent to {}'.format(email))
                    inpp = input('\nEnter the OTP: ')
                    if inpp.isdigit() and otp == int(inpp):
                        qu = 'update cust_book set Food_ID=%s,Fd_Quant=%s,Fd_Price=%s,Fd_Combo=%s, Total_Price=%s where Cust_Email=%s and Food_ID=%s'
                        my_cursor.execute(qu, ("0", "0", "0", "NO", int(res1[2]) - int(res1[1]), email, inp2))
                        my_db.commit()
                        quu = 'update cust_book set Total_Price=%s where Cust_Email=%s'
                        my_cursor.execute(quu, (int(res1[2]) - int(res1[1]), email))
                        my_db.commit()
                        que3 = 'select Avail_Quantity from food where Food_ID=%s'
                        my_cursor.execute(que3, (inp2,))
                        res2 = my_cursor.fetchone()
                        # print(res2)
                        ad = int(res2[0]) + int(inp3)
                        que4 = 'update food set Avail_Quantity=%s where Food_ID=%s'
                        my_cursor.execute(que4, (str(ad), inp2))
                        my_db.commit()
                        print('\nYour combo cancelled. You will be refunded soon !!!')
                    else:
                        print('\nInvalid OTP')
                elif int(inp3) < int(res1[0]):
                    otp = send_otp(email, name)
                    print('\nOTP has been sent to {}'.format(email))
                    inpp = input('\nEnter the OTP: ')
                    if inpp.isdigit() and otp == int(inpp):
                        co1 = int(one_food) * int(inp3)
                        que2 = 'update cust_book set Fd_Quant=%s,Fd_Price=%s,Total_Price=%s where Cust_Email=%s and Food_ID=%s'
                        my_cursor.execute(que2, (
                        int(res1[0]) - int(inp3), str(int(res1[1]) - co1), int(res1[2]) - co1, email, inp2))
                        my_db.commit()
                        quu = 'update cust_book set Total_Price=%s where Cust_Email=%s'
                        my_cursor.execute(quu, (int(res1[2]) - co1, email))
                        my_db.commit()
                        que3 = 'select Avail_Quantity from food where Food_ID=%s'
                        my_cursor.execute(que3, (inp2,))
                        res2 = my_cursor.fetchone()
                        ad = int(res2[0]) + int(inp3)
                        que4 = 'update food set Avail_Quantity=%s where Food_ID=%s'
                        my_cursor.execute(que4, (str(ad), inp2))
                        my_db.commit()
                        print('\nSelected combo quantity cancelled. You will be refunded soon !!!')
                    else:
                        print('\nInvalid OTP')
                else:
                    print('\nInvalid Selection')
            else:
                print('\nInvalid Selection')
        else:
            print('\nInvalid Selection')
    else:
        print('\nNo food bookings to cancel')


def show_movie(res):
    for i in res:
        print("\nMovie ID: {}"
              "\nMovie Name: {}"
              "\nTiming: {}"
              "\nAvailable Tickets: {}"
              "\nPrice: {}".format(i[0], i[1], i[2], i[3], i[4]))


def rem_movie():
    my_cursor.execute('select * from movie')
    res = my_cursor.fetchall()
    if len(res) == 0:
        print("\nNo Movies are primeiring")
    else:
        show_movie(res)
        de = input('\nEnter Movie ID to be deleted: ')
        if de.isdigit():
            re = check_MovieId(de)
            if re == 0:
                print('\nInvalid Selection')
            else:
                my_cursor.execute("delete from movie where Movie_ID = %s", (de, ))
                my_db.commit()
                print('Movie Deleted')
        else:
            print('\nPlease enter Correct ID')
            rem_movie()


def add_movie():
    f = 0
    movie = {}
    re = 'Y'
    movie_name = input("\nEnter movie name: ")
    while True:
        total_ticket = input("Enter the total number of tickets: ")
        if total_ticket.isdigit():
            break
        else:
            print('\nInvalid Quantity')
    while True:
        total_price = input("Enter the price of movie: ")
        if total_price.isdigit():
            break
        else:
            print('\nInvalid Price')
    while re == 'Y':
        movie_time = []
        movie_time.append(input("Enter Movie timing: HH:MM:SS: "))
        re = input("\nAdd more timing? Y/N: ").upper()
        movie[movie_name] = [total_ticket, total_price, movie_time]
        for i in movie:
            qe = 'insert into movie(Movie_Name, Show_Time, Avail_Tickets, Price)values(%s, %s, %s, %s)'
            val = (i, str(movie[i][2]), movie[i][0], movie[i][1])
            my_cursor.execute(qe, val)
            my_db.commit()
            f = 1
            movie = {}
    if f == 1:
        print("\nMovie Added")


def check_MovieId(Id_check):
    quer='select exists(select * from movie where Movie_ID=%s)' %(Id_check)
    my_cursor.execute(quer)
    result = my_cursor.fetchone()
    return result[0]


def change_movie_price():
    my_cursor.execute('select * from movie')
    res = my_cursor.fetchall()
    if len(res) == 0:
        print("\nNo Movies are primeiring")
    else:
        show_movie(res)
        modi = input('\nEnter the movie ID to modify ticket price: ')
        if modi.isdigit():
            r = check_MovieId(modi)
            if r==0:
                print('\nInvalid Selection')
            else:
                while True:
                    modify_price = input('Enter the new price: ')
                    if modify_price.isdigit():
                        q3 = 'update movie set Price=%s where Movie_ID = %s'
                        tup3 = (modify_price,modi)
                        my_cursor.execute(q3,tup3)
                        my_db.commit()
                        print('\nChanges Updated!')
                        break
                    else:
                        print('\nInvalid Price')
                        continue
        else:
            print('\nPlesse enter Correct ID')
            change_movie_price()


def change_ticket_quantity():
    my_cursor.execute('select * from movie')
    res = my_cursor.fetchall()
    if len(res) == 0:
        print("\nNo Movies are primeiring")
    else:
        show_movie(res)
        modi_id = input('\nEnter the movie ID to modify ticket quantity: ')
        if modi_id.isdigit():
            r = check_MovieId(modi_id)
            if r == 0:
                print('\nInvalid Selection')
            else:
                while True:
                    modify_quan = input('Enter the new quantity: ')
                    if modify_quan.isdigit():
                        q3 = 'update movie set Avail_Tickets=%s where Movie_ID = %s'
                        tup3=(modify_quan, modi_id)
                        my_cursor.execute(q3, tup3)
                        my_db.commit()
                        print('\nChanges Updated!')
                        break
                    else:
                        print('\nInvalid ticket quantity')
                        continue
        else:
            print('\nPlease enter Correct ID')
            change_ticket_quantity()


def add_food():
    fo_co = input('\nEnter the food combo: ')
    while True:
        fo_price = input('Enter the price: ')
        if fo_price.isdigit():
            break
        else:
            print('\nInvalid Price')
    while True:
        fo_quan = input('\nEnter the total quantity: ')
        if fo_quan.isdigit():
            break
        else:
            print('\nInvalid Quantity')
    que = 'insert into food(Food_Combo,Price,Avail_Quantity) values(%s,%s,%s)'
    my_cursor.execute(que,(fo_co, fo_price, fo_quan))
    my_db.commit()
    print('\nFood Combo Added')


def view_food():
    q = 'select * from food'
    my_cursor.execute(q)
    rr = my_cursor.fetchall()
    for i in rr:
        print("\nFood ID: {}"
              "\nFood Combo: {}"
              "\nPrice: {}"
              "\nAvailable Quantity: {}".format(i[0],i[1],i[2],i[3]))


def comboId_check(com_id):
    quer = 'select exists(select * from food where Food_ID=%s)' %(com_id)
    my_cursor.execute(quer)
    result = my_cursor.fetchone()
    return result[0]


def rem_food():
    view_food()
    de= input('\nEnter the food combo ID to delete: ')
    if de.isdigit():
        re=comboId_check(de)
        if re == 0:
            print('\nInvalid Combo ID')
        else:
            my_cursor.execute("delete from food where Food_ID=%s",(de,))
            my_db.commit()
            print('\nCombo Deleted')
    else:
        print('\nEnter Correct ID')
        rem_food()


def food_price_change():
    view_food()
    modi=input('\nEnter the food combo ID: ')
    if modi.isdigit():
        r = comboId_check(modi)
        if r == 0:
            print('\nInvalid Selection')
        else:
            while True:
                modify_price=input('Enter the new price: ')
                if modify_price.isdigit():
                    q3 = 'update food set Price=%s where Food_ID=%s'
                    tup3 = (modify_price,modi)
                    my_cursor.execute(q3,tup3)
                    my_db.commit()
                    print('\nChanges Updated!')
                    break
                else:
                    print('\nInvalid Price')
                    continue
    else:
        print('\nPlease enter Correct ID')
        food_price_change()


def food_quan_change():
    view_food()
    modi=input('Enter the food combo ID: ')
    if modi.isdigit():
        r = comboId_check(modi)
        if r == 0:
            print('Invalid Selection')
        else:
            while True:
                modify_qua = input('Enter the new quantity: ')
                if modify_qua.isdigit():
                    q3 = 'update food set Avail_Quantity=%s where Food_ID=%s'
                    tup3 = (modify_qua,modi)
                    my_cursor.execute(q3,tup3)
                    my_db.commit()
                    print('Changes Updated!')
                    break
                else:
                    print('Invalid Quantity')
                    continue
    else:
        print('Enter Correct ID')
        food_quan_change()


def movie_book(no):
    movbook = []
    cus_quan = int(input("\nEnter quantity: "))
    my_cursor.execute('select * from movie where Movie_ID=%s', (no,))
    dat_all = my_cursor.fetchone()

    if cus_quan <= int(dat_all[3]):
        chn = int(dat_all[3]) - cus_quan
        my_cursor.execute('update  movie set Avail_Tickets=%s where Movie_ID=%s', (chn, no,))
        price = int(dat_all[4]) * cus_quan
        movbook.append(cus_quan)
        movbook.append(dat_all[1])
        movbook.append(price)
        my_db.commit()

    else:
        print('\nSorry quantity not available')
        movfod_book(email)
    return movbook


def food_book():
    fodbook = []
    view_food()
    c=0
    cus_ch = int(input('\nEnter ID of preffered food item: '))

    my_cursor.execute('select Food_ID from food')
    res = my_cursor.fetchall()

    out = [i for t in res for i in t]
    for j in out:
        if j == cus_ch:
            c=1
            req = int(input('Enter Quantity: '))
            my_cursor.execute('select * from food where Food_ID=%s', (cus_ch,))
            dat_all = my_cursor.fetchone()
            if req <= int(dat_all[3]):
                chn = int(dat_all[3]) - req
                my_cursor.execute('update food set Avail_Quantity=%s where Food_ID=%s', (chn, cus_ch,))
                price = int(dat_all[2]) * req
                fodbook.append(req)
                fodbook.append(dat_all[1])
                fodbook.append(price)
                fodbook.append(cus_ch)
                my_db.commit()
                return fodbook
            else:
                print('\nSorry quantity not available')
                return food_book()

    if c == 0:
        print('\nInvalid selection. Please try again')
        g = input('Enter 10 to exit or any other number to rebook food')
        if g != 10:
            return food_book()


def movfod_book(email):
    my_cursor.execute('select * from movie')
    res = my_cursor.fetchall()
    if len(res) == 0:
        print("\nNo Movies are primeiring")
    else:
        show_movie(res)
        pr = 0
        c = 0
        totalp = 0
        fodbook = []
        no = int(input('\nSelect Movie ID to book the movie with preffered time else enter 100: '))
        my_cursor.execute('select Movie_ID from movie')
        res = my_cursor.fetchall()
        out = [i for t in res for i in t]
        for j in out:
            if int(j) == no:
                c=1
                mov = movie_book(no)
                if len(mov) > 0:
                    qa = input('\nDo you want to enjoy food ? (Y/N): ').lower()
                    if qa == 'n':
                        totalp = int(mov[2])
                        my_cursor.execute('select Email,Name from Customer where Email=%s', (email,))
                        resn = my_cursor.fetchone()
                        my_cursor.execute('select Show_Time from movie where Movie_ID=%s', (no,))
                        rese = my_cursor.fetchone()
                        t = ''.join(rese[0])
                        qe = 'insert into cust_book(' \
                             'Cust_Name,' \
                             'Cust_Email,' \
                             'Movie_ID,' \
                             'Movie_Name,' \
                             'Show_time,' \
                             'Booked_Tickets,' \
                             'Total_Ticket_Price,' \
                             'Total_Price)' \
                             'values(%s,%s,%s,%s,%s,%s,%s,%s)'
                        valu = (resn[0], resn[1], no, mov[1], str(t), mov[0], mov[2], totalp)
                        my_cursor.execute(qe, valu)
                        my_db.commit()
                    else:
                        while qa == 'y':
                            fod = food_book()
                            if len(fod) > 0:
                                fodbook.append(fod)
                                pr = pr + int(fod[2])

                            qa = input('\nDo you want to enjoy food ? [Y/N]: ').lower()
                            totalp = int(mov[2]) + int(pr)
                            my_cursor.execute('select Name, Email from Customer where Email=%s', (email,))
                            resn=my_cursor.fetchone()
                            my_cursor.execute('select Show_Time from movie where Movie_ID=%s', (no,))
                            rese = my_cursor.fetchone()
                            t=''.join(rese[0])
                            for hj in range(len(fodbook)):
                                    qe = 'insert into cust_book(' \
                                    'Cust_Name,' \
                                    'Cust_Email,' \
                                    'Movie_ID,' \
                                    'Movie_Name,' \
                                    'Show_time,' \
                                    'Booked_Tickets,' \
                                    'Food_ID,'\
                                    'Total_Ticket_Price)' \
                                    'values(%s,%s,%s,%s,%s,%s,%s,%s)'
                                    valu = (resn[0],resn[1],no,mov[1], str(t), mov[0],fodbook[hj][3], mov[2])
                                    my_cursor.execute(qe,valu)
                                    my_db.commit()

                                    my_cursor.execute('select Fd_Combo,Fd_Quant,Fd_Price, Total_Price from cust_book where Food_ID=%s AND Cust_Email=%s',((fodbook[hj][3],email,)))
                                    fo=my_cursor.fetchall()
                                    outr = [ie for te in fo for ie in te]
                                    qe = 'UPDATE cust_book SET Fd_Combo=%s , Fd_Quant=%s , Fd_Price=%s, Total_Price = %s WHERE Food_ID=%s'
                                    valu = (str(fodbook[hj][1]),str(fodbook[hj][0]),str(fodbook[hj][2]), totalp, fodbook[hj][3])
                                    my_cursor.execute(qe, valu)
                                    my_db.commit()
                                    qwe = 'UPDATE cust_book SET Total_Price=%s WHERE Cust_Email=%s'
                                    last = (totalp, email)
                                    my_cursor.execute(qwe, last)
                                    my_db.commit()
                                    fodbook = []
                        print('\nMovie successfully booked')
                else:
                    break

        if c==0:
            print('\nInvalid selection.Please try again')
            g = int(input('\nEnter 100 to exit or any other number to rebook: '))
            if g != 100:
                movfod_book(email)


def logina():
    global n
    global p
    print("\nLogin")
    print("~~~~~")
    u_email = input("Enter your EmailId: ")
    n = u_email
    my_cursor.execute('select * from Admin where Email = %s', (u_email,))
    result_a = my_cursor.fetchall()
    if len(result_a) != 0:
        for i in result_a:
            if i[3] == 'Activated':
                while True:
                    print("\n1. Enter your password")
                    print("2. Forget Password ?")
                    logina_ch = input("Select an option by selecting a number: ")
                    if logina_ch == '1':
                        pwd = input("\nEnter your password: ")
                        p = pwd
                        if i[4] == pwd:
                            print("\nSuccessfully Logged in.")
                            print("\nHello", i[0])
                            return True, u_email
                        else:
                            return "\nWrong password. Please try again with correct password", u_email
                    elif logina_ch == '2':
                        forget_pass(i[1], i[0])
                        return logina()
                    else:
                        print("\nInvalid Selection !")
            else:
                return "\nYour account is deactivated. Please contact database administrator.", u_email
    else:
        return "\nInvalid Admin MailID! PLease try again with correct Email ID", u_email

    return False, u_email


def loginc():
    global n
    global p
    print("\nLogin")
    print("~~~~~")
    u_email = input("\nEnter your EmailId: ")
    n = u_email
    my_cursor.execute('select * from Customer where Email = %s', (u_email,))
    result_a = my_cursor.fetchall()
    if len(result_a) != 0:
        for i in result_a:
            if i[3] == 'Activated':
                while True:
                    print("\n1. Enter your password")
                    print("2. Forget Password ?")
                    loginc_ch = input("Select an option by selecting a number: ")
                    if loginc_ch == '1':
                        pwd = input("\nEnter your password: ")
                        p = pwd
                        if i[4] == pwd:
                            print("\nSuccessfully Logged in.")
                            print("\nHello", i[0])
                            return True, u_email
                        else:
                            return "\nWrong password. Please try again with correct password", u_email
                    elif loginc_ch == '2':
                        forget_pass(i[1], i[0])
                        return loginc()
                    else:
                        print("\nInvalid Selection !")
            else:
                return "Your account is deactivated. Please contact database administrator.", u_email
    else:
        return "Invalid Customer MailID! Please try again with correct Email ID", u_email

    return False, u_email


def check_email():
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.com]$'
    usem = input("Enter email: ")

    '''gen_otp = send_otp(usem, uname)
        print('\nOTP has been sent to {}'.format(usem))
        inp_otp = input('\nEnter the OTP: ')
        if str(gen_otp) == inp_otp:'''
    if (re.search(regex, usem)):
        return 1, usem
    else:
        return 0, usem


def check_cust_mail(mail):
    my_cursor.execute('select exists(select * from Customer where Email = "%s")' % (mail,))
    result = my_cursor.fetchone()
    if result[0] == 1:
        return result[0]
    else:
        return result[0]


def send_otp(rec_mail, rec_name):
    otp=random.randrange(1000,10000)
    yag = yagmail.SMTP("movieticket.booking.4@gmail.com","akvy@1234")
    yag.send(
        to=rec_mail,
        subject="OTP from AKVY Movies",
        contents=["Hi " + rec_name+ "....!!!", "Your OTP is " + str(otp)]
    )
    return otp


def forget_pass(rec_mail, rec_name):
    ver_otp = send_otp(rec_mail, rec_name)
    print('\nOTP has been sent to {}'.format(rec_mail))
    inp_otp = input('\nEnter the OTP: ')
    if str(ver_otp) == inp_otp:
        ret_val = set_passwd()
        quer = 'select exists(select * from Admin where Email = "%s")' %(rec_mail)
        my_cursor.execute(quer)
        result = my_cursor.fetchone()
        if result[0] == 1:
            qu1='update Admin set Password = %s where Email = %s'
            my_cursor.execute(qu1, (ret_val, rec_mail))
            my_db.commit()
        else:
            qu1 = 'update Customer set Password = %s where Email = %s'
            my_cursor.execute(qu1, (ret_val, rec_mail))
            my_db.commit()
    else:
        print('\nEnter the correct OTP')
        forget_pass(rec_mail, rec_name)


def check_admin_mail(mail):
    my_cursor.execute('select exists(select * from Admin where Email = "%s")' % (mail,))
    result = my_cursor.fetchone()
    if result[0] == 1:
        return result[0]
    else:
        return result[0]


def cust_sign_up():
    db_cust_name = input("\nEnter your Name: ").title()
    rec, db_cust_email = check_email()
    if rec == 1:
        flag = check_cust_mail(db_cust_email)
        if flag == 1:
            print("\nEmailId {} is already registered.".format(db_cust_email))
            while True:
                print("\n1. Try again with new Email ID")
                print("2. Sign In with registered Email Id")
                chcm = input("Select the operation by entering the number: ")
                if chcm == '1':
                    return cust_sign_up()

                elif chcm == '2':
                    return customer()
                elif chcm == '3':
                    break
                else:
                    print("\nPlease select valid number !")
        else:
            db_cust_Mob = phone_no()
            db_cust_pass = set_passwd()
            sql = 'insert into Customer(' \
                  'Name, ' \
                  'Email, ' \
                  'Mob_No, ' \
                  'Password) ' \
                  'values(%s, %s, %s, %s)'

            val = (db_cust_name,
                   db_cust_email,
                   db_cust_Mob,
                   db_cust_pass)
            my_db.commit()
            my_cursor.execute(sql, val)
            my_db.commit()
            print("\nCongratulations !! Signed In successfully, please Sign In to your account!")
            customer()

    else:
        print("\nPlease enter valid email")
        cust_sign_up()


def adm_sign_up():
    db_adm_name = input("Enter Name: ").title()
    emc, db_adm_email = check_email()
    if emc == 1:
        flag = check_admin_mail(db_adm_email)
        if flag == 1:
            print("\nEmailId {} is already registered.".format(db_adm_email))
            while True:
                print("\n1. Try again with new Email ID")
                print("2. Sign In with registered Email Id")
                cham = input("Select the operation by entering the number: ")
                if cham == '1':
                    adm_sign_up()
                    break
                elif cham == '2':
                    admin()
                    break
                else:
                    print("\nPlease select valid number !")
        else:
            db_adm_Mob = phone_no()
            db_adm_pass = set_passwd()

            sql = 'insert into Admin(' \
                  'Name, ' \
                  'Email, ' \
                  'Mob_No, ' \
                  'Password) ' \
                  'values(%s, %s, %s, %s)'

            val = (db_adm_name,
                   db_adm_email,
                   db_adm_Mob,
                   db_adm_pass)
            my_db.commit()
            my_cursor.execute(sql, val)
            my_db.commit()
            print("Accout created Successfully !\nPlease Sign Out and Login with your account")
    else:
        print("\nPlease Enter a valid email")
        adm_sign_up()


def phone_no():
    f = 1
    ph_num = input("Enter Phone Number: ")
    if len(ph_num) == 10:
        for i in ph_num:
            if i.isdigit():
                if f == 1:
                    if i == '9' or i == '8' or i == '7' or i == '6':
                        f = 2
                    else:
                        print("\nNumber Invalid because phone number starts from 6, 7, 8 or 9\n")
                        return phone_no()
            else:
                print("\nPhone number does not contain alphabet. Please enter correct phone number\n")
                return phone_no()
    else:
        print("\nPhone number should be of 10 digi\n")
        return phone_no()

    if f == 2:
        return ph_num


def change_admin_passwd(mail):
    if check_admin_mail(mail):
        old_pass = input("\nEnter current Password: ")
        my_cursor.execute('select Password from Admin where Email = %s', (mail,))
        old_pass_result = my_cursor.fetchone()
        if old_pass_result[0] == old_pass:
            new_pass = input("Enter new Password: ")
            my_cursor.execute('update Admin set Password = %s where Email = %s and Password = %s',
                              (new_pass, mail, old_pass))
            print("\nPassword has been changed.")
        else:
            print("\nYour current password is invalid. Please try again with correct password")
            change_admin_passwd(mail)
        my_db.commit()
    else:
        print("\nPlease enter correct Email Id.")
        change_admin_passwd(mail)


def change_cust_passwd(email):
    old_pass = input("\nEnter current Password: ")
    my_cursor.execute('select Password from Customer where Email = %s', (email, ))
    old_pass_result = my_cursor.fetchone()
    if old_pass_result[0] == old_pass:
        new_pass = input("Enter new Password: ")
        my_cursor.execute('update Customer set Password = %s where Email = %s and Password = %s',
                          (new_pass, email, old_pass))
        print("\nPassword has been changed.")
    else:
        print("\nYour current password is invalid. Please try again with correct password")
        change_admin_passwd(email)
    my_db.commit()


def check_pincode():
    pin = input("\nEnter Pin Code: ")
    if len(pin) == 6:
        for i in pin:
            if i.isdigit():
                pass
            else:
                print("\nInvalid Pin Code")
                check_pincode()
    else:
        print("\nPin Code should of 6 digit")
        check_pincode()


def set_passwd():
    passwd = input("Enter new password: ")
    confirm_pass = input("Enter the password again: ")
    if passwd == confirm_pass:
        return passwd
    else:
        print("\nYour passwords do not match. Please set your password again\n")
        return set_passwd()


def print_admin_cust_details(res):
    for i in res:
        print("\nName: {}"
              "\nEmail: {}"
              "\nMobile No: {}"
              "\nStatus: {}".format(i[0], i[1], i[2], i[3]))


def print_cust_book_details(res):
    for i in res:
        print("\nCustomer Name :{}"
              "\nCustomer Email: {}"
              "\nMovie Name: {}"
              "\nShow Time: {}"
              "\nTotal Ticket(s): {}"
              "\nFood Combo: {}"
              "\nFood Quantity: {}"
              "\nTotal Ticket Price: {}"
              "\nTotal Food Price: {}"
              "\n Total Price: {}".format(i[0], i[1], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10]))


def admin_act_deact():
    rec, ac_deac_email = check_email()
    if rec == 1:
        flag = check_admin_mail(ac_deac_email)
        if flag == 1:
            my_cursor.execute('select Status from Admin where Email = %s', (ac_deac_email,))
            Status = my_cursor.fetchone()
            print("\nAccount Status: ", Status[0])

            if Status[0] == 'Activated':
                cha171 = input("\nDo you want to deactivate this account?(y/n): ")
                if cha171 == 'y':
                    my_cursor.execute('update Admin set Status = "Deactivated" where Email = %s', (ac_deac_email,))
                    print("\nStatus has been changed to Deactivated.")
                    my_db.commit()
                elif cha171 == 'n':
                    print("\nOkay.")

            elif Status[0] == 'Deactivated':
                cha171 = input("\nDo you want to activate this account?(y/n): ")
                if cha171 == 'y':
                    my_cursor.execute('update Admin set status = "Activated" where Email = %s', (ac_deac_email,))
                    print("\nStatus has been changed to Activated.")
                    my_db.commit()
                elif cha171 == 'n':
                    print("\nOkay.")
        else:
            print("\nIncorrect Email ! PLease try again with correct email.")
    else:
        print("Enter valid email")
        check_email()


def del_acc(email):
    db_cust_pass = input("\nEnter your password: ")
    my_cursor.execute('select Password from Customer where Email = %s', (email,))
    res = my_cursor.fetchone()
    if res[0] == db_cust_pass:
        my_cursor.execute('delete from Customer where Email = %s', (email,))
        print("\nYour Account has been deleted")
        customer()
    else:
        print("\nInvalid Password")
        del_acc(email)


def cust_act_deact():
    rec, ac_deac_email = check_email()
    if rec == 1:
        flag = check_cust_mail(ac_deac_email)
        if flag == 1:
            my_cursor.execute('select Status from Customer where Email = %s', (ac_deac_email,))
            Status = my_cursor.fetchone()
            print("\nAccount Status: ", Status[0])

            if Status[0] == 'Activated':
                cha161 = input("Do you want to deactivate this account?(y/n): ")
                if cha161 == 'y':
                    my_cursor.execute('update Customer set Status = "Deactivated" where Email = %s', (ac_deac_email,))
                    print("\nStatus has been changed to Deactivated.")
                    my_db.commit()
                elif cha161 == 'n':
                    print("\nOkay.")

            elif Status[0] == 'Deactivated':
                cha161 = input("Do you want to activate this account?(y/n): ")
                if cha161 == 'y':
                    my_cursor.execute('update Customer set status = "Activated" where Email = %s', (ac_deac_email,))
                    print("\nStatus has been changed to Activated.")
                    my_db.commit()
                elif cha161 == 'n':
                    print("\nOkay.")
        else:
            print("\nIncorrect Email ! PLease try again with correct email.")
    else:
        print("\nEnter valid email")
        check_email()


def admin():
    c, email = logina()
    if c == True:
        while True:
            print("\nWelcome to the Admin Module")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("1. Account")
            print("2. Modify")
            print("3. Log Out")

            cha = input("Select an option by entering the number: ")
            if cha == '1':
                while True:
                    print("\n")
                    print("1. Create a new Account")
                    print("2. View all Admins")
                    print("3. View all Customers")
                    print("4. Search Admins")
                    print("5. Search Customers")
                    print("6. Change Password")
                    print("7. Activate/Deactivate Account")
                    print("8. Exit")

                    cha1 = input("\nSelect an option by entering the number: ")
                    if cha1 == '1':
                        adm_sign_up()

                    elif cha1 == '2':
                        my_cursor.execute('select * from Admin')
                        res = my_cursor.fetchall()
                        if len(res) != 0:
                            print_admin_cust_details(res)
                        else:
                            print("\nNo Admins")

                    elif cha1 == '3':
                        my_cursor.execute('select * from Customer')
                        res = my_cursor.fetchall()
                        if len(res) != 0:
                            print_admin_cust_details(res)
                        else:
                            print("\nNo Customers")

                    elif cha1 == '4':
                        while True:
                            print("\n1. By Email")
                            print("2. By Name")
                            print("3. By Status")
                            print("4. Exit")
                            cha14 = input("\nSelect the operation by entering the number: ")
                            if cha14 == '1':
                                se_email = input("\nEnter the Email: ")
                                my_cursor.execute('select Email from Admin where Email = %s', (se_email,))
                                se_email_re = my_cursor.fetchall()
                                if len(se_email_re) != 0:
                                    my_cursor.execute(
                                        'select Name, Email, Mob_No, Status from '
                                        'Admin where Email = %s', (se_email,))
                                    res_pr = my_cursor.fetchall()
                                    print_admin_cust_details(res_pr)
                                else:
                                    print("\nInvalid Email")

                            elif cha14 == '2':
                                se_name = input("\nEnter the Name: ")
                                my_cursor.execute('select Name from Admin where Name = %s', (se_name,))
                                se_name_re = my_cursor.fetchall()
                                if len(se_name_re) != 0:
                                    my_cursor.execute(
                                        'select Name, Email, Mob_No, Status from '
                                        'Admin where Name = %s', (se_name,))
                                    res_pr = my_cursor.fetchall()
                                    print_admin_cust_details(res_pr)
                                else:
                                    print("\nInvalid Name")

                            elif cha14 == '3':
                                se_status = input("\nEnter the Status: ")
                                my_cursor.execute('select Status from Admin where Status = %s', (se_status,))
                                se_status_re = my_cursor.fetchall()
                                if len(se_status_re) != 0:
                                    my_cursor.execute(
                                        'select Name, Email, Mob_No, Status from '
                                        'Admin where Status = %s', (se_status,))
                                    res_pr = my_cursor.fetchall()
                                    print_admin_cust_details(res_pr)
                                else:
                                    print("\nInvalid Status")

                            elif cha14 == '4':
                                break

                            else:
                                print("\nPlease Enter the valid number")

                    elif cha1 == '5':
                        while True:
                            print("\n1. By Email")
                            print("2. By Name")
                            print("3. By Status")
                            print("4. Exit")
                            cha15 = input("Select the operation by entering the number: ")
                            if cha15 == '1':
                                se_email = input("Enter the Email: ")
                                my_cursor.execute('select Email from Customer where Email = %s', (se_email,))
                                se_email_re = my_cursor.fetchall()
                                if len(se_email_re) != 0:
                                    my_cursor.execute(
                                        'select Name, Email, Mob_No, Status from '
                                        'Customer where Email = %s', (se_email,))
                                    res_pr = my_cursor.fetchall()
                                    print_admin_cust_details(res_pr)
                                else:
                                    print("\nInvalid Email.")

                            elif cha15 == '2':
                                se_name = input("Enter the Name: ")
                                my_cursor.execute('select Name from Customer where Name = %s', (se_name,))
                                se_name_re = my_cursor.fetchone()
                                if len(se_name_re) != 0:
                                    my_cursor.execute(
                                    'select Name, Email, Mob_No, Status from '
                                    'Customer where Name = %s', (se_name,))
                                    res_pr = my_cursor.fetchall()
                                    print_admin_cust_details(res_pr)
                                else:
                                    print("\nInvalid Name.")

                            elif cha15 == '3':
                                se_status = input("Enter the Status: ")
                                my_cursor.execute('select Status from Customer where Status = %s', (se_status,))
                                se_status_re = my_cursor.fetchall()
                                if len(se_status_re) != 0:
                                    my_cursor.execute(
                                        'select Name, Email, Mob_No, Status from '
                                        'Customer where Status = %s', (se_status,))
                                    res_pr = my_cursor.fetchall()
                                    print_admin_cust_details(res_pr)
                                else:
                                    print("\nInvalid Status.")

                            elif cha15 == '4':
                                break

                            else:
                                print("Please enter valid number")

                    elif cha1 == '6':
                        change_admin_passwd(email)

                    elif cha1 == '7':
                        while True:
                            print("\n1. For Admin")
                            print("2. For Customer")
                            print("3. Exit")
                            cha17 = input("Select an operation by entering the number: ")

                            if cha17 == '1':
                                my_cursor.execute('select * from Admin')
                                res = my_cursor.fetchall()
                                if len(res) != 0:
                                    print_admin_cust_details(res_pr)
                                    admin_act_deact()
                                else:
                                    print("\nNo Admins")


                            elif cha17 == '2':
                                my_cursor.execute('select * from Customer')
                                res = my_cursor.fetchall()
                                if len(res) != 0:
                                    print_admin_cust_details(res)
                                    cust_act_deact()
                                else:
                                    print("\nNo Admins")

                            elif cha17 == '3':
                                break

                            else:
                                print("\nPlease Select a valid number")

                    elif cha1 == '8':
                        break

                    else:
                        print("\nInvalid Selection! Please select valid option and try again.\n")

            elif cha == '2':
                while True:
                    print("\n1. Modify Movie")
                    print("2. Modify Food")
                    print("3. Exit")
                    cha2 = input("\nSelect an operation by entering the number: ")
                    if cha2 == '1':
                        while True:
                            print("\n1. View all Movies")
                            print("2. Add a movie")
                            print("3. Remove a movie")
                            print("4. Change the Movie Price")
                            print("5. Change the Ticket Quantity")
                            print("6. Exit")
                            cha21 = input("\nSelect an operation by selecting number: ")

                            if cha21 == '1':
                                my_cursor.execute('select * from movie')
                                res = my_cursor.fetchall()
                                if len(res) == 0:
                                    print("\nNo Movies are primeiring")
                                else:
                                    show_movie(res)
                            elif cha21 == '2':
                                add_movie()
                            elif cha21 == '3':
                                rem_movie()
                            elif cha21 == '4':
                                change_movie_price()
                            elif cha21 == '5':
                                change_ticket_quantity()
                            elif cha21 == '6':
                                break
                            else:
                                print("\nPlease enter the valid number")

                    elif cha2 == '2':
                        while True:
                            print("1. View Food Items")
                            print("2. Add a food item")
                            print("3. Remove a food item")
                            print("4. Change Food Price")
                            print("5. Add Food Quantity")
                            print("6. Exit")
                            cha22 = input("\nSelect an operation by selecting number: ")
                            if cha22 == '1':
                                view_food()
                            elif cha22 == '2':
                                add_food()
                            elif cha22 == '3':
                                rem_food()
                            elif cha22 == '4':
                                food_price_change()
                            elif cha22 == '5':
                                food_quan_change()
                            elif cha22 == '6':
                                break
                            else:
                                print("\nInvalid Selection! Please select a valid option and try again.")

                    elif cha2 == '3':
                        break
                    else:

                        print("\nInvalid Selection! Please select a valid option and try again.")


            elif cha == '3':
                print("\nSigning Out...\nSee you soon")
                break

            else:
                print("\nInvalid Selection! Please select a valid option and try again.")

    else:
        print(c)


def customer():
    while True:
        print("\n1. Sign Up")
        print("2. Sign In")
        print("3. Exit")
        chc = input("Select an operation by entering a number: ")
        if chc == '1':
            cust_sign_up()

        elif chc == '2':
            c, email = loginc()
            if c == True:
                while True:
                    print("\nWelcome to AKVY MOVIES")
                    print("~~~~~~~~~~~~~~~~~~~~~~")
                    print("1. View Movies")
                    print("2. Search a Movie")
                    print("3. Book a Movie")
                    print("4. Cancel a Movie")
                    print("5. Download Invoice")
                    print("6. Account")
                    print("7. Exit")

                    chc1 = input("Select an operation by entering a number: ")

                    if chc1 == '1':
                        my_cursor.execute('select * from movie')
                        res = my_cursor.fetchall()
                        if len(res) == 0:
                            print("\nNo Movies are premiering")
                        else:
                            show_movie(res)

                    elif chc1 == '2':
                        movie_ser = input("Enter movie name to be searched: ").title()
                        my_cursor.execute('select * from movie where Movie_Name = %s', (movie_ser,))
                        res = my_cursor.fetchall()
                        if len(res) == 0:
                            print("\nMovie Not Available")
                        else:
                            print("\nMovie is available! Here are the details: ")
                            show_movie(res)

                    elif chc1 == '3':
                        movfod_book(email)

                    elif chc1 == '4':
                        while True:
                            print("\n1. View Bookings")
                            print("2. Cancel Entire Booking")
                            print("3. Cancel Tickets")
                            print("4. Cancel Entire Food Combo")
                            print("5. Cancel Food")
                            print("6. Exit")
                            chc141 = input("Select a operation by selecting a number: ")
                            my_cursor.execute('select Cust_Name from cust_book where Cust_Email = %s', (email, ))
                            res = my_cursor.fetchall()
                            if len(res) != 0:
                                if chc141 == '1':
                                    view_booked_details(email)
                                elif chc141 == '2':
                                    cancel_everything(email, res[0][0])
                                elif chc141 == '3':
                                    cancel_ticket(email, res[0][0])
                                elif chc141 == '4':
                                    total_combo_cancel(email, res[0][0])
                                elif chc141 == '5':
                                    cancel_food(email, res[0][0])
                                elif chc141 == '6':
                                    break
                                else:
                                    print("\nInvalid Selection")
                            elif chc141 =='6':
                                break
                            else:
                                print("\nYou have not booked any movie")
                                break

                    elif chc1 == '5':
                        l = []
                        l1 = []
                        my_cursor.execute('select * from cust_book where Cust_Email = %s', (email,))
                        data = my_cursor.fetchall()
                        sum = 0
                        for i in range(len(data)):
                            sum += int(data[i][10])
                            l1.append(data[i][9])
                            l.append(data[i][8])
                        for i in range(len(data)):
                            DATA = \
                            [
                                ["Movie_ID","", data[i][2]],
                                ["Movie_Name","", data[i][3]],
                                ["Timing","", data[i][4]],
                                ["Total Tickets","", data[i][5]],
                                ["Food & Quantity", str(l), str(l1)],
                                ["Total Ticket Price","", data[i][6]],
                                ["Total Food Price","", sum],
                                ["Total Price (Rs.)","", data[i][11]],

                            ]

                        pdf = SimpleDocTemplate("Billing Invoice.pdf", pagesize=A4)

                        styles = getSampleStyleSheet()

                        title_style = styles["Heading1"]

                        title_style.alignment = 1

                        title = Paragraph("AKVY MOVIES", title_style)

                        style = TableStyle(
                            [
                                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                                ("GRID", (0, 0), (3, 4), 1, colors.black),
                                ("BACKGROUND", (0, 0), (2, 4), colors.indianred),
                                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("BACKGROUND", (0, 5), (2, 6), colors.lightskyblue),
                                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("BACKGROUND", (0, 7), (2, 7), colors.grey),
                                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ]
                        )

                        table = Table(DATA, style=style)

                        pdf.build([title, table])
                        receiver = [data[0][1], "movieticket.booking.4@gmail.com"]
                        yag = yagmail.SMTP("movieticket.booking.4@gmail.com", "akvy@1234")
                        yag.send(
                            to=receiver,
                            subject="Billing Invoice",
                            contents=["Your billing invoice is attached below.", "Billing Invoice.pdf"]
                        )
                        print("Billing Invoice has been sent to your registered Email ID !!")
                        os.remove('Billing invoice.pdf')

                    elif chc1 == '6':
                        while True:
                            print("\n1. View Account")
                            print("2. Modify Name")
                            print("3. Modify Mobile No.")
                            print("4. Modify Password")
                            print("5. Delete Account")
                            print("6. Exit")
                            chc16 = input("Select an option by entering the number: ")

                            if chc16 == '1':
                                while True:
                                    print("\n1. View Personal Details")
                                    print("2. Booking Details")
                                    print("3. Exit")
                                    chc161 = input("Select the operation by selecting number: ")
                                    if chc161 == '1':
                                        my_cursor.execute('select * from Customer where Email = %s', (email,))
                                        res = my_cursor.fetchall()
                                        if len(res) != 0:
                                            print_admin_cust_details(res)
                                        else:
                                            print("\nInvalid Email")
                                    elif chc161 == '2':
                                        my_cursor.execute('select * from cust_book where Cust_Email = %s', (email,))
                                        res = my_cursor.fetchall()
                                        if len(res) != 0:
                                            view_booked_details(res[0][1])
                                        else:
                                            print("\nNo Booking Details!")
                                    elif chc161 == '3':
                                        break
                                    else:
                                        print("\nInvalid Selection")

                            elif chc16 == '2':
                                my_cursor.execute('select Name from Customer where Email = %s', (email, ))
                                res = my_cursor.fetchall()
                                if len(res) != 0:
                                    db_cust_name = input("\nEnter your new name: ")
                                    my_cursor.execute('update Customer set Name = %s where Email = %s', (db_cust_name, email))
                                    print("\nName Updated!")
                                    my_db.commit()
                                else:
                                    print("\nNo changes can be updated as the account registered with {} email id was deleted.".format(email))
                                    customer()


                            elif chc16 == '3':
                                my_cursor.execute('select Mob_No from Customer where Email = %s', (email,))
                                res = my_cursor.fetchall()
                                if len(res) != 0:
                                    db_cust_ph = phone_no()
                                    my_cursor.execute('update Customer set Mob_No = %s where Email = %s', (db_cust_ph, email))
                                    print("\nMobile No. Updated!")
                                    my_db.commit()
                                else:
                                    print("\nNo changes can be updated as the account registered with {} email id was deleted.".format(email))
                                    customer()

                            elif chc16 == '4':
                                my_cursor.execute('select Password from Customer where Email = %s', (email,))
                                res = my_cursor.fetchall()
                                if len(res) != 0:
                                    change_cust_passwd(email)
                                    my_db.commit()
                                else:
                                    print("\nNo changes can be updated as the account registered with {} email id was deleted.".format(email))
                                    customer()

                            elif chc16 == '5':
                                chc185 = input("\nAre you sure you want to delete your account ? (Y/N)").upper()
                                if chc185 == 'Y':
                                    del_acc(email)
                                else:
                                    print("\nOkay.")

                            elif chc16 == '6':
                                break

                            else:
                                print("\nInvalid Selection! Please select a valid option and try again.")

                    elif chc1 == '7':
                        break
                    else:
                        print("\nInvalid Selection! Please select a valid option and try again.")
            else:
                print("\n")
                print(c)

        elif chc == '3':
                break


def menu():
    while True:
        print("\nWelcome to AKVY MOVIES")
        print("~~~~~~~~~~~~~~~~~~~~~~")
        print("1. Admin")
        print("2. Customer")
        print("3. Exit")

        ch = input("Select a user by entering the number: ")

        if ch == '1':
            admin()

        elif ch == '2':
            customer()

        elif ch == '3':
            print("\n")
            print("Software Shutting Down......\n")
            print("Developed By:")
            print("Ambuj \nKoushika \nVijaya \nYash")
            break
        else:
            print("\nInvalid Selection! Please select valid option and try again.")

menu()