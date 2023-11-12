import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from pandasai import SmartDatalake
from pandasai.llm.openai import OpenAI
from pandasai.middlewares import StreamlitMiddleware
from pandasai.responses.streamlit_response import StreamlitResponse

# Loading Environment Variables Using the `dotenv` Package
load_dotenv()


if __name__ == "__main__":
    st.set_page_config(
        layout="wide",
        page_icon="./logo.svg",
        page_title="Chat with Excel / CSV Data",
    )
    st.title("Chat with Excel / CSV Data")

    st.header("Set your API Key")
    # Get API base from input or environment variable
    api_base_input = st.text_input(
        "Enter API Base (Leave empty to use environment variable)",
        value=os.environ.get("OPENAI_API_BASE"),
    )

    # Get API key from input or environment variable
    api_key_input = st.text_input(
        "Enter API Key (Leave empty to use environment variable)",
        type="password",
        value=os.environ.get("OPENAI_API_KEY"),
    )

    # Set OpenAI API key
    openai_api_base = (
        api_base_input if api_base_input else os.environ.get("OPENAI_API_BASE")
    )
    openai_api_key = (
        api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY")
    )

    # Create llm instance
    llm = OpenAI(api_token=openai_api_key)
    llm.api_base = openai_api_base

    # Allow user to upload multiple files
    input_files = st.file_uploader(
        "Upload files", type=["xlsx", "csv"], accept_multiple_files=True
    )

    # If user uploaded files, load them
    if len(input_files) > 0:
        data_list = []
        for input_file in input_files:
            if input_file.name.lower().endswith(".csv"):
                data = pd.read_csv(input_file)
            else:
                data = pd.read_excel(input_file)
            st.dataframe(data, use_container_width=True)
            data_list.append(data)
    # Otherwise, load the default file
    else:
        st.header("Example Data")
        data = pd.read_excel("./Sample.xlsx")
        st.dataframe(data, use_container_width=True)
        data_list = [data]

    # Create SmartDatalake instance
    df = SmartDatalake(
        dfs=data_list,
        config={
            "llm": llm,
            "verbose": True,
            "response_parser": StreamlitResponse,
            "middlewares": [StreamlitMiddleware()],
        },
    )

    # Input text
    st.header("Ask anything!")
    input_text = st.text_area(
        "Enter your question", value="What is the total profit for each country?"
    )

    if input_text is not None:
        if st.button("Start Execution"):
            result = df.chat(input_text)

            # Display the result
            st.header("Answer")
            st.write(result)

            # Display the corresponding code
            st.header("The corresponding code")
            st.code(df.last_code_executed, language="python", line_numbers=False)
