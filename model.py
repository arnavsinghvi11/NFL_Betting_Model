import pandas as pd
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import numpy as np
import re

conversions = {
    'Cmp': re.compile(r'^(?!.*long(est)? completion)(completions?|pass completions?|pass comp)', re.IGNORECASE),
    'Pass_Yds': re.compile(r'passing\s*(yards|yds)|pass\s*\+\s*rush\s*(yards|yds)|passing\s*\+\s*rushing\s*(yards|yds)', re.IGNORECASE),
    'Pass_TD': re.compile(r'pass(ing)?\s+touchdowns?|pass(ing)?\s+tds?', re.IGNORECASE),
    'Int': re.compile(r'int(erceptions?)?', re.IGNORECASE),
    'Pass_Att': re.compile(r'pass att(empts?)?', re.IGNORECASE),
    'Pass_Lng': re.compile(r'long(est)? completion( (yards|yds))?|((yards|yds))? longest completion', re.IGNORECASE),
    'Rush_Att': re.compile(r'rush att(empts?)?', re.IGNORECASE),
    'Rush_Yds': re.compile(r'rush(ing)? (yards|yds)', re.IGNORECASE),
    'Rush_TD': re.compile(r'rush(ing)?[\s_]?tds?(\+rec(eption)?[\s_]?tds?)?', re.IGNORECASE),
    'Rush_Lng': re.compile(r'long(est)? rush( (yards|yds))?|long rush( (yards|yds))?', re.IGNORECASE),
    'Tgt': re.compile(r'targets?|tgt', re.IGNORECASE),
    'Rec': re.compile(r'(?<!long\s)(?<!longest\s)\brec(eption)?s?\b(?!\s*(yards?|yds?|avg|average|long(est)?|receiving|targets?))', re.IGNORECASE),
    'Rec_Yds': re.compile(r'\brec(eiving|eptions)?\b (yards|yds)\b|receptions yds', re.IGNORECASE),
    'Rec_TD': re.compile(r'rec(eption)?[\s_]?tds?(\+rush(ing)?[\s_]?tds?)?', re.IGNORECASE),
    'Rec_Lng': re.compile(r'\blong(est)?\s+rec(eption)?(\s+receiving)?\s*(yards?|yds)?\b', re.IGNORECASE),
    'Pass_Yds+Rush_Yds': re.compile(r'pass(ing)?\s*(\+|and)?\s*rush(ing)?\s*(yards|yds)|pass(ing)?\s*(yards|yds)\s*\+\s*rush(ing)?\s*(yards|yds)|passing\s*\+\s*rushing\s*yards', re.IGNORECASE),
    'Rush_Yds+Rec_Yds': re.compile(r'rush(ing)?\s*(yards|yds)\s*\+\s*rec(eiving)?\s*(yards|yds)|rush\s*\+\s*rec\s*(yards|yds)', re.IGNORECASE),
    'Rush_TD+Rec_TD': re.compile(r'rush(ing)?_td\s*\+\s*rec(eiving)?_td|total\s*touchdowns', re.IGNORECASE),
    'XPM': re.compile(r'extra points made|made extra points|xpm|xps made', re.IGNORECASE),
    'FGM': re.compile(r'field goals made|made field goals|fgm|fgs made', re.IGNORECASE)
}

class Model:
    def convert_dummies(self, all_evals, column, prefix):
        #returns one-hot encoding of categorical variables
        dummy = pd.get_dummies(all_evals[column], prefix=prefix)
        all_evals = all_evals.drop(columns = [column])
        return pd.concat([all_evals.reset_index(drop=True),dummy.reset_index(drop=True)], axis=1)

    def features_remover(self, feature, features_list):
        #removes unneeded features from inputted features 
        if feature in features_list:
            features_list.remove(feature)
        return features_list

    def over(self, row):
        #returns 1 if prop bet is type - over and 0 if prop bet is type - under 
        plays = [i for i in row['Play'].split(' ') if i != '']
        if plays[1][0] == 'o' or plays[1] == 'Yes':
            val = 1
        else:
            val = 0
        return val

    def prop_bet_finder(self, row):
        prop_bet_types = row['Play'].lower().split(' ')[2:]
        prop_bet_type = ' '.join(prop_bet_types).strip()
        contains_plus = '+' in prop_bet_type
        for key, pattern in conversions.items():
            if contains_plus and '+' not in key:
                continue
            if not contains_plus and '+' in key and 'total touchdowns' not in prop_bet_type:
                continue
            if pattern.search(prop_bet_type):
                return key
        return prop_bet_type

    def preprocessing(self, data_input, is_evaluation):
        #conducts feature engineering over bets inputs and outputs preprocessed input
        data_input['Over?'] = data_input.apply(self.over, axis = 1)
        data_input['Under?'] = 1 - data_input['Over?']
        data_input['Prop Bets'] = data_input.apply(self.prop_bet_finder, axis = 1) 
        data_input = self.convert_dummies(data_input, 'Prop Bets', 'Prop_Bet_Type_')
        data_input = self.convert_dummies(data_input, 'Expert', 'Expert_')
        data_input = self.convert_dummies(data_input, 'Team', 'Team_')
        data_input = self.convert_dummies(data_input, 'Opponent', 'Opp_')
        data_input = self.convert_dummies(data_input, 'Stadium', 'Stadium_')
        data_input = self.convert_dummies(data_input, 'Roof', 'Roof_')
        data_input = self.convert_dummies(data_input, 'Surface', 'Surface_')
        data_input = self.convert_dummies(data_input, 'Forecast', 'Forecast_')
        data_input = data_input.drop(columns = ['Play'])
        if is_evaluation:
            correct = data_input.pop('Correct')
            data_input['Correct'] = correct
        return data_input
    
    def features_processing(self, features):
        #removes extraneous features from features set
        features = self.features_remover('Name', features)
        features = self.features_remover('Profit', features)
        features = self.features_remover('Net Units Record', features)
        features = self.features_remover('Odds', features)
        features = self.features_remover('Units', features)
        features = self.features_remover('Payout', features)
        return features

    def train(self, features, target, data_input):
        weights = data_input['Weight'].values
        features = [f for f in features if f != 'Weight']
        #model training to predict if bets prediction will come true
        X = data_input.loc[:, features].values * weights[:, None]
        Y = data_input.loc[:, target].values

        #split into training and testing sets 
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.4, random_state=0)


        encoder = LabelEncoder()
        y_train_encoded = encoder.fit_transform(y_train.ravel())
        y_test_encoded = encoder.transform(y_test.ravel())

        scaler = StandardScaler()
        train_scaled = scaler.fit_transform(X_train)
        test_scaled = scaler.transform(X_test)

        models = []
        models.append(('LR', LogisticRegression(random_state=0, C= 0.4, solver='liblinear', multi_class='ovr')))
        models.append(('LDA', LinearDiscriminantAnalysis(solver = 'lsqr', shrinkage = 0.91)))
        models.append(('KNN', KNeighborsClassifier(leaf_size = 1, p = 1, n_neighbors = 5)))
        models.append(('NB', GaussianNB(var_smoothing = 1.0)))
        models.append(('SVM', SVC(kernel='linear', C=1, gamma = 0.001, probability=True)))
        models.append(('MLP', MLPClassifier(random_state = 0)))
        models.append(('BAG', BaggingClassifier(base_estimator=DecisionTreeClassifier(), n_estimators=100, random_state = 0)))
        models.append(('RFC', RandomForestClassifier(n_estimators=200, random_state = 0)))
        models.append(('EX', ExtraTreesClassifier(n_estimators=200,  random_state = 0)))
        models.append(('ADA', AdaBoostClassifier(n_estimators=100,  random_state = 0)))
        models.append(('STO', GradientBoostingClassifier(n_estimators=100,  random_state = 0)))

        # evaluate each model in turn
        predictions, top5_models, final_models = [], [], []
        for name, model in models:
            model.fit(train_scaled, y_train_encoded)
            top5_models.append([model, model.score(test_scaled, y_test_encoded)])
        top5_models.sort(key = lambda x: x[1], reverse = True)
        top5_models = top5_models[:5]
        for model1 in top5_models:
            for model2 in models:
                if model1[0] == model2[1]:
                    final_models.append(model2)
        ensemble = VotingClassifier(final_models)
        return X, Y, ensemble