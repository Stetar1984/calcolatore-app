import streamlit as st
import pandas as pd

# ==============================================================================
# --- FUNZIONI DI CALCOLO ---
# ==============================================================================
def calcola_irpef(imponibile):
    """Calcola l'IRPEF lorda basata sugli scaglioni 2024/2025."""
    if imponibile <= 0: return 0
    if imponibile <= 28000: return imponibile * 0.23
    elif imponibile <= 50000: return (28000 * 0.23) + ((imponibile - 28000) * 0.35)
    else: return (28000 * 0.23) + (22000 * 0.35) + ((imponibile - 50000) * 0.43)

def calcola_inps(reddito_imponibile, gestione, minimale, fissi, scaglione1_cap, aliquota1, aliquota2, massimale):
    """Calcola i contributi INPS dovuti (fissi + variabili a scaglioni)."""
    aliquota1_dec = aliquota1 / 100.0
    aliquota2_dec = aliquota2 / 100.0
    
    # Il reddito imponibile ai fini INPS non può superare il massimale
    reddito_imponibile_capped = min(reddito_imponibile, massimale)

    if gestione == "Gestione Separata":
        # Per la Gestione Separata si applica un'aliquota unica senza minimale in questo contesto
        return reddito_imponibile_capped * aliquota1_dec
    
    elif gestione in ["Artigiani", "Commercianti"]:
        if reddito_imponibile_capped <= minimale:
            return fissi
        
        contributo1 = 0
        # Calcolo sul primo scaglione (da minimale a scaglione1_cap)
        if reddito_imponibile_capped > minimale:
            base_imponibile1 = min(reddito_imponibile_capped, scaglione1_cap) - minimale
            contributo1 = base_imponibile1 * aliquota1_dec
        
        contributo2 = 0
        # Calcolo sul secondo scaglione (oltre scaglione1_cap)
        if reddito_imponibile_capped > scaglione1_cap:
            base_imponibile2 = reddito_imponibile_capped - scaglione1_cap
            contributo2 = base_imponibile2 * aliquota2_dec
            
        return fissi + contributo1 + contributo2
    return 0

# ==============================================================================
# --- IMPOSTAZIONI PAGINA E TITOLO ---
# ==============================================================================
st.set_page_config(layout="wide", page_title="Calcolatore CPB")
st.title("Calcolatore di Convenienza Concordato Preventivo Biennale")
st.markdown("Questo strumento confronta il carico fiscale e contributivo totale con e senza l'adesione al CPB.")

# ==============================================================================
# --- DIZIONARIO DELLE DESCRIZIONI AGGIUNTIVE ---
# ==============================================================================
descrizioni_aggiuntive = {
    'reddito_simulato_2024': "CP10 colonna 2",
    'reddito_rilevante_cpb_2023': "CP1 colonna 2",
    'reddito_proposto_cpb_2024': "CP1 colonna 1",
    'reddito_impresa_rettificato_cpb': "CP7 colonna 5",
    'altri_redditi': "da riepilogo redditi RN + LC2 colonna 1",
    'oneri_deducibili': "RN3 - Inserire qui gli oneri deducibili DIVERSI dai contributi INPS, che verranno calcolati a parte.",
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
    ('Ditta Individuale', 'Società in trasparenza fiscale', 'Professionista'),
    horizontal=True,
)
st.markdown("---")

# ==============================================================================
# --- CALCOLATORE PER DITTA INDIVIDUALE O PROFESSIONISTA ---
# ==============================================================================
if tipo_calcolo == 'Ditta Individuale' or tipo_calcolo == 'Professionista':
    st.header(f"Simulazione per {tipo_calcolo}")
    
    with st.form(f"form_{tipo_calcolo.lower().replace(' ', '_')}"):
        st.subheader("Dati di Input")
        col1, col2 = st.columns(2)

        with col1:
            nome_soggetto = st.text_input(f"NOME {tipo_calcolo.upper()}:", value=f'Mio Studio {tipo_calcolo}')
            reddito_simulato_2024 = st.number_input("REDDITO EFFETTIVO O SIMULATO (CP10 colonna 6):", value=70000.0, format="%.2f", help=descrizioni_aggiuntive.get('reddito_simulato_2024'))
            reddito_rilevante_cpb_2023 = st.number_input("REDDITO RILEVANTE CPB (CP1 colonna 2):", value=65000.0, format="%.2f", help=descrizioni_aggiuntive.get('reddito_rilevante_cpb_2023'))
            reddito_proposto_cpb_2024 = st.number_input("REDDITO PROPOSTO AI FINI CPB (CP1 colonna 1):", value=72000.0, format="%.2f", help=descrizioni_aggiuntive.get('reddito_proposto_cpb_2024'))
            reddito_impresa_rettificato_cpb = st.number_input("REDDITO D'IMPRESA RETTIFICATO PER CPB (CP7 colonna 5):", value=72000.0, format="%.2f", help=descrizioni_aggiuntive.get('reddito_impresa_rettificato_cpb'))
            punteggio_isa_n_ind = st.slider("Punteggio ISA anno n (2023):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)

        with col2:
            altri_redditi = st.number_input("ALTRI REDDITI TASSABILI IRPEF (da riepilogo redditi RN + LC2 colonna 1):", value=5000.0, format="%.2f", help=descrizioni_aggiuntive.get('altri_redditi'))
            oneri_deducibili = st.number_input("ONERI DEDUCIBILI (RN3):", value=2000.0, format="%.2f", help=descrizioni_aggiuntive.get('oneri_deducibili'))
            cedolare_secca_redditi = st.number_input("REDDITI A CEDOLARE SECCA O TASS. SEPARATA (LC2 colonna 1):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('cedolare_secca_redditi'))
            imposte_gia_trattenute = st.number_input("IMPOSTE SU REDDITI GIA' TASSATI E RITENUTE (RN33 colonna 4):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('imposte_gia_trattenute'))
            imposta_su_cedolare_secca = st.number_input("IMPOSTA SU CEDOLARE SECCA (LC1 colonna 12/13):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('imposta_su_cedolare_secca'))
            acconti_versati = st.number_input("ACCONTI VERSATI (RN38 colonna 6):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('acconti versati'))
            detrazioni_irpef = st.number_input("DETRAZIONI IRPEF TOTALI (RN22):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('detrazioni IRPEF'))
            
        st.markdown("---")
        st.subheader("Dati Contributivi (INPS) - Valori 2024")
        gestione_inps = st.selectbox("Gestione INPS:", ("Artigiani", "Commercianti", "Gestione Separata"), key="gest_ind")
        
        col_inps1, col_inps2, col_inps3 = st.columns(3)
        with col_inps1:
            contributi_fissi = st.number_input("Contributi Fissi INPS Versati:", value=4515.43, format="%.2f", key="fissi_ind")
            minimale_inps = st.number_input("Reddito Minimale INPS:", value=18415.0, format="%.2f", key="min_ind")
        with col_inps2:
            scaglione1_cap_inps = st.number_input("Cap 1° Scaglione INPS:", value=55008.0, format="%.2f", key="cap1_ind")
            aliquota_inps1 = st.number_input("Aliquota 1° Scaglione (%):", value=24.0, format="%.2f", key="aliq1_ind")
        with col_inps3:
            massimale_inps = st.number_input("Reddito Massimale INPS:", value=119650.0, format="%.2f", key="max_ind")
            aliquota_inps2 = st.number_input("Aliquota 2° Scaglione (%):", value=25.0, format="%.2f", key="aliq2_ind")
        
        submitted = st.form_submit_button("Esegui Simulazione")

    if submitted:
        # Calcoli fiscali come da codice originale
        base_imponibile_no_cpb_irpef = reddito_simulato_2024 + altri_redditi - oneri_deducibili - cedolare_secca_redditi
        tassazione_no_cpb_irpef = calcola_irpef(base_imponibile_no_cpb_irpef)
        totale_tassazione_no_cpb = tassazione_no_cpb_irpef - imposte_gia_trattenute + imposta_su_cedolare_secca - acconti_versati - detrazioni_irpef
        
        base_imponibile_si_cpb_irpef = altri_redditi + reddito_impresa_rettificato_cpb - cedolare_secca_redditi - oneri_deducibili
        base_imponibile_sostitutiva = reddito_proposto_cpb_2024 - reddito_rilevante_cpb_2023
        if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
        if punteggio_isa_n_ind >= 8: aliquota_sostitutiva = 0.10
        elif punteggio_isa_n_ind >= 6: aliquota_sostitutiva = 0.12
        else: aliquota_sostitutiva = 0.15
        imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva
        tass_ordinaria_si_cpb = calcola_irpef(base_imponibile_si_cpb_irpef)
        totale_tassazione_si_cpb = imposta_sostitutiva + tass_ordinaria_si_cpb + imposta_su_cedolare_secca - acconti_versati - detrazioni_irpef - imposte_gia_trattenute
        
        # Calcoli contributivi INPS
        inps_su_effettivo = calcola_inps(reddito_simulato_2024, gestione_inps, minimale_inps, contributi_fissi, scaglione1_cap_inps, aliquota_inps1, aliquota_inps2, massimale_inps)
        inps_su_concordato = calcola_inps(reddito_proposto_cpb_2024, gestione_inps, minimale_inps, contributi_fissi, scaglione1_cap_inps, aliquota_inps1, aliquota_inps2, massimale_inps)

        # Calcoli totali
        carico_totale_no_cpb = totale_tassazione_no_cpb + inps_su_effettivo - contributi_fissi
        carico_totale_si_cpb_concordato = totale_tassazione_si_cpb + inps_su_concordato - contributi fissi
        carico_totale_si_cpb_effettivo = totale_tassazione_si_cpb + inps_su_effettivo - contributi fissi
        
        # --- TABELLA DI OUTPUT DETTAGLIATA ---
        st.markdown(f"<h4>Risultati Dettagliati per: {nome_soggetto}</h4>", unsafe_allow_html=True)
        df_risultati = pd.DataFrame({
            "Senza Concordato": [
                f"{totale_tassazione_no_cpb:,.2f} €",
                f"{inps_su_effettivo:,.2f} €",
                f"**{carico_totale_no_cpb:,.2f} €**"
            ],
            "Con Concordato (INPS su Concordato)": [
                f"{totale_tassazione_si_cpb:,.2f} €",
                f"{inps_su_concordato:,.2f} €",
                f"**{carico_totale_si_cpb_concordato:,.2f} €**"
            ],
            "Con Concordato (INPS su Effettivo)": [
                f"{totale_tassazione_si_cpb:,.2f} €",
                f"{inps_su_effettivo:,.2f} €",
                f"**{carico_totale_si_cpb_effettivo:,.2f} €**"
            ]
        }, index=["Carico Fiscale (Saldo IRPEF)", "Carico Contributivo (INPS) ", "CARICO TOTALE (Fisco + INPS) "])
        st.table(df_risultati)
        
        risparmio_concordato = carico_totale_no_cpb - carico_totale_si_cpb_concordato
        risparmio_effettivo = carico_totale_no_cpb - carico_totale_si_cpb_effettivo
        st.success(f"Risparmio/Onere scegliendo 'INPS su Concordato': {risparmio_concordato:,.2f} €")
        st.info(f"Risparmio/Onere scegliendo 'INPS su Effettivo': {risparmio_effettivo:,.2f} €")

#==============================================================================
# --- CALCOLATORE PER SOCIETÀ IN TRASPARENZA ---
#==============================================================================
elif tipo_calcolo == 'Società in trasparenza fiscale':
    st.header("Simulazione per Società in trasparenza fiscale")
    
    with st.form("form_societa"):
        # --- INPUT SOCIETA' (INVARIATI) ---
        st.subheader("Dati Società")
        col1_soc, col2_soc = st.columns(2)
        with col1_soc:
            nome_societa = st.text_input("NOME SOCIETA':", value='Mia Società S.n.c.')
            reddito_simulato_2024_soc = st.number_input("REDDITO EFFETTIVO O SIMULATO SOCIETA' (CP10 colonna 1):", value=142000.0, format="%.2f")
            reddito_rilevante_cpb_2023_soc = st.number_input("REDDITO RILEVANTE CPB SOCIETA' (CP1 colonna 2):", value=139872.0, format="%.2f")
            reddito_proposto_cpb_2024_soc = st.number_input("REDDITO PROPOSTO CPB SOCIETA' (CP1 colonna 1):", value=151784.0, format="%.2f")
            reddito_impresa_rettificato_cpb_soc = st.number_input("REDDITO D'IMPRESA RETTIFICATO PER CPB SOCIETA' (CP7 colonna 5):", value=152420.49, format="%.2f")
        with col2_soc:
            valore_produzione_simulato_2024_soc = st.number_input("VALORE PRODUZIONE EFFETTIVO O SIMULATO SOCIETA' (IP73 colonna 4):", value=149604.0, format="%.2f")
            valore_produzione_irap_rettificato_cpb_soc = st.number_input("Valore della produzione IRAP rettificato per CPB SOCIETA' (IP74):", value=318210.49, format="%.2f")
            punteggio_isa_n_soc = st.slider("Punteggio ISA Società (anno n):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)

        st.markdown("---")
        st.subheader("Dati dei Singoli Soci")
        
        num_soci = st.number_input("Numero di soci da analizzare:", min_value=1, max_value=5, value=2)
        soci_inputs = []
        
        for i in range(num_soci):
            st.markdown(f"--- \n ##### Dati Socio {i+1}")
            socio_data = {}
            col_socio_nome, col_socio_quota = st.columns(2)
            socio_data['nome_socio'] = col_socio_nome.text_input(f"Nome Socio {i+1}", value=f"Socio {i+1}", key=f"nome_{i}")
            socio_data['quota_partecipazione'] = col_socio_quota.number_input(f"Quota di Partecipazione (%) Socio {i+1}", value=(50.0 if i < 2 else 0.0), format="%.2f", key=f"quota_{i}")

            # --- SEZIONE INPUT FISCALI PER SOCIO (MODIFICATA) ---
            st.markdown(f"**Dati Fiscali Personali (IRPEF) Socio {i+1}**")
            col_socio1, col_socio2 = st.columns(2)
            with col_socio1:
                socio_data['altri_redditi'] = st.number_input(f"ALTRI REDDITI TASSABILI IRPEF Socio {i+1}", value=0.0, format="%.2f", key=f"ar_soc_{i}", help=descrizioni_aggiuntive.get('altri_redditi'))
                socio_data['oneri_deducibili'] = st.number_input(f"ONERI DEDUCIBILI Socio {i+1}", value=0.0, format="%.2f", key=f"od_soc_{i}", help=descrizioni_aggiuntive.get('oneri_deducibili'))
                socio_data['cedolare_secca_redditi'] = st.number_input(f"REDDITI A CEDOLARE SECCA O TASS. SEPARATA Socio {i+1}", value=0.0, format="%.2f", key=f"csr_soc_{i}", help=descrizioni_aggiuntive.get('cedolare_secca_redditi'))
                socio_data['imposte_gia_trattenute'] = st.number_input(f"IMPOSTE SU REDDITI GIA' TASSATI E RITENUTE Socio {i+1}", value=0.0, format="%.2f", key=f"igt_soc_{i}", help=descrizioni_aggiuntive.get('imposte_gia_trattenute'))
            with col_socio2:
                socio_data['imposta_su_cedolare_secca'] = st.number_input(f"IMPOSTA SU CEDOLARE SECCA Socio {i+1}", value=0.0, format="%.2f", key=f"ics_soc_{i}", help=descrizioni_aggiuntive.get('imposta_su_cedolare_secca'))
                socio_data['acconti_versati'] = st.number_input(f"ACCONTI VERSATI Socio {i+1}", value=0.0, format="%.2f", key=f"av_soc_{i}", help=descrizioni_aggiuntive.get('acconti versati'))
                socio_data['detrazioni_irpef'] = st.number_input(f"DETRAZIONI IRPEF TOTALI Socio {i+1}", value=0.0, format="%.2f", key=f"di_soc_{i}", help=descrizioni_aggiuntive.get('detrazioni IRPEF'))

            # --- SEZIONE INPUT INPS PER SOCIO (INVARIATA) ---
            st.markdown(f"**Dati Contributivi (INPS) Socio {i+1}**")
            col_inps_s1, col_inps_s2, col_inps_s3 = st.columns(3)
            with col_inps_s1:
                socio_data['gestione_inps'] = col_inps_s1.selectbox(f"Gestione INPS Socio {i+1}:", ("Artigiani", "Commercianti", "Gestione Separata"), key=f"gest_soc_{i}")
                socio_data['contributi_fissi'] = col_inps_s1.number_input(f"Contributi Fissi INPS Versati Socio {i+1}:", value=4515.43, format="%.2f", key=f"fissi_soc_{i}")
            with col_inps_s2:
                 socio_data['aliquota_inps1'] = col_inps_s2.number_input(f"Aliquota 1° Scaglione (%) Socio {i+1}:", value=24.0, format="%.2f", key=f"aliq1_soc_{i}")
                 socio_data['aliquota_inps2'] = col_inps_s2.number_input(f"Aliquota 2° Scaglione (%) Socio {i+1}:", value=25.0, format="%.2f", key=f"aliq2_soc_{i}")
            with col_inps_s3:
                socio_data['minimale_inps'] = col_inps_s3.number_input(f"Reddito Minimale INPS Socio {i+1}:", value=18415.0, format="%.2f", key=f"min_soc_{i}")
                socio_data['scaglione1_cap_inps'] = col_inps_s3.number_input(f"Cap 1° Scaglione INPS Socio {i+1}:", value=55008.0, format="%.2f", key=f"cap1_soc_{i}")
                socio_data['massimale_inps'] = col_inps_s3.number_input(f"Reddito Massimale INPS Socio {i+1}:", value=119650.0, format="%.2f", key=f"max_soc_{i}")
            
            soci_inputs.append(socio_data)
        
        submitted_soc = st.form_submit_button("Esegui Simulazione Società")

    if submitted_soc:
        # CALCOLO IRAP (INVARIATO)
        st.markdown("---"); st.subheader(f"Parte 1: Analisi IRAP per la Società: {nome_societa}")
        aliquota_irap = 0.039; irap_no_cpb = valore_produzione_simulato_2024_soc * aliquota_irap; irap_si_cpb = valore_produzione_irap_rettificato_cpb_soc * aliquota_irap; risparmio_irap = irap_no_cpb - irap_si_cpb
        df_irap = pd.DataFrame({"Senza Concordato": [f"{irap_no_cpb:,.2f} €"], "Con Concordato": [f"{irap_si_cpb:,.2f} €"], "Risparmio/Onere IRAP": [f"{risparmio_irap:,.2f} €"]}, index=["Imposta IRAP Dovuta"]); st.table(df_irap)
        
        st.markdown("---"); st.subheader("Parte 2: Analisi IRPEF e INPS per i Singoli Soci")
        
        for i, socio in enumerate(soci_inputs):
            perc_socio = socio['quota_partecipazione'] / 100.0
            if perc_socio == 0: continue
            
            st.markdown(f"### Riepilogo per: {socio['nome_socio']} (Quota: {socio['quota_partecipazione']:.2f}%)")
            
            quota_reddito_simulato = reddito_simulato_2024_soc * perc_socio
            quota_reddito_rilevante = reddito_rilevante_cpb_2023_soc * perc_socio
            quota_reddito_proposto = reddito_proposto_cpb_2024_soc * perc_socio
            quota_reddito_rettificato_cpb = reddito_impresa_rettificato_cpb_soc * perc_socio

            # Calcoli fiscali come da codice originale (INVARIATI)
            base_imponibile_no_cpb_irpef = quota_reddito_simulato + socio['altri_redditi'] - socio['oneri_deducibili'] - socio['cedolare_secca_redditi']
            irpef_ordinaria_no_cpb = calcola_irpef(base_imponibile_no_cpb_irpef)
            carico_fiscale_no_cpb = irpef_ordinaria_no_cpb - socio['imposte_gia_trattenute'] + socio['imposta_su_cedolare_secca'] - socio['acconti_versati'] - socio['detrazioni_irpef']

            base_imponibile_sostitutiva = quota_reddito_proposto - quota_reddito_rilevante
            if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
            if punteggio_isa_n_soc >= 8: aliquota_sostitutiva = 0.10
            elif punteggio_isa_n_soc >= 6: aliquota_sostitutiva = 0.12
            else: aliquota_sostitutiva = 0.15
            imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva
            base_imponibile_si_cpb_irpef = socio['altri_redditi'] + quota_reddito_rettificato_cpb - socio['oneri_deducibili'] - socio['cedolare_secca_redditi']
            tass_ordinaria_si_cpb = calcola_irpef(base_imponibile_si_cpb_irpef)
            carico_fiscale_concordato = imposta_sostitutiva + tass_ordinaria_si_cpb + socio['imposta_su_cedolare_secca'] - socio['acconti_versati'] - socio['detrazioni_irpef'] - socio['imposte_gia_trattenute']

            # Calcoli contributivi INPS
            inps_su_effettivo = calcola_inps(quota_reddito_simulato, socio['gestione_inps'], socio['minimale_inps'], socio['contributi_fissi'], socio['scaglione1_cap_inps'], socio['aliquota_inps1'], socio['aliquota_inps2'], socio['massimale_inps'])
            inps_su_concordato = calcola_inps(quota_reddito_proposto, socio['gestione_inps'], socio['minimale_inps'], socio['contributi_fissi'], socio['scaglione1_cap_inps'], socio['aliquota_inps1'], socio['aliquota_inps2'], socio['massimale_inps'])
            
            # Calcoli totali
            carico_totale_no_cpb = carico_fiscale_no_cpb + inps_su_effettivo - contributi_fissi
            carico_totale_si_cpb_concordato = carico_fiscale_concordato + inps_su_concordato - contributi_fissi
            carico_totale_si_cpb_effettivo = carico_fiscale_concordato + inps_su_effettivo - contributi_fissi

            # Tabella di output per il socio
            df_socio = pd.DataFrame({
                "Senza Concordato": [ f"{carico_fiscale_no_cpb:,.2f} €", f"{inps_su_effettivo:,.2f} €", f"**{carico_totale_no_cpb:,.2f} €**" ],
                "Con Concordato (INPS su Concordato)": [ f"{carico_fiscale_concordato:,.2f} €", f"{inps_su_concordato:,.2f} €", f"**{carico_totale_si_cpb_concordato:,.2f} €**" ],
                "Con Concordato (INPS su Effettivo)": [ f"{carico_fiscale_concordato:,.2f} €", f"{inps_su_effettivo:,.2f} €", f"**{carico_totale_si_cpb_effettivo:,.2f} €**" ]
            }, index=["Carico Fiscale (Saldo IRPEF)", "Carico Contributivo (INPS) ", "CARICO TOTALE (Fisco + INPS) "])
            st.table(df_socio)

            risparmio1 = carico_totale_no_cpb - carico_totale_si_cpb_concordato
            risparmio2 = carico_totale_no_cpb - carico_totale_si_cpb_effettivo
            st.success(f"Risparmio/Onere Socio (Opzione INPS su Concordato): {risparmio1:,.2f} €")
            st.info(f"Risparmio/Onere Socio (Opzione INPS su Effettivo): {risparmio2:,.2f} €")
            st.markdown("---")
