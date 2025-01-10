import streamlit as st
import PyPDF2
import pandas as pd
import re
from io import BytesIO
from PIL import Image
import pytesseract

def pulisci_testo(testo):
    return ' '.join(testo.split())

def estrai_dati_da_pdf(file_pdf):
    pdf_reader = PyPDF2.PdfReader(file_pdf)
    testo = ""
    for pagina in pdf_reader.pages:
        page_text = pagina.extract_text()
        if page_text:
            testo += page_text
    
    if not testo:
        st.error("Il testo estratto dal PDF è vuoto.")
        return None
    
    st.write("Testo estratto dal PDF:", testo)
    
    mese_anno = re.search(r'MESE (\w+)\s*\\\\\s*ANNO(\d{4})', testo)
    nome_azienda = re.search(r'Il sottoscritto (.+?) in qualità di', testo)
    indirizzo = re.search(r'con sede in (.+?),', testo)
    data_firma = re.search(r'Sanremo fi, Timbro e Firma (\d{2}/\d{2}/\d{2})', testo)
    dati_rifiuti = re.findall(r'(\d{6}\*?)\s*(.*?)(?=\d{6}|\Z)', testo, re.DOTALL)
    
    return {
        'mese_anno': f"{mese_anno.group(1)} {mese_anno.group(2)}" if mese_anno else "N/D",
        'nome_azienda': pulisci_testo(nome_azienda.group(1)) if nome_azienda else "N/D",
        'indirizzo': pulisci_testo(indirizzo.group(1)) if indirizzo else "N/D",
        'data_firma': data_firma.group(1) if data_firma else "N/D",
        'dati_rifiuti': [(cer, pulisci_testo(nome)) for cer, nome in dati_rifiuti]
    }

def estrai_dati_da_jpeg(file_jpeg):
    image = Image.open(file_jpeg)
    testo = pytesseract.image_to_string(image)
    
    if not testo:
        st.error("Il testo estratto dal JPEG è vuoto.")
        return None
    
    st.write("Testo estratto dal JPEG:", testo)
    
    mese_anno = re.search(r'MESE (\w+)\s*\\\\\s*ANNO(\d{4})', testo)
    nome_azienda = re.search(r'Il sottoscritto (.+?) in qualità di', testo)
    indirizzo = re.search(r'con sede in (.+?),', testo)
    data_firma = re.search(r'Sanremo fi, Timbro e Firma (\d{2}/\d{2}/\d{2})', testo)
    dati_rifiuti = re.findall(r'(\d{6}\*?)\s*(.*?)(?=\d{6}|\Z)', testo, re.DOTALL)
    
    return {
        'mese_anno': f"{mese_anno.group(1)} {mese_anno.group(2)}" if mese_anno else "N/D",
        'nome_azienda': pulisci_testo(nome_azienda.group(1)) if nome_azienda else "N/D",
        'indirizzo': pulisci_testo(indirizzo.group(1)) if indirizzo else "N/D",
        'data_firma': data_firma.group(1) if data_firma else "N/D",
        'dati_rifiuti': [(cer, pulisci_testo(nome)) for cer, nome in dati_rifiuti]
    }

def crea_excel(dati):
    df = pd.DataFrame(dati['dati_rifiuti'], columns=['CER', 'Nome Rifiuto'])
    df['Prodotto (Kg)'] = 'N/D'
    df['Smaltito (Kg)'] = 'N/D'
    
    buffer_excel = BytesIO()
    
    with pd.ExcelWriter(buffer_excel, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Dati Rifiuti', index=False)
        
        df_info = pd.DataFrame({
            'Campo': ['Mese/Anno', 'Nome Azienda', 'Indirizzo', 'Data Firma'],
            'Valore': [dati['mese_anno'], dati['nome_azienda'], dati['indirizzo'], dati['data_firma']]
        })
        df_info.to_excel(writer, sheet_name='Info Azienda', index=False)
    
    buffer_excel.seek(0)
    return buffer_excel

st.title('Estrattore Dati Gestione Rifiuti da PDF o JPEG a Excel')

file_caricato = st.file_uploader("Scegli un file PDF o JPEG", type=["pdf", "jpeg", "jpg"])

if file_caricato is not None:
    try:
        if file_caricato.type == "application/pdf":
            dati = estrai_dati_da_pdf(file_caricato)
        elif file_caricato.type in ["image/jpeg", "image/jpg"]:
            dati = estrai_dati_da_jpeg(file_caricato)
        
        if dati is None or not dati['dati_rifiuti']:
            st.error("Non è stato possibile estrarre i dati dei rifiuti dal file. Verifica che il file sia nel formato corretto.")
        else:
            st.subheader('Informazioni Estratte')
            st.write(f"Mese/Anno: {dati['mese_anno']}")
            st.write(f"Nome Azienda: {dati['nome_azienda']}")
            st.write(f"Indirizzo: {dati['indirizzo']}")
            st.write(f"Data Firma: {dati['data_firma']}")
            
            st.subheader('Dati Rifiuti')
            df = pd.DataFrame(dati['dati_rifiuti'], columns=['CER', 'Nome Rifiuto'])
            st.dataframe(df)
            
            file_excel = crea_excel(dati)
            
            st.download_button(
                label="Scarica file Excel",
                data=file_excel,
                file_name="dati_gestione_rifiuti.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Si è verificato un errore durante l'elaborazione del file: {str(e)}")
