import sqlite3

def obtener_precios():
    conn = sqlite3.connect("Reposteria.db")  # Conexión a la base
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, precio FROM productos")  # Solo nombre y precio
    resultados = cursor.fetchall()
    conn.close()
    return resultados

# Mostrar los resultados
precios = obtener_precios()
if precios:
    print("💰 Precios del catálogo:")
    for nombre, precio in precios:
        print(f"• {nombre}: ${precio:.2f}")
else:
    print("No hay productos cargados aún 🍃")