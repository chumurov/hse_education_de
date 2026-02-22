#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>

struct Light {
    long long a;
    long long b;
    long long p;
};

static long double min_time_with_speed(long double v, long long D, const std::vector<Light>& lights) {
    if (v <= 0.0L) return 1e100L;

    long double t = 0.0L;
    long long pos = 0;

    for (const auto& L : lights) {
        t += static_cast<long double>(L.p - pos) / v;
        pos = L.p;

        const long double a = static_cast<long double>(L.a);
        const long double cycle = static_cast<long double>(L.a + L.b);

        long double in = std::fmod(t, cycle);
        if (in < 0.0L) in += cycle;

        // Stabilize boundaries of the cycle to avoid treating tiny positive remainders as exact zero.
        const long double eps = 1e-15L * std::max(1.0L, cycle);
        if (in < eps || cycle - in < eps) in = 0.0L;

        // Red interval: (0, a], green interval: {0} U (a, cycle]
        if (in > 0.0L && in <= a) {
            t += (a - in);
        }
    }

    t += static_cast<long double>(D - pos) / v;
    return t;
}

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    long long T, D;
    int N;
    if (!(std::cin >> T >> D >> N)) return 0;

    std::vector<Light> lights;
    lights.reserve(N);

    for (int i = 0; i < N; ++i) {
        Light L{};
        std::cin >> L.a >> L.b >> L.p;
        if (L.p > 0 && L.p < D) lights.push_back(L);
    }

    std::sort(lights.begin(), lights.end(), [](const Light& x, const Light& y) {
        return x.p < y.p;
    });

    auto feasible = [&](long double v) {
        return min_time_with_speed(v, D, lights) <= static_cast<long double>(T);
    };

    // Safe upper bound: if v >= D, travel time without waiting is <= 1 sec,
    // and waiting cannot be removed by infinite speed beyond the phase structure.
    // This bound avoids relying on very large v where modulo arithmetic becomes unstable.
    long double lo = 0.0L;
    long double hi = std::max(1.0L, static_cast<long double>(D));

    if (!feasible(hi)) {
        std::cout << "-1.0";
        return 0;
    }

    for (int it = 0; it < 220; ++it) {
        long double mid = (lo + hi) / 2.0L;
        if (feasible(mid)) {
            hi = mid;
        } else {
            lo = mid;
        }
    }

    std::cout << std::fixed << std::setprecision(15) << hi;
    return 0;
}
