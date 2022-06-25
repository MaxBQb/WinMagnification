import concurrent.futures
import unittest
from itertools import cycle
import win_magnification as mag
import windows_utils
import time

ALLOW_SLEEP = False  # Change to see visual changes on test running


def delay_for_visualize(secs: float) -> None:
    pass


if ALLOW_SLEEP:
    delay_for_visualize = time.sleep


class InitFinalizeTest(unittest.TestCase):
    def test_init_finalize(self):
        mag.initialize()
        mag.finalize()

    def test_init_finalize_twice(self):
        mag.initialize()
        mag.finalize()
        self.assertRaises(RuntimeError, mag.finalize)

    def test_finalize_only(self):
        self.assertRaises(RuntimeError, mag.finalize)


class NoControlWindowTest(unittest.TestCase):
    def test_set_fullscreen_color_effect(self):
        mag_api = mag.WinMagnificationAPI()
        mag_api.fullscreen_color_effect = mag.COLOR_INVERSION_EFFECT
        self.assertEqual(mag_api.fullscreen_color_effect, mag.COLOR_INVERSION_EFFECT)
        delay_for_visualize(1)
        del mag_api.fullscreen_color_effect
        self.assertEqual(mag_api.fullscreen_color_effect, mag.NO_EFFECT)

    def test_set_fullscreen_color_effect_threaded(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_set_fullscreen_color_effect)
            concurrent.futures.as_completed([future])
            future.result()

    def test_set_fullscreen_transform(self):
        mag_api = mag.WinMagnificationAPI()
        new_transform = (1.5, (0, 0))
        mag_api.fullscreen_transform.raw = new_transform
        self.assertEqual(
            mag_api.fullscreen_transform.raw,
            new_transform
        )
        delay_for_visualize(1)
        del mag_api.fullscreen_transform.raw
        self.assertEqual(
            mag_api.fullscreen_transform.raw,
            mag.DEFAULT_FULLSCREEN_TRANSFORM
        )

    def test_set_fullscreen_transform_details(self):
        mag_api = mag.WinMagnificationAPI()
        max_scale = 10
        step = 1
        default_scale, (start_x, start_y) = mag.DEFAULT_FULLSCREEN_TRANSFORM
        del mag_api.fullscreen_transform.raw
        for i in range(max_scale):
            mag_api.fullscreen_transform.scale += step
            mag_api.fullscreen_transform.offset.x += 2 * step
            mag_api.fullscreen_transform.offset.y += 3 * step

        self.assertEqual(
            mag_api.fullscreen_transform.raw,
            (max_scale * step + default_scale, (
                2 * step * max_scale + start_x,
                3 * step * max_scale + start_y
            ))
        )

        delay_for_visualize(1)
        mag_api.fullscreen_transform.offset.raw = 150, 200
        self.assertEqual(mag_api.fullscreen_transform.offset.raw, (150, 200))

        del mag_api.fullscreen_transform.raw
        self.assertEqual(
            mag_api.fullscreen_transform.raw,
            mag.DEFAULT_FULLSCREEN_TRANSFORM
        )


class MagnificationControlWindowTest(unittest.TestCase):
    def setUp(self):
        self.window = windows_utils.MagnifierWindow()
        self.window_thread = windows_utils.run_magnifier_window(self.window)

    def tearDown(self):
        self.window.close()
        self.window_thread.join()
        self.window = None
        self.window_thread = None

    def test_fullscreen_switch(self):
        state = cycle((True, False))
        mag.set_window_transform(self.window.magnifier_hwnd, 1)
        mag.set_color_effect(self.window.magnifier_hwnd, mag.COLOR_INVERSION_EFFECT)
        for i in range(4):
            new_state = next(state)
            self.window.fullscreen_mode = new_state
            delay_for_visualize(1)
            self.assertEqual(self.window.fullscreen_mode, new_state)

    def test_effects(self):
        self.window.fullscreen_mode = True
        mag.set_window_transform(self.window.magnifier_hwnd, 1)
        mag.set_color_effect(self.window.magnifier_hwnd, mag.COLOR_INVERSION_EFFECT)
        delay_for_visualize(1)
        self.window.fullscreen_mode = False
        self.assertEqual(self.window.fullscreen_mode, False)


if __name__ == '__main__':
    unittest.main()
