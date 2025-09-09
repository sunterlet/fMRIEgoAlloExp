from .experiment import Experiment

def main():
    """Entry point for the navigation experiment."""
    player_initials = input("Enter player initials: ").strip()
    experiment = Experiment(player_initials)
    experiment.run()

if __name__ == "__main__":
    main() 