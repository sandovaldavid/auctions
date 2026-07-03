"""
Módulo de análisis de datos para el dashboard de Business Intelligence
Implementa métodos de data science para análisis de subastas
"""

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import ExtractMonth, TruncDate, TruncMonth
from django.utils import timezone
from plotly.offline import plot
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from .models import Bid, Comment, Listing, Watchlist

User = get_user_model()


class AuctionAnalytics:
    """
    Clase principal para análisis de datos de subastas
    Implementa métodos de data science para insights de negocio
    """

    def __init__(self):
        self.timezone = timezone.now()

    def get_basic_metrics(self):
        """
        Métricas básicas del sistema de subastas
        """
        total_listings = Listing.objects.count()
        active_listings = Listing.objects.filter(active=True).count()
        total_users = User.objects.count()
        total_bids = Bid.objects.count()
        total_comments = Comment.objects.count()
        total_watchlist_items = Watchlist.objects.filter(active=True).count()

        # Calcular valor total de subastas
        total_auction_value = (
            Listing.objects.aggregate(total_value=Sum("current_bid"))["total_value"]
            or 0
        )

        # Calcular valor promedio de subastas
        avg_auction_value = (
            Listing.objects.filter(current_bid__isnull=False).aggregate(
                avg_value=Avg("current_bid")
            )["avg_value"]
            or 0
        )

        return {
            "total_listings": total_listings,
            "active_listings": active_listings,
            "total_users": total_users,
            "total_bids": total_bids,
            "total_comments": total_comments,
            "total_watchlist_items": total_watchlist_items,
            "total_auction_value": float(total_auction_value),
            "avg_auction_value": float(avg_auction_value),
            "conversion_rate": (
                (total_bids / total_listings * 100) if total_listings > 0 else 0
            ),
        }

    def get_time_series_data(self, days=30):
        """
        Datos de series temporales para análisis de tendencias
        """
        end_date = self.timezone
        start_date = end_date - timedelta(days=days)

        # Listings por día
        listings_by_day = (
            Listing.objects.filter(created__gte=start_date)
            .annotate(day=TruncDate("created"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        # Bids por día
        bids_by_day = (
            Bid.objects.filter(listing__created__gte=start_date)
            .annotate(day=TruncDate("listing__created"))
            .values("day")
            .annotate(count=Count("id"), total_amount=Sum("amount"))
            .order_by("day")
        )

        # Usuarios registrados por día
        users_by_day = (
            User.objects.filter(date_joined__gte=start_date)
            .annotate(day=TruncDate("date_joined"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        def _serialize_by_day(rows):
            return [{**row, "day": row["day"].isoformat()} for row in rows]

        return {
            "listings": _serialize_by_day(listings_by_day),
            "bids": _serialize_by_day(bids_by_day),
            "users": _serialize_by_day(users_by_day),
        }

    def get_category_analysis(self):
        """
        Análisis por categorías de subastas
        """
        category_data = (
            Listing.objects.values("category")
            .annotate(
                count=Count("id"),
                avg_starting_bid=Avg("starting_bid"),
                avg_current_bid=Avg("current_bid"),
                total_bids=Count("bids"),
                avg_bids_per_listing=Count("bids") / Count("id"),
            )
            .order_by("-count")
        )

        return list(category_data)

    def get_user_behavior_analysis(self):
        """
        Análisis del comportamiento de usuarios
        """
        # Top usuarios por actividad
        top_bidders = User.objects.annotate(
            bid_count=Count("bids"),
            total_bid_amount=Sum("bids__amount"),
            listings_created=Count("listings"),
            comments_made=Count("comments"),
        ).order_by("-bid_count")[:10]

        # Análisis de engagement
        user_engagement = (
            User.objects.annotate(
                total_activity=Count("bids") + Count("listings") + Count("comments"),
                watchlist_items=Count("watchlist", filter=Q(watchlist__active=True)),
            )
            .filter(total_activity__gt=0)
            .order_by("-total_activity")
        )

        return {
            "top_bidders": list(top_bidders.values()),
            "user_engagement": list(user_engagement.values()),
        }

    def get_bid_analysis(self):
        """
        Análisis detallado de pujas
        """
        # Distribución de pujas por rango de valores
        bid_ranges = [
            (0, 50, "0-50"),
            (50, 100, "50-100"),
            (100, 500, "100-500"),
            (500, 1000, "500-1000"),
            (1000, float("inf"), "1000+"),
        ]

        bid_distribution = []
        for min_val, max_val, label in bid_ranges:
            if max_val == float("inf"):
                count = Bid.objects.filter(amount__gte=min_val).count()
            else:
                count = Bid.objects.filter(
                    amount__gte=min_val, amount__lt=max_val
                ).count()
            bid_distribution.append({"range": label, "count": count})

        # Análisis de competencia por listing
        listing_competition = (
            Listing.objects.annotate(
                bid_count=Count("bids"),
                bid_increase=(
                    (F("current_bid") - F("starting_bid")) / F("starting_bid") * 100
                ),
            )
            .filter(bid_count__gt=0)
            .order_by("-bid_count")
        )

        return {
            "bid_distribution": bid_distribution,
            "listing_competition": list(listing_competition.values()),
        }

    def predict_auction_success(self, listing_id):
        """
        Predicción de éxito de una subasta usando machine learning
        """
        try:
            # Obtener datos históricos para entrenar el modelo
            historical_data = (
                Listing.objects.filter(current_bid__isnull=False)
                .annotate(
                    bid_count=Count("bids"),
                    days_active=(self.timezone - F("created")).days,
                    price_increase=(
                        (F("current_bid") - F("starting_bid")) / F("starting_bid") * 100
                    ),
                )
                .values("starting_bid", "bid_count", "days_active", "price_increase")
            )

            if len(historical_data) < 10:
                return {"error": "Datos insuficientes para predicción"}

            # Preparar datos para el modelo
            df = pd.DataFrame(historical_data)
            X = df[["starting_bid", "bid_count", "days_active"]]  # noqa: N806
            y = df["price_increase"]

            # Entrenar modelo
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)  # noqa: N806

            model = LinearRegression()
            model.fit(X_scaled, y)

            # Obtener datos de la subasta actual
            listing = Listing.objects.get(id=listing_id)
            current_bid_count = listing.bids.count()
            days_active = (self.timezone - listing.created).days

            # Hacer predicción
            prediction_data = np.array(
                [[float(listing.starting_bid), current_bid_count, days_active]]
            )
            prediction_scaled = scaler.transform(prediction_data)
            predicted_increase = model.predict(prediction_scaled)[0]

            return {
                "predicted_price_increase": float(predicted_increase),
                "confidence": "medium",  # Simplificado para este ejemplo
                "recommendations": self._get_recommendations(
                    predicted_increase, current_bid_count
                ),
            }

        except Exception as e:
            return {"error": f"Error en predicción: {str(e)}"}

    def _get_recommendations(self, price_increase, bid_count):
        """
        Generar recomendaciones basadas en el análisis
        """
        recommendations = []

        if price_increase < 10:
            recommendations.append("Considera ajustar el precio inicial")
        elif price_increase > 100:
            recommendations.append(
                "Excelente rendimiento, considera estrategias similares"
            )

        if bid_count < 3:
            recommendations.append(
                "Promociona más la subasta para aumentar participación"
            )
        elif bid_count > 10:
            recommendations.append("Alta competencia, considera extender el tiempo")

        return recommendations

    def get_market_trends(self):
        """
        Análisis de tendencias del mercado
        """
        # Análisis mensual
        monthly_data = (
            Listing.objects.annotate(month=TruncMonth("created"))
            .values("month")
            .annotate(
                listings_count=Count("id"),
                avg_starting_bid=Avg("starting_bid"),
                avg_current_bid=Avg("current_bid"),
                total_bids=Count("bids"),
            )
            .order_by("month")
        )

        # Análisis de estacionalidad
        seasonal_data = (
            Listing.objects.annotate(month=ExtractMonth("created"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        return {
            "monthly_trends": [
                {**row, "month": row["month"].strftime("%Y-%m")} for row in monthly_data
            ],
            "seasonal_patterns": [
                {**row, "month": f"{row['month']:02d}"} for row in seasonal_data
            ],
        }

    def generate_plotly_charts(self):
        """
        Generar gráficos interactivos con Plotly
        """
        charts = {}

        # 1. Gráfico de líneas - Tendencias temporales
        time_data = self.get_time_series_data(30)
        if time_data["listings"]:
            fig_trends = go.Figure()
            fig_trends.add_trace(
                go.Scatter(
                    x=[item["day"] for item in time_data["listings"]],
                    y=[item["count"] for item in time_data["listings"]],
                    mode="lines+markers",
                    name="Listings",
                    line={"color": "#007bff"},
                )
            )
            fig_trends.add_trace(
                go.Scatter(
                    x=[item["day"] for item in time_data["bids"]],
                    y=[item["count"] for item in time_data["bids"]],
                    mode="lines+markers",
                    name="Bids",
                    line={"color": "#28a745"},
                )
            )
            fig_trends.update_layout(
                title="Tendencias de Actividad (30 días)",
                xaxis_title="Fecha",
                yaxis_title="Cantidad",
                template="plotly_white",
            )
            charts["trends"] = plot(
                fig_trends, output_type="div", include_plotlyjs=False
            )

        # 2. Gráfico de barras - Categorías
        category_data = self.get_category_analysis()
        if category_data:
            fig_categories = px.bar(
                x=[item["category"] or "Sin categoría" for item in category_data],
                y=[item["count"] for item in category_data],
                title="Listings por Categoría",
                labels={"x": "Categoría", "y": "Cantidad"},
            )
            charts["categories"] = plot(
                fig_categories, output_type="div", include_plotlyjs=False
            )

        # 3. Gráfico de dispersión - Precio vs Pujas
        listing_data = (
            Listing.objects.filter(current_bid__isnull=False)
            .annotate(bid_count=Count("bids"))
            .values("starting_bid", "current_bid", "bid_count")
        )

        if listing_data:
            df = pd.DataFrame(list(listing_data))
            fig_scatter = px.scatter(
                df,
                x="starting_bid",
                y="current_bid",
                size="bid_count",
                title="Precio Inicial vs Precio Actual",
                labels={
                    "starting_bid": "Precio Inicial",
                    "current_bid": "Precio Actual",
                },
                hover_data=["bid_count"],
            )
            charts["price_analysis"] = plot(
                fig_scatter, output_type="div", include_plotlyjs=False
            )

        return charts

    def get_kpi_dashboard_data(self):
        """
        Datos consolidados para el dashboard principal
        """
        metrics = self.get_basic_metrics()
        time_data = self.get_time_series_data(7)  # Últimos 7 días
        category_data = self.get_category_analysis()

        # Calcular métricas de crecimiento
        current_week_listings = sum(item["count"] for item in time_data["listings"])
        previous_week = self.timezone - timedelta(days=14)
        previous_week_data = Listing.objects.filter(
            created__gte=previous_week, created__lt=self.timezone - timedelta(days=7)
        ).count()

        growth_rate = (
            ((current_week_listings - previous_week_data) / previous_week_data * 100)
            if previous_week_data > 0
            else 0
        )

        return {
            "metrics": metrics,
            "growth_rate": growth_rate,
            "top_categories": category_data[:5],
            "recent_activity": time_data,
            "charts": self.generate_plotly_charts(),
        }
