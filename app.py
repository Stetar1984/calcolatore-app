import streamlit as st
import pandas as pd

# ==============================================================================
# --- FUNZIONE DI CALCOLO IRPEF (UNIVERSALE) ---
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
# --- DIZIONARIO DELLE DESCRIZIONI AGGIUNTIVE ---
# ==============================================================================
descrizioni_aggiuntive = {
    'reddito_simulato_2024': "CP10 colonna 2", 'reddito_rilevante_cpb_2023': "CP1 colonna 2",
    'reddito_proposto_cpb_2024': "CP1 colonna 1", 'reddito_impresa_rettificato_cpb': "CP7 colonna 5",
    'altri_redditi': "da riepilogo redditi RN + LC2 colonna 1", 'oneri_deducibili': "RN3",
    'cedolare_secca_redditi': "LC2 colonna 1", 'imposte_gia_trattenute': "RN33 colonna 4",
    'imposta_su_cedolare_secca': "LC1 colonna 12/13", 'acconti versati': "RN38 colonna 6",
    'detrazioni IRPEF': "RN22",
    'valore_produzione_simulato_2024': "IP73 colonna 4",
    'valore_produzione_irap_rettificato_cpb': "IP74"
}

# ==============================================================================
# --- SELETTORE PRINCIPALE ---
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
            reddito_simulato_2024 = st.number_input("REDDITO DA SIMULARE O PRESUNTO 2024:", value=70000.0, format="%.2f", help=descrizioni_aggiuntive['reddito_simulato_2024'])
            reddito_rilevante_cpb_2023 = st.number_input("REDDITO RILEVANTE CPB 2023:", value=65000.0, format="%.2f", help=descrizioni_aggiuntive['reddito_rilevante_cpb_2023'])
            reddito_proposto_cpb_2024 = st.number_input("REDDITO PROPOSTO 2024 AI FINI CPB:", value=72000.0, format="%.2f", help=descrizioni_aggiuntive['reddito_proposto_cpb_2024'])
            reddito_impresa_rettificato_cpb = st.number_input("REDDITO D'IMPRESA RETTIFICATO PER CPB 2024:", value=72000.0, format="%.2f", help=descrizioni_aggiuntive['reddito_impresa_rettificato_cpb'])
            punteggio_isa_n_ind = st.slider("Punteggio ISA anno n (2023):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)

        with col2:
            altri_redditi = st.number_input("ALTRI REDDITI TASSABILI IRPEF 2024:", value=5000.0, format="%.2f", help=descrizioni_aggiuntive['altri_redditi'])
            oneri_deducibili = st.number_input("ONERI DEDUCIBILI 2024:", value=2000.0, format="%.2f", help=descrizioni_aggiuntive['oneri_deducibili'])
            cedolare_secca_redditi = st.number_input("REDDITI A CEDOLARE SECCA O TASS. SEP. 2024:", value=0.0, format="%.2f", help=descrizioni_aggiuntive['cedolare_secca_redditi'])
            imposte_gia_trattenute = st.number_input("IMPOSTE SU REDDITI GIA' TASSATI 2024:", value=0.0, format="%.2f", help=descrizioni_aggiuntive['imposte_gia_trattenute'])
            imposta_su_cedolare_secca = st.number_input("IMPOSTA SU CEDOLARE SECCA 2024:", value=0.0, format="%.2f", help=descrizioni_aggiuntive['imposta_su_cedolare_secca'])
            acconti_versati = st.number_input("ACCONTI VERSATI 2024:", value=0.0, format="%.2f", help=descrizioni_aggiuntive['acconti versati'])
            detrazioni_irpef = st.number_input("DETRAZIONI IRPEF 2024:", value=0.0, format="%.2f", help=descrizioni_aggiuntive['detrazioni IRPEF'])
            
        submitted_ind = st.form_submit_button("Esegui Simulazione")

    if submitted_ind:
        # (La logica di calcolo rimane invariata)
        pass

# ==============================================================================
# --- CALCOLATORE PER SOCIETÀ DI PERSONE ---
# ==============================================================================
elif tipo_calcolo == 'Società di Persone':
    st.header("Simulazione per Società di Persone")
    
    with st.form("form_societa"):
        st.subheader("Dati Società")
        col1, col2 = st.columns(2)
        with col1:
            nome_societa = st.text_input("NOME SOCIETA':", value='Mia Società S.n.c.')
            reddito_simulato_2024_soc = st.number_input("REDDITO DA SIMULARE O PRESUNTO 2024 (Società):", value=142000.0, format="%.2f", help=descrizioni_aggiuntive['reddito_simulato_2024'])
            reddito_rilevante_cpb_2023_soc = st.number_input("REDDITO RILEVANTE CPB 2023 (Società):", value=139872.0, format="%.2f", help=descrizioni_aggiuntive['reddito_rilevante_cpb_2023'])
            reddito_proposto_cpb_2024_soc = st.number_input("REDDITO PROPOSTO 2024 FINI CPB (Società):", value=151784.0, format="%.2f", help=descrizioni_aggiuntive['reddito_proposto_cpb_2024'])
            reddito_impresa_rettificato_cpb_soc = st.number_input("REDDITO D'IMPRESA RETTIFICATO PER CPB:", value=152420.49, format="%.2f", help=descrizioni_aggiuntive['reddito_impresa_rettificato_cpb'])
        with col2:
            valore_produzione_simulato_2024_soc = st.number_input("VALORE PRODUZIONE DA SIMULARE O PRESUNTO 2024 (per IRAP):", value=149604.0, format="%.2f", help=descrizioni_aggiuntive['valore_produzione_simulato_2024'])
            valore_produzione_irap_rettificato_cpb_soc = st.number_input("Valore della produzione IRAP rettificato per CPB:", value=318210.49, format="%.2f", help=descrizioni_aggiuntive['valore_produzione_irap_rettificato_cpb'])
            punteggio_isa_n_soc = st.slider("Punteggio ISA Società (anno n):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)
        
        st.markdown("---")
        st.subheader("Dati dei Singoli Soci")
        
        # Creiamo le schede per i soci
        tab1, tab2, tab3, tab4 = st.tabs(["Socio 1", "Socio 2", "Socio 3", "Socio 4"])
        soci_inputs = []
        
        for i, tab in enumerate([tab1, tab2, tab3, tab4]):
            with tab:
                socio_data = {}
                c1, c2 = st.columns(2)
                socio_data['nome'] = c1.text_input(f"Nome Socio {i+1}", value=f"Socio {i+1}")
                socio_data['quota'] = c2.number_input(f"Quota di Partecipazione (%) Socio {i+1}", value=50.0 if i < 2 else 0.0, format="%.2f")
                
                col_socio1, col_socio2 = st.columns(2)
                with col_socio1:
                    socio_data['altri_redditi'] = st.number_input(f"ALTRI REDDITI {i+1}", value=0.0, format="%.2f", help=descrizioni_aggiuntive['altri_redditi'], key=f"ar_{i}")
                    socio_data['oneri_deducibili'] = st.number_input(f"ONERI DEDUCIBILI {i+1}", value=0.0, format="%.2f", help=descrizioni_aggiuntive['oneri_deducibili'], key=f"od_{i}")
                    socio_data['cedolare_secca_redditi'] = st.number_input(f"REDDITI A CEDOLARE SECCA {i+1}", value=0.0, format="%.2f", help=descrizioni_aggiuntive['cedolare_secca_redditi'], key=f"cs_{i}")
                    socio_data['imposte_gia_trattenute'] = st.number_input(f"IMPOSTE GIA' TRATTENUTE {i+1}", value=0.0, format="%.2f", help=descrizioni_aggiuntive['imposte_gia_trattenute'], key=f"igt_{i}")
                with col_socio2:
                    socio_data['imposta_su_cedolare_secca'] = st.number_input(f"IMPOSTA SU CEDOLARE SECCA {i+1}", value=0.0, format="%.2f", help=descrizioni_aggiuntive['imposta_su_cedolare_secca'], key=f"ics_{i}")
                    socio_data['acconti versati'] = st.number_input(f"ACCONTI VERSATI {i+1}", value=0.0, format="%.2f", help=descrizioni_aggiuntive['acconti versati'], key=f"av_{i}")
                    socio_data['detrazioni IRPEF'] = st.number_input(f"DETRAZIONI IRPEF {i+1}", value=0.0, format="%.2f", help=descrizioni_aggiuntive['detrazioni IRPEF'], key=f"di_{i}")
                soci_inputs.append(socio_data)
        
        submitted_soc = st.form_submit_button("Esegui Simulazione Società")

    if submitted_soc:
        # Calcolo IRAP
        st.markdown("---")
        st.subheader(f"Parte 1: Analisi IRAP per la Società: {nome_societa}")
        aliquota_irap = 0.039
        irap_no_cpb = valore_produzione_simulato_2024_soc * aliquota_irap
        irap_si_cpb = valore_produzione_irap_rettificato_cpb_soc * aliquota_irap
        df_irap = pd.DataFrame({"Senza Concordato": [irap_no_cpb], "Con Concordato": [irap_si_cpb]}, index=["Imposta IRAP Dovuta"])
        st.table(df_irap.style.format("{:,.2f} €"))
        
        st.markdown("---")
        st.subheader("Parte 2: Analisi IRPEF per i Singoli Soci")
        
        for i, socio in enumerate(soci_inputs):
            perc_socio = socio['quota'] / 100.0
            if perc_socio == 0: continue
            
            # (Logica di calcolo per ogni socio)
            st.markdown(f"##### Riepilogo per: {socio['nome']} (Quota: {socio['quota']:.2f}%)")
            st.info("Calcolo dettagliato per questo socio in fase di sviluppo.")
