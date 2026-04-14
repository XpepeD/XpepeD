import random

OFFICE_GOALS = [
    "Сократить срок согласования договоров с 7 до 4 рабочих дней к концу квартала",
    "Повысить точность отчетности до 98% по итогам квартала",
    "Провести 3 обучения по документообороту и собрать оценку не ниже 4.5/5",
    "Оптимизировать процесс обработки заявок на 20%",
]

PRODUCTION_GOALS = [
    "Снизить внеплановые простои установки на 10% к концу квартала",
    "Сократить расход пара на 5% без нарушения техрегламента",
    "Провести 100% обязательных инструктажей по ОТ и ПБ до конца месяца",
    "Увеличить долю смен без нарушений чек-листа до 95%",
]

BAD_GOALS = [
    "Делать работу качественно",
    "Улучшить взаимодействие с коллегами",
    "Закрывать задачи вовремя",
    "Помогать отделу по всем вопросам",
]

DEPARTMENTS = [
    ("Юридическая служба", "office"),
    ("Логистика", "office"),
    ("Продажи", "office"),
    ("Кредитный менеджмент", "office"),
    ("Нефтехимическое производство", "production"),
    ("Техническое обслуживание", "production"),
]



def _build_goal(role_type: str):
    quality = random.random()
    if quality < 0.25:
        goal = random.choice(BAD_GOALS)
    elif role_type == "production":
        goal = random.choice(PRODUCTION_GOALS)
    else:
        goal = random.choice(OFFICE_GOALS)

    return {
        "goal": goal,
        "result": random.choice(
            [
                "Выполнено, подтверждено отчетом",
                "Выполнено частично, требуется доработка",
                "Выполнено, сделал как нужно",
                "Не выполнено",
            ]
        ),
        "status": random.choice(["Выполнено", "В работе", "Просрочено"]),
    }


def generate_employees(count: int = 100):
    employees = []
    for idx in range(1, count + 1):
        department, role_type = random.choice(DEPARTMENTS)
        goal_count = random.randint(2, 6)
        employees.append(
            {
                "employee_id": f"EMP-{idx:04d}",
                "name": f"Сотрудник {idx}",
                "department": department,
                "role_type": role_type,
                "final_rating": random.randint(3, 7),
                "goals": [_build_goal(role_type) for _ in range(goal_count)],
            }
        )
    return employees
