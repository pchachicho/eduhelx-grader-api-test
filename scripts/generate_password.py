import string
import secrets

def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters) for i in range(length))
    return password


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a variable-length cryptographically secure random password")
    parser.add_argument(
        "--length",
        type=int,
        default=64,
        help="Character length of the generated password"
    )

    args = parser.parse_args()
    
    print(generate_password(args.length))