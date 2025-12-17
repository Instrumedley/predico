"""
Script to scrape match times and timezones from Wikipedia and update the database.

This script:
1. Scrapes match times and timezones from the 2026 FIFA World Cup Wikipedia page
2. Matches them to existing games in the database
3. Updates the match_time and timezone fields

Usage:
    python -m scripts.scrape_match_times
"""
import asyncio
import os
import sys
import re
from pathlib import Path
from datetime import datetime, date, time
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set default environment variables if not set (for local development)
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://predico_user:predico_password@localhost:5432/predico_db'
if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'dev-secret-key-for-script'

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.db.database import AsyncSessionLocal
from app.db.models.team import Team
from app.db.models.game import Game
from app.db.models.group import Group

# Team name mappings from Wikipedia to database
# Maps Wikipedia team names to database team names
TEAM_NAME_MAPPINGS = {
    'South Africa': 'S. Africa',
    'S. Africa': 'S. Africa',
    'South Korea': 'South Korea',
    'United States': 'United States',
    'Saudi Arabia': 'Saudi Arabia',
    'Cape Verde': 'Cape Verde',
    'Ivory Coast': 'Ivory Coast',
    'Côte d\'Ivoire': 'Ivory Coast',
    'Curaçao': 'Curaçao',
    'New Zealand': 'New Zealand',
    'DR Congo': 'DR Congo',
    'Republic of Ireland': 'Ireland',
    'Ireland': 'Ireland',
    'Czech Republic': 'Czech Republic',
    'North Macedonia': 'North Macedonia',
    'Bosnia and Herzegovina': 'Bosnia and Herzegovina',
    'Northern Ireland': 'Northern Ireland',
    'Wales': 'Wales',
    'Italy': 'Italy',
    'Ukraine': 'Ukraine',
    'Poland': 'Poland',
    'Albania': 'Albania',
    'Sweden': 'Sweden',
    'Turkey': 'Turkey',
    'Slovakia': 'Slovakia',
    'Kosovo': 'Kosovo',
    'Romania': 'Romania',
    'Denmark': 'Denmark',
    'Iraq': 'Iraq',
    'Bolivia': 'Bolivia',
    'Suriname': 'Suriname',
}

# Manual match time data as fallback (based on Wikipedia content)
# Format: (home_team, away_team, date) -> (time, timezone)
# Note: Dates here are from Wikipedia. The script will match these to database records
# by team names and dates, so if database dates differ, matches may not be found.
MANUAL_MATCH_TIMES = {
    # Group A - Wikipedia shows June 11, June 18, June 24
    ('Mexico', 'S. Africa', date(2026, 6, 11)): (time(13, 0), 'UTC-6'),
    ('South Korea', 'Ireland', date(2026, 6, 11)): (time(20, 0), 'UTC-6'),
    ('S. Africa', 'Ireland', date(2026, 6, 18)): (time(12, 0), 'UTC-4'),
    ('Mexico', 'South Korea', date(2026, 6, 18)): (time(19, 0), 'UTC-6'),
    ('Ireland', 'Mexico', date(2026, 6, 24)): (time(19, 0), 'UTC-6'),
    ('S. Africa', 'South Korea', date(2026, 6, 24)): (time(19, 0), 'UTC-6'),
    # Also add dates that might be in database (June 19, June 28)
    ('S. Africa', 'Ireland', date(2026, 6, 19)): (time(12, 0), 'UTC-4'),
    ('Mexico', 'South Korea', date(2026, 6, 19)): (time(19, 0), 'UTC-6'),
    ('Ireland', 'Mexico', date(2026, 6, 28)): (time(19, 0), 'UTC-6'),
    ('S. Africa', 'South Korea', date(2026, 6, 28)): (time(19, 0), 'UTC-6'),
    
    # Group B
    ('Canada', 'Italy', date(2026, 6, 12)): (time(15, 0), 'UTC-4'),
    ('Qatar', 'Switzerland', date(2026, 6, 13)): (time(12, 0), 'UTC-7'),
    ('Qatar', 'Switzerland', date(2026, 6, 12)): (time(12, 0), 'UTC-7'),  # Alternative date
    ('Italy', 'Switzerland', date(2026, 6, 18)): (time(12, 0), 'UTC-7'),
    ('Italy', 'Switzerland', date(2026, 6, 20)): (time(12, 0), 'UTC-7'),
    ('Canada', 'Qatar', date(2026, 6, 18)): (time(15, 0), 'UTC-7'),
    ('Canada', 'Qatar', date(2026, 6, 20)): (time(15, 0), 'UTC-7'),
    ('Switzerland', 'Canada', date(2026, 6, 24)): (time(12, 0), 'UTC-7'),
    ('Switzerland', 'Canada', date(2026, 6, 29)): (time(12, 0), 'UTC-7'),
    ('Italy', 'Qatar', date(2026, 6, 24)): (time(12, 0), 'UTC-7'),
    ('Italy', 'Qatar', date(2026, 6, 29)): (time(12, 0), 'UTC-7'),
    
    # Group C
    ('Brazil', 'Morocco', date(2026, 6, 13)): (time(18, 0), 'UTC-4'),
    ('Brazil', 'Morocco', date(2026, 6, 12)): (time(18, 0), 'UTC-4'),
    ('Haiti', 'Scotland', date(2026, 6, 13)): (time(21, 0), 'UTC-4'),
    ('Haiti', 'Scotland', date(2026, 6, 12)): (time(21, 0), 'UTC-4'),
    ('Morocco', 'Scotland', date(2026, 6, 19)): (time(18, 0), 'UTC-4'),
    ('Morocco', 'Scotland', date(2026, 6, 20)): (time(18, 0), 'UTC-4'),
    ('Brazil', 'Haiti', date(2026, 6, 19)): (time(21, 0), 'UTC-4'),
    ('Brazil', 'Haiti', date(2026, 6, 20)): (time(21, 0), 'UTC-4'),
    ('Scotland', 'Brazil', date(2026, 6, 24)): (time(18, 0), 'UTC-4'),
    ('Scotland', 'Brazil', date(2026, 6, 29)): (time(18, 0), 'UTC-4'),
    ('Morocco', 'Haiti', date(2026, 6, 24)): (time(18, 0), 'UTC-4'),
    ('Morocco', 'Haiti', date(2026, 6, 29)): (time(18, 0), 'UTC-4'),
    
    # Group D
    ('United States', 'Paraguay', date(2026, 6, 12)): (time(18, 0), 'UTC-7'),
    ('Australia', 'Romania', date(2026, 6, 13)): (time(21, 0), 'UTC-7'),
    ('Australia', 'Romania', date(2026, 6, 12)): (time(21, 0), 'UTC-7'),
    ('Paraguay', 'Romania', date(2026, 6, 19)): (time(12, 0), 'UTC-7'),
    ('Paraguay', 'Romania', date(2026, 6, 21)): (time(12, 0), 'UTC-7'),
    ('United States', 'Australia', date(2026, 6, 19)): (time(12, 0), 'UTC-7'),
    ('United States', 'Australia', date(2026, 6, 21)): (time(12, 0), 'UTC-7'),
    ('Romania', 'United States', date(2026, 6, 25)): (time(19, 0), 'UTC-7'),
    ('Romania', 'United States', date(2026, 6, 30)): (time(19, 0), 'UTC-7'),
    ('Paraguay', 'Australia', date(2026, 6, 25)): (time(19, 0), 'UTC-7'),
    ('Paraguay', 'Australia', date(2026, 6, 30)): (time(19, 0), 'UTC-7'),
    
    # Group E
    ('Germany', 'Curaçao', date(2026, 6, 14)): (time(12, 0), 'UTC-5'),
    ('Germany', 'Curaçao', date(2026, 6, 13)): (time(12, 0), 'UTC-5'),
    ('Ivory Coast', 'Ecuador', date(2026, 6, 14)): (time(19, 0), 'UTC-4'),
    ('Ivory Coast', 'Ecuador', date(2026, 6, 13)): (time(19, 0), 'UTC-4'),
    ('Curaçao', 'Ecuador', date(2026, 6, 20)): (time(19, 0), 'UTC-5'),
    ('Curaçao', 'Ecuador', date(2026, 6, 21)): (time(19, 0), 'UTC-5'),
    ('Germany', 'Ivory Coast', date(2026, 6, 20)): (time(16, 0), 'UTC-4'),
    ('Germany', 'Ivory Coast', date(2026, 6, 21)): (time(16, 0), 'UTC-4'),
    ('Ecuador', 'Germany', date(2026, 6, 25)): (time(16, 0), 'UTC-4'),
    ('Ecuador', 'Germany', date(2026, 6, 30)): (time(16, 0), 'UTC-4'),
    ('Curaçao', 'Ivory Coast', date(2026, 6, 25)): (time(16, 0), 'UTC-4'),
    ('Curaçao', 'Ivory Coast', date(2026, 6, 30)): (time(16, 0), 'UTC-4'),
    
    # Group F
    ('Netherlands', 'Japan', date(2026, 6, 14)): (time(15, 0), 'UTC-5'),
    ('Netherlands', 'Japan', date(2026, 6, 13)): (time(15, 0), 'UTC-5'),
    ('Sweden', 'Tunisia', date(2026, 6, 14)): (time(20, 0), 'UTC-6'),
    ('Sweden', 'Tunisia', date(2026, 6, 13)): (time(20, 0), 'UTC-6'),
    ('Japan', 'Tunisia', date(2026, 6, 20)): (time(22, 0), 'UTC-6'),
    ('Japan', 'Tunisia', date(2026, 6, 22)): (time(22, 0), 'UTC-6'),
    ('Netherlands', 'Sweden', date(2026, 6, 20)): (time(12, 0), 'UTC-5'),
    ('Netherlands', 'Sweden', date(2026, 6, 22)): (time(12, 0), 'UTC-5'),
    ('Tunisia', 'Netherlands', date(2026, 6, 25)): (time(18, 0), 'UTC-5'),
    ('Tunisia', 'Netherlands', date(2026, 7, 1)): (time(18, 0), 'UTC-5'),
    ('Japan', 'Sweden', date(2026, 6, 25)): (time(18, 0), 'UTC-5'),
    ('Japan', 'Sweden', date(2026, 7, 1)): (time(18, 0), 'UTC-5'),
    
    # Group G
    ('Belgium', 'Egypt', date(2026, 6, 15)): (time(12, 0), 'UTC-7'),
    ('Belgium', 'Egypt', date(2026, 6, 14)): (time(12, 0), 'UTC-7'),
    ('Iran', 'New Zealand', date(2026, 6, 15)): (time(18, 0), 'UTC-7'),
    ('Iran', 'New Zealand', date(2026, 6, 14)): (time(18, 0), 'UTC-7'),
    ('Egypt', 'New Zealand', date(2026, 6, 21)): (time(18, 0), 'UTC-7'),
    ('Egypt', 'New Zealand', date(2026, 6, 22)): (time(18, 0), 'UTC-7'),
    ('Belgium', 'Iran', date(2026, 6, 21)): (time(12, 0), 'UTC-7'),
    ('Belgium', 'Iran', date(2026, 6, 22)): (time(12, 0), 'UTC-7'),
    ('New Zealand', 'Belgium', date(2026, 6, 26)): (time(20, 0), 'UTC-7'),
    ('New Zealand', 'Belgium', date(2026, 7, 1)): (time(20, 0), 'UTC-7'),
    ('Egypt', 'Iran', date(2026, 6, 26)): (time(20, 0), 'UTC-7'),
    ('Egypt', 'Iran', date(2026, 7, 1)): (time(20, 0), 'UTC-7'),
    
    # Group H
    ('Spain', 'Cape Verde', date(2026, 6, 15)): (time(12, 0), 'UTC-4'),
    ('Spain', 'Cape Verde', date(2026, 6, 14)): (time(12, 0), 'UTC-4'),
    ('Saudi Arabia', 'Uruguay', date(2026, 6, 15)): (time(18, 0), 'UTC-4'),
    ('Saudi Arabia', 'Uruguay', date(2026, 6, 14)): (time(18, 0), 'UTC-4'),
    ('Cape Verde', 'Uruguay', date(2026, 6, 21)): (time(18, 0), 'UTC-4'),
    ('Cape Verde', 'Uruguay', date(2026, 6, 23)): (time(18, 0), 'UTC-4'),
    ('Spain', 'Saudi Arabia', date(2026, 6, 21)): (time(12, 0), 'UTC-4'),
    ('Spain', 'Saudi Arabia', date(2026, 6, 23)): (time(12, 0), 'UTC-4'),
    ('Uruguay', 'Spain', date(2026, 6, 26)): (time(18, 0), 'UTC-6'),
    ('Uruguay', 'Spain', date(2026, 7, 1)): (time(18, 0), 'UTC-6'),
    ('Cape Verde', 'Saudi Arabia', date(2026, 6, 26)): (time(19, 0), 'UTC-5'),
    ('Cape Verde', 'Saudi Arabia', date(2026, 7, 1)): (time(19, 0), 'UTC-5'),
    
    # Group I
    ('France', 'Senegal', date(2026, 6, 16)): (time(15, 0), 'UTC-4'),
    ('France', 'Senegal', date(2026, 6, 15)): (time(15, 0), 'UTC-4'),
    ('Iraq', 'Norway', date(2026, 6, 16)): (time(18, 0), 'UTC-4'),
    ('Iraq', 'Norway', date(2026, 6, 15)): (time(18, 0), 'UTC-4'),
    ('Senegal', 'Norway', date(2026, 6, 22)): (time(20, 0), 'UTC-4'),
    ('Senegal', 'Norway', date(2026, 6, 23)): (time(20, 0), 'UTC-4'),
    ('France', 'Iraq', date(2026, 6, 22)): (time(17, 0), 'UTC-4'),
    ('France', 'Iraq', date(2026, 6, 23)): (time(17, 0), 'UTC-4'),
    ('Norway', 'France', date(2026, 6, 26)): (time(15, 0), 'UTC-4'),
    ('Norway', 'France', date(2026, 7, 1)): (time(15, 0), 'UTC-4'),
    ('Senegal', 'Iraq', date(2026, 6, 26)): (time(15, 0), 'UTC-4'),
    ('Senegal', 'Iraq', date(2026, 7, 1)): (time(15, 0), 'UTC-4'),
    
    # Group J
    ('Argentina', 'Algeria', date(2026, 6, 16)): (time(20, 0), 'UTC-5'),
    ('Argentina', 'Algeria', date(2026, 6, 15)): (time(20, 0), 'UTC-5'),
    ('Austria', 'Jordan', date(2026, 6, 16)): (time(21, 0), 'UTC-7'),
    ('Austria', 'Jordan', date(2026, 6, 15)): (time(21, 0), 'UTC-7'),
    ('Algeria', 'Jordan', date(2026, 6, 22)): (time(20, 0), 'UTC-7'),
    ('Algeria', 'Jordan', date(2026, 6, 24)): (time(20, 0), 'UTC-7'),
    ('Argentina', 'Austria', date(2026, 6, 22)): (time(12, 0), 'UTC-5'),
    ('Argentina', 'Austria', date(2026, 6, 24)): (time(12, 0), 'UTC-5'),
    ('Jordan', 'Argentina', date(2026, 6, 27)): (time(21, 0), 'UTC-5'),
    ('Jordan', 'Argentina', date(2026, 7, 1)): (time(21, 0), 'UTC-5'),
    ('Algeria', 'Austria', date(2026, 6, 27)): (time(21, 0), 'UTC-5'),
    ('Algeria', 'Austria', date(2026, 7, 1)): (time(21, 0), 'UTC-5'),
    
    # Group K
    ('Portugal', 'DR Congo', date(2026, 6, 17)): (time(12, 0), 'UTC-5'),
    ('Portugal', 'DR Congo', date(2026, 6, 16)): (time(12, 0), 'UTC-5'),
    ('Uzbekistan', 'Colombia', date(2026, 6, 17)): (time(20, 0), 'UTC-6'),
    ('Uzbekistan', 'Colombia', date(2026, 6, 16)): (time(20, 0), 'UTC-6'),
    ('DR Congo', 'Colombia', date(2026, 6, 23)): (time(20, 0), 'UTC-6'),
    ('DR Congo', 'Colombia', date(2026, 6, 24)): (time(20, 0), 'UTC-6'),
    ('Portugal', 'Uzbekistan', date(2026, 6, 23)): (time(12, 0), 'UTC-5'),
    ('Portugal', 'Uzbekistan', date(2026, 6, 24)): (time(12, 0), 'UTC-5'),
    ('Colombia', 'Portugal', date(2026, 6, 27)): (time(19, 30), 'UTC-4'),
    ('Colombia', 'Portugal', date(2026, 7, 1)): (time(19, 30), 'UTC-4'),
    ('DR Congo', 'Uzbekistan', date(2026, 6, 27)): (time(19, 30), 'UTC-4'),
    ('DR Congo', 'Uzbekistan', date(2026, 7, 1)): (time(19, 30), 'UTC-4'),
    
    # Group L
    ('England', 'Croatia', date(2026, 6, 17)): (time(15, 0), 'UTC-5'),
    ('England', 'Croatia', date(2026, 6, 16)): (time(15, 0), 'UTC-5'),
    ('Ghana', 'Panama', date(2026, 6, 17)): (time(19, 0), 'UTC-4'),
    ('Ghana', 'Panama', date(2026, 6, 16)): (time(19, 0), 'UTC-4'),
    ('Croatia', 'Panama', date(2026, 6, 23)): (time(19, 0), 'UTC-4'),
    ('Croatia', 'Panama', date(2026, 6, 25)): (time(19, 0), 'UTC-4'),
    ('England', 'Ghana', date(2026, 6, 23)): (time(16, 0), 'UTC-4'),
    ('England', 'Ghana', date(2026, 6, 25)): (time(16, 0), 'UTC-4'),
    ('Panama', 'England', date(2026, 6, 27)): (time(17, 0), 'UTC-4'),
    ('Panama', 'England', date(2026, 7, 1)): (time(17, 0), 'UTC-4'),
    ('Croatia', 'Ghana', date(2026, 6, 27)): (time(17, 0), 'UTC-4'),
    ('Croatia', 'Ghana', date(2026, 7, 1)): (time(17, 0), 'UTC-4'),
}

# Normalize team names for matching
def normalize_team_name(name: str) -> str:
    """Normalize team name for matching."""
    # Remove extra whitespace
    name = name.strip()
    
    # Check direct mapping first
    if name in TEAM_NAME_MAPPINGS:
        return TEAM_NAME_MAPPINGS[name]
    
    # Handle common variations
    if 'South Africa' in name or name == 'S. Africa':
        return 'S. Africa'
    if 'Ivory Coast' in name or 'Côte d\'Ivoire' in name:
        return 'Ivory Coast'
    if name == 'Republic of Ireland' or name == 'Ireland':
        return 'Ireland'
    
    return name


def parse_time_and_timezone(time_str: str) -> Tuple[Optional[time], Optional[str]]:
    """
    Parse time string like "3:00 p.m. UTC−5" or "12:00 p.m. UTC−4" into time and timezone.
    
    Returns: (time_object, timezone_string)
    """
    if not time_str:
        return None, None
    
    # Pattern to match: "3:00 p.m. UTC−5" or "12:00 p.m. UTC−4" or "1:00 p.m. UTC−6"
    # Also handle "12:00 p.m. UTC−7" or "8:00 p.m. UTC−6"
    pattern = r'(\d{1,2}):(\d{2})\s*(a\.m\.|p\.m\.)\s*UTC([+-]?\d+)'
    match = re.search(pattern, time_str, re.IGNORECASE)
    
    if not match:
        # Try alternative format without UTC prefix
        pattern2 = r'(\d{1,2}):(\d{2})\s*(a\.m\.|p\.m\.)'
        match2 = re.search(pattern2, time_str, re.IGNORECASE)
        if match2:
            hour = int(match2.group(1))
            minute = int(match2.group(2))
            period = match2.group(3).lower()
            
            # Convert to 24-hour format
            if period == 'p.m.' and hour != 12:
                hour += 12
            elif period == 'a.m.' and hour == 12:
                hour = 0
            
            # Try to find timezone in the string
            tz_match = re.search(r'UTC([+-]?\d+)', time_str, re.IGNORECASE)
            timezone = f"UTC{tz_match.group(1)}" if tz_match else None
            
            return time(hour, minute), timezone
        return None, None
    
    hour = int(match.group(1))
    minute = int(match.group(2))
    period = match.group(3).lower()
    timezone_offset = match.group(4)
    
    # Convert to 24-hour format
    if period == 'p.m.' and hour != 12:
        hour += 12
    elif period == 'a.m.' and hour == 12:
        hour = 0
    
    timezone = f"UTC{timezone_offset}"
    
    return time(hour, minute), timezone


def scrape_wikipedia_match_times() -> Dict[Tuple[str, str, date], Tuple[time, str]]:
    """
    Scrape match times and timezones from Wikipedia.
    
    Returns: Dictionary mapping (home_team, away_team, match_date) -> (match_time, timezone)
    """
    url = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup#Group_stage"
    
    print("Fetching Wikipedia page...")
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    match_data = {}
    
    # The Wikipedia page structure: Each match has a format like:
    # "June 17, 2026 (2026-06-17) 3:00 p.m. UTC−5"
    # Followed by team names in links
    
    # Find all match date-time entries
    # Look for patterns like: "June 17, 2026 (2026-06-17) 3:00 p.m. UTC−5"
    date_time_pattern = r'(June|July)\s+(\d{1,2}),\s+2026\s+\(2026-\d{2}-\d{2}\)\s+(\d{1,2}):(\d{2})\s*(a\.m\.|p\.m\.)\s*UTC([−+-]?\d+)'
    
    # Parse the HTML to find match entries
    # Each match entry is typically in a structure like:
    # <p>June 17, 2026 (2026-06-17) 3:00 p.m. UTC−5</p>
    # <table>...with team links...</table>
    
    # Find all paragraphs or divs containing date-time patterns
    all_text = str(soup)
    matches = list(re.finditer(date_time_pattern, all_text, re.IGNORECASE))
    
    print(f"Found {len(matches)} date-time patterns in the page")
    
    for match_obj in matches:
        month = match_obj.group(1)
        day = int(match_obj.group(2))
        hour_str = match_obj.group(3)
        minute_str = match_obj.group(4)
        period = match_obj.group(5).lower()
        tz_offset = match_obj.group(6)
        
        # Handle different minus signs (regular hyphen, en-dash, em-dash)
        tz_offset = tz_offset.replace('−', '-').replace('—', '-')
        
        month_num = 6 if month == 'June' else 7
        match_date = date(2026, month_num, day)
        
        hour = int(hour_str)
        minute = int(minute_str)
        if period == 'p.m.' and hour != 12:
            hour += 12
        elif period == 'a.m.' and hour == 12:
            hour = 0
        
        match_time = time(hour, minute)
        timezone = f"UTC{tz_offset}"
        
        # Find the HTML element containing this match
        # Get the position in the original HTML
        match_start = match_obj.start()
        
        # Find the nearest table or div containing team information
        # Look for team links near this position - search in a larger context
        context_start = max(0, match_start - 1000)
        context_end = min(len(all_text), match_start + 3000)
        context_html = all_text[context_start:context_end]
        
        # Parse the context to find teams
        context_soup = BeautifulSoup(context_html, 'html.parser')
        
        # Find team links - they typically link to national team pages
        # Try multiple patterns for team links
        team_links = []
        
        # Pattern 1: Direct links to national team pages
        links1 = context_soup.find_all('a', href=re.compile(r'/wiki/.*national.*football.*team|/wiki/.*national.*soccer.*team'))
        if len(links1) >= 2:
            team_links = links1[:2]
        
        # Pattern 2: Links in table cells (common in Wikipedia match tables)
        if len(team_links) < 2:
            tables = context_soup.find_all('table')
            for table in tables:
                # Look for rows with team information
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    for cell in cells:
                        links = cell.find_all('a', href=re.compile(r'/wiki/.*national.*team|/wiki/.*men.*national'))
                        if len(links) >= 2:
                            team_links = links[:2]
                            break
                    if len(team_links) >= 2:
                        break
                if len(team_links) >= 2:
                    break
        
        # Pattern 3: Look for team names in bold or strong tags near the date
        if len(team_links) < 2:
            # Find the element containing the date-time
            date_elements = context_soup.find_all(string=re.compile(r'June|July.*2026.*UTC'))
            for date_elem in date_elements:
                parent = date_elem.parent
                if parent:
                    # Look for team links in the same parent or nearby
                    nearby_links = parent.find_all('a', href=re.compile(r'/wiki/.*team'))
                    if len(nearby_links) >= 2:
                        team_links = nearby_links[:2]
                        break
        
        if len(team_links) >= 2:
            # Get team names from links
            home_team_raw = team_links[0].get_text().strip()
            away_team_raw = team_links[1].get_text().strip()
            
            # Map Wikipedia team names to database team names
            home_team = normalize_team_name(home_team_raw)
            away_team = normalize_team_name(away_team_raw)
            
            # Store with both possible orders
            key1 = (home_team, away_team, match_date)
            key2 = (away_team, home_team, match_date)
            
            # Store both orders to handle different listing orders
            if key1 not in match_data and key2 not in match_data:
                match_data[key1] = (match_time, timezone)
                print(f"  Found: {home_team} vs {away_team} on {match_date} at {match_time} {timezone}")
    
    print(f"\nTotal matches found from scraping: {len(match_data)}")
    
    # Merge with manual data (manual data takes precedence for exact matches)
    for key, value in MANUAL_MATCH_TIMES.items():
        home, away, match_date = key
        normalized_key = (normalize_team_name(home), normalize_team_name(away), match_date)
        if normalized_key not in match_data:
            match_data[normalized_key] = value
            print(f"  Added from manual data: {normalized_key[0]} vs {normalized_key[1]} on {match_date}")
    
    print(f"\nTotal matches (scraped + manual): {len(match_data)}")
    return match_data


async def update_game_times(session, match_data: Dict[Tuple[str, str, date], Tuple[time, str]]):
    """
    Update games in the database with match times and timezones.
    
    Args:
        session: Database session
        match_data: Dictionary mapping (home_team, away_team, match_date) -> (match_time, timezone)
    """
    print("\nUpdating games with match times and timezones...")
    
    # Get all teams
    teams_result = await session.execute(select(Team))
    teams = {team.name: team for team in teams_result.scalars().all()}
    
    updated_count = 0
    not_found_count = 0
    
    # Get all games
    games_result = await session.execute(
        select(Game)
        .options(selectinload(Game.home_team), selectinload(Game.away_team))
    )
    games = games_result.scalars().all()
    
    for game in games:
        if not game.match_date:
            print(f"  Skipped (no match_date): {game.home_team.name} vs {game.away_team.name}")
            continue
            
        home_team_name = game.home_team.name
        away_team_name = game.away_team.name
        
        # Normalize team names
        home_normalized = normalize_team_name(home_team_name)
        away_normalized = normalize_team_name(away_team_name)
        
        # Try to find matching data
        # Try both (home, away) and (away, home) since Wikipedia might list them differently
        key1 = (home_normalized, away_normalized, game.match_date)
        key2 = (away_normalized, home_normalized, game.match_date)
        
        match_info = match_data.get(key1) or match_data.get(key2)
        
        if match_info:
            match_time, timezone = match_info
            game.match_time = match_time
            game.timezone = timezone
            updated_count += 1
            print(f"  ✓ Updated: {home_team_name} vs {away_team_name} ({game.match_date}) - {match_time} {timezone}")
        else:
            not_found_count += 1
            print(f"  ✗ Not found: {home_team_name} vs {away_team_name} ({game.match_date})")
    
    await session.commit()
    print(f"\n" + "=" * 80)
    print(f"Summary:")
    print(f"  ✓ Updated: {updated_count} games")
    print(f"  ✗ Not found: {not_found_count} games")
    print("=" * 80)


async def main():
    """Main function to scrape and update match times."""
    print("=" * 80)
    print("Scraping Match Times and Timezones from Wikipedia")
    print("=" * 80)
    print()
    
    try:
        # Scrape Wikipedia
        match_data = scrape_wikipedia_match_times()
        
        if not match_data:
            print("WARNING: No match data found. The Wikipedia page structure may have changed.")
            return
        
        # Update database
        async with AsyncSessionLocal() as session:
            await update_game_times(session, match_data)
        
        print("=" * 80)
        print("✓ Match times update complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
