

#include "util.h"
#include <math.h>


double double_limit(double x, double min_val, double max_val) {
    if (x < min_val) {
        return min_val;
    } else if (x > max_val) {
        return max_val;
    } else {
        return x;
    }
}


