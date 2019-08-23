import unittest
import re


class TestAssessment(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAssessment, self).__init__(*args, **kwargs)
        with open('order.html', 'r') as file_descriptor:
            self.dom_str = file_descriptor.read()

    # Check if redirectToCheckout function call is present
    def test_assesssment_redirect_to_checkout(self):
        self.assertNotEqual(self.dom_str, '.redirectToCheckout',
                            'No stripe redirect call found!')

    # Check if successUrl redirects to order_success.html
    def test_assesssment_success_url(self):
        self.assertRegex(self.dom_str,
                         r'successUrl: \'https:\/\/[a-z]*\.com/order_success\.html\'',
                         'No order_success.html redirect found on checkout success.')

    # Check if cancelUrl redirects to order.html
    def test_assesssment_cancel_url(self):
        self.assertRegex(self.dom_str,
                         r'cancelUrl: \'https:\/\/[a-z]*\.com/order\.html\'',
                         'No order.html redirect found on checkout cancel.')


 {{ cookiecutter.extra_data }}
        
if __name__ == '__main__':
    unittest.main()
