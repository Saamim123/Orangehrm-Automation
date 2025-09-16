import os
import uuid
from datetime import datetime
from typing import Any, Generator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.edge.webdriver import WebDriver
from selenium.webdriver.firefox.webdriver import WebDriver

from utilities.customlogger import CustomLogger
from utilities.readproperties import ReadConfig
from pageobjects.user_login import UserLoginPage
from pageobjects.user_dashboard_page import UserDashboardPage


# ---------------------- Configuration helpers ----------------------
REPORTS_DIR = "Reports"
SCREENSHOTS_DIR = "screenshots"


def _unique_suffix() -> str:
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"


def _ensure_dir(dirname: str) -> str:
    path = os.path.join(os.getcwd(), dirname)
    os.makedirs(path, exist_ok=True)
    return path


# ---------------------- Pytest CLI options ---------------------------
def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome", help="Browser to run tests on")
    parser.addoption("--headless", action="store_true", default=False, help="Run browser in headless mode")


# ---------------------- Session-level resources ---------------------
@pytest.fixture(scope="session")
def reports_dir() -> str:
    return _ensure_dir(REPORTS_DIR)


@pytest.fixture(scope="session")
def screenshots_dir() -> str:
    return _ensure_dir(SCREENSHOTS_DIR)


# ---------------------- Browser fixture -----------------------------
@pytest.fixture(scope="function")
def driver(request, screenshots_dir) -> Generator[WebDriver | WebDriver | WebDriver, Any, None]:
    """
    Create a webdriver instance for the requested browser and yield it.
    Function scope gives test isolation. Switch to scope='session' to reuse the
    browser across tests (faster but be careful with test isolation).
    """
    logger = CustomLogger.get_logger()
    browser_name = (request.config.getoption("--browser") or "chrome").lower()
    headless = request.config.getoption("--headless")

    logger.info(f"Starting browser: {browser_name} (headless={headless})")

    if browser_name == "chrome":
        opts = ChromeOptions()
        opts.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        })
        if headless:
            # Newer Chrome supports --headless=new; fallback to --headless if necessary
            opts.add_argument("--headless=new")
        opts.add_argument("--disable-notifications")
        opts.add_argument("--disable-save-password-bubble")
        driver = webdriver.Chrome(options=opts, service=ChromeService())

    elif browser_name == "firefox":
        from selenium.webdriver.firefox.options import Options as FFOptions
        opts = FFOptions()
        if headless:
            opts.add_argument("-headless")
        driver = webdriver.Firefox(options=opts)

    elif browser_name == "edge":
        from selenium.webdriver.edge.options import Options as EdgeOptions
        opts = EdgeOptions()
        if headless:
            # Edge headless flag mirrors Chrome's
            opts.add_argument("--headless=new")
        driver = webdriver.Edge(options=opts)

    else:
        raise pytest.UsageError(f"Unsupported --browser={browser_name}")

    # Global driver configuration
    driver.maximize_window()
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)  # small implicit wait; prefer explicit waits in PageObjects

    yield driver

    logger.info("Quitting browser")
    try:
        driver.quit()
    except Exception:
        logger.exception("Error while quitting browser")


# ---------------------- Login fixture -------------------------------
@pytest.fixture()
def login_fixture(driver, screenshots_dir, request):
    """
    Log the user in and yield the dashboard page object. Tests that depend on a
    logged-in session should accept the `login_fixture` fixture.

    This fixture verifies landing by asserting the Dashboard title; on failure
    it captures a screenshot and re-raises the assertion to fail the test.
    """
    logger = CustomLogger.get_logger()

    user_login_url = ReadConfig.get_user_login_url()
    username = ReadConfig.get_user_email()
    password = ReadConfig.get_user_password()

    logger.info("------- Starting User Login Test ----------")
    logger.info(f"Opening URL: {user_login_url}")
    driver.get(user_login_url)

    ulp = UserLoginPage(driver)
    ulp.get_user_login_url(user_login_url)
    logger.info("Entering username")
    ulp.enter_username(username)
    logger.info("Entering password")
    ulp.enter_password(password)
    logger.info("Clicking login")
    ulp.click_login()

    # Landing / verification
    udp = UserDashboardPage(driver)
    actual_text = udp.capture_text()

    try:
        assert actual_text == "Dashboard", f"Expected 'Dashboard' but got '{actual_text}'"
    except AssertionError:
        fname = os.path.join(screenshots_dir, f"login_failed_{_unique_suffix()}.png")
        try:
            driver.save_screenshot(fname)
            logger.error(f"Login failed - screenshot saved to {fname}")
        except Exception:
            logger.exception("Failed to save screenshot on login failure")
        raise

    # Provide the dashboard page object to dependent tests
    yield udp

    # Optional teardown: logout if implemented in PageObject
    try:
        if hasattr(udp, "logout"):
            udp.logout()
    except Exception:
        logger.exception("Logout during teardown failed (continuing).")


# ---------------------- Reporting hook --------------------------------
def pytest_configure(config):
    """Configure pytest-html output path per run to avoid collisions."""
    suffix = _unique_suffix()
    report_path = os.path.join(_ensure_dir(REPORTS_DIR), f"report_{suffix}.html")
    # pytest-html uses --html option under the hood; set it if html plugin is present
    try:
        config.option.htmlpath = report_path
        config.option.self_contained_html = True
    except Exception:
        # If pytest-html is not installed, ignore silently
        pass


# ---------------------- Screenshot on failure hook ---------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Capture screenshot automatically when a test fails (makes debugging easier).
    The screenshot is saved into the session screenshots directory if the
    `driver` fixture is available in the test's fixturenames.
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        screenshots_dir = os.path.join(os.getcwd(), SCREENSHOTS_DIR)
        os.makedirs(screenshots_dir, exist_ok=True)
        if "driver" in item.fixturenames:
            driver = item.funcargs.get("driver")
            if driver:
                fname = os.path.join(screenshots_dir, f"failure_{item.name}_{_unique_suffix()}.png")
                try:
                    driver.save_screenshot(fname)
                    logger = CustomLogger.get_logger()
                    logger.error(f"Test failed - screenshot saved to {fname}")
                except Exception:
                    # Don't raise from the hook; merely log the failure to capture screenshot
                    CustomLogger.get_logger().exception("Failed to capture screenshot for failing test")


import os, pytest
from utilities.random_data import generate_employee_with_credentials

@pytest.fixture
def employee_record():
    # Optionally read TEST_SEED and pass to generator for deterministic runs
    rec = generate_employee_with_credentials()
    # Optionally: check uniqueness vs DB/API, e.g. existing_ids = query_db_for_emp_ids()
    # If collision, regenerate or pass existing_ids to generator
    print("TEST DATA:", rec)  # helpful for replaying failures
    yield rec

    # optionally teardown: delete created employee if test created it persistently
