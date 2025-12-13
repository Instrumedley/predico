"""
Script to scrape stadium data from Wikipedia 2026 FIFA World Cup venues page.
Prints the data for review and saves to database.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set default environment variables if not set (for local development)
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://predico_user:predico_password@localhost:5432/predico_db'
if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'dev-secret-key-for-script'

import requests
from bs4 import BeautifulSoup
import re
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models.stadium import Stadium


def scrape_stadiums():
    """Scrape stadium data from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup#Venues"
    
    print(f"Fetching data from: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the venues table - it's usually in a section with id="Venues"
    # Look for the table with stadium information
    venues_section = soup.find('span', {'id': 'Venues'})
    
    if not venues_section:
        # Try alternative approach - look for table with stadium headers
        print("Could not find Venues section, searching for tables...")
        tables = soup.find_all('table', class_='wikitable')
        stadium_table = None
        for table in tables:
            headers = table.find_all('th')
            header_texts = [h.get_text(strip=True).lower() for h in headers]
            if any('stadium' in h or 'venue' in h or 'city' in h for h in header_texts):
                stadium_table = table
                break
    else:
        # Find the table after the Venues section
        parent = venues_section.find_parent()
        stadium_table = parent.find_next('table', class_='wikitable')
    
    if not stadium_table:
        print("ERROR: Could not find stadium table on the page")
        return []
    
    stadiums = []
    rows = stadium_table.find_all('tr')
    
    # First, identify column order by checking header row
    header_row = rows[0] if rows else None
    city_idx = 0
    stadium_idx = 1
    capacity_idx = 2
    
    if header_row:
        headers = header_row.find_all(['th', 'td'])
        header_texts = [h.get_text(strip=True).lower() for h in headers]
        
        # Find indices for each column - reset to None first
        city_idx = None
        stadium_idx = None
        capacity_idx = None
        
        # Match headers more specifically - check for exact matches first
        for i, header_text in enumerate(header_texts):
            header_lower = header_text.lower().strip()
            # Check capacity first (more specific)
            if 'capacity' in header_lower and capacity_idx is None:
                capacity_idx = i
            # Check stadium
            elif ('stadium' in header_lower or 'venue' in header_lower) and stadium_idx is None:
                stadium_idx = i
            # Check city last
            elif 'city' in header_lower and city_idx is None:
                city_idx = i
        
        # If we couldn't identify all columns, use defaults based on common Wikipedia table structure
        # Default order is typically: City, Stadium, Capacity
        if city_idx is None:
            city_idx = 0
        if stadium_idx is None:
            stadium_idx = 1
        if capacity_idx is None:
            capacity_idx = 2
    
    # Skip header row
    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        if len(cells) < 3:
            continue
        
        # Extract all cell texts
        all_texts = [cell.get_text(strip=True) for cell in cells]
        
        # Extract city (handle cases where city might have location in parentheses)
        city = all_texts[city_idx] if city_idx < len(all_texts) else ""
        city = re.sub(r'\[\d+\]', '', city).strip()
        # Extract main city name (before parentheses if present)
        # e.g., "Dallas(Arlington, Texas)" -> "Dallas" or "New York/New Jersey(East Rutherford, New Jersey)" -> "New York/New Jersey"
        city_match = re.match(r'^([^(]+)', city)
        if city_match:
            city = city_match.group(1).strip()
        
        # Extract stadium name
        stadium_name = all_texts[stadium_idx] if stadium_idx < len(all_texts) else ""
        stadium_name = re.sub(r'\[\d+\]', '', stadium_name).strip()
        # Remove special characters and parenthetical alternative names
        stadium_name = re.sub(r'[†‡]', '', stadium_name)
        # Keep main name, remove alternative in parentheses
        stadium_match = re.match(r'^([^(]+)', stadium_name)
        if stadium_match:
            stadium_name = stadium_match.group(1).strip()
        
        # Extract capacity
        capacity_text = all_texts[capacity_idx] if capacity_idx < len(all_texts) else ""
        capacity_text = re.sub(r'\[\d+\]', '', capacity_text)
        # Extract numbers (handle formats like "65,000" or "65,000[1]")
        capacity_match = re.search(r'([\d,]+)', capacity_text.replace(',', ''))
        capacity = int(capacity_match.group(1)) if capacity_match else None
        
        if stadium_name and city:
            stadiums.append({
                'name': stadium_name,
                'city': city,
                'capacity': capacity
            })
    
    return stadiums


async def save_stadiums_to_db(stadiums_data):
    """Save scraped stadium data to database."""
    async with AsyncSessionLocal() as session:
        saved_count = 0
        skipped_count = 0
        
        for stadium_data in stadiums_data:
            # Check if stadium already exists (by name and city)
            result = await session.execute(
                select(Stadium).where(
                    Stadium.name == stadium_data['name'],
                    Stadium.city == stadium_data['city']
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update capacity if it's different
                if existing.capacity != stadium_data['capacity']:
                    existing.capacity = stadium_data['capacity']
                    print(f"  Updated capacity for {stadium_data['name']} ({stadium_data['city']})")
                else:
                    print(f"  Skipped (already exists): {stadium_data['name']} ({stadium_data['city']})")
                    skipped_count += 1
                    continue
            else:
                # Create new stadium
                new_stadium = Stadium(
                    name=stadium_data['name'],
                    city=stadium_data['city'],
                    capacity=stadium_data['capacity']
                )
                session.add(new_stadium)
                saved_count += 1
        
        try:
            await session.commit()
            print(f"\n✓ Successfully saved {saved_count} new stadium(s)")
            if skipped_count > 0:
                print(f"  Skipped {skipped_count} existing stadium(s)")
        except Exception as e:
            await session.rollback()
            raise e


async def main():
    """Main function to scrape, display, and save stadium data."""
    print("=" * 80)
    print("Scraping 2026 FIFA World Cup Stadium Data")
    print("=" * 80)
    print()
    
    try:
        # Scrape stadium data
        stadiums = scrape_stadiums()
        
        if not stadiums:
            print("No stadiums found. Please check the Wikipedia page structure.")
            return
        
        # Display scraped data
        print(f"Found {len(stadiums)} stadiums:\n")
        print("Format: Stadium name - City - Capacity")
        print("-" * 80)
        
        for stadium in stadiums:
            capacity_str = str(stadium['capacity']) if stadium['capacity'] else 'N/A'
            print(f"{stadium['name']} - {stadium['city']} - {capacity_str}")
        
        print("-" * 80)
        print(f"\nTotal: {len(stadiums)} stadiums")
        
        # Ask for confirmation (in script, we'll just proceed)
        print("\n" + "=" * 80)
        print("Saving to database...")
        print("=" * 80)
        
        await save_stadiums_to_db(stadiums)
        
        print("\n✓ Done!")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

