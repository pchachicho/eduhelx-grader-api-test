import asyncio
from app.database import SessionLocal
from app.services import CourseService
from app.core.exceptions import CourseAlreadyExistsException

async def create_course(name: str, master_remote_url: str):
    session = SessionLocal()
    await CourseService(session).create_course(
        name=name,
        master_remote_url=master_remote_url
    )
    session.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Setup the course in the database")
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Course name"
    )
    parser.add_argument(
        "--master_remote_url",
        type=str,
        required=True,
        help="Master repository remote URL"
    )

    args = parser.parse_args()

    try:
        asyncio.run(create_course(
            name=args.name,
            master_remote_url=args.master_remote_url
        ))
        print(f"Successfully created course: {args.name}")
    except CourseAlreadyExistsException:
        print("Course already exists, exiting gracefully...")