### README for Bryle - The RAG ChatBot

---

## Bryle - The RAG ChatBot
**This is an LLM-powered RAG chatbot with scraping capabilities.**

### Installation

#### 1. Create a Conda Environment
Create a new Conda environment to manage dependencies. Replace `your_env_name` with your desired environment name.
```bash
conda create --name your_env_name
conda activate your_env_name
```

#### 2. Install Required Libraries
Install all necessary libraries listed in the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

#### 3. Run the Application
Execute the main script using Streamlit to start the chatbot.
```bash
streamlit run main.py
```

### Additional Information

#### Updating Libraries
To update the installed libraries, you can run:
```bash
pip install --upgrade -r requirements.txt
```

#### Activating the Environment
Each time you start a new terminal session, activate the Conda environment with:
```bash
conda activate your_env_name
```

#### Deactivating the Environment
To deactivate the environment when you're done, use:
```bash
conda deactivate
```

### Configuration

#### Credentials and Environment Variables
If your application requires credentials or other environment variables, ensure they are set correctly in an `.env` file. Here is an example of how to set up your `.env` file:
```env
OPENAI_API_KEY=your_api_key
APIFY_API_TOKEN=your_secret_key
WEBSITE_URL=YOUR_WEBSITE_URL_TO_SCRAPE
```

### Usage

#### Running the ChatBot
Once the environment is set up and the application is running, you can interact with the chatbot through the Streamlit interface. The chatbot is capable of answering questions, performing searches, and scraping content from the web as needed.

### Troubleshooting

#### Common Issues
- **Environment Activation**: Ensure you have activated the correct Conda environment before running commands.
- **Library Installation**: Verify that all libraries are installed without errors. Missing libraries can cause runtime issues.
- **Credentials**: Double-check that all necessary credentials are correctly set in the `.env` file.

### Contribution

#### How to Contribute
1. **Fork the Repository**: Create a personal copy of the project on your GitHub account.
2. **Clone the Forked Repository**: Clone the repository to your local machine.
    ```bash
    git clone https://github.com/your_username/Bryle.git
    ```
3. **Create a New Branch**: Create a branch for your feature or bug fix.
    ```bash
    git checkout -b feature/your_feature_name
    ```
4. **Make Your Changes**: Implement your changes and commit them with descriptive messages.
5. **Push to Your Fork**: Push your changes to your forked repository.
    ```bash
    git push origin feature/your_feature_name
    ```
6. **Submit a Pull Request**: Open a pull request to the main repository.

---

