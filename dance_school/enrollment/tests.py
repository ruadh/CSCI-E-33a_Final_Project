from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, date
import pytz
import unittest
from .models import Order, User, Semester, Course, Offering, Location, LineItem, GiftCard

# NOTE TO SELF:  python3 manage.py test enrollment.tests

# Create your tests here.

class CheckoutTestCase(TestCase):
    def setUp(Self):

        # Create a user
        u1 = User.objects.create(username='atester', first_name='A.', last_name='Tester', email='a_tester@devnull.com')
        u2 = User.objects.create(username='btester', first_name='B.', last_name='Tester', email='b_tester@devnull.com',)

        # Create a semester
        # CITATION:  https://stackabuse.com/converting-strings-to-datetime-in-python/
        registration_open = datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        registration_close = datetime.strptime('2022-05-30 00:00:00', '%Y-%m-%d %H:%M:%S')
        tz = pytz.timezone(u1.timezone)
        s1 = Semester.objects.create(name='Spring 2022', start_date='2022-01-01', end_date='2022-05-30', registration_open=tz.localize(registration_open), registration_close=tz.localize(registration_close), hide=False)

        # Create courses
        c1 = Course.objects.create(title='Level 1', subtitle='Discover Belly Dance', description='A fun intro to the dance.', requirements='Finger cymbals required.', qualifications='Suitable for newbies.')
        c2 = Course.objects.create(title='Level 2', subtitle='Skills & Zils', description='Move beyond the basics.', requirements='Finger cymbals required.', qualifications='Suitable for dancers with at least one year of recent classroom experience.')
        
        # Create locations
        l1 = Location.objects.create(name='Third Life Studio', address_1='33 Union Square', city='Somerville', state='MA')


        # Create offerings:  one that will sell out after the 1st order, one that will sell out after the 2nd order, and one that will not sell out
        off1 = Offering.objects.create(course=c1, location=l1, semester=s1, price=100, weekday=2, start_time='18:00', end_time='19:30', start_date='2022-01-05', end_date='2022-05-19', backup_date='2022-05-26', capacity=1)
        off2 = Offering.objects.create(course=c2, location=l1, semester=s1, price=150, weekday=2, start_time='19:30', end_time='21:00', start_date='2022-01-05', end_date='2022-05-19', backup_date='2022-05-26', capacity=2)
        off3 = Offering.objects.create(course=c1, location=l1, semester=s1, price=150, weekday=3, start_time='18:00', end_time='19:30', start_date='2022-01-06', end_date='2022-05-20', backup_date='2022-05-27', capacity=15)

        # Create a completed order and an incomplete order
        ord1 = Order.objects.create(student=u1, completed=datetime.now(timezone.utc))
        ord2 = Order.objects.create(student=u2)

        # Create line items:  both students add all three offerings to the cart
        l1 = LineItem.objects.create(order=ord1, offering=off1, price=off1.price)
        l2 = LineItem.objects.create(order=ord1, offering=off2, price=off2.price)
        l3 = LineItem.objects.create(order=ord1, offering=off3, price=off3.price)
        l4 = LineItem.objects.create(order=ord2, offering=off1, price=off1.price)
        l5 = LineItem.objects.create(order=ord2, offering=off2, price=off2.price)
        l6 = LineItem.objects.create(order=ord2, offering=off3, price=off3.price)
        

        # Create a gift card
        gc1 = GiftCard.objects.create(card_number='9999999999999999', month='01', year='2023', pin='1234', amount=9999.99)


# Check our sample data was created
    def test_user_exists(self):
        u = User.objects.get(id=1)
        self.assertEqual(u.first_name, 'A.')

    def test_semester_exists(self):
        s = Semester.objects.get(id=1)
        self.assertEqual(s.name, 'Spring 2022' )

    def test_course_exists(self):
        c = Course.objects.get(id=1)
        self.assertEquals(c.title, 'Level 1')

    def test_offering_exists(self):
        off = Offering.objects.get(id=1)
        self.assertEquals(off.course.title, 'Level 1')

    def test_order_exists(self):
        ord = Order.objects.get(id=1)
        self.assertEquals(ord.student.first_name, 'A.')

    def test_gift_card_exists(self):
        gc = GiftCard.objects.get(id=1)
        self.assertEquals(gc.pin, '1234')

    def test_line_item_exists(self):
        l = LineItem.objects.get(id=1)
        self.assertEquals(l.price, 100)


# Run each of the testing functions
if __name__ == "__main__":
    unittest.main()