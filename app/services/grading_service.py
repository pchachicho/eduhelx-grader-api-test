from sqlalchemy.orm import Session

class GradingService:
    def __init__(self, session: Session):
        self.session = session