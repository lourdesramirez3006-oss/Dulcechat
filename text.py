import sqlite3
def obtener_productos():
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, precio FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

compra = obtener_productos()
for producto in compra:
    print (producto[0])
    print (producto[1])