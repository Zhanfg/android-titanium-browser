"""Regression checks for the fork-local Chromium M157 toolbar source transform."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

PATCH = Path(__file__).resolve().parents[1] / "fork-patches/adaptive_toolbar.py"
spec = importlib.util.spec_from_file_location("adaptive_toolbar", PATCH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AdaptiveToolbarPatchTest(unittest.TestCase):
    def test_tablet_fold_home_and_new_tab(self):
        src = ("private static final int MINIMUM_LOCATION_BAR_WIDTH_DP = 200;\n"
               "mToolbarWidthConsumers[ToolbarComponentId.HOME] = homeButtonCoordinator;\n"
               "protected void updateOptionalButton(ButtonData buttonData) {\n")
        result = module.transform("tablet", src)
        self.assertIn("MINIMUM_LOCATION_BAR_WIDTH_DP = 240;", result)
        self.assertIn("homeButtonCoordinator.setHasSpaceToShow(false);", result)
        self.assertIn("AdaptiveToolbarButtonVariant.NEW_TAB", result)
        self.assertIn("hideOptionalButton();", result)

    def test_phone_only_new_tab_is_filtered(self):
        src = ("boolean hideHomeButton = !mIsHomeButtonEnabled || mIsToolbarUiRefactorEnabled;\n"
               "protected void updateOptionalButton(@Nullable ButtonData buttonData) {\n"
               "        mButtonData = buttonData;")
        result = module.transform("phone", src)
        self.assertIn("boolean hideHomeButton = true;", result)
        self.assertIn("buttonData = null;", result)
        self.assertIn("mButtonData = buttonData;", result)

    def test_extension_menu_precedes_omnibox_reservation(self):
        src = ("ToolbarComponentId.MENU,\n"
               "                ToolbarComponentId.TAB_SWITCHER,\n"
               "                ToolbarComponentId.LOCATION_BAR_MINIMUM,\n"
               "ToolbarComponentId.HOME,\n"
               "                ToolbarComponentId.EXTENSIONS_MENU_BUTTON,\n"
               "                ToolbarComponentId.EXTENSIONS_REQUEST_ACCESS_BUTTON,")
        result = module.transform("utils", src)
        self.assertEqual(result.count("ToolbarComponentId.EXTENSIONS_MENU_BUTTON,"), 1)
        self.assertLess(result.index("ToolbarComponentId.EXTENSIONS_MENU_BUTTON,"),
                        result.index("ToolbarComponentId.LOCATION_BAR_MINIMUM,"))

    def test_compact_overflow_entry_and_webapp_guard(self):
        src = ("private boolean isMenuButtonPinned() {\n"
               "        if (mIsWebApp) {\n"
               "        if (mProfile.shutdownStarted()) {\n"
               "            // TODO(crbug.com/459079170)")
        result = module.transform("extensions", src)
        self.assertIn("COMPACT_WINDOW_THRESHOLD_DP) return true;", result)
        self.assertLess(result.index("mIsWebApp"),
                        result.index("COMPACT_WINDOW_THRESHOLD_DP) return true;"))

    def test_fails_closed_on_upstream_drift(self):
        with self.assertRaises(ValueError):
            module.transform("tablet", "unrelated upstream revision")

    def test_no_partial_writes_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in module.FILES.values():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("unrelated", encoding="utf-8")
            first = root / module.FILES["tablet"]
            with self.assertRaises(ValueError):
                module.apply(root)
            self.assertEqual(first.read_text(encoding="utf-8"), "unrelated")


if __name__ == "__main__":
    unittest.main()
