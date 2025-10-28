# bot_basico_requests.py
import os
import time
import requests
import sqlite3

TOKEN = os.getenv("BOT_TOKEN") or "8318202594:AAEyoGmRwRqqG8DjLObHXTM1kZDv-zqE-uY"
API = f"https://api.telegram.org/bot{TOKEN}"

MESSAGE_CARGARDATO = "Los datos se ingresaron correctamente"


def obtener_nombres():
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM productos") 
    nombres = cursor.fetchall()
    conn.close()
    return nombres


def obtener_precio():
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, precio FROM precios")
    nombres = cursor.fetchall()
    conn.close()
    return nombres

def obtener_productos():
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, precio FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos


def obtener_stock(articulo):
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM productos WHERE nombre = ?", (articulo,))
    stock = cursor.fetchall()
    conn.close()
    return stock

def Insertar_producto(producto, costo):
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO productos (nombre, precio, stock)VALUES ('{producto}',{costo}, 0)")
    stock = conn.commit()
    conn.close()
    return stock

def Eliminar_producto(producto):
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE from productos where nombre='{producto}'")
    stock = conn.commit()
    conn.close()
    return stock

def Modificar_stock(producto, stock):
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE productos SET stock={stock} where nombre='{producto}'")
    stock = conn.commit()
    conn.close()
    return stock


def Guardar_producto_cliente(producto,NomCliente):
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO Pedidos (NomCliente, producto,precio,idpedido,precio, stock)VALUES ('{NomCliente}','{producto}',0,0,0,0)")
    stock = conn.commit()
    conn.close()
    return stock

def Eliminar_pedido(producto):
    conn = sqlite3.connect("Reposteria.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE from Pedidos where producto='{producto}'")
    stock = conn.commit()
    conn.close()
    return stock


def get_updates(offset=None, timeout=30):
    params = {"timeout": timeout, "offset": offset}
    r = requests.get(f"{API}/getUpdates", params=params, timeout=timeout+5)
    r.raise_for_status()
    return r.json()["result"]

def send_message(chat_id, text):
    r = requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text})
    r.raise_for_status()

estado_usuario = {}  # Guarda el estado de cada usuario
datos_temporales = {}  # Guarda datos como producto y nombre


def main():
    print("Bot corriendo (requests)…")
    last_update_id = None
#----------------------------------------------------------------------------------------------------
    usuarios_saludados = set()
    while True:
        try:
            
            updates = get_updates(offset=last_update_id+1 if last_update_id else None)
            for u in updates:
                last_update_id = u["update_id"]
                msg = u.get("message") or u.get("edited_message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                #  Opción 1 (recomendada): partition no falla si no hay ":"
                s = text
                izq, sep, der = s.partition(":")
                izq = izq.strip()
                der = der.strip() if sep else ""   # si no había ":", derecha queda vacía
                print(izq)  # -> Insertar pedido
                print(der)  # -> mensaje aleatorio

                # Flujo paso a paso: añadir al carrito
                estado = estado_usuario.get(chat_id)
#--------------------------------------------------------------------------------------------------
                if chat_id not in usuarios_saludados:
                    send_message(chat_id, "✨ ¡Hola! Bienvenid@ a nuestra dulcería mágica ✨🍰 Gracias por escribirnos. Cada pedido que recibimos es una oportunidad para endulzar tu día con amor, sabor y creatividad. ¿En qué delicia podemos ayudarte hoy?")
                    send_message(chat_id, """
Menu Cliente:
---------------------------------------------------------------
Elije una opción:\n
                1. ver productos disponibles en nuestro catálogo\n
                2. Consultar stock\n
                3. Cargar productos al carrito\n
                4. Eliminar productos del carrito\n
                5. Ver el total del carrito\n
                                                                
Menu Comercio:
---------------------------------------------------------------
Elije una opción:     
                5. Cargar nuevo producto al catalogo\n
                6.Eliminar producto\n  
                7.Actualizar stock\n
                                """)
                    usuarios_saludados.add(chat_id)
#---------------------------------------------------------------------------------------------------------



                elif text == "1":
                    productos = obtener_productos()
                    if productos:
                        mensaje = "productos disponibles:\n"
                        
                        compra = obtener_productos()
                        for producto in compra:
                            mensaje=mensaje+(f"{producto[0]} precio: {producto[1]}\n") 
                    else:
                        mensaje = "No hay productos cargados en el catálogo aún 🍃"
                    send_message(chat_id, mensaje)
#--------------------------------------------------------------------------------------------------
                elif text == "2":
                    send_message(chat_id, "¿De cúal producto desas saber el stock?")
                    estado_usuario[chat_id] = "esperando_stock_producto" 
                elif estado=="esperando_stock_producto":
                    articulo = text #aca puede estar el posible error
                    stock_articulo = obtener_stock(articulo)#revisar como muestra el precio
                    mensaje = (f" el stock del articulo {articulo} es {stock_articulo[0]}\n")
                    send_message(chat_id, mensaje)

#----------------------------------------------------------------------------------------------------
                elif text == "3":
                    send_message(chat_id, "🛒 ¿Qué producto te gustaría agregar al carrito?")
                    estado_usuario[chat_id] = "esperando_pedido"

                elif estado == "esperando_pedido":
                    producto = text
    # Guardamos el producto en datos temporales, pero sin borrar lo anterior
                    if chat_id not in datos_temporales:
                        datos_temporales[chat_id] = {}
                        datos_temporales[chat_id]["producto"] = producto

                    if "nombre" in datos_temporales[chat_id]:
                        NomCliente = datos_temporales[chat_id]["nombre"]
                        Guardar_producto_cliente(producto, NomCliente)
                        send_message(chat_id, f"Gracias {NomCliente} 💖. Añadimos '{producto}' al carrito.")
                        send_message(chat_id, "¿Deseás agregar otro producto? (Sí / No)")
                        estado_usuario[chat_id] = "confirmar_otro_pedido"
                    else:
                        send_message(chat_id, "🍓 ¡Perfecto! ¿Cuál es tu nombre?")
                        estado_usuario[chat_id] = "esperando_nombre"

                elif estado == "esperando_nombre":
                    NomCliente = text
                    producto = datos_temporales[chat_id]["producto"]

                # Guardamos el nombre para las próximas veces
                    datos_temporales[chat_id]["nombre"] = NomCliente

                    Guardar_producto_cliente(producto, NomCliente)
                    send_message(chat_id, f"Gracias {NomCliente} 💖. Añadimos '{producto}' al carrito.")
                    send_message(chat_id, "¿Deseás agregar otro producto? (Sí / No)")
                    estado_usuario[chat_id] = "confirmar_otro_pedido"

                elif estado == "confirmar_otro_pedido":
                    if text.lower() in ["sí", "si"]:
                        send_message(chat_id, "🛒 ¿Qué producto te gustaría agregar al carrito?")
                        estado_usuario[chat_id] = "esperando_pedido"
                    elif text.lower() == "no":
                        send_message(chat_id, "🧺 ¡Gracias por tu pedido!")
                        estado_usuario.pop(chat_id, None)
                        datos_temporales.pop(chat_id, None)
                    else:
                        send_message(chat_id, "Por favor respondé con 'Sí' o 'No' 😊")


#-------------------------------------------------------------------------------
                elif text.lower() == "4":
                        send_message(chat_id, "Que producto desea eliminar")
                        estado_usuario[chat_id] = "esperando_pedido_eliminado"
                elif estado == "esperando_pedido_eliminado":
                        datos_temporales[chat_id] = {"pedidoAborrar": text}
                        producto=text
                        Resultado=Eliminar_pedido(producto)
                        send_message(chat_id, f"El producto {producto} fue eliminado del sistema")




#-----------------------------------------------------------------------------------------------------------6
                elif text.lower() == "5":
                    send_message(chat_id, "🧁 Ingrese el nuevo producto a cargar")
                    estado_usuario[chat_id] = "esperando_producto_vendedor"
                elif estado == "esperando_producto_vendedor":
                    datos_temporales[chat_id] = {"productoCargar": text}
                    send_message(chat_id, f"Coloque un precio para el producto {text}")
                    estado_usuario[chat_id] = "esperando_producto_precio"

                    

                elif estado == "esperando_producto_precio":
                    producto = datos_temporales[chat_id]["productoCargar"]
                    precioCarga = text
                    resultado=Insertar_producto(producto,precioCarga)
                    send_message(chat_id, f"El producto {producto} con precio  {precioCarga} fue agregado al sistema")
 #-------------------------------------------------------------------------------------------------------------   
                elif text.lower() == "6":
                    send_message(chat_id, "Que producto desea eliminar")
                    estado_usuario[chat_id] = "esperando_producto_eliminado"
                elif estado == "esperando_producto_eliminado":
                    datos_temporales[chat_id] = {"productoAborrar": text}
                    producto=text
                    Resultado=Eliminar_producto(producto)
                    send_message(chat_id, f"El producto {producto} fue eliminado del sistema")
             
#--------------------------------------------------------------------------------------------------------------------
                elif text.lower() == "7":
                    send_message(chat_id, "Ingrese el producto a modificar")
                    estado_usuario[chat_id] = "esperando_producto_Amodificar"
                elif estado == "esperando_producto_Amodificar":
                    datos_temporales[chat_id] = {"productoAmodificar": text}
                    send_message(chat_id, f"Coloque un stock para el producto {text}")
                    estado_usuario[chat_id] = "esperando_producto_stock"

                    

                elif estado == "esperando_producto_stock":
                    producto = datos_temporales[chat_id]["productoAmodificar"]
                    CargaStock = text
                    resultado=Modificar_stock(producto, CargaStock)
                    send_message(chat_id, f"El producto {producto} con stock  {CargaStock} fue agregado al sistema")














                else:
                    send_message(chat_id, "Inserte una opción válida del menú y tenga encuenta las mayusculas para que podamos ayudarte lo más rápido posible 🍭")
        except Exception as e:#pq despues de cada mensaje me sale esto?
                    print("Error:", e)
        time.sleep(2)
                    
                
                
                
if __name__ == "__main__":
    main()
