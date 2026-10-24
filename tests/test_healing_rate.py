import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

from healer import find_with_healing

URL = "https://www.saucedemo.com"

# (how we search, broken value, what we want, the id the CORRECT element really has)
CASES = [
    (By.ID, "usr-name", "the username input on the login page", "user-name"),
    (By.ID, "pwd", "the password input on the login page", "password"),
    (By.ID, "login-btn", "the Login button on the login page", "login-button"),
    (By.CSS_SELECTOR, "input.login-submit", "the Login button on the login page", "login-button"),
    (By.XPATH, "//input[@id='username-field']", "the username input on the login page", "user-name"),
    (By.NAME, "pass-word", "the password input on the login page", "password"),
]


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(2)
    yield d
    d.quit()


@pytest.mark.parametrize("by,broken,description,expected_id", CASES)
def test_heal_returns_correct_element(driver, by, broken, description, expected_id):
    driver.get(URL)
    element = find_with_healing(driver, by, broken, description)
    # Real check: the healed element must be the correct one, not just any element
    assert element.get_attribute("id") == expected_id
