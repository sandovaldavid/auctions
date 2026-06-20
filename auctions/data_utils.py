"""
Utilidades para análisis de datos y Business Intelligence
Funciones auxiliares para el dashboard de administración
"""

from datetime import timedelta

import numpy as np
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import Bid, Listing, User


class DataProcessor:
    """
    Clase para procesamiento y análisis de datos
    """

    @staticmethod
    def calculate_growth_rate(current_value, previous_value):
        """
        Calcular tasa de crecimiento entre dos valores
        """
        if previous_value == 0:
            return 0
        return ((current_value - previous_value) / previous_value) * 100

    @staticmethod
    def get_time_periods(days=30):
        """
        Obtener períodos de tiempo para análisis
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        return {"start": start_date, "end": end_date, "days": days}

    @staticmethod
    def calculate_engagement_score(user):
        """
        Calcular score de engagement de un usuario
        """
        listings_count = user.listings.count()
        bids_count = user.bids.count()
        comments_count = user.comments.count()
        watchlist_count = user.watchlist.filter(active=True).count()

        # Peso de cada actividad
        weights = {"listings": 3, "bids": 2, "comments": 1, "watchlist": 1}

        score = (
            listings_count * weights["listings"]
            + bids_count * weights["bids"]
            + comments_count * weights["comments"]
            + watchlist_count * weights["watchlist"]
        )

        return score

    @staticmethod
    def detect_anomalies(data, threshold=2):
        """
        Detectar anomalías en los datos usando desviación estándar
        """
        if len(data) < 3:
            return []

        mean = np.mean(data)
        std = np.std(data)

        anomalies = []
        for i, value in enumerate(data):
            if abs(value - mean) > threshold * std:
                anomalies.append(
                    {"index": i, "value": value, "deviation": abs(value - mean) / std}
                )

        return anomalies

    @staticmethod
    def calculate_market_volatility(listings_data):
        """
        Calcular volatilidad del mercado basada en precios
        """
        if not listings_data:
            return 0

        prices = [
            listing["current_bid"] or listing["starting_bid"]
            for listing in listings_data
        ]
        if len(prices) < 2:
            return 0

        returns = []
        for i in range(1, len(prices)):
            if prices[i - 1] != 0:
                returns.append((prices[i] - prices[i - 1]) / prices[i - 1])

        if not returns:
            return 0

        return np.std(returns) * 100  # Volatilidad como porcentaje


class ReportGenerator:
    """
    Generador de reportes y análisis
    """

    @staticmethod
    def generate_user_activity_report(user_id=None, days=30):
        """
        Generar reporte de actividad de usuarios
        """
        time_period = DataProcessor.get_time_periods(days)

        if user_id:
            users = User.objects.filter(id=user_id)
        else:
            users = User.objects.all()

        report_data = []
        for user in users:
            # Actividad en el período
            listings = user.listings.filter(created__gte=time_period["start"])
            bids = user.bids.filter(listing__created__gte=time_period["start"])
            comments = user.comments.filter(created__gte=time_period["start"])

            # Métricas
            total_activity = listings.count() + bids.count() + comments.count()
            engagement_score = DataProcessor.calculate_engagement_score(user)

            report_data.append(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "listings_created": listings.count(),
                    "bids_made": bids.count(),
                    "comments_made": comments.count(),
                    "total_activity": total_activity,
                    "engagement_score": engagement_score,
                    "last_activity": user.last_login or user.date_joined,
                }
            )

        return sorted(report_data, key=lambda x: x["engagement_score"], reverse=True)

    @staticmethod
    def generate_market_analysis(days=30):
        """
        Generar análisis del mercado
        """
        time_period = DataProcessor.get_time_periods(days)

        # Datos de subastas
        listings = Listing.objects.filter(created__gte=time_period["start"])

        # Métricas básicas
        total_listings = listings.count()
        active_listings = listings.filter(active=True).count()
        closed_listings = listings.filter(active=False).count()

        # Análisis de precios
        price_data = listings.filter(current_bid__isnull=False).values(
            "starting_bid", "current_bid"
        )
        if price_data:
            avg_starting = sum(item["starting_bid"] for item in price_data) / len(
                price_data
            )
            avg_current = sum(item["current_bid"] for item in price_data) / len(
                price_data
            )
            price_increase = (
                ((avg_current - avg_starting) / avg_starting * 100)
                if avg_starting > 0
                else 0
            )
        else:
            avg_starting = avg_current = price_increase = 0

        # Análisis de competencia
        competition_data = listings.annotate(bid_count=Count("bids")).filter(
            bid_count__gt=0
        )

        avg_competition = competition_data.aggregate(avg=Avg("bid_count"))["avg"] or 0

        # Análisis de categorías
        category_analysis = (
            listings.values("category")
            .annotate(count=Count("id"), avg_price=Avg("current_bid"))
            .order_by("-count")
        )

        return {
            "period": f"{days} días",
            "total_listings": total_listings,
            "active_listings": active_listings,
            "closed_listings": closed_listings,
            "avg_starting_price": round(avg_starting, 2),
            "avg_current_price": round(avg_current, 2),
            "price_increase_percent": round(price_increase, 2),
            "avg_competition": round(avg_competition, 2),
            "category_breakdown": list(category_analysis),
            "market_volatility": DataProcessor.calculate_market_volatility(
                list(price_data)
            ),
        }

    @staticmethod
    def generate_performance_metrics(days=30):
        """
        Generar métricas de rendimiento
        """
        time_period = DataProcessor.get_time_periods(days)

        # Métricas de conversión
        total_listings = Listing.objects.filter(
            created__gte=time_period["start"]
        ).count()
        listings_with_bids = (
            Listing.objects.filter(
                created__gte=time_period["start"], bids__isnull=False
            )
            .distinct()
            .count()
        )

        conversion_rate = (
            (listings_with_bids / total_listings * 100) if total_listings > 0 else 0
        )

        # Métricas de engagement
        total_users = User.objects.filter(date_joined__gte=time_period["start"]).count()
        active_users = (
            User.objects.filter(
                Q(listings__created__gte=time_period["start"])
                | Q(bids__listing__created__gte=time_period["start"])
                | Q(comments__created__gte=time_period["start"])
            )
            .distinct()
            .count()
        )

        user_engagement_rate = (
            (active_users / total_users * 100) if total_users > 0 else 0
        )

        # Métricas de retención
        returning_users = (
            User.objects.filter(
                Q(listings__created__gte=time_period["start"])
                | Q(bids__listing__created__gte=time_period["start"])
            )
            .annotate(activity_count=Count("listings") + Count("bids"))
            .filter(activity_count__gt=1)
            .count()
        )

        retention_rate = (
            (returning_users / active_users * 100) if active_users > 0 else 0
        )

        return {
            "conversion_rate": round(conversion_rate, 2),
            "user_engagement_rate": round(user_engagement_rate, 2),
            "retention_rate": round(retention_rate, 2),
            "total_listings": total_listings,
            "active_users": active_users,
            "returning_users": returning_users,
        }


class AlertSystem:
    """
    Sistema de alertas para el dashboard
    """

    @staticmethod
    def check_low_activity_alert():
        """
        Verificar alerta de baja actividad
        """
        threshold_days = 7
        cutoff_date = timezone.now() - timedelta(days=threshold_days)

        recent_listings = Listing.objects.filter(created__gte=cutoff_date).count()
        recent_bids = Bid.objects.filter(listing__created__gte=cutoff_date).count()

        if recent_listings < 5 or recent_bids < 10:
            return {
                "type": "warning",
                "message": f"Baja actividad detectada: {recent_listings} subastas, {recent_bids} pujas en los últimos {threshold_days} días",
                "severity": "medium",
            }

        return None

    @staticmethod
    def check_high_value_alert():
        """
        Verificar alerta de pujas muy altas
        """
        high_value_bids = Bid.objects.filter(amount__gt=10000).count()

        if high_value_bids > 0:
            return {
                "type": "info",
                "message": f"{high_value_bids} pujas de alto valor (>$10,000) detectadas",
                "severity": "low",
            }

        return None

    @staticmethod
    def get_all_alerts():
        """
        Obtener todas las alertas activas
        """
        alerts = []

        low_activity = AlertSystem.check_low_activity_alert()
        if low_activity:
            alerts.append(low_activity)

        high_value = AlertSystem.check_high_value_alert()
        if high_value:
            alerts.append(high_value)

        return alerts
