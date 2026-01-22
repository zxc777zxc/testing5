import time
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


BASE_URL = "https://phptravels.net/"


# --------------------- helpers ---------------------

def js_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    driver.execute_script("arguments[0].click();", element)


def wait_clickable(driver, locator, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def wait_visible(driver, locator, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))


def wait_present(driver, locator, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def close_bottom_banner(driver):
    try:
        btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Hide' or contains(.,'Hide')]"))
        )
        js_click(driver, btn)
        time.sleep(0.3)
    except Exception:
        pass


def find_visible(driver, by, value):
    els = driver.find_elements(by, value)
    for e in els:
        try:
            if e.is_displayed():
                return e
        except Exception:
            continue
    return None


def click_visible(driver, by, value, timeout=20):
    end = time.time() + timeout
    last = None
    while time.time() < end:
        el = find_visible(driver, by, value)
        if el:
            try:
                js_click(driver, el)
                return el
            except Exception as ex:
                last = ex
        time.sleep(0.2)
    raise TimeoutException(f"Cannot click visible element: {value}. Last error: {last}")


def click_first_featured_hotel(driver, timeout=25):
    wait_present(driver, (By.XPATH, "//*[contains(normalize-space(),'Featured Hotels')]"), timeout)

    candidates = driver.find_elements(
        By.XPATH,
        "//*[contains(normalize-space(),'Featured Hotels')]/following::a"
        "[contains(@href,'hotel') or contains(@href,'hotels')][not(contains(.,'View More'))]"
    )

    visible = []
    for a in candidates:
        try:
            if a.is_displayed():
                txt = (a.text or "").strip()
                visible.append(a)
        except Exception:
            continue

    visible = visible[:3] if len(visible) >= 3 else visible

    if not visible:
        card = click_visible(driver, By.XPATH,
                            "//*[contains(normalize-space(),'Featured Hotels')]/following::*"
                            "[self::div or self::a][.//img][1]",
                            timeout=timeout)
        return card

    js_click(driver, visible[0])
    return visible[0]


def click_first_book_now_in_rooms(driver, timeout=25):
    wait_present(driver, (By.XPATH, "//*[normalize-space()='Rooms' or contains(normalize-space(),'Rooms')]"), timeout)

    book_btn = click_visible(driver, By.XPATH, "//button[contains(.,'Book Now') or contains(.,'Book now')]", timeout=timeout)
    return book_btn

def click_first_popular_tour(driver, timeout=25):
    wait = WebDriverWait(driver, timeout)

    popular = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Popular Tours')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", popular)
    time.sleep(0.6)

    first_tile = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "(//*[contains(normalize-space(),'Popular Tours')]/following::*"
            "[contains(@class,'item') or contains(@class,'card') or contains(@class,'tour') or self::a][1])"
            " | (//*[contains(normalize-space(),'Popular Tours')]/following::a[.//*[self::strong or self::h3 or self::h4 or self::span]][1])"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", first_tile)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", first_tile)


def click_book_now_on_tour(driver, timeout=25):
    wait = WebDriverWait(driver, timeout)

    book_btn = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(.,'Book Now') or contains(.,'Book now')]"
            " | //a[contains(.,'Book Now') or contains(.,'Book now')]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", book_btn)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", book_btn)


def tick_terms_and_conditions(driver, timeout=15):
    candidates = driver.find_elements(
        By.XPATH,
        "//input[@type='checkbox' and (contains(@id,'agree') or contains(@name,'agree') or contains(@class,'agree'))]"
        " | //input[@type='checkbox']"
    )

    for cb in candidates:
        try:
            if cb.is_displayed() and cb.is_enabled():
                wrapper_text = ""
                try:
                    wrapper_text = cb.find_element(By.XPATH, "./ancestor::*[1]").text.lower()
                except Exception:
                    pass
                if ("agree" in wrapper_text) or ("terms" in wrapper_text) or ("condition" in wrapper_text):
                    if not cb.is_selected():
                        js_click(driver, cb)
                        time.sleep(0.2)
                    return True
        except Exception:
            continue

    el = wait_clickable(
        driver,
        (
            By.XPATH,
            "//*[self::label or self::span or self::div]"
            "[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'i agree')]"
            " | //label[contains(.,'I agree')]"
        ),
        timeout,
    )
    js_click(driver, el)
    time.sleep(0.2)
    return True



# --------------------- TEST 1: VISA ---------------------

@pytest.mark.ui
def test_01_visa_flow_fill_form(driver, logger, shot):
    logger.info("[VISA] Start")
    driver.get(BASE_URL)
    close_bottom_banner(driver)

    logger.info("[VISA] Open Visa tab")
    visa_link = wait_clickable(driver, (By.XPATH, "//a[normalize-space()='Visa']"), 20)
    js_click(driver, visa_link)

    logger.info("[VISA] Wait Visa section")
    wait_present(driver, (By.XPATH, "//*[contains(.,'Submit Your Visa Today')]"), 20)
    close_bottom_banner(driver)

    logger.info("[VISA] Select countries via <select>")
    selects = driver.find_elements(By.XPATH, "//section//select")
    assert len(selects) >= 2, "No 2 dropdowns <select> found for countries on the Visa page"

    from_select = Select(selects[0])
    to_select = Select(selects[1])

    from_select.select_by_visible_text("Kazakhstan")
    to_select.select_by_visible_text("Turkey")

    logger.info("[VISA] Click Search button")
    search_btn = wait_clickable(driver, (By.XPATH, "//button[contains(@class,'btn')][.//i or .//*[name()='svg']]"), 20)
    js_click(driver, search_btn)

    logger.info("[VISA] Wait visa form page")
    wait_present(driver, (By.XPATH, "//*[contains(.,'Submission Form')]"), 20)
    close_bottom_banner(driver)

    logger.info("[VISA] Fill form fields")
    first = wait_clickable(driver, (By.XPATH, "//input[contains(@placeholder,'First') or contains(@name,'first') or contains(@id,'first')]"), 20)
    first.clear(); first.send_keys("Test")

    last = wait_present(driver, (By.XPATH, "//input[contains(@placeholder,'Last') or contains(@name,'last') or contains(@id,'last')]"), 20)
    last.clear(); last.send_keys("User")

    email = wait_present(driver, (By.XPATH, "//input[@type='email' or contains(@name,'email') or contains(@id,'email')]"), 20)
    email.clear(); email.send_keys("test.user@example.com")

    phone = wait_present(driver, (By.XPATH, "//input[contains(@placeholder,'Phone') or contains(@name,'phone') or contains(@id,'phone')]"), 20)
    phone.clear(); phone.send_keys("+77001234567")

    logger.info("[VISA] Click Submit")
    submit_btn = wait_clickable(
        driver,
        (
            By.XPATH,
            "//button[normalize-space()='Submit' or contains(.,'Submit')]"
            " | //input[@type='submit']"
            " | //button[contains(@class,'btn') and (contains(.,'Submit') or contains(.,'submit'))]"
        ),
        25,
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
    time.sleep(0.3)
    js_click(driver, submit_btn)

    logger.info("[VISA] Wait Submitted page and take screenshot")
    wait_present(driver, (By.XPATH, "//*[contains(.,'Submitted') or contains(.,'Thank You')]"), 25)
    close_bottom_banner(driver)
    shot("visa_submitted_page")

    logger.info("[VISA] End")
    assert True


# --------------------- TEST 2: Hotel Booking ---------------------

@pytest.mark.ui
def test_02_featured_hotel_booking_flow(driver, logger, shot):
    logger.info("[HOTEL] Start")
    driver.get(BASE_URL)
    close_bottom_banner(driver)

    logger.info("[HOTEL] Click one of Featured Hotels")
    click_first_featured_hotel(driver, timeout=25)

    logger.info("[HOTEL] Wait hotel page loaded (title or rooms section later)")
    WebDriverWait(driver, 25).until(lambda d: "phptravels.net" in d.current_url)
    close_bottom_banner(driver)

    logger.info("[HOTEL] Scroll to Rooms and click Book Now")
    click_first_book_now_in_rooms(driver, timeout=25)

    logger.info("[HOTEL] Wait Booking page (Personal Information)")
    wait_present(driver, (By.XPATH, "//*[contains(normalize-space(),'Personal Information')]"), 25)
    close_bottom_banner(driver)

    logger.info("[HOTEL] Fill booking form (Personal Information)")
    # Personal Information fields
    fn = wait_clickable(driver, (By.XPATH, "//input[contains(@placeholder,'First Name') or contains(@name,'first') or contains(@id,'first')]"), 20)
    fn.clear(); fn.send_keys("Test")

    ln = wait_present(driver, (By.XPATH, "//input[contains(@placeholder,'Last Name') or contains(@name,'last') or contains(@id,'last')]"), 20)
    ln.clear(); ln.send_keys("User")

    em = wait_present(driver, (By.XPATH, "//input[@type='email' or contains(@placeholder,'Email') or contains(@name,'email') or contains(@id,'email')]"), 20)
    em.clear(); em.send_keys("test.user@example.com")

    ph = wait_present(driver, (By.XPATH, "//input[contains(@placeholder,'Phone') or contains(@name,'phone') or contains(@id,'phone')]"), 20)
    ph.clear(); ph.send_keys("+77001234567")

    try:
        addr = driver.find_element(By.XPATH, "//input[contains(@placeholder,'Address') or contains(@name,'address') or contains(@id,'address')]")
        if addr.is_displayed():
            addr.clear()
            addr.send_keys("Almaty, Kazakhstan")
    except Exception:
        pass

    logger.info("[HOTEL] Fill Travellers Information (if visible)")
    try:
        t_fn = driver.find_element(By.XPATH, "(//*[contains(.,'Travellers Information')]/following::input[contains(@placeholder,'First Name')])[1]")
        t_ln = driver.find_element(By.XPATH, "(//*[contains(.,'Travellers Information')]/following::input[contains(@placeholder,'Last Name')])[1]")
        if t_fn.is_displayed():
            t_fn.clear(); t_fn.send_keys("Test")
        if t_ln.is_displayed():
            t_ln.clear(); t_ln.send_keys("User")
    except Exception:
        pass

    logger.info("[HOTEL] Tick Terms & Conditions checkbox")
    tick_terms_and_conditions(driver, timeout=15)

    logger.info("[HOTEL] Click Booking Confirm")
    confirm_btn = wait_clickable(driver,
                                 (By.XPATH, "//button[contains(.,'Booking Confirm') or contains(.,'Booking confirm')]"),
                                 25)
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", confirm_btn)
    time.sleep(0.3)
    js_click(driver, confirm_btn)

    logger.info("[HOTEL] Wait Invoice/Result page and take screenshot")
    try:
        WebDriverWait(driver, 25).until(
            lambda d: ("invoice" in d.current_url.lower())
                      or ("tours/invoice" in d.current_url.lower())
                      or ("hotels/invoice" in d.current_url.lower())
        )
    except Exception:
        pass

    wait_present(driver, (
    By.XPATH, "//*[contains(.,'Payment Status') or contains(.,'Booking Status') or contains(.,'Invoice')]"), 25)
    close_bottom_banner(driver)
    shot("hotel_after_booking_confirm_invoice")

    logger.info("[HOTEL] End")
    assert True


# --------------------- TEST 3: Tour booking ---------------------

@pytest.mark.ui
def test_03_popular_tour_booking_flow(driver, logger, shot):
    logger.info("[TOUR] Start")
    driver.get(BASE_URL)
    close_bottom_banner(driver)

    logger.info("[TOUR] Open Tours tab from header")
    tours_link = wait_clickable(driver, (By.XPATH, "//a[normalize-space()='Tours']"), 25)
    js_click(driver, tours_link)

    logger.info("[TOUR] Wait Tours page loaded")
    WebDriverWait(driver, 25).until(EC.url_contains("/tours"))
    close_bottom_banner(driver)

    logger.info("[TOUR] Click one of Popular Tours")
    click_first_popular_tour(driver, timeout=25)

    logger.info("[TOUR] Wait tour details page loaded")
    WebDriverWait(driver, 25).until(lambda d: "phptravels.net" in d.current_url)
    close_bottom_banner(driver)

    logger.info("[TOUR] Click Book Now on tour page")
    click_book_now_on_tour(driver, timeout=25)

    logger.info("[TOUR] Wait Booking page (Personal Information)")
    wait_present(driver, (By.XPATH, "//*[contains(normalize-space(),'Personal Information')]"), 25)
    close_bottom_banner(driver)

    logger.info("[TOUR] Fill booking form (Personal Information)")
    fn = wait_clickable(driver, (By.XPATH, "//input[contains(@placeholder,'First Name') or contains(@name,'first') or contains(@id,'first')]"), 20)
    fn.clear(); fn.send_keys("Test")

    ln = wait_present(driver, (By.XPATH, "//input[contains(@placeholder,'Last Name') or contains(@name,'last') or contains(@id,'last')]"), 20)
    ln.clear(); ln.send_keys("User")

    em = wait_present(driver, (By.XPATH, "//input[@type='email' or contains(@placeholder,'Email') or contains(@name,'email') or contains(@id,'email')]"), 20)
    em.clear(); em.send_keys("test.user@example.com")

    ph = wait_present(driver, (By.XPATH, "//input[contains(@placeholder,'Phone') or contains(@name,'phone') or contains(@id,'phone')]"), 20)
    ph.clear(); ph.send_keys("+77001234567")

    try:
        addr = driver.find_element(By.XPATH, "//input[contains(@placeholder,'Address') or contains(@name,'address') or contains(@id,'address')]")
        if addr.is_displayed():
            addr.clear()
            addr.send_keys("Almaty, Kazakhstan")
    except Exception:
        pass

    logger.info("[TOUR] Fill Travellers Information (if visible)")
    try:
        t_fn = driver.find_element(By.XPATH, "(//*[contains(.,'Travellers Information')]/following::input[contains(@placeholder,'First Name')])[1]")
        t_ln = driver.find_element(By.XPATH, "(//*[contains(.,'Travellers Information')]/following::input[contains(@placeholder,'Last Name')])[1]")
        if t_fn.is_displayed():
            t_fn.clear(); t_fn.send_keys("Test")
        if t_ln.is_displayed():
            t_ln.clear(); t_ln.send_keys("User")
    except Exception:
        pass

    logger.info("[TOUR] Tick Terms & Conditions checkbox")
    tick_terms_and_conditions(driver, timeout=15)

    logger.info("[TOUR] Click Booking Confirm")
    confirm_btn = wait_clickable(driver,
                                 (By.XPATH, "//button[contains(.,'Booking Confirm') or contains(.,'Booking confirm')]"),
                                 25)
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", confirm_btn)
    time.sleep(0.3)
    js_click(driver, confirm_btn)

    logger.info("[TOUR] Wait Invoice/Result page and take screenshot")
    try:
        WebDriverWait(driver, 25).until(lambda d: "invoice" in d.current_url.lower())
    except Exception:
        pass

    wait_present(driver, (
    By.XPATH, "//*[contains(.,'Payment Status') or contains(.,'Booking Status') or contains(.,'Invoice')]"), 25)
    close_bottom_banner(driver)
    shot("tour_after_booking_confirm_invoice")

    logger.info("[TOUR] End")
    assert True