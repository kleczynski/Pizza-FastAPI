from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(f'postgresql://postgres:Grzybowa12@localhost:5432/pizza_deliver',
    echo = True
)

Base = declarative_base()

Session = sessionmaker()
