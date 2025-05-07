#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import streamlit as st
from hanziconv import HanziConv
import os

# 1. Read the CSV into a DataFrame, specifying encoding
df = pd.read_csv("Laozi Parallel Corpus.csv", encoding='utf-8')  # Or 'utf-8-sig' if BOM present

# 2. Function to search for a word in the 'English' column
def search_word(word, df, selected_chapter, selected_native, selected_year):
    filtered_df = df.copy()
    if selected_chapter != "All":
        filtered_df = filtered_df[filtered_df['Chapter'] == selected_chapter]
    if selected_native != "All":
        filtered_df = filtered_df[filtered_df['Native'] == selected_native]
    filtered_df = filtered_df[
        (filtered_df['Year'] >= selected_year[0]) & (filtered_df['Year'] <= selected_year[1])
    ]
    search_results = filtered_df[filtered_df['English'].str.contains(word, case=False, na=False)]
    return search_results

# 3. Function to search Chinese characters
def search_chinese(characters, df):
    traditional_characters = HanziConv.toTraditional(characters)
    search_results = df[
        df['Chinese'].str.contains(characters, na=False) | 
        df['Chinese'].str.contains(traditional_characters, na=False)
    ]
    return search_results


# Streamlit app
st.title("Laozi Parallel Corpus")

# Introduction and Documentation Link

# Serve the PDF
with open("Documentation for the Laozi Parallel Corpus.pdf", "rb") as f:
    pdf_bytes = f.read()
    st.download_button(
        label="Download Documentation",
        data=pdf_bytes,
        file_name="Documentation for the Laozi Parallel Corpus.pdf",
        mime="application/pdf",
    )
    
st.markdown("""
The Laozi Parallel Corpus, developed by Joyce Oiwun Cheung, a Lecturer at Hong Kong Metropolitan University, serves as a resource for researchers and enthusiasts interested in the translations of the Chinese classic Laozi (道德經, Dao De Jing / Tao Te Ching). This app features 79 English translations published between 1884 and 2018, aligned line-by-line by Cheung in 2021. With a user-friendly interface, users can easily search for English words or Chinese characters, retrieving relevant sentences and their corresponding translations from various eras.

This app is intended for non-profit use only. Any parties interested in using the app should cite the following source: Cheung, J.O. (2025). Exploring L1/L2 and time impact on linguistic complexity of Laozi translations. Australian Review of Applied Linguistics. https://doi.org/10.1075/aral.24025.che. For inquiries, contact Joyce Cheung at owcheung@hkmu.edu.hk.
""")


# Sidebar filters
st.sidebar.header("Filters")
chapters = ["All"] + sorted(df['Chapter'].unique())
selected_chapter = st.sidebar.selectbox("Chapter", chapters)

natives = ["All"] + sorted(df['Native'].unique())
selected_native = st.sidebar.selectbox("Native", natives)

min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
selected_year = st.sidebar.slider(
    "Year", min_year, max_year, (min_year, max_year)
)


# Language selection
search_language = st.radio("Search in:", ("English", "Chinese"))


# Apply filters to the DataFrame
filtered_df = df.copy()
if selected_chapter != "All":
    filtered_df = filtered_df[filtered_df['Chapter'] == selected_chapter]
if selected_native != "All":
    filtered_df = filtered_df[filtered_df['Native'] == selected_native]
filtered_df = filtered_df[
    (filtered_df['Year'] >= selected_year[0]) & (filtered_df['Year'] <= selected_year[1])
]


if search_language == "English":
    search_term = st.text_input("Enter a word to search:")
    if search_term:
        results = search_word(search_term, filtered_df, selected_chapter, selected_native, selected_year)
        if not results.empty:

            sort_by = st.selectbox("Sort by", ["None", "Translator", "Year", "Chapter"])
            ascending = st.checkbox("Ascending Order", value=True)

            if sort_by != "None":
                results = results.sort_values(by=sort_by, ascending=ascending)

            st.write(f"Found {len(results)} sentences containing '{search_term}':")
            st.download_button(
                label="Download Search Results",
                data=results.to_csv(index=False, encoding='utf-8-sig'),
                file_name=f"laozi_search_results_{search_term}.csv",
                mime="text/csv",
            )

            for index, row in results.iterrows():
                if st.button(row['English'], key=f"button_{index}"):
                    chinese_sentence = row['Chinese']
                    id_results = df[df['Chinese'] == chinese_sentence]  # Corrected filter condition
                    st.write(f"**Chinese:** {chinese_sentence}")
                    st.write(f"**Other English Translations for the same Chinese sentence (ID: {row['ID']}):**")
                    st.download_button(
                        label="Download ID Results",
                        data=id_results.to_csv(index=False, encoding='utf-8-sig'),
                        file_name=f"laozi_id_results_{row['ID']}.csv",
                        mime="text/csv",
                        key=f"download_{index}"  # Added unique key for download button
                    )
                    for idx, r in id_results.iterrows():
                        st.write(f"**English:** {r['English']}")
                        st.write(f"**Translator:** {r['Translator']}")
                        st.write(f"**Year:** {r['Year']}")
                        st.write(f"**Chapter:** {r['Chapter']}")
                        st.write("---")
        else:
            st.write(f"No sentences found containing '{search_term}'.")


elif search_language == "Chinese":
    search_term = st.text_input("Enter Chinese characters to search:")
    if search_term:
        results = search_chinese(search_term, filtered_df)
        if not results.empty:
            results_with_chapter = results[['Chinese', 'Chapter']].drop_duplicates()

            sort_by_chinese = st.selectbox("Sort by", ["None", "Chapter"], key="chinese_sort")
            ascending_chinese = st.checkbox("Ascending Order", value=True, key="chinese_asc")

            if sort_by_chinese != "None":
                results_with_chapter = results_with_chapter.sort_values(by=sort_by_chinese, ascending=ascending_chinese)

            st.write(f"Found {len(results_with_chapter)} sentences containing '{search_term}':")
            st.download_button(
                label="Download Search Results",
                data=results_with_chapter.to_csv(index=False, encoding='utf-8-sig'),
                file_name=f"laozi_search_results_{search_term}.csv",
                mime="text/csv",
            )

            for index, row in results_with_chapter.iterrows():
                if st.button(row['Chinese'], key=f"button_chinese_{index}"):
                    id_results = df[df['Chinese'] == row['Chinese']]
                    st.write(f"**English Translations:**")

                    st.download_button(
                        label="Download ID Results",
                        data=id_results.to_csv(index=False, encoding='utf-8-sig'),
                        file_name=f"laozi_id_results_{row['Chinese']}.csv",  # More descriptive filename
                        mime="text/csv",
                        key=f"download_chinese_{index}" # Added unique key
                    )

                    for idx, r in id_results.iterrows():
                        st.write(f"**English:** {r['English']}")
                        st.write(f"**Translator:** {r['Translator']}")
                        st.write(f"**Year:** {r['Year']}")
                        st.write(f"**Chapter:** {r['Chapter']}")
                        st.write("---")
        else:
            st.write(f"No sentences found containing '{search_term}'.")



# CSS for left alignment
st.markdown(
    """
    <style>
    .stButton > button {
        text-align: left;
        width: 100%;
        justify-content: flex-start;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

