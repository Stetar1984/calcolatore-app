

























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
            base_imponibile_no_cpb = quota_reddito_simulato + socio['altri_redditi'] - socio['oneri_deducibili'] - socio['cedolare_secca_redditi']
            irpef_lorda_no_cpb = calcola_irpef(base_imponibile_no_cpb)
            carico_fiscale_no_cpb = (irpef_lorda_no_cpb + socio['imposta_su_cedolare_secca'] - socio['imposte_gia_trattenute'] - socio['acconti_versati'] - socio['detrazioni_irpef']
            
            # Calcolo CON concordato
            base_imponibile_si_cpb = socio['altri_redditi'] + quota_reddito_rettificato_cpb - socio['oneri_deducibili'] - socio['cedolare_secca_redditi']
            base_sostitutiva = quota_reddito_proposto - quota_reddito_rilevante
            if base_sostitutiva < 0: base_sostitutiva = 0
            if punteggio_isa_n_soc >= 8: aliquota_sostitutiva = 0.10
            elif punteggio_isa_n_soc >= 6: aliquota_sostitutiva = 0.12
            else: aliquota_sostitutiva = 0.15
            imposta_sostitutiva = base_sostitutiva * aliquota_sostitutiva
            irpef_lorda_si_cpb = calcola_irpef(base_imponibile_si_cpb)
            carico_fiscale_concordato = (irpef_lorda_si_cpb + imposta_sostitutiva + socio['imposta_su_cedolare_secca'] - socio['imposte_gia_trattenute'] - socio['acconti_versati'] - socio['detrazion_irpef']
            
            risparmio = carico_fiscale_no_cpb - carico_fiscale_concordato
            
            df_socio = pd.DataFrame({
                "Descrizione": ["Base Imponibile IRPEF", "Imposta Lorda", "Imposta Netta", "Imposta Sostitutiva", "TOTALE CARICO FISCALE"],
                "Senza Concordato": [base_imponibile_no_cpb, irpef_lorda_no_cpb, irpef_netta_no_cpb, 0, carico_fiscale_no_cpb],
                "Con Concordato": [base_imponibile_si_cpb, irpef_lorda_si_cpb, irpef_netta_si_cpb, imposta_sostitutiva, carico_fiscale_concordato]
            }).set_index("Descrizione")
            
            st.table(df_socio.style.format("{:,.2f} €"))
            st.write(f"**RISPARMIO / (MAGGIOR ONERE) per {socio['nome']}: {risparmio:,.2f} €**")
            st.markdown("---")





