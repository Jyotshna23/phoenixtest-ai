import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

URL = "https://www.saucedemo.com"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(5)
    yield d
    d.quit()


def login(driver):
    driver.get(URL)
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()


def test_login(driver):
    login(driver)
    assert "inventory" in driver.current_url


def test_add_to_cart(driver):
    login(driver)
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    badge = driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
    assert badge.text == "1"


def test_checkout(driver):
    login(driver)
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    driver.find_element(By.ID, "checkout").click()
    driver.find_element(By.ID, "first-name").send_keys("Jyotshna")
    driver.find_element(By.ID, "last-name").send_keys("Pogiri")
    driver.find_element(By.ID, "postal-code").send_keys("500072")
    driver.find_element(By.ID, "continue").click()
    driver.find_element(By.ID, "finish").click()
    assert "checkout-complete" in driver.current_url