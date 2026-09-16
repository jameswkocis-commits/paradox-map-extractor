import numpy as np
def registration_quality(errors, warning_threshold=8.0):
    errors=np.asarray(errors,float)
    rms=float(np.sqrt(np.mean(errors**2)))
    return {"rms_error":rms,"max_error":float(errors.max()),"poor":rms>warning_threshold}
