from convert import str_to_number, number_to_str
import psycopg2

## here import stuff to cipher
from crypt.aes import get_cipher
from crypt.ope import get_ope_cipher
from crypt.pailier import get_he_cipher
from base64 import b64encode, b64decode
import binascii


class Item():
    def __init__(self):
        pass

# A class to init RequestBuilder.
class Field:
    # Operation have to be one of:
    # + - for HE enc
    # = - for DET enc
    # > - for OPE enc
    # none - for skip enc
    def __init__(self, name, operation):
        self.name = name
        self.operation = operation
        
# A class to build conditions with SelectRequest
# for example, you can pass Condition("=", "Ivan Anatolyevich")
# to find Ivan ;]
class Condition:
    def __init__(self, condition, value):
        self.condition = condition
        self.value = value
        
# A class to perform select requests on PostgreSQL
class SelectRequest:
    def __init__(self):
        self.where = {}
        self.avg_requests = []
        self.search_fields = []
        
    # add WHERE condition.
    # field must be a Filed, you passed to add_field while init RequestBuilder.
    # field operation must be = or >
    # condition is a Condition.
    def add_condition(self, field, condition):
        self.where[field] = condition
    
    # add AVG() function.
    # field must be a Filed, you passed to add_field while init RequestBuilder.
    # field operation must be "+"!!
    def add_avg_request(self, field):
        self.avg_requests.append(field)
        
    # You can specify fields, you are looking for in SELECT.
    # field must be a Filed, you passed to add_field while init RequestBuilder.
    def add_search_field(self, field):
        self.search_fields.append(field)
        

# A class to build an insert request to PostgreSQL.
class InsertRequest:
    def __init__(self):
        self.values = {}
        
    # You must add all nonnull fields, which was inited in RequestBuilder
    def addValue(self, field, value):
        self.values[field] = value
        
# This class can help you to connect with Postgre.
# it supports select and insert requests.
class PostgreRepository:
    def __init__(self, dbname, user, host, password):
        self.dbname = dbname
        self.user = user
        self.host = host
        self.password = password
        
    def select(self, request):
        conn = psycopg2.connect(self.create_conn_args())
        cursor = conn.cursor()
        cursor.execute(request)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
        
    def insert(self, insert_args):
        conn = psycopg2.connect(self.create_conn_args())
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
      
# The main class of library.
class RequestBuilder:
    def __init__(self):
        self.fields = {}
        self.fields_array = []
        
    # You must specify table name, which you are using in your app.
    def set_table_name(self, name):
        self.table_name = name
        
    # You must specify all fields, that you are going to insert/select 
    # while using this class
    def add_field(self, name, operation):
        field = Field(name, operation)
        self.fields[name] = field
        self.fields_array.append(field)
        return field
        
    # Before make INSERT request, you must transorm it to encrypt all values.
    def build_insert_args(self, insert_request):
        column_names = ""
        args = []
        for field in insert_request.values.keys():
            column_names += field.name + ", "
            enc_val = None
            if field.operation == "=":
                enc_val = str_to_number(det_encrypt_string(insert_request.values[field]))
            elif field.operation == ">":
                enc_val = ope_encrypt_int(insert_request.values[field])
            elif field.operation == "+":
                enc_val = he_encrypt_int(insert_request.values[field])
            else:
                enc_val = insert_request.values[field]
            args.append(enc_val)
        column_names = column_names[:-2]
        args_str = ('%s, ' * len(insert_request.values))[:-2]
        db_request = "INSERT INTO " + self.table_name
        db_request += " (" + column_names + ") VALUES (" 
        db_request += args_str + ")"
        return (db_request, args)
        
    # After SELECT request is successfully finished, you have to decrypt all fields.
    # Pass rows, that was returned by request and SelectRequest, which you used to 
    # create request. This function decrypts all values.
    def decrypt_rows(self, rows, select_request):
        if (len(rows) == 0):    
            return rows
        operations = self.form_operations(select_request)
        d_rows = []
        if (len(operations) != len(rows[0])):
            raise Exception("Wrong length")
        if len(select_request.avg_requests) > 0:
            j = 0
            last_index = len(select_request.avg_requests)
            row = rows[0]
            d_row = []
            while j < last_index:
                d_row.append(he_decrypt(int(row[j])) / int(row[last_index]))
                j += 1
            d_rows.append(d_row)
            return d_rows
        j = 0
        for row in rows:
            d_row = []
            d_rows.append(d_row)
            i = 0
            while i < len(operations):
                dec_value = None
                if operations[i] == "=":
                    dec_value = det_decrypt_string(number_to_str(row[i]))
                elif operations[i] == ">":
                    dec_value = ope_decrypt_int(int(row[i]))
                elif operations[i] == "+":
                    dec_value = he_decrypt(int(row[i]))
                else:
                    dec_value = row[i]
                d_row.append(dec_value)
                i += 1
            j += 1
        return d_rows
        
    # private helper foo to form overations in select request.
    def form_operations(self, select_request):
        selecting = []
        if (len(select_request.avg_requests) == 0):
            if (len(select_request.search_fields) == 0):
                for field in self.fields_array:
                    selecting.append(field.operation)
            else:
                for field in select_request.search_fields:
                    selecting.append(field.operation)
        else:
            for item in select_request.avg_requests:
                selecting.append("+")
            selecting.append("none")
        return selecting
    
    # Encrypts all values an form a SELECT request. You can pass it to PostgreRepository or send by yourself.
    def build_select_request(self, select_request):
        request = "SELECT "
        avg_requests = select_request.avg_requests
        where = select_request.where.items()
        if (len(avg_requests) == 0):
            if (len(select_request.search_fields) == 0):
                request += "* "
            else:
                for field in search_fields:
                    request += field.name + " "
        else:
            he_cipher = get_he_cipher()
            he_pub = he_cipher.pub.n ** 2
            for field in avg_requests:
                request += " my_avg_2(" + str(he_pub) + ", " + field.name + ")"
            request += ", count(*) "
        request += "FROM " + self.table_name + " "
        if (len(where) != 0):
            request += "WHERE 1=1"
            for item in where:
                field = item[0]
                condition = item[1]
                enc_value = None
                if (field.operation == "="):
                    enc_value = str_to_number(det_encrypt_string(str(condition.value)))
                elif (field.operation == ">"):
                    enc_value = ope_encrypt_int(int(condition.value))
                else:
                    raise Exception('invalid operation')
                request += ' AND ' + field.name + ' ' + condition.condition + ' ' + str(enc_value)
        return request
        
      
###########################################################################
################### SOME HELPER FUNCTIONS #################################
###########################################################################
  
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
    
def he_encrypt_int(value):
    cipher = get_he_cipher()
    return cipher.encrypt(value)

def he_decrypt(value):
    cipher = get_he_cipher()
    return cipher.decrypt(value)

