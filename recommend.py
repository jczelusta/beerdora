#!/usr/bin/env ipy

from __future__ import print_function


import clr
clr.AddReference("MyMediaLite.dll")
clr.AddReference("IronPython.SQLite.dll")

import config
import logging
import MyMediaLite
import sqlite3


def train_recommender(train_data, test_data):
    """Trains the recommendation engine.

    Arguments:
        train_data: Path to training data with the schema {user_id, beer_id, 
            rating, unix_time}.
        test_data: Path to test data with the schema {user_id, beer_id, 
            rating, unix_time}.

    Returns:
        Trained recommender (a trained instance of 
            MyMediaLite.RatingPrediction.UserItemBaseline).
    """

    # Load the data
    train_data = MyMediaLite.IO.RatingData.Read(train_data)
    test_data = MyMediaLite.IO.RatingData.Read(test_data)

    # Train the recommender
    recommender = MyMediaLite.RatingPrediction.UserItemBaseline()
    recommender.Ratings = train_data
    recommender.Train()

    # Measure the accuracy on the test data set
    diagnostics = MyMediaLite.Eval.Ratings.Evaluate(recommender, test_data)
    if diagnostics["RMSE"] > config._MAX_RMSE:
        raise Exception("Root mean squared error is greater than %s " % str(config._MAX_RMSE))
    
    return recommender


def predict_rating(recommender, user_id, beer_id):
    """Predict a user's rating of a specific beer.

    Arguments:
        recommender: Trained instance of 
            MyMediaLite.RatingPrediction.UserItemBaseline.
        user_id: ID of user.
        beer_id: ID of beer.

    Returns:
        Predicted rating (float).
    """
    
    return recommender.Predict(user_id, beer_id)


def cli_app(recommender):
    """CLI app to predict ratings.

    Arguments:
        recommender: Trained instance of 
            MyMediaLite.RatingPrediction.UserItemBaseline.
    
    Returns:
        None.
    """
    
    while True:
        user_id = raw_input("Enter user_id: ")
        beer_id = raw_input("Enter beer_id: ")
        print("Predicted rating: %s" % predict_rating(recommender, int(user_id), int(beer_id)))

 
if __name__=="__main__":
    
    logging.info("Training recommender ... ")
    recommender = train_recommender(config._TRAIN, config._TEST)

    logging.info("Starting Beerdora (ctrl-c to exit) ... ")
    cli_app(recommender)
