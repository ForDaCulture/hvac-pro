import pandas as pd
import sqlite3
from models.database import get_db_connection

class CustomerDataAnalyzer:
    def generate_monthly_report(self):
        """Generate comprehensive monthly business report with raw data for charts."""
        conn = get_db_connection()
        try:
            # Revenue and jobs data
            revenue_query = """
                SELECT strftime('%Y-%m-%d', completed_at) as date,
                       SUM(job_value) as daily_revenue,
                       COUNT(*) as jobs_completed
                FROM jobs
                WHERE completed_at >= date('now', '-30 days')
                AND status = 'completed' AND job_value IS NOT NULL
                GROUP BY 1 ORDER BY 1
            """
            revenue_df = pd.read_sql_query(revenue_query, conn)

            # Service type breakdown data
            service_query = """
                SELECT job_type, COUNT(*) as count
                FROM jobs
                WHERE completed_at >= date('now', '-30 days') AND status = 'completed'
                GROUP BY 1 ORDER BY 2 DESC
            """
            service_df = pd.read_sql_query(service_query, conn)

        finally:
            conn.close()

        # Format data for Chart.js
        chart_data = {
            "revenue_trend": {
                "labels": revenue_df["date"].tolist(),
                "revenue_data": revenue_df["daily_revenue"].tolist(),
                "jobs_data": revenue_df["jobs_completed"].tolist(),
            },
            "service_breakdown": {
                "labels": service_df["job_type"].tolist(),
                "data": service_df["count"].tolist(),
            }
        }
        
        report = {
            'chart_data': chart_data
            # Other stats can be added here as before
        }
        return report

    # Keep other methods like identify_at_risk_customers if they are needed elsewhere
    def identify_at_risk_customers(self):
        """Find customers who have not had a completed service in over 90 days."""
        conn = get_db_connection()
        try:
            query = """
                SELECT c.id, c.name, MAX(j.completed_at) as last_service
                FROM customers c
                LEFT JOIN jobs j ON c.id = j.customer_id AND j.status = 'completed'
                GROUP BY c.id
                HAVING last_service IS NULL OR last_service < date('now', '-90 days')
                ORDER BY last_service ASC
            """
            at_risk_df = pd.read_sql_query(query, conn)
        finally:
            conn.close()
        return at_risk_df.to_dict('records')
