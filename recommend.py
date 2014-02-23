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


def test_recommender(recommender, test_data):
    """Tests recommender.

    Arguments:
        recommender: Trained instance of 
            MyMediaLite.RatingPrediction.UserItemBaseline.
        test_data: Path to test data with the schema {user_id, beer_id, 
            rating, unix_time}.

    Returns:
        List of tuples (user_id, actual_rating, predicted_rating).

    Side-effect:
        Prints predicted rating versus actual rating for test set.
    """

    result = []
    print("user / actual rating / predicted rating")
    with open(test_data, "r") as f:
        for line in f:
            data = line.split("\t")
            predicted_rating = predict_rating(recommender, int(data[0]), 
                                             int(data[1]))
            # Only include beers for which we have enough info to guess something
            # other than the unconditional expected value.
            if not (round(predicted_rating, 5) == 3.92828):
                result.append((data[0], data[2], predict_rating(recommender, 
                                                               int(data[0]), 
                                                               int(data[1]))))
    result = sorted(result, key=lambda t: (t[0], t[2]), reverse=True)
    
    for t in result:
        print(str(t[0]) + " / " + str(t[1]) + " / " + str(t[2]))
 

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
        if user_id.lower() == "exit":
            break
        beer_id = raw_input("Enter beer_id: ")
        if beer_id.lower() == "exit":
            break
        print("Predicted rating: %s" % predict_rating(recommender, int(user_id), int(beer_id)))

 
if __name__=="__main__":
    
    print("Training recommender ... ")
    recommender = train_recommender(config._TRAIN, config._TEST)

    print("Testing recommender ... ")
    test_recommender(recommender, config._TEST)
    
    print("Starting Beerdora ('exit' to exit) ... ")
    cli_app(recommender)
