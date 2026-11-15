import pandas as pd
for z in ('santo_domingo','daule'):
    a = pd.read_csv(f'datos/crudos/registros/cobertura_antes_{z}.csv')['cobertura'].astype(str)
    d = pd.read_csv(f'datos/procesados/celdas_{z}.csv')['cobertura'].astype(str)
    print(z, '| celdas cuyo tipo de terreno cambió al reentrenar:', f'{(a != d).mean():.1%}')
for z in ('tungurahua','cotopaxi'):
    t = pd.read_csv(f'datos/procesados/celdas_{z}.csv')
    print(z, len(t), 'celdas | columnas:', list(t.columns))
    print(t.describe().loc[['min','50%','max']].round(2).T.to_string())
    print((t['cobertura'].value_counts(normalize=True, dropna=False) * 100).round(1).to_dict())
