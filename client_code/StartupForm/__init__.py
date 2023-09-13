from ._anvil_designer import StartupFormTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class StartupForm(StartupFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.run_calculations_button.enabled = False
    self.spinning_up_text.visible = False
    self.setup_task_running = False
    self.plot_task_running = False
    self.timer_1.interval = 0

  def spin_up_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.cluster_name = self.cluster_name_box.text
    with anvil.server.no_loading_indicator:
      self.setup_task = anvil.server.call('start_cluster', self.cluster_name)
    self.setup_task_running = True
    self.spin_up_button.enabled = False
    self.spinning_up_text.visible = True
    self.timer_1.interval = 1

  def run_calculations_button_click(self, **event_args):
    """This method is called when the button is clicked"""  
    with anvil.server.no_loading_indicator:
      self.plot_task = anvil.server.call('execute', self.cluster_name)
    self.plot_task_running = True
    self.timer_1.interval = 1


  def timer_1_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    if self.setup_task_running and self.setup_task.is_completed():
      self.setup_task_running = False
      self.run_calculations_button.enabled = True
      self.timer_1.interval = 0
      alert("Your new cluster is ready!")
    if self.plot_task_running and self.plot_task.is_completed():
      self.timer_1.interval = 0
      open_form('ResultsForm', self.plot_task.get_state()['row'])






