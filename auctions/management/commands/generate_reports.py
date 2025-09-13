"""
Comando de Django para generar reportes automáticos
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from auctions.data_utils import ReportGenerator, AlertSystem
import json
import os


class Command(BaseCommand):
    help = 'Genera reportes automáticos del sistema de subastas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de días para el análisis (default: 30)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='reports',
            help='Directorio de salida para los reportes (default: reports)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv'],
            default='json',
            help='Formato de salida (default: json)'
        )

    def handle(self, *args, **options):
        days = options['days']
        output_dir = options['output_dir']
        output_format = options['format']
        
        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        self.stdout.write(f'Generando reportes para los últimos {days} días...')
        
        # Generar reporte de actividad de usuarios
        self.stdout.write('Generando reporte de actividad de usuarios...')
        user_report = ReportGenerator.generate_user_activity_report(days=days)
        
        # Generar análisis del mercado
        self.stdout.write('Generando análisis del mercado...')
        market_analysis = ReportGenerator.generate_market_analysis(days=days)
        
        # Generar métricas de rendimiento
        self.stdout.write('Generando métricas de rendimiento...')
        performance_metrics = ReportGenerator.generate_performance_metrics(days=days)
        
        # Obtener alertas
        self.stdout.write('Verificando alertas...')
        alerts = AlertSystem.get_all_alerts()
        
        # Consolidar reporte
        report_data = {
            'generated_at': timezone.now().isoformat(),
            'period_days': days,
            'user_activity': user_report,
            'market_analysis': market_analysis,
            'performance_metrics': performance_metrics,
            'alerts': alerts
        }
        
        # Guardar reporte
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format == 'json':
            filename = f'report_{timestamp}.json'
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        elif output_format == 'csv':
            # Generar archivos CSV separados
            import pandas as pd
            
            # Reporte de usuarios
            user_filename = f'user_activity_{timestamp}.csv'
            user_filepath = os.path.join(output_dir, user_filename)
            pd.DataFrame(user_report).to_csv(user_filepath, index=False)
            
            # Análisis del mercado
            market_filename = f'market_analysis_{timestamp}.csv'
            market_filepath = os.path.join(output_dir, market_filename)
            market_df = pd.DataFrame([market_analysis])
            market_df.to_csv(market_filepath, index=False)
            
            # Métricas de rendimiento
            metrics_filename = f'performance_metrics_{timestamp}.csv'
            metrics_filepath = os.path.join(output_dir, metrics_filename)
            pd.DataFrame([performance_metrics]).to_csv(metrics_filepath, index=False)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Reportes generados exitosamente en {output_dir}/'
            )
        )
        
        # Mostrar resumen
        self.stdout.write('\n--- RESUMEN DEL REPORTE ---')
        self.stdout.write(f'Período analizado: {days} días')
        self.stdout.write(f'Usuarios analizados: {len(user_report)}')
        self.stdout.write(f'Subastas totales: {market_analysis["total_listings"]}')
        self.stdout.write(f'Tasa de conversión: {performance_metrics["conversion_rate"]}%')
        self.stdout.write(f'Alertas activas: {len(alerts)}')
        
        if alerts:
            self.stdout.write('\n--- ALERTAS ---')
            for alert in alerts:
                self.stdout.write(f'- {alert["message"]} ({alert["severity"]})')
