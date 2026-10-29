import urllib.request
import json

high = {
    "school": "GP", "sex": "F", "age": 16, "address": "U", "famsize": "GT3", "Pstatus": "T",
    "Medu": 4, "Fedu": 4, "Mjob": "health", "Fjob": "teacher", "reason": "reputation",
    "guardian": "mother", "traveltime": 1, "studytime": 4, "failures": 0, "schoolsup": "no",
    "famsup": "yes", "paid": "yes", "activities": "yes", "nursery": "yes", "higher": "yes",
    "internet": "yes", "romantic": "no", "famrel": 5, "freetime": 3, "goout": 2, "Dalc": 1,
    "Walc": 1, "health": 5, "absences": 2
}

avg = {
    "school": "GP", "sex": "M", "age": 17, "address": "U", "famsize": "GT3", "Pstatus": "T",
    "Medu": 2, "Fedu": 2, "Mjob": "services", "Fjob": "other", "reason": "course",
    "guardian": "mother", "traveltime": 1, "studytime": 2, "failures": 0, "schoolsup": "no",
    "famsup": "yes", "paid": "no", "activities": "yes", "nursery": "yes", "higher": "yes",
    "internet": "yes", "romantic": "no", "famrel": 4, "freetime": 3, "goout": 3, "Dalc": 1,
    "Walc": 2, "health": 4, "absences": 6
}

risk = {
    "school": "MS", "sex": "M", "age": 19, "address": "R", "famsize": "LE3", "Pstatus": "A",
    "Medu": 1, "Fedu": 1, "Mjob": "at_home", "Fjob": "other", "reason": "other",
    "guardian": "other", "traveltime": 3, "studytime": 1, "failures": 3, "schoolsup": "yes",
    "famsup": "no", "paid": "no", "activities": "no", "nursery": "no", "higher": "no",
    "internet": "no", "romantic": "yes", "famrel": 2, "freetime": 4, "goout": 5, "Dalc": 4,
    "Walc": 5, "health": 2, "absences": 24
}

for name, payload in [("High Achiever", high), ("Average Student", avg), ("At-Risk Student", risk)]:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/predict",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    print(f"[{name}] Predicted: {res['predicted_grade']} / 20 | Rounded: {res['rounded_grade']} | Tier: {res['performance_level']}")
