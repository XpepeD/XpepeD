import re
from statistics import mean


MEASURABLE_PATTERNS = [
    r"\d+%",
    r"\d+\s*(дней|дня|день|часов|часа|час)",
    r"к\s+концу\s+(квартала|месяца|года)",
    r"до\s+\d+",
]

BAD_RESULT_PATTERNS = [
    r"сделал как нужно",
    r"выполнено",
    r"закрыл",
]

IMPACT_PATTERNS = [
    r"эконом",
    r"сниз",
    r"увелич",
    r"прибыл",
    r"выруч",
    r"производит",
    r"простой",
    r"безопас",
    r"автомат",
    r"проект",
    r"внедр",
]

ROUTINE_PATTERNS = [
    r"обработк",
    r"согласован",
    r"подготов",
    r"ведение",
    r"закрытие заявок",
    r"ежеднев",
    r"текущ",
    r"базов",
]



def _goal_quality(goal_text: str) -> float:
    text = goal_text.lower().strip()
    if not text:
        return 0.0

    score = 0.0

    if len(text) > 30:
        score += 0.2

    if any(re.search(pattern, text) for pattern in MEASURABLE_PATTERNS):
        score += 0.45

    if any(word in text for word in ["снизить", "увеличить", "сократить", "повысить", "провести", "внедрить"]):
        score += 0.2

    if any(word in text for word in ["без", "при", "не ниже", "100%", "к концу"]):
        score += 0.15

    return min(score, 1.0)



def _result_quality(result_text: str) -> float:
    text = result_text.lower().strip()
    if not text:
        return 0.0

    base = 0.7
    if any(re.search(pattern, text) for pattern in BAD_RESULT_PATTERNS):
        base -= 0.35
    if "подтверждено" in text or "отчет" in text or "метрик" in text:
        base += 0.2
    return max(0.0, min(base, 1.0))



def _impact_score(goal_text: str) -> float:
    text = goal_text.lower().strip()
    if not text:
        return 0.0

    score = 0.0
    if any(re.search(pattern, text) for pattern in IMPACT_PATTERNS):
        score += 0.5
    if any(re.search(pattern, text) for pattern in MEASURABLE_PATTERNS):
        score += 0.3
    if "проект" in text or "внедр" in text:
        score += 0.2

    return min(score, 1.0)



def _routine_score(goal_text: str) -> float:
    text = goal_text.lower().strip()
    if not text:
        return 0.0

    hits = sum(1 for pattern in ROUTINE_PATTERNS if re.search(pattern, text))
    if hits == 0:
        return 0.0
    return min(1.0, hits * 0.35)



def _build_hr_risk_flags(employee: dict) -> list:
    flags = []

    if employee["goal_quality_score"] < 0.45 and employee["final_rating"] > 5:
        flags.append("low_quality_high_rating")

    if (
        employee["final_rating"] >= 6
        and employee["goal_completion_rate"] >= 0.8
        and employee["strategic_impact_score"] < 0.4
    ):
        flags.append("overperformance_low_impact")

    if employee["goal_quality_score"] < 0.35 and employee["result_quality_score"] < 0.45:
        flags.append("weak_goal_and_result_discipline")

    return flags



def analyze_employee_batch(employees, llm_client=None):
    analyzed = []

    for employee in employees:
        goal_scores = []
        result_scores = []
        impact_scores = []
        routine_scores = []
        completed = 0
        goal_details = []

        for goal in employee["goals"]:
            goal_score = _goal_quality(goal["goal"])
            result_score = _result_quality(goal["result"])
            impact_score = _impact_score(goal["goal"])
            routine_score = _routine_score(goal["goal"])

            if goal.get("status") == "Выполнено":
                completed += 1

            llm_comment = None
            if llm_client:
                llm_comment = llm_client.evaluate_goal(
                    goal_text=goal["goal"],
                    result_text=goal["result"],
                    role_type=employee["role_type"],
                )

            goal_scores.append(goal_score)
            result_scores.append(result_score)
            impact_scores.append(impact_score)
            routine_scores.append(routine_score)
            goal_details.append(
                {
                    **goal,
                    "goal_score": goal_score,
                    "result_score": result_score,
                    "impact_score": impact_score,
                    "routine_score": routine_score,
                    "llm_comment": llm_comment,
                }
            )

        goal_completion_rate = round(completed / len(employee["goals"]), 3) if employee["goals"] else 0.0

        enriched = {
            **employee,
            "goal_quality_score": round(mean(goal_scores), 3) if goal_scores else 0.0,
            "result_quality_score": round(mean(result_scores), 3) if result_scores else 0.0,
            "strategic_impact_score": round(mean(impact_scores), 3) if impact_scores else 0.0,
            "routine_load_score": round(mean(routine_scores), 3) if routine_scores else 0.0,
            "goal_completion_rate": goal_completion_rate,
            "goals": goal_details,
        }
        enriched["hr_risk_flags"] = _build_hr_risk_flags(enriched)
        analyzed.append(enriched)

    return analyzed



def department_summary(analyzed_employees):
    summary = {}
    for employee in analyzed_employees:
        dep = employee["department"]
        summary.setdefault(dep, []).append(employee)

    result = []
    for dep, members in summary.items():
        result.append(
            {
                "department": dep,
                "count": len(members),
                "goal_quality_avg": round(mean([m["goal_quality_score"] for m in members]), 3),
                "result_quality_avg": round(mean([m["result_quality_score"] for m in members]), 3),
                "impact_avg": round(mean([m["strategic_impact_score"] for m in members]), 3),
                "risk_share": round(mean([1.0 if m["hr_risk_flags"] else 0.0 for m in members]), 3),
            }
        )
    return sorted(result, key=lambda x: x["goal_quality_avg"])
