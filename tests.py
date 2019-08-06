import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy import create_engine


@pytest.yield_fixture()
def driver():
    driver = webdriver.Chrome(
        executable_path='chromedriver2.43'
    )
    driver.set_window_size(1024, 800)
    driver.implicitly_wait(3)
    driver.set_page_load_timeout(5)
    driver.get('http://localhost:58001/')
    yield driver
    driver.quit()

@pytest.yield_fixture()
def wait(driver):
    wait = WebDriverWait(driver, 5)
    yield wait
    del(wait)

@pytest.yield_fixture()
def psql_connect():
    psql = create_engine('postgresql://postgres:devpass@localhost:5433/core')
    db_connect = psql.connect()
    yield db_connect
    db_connect.close()


def test_window_visible(wait):
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="NPS"]')))

def test_window_not_visible(driver, wait):
    driver.add_cookie(
        {
            "name" : 'NPS_sended',
            'value' : '1',
            'domain' : 'localhost'
        }
    )
    driver.refresh()
    wait.until_not(EC.element_to_be_clickable((By.XPATH, '//div[@class="NPS"]')))

def test_send_hight_opinion(driver, wait):
    button_10 = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.NPS__button.n10')
        )
    )
    button_10.click()
    assert driver.get_cookie('NPS_sended')['value'] == '1'

def test_send_low_opinion(driver, wait):
    button_0 = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.NPS__button.n0')
        )
    )
    button_0.click()
    comment_textarea = wait.until(
        EC.element_to_be_clickable(
            (By.ID, 'feedbackTextarea')
        )
    )
    comment_textarea.send_keys('time_now')
    send_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button.NPS__feedback-send')
        )
    )
    send_btn.click()
    assert driver.get_cookie('NPS_sended')['value'] == '1'

def test_db_save_low_result(wait, psql_connect):
    time_now = str(time.time())
    button_0 = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.NPS__button.n0')
        )
    )
    button_0.click()
    comment_textarea = wait.until(
        EC.element_to_be_clickable(
            (By.ID, 'feedbackTextarea')
        )
    )
    comment_textarea.send_keys(time_now)
    send_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button.NPS__feedback-send')
        )
    )
    send_btn.click()

    req = 'select result from t_feedback_models where feedback = \'{}\''.format(time_now)
    res = psql_connect.execute(req)
    assert res.returns_rows
