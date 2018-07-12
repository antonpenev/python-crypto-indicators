from sklearn.naive_bayes import *
from sklearn import linear_model
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
import random
import sklearn
import numpy as np


class ClassifierHolderBase(object):

    def __init__(self, clf_params):
        self.normalized_data = []
        self.predicted_value_list = []
        self.train_X = []
        self.train_y = []
        self.test_X = []
        self.can_be_fit = True
        self.clf_retrainable = False
        self.train_samples_since_refit = 0

        self.accumulated_samples = 0
        self.train_classes = None
        self.num_train_samples = clf_params["num_train_samples"]
        self.train_sample_size = clf_params["train_sample_size"]
        self.test_sample_size = clf_params["test_sample_size"]
        self.start_idx_offset = clf_params["start_idx_offset"]
        self.refit_on_acc_sample_size = 50
        self.train_data_start_index = 0

    def op_bin_input(self, elem1, elem2):
        return (0 if (elem1 - elem2 >= 0) else 1)

    def op_subtr_input(self, elem1, elem2):
        return round(elem1 - elem2, 4)

    def add_train_x_values(self):
        self.train_X.append(self.normalized_data[-(self.train_sample_size):])

    def add_test_values(self):
        self.test_X = [(self.normalized_data[-(self.train_sample_size):])]
        return self.test_X

    def clear_internal_data(self):
        self.normalized_data = []

    def add_train_y_value(self, val_list):
        raise Exception("The base classifier has not implemented add_train_y_value(). Override in the derived classifier!")

    def can_be_fitted(self):
        return self.can_be_fit

    def get_feature_classes(self):
        return self.train_classes

    def normalize_data(self, vals_to_normalize):
        raise Exception("The base classifier has not implemented normalize_data(). Override in the derived classifier!")

    def enough_min_train_data(self):
        raise Exception("The base classifier has not implemented enough_min_train_data(). Override in the derived classifier!")

    def train_clf(self):
        raise Exception("The base classifier has not implemented train_clf(). Override in the derived classifier!")

    def predict_feature_probability(self):
        raise Exception("The base classifier has not implemented predict_feature_probability(). Override in the derived classifier!")

    def get_actual_next_value(self):
        raise Exception("The base classifier has not implemented get_actual_next_value(). Override in the derived classifier!")


class QDAClf(ClassifierHolderBase):

    def __init__(self, clf_params):
        super().__init__(clf_params)
        self.clf_obj = QuadraticDiscriminantAnalysis()
        self.clf_retrainable = False

    def normalize_data(self, vals_to_normalize):
        for i in range(0, len(vals_to_normalize) - 1):
            self.normalized_data.append(self.op_subtr_input(vals_to_normalize[i], vals_to_normalize[i+1]))

    def train_clf(self):
        self.can_be_fit = False
        self.clf_obj.fit(self.train_X, self.train_y)
        self.train_classes = self.clf_obj.classes_

    def predict_feature_probability(self):
        return self.clf_obj.predict_proba(self.test_X)

    def enough_min_train_data(self):
        return (self.accumulated_samples >= self.num_train_samples)

    def add_train_y_value(self, val_list):
        self.accumulated_samples += 1
        for i in range(0, len(val_list) - 1):
            val = self.op_bin_input(val_list[i], val_list[i + 1])
            self.train_y.append(val)

    def add_new_train_item(self, vals_to_normalize_x, vals_to_normalize_y):
        self.normalize_data(vals_to_normalize_x)
        self.add_train_x_values()
        self.add_train_y_value(vals_to_normalize_y)

    def get_actual_next_value(self):
        return self.train_y[-1]


class RFClf(ClassifierHolderBase):

    def __init__(self, clf_params):
        super().__init__(clf_params)
        self.clf_obj = RandomForestClassifier(warm_start=True)
        self.clf_retrainable = True

    def normalize_data(self, vals_to_normalize):
        for i in range(0, len(vals_to_normalize) - 1):
            self.normalized_data.append(self.op_subtr_input(vals_to_normalize[i], vals_to_normalize[i+1]))

    def train_clf(self):
        self.can_be_fit = False
        X_data = self.train_X[self.train_data_start_index:]
        self.clf_obj.fit(X_data, self.train_y)
        self.train_data_start_index = -self.refit_on_acc_sample_size
        self.train_samples_since_refit = 0
        self.train_classes = self.clf_obj.classes_
        self.train_X = []
        self.train_y = []

    def predict_feature_probability(self):
        return self.clf_obj.predict_proba(self.test_X)

    def enough_min_train_data(self):
        return (self.accumulated_samples >= self.num_train_samples) and (self.accumulated_samples >= self.refit_on_acc_sample_size)

    def add_new_train_item(self, vals_to_normalize_x, vals_to_normalize_y):
        self.normalize_data(vals_to_normalize_x)
        self.add_train_x_values()
        self.add_train_y_value(vals_to_normalize_y)

        if self.train_samples_since_refit == self.refit_on_acc_sample_size:
           self.can_be_fit = True

    def add_train_y_value(self, val_list):
        self.train_samples_since_refit += 1
        self.accumulated_samples += 1
        for i in range(0, len(val_list) - 1):
            val = self.op_bin_input(val_list[i], val_list[i + 1])
            self.train_y.append(val)

    def get_actual_next_value(self):
        return self.train_y[-1]


class BmlIndicator(object):

    successcounter = 0
    counter = 1

    def __init__(self, processor, indicator_params):
        self.clf_cont = None
        self.enough_items = False
        self.initializer_vals = []
        self.predicted_value_list = []
        self.predict_X = None
        self.predict_y = None
        self.unread_new_prediction = False
        # supported classifiers
        self.clf_table = {"QDA" : QDAClf, "RF" : RFClf}

        requested_clf = indicator_params["classifier"]

        num_train_samples = indicator_params["num_train_samples"]
        train_sample_size = indicator_params["train_sample_size"]
        test_sample_size = indicator_params["test_sample_size"]
        start_idx_offset = indicator_params["start_idx_offset"]

        # the indicator acts as a gateway to the requested classifier parameter passing
        clf_params = {"num_train_samples":num_train_samples, "train_sample_size":train_sample_size, "test_sample_size":test_sample_size, "start_idx_offset":start_idx_offset}

        # to skip indexes of the init_vals when training (generally is 0)
        self.start_idx_offset = start_idx_offset
        # this is the number of elements of init_vals at which we will normalize
        self.train_elements_threshold = train_sample_size + 2
        self.predict_threshold = self.train_elements_threshold
        # how many elements in each element of train_x there will be
        self.train_sample_size = train_sample_size
        # how many elements in each element of test_x there will be
        self.test_sample_size = test_sample_size
        self.clear_init_vals_flag = False

        if requested_clf in self.clf_table:
            # classifier object creation
            self.clf_cont = self.clf_table[requested_clf](clf_params)
        else:
            raise Exception("Incorrect classifier has been chosen")

    def clear_init_vals(self):
        self.initializer_vals = []
        self.train_elements_threshold = self.train_sample_size + 2
        self.clf_cont.clear_internal_data()

    def process_new_val(self, value):
        self.initializer_vals.append(value)

        if len(self.initializer_vals) == self.train_elements_threshold:
            self.predict_threshold = self.train_elements_threshold + 1
            self.train_elements_threshold += (self.start_idx_offset + self.train_sample_size)

            vals_to_normalize_x = self.initializer_vals[-(self.train_sample_size + 2):-1]
            vals_to_normalize_y = self.initializer_vals[-2:]

            self.clf_cont.add_new_train_item(vals_to_normalize_x, vals_to_normalize_y)

        if len(self.initializer_vals) == self.predict_threshold:
            if self.clf_cont.enough_min_train_data():
                if self.clf_cont.can_be_fitted():
                    self.clf_cont.train_clf()
                    self.clear_init_vals_flag = True

                vals_to_normalize = self.initializer_vals[-(self.train_sample_size + 2):-1]
                self.clf_cont.normalize_data(vals_to_normalize)

                self.predict_X = self.clf_cont.add_test_values()
                self.predict_y = self.clf_cont.predict_feature_probability()
                val_prob_tuple = self.get_max_prob_data()
                self.predicted_value_list.append(val_prob_tuple)
                self.unread_new_prediction = True

        if self.clear_init_vals_flag is True:
            self.clear_init_vals_flag = False
            self.clear_init_vals()

    def get_max_prob_data(self):
        elem_idx = 0
        max_prob = self.predict_y[0][0]
        for prob in self.predict_y[0]:
            if max_prob < prob:
                elem_idx += 1
                max_prob = prob

        feature_classes = self.clf_cont.get_feature_classes()
        feature_with_max_prob = feature_classes[elem_idx]

        return (feature_with_max_prob, max_prob)

    def update(self, candle):
        value = candle['close']
        self.process_new_val(value)

    def get_expected_value(self):
        ret_val = None
        if len(self.predicted_value_list) > 0 and self.unread_new_prediction is True:
            self.unread_new_prediction = False
            ret_val = self.predicted_value_list[-1]
            # clear last values as to not let this list grow too big
            if len(self.predicted_value_list) > 10:
                self.predicted_value_list = []
        return ret_val

    def has_enough_data(self):
        return len(self.initializer_vals) > 0

