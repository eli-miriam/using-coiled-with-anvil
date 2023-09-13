import anvil.secrets
import anvil.server
import coiled
from anvil.tables import app_tables
from datetime import datetime
import dask

dask.config.set({
  "coiled.token": anvil.secrets.get_secret('coiled_token'), # get the API token
  "coiled.user": "eli-holderness",
  "coiled.account": "eli-holderness",
  "coiled.server": "https://cloud.coiled.io",
})

DEFAULT_CLUSTER_NAME = "anvil-coiled-demo"

@anvil.server.callable
def start_cluster(name):
  task = anvil.server.launch_background_task('setup_cluster', name)
  return task


@anvil.server.background_task
def setup_cluster(name):
  cluster = coiled.Cluster(
    name=name if name else DEFAULT_CLUSTER_NAME,
    n_workers=1,
    scheduler_options={"idle_timeout": "1 hour"},
    shutdown_on_close=False,
  )


@anvil.server.callable
def execute(cluster_name):
  task = anvil.server.launch_background_task('plot_timeseries_data', cluster_name)
  return task


@anvil.server.background_task
def plot_timeseries_data(cluster_name):
  reconnect_to_existing_cluster(cluster_name)
  import dask
  ddf = dask.datasets.timeseries(
    start="2000-01-01",
    end="2000-01-02",
    freq="5s",
    seed=42,
  )
  row = app_tables.output.add_row()
  total_counts = ddf.groupby(ddf.name).count().drop(labels=["x", "y"], axis=1).compute()['id']
  row['total_counts'] = [total_counts.index.values, total_counts.values]
  
  random_sample_ddf = ddf.sample(frac=0.005, random_state=42)
  random_sample_counts = random_sample_ddf.groupby(random_sample_ddf.name).count().drop(labels=["x", "y"], axis=1).compute()['id']
  row['random_sample'] = [random_sample_counts.index.values, random_sample_counts.values]
  anvil.server.task_state['row'] = row


def reconnect_to_existing_cluster(name):
  cluster = coiled.Cluster(
    name=name if name else DEFAULT_CLUSTER_NAME,
    shutdown_on_close=False
  )
  from distributed import Client
  return Client(cluster)


@anvil.server.callable
def get_pdf(row):
  pdf = anvil.pdf.PDFRenderer(
    quality="original", 
    page_size="A4",
    filename="Anvil Coiled Results.pdf"
  ).render_form(
    'ResultsForm', 
    row,
    True
  )
  return pdf