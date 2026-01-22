from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from .models import User, Product, Order, OrderItem
from . import db
import os
import base64
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random
import string

main = Blueprint('main', __name__)

# Version: 2.0 - WhatsApp Integration + Base64 Images

def generate_order_number():
    """Generate unique order number like ORD-20260122-ABCD"""
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{date_str}-{random_str}"

def send_order_email(order, items):
    """Send order confirmation email to admin"""
    try:
        sender_email = "noreply@bmlifestyle.com"  # Placeholder
        admin_email = "Saleemi31280@gmail.com"
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'New Order Received - {order.order_number}'
        msg['From'] = sender_email
        msg['To'] = admin_email
        
        # Create email body
        items_html = ""
        for item in items:
            items_html += f"<tr><td>{item.product_name}</td><td>{item.quantity}</td><td>Rs {item.product_price}</td></tr>"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #333;">New Order Received!</h2>
            <p><strong>Order Number:</strong> {order.order_number}</p>
            <p><strong>Order Date:</strong> {order.created_at.strftime('%Y-%m-%d %H:%M')}</p>
            
            <h3>Customer Details:</h3>
            <p><strong>Name:</strong> {order.customer_name}</p>
            <p><strong>Email:</strong> {order.customer_email}</p>
            <p><strong>Phone:</strong> {order.customer_phone}</p>
            
            <h3>Delivery Address:</h3>
            <p>{order.delivery_address}<br>{order.city}, {order.postal_code}</p>
            
            <h3>Order Details:</h3>
            <table border="1" cellpadding="8" style="border-collapse: collapse;">
                <tr style="background-color: #f2f2f2;">
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Price</th>
                </tr>
                {items_html}
            </table>
            
            <p><strong>Delivery Method:</strong> {order.delivery_method}</p>
            <p><strong>Payment Method:</strong> {order.payment_method}</p>
            <h3><strong>Total Amount: Rs {order.total_amount}</strong></h3>
            
            <p style="color: #666; margin-top: 20px;">This is an automated notification from BM Lifestyle.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Note: Email sending requires SMTP configuration
        # For now, just print to console (will show in Vercel logs)
        print(f"ORDER EMAIL NOTIFICATION:")
        print(f"To: {admin_email}")
        print(f"Order: {order.order_number}")
        print(f"Customer: {order.customer_name}")
        print(f"Total: Rs {order.total_amount}")
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_whatsapp_notification(order, items):
    """Send WhatsApp notification to admin"""
    try:
        # Format order details for WhatsApp message
        items_text = "\n".join([f"- {item.product_name} x{item.quantity} (Rs {item.product_price})" for item in items])
        
        message = f"""🛍️ *NEW ORDER RECEIVED*

📋 *Order Number:* {order.order_number}
📅 *Date:* {order.created_at.strftime('%Y-%m-%d %H:%M')}

👤 *Customer Details:*
• Name: {order.customer_name}
• Email: {order.customer_email}
• Phone: {order.customer_phone}

📍 *Delivery Address:*
{order.delivery_address}
{order.city}, {order.postal_code}

🛒 *Order Items:*
{items_text}

💰 *Total Amount:* Rs {order.total_amount}
🚚 *Delivery:* {order.delivery_method}
💳 *Payment:* {order.payment_method}"""

        # URL encode the message
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        # WhatsApp API URL
        whatsapp_url = f"https://wa.me/923076379929?text={encoded_message}"
        
        # Log the WhatsApp notification URL (in production, you might use WhatsApp Business API)
        print(f"WHATSAPP NOTIFICATION:")
        print(f"To: +92 307 6379929")
        print(f"Order: {order.order_number}")
        print(f"WhatsApp URL: {whatsapp_url}")
        print(f"\nMessage:\n{message}")
        
        return whatsapp_url
    except Exception as e:
        print(f"WhatsApp error: {e}")
        return None

# --- Public Routes ---

@main.route('/checkout')
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('main.shop'))
    
    cart_ids = session['cart']
    products = Product.query.filter(Product.id.in_(cart_ids)).all()
    
    cart_products = []
    total = 0
    for pid in cart_ids:
        for p in products:
            if p.id == pid:
                cart_products.append(p)
                total += p.price
                break
    
    return render_template('checkout.html', products=cart_products, total=total)

@main.route('/place_order', methods=['POST'])
def place_order():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('main.shop'))
    
    try:
        # Get form data
        customer_name = request.form.get('name')
        customer_email = request.form.get('email')
        customer_phone = request.form.get('phone')
        delivery_address = request.form.get('address')
        city = request.form.get('city')
        postal_code = request.form.get('postal_code')
        delivery_method = request.form.get('delivery_method')
        payment_method = request.form.get('payment_method')
        
        # Calculate total
        cart_ids = session['cart']
        products = Product.query.filter(Product.id.in_(cart_ids)).all()
        
        cart_products = []
        total = 0
        for pid in cart_ids:
            for p in products:
                if p.id == pid:
                    cart_products.append(p)
                    total += p.price
                    break
        
        # Add express delivery fee if selected
        if 'Express' in delivery_method:
            total += 200
        
        # Create order
        order = Order(
            order_number=generate_order_number(),
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            delivery_address=delivery_address,
            city=city,
            postal_code=postal_code,
            delivery_method=delivery_method,
            payment_method=payment_method,
            total_amount=total,
            status='Pending'
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        order_items = []
        for product in cart_products:
            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_price=product.price,
                quantity=1
            )
            order_items.append(item)
            db.session.add(item)
        
        db.session.commit()
        
        # Send email notification
        send_order_email(order, order_items)
        
        # Send WhatsApp notification
        whatsapp_url = send_whatsapp_notification(order, order_items)
        
        # Clear cart
        session.pop('cart', None)
        
        flash(f'Order placed successfully! Order Number: {order.order_number}', 'success')
        return redirect(url_for('main.order_confirmation', order_id=order.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error placing order: {str(e)}', 'danger')
        print(f"Order error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('main.checkout'))

@main.route('/order/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    items = OrderItem.query.filter_by(order_id=order_id).all()
    
    # Generate WhatsApp URL for manual sending
    whatsapp_url = send_whatsapp_notification(order, items)
    
    return render_template('order_confirmation.html', order=order, items=items, whatsapp_url=whatsapp_url)

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
            custom_category = request.form.get('customCategory')
            image = request.files.get('image')

            # Use custom category if "Other" was selected
            if category == 'Other' and custom_category:
                category = custom_category

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
