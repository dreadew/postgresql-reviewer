"""
Воркер для выполнения задач из очереди Redis.
"""

import asyncio
import logging
import json
import signal
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import redis.asyncio as redis
import httpx
from src.core.config import settings
from src.services.database_service import DatabaseService
from src.services.vault_service import VaultService
from .models import TaskType, TaskStatus, TaskQueueItem

logger = logging.getLogger(__name__)


class TaskWorker:
    """Воркер для выполнения задач."""

    def __init__(self, worker_id: str = "worker-1"):
        self.worker_id = worker_id
        self.db_service = DatabaseService()
        self.vault_service = VaultService()
        self.redis_client = None
        self.is_running = False
        self.current_task = None

    async def initialize(self):
        """Инициализация воркера."""
        try:
            redis_url = settings.redis_url or "redis://localhost:6379"
            self.redis_client = redis.from_url(redis_url)
            await self.redis_client.ping()
            logger.info(f"Воркер {self.worker_id}: подключение к Redis установлено")

            self.vault_service.initialize()
            logger.info(f"Воркер {self.worker_id}: Vault инициализирован")

        except Exception as e:
            logger.error(f"Ошибка инициализации воркера {self.worker_id}: {e}")
            raise

    async def close(self):
        """Закрытие соединений."""
        if self.redis_client:
            await self.redis_client.close()

    async def start_worker(self):
        """Запустить воркер."""
        self.is_running = True
        logger.info(f"Воркер {self.worker_id} запущен")

        def signal_handler(signum, frame):
            logger.info(f"Воркер {self.worker_id}: получен сигнал {signum}")
            self.stop_worker()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        while self.is_running:
            try:
                task_data = await self.redis_client.brpop("task_queue", timeout=10)

                if task_data:
                    try:
                        task_json = task_data[1].decode("utf-8")
                        task_item = TaskQueueItem.model_validate_json(task_json)
                        self.current_task = task_item

                        logger.info(
                            f"Воркер {self.worker_id}: получена задача {task_item.execution_id}"
                        )
                        await self.process_task(task_item)

                    except Exception as e:
                        logger.error(
                            f"Воркер {self.worker_id}: ошибка обработки задачи: {e}"
                        )
                        if self.current_task:
                            self.mark_task_failed(
                                self.current_task.execution_id, str(e)
                            )
                    finally:
                        self.current_task = None

                else:
                    continue

            except Exception as e:
                logger.error(f"Воркер {self.worker_id}: критическая ошибка: {e}")
                if self.is_running:
                    await asyncio.sleep(5)

        logger.info(f"Воркер {self.worker_id} остановлен")

    def stop_worker(self):
        """Остановить воркер."""
        self.is_running = False
        logger.info(f"Воркер {self.worker_id}: получен сигнал остановки")

    async def process_task(self, task: TaskQueueItem):
        """Обработать задачу."""
        try:
            self.mark_task_running(task.execution_id)

            connection_data = self.get_connection_data(task.connection_id)
            if not connection_data:
                raise ConnectionError(
                    f"Не удалось получить данные подключения {task.connection_id}"
                )

            result = None
            if task.task_type == TaskType.LOG_ANALYSIS:
                result = await self.process_log_analysis(
                    connection_data, task.parameters
                )
            elif task.task_type == TaskType.CONFIG_CHECK:
                result = await self.process_config_check(
                    connection_data, task.parameters
                )
            elif task.task_type == TaskType.QUERY_ANALYSIS:
                result = self.process_query_analysis(connection_data)
            elif task.task_type == TaskType.CUSTOM_SQL:
                result = await self.process_custom_sql(connection_data, task.parameters)
            elif task.task_type == TaskType.TABLE_ANALYSIS:
                result = await self.process_table_analysis(
                    connection_data, task.parameters
                )
            else:
                raise NotImplementedError(f"Неизвестный тип задачи: {task.task_type}")

            self.mark_task_completed(task.execution_id, result)
            logger.info(
                f"Воркер {self.worker_id}: задача {task.execution_id} успешно выполнена"
            )

        except Exception as e:
            logger.error(
                f"Воркер {self.worker_id}: ошибка выполнения задачи {task.execution_id}: {e}"
            )

            if task.retry_count < task.max_retries:
                await self.retry_task(task)
            else:
                self.mark_task_failed(task.execution_id, str(e))

    def get_connection_data(self, connection_id: int) -> Optional[Dict[str, Any]]:
        """Получить данные подключения из Vault."""
        try:
            query = "SELECT * FROM connections WHERE id = %s"
            connection = self.db_service.fetch_one(query, connection_id)

            if not connection:
                logger.error(f"Подключение {connection_id} не найдено")
                return None

            vault_path = connection.get("vault_path")
            if not vault_path:
                vault_path = f"database/connections/{connection_id}"

            credentials = self.vault_service.get_secret(vault_path)

            if not credentials:
                logger.error(
                    f"Учетные данные для подключения {connection_id} не найдены в Vault"
                )
                return None

            return {
                "connection_id": connection_id,
                "name": connection["name"],
                "host": credentials.get("host"),
                "port": credentials.get("port", 5432),
                "database": credentials.get("database"),
                "username": credentials.get("username"),
                "password": credentials.get("password"),
                "ssl_mode": credentials.get("ssl_mode", "prefer"),
            }

        except Exception as e:
            logger.error(f"Ошибка получения данных подключения {connection_id}: {e}")
            return None

    async def process_log_analysis(
        self, connection_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обработать задачу анализа логов."""
        try:
            logs_content = self._fetch_postgresql_logs(connection_data)

            if not logs_content:
                logs_content = "Нет доступных логов для анализа"

            api_url = f"{settings.scheduler_api_url}/api/v1/logs/analyze"

            postgresql_version = self._get_postgresql_version(connection_data)

            payload = {
                "logs": logs_content,
                "server_info": {
                    "version": postgresql_version,
                    "host": connection_data["host"],
                    "database": connection_data["database"],
                },
                "environment": parameters.get("environment", "production"),
            }

            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(api_url, json=payload)
                response.raise_for_status()

                analysis_result = response.json()

                self.save_analysis_result(
                    connection_data["connection_id"], "log_analysis", analysis_result
                )

                return analysis_result

        except Exception as e:
            logger.error(f"Ошибка анализа логов: {e}")
            raise

    def _get_postgresql_version(self, connection_data: Dict[str, Any]) -> str:
        """Получить версию PostgreSQL."""
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=connection_data["host"],
                port=connection_data["port"],
                database=connection_data["database"],
                user=connection_data["username"],
                password=connection_data["password"],
            )

            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                version_string = cursor.fetchone()[0]
                version_parts = version_string.split()
                if len(version_parts) >= 2:
                    return version_parts[1]
                return "unknown"

        except Exception as e:
            logger.warning(f"Не удалось получить версию PostgreSQL: {e}")
            return "unknown"
        finally:
            if "conn" in locals():
                conn.close()

    def _fetch_postgresql_logs(self, connection_data: Dict[str, Any]) -> str:
        """Получить логи PostgreSQL."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            conn = psycopg2.connect(
                host=connection_data["host"],
                port=connection_data["port"],
                database=connection_data["database"],
                user=connection_data["username"],
                password=connection_data["password"],
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                try:
                    cursor.execute(
                        """
                        SELECT query, calls, total_exec_time, mean_exec_time 
                        FROM pg_stat_statements 
                        WHERE total_exec_time > 1000
                        ORDER BY total_exec_time DESC 
                        LIMIT 100
                    """
                    )
                    log_entries = cursor.fetchall()

                    if log_entries:
                        logs = []
                        for entry in log_entries:
                            logs.append(
                                f"QUERY: {entry['query']} | CALLS: {entry['calls']} | TIME: {entry['total_exec_time']}ms"
                            )
                        return "\n".join(logs)

                except Exception:
                    cursor.execute("SELECT version(), now(), current_database()")
                    result = cursor.fetchone()
                    return f"PostgreSQL Info: {result['version']} | Database: {result['current_database']} | Time: {result['now']}"

            conn.close()

        except Exception as e:
            logger.warning(f"Не удалось получить логи PostgreSQL: {e}")
            return f"Информация о подключении: {connection_data['host']}:{connection_data['port']}/{connection_data['database']}"

    async def process_config_check(
        self, connection_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обработать задачу проверки конфигурации."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            conn = psycopg2.connect(
                host=connection_data["host"],
                port=connection_data["port"],
                database=connection_data["database"],
                user=connection_data["username"],
                password=connection_data["password"],
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                config_query = """
                    SELECT name, setting, unit, category, short_desc 
                    FROM pg_settings 
                    WHERE category IN ('Resource Usage / Memory', 'Resource Usage / Disk', 'Write Ahead Log', 'Query Planning')
                    ORDER BY category, name
                """

                cursor.execute(config_query)
                config_rows = cursor.fetchall()
                config = {}

                for row in config_rows:
                    config[row["name"]] = {
                        "value": row["setting"],
                        "unit": row["unit"],
                        "category": row["category"],
                        "description": row["short_desc"],
                    }

                api_url = f"{settings.scheduler_api_url}/api/v1/config/analyze"

                postgresql_version = self._get_postgresql_version(connection_data)

                payload = {
                    "config": {k: v["value"] for k, v in config.items()},
                    "server_info": {
                        "version": postgresql_version,
                        "host": connection_data["host"],
                        "database": connection_data["database"],
                    },
                    "environment": parameters.get("environment", "production"),
                }

                async with httpx.AsyncClient(timeout=300) as client:
                    response = await client.post(api_url, json=payload)
                    response.raise_for_status()

                    analysis_result = response.json()

                    analysis_result["config_details"] = config

                    self.save_analysis_result(
                        connection_data["connection_id"],
                        "config_check",
                        analysis_result,
                    )

                    return analysis_result

            conn.close()

        except Exception as e:
            logger.error(f"Ошибка проверки конфигурации: {e}")
            raise

    def process_query_analysis(self, connection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработать задачу анализа запросов."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            conn = psycopg2.connect(
                host=connection_data["host"],
                port=connection_data["port"],
                database=connection_data["database"],
                user=connection_data["username"],
                password=connection_data["password"],
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                try:
                    cursor.execute(
                        """
                        SELECT query, calls, total_exec_time, mean_exec_time, rows
                        FROM pg_stat_statements 
                        WHERE total_exec_time > 100
                        ORDER BY total_exec_time DESC 
                        LIMIT 20
                    """
                    )
                    queries = cursor.fetchall()

                    result = {
                        "message": "Анализ запросов выполнен",
                        "connection_id": connection_data["connection_id"],
                        "timestamp": datetime.now().isoformat(),
                        "analyzed_queries": len(queries),
                        "queries": [dict(q) for q in queries] if queries else [],
                    }

                except Exception:
                    result = {
                        "message": "pg_stat_statements недоступно, анализ базовой информации",
                        "connection_id": connection_data["connection_id"],
                        "timestamp": datetime.now().isoformat(),
                        "note": "Для полного анализа требуется расширение pg_stat_statements",
                    }

            conn.close()
            return result

        except Exception as e:
            logger.error(f"Ошибка анализа запросов: {e}")
            raise NotImplementedError(f"Анализ запросов недоступен: {e}")

    async def process_custom_sql(
        self, connection_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обработать задачу выполнения кастомного SQL."""
        try:
            custom_sql = parameters.get("custom_sql")
            if not custom_sql:
                raise ValueError("Не указан SQL запрос для выполнения")

            query_timeout = parameters.get("query_timeout", 300)
            output_format = parameters.get("output_format", "json")

            import psycopg2
            from psycopg2.extras import RealDictCursor

            conn = psycopg2.connect(
                host=connection_data["host"],
                port=connection_data["port"],
                database=connection_data["database"],
                user=connection_data["username"],
                password=connection_data["password"],
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"SET statement_timeout = {query_timeout * 1000}")

                start_time = datetime.now()
                cursor.execute(custom_sql)
                execution_time = (datetime.now() - start_time).total_seconds()

                sql_upper = custom_sql.strip().upper()
                is_select = sql_upper.startswith("SELECT") or sql_upper.startswith(
                    "WITH"
                )

                result = {
                    "message": "Кастомный SQL запрос выполнен успешно",
                    "connection_id": connection_data["connection_id"],
                    "timestamp": datetime.now().isoformat(),
                    "sql": custom_sql,
                    "execution_time_seconds": execution_time,
                    "query_type": "SELECT" if is_select else "DML/DDL",
                }

                if is_select:
                    rows = cursor.fetchall()
                    result.update(
                        {
                            "rows_returned": len(rows),
                            "data": (
                                [dict(row) for row in rows]
                                if output_format == "json"
                                else rows
                            ),
                            "columns": (
                                [desc[0] for desc in cursor.description]
                                if cursor.description
                                else []
                            ),
                        }
                    )
                else:
                    result.update(
                        {"rows_affected": cursor.rowcount, "operation": "completed"}
                    )

                conn.commit()

            conn.close()

            self.save_analysis_result(
                connection_data["connection_id"], "custom_sql", result
            )

            return result

        except psycopg2.Error as e:
            logger.error(f"Ошибка выполнения SQL: {e}")
            raise RuntimeError(f"Ошибка PostgreSQL: {e}")
        except Exception as e:
            logger.error(f"Ошибка выполнения кастомного SQL: {e}")
            raise

    async def process_table_analysis(
        self, connection_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обработать задачу анализа таблиц."""
        try:
            target_tables = parameters.get("target_tables", [])
            detailed_analysis = parameters.get("detailed_analysis", False)

            import psycopg2
            from psycopg2.extras import RealDictCursor

            conn = psycopg2.connect(
                host=connection_data["host"],
                port=connection_data["port"],
                database=connection_data["database"],
                user=connection_data["username"],
                password=connection_data["password"],
            )

            tables_analysis = []

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if not target_tables:
                    cursor.execute(
                        """
                        SELECT schemaname, tablename 
                        FROM pg_tables 
                        WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
                        ORDER BY schemaname, tablename
                        LIMIT 50
                    """
                    )
                    target_tables = [
                        f"{row['schemaname']}.{row['tablename']}"
                        for row in cursor.fetchall()
                    ]

                for table in target_tables:
                    table_analysis = self._analyze_table(
                        cursor, table, detailed_analysis
                    )
                    tables_analysis.append(table_analysis)

            conn.close()

            result = {
                "message": "Анализ таблиц выполнен",
                "connection_id": connection_data["connection_id"],
                "timestamp": datetime.now().isoformat(),
                "analyzed_tables_count": len(tables_analysis),
                "tables": tables_analysis,
                "detailed_analysis": detailed_analysis,
            }

            self.save_analysis_result(
                connection_data["connection_id"], "table_analysis", result
            )

            return result

        except Exception as e:
            logger.error(f"Ошибка анализа таблиц: {e}")
            raise

    def _analyze_table(
        self, cursor, table_name: str, detailed: bool = False
    ) -> Dict[str, Any]:
        """Анализ отдельной таблицы."""
        try:
            schema, table = (
                table_name.split(".") if "." in table_name else ("public", table_name)
            )

            cursor.execute(
                """
                SELECT 
                    schemaname,
                    tablename,
                    tableowner,
                    tablespace,
                    hasindexes,
                    hasrules,
                    hastriggers
                FROM pg_tables 
                WHERE schemaname = %s AND tablename = %s
            """,
                (schema, table),
            )

            table_info = cursor.fetchone()
            if not table_info:
                return {"table": table_name, "error": "Таблица не найдена"}

            cursor.execute(
                """
                SELECT 
                    pg_size_pretty(pg_total_relation_size(%s)) as total_size,
                    pg_size_pretty(pg_relation_size(%s)) as table_size,
                    pg_size_pretty(pg_total_relation_size(%s) - pg_relation_size(%s)) as indexes_size
            """,
                (table_name, table_name, table_name, table_name),
            )

            size_info = cursor.fetchone()

            cursor.execute(
                """
                SELECT n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup,
                       last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
                FROM pg_stat_user_tables 
                WHERE schemaname = %s AND relname = %s
            """,
                (schema, table),
            )

            stats_info = cursor.fetchone()

            analysis = {
                "table": table_name,
                "schema": schema,
                "owner": table_info["tableowner"],
                "total_size": size_info["total_size"],
                "table_size": size_info["table_size"],
                "indexes_size": size_info["indexes_size"],
                "estimated_rows": stats_info["n_live_tup"] if stats_info else 0,
                "dead_rows": stats_info["n_dead_tup"] if stats_info else 0,
                "has_indexes": table_info["hasindexes"],
                "has_triggers": table_info["hastriggers"],
                "last_vacuum": (
                    stats_info["last_vacuum"].isoformat()
                    if stats_info and stats_info["last_vacuum"]
                    else None
                ),
                "last_analyze": (
                    stats_info["last_analyze"].isoformat()
                    if stats_info and stats_info["last_analyze"]
                    else None
                ),
            }

            if detailed:
                cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable, column_default,
                           character_maximum_length, numeric_precision, numeric_scale
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """,
                    (schema, table),
                )

                analysis["columns"] = [dict(row) for row in cursor.fetchall()]

                cursor.execute(
                    """
                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE schemaname = %s AND tablename = %s
                """,
                    (schema, table),
                )

                analysis["indexes"] = [dict(row) for row in cursor.fetchall()]

            return analysis

        except Exception as e:
            return {"table": table_name, "error": str(e)}

    def save_analysis_result(
        self, connection_id: int, analysis_type: str, result: Dict[str, Any]
    ):
        """Сохранить результат анализа в БД."""
        try:
            query = """
                INSERT INTO analysis_results (connection_id, analysis_type, result, created_at)
                VALUES (%s, %s, %s, %s)
            """

            create_table_query = """
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id SERIAL PRIMARY KEY,
                    connection_id INTEGER REFERENCES connections(id),
                    analysis_type VARCHAR(50) NOT NULL,
                    result JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

            self.db_service.execute_query(create_table_query, fetch=False)
            self.db_service.execute_query(
                query,
                (connection_id, analysis_type, json.dumps(result), datetime.now()),
                fetch=False,
            )

            logger.info(f"Результат анализа сохранен для подключения {connection_id}")

        except Exception as e:
            logger.error(f"Ошибка сохранения результата анализа: {e}")

    def mark_task_running(self, execution_id: int):
        """Отметить задачу как выполняющуюся."""
        self.db_service.update_task_execution(
            execution_id, status=TaskStatus.RUNNING.value, started_at=datetime.now()
        )

    def mark_task_completed(self, execution_id: int, result: Dict[str, Any]):
        """Отметить задачу как завершенную."""
        self.db_service.update_task_execution(
            execution_id,
            status=TaskStatus.COMPLETED.value,
            completed_at=datetime.now(),
            result=result,
        )

    def mark_task_failed(self, execution_id: int, error_message: str):
        """Отметить задачу как неудачную."""
        self.db_service.update_task_execution(
            execution_id,
            status=TaskStatus.FAILED.value,
            completed_at=datetime.now(),
            error_message=error_message,
        )

    async def retry_task(self, task: TaskQueueItem):
        """Повторить выполнение задачи."""
        task.retry_count += 1
        logger.info(
            f"Повторная попытка выполнения задачи {task.execution_id} ({task.retry_count}/{task.max_retries})"
        )

        await asyncio.sleep(min(task.retry_count * 60, 300))
        await self.redis_client.lpush("task_queue", task.model_dump_json())


async def main():
    """Главная функция воркера."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = TaskWorker("worker-1")

    try:
        await worker.initialize()
        await worker.start_worker()
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"Критическая ошибка воркера: {e}")
        sys.exit(1)
    finally:
        await worker.close()


if __name__ == "__main__":
    asyncio.run(main())
