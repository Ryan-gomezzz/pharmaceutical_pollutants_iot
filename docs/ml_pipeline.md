# Machine Learning Training Pipeline

Follow these exact steps to generate the pollution dataset, scale your Machine Learning capabilities training via Google Colab, and spin up inference locally natively on your IoT server.

## 1. Run Dataset Generator
Run the built-in automation script to create the synthetic dataset locally:
```bash
python setup_ml_pipeline.py
```
This drops `dataset/pollution_data.csv` populated with 10k highly randomized but constrained realistic time-series samples mimicking real environmental sensor metrics.

## 2. Upload to Google Colab
1. Navigate to Google Colab.
2. Import the local file `ml_training/train_models_colab.ipynb`.
3. In the Colab sidebar (Files), manually create a folder named `dataset` and upload the generated `pollution_data.csv`.

## 3. Train Models
Run the Colab notebook cells from top-to-bottom! Because deep networks like LSTMs can benefit from immense computational power, utilizing Google's cloud GPUs rapidly accelerates compilation and epoch cycling.

## 4. Download Trained Artifacts
Once Colab finalizes your epochs, download the generated weight outputs from the cloud:
- `pollution_classifier.pkl` (Random Forest Matrix)
- `lstm_model.h5` (Keras Deep Learning Network)
- `scaler.pkl` (MinMax mapping weights required natively for the backend)

## 5. Implement Models
Move those three local files directly into the `models/` folder located in the parent directory of this project file tree.

## 6. Start the Server
Now spool up the main architecture API natively:
```bash
cd server
python app.py
```
The Flask backend natively injects data buffers dynamically to your Edge hardware IoT ecosystem, simulating pollution probability mapping seamlessly.
