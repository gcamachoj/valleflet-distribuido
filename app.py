import streamlit as st
import random
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="ValleFlet - Sistema Distribuido de Fletes",
    page_icon="🚚",
    layout="wide"
)

# Inicializar estado de la sesión (Simulación de Nodos y Red en Memoria)
if "nodos_conectados" not in st.session_state:
    st.session_state.nodos_conectados = [
        {"id": "Nodo_Conductor_01", "vehiculo": "Turbo NHR", "zona": "Yumbo - Cali", "estado": "Activo"},
        {"id": "Nodo_Conductor_02", "vehiculo": "Camión NPR", "zona": "Jamundí - Palmira", "estado": "Activo"},
        {"id": "Nodo_Conductor_03", "vehiculo": "Minimula", "zona": "Buenaventura - Cali", "estado": "Activo"}
    ]

if "historial_pujas" not in st.session_state:
    st.session_state.historial_pujas = [
        {"timestamp": "18:30:10", "nodo": "Nodo_Conductor_01", "flete": "Ruta Yumbo -> Cali", "puja": "$320.000 COP"},
        {"timestamp": "18:31:05", "nodo": "Nodo_Conductor_02", "flete": "Ruta Jamundí -> Aeropuerto", "puja": "$180.000 COP"}
    ]

if "fletes_disponibles" not in st.session_state:
    st.session_state.fletes_disponibles = [
        {"ruta": "Yumbo -> Zona Franca", "tipo": "Carga Pesada", "valor_base": 350000, "estado": "Activo"},
        {"ruta": "Cali Norte -> Jamundí", "tipo": "Paqueteo", "valor_base": 200000, "estado": "Activo"},
        {"ruta": "Palmira -> Buenaventura", "tipo": "Contenedor", "valor_base": 800000, "estado": "Activo"}
    ]

st.title("🚚 ValleFlet: Arquitectura Distribuida para Fletes P2P")
st.markdown("*Simulador interactivo bajo patrones de diseño (Mediator y Observer) para la gestión concurrente de nodos y hilos en el Valle del Cauca.*")

# Pestañas principales (4 variables para 4 pestañas)
tab_servidor, tab_cliente, tab_publicar, tab_arquitectura = st.tabs([
    "🖥️ Nodo Servidor Central (Mediator)", 
    "📱 Nodos Clientes (Conductores)", 
    "📦 Publicar Nuevo Flete (Cliente)",
    "📐 Arquitectura y UML"
])

with tab_servidor:
    st.header("Panel de Control del Servidor Central")
    st.info("El Servidor actúa como **Mediator**, centralizando las peticiones y aplicando un patrón **Observer** para el broadcast de alertas a los hilos activos.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Estado de la Red Distribuida")
        st.metric(label="Nodos Activos en la Red", value=len(st.session_state.nodos_conectados))
        st.metric(label="Pujas Procesadas", value=len(st.session_state.historial_pujas))
        st.metric(label="Fletes en Bolsa", value=len(st.session_state.fletes_disponibles))
        
        if st.button("🔄 Refrescar Estado"):
            st.rerun()

    with col2:
        st.subheader("📡 Log de Eventos en Tiempo Real (Broadcast)")
        log_container = st.container(height=250)
        with log_container:
            for evento in reversed(st.session_state.historial_pujas):
                st.text(f"[{evento['timestamp']}] ({evento['nodo']}) ofertó para {evento['flete']}: {evento['puja']}")

with tab_cliente:
    st.header("Simulador de Nodo Conductor (Cliente P2P)")
    st.markdown("Selecciona un nodo conductor activo y emite una puja concurrente.")
    
    nodos_disponibles = [n["id"] for n in st.session_state.nodos_conectados]
    nodo_seleccionado = st.selectbox("Seleccionar Nodo Conductor:", nodos_disponibles)
    
    info_nodo = next(n for n in st.session_state.nodos_conectados if n["id"] == nodo_seleccionado)
    st.caption(f"Vehículo: **{info_nodo['vehiculo']}** | Zona: **{info_nodo['zona']}**")
    
    # Extraer rutas de la bolsa dinámica
    lista_fletes_str = [f"{f['ruta']} ({f['tipo']}) - Base: ${f['valor_base']:,.0f}" for f in st.session_state.fletes_disponibles]
    
    with st.form(key="form_puja"):
        flete_objetivo = st.selectbox("Flete Disponible en la Bolsa:", lista_fletes_str)
        oferta_precio = st.number_input("Valor de la Puja (COP):", min_value=50000, max_value=5000000, step=50000, value=350000)
        
        submit_button = st.form_submit_button(label="⚡ Enviar Puja Concurrente")
        
        if submit_button:
            hora_actual = datetime.now().strftime("%H:%M:%S")
            nueva_puja = {
                "timestamp": hora_actual,
                "nodo": nodo_seleccionado,
                "flete": flete_objetivo.split(" (")[0],
                "puja": f"${oferta_precio:,.0f} COP"
            }
            st.session_state.historial_pujas.append(nueva_puja)
            st.success(f"¡Puja enviada exitosamente desde el hilo del {nodo_seleccionado}!")
            st.balloons()

with tab_publicar:
    st.header("Publicar Nuevo Flete en la Bolsa")
    st.markdown("Permite a los generadores de carga registrar ofertas de transporte para el corredor logístico del Valle del Cauca.")
    
    with st.form("form_nuevo_flete_cliente"):
        origen = st.selectbox("Ciudad de Origen", ["Cali", "Yumbo", "Jamundí", "Palmira", "Buenaventura", "Buga", "Tuluá"])
        destino = st.selectbox("Ciudad de Destino", ["Buenaventura", "Cali", "Aeropuerto", "Palmira", "Yumbo", "Ipiales"])
        tipo_carga = st.selectbox("Tipo de Carga", ["Carga Seca / Contenedor", "Carga Refrigerada", "Carga Masiva / Granel", "Paquetería Industrial"])
        valor_base = st.number_input("Valor Base Propuesto (COP)", min_value=50000, step=10000, value=200000)
        
        btn_publicar = st.form_submit_button("Publicar Flete en la Red")
        
        if btn_publicar:
            nueva_ruta = f"{origen} -> {destino}"
            st.session_state.fletes_disponibles.append({
                "ruta": nueva_ruta,
                "tipo": tipo_carga,
                "valor_base": valor_base,
                "estado": "Activo"
            })
            st.success(f"¡Flete de {nueva_ruta} publicado con éxito en la bolsa compartida!")
            st.balloons()

with tab_arquitectura:
    st.header("Resumen Arquitectónico para el Informe PDF")
    st.markdown("""
    - **Patrón Mediator:** Centraliza la comunicación y evita acoplamiento directo entre nodos.
    - **Patrón Observer Distribuido:** Notifica de forma reactiva las pujas a todos los hilos suscritos.
    - **Modelado UML:** Componentes, Secuencia y Despliegue listos para documentar en el PDF.
    """)