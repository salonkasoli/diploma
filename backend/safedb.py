
class Field:
    def __init__(self, name, operation):
        self.name = name
        self.operation = operation
        
class Condition:
    def __init__(self, condition, value):
        self.condition = condition
        self.value = value
        
class ConnectorBuilder:

    def __init__(self):
        self.fields = {}
        pass
        
    def addField(self, name, operation):
        field = Field(name, operation)
        self.fileds[name] = field
        return field
        
    def build(self):
        return DBConnector(self.fields)
        
class SafeRequest:
    
    def __init__(self):
        self.regular_request = {}
        self.avg_request = {}
        
    def addCondition(self, field, condition):
        self.regular_request[field] = condition
     
    def addAvgCondition(self, fieldname, he_pub):
        self.avg_request[fieldname] = he_pub
        
    def build(self):
        request = ""
        avg_items = self.avg_request.items()
        regular_items = self.regular_request.items()
        if (len(avg_items) == 0):
            request = """SELECT * FROM test_2 WHERE 1=1"""
        else:
            request = """SELECT """
            for item in avg_items:
                field = item[0]
                he_pub = item[1]
                request += " my_avg_2(" + str(he_pub) + ", " + field.name + ")"
            request += ", count(*) FROM test_2 WHERE 1=1"
        for item in regular_items:
            field = item[0]
            condition = item[1]
            request += ' AND ' + field.name + ' ' + condition.condition + ' ' + condition.value
        return request
        
class DBConnector:

    def __init__(self, fields):
        self.fields = fields
