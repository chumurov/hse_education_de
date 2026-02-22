#include <iostream>
#include <vector>
#include <queue>

using namespace std;

static const int dx[8] = {-1,-1,-1, 0,0, 1,1,1};
static const int dy[8] = {-1, 0, 1,-1,1,-1,0,1};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;

    vector<vector<bool>> bomb(n, vector<bool>(n, false));
    for (int i = 0; i < k; ++i) {
        int x, y;
        cin >> x >> y;
        --x; --y;
        // Input uses (column, row); internal storage is (row, column).
        bomb[y][x] = true;
    }

    vector<vector<int>> cnt(n, vector<int>(n, 0));
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (bomb[i][j]) continue;
            int c = 0;
            for (int t = 0; t < 8; ++t) {
                int ni = i + dx[t], nj = j + dy[t];
                if (0 <= ni && ni < n && 0 <= nj && nj < n && bomb[ni][nj]) ++c;
            }
            cnt[i][j] = c;
        }
    }

    vector<vector<bool>> open(n, vector<bool>(n, false));

    auto reveal = [&](int sx, int sy) {
        if (open[sx][sy] || bomb[sx][sy]) return;

        if (cnt[sx][sy] != 0) {
            open[sx][sy] = true;
            return;
        }

        queue<pair<int,int>> q;
        open[sx][sy] = true;
        q.push({sx, sy});

        while (!q.empty()) {
            auto [x, y] = q.front();
            q.pop();
            for (int t = 0; t < 8; ++t) {
                int nx = x + dx[t], ny = y + dy[t];
                if (nx < 0 || nx >= n || ny < 0 || ny >= n) continue;
                if (bomb[nx][ny] || open[nx][ny]) continue;

                open[nx][ny] = true;
                if (cnt[nx][ny] == 0) q.push({nx, ny});
            }
        }
    };

    auto print_map = [&]() {
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                if (open[i][j]) cout << cnt[i][j] << ' ';
                else cout << "X ";
            }
            cout << '\n';
        }
    };

    int m;
    cin >> m;

    for (int i = 1; i <= m; ++i) {
        int x, y;
        cin >> x >> y;
        --x; --y;
        int r = y, c = x;

        if (bomb[r][c]) {
            cout << "LOOSE\n";
            return 0;
        }

        reveal(r, c);

        if (i % 5 == 0) print_map();
    }

    print_map();
    return 0;
}
