"""
Configuración del Panel de Administración
Variables de entorno y configuraciones personalizables
"""

import os
from django.conf import settings

# Configuración del Panel de Administración
ADMIN_PANEL_CONFIG = {
    'enabled': os.getenv('ADMIN_PANEL_ENABLED', 'True').lower() == 'true',
    'refresh_interval': int(os.getenv('ADMIN_REFRESH_INTERVAL', '30000')),
    'chart_height': int(os.getenv('ADMIN_CHART_HEIGHT', '300')),
    'table_page_size': int(os.getenv('ADMIN_TABLE_PAGE_SIZE', '20')),
    'max_recent_items': int(os.getenv('ADMIN_MAX_RECENT_ITEMS', '10')),
}

# Configuración de Análisis
ANALYTICS_CONFIG = {
    'min_data_points': int(os.getenv('ANALYTICS_MIN_DATA_POINTS', '10')),
    'confidence_thresholds': {
        'high': float(os.getenv('ANALYTICS_CONFIDENCE_HIGH', '0.8')),
        'medium': float(os.getenv('ANALYTICS_CONFIDENCE_MEDIUM', '0.6')),
        'low': float(os.getenv('ANALYTICS_CONFIDENCE_LOW', '0.4')),
    }
}

# Configuración de Alertas
ALERT_CONFIG = {
    'low_activity_threshold': int(os.getenv('ALERT_LOW_ACTIVITY_THRESHOLD', '5')),
    'high_bid_threshold': int(os.getenv('ALERT_HIGH_BID_THRESHOLD', '1000')),
    'suspicious_activity_threshold': int(os.getenv('ALERT_SUSPICIOUS_ACTIVITY_THRESHOLD', '50')),
}

# Configuración de Exportación
EXPORT_CONFIG = {
    'max_records': int(os.getenv('EXPORT_MAX_RECORDS', '10000')),
    'date_format': os.getenv('EXPORT_DATE_FORMAT', '%Y-%m-%d %H:%M:%S'),
    'supported_formats': ['csv', 'xlsx', 'json'],
}

# Configuración de Colores
CHART_COLORS = {
    'primary': os.getenv('CHART_PRIMARY_COLOR', '#667eea'),
    'secondary': os.getenv('CHART_SECONDARY_COLOR', '#764ba2'),
    'success': os.getenv('CHART_SUCCESS_COLOR', '#4facfe'),
    'info': os.getenv('CHART_INFO_COLOR', '#00f2fe'),
    'warning': os.getenv('CHART_WARNING_COLOR', '#f093fb'),
    'danger': os.getenv('CHART_DANGER_COLOR', '#f5576c'),
    'light': os.getenv('CHART_LIGHT_COLOR', '#a8edea'),
    'dark': os.getenv('CHART_DARK_COLOR', '#fed6e3'),
}

# Configuración de Base de Datos para Análisis
DATABASE_CONFIG = {
    'query_timeout': int(os.getenv('DB_QUERY_TIMEOUT', '30')),
    'max_connections': int(os.getenv('DB_MAX_CONNECTIONS', '20')),
    'enable_query_logging': os.getenv('DB_ENABLE_QUERY_LOGGING', 'False').lower() == 'true',
}

# Configuración de Caché
CACHE_CONFIG = {
    'enabled': os.getenv('CACHE_ENABLED', 'True').lower() == 'true',
    'timeout': int(os.getenv('CACHE_TIMEOUT', '300')),  # 5 minutos
    'key_prefix': os.getenv('CACHE_KEY_PREFIX', 'admin_panel'),
}

# Configuración de Logging
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file': os.getenv('LOG_FILE', 'admin_panel.log'),
    'max_size': int(os.getenv('LOG_MAX_SIZE', '10485760')),  # 10MB
    'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5')),
}

def get_config(section):
    """
    Obtener configuración de una sección específica
    """
    configs = {
        'admin_panel': ADMIN_PANEL_CONFIG,
        'analytics': ANALYTICS_CONFIG,
        'alerts': ALERT_CONFIG,
        'export': EXPORT_CONFIG,
        'colors': CHART_COLORS,
        'database': DATABASE_CONFIG,
        'cache': CACHE_CONFIG,
        'logging': LOGGING_CONFIG,
    }
    
    return configs.get(section, {})

def is_feature_enabled(feature):
    """
    Verificar si una funcionalidad está habilitada
    """
    feature_configs = {
        'admin_panel': ADMIN_PANEL_CONFIG['enabled'],
        'analytics': True,
        'alerts': True,
        'export': True,
        'caching': CACHE_CONFIG['enabled'],
        'query_logging': DATABASE_CONFIG['enable_query_logging'],
    }
    
    return feature_configs.get(feature, False)

def get_chart_color(color_name):
    """
    Obtener color para gráficos
    """
    return CHART_COLORS.get(color_name, '#667eea')

def get_alert_threshold(alert_type):
    """
    Obtener umbral para alertas
    """
    return ALERT_CONFIG.get(alert_type, 0)

def get_export_limit():
    """
    Obtener límite de exportación
    """
    return EXPORT_CONFIG['max_records']

def get_refresh_interval():
    """
    Obtener intervalo de actualización
    """
    return ADMIN_PANEL_CONFIG['refresh_interval']
