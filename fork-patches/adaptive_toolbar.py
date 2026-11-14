#!/usr/bin/env python3
"""Fork-local adaptive toolbar patch for Chromium M157.

This is intentionally separate from Titanium's upstream patch.sh. Exact-match
anchors make upstream changes fail closed rather than ship a partial patch.
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLBAR = Path("chrome/browser/ui/android/toolbar/java/src/org/chromium/chrome/browser/toolbar")
FILES = {
    "tablet": TOOLBAR / "top/ToolbarTablet.java",
    "phone": TOOLBAR / "top/ToolbarPhone.java",
    "utils": TOOLBAR / "top/ToolbarUtils.java",
    "extensions": TOOLBAR / "extensions/ExtensionsToolbarCoordinatorImpl.java",
}


def replace_once(text: str, original: str, replacement: str, name: str) -> str:
    count = text.count(original)
    if count != 1:
        raise ValueError(f"{name}: expected one anchor, found {count}")
    return text.replace(original, replacement, 1)


def transform(name: str, text: str) -> str:
    if name == "tablet":
        text = replace_once(text,
            "private static final int MINIMUM_LOCATION_BAR_WIDTH_DP = 200;",
            "private static final int MINIMUM_LOCATION_BAR_WIDTH_DP = 240;", name)
        text = replace_once(text,
            "mToolbarWidthConsumers[ToolbarComponentId.HOME] = homeButtonCoordinator;",
            "mToolbarWidthConsumers[ToolbarComponentId.HOME] = null;\n"
            "        homeButtonCoordinator.setHasSpaceToShow(false);", name)
        text = replace_once(text,
            "protected void updateOptionalButton(ButtonData buttonData) {",
            "protected void updateOptionalButton(ButtonData buttonData) {\n"
            "        // New tab remains available from the tab switcher and app menu.\n"
            "        if (buttonData.getButtonSpec().getButtonVariant()\n"
            "                == org.chromium.chrome.browser.toolbar.adaptive.AdaptiveToolbarButtonVariant.NEW_TAB) {\n"
            "            hideOptionalButton();\n"
            "            return;\n"
            "        }", name)
    elif name == "phone":
        text = replace_once(text,
            "boolean hideHomeButton = !mIsHomeButtonEnabled || mIsToolbarUiRefactorEnabled;",
            "boolean hideHomeButton = true; // Fork: homepage action remains in app menu.", name)
        text = replace_once(text,
            "protected void updateOptionalButton(@Nullable ButtonData buttonData) {\n"
            "        mButtonData = buttonData;",
            "protected void updateOptionalButton(@Nullable ButtonData buttonData) {\n"
            "        // Fold only the new-tab shortcut, never other contextual actions.\n"
            "        if (buttonData != null && buttonData.getButtonSpec().getButtonVariant()\n"
            "                == org.chromium.chrome.browser.toolbar.adaptive.AdaptiveToolbarButtonVariant.NEW_TAB) {\n"
            "            buttonData = null;\n"
            "        }\n"
            "        mButtonData = buttonData;", name)
    elif name == "utils":
        text = replace_once(text,
            "ToolbarComponentId.MENU,\n"
            "                ToolbarComponentId.TAB_SWITCHER,\n"
            "                ToolbarComponentId.LOCATION_BAR_MINIMUM,",
            "ToolbarComponentId.MENU,\n"
            "                ToolbarComponentId.TAB_SWITCHER,\n"
            "                // Keep an extension overflow entry before reserving omnibox space.\n"
            "                ToolbarComponentId.EXTENSIONS_MENU_BUTTON,\n"
            "                ToolbarComponentId.LOCATION_BAR_MINIMUM,", name)
        text = replace_once(text,
            "ToolbarComponentId.HOME,\n"
            "                ToolbarComponentId.EXTENSIONS_MENU_BUTTON,\n"
            "                ToolbarComponentId.EXTENSIONS_REQUEST_ACCESS_BUTTON,",
            "ToolbarComponentId.HOME,\n"
            "                ToolbarComponentId.EXTENSIONS_REQUEST_ACCESS_BUTTON,", name)
    elif name == "extensions":
        if text.count("private boolean isMenuButtonPinned() {\n        if (mIsWebApp) {") != 1:
            raise ValueError("extensions: missing WebApp guard")
        text = replace_once(text,
            "        if (mProfile.shutdownStarted()) {\n"
            "            // TODO(crbug.com/459079170)",
            "        // Compact windows must retain the extension overflow entry.\n"
            "        if (mContainer.getResources().getConfiguration().screenWidthDp\n"
            "                < COMPACT_WINDOW_THRESHOLD_DP) return true;\n"
            "        if (mProfile.shutdownStarted()) {\n"
            "            // TODO(crbug.com/459079170)", name)
    else:
        raise ValueError(f"unknown target: {name}")
    return text


def apply(root: Path) -> None:
    updates = {}
    for name, relative in FILES.items():
        path = root / relative
        updates[path] = transform(name, path.read_text(encoding="utf-8"))
    for path, content in updates.items():
        path.write_text(content, encoding="utf-8")
    print("Adaptive toolbar: M157 source anchors applied to four Chromium files.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: adaptive_toolbar.py CHROMIUM_SOURCE_ROOT")
    apply(Path(sys.argv[1]))
