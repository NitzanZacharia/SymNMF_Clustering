#!/usr/bin/env python3
"""
Run-and-generate test harness for SymNMF project.

- (Re)creates ./tests with random datasets (varied n & d, many shapes)
- Runs & compares:
    1) symnmf.py            (as a script; avoids C-extension import clash)
    2) chat_verifier.py     (Python reference)
    3) ./symnmf CLI         (for goals {sym, ddg, norm} ONLY; NO symnmf goal)
- For symnmf: compares (1) vs (2) for multiple, diverse integer k values (2 <= k < n).
- A CASE FAILS if any required program is missing, errors, times out, or mismatches.
- Saves mismatches to ./tests_mismatches/.
"""

import os
import sys
import math
import shutil
import subprocess
from glob import glob
from pathlib import Path
import stat
import time
import numpy as np

# ================================
# Config
# ================================
TEST_DIR = "./tests"
FAIL_DIR = "./tests_mismatches"
INPUT_EXTS = (".txt", ".csv")
GOALS = ["sym", "ddg", "norm", "symnmf"]
ATOL = 1e-4                # numeric tolerance for comparing floats
TIMEOUT = 90               # seconds per subprocess run (hard stop)
CLI_PATH = "./symnmf"      # only this CLI is required/used

# Dataset generation plan: (name, n_points, dim, generator_fn_name, kwargs)
DATASETS_PLAN = [
    # Tiny / edgeish
    ("tiny2d_5",          5,  2, "gen_uniform_box",       dict(low=-1.0, high=1.0)),
    ("tiny1d_10",        10,  1, "gen_uniform_box",       dict(low=-2.0, high=2.0)),

    # Small-medium clustered Gaussians
    ("gauss2d_3c_60",    60,  2, "gen_gaussian_mixture",  dict(centers=[(-3,-3),(0,0),(3,3)], std=0.6)),
    ("gauss3d_4c_90",    90,  3, "gen_gaussian_mixture",  dict(centers="grid", k=4, spread=6.0, std=0.8)),
    ("gauss5d_5c_150",  150,  5, "gen_gaussian_mixture",  dict(centers="grid", k=5, spread=8.0, std=0.9)),

    # Larger clustered sets
    ("gauss4d_6c_240",  240,  4, "gen_gaussian_mixture",  dict(centers="grid", k=6, spread=10.0, std=0.7)),
    ("gauss8d_5c_300",  300,  8, "gen_gaussian_mixture",  dict(centers="grid", k=5, spread=12.0, std=0.9)),

    # Very high-dim moderate n
    ("gauss20d_80",      80, 20, "gen_gaussian_mixture",  dict(centers="grid", k=3, spread=5.0, std=0.7)),

    # Anisotropic Gaussians
    ("anis_gauss4d_200",200,  4, "gen_anisotropic_gauss", dict(scales=[1.0,2.0,0.5,3.0], k=4, spread=6.0)),

    # Uniform boxes (noise-like)
    ("uniform3d_120",   120,  3, "gen_uniform_box",       dict(low=-1.0, high=2.0)),
    ("uniform6d_180",   180,  6, "gen_uniform_box",       dict(low=0.0,  high=10.0)),

    # Rings / circles (non-convex structure)
    ("rings2d_180",    180,  2, "gen_concentric_rings",   dict(radii=[1.0,2.0,3.5,5.0], jitter=0.08)),

    # Heavy-tailed Laplace
    ("laplace10d_160", 160, 10, "gen_laplace",            dict(loc=0.0, scale=1.0)),

    # Slab (low-rank manifold in higher-dim)
    ("slab5d_200",     200,  5, "gen_slab",               dict(rank=2, width=0.25, span=6.0)),
]

# ================================
# Generators
# ================================
def gen_gaussian_mixture(n, d, *, centers, std=0.7, k=None, spread=5.0):
    rng = np.random.default_rng()
    if centers == "grid":
        if k is None: k = 3
        ctrs = rng.uniform(-spread, spread, size=(k, d))
    else:
        ctrs = np.array(centers, dtype=float).reshape(-1, d); k = ctrs.shape[0]
    counts = np.full(k, n // k, dtype=int); counts[: (n % k)] += 1
    Xs = []
    for i in range(k):
        mean = ctrs[i]
        cov = (std ** 2) * np.eye(d)
        Xs.append(rng.multivariate_normal(mean, cov, size=counts[i]))
    X = np.vstack(Xs); rng.shuffle(X); return X

def gen_anisotropic_gauss(n, d, *, scales, k=3, spread=6.0):
    rng = np.random.default_rng()
    scales = np.array(scales, dtype=float)
    if len(scales) != d:
        if len(scales) < d: scales = np.pad(scales, (0, d-len(scales)), constant_values=scales[-1])
        else:               scales = scales[:d]
    ctrs = rng.uniform(-spread, spread, size=(k, d))
    counts = np.full(k, n // k, dtype=int); counts[: (n % k)] += 1
    cov = np.diag(scales**2)
    Xs = [rng.multivariate_normal(ctrs[i], cov, size=counts[i]) for i in range(k)]
    X = np.vstack(Xs); rng.shuffle(X); return X

def gen_uniform_box(n, d, *, low=0.0, high=1.0):
    rng = np.random.default_rng()
    return rng.uniform(low, high, size=(n, d))

def gen_concentric_rings(n, d, *, radii, jitter=0.05):
    assert d == 2, "rings generator is 2D only"
    rng = np.random.default_rng()
    k = len(radii)
    counts = np.full(k, n // k, dtype=int); counts[: (n % k)] += 1
    Xs = []
    for i, r in enumerate(radii):
        m = counts[i]
        angles = rng.uniform(0, 2*np.pi, size=m)
        base = np.stack([r*np.cos(angles), r*np.sin(angles)], axis=1)
        noise = rng.normal(0.0, jitter, size=base.shape)
        Xs.append(base + noise)
    X = np.vstack(Xs); rng.shuffle(X); return X

def gen_laplace(n, d, *, loc=0.0, scale=1.0):
    rng = np.random.default_rng()
    return rng.laplace(loc=loc, scale=scale, size=(n, d))

def gen_slab(n, d, *, rank=2, width=0.2, span=5.0):
    rng = np.random.default_rng()
    rank = max(1, min(rank, d))
    X = np.zeros((n, d), dtype=float)
    X[:, :rank] = rng.uniform(-span, span, size=(n, rank))
    if d > rank:
        X[:, rank:] = rng.normal(0.0, width, size=(n, d-rank))
    Q, _ = np.linalg.qr(rng.normal(size=(d, d)))
    return X @ Q

# ================================
# IO helpers
# ================================
def ensure_clean_dir(dirpath):
    if os.path.isdir(dirpath):
        for p in glob(os.path.join(dirpath, "*")):
            if os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
            else:
                try: os.remove(p)
                except FileNotFoundError: pass
    else:
        os.makedirs(dirpath, exist_ok=True)

def write_dataset(path, X):
    with open(path, "w", encoding="utf-8") as f:
        for row in X:
            f.write(",".join(f"{float(x):.4f}" for x in row) + "\n")

def discover_inputs():
    return sorted([p for p in glob(os.path.join(TEST_DIR, "*")) if p.lower().endswith(INPUT_EXTS)])

def read_nonempty_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() != ""]

def count_points(path):
    return len(read_nonempty_lines(path))

def count_dims(path):
    # infer dimensionality from first non-empty line
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                return len(ln.split(",")) if "," in ln else 1
    return 1

def parse_numeric_output(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() != ""]
    if not lines: raise ValueError("empty output")
    rows = []
    for ln in lines:
        parts = [p.strip() for p in ln.split(",")] if "," in ln else [ln.strip()]
        parts = [p for p in parts if p != ""]
        rows.append([float(p) for p in parts])
    m = max(len(r) for r in rows)
    if m == 1:
        rows = [[r[0]] for r in rows]
    else:
        for r in rows:
            if len(r) != m:
                raise ValueError("non-rectangular output detected")
    return len(rows), len(rows[0]) if rows else 0, rows

def allclose_2d(a, b, atol=ATOL):
    if len(a) != len(b): return False, ("shape mismatch", (len(a), len(a[0]) if a else 0), (len(b), len(b[0]) if b else 0), None, None, None, None)
    if a and len(a[0]) != len(b[0]): return False, ("shape mismatch", (len(a), len(a[0])), (len(b), len(b[0])), None, None, None, None)
    n = len(a); m = len(a[0]) if n > 0 else 0
    for i in range(n):
        for j in range(m):
            if not (math.isfinite(a[i][j]) and math.isfinite(b[i][j])):
                return False, ("non-finite", (n,m), (n,m), i, j, a[i][j], b[i][j])
            if abs(a[i][j] - b[i][j]) > atol:
                return False, ("value mismatch", (n,m), (n,m), i, j, a[i][j], b[i][j])
    return True, None

def run_cmd(cmd, timeout=TIMEOUT):
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        # Return a special code and captured partial output; mark as timeout
        out = e.stdout or ""
        err = (e.stderr or "") + f"\n<timeout after {timeout}s>"
        return -9, out, err

def pick_cli_binary():
    p = Path(CLI_PATH)
    if p.is_file() and os.access(CLI_PATH, os.X_OK): return CLI_PATH
    if p.is_file():
        try:
            st = os.stat(CLI_PATH)
            os.chmod(CLI_PATH, st.st_mode | stat.S_IEXEC)
            if os.access(CLI_PATH, os.X_OK): return CLI_PATH
        except Exception:
            pass
    return None

# ================================
# k selection (diverse, sane, integer)
# ================================
def _anchors_for_n(n):
    if n < 3: return []
    cands = set()
    for val in [2, 3, n//6, n//4, n//3, n//2, int(math.sqrt(n)), int(math.sqrt(n))+2, n-2]:
        val = int(val)
        if 2 <= val < n: cands.add(val)
    return sorted(cands)

def gen_k_values(n, d, rng=None):
    if n < 3: return []
    if rng is None: rng = np.random.default_rng()

    base_kmax = min(n - 1, max(8, int(math.sqrt(n)) + 8, 14))

    if n <= 15:
        base_kmax = min(base_kmax, max(3, int(round(0.4 * n))))
    if d == 1:
        base_kmax = min(base_kmax, max(3, n//3 + 2, 4), 6)
    base_kmax = max(3, base_kmax)

    candidates = list(range(2, base_kmax + 1))
    if not candidates: return []

    anchors = _anchors_for_n(n)
    if 2 in anchors and len(anchors) > 1 and rng.random() < 0.5:
        anchors.remove(2)

    weights = np.array([1.0 / (k ** 0.7) for k in candidates], dtype=float)
    weights /= weights.sum()

    target = min(8, max(4, n // 60 + 4))   # aim 4..8 ks
    chosen = set()

    rng.shuffle(anchors)
    for a in anchors[: max(1, target // 2)]:
        if 2 <= a < n and a in candidates:
            chosen.add(int(a))

    # 🔧 Add max tries safeguard
    tries = 0
    max_tries = 100
    while len(chosen) < target and tries < max_tries:
        k = int(rng.choice(candidates, p=weights))
        if 2 <= k < n:
            chosen.add(k)
        tries += 1

    ks = sorted({int(k) for k in chosen if 2 <= int(k) < n})
    return ks


# ================================
# Runner
# ================================
def generate_all_datasets():
    print("Generating datasets into ./tests ...")
    ensure_clean_dir(TEST_DIR)
    for name, n, d, fn, kwargs in DATASETS_PLAN:
        if fn == "gen_gaussian_mixture":
            X = gen_gaussian_mixture(n, d, **kwargs)
        elif fn == "gen_anisotropic_gauss":
            X = gen_anisotropic_gauss(n, d, **kwargs)
        elif fn == "gen_uniform_box":
            X = gen_uniform_box(n, d, **kwargs)
        elif fn == "gen_concentric_rings":
            X = gen_concentric_rings(n, d, **kwargs)
        elif fn == "gen_laplace":
            X = gen_laplace(n, d, **kwargs)
        elif fn == "gen_slab":
            X = gen_slab(n, d, **kwargs)
        else:
            raise ValueError(f"Unknown generator {fn}")
        path = os.path.join(TEST_DIR, f"{name}.txt")
        write_dataset(path, X)
        print(f"  wrote {path}   (n={n}, d={d})")
    print("Done generating.\n")

def htag(goal, k):
    return f"k{int(k)}" if (goal == "symnmf" and k is not None) else "kNA"

def save_mismatch(base, goal, k, tag, content):
    os.makedirs(FAIL_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    fname = f"{Path(base).stem}__{goal}__{htag(goal,k)}__{tag}__{stamp}.txt"
    with open(os.path.join(FAIL_DIR, fname), "w", encoding="utf-8") as f:
        f.write(content)

def run_all_tests_over_inputs():
    files = discover_inputs()
    if not files:
        print(f"No input files found in {TEST_DIR!r} with extensions {INPUT_EXTS}")
        sys.exit(2)

    cli_bin = pick_cli_binary()
    if not cli_bin:
        print("ERROR: required CLI binary ./symnmf is missing or not executable. "
              "All sym/ddg/norm cases will be marked FAIL per requirement.\n")
    else:
        print(f"Using CLI binary: {cli_bin}")

    total = 0
    passed = 0
    failures = []

    print(f"Found {len(files)} test files.")

    for fpath in files:
        n = count_points(fpath)
        d = count_dims(fpath)
        ks_candidates = gen_k_values(n, d)

        for goal in GOALS:
            ks_for_goal = ks_candidates if goal == "symnmf" else [None]

            for k in ks_for_goal:
                total += 1

                print(f"[RUN]  {os.path.basename(fpath)} goal={goal} {htag(goal,k)}", flush=True)

                k_for_py = 2 if goal != "symnmf" else (k if k is not None else 2)
                cmd_user = [sys.executable, "symnmf.py", str(int(k_for_py)), goal, fpath]
                rc_u, out_u, err_u = run_cmd(cmd_user)
                if rc_u == -9:
                    failures.append((fpath, goal, k, "user_timeout", rc_u, err_u.strip()))
                    print(f"[FAIL] {os.path.basename(fpath)} goal={goal} {htag(goal,k)}  (your script TIMEOUT)")
                    save_mismatch(fpath, goal, k, "user_stdout", out_u)
                    save_mismatch(fpath, goal, k, "user_stderr", err_u)
                    continue
                if rc_u != 0 or "An Error Has Occurred" in out_u or "An Error Has Occurred" in err_u:
                    failures.append((fpath, goal, k, "user_run_error", rc_u, err_u.strip()))
                    print(f"[FAIL] {os.path.basename(fpath)} goal={goal} {htag(goal,k)}  (your script error)")
                    save_mismatch(fpath, goal, k, "user_stdout", out_u)
                    save_mismatch(fpath, goal, k, "user_stderr", err_u)
                    continue

                k_for_ver = k_for_py
                cmd_ver = [sys.executable, "chat_verifier.py", str(int(k_for_ver)), goal, fpath]
                rc_v, out_v, err_v = run_cmd(cmd_ver)
                if rc_v == -9:
                    failures.append((fpath, goal, k, "verifier_timeout", rc_v, err_v.strip()))
                    print(f"[FAIL] {os.path.basename(fpath)} goal={goal} {htag(goal,k)}  (verifier TIMEOUT)")
                    save_mismatch(fpath, goal, k, "ver_stdout", out_v)
                    save_mismatch(fpath, goal, k, "ver_stderr", err_v)
                    continue
                if rc_v != 0 or "An Error Has Occurred" in out_v or "An Error Has Occurred" in err_v:
                    failures.append((fpath, goal, k, "verifier_run_error", rc_v, err_v.strip()))
                    print(f"[FAIL] {os.path.basename(fpath)} goal={goal} {htag(goal,k)}  (verifier error)")
                    save_mismatch(fpath, goal, k, "ver_stdout", out_v)
                    save_mismatch(fpath, goal, k, "ver_stderr", err_v)
                    continue

                try:
                    _, _, A_user = parse_numeric_output(out_u)
                except Exception as e:
                    failures.append((fpath, goal, k, "parse_user_output", str(e), out_u[:200]))
                    print(f"[FAIL] {os.path.basename(fpath)} goal={goal} {htag(goal,k)}  (parse your output)")
                    save_mismatch(fpath, goal, k, "user_stdout_parsefail", out_u)
                    continue

                try:
                    _, _, A_ver = parse_numeric_output(out_v)
                except Exception as e:
                    failures.append((fpath, goal, k, "parse_ver_output", str(e), out_v[:200]))
                    print(f"[FAIL] {os.path.basename(fpath)} goal={goal} {htag(goal,k)}  (parse verifier output)")
                    save_mismatch(fpath, goal, k, "ver_stdout_parsefail", out_v)
                    continue

                ok_py_vs_ver, info = allclose_2d(A_user, A_ver, atol=ATOL)
                if not ok_py_vs_ver:
                    kind, sha, shb, i, j, au, bv = info
                    msg = f"{kind}; shapes {sha} vs {shb}"
                    if i is not None: msg += f"; first diff at ({i},{j}): yours={au}, ref={bv}"
                    failures.append((fpath, goal, k, "mismatch_py_ver", msg, None))
                    print(f"[FAIL] {os.path.basename(fpath)} goal={goal} {htag(goal,k)}  -> Python vs Verifier: {msg}")
                    save_mismatch(fpath, goal, k, "user_stdout", out_u)
                    save_mismatch(fpath, goal, k, "ver_stdout", out_v)
                    continue

                if goal in {"sym", "ddg", "norm"}:
                    if not cli_bin:
                        failures.append((fpath, goal, k, "cli_missing", "CLI ./symnmf not found"))
                        print(f"[FAIL] {os.path.basename(fpath)} goal={goal}  -> CLI missing (required)")
                        save_mismatch(fpath, goal, k, "py_stdout", out_u)
                        save_mismatch(fpath, goal, k, "ver_stdout", out_v)
                        continue

                    cmd_cli = [cli_bin, goal, fpath]
                    rc_c, out_c, err_c = run_cmd(cmd_cli)
                    if rc_c == -9:
                        failures.append((fpath, goal, k, "cli_timeout", rc_c, err_c.strip()))
                        print(f"[FAIL] {os.path.basename(fpath)} goal={goal}  (CLI TIMEOUT)")
                        save_mismatch(fpath, goal, k, "cli_stdout", out_c)
                        save_mismatch(fpath, goal, k, "cli_stderr", err_c)
                        continue
                    if rc_c != 0:
                        failures.append((fpath, goal, k, "cli_run_error", rc_c, err_c.strip()))
                        print(f"[FAIL] {os.path.basename(fpath)} goal={goal}  (CLI error)")
                        save_mismatch(fpath, goal, k, "cli_stdout", out_c)
                        save_mismatch(fpath, goal, k, "cli_stderr", err_c)
                        continue
                    try:
                        _, _, A_cli = parse_numeric_output(out_c)
                    except Exception as e:
                        failures.append((fpath, goal, k, "parse_cli_output", str(e), out_c[:200]))
                        print(f"[FAIL] {os.path.basename(fpath)} goal={goal}  (parse CLI output)")
                        save_mismatch(fpath, goal, k, "cli_stdout_parsefail", out_c)
                        continue

                    ok_cli_vs_ver, info_cli = allclose_2d(A_cli, A_ver, atol=ATOL)
                    if not ok_cli_vs_ver:
                        kind, sha, shb, i, j, ac, bv = info_cli
                        msg = f"{kind}; shapes {sha} vs {shb}"
                        if i is not None: msg += f"; first diff at ({i},{j}): cli={ac}, ref={bv}"
                        failures.append((fpath, goal, k, "mismatch_cli_ver", msg, None))
                        print(f"[FAIL] {os.path.basename(fpath)} goal={goal}    -> CLI vs Verifier: {msg}")
                        save_mismatch(fpath, goal, k, "cli_stdout", out_c)
                        save_mismatch(fpath, goal, k, "ver_stdout", out_v)
                        continue

                print(f"[OK]   {os.path.basename(fpath)} goal={goal} {htag(goal,k)}", flush=True)
                passed += 1

    print("\n===== SUMMARY =====")
    print(f"Total comparisons: {total}")
    print(f"Passed:            {passed}")
    print(f"Failed:            {total - passed}")
    if failures:
        print("\nFailures detail:")
        for fpath, goal, k, kind, extra, *_ in failures:
            base = os.path.basename(fpath)
            print(f"- {base} goal={goal} {htag(goal,k)}: {kind} :: {extra}")
        print(f"\nMismatched outputs saved under: {FAIL_DIR}")

def main():
    ensure_clean_dir(TEST_DIR)
    ensure_clean_dir(FAIL_DIR)
    print(">>> Generating randomized datasets...")
    generate_all_datasets()
    print(">>> Running tests across all goals and ks...")
    run_all_tests_over_inputs()

if __name__ == "__main__":
    main()