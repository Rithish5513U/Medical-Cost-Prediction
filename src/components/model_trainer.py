import os
import sys
from dataclasses import dataclass

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score
from sklearn.ensemble import AdaBoostRegressor, GradientBoostingRegressor, RandomForestRegressor

from catboost import CatBoostRegressor
from xgboost import XGBRegressor

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object, evaluate_model

@dataclass
class TrainerConfig:
    model_file_path = os.path.join("artifacts", "model.pkl")

class Trainer:
    def __init__(self):
        self.config = TrainerConfig()

    def train(self, train_arr, valid_arr):
        try:
            logging.info("Splitting trainig and test input data")
            X_train, y_train, X_valid, y_valid = (
                train_arr[:,:-1],
                train_arr[:,-1],
                valid_arr[:,:-1],
                valid_arr[:,-1]
            )

            models = {
                "Random Forest": RandomForestRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Gradient Boosting": GradientBoostingRegressor(),
                "Linear Regression": LinearRegression(),
                "AdaBoost Regressor": AdaBoostRegressor(),
                "KNeighbors Regressor": KNeighborsRegressor()
            }
            params={
                "Random Forest":{
                    'n_estimators': [8,16,32,64,128,256]
                },
                "Decision Tree": {
                    'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson']
                },
                "Gradient Boosting":{
                    'learning_rate':[.1,.01,.05,.001],
                    'subsample':[0.6,0.7,0.75,0.8,0.85,0.9],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "Linear Regression":{},
                "AdaBoost Regressor":{
                    'learning_rate':[.1,.01,0.5,.001],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "KNeighbors Regressor":{
                    'n_neighbors': [5,7,9,11]
                }
                
            }

            model_report = evaluate_model(X_train, y_train, X_valid, y_valid, models, params)
            print(model_report)

            max_ = max(zip(model_report.values(), model_report.keys()))

            best_score, best_model = max_[0], models[max_[1]]
            print(best_model, best_score)

            if best_score < 0.8:
                raise CustomException("No best model found")
            
            logging.info("Found best model on training and testing data")

            save_object(
                file_path = self.config.model_file_path,
                obj = best_model
            )

            logging.info("Saved the best model successfully")

            return best_score

        except Exception as e:
            raise CustomException(e, sys)
        

