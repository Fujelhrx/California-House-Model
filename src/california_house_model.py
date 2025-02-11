# -*- coding: utf-8 -*-
"""California_house_model.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zlzhWwTcqhrcXhgFTjLRZ0hmoBfz-xbm
"""

from pathlib import Path
import pandas as pd
import tarfile
import urllib.request

"""# Download The Data"""

from operator import truth
def load_housing_data():
  tarball_path = Path("datasets/housing.tgz")
  if not tarball_path.is_file():
    Path("datasets").mkdir(parents = True , exist_ok = True)
    url = "https://github.com/ageron/data/raw/main/housing.tgz"
    urllib.request.urlretrieve(url , tarball_path)
    with tarfile.open(tarball_path) as housing_tarball:
      housing_tarball.extractall(path = "datasets")
  return pd.read_csv(Path("datasets/housing/housing.csv"))

housing = load_housing_data()

"""# Take a Quick look at the Data Structure"""

housing.head()

housing.info()

housing["ocean_proximity"].value_counts

housing.describe()

import matplotlib.pyplot as plt

housing.hist(bins = 50, figsize = (12,8))
plt.show()

"""# Create a Test Set"""

from sklearn.model_selection import train_test_split

train_set, test_set = train_test_split(housing , test_size=0.2 , random_state=42)

import numpy as np

housing["income_cut"]= pd.cut(housing["median_income"],
                              bins = [0,1.5,3.0,4.5,6, np.inf],
                              labels = [1,2,3,4,5])

housing["income_cut"].value_counts().sort_index().plot.bar(rot = 0 , grid =True)
plt.xlabel("income Category")
plt.ylabel("number of Districts")
plt.show()

from sklearn.model_selection import StratifiedShuffleSplit

splitter = StratifiedShuffleSplit(n_splits = 10, test_size =0.2, random_state = 42)
strat_splits =[]
for train_index , test_index in splitter.split(housing ,housing["income_cut"]):
  strat_train_set_n = housing.iloc[train_index]
  strat_test_set_n = housing.iloc[test_index]
  strat_splits.append([strat_train_set_n , strat_test_set_n])

# use the first split :

strat_train_set , strat_test_set = strat_splits[0]

strat_train_set , strat_test_set = train_test_split(housing , test_size = 0.2 , stratify = housing["income_cut"], random_state = 42)

strat_test_set["income_cut"].value_counts () / len(strat_test_set)

"""# explore Visualize the Data to Gain Insights"""

housing = strat_train_set.copy()

"""# Visualizing Geographical Data"""

housing.plot(kind = "scatter", x = "longitude" , y = "latitude" , grid = True)
plt.show()

housing.plot(kind = "scatter", x = "longitude" , y = "latitude" , grid = True , alpha = 0.2)
plt.show()

housing.plot(kind = "scatter", x = "longitude" , y = "latitude" , grid = True ,
             s = housing["population"]/100 , label ="population",
             c = "median_house_value", cmap = "jet", colorbar = True,
             legend = True , sharex = False , figsize = (10,7))
plt.show()

"""# Look For Correlation"""

corr_matrix = housing.corr()
corr_matrix["median_house_value"].sort_values(ascending = False)

from pandas.plotting import scatter_matrix

attributes = ["median_house_value" , "median_income" , "total_rooms" , "housing_median_age"]
scatter_matrix (housing[attributes] , figsize = (12,8))
plt.show()

housing.plot(kind = "scatter", x = "median_income" , y = "median_house_value" , grid = True , alpha = 0.1)
plt.show()

"""# Experiment with Attribute Combinations"""

housing["rooms_per_house"] = housing["total_rooms"] / housing["households"]
housing["bedrooms_ratio"] = housing["total_bedrooms"] / housing["total_rooms"]
housing["people_per_house"] = housing["population"] / housing["households"]

corr_matrix = housing.corr()
corr_matrix["median_house_value"].sort_values(ascending = False)

""" # prepare the data for Machine Learning algorithms"""

housing = strat_train_set.drop("median_house_value" , axis = 1)
housing_labels = strat_test_set["median_house_value"].copy()

"""# Clean the Data"""

housing.dropna(subset=["total_bedrooms"], inplace =True)   # option 1
housing.drop("total_bedrooms" , axis = 1)                  # option 2
median  = housing["total_bedrooms"].median()               # option 3
housing["total_bedrooms"].fillna(median ,inplace = True)

# used a SimpleImputer


from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy = "median")
housing_num =housing.select_dtypes( include = [np.number])
imputer.fit(housing_num)

imputer.statistics_

housing_num.median().values

x = imputer.transform(housing_num)

housing_tr = pd.DataFrame( x , columns = housing_num.columns,
                          index = housing_num.index)

"""# Handling Text and Categorical Attributes"""

housing_cat = housing[["ocean_proximity"]]
housing_cat.head(8)

from sklearn.preprocessing import OrdinalEncoder

ordinal_encoder = OrdinalEncoder()
housing_cat_encoded = ordinal_encoder.fit_transform(housing_cat)

housing_cat_encoded[:8]

ordinal_encoder.categories_

"""# One Hot Encoder"""

from sklearn.preprocessing import OneHotEncoder

cat_encoder = OneHotEncoder()
housing_cat_1hot = cat_encoder.fit_transform(housing_cat)

housing_cat_1hot

housing_cat_1hot.toarray()

cat_encoder.categories_

df_test_unknown = pd.DataFrame({"ocean_proximity" : ["<2H OCEAN" ,"ISLAND"]})
pd.get_dummies(df_test_unknown)

cat_encoder.handle_unknown ="ignore"
cat_encoder.transform(df_test_unknown)

"""# Feature Scaling and Transformation"""

from sklearn.preprocessing import MinMaxScaler

min_max_scaler = MinMaxScaler(feature_range =(-1,1))
housing_num_min_max_scaled = min_max_scaler.fit_transform(housing_num)

from sklearn.preprocessing import StandardScaler

std_scaler = StandardScaler()
housing_num_std_scaled = std_scaler.fit_transform(housing_num)

# extra code – this cell generates Figure 2–17
fig, axs = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
housing["population"].hist(ax=axs[0], bins=50)
housing["population"].apply(np.log).hist(ax=axs[1], bins=50)
axs[0].set_xlabel("Population")
axs[1].set_xlabel("Log of population")
axs[0].set_ylabel("Number of districts")
plt.show()

from sklearn.metrics.pairwise import rbf_kernel

age_simil_35 = rbf_kernel(housing[["housing_median_age"]], [[35]], gamma = 0.1)

ages = np.linspace(housing["housing_median_age"].min(),
                   housing["housing_median_age"].max(),
                   500).reshape(-1, 1)
gamma1 = 0.1
gamma2 = 0.03
rbf1 = rbf_kernel(ages, [[35]], gamma=gamma1)
rbf2 = rbf_kernel(ages, [[35]], gamma=gamma2)

fig, ax1 = plt.subplots()

ax1.set_xlabel("Housing median age")
ax1.set_ylabel("Number of districts")
ax1.hist(housing["housing_median_age"], bins=50)

ax2 = ax1.twinx()  # create a twin axis that shares the same x-axis
color = "blue"
ax2.plot(ages, rbf1, color=color, label="gamma = 0.10")
ax2.plot(ages, rbf2, color=color, label="gamma = 0.03", linestyle="--")
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylabel("Age similarity", color=color)

plt.legend(loc="upper left")
plt.show()

"""# Custom Transformers"""

from sklearn.preprocessing import FunctionTransformer

log_transformer = FunctionTransformer(np.log, inverse_func=np.exp)
log_pop = log_transformer.transform(housing[["population"]])

rbf_transformer = FunctionTransformer(rbf_kernel,
                                      kw_args=dict(Y=[[35.]], gamma=0.1))
age_simil_35 = rbf_transformer.transform(housing[["housing_median_age"]])

age_simil_35

sf_coords = 37.7749, -122.41
sf_transformer = FunctionTransformer(rbf_kernel,
                                     kw_args=dict(Y=[sf_coords], gamma=0.1))
sf_simil = sf_transformer.transform(housing[["latitude", "longitude"]])

sf_simil

ratio_transformer = FunctionTransformer(lambda X: X[:, [0]] / X[:, [1]])
ratio_transformer.transform(np.array([[1., 2.], [3., 4.]]))

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_array, check_is_fitted

class StandardScalerClone(BaseEstimator, TransformerMixin):
    def __init__(self, with_mean=True):  # no *args or **kwargs!
        self.with_mean = with_mean

    def fit(self, X, y=None):  # y is required even though we don't use it
        X = check_array(X)  # checks that X is an array with finite float values
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0)
        self.n_features_in_ = X.shape[1]  # every estimator stores this in fit()
        return self  # always return self!

    def transform(self, X):
        check_is_fitted(self)  # looks for learned attributes (with trailing _)
        X = check_array(X)
        assert self.n_features_in_ == X.shape[1]
        if self.with_mean:
            X = X - self.mean_
        return X / self.scale_

from sklearn.cluster import KMeans

class ClusterSimilarity(BaseEstimator, TransformerMixin):
    def __init__(self, n_clusters=10, gamma=1.0, random_state=None):
        self.n_clusters = n_clusters
        self.gamma = gamma
        self.random_state = random_state

    def fit(self, X, y=None, sample_weight=None):
        self.kmeans_ = KMeans(self.n_clusters, n_init=10,
                              random_state=self.random_state)
        self.kmeans_.fit(X, sample_weight=sample_weight)
        return self  # always return self!

    def transform(self, X):
        return rbf_kernel(X, self.kmeans_.cluster_centers_, gamma=self.gamma)

    def get_feature_names_out(self, names=None):
        return [f"Cluster {i} similarity" for i in range(self.n_clusters)]

"""# Transfrom Pipelines

"""

from sklearn.pipeline import Pipeline

num_pipeline = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("standardize", StandardScaler()),
])

from sklearn.pipeline import make_pipeline

num_pipeline = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())

housing_num_prepared = num_pipeline.fit_transform(housing_num)
housing_num_prepared[:2].round(2)

df_housing_num_prepared = pd.DataFrame(
    housing_num_prepared, columns=num_pipeline.get_feature_names_out(),
    index=housing_num.index)

df_housing_num_prepared.head(2)

from sklearn.compose import ColumnTransformer

num_attribs = ["longitude", "latitude", "housing_median_age", "total_rooms",
               "total_bedrooms", "population", "households", "median_income"]
cat_attribs = ["ocean_proximity"]

cat_pipeline = make_pipeline(
    SimpleImputer(strategy="most_frequent"),
    OneHotEncoder(handle_unknown="ignore"))

preprocessing = ColumnTransformer([
    ("num", num_pipeline, num_attribs),
    ("cat", cat_pipeline, cat_attribs),
])

from sklearn.compose import make_column_selector, make_column_transformer

preprocessing = make_column_transformer(
    (num_pipeline, make_column_selector(dtype_include=np.number)),
    (cat_pipeline, make_column_selector(dtype_include=object)),
)

housing_prepared = preprocessing.fit_transform(housing)

housing_prepared_fr = pd.DataFrame(
    housing_prepared,
    columns=preprocessing.get_feature_names_out(),
    index=housing.index)
housing_prepared_fr.head(2)