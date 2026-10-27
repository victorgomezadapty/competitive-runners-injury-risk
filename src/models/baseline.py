"""Fixed regularized logistic baselines; all transformations fit training rows only."""
import numpy as np
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from sklearn.utils.validation import check_is_fitted


class TrainingQuantileClipper(TransformerMixin,BaseEstimator):
    def __init__(self,lower=.005,upper=.995):
        self.lower=lower
        self.upper=upper

    def fit(self,X,y=None):
        a=np.asarray(X,dtype=float)
        self.n_features_in_=a.shape[1]
        self.feature_names_in_=np.array(getattr(X,'columns',[f'x{i}' for i in range(a.shape[1])]),dtype=object)
        bounds=[]
        for col in a.T:
            finite=col[np.isfinite(col)]
            bounds.append(np.quantile(finite,[self.lower,self.upper]) if len(finite) else [-np.inf,np.inf])
        self.bounds_=np.asarray(bounds)
        return self

    def transform(self,X):
        check_is_fitted(self,'bounds_')
        a=np.asarray(X,dtype=float)
        if a.shape[1]!=self.n_features_in_:
            raise ValueError('Feature width changed')
        return np.clip(a,self.bounds_[:,0],self.bounds_[:,1])

    def get_feature_names_out(self,input_features=None):
        return self.feature_names_in_ if input_features is None else np.asarray(input_features,dtype=object)


def logistic_pipeline(clipped=True,C=1.0,quantiles=(.005,.995),max_iter=3000):
    steps=[]
    if clipped:
        steps.append(('clip',TrainingQuantileClipper(lower=quantiles[0],upper=quantiles[1])))
    steps.extend([('impute',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),
                  ('scale',RobustScaler()),
                  ('model',LogisticRegression(C=C,solver='lbfgs',max_iter=max_iter))])
    return Pipeline(steps)
