import os
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from .models import Users, Tasks, TaskStreak


def create_tables(engine: Engine):
    """
    Creates all required tables if they dont exist
    """
    Users.__table__.create(bind=engine, checkfirst=True)
    Tasks.__table__.create(bind=engine, checkfirst=True)
    TaskStreak.__table__.create(bind=engine, checkfirst=True)


    if os.getenv("DEBUG"):
        Session = sessionmaker(engine)
        
        # create an admin user if none exists
        # the username and password is hardcoded for now
        # TODO: make it configurable
        with Session() as session:
            if not session.query(Users).filter_by(user_id="342a8c4a-130a-40b9-a79f-8b784b3b3e24").first():
                user = Users(
                    user_id="342a8c4a-130a-40b9-a79f-8b784b3b3e24",
                    name="admin",
                    password="admin"

                )
                session.add(user)
            session.commit()
            
            