import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Gestione Documenti Rifiuti")

# Form per i dati principali
st.header("Dati del Documento")
col1, col2 = st.columns(2)
with col1:
    mese = st.text_input("Mese")
    anno = st.text_input("Anno")
with col2:
    nome_rappresentante = st.text_input("Nome del Rappresentante Legale")
    sede = st.text_input("Sede Legale")

# Tabella per i rifiuti
st.header("Inserimento Rifiuti")
n_rows = st.number_input("Numero di rifiuti da inserire", min_value=1, value=1)

data = {
    "C.E.R.": [""] * n_rows,
    "Nome del Rifiuto": [""] * n_rows,
    "Prodotto (kg)": [0] * n_rows,
    "Smaltito (kg)": [0] * n_rows
}

df = pd.DataFrame(data)
edited_df = st.data_editor(df)

if st.button("Genera Excel"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        edited_df.to_excel(writer, sheet_name='Rifiuti', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Rifiuti']
        
        # Aggiungi informazioni aggiuntive
        worksheet.write(0, 6, f"Mese: {mese}")
        worksheet.write(1, 6, f"Anno: {anno}")
        worksheet.write(2, 6, f"Rappresentante: {nome_rappresentante}")
        worksheet.write(3, 6, f"Sede: {sede}")
    
    output.seek(0)
    st.download_button(
        label="Download Excel",
        data=output,
        file_name=f"registro_rifiuti_{mese}_{anno}.xlsx",
        mime="application/vnd.ms-excel"
    )

