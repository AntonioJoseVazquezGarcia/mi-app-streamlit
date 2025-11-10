import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta

# ==========================================================
# PARÁMETROS GLOBALES Y DE MODELO
# ==========================================================

NUM_DIAS_SIMULACION = 28  # Horizonte de 4 semanas
NOMBRES_DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
DIAS_SEMANA = 7

# Definición de consumibles (los valores de stock_inicial y consumos se rellenan con Streamlit)
CONSUMIBLES_SETUP = {
    "contenedor": {
        "nombre": "Contenedor",
        "plazo_entrega_dias": 16,
        "cantidad_pedido": 288,
        "stock_inicial": 0,  # Se inicializa a 0, luego se actualiza con el widget
        "consumos_diarios": [], 
        "color": "blue"
    },
    "base_contenedor": {
        "nombre": "Base Contenedor",
        "plazo_entrega_dias": 16,
        "cantidad_pedido": 1000,
        "stock_inicial": 0,
        "consumos_diarios": [],
        "color": "green"
    }
}

# ==========================================================
# FUNCIONES AUXILIARES DE CÁLCULO
# ==========================================================

def get_default_daily_consumption(key, dia_nombre):
    """Devuelve el consumo diario por defecto según el enunciado."""
    if key == "contenedor":
        if dia_nombre == "Lunes": return 80
        elif dia_nombre in ["Martes", "Miércoles", "Jueves", "Viernes"]: return 40
        else: return 0
    elif key == "base_contenedor":
        if dia_nombre == "Lunes": return 160
        elif dia_nombre in ["Martes", "Miércoles", "Jueves", "Viernes"]: return 80
        else: return 0
    return 0

def calcular_dia_pedido_optimo(stock_actual, consumos_semanales, plazo_entrega, dias_semana=7):
    """
    Calcula el día (índice 0, 1, 2...) en que se debe hacer un pedido para evitar un quiebre de stock.
    Proyecta los consumos hasta un horizonte de 8 semanas.
    """
    temp_stock = stock_actual
    DIAS_PROYECCION = 8 * dias_semana 
    
    consumos_proyectados_largos = (consumos_semanales * (DIAS_PROYECCION // dias_semana + 1))[:DIAS_PROYECCION]
    
    dia_de_quiebre = -1
    
    # 1. Encontrar el día de quiebre
    for dia_idx in range(DIAS_PROYECCION):
        consumo_hoy = consumos_proyectados_largos[dia_idx]
        temp_stock -= consumo_hoy
        
        if temp_stock <= 0:
            dia_de_quiebre = dia_idx
            break
    
    if dia_de_quiebre == -1:
        return None, DIAS_PROYECCION 
    
    # 2. Calcular el día de pedido (Fecha de quiebre - Plazo de entrega)
    dia_pedido_optimo = max(0, dia_de_quiebre - plazo_entrega)
            
    return dia_pedido_optimo, dia_de_quiebre

# ==========================================================
# FUNCIÓN PRINCIPAL DE STREAMLIT
# ==========================================================

def app():
    st.set_page_config(layout="wide")
    st.title("📦 Simulación de Inventario y Pedidos (4 Semanas)")
    st.sidebar.header("⚙️ Configuración de la Simulación")

    # --- 1. ENTRADA DE FECHA Y STOCK (Sidebar) ---
    
    fecha_inicial = st.sidebar.date_input(
        "📅 Fecha de inicio de la simulación (Día 1)",
        date.today(),
        help="Los días de la semana y las fechas concretas se calculan a partir de aquí."
    )
    
    st.sidebar.subheader("Stock Inicial")
    stock_c = st.sidebar.number_input(
        f"Stock de {CONSUMIBLES_SETUP['contenedor']['nombre']}", 
        min_value=0, 
        value=100,
        step=1
    )
    stock_b = st.sidebar.number_input(
        f"Stock de {CONSUMIBLES_SETUP['base_contenedor']['nombre']}", 
        min_value=0, 
        value=200,
        step=1
    )
    
    # Actualizar los parámetros con los valores de los widgets
    CONSUMIBLES_SETUP['contenedor']['stock_inicial'] = stock_c
    CONSUMIBLES_SETUP['base_contenedor']['stock_inicial'] = stock_b

    # --- 2. ENTRADA DE CONSUMOS (Sidebar - Expandible) ---

    with st.sidebar.expander("📉 Programar Consumos Diarios (Patrón Semanal)"):
        st.write("Introduce el consumo esperado para cada día de la semana (se repetirá durante 4 semanas).")

        for key, params in CONSUMIBLES_SETUP.items():
            st.subheader(f"{params['nombre']} ({params['cantidad_pedido']}u por pedido)")
            consumos_temp = []
            cols = st.columns(DIAS_SEMANA)
            
            for i, dia_nombre in enumerate(NOMBRES_DIAS):
                default_val = get_default_daily_consumption(key, dia_nombre)
                
                consumo = cols[i].number_input(
                    dia_nombre, 
                    min_value=0, 
                    value=default_val, 
                    key=f"consumo_{key}_{i}"
                )
                consumos_temp.append(consumo)
            
            params["consumos_diarios"] = consumos_temp
    
    # Botón para ejecutar el cálculo (la lógica se ejecuta al cambiar cualquier widget, pero es bueno tener un botón explícito)
    st.sidebar.markdown("---")
    st.sidebar.button("▶️ Ejecutar Simulación y Planificación")


    # ==========================================================
    # 3. CÁLCULO DE PLANIFICACIÓN
    # ==========================================================

    st.header("1. 📅 Planificación Óptima de Pedidos")
    
    pedidos_planificados = {} 

    for key, params in CONSUMIBLES_SETUP.items():
        dia_pedido_optimo, dia_de_quiebre = calcular_dia_pedido_optimo(
            params['stock_inicial'],
            params['consumos_diarios'],
            params['plazo_entrega_dias'],
            DIAS_SEMANA 
        )
        
        if dia_pedido_optimo is not None:
            fecha_pedido_concreta = fecha_inicial + timedelta(days=dia_pedido_optimo)
            dia_relativo = dia_pedido_optimo % DIAS_SEMANA
            dia_nombre_plan = NOMBRES_DIAS[dia_relativo]
            
            pedidos_planificados[key] = {
                "dia_simulacion": dia_pedido_optimo,
                "fecha": fecha_pedido_concreta,
                "cantidad": params['cantidad_pedido']
            }
            
            st.success(f"**{params['nombre']}** ({params['plazo_entrega_dias']} días de Lead Time)")
            st.markdown(
                f"""
                - **Quiebre Previsto:** Día {dia_de_quiebre + 1} del horizonte.
                - **Próximo Pedido Óptimo:** Día absoluto {dia_pedido_optimo + 1}.
                - **🗓️ FECHA CONCRETA:** **{dia_nombre_plan}, {fecha_pedido_concreta.strftime('%d/%m/%Y')}** (Pedido de {params['cantidad_pedido']} unidades).
                """
            )
            
        else:
            st.info(f"**{params['nombre']}**: No es necesario hacer un pedido en las próximas 8 semanas con el stock y consumos actuales.")

    # ==========================================================
    # 4. SIMULACIÓN Y VISUALIZACIÓN
    # ==========================================================

    st.header("2. 📊 Evolución del Stock (4 Semanas)")

    # Variables de estado inicial
    stocks_actuales = {k: v["stock_inicial"] for k, v in CONSUMIBLES_SETUP.items()}
    pedidos_en_transito = {k: [] for k in CONSUMIBLES_SETUP.keys()} 
    historial_stock = {k: [v["stock_inicial"]] for k, v in CONSUMIBLES_SETUP.items()}
    
    # Opcional: Mostrar la simulación detallada en un expansor
    with st.expander("Ver Log de Simulación Diaria (28 Días)"):
        log = ""
        
        for dia_indice in range(NUM_DIAS_SIMULACION):
            dia_de_la_semana = dia_indice % DIAS_SEMANA
            dia_nombre = NOMBRES_DIAS[dia_de_la_semana]
            fecha_actual = fecha_inicial + timedelta(days=dia_indice) 

            log += f"\n===== {dia_nombre}, {fecha_actual.strftime('%d/%m/%Y')} (Día {dia_indice + 1}) =====\n"

            for key, params in CONSUMIBLES_SETUP.items():
                consumo_del_dia = params["consumos_diarios"][dia_de_la_semana]
                stock_antes_recibir = stocks_actuales[key]
                
                # 1. RECIBIR PEDIDOS 📦
                entregas_hoy = sum(p["cantidad"] for p in pedidos_en_transito[key] if p["dia_llegada"] == dia_indice)
                stocks_actuales[key] += entregas_hoy
                pedidos_en_transito[key] = [p for p in pedidos_en_transito[key] if p["dia_llegada"] != dia_indice]
                
                # 2. REGISTRAR CONSUMO 📉
                stocks_actuales[key] -= consumo_del_dia
                
                log += f"  {params['nombre']}: Inicio: {stock_antes_recibir}, Recibido: {entregas_hoy}, Consumido: {consumo_del_dia}, Final: {stocks_actuales[key]:.0f}\n"

                # 3. GENERAR NUEVO PEDIDO (Basado en la planificación óptima) 🛒
                if key in pedidos_planificados and dia_indice == pedidos_planificados[key]["dia_simulacion"]:
                    dia_llegada_nuevo_pedido = dia_indice + params["plazo_entrega_dias"]
                    fecha_llegada_concreta = fecha_inicial + timedelta(days=dia_llegada_nuevo_pedido)
                    
                    nuevo_pedido = {"cantidad": params["cantidad_pedido"], "dia_llegada": dia_llegada_nuevo_pedido}
                    pedidos_en_transito[key].append(nuevo_pedido)
                    
                    log += f"  🛒 **PEDIDO REALIZADO** {params['nombre']}: {params['cantidad_pedido']}u. Llega {fecha_llegada_concreta.strftime('%d/%m/%Y')}.\n"
                
                if stocks_actuales[key] < 0:
                    log += f"  ❌ ¡QUIEBRE DE STOCK! Faltaron {abs(stocks_actuales[key]):.0f} unidades.\n"
                    stocks_actuales[key] = 0 

                historial_stock[key].append(stocks_actuales[key]) 
        
        st.code(log)

    # --- 4.1 GENERACIÓN DE GRÁFICA ---

    dias_eje_x = np.arange(NUM_DIAS_SIMULACION + 1)
    
    fig, ax = plt.subplots(figsize=(15, 7))
    
    # Preparamos las etiquetas del eje X
    eje_x_labels = []
    eje_x_ticks = []
    
    eje_x_labels.append(f"Inicio\n{fecha_inicial.strftime('%d/%m')}")
    eje_x_ticks.append(0)
    
    for i in range(1, 5):
        dia_tick = i * DIAS_SEMANA
        fecha_tick = fecha_inicial + timedelta(days=dia_tick -1) # Etiqueta al final de la semana
        eje_x_labels.append(f"Fin S{i}\n{fecha_tick.strftime('%d/%m')}")
        eje_x_ticks.append(dia_tick)

    # Graficar líneas de stock
    for key, params in CONSUMIBLES_SETUP.items():
        ax.plot(dias_eje_x, historial_stock[key], label=f"{params['nombre']} (Stock)", color=params['color'], marker='.', linewidth=2)

        # Señalar Puntos de Pedido Planificados
        if key in pedidos_planificados:
            p = pedidos_planificados[key]
            stock_en_pedido = historial_stock[key][p['dia_simulacion']]
            
            # Anotación y marcador
            ax.scatter(p['dia_simulacion'], stock_en_pedido, color='red', s=150, marker='X', zorder=5)
            
            # Ajuste de posición de la etiqueta para evitar solapamiento
            xytext_c = (-50, 20) if key == 'contenedor' else (50, -20)
            bbox_fc = "yellow" if key == 'contenedor' else "cyan"

            ax.annotate(f"PEDIDO {params['nombre'][:4].upper()}\n{p['fecha'].strftime('%d/%m')}",
                        (p['dia_simulacion'], stock_en_pedido), 
                        textcoords="offset points", 
                        xytext=xytext_c, 
                        ha='center', 
                        fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.3", fc=bbox_fc, alpha=0.7),
                        arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))
    

    # Configuración final del gráfico
    ax.set_title(f'Evolución de Stock y Pedidos (4 Semanas) | Inicio: {fecha_inicial.strftime("%d/%m/%Y")}', fontsize=14)
    ax.set_xlabel('Día de Simulación', fontsize=12)
    ax.set_ylabel('Nivel de Stock (Unidades)', fontsize=12)
    
    ax.set_xticks(eje_x_ticks) 
    ax.set_xticklabels(eje_x_labels) 
    
    for i in range(1, 4):
        ax.axvline(x=i * DIAS_SEMANA, color='gray', linestyle='--', linewidth=0.8)

    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    plt.tight_layout()
    
    # Muestra el gráfico en Streamlit
    st.pyplot(fig)


if __name__ == "__main__":
    app()

    # To run the app, use the command:  
    # python3 -m streamlit run PedidosHerta0.py