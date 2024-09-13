from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import date
import datetime
from datetime import datetime
from datetime import timedelta
import pytz
from pytz import timezone
import os
import numpy as np
import pandas as pd
import regex as re
import requests
import selenium
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

def get_modified_html(initial_html, updated_html):
    initial_soup = BeautifulSoup(initial_html, "html.parser")
    updated_soup = BeautifulSoup(updated_html, "html.parser")
    modified_parts = []
    for initial_tag, updated_tag in zip(initial_soup.find_all(), updated_soup.find_all()):
        if str(initial_tag) != str(updated_tag):
            modified_parts.append(updated_tag)
    modified_html = '\n'.join(str(tag) for tag in modified_parts)
    return modified_html

def click_with_retry(driver, entry, selector, max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        try:
            see_all_button = entry.find_element(By.CSS_SELECTOR, selector)
            driver.execute_script("arguments[0].click();", see_all_button)
            return
        except selenium.common.exceptions.StaleElementReferenceException:
            attempts += 1
            time.sleep(1)

def name_processing(result):
    name_parts = ' '.join(result.split(' ')[:2])
    play = ' '.join(result.split(' ')[2:])
    first_initial = re.sub('[,.]', '', name_parts.split(' ')[0])[:1].capitalize() + '.'
    last_name = re.sub('[,.]', '', name_parts.split(' ')[1]).capitalize()
    name = first_initial + last_name
    play = name + ' ' + play
    return name, play

def extract_data(soup, rotowire_book):
    all_data = []
    player_blocks = soup.find_all("div", class_="h-full flex w-full")
    for block in player_blocks:
        player_name_tag = block.find("a")
        player_name = player_name_tag.text.strip() if player_name_tag else None
        if player_name:
          gradient_div = block.find("div", class_="w-6")
          if gradient_div:
              if "from-rose-500 to-rose-700" in str(gradient_div):
                  over_under = "u"  # 'under'
              else:
                  over_under = "o"  # 'over'
          if len(str(block.find("div", class_="text-sm sm:text-xs text-slate-600 sm:text-slate-500")).split(">")) < 2:
             continue
          prop_type = str(block.find("div", class_="text-sm sm:text-xs text-slate-600 sm:text-slate-500")).split(">")[1].split("<")[0]
          prop_num = str(block.find("div", class_="text-slate-700 tracking-tight")).split(">")[1].split("<")[0]
          if '.5' not in prop_num:
            if over_under == 'o':
              prop_num += '.5'
            elif over_under == 'u':
              prop_num = str(int(prop_num) - 1)
              prop_num += '.5'
          prop = f"{player_name} {over_under}{prop_num} {prop_type}"
          all_data.append({"Props": prop, "Expert": f"Rotowire {rotowire_book}", "Units": 1.5})
    return all_data[:2]

class Bets:
    date = date.Date()

    def site_scrape_chrome(self, url, is_action = False, is_rotowire = False, rotowire_more_less = None, rotowire_type = None):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        driver = webdriver.Chrome(options=chrome_options)
        tz_params = {'timezoneId': 'America/Los_Angeles'}
        driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
        driver.get(url)
        initial_html = driver.page_source
        time.sleep(3)
        if is_action: 
            modified_htmls = []
            entries = driver.find_elements(By.CSS_SELECTOR, '.css-1pfshtc.eyea0g80')
            for entry in entries:
                see_all_button = entry.find_element(By.CSS_SELECTOR, 'button[data-testid="expert-picks__see-all-picks"]')
                click_with_retry(driver, entry, 'button[data-testid="expert-picks__see-all-picks"]')
                time.sleep(3)
                updated_html = driver.page_source
                modified_html = get_modified_html(initial_html, updated_html)
                modified_htmls.append(modified_html)
            return modified_htmls
        elif is_rotowire:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'NFL')]"))
            ).click()
            if rotowire_type == "passing yards":
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Passing Yards')]/parent::button"))
                ).click()
                time.sleep(3)
            if rotowire_more_less == "more":
                button = driver.find_element(By.XPATH, '//button[@aria-label="Lean More"]')
                button.click()
            elif rotowire_more_less == "less":
                button = driver.find_element(By.XPATH, '//button[@aria-label="Lean Less"]')
                button.click()
            time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        driver.close()
        return soup

    def sharp_df(self, total_site_data):
        try:
            author = total_site_data.find('a', rel='author').get_text()

            consider_blocks = total_site_data.find_all('h2')
            results = []

            for block in consider_blocks:
                if 'Consider the' in block.text:
                    player_info = block.text.split('Consider the ')[1]
                    parts = player_info.split(' on ')
                    if len(parts) == 2:
                        action, player_stat = parts[0], parts[1]
                        over_under = 'o' if 'over' in action else 'u'
                        player_name, stat = player_stat.rsplit('’', 1)
                        player_name = ' '.join(player_name.split(' ')[:2])
                        stat = stat.split(' prop')[0].lstrip('’s ')
                        next_li = block.find_next('li')
                        if next_li:
                            value = re.search(r'\d+(\.\d+)?', next_li.text).group()
                            results.append(f"{player_name.strip()} {over_under}{value.strip()} {stat.strip()}")

            sharp_df = pd.DataFrame(columns=['Name', 'Expert', 'Play'])
            for result in results: 
                name, play = name_processing(result)
                new_row = pd.DataFrame([{'Name': name, 'Expert': author, 'Play': play, 'Units': 0.75}])
                sharp_df = pd.concat([sharp_df, new_row], ignore_index=True)
        
        except Exception as e:
            print(f"Sharp_df - Error occurred: {e}")
            traceback.print_exc()
            sharp_df = pd.DataFrame(columns=['Name', 'Expert', 'Play'])
        return sharp_df

    def covers_df(self, url, dates, week):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        covers_links = list({
            a_href["href"]
            for a_href in soup.find_all("a", href=True)
            if not "sign-up" in a_href["href"] and not "forum" in a_href["href"] and not "code" in a_href["href"] and not "promos" in a_href["href"]  and (
                f"week-{week}" in a_href["href"] or                
                any(re.search(rf"{month}-{day}-\d{{4}}", a_href["href"]) for month, day in dates)
            )
        })
        covers_df = pd.DataFrame(columns=['Name', 'Expert', 'Play'])
        for link in covers_links:
            time.sleep(3)
            total_site_data = self.site_scrape_chrome(url.split('/nfl')[0] + link)
            try:
                author = total_site_data.find('a', href=lambda href: href and "/writers/" in href).get_text()

                results = []
                for p_tag in total_site_data.find_all('p'):
                    if 'Prop' in p_tag.text:
                        prop_text = p_tag.text.strip()
                        if prop_text.startswith('Prop'):
                            prop_text = prop_text.split(':', 1)[1].split('(')[0].strip()
                        if 'Over' in prop_text or 'Under' in prop_text or 'anytime' in prop_text.lower():
                            results.append(prop_text)
                if not results:
                    prop_list_items = total_site_data.find_all('li')
                    for item in prop_list_items:
                        try:
                            link = item.find('a', href=True)
                            if link and 'sportsbookredirect?vertical=betting' in link['href']:
                                prop_text = (item.find('span') or item.find('strong')).text
                                results.append(prop_text)
                        except AttributeError:
                            continue
                if not results:
                    betting_card_header = total_site_data.find('h2', id='Full_betting_card')
                    if betting_card_header:
                        ul_tag = betting_card_header.find_next_sibling('ul')
                        if ul_tag:
                            list_items = ul_tag.find_all('li')
                            for li in list_items:
                                li_text = li.text.strip().split('(')[0].strip()
                                results.append(li_text)

                for result in results:
                    parts = result.split(' ')
                    if 'and' in parts:
                        continue
                    if '+' in parts:
                        over_index = parts.index('Over') if 'Over' in parts else len(parts)
                        under_index = parts.index('Under') if 'Under' in parts else len(parts)
                        plus_index = parts.index('+')
                        if plus_index < min(over_index, under_index):
                            continue
                            
                    name_parts = ' '.join(parts[:2])
                    play = ''
                    extra_info = ''

                    for i, part in enumerate(parts):
                        if part == "Over" or part == "Under":
                            if "longest" in parts[:i]:
                                longest_index = parts.index("longest")
                                extra_info = ' '.join(parts[longest_index:i])
                            play = ' '.join(parts[i:])
                            if extra_info:
                                play_parts = play.split(' ')
                                play = f"{play_parts[0]} {play_parts[1]} {extra_info} {' '.join(play_parts[2:])}"
                            break
                        elif part.endswith('+'):
                            number = int(part[:-1])
                            play = f"Over {number - 0.5} {' '.join(parts[i+1:])}"
                            break
                        elif "anytime touchdown" in result.lower() or 'anytime touchdown' in result.lower() or 'anytime TD' in result.lower() or 'scores a touchdown' in result.lower() or 'to score a touchdown' in result.lower():
                            play = "Over 0.5 Rush_TD+Rec_TD"
                            break
                    if play:
                        play = play.lower()
                        plays = play.split(' ')
                        plays[0] = 'o' if 'over' in plays[0] else 'u'
                        plays[0] = plays[0] + plays[1]
                        plays.pop(1)
                        play = ' '.join(plays)
                        name, _ = name_processing(result)
                        play = name + ' ' + play
                    else:
                        name, play = name_processing(result)
                    name = name.split(' ')[:2]
                    if 'longest' in play:
                        parts = play.split(' ')
                        for i, part in enumerate(parts):
                            if part.startswith('u') or part.startswith('o'):
                                play = ' '.join(parts[:1] + [parts[i]] + parts[1:i] + parts[i+1:])
                                break
                    if '(' in play:
                        play = play.split('(')[0].strip()
                    new_row = pd.DataFrame([{'Name': name, 'Expert': author, 'Play': play, 'Units': 0.75}])
                    covers_df = pd.concat([covers_df, new_row], ignore_index=True)

            except Exception as e:
                print(f"Covers_df - Error occurred: {e}")
                traceback.print_exc()
                covers_df = pd.DataFrame(columns=['Name', 'Expert', 'Play'])
        return covers_df

    def action_df(self, url):
        try:
            play_list, expert_list, odds_list, units_list, name_list = [], [], [], [], []
            site_data = self.site_scrape_chrome(url, is_action = True)
            for html in site_data:
                for picks in str(html).split('Player Props')[1].split('<div class="pick-card__header">')[1:]:
                    soup = BeautifulSoup(picks, 'html.parser')
                    play_elements = soup.select('.base-pick__name')
                    odds_elements = soup.select('.base-pick__secondary-text')
                    units_elements = soup.select('.base-pick__units')
                    expert_element = soup.select_one('.pick-card__expert-info > a')
                    if expert_element:
                        expert = expert_element['href'].split('/')[-1]
                    else:
                        expert = ''
                    for play_element, odds_element, units_element in zip(play_elements, odds_elements, units_elements):
                        play_text = play_element.text
                        
                        if re.match(r'[A-Z]\.[A-Za-z\-]+ [ou][\d]+\.[\d] [\w\s]+', play_text):
                            play_list.append(play_text)
                        elif re.match(r'[A-Z]\.[A-Za-z\-]+ \d+\+ [\w\s]+ Yes', play_text):
                            parts = play_text.split()
                            player_name = parts[0]
                            yardage = int(parts[1][:-1]) - 0.5
                            prop_type = ' '.join(parts[2:-1])
                            play_list.append(f"{player_name} o{yardage} {prop_type}")
                        elif re.match(r'[A-Z]\.[A-Za-z\-]+ Anytime TD Scorer Yes', play_text):
                            player_name = play_text.split()[0]
                            play_list.append(f"{player_name} o0.5 rush_td+rec_td")
                        else:
                            continue

                        expert_list.append(expert)
                        odds_list.append(odds_element.text if odds_element else '')
                        units_list.append(units_element.text.split('u')[0] if units_element else '')
                        name_list.append(play_text.split(' ')[0])
            data = {
                'Play': play_list,
                'Expert': expert_list,
                'Odds': odds_list,
                'Units': units_list,
                'Name': name_list
            }
            action_df = pd.DataFrame(data)

        except Exception as e:
            print(f"Action_df - Error occurred: {e}")
            traceback.print_exc()
            action_df = pd.DataFrame(columns=['Name', 'Expert', 'Play'])
        return action_df

    def rotowire_df(self, url, rotowire_book):
        try:
            soups = []
            scraping_functions = [
                lambda: self.site_scrape_chrome(url, is_rotowire=True),
                lambda: self.site_scrape_chrome(url, is_rotowire=True, rotowire_more_less="more"),
                lambda: self.site_scrape_chrome(url, is_rotowire=True, rotowire_more_less="less"),
            ]

            for i, scrape_func in enumerate(scraping_functions):
                try:
                    result = scrape_func()
                    soups.append(result)
                except Exception as e:
                    print(f"Scraping function {i+1} failed: {e}")

            data = [extract_data(soup, rotowire_book) for soup in soups]
            df = pd.DataFrame([item for sublist in data for item in sublist]).drop_duplicates()
            df['Odds'] = 100
            df['Props'] = df['Props'].str.lower()
            df['Props'] = df['Props'].str.replace(' Jr.', '')
            df['Props'] = df['Props'].str.replace(r'over\s*(\d+\.\d+)', r'o\1', regex=True)
            df['Props'] = df['Props'].str.replace(r'under\s*(\d+\.\d+)', r'u\1', regex=True)
            df['Props'] = df['Props'].str.replace(r'o\s+(\d+\.\d+)', r'o\1')
            df['Props'] = df['Props'].str.replace(r'u\s+(\d+\.\d+)', r'u\1')
            df['First Initial'] = df['Props'].str.split().str[:1].str.join(' ').str.replace('[,.]', '').str[:1].str.capitalize() + '.'
            df['Last Name'] = df['Props'].str.split().str[1:2].str.join(' ').str.replace('[,.]', '').str.capitalize()
            df['Name'] = df['First Initial'] + df['Last Name']
            df['Prop Num'] = df['Props'].str.split().str[2:3].str.join(' ')
            df['Prop Type'] = df['Props'].str.extract(r'[ou]\d+\.\d+\s+(.*)')
            df = df.dropna()
            df['Play'] = df['Name'] + ' ' + df['Prop Num'] + ' ' + df['Prop Type']
            df = df.drop_duplicates(subset=['Play', 'Expert'], keep='first').reset_index(drop=True)
            df =  df[['Play', 'Expert', 'Odds', 'Units', 'Name']]
            rotowire_df = df
        except Exception as e:
            print(f"rotowire_df - Error occurred: {e}")
            traceback.print_exc()
            rotowire_df = pd.DataFrame(columns=['Name', 'Expert', 'Play'])
        return rotowire_df
       