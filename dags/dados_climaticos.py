from airflow.models import DAG
import pendulum
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.macros import ds_add
import pandas as pd
import os

with DAG(
    "dados_climaticos",
    start_date=pendulum.datetime(2025, 3, 3, tz="UTC"),
    schedule_interval='0 0 * * 1'
) as dag:
    
    tarefa_1 = BashOperator(
        task_id='cria_pasta',
        bash_command='mkdir -p "/home/andressa/airflow/semana={{ data_interval_end.strftime("%Y-%m-%d") }}"'
    )

    def extrai_dados(data_interval_end):  
        city = 'Itaitinga'
        key = 'X'

        start_date = data_interval_end
        end_date = ds_add(data_interval_end, 7)

       
        url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{start_date}/{end_date}?unitGroup=metric&include=days&key={key}&contentType=csv'

        
        dados = pd.read_csv(url)

       
        file_path = f'/home/andressa/airflowa/semana={start_date}/'
        os.makedirs(file_path, exist_ok=True)  

        
        dados.to_csv(file_path + 'dados_brutos.csv', index=False)
        dados[['datetime', 'tempmin', 'temp', 'tempmax']].to_csv(file_path + 'temperaturas.csv', index=False)
        dados[['datetime', 'description', 'icon']].to_csv(file_path + 'condicoes.csv', index=False)

    tarefa_2 = PythonOperator(
        task_id='extrai_dados',
        python_callable=extrai_dados,
        op_kwargs={'data_interval_end': '{{ data_interval_end.strftime("%Y-%m-%d") }}'}
    )

    tarefa_1 >> tarefa_2  
