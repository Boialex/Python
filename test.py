import random
import datetime
import json

user_schedule = {
    "display": [
        {
            "id": "GALLERY_MOS7001A1OMDB",
            "operator": "GALLERY",
            "name": "MOS7001A1OMDB",
            "coordinates": {
                "lat": 55.768438,
                "lon": 37.557919,
                "angle": 30
            },
            "stat": {
                "ots": random.randint(0, 10**3),
                "reach": random.randint(0, 10**3),
                "grp": 100,
                "frequency": 1. * random.randint(0, 100),
                "percentage": 10
            }
        },
        {
            "id": "GALLERY_MOS7003A1GGDB",
            "operator": "GALLERY",
            "name": "MOS7003A1GGDB",
            "coordinates": {
                "lat": 55.85815,
                "lon": 37.58398,
                "angle": 0
            },
            "stat": {
                "ots": random.randint(0, 10**4),
                "reach": random.randint(0, 10**3),
                "grp": 100,
                "frequency": 1. * random.randint(0, 100),
                "percentage": 10
            }
        }
    ],
    "stat": {
        "ots": random.randint(0, 10**6),
        "grp": random.randint(0, 10**3),
        "reach": 1,
        "frequency": 1. * random.randint(0, 100)
    },
    "stat_targeting": {
        "ots": random.randint(0, 10**6),
        "grp": random.randint(0, 10**3),
        "reach": 1,
        "frequency": 1. * random.randint(0, 100)
    },
    "error_code": 1,
    "displays_count": 42
}
min_data = datetime.datetime.max
max_data = datetime.datetime.min
user_schedule["period"] = {
    "begin": max_data.ctime(),
    "end": min_data.ctime()
}

print(str(json.loads(json.dumps(user_schedule))))