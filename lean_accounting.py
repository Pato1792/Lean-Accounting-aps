# lean_accounting.py

import io
import openpyxl
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lean Accounting", layout="centered")

st.title("📊 Lean Accounting - Módulo de Flujos de Valor")

# Inicializa la base de datos en sesión
if 'value_streams' not in st.session_state:
    st.session_state.value_streams = []

st.subheader("➕ Crear nuevo Flujo de Valor")

with st.form("value_stream_form"):
    name = st.text_input("Nombre del flujo de valor", "")
    income = st.number_input("Ingresos ($)", min_value=0.0, step=100.0)
    direct_costs = st.number_input("Costos Directos ($)", min_value=0.0, step=100.0)
    indirect_costs = st.number_input("Costos Indirectos ($)", min_value=0.0, step=100.0)
    submitted = st.form_submit_button("Guardar")

    if submitted and name:
        st.session_state.value_streams.append({
            "Flujo": name,
            "Ingresos": income,
            "Costos Directos": direct_costs,
            "Costos Indirectos": indirect_costs,
            "Rentabilidad": income - (direct_costs + indirect_costs)
        })
        st.success(f"Flujo '{name}' agregado.")

# Mostrar tabla de resultados
if st.session_state.value_streams:
    st.subheader("📈 Rentabilidad por Flujo")
    df = pd.DataFrame(st.session_state.value_streams)
    st.dataframe(df.style.format({"Ingresos": "${:,.2f}", "Costos Directos": "${:,.2f}", 
                                  "Costos Indirectos": "${:,.2f}", "Rentabilidad": "${:,.2f}"}))
import matplotlib.pyplot as plt

# Mostrar tabla de resultados
if st.session_state.value_streams:
    st.subheader("📈 Rentabilidad por Flujo")
    df = pd.DataFrame(st.session_state.value_streams)

    st.dataframe(df.style.format({
        "Ingresos": "${:,.2f}",
        "Costos Directos": "${:,.2f}",
        "Costos Indirectos": "${:,.2f}",
        "Rentabilidad": "${:,.2f}"
    }))

    # Gráfico de barras de rentabilidad
    st.subheader("📊 Rentabilidad por Flujo")
    st.subheader("📂 Cargar flujos desde archivo Excel")

uploaded_file = st.file_uploader("Selecciona un archivo .xlsx con los flujos", type=["xlsx"])

if uploaded_file is not None:
    try:
        df_excel = pd.read_excel(uploaded_file)
        required_columns = {"Flujo", "Ingresos", "Costos Directos", "Costos Indirectos"}
        if required_columns.issubset(df_excel.columns):
            df_excel["Rentabilidad"] = df_excel["Ingresos"] - (
                df_excel["Costos Directos"] + df_excel["Costos Indirectos"]
            )
            st.session_state.value_streams = df_excel.to_dict(orient="records")
            st.success("Archivo cargado correctamente.")
        else:
            st.error(f"El archivo debe contener las columnas: {required_columns}")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
    fig1, ax1 = plt.subplots()
    ax1.bar(df["Flujo"], df["Rentabilidad"], color="teal")
    ax1.set_ylabel("Rentabilidad ($)")
    ax1.set_title("Rentabilidad por Flujo de Valor")
    st.pyplot(fig1)

    # Gráfico de pastel de ingresos
    st.subheader("🧁 Distribución de Ingresos")
    fig2, ax2 = plt.subplots()
    ax2.pie(df["Ingresos"], labels=df["Flujo"], autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    ax2.set_title("Distribución de Ingresos Totales")
    st.pyplot(fig2)
import io

# Exportar a CSV
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
