import streamlit as st
import requests
import json
import io

st.set_page_config(page_title="Code Smell Detection Agent", page_icon="🧠", layout="centered")
st.title("🧠 Code Smell Detection Agent")
st.write("Upload your Python file below to detect code smells and get optimization suggestions.")

uploaded_file = st.file_uploader("Upload a Python (.py) file", type=["py"])

if uploaded_file is not None:
    if st.button("🔍 Analyze Code"):
        with st.spinner("Analyzing your code... ⏳"):
            try:
                # Convert uploaded file to bytes
                files = {"file": (uploaded_file.name, io.BytesIO(uploaded_file.getvalue()), "text/x-python")}

                # Send request to FastAPI backend
                response = requests.post("http://127.0.0.1:8000/analyze", files=files)

                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Analysis Complete!")

                    if isinstance(data["report"], str):
                        st.info(data["report"])
                    else:
                        st.json(data["report"])

                    # Option to download report
                    report_json = json.dumps(data, indent=4)
                    st.download_button(
                        label="⬇️ Download Report",
                        data=report_json,
                        file_name="code_smell_report.json",
                        mime="application/json"
                    )
                else:
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error occurred')}")

            except requests.ConnectionError:
                st.error("🚫 Cannot connect to backend. Please ensure FastAPI is running.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
