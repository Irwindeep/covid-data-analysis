# model.py
def classify_data(temperature):
    return "healthy" if temperature < 38 else "unhealthy"
