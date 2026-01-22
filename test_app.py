from app import create_app
import unittest

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory DB for tests
        self.client = self.app.test_client()
        
        with self.app.app_context():
            from app import db
            from app.models import Product, User
            db.create_all()
            
            # Create a test product
            p1 = Product(name='Test Product', price=100.0, category='Test', image_file='default.jpg')
            db.session.add(p1)
            db.session.commit()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_shop_page(self):
        response = self.client.get('/shop')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_login_page(self):
        response = self.client.get('/admin/login')
        self.assertEqual(response.status_code, 200)

    def test_search_route(self):
        response = self.client.get('/search?q=Lawn')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Search Results', response.data)

    def test_contact_page(self):
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Contact Us', response.data)

    def test_cart_operations(self):
        # Test empty cart
        response = self.client.get('/cart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your cart is empty', response.data)

        # Test adding item (requires a product first, but we can mock session or rely on database)
        # Since we have seed data, let's assume ID 1 exists (Regalia Textile)
        with self.client:
             self.client.get('/cart/add/1', follow_redirects=True)
             self.assertIn('cart', session)
             self.assertEqual(len(session['cart']), 1)
             
             # Test view cart again
             response = self.client.get('/cart')
             self.assertEqual(response.status_code, 200)
             self.assertNotIn(b'Your cart is empty', response.data)

if __name__ == '__main__':
    unittest.main()
