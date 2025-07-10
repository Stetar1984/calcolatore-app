import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import base64

#==============================================================================
# --- Funzioni Helper Globali ---
#==============================================================================
def create_download_link(html_content, filename, link_text):
    """Genera un link per scaricare una stringa HTML come file."""
    style = "<style> body { font-family: Arial, sans-serif; margin: 20px; } h1, h2, h3, h4, h5 { color: #333; } table { border-collapse: collapse; width: 80%; margin: 20px 0; font-size: 12px; } th, td { border: 1px solid #ddd; padding: 8px; text-align: left; } th { background-color: #f2f2f2; } </style>"
    final_html = f"<html><head><title>Report CPB</title>{style}</head><body>{html_content}</body></html>"
    b64 = base64.b64encode(final_html.encode('utf-8')).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="font-size: 14px; background-color: #17a2b8; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">{link_text}</a>'

def calcola_irpef(imponibile):
    """Calcola l'IRPEF lorda basata sugli scaglioni."""
    if imponibile <= 0: return 0
    if imponibile <= 28000: return imponibile * 0.23
    elif imponibile <= 50000: return (28000 * 0.23) + ((imponibile - 28000) * 0.35)
    else: return (28000 * 0.23) + (22000 * 0.35) + ((imponibile - 50000) * 0.43)

#==============================================================================
# --- DEFINIZIONE CALCOLATORE N.1: DITTA INDIVIDUALE ---
#==============================================================================

style_ind = {'description_width': 'initial'}
layout_ind = widgets.Layout(width='auto', margin='3px 0')
input_widgets_ind = {
    'nome_ditta': widgets.Text(value='La Mia Ditta Individuale', description="NOME DITTA:", style=style_ind, layout=layout_ind),
    'reddito_simulato_2024': widgets.FloatText(value=0, description="REDDITO DA SIMULARE O PRESUNTO 2024:", style=style_ind, layout=layout_ind),
    'reddito_rilevante_cpb_2023': widgets.FloatText(value=0, description="REDDITO RILEVANTE CPB 2023:", style=style_ind, layout=layout_ind),
    'reddito_proposto_cpb_2024': widgets.FloatText(value=0, description="REDDITO PROPOSTO 2024 AI FINI CPB:", style=style_ind, layout=layout_ind),
    'reddito_impresa_rettificato_cpb': widgets.FloatText(value=0, description="REDDITO D'IMPRESA RETTIFICATO PER CPB 2024:", style=style_ind, layout=layout_ind),
    'punteggio_isa_n_ind': widgets.FloatSlider(value=1.0, min=1, max=10, step=0.1, description="Punteggio ISA anno n (2023):", style=style_ind, layout=layout_ind),
    'altri_redditi': widgets.FloatText(value=0, description="ALTRI REDDITI TASSABILI IRPEF 2024:", style=style_ind, layout=layout_ind),
    'oneri_deducibili': widgets.FloatText(value=0, description="ONERI DEDUCIBILI 2024:", style=style_ind, layout=layout_ind),
    'cedolare_secca_redditi': widgets.FloatText(value=0, description="REDDITI A CEDOLARE SECCA O TASS. SEP. 2024:", style=style_ind, layout=layout_ind),
    'imposte_gia_trattenute': widgets.FloatText(value=0, description="IMPOSTE SU REDDITI GIA' TASSATI 2024:", style=style_ind, layout=layout_ind),
    'imposta_su_cedolare_secca': widgets.FloatText(value=0, description="IMPOSTA SU CEDOLARE SECCA 2024:", style=style_ind, layout=layout_ind),
    'acconti versati': widgets.FloatText(value=0, description="ACCONTI VERSATI 2024:", style=style_ind, layout=layout_ind),
    'detrazioni IRPEF' : widgets.FloatText(value=0, description="DETRAZIONI IRPEF 2024:", style=style_ind, layout=layout_ind)



}
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



button_ind = widgets.Button(description="Esegui Simulazione", button_style='success', icon='calculator', layout=widgets.Layout(width='49%', margin='10px 0'))
button_export_ind = widgets.Button(description="Esporta Report", button_style='info', icon='download', layout=widgets.Layout(width='49%', margin='10px 0'))
output_area_ind = widgets.Output(); output_export_ind = widgets.Output()







def esegui_calcolo_individuale(b):
    with output_area_ind:
        clear_output(wait=True); val = {k: w.value for k, w in input_widgets_ind.items()}
        base_imponibile_si_cpb = val['altri_redditi'] + val['reddito_impresa_rettificato_cpb'] - val['cedolare_secca_redditi'] - val['oneri_deducibili']
        base_imponibile_no_cpb = val['reddito_simulato_2024'] + val['altri_redditi'] - val['oneri_deducibili'] - val['cedolare_secca_redditi']
        base_imponibile_sostitutiva = val['reddito_proposto_cpb_2024'] - val['reddito_rilevante_cpb_2023']
        if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
        if val['punteggio_isa_n_ind'] >= 8: aliquota_sostitutiva = 0.10
        elif val['punteggio_isa_n_ind'] >= 6: aliquota_sostitutiva = 0.12
        else: aliquota_sostitutiva = 0.15
        imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva
        tass_ordinaria_si_cpb = calcola_irpef(base_imponibile_si_cpb)
        totale_tassazione_si_cpb = imposta_sostitutiva + tass_ordinaria_si_cpb + val['imposta_su_cedolare_secca'] - val['acconti versati'] - val['detrazioni IRPEF'] - val['imposte_gia_trattenute']
        tassazione_no_cpb_irpef = calcola_irpef(base_imponibile_no_cpb)
        totale_tassazione_no_cpb = tassazione_no_cpb_irpef - val['imposte_gia_trattenute'] + val['imposta_su_cedolare_secca'] - val['acconti versati'] - val['detrazioni IRPEF']
        risparmio_fiscale = totale_tassazione_no_cpb - totale_tassazione_si_cpb
        display(HTML(f"<h4>Risultati per: {val['nome_ditta']}</h4>")); pd.options.display.float_format = '{:,.2f} €'.format
        df_risultati = pd.DataFrame({"Senza Concordato": [f"{totale_tassazione_no_cpb:,.2f} €"], "Con Concordato": [f"{totale_tassazione_si_cpb:,.2f} €"], "Risparmio/Onere": [f"{risparmio_fiscale:,.2f} €"]}, index=["Carico Fiscale Totale"]); display(df_risultati)

def export_report_individuale(b):
    with output_export_ind:
        clear_output(wait=True); val = {k: w.value for k, w in input_widgets_ind.items()}
        # Riesegue i calcoli per avere i dati aggiornati
        base_imponibile_si_cpb = val['altri_redditi'] + val['reddito_impresa_rettificato_cpb'] - val['cedolare_secca_redditi'] - val['oneri_deducibili']; base_imponibile_no_cpb = val['reddito_simulato_2024'] + val['altri_redditi'] - val['oneri_deducibili'] - val['cedolare_secca_redditi']; base_imponibile_sostitutiva = val['reddito_proposto_cpb_2024'] - val['reddito_rilevante_cpb_2023'];
        if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
        if val['punteggio_isa_n_ind'] >= 8: aliquota_sostitutiva = 0.10
        elif val['punteggio_isa_n_ind'] >= 6: aliquota_sostitutiva = 0.12
        else: aliquota_sostitutiva = 0.15
        imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva; tass_ordinaria_si_cpb = calcola_irpef(base_imponibile_si_cpb); totale_tassazione_si_cpb = imposta_sostitutiva + tass_ordinaria_si_cpb + val['imposta_su_cedolare_secca'] - val['acconti versati'] - val['detrazioni IRPEF'] - val['imposte_gia_trattenute']; tassazione_no_cpb_irpef = calcola_irpef(base_imponibile_no_cpb); totale_tassazione_no_cpb = tassazione_no_cpb_irpef - val['imposte_gia_trattenute'] + val['imposta_su_cedolare_secca'] - val['acconti versati'] - val['detrazioni IRPEF']; risparmio_fiscale = totale_tassazione_no_cpb - totale_tassazione_si_cpb

        df_input = pd.DataFrame.from_dict(val, orient='index', columns=['Valore Inserito'])
        df_results = pd.DataFrame({"Senza Concordato": [f"{totale_tassazione_no_cpb:,.2f} €"], "Con Concordato": [f"{totale_tassazione_si_cpb:,.2f} €"], "Risparmio/Onere": [f"{risparmio_fiscale:,.2f} €"]}, index=["Carico Fiscale Totale"])

        html_content = f"<h1>Report di Convenienza CPB per {val['nome_ditta']}</h1><h2>Dati di Input</h2>{df_input.to_html()}<h2>Risultato Simulazione</h2>{df_results.to_html()}"
        link = create_download_link(html_content, f"report_{val['nome_ditta'].replace(' ', '_')}.html", "Scarica Report HTML")
        display(HTML(link))








button_ind.on_click(esegui_calcolo_individuale); button_export_ind.on_click(export_report_individuale)
col_sx_widgets_ind = [widgets.VBox([input_widgets_ind[k], widgets.HTML(f"<i style='color:grey;font-size:10px;'>{descrizioni_aggiuntive.get(k,'')}</i>")]) for k in list(input_widgets_ind.keys())[:7]]
col_dx_widgets_ind = [widgets.VBox([input_widgets_ind[k], widgets.HTML(f"<i style='color:grey;font-size:10px;'>{descrizioni_aggiuntive.get(k,'')}</i>")]) for k in list(input_widgets_ind.keys())[7:]]
col_sx_ind = widgets.VBox(col_sx_widgets_ind); col_dx_ind = widgets.VBox(col_dx_widgets_ind)
box_input_ind = widgets.HBox([col_sx_ind, col_dx_ind])
app_individuale = widgets.VBox([widgets.HTML("<h3>CALCOLO CONVENIENZA CPB DITTA INDIVIDUALE</h3>"), box_input_ind, widgets.HBox([button_ind, button_export_ind]), widgets.HTML("<hr>"), output_area_ind, output_export_ind])








#==============================================================================
# DEFINIZIONE DEL CALCOLATORE N.2: SOCIETÀ DI PERSONE
#==============================================================================
style_soc = {'description_width': 'initial'}; layout_largo_soc = widgets.Layout(width='auto', margin='5px 0'); layout_stretto_soc = widgets.Layout(width='auto', margin='3px 0')

# --- CORREZIONE: ripristinato il nome corretto del dizionario ---
input_societa_widgets = {
    'nome_societa': widgets.Text(value='Mia Società S.n.c.', description="NOME SOCIETA':", style=style_soc, layout=layout_largo_soc),
    'reddito_simulato_2024': widgets.FloatText(value=0.0, description="REDDITO DA SIMULARE O PRESUNTO 2024 (Società):", style=style_soc, layout=layout_largo_soc),
    'valore_produzione_simulato_2024': widgets.FloatText(value=0.0, description="VALORE PRODUZIONE DA SIMULARE O PRESUNTO 2024 (per IRAP):", style=style_soc, layout=layout_largo_soc),
    'reddito_rilevante_cpb_2023': widgets.FloatText(value=0.0, description="REDDITO RILEVANTE CPB 2023 (Società):", style=style_soc, layout=layout_largo_soc),
    'reddito_proposto_cpb_2024': widgets.FloatText(value=0.0, description="REDDITO PROPOSTO 2024 FINI CPB (Società):", style=style_soc, layout=layout_largo_soc),
    'reddito_impresa_rettificato_cpb': widgets.FloatText(value=0.0, description="REDDITO D'IMPRESA RETTIFICATO PER CPB:", style=style_soc, layout=layout_largo_soc),
    'valore_produzione_irap_rettificato_cpb': widgets.FloatText(value=0.0, description="Valore della produzione IRAP rettificato per CPB:", style=style_soc, layout=layout_largo_soc),
    'punteggio_isa_n_soc': widgets.FloatSlider(value=1.0, min=1, max=10, step=0.1, description="Punteggio ISA Società (anno n):", style=style_soc, layout=layout_largo_soc)
}
soci_widgets = []
valori_socio1 = {'nome': 'Socio 1', 'quota': 0.0, 'altri_redditi': 0.0, 'oneri_deducibili': 0.0, 'cedolare_secca_redditi': 0.0, 'imposte_gia_trattenute': 0.0, 'imposta_su_cedolare_secca': 0.0, 'acconti versati': 0.0, 'detrazioni IRPEF': 0.0}
for i in range(4):
    val_default = valori_socio1 if i == 0 else {'nome': f'Socio {i+1}', 'quota': 0.0, 'altri_redditi': 0.0, 'oneri_deducibili': 0.0, 'cedolare_secca_redditi': 0.0, 'imposte_gia_trattenute': 0.0, 'imposta_su_cedolare_secca': 0.0, 'acconti versati': 0.0, 'detrazioni IRPEF': 0.0}
    soci_widgets.append({'nome_socio': widgets.Text(value=val_default['nome'], description="Nome Socio:", style=style_soc, layout=layout_stretto_soc), 'quota_partecipazione': widgets.FloatText(value=val_default['quota'], description="QUOTA PARTECIPAZIONE (%):", style=style_soc, layout=layout_stretto_soc), 'altri_redditi': widgets.FloatText(value=val_default['altri_redditi'], description="ALTRI REDDITI TASSABILI IRPEF:", style=style_soc, layout=layout_stretto_soc), 'oneri_deducibili': widgets.FloatText(value=val_default['oneri_deducibili'], description="ONERI DEDUCIBILI:", style=style_soc, layout=layout_stretto_soc), 'cedolare_secca_redditi': widgets.FloatText(value=val_default['cedolare_secca_redditi'], description="REDDITI A CEDOLARE SECCA O TASS. SEP.:", style=style_soc, layout=layout_stretto_soc), 'imposte_gia_trattenute': widgets.FloatText(value=val_default['imposte_gia_trattenute'], description="IMPOSTE SU REDDITI GIA' TASSATI:", style=style_soc, layout=layout_stretto_soc), 'imposta_su_cedolare_secca': widgets.FloatText(value=val_default['imposta_su_cedolare_secca'], description="IMPOSTA SU CEDOLARE SECCA:", style=style_soc, layout=layout_stretto_soc), 'acconti versati': widgets.FloatText(value=val_default['acconti versati'], description="ACCONTI VERSATI:", style=style_soc, layout=layout_stretto_soc), 'detrazioni IRPEF': widgets.FloatText(value=val_default['detrazioni IRPEF'], description="DETRAZIONI IRPEF:", style=style_soc, layout=layout_stretto_soc)})
button_soc = widgets.Button(description="Esegui Simulazione", button_style='success', icon='calculator', layout=widgets.Layout(width='49%', margin='10px 0'))
button_export_soc = widgets.Button(description="Esporta Report", button_style='info', icon='download', layout=widgets.Layout(width='49%', margin='10px 0'))
output_area_soc = widgets.Output(); output_export_soc = widgets.Output()















def esegui_calcolo_societa(b):
    with output_area_soc:
        clear_output(wait=True); val_societa = {k: w.value for k, w in input_societa_widgets.items()}
        display(HTML(f"<h3>Parte 1: Analisi IRAP per la Società: {val_societa['nome_societa']}</h3>"));
        aliquota_irap = 0.039; irap_no_cpb = val_societa['valore_produzione_simulato_2024'] * aliquota_irap; irap_si_cpb = val_societa['valore_produzione_irap_rettificato_cpb'] * aliquota_irap; risparmio_irap = irap_no_cpb - irap_si_cpb
        df_irap = pd.DataFrame({"Senza Concordato": [irap_no_cpb], "Con Concordato": [irap_si_cpb], "Risparmio/Onere IRAP": [risparmio_irap]}, index=["Imposta IRAP Dovuta"]); display(df_irap)
        display(HTML("<hr><h3>Parte 2: Analisi IRPEF per i Singoli Soci</h3>"))
        for i in range(4):
            val_socio = {k: w.value for k, w in soci_widgets[i].items()}; perc_socio = val_socio['quota_partecipazione'] / 100.0
            if perc_socio == 0: continue
            quota_reddito_simulato = val_societa['reddito_simulato_2024'] * perc_socio; quota_reddito_rilevante = val_societa['reddito_rilevante_cpb_2023'] * perc_socio; quota_reddito_proposto = val_societa['reddito_proposto_cpb_2024'] * perc_socio; quota_reddito_rettificato_cpb = val_societa['reddito_impresa_rettificato_cpb'] * perc_socio
            base_imponibile_no_cpb = quota_reddito_simulato + val_socio['altri_redditi'] - val_socio['oneri_deducibili']- val_socio['cedolare_secca_redditi']
            irpef_ordinaria_no_cpb = calcola_irpef(base_imponibile_no_cpb)
            carico_fiscale_no_cpb = irpef_ordinaria_no_cpb - val_socio['imposte_gia_trattenute'] + val_socio['imposta_su_cedolare_secca'] - val_socio['acconti versati'] - val_socio['detrazioni IRPEF']
            base_imponibile_sostitutiva = quota_reddito_proposto - quota_reddito_rilevante
            if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
            if val_societa['punteggio_isa_n_soc'] >= 8: aliquota_sostitutiva = 0.10
            elif val_societa['punteggio_isa_n_soc'] >= 6: aliquota_sostitutiva = 0.12
            else: aliquota_sostitutiva = 0.15
            imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva
            base_imponibile_si_cpb = val_socio['altri_redditi'] + quota_reddito_rettificato_cpb - val_socio['cedolare_secca_redditi'] - val_socio['oneri_deducibili']
            tass_ordinaria_si_cpb = calcola_irpef(base_imponibile_si_cpb)
            carico_fiscale_concordato = imposta_sostitutiva + tass_ordinaria_si_cpb + val_socio['imposta_su_cedolare_secca'] - val_socio['acconti versati'] - val_socio['detrazioni IRPEF'] - val_socio['imposte_gia_trattenute']
            risparmio = carico_fiscale_no_cpb - carico_fiscale_concordato
            display(HTML(f"<h4>Riepilogo per: {val_socio['nome_socio']} (Quota: {val_socio['quota_partecipazione']:.2f}%)</h4>"))
            df_socio = pd.DataFrame({"Senza Concordato": [f"{carico_fiscale_no_cpb:,.2f} €"], "Con Concordato": [f"{carico_fiscale_concordato:,.2f} €"], "Risparmio/Onere": [f"{risparmio:,.2f} €"]}, index=["Carico Fiscale del Socio"]); display(df_socio)




def export_report_societa(b):
    with output_export_soc:
        clear_output(wait=True)
        val_societa = {k: w.value for k, w in input_societa_widgets.items()}
        html_content = f"<h1>Report di Convenienza CPB per la Società: {val_societa['nome_societa']}</h1>"

        # Aggiungo i dati della società al report
        df_societa_input = pd.DataFrame.from_dict(val_societa, orient='index', columns=['Valore Inserito'])
        html_content += f"<h2>Dati Società</h2>{df_societa_input.to_html()}"

        # Aggiungo l'analisi IRAP al report
        aliquota_irap = 0.039
        irap_no_cpb = val_societa['valore_produzione_simulato_2024'] * aliquota_irap
        irap_si_cpb = val_societa['valore_produzione_irap_rettificato_cpb'] * aliquota_irap
        risparmio_irap = irap_no_cpb - irap_si_cpb
        df_irap = pd.DataFrame({"Senza Concordato": [irap_no_cpb], "Con Concordato": [irap_si_cpb], "Risparmio/Onere IRAP": [risparmio_irap]}, index=["Imposta IRAP Dovuta"])
        html_content += f"<h2>Analisi IRAP</h2>{df_irap.to_html()}"

        html_content += "<h2>Analisi Singoli Soci</h2>"

        # Itera su ogni socio, riesegue i calcoli e aggiunge i risultati al report
        for i in range(4):
            val_socio = {k: w.value for k, w in soci_widgets[i].items()}
            perc_socio = val_socio['quota_partecipazione'] / 100.0
            if perc_socio == 0:
                continue

            # Ripartizione dei redditi societari
            quota_reddito_simulato = val_societa['reddito_simulato_2024'] * perc_socio
            quota_reddito_rilevante = val_societa['reddito_rilevante_cpb_2023'] * perc_socio
            quota_reddito_proposto = val_societa['reddito_proposto_cpb_2024'] * perc_socio
            quota_reddito_rettificato_cpb = val_societa['reddito_impresa_rettificato_cpb'] * perc_socio

            # Calcolo dettagliato per il socio (identico a quello della ditta individuale)
            base_imponibile_no_cpb = quota_reddito_simulato + val_socio['altri_redditi'] - val_socio['oneri_deducibili'] - val_socio['cedolare_secca_redditi']
            base_imponibile_si_cpb = val_socio['altri_redditi'] + quota_reddito_rettificato_cpb - val_socio['cedolare_secca_redditi'] - val_socio['oneri_deducibili']
            base_imponibile_sostitutiva = quota_reddito_proposto - quota_reddito_rilevante
            if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
            if val_societa['punteggio_isa_n_soc'] >= 8: aliquota_sostitutiva = 0.10
            elif val_societa['punteggio_isa_n_soc'] >= 6: aliquota_sostitutiva = 0.12
            else: aliquota_sostitutiva = 0.15
            imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva

            tass_ordinaria_si_cpb = calcola_irpef(base_imponibile_si_cpb)
            totale_tassazione_si_cpb = imposta_sostitutiva + tass_ordinaria_si_cpb + val_socio['imposta_su_cedolare_secca'] - val_socio['acconti versati'] - val_socio['detrazioni IRPEF'] - val_socio['imposte_gia_trattenute']

            tassazione_no_cpb_irpef = calcola_irpef(base_imponibile_no_cpb)
            totale_tassazione_no_cpb = tassazione_no_cpb_irpef - val_socio['imposte_gia_trattenute'] + val_socio['imposta_su_cedolare_secca'] - val_socio['acconti versati'] - val_socio['detrazioni IRPEF']

            risparmio_fiscale = totale_tassazione_no_cpb - totale_tassazione_si_cpb

            # Aggiunge i risultati del socio al report HTML
            df_socio_input = pd.DataFrame.from_dict(val_socio, orient='index', columns=['Valore Inserito'])
            html_content += f"<h4>Dati per {val_socio['nome_socio']} (Quota: {val_socio['quota_partecipazione']:.2f}%)</h4>{df_socio_input.to_html()}"

            df_socio_results = pd.DataFrame({
                "Descrizione": ["1) Base Imponibile IRPEF (con CPB)", "2) Base Imponibile IRPEF (senza CPB)", "3) Base Imponibile Sostitutiva", "4) Imposta Sostitutiva Calcolata", "5) Tassazione Ordinaria Residua (con CPB)", "6) TOTALE TASSE (CON ADESIONE CPB)", "7) Tassazione Totale (SENZA ADESIONE CPB)"],
                "Valore Calcolato": [base_imponibile_si_cpb, base_imponibile_no_cpb, base_imponibile_sostitutiva, imposta_sostitutiva, tass_ordinaria_si_cpb, totale_tassazione_si_cpb, totale_tassazione_no_cpb]
            }).set_index("Descrizione")

            html_content += f"<h4>Risultati per {val_socio['nome_socio']}</h4>{df_socio_results.to_html()}"
            html_content += f"<p><b>RISPARMIO / (MAGGIOR ONERE) per {val_socio['nome_socio']}: {risparmio_fiscale:,.2f} €</b></p><hr>"

        # Genera il link per il download
        link = create_download_link(html_content, f"report_{val_societa['nome_societa'].replace(' ', '_')}.html", "Scarica Report Società HTML")
        display(HTML(link))







def export_report_societa(b):
    with output_export_soc:
        clear_output(wait=True)
        val_societa = {k: w.value for k, w in input_societa_widgets.items()}
        html_content = f"<h1>Report di Convenienza CPB per la Società: {val_societa['nome_societa']}</h1>"

        # Dati Società
        df_societa_input = pd.DataFrame.from_dict(val_societa, orient='index', columns=['Valore Inserito'])
        html_content += f"<h2>Dati Società</h2>{df_societa_input.to_html()}"

        # Analisi IRAP
        aliquota_irap = 0.039
        irap_no_cpb = val_societa['valore_produzione_simulato_2024'] * aliquota_irap
        irap_si_cpb = val_societa['valore_produzione_irap_rettificato_cpb'] * aliquota_irap
        risparmio_irap = irap_no_cpb - irap_si_cpb
        df_irap = pd.DataFrame({"Senza Concordato": [irap_no_cpb], "Con Concordato": [irap_si_cpb], "Risparmio/Onere IRAP": [risparmio_irap]}, index=["Imposta IRAP Dovuta"])
        html_content += f"<h2>Analisi IRAP</h2>{df_irap.to_html()}"

        html_content += "<h2>Analisi Singoli Soci</h2>"

        # Itera su ogni socio per creare il report completo
        for i in range(4):
            val_socio = {k: w.value for k, w in soci_widgets[i].items()}
            perc_socio = val_socio['quota_partecipazione'] / 100.0
            if perc_socio == 0:
                continue

            # --- CORREZIONE QUI: Aggiunta tabella dati input del socio ---
            df_socio_input = pd.DataFrame.from_dict(val_socio, orient='index', columns=['Valore Inserito'])
            html_content += f"<h4>Dati per {val_socio['nome_socio']} (Quota: {val_socio['quota_partecipazione']:.2f}%)</h4>{df_socio_input.to_html()}"

            # Ripartizione dei redditi societari
            quota_reddito_simulato = val_societa['reddito_simulato_2024'] * perc_socio
            quota_reddito_rilevante = val_societa['reddito_rilevante_cpb_2023'] * perc_socio
            quota_reddito_proposto = val_societa['reddito_proposto_cpb_2024'] * perc_socio
            quota_reddito_rettificato_cpb = val_societa['reddito_impresa_rettificato_cpb'] * perc_socio

            # Calcolo dettagliato per il socio
            base_imponibile_no_cpb = quota_reddito_simulato + val_socio['altri_redditi'] - val_socio['oneri_deducibili'] - val_socio['cedolare_secca_redditi']
            irpef_ordinaria_no_cpb = calcola_irpef(base_imponibile_no_cpb)
            carico_fiscale_no_cpb = irpef_ordinaria_no_cpb - val_socio['imposte_gia_trattenute'] + val_socio['imposta_su_cedolare_secca'] - val_socio['acconti versati'] - val_socio['detrazioni IRPEF']

            base_imponibile_sostitutiva = quota_reddito_proposto - quota_reddito_rilevante
            if base_imponibile_sostitutiva < 0: base_imponibile_sostitutiva = 0
            if val_societa['punteggio_isa_n_soc'] >= 8: aliquota_sostitutiva = 0.10
            elif val_societa['punteggio_isa_n_soc'] >= 6: aliquota_sostitutiva = 0.12
            else: aliquota_sostitutiva = 0.15
            imposta_sostitutiva = base_imponibile_sostitutiva * aliquota_sostitutiva

            base_imponibile_si_cpb = val_socio['altri_redditi'] + quota_reddito_rettificato_cpb - val_socio['cedolare_secca_redditi'] - val_socio['oneri_deducibili']
            tass_ordinaria_si_cpb = calcola_irpef(base_imponibile_si_cpb)
            carico_fiscale_concordato = imposta_sostitutiva + tass_ordinaria_si_cpb + val_socio['imposta_su_cedolare_secca'] - val_socio['acconti versati'] - val_socio['detrazioni IRPEF'] - val_socio['imposte_gia_trattenute']

            risparmio_fiscale = carico_fiscale_no_cpb - carico_fiscale_concordato

            # Creazione della tabella di riepilogo per il socio
            df_socio_results = pd.DataFrame({
                "Senza Concordato": [f"{carico_fiscale_no_cpb:,.2f} €"],
                "Con Concordato": [f"{carico_fiscale_concordato:,.2f} €"],
                "Risparmio/Onere": [f"{risparmio_fiscale:,.2f} €"]
            }, index=["Carico Fiscale del Socio"])

            html_content += f"<h4>Risultati per {val_socio['nome_socio']}</h4>{df_socio_results.to_html()}<hr>"

        # Genera il link per il download
        link = create_download_link(html_content, f"report_{val_societa['nome_societa'].replace(' ', '_')}.html", "Scarica Report Società HTML")
        display(HTML(link))






button_soc.on_click(esegui_calcolo_societa); button_export_soc.on_click(export_report_societa)
box_societa_widgets = [widgets.VBox([input_societa_widgets[k], widgets.HTML(f"<i style='color:grey;font-size:10px;'>{descrizioni_aggiuntive.get(k,'')}</i>")]) for k in input_societa_widgets.keys()]
box_societa = widgets.VBox(box_societa_widgets, layout=widgets.Layout(border='1px solid #e0e0e0', padding='10px', margin='5px'))
tab_children = []
for i in range(4):
    socio_box_widgets = [widgets.VBox([soci_widgets[i][k], widgets.HTML(f"<i style='color:grey;font-size:10px;'>{descrizioni_aggiuntive.get(k,'')}</i>")]) for k in list(soci_widgets[i].keys()) if k not in ['nome_socio', 'quota_partecipazione']]
    socio_box_main = widgets.VBox([soci_widgets[i]['nome_socio'], soci_widgets[i]['quota_partecipazione']])
    col_sx_socio = widgets.VBox(socio_box_widgets[:4]); col_dx_socio = widgets.VBox(socio_box_widgets[4:])
    socio_box_cols = widgets.HBox([col_sx_socio, col_dx_socio])
    tab_children.append(widgets.VBox([socio_box_main, socio_box_cols]))
tab = widgets.Tab(); tab.children = tab_children
for i in range(4): tab.set_title(i, f"Socio {i+1}")
app_societa = widgets.VBox([widgets.HTML("<h3>CALCOLO CONVENIENZA CPB SOCIETÀ</h3>"), widgets.HTML("<h4>Dati Società</h4>"), box_societa, widgets.HTML("<h4>Dati dei Singoli Soci</h4>"), tab, widgets.HBox([button_soc, button_export_soc]), widgets.HTML("<hr>"), output_area_soc, output_export_soc])







#==============================================================================
# PASSO FINALE: CREAZIONE DELL'INTERFACCIA UNIFICATA CON SCELTA
#==============================================================================
app_individuale.layout.display = 'none'; app_societa.layout.display = 'none'
selettore = widgets.ToggleButtons(options=['Ditta Individuale', 'Società di Persone'], description='Seleziona il tipo di calcolo:', button_style='info')
def seleziona_calcolatore(change):
    scelta = change['new']
    if scelta == 'Ditta Individuale': app_individuale.layout.display = 'flex'; app_societa.layout.display = 'none'
    elif scelta == 'Società di Persone': app_individuale.layout.display = 'none'; app_societa.layout.display = 'flex'
selettore.observe(seleziona_calcolatore, names='value')
titolo_principale = widgets.HTML("<h1>Calcolatore di Convenienza Concordato Preventivo Biennale</h1>")
display(titolo_principale, selettore, app_individuale, app_societa)
