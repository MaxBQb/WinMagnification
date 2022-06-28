import concurrent.futures
import unittest
from contextlib import suppress
from itertools import cycle
import win_magnification as mag
import windows_utils
import time

# Change to see visual changes on test running
ALLOW_SLEEP = False  # TODO: Don't forget reset to False


def delay_for_visualize(secs: float, apply=ALLOW_SLEEP):
    if apply:
        time.sleep(secs)


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
        mag_api.fullscreen.transform.raw = new_transform
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
            with mag_api.fullscreen.transform.batch() as transform:
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
        mag_api.fullscreen.transform.scale = 1
        mag_api.fullscreen.transform.offset.pair = (150, 200)
        self.assertEqual(mag_api.fullscreen.transform.offset.pair, (150, 200))

        delay_for_visualize(1)
        offset = 15
        mag_api.fullscreen.transform.offset.same = offset
        self.assertEqual(mag_api.fullscreen.transform.offset.x, offset)
        self.assertEqual(mag_api.fullscreen.transform.offset.y, offset)
        self.assertEqual(mag_api.fullscreen.transform.offset.same, offset)

        with mag_api.fullscreen.transform.batch() as transform:
            transform.reset_offset()
            transform.reset_scale()
            transform.scale = 2
        self.assertEqual(mag_api.fullscreen.transform.offset.pair, mag_api.fullscreen.default_transform.offset.pair)
        self.assertEqual(mag_api.fullscreen.transform.scale, 2)

        mag_api.fullscreen.reset_transform()
        self.assertEqual(
            mag_api.fullscreen.transform.raw,
            mag.DEFAULT_FULLSCREEN_TRANSFORM
        )

    def test_idempotent(self):
        mag_api = mag.WinMagnificationAPI()
        last = mag_api.fullscreen.transform
        mag_api.fullscreen.transform.raw = last.raw
        self.assertEqual(mag_api.fullscreen.transform.raw, last.raw)

    def test_gradation(self):
        mag_api = mag.WinMagnificationAPI()
        for i in range(100+1):
            mag_api.fullscreen.color_effect = mag.get_color_matrix_inversion(i/100.0)
            delay_for_visualize(0.01)
        self.assertEqual(mag_api.fullscreen.color_effect, mag.COLOR_INVERSION_EFFECT)

    def test_cursor(self):
        mag_api = mag.WinMagnificationAPI()
        mag_api.fullscreen.set_cursor_visibility(False)
        delay_for_visualize(1)
        mag_api.fullscreen.set_cursor_visibility(True)

    def test_input_transform(self):
        mag_api = mag.WinMagnificationAPI()
        rectangles = (0, 0, 2, 2), (0, 0, 3, 3)
        self.assertEqual(mag_api.fullscreen.input_transform.raw, (False, *((0,) * 4,) * 2))
        with suppress(OSError):
            mag_api.fullscreen.input_transform.raw = True, *rectangles
            self.assertTrue(mag_api.fullscreen.input_transform.enabled)
            self.assertEqual(mag_api.fullscreen.input_transform.source, rectangles[0])
            self.assertEqual(mag_api.fullscreen.input_transform.destination, rectangles[1])
            mag_api.fullscreen.input_transform = mag_api.fullscreen.input_transform
            self.assertEqual(mag_api.fullscreen.input_transform.raw, (True, *rectangles))
        with suppress(OSError):
            with mag_api.fullscreen.input_transform.batch() as input_transform:
                input_transform.destination = (0, 0, 0, 0)
                input_transform.source = (0, 0, 0, 0)
                input_transform.enabled = False
            self.assertEqual(mag_api.fullscreen.input_transform.raw, (False, *((0,) * 4,) * 2))


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
        self.window.controller.color_effect = mag.COLOR_INVERSION_EFFECT
        for i in range(4):
            new_state = next(state)
            self.window.fullscreen_mode = new_state
            delay_for_visualize(1)
            self.assertEqual(self.window.fullscreen_mode, new_state)

    def test_effects(self):
        self.window.fullscreen_mode = True
        scale = 1.5
        self.window.controller.scale.same = scale
        self.window.controller.color_effect = mag.COLOR_INVERSION_EFFECT
        self.assertEqual(self.window.controller.source, self.window.current_rectangle)
        self.assertEqual(self.window.controller.scale.same, scale)
        self.assertEqual(self.window.controller.scale.pair, (scale, scale))
        delay_for_visualize(1)
        self.window.controller.scale.pair = scale, scale * 2
        self.assertEqual(self.window.controller.scale.x, scale)
        self.assertEqual(self.window.controller.scale.y, 2*scale)
        self.window.fullscreen_mode = False
        delay_for_visualize(1)
        self.window.controller.reset_scale()
        self.assertEqual(self.window.controller.scale.matrix, mag.DEFAULT_TRANSFORM)
        self.assertEqual(self.window.controller.color_effect, mag.COLOR_INVERSION_EFFECT)
        self.assertEqual(self.window.fullscreen_mode, False)
        delay_for_visualize(1)
        mag.set_transform(self.window.magnifier_hwnd, scale)
        self.assertEqual(self.window.controller.scale.pair, (scale, scale))
        delay_for_visualize(1)
        mag.set_transform(self.window.magnifier_hwnd, (scale, scale * 2))
        self.assertEqual(self.window.controller.scale.pair, (scale, 2*scale))
        self.assertEqual(self.window.controller.color_effect, mag.COLOR_INVERSION_EFFECT)
        self.window.controller.reset_color_effect()
        self.assertEqual(self.window.controller.color_effect, self.window.controller.default_color_effect)

    def test_idempotent(self):
        last = self.window.controller.scale
        self.window.controller.scale.pair = last.pair
        self.assertEqual(self.window.controller.scale.pair, last.pair)
        self.window.controller.reset_scale()
        self.assertEqual(self.window.controller.scale, self.window.controller.default_scale)

    def test_exclusion_filters(self):
        self.window.controller.color_effect = mag.COLOR_INVERSION_EFFECT
        result_list = (1902036, 65552, 1)
        self.window.controller.filters = result_list
        self.assertEqual(self.window.controller.filters, result_list)
        delay_for_visualize(1)
        self.window.controller.filters = ()
        self.assertEqual(self.window.controller.filters, tuple())
        delay_for_visualize(1)
        self.assertRaises(RuntimeError, mag.get_filters, 0)


if __name__ == '__main__':
    unittest.main()
