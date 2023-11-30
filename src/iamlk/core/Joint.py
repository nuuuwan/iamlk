from functools import cached_property

import numpy as np
from sklearn.linear_model import LinearRegression
from utils import Log

log = Log('Joint')


class Joint:
    def __init__(self, X, Y, w):
        self.X = X
        self.Y = Y
        self.w = w

    @staticmethod
    def lr_coefs(X, y, w):
        lr = LinearRegression(fit_intercept=False, positive=True)
        lr.fit(X, y, w)
        return lr.coef_

    @staticmethod
    def jointXY(X, Y, w):
        m_y = len(Y[0])
        j = []
        for i_y in range(m_y):
            y = [y[i_y] for y in Y]
            j.append(Joint.lr_coefs(X, y, w))
        return np.array(j)

    @staticmethod
    def pretty_print(X):
        print('-' * 8)
        for row in X:
            for x in row:
                s = f'{x:.1%}' if x > 0.0005 else '-'
                print(s, end='\t')
            print()
        print('-' * 8)

    @staticmethod
    def normalize_rows(X, Y):
        sumX = X.sum(axis=1)
        sumY = Y.sum(axis=1)
        k = sumY / sumX
        X = X * k[:, np.newaxis]
        return X

    def normalize_all(X):
        sumX = X.sum()
        X = X / sumX
        return X

    def normalize(X, Y):
        EPSILON = 0.1**6
        i = 0
        Z = None
        diff = None

        Joint.pretty_print(X)
        Joint.pretty_print(Y)

        while True:
            i += 1
            X0 = X.copy()
            Y0 = Y.copy()

            Z = (X0 + Y0) / 2
            X = Joint.normalize_rows(X0.T, Z.T).T
            Y = Joint.normalize_rows(Y0, Z)
            X = Joint.normalize_all(X)
            Y = Joint.normalize_all(Y)

            diff = np.sum(np.abs(X - Y))

            if diff < EPSILON:
                break

            if i >= 100:
                break
        log.debug(f'{diff=}, {i=}')
        return Z

    @cached_property
    def joint(self):
        jointXY = Joint.jointXY(self.X, self.Y, self.w)
        jointYX = Joint.jointXY(self.Y, self.X, self.w).T

        joint = Joint.normalize(jointXY, jointYX)
        return joint
