from sqlmodel import create_engine, SQLModel

engine = create_engine(
    "sqlite:///healthcare.db",
    connect_args={"check_same_thread": False}
)

def init_db():
    SQLModel.metadata.create_all(engine)
