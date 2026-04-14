from flask import Flask, render_template, request

from data.mock_data import generate_employees
from services.analyzer import analyze_employee_batch, department_summary
from services.llm_client import LLMClient

app = Flask(__name__)


# Мок-данные (заменится вашим классом личного кабинета)
EMPLOYEES = generate_employees(120)

# Обертка над вашей функцией giga. По умолчанию выключена.
llm_client = LLMClient(enabled=False)


FLAG_LABELS = {
    "low_quality_high_rating": "Низкое качество целей при оценке > 5",
    "overperformance_low_impact": "Высокая оценка/выполнение при низком стратегическом влиянии",
    "weak_goal_and_result_discipline": "Слабая дисциплина целеполагания и отчетности",
}


def _to_bool(value: str) -> bool:
    return str(value).lower() in {"1", "true", "yes", "on"}


@app.route("/")
def dashboard():
    use_llm = _to_bool(request.args.get("use_llm", "0"))

    analyzed = analyze_employee_batch(EMPLOYEES, llm_client=llm_client if use_llm else None)
    flagged = [item for item in analyzed if item["hr_risk_flags"]]

    summary = department_summary(analyzed)

    return render_template(
        "dashboard.html",
        employees=analyzed,
        flagged=flagged,
        summary=summary,
        use_llm=use_llm,
        flag_labels=FLAG_LABELS,
    )


@app.route("/employee/<employee_id>")
def employee_card(employee_id: str):
    use_llm = _to_bool(request.args.get("use_llm", "0"))
    analyzed = analyze_employee_batch(EMPLOYEES, llm_client=llm_client if use_llm else None)
    employee = next((x for x in analyzed if x["employee_id"] == employee_id), None)

    if employee is None:
        return "Сотрудник не найден", 404

    return render_template("employee.html", employee=employee, use_llm=use_llm, flag_labels=FLAG_LABELS)


@app.route("/self-check", methods=["GET", "POST"])
def self_check():
    result = None
    if request.method == "POST":
        goal_text = request.form.get("goal_text", "")
        result = analyze_employee_batch(
            [
                {
                    "employee_id": "SELF-001",
                    "name": "Самопроверка",
                    "department": request.form.get("department", "Офис"),
                    "role_type": request.form.get("role_type", "office"),
                    "final_rating": 5,
                    "goals": [
                        {
                            "goal": goal_text,
                            "result": request.form.get("result", ""),
                            "status": "В работе",
                        }
                    ],
                }
            ],
            llm_client=llm_client if _to_bool(request.form.get("use_llm", "0")) else None,
        )[0]

    return render_template("self_check.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
