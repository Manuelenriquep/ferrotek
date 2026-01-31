import streamlit as st
from core_calculo import SistemaFerrotek

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Ferrotek | Ingeniería Rural", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES FERROTEK ---
st.markdown("""
<style>
    .block-container {padding-top: 2rem;}
    h1 {color: #2C3E50;}
    h2 {color: #D35400; font-size: 24px;} /* Naranja Ladrillo */
    .price-tag {
        font-size: 36px; 
        font-weight: bold; 
        color: #27AE60;
        background-color: #EAFAF1;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #27AE60;
    }
    .metric-card {
        background-color: #F4F6F7;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2C3E50; /* Gris Acero */
    }
</style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.write("## 🛡️") 
with col_title:
    st.title("FERROTEK")
    st.write("**Ingeniería de Precisión para el Campo**")

st.markdown("---")

# Inicializar Cerebro
sistema = SistemaFerrotek()

# --- BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.header("🔧 Configuración")
    st.info("Catálogo Digital v1.0")
    
    opcion = st.radio(
        "Seleccione Modelo:",
        ("1_alcoba", "2_alcobas", "3_alcobas"),
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    st.markdown("---")
    st.write("📍 **Ferrotek Ingeniería**")
    st.caption("División de Guanes.biz")
    st.caption("Santander, Colombia")

# --- LÓGICA DE CÁLCULO ---
datos = sistema.calcular_modelo(opcion)

if datos:
    # --- COLUMNA IZQUIERDA: IMAGEN DEL MODELO ---
    col_img, col_info = st.columns([1, 1])
    
    with col_img:
        st.subheader(f"🏠 {datos['Modelo']}")
        
        # Imágenes de referencia (Temporales)
        if opcion == "1_alcoba":
            st.image("https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&q=80&w=800", caption="Ref: Suite Rural Compacta")
        elif opcion == "2_alcobas":
            st.image("https://images.unsplash.com/photo-1513584685908-2274653fa36f?auto=format&fit=crop&q=80&w=800", caption="Ref: Casa Tradicional")
        else:
            st.image("https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&q=80&w=800", caption="Ref: Casa Familiar Grande")

        st.info("💡 **Sistema:** Estructura Tubular 50x50 + Doble Membrana + Mezcla Antihongos")

    # --- COLUMNA DERECHA: PRECIOS Y RESUMEN ---
    with col_info:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Presupuesto Estimado")
        
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Costo Directo (Materiales + MO)")
            st.markdown(f"**${datos['costo_total']:,.0f}**")
        with c2:
            st.caption("Precio Sugerido Venta")
            st.markdown(f'<div class="price-tag">${datos["precio_venta"]:,.0f}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 📋 Ficha Técnica")
        st.write(f"**Área Construida:** {datos['Area']}")
        st.write(f"**Distribución:** {datos['Configuracion']}")
        
        with st.expander("Ver Desglose de Materiales"):
            st.markdown("**🦴 Estructura Metálica:**")
            st.write(f"- {datos['Resumen_Estructura']['Tubos_50x50']} Tubos Estructurales 50x50")
            st.write(f"- {datos['Resumen_Estructura']['Tornillos_Estructurales_HEX']}")
            
            st.markdown("**🧥 Piel & Acabados:**")
            st.write(f"- {datos['Resumen_Piel']['Malla_Electro']} Paneles Electrosoldados")
            st.write(f"- {datos['Resumen_Piel']['Zaranda_Rollos']} Rollos Zaranda")
            st.write(f"- {datos['Resumen_Piel']['Tornillos_Fijacion_LENTEJA']}")
            
            st.markdown("**🧪 Mezcla Impermeable (1:3:3):**")
            st.write(f"- {datos['Resumen_Mezcla_Impermeable']['Cemento']} (Cemento)")
            st.write(f"- {datos['Resumen_Mezcla_Impermeable']['Cal_Hidratada']} (Cal Antihongos)")
            st.write(f"- {datos['Resumen_Mezcla_Impermeable']['Arena_Fina']} (Arena Fina)")

    st.success("✅ Cotización Oficial Ferrotec.")