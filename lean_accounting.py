import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime
import openpyxl

# Configuración de página
st.set_page_config(page_title="Lean Accounting", layout="wide")

# Inicializar variables de sesión
if 'value_streams' not in st.session_state:
    st.session_state.value_streams = []
if 'page' not in st.session_state:
    st.session_state.page = 'menu'
if 'mode' not in st.session_state:
    st.session_state.mode = 'PC'
if 'mostrar_graficos' not in st.session_state:
    st.session_state.mostrar_graficos = False

# Funciones reutilizables
def mostrar_menu():
    st.markdown("""
    <h1 style='text-align: center;'>📊 Lean Accounting</h1>
    <h3 style='text-align: center;'>Sistema de Control Contable por Flujos de Valor</h3>
    """, unsafe_allow_html=True)

    st.session_state.mode = st.radio("Selecciona el modo de visualización:", ["PC", "Móvil"], horizontal=True)

    if st.session_state.value_streams:
        df = pd.DataFrame(st.session_state.value_streams)
        total_ingresos = df["Ingresos"].sum()
        total_rentabilidad = df["Rentabilidad"].sum()
        col1, col2 = st.columns(2)
        col1.metric("Ingresos Totales", f"${total_ingresos:,.0f}")
        col2.metric("Rentabilidad Total", f"${total_rentabilidad:,.0f}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧮 Módulo Contable (Flujos de Valor)"):
            st.session_state.page = 'contabilidad'
    with col2:
        if st.button("📈 Entorno de Análisis y Simulación"):
            st.session_state.page = 'simulacion'


def boton_volver():
    if st.button("⬅ Volver al Menú"):
        st.session_state.page = 'menu'


def boton_imprimir():
    st.markdown("""
        <script>
        function printPage() {
            window.print();
        }
        </script>
        <button onclick="printPage()">🖨️ Imprimir Página</button>
        """, unsafe_allow_html=True)


def mostrar_tarjetas(df):
    for index, row in df.iterrows():
        st.markdown(f"""
        <div style='background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-radius: 10px;'>
            <h4>{row['Flujo']} - {row['Fecha']}</h4>
            <b>Ingresos:</b> ${row['Ingresos']:,.2f}<br>
            <b>Costos Directos:</b> ${row['Costos Directos']:,.2f}<br>
            <b>Costos Indirectos:</b> ${row['Costos Indirectos']:,.2f}<br>
            <b>Rentabilidad:</b> ${row['Rentabilidad']:,.2f}<br>
            <b>% Rentabilidad:</b> {row['% Rentabilidad']:.2%}<br>
            <b>Riesgo:</b> {row['Riesgo']}
        </div>
        """, unsafe_allow_html=True)

# Módulo Contabilidad
if st.session_state.page == 'menu':
    mostrar_menu()

elif st.session_state.page == 'contabilidad':
    st.title("📊 Lean Accounting - Módulo de Flujos de Valor")

    if st.session_state.mode == 'PC':
        st.subheader("➕ Crear nuevo Flujo de Valor")
        with st.form("value_stream_form"):
            name = st.text_input("Nombre del flujo de valor", "")
            income = st.number_input("Ingresos ($)", min_value=0.0, step=100.0)
            direct_costs = st.number_input("Costos Directos ($)", min_value=0.0, step=100.0)
            indirect_costs = st.number_input("Costos Indirectos ($)", min_value=0.0, step=100.0)
            submitted = st.form_submit_button("Guardar")

            if submitted and name:
                if income <= 0:
                    st.warning("Los ingresos deben ser mayores a cero.")
                elif name in [v["Flujo"] for v in st.session_state.value_streams]:
                    st.warning("Ese flujo ya existe.")
                else:
                    rentabilidad = income - (direct_costs + indirect_costs)
                    fecha = datetime.today().date()
                    porcentaje = rentabilidad / income if income > 0 else 0
                    riesgo = "🔴 Alto" if rentabilidad < 0 else "🟢 OK"
                    st.session_state.value_streams.append({
                        "Flujo": name,
                        "Ingresos": income,
                        "Costos Directos": direct_costs,
                        "Costos Indirectos": indirect_costs,
                        "Rentabilidad": rentabilidad,
                        "% Rentabilidad": porcentaje,
                        "Costo Total": direct_costs + indirect_costs,
                        "Costo Promedio": (direct_costs + indirect_costs) / income if income > 0 else 0,
                        "Fecha": str(fecha),
                        "Riesgo": riesgo
                    })
                    st.success(f"Flujo '{name}' agregado.")

        st.subheader("📂 Cargar flujos desde archivo Excel")
        uploaded_file = st.file_uploader("Selecciona un archivo .xlsx", type=["xlsx"])

        if uploaded_file is not None:
            try:
                df_excel = pd.read_excel(uploaded_file)
                required = {"Flujo", "Ingresos", "Costos Directos", "Costos Indirectos"}
                if required.issubset(df_excel.columns):
                    df_excel["Rentabilidad"] = df_excel["Ingresos"] - (df_excel["Costos Directos"] + df_excel["Costos Indirectos"])
                    df_excel["% Rentabilidad"] = df_excel["Rentabilidad"] / df_excel["Ingresos"]
                    df_excel["Costo Total"] = df_excel["Costos Directos"] + df_excel["Costos Indirectos"]
                    df_excel["Costo Promedio"] = df_excel["Costo Total"] / df_excel["Ingresos"]
                    df_excel["Fecha"] = str(datetime.today().date())
                    df_excel["Riesgo"] = df_excel["Rentabilidad"].apply(lambda x: "🔴 Alto" if x < 0 else "🟢 OK")
                    st.session_state.value_streams = df_excel.to_dict(orient="records")
                    st.success("Archivo cargado correctamente.")
                else:
                    st.error(f"El archivo debe tener las columnas: {required}")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

    if st.session_state.value_streams:
        df = pd.DataFrame(st.session_state.value_streams)

        st.subheader("📈 Rentabilidad por Flujo")
        if st.session_state.mode == 'PC':
            st.dataframe(df)
        else:
            mostrar_tarjetas(df)

        if st.button("📊 Mostrar gráficos"):
            st.session_state.mostrar_graficos = True

        if st.session_state.mostrar_graficos:
            fig1, ax1 = plt.subplots(figsize=(8, 3))
            ax1.bar(df["Flujo"], df["Rentabilidad"], color="teal")
            ax1.set_ylabel("Rentabilidad ($)")
            ax1.set_title("Rentabilidad por Flujo de Valor")
            ax1.set_xticklabels(df["Flujo"], rotation=45)
            st.pyplot(fig1)

            fig2, ax2 = plt.subplots(figsize=(5, 5))
            ax2.pie(df["Ingresos"], labels=df["Flujo"], autopct="%1.1f%%", startangle=90)
            ax2.axis("equal")
            ax2.set_title("Distribución de Ingresos Totales")
            st.pyplot(fig2)

        st.subheader("💾 Exportar datos")
        if not df.empty:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv_buffer.getvalue(),
                file_name="flujos_lean_accounting.csv",
                mime="text/csv"
            )

    boton_imprimir()
    boton_volver()

# Entorno de simulación
elif st.session_state.page == 'simulacion':
    st.title("📈 Simulador Económico Lean")

    if st.session_state.value_streams:
        df = pd.DataFrame(st.session_state.value_streams)
        variacion = st.slider("Variación de ingresos (%)", -50, 50, 0)
        df_simulado = df.copy()

        df_simulado["Ingresos"] *= (1 + variacion / 100)
        df_simulado["Rentabilidad"] = df_simulado["Ingresos"] - (
            df_simulado["Costos Directos"] + df_simulado["Costos Indirectos"]
        )
        df_simulado["% Rentabilidad"] = df_simulado["Rentabilidad"] / df_simulado["Ingresos"]
        df_simulado["Riesgo"] = df_simulado["Rentabilidad"].apply(lambda x: "🔴 Alto" if x < 0 else "🟢 OK")

        if st.session_state.mode == 'PC':
            st.dataframe(df_simulado)
        else:
            mostrar_tarjetas(df_simulado)

        fig, ax = plt.subplots(figsize=(5, 5))
        wedges, texts, autotexts = ax.pie(
            df_simulado['Rentabilidad'],
            labels=df_simulado['Flujo'],
            autopct='%1.1f%%',
            startangle=90
        )
        ax.axis('equal')
        ax.set_title(f"Distribución de Rentabilidad Simulada ({variacion}%)")
        st.pyplot(fig)
        fig = None  # prevenir doble graficado
        

        if st.session_state.mode == 'PC':
            csv_sim = io.StringIO()
            df_simulado.to_csv(csv_sim, index=False)
            st.download_button(
                label="📥 Descargar escenario simulado",
                data=csv_sim.getvalue(),
                file_name=f"escenario_{variacion}.csv",
                mime="text/csv"
            )

    else:
        st.warning("Primero debes ingresar o cargar datos en el módulo contable.")

    boton_imprimir()
    boton_volver()
