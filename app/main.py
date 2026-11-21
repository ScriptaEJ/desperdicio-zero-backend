from fastapi import FastAPI
from app.exceptions.exceptions import UserNotFound, DistinctPasswords, DesactivatedUser, UsuarioNaoAutorizado, TokenNaoAutenticado, RestauranteNaoEncontrado, RestauranteJaExiste, InsumoNaoEncontrado, DadosInvalidosInsumo, PerdaNaoEncontrada, PerdaDadosInvalidos
from app.exceptions.handlers import user_not_found_handler, distinct_passwords_handler, desactivated_user_handler, usuario_nao_Autorizado, token_nao_Autenticado, dados_invalidos, conta_existente, RestauranteNaoEncontrado, RestauranteJaExiste, insumo_nao_encontrado, dados_invalidos_insumo, perda_nao_encontrada, perda_dados_invalidos
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_routes import auth_routes
from app.routes.usuario_routes import user_routes
from app.routes.insumos_routes import insumos_routes
from app.routes.perda_routes import perda_router
from app.routes.restaurante_routes import router as restaurante_router
from app.routes.relatorios_routes import relatorios_router

app = FastAPI()

# ---------------- CORS ----------------

origins = [
    "http://localhost:5173",
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ HANDLERS ------------------

app.add_exception_handler(
    UserNotFound,
    user_not_found_handler
)

app.add_exception_handler(
    DistinctPasswords,
    distinct_passwords_handler
)

app.add_exception_handler(
    DesactivatedUser,
    desactivated_user_handler
)

app.add_exception_handler(
    TokenNaoAutenticado,
    token_nao_Autenticado
)

app.add_exception_handler(
    UsuarioNaoAutorizado,
    usuario_nao_Autorizado
)

app.add_exception_handler(
    RestauranteNaoEncontrado,
    RestauranteNaoEncontrado
)

app.add_exception_handler(
    RestauranteJaExiste,
    RestauranteJaExiste
)

app.add_exception_handler(
    InsumoNaoEncontrado,
    insumo_nao_encontrado
)

app.add_exception_handler(
    DadosInvalidosInsumo,
    dados_invalidos_insumo
)

app.add_exception_handler(
    PerdaNaoEncontrada,
    perda_nao_encontrada
)

app.add_exception_handler(
    PerdaDadosInvalidos,
    perda_dados_invalidos
)

# ------------------ HANDLERS ------------------

app.include_router(auth_routes, prefix='/api')
app.include_router(user_routes, prefix='/api')
app.include_router(insumos_routes, prefix='/api')
app.include_router(restaurante_router, prefix='/api')
app.include_router(perda_router, prefix='/api')
app.include_router(relatorios_router, prefix='/api')


@app.get('/')
def root():
    return {'status_api': 'active'}

