class Auditor:
    """
      Handles Authentication and authorization.
      This class should not be used driectly. Inherit from it and add
      `authenticate_[get|post|put|delete]` methods.
      """

    def __init__(self, query, request):
        self.query = query
        self.request = request

    def audit(self):
        """
        This is just a wrapper that chooses the appropriate authentication function based on
        the request and runs it.
        """
        method = self.request.method.lower()

        auth_func = f"authenticate_{method}"

        if not hasattr(self, auth_func):
            raise NotImplementedError

        return getattr(self, auth_func)(query=self.query, request=self.request)
