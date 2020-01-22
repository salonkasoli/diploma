import psycopg2

# Legacy class. Use it, because safedb module cant work with unencrypted db.
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
    
    def build(self, base = 'test_2'):
        request = ""
        if (self.avg_gen_before == None and self.avg_gen_after == None):
            request = """SELECT * FROM """ + base + """ WHERE 1=1"""
        else:
            request = """SELECT """
            if (base == 'test_2'):
                if (self.avg_gen_before != None): 
                    request += """ my_avg_2(""" + str(self.he_pub) + """, gen_before)"""
                if (self.avg_gen_after != None):
                    if (self.avg_gen_before != None):
                        request += ','
                    request += """ my_avg_2(""" + str(self.he_pub) + """, gen_after)"""
                request += """, count(gen_after) FROM test_2 WHERE 1=1"""
                #request += """ FROM test_2 WHERE 1=1"""
            else:
                request += ' avg(gen_before) FROM test_clear WHERE 1=1'
        
        if (self.min_age != None):
            request += ' AND age > ' + str(self.min_age)
        if (self.max_age != None):
            request += ' AND age < ' + str(self.max_age)
        if (self.is_effective != None):
            request += ' AND is_effective = '
            if base == 'test_clear':
                request += "'"
            request += str(self.is_effective)
            if base == 'test_clear':
                request += "'"
        if (self.name != None):
            request += ' AND name = ' 
            if base == 'test_clear':
                request += "'"
            request += str(self.name)
            if base == 'test_clear':
                request += "'"
        if (self.min_therapy_duration != None):
            request += ' AND therapy_duration > ' + str(self.min_therapy_duration)
        if (self.max_therapy_duration != None):
            request += ' AND therapy_duration < ' + str(self.max_therapy_duration)
        return request


def insert(name, age, therapy_duration, gen_before, gen_after, is_effective, base = 'test_2'):
    conn = psycopg2.connect("dbname='test_1' user='ivan' host='localhost' password='qweasdzxc'")
    cursor = conn.cursor()
    request = """INSERT INTO """ + base + """ (name, age, therapy_duration, gen_before, gen_after, is_effective) VALUES (%s, %s, %s, %s, %s, %s)"""
    args = (name, age, therapy_duration, gen_before, gen_after, is_effective)
    cursor.execute(request, args)
    conn.commit()
    cursor.close()
    conn.close()
    
def select(request, base = "test_2"):
    conn = psycopg2.connect("dbname='test_1' user='ivan' host='localhost' password='qweasdzxc'")
    cursor = conn.cursor()
    print 'actual = ' + request.build()
    req = request.build(base)
    cursor.execute(req)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
    
