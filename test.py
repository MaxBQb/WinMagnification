import concurrent.futures
import unittest

import win_magnification as mag


class InitUninitTest(unittest.TestCase):
    def test_init_uninit(self):
        mag.safe_initialize()
        mag.safe_uninitialize()

    def test_initialize_twice(self):
        mag.safe_initialize()
        self.assertRaises(RuntimeError, mag.safe_initialize)

    def test_uninitialize_twice(self):
        mag.safe_uninitialize()
        self.assertRaises(RuntimeError, mag.safe_uninitialize)


class NoControlWindowTest(unittest.TestCase):
    def test_set_fullscreen_color_effect(self):
        mag_api = mag.WinMagnificationAPI()
        mag_api.fullscreen_color_effect = mag.COLOR_INVERSION_EFFECT
        self.assertEqual(mag_api.fullscreen_color_effect, mag.COLOR_INVERSION_EFFECT)
        # Note: Set delay with time.sleep to see visual difference
        mag_api.fullscreen_color_effect = mag.NO_EFFECT
        self.assertEqual(mag_api.fullscreen_color_effect, mag.NO_EFFECT)

    def test_set_fullscreen_color_effect_threaded(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_set_fullscreen_color_effect)
            concurrent.futures.as_completed([future])
            future.result()

    def test_set_fullscreen_transform(self):
        mag_api = mag.WinMagnificationAPI()
        new_transform = (1.5, (0, 0))
        mag_api.fullscreen_transform = new_transform
        self.assertEqual(
            mag_api.fullscreen_transform.raw,
            new_transform
        )
        # Note: Set delay with time.sleep to see visual difference
        mag.reset_fullscreen_transform()
        self.assertEqual(
            mag_api.fullscreen_transform.raw,
            mag.DEFAULT_FULLSCREEN_TRANSFORM
        )

    def test_set_fullscreen_transform_details(self):
        mag_api = mag.WinMagnificationAPI()
        max_scale = 10
        step = 1
        default_scale, (start_x, start_y) = mag.DEFAULT_FULLSCREEN_TRANSFORM
        mag.reset_fullscreen_transform()
        for i in range(max_scale):
            mag_api.fullscreen_transform.scale += step
            mag_api.fullscreen_transform.offset.x += 2*step
            mag_api.fullscreen_transform.offset.y += 3*step

        self.assertEqual(
            mag_api.fullscreen_transform.raw,
            (max_scale*step + default_scale, (
                2*step*max_scale+start_x,
                3*step*max_scale+start_y
            ))
        )

        # Note: Set delay with time.sleep to see visual difference
        mag_api.fullscreen_transform.offset = 150, 200
        self.assertEqual(mag_api.fullscreen_transform.offset.raw, (150, 200))

        mag.reset_fullscreen_transform()
        self.assertEqual(
            mag_api.fullscreen_transform.raw,
            mag.DEFAULT_FULLSCREEN_TRANSFORM
        )


if __name__ == '__main__':
    unittest.main()
