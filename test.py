import concurrent.futures
import unittest
from itertools import cycle
import win_magnification as mag
import windows_utils
import time

# Change to see visual changes on test running
ALLOW_SLEEP = False  # TODO: Don't forget reset to False


# noinspection PyUnusedLocal
def delay_for_visualize(secs: float) -> None:
    pass


if ALLOW_SLEEP:
    # noinspection PyRedeclaration
    delay_for_visualize = time.sleep


# noinspection PyMethodMayBeStatic
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
        mag_api.fullscreen.color_effect = mag.COLOR_INVERSION_EFFECT
        self.assertEqual(mag_api.fullscreen.color_effect, mag.COLOR_INVERSION_EFFECT)
        delay_for_visualize(1)
        mag_api.fullscreen.reset_color_effect()
        self.assertEqual(
            mag_api.fullscreen.color_effect,
            mag_api.fullscreen.default_color_effect
        )

    def test_set_fullscreen_color_effect_threaded(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_set_fullscreen_color_effect)
            concurrent.futures.as_completed([future])
            future.result()

    def test_set_fullscreen_transform(self):
        mag_api = mag.WinMagnificationAPI()
        new_transform = (1.5, (0, 0))
        mag_api.fullscreen.transform = mag.FullscreenTransform.fromRaw(new_transform)
        self.assertEqual(
            mag_api.fullscreen.transform.raw,
            new_transform
        )
        delay_for_visualize(1)
        mag_api.fullscreen.reset_transform()
        self.assertEqual(
            mag_api.fullscreen.transform,
            mag_api.fullscreen.default_transform,
        )

    def test_set_fullscreen_transform_details(self):
        mag_api = mag.WinMagnificationAPI()
        max_scale = 10
        step = 1
        default_scale, (start_x, start_y) = mag.DEFAULT_FULLSCREEN_TRANSFORM
        mag_api.fullscreen.reset_transform()
        for i in range(max_scale):
            with mag_api.fullscreen.transform as transform:
                transform.scale += step
                transform.offset.x += 2 * step
                transform.offset.y += 3 * step

        self.assertEqual(
            mag_api.fullscreen.transform.raw,
            (max_scale * step + default_scale, (
                2 * step * max_scale + start_x,
                3 * step * max_scale + start_y
            ))
        )

        delay_for_visualize(1)
        with mag_api.fullscreen.transform as transform:
            transform.offset = mag.Offset(150, 200)
        self.assertEqual(mag_api.fullscreen.transform.offset.raw, (150, 200))

        delay_for_visualize(1)
        offset = 15
        with mag_api.fullscreen.transform as transform:
            transform.offset = mag.Offset.same(offset)
        self.assertEqual(mag_api.fullscreen.transform.offset.x, offset)
        self.assertEqual(mag_api.fullscreen.transform.offset.y, offset)

        mag_api.fullscreen.reset_transform()
        self.assertEqual(
            mag_api.fullscreen.transform.raw,
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
        delay_for_visualize(1)
        self.assertEqual(self.window.fullscreen_mode, False)


if __name__ == '__main__':
    unittest.main()
