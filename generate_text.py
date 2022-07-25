import streamlit as st
import numpy as np
import os
from typing import List, Callable
import matplotlib.pyplot as plt


def clean_tokens(tokens: List[str]) -> List[str]:
    tokens = [t.replace(" ", "") for t in tokens]
    return tokens

def tokens_for_folder(folder: str, filter: Callable[[str], bool] = lambda x: True) -> List[str]:
    tokens: List[str] = []
    for file in os.listdir(folder):
        if filter(file):
            with open(folder + "/" + file) as f:
                tokens.extend(f.read().split())
    tokens = clean_tokens(tokens)
    return tokens

def tokens_for_file(file):
    tokens: List[str] = []
    with open(file) as f:
        tokens = f.read().split()
    tokens = clean_tokens(tokens)
    return tokens

def load_file(file):
    with open(file) as f:
        return f.read()

def tokens_for_string(str: str) -> List[str]:
    return clean_tokens(str.split())

def calculate_transition_matrix(tokens: List[str]) -> np.ndarray:
    
    unique_tokens = list(set(tokens))
    unique_word_combination_counts = {}
    total_froms = {}

    transition_matrix = np.zeros((len(unique_tokens), len(unique_tokens)))

    for i, token in enumerate(tokens):
        if i < len(tokens) - 1:
            from_to = (token, tokens[i + 1])
            unique_word_combination_counts[from_to] = unique_word_combination_counts.get(from_to, 0) + 1
            total_froms[token] = total_froms.get(token, 0) + 1

    for key, value in unique_word_combination_counts.items():
        _from, _to = key 
        
        transition_matrix[unique_tokens.index(_from), unique_tokens.index(_to)] = value / total_froms[_from]
        
    return transition_matrix

def generate_text(tokens: List[str], length: int, P_matrix: np.ndarray, P_init: np.ndarray=None) -> str:
    unique_tokens = list(set(tokens))
    
    text = []
    if P_init is not None:
      current_token = np.random.choice(unique_tokens, p=P_init) 
    else:
        current_token = np.random.choice(unique_tokens)
    
    text.append(current_token)
    for i in range(length):
        # Token should not be the last token in the text as there is no probability of transitioning from it to anything
        # Workaround could be to use the first token as the token to transition to
        while current_token == tokens[-1]:
            current_token = np.random.choice(unique_tokens)
    
        current_token = np.random.choice(unique_tokens, p=P_matrix[unique_tokens.index(current_token)])
        text.append(current_token)
    return " ".join(text)


def plot_transition_matrix(P_matrix: np.ndarray):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.spy(P_matrix, markersize=2)
    plt.title("Transition Matrix")
    return fig

example_text_mapping = {
    "Las Vegas (German)": "text.txt",
    "Sport (German)": "text2.txt"
}

if "source_text" not in st.session_state:
    st.session_state.source_text = ""
if "P_matrix" not in st.session_state:
    st.session_state["P_matrix"] = None
if "P_init" not in st.session_state:
    st.session_state["P_init"] = None
if "tokens" not in st.session_state:
    st.session_state["tokens"] = []
if "initial_word" not in st.session_state:
    st.session_state["initial_word"] = ""
if "selected_text" not in st.session_state:
    st.session_state["selected_text"] = ""


st.sidebar.write("### Examples")
selected_example_text = st.sidebar.selectbox("Select Example Text", ["Custom", "Las Vegas (German)", "Sport (German)"])
st.write("# Markov Chain Text Generator")
st.write("This is a simple text generator that uses markov chains to generate text based on a source text. Read more about the way it works in the [related blog post](https://)")


def reload_generator():

    print("Relaoading generator")
    
    tokens = tokens_for_string(st.session_state["source_text"])

    st.session_state["tokens"] = tokens
    st.session_state["P_matrix"] = calculate_transition_matrix(tokens)

if selected_example_text != "Custom":
        st.session_state["selected_text"] = load_file(example_text_mapping[selected_example_text])


source_text = st.text_area("Paste or write source text here:", st.session_state["selected_text"])
st.text_input("Start generated text with this word or sentence (last word has to be in the source text):", key="initial_word")
length = st.number_input("Length of the generated text (in words):", value=100)
show_transition_matrix = st.checkbox("Show transition matrix")


if st.button("Generate Text"):
    with st.spinner("Generating text"):
          
        if st.session_state["source_text"] != source_text:
            print("Have to reload generator")

            print(source_text[:10])
            print(st.session_state["source_text"][:10])
    
            st.session_state["source_text"] = source_text
            reload_generator()
            # print(st.session_state["source_text"][:10])
            print("Reloaded generator")

        if st.session_state["initial_word"] != "":
            st.session_state["P_init"] = None
            unique_tokens = list(set(st.session_state["tokens"]))
            start_token = st.session_state["initial_word"].split()[-1]
            if start_token in unique_tokens:
                st.session_state["P_init"] = np.zeros(len(unique_tokens))
                st.session_state["P_init"][unique_tokens.index(start_token)] = 1    

        text = " ".join(st.session_state["initial_word"].split()[:-1]) + " "
        text += generate_text(st.session_state["tokens"], length, st.session_state["P_matrix"], st.session_state["P_init"])

        st.write("### Generated text:")
        st.write(text)

        st.write("Length of source text:", len(st.session_state["tokens"]))

        if show_transition_matrix:
            st.write("### Transition matrix:")
            st.write("Shape:", st.session_state["P_matrix"] .shape)
            st.write(plot_transition_matrix(st.session_state["P_matrix"]))
            st.write(st.session_state["P_matrix"])


