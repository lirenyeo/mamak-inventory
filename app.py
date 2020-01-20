import os
import peeweedbevolve
from flask import Flask, render_template, request, flash, redirect
from models import db, Store, Warehouse, Product

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET')

@app.before_request
def before_request():
   db.connect()

@app.after_request
def after_request(response):
   db.close()
   return response

@app.cli.command()
def migrate():
   db.evolve(ignore_tables={'base_model'})

@app.route("/")
def index():
    all_stores = Store.select()
    return render_template('home.html', stores=all_stores)

@app.route("/stores", methods=["POST"])
def store_create():
    store_name = request.form.get('store_name')
    store = Store(name=store_name)
    if store.save():
        flash(f"{store_name} has been created!", 'info')
    else:
        flash('Something went wrong!')

    return redirect('/')

@app.route("/stores/<id>")
def store_show(id):
    store = Store.get_by_id(id)
    return render_template('store_show.html', store=store)

@app.route("/warehouses/new")
def warehouse_new():
    return render_template('warehouse_new.html')

@app.route("/warehouses", methods=["POST"])
def warehouse_create():
    location = request.form.get('wh_location')
    wh = Warehouse(location=location, store_id=1)
    if wh.save():
        flash(f"Warehouse at {location} has been created!", 'danger')
    else:
        flash('Something went wrong!')

    return redirect('/')

@app.route("/stores/<id>/delete", methods=["POST"])
def store_delete(id):
    store = Store.get_by_id(id)
    query = Warehouse.delete().where(Warehouse.store_id == id)
    query.execute()
    store.delete_instance()

    return redirect('/')

if __name__ == '__main__':
   app.run()