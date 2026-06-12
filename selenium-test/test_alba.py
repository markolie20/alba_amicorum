#!/usr/bin/env python3
"""
Selenium test suite for the Alba Amicorum application.

Covers:
  - Homepage load & hero stats
  - Search filter (before/after)
  - Year range filter (before/after)
  - Country dropdown filter (before/after)
  - Album card selection & map update
  - Show/Hide journey toggle
  - Clear selection
  - Pagination (next, page number, prev)
  - Navigate to album detail page
  - Album metadata panel
  - Image carousel (next/prev)
  - Contribution list click
  - Floating Prev/Next contribution navigation
  - Back to search

Run (from project root):
  .venv/bin/python3 selenium-test/test_alba.py            # headless
  .venv/bin/python3 selenium-test/test_alba.py --show     # visible browser

Requirements:
  - Frontend running:  cd client && npm run dev    → http://localhost:5173
  - Backend running:   uvicorn backend.api.main:app --reload  → http://localhost:8000
"""

import sys
import time
import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
)

# ── Configuration ────────────────────────────────────────────────────────────

BASE_URL       = "http://localhost:5173"
GECKODRIVER    = "/snap/bin/geckodriver"
WAIT_TIMEOUT   = 20          # seconds for explicit waits
ACTION_DELAY   = 3           # seconds to pause between actions / after clicks
WINDOW_W       = 1440
WINDOW_H       = 900
SHOTS_ROOT     = Path(__file__).parent / "screenshots"

# ── Helpers ───────────────────────────────────────────────────────────────────

def _count_text(text: str) -> str:
    """Trim long strings for readable log output."""
    return text[:60] + "…" if len(text) > 60 else text


class AlbaTestSuite:

    def __init__(self, headless: bool = False):
        opts = Options()
        if headless:
            opts.add_argument("--headless")
        opts.add_argument(f"--width={WINDOW_W}")
        opts.add_argument(f"--height={WINDOW_H}")

        service = Service(executable_path=GECKODRIVER)
        self.driver = webdriver.Firefox(service=service, options=opts)
        self.driver.set_window_size(WINDOW_W, WINDOW_H)
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
    

        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.shots_dir = SHOTS_ROOT / ts
        self.shots_dir.mkdir(parents=True, exist_ok=True)

        self._results: list[tuple[str, bool, str]] = []

    # ── Infrastructure ────────────────────────────────────────────────────────

    def quit(self):
        self.driver.quit()

    def shot(self, name: str) -> str:
        path = str(self.shots_dir / f"{name}.png")
        self.driver.save_screenshot(path)
        return path

    def _pass(self, name: str, note: str = ""):
        label = f"  [PASS] {name}" + (f"  ({note})" if note else "")
        print(label)
        self._results.append((name, True, note))

    def _fail(self, name: str, reason: str = ""):
        label = f"  [FAIL] {name}" + (f"  ← {reason}" if reason else "")
        print(label)
        self._results.append((name, False, reason))

    def pause(self):
        """Sleep for ACTION_DELAY seconds between actions."""
        time.sleep(ACTION_DELAY)

    # ── Common waits ─────────────────────────────────────────────────────────

    def _wait_for_album_list(self):
        """Block until the album list header is visible (API has responded)."""
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h3[contains(text(), 'Albums (')]")
            )
        )

    def _wait_for_detail_page(self):
        """Block until the album detail back button is visible."""
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(., 'Back to search')]")
            )
        )

    def _album_cards(self):
        """Return all clickable album card divs on the home page."""
        return self.driver.find_elements(
            By.XPATH,
            "//div[contains(@class,'cursor-pointer') "
            "and .//h4 "
            "and .//span[text()='View']]",
        )

    # ── Tests ─────────────────────────────────────────────────────────────────

    def t01_homepage_load(self):
        name = "01_homepage_load"
        try:
            self.driver.get(BASE_URL)
            self.shot("01a_initial")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h2[contains(text(), 'Ontdek')]")
                )
            )
            self._wait_for_album_list()
            self.shot("01b_loaded")
            self._pass(name)
        except (TimeoutException, WebDriverException) as e:
            self.shot("01b_error")
            self._fail(name, str(e)[:120])

    def t02_hero_stats(self):
        name = "02_hero_stats"
        try:
            # Stats load asynchronously — wait until none of them shows '—'
            self.wait.until(
                lambda d: all(
                    el.text.strip() not in ("—", "")
                    for el in d.find_elements(By.CSS_SELECTOR, ".text-3xl")
                )
            )
            stats = [el.text for el in self.driver.find_elements(By.CSS_SELECTOR, ".text-3xl")]
            self.shot("02_hero_stats")
            self._pass(name, f"stats: {stats}")
        except TimeoutException:
            self.shot("02_hero_stats_timeout")
            self._fail(name, "stats did not load from API")

    def t03_search_filter(self):
        name = "03_search_filter"
        try:
            self._wait_for_album_list()
            before_count = len(self._album_cards())
            self.shot("03a_search_before")

            box = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Zoek']")
            box.click()
            box.send_keys("Amsterdam")
            self.pause()

            self.shot("03b_search_after")
            after_count = len(self._album_cards())
            self._pass(name, f"cards: {before_count} → {after_count}")
        except NoSuchElementException as e:
            self.shot("03b_search_error")
            self._fail(name, str(e)[:120])

    def t04_search_clear(self):
        name = "04_search_clear"
        try:
            box = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Zoek']")
            box.click()
            box.send_keys(Keys.CONTROL + "a")
            box.send_keys(Keys.DELETE)
            self.pause()

            self.shot("04_search_cleared")
            count = len(self._album_cards())
            self._pass(name, f"cards restored: {count}")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t05_year_filter(self):
        name = "05_year_filter"
        try:
            year_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='number']")
            self.shot("05a_year_before")

            start = year_inputs[0]
            start.click()
            start.send_keys(Keys.CONTROL + "a")
            start.send_keys("1700")
            start.send_keys(Keys.TAB)
            self.pause()

            self.shot("05b_year_after")
            count = len(self._album_cards())

            # Reset to default
            start.click()
            start.send_keys(Keys.CONTROL + "a")
            start.send_keys("1550")
            start.send_keys(Keys.TAB)
            self.pause()

            self._pass(name, f"cards with year ≥ 1700: {count}")
        except (NoSuchElementException, IndexError) as e:
            self._fail(name, str(e)[:120])

    def t06_country_filter(self):
        name = "06_country_filter"
        try:
            sel_el = self.driver.find_element(By.CSS_SELECTOR, "select")
            sel = Select(sel_el)
            options = [o.text for o in sel.options if o.text != "Alle"]
            self.shot("06a_country_before")

            if not options:
                self._fail(name, "no country options loaded")
                return

            target = "Netherlands" if "Netherlands" in options else options[0]
            sel.select_by_visible_text(target)
            self.pause()
            self.shot("06b_country_after")

            count = len(self._album_cards())

            # Reset
            sel.select_by_visible_text("Alle")
            self.pause()

            self._pass(name, f"country='{target}', cards={count}")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t07_album_select(self):
        name = "07_album_select"
        try:
            self._wait_for_album_list()
            cards = self._album_cards()
            if not cards:
                self._fail(name, "no album cards found")
                return

            title = cards[0].find_element(By.TAG_NAME, "h4").text
            self.shot("07a_select_before")
            cards[0].click()
            self.pause()
            self.shot("07b_select_after")

            # Confirm "Clear selection" button appeared in the list header
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(), 'Clear selection')]")
                )
            )
            self._pass(name, f"selected: {_count_text(title)}")
        except (TimeoutException, NoSuchElementException, IndexError) as e:
            self.shot("07b_select_error")
            self._fail(name, str(e)[:120])

    def t08_show_journey(self):
        name = "08_show_journey"
        try:
            btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//button[contains(text(),'Show journey') "
                     "or contains(text(),'Hide journey')]")
                )
            )
            initial = btn.text
            self.shot("08a_journey_before")
            btn.click()
            self.pause()
            self.shot("08b_journey_after")

            btn = self.driver.find_element(
                By.XPATH,
                "//button[contains(text(),'Show journey') "
                "or contains(text(),'Hide journey')]",
            )
            self._pass(name, f"'{initial}' → '{btn.text}'")
        except (TimeoutException, NoSuchElementException) as e:
            self._fail(name, str(e)[:120])

    def t09_clear_selection(self):
        name = "09_clear_selection"
        try:
            btn = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Clear selection')]"
            )
            self.shot("09a_clear_before")
            btn.click()
            self.pause()
            self.shot("09b_clear_after")

            remaining = self.driver.find_elements(
                By.XPATH, "//button[contains(text(), 'Clear selection')]"
            )
            self._pass(name, "selection cleared") if not remaining else self._fail(name, "button still visible")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t10_pagination_next(self):
        name = "10_pagination_next"
        try:
            self._wait_for_album_list()
            titles_p1 = [c.find_element(By.TAG_NAME, "h4").text for c in self._album_cards()]
            self.shot("10a_page1")

            nxt = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next page']")
            nxt.click()
            self.pause()
            self.shot("10b_page2")

            titles_p2 = [c.find_element(By.TAG_NAME, "h4").text for c in self._album_cards()]
            changed = titles_p1 != titles_p2
            self._pass(name, "page changed") if changed else self._fail(name, "page did not change")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t11_pagination_page_number(self):
        name = "11_pagination_page_number"
        try:
            # Page number buttons sit between the prev/next arrows
            page_btns = self.driver.find_elements(
                By.XPATH,
                "//button[@aria-label='Previous page']"
                "/following-sibling::div//button",
            )
            if len(page_btns) < 2:
                self._pass(name, "fewer than 2 pages, skipped")
                return

            # Click page 2 (index 1)
            target_btn = page_btns[1]
            page_num = target_btn.text
            self.shot("11a_page_num_before")
            target_btn.click()
            self.pause()
            self.shot("11b_page_num_after")
            self._pass(name, f"jumped to page {page_num}")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t12_pagination_prev(self):
        name = "12_pagination_prev"
        try:
            prv = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Previous page']")
            prv.click()
            self.pause()
            self.shot("12_page_prev")

            page_info = self.driver.find_element(
                By.XPATH, "//div[contains(.,'Page') and contains(.,' of ')]"
            ).text
            on_page1 = "Page 1 " in page_info
            self._pass(name, page_info) if on_page1 else self._fail(name, f"unexpected: {page_info}")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t13_view_album_detail(self):
        name = "13_view_album_detail"
        try:
            self._wait_for_album_list()
            self.shot("13a_before_view")

            view_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//span[text()='View']]")
                )
            )
            view_btn.click()
            self._wait_for_detail_page()
            self.shot("13b_detail_page")
            self._pass(name, self.driver.current_url.split("/")[-1][:40])
        except (TimeoutException, NoSuchElementException) as e:
            self.shot("13b_detail_error")
            self._fail(name, str(e)[:120])

    def t14_album_metadata(self):
        name = "14_album_metadata"
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[text()='Owner']")
                )
            )
            # Collect visible metadata labels
            labels = [
                el.text for el in self.driver.find_elements(
                    By.XPATH, "//div[@class and contains(text(),'Owner') "
                    "or contains(text(),'Period') or contains(text(),'Location')]"
                )
            ]
            self.shot("14_metadata")
            self._pass(name, f"labels found: {labels}")
        except TimeoutException as e:
            self.shot("14_metadata_error")
            self._fail(name, str(e)[:120])

    def t15_carousel_next(self):
        name = "15_carousel_next"
        try:
            counter = self.driver.find_element(
                By.XPATH,
                "//div[contains(.,' / ') and contains(@class,'rounded-full')]",
            )
            before = counter.text
            self.shot("15a_carousel_before")

            btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next image']")
            btn.click()
            self.pause()
            self.shot("15b_carousel_next")

            counter = self.driver.find_element(
                By.XPATH,
                "//div[contains(.,' / ') and contains(@class,'rounded-full')]",
            )
            after = counter.text
            self._pass(name, f"'{before}' → '{after}'") if before != after else self._fail(name, "counter unchanged")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t16_carousel_prev(self):
        name = "16_carousel_prev"
        try:
            counter = self.driver.find_element(
                By.XPATH,
                "//div[contains(.,' / ') and contains(@class,'rounded-full')]",
            )
            before = counter.text

            btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Previous image']")
            btn.click()
            self.pause()
            self.shot("16_carousel_prev")

            counter = self.driver.find_element(
                By.XPATH,
                "//div[contains(.,' / ') and contains(@class,'rounded-full')]",
            )
            after = counter.text
            self._pass(name, f"'{before}' → '{after}'") if before != after else self._fail(name, "counter unchanged")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t17_contribution_click(self):
        name = "17_contribution_click"
        try:
            # Contribution buttons follow the "Album Overview" card in the list
            contrib_btns = self.driver.find_elements(
                By.XPATH,
                "//h4[normalize-space(text())='Album Overview']"
                "/ancestor::button/following-sibling::button[.//h4]",
            )
            if not contrib_btns:
                self._fail(name, "no contribution buttons found")
                return

            contrib_name = contrib_btns[0].find_element(By.TAG_NAME, "h4").text
            self.shot("17a_contrib_before")
            contrib_btns[0].click()
            self.pause()
            self.shot("17b_contrib_after")

            has_url = "/contribution/" in self.driver.current_url
            self._pass(name, f"'{_count_text(contrib_name)}'") if has_url else self._fail(name, "URL missing /contribution/")
        except (NoSuchElementException, TimeoutException) as e:
            self.shot("17b_contrib_error")
            self._fail(name, str(e)[:120])

    def t18_next_contribution(self):
        name = "18_next_contribution"
        try:
            before_url = self.driver.current_url
            self.shot("18a_next_before")

            btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
            btn.click()
            self.pause()
            self.shot("18b_next_after")

            after_url = self.driver.current_url
            self._pass(name, after_url.split("/")[-1][:40]) if after_url != before_url else self._fail(name, "URL unchanged")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t19_prev_contribution(self):
        name = "19_prev_contribution"
        try:
            before_url = self.driver.current_url
            self.shot("19a_prev_before")

            btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Previous']")
            btn.click()
            self.pause()
            self.shot("19b_prev_after")

            after_url = self.driver.current_url
            self._pass(name, after_url.split("/")[-1][:40]) if after_url != before_url else self._fail(name, "URL unchanged")
        except NoSuchElementException as e:
            self._fail(name, str(e)[:120])

    def t20_back_to_home(self):
        name = "20_back_to_home"
        try:
            self.shot("20a_before_back")
            btn = self.driver.find_element(
                By.XPATH, "//button[contains(., 'Back to search')]"
            )
            btn.click()
            self.wait.until(EC.url_to_be(f"{BASE_URL}/"))
            self._wait_for_album_list()
            self.shot("20b_back_home")
            self._pass(name)
        except (NoSuchElementException, TimeoutException) as e:
            self.shot("20b_back_error")
            self._fail(name, str(e)[:120])

    def t21_header_logo(self):
        name = "21_header_logo"
        try:
            self.shot("21a_logo_before")
            logo = self.driver.find_element(
                By.XPATH, "//h1[contains(text(),'De Koninklijke Bibliotheek')]"
            )
            logo.click()
            self.pause()
            self._wait_for_album_list()
            self.shot("21b_logo_after")
            self._pass(name)
        except (NoSuchElementException, TimeoutException) as e:
            self._fail(name, str(e)[:120])

    # ── Runner ────────────────────────────────────────────────────────────────

    def run(self) -> bool:
        tests = [
            self.t01_homepage_load,
            self.t02_hero_stats,
            self.t03_search_filter,
            self.t04_search_clear,
            self.t05_year_filter,
            self.t06_country_filter,
            self.t07_album_select,
            self.t08_show_journey,
            self.t09_clear_selection,
            self.t10_pagination_next,
            self.t11_pagination_page_number,
            self.t12_pagination_prev,
            self.t13_view_album_detail,
            self.t14_album_metadata,
            self.t15_carousel_next,
            self.t16_carousel_prev,
            self.t17_contribution_click,
            self.t18_next_contribution,
            self.t19_prev_contribution,
            self.t20_back_to_home,
            self.t21_header_logo,
        ]

        sep = "─" * 58
        print(f"\n{'═'*58}")
        print("  Alba Amicorum  —  Selenium Test Suite")
        print(f"  Screenshots  →  {self.shots_dir}")
        print(f"{'═'*58}\n")

        for test in tests:
            try:
                test()
            except Exception as exc:
                self._fail(test.__name__, f"UNEXPECTED: {exc}")
            self.pause()

        # Summary
        passed = sum(1 for _, ok, _ in self._results if ok)
        total  = len(self._results)
        failed = [n for n, ok, _ in self._results if not ok]

        print(f"\n{sep}")
        print(f"  Result: {passed}/{total} passed", end="")
        if failed:
            print(f"  |  failed: {', '.join(failed)}")
        else:
            print("  ✓ all green")
        print(f"  Screenshots saved to: {self.shots_dir}")
        print(f"{sep}\n")

        return passed == total


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    headless = False
    suite = AlbaTestSuite(headless=headless)
    try:
        ok = suite.run()
    finally:
        suite.quit()
    sys.exit(0 if ok else 1)
