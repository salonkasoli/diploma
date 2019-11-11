def save(filename, text):
    f = open(filename, "w+")
    f.write(text)
    f.close()
 
 
if __name__ == "__main__":   
    save("text.txt", "lol")
