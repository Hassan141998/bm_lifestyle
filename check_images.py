"""
Script to verify Base64 images in database and test image display
"""
from app import create_app, db
from app.models import Product

app = create_app()

with app.app_context():
    products = Product.query.all()
    print(f"\n=== Found {len(products)} products ===\n")
    
    for p in products:
        image_type = "Base64" if p.image_file.startswith('data:') else "File path"
        image_preview = p.image_file[:50] + "..." if len(p.image_file) > 50 else p.image_file
        print(f"ID: {p.id} | Name: {p.name}")
        print(f"  Image Type: {image_type}")
        print(f"  Image Data: {image_preview}")
        print()
