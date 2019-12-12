import psycopg2

class Request:
    min_age = None
    max_age = None
    is_effective = None
    name = None
    min_therapy_duration = None
    max_therapy_duration = None
    avg_gen_before = None
    avg_gen_after = None
    he_pub = None
    
    def build(self):
        request = ""
        if (self.avg_gen_before == None):
            request = """SELECT * FROM test_2 WHERE 1=1"""
        else:
            request = """SELECT my_avg_2(""" + str(self.he_pub) + """, gen_before), count(gen_before) FROM test_2 WHERE 1=1"""
        
        if (self.min_age != None):
            request += ' AND age > ' + str(self.min_age)
        if (self.max_age != None):
            request += ' AND age < ' + str(self.max_age)
        if (self.is_effective != None):
            request += ' AND is_effective = ' + str(self.is_effective)
        if (self.name != None):
            request += ' AND name = ' + str(self.name)
        if (self.min_therapy_duration != None):
            request += ' AND therapy_duration > ' + str(self.min_therapy_duration)
        if (self.max_therapy_duration != None):
            request += ' AND therapy_duration < ' + str(self.max_therapy_duration)
        return request


def insert(name, age, therapy_duration, gen_before, gen_after, is_effective):
    conn = psycopg2.connect("dbname='test_1' user='ivan' host='localhost' password='qweasdzxc'")
    cursor = conn.cursor()
    request = """INSERT INTO test_2 (name, age, therapy_duration, gen_before, gen_after, is_effective) VALUES (%s, %s, %s, %s, %s, %s)"""
    args = (name, age, therapy_duration, gen_before, gen_after, is_effective)
    cursor.execute(request, args)
    conn.commit()
    cursor.close()
    conn.close()
    
def select(request):
    conn = psycopg2.connect("dbname='test_1' user='ivan' host='localhost' password='qweasdzxc'")
    cursor = conn.cursor()
    cursor.execute(request.build())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
    
