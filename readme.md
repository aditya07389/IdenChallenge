# Iden Challenge: Automated Product Data Extractor

## 📝 Summary

This repository contains a Python script developed as a solution for the Iden Integration Engineer Challenge. The script uses Playwright to perform end-to-end browser automation, logging into a secure web application, navigating to a product catalog, and extracting a complete dataset from a dynamically loaded list.

The solution is designed to be robust, secure, and resilient, demonstrating professional software development practices.

---

## ✨ Features

-   **Secure Credential Handling**: Uses environment variables to manage credentials, ensuring no sensitive information is hardcoded in the source code.
-   **Intelligent Session Management**: Checks for, reuses, and saves login sessions (`auth_state.json`) to significantly speed up subsequent runs.
-   **Robust Dynamic Scraping**: Implements a "scrape-as-you-scroll" technique to reliably handle "infinite scroll" pages, ensuring all products are captured.
-   **Resilient Checkpointing**: Saves progress incrementally to the output file every 10 products, preventing data loss in case of interruption during long scraping jobs.
-   **Structured Data Output**: Exports the final, complete dataset into a clean, well-formatted `products.json` file for easy analysis.

---

## ⚙️ Setup and Installation

Follow these steps to set up the environment and run the script.

### Prerequisites

-   Python 3.8+
-   Git

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **Install the required Python package:**
    ```bash
    pip install playwright
    ```

3.  **Install the necessary browser binaries for Playwright:**
    ```bash
    python -m playwright install
    ```

---

## 🚀 How to Run

### 1. Configure Credentials

This script requires credentials to be set as environment variables before execution.

**On Windows (PowerShell):**
```powershell
$env:IDEN_USERNAME="your_email@example.com"
$env:IDEN_PASSWORD="your_password_here"
```

**On macOS / Linux (Bash/Zsh):**
```bash
export IDEN_USERNAME="your_email@example.com"
export IDEN_PASSWORD="your_password_here"
```

### 2. Execute the Script

Once the environment variables are set, run the script from your terminal:
```bash
python scraper.py
```

---

## 🤖 Script Logic Explained

The script executes the following steps to accomplish its mission:

1.  **Initialization**: The script starts and checks if the required `IDEN_USERNAME` and `IDEN_PASSWORD` environment variables are available.

2.  **Session Handling**: It first looks for an `auth_state.json` file. If a valid session file exists, it injects it into a new browser context to bypass the login process and load directly into the application.

3.  **Authentication**: If no session file is found, the script performs a full, one-time login by navigating to the login page, entering the credentials, and clicking through the post-login steps. Upon success, it saves the browser state to `auth_state.json` for future runs.

4.  **Navigation**: After a successful login, it follows the specified breadcrumb trail: **Dashboard → Inventory → Products → Full Catalog**.

5.  **Data Extraction**: On the product page, it begins the core "scrape-as-you-scroll" loop. This loop repeatedly:
    -   Finds all product elements currently visible on the page.
    -   Checks each product's ID against a set of already scraped IDs to avoid duplicates.
    -   Scrapes all required data fields for any new products.
    -   Scrolls to the bottom of the page to trigger the loading of more products.

6.  **Checkpointing**: For resilience, the script saves the entire list of currently scraped products to `products.json` after every 10 new items are found. This ensures that progress is not lost if the script is interrupted.

7.  **Completion**: The loop terminates automatically when a full scroll cycle yields no new products. A final save is then performed to capture any remaining items. The browser is then gracefully closed.

## 📁 Output Files

-   `products.json`: The final, structured JSON output containing all extracted product data.
-   `auth_state.json`: The session file created after the first successful login. This should be kept private and is included in the `.gitignore` file.
