import json
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, expect
import os
import sys

# --- Configuration ---
BASE_URL = "https://hiring.idenhq.com"
LOGIN_URL = "https://hiring.idenhq.com"
SESSION_FILE = Path("auth_state.json")

# Fill in your credentials here ⬇️
USERNAME = os.getenv("IDEN_USERNAME")
PASSWORD = os.getenv("IDEN_PASSWORD")


def run(page: Page):
    """Handles the main navigation and initiates the scraping process."""
    print("Navigating the hidden path to the products table...")
    page.get_by_role("button", name="Dashboard").click()
    page.get_by_text("Inventory").click()
    page.get_by_text("Products").click()
    page.get_by_text("Full Catalog").click()

    print("Successfully navigated to the products page...")

    output_file = Path("products.json")
    total_products = scrape_all_pages(page, output_file)

    print(f"✅ Exported {total_products} products to {output_file}")


def scrape_all_pages(page: Page, output_file: Path) -> int:
    """Scrolls, scrapes, and saves progress incrementally for maximum resilience."""
    product_item_selector = "div.space-y-2 > div"
    print("Waiting for initial products to load...")
    page.wait_for_selector(product_item_selector, state="visible", timeout=15000)
    
    scraped_products = []
    scraped_product_ids = set()

    print("Starting scroll and scrape process...")
    while True:
        product_items = page.locator(product_item_selector).all()
        new_products_found_this_scroll = 0

        for item in product_items:
            try:
                id_text = item.locator("div.text-muted-foreground > span:first-child").inner_text()
                product_id = id_text.split(":")[1].strip()

                if product_id not in scraped_product_ids:
                    new_products_found_this_scroll += 1
                    scraped_product_ids.add(product_id)

                    name = item.locator("h3").inner_text()
                    price_text = item.locator('span:text-is("Price") + span.font-medium').inner_text()
                    item_code = item.locator('span:text-is("Item Code") + span.font-medium').inner_text()
                    score = item.locator('span:text-is("Score") + span.font-medium').inner_text()
                    updated = item.locator('span:text-is("Updated") + span.font-medium').inner_text()

                    product_data = {
                        "name": name,
                        "id": product_id,
                        "price": price_text.strip('$'),
                        "item_code": item_code,
                        "score": score,
                        "updated": updated,
                    }
                    scraped_products.append(product_data)
                    
                    # Save progress after every 10 new products are scraped
                    if len(scraped_products) % 10 == 0:
                        print(f"--- Checkpoint: Scraped {len(scraped_products)} products. Saving progress... ---")
                        with open(output_file, "w") as f:
                            json.dump(scraped_products, f, indent=4)
            except Exception:
                continue
        
        print(f"Found {len(scraped_products)} products so far...")

        page.keyboard.press("End")
        page.wait_for_timeout(3000)

        if new_products_found_this_scroll == 0:
            print("No new products found after scroll. Reached the end of the list.")
            break
            
    # Perform one final save to ensure all products are written to the file
    print("--- Scraping complete. Performing final save... ---")
    with open(output_file, "w") as f:
        json.dump(scraped_products, f, indent=4)
        
    return len(scraped_products)


def main():
    """Main function to launch the browser and orchestrate the process."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = None
        
        if SESSION_FILE.exists():
            print(f"Attempting to use existing session file: {SESSION_FILE}")
            try:
                context = browser.new_context(storage_state=SESSION_FILE)
                page = context.new_page()
                page.goto(BASE_URL)
                expect(page.get_by_role("button", name="Dashboard")).to_be_visible(timeout=5000)
                print("Session loaded successfully.")
            except Exception as e:
                print(f"Could not use session file. Re-authenticating. Error: {e}")
                context = None
                
        if not context:
            print("No valid session found. Performing login...")
            context = browser.new_context()
            page = context.new_page()
            page.goto(LOGIN_URL)
            page.get_by_placeholder("name@example.com").fill(USERNAME)
            page.get_by_label("Password").fill(PASSWORD)
            page.get_by_role("button", name="Sign in").click()

            page.wait_for_url("**/instructions", timeout=10000)
            print("Login successful, landed on instructions page.")

            page.get_by_role("button", name="Launch Challenge").click()
            print("Clicked 'Launch Challenge' button.")
            
            page.wait_for_url("**/challenge", timeout=10000)
            print("Challenge dashboard loaded successfully.")

            context.storage_state(path=SESSION_FILE)
            print(f"Session state saved to '{SESSION_FILE}'.")
            
        run(page)
        
        context.close()
        browser.close()


if __name__ == "__main__":
    main()