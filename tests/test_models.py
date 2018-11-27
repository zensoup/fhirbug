import unittest
from fhirball.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

from . import models_sqlAlchemy


session = None

def setUpModule():
    global session
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    models_sqlAlchemy.Base.metadata.create_all(engine)
    session.add(models_sqlAlchemy.DatabaseModel(id=1, name="ion torrent", fullname="start", password='asas'))
    session.commit()


class TestModel(unittest.TestCase):
    def test_something(self):
        q = session.query(models_sqlAlchemy.DatabaseModel).all()
        print(q)
    # def test_getter_string(self):
    #     """
    #     Getter can be a string representing the name of an attribute of _model
    #     """
    #     inst = models.AttributeWithStringGetter()
    #
    #     self.assertEquals(inst.name, "my_name")
