import datetime as datatt
from PyQt5 import uic,QtWidgets
import pymysql


db_name    = "bot_iqoption"
host_db    = "localhost"
user_db    = "root"
senha_db   = ""



def cadastrar():
    
    
    email       = registroAdm.lineEmail.text()
    senha       = registroAdm.lineSenha.text()
    data        = registroAdm.lineData.text()
    datainicial = datatt.datetime.strptime(data, "%d/%m/%Y")

    quant_dias =  int(registroAdm.lineExpiracao.text())

    # Adiciona dias à data
    datafinal = datainicial + datatt.timedelta(quant_dias)

    conexao = pymysql.connect(host = host_db, user = user_db, passwd = senha_db, db = db_name)
    cursor = conexao.cursor()
        
    cursor.execute("INSERT INTO usuarios (email, senha, data_registro, data_expiracao) VALUES (%s, %s, %s, %s)",(email, senha, datainicial, datafinal))
    conexao.commit()
    conexao.close()
    registroAdm.labelConcluido.setText("Usuario cadastrado com sucesso")








# finaliza a conexão



app         = QtWidgets.QApplication([])
registroAdm = uic.loadUi("registroAdm.ui")
registroAdm.btnRegistra.clicked.connect(cadastrar) 

registroAdm.show()
app.exec()
