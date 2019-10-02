import os
import re
import json
import unittest
import urllib.request

import stripe
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class TestAcceptanceStripe(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAcceptanceStripe, self).__init__(*args, **kwargs)
        with open('client/order.html', 'r') as file_descriptor:
            self.order_html_str = file_descriptor.read()

        with open('app.py', 'r') as file_descriptor:
            self.app_py_str = file_descriptor.read()

    def test_acceptance_stripe_public_key_env_has_been_set_in_order_html(self):
        """Check if Stripe public key env was defined in order.html."""
        pattern = re.compile(
            r"Stripe\((\"|')pk_test_\w+(\"|')\);",
            re.I | re.M
        )
        res = re.search(pattern, self.order_html_str)

        self.assertIsNone(
            res,
            msg="You shouldn't hardcode the Stripe key in order.html."
        )

    def test_acceptance_stripe_public_key_env_has_been_set_in_app_py(self):
        """Check if Stripe public key env was defined in app.py."""
        pattern = re.compile(
            r"stripe.api_key = (\"|')pk_test_\w+(\"|')",
            re.I | re.M
        )
        res = re.search(pattern, self.app_py_str)

        self.assertIsNone(
            res,
            msg="You shouldn't hardcode the Stripe key in app.py."
        )

    def test_acceptance_stripe_script_has_been_inserted(self):
        """Check if Stripe script was inserted."""
        pattern = re.compile(
            r"<script src=(\"|')https://js.stripe.com/v3(\"|')></script>",
            re.I | re.M
        )
        res = re.search(pattern, self.order_html_str)

        self.assertTrue(
            hasattr(res, 'group'),
            msg="You didn't insert a Stripe script file."
        )

    def test_acceptance_checkout_button_was_instantiated(self):
        """Check if checkout button was captured."""
        pattern = re.compile(
            r"document.getElementById\((\"|')checkout-button(\"|')\);",
            re.I | re.M
        )

        res = re.search(pattern, self.order_html_str)
        self.assertTrue(
            hasattr(res, 'group'),
            msg="You didn't add a checkout button."
        )

    def test_acceptance_product_defined_on_checkout(self):
        """Check if product was defined on checkout."""
        pattern = re.compile(
            r"product = (\"|')Chocolate Cupcake \w{5}(\"|')",
            re.I | re.M
        )
        res_var = re.search(pattern, self.order_html_str)

        pattern = re.compile(
            r"name: product",
            re.I | re.M
        )
        res_body = re.search(pattern, self.order_html_str)

        self.assertTrue(
            hasattr(res_var, 'group') and hasattr(res_body, 'group'),
            msg="You didn't add the product in the checkout."
        )

    def test_amount_defined_on_checkout(self):
        """Check if amount was defined on checkout."""
        pattern = re.compile(
            r"amount = -?(?:0|[1-9]\d{0,2}(?:,?\d{3})*)(?:\.\d{1,2})?",
            re.I | re.M
        )
        res_var = re.search(pattern, self.order_html_str)

        pattern = re.compile(
            r"amount: amount",
            re.I | re.M
        )
        res_body = re.search(pattern, self.order_html_str)

        self.assertTrue(
            hasattr(res_var, 'group') and hasattr(res_body, 'group'),
            msg="You didn't add the amount code in the checkout."
        )


    def test_acceptance_redirect_to_checkout(self):
        """Check if redirectToCheckout function call is present"""
        pattern = re.compile(
            r".redirectToCheckout",
            re.I | re.M
        )
        res = re.search(pattern, self.order_html_str)

        self.assertTrue(
            hasattr(res, 'group'),
            msg="No checkout redirection was found."
        )

    def test_acceptance_success_url(self):
        """Check if success_url redirects to the /order_success route"""
        pattern = re.compile(
            r"success_url=domain_url \+ (\"|')/order_success\?session_id={CHECKOUT_SESSION_ID}(\"|')",
            re.I | re.M
        )
        res = re.search(pattern, self.app_py_str)

        self.assertTrue(
            hasattr(res, 'group'),
            msg="You didn't define a success URL."
        )

    def test_acceptance_cancel_url(self):
        """Check if cancel_url redirects to the index route"""
        pattern = re.compile(
            r"cancel_url=domain_url \+ (\"|')/(\"|')",
            re.I | re.M
        )
        res = re.search(pattern, self.app_py_str)

        self.assertTrue(hasattr(res, 'group'), msg="You didn't define a cancel URL.")


class ASTTestCases(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ASTTestCases, self).__init__(*args, **kwargs)
        with open('client/order.html', 'r') as file_descriptor:
            self.order_html_str = file_descriptor.read()

    def test_ast_use_correct_product(self):
        pattern = re.compile(
            r"product = (\"|'){{ cookiecutter.product }}(\"|')",
            re.I | re.M
        )
        res = re.search(pattern, self.order_html_str)

        self.assertTrue(hasattr(res, 'group'))

    def test_ast_use_correct_amount(self):
        pattern = re.compile(
            r"amount = {{ cookiecutter.amount }}",
            re.I | re.M
        )
        res = re.search(pattern, self.order_html_str)

        self.assertTrue(hasattr(res, 'group'))


class AssessmentTestCases(unittest.TestCase):

    def setUp(self):
        with open("client/order.html", "r") as file_descriptor:
            self.dom_str = file_descriptor.read()

        WINDOW_SIZE = "1920,1080"

        options = selenium.webdriver.ChromeOptions()
        options.headless = True
        options.binary_location = os.getenv('CHROME_BIN')
        options.add_argument("--window-size=%s" % WINDOW_SIZE)
        options.add_argument("--disable-gpu")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(os.getenv('CHROMEDRIVER_PATH'), options=options)

    def _get_button_id(self):
        pattern = re.compile(
            r"\('checkout-button'\);", re.I | re.M
        )
        res = re.search(pattern, self.dom_str)
        return res.group().split("'")[1]

    def _get_url(self):
        return "{{cookiecutter.domain}}"

    def _check_webhook_data(self):
        x = urllib.request.urlopen(f'{self._get_url()}/payment_intent')
        return json.loads(x.read())

    def _retrieve_stripe_event(self, event):
        stripe.api_key = "{{cookiecutter.access_token}}"

        return stripe.Event.retrieve(event)

    def _get_success_url(self):
        pattern = re.compile(r"^(https\:\/\/)(.*)/order_success\?session_id=(.*)$")
        return pattern

    def test__successful_payment_on_the_checkout_page_redirects_to_order_html__clientcheckout__2(
        self
    ):
        self.driver.get(self._get_url())
        wait = WebDriverWait(self.driver, 20)

        amount_elem = self.driver.find_element_by_id("productAmount")
        formatted_amount = amount_elem.text.replace('$', '')
        formatted_amount = formatted_amount.replace('.', '')

        elem = wait.until(EC.presence_of_element_located((By.ID, self._get_button_id())))
        elem.click()

        email_elem = wait.until(EC.presence_of_element_located((By.ID, "email")))

        cardnum_elem = self.driver.find_element_by_id("cardNumber")
        cardexp_elem = self.driver.find_element_by_id("cardExpiry")
        cardcvc_elem = self.driver.find_element_by_id("cardCvc")
        cardname_elem = self.driver.find_element_by_id("billingName")

        email_elem.send_keys("assessment@test.com.br")
        cardnum_elem.send_keys("555555555555")
        cardnum_elem.click()
        cardnum_elem.send_keys("4444")
        cardexp_elem.send_keys("0439")
        cardcvc_elem.send_keys("424")
        cardname_elem.send_keys("Selenium Test WebDriver")

        confirm_elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "SubmitButton--complete")))
        confirm_elem.click()

        session_id_elem = wait.until(
            EC.presence_of_element_located((By.ID, "sessionId"))
        )

        assert re.match(self._get_success_url(), self.driver.current_url)
        self.assertTrue(session_id_elem.text)

    def test__successful_payment_on_the_checkout_page_creates_a_payment_intent_on_server__payments__2(
        self
    ):
        self.driver.get(self._get_url())
        wait = WebDriverWait(self.driver, 20)

        amount_elem = self.driver.find_element_by_id("productAmount")
        formatted_amount = amount_elem.text.replace('$', '')
        formatted_amount = formatted_amount.replace('.', '')

        elem = wait.until(EC.presence_of_element_located((By.ID, self._get_button_id())))
        elem.click()

        email_elem = wait.until(EC.presence_of_element_located((By.ID, "email")))

        cardnum_elem = self.driver.find_element_by_id("cardNumber")
        cardexp_elem = self.driver.find_element_by_id("cardExpiry")
        cardcvc_elem = self.driver.find_element_by_id("cardCvc")
        cardname_elem = self.driver.find_element_by_id("billingName")

        email_elem.send_keys("assessment@test.com.br")
        cardnum_elem.send_keys("555555555555")
        cardnum_elem.click()
        cardnum_elem.send_keys("4444")
        cardexp_elem.send_keys("0439")
        cardcvc_elem.send_keys("424")
        cardname_elem.send_keys("Selenium Test WebDriver")

        confirm_elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "SubmitButton--complete")))
        confirm_elem.click()

        session_id_elem = wait.until(
            EC.presence_of_element_located((By.ID, "sessionId"))
        )

        payment_intent = self._check_webhook_data()

        self.assertEqual(payment_intent.get('status'), "succeeded")
        self.assertEqual(int(payment_intent.get('amount_received')), int(formatted_amount))

    def test__successful_payment_should_have_no_pending_webhooks__webhooks__2(
        self
    ):
        self.driver.get(self._get_url())
        wait = WebDriverWait(self.driver, 20)

        amount_elem = self.driver.find_element_by_id("productAmount")
        formatted_amount = amount_elem.text.replace('$', '')
        formatted_amount = formatted_amount.replace('.', '')

        elem = wait.until(EC.presence_of_element_located((By.ID, self._get_button_id())))
        elem.click()

        email_elem = wait.until(EC.presence_of_element_located((By.ID, "email")))

        cardnum_elem = self.driver.find_element_by_id("cardNumber")
        cardexp_elem = self.driver.find_element_by_id("cardExpiry")
        cardcvc_elem = self.driver.find_element_by_id("cardCvc")
        cardname_elem = self.driver.find_element_by_id("billingName")

        email_elem.send_keys("assessment@test.com.br")
        cardnum_elem.send_keys("555555555555")
        cardnum_elem.click()
        cardnum_elem.send_keys("4444")
        cardexp_elem.send_keys("0439")
        cardcvc_elem.send_keys("424")
        cardname_elem.send_keys("Selenium Test WebDriver")

        confirm_elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "SubmitButton--complete")))
        confirm_elem.click()

        session_id_elem = wait.until(
            EC.presence_of_element_located((By.ID, "sessionId"))
        )

        payment_intent = self._check_webhook_data()

        response = self._retrieve_stripe_event(payment_intent.get('id'))

        self.assertEqual(response.get('pending_webhooks'), 0)

    def tearDown(self):
        self.driver.close()


    {{cookiecutter.extra_data}}


if __name__ == "__main__":
    unittest.main()
