# DDI-MLops

DDI-MLops is a Dockerised MLOps pipeline designed to streamline Drug-Drug interaction machine learning development, deployment, and monitoring. It provides a containerised environment that integrates model training, serving, and experiment tracking using modern MLOps tools.

## 📦 Features

- Dockerised ML pipeline for easy deployment
- Integrated Random Forest Classification model training and inference
- Scalable and reproducible workflows
- Integration with experiment tracking tools “MLflow”

## 🛠️ Built With
- Docker
- Python
- Airflow
- MariaDB
- Pandas
- MLflow
- Scikit-learn
- Flask
- Redis

<!-- - [Docker](doc/docker.md)
- [Python](doc/python.md)
- [Airflow](doc/airflow.md)
- [MariaDB](doc/mariadb.md)
- [Pandas](doc/Pandas.md)
- [MLflow](doc/mlflow.md)
- [Scikit-learn](doc/scikit-learn.md)
- [Flask](doc/flask.md)
- [Redis](doc/redis.md) -->
## 🐳 Getting Started

### Prerequisites

Ensure the following tools are installed:

- [Docker](https://www.docker.com/get-started)
- [Git](https://git-scm.com/)

### Clone the Repository

```bash
git clone https://github.com/Abdulrahman-AlAsali/DDI-MLops.git
cd DDI-MLops
```

### Run the application

```bash
docker-compose up
```

Now wait till the containers are all up and running, then the application can be accessed using ports:
- `80` for the frontend
- `8080` for Airflow frontend
- `5000` for MLflow

## 📚 Documentation
- [Data ingestion](doc/data_ingestion.md)
- [Data transformation](doc/data_transformation.md)
- [Model training](doc/model_training.md)
- [Caching](doc/caching.md)
- [Application interface](doc/application_interface.md)

## 📄 License
This project is licensed under the BSD 3 License – see the LICENSE file for details.

## Contributing
Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## 🙌 Acknowledgments 
- **Sima Iranmanesh** Lecturer in Data Science at Birmingham City University
