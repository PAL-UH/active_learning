#!/usr/bin/env python3

"""
Support Vector Machine using active learning with UncertaintySampling
Author: Michael M.Meskhi
Project: Domain Adaptation with Active Learning
Date: 2018-03-21
"""

import copy
import os
import numpy as np
import matplotlib.pyplot as plt
try:
    from sklearn.model_selection import train_test_split
except ImportError:
    from sklearn.cross_validation import train_test_split

# libact classes
from libact.base.dataset import Dataset, import_libsvm_sparse
from libact.models import *
from libact.query_strategies import *
from libact.labelers import IdealLabeler


def results(accuracy):
    print("Standard Deviation: " + str(np.std(accuracy)) + "\n" + "Mean Accuracy: " + str(np.mean(accuracy)))

def run(trn_ds, tst_ds, lbr, model, qs, quota):
    E_in, E_out, accuracy = [], [], []

    for _ in range(quota):
        ask_id = qs.make_query()
        X, _ = zip(*trn_ds.data)
        lb = lbr.label(X[ask_id])
        trn_ds.update(ask_id, lb)

        model.train(trn_ds)
        E_in = np.append(E_in, 1 - model.score(trn_ds))
        E_out = np.append(E_out, 1 - model.score(tst_ds))
        accuracy = np.append(accuracy, model.score(tst_ds))

    return E_in, E_out, accuracy


def split_train_test(dataset_filepath, test_size, n_labeled):
    X, y = import_libsvm_sparse(dataset_filepath).format_sklearn()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, shuffle=True)
    trn_ds = Dataset(X_train, np.concatenate([y_train[:n_labeled], [None] * (len(y_train) - n_labeled)]))
    tst_ds = Dataset(X_test, y_test)
    fully_labeled_trn_ds = Dataset(X_train, y_train)

    return trn_ds, tst_ds, y_train, fully_labeled_trn_ds

def main():
    # Path to your libsvm_sparse type classification dataset.
    # If dataset not in libsvm_sparse type use libsvm to convert.
    dataset_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/mars.txt')
    test_size = 0.5    # The percentage of samples in the dataset that will be randomly selected and assigned to the test set.
    n_labeled = 10      # Number of samples that are initially labeled.

    # Load dataset
    trn_ds, tst_ds, y_train, fully_labeled_trn_ds = split_train_test(dataset_filepath, test_size, n_labeled)
    trn_ds2 = copy.deepcopy(trn_ds)
    lbr = IdealLabeler(fully_labeled_trn_ds)

    quota = 200   # Number of samples to query.

    # Model is the base learner, e.g. LogisticRegression, SVM ... etc.
    qs = UncertaintySampling(trn_ds, method='lc', model=SVM())
    model = LogisticRegression()
    E_in_1, E_out_1, accuracy = run(trn_ds, tst_ds, lbr, model, qs, quota)

    # Plot the learning curve of UncertaintySampling.
    # The x-axis is the number of queries, and the y-axis is the corresponding error rate.
    query_num = np.arange(1, quota + 1)
    plt.plot(query_num, E_in_1, 'b', label='qs Ein')
    plt.plot(query_num, E_out_1, 'g', label='qs Eout')
    plt.xlabel('Number of Queries')
    plt.ylabel('Error')
    plt.title('Experiment Result')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.show()

    # Plot the accuracy over requested queries. 
    # The x-axis is the number of queries, and the y-axis is the corresponding accuracy rate.
    plt.plot(query_num, accuracy, 'y', label="accuracy")
    plt.xlabel('Number of Queries')
    plt.ylabel('Accuracy')
    plt.title('SVM + Active Learning')
    plt.legend(loc='upper center', bbox_to_anchor=(0.8, -0.5), fancybox=True, shadow=True, ncol=5)
    plt.savefig('vis/svm.png')
    plt.show()

    results(accuracy)

if __name__ == '__main__':
    main()