import pytest
from playwright.sync_api import sync_playwright, expect

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()
        
@pytest.fixture()
def context(browser):
    context = browser.new_context()
    yield context
    context.close()
    
@pytest.fixture()
def page(context):
    page = context.new_page()
    yield page
    page.close()
    
def test_second_example(page):
    page.goto("https://practicesoftwaretesting.com/")
    
    page.locator('[data-test="search-query"]').fill("Hammer")
    page.locator('[data-test="search-submit"]').click()
    
    products = page.locator('[data-test="product-name"]')
    prices = page.locator('[data-test="product-price"]')
    expect(products.first).to_be_visible()
    
    page.locator('[data-test="sort"]').select_option("price,desc")
    
    page.wait_for_function(
    """(priceSelector) => {
        const priceEls = Array.from(document.querySelectorAll(priceSelector));
        const firstPrice = parseFloat(priceEls[0].innerText.replace('$',''));
        const maxPrice = Math.max(...priceEls.map(p => parseFloat(p.innerText.replace('$',''))));
        return firstPrice === maxPrice;
    }""",
    arg='[data-test="product-price"]',
    timeout=10000
)
    
    products.first.click()
     
    product_price = page.locator('[data-test="unit-price"]').inner_text()
    product_title = page.locator('[data-test="product-name"]').inner_text()

    page.locator('[data-test="increase-quantity"]').click()
    page.locator('[data-test="add-to-cart"]').click()
    
    page.locator('[data-test="nav-cart"]').click()
    
    expect(page.locator('[data-test="product-title"]')).to_contain_text(product_title)
    expect(page.locator('[data-test="product-quantity"]')).to_have_value("2")
    expect(page.locator('[data-test="product-price"]')).to_contain_text(product_price)