import unittest

from shop import apply_discount, cart_total


class TestShop(unittest.TestCase):
    def test_ten_percent_off(self):
        self.assertAlmostEqual(apply_discount(200, 10), 180)

    def test_no_discount(self):
        self.assertAlmostEqual(apply_discount(50, 0), 50)

    def test_cart_total(self):
        self.assertAlmostEqual(cart_total([10, 20, 30], 50), 30)

    def test_rejects_bad_percent(self):
        with self.assertRaises(ValueError):
            apply_discount(10, 150)


if __name__ == "__main__":
    unittest.main()
