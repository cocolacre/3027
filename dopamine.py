import random

class Hat:
    def __init__(self, expertise, systems):
        self.expertise = expertise
        self.systems = systems

    def implement_systems(self):
        if self.expertise >= 10 and self.systems:
            print(f"{self.__class__.__name__}'s systems implemented.")
            return True
        else:
            print(f"{self.__class__.__name__}'s systems not implemented.")
            return False

class BlackHat(Hat):
    def __init__(self, expertise, destructive_plans):
        super().__init__(expertise, destructive_plans)

    def implement_destructive_plans(self):
        return self.implement_systems()

class WhiteHat(Hat):
    def __init__(self, expertise, preventive_measures):
        super().__init__(expertise, preventive_measures)

    def implement_preventive_measures(self):
        return self.implement_systems()

class GreenHat(Hat):
    def __init__(self, expertise, monitoring_systems):
        super().__init__(expertise, monitoring_systems)

    def monitor_systems(self):
        return self.implement_systems()

class PinkHat(Hat):
    def __init__(self, expertise, communication_systems):
        super().__init__(expertise, communication_systems)

    def communicate_with_allies(self):
        return self.implement_systems()

class GrayHat(Hat):
    def __init__(self, expertise, hacking_systems):
        super().__init__(expertise, hacking_systems)

    def hack_into_systems(self):
        return self.implement_systems()

def battle_of_the_hats(black_hat, white_hat, green_hat, pink_hat, gray_hat):
    if black_hat.implement_destructive_plans():
        if white_hat.implement_preventive_measures():
            print("Black hat's destructive plans prevented.")
        else:
            if green_hat.monitor_systems():
                if pink_hat.communicate_with_allies():
                    if gray_hat.hack_into_systems():
                        print("Allies hacked into systems and prevented black hat's destructive plans.")
                    else:
                        print("Allies hacked into systems but failed to prevent black hat's destructive plans.")
                else:
                    print("Allies hacked into systems but failed to prevent black hat's destructive plans.")
            else:
                print("Black hat's destructive plans succeeded.")
    else:
        print("Black hat's destructive plans failed.")

def main():
    black_hat = BlackHat(10, True)
    white_hat = WhiteHat(10, True)
    green_hat = GreenHat(10, True)
    pink_hat = PinkHat(10, True)
    gray_hat = GrayHat(10, True)
    battle_of_the_hats(black_hat, white_hat, green_hat, pink_hat, gray_hat)

if __name__ == "__main__":
    main()