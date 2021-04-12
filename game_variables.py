import hashlib

teams_passwords = {
    'Pluk': 'generál',
    '5,5': 'miminko',
    'SPLAV': 'Dobruška',
    'Quinquegae': 'Panda',
    'Jdemenato': 'Pepeteam',
    'Šalingrad': 'Šohaju!',
    'Čumílkovi': 'pancumilek007',
    'Minimalisti': 'generatornahodnychslov',
    'Mudresovy': 'Neposeto!',
    'oxymoroni': 'numberwang',
    'Bubáci': 'Divoženky',
    'Kuřátka': 'Slepička',
    'Plášata': 'Zmijozel',
    'FisCis': 'onlajnhra',
    'Nepromoření': 'Omerta',
    'His': 'Pope',
    'Májovci': 'majovci',
    'Pacific': 'Trebon',
    'PozdniSber2020': 'KroMan',
    'PrahaVenkov': 'olseH',
    'hchkrdtn': 'makáme',
    'Salašníci': 'Hradec',
    'Jednotlivci': 'VKH',
    'test': 'est',
}


teams_secret_passwords = {
    n: hashlib.md5((n + "__" + p).encode()).hexdigest() for n, p in teams_passwords.items()
}

secpasswords_teams = {v: k for k, v in teams_secret_passwords.items()}

if __name__ == "__main__":
    for n, s in teams_secret_passwords.items():
        print(n, s)
