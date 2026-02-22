#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <algorithm>
#include <cstdint>

using namespace std;

static inline uint64_t pack_perm(const vector<int>& p) {

    uint64_t x = 0;
    for (size_t i = 0; i < p.size(); ++i) {
        x |= (uint64_t)(p[i] & 15) << (4 * i);
    }
    return x;
}

static inline vector<int> unpack_perm(uint64_t x, int n) {
    vector<int> p(n);
    for (int i = 0; i < n; ++i) p[i] = (int)((x >> (4 * i)) & 15);
    return p;
}

static inline bool is_goal_cycle(const vector<int>& p) {
    int n = (int)p.size();
    int pos1 = -1;
    for (int i = 0; i < n; ++i) if (p[i] == 1) { pos1 = i; break; }
    for (int t = 0; t < n; ++t) {
        if (p[(pos1 + t) % n] != t + 1) return false;
    }
    return true;
}

static inline bool can_swap(int a, int b) {
    return std::abs(a - b) > 1;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    vector<int> p(N);
    for (int i = 0; i < N; ++i) cin >> p[i];

    vector<pair<int,int>> ops;
    ops.reserve(50000);

    auto do_swap_adj = [&](int i) {

        int j = (i + 1) % N;
        ops.push_back({p[i], p[j]});
        std::swap(p[i], p[j]);
    };


    if (N <= 11) {
        uint64_t start = pack_perm(p);
        queue<uint64_t> q;
        unordered_map<uint64_t, pair<uint64_t,int>> prev; // state -> (parent, moveIndex)
        prev.reserve(5000000);

        q.push(start);
        prev[start] = {0ULL, -1};

        uint64_t goal = 0ULL;
        bool found = false;

        while (!q.empty() && !found) {
            uint64_t cur = q.front(); q.pop();
            auto perm = unpack_perm(cur, N);

            if (is_goal_cycle(perm)) {
                goal = cur;
                found = true;
                break;
            }

            for (int i = 0; i < N; ++i) {
                int j = (i + 1) % N;
                if (!can_swap(perm[i], perm[j])) continue;
                auto nxt = perm;
                std::swap(nxt[i], nxt[j]);
                uint64_t key = pack_perm(nxt);
                if (!prev.count(key)) {
                    prev[key] = {cur, i};
                    q.push(key);
                }
            }
        }

        if (!found) {
            cout << -1;
            return 0;
        }

    
        vector<int> moves;
        for (uint64_t s = goal; s != start; ) {
            auto it = prev.find(s);
            moves.push_back(it->second.second);
            s = it->second.first;
        }
        reverse(moves.begin(), moves.end());


        for (int idx : moves) {
            int j = (idx + 1) % N;
            if (!can_swap(p[idx], p[j])) { cout << -1; return 0; }
            cout << p[idx] << ' ' << p[j] << "\n";
            std::swap(p[idx], p[j]);
        }
        cout << 0;
        return 0;
    }

    auto index_of = [&](int val) {
        for (int i = 0; i < N; ++i) if (p[i] == val) return i;
        return -1;
    };

    auto rotate_to_make1_first = [&]() {
        int pos1 = index_of(1);
        if (pos1 == 0) return;

        vector<int> q(N);
        for (int i = 0; i < N; ++i) q[i] = p[(pos1 + i) % N];
        p.swap(q);
    };


    auto bubble_left = [&](int i) -> bool {
        if (i == 0) return true;
        if (!can_swap(p[i-1], p[i])) return false;
        do_swap_adj(i-1);
        return true;
    };

 
    auto bubble_right = [&](int i) -> bool {
        int j = (i + 1) % N;
        if (!can_swap(p[i], p[j])) return false;
        do_swap_adj(i);
        return true;
    };

   
    auto fix_with_buffer = [&](int pos) -> bool {
    
        int a = p[pos-1], b = p[pos];
        int B = N;
        if (!can_swap(B, a) || !can_swap(B, b)) B = N-2;
        if (B < 1) return false;
        if (!can_swap(B, a) || !can_swap(B, b)) return false;

        int ib = index_of(B);
        if (ib == -1) return false;


        int target = (pos + 1) % N;

     
        for (int step = 0; step < 3 * N; ++step) {
            if (ib == target) break;
       
            int distR = (target - ib + N) % N;
            int distL = (ib - target + N) % N;
            if (distR <= distL) {
               
                if (!bubble_right(ib)) return false;
                ib = (ib + 1) % N;
            } else {
            
                int il = (ib - 1 + N) % N;
                if (!can_swap(p[il], p[ib])) return false;
                do_swap_adj(il);
                ib = il;
            }
        }
        if (ib != target) return false;

   
        int i1 = pos;              // b with B at pos,pos+1
        if (!can_swap(p[i1], p[(i1+1)%N])) return false;
        do_swap_adj(i1);

        int i2 = pos - 1;
        if (i2 < 0) i2 += N;
        if (!can_swap(p[i2], p[(i2+1)%N])) return false;
        do_swap_adj(i2);

        int i3 = pos;
        if (!can_swap(p[i3], p[(i3+1)%N])) return false;
        do_swap_adj(i3);

        return true;
    };

  
    rotate_to_make1_first();

    
    bool ok = false;
    for (int pass = 0; pass < 5 && (int)ops.size() <= 50000; ++pass) {
        for (int i = 1; i < N; ++i) {
    
            while (i > 0 && p[i] < p[i-1]) {
                if (can_swap(p[i-1], p[i])) {
                    do_swap_adj(i-1);
                    --i;
                } else {
               
                    if (!fix_with_buffer(i)) break;
                    --i;
                }
                if ((int)ops.size() > 50000) break;
            }
            if ((int)ops.size() > 50000) break;
        }
        if (is_goal_cycle(p)) { ok = true; break; }
    }

    if (!ok || (int)ops.size() > 50000) {
        cout << -1;
        return 0;
    }

    for (auto [x,y] : ops) {
        cout << x << ' ' << y << "\n";
    }
    cout << 0;
    return 0;
}
