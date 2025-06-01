import requests
import pandas as pd
from bs4 import BeautifulSoup

# Define URL
rate_limits_url = "https://ai.google.dev/gemini-api/docs/rate-limits"

# --- Function to fetch and parse content ---
def fetch_and_parse(url):
    try:
        print(f"Fetching {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Will raise an HTTPError for bad responses (4XX or 5XX)
        print(f"Successfully fetched {url}.")
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return None

# --- Fetch and parse page ---
soup = fetch_and_parse(rate_limits_url)

free_tier_limits_data = []

if soup:
    print("\nLooking for the 'Free tier' section and its rate limits table...")
    
    # 1. Find the anchor element for the "Free tier" section.
    #    This is commonly a heading (h1, h2, h3, etc.) with id="free-tier".
    free_tier_anchor = soup.find(id="free-tier")
    
    if free_tier_anchor:
        print(f"Found anchor element for 'Free tier': <{free_tier_anchor.name}> {free_tier_anchor.text[:50]}...")
        
        # 2. Find the table that contains the free tier rate limits.
        #    This table is usually the next 'table' sibling or one of the next few general siblings.
        #    We'll look for the first table that appears after this anchor.
        
        free_tier_table = None
        current_element = free_tier_anchor
        # Iterate through next siblings to find the table
        while current_element:
            if current_element.name == 'table':
                free_tier_table = current_element
                print("Found the rate limits table associated with the 'Free tier' section.")
                break
            current_element = current_element.find_next_sibling()

        if not free_tier_table:
            # Fallback if not a direct sibling, try finding the next table tag generally
            free_tier_table = free_tier_anchor.find_next('table')
            if free_tier_table:
                 print("Found the rate limits table (using find_next) associated with the 'Free tier' section.")
            else:
                print("Could not find the table for 'Free tier' rate limits. The page structure might have changed.")

        if free_tier_table:
            # 3. Parse the identified table
            headers = []
            header_elements = free_tier_table.find_all('th')
            if header_elements:
                headers = [th.text.strip().lower().replace('\n', ' ').strip() for th in header_elements]
                print(f"Table Headers: {headers}")
            else: # Sometimes tables might not use <th> for headers in simple structures
                first_row_cells = free_tier_table.find('tr').find_all('td') if free_tier_table.find('tr') else []
                if first_row_cells and len(first_row_cells) > 1: # A heuristic
                    headers = [cell.text.strip().lower().replace('\n', ' ').strip() for cell in first_row_cells]
                    print(f"Inferred Table Headers from first row: {headers}")


            if not headers:
                print("Could not determine table headers for the Free tier table.")
            else:
                tbody = free_tier_table.find('tbody')
                if not tbody: # If no tbody, assume rows are directly under table or in tr tags
                    data_rows = free_tier_table.find_all('tr')
                    if data_rows and header_elements: # If headers were th, skip the first row if it's the header row
                         data_rows = data_rows[1:]
                    elif data_rows and not header_elements and first_row_cells: # if headers were inferred from first td row
                         data_rows = data_rows[1:]

                else:
                    data_rows = tbody.find_all('tr')

                for row_idx, row in enumerate(data_rows):
                    cols = row.find_all(['td', 'th']) # Allow th in body for some table structures
                    if not cols:
                        continue

                    row_data = {}
                    model_name = "N/A"

                    # Extract model name (usually the first column)
                    if len(cols) > 0:
                         model_name = cols[0].text.strip()
                         row_data['Model'] = model_name
                    
                    # Map other columns based on headers
                    # This requires knowing the exact headers on the page or making educated guesses.
                    # Based on manual check of the page, the free tier table has:
                    # "Model", "Requests per minute (RPM)", "Requests per day (RPD)"
                    # "Gemini 1.5 Flash" also has "Tokens per minute (TPM)"

                    # RPM, RPD, TPM are common. Let's try to map them.
                    rpm, rpd, tpm = "N/A", "N/A", "N/A"

                    for i, header_text in enumerate(headers):
                        if i < len(cols): # Make sure column index is valid
                            cell_text = cols[i].text.strip()
                            if "model" in header_text : # Already handled model_name generally
                                if 'Model' not in row_data: row_data['Model'] = cell_text # If first col wasn't model.
                            elif "requests per minute" in header_text or header_text == "rpm":
                                rpm = cell_text
                            elif "requests per day" in header_text or header_text == "rpd":
                                rpd = cell_text
                            elif "tokens per minute" in header_text or header_text == "tpm":
                                tpm = cell_text
                    
                    row_data['RPM'] = rpm
                    row_data['RPD'] = rpd
                    row_data['TPM'] = tpm
                    
                    if model_name != "N/A" and model_name.lower() != "model": # Avoid adding header row as data
                        free_tier_limits_data.append(row_data)
                
                if free_tier_limits_data:
                    print(f"\nSuccessfully extracted {len(free_tier_limits_data)} entries from the Free tier table.")
                else:
                    print("\nNo data extracted from the Free tier table. Check row parsing logic or if table was empty.")

    else:
        print("Could not find the 'Free tier' anchor (id='free-tier') on the page.")
else:
    print("Page could not be fetched or parsed.")

# --- Create and display DataFrame ---
if free_tier_limits_data:
    print("\nCreating DataFrame for Free Tier Rate Limits...")
    df = pd.DataFrame(free_tier_limits_data)
    
    # Define a preferred column order
    column_order = ['Model', 'RPM', 'TPM', 'RPD']
    # Filter to only include columns that actually exist in the DataFrame
    df_display_columns = [col for col in column_order if col in df.columns]
    df_display = df[df_display_columns]
    
    print("\nFree Tier Rate Limits:")
    print(df_display.to_string())
else:
    print("\nNo data extracted for Free Tier Rate Limits to display in DataFrame.")