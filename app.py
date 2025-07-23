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

def calcola_acconti_inps(reddito_base_acconto, gestione, minimale_acconti, scaglione1_cap_acconti, aliquota1, aliquota2, massimale):
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
        cap_primo_scaglione_variabile = scaglione1_cap_acconti - minimale_acconti
        base1 = min(base_imponibile_acconto_capped, cap_primo_scaglione_variabile)
        contributo1 = base1 * aliquota1_dec
    
    contributo2 = 0
    if base_imponibile_acconto_capped > (scaglione1_cap_acconti - minimale_acconti):
        base2 = base_imponibile_acconto_capped - (scaglione1_cap_acconti - minimale_acconti)
        contributo2 = base2 * aliquota2_dec
        
    totale_acconto = contributo1 + contributo2
    return totale_acconto * 0.50, totale_acconto * 0.50

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
            aliquota_add_regionale = st.number_input("Aliquota Addizionale Regionale (%):", value=1.23, format="%.2f", key="add_reg_ind")
            addizionale_regionale_trattenuta = st.number_input("Addizionale Regionale già Trattenuta:", value=0.0, format="%.2f", key="add_reg_tratt_ind")
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
            scaglione1_cap_inps = st.number_input("Cap 1° Scaglione INPS (saldo):", value=55008.0, format="%.2f", key="cap1_ind")
            aliquota_inps1 = st.number_input("Aliquota 1° Scaglione (%):", value=24.0, format="%.2f", key="aliq1_ind")
        with col_inps3:
            massimale_inps = st.number_input("Reddito Massimale INPS:", value=119650.0, format="%.2f", key="max_ind")
            aliquota_inps2 = st.number_input("Aliquota 2° Scaglione (%):", value=25.0, format="%.2f", key="aliq2_ind")
            scaglione1_cap_inps_acconti = st.number_input("Cap 1° Scaglione INPS (acconti):", value=55448.0, format="%.2f", key="cap1_acc_ind")

        submitted = st.form_submit_button("Esegui Simulazione")

    if submitted:
        # Calcolo imponibili IRPEF
        base_imponibile_no_cpb_irpef = reddito_simulato_2024 + altri_redditi - oneri_deducibili
        base_imponibile_si_cpb_irpef = altri_redditi + reddito_impresa_rettificato_cpb - oneri_deducibili
        
        # Calcolo IRPEF lorda
        irpef_lorda_no_cpb = calcola_irpef(base_imponibile_no_cpb_irpef)
        
        base_imponibile_sostitutiva = reddito_proposto_cpb_2024 - reddito_rilevante_cpb_2023
        if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
        if punteggio_isa_n_ind >= 8: aliquota_sostitutiva = 0.10
        elif punteggio_isa_n_ind >= 6: aliquota_sostitutiva = 0.12
        else: aliquota_sostitutiva = 0.15
        imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva
        irpef_lorda_si_cpb = calcola_irpef(base_imponibile_si_cpb_irpef)

        # Calcolo Addizionali
        addizionale_regionale_no_cpb = base_imponibile_no_cpb_irpef * (aliquota_add_regionale / 100.0)
        addizionale_comunale_no_cpb = base_imponibile_no_cpb_irpef * (aliquota_add_comunale / 100.0)
        addizionale_regionale_si_cpb = base_imponibile_si_cpb_irpef * (aliquota_add_regionale / 100.0)
        addizionale_comunale_si_cpb = base_imponibile_si_cpb_irpef * (aliquota_add_comunale / 100.0)
        
        # Calcolo Contributi INPS
        inps_dovuti_effettivo = calcola_inps_saldo(reddito_simulato_2024, gestione_inps, minimale_inps, contributi_fissi, scaglione1_cap_inps, aliquota_inps1, aliquota_inps2, massimale_inps)
        inps_dovuti_concordato = calcola_inps_saldo(reddito_proposto_cpb_2024, gestione_inps, minimale_inps, contributi_fissi, scaglione1_cap_inps, aliquota_inps1, aliquota_inps2, massimale_inps)
        
        # Calcolo Saldo INPS
        saldo_inps_no_cpb = inps_dovuti_effettivo - contributi_fissi - acconti_inps_versati
        saldo_inps_si_cpb_concordato = inps_dovuti_concordato - contributi_fissi - acconti_inps_versati
        saldo_inps_si_cpb_effettivo = inps_dovuti_effettivo - contributi_fissi - acconti_inps_versati
        
        # --- MODIFICA RICHIESTA: CALCOLO IRPEF NETTA E SALDO ---
        irpef_netta_no_cpb = max(0, irpef_lorda_no_cpb - detrazioni_irpef)
        saldo_irpef_no_cpb = irpef_netta_no_cpb - imposte_gia_trattenute - acconti_versati
        
        irpef_netta_si_cpb = max(0, irpef_lorda_si_cpb - detrazioni_irpef)
        saldo_irpef_si_cpb = irpef_netta_si_cpb - imposte_gia_trattenute - acconti_versati
        
        # Calcolo Acconti 2025
        base_acconto_irpef_no_cpb = irpef_netta_no_cpb - imposte_gia_trattenute
        acconto_irpef_no_cpb = (base_acconto_irpef_no_cpb * 0.50) if base_acconto_irpef_no_cpb > 0 else 0
        
        base_acconto_irpef_si_cpb = irpef_netta_si_cpb - imposte_gia_trattenute
        acconto_irpef_si_cpb = (base_acconto_irpef_si_cpb * 0.50) if base_acconto_irpef_si_cpb > 0 else 0

        acconto_comunale_no_cpb = addizionale_comunale_no_cpb * (aliquota_acconto_comunale / 100.0)
        acconto_comunale_si_cpb = addizionale_comunale_si_cpb * (aliquota_acconto_comunale / 100.0)
        
        acconto_1_inps_no_cpb, acconto_2_inps_no_cpb = calcola_acconti_inps(reddito_simulato_2024, gestione_inps, imponibile_minimale_acconti_2025, scaglione1_cap_inps_acconti, aliquota_inps1, aliquota_inps2, massimale_inps)
        acconto_1_inps_si_cpb, acconto_2_inps_si_cpb = calcola_acconti_inps(reddito_proposto_cpb_2024, gestione_inps, imponibile_minimale_acconti_2025, scaglione1_cap_inps_acconti, aliquota_inps1, aliquota_inps2, massimale_inps)




# --- PRESENTAZIONE RISULTATI ---
        st.markdown(f"<h4>Risultati Dettagliati per: {nome_soggetto}</h4>", unsafe_allow_html=True)
        st.subheader("Riepilogo Saldi Finali e Acconti da Versare")
        
        # Calcolo totali da versare
        totale_versare_no_cpb = saldo_irpef_no_cpb + saldo_add_regionale_no_cpb + saldo_add_comunale_no_cpb + saldo_inps_no_cpb + (acconto_irpef_no_cpb * 2) + acconto_comunale_no_cpb + acconto_1_inps_no_cpb + acconto_2_inps_no_cpb
        totale_versare_si_cpb_conc = saldo_irpef_si_cpb + imposta_sostitutiva + saldo_add_regionale_si_cpb + saldo_add_comunale_si_cpb + saldo_inps_si_cpb_concordato + (acconto_irpef_si_cpb * 2) + acconto_comunale_si_cpb + acconto_1_inps_si_cpb + acconto_2_inps_si_cpb
        totale_versare_si_cpb_eff = saldo_irpef_si_cpb + imposta_sostitutiva + saldo_add_regionale_si_cpb + saldo_add_comunale_si_cpb + saldo_inps_si_cpb_effettivo + (acconto_irpef_si_cpb * 2) + acconto_comunale_si_cpb + acconto_1_inps_no_cpb + acconto_2_inps_no_cpb # Per l'opzione INPS su effettivo, anche gli acconti INPS si basano sull'effettivo

        df_saldi = pd.DataFrame({
             "Senza Concordato": [f"{saldo_irpef_no_cpb:,.2f} €", f"N/A", f"{saldo_add_regionale_no_cpb:,.2f} €", f"{saldo_add_comunale_no_cpb:,.2f} €", f"{saldo_inps_no_cpb:,.2f} €", f"{acconto_irpef_no_cpb:,.2f} €", f"{acconto_irpef_no_cpb:,.2f} €", f"{acconto_comunale_no_cpb:,.2f} €", f"{acconto_1_inps_no_cpb:,.2f} €", f"{acconto_2_inps_no_cpb:,.2f} €", f"**{totale_versare_no_cpb:,.2f} €**"],
             "Con Concordato (INPS su Concordato)": [f"{saldo_irpef_si_cpb:,.2f} €", f"{imposta_sostitutiva:,.2f} €", f"{saldo_add_regionale_si_cpb:,.2f} €", f"{saldo_add_comunale_si_cpb:,.2f} €", f"{saldo_inps_si_cpb_concordato:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_comunale_si_cpb:,.2f} €", f"{acconto_1_inps_si_cpb:,.2f} €", f"{acconto_2_inps_si_cpb:,.2f} €", f"**{totale_versare_si_cpb_conc:,.2f} €**"],
             "Con Concordato (INPS su Effettivo)": [f"{saldo_irpef_si_cpb:,.2f} €", f"{imposta_sostitutiva:,.2f} €", f"{saldo_add_regionale_si_cpb:,.2f} €", f"{saldo_add_comunale_si_cpb:,.2f} €", f"{saldo_inps_si_cpb_effettivo:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_comunale_si_cpb:,.2f} €", f"{acconto_1_inps_no_cpb:,.2f} €", f"{acconto_2_inps_no_cpb:,.2f} €", f"**{totale_versare_si_cpb_eff:,.2f} €**"],
        }, index=["IRPEF a Debito/Credito", "Imposta Sostitutiva CPB", "Addizionale Regionale", "Saldo Add. Comunale", "Saldo INPS a Debito/Credito", "1° Acconto IRPEF", "2° Acconto IRPEF", "Acconto Add. Comunale", "1° Acconto INPS", "2° Acconto INPS", "TOTALE DA VERSARE"])
        st.table(df_saldi)





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
                socio_data['altri_redditi'] = st.number_input(f"ALTRI REDDITI TASSABILI IRPEF Socio {i+1}", value=0.0, format="%.2f", key=f"ar_soc_{i}")
                socio_data['oneri_deducibili'] = st.number_input(f"ONERI DEDUCIBILI (escluso INPS quota socio) Socio {i+1}", value=0.0, format="%.2f", key=f"od_soc_{i}")
                socio_data['cedolare_secca_redditi'] = st.number_input(f"REDDITI A CEDOLARE SECCA O TASS. SEPARATA Socio {i+1}", value=0.0, format="%.2f", key=f"csr_soc_{i}")
                socio_data['imposte_gia_trattenute'] = st.number_input(f"RITENUTE TOTALI SUBITE Socio {i+1}", value=0.0, format="%.2f", key=f"igt_soc_{i}")
            with col_socio2:
                socio_data['imposta_su_cedolare_secca'] = st.number_input(f"IMPOSTA SU CEDOLARE SECCA Socio {i+1}", value=0.0, format="%.2f", key=f"ics_soc_{i}")
                socio_data['acconti_versati'] = st.number_input(f"ACCONTI IRPEF VERSATI Socio {i+1}", value=0.0, format="%.2f", key=f"av_soc_{i}")
                socio_data['detrazioni_irpef'] = st.number_input(f"DETRAZIONI IRPEF TOTALI Socio {i+1}", value=0.0, format="%.2f", key=f"di_soc_{i}")
            
            st.markdown(f"**Addizionali e Contributi Socio {i+1}**")
            col_add_soc1, col_add_soc2 = st.columns(2)
            with col_add_soc1:
                socio_data['aliquota_add_regionale'] = col_add_soc1.number_input(f"Aliquota Add. Regionale (%) Socio {i+1}", value=1.73, format="%.2f", key=f"add_reg_soc_{i}")
                socio_data['aliquota_add_comunale'] = col_add_soc1.number_input(f"Aliquota Add. Comunale (%) Socio {i+1}", value=0.8, format="%.2f", key=f"add_com_soc_{i}")
                socio_data['aliquota_acconto_comunale'] = col_add_soc1.number_input(f"Aliquota Acconto Add. Comunale (%) Socio {i+1}", value=30.0, format="%.2f", key=f"acc_com_soc_{i}")
                socio_data['addizionale_comunale_trattenuta'] = col_add_soc1.number_input(f"Addizionale Comunale già Trattenuta Socio {i+1}:", value=0.0, format="%.2f", key=f"add_com_trat_soc_{i}")
            with col_add_soc2:
                socio_data['gestione_inps'] = col_add_soc2.selectbox(f"Gestione INPS Socio {i+1}:", ("Artigiani", "Commercianti", "Gestione Separata"), key=f"gest_soc_{i}")
                socio_data['acconti_inps_versati'] = col_add_soc2.number_input(f"Acconti INPS Versati (var.) Socio {i+1}", value=0.0, format="%.2f", key=f"acc_inps_soc_{i}")
                socio_data['imponibile_minimale_acconti_2025'] = col_add_soc2.number_input(f"Imponibile Minimale Acconti INPS 2025 Socio {i+1}", value=18415.0, format="%.2f", key=f"min_acc_soc_{i}")
            
            col_inps_s1, col_inps_s2, col_inps_s3 = st.columns(3)
            with col_inps_s1:
                socio_data['contributi_fissi'] = col_inps_s1.number_input(f"Contributi Fissi INPS Versati Socio {i+1}:", value=4515.43, format="%.2f", key=f"fissi_soc_{i}")
                socio_data['minimale_inps'] = col_inps_s1.number_input(f"Reddito Minimale INPS (saldo) Socio {i+1}:", value=18415.0, format="%.2f", key=f"min_soc_{i}")
            with col_inps_s2:
                 socio_data['aliquota_inps1'] = col_inps_s2.number_input(f"Aliquota 1° Scaglione (%) Socio {i+1}:", value=24.0, format="%.2f", key=f"aliq1_soc_{i}")
                 socio_data['aliquota_inps2'] = col_inps_s2.number_input(f"Aliquota 2° Scaglione (%) Socio {i+1}:", value=25.0, format="%.2f", key=f"aliq2_soc_{i}")
            with col_inps_s3:
                socio_data['scaglione1_cap_inps'] = col_inps_s3.number_input(f"Cap 1° Scaglione INPS (saldo) Socio {i+1}:", value=55008.0, format="%.2f", key=f"cap1_soc_{i}")
                socio_data['massimale_inps'] = col_inps_s3.number_input(f"Reddito Massimale INPS Socio {i+1}:", value=119650.0, format="%.2f", key=f"max_soc_{i}")
                socio_data['scaglione1_cap_inps_acconti'] = col_inps_s3.number_input(f"Cap 1° Scaglione INPS (acconti) Socio {i+1}", value=55448.0, format="%.2f", key=f"cap1_acc_soc_{i}")
            
            soci_inputs.append(socio_data)
        
        submitted_soc = st.form_submit_button("Esegui Simulazione Società")



 if submitted_soc:
        # CALCOLO IRAP
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

            # Calcoli imponibili e addizionali
            base_imponibile_no_cpb_irpef = quota_reddito_simulato + socio['altri_redditi'] - socio['oneri_deducibili'] - socio['cedolare_secca_redditi']
            base_imponibile_si_cpb_irpef = socio['altri_redditi'] + quota_reddito_rettificato_cpb - socio['oneri_deducibili'] - socio['cedolare_secca_redditi']
            
            irpef_lorda_no_cpb = calcola_irpef(base_imponibile_no_cpb_irpef)
            addizionale_regionale_socio_no_cpb = base_imponibile_no_cpb_irpef * (socio['aliquota_add_regionale'] / 100.0)
            addizionale_comunale_socio_no_cpb = base_imponibile_no_cpb_irpef * (socio['aliquota_add_comunale'] / 100.0)
            
            base_imponibile_sostitutiva = quota_reddito_proposto - quota_reddito_rilevante
            if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
            if punteggio_isa_n_soc >= 8: aliquota_sostitutiva = 0.10
            elif punteggio_isa_n_soc >= 6: aliquota_sostitutiva = 0.12
            else: aliquota_sostitutiva = 0.15
            imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva
            irpef_lorda_si_cpb = calcola_irpef(base_imponibile_si_cpb_irpef)
            addizionale_regionale_socio_si_cpb = base_imponibile_si_cpb_irpef * (socio['aliquota_add_regionale'] / 100.0)
            addizionale_comunale_socio_si_cpb = base_imponibile_si_cpb_irpef * (socio['aliquota_add_comunale'] / 100.0)

            # Calcolo Tassazione Lorda e Saldo IRPEF
            tassazione_lorda_no_cpb = irpef_lorda_no_cpb
            saldo_irpef_no_cpb = tassazione_lorda_no_cpb - socio['detrazioni_irpef'] - socio['imposte_gia_trattenute'] - socio['acconti_versati']
            
            tassazione_lorda_si_cpb =  irpef_lorda_si_cpb
            saldo_irpef_si_cpb = tassazione_lorda_si_cpb - socio['detrazioni_irpef'] - socio['imposte_gia_trattenute'] - socio['acconti_versati']
            
            # Calcoli Contributivi e Saldo INPS
            inps_dovuti_effettivo = calcola_inps_saldo(quota_reddito_simulato, socio['gestione_inps'], socio['minimale_inps'], socio['contributi_fissi'], socio['scaglione1_cap_inps'], socio['aliquota_inps1'], socio['aliquota_inps2'], socio['massimale_inps'])
            inps_dovuti_concordato = calcola_inps_saldo(quota_reddito_rettificato_cpb + base_imponibile_sostitutiva, socio['gestione_inps'], socio['minimale_inps'], socio['contributi_fissi'], socio['scaglione1_cap_inps'], socio['aliquota_inps1'], socio['aliquota_inps2'], socio['massimale_inps'])
            saldo_inps_no_cpb = inps_dovuti_effettivo - socio['contributi_fissi'] - socio['acconti_inps_versati']
            saldo_inps_si_cpb_concordato = inps_dovuti_concordato - socio['contributi_fissi'] - socio['acconti_inps_versati']
            saldo_inps_si_cpb_effettivo = inps_dovuti_effettivo - socio['contributi_fissi'] - socio['acconti_inps_versati']

            # Calcolo Acconti IRPEF e Comunale
             # Calcolo Saldi e Acconti
            saldo_irpef_no_cpb = irpef_lorda_no_cpb - socio['detrazioni_irpef'] - socio['imposte_gia_trattenute'] - socio['acconti_versati']
            saldo_inps_no_cpb = inps_dovuti_effettivo - socio['contributi_fissi'] - socio['acconti_inps_versati']
            
            saldo_irpef_si_cpb = irpef_lorda_si_cpb - socio['detrazioni_irpef'] - socio['imposte_gia_trattenute'] - socio['acconti_versati']
            saldo_inps_si_cpb_concordato = inps_dovuti_concordato - socio['contributi_fissi'] - socio['acconti_inps_versati']
            saldo_inps_si_cpb_effettivo = inps_dovuti_effettivo - socio['contributi_fissi'] - socio['acconti_inps_versati']
            
            base_acconto_irpef_no_cpb_soc = irpef_lorda_no_cpb - socio['detrazioni_irpef'] - socio['imposte_gia_trattenute']
            acconto_irpef_no_cpb = (base_acconto_irpef_no_cpb_soc * 0.50) if base_acconto_irpef_no_cpb_soc > 0 else 0
            acconto_comunale_no_cpb = addizionale_comunale_socio_no_cpb * (socio['aliquota_acconto_comunale'] / 100.0)
            
            base_acconto_irpef_si_cpb_soc = irpef_lorda_si_cpb - socio['detrazioni_irpef'] - socio['imposte_gia_trattenute']
            acconto_irpef_si_cpb = (base_acconto_irpef_si_cpb_soc * 0.50) if base_acconto_irpef_si_cpb_soc > 0 else 0
            acconto_comunale_si_cpb = addizionale_comunale_socio_si_cpb * (socio['aliquota_acconto_comunale'] / 100.0)

            # Calcolo Acconti INPS
            acconto_1_inps_no_cpb, acconto_2_inps_no_cpb = calcola_acconti_inps(quota_reddito_simulato, socio['gestione_inps'], socio['imponibile_minimale_acconti_2025'], socio['scaglione1_cap_inps_acconti'], socio['aliquota_inps1'], socio['aliquota_inps2'], socio['massimale_inps'])
            acconto_1_inps_si_cpb_conc, acconto_2_inps_si_cpb_conc = calcola_acconti_inps(quota_reddito_rettificato_cpb + base_imponibile_sostitutiva, socio['gestione_inps'], socio['imponibile_minimale_acconti_2025'], socio['scaglione1_cap_inps_acconti'], socio['aliquota_inps1'], socio['aliquota_inps2'], socio['massimale_inps'])
            acconto_1_inps_si_cpb_eff, acconto_2_inps_si_cpb_eff = calcola_acconti_inps(quota_reddito_simulato, socio['gestione_inps'], socio['imponibile_minimale_acconti_2025'], socio['scaglione1_cap_inps_acconti'], socio['aliquota_inps1'], socio['aliquota_inps2'], socio['massimale_inps'])

            # Presentazione risultati per il socio
            st.markdown(f"**Riepilogo Saldi Finali e Acconti da Versare Socio {i+1}**")
            
            # Calcolo totali da versare
            totale_versare_no_cpb = saldo_irpef_no_cpb + (addizionale_regionale_socio_no_cpb - socio['addizionale_regionale_trattenuta']) + (addizionale_comunale_socio_no_cpb - socio['addizionale_comunale_trattenuta']) + saldo_inps_no_cpb + acconto_1_inps_no_cpb + acconto_2_inps_no_cpb + (acconto_irpef_no_cpb * 2) + acconto_comunale_no_cpb
            totale_versare_si_cpb_conc = saldo_irpef_si_cpb + imposta_sostitutiva + (addizionale_regionale_socio_si_cpb - socio['addizionale_regionale_trattenuta']) + (addizionale_comunale_socio_si_cpb - socio['addizionale_comunale_trattenuta']) + saldo_inps_si_cpb_concordato + acconto_1_inps_si_cpb_conc + acconto_2_inps_si_cpb_conc + (acconto_irpef_si_cpb * 2) + acconto_comunale_si_cpb
            totale_versare_si_cpb_eff = saldo_irpef_si_cpb + imposta_sostitutiva + (addizionale_regionale_socio_si_cpb - socio['addizionale_regionale_trattenuta']) + (addizionale_comunale_socio_si_cpb - socio['addizionale_comunale_trattenuta']) + saldo_inps_si_cpb_effettivo + acconto_1_inps_si_cpb_eff + acconto_2_inps_si_cpb_eff + (acconto_irpef_si_cpb * 2) + acconto_comunale_si_cpb

            df_saldi_socio = pd.DataFrame({
                "Senza Concordato": [f"{saldo_irpef_no_cpb:,.2f} €", f"N/A", f"{addizionale_regionale_socio_no_cpb:,.2f} €", f"{addizionale_comunale_socio_no_cpb - socio['addizionale_comunale_trattenuta']:,.2f} €", f"{saldo_inps_no_cpb:,.2f} €", f"{acconto_irpef_no_cpb:,.2f} €", f"{acconto_irpef_no_cpb:,.2f} €", f"{acconto_comunale_no_cpb:,.2f} €", f"{acconto_1_inps_no_cpb:,.2f} €", f"{acconto_2_inps_no_cpb:,.2f} €", f"**{totale_versare_no_cpb:,.2f} €**"],
                "Con Concordato (INPS su Concordato)": [f"{saldo_irpef_si_cpb:,.2f} €", f"{imposta_sostitutiva:,.2f} €", f"{addizionale_regionale_socio_si_cpb:,.2f} €", f"{addizionale_comunale_socio_si_cpb - socio['addizionale_comunale_trattenuta']:,.2f} €", f"{saldo_inps_si_cpb_concordato:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_comunale_si_cpb:,.2f} €", f"{acconto_1_inps_si_cpb_conc:,.2f} €", f"{acconto_2_inps_si_cpb_conc:,.2f} €", f"**{totale_versare_si_cpb_conc:,.2f} €**"],
                "Con Concordato (INPS su Effettivo)": [f"{saldo_irpef_si_cpb:,.2f} €", f"{imposta_sostitutiva:,.2f} €", f"{addizionale_regionale_socio_si_cpb:,.2f} €", f"{addizionale_comunale_socio_si_cpb - socio['addizionale_comunale_trattenuta']:,.2f} €", f"{saldo_inps_si_cpb_effettivo:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_comunale_si_cpb:,.2f} €", f"{acconto_1_inps_si_cpb_eff:,.2f} €", f"{acconto_2_inps_si_cpb_eff:,.2f} €", f"**{totale_versare_si_cpb_eff:,.2f} €**"],
            }, index=["IRPEF a Debito/Credito", "Imposta Sostitutiva CPB", "Addizionale Regionale", "Saldo Add. Comunale", "Saldo INPS a Debito/Credito", "1° Acconto IRPEF", "2° Acconto IRPEF", "Acconto Add. Comunale", "1° Acconto INPS", "2° Acconto INPS", "TOTALE DA VERSARE"])
            st.table(df_saldi_socio)
            
            st.markdown("---")
