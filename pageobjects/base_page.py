# pageobjects/base_page.py
from __future__ import annotations
import os, time, traceback
from typing import Optional, Tuple, List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement

Locator = Tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver, default_timeout: int = 8):
        self.driver = driver
        self.default_timeout = default_timeout
        os.makedirs("screenshots", exist_ok=True)

    # -------- low-level wait helper --------
    def _wait(self, condition, timeout: Optional[int] = None):
        t = timeout if timeout is not None else self.default_timeout
        return WebDriverWait(self.driver, t).until(condition)

    # -------- find helpers --------

    def open_url(self, url: str, wait_for_locator: Optional[Locator] = None, timeout: Optional[int] = None) -> None:
        """
        Navigate to an absolute URL and wait until page is loaded.
        :param url: full URL including scheme (http:// or https://)
        :param wait_for_locator: optional locator to wait for (a stable element on the target page)
        :param timeout: seconds to wait (falls back to self.default_timeout)
        """
        if not url:
            raise ValueError("url must be a non-empty string")
        if not url.startswith(("http://", "https://")):
            raise ValueError("open_url expects a full url starting with http:// or https://")

        t = timeout if timeout is not None else self.default_timeout

        try:
            self.driver.get(url)
        except WebDriverException as e:
            # capture screenshot for debugging and re-raise
            self.save_screenshot(f"screenshots/open_url_error_{int(time.time())}.png")
            raise

        # wait for document.readyState == 'complete'
        try:
            WebDriverWait(self.driver, t).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            # still continue to optional element wait but capture screenshot
            self.save_screenshot(f"screenshots/open_url_readystate_timeout_{int(time.time())}.png")

        # optional: wait for a stable element to be visible (recommended when landing page is dynamic)
        if wait_for_locator:
            try:
                WebDriverWait(self.driver, t).until(EC.visibility_of_element_located(wait_for_locator))
            except TimeoutException:
                # give diagnostic screenshot and re-raise so test fails with useful artifact
                fname = self.save_screenshot(f"screenshots/open_url_wait_for_locator_timeout_{int(time.time())}.png")
                raise AssertionError(f"Timed out waiting for locator {wait_for_locator}. Screenshot: {fname}")

    def open(self, path_or_url: str = "/", wait_for_locator: Optional[Locator] = None,
             timeout: Optional[int] = None) -> None:
        """
        Open a path relative to base URL (or an absolute URL).
        If path_or_url is an absolute URL (starts with http/https), it calls open_url directly.
        Otherwise it builds: base_url + path_or_url
        The project should expose a base URL via ReadConfig.get_application_url() or environment BASE_URL.
        """
        # allow absolute URL
        if path_or_url.startswith(("http://", "https://")):
            return self.open_url(path_or_url, wait_for_locator=wait_for_locator, timeout=timeout)

        # find base URL: prefer ReadConfig.get_application_url(), fall back to BASE_URL env
        base = None
        try:
            from utilities.readproperties import ReadConfig
            base = ReadConfig.get_user_login_url()
        except Exception:
            base = os.getenv("BASE_URL", "").strip()

        if not base:
            raise RuntimeError("Base URL not configured. Set ReadConfig.get_application_url() or env BASE_URL")

        # join safely
        full = base.rstrip("/") + "/" + path_or_url.lstrip("/")
        return self.open_url(full, wait_for_locator=wait_for_locator, timeout=timeout)
    def find(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self._wait(EC.presence_of_element_located(locator), timeout)

    def find_visible(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self._wait(EC.visibility_of_element_located(locator), timeout)

    def find_clickable(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self._wait(EC.element_to_be_clickable(locator), timeout)

    def get_element_list(self, locator: Locator, timeout: Optional[int] = None) -> List[WebElement]:
        t = timeout if timeout is not None else self.default_timeout
        end = time.time() + t
        while time.time() < end:
            elems = self.driver.find_elements(*locator)
            if elems:
                return elems
            time.sleep(0.15)
        return []

    # -------- basic actions --------
    def click(self, locator: Locator, timeout: Optional[int] = None) -> None:
        el = self.find_clickable(locator, timeout)
        try:
            el.click()
        except WebDriverException:
            # fallback: JS click
            self.driver.execute_script("arguments[0].click();", el)

    def clear(self, locator: Locator, timeout: Optional[int] = None) -> None:
        el = self.find_visible(locator, timeout)
        try:
            el.clear()
        except WebDriverException:
            try:
                el.send_keys(Keys.CONTROL, "a", Keys.DELETE)
            except Exception:
                pass

    def type(self, locator: Locator, text: str, timeout: Optional[int] = None,
             clear_first: bool = True, send_enter: bool = False) -> None:
        """Simple typing - keeps behavior you had but no verification."""
        el = self.find_visible(locator, timeout)
        try:
            el.click()
        except WebDriverException:
            pass
        if clear_first:
            try:
                el.clear()
            except WebDriverException:
                try:
                    el.send_keys(Keys.CONTROL, "a", Keys.DELETE)
                except Exception:
                    pass
        el.send_keys(text)
        if send_enter:
            el.send_keys(Keys.ENTER)

    def type_and_verify(self,
                        locator: Locator,
                        text: str,
                        timeout: Optional[int] = None,
                        clear_first: bool = True,
                        allow_partial: bool = False,
                        send_enter: bool = False) -> str:
        """
        Type text and verify the element's value matches (or contains if allow_partial).
        Returns the final value seen in the element.
        """
        el = self.find_visible(locator, timeout)
        try:
            el.click()
        except WebDriverException:
            pass

        if clear_first:
            try:
                el.clear()
            except WebDriverException:
                try:
                    el.send_keys(Keys.CONTROL, "a", Keys.DELETE)
                except Exception:
                    pass

        el.send_keys(text)
        if send_enter:
            el.send_keys(Keys.ENTER)

        # trigger potential change handlers
        try:
            el.send_keys(Keys.TAB)
        except Exception:
            pass

        t = timeout if timeout is not None else self.default_timeout
        end = time.time() + t
        last_val = ""
        while time.time() < end:
            try:
                last_val = (el.get_attribute("value") or el.text or "").strip()
            except Exception:
                last_val = ""
            if last_val == text or (allow_partial and text in last_val):
                return last_val
            time.sleep(0.12)

        # JS fallback: directly set value and dispatch events
        try:
            self.driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input'));"
                "arguments[0].dispatchEvent(new Event('change'));",
                el, text
            )
            time.sleep(0.12)
            last_val = (el.get_attribute("value") or el.text or "").strip()
            if last_val == text or (allow_partial and text in last_val):
                return last_val
        except Exception:
            pass

        # final: return whatever is present (caller should inspect)
        return last_val

    def get_text(self, locator: Locator, timeout: Optional[int] = None) -> str:
        el = self.find_visible(locator, timeout)
        return (el.text or "").strip()

    # -------- diagnostics --------
    def save_screenshot(self, name: Optional[str] = None) -> str:
        ts = time.strftime("%Y%m%d_%H%M%S")
        fname = name or f"screenshots/snap_{ts}.png"
        self.driver.save_screenshot(fname)
        return fname

    def fail_and_screenshot(self, msg: str):
        fname = self.save_screenshot()
        # optional logging hook
        print(f"[FAIL] {msg} - screenshot: {fname}")
        # raise to fail test
        raise AssertionError(f"{msg}. Screenshot: {fname}")

    # convenience for tests
    def element_value(self, locator: Locator, timeout: Optional[int] = None) -> str:
        el = self.find_visible(locator, timeout)
        return (el.get_attribute("value") or "").strip()

    def is_visible(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self._wait(EC.visibility_of_element_located(locator), timeout)
