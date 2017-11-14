

class Auditor:
  '''
  Handles Authentication and authorization.
  '''

  def __init__(self, query, request):
    self.query = query
    self.request = request

  def audit(self):
    method = self.request.method.lower()

    auth_func = f'authenticate_{method}'

    if not hasattr(self, auth_func):
      raise NotImplementedError

    return getattr(self, auth_func)(query=self.query, request=self.request)
