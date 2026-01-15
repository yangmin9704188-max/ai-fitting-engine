import time
import statistics
import torch

def _sync_if_cuda(device):
    if device is not None and str(device).startswith("cuda") and torch.cuda.is_available():
        torch.cuda.synchronize(device=device)

class BenchResult:
    def __init__(self, name, times_ms):
        self.name = name
        self.times_ms = times_ms

    def summary(self):
        t = sorted(self.times_ms)
        n = len(t)

        def pct(p):
            if n == 0:
                return float("nan")
            k = int(round((p / 100.0) * (n - 1)))
            k = max(0, min(n - 1, k))
            return t[k]

        return {
            "name": self.name,
            "n": n,
            "mean_ms": statistics.mean(t) if n else float("nan"),
            "p50_ms": pct(50),
            "p95_ms": pct(95),
            "min_ms": t[0] if n else float("nan"),
            "max_ms": t[-1] if n else float("nan"),
        }

class BenchTimer:
    def __init__(self, device=None):
        self.device = device

    def run(self, name, fn, warmup=10, repeat=50):
        # warmup: 캐시/커널 예열
        for _ in range(max(0, warmup)):
            _sync_if_cuda(self.device)
            fn()
            _sync_if_cuda(self.device)

        # measure
        times = []
        for _ in range(max(1, repeat)):
            _sync_if_cuda(self.device)
            t0 = time.perf_counter()
            fn()
            _sync_if_cuda(self.device)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)

        return BenchResult(name, times)

def print_bench(results):
    header = f"{'Name':30s} {'n':>4s} {'mean':>9s} {'p50':>9s} {'p95':>9s} {'min':>9s} {'max':>9s}"
    print(header)
    print("-" * len(header))
    for r in results:
        s = r.summary()
        print(
            f"{s['name'][:30]:30s} {s['n']:4d} "
            f"{s['mean_ms']:9.3f} {s['p50_ms']:9.3f} {s['p95_ms']:9.3f} "
            f"{s['min_ms']:9.3f} {s['max_ms']:9.3f}"
        )
