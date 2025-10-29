import time
from ConsultaSQL import obtener_nombres,obtener_pedidosRealizados,obtener_precio,obtener_productos,obtener_stock,Insertar_producto,confirmar_pedido,Eliminar_carrito,Modificar_stock,Guardar_producto_cliente,Eliminar_pedido,Eliminar_producto,calcular_total_carrito,get_updates,send_message



MESSAGE_CARGARDATO = "Los datos se ingresaron correctamente"
MESSAGE_MENU_ADMIN = """
Menu Administrador/Comercio:
---------------------------------------------------------------
Elije una opción: 
                6. Consultar productos y precios actualizados\n   
                7. Cargar nuevo producto al catalogo\n
                8.Eliminar producto\n  
                9.Actualizar stock\n
                10. Pedidos realizados
                0.Volver a menu de cliente\n"""
                
MESSAGE_MENU_PRINCIPAL = """
Menu Cliente:
---------------------------------------------------------------
Elije una opción:\n
                1. ver productos disponibles en nuestro catálogo\n
                2. Consultar stock\n
                3. Cargar productos al carrito\n
                4. Eliminar productos del carrito\n
                5. Ver el total del carrito\n
                                """




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
                    send_message(chat_id, "✨ ¡Hola! Bienvenidos a nuestra pasterleria mágica ✨🍰 Gracias por escribirnos. Cada pedido que recibimos es una oportunidad para alegrar tu día con amor, sabor y creatividad. ¿En qué podemos ayudarte hoy?")
                    
                    send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
                    usuarios_saludados.add(chat_id)



#---------------------------------------------------------------------------------------------------------




#---------------------------------------------------------------------------------------------------------



                elif text == "1" and (estado == '' or estado is None):
                    productos = obtener_productos()
                    if productos:
                        mensaje = "productos disponibles:\n"
                        
                        compra = obtener_productos()
                        for producto in compra:
                            mensaje=mensaje+(f"{producto[0]} precio: {producto[1]}\n") 
                    else:
                        mensaje = "No hay productos cargados en el catálogo aún 🍃"
                    send_message(chat_id, mensaje)
                    send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
#--------------------------------------------------------------------------------------------------
                elif text == "2" and (estado == '' or estado is None):
                    send_message(chat_id, "¿De cúal producto deseas saber el stock?")
                    estado_usuario[chat_id] = "esperando_stock_producto" 
                elif estado=="esperando_stock_producto":
                    articulo = text #aca puede estar el posible error
                    stock_articulo = obtener_stock(articulo)#revisar como muestra el precio
                    mensaje = (f" el stock del articulo {articulo} es {stock_articulo[0]}\n")
                    send_message(chat_id, mensaje)
                    send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
                    estado_usuario[chat_id] = "" 

#----------------------------------------------------------------------------------------------------
                elif text == "3" and (estado == '' or estado is None):
                    send_message(chat_id, "🛒 ¿Qué producto te gustaría agregar al carrito?")
                    estado_usuario[chat_id] = "esperando_pedido"

                elif estado == "esperando_pedido":
                    producto = text.strip()

                    tmp = datos_temporales.setdefault(chat_id, {})
                    tmp.setdefault("productos", []).append(producto)

                    if "nombre" in tmp:
                        NomCliente = tmp["nombre"]
                        Guardar_producto_cliente(producto, NomCliente, chat_id)
                        send_message(chat_id, f"Gracias {NomCliente} 💖. Añadimos '{producto}' al carrito.")
                        send_message(chat_id, "¿Deseás agregar otro producto? (Sí / No)")
                        estado_usuario[chat_id] = "confirmar_otro_pedido"
                    else:
                        send_message(chat_id, "🍓 ¡Perfecto! ¿Cuál es tu nombre?")
                        estado_usuario[chat_id] = "esperando_nombre"

                elif estado == "esperando_nombre":
                    NomCliente = text.strip()

                    tmp = datos_temporales.setdefault(chat_id, {})
                    tmp["nombre"] = NomCliente

                    # Asegurar estructura de productos (string -> lista, o lista vacía)
                    productos = tmp.get("productos") or []
                    if isinstance(productos, str):
                        productos = [productos]
                    tmp["productos"] = productos  # normalizado

                    if not productos:
                        send_message(chat_id, f"Gracias {NomCliente}. Aún no tengo productos en tu carrito.")
                        send_message(chat_id, "Decime el primer producto que querés.")
                        estado_usuario[chat_id] = "esperando_pedido"
                        return

                    # Persistir todo lo que ya estaba en el carrito
                    for p in productos:
                        Guardar_producto_cliente(p, NomCliente, chat_id)

                    send_message(chat_id, f"Gracias {NomCliente} 💖. Añadimos {len(productos)} producto(s) al carrito.")
                    send_message(chat_id, "¿Deseás agregar otro producto? (Sí / No)")
                    estado_usuario[chat_id] = "confirmar_otro_pedido"



                elif estado == "confirmar_otro_pedido":
                    if text.lower() in ["sí", "si"]:
                        send_message(chat_id, "🛒 ¿Qué producto te gustaría agregar al carrito?")
                        estado_usuario[chat_id] = "esperando_pedido"
                    elif text.lower() == "no":
                        send_message(chat_id, "¡Gracias por tu pedido!")
                        send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
                        estado_usuario.pop(chat_id, None)
                        datos_temporales.pop(chat_id, None)
                    else:
                        send_message(chat_id, "Por favor respondé con 'Sí' o 'No' 😊")

                elif estado == "confirmar_finalizar_pedido":
                        if text.lower() in ["sí", "si"]:
                            # tmp = datos_temporales.setdefault(chat_id, {})
                            # NomCliente = tmp["nombre"] 
                            lista, total = calcular_total_carrito(chat_id)
                            mensaje,status = confirmar_pedido(chat_id, NomCliente)
                            if status == True:
                                send_message(chat_id, mensaje)
                                send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
                                estado_usuario[chat_id] = ""
                            else:
                                send_message(chat_id, mensaje)
                                send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
                                estado_usuario[chat_id] = ""
                        elif text.lower() == "no":
                            send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
                            estado_usuario[chat_id] = ""
                        else:
                            send_message(chat_id, "Por favor respondé con 'Sí' o 'No' 😊")


#-------------------------------------------------------------------------------
                elif text.lower() == "4" and (estado == '' or estado is None):
                    send_message(chat_id, "🗑️ ¿Qué producto deseas eliminar del carrito?")
                    estado_usuario[chat_id] = "esperando_pedido_eliminado"
                elif estado == "esperando_pedido_eliminado":
                    producto = text
                    if Eliminar_carrito(producto, chat_id):
                        send_message(chat_id, f"✅ El producto '{producto}' fue eliminado de tu carrito.")
                        send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
                        estado_usuario[chat_id] = ""
                    else:
                        send_message(chat_id, f"⚠️ No encontramos '{producto}' en tu carrito.")
                        send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
                        estado_usuario[chat_id] = ""
                        
#-----------------------------------------------------------------------------------------------------------
                elif text == "5" and (estado == '' or estado is None):
                    lista, total = calcular_total_carrito(chat_id)
                    if total == 0:
                        send_message(chat_id, "Tu carrito está vacío.")
                        send_message(chat_id,MESSAGE_MENU_PRINCIPAL)
                    else:
                        mensaje = f"Productos en tu carrito:\n{lista}\n\n🧾 Total: ${total:.2f}\n ¿Desea finalizar el pedido? (Sí / No)"
                        estado_usuario[chat_id] = "confirmar_finalizar_pedido"
                        send_message(chat_id, mensaje)

                        

#---------------------------------------------------------------------------------------------------------------
                elif text == "admin" and (estado == '' or estado is None):
                    send_message(chat_id,MESSAGE_MENU_ADMIN)
                    estado_usuario[chat_id] = "menu_admin"

                elif text == "6" and estado == 'menu_admin':
                    productos = obtener_productos()
                    if productos:
                        mensaje = "productos actualizados:\n"
                        
                        compra = obtener_productos()
                        for producto in compra:
                            mensaje=mensaje+(f"{producto[0]} precio: {producto[1]}\n") 
                    else:
                        mensaje = "No hay productos cargados en el catálogo aún"
                    send_message(chat_id, mensaje)
                    send_message(chat_id,MESSAGE_MENU_ADMIN)

#-------------------------------------------------------------------------------------------------------------------
                elif text.lower() == "7" and estado == 'menu_admin':
                    send_message(chat_id, "🧁 Ingrese el nuevo producto a cargar")
                    estado_usuario[chat_id] = "esperando_producto_vendedor"
                elif estado == "esperando_producto_vendedor":
                    datos_temporales[chat_id] = {"productoCargar": text}
                    send_message(chat_id, f"Coloque un precio para el producto {text}")
                    estado_usuario[chat_id] = "esperando_producto_precio"

                    

                elif estado == "esperando_producto_precio":
                    producto = datos_temporales[chat_id]["productoCargar"]
                    precioCarga = text
                    resultado=Insertar_producto(producto,precioCarga, chat_id)
                    send_message(chat_id, f"El producto {producto} con precio  {precioCarga} fue agregado al sistema")
                    send_message(chat_id,MESSAGE_MENU_ADMIN)
                    estado_usuario[chat_id] = ""
#-------------------------------------------------------------------------------------------------------------   
                elif text.lower() == "8" and estado == 'menu_admin':
                    send_message(chat_id, "Que producto desea eliminar")
                    estado_usuario[chat_id] = "esperando_producto_eliminado"
                elif estado == "esperando_producto_eliminado":
                    datos_temporales[chat_id] = {"productoAborrar": text}
                    producto=text
                    Resultado=Eliminar_producto(producto)
                    send_message(chat_id, f"El producto {producto} fue eliminado del sistema")
                    send_message(chat_id,MESSAGE_MENU_ADMIN)
                    estado_usuario[chat_id] = ""
#--------------------------------------------------------------------------------------------------------------------
                elif text.lower() == "9" and estado == 'menu_admin':
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
                    send_message(chat_id, f"El stock del producto {producto} fue actualizado a {CargaStock} en el sistema")
                    send_message(chat_id,MESSAGE_MENU_ADMIN)
                    estado_usuario[chat_id] = ""

                elif text.lower() == "0" and estado == 'menu_admin':
                    estado_usuario[chat_id] = ""
                    send_message(chat_id,MESSAGE_MENU_PRINCIPAL)

    #--------------------------------------------------------------------------------------------------
                elif text == "10" and estado == 'menu_admin':
                    pedidos = obtener_pedidosRealizados()
                    if pedidos:
                        mensaje = "productos disponibles:\n"
                        
                        compra = obtener_productos()
                        for pedido in pedidos:
                            mensaje=mensaje+(f"----------------\nPedido de  {pedido[0]}\n pedido\n {pedido[1]}\n TOTAL: ${pedido[2]}\n----------------\n") 
                    else:
                        mensaje = "No hay productos cargados en el catálogo aún"
                    send_message(chat_id, mensaje)
                    send_message(chat_id,MESSAGE_MENU_ADMIN)
    #--------------------------------------------------------------------------------------------------











                else:
                    send_message(chat_id, "Inserte una opción válida del menú y tenga encuenta las mayusculas para que podamos ayudarte lo más rápido posible 🍭")
        except Exception as e:#pq despues de cada mensaje me sale esto?
                    print("Error:", e)
        time.sleep(2)
                    
                
                
                
if __name__ == "__main__":
    main()
