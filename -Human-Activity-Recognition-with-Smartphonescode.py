# --------------
import pandas as pd
from collections import Counter

# Load dataset
data = pd.read_csv(path)


# --------------
import seaborn as sns
from matplotlib import pyplot as plt
sns.set_style(style='darkgrid')

# Store the label values 
label = data['Activity']

# plot the countplot
# sns.countplot(x=label)


# --------------
# make the copy of dataset

data_copy = data.copy()

# Create an empty column 

data_copy["duration"] = ""

# Calculate the duration

duration_df = (data_copy.groupby([label[label.isin(['WALKING_UPSTAIRS', 'WALKING_DOWNSTAIRS'])], 'subject'])['duration'].count() * 1.28)
duration_df = pd.DataFrame(duration_df)

# Sort the values of duration

plot_data = duration_df.reset_index().sort_values('duration', ascending=False)
plot_data['Activity'] = plot_data['Activity'].map({'WALKING_UPSTAIRS':'Upstairs', 'WALKING_DOWNSTAIRS':'Downstairs'})
sns.barplot(data=plot_data, x='subject', y='duration', hue='Activity')


# --------------
import numpy as np

#exclude the Activity column and the subject column
feature_cols = data.select_dtypes(exclude='object').columns.drop("subject")

#Calculate the correlation values
correlated_values = data[feature_cols].corr()

#stack the data and convert to a dataframe
correlated_values = correlated_values.stack().to_frame().reset_index().rename(columns={'level_0':'Feature_1', 'level_1': 'Feature_2', 0:'Correlation_score'})

#create an abs_correlation column
correlated_values["abs_correlation"] = abs(correlated_values["Correlation_score"])

#Picking most correlated features without having self correlated pairs
top_corr_fields = correlated_values.sort_values("Correlation_score", ascending=False)
top_corr_fields = top_corr_fields[top_corr_fields['Feature_1'] != top_corr_fields['Feature_2']].reset_index(drop=True)
top_corr_fields = top_corr_fields[top_corr_fields["abs_correlation"]>0.8]


# --------------
# importing neccessary libraries
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import precision_recall_fscore_support as error_metric
from sklearn.metrics import confusion_matrix, accuracy_score

# Encoding the target variable
le = LabelEncoder()
data["Activity"] = le.fit_transform(data["Activity"])

# split the dataset into train and test
X = data.drop(columns="Activity")
y = data["Activity"]
X_train, X_test, y_train, y_test = train_test_split(data.drop(columns="Activity"), data["Activity"], test_size=0.3, random_state=40)

# Baseline model 
classifier = SVC()
clf = classifier.fit(X_train, y_train)
y_pred = clf.predict(X_test)
precision, accuracy, f_score, na = error_metric(y_test, y_pred, average='weighted')
model1_score = clf.score(X_test, y_test)
model1_score, precision, accuracy, f_score


# --------------
# importing libraries
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import precision_recall_fscore_support as error_metric
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score

# Feature selection using Linear SVC
lsvc = LinearSVC(C = 0.01, penalty = 'l1', dual = False, random_state =42)
lsvc.fit(X_train, y_train)


# model building on reduced set of features
model_2 = SelectFromModel(lsvc, prefit=True)
new_train_features = model_2.transform(X_train)
new_test_features = model_2.transform(X_test)
classifier_2 = SVC()
clf_2 = classifier_2.fit(new_train_features, y_train)
y_pred_new = clf_2.predict(new_test_features)
model2_score = clf_2.score(new_test_features, y_test)
precision, recall, f_score, support = error_metric(y_test, clf_2.predict(new_test_features))
f_score = f1_score(y_test, y_pred_new, average='weighted')
print(f_score)


# --------------
# Importing Libraries
from sklearn.model_selection import GridSearchCV

# Set the hyperparmeters
parameters = {'kernel': ['linear', 'rbf'], 'C': [100, 20, 1, 0.1]}

# Usage of grid search to select the best hyperparmeters
selector = GridSearchCV(SVC(), scoring='accuracy', param_grid=parameters)
selector.fit(new_train_features, y_train)

means = selector.cv_results_['mean_test_score']
stds = selector.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, selector.cv_results_['params']):

    print('%0.3f (+/-%0.03f) for %r' % (mean, std * 2, params))

    print()
params = selector.best_params_

# Model building after Hyperparameter tuning
classifier_3 = SVC(C=params["C"], kernel=params["kernel"])
clf_3 = classifier_3.fit(new_train_features, y_train)
y_pred_final = clf_3.predict(new_test_features)
model3_score = clf_3.score(new_test_features, y_test)
# f_score = f1_score(y_test, y_pred_final, average='weighted')


