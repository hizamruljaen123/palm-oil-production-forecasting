import numpy as np

def double_exponential_smoothing(data, alpha=0.8, beta=0.2, n_preds=36, recursive=False):
    """
    Double Exponential Smoothing (Holt).
    Jika `recursive=True`, setiap prediksi masa depan akan digunakan sebagai observasi
    untuk memperbarui level & trend (iterative forecasting). Jika False, gunakan
    formula analitik F_{t+m} = L_t + m*T_t.
    """
    n = len(data)
    if n < 2:
        raise ValueError("Data minimal harus 2 titik.")

    result = []     # Forecast (F_t)
    smoothed = []   # Level (L_t)
    trend = []      # Trend (T_t)

    # === Inisialisasi otomatis ===
    level = float(data[0])                 # L1
    slope = float(data[1]) - float(data[0])  # T1 = X2 - X1
    smoothed.append(level)
    trend.append(slope)
    result.append(level + slope)  # F1 = L1 + T1

    # Loop data historis
    for i in range(1, n):
        last_level = level
        last_trend = slope

        # Update level & trend
        level = alpha * float(data[i]) + (1 - alpha) * (level + slope)
        slope = beta * (level - last_level) + (1 - beta) * slope

        # Forecast pakai L(t-1)+T(t-1)
        forecast = last_level + last_trend

        smoothed.append(level)
        trend.append(slope)
        result.append(forecast)

    # Prediksi ke depan
    if not recursive:
        # Analitik: F_{t+m} = L_t + m*T_t (level & trend tidak berubah)
        for i in range(1, n_preds + 1):
            future_forecast = level + i * slope
            result.append(future_forecast)
        # Untuk keperluan tampilan, isi smoothed/trend masa depan dengan nilai terakhir
        for i in range(1, n_preds + 1):
            smoothed.append(level)
            trend.append(slope)
    else:
        # Iterative forecasting: gunakan setiap prediksi sebagai "observasi" untuk update
        last_level = level
        last_trend = slope
        for i in range(1, n_preds + 1):
            forecast = last_level + last_trend
            result.append(forecast)

            # Treat forecast as observation and update level/trend
            new_level = alpha * forecast + (1 - alpha) * (last_level + last_trend)
            new_trend = beta * (new_level - last_level) + (1 - beta) * last_trend

            smoothed.append(new_level)
            trend.append(new_trend)

            last_level = new_level
            last_trend = new_trend

    return result, smoothed, trend


def calculate_mape(actual, predicted):
    actual = np.array(actual)
    predicted = np.array(predicted[:len(actual)])

    # Abaikan APE pertama (mulai dari indeks ke-1)
    if len(actual) <= 1:
        return None
    actual = actual[1:]
    predicted = predicted[1:]

    mask = actual != 0
    if not mask.any():
        return None

    mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
    return mape
