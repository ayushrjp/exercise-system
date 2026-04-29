class RepCounter:
    def __init__(self):
        self.count = 0
        self.stage = None

    def update(self, knee_angle):
        if knee_angle > 160:
            self.stage = "up"

        if knee_angle < 90 and self.stage == "up":
            self.stage = "down"
            self.count += 1

        return self.count, self.stage