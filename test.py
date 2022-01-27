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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mag = mag.WinMagnificationAPI()

    def test_set_fullscreen_color_effect(self):
        self.mag.fullscreen_color_effect = mag.COLOR_INVERSION_EFFECT
        self.assertEqual(self.mag.fullscreen_color_effect, mag.COLOR_INVERSION_EFFECT)
        # Note: Set delay with time.sleep to see visual difference
        self.mag.fullscreen_color_effect = mag.NO_EFFECT
        self.assertEqual(self.mag.fullscreen_color_effect, mag.NO_EFFECT)

    def test_set_fullscreen_color_effect_threaded(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_set_fullscreen_color_effect)
            concurrent.futures.as_completed([future])
            future.result()

    def test_set_fullscreen_transform(self):
        new_transform = (1.5, (0, 0))
        self.mag.fullscreen_transform = new_transform
        self.assertEqual(
            self.mag.fullscreen_transform,
            new_transform
        )
        # Note: Set delay with time.sleep to see visual difference
        self.mag.fullscreen_transform = new_transform = 1, (0, 0)
        self.assertEqual(
            self.mag.fullscreen_transform,
            new_transform
        )


if __name__ == '__main__':
    unittest.main()
