from app.schemas.common import AppBaseModel, TimeSeriesPoint


class ReportSummary(AppBaseModel):
    daily_liters_sold: list[TimeSeriesPoint]
    daily_revenue: list[TimeSeriesPoint]
    pump_comparison: list[dict]
    station_ranking: list[dict]
    anomaly_trends: list[TimeSeriesPoint]
    attendant_productivity: list[dict]

