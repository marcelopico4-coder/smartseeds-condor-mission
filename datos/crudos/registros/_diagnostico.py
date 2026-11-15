import sys, rasterio
from rasterio.windows import Window
from src.suelo_lluvia import URL_CHELSA
OPC = dict(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',
           GDAL_HTTP_TIMEOUT='120', GDAL_HTTP_MAX_RETRY='3')
def paso(t):
    print('  paso:', t, flush=True)
with rasterio.Env(**OPC), rasterio.open('/vsicurl/' + URL_CHELSA) as f:
    paso('abierto')
    pass
from src.lectura_remota import _leer_directo
r = _leer_directo(URL_CHELSA, (-78.81, -1.51, -78.39, -1.09))
print(r['datos'].shape, r['escala'], r['desfase'])
