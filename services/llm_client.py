"""Адаптер для подключения вашего класса giga.

По умолчанию отключен (enabled=False), чтобы приложение работало на моках.
Когда подключите реальный модуль, передайте callable в конструктор.
"""


class LLMClient:
    def __init__(self, enabled=False, giga_callable=None):
        self.enabled = enabled
        self.giga_callable = giga_callable

    def evaluate_goal(self, goal_text: str, result_text: str, role_type: str):
        if not self.enabled or self.giga_callable is None:
            return "LLM выключен: используется локальная эвристика"

        system_prompt = (
            "Ты HR-ассистент по оценке целей сотрудников. "
            "Оцени ясность, измеримость и проверяемость результата. "
            "Учитывай тип роли: office или production. "
            "Ответ кратко, 2-3 предложения."
        )
        prompt = (
            f"Тип роли: {role_type}\n"
            f"Цель: {goal_text}\n"
            f"Результат: {result_text}\n"
            "Дай комментарий, что улучшить."
        )

        try:
            return self.giga_callable(prompt, system_prompt)
        except Exception as exc:
            return f"Ошибка LLM: {exc}"
