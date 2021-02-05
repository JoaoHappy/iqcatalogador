from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
from colorama import init, Fore, Back
from time import time
import sys, os, configparser
import numpy as np
from PyQt5 import uic,QtWidgets
import pymysql

db_name    = "bot_iqoption"
host_db    = "localhost"
user_db    = "root"
senha_db   = ""

def login_user():
    
    
    email = login.lineLogin.text()
    senha = login.lineSenha.text()
    
    conexao = pymysql.connect(host = host_db, user = user_db, passwd = senha_db, db = db_name)
    cursor = conexao.cursor()
    
    try:
        cursor.execute("SELECT senha FROM usuarios WHERE email = '{}'".format(email))
        senha_dbase = cursor.fetchall()
        conexao.commit()
        conexao.close()
    except:
        login.loginErrado.setText("Login errado!")
        
    if senha == senha_dbase[0][0]:
        login.close()
        catalogador.show()
    else:
        login.loginErrado.setText("Login errado!")

def login_iqoption():
    
    global API
    email_iq = catalogador.lineEmail.text()
    senha_iq = catalogador.lineSenha.text()
    API = IQ_Option(email_iq, senha_iq)
    print('Conectando....')
    
    API.connect()

    if API.check_connect():
        print("Conectado")
    else:
        print("conectado")
        
# def Conexao():
#     print('Conectando....')
    
#     API.connect()

#     if API.check_connect():
#         print("Conectado")
#     else:
#         print("conectado")

def cataloga(par, dias, prct_call, prct_put, timeframe):
    data = []
    datas_testadas = []
    time_ = time()
    sair = False
    while sair == False:
        velas = API.get_candles(par, (timeframe * 60), 1000, time_)
        velas.reverse()
        for x in velas:
            if datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d') not in datas_testadas:
                datas_testadas.append(datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d'))

            if len(datas_testadas) <= dias:
                x.update({'cor': 'verde' if x['open'] < x['close'] else 'vermelha' if x['open'] > x['close'] else 'doji'})
                data.append(x)
            else:
                sair = True
                break

        time_ = int(velas[-1]['from'] - 1)

    analise = {}
    for velas in data:
        horario = datetime.fromtimestamp(velas['from']).strftime('%H:%M')
        if horario not in analise: analise.update({horario: {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0, 'dir': ''}})
        analise[horario][velas['cor']] += 1

        try:
            analise[horario]['%'] = round(100 * (analise[horario]['verde'] / (analise[horario]['verde'] + analise[horario]['vermelha'] + analise[horario]['doji'])))
        except:
            pass

    for horario in analise:
        if analise[horario]['%'] > 50: analise[horario]['dir'] = 'CALL'
        if analise[horario]['%'] < 50: analise[horario]['%'], analise[horario]['dir'] = 100 - analise[horario]['%'], 'PUT '

    return analise


def Obter_Paridades():
    global API
    P = API.get_all_open_time()
    paridades = []
    pares = 'N'
    if pares == 'S':
        for pares in P['digital']:
            paridades.append(pares)
        for pares in P['turbo']:
            paridades.append(pares)
    else:
        for pares in P['digital']:
            if P['digital'][pares]['open'] == True:
                paridades.append(pares)
        for pares in P['turbo']:
            if P['turbo'][pares]['open'] == True:
                paridades.append(pares)

    return np.unique(paridades)


print('=========================================\n|         CATALOGADOR DE SINAIS         |\n=========================================')
check_lista_config = "S"
arquivo_saida_config     = "lista.csv"
arquivo_saida = arquivo_saida_config
check_lista = check_lista_config
timeframe_config = "5"
dias = int(30)
porcentagem = int(100)
martingale = "0"
prct_call = abs(porcentagem)
prct_put = abs(100 - porcentagem)
paridades = Obter_Paridades()
data = datetime.now().strftime('%Y-%m-%d')
for timeframe in timeframe_config:
    catalogacao = {}
    contador = 1
    for par in paridades:
        timer = int(time())
        print(f'{contador} - {Fore.GREEN}CATALOGANDO - {Fore.RESET} {Fore.BLUE}{par}{Fore.RESET} | TIMEFRAME {Fore.GREEN}M{timeframe}{Fore.RESET}...', end='')
        catalogacao.update({par: cataloga(par, dias, prct_call, prct_put, timeframe)})

        for par in catalogacao:
            for horario in sorted(catalogacao[par]):
                if martingale.strip() != '':

                    mg_time = horario
                    soma = {'verde': catalogacao[par][horario]['verde'], 'vermelha': catalogacao[par][horario]['vermelha'], 'doji': catalogacao[par][horario]['doji']}

                    for i in range(int(martingale)):

                        catalogacao[par][horario].update({'mg' + str(i + 1): {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0}})

                        mg_time = str(datetime.strptime((datetime.now()).strftime('%Y-%m-%d ') + str(mg_time), '%Y-%m-%d %H:%M') + timedelta(minutes=timeframe))[11:-3]

                        if mg_time in catalogacao[par]:
                            catalogacao[par][horario]['mg' + str(i + 1)]['verde'] += catalogacao[par][mg_time]['verde'] + soma['verde']
                            catalogacao[par][horario]['mg' + str(i + 1)]['vermelha'] += catalogacao[par][mg_time]['vermelha'] + soma['vermelha']
                            catalogacao[par][horario]['mg' + str(i + 1)]['doji'] += catalogacao[par][mg_time]['doji'] + soma['doji']

                            catalogacao[par][horario]['mg' + str(i + 1)]['%'] = round(100 * (catalogacao[par][horario]['mg' + str(i + 1)]['verde' if catalogacao[par][horario]['dir'] == 'CALL' else 'vermelha'] / (catalogacao[par][horario]['mg' + str(i + 1)]['verde'] + catalogacao[par][horario]['mg' + str(i + 1)]['vermelha'] + catalogacao[par][horario]['mg' + str(i + 1)]['doji'])))

                            soma['verde'] += catalogacao[par][mg_time]['verde']
                            soma['vermelha'] += catalogacao[par][mg_time]['vermelha']
                            soma['doji'] += catalogacao[par][mg_time]['doji']
                        else:
                            catalogacao[par][horario]['mg' + str(i + 1)]['%'] = 0

        print('finalizado em ' + str(int(time()) - timer) + ' segundos')
        contador += 1

        print('\n\n')

    for par in catalogacao:
        for horario in sorted(catalogacao[par]):
            ok = False

            if catalogacao[par][horario]['%'] >= porcentagem:
                ok = True
            else:
                for i in range(int(martingale)):
                    if catalogacao[par][horario]['mg' + str(i + 1)]['%'] >= porcentagem:
                        ok = True
                        break

            if ok == True:

                msg = Fore.YELLOW + par + Fore.RESET + ' - ' + horario + ' - ' + (Fore.RED if catalogacao[par][horario]['dir'] == 'PUT ' else Fore.GREEN) + catalogacao[par][horario]['dir'] + Fore.RESET + ' - ' + str(catalogacao[par][horario]['%']) + '% - ' + Back.GREEN + Fore.BLACK + str(catalogacao[par][horario]['verde']) + Back.RED + Fore.BLACK + str(catalogacao[par][horario]['vermelha']) + Back.RESET + Fore.RESET + str(catalogacao[par][horario]['doji'])

                if martingale.strip() != '':
                    for i in range(int(martingale)):
                        if str(catalogacao[par][horario]['mg' + str(i + 1)]['%']) != 'N/A':
                            msg += ' | MG ' + str(i + 1) + ' - ' + str(catalogacao[par][horario]['mg' + str(i + 1)]['%']) + '% - ' + Back.GREEN + Fore.BLACK + str(catalogacao[par][horario]['mg' + str(i + 1)]['verde']) + Back.RED + Fore.BLACK + str(catalogacao[par][horario]['mg' + str(i + 1)]['vermelha']) + Back.RESET + Fore.RESET + str(catalogacao[par][horario]['mg' + str(i + 1)]['doji'])
                        else:
                            msg += ' | MG ' + str(i + 1) + ' - N/A - N/A'

                print(msg)
                direcao = catalogacao[par][horario]['dir'].strip()
                open(arquivo_saida, 'a').write('M' + str(timeframe) + ';' + par + ';' + horario + ';' + direcao + '\n')
                if check_lista == 'S':
                    open(str(arquivo_saida) + '-CHECK', 'a').write(f'{data} {str(horario) + ":00"} {par} {direcao} {str(martingale) + "GL"} {str(timeframe) + "TM"}\n')

app         = QtWidgets.QApplication([])
login       = uic.loadUi("login.ui")
catalogador = uic.loadUi("catalogador.ui")
login.btnLogin.clicked.connect(login_user)
catalogador.btnLogin.clicked.connect(login_iqoption)
catalogador.btnLogin.clicked.connect(cataloga)


login.show()
app.exec()