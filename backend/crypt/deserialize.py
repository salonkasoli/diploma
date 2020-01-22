# Small module for deserialization
def load(filename):
    try:
        f = open(filename, "r")
        text = f.read()
        f.close()
        return text
    except IOError:
        return None
    

if __name__ == "__main__":
    a = load("text.txt")
    if a == None:
        print "No such file!"
