from flask import Flask,render_template, url_for, request, redirect, session, jsonify, send_file
from just import connection
from datetime import datetime
import hashlib
import secrets
from flask_mail import *
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

#postgres://trackmate:LuMB2jRBLleXqpmyD4Yv7ircnKNYzoXm@dpg-cm1ejjmn7f5s73e849k0-a.singapore-postgres.render.com/trackmate

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']='trackmate360@gmail.com'
app.config['MAIL_PASSWORD']='edlcfbtvgibucjji'
app.config['MAIL_USE_TLS']=True 

mail=Mail(app)
    
app.secret_key = secrets.token_hex(16)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/login')

def login():
    user_id = session.get('user_id')

    if user_id:

        return  redirect('/layout')
    else:
        return 'You are not logged in'
    
def execute_query(query, params=None):
    with connection().cursor() as cursor:
        cursor.execute(query, params)
        result = cursor.fetchall()
    return result

@app.route('/check_user/<string:email>')
def check_user(email):
    query = "SELECT password FROM users WHERE user_email = %s;"
    values = execute_query(query, (email,))
    value = [value[0] for value in values]
    print (f"returned password : {value}")
    return jsonify(value[0])

@app.route('/get_values/<string:attribute>')
def get_values(attribute):
    user_id = session.get('user_id')
    query = "SELECT att_value FROM attributes WHERE att_name = %s AND u_id = %s;"
    values = execute_query(query, (attribute,user_id))
    values = [value[0] for value in values]
    return jsonify(values)

@app.route('/get_brands/<string:category>')
def get_brands(category):
    user_id = session.get('user_id')
    query = "SELECT distinct brand_name FROM products WHERE cat_name = %s AND u_id = %s;"
    brands = execute_query(query, (category,user_id))
    brands = [value[0] for value in brands]
    return jsonify(brands)

@app.route('/get_products/<string:category>/<string:brand>')
def get_products(category,brand):
    user_id = session.get('user_id')
    query = "SELECT pro_name,att_value,price,sold_as FROM products WHERE cat_name = %s AND u_id = %s AND brand_name = %s ;"
    data = execute_query(query, (category,user_id,brand))
    data = [{'pro_name' : value[0], 'att_value' : value[1], 'price' : value[2], 'soldas' : value[3]} for value in data]
    return jsonify(data)

@app.route('/get_stock/<string:category>/<string:brand>/<string:product>')
def get_stock(category,brand,product):
    user_id = session.get('user_id')
    print("Value of product:", product)

    pro_name, att_value, price, soldas = product.split(',')
    print (f"Selected Product in javascript: {pro_name}, Attribute: {att_value}, Price: {price}, Sold_as : {soldas}")

    query = "SELECT inventory FROM products WHERE cat_name = %s AND u_id = %s AND pro_name = %s AND brand_name = %s;"
    stocks = execute_query(query, (category,user_id,pro_name,brand))
    data = [stock[0] for stock in stocks]

    return jsonify(data)

@app.route('/info/<string:mail>/<string:pwd>')


        

@app.route('/info',methods=['GET','POST'])

def info():
    if request.method == 'POST':
        mail = request.form['mail']
        pwd = request.form['pwd']

        conn = connection()
        cursor = conn.cursor()

        # Insert user using raw SQL query
        sql_query = "SELECT id FROM users WHERE user_email = %s AND password = %s;"
        cursor.execute(sql_query, (mail,pwd))

        user_id = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if user_id:
            # Store the user_id in the session
            session['user_id'] = user_id[0]
            return redirect('/login')
        else:
            return 'Invalid email or password'
        
    else:
        return render_template('demo.html')

@app.route('/categories', methods=['POST','GET'])

def categories():
    
    if request.method == 'POST':
        task_cont = request.form['content']
        
        user_id = session.get('user_id')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT cat_id FROM categories WHERE u_id = %s AND cat_name = %s;"
        cursor.execute(qry,(user_id,task_cont))

        res = cursor.fetchone()

        if res:
            return 'this data already exists...'
        else :
            sql_query = "INSERT INTO categories (u_id,cat_name) VALUES (%s,%s);"
            cursor.execute(sql_query, (user_id,task_cont))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/categories')
        except:
            return 'There was an issue'
        

    else:
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT * FROM categories WHERE u_id = %s ORDER BY cat_name;"                
        cursor.execute(qry,(user_id,))
        tasks = cursor.fetchall()

        print(f"Task retrieved: {tasks}")

        task_data = [{'cat_id': task[0],'cat_name': task[1]} for task in tasks]

        return render_template('categories.html',tasks=task_data)   


@app.route('/update1/<int:id>', methods=['GET','POST'])

def update1(id):

    conn = connection()
    cursor = conn.cursor()

    qry = "SELECT * FROM categories WHERE cat_id =%s;"
    cursor.execute(qry,(id,))
    task = cursor.fetchone() 

    print(f"Task retrieved: {task}")


    if request.method == 'POST':
        new_cont = request.form['content']

        qry = "UPDATE categories SET cat_name = %s WHERE cat_id = %s;"
        cursor.execute(qry,(new_cont,id))
        
        try:
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/view_categories')
        
        except:
            return 'There was an issue'
        
    else:
        return render_template('add.html',task={'cat_id': task[0], 'cat_name': task[1]})
    
@app.route('/delete1/<int:id>')

def delete1 (id):
        conn = connection()
        cursor = conn.cursor()

        sql_query = "DELETE FROM categories WHERE cat_id = %s;"
        cursor.execute(sql_query, (id,))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/view_categories')
        
        except:
            return 'There was a problem in deleting that task'


@app.route('/brands', methods=['POST','GET'])

def index2():
    
    if request.method == 'POST':
        task_cont = request.form['content']
        
        user_id = session.get('user_id')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT brand_id FROM brands WHERE u_id = %s AND brand_name = %s;"
        cursor.execute(qry,(user_id,task_cont))

        res = cursor.fetchone()

        if res:
            return 'this brand already exists...'
        else :
            sql_query = "INSERT INTO brands (u_id,brand_name) VALUES (%s,%s);"
            cursor.execute(sql_query, (user_id,task_cont))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/brands')
        except:
            return 'There was an issue'
        

    else:
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT * FROM brands WHERE u_id = %s ORDER BY brand_name;"                
        cursor.execute(qry,(user_id,))
        tasks = cursor.fetchall()

        print(f"Task retrieved: {tasks}")

        task_data = [{'b_id': task[1],'b_name': task[2]} for task in tasks]

        return render_template('brands.html',tasks=task_data) 

@app.route('/update2/<int:id>', methods=['GET','POST'])  

def update2(id):

    conn = connection()
    cursor = conn.cursor()

    qry = "SELECT * FROM brands WHERE brand_id =%s;"
    cursor.execute(qry,(id,))
    task = cursor.fetchone() 

    print(f"Task retrieved: {task}")


    if request.method == 'POST':
        new_cont = request.form['content']

        qry = "UPDATE brands SET brand_name = %s WHERE brand_id = %s;"
        cursor.execute(qry,(new_cont,id))
        
        try:
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/view_brands')
        
        except:
            return 'There was an issue'
        
    else:
        return render_template('add1.html',task={'b_id': task[1], 'b_name': task[2]})
    
@app.route('/delete2/<int:id>')

def delete2 (id):
        conn = connection()
        cursor = conn.cursor()

        sql_query = "DELETE FROM brands WHERE brand_id = %s;"
        cursor.execute(sql_query, (id,))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/view_brands')
        
        except:
            return 'There was a problem in deleting that task'
        


@app.route('/attributes', methods=['POST','GET'])

def index3():
    
    if request.method == 'POST':
        att_name = request.form['content']
        att_value = request.form['val']
        
        user_id = session.get('user_id')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT att_id FROM attributes WHERE u_id = %s AND att_name = %s AND att_value = %s;"
        cursor.execute(qry,(user_id,att_name,att_value))

        res = cursor.fetchone()

        if res:
            return 'this attribute and value pair already exists...'
        else :
            sql_query = "INSERT INTO attributes (u_id,att_name,att_value) VALUES (%s,%s,%s);"
            cursor.execute(sql_query, (user_id,att_name,att_value))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/attributes')
        except:
            return 'There was an issue'
        

    else:
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT * FROM attributes WHERE u_id = %s ORDER BY att_name,att_value;"                
        cursor.execute(qry,(user_id,))
        tasks = cursor.fetchall()

        print(f"Task retrieved: {tasks}")

        task_data = [{'att_id': task[1],'att_name': task[2], 'att_value' : task[3]} for task in tasks]

        return render_template('attributes.html',tasks=task_data) 

@app.route('/update3/<int:id>', methods=['GET','POST'])  

def update3(id):

    conn = connection()
    cursor = conn.cursor()

    qry = "SELECT * FROM attributes WHERE att_id =%s;"
    cursor.execute(qry,(id,))
    task = cursor.fetchone() 

    print(f"Task retrieved: {task}")


    if request.method == 'POST':
        new_cont = request.form['content']
        new_val = request.form['val']

        qry = "UPDATE attributes SET att_name = %s,att_value = %s WHERE att_id = %s;"
        cursor.execute(qry,(new_cont,new_val,id))
        
        try:
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/view_attributes')
        
        except:
            return 'There was an issue'
        
    else:
        return render_template('add3.html',task={'att_id': task[1], 'att_name': task[2], 'att_value': task[3]})
    
@app.route('/delete3/<int:id>')

def delete3(id):
        conn = connection()
        cursor = conn.cursor()

        sql_query = "DELETE FROM attributes WHERE att_id = %s;"
        cursor.execute(sql_query, (id,))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/view_attributes')
        
        except:
            return 'There was a problem in deleting that task'


@app.route('/products', methods=['POST','GET'])

def index4():
    
    if request.method == 'POST':

        item = request.form['item']
        cat = request.form.get('cat')
        brand = request.form.get('brand')
        att_name = request.form.get('att_name')
        att_val = request.form.get('att_value')
        inventory = request.form['invent']
        soldas = request.form['soldas']
        price = request.form['price']
        tax = request.form['tax']

        
        user_id = session.get('user_id')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT pro_id FROM products WHERE u_id = %s AND pro_name = %s AND cat_name = %s AND brand_name = %s;"
        cursor.execute(qry,(user_id,item,cat,brand))

        res = cursor.fetchone()

        if res:
            return 'this product already exists...'
        else :
            sql_query = "INSERT INTO products (u_id,pro_name,cat_name,brand_name,att_name,att_value,inventory,price,tax,sold_as) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            cursor.execute(sql_query, (user_id,item,cat,brand,att_name,att_val,inventory,price,tax,soldas))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/products')
        except:
            return 'There was an issue'
        

    else:
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT * FROM products WHERE u_id = %s ORDER BY pro_name,cat_name,brand_name;"                
        cursor.execute(qry,(user_id,))
        tasks = cursor.fetchall()

        cursor.close()

        cursor = conn.cursor()

        qry1 = "SELECT cat_name FROM categories WHERE u_id = %s ORDER BY cat_name;"
        cursor.execute(qry1,(user_id,))

        cats = cursor.fetchall()

        cursor.close()

        cursor = conn.cursor()

        qry2 = "SELECT brand_name FROM brands WHERE u_id = %s ORDER BY brand_name;"
        cursor.execute(qry2,(user_id,))

        brands = cursor.fetchall()

        
        qry3 = "SELECT distinct att_name FROM attributes WHERE u_id = %s ORDER BY att_name;"

        cursor.execute(qry3,(user_id,))

        atts_name = cursor.fetchall()

        cursor.close()
        cursor = conn.cursor()

        print(f"Task retrieved: {tasks}")

        task_data = [{'pro_id': task[1],'pro_name': task[2], 'cat' : task[3], 'brand' : task[4], 'att_name' : task[5], 'att_value' : task[6],'inventory' : task[7],'price' : task[8],'tax' : task[9],'soldas' : task[10]} for task in tasks]
        cat_data = [cat[0] for cat in cats]
        brand_data = [brand[0] for brand in brands]
        att_name_data = [atts_name[0] for atts_name in atts_name]

        return render_template('products.html',tasks=task_data,cat=cat_data,brand=brand_data,atts_name = att_name_data) 

@app.route('/update4/<int:id>', methods=['GET','POST'])  

def update4(id):
    if request.method == 'POST':

        conn = connection()

        item = request.form['item']
        cat = request.form.get('cat')
        brand = request.form.get('brand')
        att_name = request.form.get('att_name')
        att_val = request.form.get('att_value')
        invent = request.form['invent']
        soldas = request.form['soldas']
        price = request.form['price']
        tax = request.form['tax']

        cursor = conn.cursor()

        qry3 = "UPDATE products SET pro_name = %s,cat_name = %s, brand_name = %s,inventory = %s, price = %s, tax = %s, sold_as = %s, att_name = %s, att_value = %s WHERE pro_id = %s;"
        cursor.execute(qry3,(item,cat,brand,invent,price,tax,soldas,att_name,att_val,id))

        try:
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/view_products')
        
        except:
            return 'There was an issue'
        
    else:
        user_id = session.get('user_id')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT * FROM products WHERE pro_id =%s;"
        cursor.execute(qry,(id,))
        task = cursor.fetchone() 

        cursor.close()

        cursor = conn.cursor()

        qry1 = "SELECT cat_name FROM categories WHERE u_id = %s ORDER BY cat_name;"
        cursor.execute(qry1,(user_id,))

        cats = cursor.fetchall()

        cursor.close()

        cursor = conn.cursor()

        qry2 = "SELECT brand_name FROM brands WHERE u_id = %s ORDER BY brand_name;"
        cursor.execute(qry2,(user_id,))

        brands = cursor.fetchall()

        qry3 = "SELECT distinct att_name FROM attributes WHERE u_id = %s ORDER BY att_name;"

        cursor.execute(qry3,(user_id,))

        atts_name = cursor.fetchall()

        cursor.close()
        cursor = conn.cursor()

        print(f"Task retrieved: {task}")

        task_data = {'pro_id': task[1],'pro_name': task[2],'cat' : task[3],'brand'  :  task[6],'invent' : task[7],'price' : task[8],'tax' : task[9],'soldas' : task[10]}
        cat_data = [cat[0] for cat in cats]
        brand_data = [brand[0] for brand in brands]
        att_name_data = [atts_name[0] for atts_name in atts_name]

        conn.commit()
        cursor.close()
        conn.close()

        return render_template('add4.html',task=task_data,cat=cat_data,brand=brand_data,att_name = att_name_data ) 
    
@app.route('/delete4/<int:id>')

def delete4(id):
        conn = connection()
        cursor = conn.cursor()

        sql_query = "DELETE FROM products WHERE pro_id = %s;"
        cursor.execute(sql_query, (id,))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/view_products')
        
        except:
            return 'There was a problem in deleting that task'

def calculate(pro_name,cat,brand):

    qry = "SELECT price,tax FROM products WHERE pro_name = %s AND cat_name = %s AND brand_name = %s;"
    res = execute_query(qry,(pro_name,cat,brand))

    if res:
        price = res[0][0]
        tax = res[0][1]
        ans = price * (tax / 100)
        print (f"tax_price  = {ans+price}")
        return ans+price
    else:
        print("failed")
        return 0

@app.route('/sales', methods=['POST','GET'])

def index5():
    
    if request.method == 'POST':

        cat = request.form.get('cat')
        brand = request.form.get('brand')
        product = request.form.get('value')

        print("Value of product:", product)

        pro_name, att_value, price, soldas = product.split(',')

        print (f"Selected Product: {pro_name}, Attribute: {att_value}, Price: {price}, Sold_as : {soldas}")


        quantity = request.form['quantity']
        date = request.form['date']

        tax_price = float(calculate(pro_name, cat, brand))
        total_price = tax_price * int(quantity)

        tax_less_total = int(quantity) * float(price)

        
        user_id = session.get('user_id')

        conn = connection()
        cursor = conn.cursor()

        # qry = "SELECT pro_id FROM products WHERE u_id = %s AND pro_name = %s AND cat_name = %s AND brand_name = %s;"
        # cursor.execute(qry,(user_id,item,cat,brand))

        # res = cursor.fetchone()

        # if res:
        #     return 'this product already exists...'
        # else :
        drop_trigger()
        create_trigger()
        sql_query = "INSERT INTO sales (u_id,cat_name,brand_name,pro_name,att_value,tax_less_total,total_price,quantity,sales_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        
        cursor.execute(sql_query, (user_id,cat,brand,pro_name,att_value,tax_less_total,total_price,quantity,date))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/sales')
        except:
            return 'There was an issue'
        

    else:
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        qry = "SELECT sales_id,sales.pro_name,sales.att_value,price,sold_as,quantity,total_price FROM sales INNER JOIN products USING (pro_name,cat_name,brand_name) WHERE sales.u_id = %s ORDER BY sales_date;"
        sales = execute_query(qry,(user_id,))

        qry1 = "SELECT cat_name FROM categories WHERE u_id = %s ORDER BY cat_name;"
        cats = execute_query(qry1,(user_id,))


        qry2 = "SELECT brand_name FROM brands WHERE u_id = %s ORDER BY brand_name;"
        brands = execute_query(qry2,(user_id,))

        qry3 = "SELECT pro_id,pro_name,att_value,price,sold_as FROM products WHERE u_id = %s ORDER BY pro_name;"
        pros = execute_query(qry3,(user_id,))


        print(f"Task retrieved: {sales}")

        sales_data = [{'sales_id': task[0],'pro_name': task[1], 'att_value' : task[2], 'price' : task[3], 'soldas' : task[4], 'quantity' : task[5], 'total' : task[6]} for task in sales]
        cat_data = [cat[0] for cat in cats]
        brand_data = [brand[0] for brand in brands]
        pro_drop_data = [{'pro_name' : task[1], 'att_value' : task[2], 'price' : task[3] , 'soldas' : task[4]} for task in pros]

        return render_template('sales.html',sales=sales_data,cat=cat_data,brand=brand_data,product = pro_drop_data) 

@app.route('/delete_sales/<int:id>')

def delete5(id):
        conn = connection()
        cursor = conn.cursor()

        sql_query = "DELETE FROM sales WHERE sales_id = %s;"
        cursor.execute(sql_query, (id,))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/sales')
        
        except:
            return 'There was a problem in deleting that task'
        
@app.route('/update_sales/<int:id>', methods=['GET','POST'])  

def update_sales(id):

    if request.method == 'POST':
        conn = connection()

        cat = request.form.get('cat')
        brand = request.form.get('brand')
        product = request.form.get('value')

        print("Value of product:", product)

        pro_name, att_value, price, soldas = product.split(',')

        print (f"Selected Product: {pro_name}, Attribute: {att_value}, Price: {price}, Sold_as : {soldas}")

        quantity = request.form['quantity']
        date = request.form['date']

        tax_price = float(calculate(pro_name, cat, brand))
        total_price = tax_price * int(quantity)

        tax_less_total = int(quantity) * float(price)

        cursor = conn.cursor()

        qry3 = "UPDATE sales SET pro_name = %s,cat_name = %s, brand_name = %s,quantity = %s, price = %s, tax_less_total = %s, total_price = %s, sold_as = %s, att_value = %s, sales_date = %s WHERE pro_id = %s;"
        cursor.execute(qry3,(pro_name,cat,brand,quantity,price,tax_less_total,total_price,soldas,att_value,date,id))

        try:
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/products')
        
        except:
            return 'There was an issue'
        
    else:
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        qry = "SELECT sales_id,sales.pro_name,sales.att_value,price,sold_as,quantity,total_price,sales_date FROM sales INNER JOIN products USING (pro_name,cat_name,brand_name) WHERE sales.u_id = %s ORDER BY sales_date;"
        sales = execute_query(qry,(user_id,))

        qry1 = "SELECT cat_name FROM categories WHERE u_id = %s ORDER BY cat_name;"
        cats = execute_query(qry1,(user_id,))


        qry2 = "SELECT brand_name FROM brands WHERE u_id = %s ORDER BY brand_name;"
        brands = execute_query(qry2,(user_id,))

        qry3 = "SELECT pro_id,pro_name,att_value,price,sold_as FROM products WHERE u_id = %s ORDER BY pro_name;"
        pros = execute_query(qry3,(user_id,))


        print(f"Task retrieved: {sales}")

        sales_data = [{'sales_id': task[0],'pro_name': task[1], 'att_value' : task[2], 'price' : task[3], 'soldas' : task[4], 'quantity' : task[5], 'total' : task[6], 'date' : task[7]} for task in sales]
        cat_data = [cat[0] for cat in cats]
        brand_data = [brand[0] for brand in brands]
        pro_drop_data = [{'pro_name' : task[1], 'att_value' : task[2], 'price' : task[3] , 'soldas' : task[4]} for task in pros]

        return render_template('update_sales.html',sales=sales_data,cat=cat_data,brand=brand_data,product = pro_drop_data) 

@app.route('/invent')

def invent():
    user_id = session.get('user_id')
    print (f'your user id is {user_id}')


    qry = "SELECT sales.pro_name,sales.att_value,price,sold_as,total_price,tax,price+price*tax/100 as selling_price,inventory,sales.quantity FROM sales INNER JOIN products USING (pro_name,cat_name,brand_name) WHERE sales.u_id = %s GROUP BY sales.pro_name,sales.att_value,price,sold_as,total_price,tax,price+price*tax/100,inventory,sales.quantity;"
    sales = execute_query(qry,(user_id,))

    sales_data = [{'pro_name': task[0], 'att_value' : task[1], 'price' : task[2], 'soldas' : task[3], 'total' : task[4],'tax' : task[5],'sell' : task[6],'invent' : task[7],'quantity' : task[8]} for task in sales]

    qry = "SELECT sales.pro_name,sales.att_value,price,sold_as,total_price,tax,price+price*tax/100 as selling_price,inventory,sales.quantity FROM sales INNER JOIN products USING (pro_name,cat_name,brand_name) WHERE sales.u_id = 1 GROUP BY sales.pro_name,sales.att_value,price,sold_as,total_price,tax,price+price*tax/100,inventory,sales.quantity;"
    sales = execute_query(qry,(user_id,))

    sales_data = [{'pro_name': task[0], 'att_value' : task[1], 'price' : task[2], 'soldas' : task[3], 'total' : task[4],'tax' : task[5],'sell' : task[6],'invent' : task[7], 'quantity' : task[8]} for task in sales]


    return render_template('inventory.html',tasks = sales_data)

@app.route('/purchases')

def purchases():
    user_id = session.get('user_id')
    print (f'your user id is {user_id}')

    qry = "SELECT * FROM purchases WHERE u_id = %s ORDER BY pro_name,cat_name,brand_name;"                
    sales = execute_query(qry,(user_id,))

    sales_data = [{'pro_id': task[1],'pro_name': task[2], 'cat' : task[3], 'brand' : task[4], 'att_name' : task[5], 'att_value' : task[6],'inventory' : task[7],'price' : task[8],'tax' : task[9],'soldas' : task[10],'pur_id': task[11]} for task in sales]

    return render_template('purchase.html',tasks = sales_data)

@app.route('/delete_purchase/<int:id>')

def delete_purchase(id):
        conn = connection()
        cursor = conn.cursor()

        sql_query = "DELETE FROM purchases WHERE pur_id = %s;"
        cursor.execute(sql_query, (id,))

        try:

            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/purchases')
        
        except:
            return 'There was a problem in deleting that task'

@app.route('/layout')

def layout():
    user_id = session.get('user_id')
    qry = "SELECT sum(tax_less_total),sum(total_price),sum(total_price-tax_less_total) FROM sales WHERE u_id = %s;"
    final = execute_query(qry,(user_id,))
    final_data = [{'expense': task[0],'income': task[1], 'profit' : task[2]} for task in final]

    qry1 = "SELECT count(*) FROM sales WHERE u_id = %s;"
    count = execute_query(qry1,(user_id,))
    count_data = [{'count': task[0]} for task in count]

    return render_template('layout.html',data = final_data,count = count_data)

@app.route('/attributes')

def attributes():
    return render_template('attributes.html')

@app.route('/inventory')

def inventory():
    return render_template('inventory.html')

@app.route('/brands')

def brands():
    return render_template('brands.html')

@app.route('/products')

def products():
    return render_template('products.html')

@app.route('/sales')

def sales():
    return render_template('sales.html')

@app.route('/reports')

def reports():
    return render_template('reports.html')

@app.route("/demo")
def demo():
     return render_template('demo.html')

@app.route("/charts")
def charts():
     return render_template('chart.html')

@app.route("/")
def landing():
     return render_template('landing.html')

@app.route("/view_categories")
def view_categories():
    user_id = session.get('user_id')
    print (f'your user id is {user_id}')

    conn = connection()
    cursor = conn.cursor()

    qry = "SELECT * FROM categories WHERE u_id = %s ORDER BY cat_name;"                
    cursor.execute(qry,(user_id,))
    tasks = cursor.fetchall()

    print(f"Task retrieved: {tasks}")

    task_data = [{'cat_id': task[0],'cat_name': task[1]} for task in tasks]

    return render_template('view_categories.html',tasks=task_data)


@app.route("/view_brands")
def view_brands():
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT * FROM brands WHERE u_id = %s ORDER BY brand_name;"                
        cursor.execute(qry,(user_id,))
        tasks = cursor.fetchall()

        print(f"Task retrieved: {tasks}")

        task_data = [{'b_id': task[1],'b_name': task[2]} for task in tasks]

        return render_template('view_brands.html',tasks=task_data)

@app.route("/view_attributes")
def view_attributes():
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT * FROM attributes WHERE u_id = %s ORDER BY att_name,att_value;"                
        cursor.execute(qry,(user_id,))
        tasks = cursor.fetchall()

        print(f"Task retrieved: {tasks}")

        task_data = [{'att_id': task[1],'att_name': task[2], 'att_value' : task[3]} for task in tasks]

        return render_template('view_attributes.html',tasks=task_data) 

@app.route("/view_products")
def view_products():
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        conn = connection()
        cursor = conn.cursor()

        qry = "SELECT * FROM products WHERE u_id = %s ORDER BY pro_name,cat_name,brand_name;"                
        cursor.execute(qry,(user_id,))
        tasks = cursor.fetchall()

        cursor.close()


        print(f"Task retrieved: {tasks}")

        task_data = [{'pro_id': task[1],'pro_name': task[2], 'cat' : task[3], 'brand' : task[4], 'att_name' : task[5], 'att_value' : task[6],'inventory' : task[7],'price' : task[8],'tax' : task[9],'soldas' : task[10]} for task in tasks]


        return render_template('view_products.html',tasks=task_data) 
@app.route("/view_sales")
def view_sales():
        user_id = session.get('user_id')
        print (f'your user id is {user_id}')

        qry = "SELECT sales_id,sales.pro_name,sales.att_value,price,sold_as,quantity,total_price FROM sales INNER JOIN products USING (pro_name,cat_name,brand_name) WHERE sales.u_id = %s ORDER BY sales_date;"
        sales = execute_query(qry,(user_id,))

        qry1 = "SELECT cat_name FROM categories WHERE u_id = %s ORDER BY cat_name;"
        cats = execute_query(qry1,(user_id,))


        qry2 = "SELECT brand_name FROM brands WHERE u_id = %s ORDER BY brand_name;"
        brands = execute_query(qry2,(user_id,))

        qry3 = "SELECT pro_id,pro_name,att_value,price,sold_as FROM products WHERE u_id = %s ORDER BY pro_name;"
        pros = execute_query(qry3,(user_id,))

        qry4 = '''
                    WITH MaxCountCTE AS (
                        SELECT COUNT(*) AS max_count
                        FROM sales
                        INNER JOIN products USING (pro_name)
                        WHERE sales.u_id = %s
                        GROUP BY pro_id
                        ORDER BY max_count DESC
                        LIMIT 1
                    )

                    SELECT pro_name AS count
                    FROM sales
                    INNER JOIN products USING (pro_name)
                    GROUP BY pro_name
                    HAVING COUNT(*) = (SELECT max_count FROM MaxCountCTE);
                    '''
        maxsale = execute_query(qry4,(user_id,))

        print(f"Task retrieved: {sales}")
        max_sale = [{'pro_name':task[0]} for task in maxsale]
        sales_data = [{'sales_id': task[0],'pro_name': task[1], 'att_value' : task[2], 'price' : task[3], 'soldas' : task[4], 'quantity' : task[5], 'total' : task[6]} for task in sales]
        cat_data = [cat[0] for cat in cats]
        brand_data = [brand[0] for brand in brands]
        pro_drop_data = [{'pro_name' : task[1], 'att_value' : task[2], 'price' : task[3] , 'soldas' : task[4]} for task in pros]

        return render_template('view_sales.html',sales=sales_data,cat=cat_data,brand=brand_data,product = pro_drop_data,maxsale=max_sale) 



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.clear()
    return render_template('landing.html')

@app.route("/contact" , methods=['POST','GET'])
def contact():
     if request.method == "POST":
         name= request.form["name"]
         email= request.form["userEmail"]
         sub= request.form["sub"]
         message= request.form["usermessage"]

         users=[{'name':name,'email':email,'msg': message}]

     with mail.connect() as con:
         for user in users:
             msg1="Hello I am %s my idea is %s email: %s" % (user ['name'] , user['msg'], user['email'])
             msgs=Message(recipients=['trackmate360@gmail.com'], body=msg1, subject="imp mail", sender="your created email id")
             con.send(msgs)

     msg= Message(sub,sender='trackmate360@gmail.com',recipients=['trackmate360@gmail.com'])
     msg.body=msg1
     mail.send(msg)

     return render_template('thank.html',name=name)

def create_function():
    conn = connection()
    cursor = conn.cursor()
    qry="CREATE OR REPLACE FUNCTION change_invent() RETURNS TRIGGER AS $$ BEGIN UPDATE products SET inventory = inventory - NEW.quantity FROM sales WHERE products.pro_name = NEW.pro_name AND products.brand_name = NEW.brand_name  AND  products.cat_name = NEW.cat_name ;RETURN NEW; END; $$ LANGUAGE plpgsql;"
    cursor.execute(qry)

def create_trigger():
    conn = connection()
    cursor = conn.cursor()
    qry="CREATE OR REPLACE FUNCTION change_invent() RETURNS TRIGGER AS $$ BEGIN UPDATE products SET inventory = inventory - NEW.quantity FROM sales WHERE products.pro_name = NEW.pro_name AND products.brand_name = NEW.brand_name  AND  products.cat_name = NEW.cat_name ;RETURN NEW; END; $$ LANGUAGE plpgsql;"
    cursor.execute(qry)
    qry1 = '''CREATE OR REPLACE FUNCTION create_purchase_table()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'purchases') THEN
                EXECUTE 'CREATE TABLE purchases AS SELECT * FROM products WHERE false;';
            END IF;

            INSERT INTO purchases SELECT * FROM products WHERE pro_id = NEW.pro_id AND inventory = 0;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql'''
    cursor.execute(qry1)
    cursor = conn.cursor()
    qry2="CREATE TRIGGER after_sales_update AFTER INSERT OR UPDATE ON sales FOR EACH ROW EXECUTE FUNCTION change_invent();"
    cursor.execute(qry2)
    qry3="CREATE TRIGGER check_inventory_trigger AFTER UPDATE ON products FOR EACH ROW WHEN (new.inventory = 0 AND old.inventory > 0) EXECUTE FUNCTION create_purchase_table();"
    cursor.execute(qry3)
    conn.commit()
    cursor.close()
    conn.close()


def drop_trigger():
    conn = connection()
    cursor = conn.cursor()
    qry="DROP TRIGGER IF EXISTS after_sales_update ON sales;"
    cursor.execute(qry)
    qry1="DROP TRIGGER IF EXISTS check_inventory_trigger ON products;"
    cursor.execute(qry1)
    conn.commit()
    cursor.close()
    conn.close()


@app.route('/get_data_from_db')
def get_data_from_db():

    user_id = session.get('user_id')
    conn = connection()
    cursor = conn.cursor()

    # Execute a query to fetch data
    cursor.execute('SELECT quantity,total_price FROM sales WHERE u_id = %s;',(user_id,))
    data = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    # Convert the data to a JSON format
    data_json = [{'column1': row[0], 'column2': row[1]} for row in data]

    return jsonify(data_json)


@app.route('/get_sales_data_from_db')
def get_sales_data_from_db():

    user_id = session.get('user_id')
    conn = connection()
    cursor = conn.cursor()

    # Execute a query to fetch data
    cursor.execute('SELECT sales_date,count(*) as num_sales FROM sales WHERE u_id = %s GROUP BY sales_date ORDER BY sales_date;',(user_id,)  )
    data = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    # Convert the data to a JSON format
    data_json = [{'date_of_sales': row[0], 'number_of_sales': row[1]} for row in data]

    return jsonify(data_json)



def generate_excel(date,date1):
    user_id = session.get('user_id')
    try:
        
        conn = connection()

 
        query = f"SELECT * FROM sales WHERE sales_date between '{date}' and '{date1}' and u_id= {user_id}"
        df = pd.read_sql_query(query, conn)

    
        conn.commit()

       
        excel_filename = f"report_{date}.xlsx"

        
        df.to_excel(excel_filename, index=False)

        return excel_filename

    except Exception as e:
        return f"Error: {e}"

def convert_excel_to_pdf(excel_filename, pdf_filename):
    df = pd.read_excel(excel_filename)

  
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)

   
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data, repeatRows=1)

 
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#44195e'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#E5D4FF'),
    ])

    table.setStyle(style)

   
    elements = [table]
    pdf.build(elements)

    pdf_buffer.seek(0)

   
    with open(pdf_filename, 'wb') as pdf_file:
        pdf_file.write(pdf_buffer.read())

@app.route("/reports")
def index():
    return render_template('reports.html')

@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    try:
      
        date = request.form.get("date")
        date1 = request.form.get("date1")

      
        excel_filename = generate_excel(date,date1)

       
        pdf_filename = f"report_{date}.pdf"

       
        convert_excel_to_pdf(excel_filename, pdf_filename)

        
        return send_file(pdf_filename, as_attachment=True)

    except Exception as e:
        return f"Error: {e}"

@app.route('/create_tables')

def create_tables():
    conn = connection()
    cursor = conn.cursor()

    users = '''

        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR,
            password VARCHAR,
            user_email VARCHAR
        );'''


    cats = '''CREATE TABLE categories (
    cat_id SERIAL,
    cat_name VARCHAR(255) NOT NULL,
    u_id INTEGER NOT NULL,
    FOREIGN KEY (u_id) REFERENCES users(id),
    PRIMARY KEY(u_id,cat_name)
    );'''


    atts =  '''CREATE TABLE attributes (
            u_id INTEGER REFERENCES users(id),
            att_id SERIAL,
            att_name VARCHAR(255),
            att_value VARCHAR(255)
        );'''


    brands = '''CREATE TABLE brands (
        u_id INTEGER REFERENCES users(id),
        brand_id SERIAL,
        brand_name VARCHAR(255)
    );'''


    purch = '''CREATE TABLE purchases (
        u_id INTEGER,
        pro_id INTEGER,
        pro_name VARCHAR(255),
        cat_name VARCHAR(255),
        brand_name VARCHAR(255),
        att_name VARCHAR,
        att_value VARCHAR,
        inventory INTEGER,
        price REAL,
        tax REAL,
        sold_as VARCHAR,
        pur_id SERIAL PRIMARY KEY
    );'''


    pro = '''CREATE TABLE products (
        u_id INTEGER REFERENCES users(id),
        pro_id SERIAL PRIMARY KEY,
        pro_name VARCHAR(255),
        cat_name VARCHAR(255),
        brand_name VARCHAR(255),
        att_name VARCHAR,
        att_value VARCHAR,
        inventory INTEGER,
        price REAL,
        tax REAL,
        sold_as VARCHAR
    );'''


    sales = '''CREATE TABLE sales (
        u_id INTEGER,
        sales_id SERIAL PRIMARY KEY,
        cat_name VARCHAR,
        brand_name VARCHAR,
        pro_name VARCHAR,
        att_value VARCHAR,
        quantity INTEGER,
        tax_less_total REAL,
        total_price REAL,
        sales_date DATE
    );'''

    cursor.execute(users)
    cursor.execute(cats)
    cursor.execute(brands)
    cursor.execute(atts)
    cursor.execute(pro)
    cursor.execute(sales)
    cursor.execute(purch)


    conn.commit()
    cursor.close()
    conn.close()

    return "success"

if __name__=='__main__':
     app.run(debug=True)


#     conn.commit()
#     cursor.close()
#     conn.close()

#     return "success"

# @app.errorhandler(500)
# def internal_server_error(e):
#     app.logger.error(f"Internal Server Error: {e}")
#     return render_template("500.html"), 500

# if __name__ == "__main__":
#     app.run(debug=True)




