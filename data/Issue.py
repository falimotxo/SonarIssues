"""
Clase que representa una incidencia de un usuario
"""
class Issues:

    accumulatedDebt = 0

    def __init__(self, key, rule, severity, component, componentId, project,
    line, textRange, flows, status, message, effort, debt, assignee, author,
    tags, creationDate, updateDate, typ):
        self.key = key
        self.rule = rule
        self.severity = severity
        self.component = component
        self.componentId = componentId
        self.project = project
        self.line = line
        self.textRange = textRange
        self.flows = flows
        self.status = status
        self.message = message
        self.effort = effort
        self.debt = debt
        self.assignee = assignee
        self.author = author
        self.tags = tags
        self.creationDate = creationDate
        self.updateDate = updateDate
        self.type = typ

    def as_payload(issue):
        line = -1
        textRange = []
        effort = '0min'
        debt = '0min'

        if 'line' in issue:
            line = issue['line']
        if 'textRange' in issue:
            textRange = issue['textRange']
        if 'effort' in issue:
            effort = issue['effort']
        if 'debt' in issue:
            debt = issue['debt']

        return Issues(issue['key'], issue['rule'], issue['severity'],
        issue['component'], issue['componentId'], issue['project'],
        line, textRange, issue['flows'], issue['status'],
        issue['message'], effort, debt, issue['assignee'],
        issue['author'], issue['tags'], issue['creationDate'],
        issue['updateDate'], issue['type'])
