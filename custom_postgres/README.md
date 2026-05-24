ELT Pipeline with dbt & Airflow
An automated data pipeline that extracts film data from a source database, loads it into a destination database, and transforms it into clean, analysis-ready model: all orchestrated by Apache Airflow inside Docker.

How It Works?
1.Extract & Load — elt_script.py uses pg_dump to copy raw data (films, actors, mappings) from the source database into the destination database
2.Transform — dbt joins and enriches the data, adding rating categories (Excellent / Good / Average / Poor) and actor lists per film
3.Orchestrate — Airflow runs these two steps in order, every day automatically

Running It
bash
-docker-compose up --build

- Open Airflow UI
http://localhost:8096 and login

-Trigger the DAG
