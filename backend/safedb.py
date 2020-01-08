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
        
class SelectRequest:
    def __init__(self):
        self.where = {}
        self.avg_request = {}
        self.search_fields = []
        
    def addCondition(self, field, condition):
        self.where[field] = condition
    
    def addAvgCondition(self, fieldname, he_pub):
        self.avg_request[fieldname] = he_pub
        
    def addSearchField(self, field):
        self.search_fields.append(field)
        
       
class InsertRequest:
    def __init__(self):
        self.values = {}
        
    def addValue(self, field, value):
        self.values[field] = value
        
class PostgreRepository:
    def __init__(self, dbname, user, host, password):
        self.dbname = dbname
        self.user = user
        self.host = host
        self.password = password
        
    def select(self, request):
        conn = psycopg2.connect(create_conn_args())
        cursor = conn.cursor()
        cursor.execute(request)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
        
    def insert(self, insert_args):
        conn = psycopg2.connect(create_conn_args())
        cursor = conn.cursor()
        cursor.execute(insert_args[0], insert_args[1])
        conn.commit()
        cursor.close()
        conn.close()
        
    def create_conn_args(self):
        conn_args = "dbname='" + self.dbname
        conn_args += "' user='" + self.user
        conn_args += "' host='" + self.host
        conn_args += "' password='" + self.password + "'"
        return conn_args
        
class RequestBuilder:
    def __init__(self):
        self.fields = {}
        self.fields_array = []
        
    def set_table_name(self, name):
        self.table_name = name
        
    def add_field(self, name, operation):
        field = Field(name, operation)
        self.fields[name] = field
        self.fields_array.append(field)
        return field
        
    def build_insert_args(self, insert_request):
        column_names = ""
        args = []
        for field in insert_request.values.keys():
            column_names += field.name + ", "
            encryptedValue = None
            if field.operation == "=":
                encryptedValue = str_to_number(det_encrypt_string(insert_request.values[field]))
            elif field.operation == ">":
                encryptedValue = ope_encrypt_int(insert_request.values[field])
            elif field.operation == "+":
                encryptedValue = he_encrypt(insert_request.values[field])
            else:
                encryptedValue = insert_request.values[field]
            args.append(encryptedValue)
        column_names = column_names[:-2]
        db_request = "INSERT INTO " + self.table_name + " (" + column_names + ") VALUES (" + ('%s, ' * len(insert_request.values))[:-2] + ")"
        return (db_request, args)
        
    def decrypt_rows(self, rows, select_request):
        if (len(rows) == 0):    
            return rows
        operations = self.form_operations(select_request)
        dRows = []
        if (len(operations) != len(rows[0])):
            raise Exception("Wrong length")
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
        
    def form_operations(self, select_request):
        selecting = []
        if (len(select_request.avg_request) == 0):
            if (len(select_request.search_fields) == 0):
                for field in self.fields_array:
                    selecting.append(field.operation)
            else:
                for field in select_request.search_fields:
                    selecting.append(field.operation)
        else:
            for item in select_request.avg_request:
                selecting.append("+")
            selecting.append("none")
        return selecting
    
    def build_select_request(self, select_request):
        request = "SELECT "
        avg_items = select_request.avg_request.items()
        where = select_request.where.items()
        if (len(avg_items) == 0):
            if (len(select_request.search_fields) == 0):
                request += "* "
            else:
                for field in search_fields:
                    request += field.name + " "
        else:
            for item in avg_items:
                field = item[0]
                he_pub = item[1]
                request += " my_avg_2(" + str(he_pub) + ", " + field.name + ")"
            request += ", count(*) "
        request += "FROM " + self.table_name
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

