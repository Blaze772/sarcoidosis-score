# Sarcoidosis Diagnostic Scoring Tool

def get_score():
    print("\nEnter findings for each organ system:")
    print("Type: 0 = none, 2 = somewhat probable, 3 = highly probable\n")

    systems = {
        "Lung": 0,
        "Brain": 0,
        "Skin": 0,
        "Eyes": 0,
        "Bone Marrow": 0,
        "Bone": 0,
        "Parotid/Salivary Glands": 0,
        "Endocrine": 0,
        "ENT/Muscle/Kidney/Heart": 0
    }

    total_score = 0

    for system in systems:
        while True:
            try:
                score = int(input(f"{system}: "))
                if score in [0, 2, 3]:
                    systems[system] = score
                    total_score += score
                    break
                else:
                    print("Enter only 0, 2, or 3.")
            except ValueError:
                print("Invalid input. Try again.")

    return total_score, systems


def interpret_score(score):
    print("\n--- RESULT ---")
    print(f"Total Score: {score}\n")

    if score >= 12:
        print("High likelihood of sarcoidosis")
    elif 8 <= score < 12:
        print("Moderate likelihood of sarcoidosis")
    elif 4 <= score < 8:
        print("Low likelihood — consider further testing")
    else:
        print("Unlikely sarcoidosis")


def main():
    print("=== Sarcoidosis Clinical Diagnostic Tool ===")
    total_score, systems = get_score()

    print("\nBreakdown:")
    for system, score in systems.items():
        print(f"{system}: {score}")

    interpret_score(total_score)


if __name__ == "__main__":
    main()