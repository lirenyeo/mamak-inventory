import os
import peeweedbevolve
from flask import Flask, render_template, request, flash, redirect, jsonify
from models import db, Store, Warehouse, Product, Discount

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

# @app.route('/products/<p_id>')
# def product_show(p_id):
#     p = Product.get_or_none(Product.id == p_id)
#     # if p_id does not exist
#     if not p:
#         flash('no such product')
#         redirect('/')

#     dc_args = request.args.get('dc')

#     if dc_args:
#         dc_row = Discount.get_or_none(Discount.discount_code == dc_args)
#         if dc_row:
#             dc_multiplier = (100 - dc_row.discount_percentage) / 100
#             return render_template
#         else:
#             return jsonify({
#                 "message": 'Wrong discount code'
#             })
#     else:
#         return redirect

# API ENDPOINT FOR DISCOUNT
@app.route('/api/products/<p_id>')
def api_product_show(p_id):
    p = Product.get_or_none(Product.id == p_id)
    # if p_id does not exist
    if not p:
        return jsonify({
            "message": 'No such product'
        })

    dc_args = request.args.get('dc')

    if dc_args:
        dc_row = Discount.get_or_none(Discount.discount_code == dc_args)
        if dc_row:
            dc_multiplier = (100 - dc_row.discount_percentage) / 100
            return jsonify({
                "name": p.name,
                "description": p.description,
                "originalPrice": p.price,
                "discountedPrice": p.price * dc_multiplier
            })
        else:
            return jsonify({
                "message": 'Wrong discount code'
            })
    else:
        return jsonify({
            "name": p.name,
            "description": p.description,
            "price": p.price
        })



if __name__ == '__main__':
   app.run()