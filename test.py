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


class NoControlWindowTest(unittest.TestCase):
    def setUp(self):
        mag.initialize()

    def tearDown(self):
        mag.uninitialize()

    def test_get_fullscreen_color_effect(self):
        self.assertEqual(mag.get_fullscreen_color_effect(), mag.IDENTITY_MATRIX)

    def test_set_fullscreen_color_effect(self):
        self.assertTrue(mag.set_fullscreen_color_effect(mag.COLOR_INVERSION_EFFECT))
        self.assertEqual(mag.get_fullscreen_color_effect(), mag.COLOR_INVERSION_EFFECT)
        # Note: Set delay with time.sleep to see visual difference
        self.assertTrue(mag.set_fullscreen_color_effect(mag.NO_EFFECT))
        self.assertEqual(mag.get_fullscreen_color_effect(), mag.NO_EFFECT)


if __name__ == '__main__':
    unittest.main()
