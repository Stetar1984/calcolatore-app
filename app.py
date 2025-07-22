import streamlit as st
import pandas as pd
import math

# ==============================================================================
# --- FUNZIONI DI CALCOLO ---
# ==============================================================================
def calcola_irpef(imponibile):
    """Calcola l'IRPEF lorda basata sugli scaglioni 2024/2025."""
    if imponibile <= 0: return 0
    if imponibile <= 28000: return imponibile * 0.23
    elif imponibile <= 50000: return (28000 * 0.23) + ((imponibile - 28000) * 0.35)
    else: return (28000 * 0.23) + (22000 * 0.35) + ((imponibile - 50000) * 0.43)

def calcola_inps_saldo(reddito_imponibile, gestione, minimale, fissi, scaglione1_cap, aliquota1, aliquota2, massimale):
    """Calcola il contributo INPS a saldo (fissi + variabili a scaglioni)."""
    aliquota1_dec = aliquota1 / 100.0
    aliquota2_dec = aliquota2 / 100.0
    
    reddito_imponibile_capped = min(reddito_imponibile, massimale)

    if gestione == "Gestione Separata":
        return reddito_imponibile_capped * aliquota1_dec
    
    elif gestione in ["Artigiani", "Commercianti"]:
        if reddito_imponibile_capped <= minimale:
            return fissi
        
        contributo1 = 0
        if reddito_imponibile_capped > minimale:
            base_imponibile1 = min(reddito_imponibile_capped, scaglione1_cap) - minimale
            contributo1 = base_imponibile1 * aliquota1_dec
        
        contributo2 = 0
        if reddito_imponibile_capped > scaglione1_cap:
            base_imponibile2 = reddito_imponibile_capped - scaglione1_cap
            contributo2 = base_imponibile2 * aliquota2_dec
            
        return fissi + contributo1 + contributo2
    return 0

def calcola_acconti_inps(reddito_base_acconto, gestione, minimale_acconti, scaglione1_cap, aliquota1, aliquota2, massimale):
    """Calcola i due acconti INPS per l'anno successivo."""
    if gestione == "Gestione Separata":
        totale_acconto = reddito_base_acconto * (aliquota1 / 100.0)
        return totale_acconto * 0.50, totale_acconto * 0.50

    base_imponibile_acconto = reddito_base_acconto - minimale_acconti
    if base_imponibile_acconto <= 0:
        return 0, 0
    
    base_imponibile_acconto_capped = min(base_imponibile_acconto + minimale_acconti, massimale) - minimale_acconti

    aliquota1_dec = aliquota1 / 100.0
    aliquota2_dec = aliquota2 / 100.0
    
    contributo1 = 0
    if base_imponibile_acconto_capped > 0:
        cap_primo_scaglione_variabile = scaglione1_cap - minimale_acconti
        base1 = min(base_imponibile_acconto_capped, cap_primo_scaglione_variabile)
        contributo1 = base1 * aliquota1_dec
    
    contributo2 = 0
    if base_imponibile_acconto_capped > (scaglione1_cap - minimale_acconti):
        base2 = base_imponibile_acconto_capped - (scaglione1_cap - minimale_acconti)
        contributo2 = base2 * aliquota2_dec
        
    totale_acconto = contributo1 + contributo2
    return totale_acconto * 0.50, totale_acconto * 0.50

def arrotonda_standard(valore):
    """Arrotonda un valore con il metodo standard (0.5 arrotonda per eccesso)."""
    return math.floor(valore * 100 + 0.5) / 100.0

# ==============================================================================
# --- DATABASE ALIQUOTE E IMPOSTAZIONI PAGINA ---
# ==============================================================================

aliquote_regionali_2024 = {
    "Abruzzo": 1.73, "Basilicata": 1.23, "Calabria": 1.73, "Campania": 1.73,
    "Emilia-Romagna": 1.33, "Friuli Venezia Giulia": 0.70, "Lazio": 1.73,
    "Liguria": 1.23, "Lombardia": 1.23, "Marche": 1.23, "Molise": 1.73,
    "Piemonte": 1.62, "Puglia": 1.33, "Sardegna": 1.23, "Sicilia": 1.23,
    "Toscana": 1.42, "Umbria": 1.23, "Valle d'Aosta": 1.23, "Veneto": 1.23,
    "Prov. Aut. Bolzano": 1.23, "Prov. Aut. Trento": 1.23
}
lista_regioni = list(aliquote_regionali_2024.keys())

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
            oneri_deducibili = st.number_input("ONERI DEDUCIBILI (escluso INPS) (RN3):", value=2000.0, format="%.2f", help=descrizioni_aggiuntive.get('oneri_deducibili'))
            cedolare_secca_redditi = st.number_input("REDDITI A CEDOLARE SECCA O TASS. SEPARATA (LC2 colonna 1):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('cedolare_secca_redditi'))
            imposte_gia_trattenute = st.number_input("RITENUTE TOTALI SUBITE (RN33 colonna 4):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('imposte_gia_trattenute'))
            imposta_su_cedolare_secca = st.number_input("IMPOSTA SU CEDOLARE SECCA (LC1 colonna 12/13):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('imposta_su_cedolare_secca'))
            acconti_versati = st.number_input("ACCONTI IRPEF VERSATI (RN38 colonna 6):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('acconti versati'))
            detrazioni_irpef = st.number_input("DETRAZIONI IRPEF TOTALI (RN22):", value=0.0, format="%.2f", help=descrizioni_aggiuntive.get('detrazioni IRPEF'))
            
        st.markdown("---")
        st.subheader("Addizionali e Contributi")
        col_add1, col_add2 = st.columns(2)
        with col_add1:
            st.markdown("**Addizionali IRPEF**")
            regione_selezionata = st.selectbox("Regione di Residenza:", options=lista_regioni, key="reg_ind", help="L'aliquota verrà applicata automaticamente. Per le regioni con aliquote progressive, viene usata l'aliquota base.")
            aliquota_add_comunale = st.number_input("Aliquota Addizionale Comunale (%):", value=0.80, format="%.2f", key="add_com_ind")
            aliquota_acconto_comunale = st.number_input("Aliquota Acconto Add. Comunale (%):", value=30.0, format="%.2f", key="acc_com_ind")
            addizionale_comunale_trattenuta = st.number_input("Addizionale Comunale già Trattenuta:", value=0.0, format="%.2f", key="add_com_trat_ind")
        
        with col_add2:
            st.markdown("**Dati Contributivi (INPS) - Valori 2024**")
            gestione_inps = st.selectbox("Gestione INPS:", ("Artigiani", "Commercianti", "Gestione Separata"), key="gest_ind")
            acconti_inps_versati = st.number_input("Acconti INPS Versati (parte variabile):", value=0.0, format="%.2f", key="acc_inps_ind")
            imponibile_minimale_acconti_2025 = st.number_input("Imponibile Minimale Acconti INPS 2025:", value=18415.0, format="%.2f", key="min_acc_ind")

        col_inps1, col_inps2, col_inps3 = st.columns(3)
        with col_inps1:
            contributi_fissi = st.number_input("Contributi Fissi INPS Versati:", value=4515.43, format="%.2f", key="fissi_ind")
            minimale_inps = st.number_input("Reddito Minimale INPS (saldo):", value=18415.0, format="%.2f", key="min_ind")
        with col_inps2:
            scaglione1_cap_inps = st.number_input("Cap 1° Scaglione INPS:", value=55008.0, format="%.2f", key="cap1_ind")
            aliquota_inps1 = st.number_input("Aliquota 1° Scaglione (%):", value=24.0, format="%.2f", key="aliq1_ind")
        with col_inps3:
            massimale_inps = st.number_input("Reddito Massimale INPS:", value=119650.0, format="%.2f", key="max_ind")
            aliquota_inps2 = st.number_input("Aliquota 2° Scaglione (%):", value=25.0, format="%.2f", key="aliq2_ind")
        
        submitted = st.form_submit_button("Esegui Simulazione")

    if submitted:
        # Codice di calcolo e output per Ditta Individuale/Professionista
        pass

#==============================================================================
# --- CALCOLATORE PER SOCIETÀ IN TRASPARENZA ---
#==============================================================================
elif tipo_calcolo == 'Società in trasparenza fiscale':
    st.header("Simulazione per Società in trasparenza fiscale")
    
    with st.form("form_societa"):
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

            st.markdown(f"**Dati Fiscali Personali (IRPEF) Socio {i+1}**")
            col_socio1, col_socio2 = st.columns(2)
            with col_socio1:
                socio_data['altri_redditi'] = st.number_input(f"ALTRI REDDITI TASSABILI IRPEF Socio {i+1}", value=0.0, format="%.2f", key=f"ar_soc_{i}", help=descrizioni_aggiuntive.get('altri_redditi'))
                socio_data['oneri_deducibili'] = st.number_input(f"ONERI DEDUCIBILI (escluso INPS quota socio) Socio {i+1}", value=0.0, format="%.2f", key=f"od_soc_{i}", help=descrizioni_aggiuntive.get('oneri_deducibili'))
                socio_data['cedolare_secca_redditi'] = st.number_input(f"REDDITI A CEDOLARE SECCA O TASS. SEPARATA Socio {i+1}", value=0.0, format="%.2f", key=f"csr_soc_{i}", help=descrizioni_aggiuntive.get('cedolare_secca_redditi'))
                socio_data['imposte_gia_trattenute'] = st.number_input(f"RITENUTE TOTALI SUBITE Socio {i+1}", value=0.0, format="%.2f", key=f"igt_soc_{i}", help=descrizioni_aggiuntive.get('imposte_gia_trattenute'))
            with col_socio2:
                socio_data['imposta_su_cedolare_secca'] = st.number_input(f"IMPOSTA SU CEDOLARE SECCA Socio {i+1}", value=0.0, format="%.2f", key=f"ics_soc_{i}", help=descrizioni_aggiuntive.get('imposta_su_cedolare_secca'))
                socio_data['acconti_versati'] = st.number_input(f"ACCONTI IRPEF VERSATI Socio {i+1}", value=0.0, format="%.2f", key=f"av_soc_{i}", help=descrizioni_aggiuntive.get('acconti versati'))
                socio_data['detrazioni_irpef'] = st.number_input(f"DETRAZIONI IRPEF TOTALI Socio {i+1}", value=0.0, format="%.2f", key=f"di_soc_{i}", help=descrizioni_aggiuntive.get('detrazioni IRPEF'))

            st.markdown(f"**Addizionali e Contributi Socio {i+1}**")
            col_add_soc1, col_add_soc2 = st.columns(2)
            with col_add_soc1:
                socio_data['regione_selezionata'] = col_add_soc1.selectbox(f"Regione di Residenza Socio {i+1}:", options=lista_regioni, key=f"reg_soc_{i}")
                socio_data['aliquota_add_comunale'] = col_add_soc1.number_input(f"Aliquota Add. Comunale (%) Socio {i+1}", value=0.8, format="%.2f", key=f"add_com_soc_{i}")
                socio_data['aliquota_acconto_comunale'] = col_add_soc1.number_input(f"Aliquota Acconto Add. Comunale (%) Socio {i+1}", value=30.0, format="%.2f", key=f"acc_com_soc_{i}")
                socio_data['addizionale_comunale_trattenuta'] = col_add_soc1.number_input(f"Addizionale Comunale già Trattenuta Socio {i+1}:", value=0.0, format="%.2f", key=f"add_com_trat_soc_{i}")
            with col_add_soc2:
                socio_data['gestione_inps'] = col_add_soc2.selectbox(f"Gestione INPS Socio {i+1}:", ("Artigiani", "Commercianti", "Gestione Separata"), key=f"gest_soc_{i}")
                socio_data['acconti_inps_versati'] = col_add_soc2.number_input(f"Acconti INPS Versati (var.) Socio {i+1}", value=0.0, format="%.2f", key=f"acc_inps_soc_{i}")
            
            col_inps_s1, col_inps_s2, col_inps_s3 = st.columns(3)
            with col_inps_s1:
                socio_data['contributi_fissi'] = col_inps_s1.number_input(f"Contributi Fissi INPS Versati Socio {i+1}:", value=4515.43, format="%.2f", key=f"fissi_soc_{i}")
                socio_data['minimale_inps'] = col_inps_s1.number_input(f"Reddito Minimale INPS (saldo) Socio {i+1}:", value=18415.0, format="%.2f", key=f"min_soc_{i}")
            with col_inps_s2:
                 socio_data['aliquota_inps1'] = col_inps_s2.number_input(f"Aliquota 1° Scaglione (%) Socio {i+1}:", value=24.0, format="%.2f", key=f"aliq1_soc_{i}")
                 socio_data['aliquota_inps2'] = col_inps_s2.number_input(f"Aliquota 2° Scaglione (%) Socio {i+1}:", value=25.0, format="%.2f", key=f"aliq2_soc_{i}")
            with col_inps_s3:
                socio_data['scaglione1_cap_inps'] = col_inps_s3.number_input(f"Cap 1° Scaglione INPS Socio {i+1}:", value=55008.0, format="%.2f", key=f"cap1_soc_{i}")
                socio_data['massimale_inps'] = col_inps_s3.number_input(f"Reddito Massimale INPS Socio {i+1}:", value=119650.0, format="%.2f", key=f"max_soc_{i}")
            
            soci_inputs.append(socio_data)
        
        submitted_soc = st.form_submit_button("Esegui Simulazione Società")

    if submitted_soc:
        # Codice di calcolo e output per Società in Trasparenza...
        # ... (omesso per brevità, resta invariato)
        pass
