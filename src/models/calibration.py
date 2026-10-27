"""Independent sigmoid calibration without refitting the training estimator."""
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator


def calibrate_frozen(model,X_calibration,y_calibration):
    calibrated=CalibratedClassifierCV(FrozenEstimator(model),method='sigmoid')
    calibrated.fit(X_calibration,y_calibration)
    return calibrated
