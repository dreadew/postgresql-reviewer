import hvac
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VaultAuthenticationError(Exception):
    """Ошибка аутентификации в Vault."""

    pass


class VaultService:
    def __init__(self):
        self.vault_addr = os.getenv("VAULT_ADDR", "http://localhost:8200")
        self.vault_token = os.getenv("VAULT_TOKEN")

        if not self.vault_token:
            raise ValueError("VAULT_TOKEN не установлен")

        self.client = hvac.Client(url=self.vault_addr, token=self.vault_token)

    def initialize(self):
        """Инициализация сервиса Vault."""
        try:
            if not self.client.is_authenticated():
                raise VaultAuthenticationError("Не удалось аутентифицироваться в Vault")
            logger.info("Vault сервис инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Vault: {e}")
            raise

    def store_credentials(self, path: str, credentials: Dict[str, str]) -> bool:
        """Сохранить учетные данные в Vault."""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path, secret=credentials
            )
            logger.info(f"Учетные данные сохранены в Vault по пути: {path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения учетных данных в Vault: {e}")
            return False

    def get_credentials(self, path: str) -> Optional[Dict[str, Any]]:
        """Получить учетные данные из Vault."""
        try:
            logger.info(f"Получение секрета из Vault по пути: {path}")
            secret_response = self.client.secrets.kv.v2.read_secret_version(path=path)
            logger.info("Успешно получен секрет из Vault")
            return secret_response["data"]["data"]
        except Exception as e:
            logger.error(f"Ошибка получения учетных данных из Vault: {e}")
            return None

    def get_secret(self, path: str) -> Optional[Dict[str, Any]]:
        """Получение секрета из Vault."""
        return self.get_credentials(path)

    def delete_credentials(self, path: str) -> bool:
        """Удалить учетные данные из Vault."""
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)
            logger.info(f"Учетные данные удалены из Vault по пути: {path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления учетных данных из Vault: {e}")
            return False
