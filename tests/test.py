import doctest
import inspect
import threading
import time
import unittest
from contextlib import suppress
from itertools import cycle

import win_magnification as mag
import win_magnification.old as old_mag
from example import windows_utils  # type: ignore

# Change to see visual changes on test running
ALLOW_SLEEP = False  # TODO: Don't forget reset to False


def delay_for_visualize(secs: float, apply=ALLOW_SLEEP):
    if apply:
        time.sleep(secs)


# noinspection PyUnusedLocal
def load_tests(loader, tests, ignore):
    for name, module in inspect.getmembers(mag, inspect.ismodule):
        tests.addTests(doctest.DocTestSuite(module))
    return tests


# noinspection PyMethodMayBeStatic
class InitFinalizeTest(unittest.TestCase):
    def test_init_finalize(self):
        old_mag.MagInitialize()
        old_mag.MagUninitialize()

    def test_init_finalize_twice(self):
        mag.initialize()
        mag.finalize()
        self.assertRaises(RuntimeError, mag.finalize)

    def test_finalize_only(self):
        self.assertRaises(RuntimeError, mag.finalize)


class NoControlWindowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.api = mag.WinMagnificationAPI()

    def tearDown(self) -> None:
        self.api.dispose()

    @property
    def magnifier(self):
        return self.api.fullscreen

    def test_set_fullscreen_color_effect(self):
        self.magnifier.color_effect.raw = mag.const.COLOR_INVERSION_EFFECT
        self.assertEqual(self.magnifier.color_effect.raw, mag.const.COLOR_INVERSION_EFFECT)
        delay_for_visualize(1)
        self.magnifier.color_effect.reset()
        self.assertEqual(
            self.magnifier.color_effect.raw,
            self.magnifier.color_effect.default
        )

    def test_set_fullscreen_transform(self):
        new_transform = (1.5, (0, 0))
        self.magnifier.transform.raw = new_transform
        self.assertEqual(
            self.magnifier.transform.raw,
            new_transform
        )
        delay_for_visualize(1)
        del self.magnifier.transform.raw
        self.assertEqual(
            self.magnifier.transform,
            self.magnifier.transform.default,
        )

    def test_set_fullscreen_transform_details(self):
        max_scale = 10
        step = 1
        default_scale, (start_x, start_y) = self.magnifier.transform.default.raw
        self.magnifier.transform.offset = self.magnifier.transform.offset
        self.magnifier.transform.reset()
        for i in range(max_scale):
            with self.magnifier.transform.batch() as transform:
                transform.scale += step
                transform.offset.x += 2 * step
                transform.offset.y += 3 * step

        self.assertEqual(
            self.magnifier.transform.raw,
            (max_scale * step + default_scale, (
                2 * step * max_scale + start_x,
                3 * step * max_scale + start_y
            ))
        )

        delay_for_visualize(1)
        self.magnifier.transform.scale = 1
        self.magnifier.transform.offset.raw = (150, 200)
        self.assertEqual(self.magnifier.transform.offset.raw, (150, 200))

        delay_for_visualize(1)
        offset = 15
        self.magnifier.transform.offset.same = offset
        self.assertEqual(self.magnifier.transform.offset.x, offset)
        self.assertEqual(self.magnifier.transform.offset.y, offset)
        self.assertEqual(self.magnifier.transform.offset.same, offset)

        with self.magnifier.transform.batch() as transform:
            del transform.offset
            del transform.scale
            transform.transform = 2

        self.assertEqual(self.magnifier.transform.offset.raw,
                         self.magnifier.transform.default.offset.raw)
        self.assertEqual(self.magnifier.transform.transform, 2)

        self.magnifier.transform.reset()
        self.assertEqual(
            self.magnifier.transform.raw,
            self.magnifier.transform.default.raw
        )

    def test_idempotent(self):
        last = self.magnifier.transform
        self.magnifier.transform.raw = last.raw
        self.assertEqual(self.magnifier.transform.raw, last.raw)

    def test_gradation(self):
        for i in range(100+1):
            self.magnifier.color_effect.raw = mag.effects.inversion(i / 100.0)
            delay_for_visualize(0.01)
        self.assertEqual(self.magnifier.color_effect.raw, mag.const.COLOR_INVERSION_EFFECT)

    def test_cursor(self):
        self.magnifier.cursor_visible = False
        self.assertFalse(self.magnifier.cursor_visible)
        delay_for_visualize(1)
        self.magnifier.cursor_visible = True
        # Getter test have no sense, because it returns cached value, not a real one
        self.assertTrue(self.magnifier.cursor_visible)
        self.magnifier.cursor_visible = True
        self.assertTrue(self.magnifier.cursor_visible)

    def test_input_transform(self):
        rectangles = (0, 0, 2, 2), (0, 0, 3, 3)
        self.assertEqual(self.magnifier.input_transform.raw, self.magnifier.input_transform.default.raw)
        with suppress(OSError):
            self.magnifier.input_transform.raw = True, *rectangles
            self.assertTrue(self.magnifier.input_transform.enabled)
            self.assertEqual(self.magnifier.input_transform.source.raw, rectangles[0])
            self.assertEqual(self.magnifier.input_transform.destination.raw, rectangles[1])
            self.assertEqual(self.magnifier.input_transform.raw, (True, *rectangles))
        with suppress(OSError):
            with self.magnifier.input_transform.batch() as input_transform:
                del input_transform.destination
                del input_transform.source
                del input_transform.enabled
            self.assertEqual(self.magnifier.input_transform.raw, self.magnifier.input_transform.default.raw)


class NoControlWindowThreaded(unittest.TestCase):
    def test_set_fullscreen_color_effect_threaded(self):
        tasks_count = 1

        def test():
            try:
                mag_api = mag.WinMagnificationAPI()
                color_effect = mag_api.fullscreen.color_effect
                color_effect.raw = mag.const.COLOR_INVERSION_EFFECT
                self.assertEqual(color_effect.raw, mag.const.COLOR_INVERSION_EFFECT)
                delay_for_visualize(0.1)
                color_effect.reset()
                self.assertEqual(
                    color_effect.raw,
                    color_effect.default
                )
            except Exception as e:
                print("Threaded", e)

        tasks = []
        for _ in range(tasks_count):
            tasks.append(threading.Thread(target=test))
            tasks[-1].start()

        for task in tasks:
            task.join()


class MagnificationControlWindowTest(unittest.TestCase):
    def setUp(self):
        self.window = windows_utils.MagnifierWindow()
        self.window.run()

    def tearDown(self):
        self.window.close()
        self.window.wait_window_stop()
        self.window = None

    @property
    def magnifier(self):
        return self.window.controller

    def test_fullscreen_switch(self):
        state = cycle((True, False))
        self.magnifier.color_effect.raw = mag.const.COLOR_INVERSION_EFFECT
        for i in range(4):
            new_state = next(state)
            self.window.fullscreen_mode = new_state
            delay_for_visualize(1)
            self.assertEqual(self.window.fullscreen_mode, new_state)

    def test_effects(self):
        self.window.fullscreen_mode = True
        self.magnifier.color_effect.raw = mag.const.COLOR_INVERSION_EFFECT
        time.sleep(0.01)
        self.assertEqual(self.magnifier.source.raw, self.window.current_rectangle)
        with self.magnifier.source.batch() as source:
            source.same = -1
            source.start_same = 0
            source.end_same = 8
            self.assertEqual(source.same, source.start_same)
            self.assertEqual(source.right, source.end_same)
            self.assertEqual((0, 0), source.start)
            self.assertEqual((8, 8), source.end)
        delay_for_visualize(1)
        self.window.fullscreen_mode = False
        self.assertEqual(self.magnifier.color_effect.raw, mag.const.COLOR_INVERSION_EFFECT)
        self.assertEqual(self.window.fullscreen_mode, False)
        delay_for_visualize(1)
        self.assertEqual(self.magnifier.color_effect.raw, mag.const.COLOR_INVERSION_EFFECT)
        self.magnifier.color_effect.reset()
        self.assertEqual(self.magnifier.color_effect.raw, self.magnifier.color_effect.default)

    def test_transform(self):
        scale = 1.5
        self.magnifier.transform.scale.same = scale
        self.assertEqual(self.magnifier.transform.scale.same, scale)
        self.assertEqual(self.magnifier.transform.scale.raw, (scale, scale))
        delay_for_visualize(1)
        steps = 2
        sub_steps = 1
        for i in range(int(scale*steps)):
            for j in range(i*sub_steps, (i+1)*sub_steps):
                with self.magnifier.transform.batch() as transform:
                    transform.scale.same += 1 / sub_steps
                    transform.offset.same += 1
                delay_for_visualize(0.01)
        self.assertAlmostEqual(self.magnifier.transform.scale.same, scale * (steps+1), 4)
        self.assertAlmostEqual(self.magnifier.transform.offset.x, scale*steps*sub_steps, 4)
        self.assertAlmostEqual(self.magnifier.transform.offset.y, scale*steps*sub_steps, 4)
        delay_for_visualize(1)
        self.magnifier.transform.scale.raw = scale, scale * 2
        self.assertEqual(self.magnifier.transform.scale.x, scale)
        self.assertEqual(self.magnifier.transform.scale.y, 2 * scale)
        delay_for_visualize(1)
        self.magnifier.transform.reset()
        self.assertEqual(self.magnifier.transform, self.magnifier.transform.default)
        delay_for_visualize(1)
        mag.set_transform(self.window.magnifier_hwnd, scale)
        self.assertEqual(self.magnifier.transform.scale.raw, (scale, scale))
        delay_for_visualize(1)
        mag.set_transform(self.window.magnifier_hwnd, (scale, scale * 2))
        self.assertEqual(self.magnifier.transform.scale.raw, (scale, 2 * scale))
        delay_for_visualize(1)
        mag.set_transform(self.window.magnifier_hwnd, (scale, scale * 2), (100.0, 150.0))
        self.assertEqual(self.magnifier.transform.scale.raw, (scale, 2 * scale))
        self.assertEqual(self.magnifier.transform.offset.raw, (100.0, 150.0))
        self.assertEqual(self.magnifier.transform.pair, mag.get_transform(self.window.magnifier_hwnd))

    def test_idempotent(self):
        last = self.magnifier.transform.scale
        self.magnifier.transform.scale = last
        self.assertEqual(self.magnifier.transform.scale, last)
        self.magnifier.transform.reset()
        self.assertEqual(self.magnifier.transform, self.magnifier.transform.default)
        self.assertNotEqual(id(self.magnifier.transform), id(self.magnifier.transform.default))

    def test_exclusion_filters(self):
        self.magnifier.color_effect.raw = mag.const.COLOR_INVERSION_EFFECT
        result_list = (1902036, 65552, 1)
        self.magnifier.filters.raw = result_list
        self.assertEqual(self.magnifier.filters.raw, result_list)
        delay_for_visualize(1)
        self.magnifier.filters.reset()
        self.assertEqual(self.magnifier.filters.raw, self.magnifier.filters.default)
        delay_for_visualize(1)
        self.assertRaises(RuntimeError, mag.get_filters, 0)


if __name__ == '__main__':
    unittest.main()
