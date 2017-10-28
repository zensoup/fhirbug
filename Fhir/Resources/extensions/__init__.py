from Fhir.Resources import identifier
class AMKA(identifier.Identifier):
  def __init__(self, jsondict, *args, **kwargs):
    # TODO: validate

    amka_dict = {
      'value': jsondict,
      'system': 'AMKA'
    }
    return super(AMKA, self).__init__(amka_dict, *args, **kwargs)
