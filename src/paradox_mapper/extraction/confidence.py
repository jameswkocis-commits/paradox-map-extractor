def observation_confidence(sample_count,dispersion,visible_fraction,min_pixels=9):
    count=min(1.0,sample_count/max(min_pixels,1)); consistency=max(0.0,1.0-dispersion/40.0)
    return float(max(0,min(1,count*consistency*(0.4+0.6*visible_fraction))))
