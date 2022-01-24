import unittest
import win_magnification as mag


class InitTest(unittest.TestCase):
    def tearDown(self):
        mag.uninitialize()

    def test_initialize(self):
        self.assertTrue(mag.initialize())

    def test_initialize_twice(self):
        self.assertTrue(mag.initialize())
        self.assertTrue(mag.initialize())


class UnInitTest(unittest.TestCase):
    def setUp(self):
        mag.initialize()

    def test_uninitialize(self):
        self.assertTrue(mag.uninitialize())

    def test_uninitialize_twice(self):
        self.assertTrue(mag.uninitialize())
        self.assertTrue(mag.uninitialize())


if __name__ == '__main__':
    unittest.main()
