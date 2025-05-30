# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import timedelta
import psutil
from odoo import models, fields, api


class DatabaseMetrics(models.Model):
    _name = 'database.metrics'
    _description = 'Database Metrics'

    @api.model
    def collect_metrics(self):
        """collect database metrics"""

        cur = self.env.cr
        active_db = cur.dbname
        # Get total connections
        cur.execute("SELECT count(*) FROM pg_stat_activity;")
        total_connections = cur.fetchone()[0]

        # Get database size
        cur.execute("""
            SELECT pg_database_size(current_database()) / 1024.0 / 1024.0;
              """)
        db_size_mb = round(cur.fetchone()[0], 2)

        # Get cache hit ratio
        cur.execute("""
                  SELECT
                  sum(heap_blks_hit) / (sum(heap_blks_hit) +
                  sum(heap_blks_read)) * 100
                  FROM pg_statio_user_tables;
              """)
        cache_hit_ratio = round(cur.fetchone()[0], 2)

        # Get deadlocks
        cur.execute("""
                  SELECT deadlocks
                  FROM pg_stat_database
                  WHERE datname = current_database();
              """)
        deadlocks = cur.fetchone()[0]

        # Get long running queries (>5 minutes)
        cur.execute("""
                  SELECT COUNT(*)
                  FROM pg_stat_activity
                  WHERE state = 'active'
                  AND now() - query_start > interval '5 minutes';
              """)
        long_running_queries = cur.fetchone()[0]

        cur.execute("SELECT pg_backend_pid();")
        pg_pid = cur.fetchone()[0]

        # Get max_connections setting
        cur.execute("SHOW max_connections;")
        max_connections = int(cur.fetchone()[0])

        # Get current connection counts by state
        cur.execute("""
                    SELECT state, COUNT(*)
                    FROM pg_stat_activity
                    GROUP BY state;
                """)
        state_counts = dict(cur.fetchall())
        total_current = sum(state_counts.values())
        connection_utilization = round(((total_current / max_connections) * 100), 2)

        cur.execute("""
                   SELECT
                       pg_database_size(current_database()) / (1024*1024.0) as size_mb
               """)
        process = psutil.Process(pg_pid)
        cpu_usage_percent = process.cpu_percent()
        memory_usage_mb = round(process.memory_info().rss / 1024 / 1024, 2)
        return {'db_name': active_db,
                'total_connections': total_connections,
                'db_size_mb': db_size_mb,
                'cache_hit_ratio': cache_hit_ratio,
                'deadlocks': deadlocks,
                'long_running_queries': long_running_queries,
                'connection_utilization': connection_utilization,
                'cpu_usage_percent': cpu_usage_percent,
                'memory_usage_mb': memory_usage_mb
                }

    @api.model
    def odoo_file_health(self):
        """fetch odoo's file health"""

        files_data = self.env['ir.attachment'].search([])
        uploaded_files = files_data.search_count([
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=30))])

        total_size = sum([len(attachment.datas) for attachment in files_data])
        total_size_mb = total_size / (1024 * 1024)

        files = files_data.filtered(lambda file: file.create_date >= fields.Datetime.now() - timedelta(days=30))

        # Calculate average size
        if len(files) > 0:
            total_size_last_30_days = sum([len(file.datas) for file in files])
            average_size_bytes = (total_size_last_30_days / len(files))/(1024 * 1024)
            average_size_mb = average_size_bytes / (1024 * 1024)  # Convert to MB
        else:
            average_size_mb = 0

        max_size = max([len(file.datas) for file in files], default=0)
        access_failures = self.env['ir.logging'].search_count([
            ('message', 'ilike', 'file'),
            ('level', '=', 'error'),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=30))
        ])
        deleted_files = files_data.search_count([
            ('datas', '=', False),
            ('write_date', '>=', fields.Datetime.now() - timedelta(days=30))
        ])

        file_types = defaultdict(int)
        for file in files:
            mimetype = file.mimetype
            if mimetype:
                mimetype = mimetype.strip().lower()
                if mimetype:
                    file_types[mimetype] += 1
                else:
                    print(f"Skipping file with invalid MIME type: {file.name}")
            else:
                print(f"Skipping file with missing MIME type: {file.name}")

        size_distribution = defaultdict(int)
        for attachment in files_data:
            file_size = attachment.file_size or 0

            if file_size < 10 * 1024:
                size_distribution['Small (<10KB)'] += 1
            elif file_size < 100 * 1024:
                size_distribution['Medium (10KB-100KB)'] += 1
            elif file_size < 500 * 1024:
                size_distribution['Large (100KB-500KB)'] += 1
            else:
                size_distribution['Very Large (>500KB)'] += 1

        free_disk_space = psutil.disk_usage('/').free
        free_disk_space_mb = free_disk_space / (1024 * 1024)
        available_memory = psutil.virtual_memory().available
        available_memory_mb = available_memory / (1024 * 1024)
        cpu_usage = psutil.cpu_percent(interval=1)
        disk_limit_mb = free_disk_space_mb * 0.1
        memory_limit_mb = available_memory_mb * 0.2

        if cpu_usage > 80:
            cpu_limit_mb = 5  # Limit to 5MB if CPU usage is high
        else:
            cpu_limit_mb = 100  # 100MB if CPU usage is low

        safe_upload_limit = min(disk_limit_mb, memory_limit_mb, cpu_limit_mb)
        average_size = round(average_size_mb, 10)

        return {
            'uploaded_files': uploaded_files,
            'average_size': average_size,
            'access_failures': access_failures,
            'deleted_files': deleted_files,
            'max_size': max_size,
            'file_types': file_types,
            'file_distribution': size_distribution,
            'safe_upload_limit': safe_upload_limit,
            'total_size_mb': round(total_size_mb, 2)
        }

    @api.model
    def get_concurrent_session_count(self):
        """Fetch Concurrent sesssions"""

        active_db = self.env.cr.dbname
        self.env.cr.execute(""" SELECT COUNT(*) FROM pg_stat_activity WHERE datname = %s AND state = 'active'; """, (active_db,))

        active_sessions = self.env.cr.fetchone()
        active_sessions_count = int(active_sessions[0]) if active_sessions else 0  # Convert to int

        self.env.cr.execute("""
                            SELECT setting
                            FROM pg_settings
                            WHERE name = 'max_connections';
                        """)
        max_connections = self.env.cr.fetchone()
        max_connections_value = int(max_connections[0]) if max_connections else 0  # Convert to int

        return {
            'active_sessions': active_sessions_count,
            'max_connections': max_connections_value
        }
