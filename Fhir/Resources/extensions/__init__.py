'''
Subclasses of Fhir Resources that provide som functionality shortcuts.
'''

from Fhir.Resources import identifier
class AMKA(identifier.Identifier):
  '''
  Create an Identifier Resource representing the AMKA coding from a string
  containing the AMKA code.

  >>> a = AMKA('123')
  >>> isinstance(a, identifier.Identifier)
  True
  >>> a.as_json()
  {'system': 'AMKA', 'value': '123'}
  '''

  def __init__(self, jsondict, *args, **kwargs):
    # TODO: validate

    amka_dict = {
      'value': jsondict,
      'system': 'AMKA'
    }
    return super(AMKA, self).__init__(amka_dict, *args, **kwargs)
