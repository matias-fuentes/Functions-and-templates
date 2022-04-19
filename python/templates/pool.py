poolData = {
    "poolName": {{ poolName }},
    "host": {{ host }},
    "port": {{ port }},
    "user": {{ user }},
    "password": {{ password }},
    "db": {{ db }}
}

pool = createPool(poolData)