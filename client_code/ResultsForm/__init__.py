from ._anvil_designer import ResultsFormTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.media

class ResultsForm(ResultsFormTemplate):
  def __init__(self, row, as_pdf=False, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.row = row
    
    # Any code you write here will run when the form opens.
    total_plot_data = row['total_counts']
    self.total_plot.data = go.Bar(
        x = total_plot_data[0],
        y = total_plot_data[1]
      )
    random_sample_data = row['random_sample']
    self.random_plot.data =  go.Bar(
        x = random_sample_data[0],
        y = random_sample_data[1]
      )
    if as_pdf:
      self.pdf_button.visible = False
      self.return_button.visible = False

  def pdf_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pdf = anvil.server.call('get_pdf', self.row)
    anvil.media.download(pdf)

  def return_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('StartupForm')




