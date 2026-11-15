from src.lectura_remota import forma_de_leer, leer_recuadro
from src.suelo_lluvia import URL_CHELSA
r = leer_recuadro(URL_CHELSA, (-78.62, -1.32, -78.58, -1.28))
print('forma:', forma_de_leer(), '· recuadro de', r['datos'].shape, '· lluvia del año en Ambato:',
      round(float(r['datos'].mean() * r['escala'] + r['desfase'])), 'mm')
