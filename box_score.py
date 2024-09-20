from bs4 import BeautifulSoup, Comment
import datetime
import helper_functions
import pandas as pd
import pytz
from pytz import timezone
import re
import requests
import time
from unidecode import unidecode

team_map = {
    'NOR': 'New Orleans Saints',
    'HOU': 'Houston Texans',
    'KAN': 'Kansas City Chiefs',
    'TEN': 'Tennessee Titans',
    'NYG': 'New York Giants',
    'PIT': 'Pittsburgh Steelers',
    'LAR': 'Los Angeles Rams',
    'DAL': 'Dallas Cowboys',
    'SFO': 'San Francisco 49ers',
    'ARI': 'Arizona Cardinals',
    'TAM': 'Tampa Bay Buccaneers',
    'CIN': 'Cincinnati Bengals',
    'LAC': 'Los Angeles Chargers',
    'WAS': 'Washington Commanders',
    'PHI': 'Philadelphia Eagles',
    'BAL': 'Baltimore Ravens',
    'CLE': 'Cleveland Browns',
    'NWE': 'New England Patriots',
    'MIA': 'Miami Dolphins',
    'MIN': 'Minnesota Vikings',
    'GNB': 'Green Bay Packers',
    'JAX': 'Jacksonville Jaguars',
    'IND': 'Indianapolis Colts',
    'DET': 'Detroit Lions',
    'CHI': 'Chicago Bears',
    'CAR': 'Carolina Panthers',
    'LVR': 'Las Vegas Raiders',
    'BUF': 'Buffalo Bills',
    'NYJ': 'New York Jets',
    'ATL': 'Atlanta Falcons',
    'SEA': 'Seattle Seahawks',
    'DEN': 'Denver Broncos'
}

def map_forecast(forecast):
    if forecast in ["Clear", "Mostly Sunny", "Clear Windy"]:
        return "Clear"
    elif forecast in ["Partly Cloudy", "Humid And Partly Cloudy", "Few Clouds"]:
        return "Partly Cloudy"
    elif forecast in ["Mostly Cloudy", "Humid And Mostly Cloudy", "Cloudy", "Definite Haze"]:
        return "Mostly Cloudy"
    elif forecast in ["Overcast", "Humid And Overcast", "Windy And Overcast"]:
        return "Overcast"
    elif forecast in ["Foggy", "Fog", "Patchy Fog"]:
        return "Foggy"
    elif forecast in ["Light Rain", "Rain", "Drizzle", "Possible Drizzle", "Rain And Windy", "Light Rain And Windy",
                    "Isolated Thunderstorms", "Chance Thunderstorms",  "Chance Rain", "Chance Rain Showers", "Slight Chance Thunderstorms", "Likely Rain", "Definite Rain", "Slight Chance Rain Showers", "Numerous Rain Showers", "Likely Rain Showers", "Numerous Thunderstorms", "Slight Chance Rain"]:
        return "Rain" 
    elif forecast in ["Snow", "Possible Flurries", "Light Snow", "Possible Light Snow", "Light Snow And Windy", "Heavy Snow"]:
        return "Snow"
    elif forecast in ["Humid"]:
        return "Humid"
    else:
        print(forecast)
        print('not found in forecast')
        return forecast



class BoxScore:

    def full_box_scores(self, week):
        import bets_scrape
        bets_scraper = bets_scrape.Bets()
        team_weather_data = {}
        url = f'https://www.nflweather.com/week/2024/week-{week}'
        weather_soup = bets_scraper.site_scrape_chrome(url)
        time.sleep(3)
        game_boxes = weather_soup.find_all('div', class_='game-box')
        for game_box in game_boxes:
            date_div = game_box.find('div', class_='fw-bold text-wrap')
            date = date_div.text.strip().split()[0]
            game_url_tag = game_box.select_one('div.info-game-box a.text-dark[href*="/games/"]')
            game_url = f"https://www.nflweather.com{game_url_tag['href']}" if game_url_tag else None
            time.sleep(3)
            game_soup = bets_scraper.site_scrape_chrome(game_url)
            temperature = game_soup.find('p', class_='weather-temperature').text.strip().split()[0]
            wind_tag = game_soup.find('span', class_='material-icons', text='air').parent
            wind = wind_tag.text.strip().split()[1]
            precipitation_tag = game_soup.find('span', class_='material-icons', text='water_drop').parent
            precipitation = precipitation_tag.text.strip().split()[-2]
            humidity = None
            for p_tag in game_soup.find_all('p', class_='weather-data'):
                if 'Humidity' in p_tag.text:
                    humidity = p_tag.text.strip().split()[-2]
                    break
            forecast = game_soup.find('img', class_='rounded weather-image')
            if forecast:
                forecast = forecast.find_next('p').text.strip()
            else:
                teams_divs = game_box.find_all('div', class_='team-game-box')
                team1 = teams_divs[0].find('span', class_='fw-bold').text.strip()
                team2 = teams_divs[1].find('span', class_='fw-bold ms-1').text.strip()
                forecast = 'Clear'
                precipitation = '0'

            teams_divs = game_box.find_all('div', class_='team-game-box')
            team1 = teams_divs[0].find('span', class_='fw-bold').text.strip()
            team2 = teams_divs[1].find('span', class_='fw-bold ms-1').text.strip()
            if team1 == "Redskins" or team1 == "Washington":
                team1 = "Commanders"
            if team2 == "Redskins" or team2 == "Washington":
                team2 = "Commanders"

            if 'Prob' in precipitation:
                precipitation = 0
            if 'Humidity' in humidity:
                humidity = 0

            weather_data = {
                'Temperature': temperature,
                'Wind': wind,
                'Precipitation': precipitation,
                'Humidity': humidity,
                'Forecast': map_forecast(forecast)
            }

            team_weather_data[team1] = weather_data
            team_weather_data[team2] = weather_data


        def assign_opponent_and_advantage(row):
            team_name = row['Tm']
            if team_name == home:
                hmcrt_adv = 1
                opp = away
            elif team_name == away:
                hmcrt_adv = 0
                opp = home
            else:
                raise ValueError(f"Invalid team name: {team_name}")
            return pd.Series([opp, hmcrt_adv], index=['Opponent', 'Hmcrt_adv'])

        def extract_table_data(soup, table_id, is_advanced=False, is_snap_counts=False):
            table = soup.find('div', id=table_id)
            if is_snap_counts:
                comment = table.find(string=lambda text: isinstance(text, Comment))
                table = BeautifulSoup(comment, 'html.parser')
            headers = [th.get_text(strip=True) for th in table.find('thead').find_all('tr')[-1].find_all('th')]
            data = [[cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])] for row in table.find('tbody').find_all('tr')]
            if is_advanced:
                for i, th in enumerate(table.find('thead').find_all('tr')[-1].find_all('th')):
                    over_header = th.get('data-over-header', '').strip()
                    if over_header == 'Rushing':
                        headers[i] = f'Rush_{headers[i]}'
                    elif over_header == 'Receiving':
                        headers[i] = f'Rec_{headers[i]}'
            else:
                headers.insert(1, 'player_link')
                for row in table.find('tbody').find_all('tr'):
                    if 'data-append-csv' in str(row.find('th')):
                        player_link = row.find('th').find('a')['href']
                        data_row = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
                        data_row.insert(1, player_link)
                        data.append(data_row)
            return pd.DataFrame(data, columns=headers)

        def clean_dataframe(df, subset_column, drop_duplicates=False, percent_column=None):
            df = df[df[subset_column] != subset_column]
            if drop_duplicates:
                df = df.loc[:, ~df.columns.duplicated()]
            if percent_column:
                df[percent_column] = df[percent_column].str.rstrip('%').astype(float)
            return df

        def merge_and_clean_dfs(main_df, df_to_merge, on_columns):
            merged_df = main_df.merge(df_to_merge, on=on_columns, how='left')
            for col in merged_df.columns:
                if col.endswith('_x'):
                    base_col = col[:-2]
                    if f'{base_col}_y' in merged_df.columns:
                        merged_df.drop(f'{base_col}_y', axis=1, inplace=True)
                    merged_df.rename(columns={col: base_col}, inplace=True)
            return merged_df

        def process_snap_counts_table(soup, table_id):
            df = extract_table_data(soup, table_id, is_snap_counts=True)
            df = clean_dataframe(df, 'Player', drop_duplicates=True, percent_column='Pct')
            df = df[df['Pct'] >= 20]
            return df

        def process_offense_data(soup, table_id, offense_df):
            advanced_df = extract_table_data(soup, table_id, is_advanced=True)
            advanced_df = clean_dataframe(advanced_df, 'Player')
            merged_df = merge_and_clean_dfs(advanced_df, offense_df, ['Player', 'Tm'])
            if table_id == 'all_passing_advanced':
                columns = [column for column in merged_df.columns if column.startswith('Rec')]
                merged_df.drop(columns=columns + ['Tgt', 'Att', 'Yds'], inplace=True)
                merged_df = merged_df[merged_df['Pass_Att'].astype(float) > 3]
            elif table_id == 'all_rushing_advanced' or table_id == 'all_receiving_advanced':
                columns = [column for column in merged_df.columns if column.startswith('Pass') or column.startswith('Sk')]
                if table_id == 'all_rushing_advanced':
                    merged_df.drop(columns=columns + ['Cmp', 'Int', 'Att', 'Yds', 'TD', 'Rate'], inplace=True)
                else:
                    merged_df.drop(columns=columns + ['Cmp', 'Int', 'Yds', 'TD', 'Rate'], inplace=True)
            merged_df.drop(columns=['Fmb'], inplace=True)
            return merged_df

        def process_and_merge_snap_counts(soup):
            home_snap_counts_df = process_snap_counts_table(soup, 'all_home_snap_counts')
            vis_snap_counts_df = process_snap_counts_table(soup, 'all_vis_snap_counts')
            snap_counts_df = pd.concat([home_snap_counts_df, vis_snap_counts_df], axis=0, ignore_index=True)
            snap_counts_df.drop(columns=['player_link'], inplace=True)
            return snap_counts_df

        def merge_snap_counts_with_box_scores(offense_dfs, snap_counts_df):
            merged_dfs = []
            for df in offense_dfs:
                merged_df = df.merge(snap_counts_df, on=['Player'], how='left').dropna()
                merged_dfs.append(merged_df)
            return merged_dfs

        def add_stadium_and_date_info(box_scores, stadium_box_score, game_date):
            import date
            date_tracker = date.Date()

            for df in box_scores:
                for col in stadium_box_score.columns:
                    df[col] = stadium_box_score.iloc[0][col]
                df['Date'] = game_date
                df['Date'] = df['Date'].apply(date_tracker.date_converter)
                df['Tm'] = df['Tm'].map(team_map)
                df[['Opponent', 'Hmcrt_adv']] = df.apply(assign_opponent_and_advantage, axis=1)
            return box_scores

        def clean_and_rearrange_columns(df):
            df = df.rename(columns={'Player': 'Name', 'Tm': 'Team'})
            df['Name'] = df['Name'].apply(unidecode)
            df['Name'] = df['Name'].apply(helper_functions.abbrv)
            df['Temperature'] = df['Team'].apply(lambda team: next((team_weather_data[key]['Temperature'] for key in team_weather_data if key in team), None))
            df['Humidity'] = df['Team'].apply(lambda team: next((team_weather_data[key]['Humidity'] for key in team_weather_data if key in team), None))
            df['Wind'] = df['Team'].apply(lambda team: next((team_weather_data[key]['Wind'] for key in team_weather_data if key in team), None))
            df['Precipitation'] = df['Team'].apply(lambda team: next((team_weather_data[key]['Precipitation'] for key in team_weather_data if key in team), None))
            df['Forecast'] = df['Team'].apply(lambda team: next((team_weather_data[key]['Forecast'] for key in team_weather_data if key in team), None))
            columns_to_drop = ['Pos', 'Num']
            df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
            cols_to_move = ['Opponent', 'Hmcrt_adv', 'Stadium', 'Roof', 'Surface', 'Temperature', 'Humidity', 'Wind', 'Precipitation', 'Forecast']
            df = df[['Name', 'Team'] + [col for col in df.columns if col not in cols_to_move] + cols_to_move]
            df = df.loc[:, ~df.columns.duplicated()]
            return df

        total_site_data = bets_scraper.site_scrape_chrome(f'https://www.pro-football-reference.com/years/2024/week_{week}.htm')
        time.sleep(3)
        import date
        date_tracker = date.Date()
        month, day = date_tracker.date_month_day(-1)
        box_score_month = month.zfill(2)
        box_score_day = day.zfill(2)
        links = {
            'https://www.pro-football-reference.com/' + a_href["href"]
            for a_href in total_site_data.find_all("a", href=True) if "boxscores" in a_href["href"] and "htm" in a_href["href"] and 'game-scores' not in a_href["href"] and f'2024{box_score_month}{box_score_day}' in a_href["href"]
        }
        passing_box_scores, rushing_box_scores, receiving_box_scores, kicking_box_scores = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        for link in links:
            time.sleep(3)
            page = requests.get(link)
            soup = BeautifulSoup(page.content)

            title = soup.title.string
            pattern = r"(.+) at (.+) - .+ \| Pro-Football-Reference\.com|.+ - (.+) vs\. (.+) - .+"
            match = re.match(pattern, title)
            if match:
                if match.group(1) and match.group(2):
                    away = match.group(1).split('-')[-1].strip() if '-' in match.group(1) else match.group(1).strip()
                    home = match.group(2).strip()
                else:
                    away = match.group(3).strip()
                    home = match.group(4).strip()
            else:
                away, home = None, None

            if away == 'Washington Football Team':
                away = 'Washington Commanders'
            if home == 'Washington Football Team':
                home = 'Washington Commanders'
            
            stadium_data = {'Stadium': None, 'Roof': None, 'Surface': None}

            stadium_data['Stadium'] = str(soup.find('div', class_ ='scorebox_meta')).split('Stadium')[1].split('</a>')[0].split('htm">')[1].strip()
            all_game_info_div = soup.find('div', id='all_game_info')
            if all_game_info_div:
                comments = all_game_info_div.find_all(string=lambda text: isinstance(text, Comment))
                for comment in comments:
                    comment_soup = BeautifulSoup(comment, 'html.parser')
                    game_info_table = comment_soup.find('table', id='game_info')
                    if game_info_table:
                        rows = game_info_table.find_all('tr')
                        for row in rows:
                            th = row.find('th')
                            td = row.find('td')
                            if th and td:
                                key = th.text.strip()
                                value = td.text.strip()
                                if key == 'Roof':
                                    stadium_data['Roof'] = value
                                elif key == 'Surface':
                                    stadium_data['Surface'] = value

            stadium_box_score = pd.DataFrame([stadium_data])
            stadium_box_score['Roof'] = stadium_box_score['Roof'].apply(lambda x: 'indoors' if x != 'outdoors' else x)
            stadium_box_score['Surface'] = stadium_box_score['Surface'].apply(lambda x: 'turf' if x != 'grass' else x)

            all_player_kicking_table = soup.find('div', id='all_kicking')
            comment = all_player_kicking_table.find(string=lambda text: isinstance(text, Comment))
            comment_soup = BeautifulSoup(comment, 'html.parser')

            headers = []
            thead = comment_soup.find('thead')
            if thead:
                header_rows = thead.find_all('tr')
                if len(header_rows) > 1:
                    header_cells = header_rows[1].find_all('th')
                    headers = [cell.get_text() for cell in header_cells]

            data = []
            tbody = comment_soup.find('tbody')
            if tbody:
                for row in tbody.find_all('tr'):
                    cells = row.find_all(['th', 'td'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    data.append(row_data)
            if headers and data:
                kicking_df = pd.DataFrame(data, columns=headers)
            kicking_df.dropna(subset=['Lng'], inplace=True)
            kicking_df = kicking_df[kicking_df['Player'] != 'Player']
            kicking_df = kicking_df[~((kicking_df['XPM'] == '') & 
                                    (kicking_df['XPA'] == '') & 
                                    (kicking_df['FGM'] == '') & 
                                    (kicking_df['FGA'] == ''))]
            kicking_df.replace('', '0', inplace=True)
            kicking_df.drop(columns=['Pnt', 'Yds', 'Y/P', 'Lng'], inplace=True)
            kicking_box_score = kicking_df

            offense_df = extract_table_data(soup, 'all_player_offense')

            new_column_names = [
                'Player', 'Link', 'Tm', 'Cmp', 'Pass_Att', 'Pass_Yds', 'Pass_TD', 'Int', 'Sk', 'Sk_Yds', 'Pass_Lng',
                'Rate', 'Rush_Att', 'Rush_Yds', 'Rush_TD', 'Rush_Lng', 'Tgt', 'Rec', 'Rec_Yds', 'Rec_TD', 'Rec_Lng',
                'Fmb', 'FL'
            ]

            offense_df.columns = new_column_names
            offense_df = clean_dataframe(offense_df, 'FL')
            offense_data_ids = ['all_passing_advanced', 'all_rushing_advanced', 'all_receiving_advanced']
            advanced_passing_dfs, advanced_rushing_dfs, advanced_receiving_dfs = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

            try:
                for table_id in offense_data_ids:
                    offense_df = process_offense_data(soup, table_id, offense_df)
                    offense_dfs.append(offense_df)
            except AttributeError:
                base_url = "https://www.pro-football-reference.com/"
                
                for idx, row in offense_df.iterrows():
                    link = f"{base_url}{row['Link'][:-4]}/gamelog/2024/advanced/"
                    if row['Link'][:-4]:
                        player_name = row['Player']
                        time.sleep(5) 
                        page = requests.get(link)
                        player_soup = BeautifulSoup(page.content, 'html.parser')
                        if 'Advanced Passing' in str(player_soup): 
                            advanced_df = extract_table_data(player_soup, 'all_advanced_passing', is_advanced=True)
                            match_date = f"2024-{box_score_month}-{box_score_day}"
                            advanced_df = advanced_df[advanced_df['Date'] == match_date]
                            advanced_df['Player'] = player_name
                            columns_to_drop = ['Rk', 'Date', 'G#', 'Week', 'Age', '', 'Opp', 'Result']
                            advanced_df = advanced_df.drop(columns=[col for col in columns_to_drop if col in advanced_df.columns]).replace('', 0).fillna(0)
                            advanced_df = clean_dataframe(advanced_df, 'Player')
                            merged_df = merge_and_clean_dfs(advanced_df, offense_df, ['Player', 'Tm'])
                            columns = [column for column in merged_df.columns if column.startswith('Rec')]
                            merged_df.drop(columns=columns + ['Tgt', 'Att', 'Yds'], inplace=True)
                            merged_df = merged_df[merged_df['Pass_Att'].astype(float) > 3]
                            advanced_passing_dfs = pd.concat([merged_df, advanced_passing_dfs])

                        if 'Advanced Rushing' in str(player_soup):
                            advanced_df = extract_table_data(player_soup, 'all_advanced_rushing_and_receiving', is_advanced=True)
                            match_date = f"2024-{box_score_month}-{box_score_day}"
                            advanced_df = advanced_df[advanced_df['Date'] == match_date]
                            advanced_df['Player'] = player_name
                            columns_to_drop = ['Rk', 'Date', 'G#', 'Week', 'Age', '', 'Opp', 'Result']
                            advanced_df = advanced_df.drop(columns=[col for col in columns_to_drop if col in advanced_df.columns]).replace('', 0).fillna(0)

                            mapping = {
                                'Rush_Att/Br': 'Att/Br',
                                'Rec_Tgt': 'Tgt',
                                'Rec_Rec': 'Rec',
                                'Rec_ADOT': 'ADOT',
                                'Rec_Drop': 'Drop',
                                'Rec_Drop%': 'Drop%',
                                'Rec_Int': 'Int',
                                'Rec_Rat': 'Rat'
                            }

                            advanced_df = advanced_df.rename(columns=mapping)
                            advanced_df = clean_dataframe(advanced_df, 'Player')
                            merged_df = merge_and_clean_dfs(advanced_df, offense_df, ['Player', 'Tm'])
                            columns = [column for column in merged_df.columns if column.startswith('Pass') or column.startswith('Sk')]
                            merged_df.drop(columns=columns + ['Cmp', 'Int', 'Rate', 'Fmb', 'Link'], inplace=True)
                            if 'Rec_YBC' in advanced_df.columns and 'Rush_YBC' in advanced_df.columns:
                                rushing_df = merged_df.copy()
                                rushing_columns_to_keep = ['Rec', 'Rec_Lng', 'Rec_TD', 'Rec_Yds']
                                rushing_df = rushing_df[[col for col in rushing_df.columns if not col.startswith('Rec') or col in rushing_columns_to_keep]]
                                rushing_df.columns = [col.replace('Rush_', '') if col.startswith('Rush_') and col not in ['Rush_Att', 'Rush_Lng', 'Rush_TD', 'Rush_Yds'] else col for col in rushing_df.columns]
                                rushing_df.drop(columns=['ADOT', 'Drop', 'Rat', 'Drop%'], inplace=True)
                                advanced_rushing_dfs = pd.concat([rushing_df, advanced_rushing_dfs], ignore_index=True)
                                receiving_df = merged_df.copy()
                                receiving_columns_to_keep = ['Rush', 'Rush_Lng', 'Rush_TD', 'Rush_Yds']
                                receiving_df = receiving_df[[col for col in receiving_df.columns if not col.startswith('Rush') or col in receiving_columns_to_keep]]
                                receiving_df.columns = [col.replace('Rec_', '') if col.startswith('Rec_') and col not in ['Rec', 'Rec_Lng', 'Rec_TD', 'Rec_Yds'] else col for col in receiving_df.columns]
                                receiving_df.drop(columns=['Att/Br'], inplace=True)
                                advanced_receiving_dfs = pd.concat([receiving_df, advanced_receiving_dfs], ignore_index=True)
                            elif 'Rush_Att' in advanced_df.columns:
                                advanced_rushing_dfs = pd.concat([merged_df, advanced_rushing_dfs], ignore_index=True)
                            elif 'Rec' in advanced_df.columns:
                                advanced_receiving_dfs = pd.concat([merged_df, advanced_receiving_dfs], ignore_index=True)

            offense_dfs = [advanced_passing_dfs, advanced_rushing_dfs, advanced_receiving_dfs]
            offense_dfs = [df.fillna(0) for df in offense_dfs]
            snap_counts_df = process_and_merge_snap_counts(soup)
            box_scores = merge_snap_counts_with_box_scores(offense_dfs, snap_counts_df) + [kicking_box_score]

            from datetime import datetime
            date_object = datetime.strptime(str(soup.find('div', class_='scorebox_meta')).split('<div>')[1].split('</div>')[0], "%A %b %d, %Y")
            game_date = str(date_object.month) + "-" + str(date_object.day)
            box_score_dfs = [passing_box_scores, rushing_box_scores, receiving_box_scores, kicking_box_scores]
            box_scores = add_stadium_and_date_info(box_scores, stadium_box_score, game_date)
            for i, box_score in enumerate(box_scores):
                box_score = clean_and_rearrange_columns(box_score)
                box_score_dfs[i] = pd.concat([box_score_dfs[i], box_score], ignore_index=True).drop_duplicates()
            passing_box_scores, rushing_box_scores, receiving_box_scores, kicking_box_scores = box_score_dfs
        return passing_box_scores, rushing_box_scores, receiving_box_scores, kicking_box_scores