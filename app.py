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

def calcola_inps(reddito_imponibile, gestione, minimale, fissi, aliquota):
    """Calcola i contributi INPS dovuti (fissi + variabili)."""
    aliquota_dec = aliquota / 100.0
    # Per la Gestione Separata, non ci sono minimali o fissi in questo contesto
    if gestione == "Gestione Separata":
        return reddito_imponibile * aliquota_dec
    # Per Artigiani e Commercianti
    elif gestione in ["Artigiani", "Commercianti"]:
        if reddito_imponibile <= minimale:
            return fissi  # Solo i contributi fissi sono dovuti
        else:
            contributo_variabile = (reddito_imponibile - minimale) * aliquota_dec
            return fissi + contributo_variabile
    return 0

# ==============================================================================
# --- IMPOSTAZIONI PAGINA E TITOLO ---
# ==============================================================================
st.set_page_config(layout="wide", page_title="Calcolatore Convenienza CPB")
st.title("Simulatore di Convenienza Concordato Preventivo Biennale (CPB)")
st.markdown("Questo strumento confronta il carico fiscale e contributivo totale con e senza l'adesione al CPB.")


# ==============================================================================
# --- SELETTORE PRINCIPALE ---
# ==============================================================================
tipo_calcolo = st.radio(
    "Seleziona la tipologia di contribuente:",
    ('Ditta Individuale', 'Professionista', 'Società in trasparenza fiscale'),
    horizontal=True,
    key="tipo_soggetto"
)
st.markdown("---")

# ==============================================================================
# --- CALCOLATORE PER DITTA INDIVIDUALE O PROFESSIONISTA ---
# ==============================================================================
if tipo_calcolo == 'Ditta Individuale' or tipo_calcolo == 'Professionista':
    st.header(f"Simulazione per {tipo_calcolo}")

    with st.form(f"form_{tipo_calcolo.lower().replace(' ', '_')}"):
        st.subheader("Dati Fiscali (IRPEF)")
        col1, col2 = st.columns(2)

        with col1:
            nome_soggetto = st.text_input(f"NOME SOGGETTO:", value=f'Mario Rossi')
            reddito_simulato_2024 = st.number_input("Reddito Effettivo/Simulato 2024:", value=70000.0, format="%.2f")
            reddito_proposto_cpb_2024 = st.number_input("Reddito Proposto per CPB 2024:", value=72000.0, format="%.2f")
        
        with col2:
            altri_redditi = st.number_input("Altri Redditi Tassabili IRPEF:", value=0.0, format="%.2f")
            oneri_deducibili_extra = st.number_input("Altri Oneri Deducibili (escluso INPS):", value=2000.0, format="%.2f")
            detrazioni_irpef = st.number_input("Detrazioni IRPEF Totali:", value=1500.0, format="%.2f")
            acconti_irpef_versati = st.number_input("Acconti IRPEF Versati:", value=10000.0, format="%.2f")

        st.markdown("---")
        st.subheader("Dati Contributivi (INPS)")
        col_inps1, col_inps2, col_inps3, col_inps4 = st.columns(4)
        with col_inps1:
            gestione_inps = st.selectbox("Gestione INPS:", ("Artigiani", "Commercianti", "Gestione Separata"), key="gest_ind")
        with col_inps2:
            aliquota_inps = st.number_input("Aliquota INPS Variabile (%):", value=24.0, format="%.2f", key="aliq_ind")
        with col_inps3:
            minimale_inps = st.number_input("Reddito Minimale INPS:", value=18415.0, format="%.2f", key="min_ind", help="Reddito sotto il quale si pagano solo i fissi (per Artigiani/Commercianti)")
        with col_inps4:
            contributi_fissi = st.number_input("Contributi Fissi INPS Versati:", value=4515.43, format="%.2f", key="fissi_ind", help="Importo annuale dei contributi sul minimale")

        submitted = st.form_submit_button("Esegui Simulazione")

    if submitted:
        # --- CALCOLO CONTRIBUTI INPS PER I DUE SCENARI ---
        inps_su_effettivo = calcola_inps(reddito_simulato_2024, gestione_inps, minimale_inps, contributi_fissi, aliquota_inps)
        inps_su_concordato = calcola_inps(reddito_proposto_cpb_2024, gestione_inps, minimale_inps, contributi_fissi, aliquota_inps)

        # --- SCENARIO 1: SENZA CONCORDATO ---
        oneri_deducibili_no_cpb = oneri_deducibili_extra + inps_su_effettivo
        base_imponibile_irpef_no_cpb = reddito_simulato_2024 + altri_redditi - oneri_deducibili_no_cpb
        irpef_netta_no_cpb = calcola_irpef(base_imponibile_irpef_no_cpb) - detrazioni_irpef
        carico_fiscale_no_cpb = irpef_netta_no_cpb - acconti_irpef_versati
        carico_totale_no_cpb = carico_fiscale_no_cpb + inps_su_effettivo

        # --- SCENARIO 2: CON CONCORDATO (INPS SUL CONCORDATO) ---
        oneri_deducibili_si_cpb_conc = oneri_deducibili_extra + inps_su_concordato
        base_imponibile_irpef_si_cpb_conc = reddito_proposto_cpb_2024 + altri_redditi - oneri_deducibili_si_cpb_conc
        irpef_netta_si_cpb_conc = calcola_irpef(base_imponibile_irpef_si_cpb_conc) - detrazioni_irpef
        carico_fiscale_si_cpb_conc = irpef_netta_si_cpb_conc - acconti_irpef_versati
        carico_totale_si_cpb_concordato = carico_fiscale_si_cpb_conc + inps_su_concordato
        
        # --- SCENARIO 3: CON CONCORDATO (INPS SULL'EFFETTIVO - OPZIONALE) ---
        oneri_deducibili_si_cpb_eff = oneri_deducibili_extra + inps_su_effettivo
        base_imponibile_irpef_si_cpb_eff = reddito_proposto_cpb_2024 + altri_redditi - oneri_deducibili_si_cpb_eff
        irpef_netta_si_cpb_eff = calcola_irpef(base_imponibile_irpef_si_cpb_eff) - detrazioni_irpef
        carico_fiscale_si_cpb_eff = irpef_netta_si_cpb_eff - acconti_irpef_versati
        carico_totale_si_cpb_effettivo = carico_fiscale_si_cpb_eff + inps_su_effettivo

        # --- PRESENTAZIONE RISULTATI ---
        st.markdown(f"<h4>Risultati Dettagliati per: {nome_soggetto}</h4>", unsafe_allow_html=True)
        df_risultati = pd.DataFrame({
            "Senza Concordato": [
                f"{carico_fiscale_no_cpb:,.2f} €",
                f"{inps_su_effettivo:,.2f} €",
                f"**{carico_totale_no_cpb:,.2f} €**"
            ],
            "Con Concordato (INPS su Concordato)": [
                f"{carico_fiscale_si_cpb_conc:,.2f} €",
                f"{inps_su_concordato:,.2f} €",
                f"**{carico_totale_si_cpb_concordato:,.2f} €**"
            ],
            "Con Concordato (INPS su Effettivo)": [
                f"{carico_fiscale_si_cpb_eff:,.2f} €",
                f"{inps_su_effettivo:,.2f} €",
                f"**{carico_totale_si_cpb_effettivo:,.2f} €**"
            ]
        }, index=["Carico Fiscale (Saldo IRPEF)", "Carico Contributivo (INPS)", "CARICO TOTALE (Fisco + INPS)"])
        st.table(df_risultati)
        
        risparmio_concordato = carico_totale_no_cpb - carico_totale_si_cpb_concordato
        risparmio_effettivo = carico_totale_no_cpb - carico_totale_si_cpb_effettivo
        st.success(f"Risparmio/Onere scegliendo l'opzione 'INPS su Concordato': {risparmio_concordato:,.2f} €")
        st.info(f"Risparmio/Onere scegliendo l'opzione 'INPS su Effettivo': {risparmio_effettivo:,.2f} €")


#==============================================================================
# --- CALCOLATORE PER SOCIETÀ IN TRASPARENZA ---
#==============================================================================
elif tipo_calcolo == 'Società in trasparenza fiscale':
    st.header("Simulazione per Società in trasparenza fiscale")
    
    with st.form("form_societa"):
        st.subheader("Dati Società")
        nome_societa = st.text_input("NOME SOCIETA':", value='Mia Società S.n.c.')
        reddito_simulato_2024_soc = st.number_input("REDDITO EFFETTIVO O SIMULATO SOCIETA':", value=142000.0, format="%.2f")
        reddito_proposto_cpb_2024_soc = st.number_input("REDDITO PROPOSTO CPB SOCIETA':", value=151784.0, format="%.2f")
       
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

            st.markdown(f"**Dati Fiscali (IRPEF) Socio {i+1}**")
            col_socio1, col_socio2, col_socio3 = st.columns(3)
            socio_data['altri_redditi'] = col_socio1.number_input(f"Altri Redditi IRPEF Socio {i+1}", value=0.0, format="%.2f", key=f"ar_{i}")
            socio_data['oneri_deducibili_extra'] = col_socio2.number_input(f"Altri Oneri Deducibili (escl. INPS) Socio {i+1}", value=0.0, format="%.2f", key=f"od_{i}")
            socio_data['detrazioni_irpef'] = col_socio3.number_input(f"Detrazioni IRPEF Socio {i+1}", value=0.0, format="%.2f", key=f"di_{i}")
            socio_data['acconti_irpef_versati'] = col_socio1.number_input(f"Acconti IRPEF Versati Socio {i+1}", value=0.0, format="%.2f", key=f"av_{i}")

            st.markdown(f"**Dati Contributivi (INPS) Socio {i+1}**")
            col_inps_s1, col_inps_s2, col_inps_s3, col_inps_s4 = st.columns(4)
            socio_data['gestione_inps'] = col_inps_s1.selectbox("Gestione INPS:", ("Artigiani", "Commercianti", "Gestione Separata"), key=f"gest_soc_{i}")
            socio_data['aliquota_inps'] = col_inps_s2.number_input("Aliquota INPS Variabile (%):", value=24.0, format="%.2f", key=f"aliq_soc_{i}")
            socio_data['minimale_inps'] = col_inps_s3.number_input("Reddito Minimale INPS:", value=18415.0, format="%.2f", key=f"min_soc_{i}")
            socio_data['contributi_fissi'] = col_inps_s4.number_input("Contributi Fissi INPS Versati:", value=4515.43, format="%.2f", key=f"fissi_soc_{i}")

            soci_inputs.append(socio_data)
        
        submitted_soc = st.form_submit_button("Esegui Simulazione Società")

    if submitted_soc:
        st.markdown("---")
        st.header(f"Risultati Dettagliati per {nome_societa}")
        
        for i, socio in enumerate(soci_inputs):
            perc_socio = socio['quota_partecipazione'] / 100.0
            if perc_socio == 0: continue
            
            st.markdown(f"### Riepilogo per: {socio['nome_socio']} (Quota: {socio['quota_partecipazione']:.2f}%)")
            
            quota_reddito_simulato = reddito_simulato_2024_soc * perc_socio
            quota_reddito_concordato = reddito_proposto_cpb_2024_soc * perc_socio
            
            # Calcoli INPS
            inps_su_effettivo = calcola_inps(quota_reddito_simulato, socio['gestione_inps'], socio['minimale_inps'], socio['contributi_fissi'], socio['aliquota_inps'])
            inps_su_concordato = calcola_inps(quota_reddito_concordato, socio['gestione_inps'], socio['minimale_inps'], socio['contributi_fissi'], socio['aliquota_inps'])

            # Calcolo SENZA Concordato
            oneri_deducibili_no_cpb = socio['oneri_deducibili_extra'] + inps_su_effettivo
            base_imponibile_irpef_no_cpb = quota_reddito_simulato + socio['altri_redditi'] - oneri_deducibili_no_cpb
            irpef_netta_no_cpb = calcola_irpef(base_imponibile_irpef_no_cpb) - socio['detrazioni_irpef']
            carico_fiscale_no_cpb = irpef_netta_no_cpb - socio['acconti_irpef_versati']
            carico_totale_no_cpb = carico_fiscale_no_cpb + inps_su_effettivo

            # Calcolo CON Concordato (Opzione 1: INPS su Concordato)
            oneri_deducibili_si_cpb_conc = socio['oneri_deducibili_extra'] + inps_su_concordato
            base_imponibile_irpef_si_cpb_conc = quota_reddito_concordato + socio['altri_redditi'] - oneri_deducibili_si_cpb_conc
            irpef_netta_si_cpb_conc = calcola_irpef(base_imponibile_irpef_si_cpb_conc) - socio['detrazioni_irpef']
            carico_fiscale_si_cpb_conc = irpef_netta_si_cpb_conc - socio['acconti_irpef_versati']
            carico_totale_si_cpb_concordato = carico_fiscale_si_cpb_conc + inps_su_concordato

            # Calcolo CON Concordato (Opzione 2: INPS su Effettivo)
            oneri_deducibili_si_cpb_eff = socio['oneri_deducibili_extra'] + inps_su_effettivo
            base_imponibile_irpef_si_cpb_eff = quota_reddito_concordato + socio['altri_redditi'] - oneri_deducibili_si_cpb_eff
            irpef_netta_si_cpb_eff = calcola_irpef(base_imponibile_irpef_si_cpb_eff) - socio['detrazioni_irpef']
            carico_fiscale_si_cpb_eff = irpef_netta_si_cpb_eff - socio['acconti_irpef_versati']
            carico_totale_si_cpb_effettivo = carico_fiscale_si_cpb_eff + inps_su_effettivo

            # Presentazione risultati per il socio
            df_socio = pd.DataFrame({
                "Senza Concordato": [
                    f"{carico_fiscale_no_cpb:,.2f} €",
                    f"{inps_su_effettivo:,.2f} €",
                    f"**{carico_totale_no_cpb:,.2f} €**"
                ],
                "Con Concordato (INPS su Concordato)": [
                    f"{carico_fiscale_si_cpb_conc:,.2f} €",
                    f"{inps_su_concordato:,.2f} €",
                    f"**{carico_totale_si_cpb_concordato:,.2f} €**"
                ],
                "Con Concordato (INPS su Effettivo)": [
                    f"{carico_fiscale_si_cpb_eff:,.2f} €",
                    f"{inps_su_effettivo:,.2f} €",
                    f"**{carico_totale_si_cpb_effettivo:,.2f} €**"
                ]
            }, index=["Carico Fiscale (Saldo IRPEF)", "Carico Contributivo (INPS)", "CARICO TOTALE (Fisco + INPS)"])
            st.table(df_socio)

            risparmio1 = carico_totale_no_cpb - carico_totale_si_cpb_concordato
            risparmio2 = carico_totale_no_cpb - carico_totale_si_cpb_effettivo
            st.success(f"Risparmio/Onere Socio (Opzione INPS su Concordato): {risparmio1:,.2f} €")
            st.info(f"Risparmio/Onere Socio (Opzione INPS su Effettivo): {risparmio2:,.2f} €")
            st.markdown("---")
