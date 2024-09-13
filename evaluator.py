from unidecode import unidecode
from itertools import combinations
import numpy as np
import pandas as pd
import os

class Evaluator:
    def stat_greater_than(self, stat, player_data, threshold):
        # returns if player's given statistic is higher than passed in threshold
        actual_value = float(player_data[stat].values[0])
        return actual_value, actual_value > float(threshold)

    def stat_less_than(self, stat, player_data, threshold):
        # returns if player's given statistic is lower than passed in threshold
        actual_value = float(player_data[stat].values[0])
        return actual_value, actual_value < float(threshold)

    def evaluator(self, symbol, first_stat, second_stat, third_stat, player_data, threshold):
        # returns if player achieved above prop threshold if an over bet, under prop threshold if an under bet

        # preprocessing for triple double props
        if third_stat:
            actual_value = float(player_data[first_stat].values[0]) + float(player_data[second_stat].values[0]) + float(player_data[third_stat].values[0])
            label = 'Y' if (actual_value > threshold if symbol == '>' else actual_value < threshold) else 'N'
            return actual_value, label

        # preprocessing for double double props
        if second_stat:
            actual_value = float(player_data[first_stat].values[0]) + float(player_data[second_stat].values[0])
            label = 'Y' if (actual_value > threshold if symbol == '>' else actual_value < threshold) else 'N'
            return actual_value, label

        if symbol == '>':
            actual_value, is_greater = self.stat_greater_than(first_stat, player_data, threshold)
        else:
            actual_value, is_less = self.stat_less_than(first_stat, player_data, threshold)

        label = 'Y' if (is_greater if symbol == '>' else is_less) else 'N'
        return actual_value, label


    def predictions_evaluator(self, predictions, passing_box_score, rushing_box_score, receiving_box_score, kicking_box_score):
        #returns evaluations of past predictions based on past box score corresponding
        correct, actual_values = [], []
        for p in range(len(predictions)):
            bet = predictions.loc[p]
            bet['Play'] = bet['Play'].replace('  ', ' ')
            bet['Play'] = bet['Play'].lower()
            i = bet['Play']
            name = unidecode(i.split(' ')[0])
            teams = [bet['Team']]
            prop_bet_types = bet['Play'].split(' ')[2:]
            if len(prop_bet_types) > 1:
                prop_bet_type = ''
                for prop_bet in prop_bet_types:
                    prop_bet_type += prop_bet
                    prop_bet_type += ' '
            else:
                prop_bet_type = prop_bet_types[0]
            prop_bet_type = prop_bet_type.strip()

            if prop_bet_type == 'completions' or prop_bet_type == 'passing yards'  or prop_bet_type == 'passing yds'  or prop_bet_type == 'pass att' or prop_bet_type == 'pass attempts' or prop_bet_type == 'longest completion' or prop_bet_type == 'longest completion yards' or prop_bet_type == 'yards longest completion' or prop_bet_type == 'pass yards' or prop_bet_type == 'pass yds' or prop_bet_type == 'passing tds' or prop_bet_type == 'passing touchdowns' or prop_bet_type == 'passing tds' or prop_bet_type == 'pass tds' or prop_bet_type == 'pass comp' or prop_bet_type == 'pass completions' or prop_bet_type == 'interceptions' or prop_bet_type == 'ints' or prop_bet_type == 'int' or prop_bet_type == 'passing + rushing yards' or prop_bet_type == 'pass yds + rush yds' or prop_bet_type == 'pass + rush yds':
                passing_box_score['Name'] = passing_box_score['Name'].apply(unidecode)
                matching_name = passing_box_score[passing_box_score['Name'].str.lower() == name]
                player_data = matching_name[matching_name['Team'].isin(teams)]
            elif prop_bet_type == 'rush att' or prop_bet_type == 'rush attempts' or prop_bet_type == 'rushing yds' or prop_bet_type == 'rushing yards' or prop_bet_type == 'rush yds' or prop_bet_type == 'rush yards' or prop_bet_type == 'longest rush' or prop_bet_type == 'longest rush yards' or prop_bet_type == 'long rush' or prop_bet_type == 'long rush yards' or prop_bet_type == 'rushing + receiving yards' or prop_bet_type == 'rush yds + rec yds' or prop_bet_type == 'rush + rec yds':
                rushing_box_score['Name'] = rushing_box_score['Name'].apply(unidecode)
                matching_name = rushing_box_score[rushing_box_score['Name'].str.lower() == name]
                player_data = matching_name[matching_name['Team'].isin(teams)]
                if len(player_data) == 0:
                    receiving_box_score['Name'] = receiving_box_score['Name'].apply(unidecode)
                    matching_name = receiving_box_score[receiving_box_score['Name'].str.lower() == name]
                    player_data = matching_name[matching_name['Team'].isin(teams)]
                    if len(player_data) == 0:
                        passing_box_score['Name'] = passing_box_score['Name'].apply(unidecode)
                        matching_name = passing_box_score[passing_box_score['Name'].str.lower() == name]
                        player_data = matching_name[matching_name['Team'].isin(teams)]
            elif prop_bet_type == 'receptions' or prop_bet_type == 'recs' or prop_bet_type == 'rec' or prop_bet_type == 'reception' or prop_bet_type == 'receiving yards' or prop_bet_type == 'receiving yds' or prop_bet_type == 'rec yds' or prop_bet_type == 'receptions yds' or prop_bet_type == 'longest reception' or prop_bet_type == 'longest reception receiving yards' or prop_bet_type == 'longest reception yards' or prop_bet_type == 'long reception' or prop_bet_type == 'rush_td+rec_td' or prop_bet_type == 'total touchdowns':
                receiving_box_score['Name'] = receiving_box_score['Name'].apply(unidecode)
                matching_name = receiving_box_score[receiving_box_score['Name'].str.lower() == name]
                player_data = matching_name[matching_name['Team'].isin(teams)]
                if len(player_data) == 0:
                    rushing_box_score['Name'] = rushing_box_score['Name'].apply(unidecode)
                    matching_name = rushing_box_score[rushing_box_score['Name'].str.lower() == name]
                    player_data = matching_name[matching_name['Team'].isin(teams)]
            elif prop_bet_type == 'field goals made' or prop_bet_type == 'made field goals' or prop_bet_type == 'fgm' or prop_bet_type == 'fgs made' or prop_bet_type == 'extra points made' or prop_bet_type == 'made extra points' or prop_bet_type == 'xpm' or prop_bet_type == 'xps made':
                kicking_box_score['Name'] = kicking_box_score['Name'].apply(unidecode)
                matching_name = kicking_box_score[kicking_box_score['Name'].str.lower() == name]
                player_data = matching_name[matching_name['Team'].isin(teams)]
            else:
                player_data = pd.DataFrame()
            #return 'X' if player did not play in past box score
            if len(player_data) == 0:
                if '+' in prop_bet_type:
                    if any(x in prop_bet_type for x in ['passing', 'pass']) and any(x in prop_bet_type for x in ['rushing', 'rush']):
                        rushing_box_score['Name'] = rushing_box_score['Name'].apply(unidecode)
                        matching_name = rushing_box_score[rushing_box_score['Name'].str.lower() == name]
                        if len(matching_name) != 0:
                            player_data = matching_name[matching_name['Team'].isin(teams)]
                    elif any(x in prop_bet_type for x in ['rushing', 'rush']) and any(x in prop_bet_type for x in ['receiving', 'rec']):
                        receiving_box_score['Name'] = receiving_box_score['Name'].apply(unidecode)
                        matching_name = receiving_box_score[receiving_box_score['Name'].str.lower() == name]
                        if len(matching_name) != 0:
                            player_data = matching_name[matching_name['Team'].isin(teams)]
                        print(name)
                        print(len(player_data))
                    if len(player_data) == 0:
                        correct.append('X')
                        actual_values.append(np.nan)
                        continue
                else:
                    correct.append('X')
                    actual_values.append(np.nan)
                    continue
            
            prediction = [j for j in i.split(' ')[1:] if len(j) > 0]
            if prediction[0][0] == 'o':
                if prop_bet_type in ['completions', 'pass completions', 'pass comp']:
                    actual_value, result = self.evaluator('>', 'Cmp', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['passing yards', 'passing yds', 'pass yards', 'pass yds']:
                    actual_value, result = self.evaluator('>', 'Pass_Yds', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['passing tds', 'passing touchdowns', 'pass tds']:
                    actual_value, result = self.evaluator('>', 'Pass_TD', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['pass att', 'pass attempts']:
                    actual_value, result = self.evaluator('>', 'Pass_Att', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['longest completion', 'longest completion yards', 'yards longest completion']:
                    actual_value, result = self.evaluator('>', 'Pass_Lng', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['interceptions', 'ints', 'int']:
                    actual_value, result = self.evaluator('>', 'Int', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['rush att', 'rush attempts']:
                    actual_value, result = self.evaluator('>', 'Rush_Att', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['rushing yards', 'rushing yds', 'rush yds', 'rush yards']:
                    actual_value, result = self.evaluator('>', 'Rush_Yds', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['longest rush', 'long rush', 'long rush yards', 'longest rush yards']:
                    actual_value, result = self.evaluator('>', 'Rush_Lng', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['receptions', 'recs', 'rec', 'reception']:
                    actual_value, result = self.evaluator('>', 'Rec', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['receiving yards', 'receiving yds', 'rec yds', 'receptions yds']:
                    actual_value, result = self.evaluator('>', 'Rec_Yds', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['longest reception', 'long reception', 'longest reception receiving yards', 'longest reception yards']:
                    actual_value, result = self.evaluator('>', 'Rec_Lng', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['field goals made', 'made field goals', 'fgm', 'fgs made']:
                    actual_value, result = self.evaluator('>', 'FGM', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['extra points made', 'made extra points', 'xpm', 'xps made']:
                    actual_value, result = self.evaluator('>', 'XPM', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['pass yds + rush yds', 'pass + rush yds', 'passing + rushing yards']:
                    actual_value, result = self.evaluator('>', 'Pass_Yds', 'Rush_Yds', None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['rush yds + rec yds', 'rush + rec yds', 'rushing + receiving yards']:
                    actual_value, result = self.evaluator('>', 'Rush_Yds', 'Rec_Yds', None, player_data, float(prediction[0][1:]))
                elif prop_bet_type == 'rush_td+rec_td' or prop_bet_type == 'total touchdowns':
                    actual_value, result = self.evaluator('>', 'Rush_TD', 'Rec_TD', None, player_data, float(prediction[0][1:]))

            elif prediction[0][0] == 'u':
                if prop_bet_type in ['completions', 'pass completions', 'pass comp']:
                    actual_value, result = self.evaluator('<', 'Cmp', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['passing yards', 'passing yds', 'pass yards', 'pass yds']:
                    actual_value, result = self.evaluator('<', 'Pass_Yds', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['passing tds', 'passing touchdowns', 'pass tds']:
                    actual_value, result = self.evaluator('<', 'Pass_TD', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['pass att', 'pass attempts']:
                    actual_value, result = self.evaluator('<', 'Pass_Att', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['longest completion', 'longest completion yards', 'yards longest completion']:
                    actual_value, result = self.evaluator('<', 'Pass_Lng', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type == ['interceptions', 'ints', 'int']:
                    actual_value, result = self.evaluator('<', 'Int', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['rush att', 'rush attempts']:
                    actual_value, result = self.evaluator('<', 'Rush_Att', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['rushing yards', 'rushing yds', 'rush yds', 'rush yards']:
                    actual_value, result = self.evaluator('<', 'Rush_Yds', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['longest rush', 'long rush', 'long rush yards', 'longest rush yards']:
                    actual_value, result = self.evaluator('<', 'Rush_Lng', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['receptions', 'recs', 'rec', 'reception']:
                    actual_value, result = self.evaluator('<', 'Rec', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['receiving yards', 'receiving yds', 'rec yds', 'receptions yds']:
                    actual_value, result = self.evaluator('<', 'Rec_Yds', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['longest reception', 'long reception', 'longest reception receiving yards', 'longest reception yards']:
                    actual_value, result = self.evaluator('<', 'Rec_Lng', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['field goals made', 'made field goals', 'fgm', 'fgs made']:
                    actual_value, result = self.evaluator('<', 'FGM', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['extra points made', 'made extra points', 'xpm', 'xps made']:
                    actual_value, result = self.evaluator('<', 'XPM', None, None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['pass yds + rush yds', 'pass + rush yds', 'passing + rushing yards']:
                    actual_value, result = self.evaluator('<', 'Pass_Yds', 'Rush_Yds', None, player_data, float(prediction[0][1:]))
                elif prop_bet_type in ['rush yds + rec yds', 'rush + rec yds', 'rushing + receiving yards']:
                    actual_value, result = self.evaluator('<', 'Rush_Yds', 'Rec_Yds', None, player_data, float(prediction[0][1:]))
                elif prop_bet_type == 'rush_td+rec_td' or prop_bet_type == 'total touchdowns':
                    actual_value, result = self.evaluator('<', 'Rush_TD', 'Rec_TD', None, player_data, float(prediction[0][1:]))
            
            correct.append(result)
            actual_values.append(actual_value)

        predictions['Correct'] = correct
        predictions['Actual Value'] = actual_values
        return predictions.loc[predictions['Correct'] != 'X']

    def past_games_stats_evaluator(self, vals, prop_bet_number, is_over):
        #returns array of how many games player performs above or below given threshold
        vals = [float(i) for i in vals]
        ovr_avg_correct = []
        if is_over:
            for i in vals:
                if prop_bet_number < i:
                    ovr_avg_correct.append('Y')
                else:
                    ovr_avg_correct.append('N')
            return ovr_avg_correct
        else:
            for i in vals:
                if prop_bet_number > i:
                    ovr_avg_correct.append('Y')
                else:
                    ovr_avg_correct.append('N')
            return ovr_avg_correct

    def past_evaluator(self, games, prop_bet_type, prop_bet_number, is_over):
        #returns past game evaluations for prop types
        if len(games) == 0:
            return 0.0, 0
        if prop_bet_type == 'completions' or prop_bet_type == 'pass completions' or prop_bet_type == 'pass comp':
            vals = games['Cmp'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'passing yards' or prop_bet_type == 'passing yds' or prop_bet_type == 'pass yards' or prop_bet_type == 'pass yds':
            vals = games['Pass_Yds'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'passing tds' or prop_bet_type == 'passing touchdowns' or prop_bet_type == 'pass tds':
            vals = games['Pass_TD'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'pass att' or prop_bet_type == 'pass attempts':
            vals = games['Pass_Att'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'longest completion' or prop_bet_type == 'longest completion yards' or prop_bet_type == 'yards longest completion':
            vals = games['Pass_Lng'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'interceptions' or prop_bet_type == 'int' or prop_bet_type == 'ints':
            vals = games['Int'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'rush att' or prop_bet_type == 'rush attempts':
            vals = games['Rush_Att'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'rushing yards' or prop_bet_type == 'rushing yds' or prop_bet_type == 'rush yds' or prop_bet_type == 'rush yards':
            vals = games['Rush_Yds'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'longest rush' or prop_bet_type == 'long rush' or prop_bet_type == 'long rush yards' or prop_bet_type == 'longest rush yards':
            vals = games['Rush_Lng'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'receptions' or prop_bet_type == 'recs' or prop_bet_type == 'rec' or prop_bet_type == 'receptions' or prop_bet_type == 'reception':
            vals = games['Rec'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'receiving yards' or prop_bet_type == 'rec yds' or prop_bet_type == 'receptions yds' or prop_bet_type == 'receiving yds':
            vals = games['Rec_Yds'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'longest reception' or prop_bet_type == 'long reception' or prop_bet_type == 'longest reception receiving yards' or prop_bet_type == 'longest reception yards':
            vals = games['Rec_Lng'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'field goals made' or prop_bet_type == 'made field goals' or prop_bet_type == 'fgm' or prop_bet_type == 'fgs made':
            vals = games['FGM'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'extra points made' or prop_bet_type == 'made extra points' or prop_bet_type == 'xpm' or prop_bet_type == 'xps made':
            vals = games['XPM'].values
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'pass yds + rush yds' or prop_bet_type == 'pass + rush yds' or prop_bet_type == 'passing + rushing yards':
            vals = [v1 + v2 for v1, v2 in zip(games['Pass_Yds'].values, games['Rush_Yds'].values)]
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'rush yds + rec yds' or prop_bet_type == 'rush + rec yds' or prop_bet_type == 'rushing + receiving yards':
            vals = [v1 + v2 for v1, v2 in zip(games['Rush_Yds'].values, games['Rec_Yds'].values)]
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        if prop_bet_type == 'rush_td+rec_td' or prop_bet_type == 'total touchdowns':
            vals = [v1 + v2 for v1, v2 in zip(games['Rush_TD'].values, games['Rec_TD'].values)]
            ovr_avg_correct = self.past_games_stats_evaluator(vals, prop_bet_number, is_over)
        ovr_avg_correct_prct = sum([1 for i in ovr_avg_correct if i == 'Y']) / len(ovr_avg_correct)
        if ovr_avg_correct_prct > 0.5:
            over_half = 1
        else:
            over_half = 0
        return ovr_avg_correct_prct, over_half

    def past_games_trends(self, predictions, passing_box_score_results, rushing_box_score_results, receiving_box_score_results, kicking_box_score_results, is_evaluation):
        #returns evaluations if a player performs above or below given threshold for all games played, past 5 games played, past 3 games played
        all_games_prcts, all_games_trues, last3_prcts, last3_trues, last5_prcts, last5_trues = [], [], [], [], [], []
        for i in predictions.index:
            bet = predictions.loc[i]
            bet['Play'] = bet['Play'].replace('  ', ' ')
            bet['Play'] = bet['Play'].lower()
            print(bet['Play'])
            name = bet['Play'].split(' ')[0]
            teams = [bet['Team']]
            prop = bet['Play'].split(' ')[1]
            #determine type of prop bets
            prop_bet_types = bet['Play'].split(' ')[2:]
            if len(prop_bet_types) > 1:
                prop_bet_type = ''
                for prop_bet in prop_bet_types:
                    prop_bet_type += prop_bet
                    prop_bet_type += ' '
            else:
                prop_bet_type = prop_bet_types[0]
            prop_bet_type = prop_bet_type.strip()
            over = prop[0] == 'o'
            prop_bet_number = float(prop[1:].split(' ')[0])

            #evaluate past trends based on identified player's past statistics
            if prop_bet_type == 'completions' or prop_bet_type == 'pass comp' or prop_bet_type == 'passing yards' or prop_bet_type == 'passing yds' or prop_bet_type == 'pass att' or prop_bet_type == 'pass attempts' or prop_bet_type == 'longest completion' or prop_bet_type == 'longest completion yards' or prop_bet_type == 'yards longest completion' or prop_bet_type == 'pass yards' or prop_bet_type == 'pass yds' or prop_bet_type == 'passing tds' or prop_bet_type == 'passing touchdowns' or prop_bet_type == 'pass tds' or prop_bet_type == 'pass completions' or prop_bet_type == 'interceptions' or prop_bet_type == 'int' or prop_bet_type == 'ints' or prop_bet_type == 'passing + rushing yards' or prop_bet_type == 'pass yds + rush yds' or prop_bet_type == 'pass + rush yds':
                matching_name = passing_box_score_results[passing_box_score_results['Name'].str.lower() == name]
                all_games = matching_name[matching_name['Team'].isin(teams)]
            elif prop_bet_type == 'rush att' or prop_bet_type == 'rush attempts' or prop_bet_type == 'rushing yards' or prop_bet_type == 'rush yds' or prop_bet_type == 'rush yards' or prop_bet_type == 'rushing yds' or prop_bet_type == 'longest rush' or prop_bet_type == 'longest rush yards' or prop_bet_type == 'long rush' or prop_bet_type == 'long rush yards' or prop_bet_type == 'rushing + receiving yards' or prop_bet_type == 'rush yds + rec yds' or prop_bet_type == 'rush + rec yds':
                matching_name = rushing_box_score_results[rushing_box_score_results['Name'].str.lower() == name]
                all_games = matching_name[matching_name['Team'].isin(teams)]
            elif prop_bet_type == 'receptions' or prop_bet_type == 'recs' or prop_bet_type == 'rec' or prop_bet_type == 'reception' or prop_bet_type == 'receiving yards' or prop_bet_type == 'receiving yds' or prop_bet_type == 'rec yds' or prop_bet_type == 'receptions yds' or prop_bet_type == 'longest reception' or prop_bet_type == 'long reception'  or prop_bet_type == 'longest reception receiving yards' or prop_bet_type == 'longest reception yards' or prop_bet_type == 'rush_td+rec_td' or prop_bet_type == 'total touchdowns':
                matching_name = receiving_box_score_results[receiving_box_score_results['Name'].str.lower() == name]
                all_games = matching_name[matching_name['Team'].isin(teams)]
            elif prop_bet_type in ['field goals made', 'made field goals', 'fgm', 'fgs made', 'extra points made', 'made extra points', 'xpm', 'xps made']:
                matching_name = kicking_box_score_results[kicking_box_score_results['Name'].str.lower() == name]
                all_games = matching_name[matching_name['Team'].isin(teams)]

            if '+' in prop_bet_type:
                if any(x in prop_bet_type for x in ['passing', 'pass']) and any(x in prop_bet_type for x in ['rushing', 'rush']):
                    matching_name_extra = rushing_box_score_results[rushing_box_score_results['Name'].str.lower() == name]
                    all_games_extra = matching_name_extra[matching_name_extra['Team'].isin(teams)]
                    similar_columns = set(all_games.columns).intersection(set(all_games_extra.columns))
                    missing_dates = all_games_extra[~all_games_extra['Date'].isin(all_games['Date'])]
                    new_rows = []
                    for index, row in missing_dates.iterrows():
                        new_row = {col: row[col] if col in similar_columns else 0 for col in all_games.columns}
                        new_rows.append(new_row)
                    new_rows_df = pd.DataFrame(new_rows, columns=all_games.columns)
                    all_games = pd.concat([all_games, new_rows_df], ignore_index=True)
                    all_games = all_games.sort_values(by='Date', ascending=False)

                elif any(x in prop_bet_type for x in ['rushing', 'rush']) and any(x in prop_bet_type for x in ['receiving', 'rec']):
                    matching_name_extra = receiving_box_score_results[receiving_box_score_results['Name'].str.lower() == name]
                    all_games_extra = matching_name_extra[matching_name_extra['Team'].isin(teams)]
                    similar_columns = set(all_games.columns).intersection(set(all_games_extra.columns))
                    missing_dates = all_games_extra[~all_games_extra['Date'].isin(all_games['Date'])]
                    new_rows = []
                    for index, row in missing_dates.iterrows():
                        new_row = {col: row[col] if col in similar_columns else 0 for col in all_games.columns}
                        new_rows.append(new_row)
                    new_rows_df = pd.DataFrame(new_rows, columns=all_games.columns)
                    all_games = pd.concat([all_games, new_rows_df], ignore_index=True)
                    all_games = all_games.sort_values(by='Date', ascending=False)

            last3_games = all_games[:3]
            last5_games =  all_games[:5]
            all_games_prct, all_games_true = self.past_evaluator(all_games, prop_bet_type, prop_bet_number, over)
            last3_prct, last3_true = self.past_evaluator(last3_games, prop_bet_type, prop_bet_number, over)
            last5_prct, last5_true = self.past_evaluator(last5_games, prop_bet_type, prop_bet_number, over)
            all_games_prcts.append(all_games_prct)
            all_games_trues.append(all_games_true)
            last3_prcts.append(last3_prct)
            last3_trues.append(last3_true)
            last5_prcts.append(last5_prct)
            last5_trues.append(last5_true)

        predictions['All Game Percentages'], predictions['All Game Correct'], predictions['Last 3 Percentages'], predictions['Last 3 Correct'], predictions['Last 5 Percentages'], predictions['Last 5 Correct']  = all_games_prcts, all_games_trues, last3_prcts, last3_trues, last5_prcts, last5_trues
        #determine if inputs for evaluted predictions which have 'Correct' feature identified or current predictions which are to be determined
        if is_evaluation:
            features_list = ['Play', 'Expert', 'Team', 'Name', 'Opponent',
            'Hmcrt_adv', 'Correct', 'Actual Value', 'All Game Percentages',
            'All Game Correct', 'Last 3 Percentages', 'Last 3 Correct',
            'Last 5 Percentages', 'Last 5 Correct', 'Temperature','Wind','Humidity','Precipitation','Forecast','Stadium','Roof','Surface'] #'Odds', 'Units', 'Payout','Profit'
        else:
            features_list = ['Play', 'Expert', 'Team', 'Name', 'Opponent',
            'Hmcrt_adv', 'All Game Percentages',
        'All Game Correct', 'Last 3 Percentages', 'Last 3 Correct',
        'Last 5 Percentages', 'Last 5 Correct', 'Temperature','Wind','Humidity','Precipitation','Forecast','Stadium','Roof','Surface']
        return predictions[features_list]

    def optimized_predictions_evaluator(self, optimized_predictions, current_evaluation):
        #return evaluations of past optimized predictions
        optimized_correct = []
        for i in range(len(optimized_predictions)):
            optimized_prediction = optimized_predictions.loc[i]
            if len(current_evaluation[(current_evaluation['Play'] == optimized_prediction['Play']) & (current_evaluation['Expert'] == optimized_prediction['Expert'])  & (current_evaluation['Odds'] == optimized_prediction['Odds'])]) == 0:
                optimized_correct.append('X')
            else:
                optimized_correct.append(current_evaluation[(current_evaluation['Play'] == optimized_prediction['Play']) & (current_evaluation['Expert'] == optimized_prediction['Expert'])  & (current_evaluation['Odds'] == optimized_prediction['Odds'])]['Correct'].values[0])
        return optimized_correct