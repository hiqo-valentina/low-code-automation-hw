from playwright.sync_api import Page, expect, Route
from http.cookies import SimpleCookie


def test_api_examples(page: Page) -> None:
    created_contact = {}
    base_url = "https://thinking-tester-contact-list.herokuapp.com"
    login_email = "random@mail.org"
    login_pwd = "1234567"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone_number = "123456789"

    # Task-Part-3.1: Add country data to the request payload in the Add Contact request interception
    def handle_contacts(route: Route):
        # intercept Add Contact request
        if route.request.method == "POST":
            original_payload = route.request.post_data_json
            original_payload["country"] = "USA"
            response = route.fetch(post_data=original_payload)
            nonlocal created_contact
            created_contact = response.json()
            route.fulfill(response=response)
        # intercept Get Contact List request   
        elif route.request.method == "GET":
            response = route.fetch()
            json = response.json()
            json.append({"_id": "001", "firstName": "Fake", "lastName": "Contact", "email": "fake@mail.com",
                        "phone": "12345", "owner": "6894ad53a0504000151c0ba5", "__v": 0})
            route.fulfill(response=response, json=json)        
        else:
            route.continue_()

    page.route("**/contacts", handle_contacts)

    # login via API
    response = page.request.post(url=base_url + "/users/login",
                      data={"email": login_email, "password": login_pwd})
    assert response.ok, "Login response status should be OK"
    assert "set-cookie" in response.headers, "Login response should contain set-cookie header"
 
    # Task-Part-2: Replace logic from the block above - retrieve auth token from the browser context (hint: use page.context.cookies())
    cookies = page.context.cookies()
    token = next(cookie["value"] for cookie in cookies if cookie["name"] == "token")
    
    # UI test part - add new contact
    page.goto(base_url + "/contactList")
    page.get_by_role("button", name="Add a New Contact").click()
    page.locator("#firstName").fill(first_name)
    page.locator("#lastName").fill(last_name)
    page.locator("#email").fill(email)
    page.locator("#phone").fill(phone_number)
    page.get_by_role("button", name="Submit").click()
    expect(page.locator("#myTable")).to_be_visible()

    # verify created entity
    assert created_contact["firstName"] == first_name, "Created contact first name should equal to that entered"
    assert created_contact["lastName"] == last_name, "Created contact last name should equal to that entered"
    assert created_contact["email"] == email, "Created contact email should equal to that entered"
    assert created_contact["phone"] == phone_number, "Created contact phone should equal to that entered"
    # Task-Part-3.2: Add an assertion for country field
    assert created_contact["country"] == "USA", "Created contact country should equal the modified value"

    # Task-Part-4: Update the contact's firstName using PATCH API request, assert the response status and the updated field value
    updated_first_name = "Bill"

    response = page.request.patch(
        url = base_url + "/contacts/" + created_contact["_id"],
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        },
        data = {
            "firstName": updated_first_name
        }
    )
    
    assert response.ok, "Update Contact response status should be OK"

    updated_contact = response.json()
    assert updated_contact["firstName"] == updated_first_name, \
        "Contact firstName should be updated via PATCH request"
        
    # clean server state
    response = page.request.delete(url=base_url + "/contacts/" + created_contact["_id"], 
                     headers={"Authorization": "Bearer " + token})
    assert response.ok, "Delete Contact response status should be OK"