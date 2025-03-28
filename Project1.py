from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

def setup_driver():
    options = Options()
    options.add_experimental_option("debuggerAddress", "localhost:9222")  # 👈 Connect to the browser you started manually
    return webdriver.Chrome(options=options)

from selenium.webdriver.common.by import By

def scrape_leaderboard(driver, year, board_type):
    url = f"https://www.atptour.com/en/stats/leaderboard?boardType={board_type}&timeFrame={year}&surface=all"
    driver.get(url)

    print(f"\n🌐 {board_type.upper()} leaderboard for {year} loaded. Solve Cloudflare if needed.")
    input(f"👉 Press ENTER once the {board_type.upper()} table is visible for {year}...")

    try:
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        headers = [th.text.strip() for th in rows[0].find_elements(By.TAG_NAME, "th")]
        data = []
        for row in rows[1:]:
            cells = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
            if cells:
                data.append(cells)

        df = pd.DataFrame(data, columns=headers)
        df["Year"] = year
        df["Board_Type"] = board_type
        return df

    except Exception as e:
        print(f"⚠️ Failed to scrape table for {board_type} {year}: {e}")
        return None



def main():
    driver = setup_driver()
    all_data = []

    for year in range(2024, 2013, -1):
        for board_type in ["serve", "return"]:
            try:
                df = scrape_leaderboard(driver, year, board_type)
                if df is not None:
                    all_data.append(df)
            except Exception as e:
                print(f"❌ Error for {board_type} {year}: {e}")

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv("atp_leaderboards_2014_2024.csv", index=False)
        print("✅ All data saved to 'atp_leaderboards_2014_2024.csv'")
    else:
        print("❌ No data was collected.")

if __name__ == "__main__":
    main()
