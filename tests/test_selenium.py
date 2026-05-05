"""
Selenium tests for ClubSync.

Requires a running Flask server. Start it before running these tests:
    python app.py

Then run:
    pytest tests/test_selenium.py
"""

import threading
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5000"

TEST_EMAIL = f"selenium_{int(time.time())}@example.com"
TEST_PASSWORD = "seleniumpass123"
TEST_NAME = "Selenium User"


@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(5)
    yield browser
    browser.quit()


def wait_for(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


# ---------------------------------------------------------------------------
# Test 1: Home page loads and shows the ClubSync brand
# ---------------------------------------------------------------------------
def test_home_page_loads(driver):
    driver.get(BASE_URL)
    assert "ClubSync" in driver.page_source


# ---------------------------------------------------------------------------
# Test 2: Register page renders and shows the sign-up form
# ---------------------------------------------------------------------------
def test_register_page_renders(driver):
    driver.get(f"{BASE_URL}/register")
    wait_for(driver, By.NAME, "name")
    assert driver.find_element(By.NAME, "email")
    assert driver.find_element(By.NAME, "password")


# ---------------------------------------------------------------------------
# Test 3: Register a new user successfully redirects to dashboard
# ---------------------------------------------------------------------------
def test_register_new_user(driver):
    driver.get(f"{BASE_URL}/register")
    wait_for(driver, By.NAME, "name").send_keys(TEST_NAME)
    driver.find_element(By.NAME, "email").send_keys(TEST_EMAIL)
    driver.find_element(By.NAME, "password").send_keys(TEST_PASSWORD)
    driver.find_element(By.NAME, "confirmPassword").send_keys(TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "form button[type=submit], form input[type=submit]").click()
    # Should land on dashboard or home after registration
    WebDriverWait(driver, 10).until(lambda d: d.current_url != f"{BASE_URL}/register")
    assert "register" not in driver.current_url


# ---------------------------------------------------------------------------
# Test 4: Logout clears session and redirects to home/login
# ---------------------------------------------------------------------------
def test_logout(driver):
    driver.get(f"{BASE_URL}/logout")
    # After logout the nav should show Login link
    wait_for(driver, By.LINK_TEXT, "Login")
    assert driver.find_element(By.LINK_TEXT, "Login")


# ---------------------------------------------------------------------------
# Test 5: Login page renders correctly
# ---------------------------------------------------------------------------
def test_login_page_renders(driver):
    driver.get(f"{BASE_URL}/login")
    wait_for(driver, By.NAME, "email")
    assert driver.find_element(By.NAME, "password")
    assert "Login" in driver.page_source


# ---------------------------------------------------------------------------
# Test 6: Login with valid credentials
# ---------------------------------------------------------------------------
def test_login_valid_credentials(driver):
    driver.get(f"{BASE_URL}/login")
    wait_for(driver, By.NAME, "email").send_keys(TEST_EMAIL)
    driver.find_element(By.NAME, "password").send_keys(TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "form button[type=submit], form input[type=submit]").click()
    WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
    assert "login" not in driver.current_url


# ---------------------------------------------------------------------------
# Test 7: Clubs page loads and shows at least one club card
# ---------------------------------------------------------------------------
def test_clubs_page_loads(driver):
    driver.get(f"{BASE_URL}/clubs")
    wait_for(driver, By.CSS_SELECTOR, "body")
    assert "ClubSync" in driver.page_source
    # The seeded data should have at least one club listed
    assert driver.find_element(By.CLASS_NAME, "clubs-page")


# ---------------------------------------------------------------------------
# Test 8: Navigating to a club detail page shows club name
# ---------------------------------------------------------------------------
def test_club_detail_page(driver):
    driver.get(f"{BASE_URL}/clubs")
    wait_for(driver, By.CSS_SELECTOR, "a[href*='/clubs/']")
    club_link = driver.find_element(By.CSS_SELECTOR, "a[href*='/clubs/']")
    club_link.click()
    wait_for(driver, By.CSS_SELECTOR, "body")
    # Detail page should have member count text
    assert "member" in driver.page_source.lower()


# ---------------------------------------------------------------------------
# Test 9: Login with wrong password shows error message
# ---------------------------------------------------------------------------
def test_login_wrong_password(driver):
    driver.get(f"{BASE_URL}/logout")
    driver.get(f"{BASE_URL}/login")
    wait_for(driver, By.NAME, "email").send_keys(TEST_EMAIL)
    driver.find_element(By.NAME, "password").send_keys("wrongpassword")
    driver.find_element(By.CSS_SELECTOR, "form button[type=submit], form input[type=submit]").click()
    WebDriverWait(driver, 10).until(lambda d: "Invalid email or password" in d.page_source)
    assert "Invalid email or password" in driver.page_source


# ---------------------------------------------------------------------------
# Test 10: My Clubs page redirects to login when not authenticated
# ---------------------------------------------------------------------------
def test_myclubs_requires_login(driver):
    # Ensure logged out first
    driver.get(f"{BASE_URL}/logout")
    driver.get(f"{BASE_URL}/myclubs")
    # Should redirect to login
    WebDriverWait(driver, 10).until(lambda d: "login" in d.current_url or "Login" in d.page_source)
    assert "login" in driver.current_url or "Login" in driver.page_source
