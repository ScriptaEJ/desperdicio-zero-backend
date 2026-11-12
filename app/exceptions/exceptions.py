# --------------------------- USUARIOS ---------------------------

class UsuarioNaoAutorizado(Exception):
    def __init__(self, message='Usuario não autorizado'):
        self.message = message
        super().__init__(message)

class UserNotFound(Exception):
    def __init__(self, message='Usuário não encontrado.'):
        self.message = message
        super().__init__(message)

class DistinctPasswords(Exception):
    def __init__(self, message='Senhas diferentes.'):
        self.message=message
        super().__init__(message)

class DesactivatedUser(Exception):
    def __init__(self, message='Usuário desativado.'):
        self.message=message
        super().__init__(message)

class DadosInvalidos(Exception):
    def __init__(self, message='Dados Inválidos.'):
            self.message=message
            super().__init__(message)

class ContaExistente(Exception):
    def __init__(self, message='Conta já existe.'):
            self.message=message
            super().__init__(message)

class TokenNaoAutenticado(Exception):
    def __init__(self, message='Token não autenticado.'):
            self.message=message
            super().__init__(message)