import os
import sys
from dataclasses import dataclass
from typing import List, Tuple

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object, evaluate_model

from catboost import CatBoostRegressor
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor
# from xgboost import XGBRegressor


@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join("artifacts", "model.pkl")


class ModelTrainer:
    def __init__(self):
        self.mdl_trn_cfg = ModelTrainerConfig()

    def initiate_model_trainer(
        self, ary_train: List[float], ary_test: List[float]
    ) -> Tuple[float, str]:
        """Method that will find best model for inputted data and output the model and its r2_score

        Args:
            ary_train (array): training dataset
            ary_test (array): test dataset

        Raises:
            CustomException: Error if best model r2_score < 60%
            CustomException: Error while training the models

        Returns:
            r2_score (float): Best models r2_score
            model name (str): best models name
        """
        logging.info("Entered model trainer method")
        try:
            logging.info("Splitting train and test datasets")
            X_train, Y_train, X_test, Y_test = (
                ary_train[:, :-1],
                ary_train[:, -1],
                ary_test[:, :-1],
                ary_test[:, -1],
            )

            models = {
                "Random Forest": RandomForestRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Gradient Boosting": GradientBoostingRegressor(),
                "Linear Regression": LinearRegression(),
                "K-Neighbours Regressor": KNeighborsRegressor(),
                # "XGB Regressor": XGBRegressor(),
                "CatBoosting Regressor": CatBoostRegressor(verbose=False),
                "AdaBoost Regressor": AdaBoostRegressor(),
            }

            params = {
                "Decision Tree": {
                    "criterion": [
                        "squared_error",
                        "friedman_mse",
                        "absolute_error",
                        "poisson",
                    ],
                    # 'splitter':['best','random'],
                    # 'max_features':['sqrt','log2'],
                },
                "Random Forest": {
                    # 'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    # 'max_features':['sqrt','log2',None],
                    "n_estimators": [8, 16, 32, 64, 128, 256]
                },
                "Gradient Boosting": {
                    # 'loss':['squared_error', 'huber', 'absolute_error', 'quantile'],
                    "learning_rate": [0.1, 0.01, 0.05, 0.001],
                    "subsample": [0.6, 0.7, 0.75, 0.8, 0.85, 0.9],
                    # 'criterion':['squared_error', 'friedman_mse'],
                    # 'max_features':['auto','sqrt','log2'],
                    "n_estimators": [8, 16, 32, 64, 128, 256],
                },
                "Linear Regression": {},
                "K-Neighbours Regressor": {},
                # "XGB Regressor": {  # },
                #     "learning_rate": [0.1, 0.01, 0.05, 0.001],
                #     "n_estimators": [8, 16, 32, 64, 128, 256],
                # },
                "CatBoosting Regressor": {
                    "depth": [6, 8, 10],
                    "learning_rate": [0.01, 0.05, 0.1],
                    "iterations": [30, 50, 100],
                },
                "AdaBoost Regressor": {
                    "learning_rate": [0.1, 0.01, 0.5, 0.001],
                    # 'loss':['linear','square','exponential'],
                    "n_estimators": [8, 16, 32, 64, 128, 256],
                },
            }

            Model_scores, max_model = evaluate_model(
                X_train=X_train,
                Y_train=Y_train,
                X_test=X_test,
                Y_test=Y_test,
                Models=models,
                param=params,
            )
            best_model = models[list(max_model.keys())[0]]

            if list(max_model.values())[0][1] < 0.6:
                raise CustomException("No best Model found")

            save_object(
                file_path=self.mdl_trn_cfg.trained_model_file_path, obj=best_model
            )
            logging.info("Best trained model saved")

            best_model.fit(X_train, Y_train)
            predicted = best_model.predict(X_test)
            r2_square = r2_score(y_true=Y_test, y_pred=predicted)

            return r2_square, list(max_model.keys())[0]

        except Exception as e:
            logging.info(f"Error in model_trainer.py: {e}")
            raise CustomException(e, sys)
