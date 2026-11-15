import pandas as pd, pathlib
for z in ('santo_domingo','daule'):
    pd.read_csv(f'datos/procesados/celdas_{z}.csv', usecols=['celda','cobertura']).to_csv(f'datos/crudos/registros/cobertura_antes_{z}.csv', index=False)
