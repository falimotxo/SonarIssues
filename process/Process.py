"""
Clase que representa la lista de incidencias de un usuario
"""
import re
from collections import Counter
class IssueSonar:

    def __init__(self, issues):
        self.total = issues.__sizeof__()
        self.issues = issues

    def getNumIssuesBlocker(self):
        """ Obtiene el número de incidencias blocker que tiene el usuario """
        result = 0
        for issue in self.issues:
            if (issue.severity == 'BLOCKER'):
                result += 1
        return result

    def getNumIssuesCritical(self):
        """ Obtiene el número de incidencias critical que tiene el usuario """
        result = 0
        for issue in self.issues:
            if (issue.severity == 'CRITICAL'):
                result += 1
        return result

    def getNumIssuesMajor(self):
        """ Obtiene el número de incidencias major que tiene el usuario """
        result = 0
        for issue in self.issues:
            if (issue.severity == 'MAJOR'):
                result += 1
        return result

    def getNumIssuesMinor(self):
        """ Obtiene el número de incidencias minor que tiene el usuario """
        result = 0
        for issue in self.issues:
            if (issue.severity == 'MINOR'):
                result += 1
        return result

    def getNumIssuesInfo(self):
        """ Obtiene el número de incidencias info que tiene el usuario """
        result = 0
        for issue in self.issues:
            if (issue.severity == 'INFO'):
                result += 1
        return result

    def parseDebtToFormat(self, seconds):
        """ #Pasa los segundos a formato D H:m:s """
        dias = (int(seconds / 86400))
        horas = (int((seconds - (dias * 86400)) / 3600))
        minutos = int((seconds - ((dias * 86400) + (horas * 3600))) / 60)
        segundos = seconds - ((dias * 86400) + (horas * 3600) + (minutos * 60))

        return str(dias) + "D " + str(horas) + "h " + str(minutos) + "m " + str(segundos) + "s"

    def getAccumulatedDebt(self):
        """ Obtiene la deuda técnica acumulada en el periodo de observación (en días) """
        result = 0
        for issue in self.issues:
            split = re.split('([0-9]+[a-z]+)', issue.debt)
            for accumulated in split:
                if accumulated != '':
                    temp = re.findall('[a-zA-Z]+', accumulated)
                    cant = int(re.findall('[0-9]+', accumulated)[0])
                    if temp[0] == 'd':
                        result += cant*86400
                    elif temp[0] == 'h':
                        result += cant * 3600
                    elif temp[0] == 'min':
                        result += cant * 60
                    elif temp[0] == 's':
                        result += cant

        return result

    def getAffectedClass(self):
        result = ''
        mapClass = dict()
        for issue in self.issues:
            line = issue.line
            route_class = (issue.component).rpartition(':')[2]

            nom_class_aux = route_class.split('main/java')
            nom_class = ''

            if(len(nom_class_aux) > 1):
                nom_class = route_class.split('main/java')[1].replace('/', '.').lstrip('.')
            else:
                nom_class_aux = route_class.split('test/java')
                if (len(nom_class_aux) > 1):
                    nom_class = '[*TEST*] ' + route_class.split('test/java')[1].replace('/', '.').lstrip('.')

            if nom_class in mapClass:
                listLineClass = mapClass[nom_class]
                if line != -1:
                    listLineClass.append(line)
                mapClass[nom_class] = listLineClass
            else:
                listLineClass = []
                if line != -1:
                    listLineClass.append(line)
                mapClass[nom_class] = listLineClass

        for k, v in mapClass.items():
            v.sort()
            v_new = []
            for i in v:
                if i not in v_new:
                    v_new.append(i)

            result += '<dd>' + k + ' ' + str(v_new) + '' + '</dd>'

        return result

    def getIssuesClasification(self):
        result = ''
        messages = Counter(getattr(i, 'message') for i in self.issues).most_common()
        for message, count in messages:
            severity = ''
            initSeveritiTag = '<b>'
            endSeverityTag = '</b>'
            for issue in self.issues:
                if issue.message == message:
                    severity = issue.severity
                    if severity == 'BLOCKER' or severity == 'CRITICAL':
                        initSeveritiTag = '<b><font color="red">'
                        endSeverityTag = '</b></font>'
                    break
            result += '<dd>' + initSeveritiTag + severity + endSeverityTag + ': ' + message + ' - Nº veces: ' + str(count) + '</dd>'

        return result

    def getIssuesBlockerAndCritical(self):
        result = ''
        count = 0
        for issue in self.issues:
            if (issue.severity == 'BLOCKER' or issue.severity == 'CRITICAL'):
                count += 1
                route_class = (issue.component).rpartition(':')[2]

                nom_class_aux = route_class.split('main/java')
                nom_class = ''

                if (len(nom_class_aux) > 1):
                    nom_class = route_class.split('main/java')[1].replace('/', '.').lstrip('.')
                else:
                    nom_class_aux = route_class.split('test/java')
                    if (len(nom_class_aux) > 1):
                        nom_class = '[*TEST*] ' + route_class.split('test/java')[1].replace('/', '.').lstrip('.')

                line = issue.line
                message = issue.message

                if line == -1:
                    line = ''

                result += '<tr><td>Incidencia: ' + issue.severity + '</br>'
                result += 'Clase: ' + nom_class + ' [' + str(line) + ']</br>'
                result += 'Message: ' + message + '</td></tr>'

        return result