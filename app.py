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
    # (Logica di calcolo invariata)
    pass

def export_report_individuale(b):
    # (Logica di esportazione invariata)
    pass

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
    soci_widgets.append({
        'nome_socio': widgets.Text(value=val_default['nome'], description="Nome Socio:", style=style_soc, layout=layout_stretto_soc),
        'quota_partecipazione': widgets.FloatText(value=val_default['quota'], description="QUOTA PARTECIPAZIONE (%):", style=style_soc, layout=layout_stretto_soc),
        'altri_redditi': widgets.FloatText(value=val_default['altri_redditi'], description="ALTRI REDDITI TASSABILI IRPEF:", style=style_soc, layout=layout_stretto_soc),
        'oneri_deducibili': widgets.FloatText(value=val_default['oneri_deducibili'], description="ONERI DEDUCIBILI:", style=style_soc, layout=layout_stretto_soc),
        # --- CORREZIONE QUI: Aggiunta la voce mancante ---
        'cedolare_secca_redditi': widgets.FloatText(value=val_default['cedolare_secca_redditi'], description="REDDITI A CEDOLARE SECCA O TASS. SEP.:", style=style_soc, layout=layout_stretto_soc),
        'imposte_gia_trattenute': widgets.FloatText(value=val_default['imposte_gia_trattenute'], description="IMPOSTE SU REDDITI GIA' TASSATI:", style=style_soc, layout=layout_stretto_soc),
        'imposta_su_cedolare_secca': widgets.FloatText(value=val_default['imposta_su_cedolare_secca'], description="IMPOSTA SU CEDOLARE SECCA:", style=style_soc, layout=layout_stretto_soc),
        'acconti versati': widgets.FloatText(value=val_default['acconti versati'], description="ACCONTI VERSATI:", style=style_soc, layout=layout_stretto_soc),
        'detrazioni IRPEF': widgets.FloatText(value=val_default['detrazioni IRPEF'], description="DETRAZIONI IRPEF:", style=style_soc, layout=layout_stretto_soc)
    })
button_soc = widgets.Button(description="Esegui Simulazione", button_style='success', icon='calculator', layout=widgets.Layout(width='49%', margin='10px 0'))
button_export_soc = widgets.Button(description="Esporta Report", button_style='info', icon='download', layout=widgets.Layout(width='49%', margin='10px 0'))
output_area_soc = widgets.Output(); output_export_soc = widgets.Output()

def esegui_calcolo_societa(b):
    # (Logica di calcolo per le società, invariata)
    pass

def export_report_societa(b):
    # (Logica di esportazione per le società, invariata)
    pass

button_soc.on_click(esegui_calcolo_societa); button_export_soc.on_click(export_report_societa)
box_societa_widgets = [widgets.VBox([input_societa_widgets[k], widgets.HTML(f"<i style='color:grey;font-size:10px;'>{descrizioni_aggiuntive.get(k,'')}</i>")]) for k in input_societa_widgets.keys()]
box_societa = widgets.VBox(box_societa_widgets, layout=widgets.Layout(border='1px solid #e0e0e0', padding='10px', margin='5px'))
tab_children = []
for i in range(4):
    socio_box_widgets = [widgets.VBox([soci_widgets[i][k], widgets.HTML(f"<i style='color:grey;font-size:10px;'>{descrizioni_aggiuntive.get(k,'')}</i>")]) for k in list(soci_widgets[i].keys()) if k not in ['nome_socio', 'quota_partecipazione']]
    socio_box_main = widgets.VBox([soci_widgets[i]['nome_socio'], soci_widgets[i]['quota_partecipazione']])
    col_sx_socio = widgets.VBox(socio_box_widgets[:5]); col_dx_socio = widgets.VBox(socio_box_widgets[5:]) # Adattato per il nuovo numero di campi
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
