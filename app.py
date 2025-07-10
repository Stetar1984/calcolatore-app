import streamlit as st
import pandas as pd

# ==============================================================================
# --- Funzione di Calcolo IRPEF (Universale) ---
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
            reddito_simulato_2024 = st.number_input("REDDITO DA SIMULARE O PRESUNTO 2024:", value=70000.0, format="%.2f")
            reddito_rilevante_cpb_2023 = st.number_input("REDDITO RILEVANTE CPB 2023:", value=65000.0, format="%.2f")
            reddito_proposto_cpb_2024 = st.number_input("REDDITO PROPOSTO 2024 AI FINI CPB:", value=72000.0, format="%.2f")
            reddito_impresa_rettificato_cpb = st.number_input("REDDITO D'IMPRESA RETTIFICATO PER CPB 2024:", value=72000.0, format="%.2f")
            punteggio_isa_n_ind = st.slider("Punteggio ISA anno n (2023):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)

        with col2:
            altri_redditi = st.number_input("ALTRI REDDITI TASSABILI IRPEF 2024:", value=5000.0, format="%.2f")
            oneri_deducibili = st.number_input("ONERI DEDUCIBILI 2024:", value=2000.0, format="%.2f")
            imposte_gia_trattenute = st.number_input("IMPOSTE GIA' TRATTENUTE/RITENUTE D'ACCONTO:", value=0.0, format="%.2f")
            imposta_su_cedolare_secca = st.number_input("IMPOSTA SU CEDOLARE SECCA 2024:", value=0.0, format="%.2f")
            acconti_versati = st.number_input("ACCONTI VERSATI 2024:", value=0.0, format="%.2f")
            detrazioni_irpef = st.number_input("DETRAZIONI IRPEF 2024:", value=0.0, format="%.2f")
            # --- CAMPO MANCANTE AGGIUNTO QUI ---
            crediti_imposta = st.number_input("CREDITI D'IMPOSTA 2024:", value=0.0, format="%.2f")

        submitted = st.form_submit_button("Esegui Simulazione")

    if submitted:
        # Calcoli SENZA concordato
        base_imp_no_cpb = reddito_simulato_2024 + altri_redditi - oneri_deducibili
        imp_lorda_no_cpb = calcola_irpef(base_imp_no_cpb)
        imp_netta_no_cpb = imp_lorda_no_cpb - detrazioni_irpef
        carico_fiscale_no_cpb = (imp_netta_no_cpb if imp_netta_no_cpb > 0 else 0) + imposta_su_cedolare_secca + imposte_gia_trattenute - acconti_versati - crediti_imposta
        
        # Calcoli CON concordato
        base_imp_si_cpb = altri_redditi + reddito_impresa_rettificato_cpb - oneri_deducibili
        base_sostitutiva = reddito_proposto_cpb_2024 - reddito_rilevante_cpb_2023
        if base_sostitutiva < 0: base_sostitutiva = 0
        if punteggio_isa_n_ind >= 8: aliquota_sostitutiva = 0.10
        elif punteggio_isa_n_ind >= 6: aliquota_sostitutiva = 0.12
        else: aliquota_sostitutiva = 0.15
        imp_sostitutiva = base_sostitutiva * aliquota_sostitutiva
        imp_lorda_si_cpb = calcola_irpef(base_imp_si_cpb)
        imp_netta_si_cpb = imp_lorda_si_cpb - detrazioni_irpef
        carico_fiscale_si_cpb = (imp_netta_si_cpb if imp_netta_si_cpb > 0 else 0) + imposta_sostitutiva + imposta_su_cedolare_secca + imposte_gia_trattenute - acconti_versati - crediti_imposta
        
        risparmio_fiscale = carico_fiscale_no_cpb - carico_fiscale_si_cpb
        
        st.markdown("---")
        st.subheader(f"Risultati della Simulazione per: {nome_ditta}")
        
        df_risultati = pd.DataFrame({
            "Descrizione": ["Base Imponibile IRPEF", "Imposta Lorda", "Imposta Netta", "Imposta Sostitutiva", "TOTALE CARICO FISCALE"],
            "Senza Concordato": [base_imp_no_cpb, imp_lorda_no_cpb, imp_netta_no_cpb, 0, carico_fiscale_no_cpb],
            "Con Concordato": [base_imp_si_cpb, imp_lorda_si_cpb, imp_netta_si_cpb, imp_sostitutiva, carico_fiscale_si_cpb]
        }).set_index("Descrizione")
        
        st.table(df_risultati.style.format("{:,.2f} €"))
        st.subheader(f"RISPARMIO / (MAGGIOR ONERE): {risparmio_fiscale:,.2f} €")





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
            reddito_simulato_2024_soc = st.number_input("REDDITO DA SIMULARE O PRESUNTO 2024 (Società):", value=142000.0, format="%.2f")
            reddito_rilevante_cpb_2023_soc = st.number_input("REDDITO RILEVANTE CPB 2023 (Società):", value=139872.0, format="%.2f")
            reddito_proposto_cpb_2024_soc = st.number_input("REDDITO PROPOSTO 2024 FINI CPB (Società):", value=151784.0, format="%.2f")
            reddito_impresa_rettificato_cpb_soc = st.number_input("REDDITO D'IMPRESA RETTIFICATO PER CPB:", value=152420.49, format="%.2f")
        with col2:
            valore_produzione_simulato_2024_soc = st.number_input("VALORE PRODUZIONE DA SIMULARE O PRESUNTO 2024 (per IRAP):", value=149604.0, format="%.2f")
            valore_produzione_irap_rettificato_cpb_soc = st.number_input("Valore della produzione IRAP rettificato per CPB:", value=318210.49, format="%.2f")
            punteggio_isa_n_soc = st.slider("Punteggio ISA Società (anno n):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)
        
        st.markdown("---")
        st.subheader("Dati dei Singoli Soci")
        
        tabs = st.tabs([f"Socio {i+1}" for i in range(4)])
        soci_inputs = []
        for i, tab in enumerate(tabs):
            with tab:
                socio_data = {}
                c1, c2 = st.columns(2)
                socio_data['nome'] = c1.text_input(f"Nome Socio {i+1}", value=f"Socio {i+1}", key=f"nome_{i}")
                socio_data['quota'] = c2.number_input(f"Quota di Partecipazione (%) Socio {i+1}", value=50.0 if i < 2 else 0.0, format="%.2f", key=f"quota_{i}")
                
                col_socio1, col_socio2 = st.columns(2)
                with col_socio1:
                    socio_data['altri_redditi'] = st.number_input(f"ALTRI REDDITI {i+1}", value=0.0, format="%.2f", key=f"ar_{i}")
                    socio_data['oneri_deducibili'] = st.number_input(f"ONERI DEDUCIBILI {i+1}", value=0.0, format="%.2f", key=f"od_{i}")
                    socio_data['imposte_gia_trattenute'] = st.number_input(f"IMPOSTE GIA' TRATTENUTE {i+1}", value=0.0, format="%.2f", key=f"igt_{i}")
                with col_socio2:
                    socio_data['imposta_su_cedolare_secca'] = st.number_input(f"IMPOSTA SU CEDOLARE SECCA {i+1}", value=0.0, format="%.2f", key=f"ics_{i}")
                    socio_data['acconti_versati'] = st.number_input(f"ACCONTI VERSATI {i+1}", value=0.0, format="%.2f", key=f"av_{i}")
                    socio_data['detrazioni_irpef'] = st.number_input(f"DETRAZIONI IRPEF {i+1}", value=0.0, format="%.2f", key=f"di_{i}")
                    socio_data['crediti_imposta'] = st.number_input(f"CREDITI D'IMPOSTA {i+1}", value=0.0, format="%.2f", key=f"ci_{i}")
                soci_inputs.append(socio_data)
        
        submitted_soc = st.form_submit_button("Esegui Simulazione Società")

    if submitted_soc:
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
            
            st.markdown(f"##### Riepilogo per: {socio['nome']} (Quota: {socio['quota']:.2f}%)")
            
            # Ripartizione redditi
            quota_reddito_simulato = reddito_simulato_2024_soc * perc_socio
            quota_reddito_rilevante = reddito_rilevante_cpb_2023_soc * perc_socio
            quota_reddito_proposto = reddito_proposto_cpb_2024_soc * perc_socio
            quota_reddito_rettificato_cpb = reddito_impresa_rettificato_cpb_soc * perc_socio
            
            # Calcolo SENZA concordato
            base_imponibile_no_cpb = quota_reddito_simulato + socio['altri_redditi'] - socio['oneri_deducibili']
            irpef_lorda_no_cpb = calcola_irpef(base_imponibile_no_cpb)
            irpef_netta_no_cpb = irpef_lorda_no_cpb - socio['detrazioni_irpef']
            carico_fiscale_no_cpb = (irpef_netta_no_cpb if irpef_netta_no_cpb > 0 else 0) + socio['imposta_su_cedolare_secca'] + socio['imposte_gia_trattenute'] - socio['acconti_versati'] - socio['crediti_imposta']
            
            # Calcolo CON concordato
            base_imponibile_si_cpb = socio['altri_redditi'] + quota_reddito_rettificato_cpb - socio['oneri_deducibili']
            base_sostitutiva = quota_reddito_proposto - quota_reddito_rilevante
            if base_sostitutiva < 0: base_sostitutiva = 0
            if punteggio_isa_n_soc >= 8: aliquota_sostitutiva = 0.10
            elif punteggio_isa_n_soc >= 6: aliquota_sostitutiva = 0.12
            else: aliquota_sostitutiva = 0.15
            imposta_sostitutiva = base_sostitutiva * aliquota_sostitutiva
            irpef_lorda_si_cpb = calcola_irpef(base_imponibile_si_cpb)
            irpef_netta_si_cpb = irpef_lorda_si_cpb - socio['detrazioni_irpef']
            carico_fiscale_concordato = (irpef_netta_si_cpb if irpef_netta_si_cpb > 0 else 0) + imposta_sostitutiva + socio['imposta_su_cedolare_secca'] + socio['imposte_gia_trattenute'] - socio['acconti_versati'] - socio['crediti_imposta']
            
            risparmio = carico_fiscale_no_cpb - carico_fiscale_concordato
            
            df_socio = pd.DataFrame({
                "Descrizione": ["Base Imponibile IRPEF", "Imposta Lorda", "Imposta Netta", "Imposta Sostitutiva", "TOTALE CARICO FISCALE"],
                "Senza Concordato": [base_imponibile_no_cpb, irpef_lorda_no_cpb, irpef_netta_no_cpb, 0, carico_fiscale_no_cpb],
                "Con Concordato": [base_imponibile_si_cpb, irpef_lorda_si_cpb, irpef_netta_si_cpb, imposta_sostitutiva, carico_fiscale_concordato]
            }).set_index("Descrizione")
            
            st.table(df_socio.style.format("{:,.2f} €"))
            st.write(f"**RISPARMIO / (MAGGIOR ONERE) per {socio['nome']}: {risparmio:,.2f} €**")
            st.markdown("---")





