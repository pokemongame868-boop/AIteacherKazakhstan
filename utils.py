# utils.py файлы

def points_to_grade(points):
    """Баллды әріптік бағаға түрлендіру"""
    try:
        # Санға түрлендіру
        if isinstance(points, str):
            points = points.strip()
            if points == '':
                return "F"
            points_int = int(points)
        elif isinstance(points, (int, float)):
            points_int = int(points)
        else:
            return "F"
        
        # Бағаны анықтау
        if points_int >= 9:
            return "A"
        elif points_int >= 7:
            return "B"
        elif points_int >= 5:
            return "C"
        elif points_int >= 3:
            return "D"
        else:
            return "F"
    except (ValueError, TypeError):
        return "F"

def get_grade_class(grade):
    """Баға класын алу"""
    grade_classes = {
        "A": "grade-a",
        "B": "grade-b",
        "C": "grade-c",
        "D": "grade-d",
        "F": "grade-f"
    }
    return grade_classes.get(grade, "grade-f")