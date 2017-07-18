import datetime
import warnings
import requests
import sys
import re

from configparser import ConfigParser
from data.Issue import Issues
from data.User import User
from process.Process import IssueSonar
from process.SendEmail import SendEmail

# Se ignora los warnings de conexión
warnings.filterwarnings('ignore')

STR_USERS_GROUP = 'users_group'
STR_CREATED_IN_LAST = 'created_in_last'
STR_ADDRESS_EMAIL = 'address_email'
STR_PORT_EMAIL = 'port_email'

print('INFO - {} : ****** Iniciando generador de informes de incidencias de Sonar ******'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
print('INFO - {} : Inicio obtención de parámetros de configuración'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
#INICIO OBTENCIÓN DE PARÁMETROS DE CONFIGURACIÓN

# Se recoge la dirección y contraseña del email por parámetro de consola de comandos
print('INFO - {} : Obteniendo parámetros de configuración por consola de comandos'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
if len(sys.argv) != 5:
    print('ERROR - {} : Parámetros erróneos, la llamada debe ser del typo "SonarIssues.py user_sonar password_sonar login_email password_email"'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

user_sonar = sys.argv[1]
password_sonar = sys.argv[2]
login_email = sys.argv[3]
password_email = sys.argv[4]

try:
    user_sonar
except NameError:
    print('ERROR - {} : User Sonar no definido por consola de comandos'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

try:
    password_sonar
except NameError:
    print('ERROR - {} : Password Sonar no definido por consola de comandos'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

try:
    login_email
except NameError:
    print('ERROR - {} : Usuario servidor de correo no definido por consola de comandos'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

try:
    password_email
except NameError:
    print('ERROR - {} : Password servidor de correo no definido por consola de comandos'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

if(user_sonar is None or user_sonar == '' or password_sonar is None or password_sonar == ''
   or login_email is None or login_email == '' or password_email is None or password_email == ''):
    print('ERROR - {} : Parámetros erróneos por consola de comandos'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

print('INFO - {} : Parámetros de configuración por consola de comandos obtenidos correctamente'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
print('INFO - {} : Obteniendo parámetros de configuración de login'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
config = ConfigParser()
config.read("config/config.ini")

print('INFO - {} : Parámetros de configuración de login obtenidos correctamente'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
print('INFO - {} : Obteniendo parámetros de configuración de búsqueda de incidencias'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))

for item in config.items("PARAM_SEARCH"):
    if (item[0] == STR_CREATED_IN_LAST):
        createdInLast = item[1]

try:
    createdInLast
except NameError:
    print('ERROR - {} : Fecha de consulta no definido en el archivo de configuración'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

if(createdInLast is None or createdInLast == ''):
    print('ERROR - {} : Parámetros de búsqueda no definidas en el archivo de configuración'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

#Traducimos el tiempo de consulta para mostrarlo en el email
strCreatedInLast = ''
splitCreatedInLast = re.split('([0-9]+[a-z]+)', createdInLast)
ifFirstIteration = True
for timeInLast in splitCreatedInLast:
    if timeInLast != '':
        if not ifFirstIteration:
            strCreatedInLast += ', '

        temp = re.findall('[a-zA-Z]+', timeInLast)
        cant = int(re.findall('[0-9]+', timeInLast)[0])
        if temp[0] == 'd':
            if cant == 1:
                strCreatedInLast += str(cant) + ' día'
            else:
                strCreatedInLast += str(cant) + ' dias'
        elif temp[0] == 'w':
            if cant == 1:
                strCreatedInLast += str(cant) + ' semana'
            else:
                strCreatedInLast += str(cant) + ' semanas'
        elif temp[0] == 'm':
            if cant == 1:
                strCreatedInLast += str(cant) + ' mes'
            else:
                strCreatedInLast += str(cant) + ' meses'
        elif temp[0] == 'y':
            if cant == 1:
                strCreatedInLast += str(cant) + ' año'
            else:
                strCreatedInLast += str(cant) + ' años'
        ifFirstIteration = False

print('INFO - {} : Parámetros de configuración de búsqueda de incidencias obtenidas correctamente'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
print('INFO - {} : Obteniendo usuarios'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))

listUsers = []
mapGroupUsers = dict()
mapRespUsers = dict()
for item in config.items("USERS_GROUP"):
    resp = item[0]
    users_resp = item[1]

    #A los responsables no se le genera informe
    #for i in resp.split(','):
        #if i not in listUsers:
            #listUsers.append(i)

    for i in users_resp.split(','):
        if i not in listUsers:
            listUsers.append(i)
            if i not in mapRespUsers:
                mapRespUsers[i] = resp

    mapGroupUsers[resp] = users_resp

if(len(listUsers) <= 0 or len(mapGroupUsers) <= 0):
    print('ERROR - {} : Usuarios no definidos en el archivo de configuración'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

print('INFO - {} : Usuarios obtenidos correctamente'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
print('INFO - {} : Obteniendo parámetros de configuración de envío de email'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))

for item in config.items("EMAIL"):
    if (item[0] == STR_ADDRESS_EMAIL):
        address_email = item[1]
    elif (item[0] == STR_PORT_EMAIL):
        port_email = item[1]

try:
    address_email
except NameError:
    print('ERROR - {} : Dirección servidor de correo no definido en el archivo de configuración'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

try:
    port_email
except NameError:
    print('ERROR - {} : Puerto servidor de correo no definido en el archivo de configuración'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

if(address_email is None or address_email == '' or port_email is None or port_email == ''):
    print('ERROR - {} : Parámetros de servidor de correo no definidas en el archivo de configuración'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
    exit(1)

print('INFO - {} : Parámetros de configuración de envío de email obtenidos correctamente'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
print('INFO - {} : Parámetros de configuración obtenidos correctamente'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))

#FIN OBTENCIÓN DE PARÁMETROS DE CONFIGURACIÓN
print('INFO - {} : Inicio generación de informes de incidencias de Sonar'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))

# Map <Usuario - Mensaje común> para almacenar la información por usuario que se enviará al responsable al finalizar
mapMessageComunByUser = dict()
# Map <Usuario - Mensaje> para almacenar la información por usuario que se enviará al correo
mapMessageByUser = dict()
# Mapa de información de personas
mapInfoUser = dict()
# Mapa <Usuario - debito acumulado> para almacenar la información de débito por usuario
mapDebtByUser = dict()

for user in listUsers:
    payload = {'q': user}
    response = requests.get('https://qamind.indra.es/api/users/search', params=payload, auth=(user_sonar, password_sonar), verify=False)
    if response.status_code == 200:
        data = response.json()

        if data['total'] == 1:
            person = ''
            for i in data['users']:
                person = User.as_payload(i)
                mapInfoUser[user] = person

            payload = {'authors' : user, 'createdInLast' : createdInLast, 'ps' : 500}
            response = requests.get('https://qamind.indra.es/api/issues/search', params=payload, auth=(user_sonar, password_sonar), verify=False)

            if response.status_code == 200:
                print('INFO - {} : ****** Iniciando generación de informe para el usuario {} ******'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y'), user))
                messageHtml = '<h1>Informe Incidencias Sonar</h1>'
                messageComunHtml = '<h4>Usuario: ' + person.name + ' (' + user + ')</h4>'

                data = response.json()

                total = data["total"]
                ps = data["ps"]
                num_pages = total // ps
                if total % ps > 0:
                    num_pages += 1

                messageComunHtml += '<p><b>Total incidencias en periodo de observacion (' + strCreatedInLast + '): ' + str(total) + '</p></b>'

                issueList = []
                for i in data['issues']:
                    issueList.append(Issues.as_payload(i))

                if num_pages > 1:
                    for i in range(1, num_pages):
                        payload = {'authors' : user, 'createdInLast' : createdInLast, 'ps' : 500,  'p' : (i+1)}
                        response = requests.get('https://qamind.indra.es/api/issues/search', params=payload, auth=(user_sonar, password_sonar), verify=False)
                        data = response.json()
                        for i in data['issues']:
                            issueList.append(Issues.as_payload(i))

                issueSonar = IssueSonar(issueList)

                numIssuesBlocker = issueSonar.getNumIssuesBlocker()
                numIssuesCritical = issueSonar.getNumIssuesCritical()
                messageComunHtml += '<p><b><font color="red">Número de incidencias BLOCKER: ' + str(numIssuesBlocker) + '</font></b></p>'
                messageComunHtml += '<p><b><font color="red">Número de incidencias CRITICAL: ' + str(numIssuesCritical) + '</font></b></p>'
                messageComunHtml += '<p><b>Número de incidencias MAJOR: ' + str(issueSonar.getNumIssuesMajor()) + '</b></p>'
                messageComunHtml += '<p><b>Número de incidencias MINOR: ' + str(issueSonar.getNumIssuesMinor()) + '</b></p>'
                messageComunHtml += '<p><b>Número de incidencias INFO: ' +  str(issueSonar.getNumIssuesInfo()) + '</b></p>'

                messageHtml += messageComunHtml
                messageHtml += '<dl><dt><b>Clases afectadas:</b></dt>'
                messageHtml += issueSonar.getAffectedClass()
                messageHtml += '</dl></br>'

                messageHtml += '<dl><dt><b>Clasificación por incidencias:</b></dt>'
                messageHtml += issueSonar.getIssuesClasification()
                messageHtml += '</dl></br>'

                #Imprimimos las incidencias BLOCKER Y CRITICAL, en el caso que existan
                if numIssuesBlocker > 0 or numIssuesCritical > 0:
                    messageHtml += '<table border="1" style="border-collapse: collapse; border: 1px solid black;">'
                    messageHtml += '<tr><th style="background-color: #00bfff;">Incidencias BLOCKER/CRITICAL</th></tr>'
                    messageHtml += issueSonar.getIssuesBlockerAndCritical()
                    messageHtml += '</table></br>'

                accumulatedDebt = issueSonar.getAccumulatedDebt()
                # Se almacena la información de débito
                mapDebtByUser[user] = accumulatedDebt
                messageHtml += '<p><b>Deuda técnica acumulada en el periodo de observación (' + strCreatedInLast + '): ' + issueSonar.parseDebtToFormat(accumulatedDebt) + '</p></b>'

                #Obtener todas las incidencias existentes para poder calcular la deuda total
                payload = {'authors': user, 'ps' : 500}
                response = requests.get('https://qamind.indra.es/api/issues/search', params=payload, auth=(user_sonar, password_sonar), verify=False)
                data = response.json()
                total = data["total"]
                ps = data["ps"]
                num_pages = total // ps
                if total % ps > 0:
                    num_pages += 1
                issueList = []
                for i in data['issues']:
                    issueList.append(Issues.as_payload(i))

                if num_pages > 1:
                    for i in range(1, num_pages):
                        payload = {'authors': user, 'ps' : 500, 'p': (i + 1)}
                        response = requests.get('https://qamind.indra.es/api/issues/search', params=payload, auth=(user_sonar, password_sonar), verify=False)
                        data = response.json()
                        for i in data['issues']:
                            issueList.append(Issues.as_payload(i))

                issueSonar = IssueSonar(issueList)

                accumulatedDebt = issueSonar.getAccumulatedDebt()
                messageHtml += '<p><b>Deuda técnica acumulada en todos los proyectos: ' + issueSonar.parseDebtToFormat(accumulatedDebt) + '</p></b>'

                # Añadir enlace a Sonar

                # Se inserta la información común a enviar al responsable
                mapMessageComunByUser[user] = messageComunHtml
                # Se inserta la información a enviar al usuario
                mapMessageByUser[user] = messageHtml

                print('INFO - {} : ****** Informe para el usuario {} finalizado correctamente ******'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y'), user))
            elif response.status_code == 401:
                print('ERROR - {} : Error en la generación de informe: Autenticación errónea'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
                exit(1)
            else:
                print('ERROR - {} : Error en la generación de informe: Error inesperado'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
                exit(1)
        else:
            print('WARNING - {} : No existe el usuario {}'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y'), user))
    elif response.status_code == 401:
        print('ERROR - {} : Error en la generación de informe: Autenticación errónea'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
        exit(1)
    else:
        print('ERROR - {} : Error en la generación de informe: Error inesperado'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
        exit(1)

# Generamos el ranking de usuario por débito
rankingHtml = ''
if len(mapDebtByUser) > 0:
    rankingHtml += '<table border="1" style="border-collapse: collapse; border: 1px solid black;"><tr>'
    rankingHtml += '<th colspan="3" style="background-color: #00bfff;">Ranking de usuarios por deuda técnica en el periodo de observación (' + strCreatedInLast + ')</th></tr>'
    listOrderDebtByUser = sorted(mapDebtByUser, key=lambda x: mapDebtByUser[x])
    count = 1
    for orderUser in listOrderDebtByUser:
        seconds = mapDebtByUser.get(orderUser)
        dias = (int(seconds / 86400))
        horas = (int((seconds - (dias * 86400)) / 3600))
        minutos = int((seconds - ((dias * 86400) + (horas * 3600))) / 60)
        segundos = seconds - ((dias * 86400) + (horas * 3600) + (minutos * 60))
        formatDebt = str(dias) + "D " + str(horas) + "h " + str(minutos) + "m " + str(segundos) + "s"
        rankingHtml += '<tr><td style="text-align: center;">' + str(count) + '</td><td>' + orderUser + '</td><td>' + formatDebt + '</td></tr>'
        count+=1
        # Mostramos los 5 primeros del ranking
        if count > 5:
            break

    rankingHtml += '</table>'

# Envíamos emails a los usuarios
print('INFO - {} : ****** Inicio envíos de email a los usuarios ******'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
for user in listUsers:
    if user in mapInfoUser:
        infoUser = mapInfoUser[user]
        #Hay que obtener los email de los responsables para enviar el correo con CC
        emailResp = ''
        if user in mapRespUsers:
            respUser = mapRespUsers[user]
            for i in respUser.split(','):
                if i in mapInfoUser:
                    infoResp = mapInfoUser[i]
                    emailResp += infoResp.email + ','

        # Enviar email
        print('INFO - {} : Inicio envío de email al usuario {}'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y'), user))
        sendEmail = SendEmail(address_email, port_email, login_email, password_email, infoUser.email, emailResp)

        if user in mapMessageByUser:
            messageHtmlToEmail = mapMessageByUser[user]
            messageHtmlToEmail += '</br>' + rankingHtml + '</br>'
            sendEmail.sendEmail('Resumen incidencias Sonar', messageHtmlToEmail)

        print('INFO - {} : Finalizado envío de email al usuario {}'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y'), user))

print('INFO - {} : ****** Envío de email a los usuarios finalizado correctamente ******'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))

# Recorremos el mapa de grupos para obtener a los responsables y enviar la info común de los usuarios que les corresponde
print('INFO - {} : ****** Inicio generación de informe a responsables ******'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
for k in mapGroupUsers.keys():
    listUsersResp = mapGroupUsers[k]
    messageRespHtml = '<h1>Informe resúmen Incidencias Sonar</h1>'
    emailResp = ''
    for u in listUsersResp.split(','):
        if u in mapMessageComunByUser:
            messageRespHtml += mapMessageComunByUser[u]
            messageRespHtml += '</br>'

    for r in k.split(','):
        if r in mapInfoUser:
            infoUser = mapInfoUser[r]
            sendEmail = SendEmail(address_email, port_email, login_email, password_email, infoUser.email, emailResp)
            sendEmail.sendEmail('Resumen equipo incidencias Sonar', messageRespHtml)

print('INFO - {} : ****** Finalizado generación de informe a responsables ******'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
print('INFO - {} : ****** Generador de informes de incidencias de Sonar finalizado correctamente ******'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
#exit(0)