import os
import base64
import logging
import datetime as dt
import pytest

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

BASE_URL = "https://phptravels.net/"


def ensure_dirs():
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)


@pytest.fixture(scope="session")
def run_id():
    ensure_dirs()
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


@pytest.fixture(scope="session")
def logger(run_id):
    logger = logging.getLogger(f"ui-tests-{run_id}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        fh = logging.FileHandler(f"logs/test_run_{run_id}.log", encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)

    return logger


@pytest.fixture(scope="function")
def driver(logger):
    logger.info("=== SETUP: start Edge browser ===")

    options = Options()
    options.add_argument("--start-maximized")

    service = Service("edgedriver_win64/msedgedriver.exe")
    drv = webdriver.Edge(service=service, options=options)
    drv.set_page_load_timeout(60)

    yield drv

    logger.info("=== TEARDOWN: quit browser ===")
    drv.quit()


def _save_png(driver, name: str) -> str:
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name)
    path = os.path.join("screenshots", f"{safe}.png")
    driver.save_screenshot(path)
    return path


def _png_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@pytest.fixture(scope="function")
def shot(driver, request):
    def _do(step_name: str):
        path = _save_png(driver, f"{request.node.name}__{step_name}")
        try:
            import pytest_html
            extras = getattr(request.node, "_html_extras", [])
            extras.append(pytest_html.extras.png(_png_to_b64(path), mime_type="image/png"))
            request.node._html_extras = extras
        except Exception:
            pass
        return path

    return _do



@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    report.extras = getattr(report, "extras", [])

    report.extras += getattr(item, "_html_extras", [])

    try:
        import glob
        import pytest_html

        logs = sorted(glob.glob("logs/test_run_*.log"))
        if logs:
            report.extras.append(pytest_html.extras.url(logs[-1], name="Log file"))
    except Exception:
        pass

    if report.failed:
        drv = item.funcargs.get("driver", None)
        if drv:
            path = _save_png(drv, f"FAIL__{item.name}")
            try:
                import pytest_html
                report.extras.append(
                    pytest_html.extras.png(_png_to_b64(path), mime_type="image/png")
                )
            except Exception:
                pass



def pytest_configure(config):
    config._metadata = getattr(config, "_metadata", {})
    config._metadata["Base URL"] = BASE_URL
