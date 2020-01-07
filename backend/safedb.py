from convert import str_to_number, number_to_str
import psycopg2

## here import stuff to cypher
from crypt.aes import get_cipher
from crypt.ope import get_ope_cipher
from crypt.pailier import get_he_cipher
from base64 import b64encode, b64decode
import binascii


class Item():
    def __init__(self):
        pass

class Field:
    def __init__(self, name, operation):
        self.name = name
        self.operation = operation
        
class Condition:
    def __init__(self, condition, value):
        self.condition = condition
        self.value = value
        
class SafeRequest:
    def __init__(self):
        self.where = {}
        self.avg_request = {}
        self.search_fields = []
        
    def addCondition(self, field, condition):
        self.where[field] = condition
    
    def addAvgCondition(self, fieldname, he_pub):
        self.avg_request[fieldname] = he_pub
        
       
class InsertRequest:

    def __init__(self):
        # dict Field -> String/Int
        self.values = {}
        
    def addValue(self, field, value):
        self.values[field] = value
        
class SafeDB:

    def __init__(self):
        self.fields = {}
        self.fields_array = []
        
    def addField(self, name, operation):
        field = Field(name, operation)
        self.fields[name] = field
        self.fields_array.append(field)
        return field
        
    def select(self, selectRequest):
        request = self.buildSelect(selectRequest)
        encryptedRequest = self.buildSelectEncrypt(selectRequest)
        print "executing " + request
        print "encrypted " + encryptedRequest
        conn = psycopg2.connect("dbname='test_1' user='ivan' host='localhost' password='qweasdzxc'")
        cursor = conn.cursor()
        cursor.execute(encryptedRequest)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        dRows = self.decryptRows(rows, selectRequest)
        print "drows = " + str(dRows)
        return dRows
        
    def decryptRows(self, rows, selectRequest):
        if (len(rows) == 0):    
            return rows
        operations = self.formOperations(selectRequest)
        dRows = []
        if (len(operations) != len(rows[0])):
            raise Exception("wrong length")
        j = 0
        for row in rows:
            dRow = []
            dRows.append(dRow)
            i = 0
            while i < len(operations):
                decryptedValue = None
                if operations[i] == "=":
                    decryptedValue = det_decrypt_string(number_to_str(row[i]))
                elif operations[i] == ">":
                    decryptedValue = ope_decrypt_int(int(row[i]))
                elif operations[i] == "+":
                    decryptedValue = he_decrypt(int(row[i]))
                else:
                    decryptedValue = row[i]
                dRow.append(decryptedValue)
                i += 1
            j += 1
        return dRows
        
    def formOperations(self, selectRequest):
        selecting = []
        if (len(selectRequest.avg_request) == 0):
            if (len(selectRequest.search_fields) == 0):
                for field in self.fields_array:
                    selecting.append(field.operation)
            else:
                for field in selectRequest.search_fields:
                    selecting.append(field.operation)
        else:
            for item in selectRequest.avg_request:
                selecting.append("+")
            selecting.append("none")
        print "formed operations = " + str(selecting)
        return selecting
        
    def insert(self, insertRequest):
        print "inserting " + str(insertRequest.values)
        #conn = psycopg2.connect("dbname='test_1' user='ivan' host='localhost' password='qweasdzxc'")
        #cursor = conn.cursor()
        #request = """INSERT INTO test_2 (name, age, therapy_duration, gen_before, gen_after, is_effective) VALUES (%s, %s, %s, %s, %s, %s)"""
        #args = (name, age, therapy_duration, gen_before, gen_after, is_effective)
        #cursor.execute(request, args)
        #conn.commit()
        #cursor.close()
        #conn.close()
        
    def buildSelect(self, selectRequest):
        request = "SELECT "
        avg_items = selectRequest.avg_request.items()
        where = selectRequest.where.items()
        if (len(avg_items) == 0):
            if (len(selectRequest.search_fields) == 0):
                request += "* "
            else:
                for field in search_fields:
                    request += field.name + " "
            request += "FROM test_2"
        else:
            for item in avg_items:
                field = item[0]
                he_pub = item[1]
                request += " my_avg_2(" + str(he_pub) + ", " + field.name + ")"
            request += ", count(*) FROM test_2"
        if (len(where) != 0):
            request += "WHERE 1=1"
            for item in where:
                field = item[0]
                condition = item[1]
                request += ' AND ' + field.name + ' ' + condition.condition + ' ' + condition.value
        return request
        
    def buildSelectEncrypt(self, selectRequest):
        request = "SELECT "
        avg_items = selectRequest.avg_request.items()
        where = selectRequest.where.items()
        if (len(avg_items) == 0):
            if (len(selectRequest.search_fields) == 0):
                request += "* "
            else:
                for field in search_fields:
                    request += field.name + " "
            request += "FROM test_2 "
        else:
            for item in avg_items:
                field = item[0]
                he_pub = item[1]
                request += " my_avg_2(" + str(he_pub) + ", " + field.name + ")"
            request += ", count(*) FROM test_2 "
        if (len(where) != 0):
            request += "WHERE 1=1"
            for item in where:
                field = item[0]
                condition = item[1]
                encryptedValue = None
                if (field.operation == "="):
                    encryptedValue = str_to_number(det_encrypt_string(str(condition.value)))
                elif (field.operation == ">"):
                    encryptedValue = ope_encrypt_int(int(condition.value))
                else:
                    raise Exception('invalid operation')
                request += ' AND ' + field.name + ' ' + condition.condition + ' ' + str(encryptedValue)
        return request
        
        
def det_encrypt_string(s):
    cipher = get_cipher()
    ct = cipher.encrypt(bytes(s))
    return b64encode(ct)
    
def det_decrypt_string(s):
    ct = b64decode(s)
    cipher = get_cipher()
    pt = cipher.decrypt(ct)
    return pt
    
def ope_encrypt_int(value):
    cipher = get_ope_cipher()
    return cipher.encrypt(value)
    
def ope_decrypt_int(value):
    cipher = get_ope_cipher()
    return cipher.decrypt(value)
    
def he_encrypt(value):
    cipher = get_he_cipher()
    return cipher.encrypt(value)

def he_decrypt(value):
    cipher = get_he_cipher()
    return cipher.decrypt(value)

