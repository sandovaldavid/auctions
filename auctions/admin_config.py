"""
Configuración del panel de administración
Configuraciones específicas para el dashboard de BI
"""

# Configuración de colores para gráficos
CHART_COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#4facfe',
    'info': '#00f2fe',
    'warning': '#f093fb',
    'danger': '#f5576c',
    'light': '#a8edea',
    'dark': '#fed6e3'
}

# Configuración de métricas
METRICS_CONFIG = {
    'refresh_interval': 30000,  # 30 segundos
    'chart_height': 300,
    'table_page_size': 20,
    'max_recent_items': 10
}

# Configuración de exportación
EXPORT_CONFIG = {
    'supported_formats': ['csv', 'xlsx'],
    'max_records_per_export': 10000,
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# Configuración de análisis predictivo
PREDICTION_CONFIG = {
    'min_data_points': 10,
    'confidence_thresholds': {
        'high': 0.8,
        'medium': 0.6,
        'low': 0.4
    }
}

# Configuración de alertas
ALERT_CONFIG = {
    'low_activity_threshold': 5,  # días sin actividad
    'high_bid_threshold': 1000,  # pujas muy altas
    'suspicious_activity_threshold': 50  # pujas por usuario por día
}
