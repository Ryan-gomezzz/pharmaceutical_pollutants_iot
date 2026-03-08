import os
import subprocess

def main():
    print("====================================")
    print("   ML Pipeline Automation Script")
    print("====================================")
    
    # 1. Generate Dataset
    print("\n[Step 1] Generating Synthetic Dataset...")
    script_path = os.path.join("ml_training", "dataset_generator.py")
    
    if os.path.exists(script_path):
        subprocess.run(["python", script_path])
    else:
        print(f"Error: Could not find {script_path}")
        return

    # 2. Verify dataset saved
    dataset_path = os.path.join("dataset", "pollution_data.csv")
    if os.path.exists(dataset_path):
        print(f"Success: Dataset verified at {dataset_path}")
    else:
        print(f"Error: Dataset {dataset_path} was not created.")
        return
        
    # 3. Print instructions for training
    print("\n====================================")
    print("   Google Colab Training Workflow")
    print("====================================")
    print("1. Open Google Colab (colab.research.google.com).")
    print("2. Upload 'ml_training/train_models_colab.ipynb' to Google Colab.")
    print("3. In the Colab file explorer menu, manually create a 'dataset/' folder.")
    print("4. Upload the generated 'dataset/pollution_data.csv' file into the 'dataset/' folder on Colab.")
    print("5. Run all cells in the Colab notebook to train the Random Forest, LSTM, and feature scaler dynamically.")
    print("6. Download 'pollution_classifier.pkl', 'lstm_model.h5', and 'scaler.pkl' from Colab's output directory.")
    print("7. Place these three models locally into your computer's 'models/' project folder.")
    print("8. Run your final deployment backend using: python server/app.py")
    print("====================================\n")

if __name__ == "__main__":
    main()
