import psycopg2
from typing import List, Dict, Any
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PostgresService:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с PostgreSQL."""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string, connect_timeout=10)
            yield conn
        except Exception as e:
            logger.error(f"Ошибка соединения с PostgreSQL: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_connection_config(self) -> Dict[str, Any]:
        """Получить параметры конфигурации PostgreSQL."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT name, setting, unit, short_desc
                    FROM pg_settings
                    WHERE name IN (
                        'work_mem', 'shared_buffers', 'effective_cache_size',
                        'maintenance_work_mem', 'max_connections',
                        'checkpoint_timeout', 'max_wal_size',
                        'fsync', 'wal_sync_method', 'autovacuum'
                    )
                    """
                )
                config = {}
                for row in cur.fetchall():
                    config[row[0]] = {
                        "setting": row[1],
                        "unit": row[2],
                        "description": row[3],
                    }

                return config

    def get_database_stats(self) -> Dict[str, Any]:
        """Получить статистику базы данных."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT schemaname, tablename,
                           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                           n_tup_ins + n_tup_upd + n_tup_del as row_count
                    FROM pg_tables t
                    LEFT JOIN pg_stat_user_tables s ON t.schemaname = s.schemaname AND t.tablename = s.relname
                    ORDER BY pg_total_relation_size(t.schemaname||'.'||t.tablename) DESC
                    LIMIT 10
                    """
                )

                tables = []
                for row in cur.fetchall():
                    tables.append(
                        {
                            "schema": row[0],
                            "table": row[1],
                            "size": row[2],
                            "row_count": row[3] or 0,
                        }
                    )

                cur.execute("SELECT count(*) FROM pg_stat_activity")
                connection_count = cur.fetchone()[0]

                return {"tables": tables, "connection_count": connection_count}

    def get_slow_queries(self, duration_ms: int = 1000) -> List[Dict[str, Any]]:
        """Получить медленные запросы из pg_stat_statements."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        query,
                        calls,
                        total_exec_time,
                        mean_exec_time,
                        rows
                    FROM pg_stat_statements
                    WHERE mean_exec_time > %s
                    ORDER BY mean_exec_time DESC
                    LIMIT 20
                    """,
                    (duration_ms,),
                )

                queries = []
                for row in cur.fetchall():
                    queries.append(
                        {
                            "query": row[0],
                            "calls": row[1],
                            "total_time": row[2],
                            "mean_time": row[3],
                            "rows": row[4],
                        }
                    )

                return queries

    def get_log_entries(self, since_minutes: int = 60) -> List[Dict[str, Any]]:
        """Получить записи из логов PostgreSQL."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        SELECT
                            log_time,
                            user_name,
                            database_name,
                            process_id,
                            connection_from,
                            session_id,
                            session_line_num,
                            command_tag,
                            session_start_time,
                            virtual_transaction_id,
                            transaction_id,
                            error_severity,
                            sql_state_code,
                            message,
                            detail,
                            hint,
                            internal_query,
                            internal_query_pos,
                            context,
                            query,
                            query_pos,
                            location,
                            application_name
                        FROM pg_log
                        WHERE log_time >= NOW() - INTERVAL '%s minutes'
                        ORDER BY log_time DESC
                        LIMIT 100
                        """,
                        (since_minutes,),
                    )

                    logs = []
                    for row in cur.fetchall():
                        logs.append(
                            {
                                "log_time": row[0],
                                "user_name": row[1],
                                "database_name": row[2],
                                "process_id": row[3],
                                "connection_from": row[4],
                                "session_id": row[5],
                                "session_line_num": row[6],
                                "command_tag": row[7],
                                "session_start_time": row[8],
                                "virtual_transaction_id": row[9],
                                "transaction_id": row[10],
                                "error_severity": row[11],
                                "sql_state_code": row[12],
                                "message": row[13],
                                "detail": row[14],
                                "hint": row[15],
                                "internal_query": row[16],
                                "internal_query_pos": row[17],
                                "context": row[18],
                                "query": row[19],
                                "query_pos": row[20],
                                "location": row[21],
                                "application_name": row[22],
                            }
                        )

                    return logs

                except Exception as e:
                    logger.warning(f"Не удалось получить логи из pg_log: {e}")
                    logger.info(
                        "Для работы с логами требуется настройка logging_collector в postgresql.conf"
                    )
                    return []

    def get_log_entries(self) -> List[Dict[str, Any]]:
        """Получить записи из логов PostgreSQL."""
        logger.warning(
            "get_log_entries не реализован - требуется настройка логирования PostgreSQL"
        )
        return []
