#ifndef RUN3_TARGET_CUTS_H
#define RUN3_TARGET_CUTS_H
#include <cmath>

inline bool Run3TargetHtRatio(double ht5,double ht,double maximum=2.) {
  return std::isfinite(ht5) && std::isfinite(ht) && ht5>=0 && ht>0 &&
    std::isfinite(maximum) && maximum>0 && ht5<maximum*ht;
}
inline bool Run3TargetMetConsistency(double met,double mht,double maximum=100.) {
  return std::isfinite(met) && std::isfinite(mht) && met>=0 && mht>=0 &&
    std::isfinite(maximum) && maximum>0 && std::abs(met-mht)<maximum;
}
#endif
