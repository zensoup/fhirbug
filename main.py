from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import settings
from models import Patient

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

Session = sessionmaker(bind=engine)

session = Session()

pat = session.query(Patient).first()

print(pat.patient_id)
pat.bla()
