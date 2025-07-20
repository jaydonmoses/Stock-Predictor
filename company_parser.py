import csv
from urllib.parse import urlparse

# This csv_file_path variable is not used when load_companies is called from app.py
# as app.py will pass the path directly.
# csv_file_path = 'companies.csv'

def clean_domain(url):
    """
    Cleans a URL to return only the netloc (e.g., 'example.com').
    If urlparse fails, it returns the original url as a fallback.
    """
    try:
        if not url:
            return ''
        # Prepend scheme if missing, for urlparse to work correctly
        if "://" not in url:
            url = "http://" + url
        parsed_url = urlparse(url)
        clean_netloc = parsed_url.netloc
        # Remove 'www.' if present
        if clean_netloc.startswith('www.'):
            clean_netloc = clean_netloc[4:]
        return clean_netloc or url
    except Exception as e:
        print(f"Error cleaning URL '{url}': {e}")
        return url

def load_companies(csv_file_path):
    """Load companies from a CSV file and return a list of dictionaries."""
    companies = []
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Clean the website URL as it's loaded
                website = row.get('Website', '').strip()
                row['website'] = clean_domain(website) if website else ''
                
                # Ensure 'Symbol' and 'Company Name' are correctly mapped
                row['ticker'] = row.get('Symbol', '').strip().upper()
                row['name'] = row.get('Company Name', '').strip()

                companies.append(row)
    except FileNotFoundError:
        print(f"Error: companies.csv not found at {csv_file_path}. Please ensure it's in the correct location.")
    except Exception as e:
        print(f"Error loading companies data from CSV: {e}")
    return companies

def get_company_by_ticker(companies, ticker):
    """Find a company by its ticker symbol."""
    for company in companies:
        if company.get('ticker', '').lower() == ticker.lower():
            return company
    return None

def get_company_by_name(companies, name):
    """Find a company by its name."""
    for company in companies:
        # Check both 'name' (cleaned) and 'company name' (original CSV)
        if company.get('name', '').lower() == name.lower() or \
           company.get('Company Name', '').lower() == name.lower():
            return company
    return None

def get_company_website(companies, ticker):
    """Get the website of a company by its ticker symbol."""
    company = get_company_by_ticker(companies, ticker)
    if company:
        # Return the already cleaned 'website' field
        return company.get('website', 'Website not available')
    return 'Company not found'

def get_company_description(companies, ticker):
    """Get the description of a company by its ticker symbol."""
    company = get_company_by_ticker(companies, ticker)
    if company:
        return company.get('Description', 'Description not available') # Use original CSV header for description
    return 'Company not found'

def get_company_ceo(companies, ticker):
    """Get the CEO of a company by its ticker symbol."""
    company = get_company_by_ticker(companies, ticker)
    if company:
        return company.get('CEO', 'CEO not available') # Use original CSV header for CEO
    return 'Company not found'

def get_company_tag_1 (companies, ticker):
    """Get the first tag of a company by its ticker symbol."""
    company = get_company_by_ticker(companies, ticker)
    if company:
        return company.get('tag_1', 'Tag 1 not available')
    return 'Company not found'

def return_company_info(companies, identifier):
    """
    Return a dictionary with company information by ticker symbol or company name.
    Prioritizes ticker lookup.
    """
    company = get_company_by_ticker(companies, identifier)
    if not company:
        company = get_company_by_name(companies, identifier) # Try by name if ticker fails

    if company:
        return {
            'name': company.get('name', company.get('Company Name', 'N/A')),
            'ticker': company.get('ticker', company.get('Symbol', 'N/A')),
            'description': company.get('Description', 'Description not available'),
            'ceo': company.get('CEO', 'CEO not available'),
            'website': company.get('website', 'Website not available'), # Use the already cleaned 'website'
            'tag_1': company.get('tag_1', 'Tag 1 not available'),
            'logo_url': f"https://logo.clearbit.com/{company.get('website', '')}" if company.get('website') else '/static/default-logo.png'
        }
    return None

def sort_by_market_cap(companies):
    """Sort companies by market capitalization."""
    # Ensure 'market_cap' is treated as a float, default to 0 if missing
    return sorted(companies, key=lambda x: float(x.get('market_cap', 0) or 0), reverse=True)
