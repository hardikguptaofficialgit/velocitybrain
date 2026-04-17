from fastapi import APIRouter

router = APIRouter(prefix='/v1')

@router.get('/healthz')
def healthz():
    return {'ok': True}
