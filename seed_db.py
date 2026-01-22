from app import create_app, db
from app import create_app, db
from app.models import User, Product

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin', password='password123') 
        db.session.add(user)
        db.session.commit()
        print("Admin user created: admin/password123")
    else:
        print("Admin user already exists")

    if not Product.query.filter_by(name='Regalia Textile Unstitched').first():
        p1 = Product(
            name='Regalia Textile Unstitched',
            price=4000.0,
            description='Embroided Lawn 3Piece suit. Summer collection.',
            category='Summer Collection',
            image_file='default.jpg' 
        )
        db.session.add(p1)
        db.session.commit()
        print("Added product: Regalia Textile Unstitched")

    # Add more sample products if they don't exist
    sample_products = [
        {"name": "Luxury Silk Tunic", "price": 5500.0, "category": "Clothes", "desc": "Premium silk tunic for evening wear."},
        {"name": "Floral Summer Breeze", "price": 3200.0, "category": "Summer Collection", "desc": "Lightweight cotton lawn with floral prints."},
        {"name": "Classic White Kurta", "price": 2500.0, "category": "Clothes", "desc": "Traditional white kurta with subtle embroidery."},
        {"name": "Royal Velvet Shawl", "price": 8000.0, "category": "Other", "desc": "Hand-woven velvet shawl."}
    ]

    for prod in sample_products:
        if not Product.query.filter_by(name=prod["name"]).first():
            p = Product(
                name=prod["name"],
                price=prod["price"],
                description=prod["desc"],
                category=prod["category"],
                image_file='default.jpg'
            )
            db.session.add(p)
            print(f"Added product: {prod['name']}")
    
    db.session.commit()
