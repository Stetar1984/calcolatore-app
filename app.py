import streamlit as st
import pandas as pd

# ==============================================================================
# --- Funzione di Calcolo IRPEF ---
# ==============================================================================
def calcola_irpef(imponibile):
    if imponibile <= 0: return 0
    if imponibile <= 28000: return imponibile * 0.23
    elif imponibile <= 50000: return (28000 * 0.23) + ((imponibile - 28000) * 0.35)
    else: return (28000 * 0.23) + (22000 * 0.35) + ((imponibile - 50000) * 0.43)

# ==============================================================================
# --- IMPOSTAZIONI PAGINA E TITOLO ---
# ==============================================================================
st.set_page_config(layout="wide", page_title="Calcolatore CPB")
st.title("Calcolatore di Convenienza Concordato Preventivo Biennale")

# ==============================================================================
# --- Selettore Principale ---
# ==============================================================================
tipo_calcolo = st.radio(
    "Seleziona il tipo di calcolo:",
    ('Ditta Individuale', 'Società di Persone'),
    horizontal=True,
)
st.markdown("---")

# ==============================================================================
# --- CALCOLATORE PER DITTA INDIVIDUALE ---
# ==============================================================================
if tipo_calcolo == 'Ditta Individuale':
    st.header("Simulazione per Ditta Individuale")
    
    with st.form("form_individuale"):
        st.subheader("Dati di Input")
        col1, col2 = st.columns(2)

        with col1:
            nome_ditta = st.text_input("NOME DITTA:", value='La Mia Ditta Individuale')
            reddito_simulato_2024 = st.number_input("REDDITO DA SIMULARE O PRESUNTO 2024:", value=70000.0, format="%.2f", help="CP10 colonna 2")
            reddito_rilevante_cpb_2023 = st.number_input("REDDITO RILEVANTE CPB 2023:", value=65000.0, format="%.2f", help="CP1 colonna 2")
            reddito_proposto_cpb_2024 = st.number_input("REDDITO PROPOSTO 2024 AI FINI CPB:", value=72000.0, format="%.2f", help="CP1 colonna 1")
            reddito_impresa_rettificato_cpb = st.number_input("REDDITO D'IMPRESA RETTIFICATO PER CPB 2024:", value=72000.0, format="%.2f", help="CP7 colonna 5")
            punteggio_isa_n_ind = st.slider("Punteggio ISA anno n (2023):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)

        with col2:
            altri_redditi = st.number_input("ALTRI REDDITI TASSABILI IRPEF 2024:", value=5000.0, format="%.2f", help="da riepilogo redditi RN + LC2 colonna 1")
            oneri_deducibili = st.number_input("ONERI DEDUCIBILI 2024:", value=2000.0, format="%.2f", help="RN3")
            cedolare_secca_redditi = st.number_input("REDDITI A CEDOLARE SECCA O TASS. SEP. 2024:", value=0.0, format="%.2f", help="LC2 colonna 1")
            imposte_gia_trattenute = st.number_input("IMPOSTE SU REDDITI GIA' TASSATI 2024:", value=0.0, format="%.2f", help="RN33 colonna 4")
            imposta_su_cedolare_secca = st.number_input("IMPOSTA SU CEDOLARE SECCA 2024:", value=0.0, format="%.2f", help="LC1 colonna 12/13")
            acconti_versati = st.number_input("ACCONTI VERSATI 2024:", value=0.0, format="%.2f", help="RN38 colonna 6")
            detrazioni_irpef = st.number_input("DETRAZIONI IRPEF 2024:", value=0.0, format="%.2f", help="RN22")
            
        submitted = st.form_submit_button("Esegui Simulazione")

    if submitted:
        # Calcoli SENZA concordato
        base_imponibile_no_cpb = reddito_simulato_2024 + altri_redditi - oneri_deducibili - cedolare_secca_redditi
        tassazione_no_cpb_irpef = calcola_irpef(base_imponibile_no_cpb)
        totale_tassazione_no_cpb = tassazione_no_cpb_irpef - imposte_gia_trattenute + imposta_su_cedolare_secca - acconti_versati - detrazioni_irpef

        # Calcoli CON concordato
        base_imponibile_si_cpb = altri_redditi + reddito_impresa_rettificato_cpb - cedolare_secca_redditi - oneri_deducibili
        base_imponibile_sostitutiva = reddito_proposto_cpb_2024 - reddito_rilevante_cpb_2023
        if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
        if punteggio_isa_n_ind >= 8: aliquota_sostitutiva = 0.10
        elif punteggio_isa_n_ind >= 6: aliquota_sostitutiva = 0.12
        else: aliquota_sostitutiva = 0.15
        imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva
        tass_ordinaria_si_cpb = calcola_irpef(base_imponibile_si_cpb)
        totale_tassazione_si_cpb = imposta_sostitutiva + tass_ordinaria_si_cpb + imposta_su_cedolare_secca - acconti_versati - detrazioni_irpef - imposte_gia_trattenute
        
        risparmio_fiscale = totale_tassazione_no_cpb - totale_tassazione_si_cpb
        
        st.markdown("---")
        st.subheader(f"Risultati per: {nome_ditta}")
        
        df_risultati = pd.DataFrame({
            "Descrizione": ["Base Imponibile IRPEF (con CPB)", "Base Imponibile IRPEF (senza CPB)", "Base Imponibile Sostitutiva", "Imposta Sostitutiva Calcolata", "Tassazione Ordinaria Residua (con CPB)", "TOTALE TASSE (CON ADESIONE CPB)", "Tassazione Totale (SENZA ADESIONE CPB)"],
            "Valore Calcolato": [base_imponibile_si_cpb, base_imponibile_no_cpb, base_imponibile_sostitutiva, imposta_sostitutiva, tass_ordinaria_si_cpb, totale_tassazione_si_cpb, totale_tassazione_no_cpb]
        }).set_index("Descrizione")
        
        st.table(df_risultati.style.format("{:,.2f} €"))
        st.subheader(f"RISPARMIO / (MAGGIOR ONERE): {risparmio_fiscale:,.2f} €")
