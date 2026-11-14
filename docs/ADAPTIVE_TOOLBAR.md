# Fork adaptive toolbar v1 (Chromium 157)

Scope: Android top toolbar only, independent of the upstream Titanium patch implementation.

## Behavior
- Home shortcut: hidden in phone and tablet top bars. Existing Homepage app-menu item stays available when configured.
- New tab shortcut: hide only the optional NEW_TAB toolbar action. App menu and tab switcher continue to open tabs. Other contextual optional actions remain unchanged.
- Compact extension access: the puzzle/overflow button is always available for windows below 600 dp, except in WebApp mode. The existing pinned extension list continues to use Chromium's width-based collapse.
- Omnibox: tablet reserved width increases from 200 to 240 dp, subject to actual available width. Extension overflow entry is prioritized before minimum omnibox reservation.
- Does not disable, reload, unpin or remove an extension. Does not touch extension popup content or Side Panel behavior.
- This iteration uses a fixed fork preset; no in-app settings UI is included.

## Isolation
- Upstream patch.sh is untouched apart from the final one-line invocation.
- Fork patch: fork-patches/adaptive_toolbar.py
- Unit tests: tests/test_adaptive_toolbar.py
- Verification CI: .github/workflows/adaptive-toolbar-verify.yml
- The transform validates all four exact Chromium M157 source anchors before writing, and fails closed after upstream drift.

## Tests and acceptance
Automated test: run the Python unit test suite and verify the patch applies to four real Chromium 157.0.8103.78 files. This is NOT a full Android compile.

Manual Android gates before marking the PR ready:
1. 360 / 393 / 600 / 840 dp widths; phone portrait/landscape, tablet, foldable and split screen.
2. 0, 1, 5 and 10 extensions; pinned and unpinned; menu and popup still reachable.
3. Address bar idle/focused, IME displayed, new tab, incognito, RTL, screen-reader touch targets.
4. Confirm navigation via Homepage app menu item (if configured) and New tab through menu/tab switcher.
5. Verify no popup anchoring regression and no extension context menu changes.
6. Build Chromium arm64 APK on a capable runner and test actual device rendering.

## Build safety
The inherited Build workflow is disabled and defaults to a self-hosted runner.
It can update Vanadium, sign artifacts and publish a GitHub Release. Do not
enable or run it blindly for a Draft PR. Use a non-publishing arm64 compile
path on a capable builder, then install and test before requesting review.
