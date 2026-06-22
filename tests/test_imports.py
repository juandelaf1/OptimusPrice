import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor


def test_imports():
    assert pd is not None
    assert np is not None
    assert RandomForestRegressor is not None


def test_data_processing_imports():
    from optimus_price.data_processing import load_and_clean_data, prepare_features

    assert callable(load_and_clean_data)
    assert callable(prepare_features)


def test_training_imports():
    from optimus_price.training import train_and_save_model

    assert callable(train_and_save_model)
