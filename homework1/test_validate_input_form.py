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
    
def test_example(page):
    test_first_name = "test name"
    test_last_name = "test last name"
    test_age = "18"
    test_notes = "test 123"

    page.goto("https://testpages.eviltester.com/styled/validation/input-validation.html")
    
    page.get_by_role("textbox", name="First name").fill(test_first_name)
    page.get_by_role("textbox", name="Last name").fill(test_last_name)
    page.get_by_role("spinbutton", name="Age").fill(test_age)
    page.get_by_label("Country:").select_option("Belgium")
    page.get_by_role("textbox", name="Notes").fill(test_notes)
    page.get_by_role("button", name="Submit").click()
    
    expect(page.locator("#firstname-value"),
           f"Expected first name to be '{test_first_name}' but found different").to_have_text(test_first_name)
    expect(page.locator("#surname-value")).to_have_text(test_last_name)
    expect(page.locator("#age-value")).to_have_text(test_age)
    expect(page.locator("#country-value")).to_have_text("Belgium")
    expect(page.locator("#notes-value")).to_have_text(test_notes)