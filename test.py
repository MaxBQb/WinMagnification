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
        mag_api.fullscreen.color_effect.raw = mag.COLOR_INVERSION_EFFECT
        self.assertEqual(mag_api.fullscreen.color_effect.raw, mag.COLOR_INVERSION_EFFECT)
        delay_for_visualize(1)
        mag_api.fullscreen.color_effect.reset()
        self.assertEqual(
            mag_api.fullscreen.color_effect.raw,
            mag_api.fullscreen.color_effect.default
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
        del mag_api.fullscreen.transform.raw
        self.assertEqual(
            mag_api.fullscreen.transform.value,
            mag_api.fullscreen.transform.default,
        )

    def test_set_fullscreen_transform_details(self):
        mag_api = mag.WinMagnificationAPI()
        max_scale = 10
        step = 1
        default_scale, (start_x, start_y) = mag_api.fullscreen.transform.default.raw
        del mag_api.fullscreen.transform.value
        for i in range(max_scale):
            with mag_api.fullscreen.transform.value.batch() as transform:
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
        mag_api.fullscreen.transform.value.scale = 1
        mag_api.fullscreen.transform.value.offset.raw = (150, 200)
        self.assertEqual(mag_api.fullscreen.transform.value.offset.raw, (150, 200))

        delay_for_visualize(1)
        offset = 15
        mag_api.fullscreen.transform.value.offset.same = offset
        self.assertEqual(mag_api.fullscreen.transform.value.offset.x, offset)
        self.assertEqual(mag_api.fullscreen.transform.value.offset.y, offset)
        self.assertEqual(mag_api.fullscreen.transform.value.offset.same, offset)

        with mag_api.fullscreen.transform.value.batch() as transform:
            transform.offset = mag_api.fullscreen.transform.default.offset
            transform.scale = mag_api.fullscreen.transform.default.scale
            transform.scale = 2
        self.assertEqual(mag_api.fullscreen.transform.value.offset.raw,
                         mag_api.fullscreen.transform.default.offset.raw)
        self.assertEqual(mag_api.fullscreen.transform.value.scale, 2)

        mag_api.fullscreen.transform.reset()
        self.assertEqual(
            mag_api.fullscreen.transform.raw,
            mag_api.fullscreen.transform.default.raw
        )

    def test_idempotent(self):
        mag_api = mag.WinMagnificationAPI()
        last = mag_api.fullscreen.transform.value
        mag_api.fullscreen.transform.raw = last.raw
        self.assertEqual(mag_api.fullscreen.transform.raw, last.raw)

    def test_gradation(self):
        mag_api = mag.WinMagnificationAPI()
        for i in range(100+1):
            mag_api.fullscreen.color_effect.raw = mag.get_color_matrix_inversion(i/100.0)
            delay_for_visualize(0.01)
        self.assertEqual(mag_api.fullscreen.color_effect.raw, mag.COLOR_INVERSION_EFFECT)

    def test_cursor(self):
        mag_api = mag.WinMagnificationAPI()
        mag_api.fullscreen.cursor_visible = False
        self.assertFalse(mag_api.fullscreen.cursor_visible)
        delay_for_visualize(1)
        mag_api.fullscreen.cursor_visible = True
        # Getter test have no sense, because it returns cached value, not a real one
        self.assertTrue(mag_api.fullscreen.cursor_visible)
        mag_api.fullscreen.cursor_visible = True
        self.assertTrue(mag_api.fullscreen.cursor_visible)

    def test_input_transform(self):
        mag_api = mag.WinMagnificationAPI()
        rectangles = (0, 0, 2, 2), (0, 0, 3, 3)
        self.assertEqual(mag_api.fullscreen.input_transform.raw, mag_api.fullscreen.input_transform.default.raw)
        with suppress(OSError):
            mag_api.fullscreen.input_transform.raw = True, *rectangles
            self.assertTrue(mag_api.fullscreen.input_transform.value.enabled)
            self.assertEqual(mag_api.fullscreen.input_transform.value.source.raw, rectangles[0])
            self.assertEqual(mag_api.fullscreen.input_transform.value.destination.raw, rectangles[1])
            self.assertEqual(mag_api.fullscreen.input_transform.raw, (True, *rectangles))
        with suppress(OSError):
            with mag_api.fullscreen.input_transform.value.batch():
                input_transform = mag_api.fullscreen.input_transform.value
                default = mag_api.fullscreen.input_transform.default
                input_transform.destination.raw = default.destination.raw
                input_transform.source.raw = default.source.raw
                input_transform.enabled = default.enabled
            self.assertEqual(mag_api.fullscreen.input_transform.raw, mag_api.fullscreen.input_transform.default.raw)


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
        self.window.controller.color_effect.raw = mag.COLOR_INVERSION_EFFECT
        for i in range(4):
            new_state = next(state)
            self.window.fullscreen_mode = new_state
            delay_for_visualize(1)
            self.assertEqual(self.window.fullscreen_mode, new_state)

    def test_effects(self):
        self.window.fullscreen_mode = True
        scale = 1.5
        self.window.controller.scale.value.same = scale
        self.window.controller.color_effect.raw = mag.COLOR_INVERSION_EFFECT
        self.assertEqual(self.window.controller.source.raw, self.window.current_rectangle)
        self.assertEqual(self.window.controller.scale.value.same, scale)
        self.assertEqual(self.window.controller.scale.value.pair, (scale, scale))
        delay_for_visualize(1)
        self.window.controller.scale.value.pair = scale, scale * 2
        self.assertEqual(self.window.controller.scale.value.x, scale)
        self.assertEqual(self.window.controller.scale.value.y, 2*scale)
        self.window.fullscreen_mode = False
        delay_for_visualize(1)
        self.window.controller.scale.reset()
        self.assertEqual(self.window.controller.scale.value, self.window.controller.scale.default)
        self.assertEqual(self.window.controller.color_effect.raw, mag.COLOR_INVERSION_EFFECT)
        self.assertEqual(self.window.fullscreen_mode, False)
        delay_for_visualize(1)
        mag.set_transform(self.window.magnifier_hwnd, scale)
        self.assertEqual(self.window.controller.scale.value.pair, (scale, scale))
        delay_for_visualize(1)
        mag.set_transform(self.window.magnifier_hwnd, (scale, scale * 2))
        self.assertEqual(self.window.controller.scale.value.pair, (scale, 2*scale))
        self.assertEqual(self.window.controller.color_effect.raw, mag.COLOR_INVERSION_EFFECT)
        self.window.controller.color_effect.reset()
        self.assertEqual(self.window.controller.color_effect.raw, self.window.controller.color_effect.default)

    def test_idempotent(self):
        last = self.window.controller.scale.value
        self.window.controller.scale.value.pair = last.pair
        self.assertEqual(self.window.controller.scale.value.pair, last.pair)
        self.window.controller.scale.reset()
        self.assertEqual(self.window.controller.scale.raw, self.window.controller.scale.default.raw)

    def test_exclusion_filters(self):
        self.window.controller.color_effect.raw = mag.COLOR_INVERSION_EFFECT
        result_list = (1902036, 65552, 1)
        self.window.controller.filters.raw = result_list
        self.assertEqual(self.window.controller.filters.raw, result_list)
        delay_for_visualize(1)
        self.window.controller.filters.reset()
        self.assertEqual(self.window.controller.filters.raw, self.window.controller.filters.default)
        delay_for_visualize(1)
        self.assertRaises(RuntimeError, mag.get_filters, 0)


if __name__ == '__main__':
    unittest.main()
