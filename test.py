import unittest
import concurrent.futures

import win_magnification as mag


class InitUninitTest(unittest.TestCase):
    def test_init_uninit(self):
        mag.initialize()
        mag.uninitialize()

    def test_initialize_twice(self):
        mag.initialize()
        mag.initialize()

    def test_uninitialize_twice(self):
        mag.uninitialize()
        mag.uninitialize()


class NoControlWindowTest(unittest.TestCase):
    def setUp(self):
        mag.initialize()

    def tearDown(self):
        mag.uninitialize()

    def test_get_fullscreen_color_effect(self):
        self.assertEqual(mag.get_fullscreen_color_effect(), mag.IDENTITY_MATRIX)

    def test_set_fullscreen_color_effect(self):
        mag.set_fullscreen_color_effect(mag.COLOR_INVERSION_EFFECT)
        self.assertEqual(mag.get_fullscreen_color_effect(), mag.COLOR_INVERSION_EFFECT)
        # Note: Set delay with time.sleep to see visual difference
        mag.set_fullscreen_color_effect(mag.NO_EFFECT)
        self.assertEqual(mag.get_fullscreen_color_effect(), mag.NO_EFFECT)

    def test_set_fullscreen_color_effect_threaded(self):
        # TODO: Prevent exception
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_set_fullscreen_color_effect)
            concurrent.futures.as_completed([future])
            future.result()


if __name__ == '__main__':
    unittest.main()
