import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import InstructorService
from app.models import InstructorModel
from scripts.generate_password import generate_password

async def create_instructor(
    onyen: str,
    first_name: str,
    last_name: str,
    email: str,
    password: str
) -> InstructorModel:
    session = SessionLocal()

    instructor = await InstructorService(session).create_instructor(
        onyen=onyen,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        confirm_password=password
    )
    
    session.close()

    return instructor


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create an instructor in the database")
    parser.add_argument(
        "--onyen",
        type=str,
        required=True,
        help="Onyen (must be unique)",
    )
    parser.add_argument(
        "--first_name",
        type=str,
        required=True,
        help="First name"
    )
    parser.add_argument(
        "--last_name",
        type=str,
        required=True,
        help="Last name"
    )
    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="Email (must be unique)"
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password"
    )

    args = parser.parse_args()

    asyncio.run(create_instructor(
        onyen=args.onyen,
        first_name=args.first_name,
        last_name=args.last_name,
        email=args.email,
        password=args.password
    ))

    print("Successfully created instructor")