import os
import re
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit


# ============================================================
# USER SETTINGS
# ============================================================
FILE_PATH = r"C:\Users\glauc\Downloads\RH_NN\data.txt"

# Sampling
SAMPLE_SECONDS = 10.0
SAMPLE_MINUTES = SAMPLE_SECONDS / 60.0

# Extrapolation duration after next trigger
EXTRAPOLATION_HOURS = 2

# Event detection
DROP_THRESHOLD_RH = 1.0
DROP_WINDOW_MIN = 5.0
SMOOTH_WINDOW = 15
MIN_TRIGGER_SPACING_MIN = 5.0
SLOPE_TOL_PER_SAMPLE = 0.005
POST_MIN_SEARCH_MIN = 10.0
PRE_MAX_SEARCH_MIN = 10.0

FIT_IGNORE_INITIAL_MIN = 1.0

# Recovery fit
FIT_START_OFFSET_MIN = 0.0      # start fitting this much after minimum
MIN_FIT_POINTS = 12             # minimum points for fitting
MAX_TAU_MIN = 24 * 60.0         # upper bound for tau in minutes
MAX_EXTRA_RH = 10.0             # RH_inf can be at most this much above observed recovery max

# Plotting
FIGSIZE_MAIN = (18, 7)
FIGSIZE_DET = (18, 6)


# ============================================================
# DATA LOADING
# ============================================================
def load_single_column_rh(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    values = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            line = line.replace(",", ".")
            match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line)
            if match:
                values.append(float(match.group(0)))

    if len(values) < 100:
        raise ValueError(f"Too few numeric samples found: {len(values)}")

    rh = np.array(values, dtype=float)
    time_min = np.arange(len(rh), dtype=float) * SAMPLE_MINUTES
    return time_min, rh


# ============================================================
# HELPERS
# ============================================================
def minutes_to_samples(minutes_value):
    return max(1, int(round(minutes_value / SAMPLE_MINUTES)))


def moving_average(x, window):
    if window <= 1:
        return x.copy()

    kernel = np.ones(window, dtype=float) / window
    x_pad = np.pad(x, (window // 2, window - 1 - window // 2), mode="edge")
    return np.convolve(x_pad, kernel, mode="valid")


def find_local_extrema(rh_s, slope_tol):
    """
    Local maxima:
        derivative changes from positive to negative
    Local minima:
        derivative changes from negative to positive
    """
    d = np.diff(rh_s)

    maxima = []
    minima = []

    for i in range(1, len(d)):
        prev_slope = d[i - 1]
        curr_slope = d[i]

        if prev_slope > slope_tol and curr_slope <= -slope_tol:
            maxima.append(i)

        if prev_slope < -slope_tol and curr_slope >= slope_tol:
            minima.append(i)

    return np.array(maxima, dtype=int), np.array(minima, dtype=int)


def compute_drop_series(rh_s, drop_window_samples):
    drop = np.full(len(rh_s), np.nan, dtype=float)
    for i in range(drop_window_samples, len(rh_s)):
        drop[i] = rh_s[i - drop_window_samples] - rh_s[i]
    return drop


# ============================================================
# UMLUFT DETECTION
# ============================================================
def detect_umluft_events(time_min, rh_raw):
    """
    Event rule:
    - detect a drop >= DROP_THRESHOLD_RH within DROP_WINDOW_MIN
    - define each trigger from the local maximum before that drop
    - define the event minimum as the GLOBAL minimum between two consecutive triggers
    """
    rh_s = moving_average(rh_raw, SMOOTH_WINDOW)

    drop_window_samples = minutes_to_samples(DROP_WINDOW_MIN)
    min_trigger_spacing_samples = minutes_to_samples(MIN_TRIGGER_SPACING_MIN)
    pre_max_search_samples = minutes_to_samples(PRE_MAX_SEARCH_MIN)

    drop = compute_drop_series(rh_s, drop_window_samples)
    maxima, minima = find_local_extrema(rh_s, SLOPE_TOL_PER_SAMPLE)

    # ------------------------------------------------------------
    # Step 1: find trigger candidates
    # ------------------------------------------------------------
    trigger_candidates = []
    i = drop_window_samples
    n = len(rh_s)
    last_drop_idx = -10**9

    while i < n:
        if np.isnan(drop[i]) or drop[i] < DROP_THRESHOLD_RH:
            i += 1
            continue

        run_start = i
        while i + 1 < n and not np.isnan(drop[i + 1]) and drop[i + 1] >= DROP_THRESHOLD_RH:
            i += 1
        run_end = i

        drop_idx = run_start + int(np.argmax(drop[run_start:run_end + 1]))

        if drop_idx - last_drop_idx < min_trigger_spacing_samples:
            i += 1
            continue

        max_candidates = maxima[
            (maxima >= max(0, drop_idx - pre_max_search_samples)) &
            (maxima < drop_idx)
        ]

        if len(max_candidates) == 0:
            left = max(0, drop_idx - pre_max_search_samples)
            trigger_idx = left + int(np.argmax(rh_s[left:drop_idx + 1]))
        else:
            trigger_idx = max_candidates[np.argmax(rh_s[max_candidates])]

        trigger_candidates.append({
            "trigger_idx": int(trigger_idx),
            "drop_idx": int(drop_idx),
            "trigger_min": float(time_min[trigger_idx]),
            "drop_min": float(time_min[drop_idx]),
            "rh_trigger": float(rh_raw[trigger_idx]),
            "rh_drop_point": float(rh_raw[drop_idx]),
            "drop_window_value": float(drop[drop_idx]),
        })

        last_drop_idx = drop_idx
        i = drop_idx + min_trigger_spacing_samples

    # ------------------------------------------------------------
    # Step 2: define the minimum as the GLOBAL minimum between
    # consecutive triggers
    # ------------------------------------------------------------
    events = []

    for k, trig in enumerate(trigger_candidates):
        start_idx = trig["trigger_idx"]

        if k < len(trigger_candidates) - 1:
            next_trigger_idx = trigger_candidates[k + 1]["trigger_idx"]
            right_bound = max(start_idx + 1, next_trigger_idx)
        else:
            next_trigger_idx = None
            right_bound = n - 1

        if right_bound <= start_idx:
            continue

        min_idx = start_idx + int(np.argmin(rh_s[start_idx:right_bound + 1]))

        if min_idx <= start_idx:
            continue

        peak_to_trough_drop = rh_s[start_idx] - rh_s[min_idx]
        if peak_to_trough_drop < DROP_THRESHOLD_RH:
            continue

        events.append({
            "trigger_idx": int(start_idx),
            "drop_idx": int(trig["drop_idx"]),
            "min_idx": int(min_idx),
            "next_trigger_idx": None if next_trigger_idx is None else int(next_trigger_idx),
            "trigger_min": float(time_min[start_idx]),
            "drop_min": float(time_min[trig["drop_idx"]]),
            "min_min": float(time_min[min_idx]),
            "rh_trigger": float(rh_raw[start_idx]),
            "rh_drop_point": float(rh_raw[trig["drop_idx"]]),
            "rh_min": float(rh_raw[min_idx]),
            "drop_window_value": float(trig["drop_window_value"]),
            "peak_to_trough_drop": float(peak_to_trough_drop),
        })

    return events, rh_s, drop, maxima, minima


def build_recovery_fits(time_min, rh, events):
    """
    For event i:
    - fit starts at minimum_i + FIT_IGNORE_INITIAL_MIN
    - fit ends at trigger_(i+1)
    - extrapolation starts at trigger_(i+1)
    - minimum_i is already defined as the GLOBAL minimum between consecutive triggers
    """
    extra_steps = minutes_to_samples(EXTRAPOLATION_HOURS * 60.0)
    ignore_samples = minutes_to_samples(FIT_IGNORE_INITIAL_MIN)

    results = []

    for i, ev in enumerate(events):
        raw_fit_start_idx = ev["min_idx"]
        fit_start_idx = min(raw_fit_start_idx + ignore_samples, len(rh) - 1)

        if i < len(events) - 1:
            next_trigger_idx = events[i + 1]["trigger_idx"]
            fit_end_idx = next_trigger_idx
            extrap_start_idx = next_trigger_idx
        else:
            next_trigger_idx = None
            fit_end_idx = len(rh) - 1
            extrap_start_idx = len(rh) - 1

        if fit_end_idx <= fit_start_idx:
            results.append(None)
            continue

        time_fit = time_min[fit_start_idx:fit_end_idx + 1]
        rh_fit = rh[fit_start_idx:fit_end_idx + 1]

        fit = fit_recovery_segment(time_fit, rh_fit)
        if fit is None:
            results.append(None)
            continue

        forecast_idx = np.arange(extrap_start_idx, extrap_start_idx + extra_steps + 1)
        forecast_time = forecast_idx * SAMPLE_MINUTES
        t_rel_forecast = forecast_time - time_min[fit_start_idx]
        forecast_values = exp_rise_model(
            t_rel_forecast,
            fit["rh_inf"],
            fit["A"],
            fit["tau_min"]
        )

        fitted_time = time_fit
        fitted_values = exp_rise_model(
            time_fit - time_fit[0],
            fit["rh_inf"],
            fit["A"],
            fit["tau_min"]
        )

        results.append({
            "event_index": i,
            "raw_fit_start_idx": raw_fit_start_idx,
            "fit_start_idx": fit_start_idx,
            "fit_end_idx": fit_end_idx,
            "next_trigger_idx": next_trigger_idx,
            "extrap_start_idx": extrap_start_idx,
            "fit_start_min": time_min[fit_start_idx],
            "fit_end_min": time_min[fit_end_idx],
            "extrap_start_min": extrap_start_idx * SAMPLE_MINUTES,
            "fitted_time": fitted_time,
            "fitted_values": fitted_values,
            "forecast_time": forecast_time,
            "forecast_values": forecast_values,
            **fit,
        })

    return results


# ============================================================
# MONOTONIC EXPONENTIAL RECOVERY FIT
# ============================================================
def exp_rise_model(t, rh_inf, A, tau):
    return rh_inf - A * np.exp(-t / tau)


def fit_recovery_segment(time_seg_min, rh_seg):
    """
    Fits RH(t) = RH_inf - A * exp(-t/tau)
    with constraints that encourage monotonic rise:
    - RH_inf >= max(observed)
    - A >= 0
    - tau > 0
    """
    if len(time_seg_min) < MIN_FIT_POINTS:
        return None

    t = np.asarray(time_seg_min, dtype=float)
    y = np.asarray(rh_seg, dtype=float)

    t = t - t[0]

    y0 = float(y[0])
    ymax = float(np.max(y))

    # Initial guesses
    rh_inf_0 = ymax + 0.5
    A_0 = max(0.05, rh_inf_0 - y0)
    tau_0 = max(5.0, 0.25 * (t[-1] - t[0] + 1e-9))

    lower_bounds = [ymax, 0.0, 0.1]
    upper_bounds = [ymax + MAX_EXTRA_RH, max(20.0, ymax - np.min(y) + MAX_EXTRA_RH), MAX_TAU_MIN]

    try:
        popt, _ = curve_fit(
            exp_rise_model,
            t,
            y,
            p0=[rh_inf_0, A_0, tau_0],
            bounds=(lower_bounds, upper_bounds),
            maxfev=20000
        )
    except Exception:
        return None

    rh_inf, A, tau = popt

    y_fit = exp_rise_model(t, rh_inf, A, tau)
    residuals = y - y_fit
    rmse = float(np.sqrt(np.mean(residuals ** 2)))

    return {
        "rh_inf": float(rh_inf),
        "A": float(A),
        "tau_min": float(tau),
        "rmse": rmse,
        "t_fit": t,
        "y_fit": y_fit,
    }


def build_recovery_fits(time_min, rh, events):
    """
    For event i:
    - fit starts at minimum_i + FIT_IGNORE_INITIAL_MIN
    - fit ends at trigger_(i+1) if available
    - extrapolation starts exactly at trigger_(i+1)
    - extrapolation lasts EXTRAPOLATION_HOURS
    - for the last event, fit goes to end of available data and extrapolation starts there
    """
    extra_steps = minutes_to_samples(EXTRAPOLATION_HOURS * 60.0)
    ignore_samples = minutes_to_samples(FIT_IGNORE_INITIAL_MIN)

    results = []

    for i, ev in enumerate(events):
        raw_fit_start_idx = ev["min_idx"]
        fit_start_idx = min(raw_fit_start_idx + ignore_samples, len(rh) - 1)

        if i < len(events) - 1:
            next_trigger_idx = events[i + 1]["trigger_idx"]
            fit_end_idx = next_trigger_idx
            extrap_start_idx = next_trigger_idx
        else:
            next_trigger_idx = None
            fit_end_idx = len(rh) - 1
            extrap_start_idx = len(rh) - 1

        if fit_end_idx <= fit_start_idx:
            results.append(None)
            continue

        time_fit = time_min[fit_start_idx:fit_end_idx + 1]
        rh_fit = rh[fit_start_idx:fit_end_idx + 1]

        fit = fit_recovery_segment(time_fit, rh_fit)
        if fit is None:
            results.append(None)
            continue

        forecast_idx = np.arange(extrap_start_idx, extrap_start_idx + extra_steps + 1)
        forecast_time = forecast_idx * SAMPLE_MINUTES

        # keep the exponential time origin aligned with the fit start
        t_rel_forecast = forecast_time - time_min[fit_start_idx]
        forecast_values = exp_rise_model(
            t_rel_forecast,
            fit["rh_inf"],
            fit["A"],
            fit["tau_min"]
        )

        fitted_time = time_fit
        fitted_values = exp_rise_model(
            time_fit - time_fit[0],
            fit["rh_inf"],
            fit["A"],
            fit["tau_min"]
        )

        results.append({
            "event_index": i,
            "raw_fit_start_idx": raw_fit_start_idx,
            "fit_start_idx": fit_start_idx,
            "fit_end_idx": fit_end_idx,
            "next_trigger_idx": next_trigger_idx,
            "extrap_start_idx": extrap_start_idx,
            "fit_start_min": time_min[fit_start_idx],
            "fit_end_min": time_min[fit_end_idx],
            "extrap_start_min": extrap_start_idx * SAMPLE_MINUTES,
            "fitted_time": fitted_time,
            "fitted_values": fitted_values,
            "forecast_time": forecast_time,
            "forecast_values": forecast_values,
            **fit,
        })

    return results


# ============================================================
# PLOTS
# ============================================================
def plot_detection(time_min, rh_raw, rh_s, events):
    plt.figure(figsize=FIGSIZE_DET)
    plt.plot(time_min, rh_raw, label="RH raw")
    plt.plot(time_min, rh_s, label="RH smoothed")

    for i, ev in enumerate(events):
        plt.axvspan(
            ev["trigger_min"],
            ev["min_min"],
            alpha=0.15,
            label="Detected umluft" if i == 0 else None
        )

        plt.plot(
            ev["trigger_min"],
            ev["rh_trigger"],
            "o",
            markersize=7,
            label="Local maximum before drop" if i == 0 else None
        )

        plt.plot(
            ev["drop_min"],
            ev["rh_drop_point"],
            "s",
            markersize=6,
            label="Strongest drop point" if i == 0 else None
        )

        plt.plot(
            ev["min_min"],
            ev["rh_min"],
            "x",
            markersize=8,
            label="Local minimum after drop" if i == 0 else None
        )

    plt.title("Detected umluft events")
    plt.xlabel("Time [min]")
    plt.ylabel("RH [%]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()


def plot_event_fits(time_min, rh, events, fit_results):
    plt.figure(figsize=FIGSIZE_MAIN)
    plt.plot(time_min, rh, label="Observed RH")

    for i, ev in enumerate(events):
        plt.axvspan(
            ev["trigger_min"],
            ev["min_min"],
            alpha=0.10,
            label="Detected umluft" if i == 0 else None
        )
        plt.plot(
            ev["trigger_min"],
            ev["rh_trigger"],
            "o",
            markersize=6,
            label="Trigger" if i == 0 else None
        )
        plt.plot(
            ev["min_min"],
            ev["rh_min"],
            "x",
            markersize=7,
            label="Minimum" if i == 0 else None
        )

    for i, fit in enumerate(fit_results):
        if fit is None:
            continue

        # fitted curve over measured interval
        plt.plot(
            fit["fitted_time"],
            fit["fitted_values"],
            linewidth=2.0,
            label="Fit on measured recovery" if i == 0 else None
        )

        # extrapolated only after measurement cutoff for that event
        plt.plot(
            fit["forecast_time"],
            fit["forecast_values"],
            linestyle="--",
            linewidth=2.0,
            label="Extrapolation after next trigger" if i == 0 else None
        )

        plt.hlines(
            fit["rh_inf"],
            xmin=fit["forecast_time"][0],
            xmax=fit["forecast_time"][-1],
            linestyles=":",
            linewidth=1.5,
            label="Estimated steady-state RH" if i == 0 else None
        )

    plt.title(
        f"Fit from each minimum to next trigger, extrapolated {EXTRAPOLATION_HOURS:.1f} h beyond"
    )
    plt.xlabel("Time [min]")
    plt.ylabel("RH [%]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

def plot_single_event_diagnostics(time_min, rh, events, fit_results):
    valid = [(ev, fr) for ev, fr in zip(events, fit_results) if fr is not None]
    if not valid:
        return

    n = len(valid)
    cols = 2
    rows = int(np.ceil(n / cols))
    plt.figure(figsize=(14, 4 * rows))

    for idx, (ev, fit) in enumerate(valid, start=1):
        plt.subplot(rows, cols, idx)

        plt.plot(
            fit["fitted_time"] - fit["fitted_time"][0],
            rh[fit["fit_start_idx"]:fit["fit_end_idx"] + 1],
            label="Observed recovery"
        )

        plt.plot(
            fit["fitted_time"] - fit["fitted_time"][0],
            fit["fitted_values"],
            label="Fit on measured recovery"
        )

        plt.plot(
            fit["forecast_time"] - fit["fitted_time"][0],
            fit["forecast_values"],
            linestyle="--",
            label="Extrapolation"
        )

        plt.axhline(fit["rh_inf"], linestyle=":", label="RH_inf")
        plt.title(
            f"Event {fit['event_index']:02d} | RH_inf={fit['rh_inf']:.2f} | tau={fit['tau_min']:.1f} min"
        )
        plt.xlabel("Time since fit start [min]")
        plt.ylabel("RH [%]")
        plt.grid(True)
        plt.legend()

    plt.tight_layout()

# ============================================================
# MAIN
# ============================================================
def main():
    time_min, rh = load_single_column_rh(FILE_PATH)

    print(f"Loaded {len(rh)} valid samples")
    print(f"Sample interval: {SAMPLE_SECONDS:.1f} s")
    print(f"Extrapolation duration after next trigger: {EXTRAPOLATION_HOURS:.1f} h")

    events, rh_s, drop, maxima, minima = detect_umluft_events(time_min, rh)

    print(f"\nDetected umluft events: {len(events)}")
    for i, ev in enumerate(events):
        print(
            f"Event {i:02d} | "
            f"max_before_drop={ev['trigger_min']:.2f} min | "
            f"drop_point={ev['drop_min']:.2f} min | "
            f"min_after_drop={ev['min_min']:.2f} min | "
            f"drop_window={ev['drop_window_value']:.3f} %RH | "
            f"peak_to_trough={ev['peak_to_trough_drop']:.3f} %RH"
        )

    fit_results = build_recovery_fits(time_min, rh, events)

    print("\nRecovery fit summary:")
    for i, fit in enumerate(fit_results):
        if fit is None:
            print(f"Event {i:02d} | fit failed or too few points")
            continue

        print(
            f"Event {i:02d} | "
            f"fit_start={fit['fit_start_min']:.2f} min | "
            f"fit_end={fit['fit_end_min']:.2f} min | "
            f"extrap_start={fit['extrap_start_min']:.2f} min | "
            f"RH_inf={fit['rh_inf']:.3f} | "
            f"tau={fit['tau_min']:.2f} min | "
            f"RMSE={fit['rmse']:.4f}"
        )

    plot_detection(time_min, rh, rh_s, events)
    plot_event_fits(time_min, rh, events, fit_results)
    plot_single_event_diagnostics(time_min, rh, events, fit_results)

    plt.show()


if __name__ == "__main__":
    main()