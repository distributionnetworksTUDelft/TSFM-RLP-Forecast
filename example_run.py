from gluonts.evaluation import make_evaluation_predictions, Evaluator
import matplotlib.pyplot as plt
import matplotlib as mpl
import json

from dataset.example import get_example_dataset
from model.example import ExampleEstimator, ExampleTrainer
from utility.configuration import ExampleDataConfig, ExampleModelConfig, ExperimentConfig

def main():
    data_config = ExampleDataConfig.from_yaml(
        'configs/data/example.yaml'
    )
    model_config = ExampleModelConfig.from_yaml(
        'configs/model/example.yaml'
    )
    exp_config = ExperimentConfig(
        exp_id='0.0.666',
        data=data_config,
        model=model_config,
    )
    dataset = get_example_dataset(data_config)
    trainer = ExampleTrainer(lr=0.001, epochs=50)
    estimator = ExampleEstimator(
        prediction_length=model_config.prediction_length, # TODO: should be in the data config
        past_length=model_config.past_length,
        hidden_dim=model_config.hidden_dim,
        trainer=trainer,
    )
    estimator.create_training_data_loader(dataset)
    estimator.create_training_network()
    predictor = estimator.train(dataset)
    
    # Evaluation
    forecast_it, ts_it = make_evaluation_predictions(
        dataset=dataset.test,
        predictor=predictor,
        num_samples=100,
    )
    ts_entry = next(iter(ts_it))
    forecast_entry = next(iter(forecast_it))
    plt.plot(ts_entry[-150:].to_timestamp())
    forecast_entry.plot(show_label=True)
    plt.legend()
    
    evaluator = Evaluator(quantiles=[0.1, 0.5, 0.9])
    agg_metrics, item_metrics = evaluator(
        iter(ts_it),
        iter(forecast_it),
        num_series=len(dataset.test),
    )
    print(json.dump(agg_metrics, indent=4))
    print(item_metrics.head())

if __name__ == "__main__":
    main()