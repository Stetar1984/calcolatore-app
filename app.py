import streamlit as st
import pandas as pd
import base64

# ==============================================================================
# --- FUNZIONI HELPER GLOBALI ---
# ==============================================================================

def calcola_irpef(imponibile):
    """Calcola l'IRPEF lorda basata sugli scaglioni."""
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
    'reddito_simulato_2024': "CP10 colonna 2",
    'reddito_rilevante_cpb_2023': "CP1 colonna 2",
    'reddito_proposto_cpb_2024': "CP1 colonna 1",
    'reddito_impresa_rettificato_cpb': "CP7 colonna 5",
    'altri_redditi': "da riepilogo redditi RN + LC2 colonna 1",
    'oneri_deducibili': "RN3",
    'cedolare_secca_redditi': "LC2 colonna 1",
    'imposte_gia_trattenute': "RN33 colonna 4",
    'imposta_su_cedolare_secca': "LC1 colonna 12/13",
    'acconti versati': "RN38 colonna 6",
    'detrazioni IRPEF': "RN22",
    'valore_produzione_simulato_2024': "IP73 colonna 4",
    'valore_produzione_irap_rettificato_cpb': "IP74"
}

# ==============================================================================
# --- SELETTORE PRINCIPALE ---
# ==============================================================================
tipo_calcolo = st.radio(
    "Seleziona il tipo di calcolo:",
    ('Ditta Individuale', 'Società in trasparenza fiscale'),
    horizontal=True,
    label_visibility="collapsed"
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
            reddito_simulato_2024 = st.number_input("REDDITO DA SIMULARE O PRESUNTO 2024 (CP10 colonna 2):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['reddito_simulato_2024'])
            reddito_rilevante_cpb_2023 = st.number_input("REDDITO RILEVANTE CPB 2023 (CP1 colonna 2):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['reddito_rilevante_cpb_2023'])
            reddito_proposto_cpb_2024 = st.number_input("REDDITO PROPOSTO 2024 AI FINI CPB (CP1 colonna 1):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['reddito_proposto_cpb_2024'])
            reddito_impresa_rettificato_cpb = st.number_input("REDDITO D'IMPRESA RETTIFICATO PER CPB 2024 (CP7 colonna 5):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['reddito_impresa_rettificato_cpb'])
            punteggio_isa_n_ind = st.slider("Punteggio ISA anno n (2023):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)

        with col2:
            altri_redditi = st.number_input("ALTRI REDDITI TASSABILI (da riepilogo redditi RN + LC2 colonna 1):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['altri_redditi'])
            oneri_deducibili = st.number_input("ONERI DEDUCIBILI (RN3):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['oneri_deducibili'])
            cedolare_secca_redditi = st.number_input("REDDITI A CEDOLARE SECCA O TASS. SEPARATA (LC2 colonna 1):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['cedolare_secca_redditi'])
            imposte_gia_trattenute = st.number_input("IMPOSTE SU REDDITI GIA' TASSATI E RITENUTE (RN33 colonna 4):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['imposte_gia_trattenute'])
            imposta_su_cedolare_secca = st.number_input("IMPOSTA SU CEDOLARE SECCA (LC1 colonna 12/13):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['imposta_su_cedolare_secca'])
            acconti_versati = st.number_input("ACCONTI VERSATI (RN38 colonna 6):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['acconti versati'])
            detrazioni_irpef = st.number_input("DETRAZIONI IRPEF (RN22):", value=0.0, format="%.2f", help=descrizioni_aggiuntive['detrazioni IRPEF'])
            
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
        
        st.markdown(f"<h4>Risultati per: {nome_ditta}</h4>", unsafe_allow_html=True)
        df_risultati = pd.DataFrame({"Senza Concordato": [f"{totale_tassazione_no_cpb:,.2f} €"], "Con Concordato": [f"{totale_tassazione_si_cpb:,.2f} €"], "Risparmio/Onere": [f"{risparmio_fiscale:,.2f} €"]}, index=["Carico Fiscale Totale"])
        st.table(df_risultati)

#==============================================================================
# --- CALCOLATORE PER SOCIETÀ DI PERSONE ---
#==============================================================================
elif tipo_calcolo == 'Società di Persone':
    st.header("Simulazione per Società di Persone")
    with st.form("form_societa"):
        st.subheader("Dati Società")
        col1, col2 = st.columns(2)
        with col1:
            nome_societa = st.text_input("NOME SOCIETA':", value='Mia Società S.n.c.')
            reddito_simulato_2024_soc = st.number_input("REDDITO DA SIMULARE O PRESUNTO 2024 (CP10 colonna 1):", value=142000.0, format="%.2f", help=descrizioni_aggiuntive.get('reddito_simulato_2024'))
            reddito_rilevante_cpb_2023_soc = st.number_input("REDDITO RILEVANTE CPB 2023 (CP1 colonna 2):", value=139872.0, format="%.2f", help=descrizioni_aggiuntive.get('reddito_rilevante_cpb_2023'))
            reddito_proposto_cpb_2024_soc = st.number_input("REDDITO PROPOSTO 2024 FINI CPB (CP1 colonna 1):", value=151784.0, format="%.2f", help=descrizioni_aggiuntive.get('reddito_proposto_cpb_2024'))
            reddito_impresa_rettificato_cpb_soc = st.number_input("REDDITO D'IMPRESA RETTIFICATO PER CPB (CP7 colonna 5):", value=152420.49, format="%.2f", help=descrizioni_aggiuntive.get('reddito_impresa_rettificato_cpb'))
        with col2:
            valore_produzione_simulato_2024_soc = st.number_input("VALORE PRODUZIONE DA SIMULARE O PRESUNTO 2024 (IP73 colonna 4):", value=149604.0, format="%.2f", help=descrizioni_aggiuntive.get('valore_produzione_simulato_2024'))
            valore_produzione_irap_rettificato_cpb_soc = st.number_input("Valore della produzione IRAP rettificato per CPB (IP74):", value=318210.49, format="%.2f", help=descrizioni_aggiuntive.get('valore_produzione_irap_rettificato_cpb'))
            punteggio_isa_n_soc = st.slider("Punteggio ISA Società (anno n):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)
        
        st.markdown("---")
        st.subheader("Dati dei Singoli Soci")
        tabs = st.tabs([f"Socio {i+1}" for i in range(4)])
        soci_inputs = []
        for i, tab in enumerate(tabs):
            with tab:
                socio_data = {}
                c1, c2 = st.columns(2)
                socio_data['nome_socio'] = c1.text_input(f"Nome Socio {i+1}", value=f"Socio {i+1}", key=f"nome_{i}")
                socio_data['quota_partecipazione'] = c2.number_input(f"Quota di Partecipazione (%) Socio {i+1}", value=50.0 if i < 2 else 0.0, format="%.2f", key=f"quota_{i}")
                col_socio1, col_socio2 = st.columns(2)
                with col_socio1:
                    socio_data['altri_redditi'] = st.number_input(f"ALTRI REDDITI TASSABILI {i+1}", value=0.0, format="%.2f", key=f"ar_{i}", help=descrizioni_aggiuntive.get('altri_redditi'))
                    socio_data['oneri_deducibili'] = st.number_input(f"ONERI DEDUCIBILI {i+1}", value=0.0, format="%.2f", key=f"od_{i}", help=descrizioni_aggiuntive.get('oneri_deducibili'))
                    socio_data['cedolare_secca_redditi'] = st.number_input(f"REDDITI A CEDOLARE SECCA O TASS. SEPARATA {i+1}", value=0.0, format="%.2f", key=f"csr_{i}", help=descrizioni_aggiuntive.get('cedolare_secca_redditi'))
                    socio_data['imposte_gia_trattenute'] = st.number_input(f"IMPOSTE SU REDDITI GIA' TASSATI E RITENUTE {i+1}", value=0.0, format="%.2f", key=f"igt_{i}", help=descrizioni_aggiuntive.get('imposte_gia_trattenute'))
                with col_socio2:
                    socio_data['imposta_su_cedolare_secca'] = st.number_input(f"IMPOSTA SU CEDOLARE SECCA {i+1}", value=0.0, format="%.2f", key=f"ics_{i}", help=descrizioni_aggiuntive.get('imposta_su_cedolare_secca'))
                    socio_data['acconti versati'] = st.number_input(f"ACCONTI VERSATI {i+1}", value=0.0, format="%.2f", key=f"av_{i}", help=descrizioni_aggiuntive.get('acconti versati'))
                    socio_data['detrazioni IRPEF'] = st.number_input(f"DETRAZIONI IRPEF {i+1}", value=0.0, format="%.2f", key=f"di_{i}", help=descrizioni_aggiuntive.get('detrazioni IRPEF'))
                soci_inputs.append(socio_data)
        
        submitted_soc = st.form_submit_button("Esegui Simulazione Società")

    if submitted_soc:
        st.markdown("---"); st.subheader(f"Parte 1: Analisi IRAP per la Società: {nome_societa}")
        aliquota_irap = 0.039; irap_no_cpb = valore_produzione_simulato_2024_soc * aliquota_irap; irap_si_cpb = valore_produzione_irap_rettificato_cpb_soc * aliquota_irap; risparmio_irap = irap_no_cpb - irap_si_cpb
        df_irap = pd.DataFrame({"Senza Concordato": [irap_no_cpb], "Con Concordato": [irap_si_cpb], "Risparmio/Onere IRAP": [risparmio_irap]}, index=["Imposta IRAP Dovuta"]); st.table(df_irap.style.format("{:,.2f} €"))
        st.markdown("---"); st.subheader("Parte 2: Analisi IRPEF per i Singoli Soci")
        
        for i, socio in enumerate(soci_inputs):
            perc_socio = socio['quota_partecipazione'] / 100.0
            if perc_socio == 0: continue
            
            st.markdown(f"<h4>Riepilogo per: {socio['nome_socio']} (Quota: {socio['quota_partecipazione']:.2f}%)</h4>", unsafe_allow_html=True)
            quota_reddito_simulato = reddito_simulato_2024_soc * perc_socio; quota_reddito_rilevante = reddito_rilevante_cpb_2023_soc * perc_socio; quota_reddito_proposto = reddito_proposto_cpb_2024_soc * perc_socio; quota_reddito_rettificato_cpb = reddito_impresa_rettificato_cpb_soc * perc_socio
            base_imponibile_no_cpb = quota_reddito_simulato + socio['altri_redditi'] - socio['oneri_deducibili']- socio['cedolare_secca_redditi']
            irpef_ordinaria_no_cpb = calcola_irpef(base_imponibile_no_cpb)
            carico_fiscale_no_cpb = irpef_ordinaria_no_cpb - socio['imposte_gia_trattenute'] + socio['imposta_su_cedolare_secca'] - socio['acconti versati'] - socio['detrazioni IRPEF']
            base_imponibile_sostitutiva = quota_reddito_proposto - quota_reddito_rilevante
            if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
            if punteggio_isa_n_soc >= 8: aliquota_sostitutiva = 0.10
            elif punteggio_isa_n_soc >= 6: aliquota_sostitutiva = 0.12
            else: aliquota_sostitutiva = 0.15
            imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva
            base_imponibile_si_cpb = socio['altri_redditi'] + quota_reddito_rettificato_cpb - socio['cedolare_secca_redditi'] - socio['oneri_deducibili']
            tass_ordinaria_si_cpb = calcola_irpef(base_imponibile_si_cpb)
            carico_fiscale_concordato = imposta_sostitutiva + tass_ordinaria_si_cpb + socio['imposta_su_cedolare_secca'] - socio['acconti versati'] - socio['detrazioni IRPEF'] - socio['imposte_gia_trattenute']
            risparmio = carico_fiscale_no_cpb - carico_fiscale_concordato
            
            df_socio = pd.DataFrame({"Senza Concordato": [f"{carico_fiscale_no_cpb:,.2f} €"], "Con Concordato": [f"{carico_fiscale_concordato:,.2f} €"], "Risparmio/Onere": [f"{risparmio:,.2f} €"]}, index=["Carico Fiscale del Socio"]); st.table(df_socio)
            st.markdown("---")
