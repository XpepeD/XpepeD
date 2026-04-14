import unittest

from services.analyzer import analyze_employee_batch


class AnalyzerTests(unittest.TestCase):
    def test_low_quality_high_rating_flag(self):
        employees = [
            {
                "employee_id": "E1",
                "name": "A",
                "department": "Юридическая служба",
                "role_type": "office",
                "final_rating": 6,
                "goals": [
                    {"goal": "Делать работу качественно", "result": "Выполнено", "status": "Выполнено"}
                ],
            }
        ]
        analyzed = analyze_employee_batch(employees)[0]
        self.assertIn("low_quality_high_rating", analyzed["hr_risk_flags"])

    def test_overperformance_low_impact_flag(self):
        employees = [
            {
                "employee_id": "E2",
                "name": "B",
                "department": "Логистика",
                "role_type": "office",
                "final_rating": 6,
                "goals": [
                    {
                        "goal": "Ежедневная обработка заявок в срок",
                        "result": "Выполнено, подтверждено отчетом",
                        "status": "Выполнено",
                    },
                    {
                        "goal": "Подготовка документов без ошибок",
                        "result": "Выполнено, подтверждено отчетом",
                        "status": "Выполнено",
                    },
                ],
            }
        ]
        analyzed = analyze_employee_batch(employees)[0]
        self.assertIn("overperformance_low_impact", analyzed["hr_risk_flags"])


if __name__ == "__main__":
    unittest.main()
