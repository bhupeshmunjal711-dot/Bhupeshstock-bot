from playwright.sync_api import sync_playwright

OUT = ["out of stock","currently unavailable","sold out","unavailable","not available"]
IN = ["add to cart","buy now","in stock","available"]

def check_product(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        text = page.locator("body").inner_text().lower()
        browser.close()

    # Explicit out-of-stock signals take priority.
    if any(x in text for x in OUT):
        return "OUT_OF_STOCK"
    if any(x in text for x in IN):
        return "IN_STOCK"
    return "UNKNOWN"
