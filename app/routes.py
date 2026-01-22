from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from .models import User, Product
from . import db
import os
from PIL import Image

main = Blueprint('main', __name__)

# --- Public Routes ---

@main.route('/cart/add/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    cart.append(product_id)
    session['cart'] = cart
    flash('Item added to cart!', 'success')
    return redirect(request.referrer or url_for('main.shop'))

@main.route('/cart')
def view_cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', products=[], total=0)
    
    cart_ids = session['cart']
    products = Product.query.filter(Product.id.in_(cart_ids)).all()
    
    # Calculate total and handle quantity (simplified: 1 of each for now or duplicates in list)
    # Better approach: count occurrences if we want quantity, but let's keep it simple: 
    # Just list all items found. If user clicked add twice, ID is there twice.
    # SQL 'in_' will only return unique products. We need to reconstruct the list based on IDs.
    
    cart_products = []
    total = 0
    for pid in cart_ids:
        for p in products:
            if p.id == pid:
                cart_products.append(p)
                total += p.price
                break
                
    return render_template('cart.html', products=cart_products, total=total)

@main.route('/cart/clear')
def clear_cart():
    session.pop('cart', None)
    flash('Cart cleared.', 'info')
    return redirect(url_for('main.view_cart'))

@main.route('/')
def home():
    products = Product.query.order_by(Product.id.desc()).limit(8).all()
    return render_template('index.html', products=products)

@main.route('/shop')
def shop():
    products = Product.query.all()
    return render_template('shop.html', products=products, title='Shop')

@main.route('/search')
def search():
    query = request.args.get('q')
    if query:
        products = Product.query.filter(Product.name.contains(query) | Product.description.contains(query)).all()
    else:
        products = []
    return render_template('shop.html', products=products, title=f'Search Results for "{query}"')

@main.route('/contact')
def contact():
    return render_template('contact.html', title='Contact Us')

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

# --- Admin Routes ---

@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password: # Note: Use hashing in production!
            login_user(user)
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Login Failed. Check username and password.', 'danger')
            
    return render_template('admin_login.html')

@main.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/admin')
@login_required
def admin_dashboard():
    products = Product.query.all()
    return render_template('admin_dashboard.html', products=products)

@main.route('/admin/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            price = request.form.get('price')
            description = request.form.get('description')
            category = request.form.get('category')
            image = request.files.get('image')

            image_data = 'default.jpg'
            if image:
                # Vercel doesn't support local file system persistence. 
                # We convert the image to base64 and store it directly in the DB.
                img_bytes = image.read()
                b64_string = base64.b64encode(img_bytes).decode('utf-8')
                # Determine mime type (simple guess)
                mime_type = 'image/jpeg'
                if image.filename.lower().endswith('.png'):
                    mime_type = 'image/png'
                elif image.filename.lower().endswith('.gif'):
                    mime_type = 'image/gif'
                    
                image_data = f"data:{mime_type};base64,{b64_string}"

            product = Product(name=name, price=float(price), description=description, category=category, image_file=image_data)
            db.session.add(product)
            db.session.commit()
            flash('Product has been created!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating product: {str(e)}', 'danger')
            print(f"ERROR: {e}")  # This will show in Vercel logs
            import traceback
            traceback.print_exc()
        
    return render_template('create_product.html', title='New Product')

@main.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect(url_for('main.admin_dashboard'))
