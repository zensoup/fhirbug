from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ResourceMapping(Base):
  '''
  The base class to provide functionality to
  our models.
  '''
  __abstract__ = True
  
  def bla(self):
    print('blu')
