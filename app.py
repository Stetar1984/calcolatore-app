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
            totale_versare_no_cpb = saldo_irpef_no_cpb + addizionale_regionale_socio_no_cpb + (addizionale_comunale_socio_no_cpb - socio['addizionale_comunale_trattenuta']) + saldo_inps_no_cpb + acconto_1_inps_no_cpb + acconto_2_inps_no_cpb + (acconto_irpef_no_cpb * 2) + acconto_comunale_no_cpb
            totale_versare_si_cpb_conc = saldo_irpef_si_cpb + imposta_sostitutiva + addizionale_regionale_socio_si_cpb + (addizionale_comunale_socio_si_cpb - socio['addizionale_comunale_trattenuta']) + saldo_inps_si_cpb_concordato + acconto_1_inps_si_cpb_conc + acconto_2_inps_si_cpb_conc + (acconto_irpef_si_cpb * 2) + acconto_comunale_si_cpb
            totale_versare_si_cpb_eff = saldo_irpef_si_cpb + imposta_sostitutiva + addizionale_regionale_socio_si_cpb + (addizionale_comunale_socio_si_cpb - socio['addizionale_comunale_trattenuta']) + saldo_inps_si_cpb_effettivo + acconto_1_inps_si_cpb_eff + acconto_2_inps_si_cpb_eff + (acconto_irpef_si_cpb * 2) + acconto_comunale_si_cpb

            df_saldi_socio = pd.DataFrame({
                "Senza Concordato": [f"{saldo_irpef_no_cpb:,.2f} €", f"N/A", f"{addizionale_regionale_socio_no_cpb:,.2f} €", f"{addizionale_comunale_socio_no_cpb - socio['addizionale_comunale_trattenuta']:,.2f} €", f"{saldo_inps_no_cpb:,.2f} €", f"{acconto_irpef_no_cpb:,.2f} €", f"{acconto_irpef_no_cpb:,.2f} €", f"{acconto_comunale_no_cpb:,.2f} €", f"{acconto_1_inps_no_cpb:,.2f} €", f"{acconto_2_inps_no_cpb:,.2f} €", f"**{totale_versare_no_cpb:,.2f} €**"],
                "Con Concordato (INPS su Concordato)": [f"{saldo_irpef_si_cpb:,.2f} €", f"{imposta_sostitutiva:,.2f} €", f"{addizionale_regionale_socio_si_cpb:,.2f} €", f"{addizionale_comunale_socio_si_cpb - socio['addizionale_comunale_trattenuta']:,.2f} €", f"{saldo_inps_si_cpb_concordato:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_comunale_si_cpb:,.2f} €", f"{acconto_1_inps_si_cpb_conc:,.2f} €", f"{acconto_2_inps_si_cpb_conc:,.2f} €", f"**{totale_versare_si_cpb_conc:,.2f} €**"],
                "Con Concordato (INPS su Effettivo)": [f"{saldo_irpef_si_cpb:,.2f} €", f"{imposta_sostitutiva:,.2f} €", f"{addizionale_regionale_socio_si_cpb:,.2f} €", f"{addizionale_comunale_socio_si_cpb - socio['addizionale_comunale_trattenuta']:,.2f} €", f"{saldo_inps_si_cpb_effettivo:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_irpef_si_cpb:,.2f} €", f"{acconto_comunale_si_cpb:,.2f} €", f"{acconto_1_inps_si_cpb_eff:,.2f} €", f"{acconto_2_inps_si_cpb_eff:,.2f} €", f"**{totale_versare_si_cpb_eff:,.2f} €**"],
            }, index=["IRPEF a Debito/Credito", "Imposta Sostitutiva CPB", "Addizionale Regionale", "Saldo Add. Comunale", "Saldo INPS a Debito/Credito", "1° Acconto IRPEF", "2° Acconto IRPEF", "Acconto Add. Comunale", "1° Acconto INPS", "2° Acconto INPS", "TOTALE DA VERSARE"])
            st.table(df_saldi_socio)
            
            st.markdown("---")
