import datetime

# Obtem a data de emissão
entrada = input("Data Inicial dd/mm/aaaa: ")
datainicial = datetime.datetime.strptime(entrada, "%d/%m/%Y")

# Obtem o numero de dias
quant_dias = int(input("Quantos dias? "))

# Adiciona dias à data
datafinal = datainicial + datetime.timedelta(quant_dias)

# Exibe o resultado
print ("data Inicial: ", datainicial.strftime("%d/%m/%Y"))
print ("Nº de dias: ", quant_dias)
print ("Data de vencimento: ", datafinal.strftime("%d/%m/%Y"))