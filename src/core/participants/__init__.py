"""
Пакет participants содержит классы, представляющие различные роли участников
в системе цифрового рубля: Центральный банк, Финансовые Организации, Пользователи.
"""
# Явно импортируем классы, чтобы они были доступны как participants.CentralBank и т.д.
from .user import User, UserType
from .central_bank import CentralBank
from .financial_org import FinancialOrg

# Опционально: можно объявить __all__, чтобы указать, что экспортируется
__all__ = ['User', 'UserType', 'CentralBank', 'FinancialOrg']
