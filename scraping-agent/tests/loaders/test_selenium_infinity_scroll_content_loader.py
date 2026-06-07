from bs4 import BeautifulSoup
import pytest

from scraperkit.loaders.selenium_infinity_scroll_content_loader import (
    SeleniumInfinityScrollContentLoader,
)


SOULED_STORE_LISTING_URL = "https://www.thesouledstore.com/men-classic-tshirts"
SOULED_STORE_TARGET_CLASS = "tss-footer"


def build_loader(**overrides):
    overrides.setdefault("target_class_name", SOULED_STORE_TARGET_CLASS)
    overrides.setdefault("scroll_delay", 2)
    overrides.setdefault("headless", True)
    overrides.setdefault("max_scrolls", 4)
    return SeleniumInfinityScrollContentLoader(**overrides)


def extract_product_card_count(page_content):
    soup = BeautifulSoup(page_content, "html.parser")
    return len(soup.find_all("div", class_="productCard"))


@pytest.mark.integration
def test_infinity_scroll_loader_loads_real_page_content():
    loader = build_loader(max_scrolls=2)

    try:
        page_content = loader.load_content(SOULED_STORE_LISTING_URL)
    finally:
        loader.close()

    assert "<html" in page_content.lower()
    assert extract_product_card_count(page_content) > 0


@pytest.mark.integration
def test_infinity_scroll_loader_performs_multiple_scrolls_on_real_page():
    loader = build_loader(max_scrolls=4)
    original_execute_script = loader.driver.execute_script
    scroll_scripts = []

    def tracked_execute_script(script, *args):
        if "scrollIntoView" in script or "window.scrollTo" in script:
            scroll_scripts.append(script)
        return original_execute_script(script, *args)

    loader.driver.execute_script = tracked_execute_script

    try:
        page_content = loader.load_content(SOULED_STORE_LISTING_URL)
    finally:
        loader.close()

    assert extract_product_card_count(page_content) > 0
    assert len(scroll_scripts) >= 2


@pytest.mark.integration
def test_infinity_scroll_loader_with_more_scrolls_keeps_or_increases_loaded_cards():
    short_loader = build_loader(max_scrolls=1)
    long_loader = build_loader(max_scrolls=4)

    try:
        short_content = short_loader.load_content(SOULED_STORE_LISTING_URL)
    finally:
        short_loader.close()

    try:
        long_content = long_loader.load_content(SOULED_STORE_LISTING_URL)
    finally:
        long_loader.close()

    short_count = extract_product_card_count(short_content)
    long_count = extract_product_card_count(long_content)

    assert short_count > 0
    assert long_count >= short_count
